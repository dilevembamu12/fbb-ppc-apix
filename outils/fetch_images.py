#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
fetch_images.py â€” RÃ©cupÃ©ration d'images libres pour la prÃ©sentation APIX All In One.

Source unique : Wikimedia Commons (licences Creative Commons ou domaine public).
L'intÃ©rÃªt est double : les images sont rÃ©ellement documentaires (Goma, routes
nationales congolaises, usines, ports), et leur licence autorise une rÃ©utilisation
commerciale sous rÃ©serve de crÃ©diter l'auteur.

Le script :
  1. cherche, pour chaque thÃ¨me, une photo rÃ©pondant aux critÃ¨res de qualitÃ© ;
  2. la tÃ©lÃ©charge en dÃ©finition raisonnable (2000 px de large) ;
  3. la recadre au format 16:9 pour un usage plein cadre ;
  4. consigne auteur, licence et page source dans assets/credits.json ;
  5. n'Ã©crase rien sans --force.

Usage :
    python outils/fetch_images.py
    python outils/fetch_images.py --force
    python outils/fetch_images.py --liste      # montre les thÃ¨mes sans tÃ©lÃ©charger
"""

from __future__ import annotations

import argparse
import json
import re
import sys
import time
from pathlib import Path

import requests
from PIL import Image

RACINE = Path(__file__).resolve().parent.parent
DOSSIER_IMAGES = RACINE / "assets" / "images"
FICHIER_CREDITS = RACINE / "assets" / "credits.json"

# La console Windows est en cp1252 : sans cela, les flÃ¨ches et accents font Ã©chouer
# l'affichage alors que le tÃ©lÃ©chargement, lui, a bien lieu.
try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")
except (AttributeError, ValueError):
    pass

API = "https://commons.wikimedia.org/w/api.php"
# Wikimedia exige un agent utilisateur identifiant le demandeur et un contact.
ENTETES = {
    "User-Agent": (
        "FBB-APIX-AllInOne/1.0 "
        "(https://github.com/dilevembamu12/fbb-ppc-apix; fbb@local) python-requests"
    )
}

LARGEUR_CIBLE = 2000
RATIO_CIBLE = 16 / 9

# ---------------------------------------------------------------------------
# ThÃ¨mes : chacun alimente une diapositive prÃ©cise.
# Â« recherches Â» est une liste de requÃªtes essayÃ©es dans l'ordre.
# Â« titre_exact Â» force un fichier prÃ©cis quand il a Ã©tÃ© identifiÃ© comme pertinent.
# ---------------------------------------------------------------------------
THEMES = [
    {
        "cle": "couverture",
        "usage": "Diapositive de couverture",
        "titre_exact": "File:Cement bags in Douma.jpg",
        "recherches": ["cement bags stack", "cement sacks warehouse"],
    },
    {
        "cle": "douleur_manutention",
        "usage": "Douleur : manutention et casse des sacs",
        "titre_exact": "File:Father and son loading and unloading cement in Goma, Congo.jpg",
        "recherches": ["loading cement bags Africa", "unloading cement Congo"],
    },
    {
        "cle": "douleur_route",
        "usage": "Douleur : Ã©tat des routes et retards",
        "titre_exact": None,
        "recherches": [
            "truck stuck mud road Congo",
            "camion route nationale Congo",
            "truck broken road Africa",
            "rainy season road Congo truck",
        ],
    },
    {
        "cle": "douleur_attente",
        "usage": "Douleur : files d'attente et immobilisation des camions",
        "titre_exact": "File:Namanga.jpg",
        "recherches": ["truck queue border", "trucks waiting factory gate"],
    },
    {
        "cle": "usine",
        "usage": "Le produit : usine et production",
        "titre_exact": None,
        "recherches": ["cement plant kiln", "cement factory silo", "cement works"],
    },
    {
        "cle": "livraison",
        "usage": "La livraison : camion et dÃ©chargement",
        "titre_exact": "File:Semi truck for cement transportation.jpg",
        "recherches": [
            "cement truck Africa",
            "truck unloading construction material",
        ],
    },
    {
        "cle": "mobile",
        "usage": "L'ubiquitÃ© : paiement mobile et smartphone",
        "titre_exact": "File:Mobile Money Kiosk.jpg",
        "recherches": ["mobile money shop Africa", "smartphone market Africa"],
    },
    {
        "cle": "ville",
        "usage": "Le marchÃ© : quartiers et points de vente",
        "titre_exact": "File:Construction site in Pretoria Central.jpg",
        "recherches": ["Kinshasa market", "construction site Africa building"],
    },
]

# Licences acceptÃ©es pour un usage commercial avec attribution.
LICENCES_ACCEPTEES = ("cc by", "cc-by", "cc0", "public domain", "domaine public", "pd")


def nettoyer_html(texte: str) -> str:
    """Retire les balises HTML renvoyÃ©es par l'API pour les champs auteur."""
    if not texte:
        return ""
    texte = re.sub(r"<[^>]+>", " ", texte)
    return re.sub(r"\s+", " ", texte).strip()


