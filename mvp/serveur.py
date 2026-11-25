#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Moteur du MVP APIX — les sept jalons du document 05, sans dépendance externe.

Bibliothèque standard uniquement : un fichier SQLite, un serveur HTTP, les règles
du dossier. Aucun serveur de messages, aucune base distante, aucun modèle de langue.

Jalons couverts (document 05, §2.2) :

    J1  Compte et vérification d'identité   — compte, pièces, palier, plafond
    J2  Cotation certifiée                  — prix du profil, numéro, validité
    J3  Paiement encaissé                   — référence à la cotation, contrôle du plafond
    J4  Bon de commande émis                — nominatif, usage unique, QR signé ou code
    J5  Chargement et transport             — contrôle, poids, sacs, scellé, course
    J6  Livraison prouvée                   — réception, écart, dossier, litige instruit
    J7  Reçu et historique                  — reçu vérifiable, historique du client

Règles appliquées (annexe A1) :
    RG-COT-01  aucun prix avant vérification de l'identité
    RG-COT-04  la cotation est la référence du paiement
    RG-COT-05  une cotation expirée n'est pas payable
    RG-CMD-01  le bon naît de l'encaissement, jamais d'une demande
    RG-CMD-05  le bon est à usage unique : un second contrôle est refusé
    RG-CHG-02  le bon est contrôlé par son QR signé ou par son code de retrait
    RG-PAY-14  le plafond du palier s'applique au total de la cotation
    RG-PAY-16  le fractionnement pour passer sous un plafond est refusé
    RG-POD-04  l'écart hors tolérance ouvre un litige
    RG-LIT-02  le litige est instruit : montant retenu, montant libéré

Usage :
    python mvp/serveur.py [--port 8765] [--reinitialiser]
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

SECRET = b"apix-mvp-demonstration"
VALIDITE_HEURES = 48
TOLERANCE_SACS = 2
CATALOGUE = "apix-mvp-v1"

PALIERS = {
    "non_verifie": {"libelle": "Non vérifié", "plafond": 0.0},
    "verifie": {"libelle": "Client vérifié", "plafond": 2500.0},
    "entreprise": {"libelle": "Entreprise vérifiée", "plafond": 10000.0},
}


# ---------------------------------------------------------------------------
# Utilitaires
# ---------------------------------------------------------------------------
def maintenant() -> datetime:
    return datetime.now().replace(microsecond=0)


def iso(moment: datetime) -> str:
    return moment.isoformat(timespec="seconds")


def affichable(valeur: str) -> str:
    return valeur.replace("T", " à ") if valeur else ""


def connexion() -> sqlite3.Connection:
    base = sqlite3.connect(BASE)
    base.row_factory = sqlite3.Row
    base.execute("PRAGMA foreign_keys = ON")
    return base


