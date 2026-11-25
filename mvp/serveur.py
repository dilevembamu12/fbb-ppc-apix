#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Moteur du MVP APIX — chaîne de preuve, sans dépendance externe.

Ce fichier n'utilise que la bibliothèque standard de Python : pas de framework,
pas de serveur de messages, pas de base distante. Un fichier SQLite, un serveur
HTTP, et les règles du dossier.

Les règles appliquées (annexe A1, règles de gestion) :

    RG-COT-04   La cotation est la référence du paiement.
    RG-COT-05   Une cotation expirée n'est pas payable.
    RG-CMD-01   Le bon naît de l'encaissement, jamais d'une demande.
    RG-CMD-04   Le bon est nominatif.
    RG-CMD-05   Le bon est à usage unique : un second contrôle est refusé.
    RG-CHG-02   Le bon est contrôlé par son QR signé *ou* par son code de retrait.

Le bon porte une signature : un bon modifié est refusé pour signature invalide.
C'est ce refus qui prouve que le contrôle existe.

Usage :
    python mvp/serveur.py            # http://127.0.0.1:8765
    python mvp/serveur.py --port 9000
"""

from __future__ import annotations

import argparse
import hashlib
import hmac
import json
import mimetypes
import re
import secrets
import sqlite3
import sys
from datetime import datetime, timedelta
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import urlparse

RACINE = Path(__file__).resolve().parent
WEB = RACINE / "web"
BASE = RACINE / "mvp.sqlite3"

SECRET = b"apix-mvp-demonstration"          # signature des bons : à sortir du code en production
VALIDITE_HEURES = 48                         # durée de validité d'une cotation (Q-51)
TOLERANCE_SACS = 2                           # écart accepté à la réception (RG-POD-04)


# ---------------------------------------------------------------------------
# Base de données
# ---------------------------------------------------------------------------
def maintenant() -> datetime:
    return datetime.now().replace(microsecond=0)


def iso(moment: datetime) -> str:
    return moment.isoformat(timespec="seconds")


def connexion() -> sqlite3.Connection:
    base = sqlite3.connect(BASE)
    base.row_factory = sqlite3.Row
    base.execute("PRAGMA foreign_keys = ON")
    return base


SCHEMA = """
CREATE TABLE IF NOT EXISTS produits (
    id        INTEGER PRIMARY KEY,
    nom       TEXT NOT NULL,
    prix_sac  REAL NOT NULL
);
CREATE TABLE IF NOT EXISTS zones (
    id             INTEGER PRIMARY KEY,
    nom            TEXT NOT NULL,
    prix_transport REAL NOT NULL
);
CREATE TABLE IF NOT EXISTS cotations (
    numero        TEXT PRIMARY KEY,
    client        TEXT NOT NULL,
    telephone     TEXT NOT NULL,
    produit       TEXT NOT NULL,
    quantite      INTEGER NOT NULL,
    zone          TEXT NOT NULL,
    option        TEXT NOT NULL,           -- A enlèvement, B transport PPC
    prix_unitaire REAL NOT NULL,
    transport     REAL NOT NULL,
    total         REAL NOT NULL,
    emise_le      TEXT NOT NULL,
    valide_jusqua TEXT NOT NULL,
    statut        TEXT NOT NULL            -- emise, payee, perimee
);
CREATE TABLE IF NOT EXISTS paiements (
    id             INTEGER PRIMARY KEY AUTOINCREMENT,
    cotation       TEXT NOT NULL REFERENCES cotations(numero),
    canal          TEXT NOT NULL,
    reference      TEXT NOT NULL,
    montant        REAL NOT NULL,
    encaisse_le    TEXT NOT NULL
);
CREATE TABLE IF NOT EXISTS bons (
    code        TEXT PRIMARY KEY,          -- code de retrait à six chiffres
    numero      TEXT NOT NULL UNIQUE,      -- BON-000123
    cotation    TEXT NOT NULL REFERENCES cotations(numero),
    client      TEXT NOT NULL,
    produit     TEXT NOT NULL,
    quantite    INTEGER NOT NULL,
    zone        TEXT NOT NULL,
    emis_le     TEXT NOT NULL,
    statut      TEXT NOT NULL              -- emis, charge, livre
);
CREATE TABLE IF NOT EXISTS chargements (
    id        INTEGER PRIMARY KEY AUTOINCREMENT,
    bon       TEXT NOT NULL REFERENCES bons(code),
    agent     TEXT NOT NULL,
    sacs      INTEGER NOT NULL,
    scelle    TEXT NOT NULL,
    charge_le TEXT NOT NULL
);
CREATE TABLE IF NOT EXISTS receptions (
    id           INTEGER PRIMARY KEY AUTOINCREMENT,
    bon          TEXT NOT NULL REFERENCES bons(code),
    sacs_recus   INTEGER NOT NULL,
    ecart        INTEGER NOT NULL,
    etat         TEXT NOT NULL,
    scelle_ok    INTEGER NOT NULL,
    recu_le      TEXT NOT NULL,
    litige       INTEGER NOT NULL
);
"""


def amorcer() -> None:
    """Crée le schéma et les données de référence (prix réels PPC, barème de travail)."""
    base = connexion()
    base.executescript(SCHEMA)
    if base.execute("SELECT COUNT(*) AS n FROM produits").fetchone()["n"] == 0:
        base.executemany(
            "INSERT INTO produits (nom, prix_sac) VALUES (?, ?)",
            [("Surecem", 9.5), ("Surecast", 8.0)],
        )
        base.executemany(
            "INSERT INTO zones (nom, prix_transport) VALUES (?, ?)",
            [("Gombé", 320.0), ("Limete", 280.0), ("Ngaliema", 360.0), ("Basoko", 340.0)],
        )
        base.commit()
    base.close()


# ---------------------------------------------------------------------------
# Signature du bon
# ---------------------------------------------------------------------------
def signature(numero: str, quantite: int, produit: str) -> str:
    contenu = f"{numero}|{quantite}|{produit}".encode("utf-8")
    return hmac.new(SECRET, contenu, hashlib.sha256).hexdigest()[:10]


def charge_utile(bon: sqlite3.Row) -> str:
    """Contenu du QR : numéro, quantité, produit et signature. Non modifiable sans invalidation."""
    return f"{bon['numero']}|{bon['quantite']}|{bon['produit']}|{signature(bon['numero'], bon['quantite'], bon['produit'])}"


def verifier_charge_utile(charge: str) -> str | None:
    """Rend le numéro de bon si la signature est valide, sinon None."""
    morceaux = charge.split("|")
    if len(morceaux) != 4:
        return None
    numero, quantite, produit, sceau = morceaux
    if not quantite.isdigit():
        return None
    attendu = signature(numero, int(quantite), produit)
    return numero if hmac.compare_digest(attendu, sceau) else None


# ---------------------------------------------------------------------------
# Erreurs métier
# ---------------------------------------------------------------------------
class Refus(Exception):
    """Refus métier : porte un code et un motif lisible par l'utilisateur."""

    def __init__(self, code: str, motif: str, statut: int = 409):
        super().__init__(motif)
        self.code = code
        self.motif = motif
        self.statut = statut