def licence_acceptee(licence: str) -> bool:
    minuscule = (licence or "").lower()
    if any(mot in minuscule for mot in ("nc", "nd", "non commercial", "non-commercial")):
        # Les licences Â« pas d'usage commercial Â» ou Â« pas de modification Â» sont Ã©cartÃ©es.
        if "cc by-nc" in minuscule or "cc-by-nc" in minuscule or "non commercial" in minuscule:
            return False
    return any(mot in minuscule for mot in LICENCES_ACCEPTEES)


def interroger(parametres: dict) -> dict:
    reponse = requests.get(API, params=parametres, headers=ENTETES, timeout=40)
    reponse.raise_for_status()
    return reponse.json()


def normaliser_page(page: dict) -> dict | None:
    infos = (page.get("imageinfo") or [{}])[0]
    metadonnees = infos.get("extmetadata", {})
    licence = nettoyer_html(metadonnees.get("LicenseShortName", {}).get("value", ""))
    if not licence_acceptee(licence):
        return None
    if infos.get("mime") not in ("image/jpeg", "image/png"):
        return None
    largeur = infos.get("width") or 0
    hauteur = infos.get("height") or 0
    if largeur < 1200 or hauteur < 700:
        return None
    return {
        "titre": page.get("title", ""),
        "auteur": nettoyer_html(metadonnees.get("Artist", {}).get("value", "auteur non renseignÃ©")),
        "licence": licence,
        "page": infos.get("descriptionurl", ""),
        # On privilÃ©gie le fichier d'origine : l'URL de vignette porte des paramÃ¨tres
        # de suivi que le CDN de Wikimedia rejette en limitant le dÃ©bit.
        "url": (infos.get("url") or infos.get("thumburl") or "").split("?")[0],
        "largeur_source": largeur,
        "hauteur_source": hauteur,
    }


def chercher_par_titre(titre: str) -> dict | None:
    donnees = interroger({
        "action": "query", "format": "json", "titles": titre,
        "prop": "imageinfo", "iiprop": "url|extmetadata|size|mime", "iiurlwidth": str(LARGEUR_CIBLE),
    })
    for page in donnees.get("query", {}).get("pages", {}).values():
        resultat = normaliser_page(page)
        if resultat:
            return resultat
    return None


def chercher_par_requete(requete: str, limite: int = 10) -> dict | None:
    donnees = interroger({
        "action": "query", "format": "json", "generator": "search",
        "gsrsearch": requete, "gsrnamespace": "6", "gsrlimit": str(limite),
        "prop": "imageinfo", "iiprop": "url|extmetadata|size|mime", "iiurlwidth": str(LARGEUR_CIBLE),
    })
    pages = (donnees.get("query") or {}).get("pages") or {}
    # Ordre de pertinence : l'API renvoie un index croissant.
    for page in sorted(pages.values(), key=lambda p: p.get("index", 999)):
        resultat = normaliser_page(page)
        if resultat:
            return resultat
    return None


def recadrer(source: Path, destination: Path) -> tuple[int, int]:
    """Recadre au format 16:9 en coupant l'excÃ©dent, puis enregistre en JPEG."""
    with Image.open(source) as image:
        image = image.convert("RGB")
        largeur, hauteur = image.size
        if largeur / hauteur > RATIO_CIBLE:
            nouvelle_largeur = int(hauteur * RATIO_CIBLE)
            gauche = (largeur - nouvelle_largeur) // 2
            image = image.crop((gauche, 0, gauche + nouvelle_largeur, hauteur))
        else:
            nouvelle_hauteur = int(largeur / RATIO_CIBLE)
            haut = (hauteur - nouvelle_hauteur) // 2
            image = image.crop((0, haut, largeur, haut + nouvelle_hauteur))
        if image.width > LARGEUR_CIBLE:
            image = image.resize((LARGEUR_CIBLE, int(LARGEUR_CIBLE / RATIO_CIBLE)), Image.LANCZOS)
        image.save(destination, "JPEG", quality=86, optimize=True)
        return image.size