SCHEMA = """
CREATE TABLE IF NOT EXISTS clients (
    id         INTEGER PRIMARY KEY AUTOINCREMENT,
    nom        TEXT NOT NULL,
    telephone  TEXT NOT NULL,
    type       TEXT NOT NULL,
    statut     TEXT NOT NULL,
    palier     TEXT NOT NULL,
    cree_le    TEXT NOT NULL,
    verifie_le TEXT
);
CREATE TABLE IF NOT EXISTS pieces (
    id         INTEGER PRIMARY KEY AUTOINCREMENT,
    client     INTEGER NOT NULL REFERENCES clients(id),
    type_piece TEXT NOT NULL,
    recto      INTEGER NOT NULL,
    verso      INTEGER NOT NULL,
    depose_le  TEXT NOT NULL
);
CREATE TABLE IF NOT EXISTS produits (
    id INTEGER PRIMARY KEY, nom TEXT NOT NULL, prix_sac REAL NOT NULL
);
CREATE TABLE IF NOT EXISTS zones (
    id INTEGER PRIMARY KEY, nom TEXT NOT NULL, prix_transport REAL NOT NULL
);
CREATE TABLE IF NOT EXISTS cotations (
    numero TEXT PRIMARY KEY,
    client_id INTEGER NOT NULL REFERENCES clients(id),
    client TEXT NOT NULL, telephone TEXT NOT NULL,
    produit TEXT NOT NULL, quantite INTEGER NOT NULL, zone TEXT NOT NULL,
    option TEXT NOT NULL, prix_unitaire REAL NOT NULL,
    transport REAL NOT NULL, total REAL NOT NULL,
    emise_le TEXT NOT NULL, valide_jusqua TEXT NOT NULL,
    statut TEXT NOT NULL
);
CREATE TABLE IF NOT EXISTS paiements (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    cotation TEXT NOT NULL REFERENCES cotations(numero),
    canal TEXT NOT NULL, reference TEXT NOT NULL,
    montant REAL NOT NULL, encaisse_le TEXT NOT NULL
);
CREATE TABLE IF NOT EXISTS bons (
    code TEXT PRIMARY KEY, numero TEXT NOT NULL UNIQUE,
    cotation TEXT NOT NULL REFERENCES cotations(numero),
    client TEXT NOT NULL, produit TEXT NOT NULL, quantite INTEGER NOT NULL,
    zone TEXT NOT NULL, emis_le TEXT NOT NULL, statut TEXT NOT NULL
);
CREATE TABLE IF NOT EXISTS chargements (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    bon TEXT NOT NULL REFERENCES bons(code), agent TEXT NOT NULL,
    sacs INTEGER NOT NULL, poids_kg REAL NOT NULL, scelle TEXT NOT NULL,
    transporteur TEXT NOT NULL, plaque TEXT NOT NULL, charge_le TEXT NOT NULL
);
CREATE TABLE IF NOT EXISTS receptions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    bon TEXT NOT NULL REFERENCES bons(code),
    sacs_recus INTEGER NOT NULL, ecart INTEGER NOT NULL, poids_recu_kg REAL NOT NULL,
    etat TEXT NOT NULL, scelle_ok INTEGER NOT NULL, recu_le TEXT NOT NULL
);
CREATE TABLE IF NOT EXISTS litiges (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    bon TEXT NOT NULL REFERENCES bons(code),
    motif TEXT NOT NULL, ecart INTEGER NOT NULL, ouvert_le TEXT NOT NULL,
    statut TEXT NOT NULL, retenu REAL NOT NULL DEFAULT 0,
    libere REAL NOT NULL DEFAULT 0, instruit_le TEXT, decision TEXT
);
"""


def amorcer() -> None:
    base = connexion()
    base.executescript(SCHEMA)
    if base.execute("SELECT COUNT(*) AS n FROM produits").fetchone()["n"] == 0:
        base.executemany("INSERT INTO produits (nom, prix_sac) VALUES (?, ?)",
                         [("Surecem", 9.5), ("Surecast", 8.0)])
        base.executemany("INSERT INTO zones (nom, prix_transport) VALUES (?, ?)",
                         [("Gombé", 320.0), ("Limete", 280.0), ("Ngaliema", 360.0), ("Basoko", 340.0)])
        base.commit()
    base.close()


# ---------------------------------------------------------------------------
# Signature
# ---------------------------------------------------------------------------
def signature(numero: str, quantite: int, produit: str) -> str:
    contenu = f"{numero}|{quantite}|{produit}".encode("utf-8")
    return hmac.new(SECRET, contenu, hashlib.sha256).hexdigest()[:10]


def charge_utile(bon) -> str:
    return (f"{bon['numero']}|{bon['quantite']}|{bon['produit']}|"
            f"{signature(bon['numero'], bon['quantite'], bon['produit'])}")


def verifier_charge_utile(charge: str) -> str | None:
    morceaux = charge.split("|")
    if len(morceaux) != 4:
        return None
    numero, quantite, produit, sceau = morceaux
    if not quantite.isdigit():
        return None
    attendu = signature(numero, int(quantite), produit)
    return numero if hmac.compare_digest(attendu, sceau) else None