# ---------------------------------------------------------------------------
# Règles métier
# ---------------------------------------------------------------------------
def prochain_numero(base: sqlite3.Connection, prefixe: str, table: str, colonne: str) -> str:
    annee = maintenant().year
    rang = base.execute(f"SELECT COUNT(*) AS n FROM {table}").fetchone()["n"] + 1
    return f"{prefixe}-{annee}-{rang:06d}"


def creer_cotation(base, donnees: dict) -> dict:
    produit = base.execute("SELECT * FROM produits WHERE nom = ?", (donnees.get("produit"),)).fetchone()
    if not produit:
        raise Refus("produit_inconnu", "Produit inconnu.", 400)
    zone = base.execute("SELECT * FROM zones WHERE nom = ?", (donnees.get("zone"),)).fetchone()
    if not zone:
        raise Refus("zone_inconnue", "Zone inconnue.", 400)

    quantite = donnees.get("quantite")
    if not isinstance(quantite, int) or quantite <= 0:
        raise Refus("quantite_invalide", "La quantité doit être un entier positif.", 400)

    option = donnees.get("option", "B")
    if option not in ("A", "B"):
        raise Refus("option_invalide", "Option inconnue : A (enlèvement) ou B (transport PPC).", 400)

    transport = zone["prix_transport"] if option == "B" else 0.0
    total = round(produit["prix_sac"] * quantite + transport, 2)

    numero = prochain_numero(base, "COT", "cotations", "numero")
    emise = maintenant()
    base.execute(
        "INSERT INTO cotations (numero, client, telephone, produit, quantite, zone, option,"
        " prix_unitaire, transport, total, emise_le, valide_jusqua, statut)"
        " VALUES (?,?,?,?,?,?,?,?,?,?,?,?, 'emise')",
        (numero, donnees.get("client", "Client démonstration"), donnees.get("telephone", ""),
         produit["nom"], quantite, zone["nom"], option, produit["prix_sac"], transport,
         total, iso(emise), iso(emise + timedelta(hours=VALIDITE_HEURES))),
    )
    base.commit()
    return lire_cotation(base, numero)


