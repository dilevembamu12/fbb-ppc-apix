#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Génère les sept lignes de voix off du film avec Kokoro, via le CLI HyperFrames.

Le texte est passé en argument depuis Python (UTF-8 natif) : la console Windows en cp1252
abîmerait les accents si on le passait par PowerShell.
"""

import json
import subprocess
import sys
from pathlib import Path

RACINE = Path(__file__).resolve().parent

VOIX = "ff_siwis"
LANGUE = "fr-fr"

LIGNES = [
    "Où est mon camion ? Combien de sacs sont arrivés ? Qui paie les manquants ? "
    "Trois questions. Aucune preuve.",
    "Une seule cotation, un seul bon de commande. Sur l'application, mais aussi sur WhatsApp, "
    "Telegram, par e-mail, par SMS et par USSD.",
    "Sur WhatsApp, le client demande un prix, reçoit sa cotation, paie en la référençant — "
    "et le bon arrive dans la conversation, avec son QR.",
    "Sur SMS, trois mots suffisent. Sur USSD, un menu, sans internet. Le paiement passe, "
    "et le bon devient un code de retrait que l'agent saisit.",
    "Telegram fait la même chose avec des boutons. Et par e-mail, la cotation arrive en PDF, "
    "avec un lien de paiement signé.",
    "Côté PPC, rien ne change : la console de chargement contrôle le bon, QR ou code, "
    "et refuse un bon expiré ou déjà utilisé. Le back-office garde la main sur les canaux, "
    "les modèles et le routage.",
    "Un client peut commencer sur USSD et terminer sur WhatsApp. "
    "Même cotation, même bon, même preuve.",
]


def main() -> int:
    total = 0.0
    for index, texte in enumerate(LIGNES, start=1):
        sortie = RACINE / f"l{index:02d}.wav"
        resultat = subprocess.run(
            ["npx", "hyperframes", "tts", texte, "-v", VOIX, "-l", LANGUE,
             "-o", str(sortie), "--json"],
            capture_output=True, text=True, encoding="utf-8", errors="replace", shell=True,
        )
        charge = None
        for ligne in (resultat.stdout or "").splitlines():
            ligne = ligne.strip()
            if ligne.startswith("{"):
                try:
                    charge = json.loads(ligne)
                except json.JSONDecodeError:
                    pass
        if not charge or not charge.get("ok"):
            print(f"[ECHEC] ligne {index} : {(resultat.stdout or resultat.stderr or '')[:200]}")
            continue
        duree = float(charge["durationSeconds"])
        total += duree
        print(f"[OK] l{index:02d}.wav — {duree:5.2f} s — {sortie.stat().st_size // 1024} Ko")

    print(f"\nDurée cumulée de la voix : {total:.2f} s pour un film de 90 s")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