def empreinte_recu(ligne) -> str:
    contenu = f"RECU|{ligne['numero']}|{ligne['quantite']}|{ligne['produit']}|{ligne['emis_le']}".encode("utf-8")
    return hmac.new(SECRET, contenu, hashlib.sha256).hexdigest()[:16].upper()


# ---------------------------------------------------------------------------
# Erreurs métier
# ---------------------------------------------------------------------------
class Refus(Exception):
    def __init__(self, code: str, motif: str, statut: int = 409):
        super().__init__(motif)
        self.code, self.motif, self.statut = code, motif, statut


def exiger(condition: bool, code: str, motif: str, statut: int = 400) -> None:
    if not condition:
        raise Refus(code, motif, statut)


# ---------------------------------------------------------------------------
# J1 — compte et vérification d'identité
# ---------------------------------------------------------------------------
def creer_client(base, d: dict) -> dict:
    nom = (d.get("nom") or "").strip()
    telephone = (d.get("telephone") or "").strip()
    type_client = d.get("type") or "particulier"
    exiger(bool(nom), "nom_manquant", "Le nom est obligatoire.")
    exiger(bool(telephone), "telephone_manquant", "Le numéro de téléphone est obligatoire.")
    exiger(type_client in ("particulier", "depot", "entreprise"), "type_inconnu",
           "Type de compte inconnu : particulier, depot ou entreprise.")
    curseur = base.execute(
        "INSERT INTO clients (nom, telephone, type, statut, palier, cree_le)"
        " VALUES (?,?,?, 'en_attente', 'non_verifie', ?)",
        (nom, telephone, type_client, iso(maintenant())),
    )
    base.commit()
    return lire_client(base, curseur.lastrowid)


def depoter_pieces(base, client_id: int, d: dict) -> dict:
    client = lire_client(base, client_id)
    type_piece = d.get("type_piece") or "carte_identite"
    recto = bool(d.get("recto", True))
    verso = bool(d.get("verso", True))
    exiger(recto, "recto_manquant", "Le recto de la pièce est obligatoire.")
    exiger(verso, "verso_manquant", "Le verso de la pièce est obligatoire.")

    base.execute("INSERT INTO pieces (client, type_piece, recto, verso, depose_le) VALUES (?,?,?,?,?)",
                 (client_id, type_piece, int(recto), int(verso), iso(maintenant())))
    # La vérification est simulée : un dépôt complet suffit à monter de palier.
    palier = "entreprise" if client["type"] in ("depot", "entreprise") else "verifie"
    base.execute("UPDATE clients SET statut = 'verifie', palier = ?, verifie_le = ? WHERE id = ?",
                 (palier, iso(maintenant()), client_id))
    base.commit()
    return lire_client(base, client_id)


def lire_client(base, client_id: int) -> dict:
    ligne = base.execute("SELECT * FROM clients WHERE id = ?", (client_id,)).fetchone()
    exiger(ligne is not None, "client_inconnu", "Client inconnu.", 404)
    client = dict(ligne)
    client["plafond"] = PALIERS[client["palier"]]["plafond"]
    client["palier_libelle"] = PALIERS[client["palier"]]["libelle"]
    client["pieces"] = [dict(p) for p in base.execute(
        "SELECT type_piece, recto, verso, depose_le FROM pieces WHERE client = ?", (client_id,)).fetchall()]
    return client


def lister_clients(base) -> dict:
    clients = []
    for ligne in base.execute("SELECT * FROM clients ORDER BY id DESC LIMIT 50").fetchall():
        client = dict(ligne)
        client["plafond"] = PALIERS[client["palier"]]["plafond"]
        client["palier_libelle"] = PALIERS[client["palier"]]["libelle"]
        clients.append(client)
    return {"clients": clients}


# ---------------------------------------------------------------------------
# J2 — cotation certifiée
# ---------------------------------------------------------------------------
def prochain_numero(base, prefixe: str, table: str) -> str:
    rang = base.execute(f"SELECT COUNT(*) AS n FROM {table}").fetchone()["n"] + 1
    return f"{prefixe}-{maintenant().year}-{rang:06d}"