def lire_cotation(base, numero: str) -> dict:
    ligne = base.execute("SELECT * FROM cotations WHERE numero = ?", (numero,)).fetchone()
    if not ligne:
        raise Refus("cotation_inconnue", "Cotation inconnue.", 404)
    cotation = dict(ligne)
    paiement = base.execute("SELECT * FROM paiements WHERE cotation = ?", (numero,)).fetchone()
    cotation["paiement"] = dict(paiement) if paiement else None
    bon = base.execute("SELECT * FROM bons WHERE cotation = ?", (numero,)).fetchone()
    cotation["bon"] = dict(bon) if bon else None
    if cotation["paiement"]:
        cotation["statut"] = "payee"
    elif datetime.fromisoformat(cotation["valide_jusqua"]) < maintenant():
        cotation["statut"] = "perimee"
    return cotation


def payer(base, donnees: dict) -> dict:
    """RG-COT-04 et RG-CMD-01 : la cotation est la référence, le bon naît de l'encaissement."""
    cotation = lire_cotation(base, donnees.get("cotation", ""))
    if cotation["paiement"]:
        raise Refus("deja_payee", f"Cotation déjà payée le {cotation['paiement']['encaisse_le']}."
                                  f" Le bon existe déjà.", 409)
    if datetime.fromisoformat(cotation["valide_jusqua"]) < maintenant():
        raise Refus("cotation_perimee",
                    f"Cotation expirée le {cotation['valide_jusqua'].replace('T', ' à ')}."
                    " Une nouvelle cotation est nécessaire.", 409)

    canal = donnees.get("canal", "")
    if canal not in ("m_pesa", "airtel", "orange", "carte", "virement"):
        raise Refus("canal_invalide", "Canal de paiement inconnu.", 400)

    encaisse = maintenant()
    reference = donnees.get("reference") or f"SIM-{secrets.token_hex(4).upper()}"
    base.execute(
        "INSERT INTO paiements (cotation, canal, reference, montant, encaisse_le) VALUES (?,?,?,?,?)",
        (cotation["numero"], canal, reference, cotation["total"], iso(encaisse)),
    )
    base.execute("UPDATE cotations SET statut = 'payee' WHERE numero = ?", (cotation["numero"],))

    # Le bon naît ici, et nulle part ailleurs.
    numero_bon = prochain_numero_bon(base)
    code = f"{secrets.randbelow(900000) + 100000}"
    base.execute(
        "INSERT INTO bons (code, numero, cotation, client, produit, quantite, zone, emis_le, statut)"
        " VALUES (?,?,?,?,?,?,?,?, 'emis')",
        (code, numero_bon, cotation["numero"], cotation["client"], cotation["produit"],
         cotation["quantite"], cotation["zone"], iso(encaisse)),
    )
    base.commit()
    return lire_bon(base, code)


def prochain_numero_bon(base) -> str:
    rang = base.execute("SELECT COUNT(*) AS n FROM bons").fetchone()["n"] + 1
    return f"BON-{maintenant().year}-{rang:06d}"


def lire_bon(base, code: str) -> dict:
    ligne = base.execute("SELECT * FROM bons WHERE code = ? OR numero = ?", (code, code)).fetchone()
    if not ligne:
        raise Refus("bon_inconnu", "Bon inconnu.", 404)
    bon = dict(ligne)
    bon["signature"] = signature(bon["numero"], bon["quantite"], bon["produit"])
    bon["qr"] = charge_utile(ligne)
    chargement = base.execute("SELECT * FROM chargements WHERE bon = ?", (bon["code"],)).fetchone()
    bon["chargement"] = dict(chargement) if chargement else None
    reception = base.execute("SELECT * FROM receptions WHERE bon = ?", (bon["code"],)).fetchone()
    bon["reception"] = dict(reception) if reception else None
    return bon


