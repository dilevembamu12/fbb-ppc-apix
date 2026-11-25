#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Épreuve de la chaîne complète du MVP, jalon par jalon.

    python mvp/verifier_chaine.py

Le script démarre le serveur sur un port libre, joue les sept jalons du document 05,
vérifie que chaque refus est bien prononcé, puis arrête tout. Il ne teste pas
l'interface : il teste les règles.
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
    donnees = json.dumps(corps).encode("utf-8") if corps is not None else None
    requete = urllib.request.Request(base + chemin, data=donnees, method=methode,
                                     headers={"Content-Type": "application/json"})
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
        stdout=subprocess.DEVNULL, stderr=subprocess.PIPE)
    try:
        for _ in range(50):
            try:
                with socket.create_connection(("127.0.0.1", port), timeout=0.2):
                    break
            except OSError:
                time.sleep(0.1)

        print("\nJ1 — Compte et vérification d'identité")
        statut, client = appeler(base, "POST", "/api/clients",
                                 {"nom": "Dépôt Kintoko", "telephone": "+243 820 001 234", "type": "depot"})
        attendre("le compte est créé", statut == 200, str(client))
        attendre("il naît non vérifié", client.get("statut") == "en_attente", str(client.get("statut")))
        attendre("son plafond est nul", client.get("plafond") == 0.0, str(client.get("plafond")))
        client_id = client.get("id")

        statut, refus = appeler(base, "POST", "/api/cotations",
                                {"client_id": client_id, "produit": "Surecem", "quantite": 100,
                                 "zone": "Gombé", "option": "B"})
        attendre("aucun prix n'est produit avant vérification (RG-COT-01)",
                 statut == 403 and refus.get("erreur") == "identite_non_verifiee", str(refus))

        statut, refus = appeler(base, "POST", f"/api/clients/{client_id}/pieces", {"recto": False})
        attendre("une pièce incomplète est refusée", statut == 400, str(refus))

        statut, client = appeler(base, "POST", f"/api/clients/{client_id}/pieces",
                                 {"type_piece": "carte_identite", "recto": True, "verso": True})
        attendre("le dépôt complet vérifie le compte", client.get("statut") == "verifie", str(client))
        attendre("le palier entreprise donne 10 000 $", client.get("plafond") == 10000.0,
                 str(client.get("plafond")))

        print("\nJ2 — Cotation certifiée")
        statut, cotation = appeler(base, "POST", "/api/cotations",
                                   {"client_id": client_id, "produit": "Surecem", "quantite": 100,
                                    "zone": "Gombé", "option": "B"})
        attendre("la cotation est émise", statut == 200, str(cotation))
        numero = cotation.get("numero", "")
        attendre("elle porte un numéro", numero.startswith("COT-"), numero)
        attendre("le total est juste (9,5 × 100 + 320)", cotation.get("total") == 1270.0,
                 str(cotation.get("total")))
        attendre("elle expose son délai restant", cotation.get("expire_dans_s", 0) > 0,
                 str(cotation.get("expire_dans_s")))

        statut, refus = appeler(base, "POST", "/api/cotations",
                                {"client_id": client_id, "produit": "Surecem", "quantite": 5000,
                                 "zone": "Gombé", "option": "B"})
        attendre("le plafond du palier arrête la commande (RG-PAY-14)",
                 statut == 409 and refus.get("erreur") == "plafond_depasse", str(refus))

        print("\nJ3 — Paiement encaissé")
        statut, bon = appeler(base, "POST", "/api/paiements", {"cotation": numero, "canal": "m_pesa"})
        attendre("le paiement est encaissé", statut == 200, str(bon))
        attendre("le bon naît de l'encaissement (RG-CMD-01)", bool(bon.get("code")), str(bon))
        code, qr = bon.get("code", ""), bon.get("qr", "")

        statut, refus = appeler(base, "POST", "/api/paiements", {"cotation": numero, "canal": "m_pesa"})
        attendre("un second paiement est refusé", statut == 409 and refus.get("erreur") == "deja_payee",
                 str(refus))

        print("\nJ4 et J5 — Bon, contrôle et chargement")
        statut, refus = appeler(base, "POST", "/api/controles", {"saisie": code})
        attendre("le poids est exigé au chargement", statut == 400 and refus.get("erreur") == "poids_invalide",
                 str(refus))

        statut, charge = appeler(base, "POST", "/api/controles",
                                 {"saisie": code, "poids_kg": 5000, "transporteur": "Trans-Kinshasa",
                                  "plaque": "KN 4321 CD"})
        attendre("le code de retrait est accepté", statut == 200 and charge.get("statut") == "charge",
                 str(charge))
        attendre("le scellé et le transporteur sont enregistrés",
                 charge["chargement"]["transporteur"] == "Trans-Kinshasa"
                 and bool(charge["chargement"]["scelle"]), str(charge.get("chargement")))

        statut, refus = appeler(base, "POST", "/api/controles", {"saisie": code, "poids_kg": 5000})
        attendre("le second passage est refusé (RG-CMD-05)",
                 statut == 409 and refus.get("erreur") == "deja_utilise", str(refus))

        statut, refus = appeler(base, "POST", "/api/controles",
                                {"saisie": qr.replace("|100|", "|200|"), "poids_kg": 5000})
        attendre("un bon modifié est refusé (signature)", 
                 statut == 409 and refus.get("erreur") == "signature_invalide", str(refus))

        print("\nJ6 — Livraison prouvée et litige")
        statut, refus = appeler(base, "GET", f"/api/recus/{code}")
        attendre("aucun reçu avant livraison", statut == 409 and refus.get("erreur") == "pas_livre", str(refus))

        statut, recu = appeler(base, "POST", "/api/receptions",
                               {"code": code, "sacs_recus": 95, "poids_recu_kg": 4750, "scelle_ok": True})
        attendre("la réception est enregistrée", statut == 200, str(recu))
        attendre("l'écart est calculé", recu["reception"]["ecart"] == -5, str(recu.get("reception")))
        attendre("l'écart hors tolérance ouvre un litige (RG-POD-04)",
                 recu.get("litige") is not None, str(recu.get("litige")))

        statut, preuve = appeler(base, "GET", f"/api/preuves/{code}")
        attendre("le dossier de preuve est constitué", statut == 200 and len(preuve.get("etapes", [])) >= 5,
                 str(len(preuve.get("etapes", []))))

        litige_id = recu["litige"]["id"]
        statut, instruit = appeler(base, "POST", f"/api/litiges/{litige_id}/instruction",
                                   {"retenu": 47.5, "libere": 0, "decision": "5 sacs manquants, retenue au transporteur"})
        attendre("le litige est instruit (RG-LIT-02)",
                 statut == 200 and instruit["litige"]["statut"] == "instruit", str(instruit))

        print("\nJ7 — Reçu et historique")
        statut, recu_final = appeler(base, "GET", f"/api/recus/{code}")
        attendre("le reçu est délivré après livraison", statut == 200, str(recu_final))
        attendre("il porte une empreinte vérifiable", len(recu_final.get("empreinte", "")) == 16, str(recu_final))

        statut, historique = appeler(base, "GET", f"/api/clients/{client_id}/historique")
        attendre("l'historique du client est disponible",
                 statut == 200 and len(historique.get("cotations", [])) == 1, str(historique))

        print("\nPilotage")
        statut, tableau = appeler(base, "GET", "/api/tableau")
        attendre("le tableau répond", statut == 200, str(statut))
        attendre("un litige ouvert est compté", tableau.get("litiges_ouverts") == 0,
                 "instruit, donc plus ouvert : " + str(tableau.get("litiges_ouverts")))
        attendre("l'encaissement est de 1 270 $", tableau.get("encaisse") == 1270.0, str(tableau.get("encaisse")))

        statut, bureau = appeler(base, "GET", "/api/backoffice")
        attendre("le back-office liste cotations, bons et litiges",
                 statut == 200 and len(bureau.get("cotations", [])) == 1
                 and len(bureau.get("litiges", [])) == 1, str(bureau.keys()))

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