def creer_cotation(base, d: dict) -> dict:
    client = lire_client(base, int(d.get("client_id") or 0))

    # RG-COT-01 : aucun prix avant vérification de l'identité.
    exiger(client["statut"] == "verifie", "identite_non_verifiee",
           "Aucun prix n'est produit avant vérification de l'identité. Déposez vos pièces.", 403)

    produit = base.execute("SELECT * FROM produits WHERE nom = ?", (d.get("produit"),)).fetchone()
    exiger(produit is not None, "produit_inconnu", "Produit inconnu.")
    zone = base.execute("SELECT * FROM zones WHERE nom = ?", (d.get("zone"),)).fetchone()
    exiger(zone is not None, "zone_inconnue", "Zone inconnue.")

    quantite = d.get("quantite")
    exiger(isinstance(quantite, int) and quantite > 0, "quantite_invalide",
           "La quantité doit être un entier positif.")
    option = d.get("option", "B")
    exiger(option in ("A", "B"), "option_invalide", "Option inconnue : A ou B.")

    transport = zone["prix_transport"] if option == "B" else 0.0
    total = round(produit["prix_sac"] * quantite + transport, 2)

    # RG-PAY-14 / RG-PAY-16 : plafond du palier, sans fractionnement.
    exiger(total <= client["plafond"], "plafond_depasse",
           f"Total {total:.2f} $ au-delà du plafond de votre palier ({client['plafond']:.2f} $)."
           " Le fractionnement n'est pas autorisé : réglez par virement ou réduisez la commande.", 409)

    numero = prochain_numero(base, "COT", "cotations")
    emise = maintenant()
    base.execute(
        "INSERT INTO cotations (numero, client_id, client, telephone, produit, quantite, zone, option,"
        " prix_unitaire, transport, total, emise_le, valide_jusqua, statut)"
        " VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?, 'emise')",
        (numero, client["id"], client["nom"], client["telephone"], produit["nom"], quantite,
         zone["nom"], option, produit["prix_sac"], transport, total, iso(emise),
         iso(emise + timedelta(hours=VALIDITE_HEURES))),
    )
    base.commit()
    return lire_cotation(base, numero)


def lire_cotation(base, numero: str) -> dict:
    ligne = base.execute("SELECT * FROM cotations WHERE numero = ?", (numero,)).fetchone()
    exiger(ligne is not None, "cotation_inconnue", "Cotation inconnue.", 404)
    cotation = dict(ligne)
    paiement = base.execute("SELECT * FROM paiements WHERE cotation = ?", (numero,)).fetchone()
    cotation["paiement"] = dict(paiement) if paiement else None
    bon = base.execute("SELECT * FROM bons WHERE cotation = ?", (numero,)).fetchone()
    cotation["bon"] = dict(bon) if bon else None
    if cotation["paiement"]:
        cotation["statut"] = "payee"
    elif datetime.fromisoformat(cotation["valide_jusqua"]) < maintenant():
        cotation["statut"] = "perimee"
    cotation["expire_dans_s"] = max(
        0, int((datetime.fromisoformat(cotation["valide_jusqua"]) - maintenant()).total_seconds()))
    return cotation


def historique_client(base, client_id: int) -> dict:
    lignes = base.execute("SELECT numero FROM cotations WHERE client_id = ? ORDER BY emise_le DESC",
                          (client_id,)).fetchall()
    return {"cotations": [lire_cotation(base, l["numero"]) for l in lignes]}


# ---------------------------------------------------------------------------
# J3 — paiement
# ---------------------------------------------------------------------------
CANAUX = ("m_pesa", "airtel", "orange", "carte", "virement")