def controler(base, donnees: dict) -> dict:
    """Le contrôle au chargement : QR signé ou code de retrait, puis usage unique."""
    saisie = (donnees.get("saisie") or "").strip()
    agent = donnees.get("agent") or "Agent de chargement"

    if "|" in saisie:
        numero = verifier_charge_utile(saisie)
        if numero is None:
            raise Refus("signature_invalide",
                        "Signature du bon invalide : le bon a été modifié. Chargement refusé.", 409)
        ligne = base.execute("SELECT * FROM bons WHERE numero = ?", (numero,)).fetchone()
    else:
        ligne = base.execute("SELECT * FROM bons WHERE code = ?", (saisie,)).fetchone()

    if not ligne:
        raise Refus("bon_inconnu", "Aucun bon ne correspond à cette saisie.", 404)

    bon = dict(ligne)
    if bon["statut"] == "charge":
        chargement = base.execute("SELECT * FROM chargements WHERE bon = ?", (bon["code"],)).fetchone()
        quand = chargement["charge_le"].replace("T", " à ") if chargement else "date inconnue"
        raise Refus("deja_utilise",
                    f"Bon déjà utilisé le {quand}. Un bon est à usage unique : chargement refusé.", 409)
    if bon["statut"] == "livre":
        raise Refus("deja_livre", "Bon déjà livré. Chargement refusé.", 409)

    charge = maintenant()
    base.execute(
        "INSERT INTO chargements (bon, agent, sacs, scelle, charge_le) VALUES (?,?,?,?,?)",
        (bon["code"], agent, bon["quantite"], f"SC-{secrets.token_hex(3).upper()}", iso(charge)),
    )
    base.execute("UPDATE bons SET statut = 'charge' WHERE code = ?", (bon["code"],))
    base.commit()
    return lire_bon(base, bon["code"])


def recevoir(base, donnees: dict) -> dict:
    """Réception prouvée : écart calculé contre la tolérance, litige si dépassement."""
    bon = lire_bon(base, donnees.get("code", ""))
    if bon["statut"] != "charge":
        raise Refus("pas_charge", "Le bon n'a pas été chargé : la réception ne peut pas être enregistrée.", 409)

    sacs = donnees.get("sacs_recus")
    if not isinstance(sacs, int) or sacs < 0:
        raise Refus("sacs_invalides", "Nombre de sacs reçus invalide.", 400)

    ecart = sacs - bon["quantite"]
    scelle_ok = 1 if donnees.get("scelle_ok", True) else 0
    litige = 1 if (abs(ecart) > TOLERANCE_SACS or not scelle_ok) else 0

    base.execute(
        "INSERT INTO receptions (bon, sacs_recus, ecart, etat, scelle_ok, recu_le, litige)"
        " VALUES (?,?,?,?,?,?,?)",
        (bon["code"], sacs, ecart, donnees.get("etat", "conforme"), scelle_ok,
         iso(maintenant()), litige),
    )
    base.execute("UPDATE bons SET statut = 'livre' WHERE code = ?", (bon["code"],))
    base.commit()
    return lire_bon(base, bon["code"])


def tableau_de_bord(base) -> dict:
    compter = lambda table: base.execute(f"SELECT COUNT(*) AS n FROM {table}").fetchone()["n"]  # noqa: E731
    encaisse = base.execute("SELECT COALESCE(SUM(montant), 0) AS s FROM paiements").fetchone()["s"]
    litiges = base.execute("SELECT COUNT(*) AS n FROM receptions WHERE litige = 1").fetchone()["n"]
    return {
        "cotations": compter("cotations"),
        "paiements": compter("paiements"),
        "bons": compter("bons"),
        "chargements": compter("chargements"),
        "livraisons": compter("receptions"),
        "litiges": litiges,
        "encaisse": round(encaisse, 2),
    }


def referentiel(base) -> dict:
    return {
        "produits": [dict(l) for l in base.execute("SELECT * FROM produits").fetchall()],
        "zones": [dict(l) for l in base.execute("SELECT * FROM zones").fetchall()],
        "validite_heures": VALIDITE_HEURES,
        "tolerance_sacs": TOLERANCE_SACS,
    }


