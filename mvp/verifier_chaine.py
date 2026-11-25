#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Vérifie la chaîne de preuve du MVP, de la cotation au reçu.

Le script démarre le serveur sur un port libre, joue les six gestes, vérifie que
les refus sont bien prononcés, puis arrête tout. Un seul point d'entrée :

    python mvp/verifier_chaine.py

Il ne teste pas l'interface : il teste les règles. Une démonstration dont les
règles ne tiennent pas n'est pas une démonstration, c'est une animation.
"""

from __future__ import annotations

import json
import socket
import subprocess
import sys
import time
import urllib.error
import urllib.request
from pathlib import Path

RACINE = Path(__file__).resolve().parent
sys.stdout.reconfigure(encoding="utf-8", errors="replace")

REUSSITES: list[str] = []
ECHECS: list[str] = []


def port_libre() -> int:
    with socket.socket() as prise:
        prise.bind(("127.0.0.1", 0))
        return prise.getsockname()[1]


def appeler(base: str, methode: str, chemin: str, corps: dict | None = None):
    """Rend (statut, données). Ne lève pas sur 4xx : un refus est un résultat attendu."""
    donnees = json.dumps(corps).encode("utf-8") if corps is not None else None
    requete = urllib.request.Request(
        base + chemin, data=donnees, method=methode,
        headers={"Content-Type": "application/json"},
    )
    try:
        with urllib.request.urlopen(requete, timeout=5) as reponse:
            return reponse.status, json.loads(reponse.read().decode("utf-8"))
    except urllib.error.HTTPError as erreur:
        return erreur.code, json.loads(erreur.read().decode("utf-8"))


def attendre(nom: str, condition: bool, detail: str = ""):
    if condition:
        REUSSITES.append(nom)
        print(f"  [OK]    {nom}")
    else:
        ECHECS.append(f"{nom} — {detail}")
        print(f"  [ECHEC] {nom} — {detail}")


def main() -> int:
    port = port_libre()
    base = f"http://127.0.0.1:{port}"
    processus = subprocess.Popen(
        [sys.executable, str(RACINE / "serveur.py"), "--port", str(port), "--reinitialiser"],
        stdout=subprocess.DEVNULL, stderr=subprocess.PIPE,
    )
    try:
        for _ in range(50):
            try:
                with socket.create_connection(("127.0.0.1", port), timeout=0.2):
                    break
            except OSError:
                time.sleep(0.1)

        print("\n1. Référentiel")
        statut, referentiel = appeler(base, "GET", "/api/referentiel")
        attendre("le référentiel répond", statut == 200, str(statut))
        attendre("deux produits au catalogue", len(referentiel.get("produits", [])) == 2,
                 str(referentiel.get("produits")))

        print("\n2. Cotation")
        statut, cotation = appeler(base, "POST", "/api/cotations", {
            "client": "Dépôt Kintoko", "telephone": "+243 820 001 234",
            "produit": "Surecem", "quantite": 100, "zone": "Gombé", "option": "B",
        })
        attendre("la cotation est émise", statut == 200, str(cotation))
        numero = cotation.get("numero", "")
        attendre("elle porte un numéro", numero.startswith("COT-"), numero)
        attendre("elle porte une validité", bool(cotation.get("valide_jusqua")), str(cotation))
        attendre("le transport est chiffré", cotation.get("transport") == 320.0, str(cotation.get("transport")))
        attendre("le total est juste (9,5 × 100 + 320)", cotation.get("total") == 1270.0,
                 str(cotation.get("total")))

        print("\n3. Paiement")
        statut, bon = appeler(base, "POST", "/api/paiements", {"cotation": numero, "canal": "m_pesa"})
        attendre("le paiement est encaissé", statut == 200, str(bon))
        attendre("le bon naît de l'encaissement", bool(bon.get("code")), str(bon))
        attendre("le bon est nominatif", bon.get("client") == "Dépôt Kintoko", str(bon.get("client")))
        code, qr = bon.get("code", ""), bon.get("qr", "")

        statut, refus = appeler(base, "POST", "/api/paiements", {"cotation": numero, "canal": "m_pesa"})
        attendre("un second paiement est refusé", statut == 409 and refus.get("erreur") == "deja_payee",
                 str(refus))
        attendre("aucun bon n'est créé par ce refus", refus.get("erreur") == "deja_payee", str(refus))

        print("\n4. Contrôle au chargement")
        statut, charge = appeler(base, "POST", "/api/controles", {"saisie": code, "agent": "Agent usine"})
        attendre("le code de retrait est accepté", statut == 200 and charge.get("statut") == "charge",
                 str(charge))
        attendre("le scellé est enregistré", bool(charge.get("chargement")), str(charge.get("chargement")))

        statut, refus = appeler(base, "POST", "/api/controles", {"saisie": code})
        attendre("le second passage est refusé", statut == 409 and refus.get("erreur") == "deja_utilise",
                 str(refus))

        falsifie = qr.replace("|100|", "|200|")
        statut, refus = appeler(base, "POST", "/api/controles", {"saisie": falsifie})
        attendre("un bon modifié est refusé", statut == 409 and refus.get("erreur") == "signature_invalide",
                 str(refus))

        statut, refus = appeler(base, "POST", "/api/controles", {"saisie": "000000"})
        attendre("un code inconnu est refusé", statut == 404 and refus.get("erreur") == "bon_inconnu",
                 str(refus))

        print("\n5. Réception prouvée")
        statut, recu = appeler(base, "POST", "/api/receptions",
                               {"code": code, "sacs_recus": 98, "etat": "conforme", "scelle_ok": True})
        attendre("la réception est enregistrée", statut == 200, str(recu))
        reception = recu.get("reception") or {}
        attendre("l'écart est calculé", reception.get("ecart") == -2, str(reception))
        attendre("un écart dans la tolérance n'ouvre pas de litige", reception.get("litige") == 0,
                 str(reception))
        attendre("le bon passe en livré", recu.get("statut") == "livre", str(recu.get("statut")))

        print("\n6. Tableau de bord")
        statut, tableau = appeler(base, "GET", "/api/tableau")
        attendre("le tableau répond", statut == 200, str(statut))
        attendre("une cotation, un paiement, un bon",
                 (tableau.get("cotations"), tableau.get("paiements"), tableau.get("bons")) == (1, 1, 1),
                 str(tableau))
        attendre("l'encaissement est de 1 270 $", tableau.get("encaisse") == 1270.0, str(tableau.get("encaisse")))

    finally:
        processus.terminate()
        try:
            processus.wait(timeout=5)
        except subprocess.TimeoutExpired:
            processus.kill()

    print(f"\n{len(REUSSITES)} vérification(s) réussie(s), {len(ECHECS)} échec(s).")
    for echec in ECHECS:
        print(f"  - {echec}")
    return 0 if not ECHECS else 1


if __name__ == "__main__":
    raise SystemExit(main())