def payer(base, d: dict) -> dict:
    cotation = lire_cotation(base, d.get("cotation", ""))
    exiger(cotation["paiement"] is None, "deja_payee",
           f"Cotation déjà payée le {affichable(cotation['paiement']['encaisse_le']) if cotation['paiement'] else ''}."
           " Le bon existe déjà.", 409)
    exiger(datetime.fromisoformat(cotation["valide_jusqua"]) >= maintenant(), "cotation_perimee",
           f"Cotation expirée le {affichable(cotation['valide_jusqua'])}."
           " Une nouvelle cotation est nécessaire.")
    canal = d.get("canal", "")
    exiger(canal in CANAUX, "canal_invalide", "Canal de paiement inconnu.")

    encaisse = maintenant()
    reference = d.get("reference") or f"SIM-{secrets.token_hex(4).upper()}"
    base.execute("INSERT INTO paiements (cotation, canal, reference, montant, encaisse_le) VALUES (?,?,?,?,?)",
                 (cotation["numero"], canal, reference, cotation["total"], iso(encaisse)))
    base.execute("UPDATE cotations SET statut = 'payee' WHERE numero = ?", (cotation["numero"],))

    code = f"{secrets.randbelow(900000) + 100000}"
    base.execute(
        "INSERT INTO bons (code, numero, cotation, client, produit, quantite, zone, emis_le, statut)"
        " VALUES (?,?,?,?,?,?,?,?, 'emis')",
        (code, prochain_numero(base, "BON", "bons"), cotation["numero"], cotation["client"],
         cotation["produit"], cotation["quantite"], cotation["zone"], iso(encaisse)),
    )
    base.commit()
    return lire_bon(base, code)


# ---------------------------------------------------------------------------
# J4 et J5 — bon, contrôle, chargement
# ---------------------------------------------------------------------------
def lire_bon(base, code: str) -> dict:
    ligne = base.execute("SELECT * FROM bons WHERE code = ? OR numero = ?", (code, code)).fetchone()
    exiger(ligne is not None, "bon_inconnu", "Bon inconnu.", 404)
    bon = dict(ligne)
    bon["signature"] = signature(bon["numero"], bon["quantite"], bon["produit"])
    bon["qr"] = charge_utile(ligne)
    chargement = base.execute("SELECT * FROM chargements WHERE bon = ?", (bon["code"],)).fetchone()
    bon["chargement"] = dict(chargement) if chargement else None
    reception = base.execute("SELECT * FROM receptions WHERE bon = ?", (bon["code"],)).fetchone()
    bon["reception"] = dict(reception) if reception else None
    litige = base.execute("SELECT * FROM litiges WHERE bon = ? ORDER BY id DESC", (bon["code"],)).fetchone()
    bon["litige"] = dict(litige) if litige else None
    return bon


def controler(base, d: dict) -> dict:
    saisie = (d.get("saisie") or "").strip()
    agent = d.get("agent") or "Agent de chargement"
    transporteur = (d.get("transporteur") or "PPC Logistique").strip()
    plaque = (d.get("plaque") or "KN 0001 AB").strip()

    if "|" in saisie:
        numero = verifier_charge_utile(saisie)
        exiger(numero is not None, "signature_invalide",
               "Signature du bon invalide : le bon a été modifié. Chargement refusé.", 409)
        ligne = base.execute("SELECT * FROM bons WHERE numero = ?", (numero,)).fetchone()
    else:
        ligne = base.execute("SELECT * FROM bons WHERE code = ?", (saisie,)).fetchone()

    exiger(ligne is not None, "bon_inconnu", "Aucun bon ne correspond à cette saisie.", 404)
    bon = dict(ligne)

    if bon["statut"] == "charge":
        chargement = base.execute("SELECT * FROM chargements WHERE bon = ?", (bon["code"],)).fetchone()
        exiger(False, "deja_utilise",
               f"Bon déjà utilisé le {affichable(chargement['charge_le']) if chargement else 'date inconnue'}."
               " Un bon est à usage unique : chargement refusé.", 409)
    exiger(bon["statut"] == "emis", "statut_invalide",
           f"Bon au statut {bon['statut']} : chargement refusé.", 409)

    poids = d.get("poids_kg")
    exiger(isinstance(poids, (int, float)) and poids > 0, "poids_invalide",
           "Le poids pesé est obligatoire : il entre dans le dossier de preuve.")
    sacs = d.get("sacs") or bon["quantite"]
    exiger(isinstance(sacs, int) and sacs > 0, "sacs_invalides", "Nombre de sacs chargés invalide.")

    base.execute(
        "INSERT INTO chargements (bon, agent, sacs, poids_kg, scelle, transporteur, plaque, charge_le)"
        " VALUES (?,?,?,?,?,?,?,?)",
        (bon["code"], agent, sacs, float(poids), f"SC-{secrets.token_hex(3).upper()}",
         transporteur, plaque, iso(maintenant())),
    )
    base.execute("UPDATE bons SET statut = 'charge' WHERE code = ?", (bon["code"],))
    base.commit()
    return lire_bon(base, bon["code"])