# ---------------------------------------------------------------------------
# Serveur HTTP
# ---------------------------------------------------------------------------
ROUTES = [
    ("GET", r"^/api/referentiel$", lambda b, m, d: referentiel(b)),
    ("GET", r"^/api/tableau$", lambda b, m, d: tableau_de_bord(b)),
    ("POST", r"^/api/cotations$", lambda b, m, d: creer_cotation(b, d)),
    ("GET", r"^/api/cotations/([A-Za-z0-9\-]+)$", lambda b, m, d: lire_cotation(b, m.group(1))),
    ("POST", r"^/api/paiements$", lambda b, m, d: payer(b, d)),
    ("GET", r"^/api/bons/([A-Za-z0-9\-]+)$", lambda b, m, d: lire_bon(b, m.group(1))),
    ("POST", r"^/api/controles$", lambda b, m, d: controler(b, d)),
    ("POST", r"^/api/receptions$", lambda b, m, d: recevoir(b, d)),
]
ROUTES_COMPILEES = [(verbe, re.compile(motif), action) for verbe, motif, action in ROUTES]


class Gestionnaire(BaseHTTPRequestHandler):
    serveur_version = "APIX-MVP"

    def log_message(self, format, *args):  # noqa: A002 — silence : la console reste lisible
        pass

    def _envoyer(self, donnees: dict, statut: int = 200):
        corps = json.dumps(donnees, ensure_ascii=False).encode("utf-8")
        self.send_response(statut)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(corps)))
        self.send_header("Cache-Control", "no-store")
        self.end_headers()
        self.wfile.write(corps)

    def _corps(self) -> dict:
        longueur = int(self.headers.get("Content-Length") or 0)
        if not longueur:
            return {}
        try:
            return json.loads(self.rfile.read(longueur).decode("utf-8"))
        except json.JSONDecodeError:
            raise Refus("corps_invalide", "Corps de requête JSON invalide.", 400)

    def _traiter(self, methode: str):
        chemin = urlparse(self.path).path
        for verbe, motif, action in ROUTES_COMPILEES:
            if verbe != methode:
                continue
            correspondance = motif.match(chemin)
            if not correspondance:
                continue
            base = connexion()
            try:
                donnees = self._corps() if methode == "POST" else {}
                self._envoyer(action(base, correspondance, donnees))
            except Refus as refus:
                self._envoyer({"erreur": refus.code, "motif": refus.motif}, refus.statut)
            except Exception as erreur:  # noqa: BLE001 — une erreur ne doit pas tuer le serveur
                self._envoyer({"erreur": "erreur_interne", "motif": str(erreur)}, 500)
            finally:
                base.close()
            return
        self._statique(chemin)

    def _statique(self, chemin: str):
        if chemin in ("/", ""):
            chemin = "/index.html"
        cible = (WEB / chemin.lstrip("/")).resolve()
        if not str(cible).startswith(str(WEB.resolve())) or not cible.is_file():
            self._envoyer({"erreur": "introuvable", "motif": "Ressource inconnue."}, 404)
            return
        type_mime, _ = mimetypes.guess_type(cible.name)
        contenu = cible.read_bytes()
        self.send_response(200)
        self.send_header("Content-Type", (type_mime or "application/octet-stream") + "; charset=utf-8")
        self.send_header("Content-Length", str(len(contenu)))
        self.send_header("Cache-Control", "no-store")
        self.end_headers()
        self.wfile.write(contenu)

    def do_GET(self):        # noqa: N802
        self._traiter("GET")

    def do_POST(self):       # noqa: N802
        self._traiter("POST")


def main() -> int:
    analyseur = argparse.ArgumentParser(description="Moteur du MVP APIX.")
    analyseur.add_argument("--port", type=int, default=8765)
    analyseur.add_argument("--reinitialiser", action="store_true",
                           help="Efface la base de démonstration avant de démarrer.")
    arguments = analyseur.parse_args()

    if arguments.reinitialiser and BASE.exists():
        BASE.unlink()
    amorcer()

    serveur = ThreadingHTTPServer(("127.0.0.1", arguments.port), Gestionnaire)
    print(f"MVP APIX — http://127.0.0.1:{arguments.port}")
    print(f"Base    {BASE.name}  ·  validité cotation {VALIDITE_HEURES} h  ·  tolérance {TOLERANCE_SACS} sacs")
    try:
        serveur.serve_forever()
    except KeyboardInterrupt:
        print("\nArrêt.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