def telecharger(url: str, destination: Path, tentatives: int = 4) -> None:
    """TÃ©lÃ©charge un fichier avec temporisation, car Wikimedia limite le dÃ©bit (HTTP 429)."""
    attente = 5
    for essai in range(1, tentatives + 1):
        try:
            with requests.get(url, headers=ENTETES, timeout=90, stream=True) as flux:
                if flux.status_code == 429:
                    raise requests.HTTPError("429", response=flux)
                flux.raise_for_status()
                with open(destination, "wb") as fichier:
                    for morceau in flux.iter_content(65536):
                        fichier.write(morceau)
            return
        except requests.HTTPError as erreur:
            if essai == tentatives:
                raise
            print(f"  (nouvelle tentative {essai}/{tentatives - 1} dans {attente} s : {erreur})")
            time.sleep(attente)
            attente *= 2


def resoudre_candidat(theme: dict) -> dict | None:
    """Trouve la meilleure image disponible pour un thÃ¨me, sans la tÃ©lÃ©charger."""
    candidat = None
    if theme.get("titre_exact"):
        candidat = chercher_par_titre(theme["titre_exact"])
        if candidat:
            print(f"  titre exact retenu : {candidat['titre']}")
    if not candidat:
        for requete in theme["recherches"]:
            candidat = chercher_par_requete(requete)
            if candidat:
                print(f"  requÃªte Â« {requete} Â» retenue : {candidat['titre']}")
                break
    return candidat


def traiter_theme(theme: dict, forcer: bool) -> dict | None:
    destination = DOSSIER_IMAGES / f"{theme['cle']}.jpg"
    if destination.exists() and not forcer:
        # Le fichier est lÃ  : on ne rÃ©cupÃ¨re que les mÃ©tadonnÃ©es de crÃ©dit manquantes.
        candidat = resoudre_candidat(theme)
        print(f"[garde] {theme['cle']} dÃ©jÃ  prÃ©sent")
        if not candidat:
            return None
        return {
            "theme": theme["cle"],
            "usage": theme["usage"],
            "fichier": destination.name,
            "titre": candidat["titre"],
            "auteur": candidat["auteur"],
            "licence": candidat["licence"],
            "page": candidat["page"],
        }

    candidat = resoudre_candidat(theme)
    if not candidat or not candidat.get("url"):
        print(f"[echec] {theme['cle']} : aucune image conforme trouvÃ©e")
        return None

    temporaire = DOSSIER_IMAGES / f"_tmp_{theme['cle']}"
    telecharger(candidat["url"], temporaire)

    largeur, hauteur = recadrer(temporaire, destination)
    temporaire.unlink(missing_ok=True)
    print(f"[ok] {destination.name} â€” {largeur}x{hauteur} â€” {candidat['licence']}")

    return {
        "theme": theme["cle"],
        "usage": theme["usage"],
        "fichier": destination.name,
        "titre": candidat["titre"],
        "auteur": candidat["auteur"],
        "licence": candidat["licence"],
        "page": candidat["page"],
    }


def main() -> int:
    analyseur = argparse.ArgumentParser(description="RÃ©cupÃ©ration des images libres du dossier APIX.")
    analyseur.add_argument("--force", action="store_true", help="RetÃ©lÃ©charge mÃªme si le fichier existe.")
    analyseur.add_argument("--liste", action="store_true", help="Affiche les thÃ¨mes sans tÃ©lÃ©charger.")
    arguments = analyseur.parse_args()

    if arguments.liste:
        for theme in THEMES:
            print(f"- {theme['cle']:<22} {theme['usage']}")
        return 0

    DOSSIER_IMAGES.mkdir(parents=True, exist_ok=True)
    credits = {}
    if FICHIER_CREDITS.exists():
        credits = {c["theme"]: c for c in json.loads(FICHIER_CREDITS.read_text(encoding="utf-8"))}

    for theme in THEMES:
        print(f"â†’ {theme['cle']} ({theme['usage']})")
        resultat = traiter_theme(theme, arguments.force)
        if resultat:
            credits[theme["cle"]] = resultat
        elif (DOSSIER_IMAGES / f"{theme['cle']}.jpg").exists() and theme["cle"] not in credits:
            print(f"  (fichier prÃ©sent sans crÃ©dit enregistrÃ© : {theme['cle']})")
        time.sleep(3)  # respect de la limite de dÃ©bit de Wikimedia

    FICHIER_CREDITS.parent.mkdir(parents=True, exist_ok=True)
    FICHIER_CREDITS.write_text(
        json.dumps(sorted(credits.values(), key=lambda c: c["theme"]), ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    print(f"\n{len(credits)} image(s) documentÃ©e(s) dans {FICHIER_CREDITS.relative_to(RACINE)}")
    return 0 if credits else 1


if __name__ == "__main__":
    raise SystemExit(main())