# ---------------------------------------------------------------------------
# J6 — livraison prouvée et litige
# ---------------------------------------------------------------------------
def recevoir(base, d: dict) -> dict:
    bon = lire_bon(base, d.get("code", ""))
    exiger(bon["statut"] == "charge", "pas_charge",
           "Le bon n'a pas été chargé : la réception ne peut pas être enregistrée.")
    sacs = d.get("sacs_recus")
    exiger(isinstance(sacs, int) and sacs >= 0, "sacs_invalides", "Nombre de sacs reçus invalide.")
    poids = d.get("poids_recu_kg")
    exiger(isinstance(poids, (int, float)) and poids >= 0, "poids_invalide",
           "Le poids reçu est obligatoire.")

    ecart = sacs - bon["quantite"]
    scelle_ok = 1 if d.get("scelle_ok", True) else 0
    base.execute(
        "INSERT INTO receptions (bon, sacs_recus, ecart, poids_recu_kg, etat, scelle_ok, recu_le)"
        " VALUES (?,?,?,?,?,?,?)",
        (bon["code"], sacs, ecart, float(poids), d.get("etat", "conforme"), scelle_ok, iso(maintenant())),
    )

    if abs(ecart) > TOLERANCE_SACS or not scelle_ok:
        motif = "scelle_rompu" if not scelle_ok else ("manquant" if ecart < 0 else "excedent")
        base.execute("INSERT INTO litiges (bon, motif, ecart, ouvert_le, statut) VALUES (?,?,?,?, 'ouvert')",
                     (bon["code"], motif, ecart, iso(maintenant())))

    base.execute("UPDATE bons SET statut = 'livre' WHERE code = ?", (bon["code"],))
    base.commit()
    return lire_bon(base, bon["code"])


def dossier_preuve(base, code: str) -> dict:
    bon = lire_bon(base, code)
    exiger(bon["chargement"] is not None, "pas_de_preuve",
           "Aucun chargement enregistré : le dossier de preuve est vide.", 409)
    cotation = lire_cotation(base, bon["cotation"])
    etapes = [
        {"etape": "Cotation", "quand": affichable(cotation["emise_le"]),
         "detail": f"{cotation['numero']} · {cotation['total']:.2f} $ · validité {VALIDITE_HEURES} h"},
        {"etape": "Paiement", "quand": affichable(cotation["paiement"]["encaisse_le"]) if cotation["paiement"] else "",
         "detail": f"{cotation['paiement']['canal']} · réf. {cotation['paiement']['reference']}"
                   if cotation["paiement"] else ""},
        {"etape": "Bon émis", "quand": affichable(bon["emis_le"]), "detail": bon["numero"]},
        {"etape": "Chargement", "quand": affichable(bon["chargement"]["charge_le"]),
         "detail": f"{bon['chargement']['sacs']} sacs · {bon['chargement']['poids_kg']} kg · "
                   f"scellé {bon['chargement']['scelle']} · {bon['chargement']['transporteur']} "
                   f"({bon['chargement']['plaque']})"},
    ]
    if bon["reception"]:
        etapes.append({"etape": "Réception", "quand": affichable(bon["reception"]["recu_le"]),
                       "detail": f"{bon['reception']['sacs_recus']} sacs · "
                                 f"{bon['reception']['poids_recu_kg']} kg · écart "
                                 f"{bon['reception']['ecart']:+d} sac · scellé "
                                 f"{'intact' if bon['reception']['scelle_ok'] else 'rompu'}"})
    if bon["litige"]:
        etapes.append({"etape": "Litige", "quand": affichable(bon["litige"]["ouvert_le"]),
                       "detail": f"{bon['litige']['motif']} · {bon['litige']['statut']}"})
    return {"bon": bon, "etapes": etapes}


def recu_de(base, code: str) -> dict:
    bon = lire_bon(base, code)
    exiger(bon["statut"] == "livre", "pas_livre", "Le reçu n'existe qu'après la livraison.", 409)
    ligne = base.execute("SELECT * FROM bons WHERE code = ?", (code,)).fetchone()
    return {
        "numero": f"RECU-{bon['numero'].split('-')[-1]}",
        "bon": bon["numero"],
        "client": bon["client"],
        "produit": bon["produit"],
        "quantite": bon["quantite"],
        "zone": bon["zone"],
        "livre_le": affichable(bon["reception"]["recu_le"]) if bon["reception"] else "",
        "empreinte": empreinte_recu(ligne),
    }


def ouvrir_litige(base, d: dict) -> dict:
    bon = lire_bon(base, d.get("code", ""))
    exiger(bon["litige"] is None, "litige_existant", "Un litige est déjà ouvert sur ce bon.")
    motif = d.get("motif") or "contestation_client"
    base.execute("INSERT INTO litiges (bon, motif, ecart, ouvert_le, statut) VALUES (?,?,?,?, 'ouvert')",
                 (bon["code"], motif, 0, iso(maintenant())))
    base.commit()
    return lire_bon(base, bon["code"])


def instruire_litige(base, litige_id: int, d: dict) -> dict:
    ligne = base.execute("SELECT * FROM litiges WHERE id = ?", (litige_id,)).fetchone()
    exiger(ligne is not None, "litige_inconnu", "Litige inconnu.", 404)
    exiger(ligne["statut"] == "ouvert", "litige_instruit", "Ce litige est déjà instruit.")
    retenu = float(d.get("retenu") or 0)
    libere = float(d.get("libere") or 0)
    exiger(retenu >= 0 and libere >= 0, "montant_invalide", "Les montants doivent être positifs.")
    decision = (d.get("decision") or "").strip()
    exiger(bool(decision), "decision_manquante", "Une décision motivée est obligatoire.")
    base.execute("UPDATE litiges SET statut = 'instruit', retenu = ?, libere = ?, instruit_le = ?,"
                 " decision = ? WHERE id = ?", (retenu, libere, iso(maintenant()), decision, litige_id))
    base.commit()
    return {"litige": dict(base.execute("SELECT * FROM litiges WHERE id = ?", (litige_id,)).fetchone())}


# ---------------------------------------------------------------------------
# Pilotage et référentiel
# ---------------------------------------------------------------------------
def tableau_de_bord(base) -> dict:
    def compter(table: str) -> int:
        return base.execute(f"SELECT COUNT(*) AS n FROM {table}").fetchone()["n"]

    return {
        "clients": compter("clients"),
        "clients_verifies": base.execute(
            "SELECT COUNT(*) AS n FROM clients WHERE statut = 'verifie'").fetchone()["n"],
        "cotations": compter("cotations"),
        "paiements": compter("paiements"),
        "bons": compter("bons"),
        "chargements": compter("chargements"),
        "livraisons": compter("receptions"),
        "litiges_ouverts": base.execute(
            "SELECT COUNT(*) AS n FROM litiges WHERE statut = 'ouvert'").fetchone()["n"],
        "encaisse": round(base.execute(
            "SELECT COALESCE(SUM(montant), 0) AS s FROM paiements").fetchone()["s"], 2),
    }


def backoffice(base) -> dict:
    return {
        "cotations": [dict(l) for l in base.execute(
            "SELECT numero, client, total, statut, emise_le FROM cotations"
            " ORDER BY emise_le DESC LIMIT 20")],
        "bons": [dict(l) for l in base.execute(
            "SELECT code, numero, client, quantite, statut, emis_le FROM bons"
            " ORDER BY emis_le DESC LIMIT 20")],
        "litiges": [dict(l) for l in base.execute(
            "SELECT l.*, b.numero AS bon_numero, b.client FROM litiges l"
            " JOIN bons b ON b.code = l.bon ORDER BY l.id DESC LIMIT 20")],
    }


def referentiel(base) -> dict:
    return {
        "produits": [dict(l) for l in base.execute("SELECT * FROM produits").fetchall()],
        "zones": [dict(l) for l in base.execute("SELECT * FROM zones").fetchall()],
        "paliers": PALIERS,
        "canaux": list(CANAUX),
        "validite_heures": VALIDITE_HEURES,
        "tolerance_sacs": TOLERANCE_SACS,
        "catalogue": CATALOGUE,
    }


# ---------------------------------------------------------------------------
# Routes
# ---------------------------------------------------------------------------
ROUTES = [
    ("GET", r"^/api/referentiel$", lambda b, m, d: referentiel(b)),
    ("GET", r"^/api/tableau$", lambda b, m, d: tableau_de_bord(b)),
    ("GET", r"^/api/backoffice$", lambda b, m, d: backoffice(b)),
    ("GET", r"^/api/clients$", lambda b, m, d: lister_clients(b)),
    ("POST", r"^/api/clients$", lambda b, m, d: creer_client(b, d)),
    ("GET", r"^/api/clients/(\d+)$", lambda b, m, d: lire_client(b, int(m.group(1)))),
    ("POST", r"^/api/clients/(\d+)/pieces$", lambda b, m, d: depoter_pieces(b, int(m.group(1)), d)),
    ("GET", r"^/api/clients/(\d+)/historique$", lambda b, m, d: historique_client(b, int(m.group(1)))),
    ("POST", r"^/api/cotations$", lambda b, m, d: creer_cotation(b, d)),
    ("GET", r"^/api/cotations/([A-Za-z0-9\-]+)$", lambda b, m, d: lire_cotation(b, m.group(1))),
    ("POST", r"^/api/paiements$", lambda b, m, d: payer(b, d)),
    ("GET", r"^/api/bons/([A-Za-z0-9\-]+)$", lambda b, m, d: lire_bon(b, m.group(1))),
    ("POST", r"^/api/controles$", lambda b, m, d: controler(b, d)),
    ("POST", r"^/api/receptions$", lambda b, m, d: recevoir(b, d)),
    ("GET", r"^/api/preuves/([A-Za-z0-9\-]+)$", lambda b, m, d: dossier_preuve(b, m.group(1))),
    ("GET", r"^/api/recus/([A-Za-z0-9\-]+)$", lambda b, m, d: recu_de(b, m.group(1))),
    ("POST", r"^/api/litiges$", lambda b, m, d: ouvrir_litige(b, d)),
    ("POST", r"^/api/litiges/(\d+)/instruction$", lambda b, m, d: instruire_litige(b, int(m.group(1)), d)),
]
ROUTES_COMPILEES = [(verbe, re.compile(motif), action) for verbe, motif, action in ROUTES]


class Gestionnaire(BaseHTTPRequestHandler):
    serveur_version = "APIX-MVP"

    def log_message(self, format, *args):  # noqa: A002
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
            except Exception as erreur:  # noqa: BLE001
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
    analyseur.add_argument("--reinitialiser", action="store_true")
    arguments = analyseur.parse_args()

    if arguments.reinitialiser and BASE.exists():
        BASE.unlink()
    amorcer()

    serveur = ThreadingHTTPServer(("127.0.0.1", arguments.port), Gestionnaire)
    print(f"MVP APIX — http://127.0.0.1:{arguments.port}")
    print(f"Base {BASE.name} · validité {VALIDITE_HEURES} h · tolérance {TOLERANCE_SACS} sacs · {CATALOGUE}")
    try:
        serveur.serve_forever()
    except KeyboardInterrupt:
        print("\nArrêt.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
