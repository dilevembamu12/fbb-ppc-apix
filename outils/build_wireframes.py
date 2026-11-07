#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
build_wireframes.py — Dessin des wireframes d'interface du MVP (document 05).

Usage :
    python outils/build_wireframes.py           # toutes les planches
    python outils/build_wireframes.py --only cli # planches dont le nom contient "cli"

Convention graphique : niveaux de gris uniquement, un seul accent orange réservé
à l'action principale. Les zones de texte longues sont représentées par des
barres grises, jamais par du faux texte. Chaque écran porte son code et son nom
en pied, pour rester identifiable hors contexte.

Sorties : assets/wireframes/*.png
"""

from __future__ import annotations

import argparse
import random
import sys
from functools import lru_cache
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

sys.stdout.reconfigure(encoding="utf-8", errors="replace")

RACINE = Path(__file__).resolve().parent.parent
SORTIE = RACINE / "assets" / "wireframes"

# --------------------------------------------------------------------------
# Palette : gris de wireframe, un seul accent
# --------------------------------------------------------------------------
BLANC = (255, 255, 255)
FOND = (250, 250, 250)
REMPLI = (236, 239, 241)
REMPLI_FORT = (215, 220, 225)
TRAIT = (184, 192, 200)
TRAIT_FORT = (123, 135, 148)
TEXTE = (31, 41, 51)
TEXTE_FAIBLE = (123, 135, 148)
BANDE = (244, 241, 234)
ACCENT = (224, 107, 45)
ACCENT_PALE = (246, 223, 210)

POLICES = {
    (False, False): "segoeui.ttf",
    (True, False): "segoeuib.ttf",
    (False, True): "seguisb.ttf",
    (True, True): "segoeuib.ttf",
}


@lru_cache(maxsize=256)
def police(taille: int, gras: bool = False, semi: bool = False) -> ImageFont.FreeTypeFont:
    nom = POLICES[(gras, semi)]
    return ImageFont.truetype(f"C:/Windows/Fonts/{nom}", taille)


# --------------------------------------------------------------------------
# Toile : toutes les coordonnées sont exprimées en pixels logiques
# --------------------------------------------------------------------------
class Toile:
    def __init__(self, largeur: int, hauteur: int, echelle: int = 2, fond: int = BLANC, ft: float = 1.0):
        self.e = echelle
        self.ft = ft  # facteur de taille de texte : les grands écrans sont vus de loin
        self.largeur = largeur
        self.hauteur = hauteur
        self.image = Image.new("RGB", (largeur * echelle, hauteur * echelle), fond)
        self.d = ImageDraw.Draw(self.image)

    # -- primitives ------------------------------------------------------
    def r(self, x, y, w, h, remplissage=None, contour=None, ep=1, arrondi=0):
        boite = [x * self.e, y * self.e, (x + w) * self.e, (y + h) * self.e]
        if arrondi:
            self.d.rounded_rectangle(
                boite, radius=int(arrondi * self.e), fill=remplissage,
                outline=contour, width=int(ep * self.e),
            )
        else:
            self.d.rectangle(boite, fill=remplissage, outline=contour, width=int(ep * self.e))

    def rp(self, x, y, w, h, contour=TRAIT, ep=1, fond=None):
        """Rectangle en pointillés (zones à remplir, placeholders)."""
        self.r(x, y, w, h, remplissage=fond)
        self.ligne(x, y, x + w, y, contour, ep, pointille=True)
        self.ligne(x, y + h, x + w, y + h, contour, ep, pointille=True)
        self.ligne(x, y, x, y + h, contour, ep, pointille=True)
        self.ligne(x + w, y, x + w, y + h, contour, ep, pointille=True)

    def ligne(self, x1, y1, x2, y2, couleur=TRAIT, ep=1, pointille=False):
        if not pointille:
            self.d.line([x1 * self.e, y1 * self.e, x2 * self.e, y2 * self.e],
                        fill=couleur, width=int(ep * self.e))
            return
        import math
        longueur = math.hypot(x2 - x1, y2 - y1)
        if longueur == 0:
            return
        pas, tiret = 6.0, 3.5
        parcouru = 0.0
        while parcouru < longueur:
            fin = min(parcouru + tiret, longueur)
            ax = x1 + (x2 - x1) * parcouru / longueur
            ay = y1 + (y2 - y1) * parcouru / longueur
            bx = x1 + (x2 - x1) * fin / longueur
            by = y1 + (y2 - y1) * fin / longueur
            self.d.line([ax * self.e, ay * self.e, bx * self.e, by * self.e],
                        fill=couleur, width=int(ep * self.e))
            parcouru += pas

    def t(self, x, y, texte, taille=11, gras=False, semi=False, couleur=TEXTE, ancre="la"):
        self.d.text((x * self.e, y * self.e), texte,
                    font=police(int(taille * self.ft * self.e), gras, semi), fill=couleur, anchor=ancre)

    def tl(self, x, y, largeur, texte, taille=11, gras=False, semi=False,
           couleur=TEXTE, interligne=1.4):
        """Texte enveloppé ; renvoie la hauteur consommée."""
        f = police(int(taille * self.ft * self.e), gras, semi)
        mots, ligne, hauteur = texte.split(), "", 0
        for mot in mots:
            essai = f"{ligne} {mot}".strip()
            if self.d.textlength(essai, font=f) <= largeur * self.e or not ligne:
                ligne = essai
            else:
                self.d.text((x * self.e, (y + hauteur) * self.e), ligne, font=f,
                            fill=couleur, anchor="la")
                hauteur += taille * self.ft * interligne
                ligne = mot
        if ligne:
            self.d.text((x * self.e, (y + hauteur) * self.e), ligne, font=f,
                        fill=couleur, anchor="la")
            hauteur += taille * self.ft * interligne
        return hauteur

    def nb_lignes(self, texte, largeur, taille=11, gras=False, semi=False):
        """Nombre de lignes qu'occupera un texte enveloppé dans la largeur donnée."""
        f = police(int(taille * self.ft * self.e), gras, semi)
        mots, ligne, nombre = texte.split(), "", 1
        for mot in mots:
            essai = f"{ligne} {mot}".strip()
            if self.d.textlength(essai, font=f) <= largeur * self.e or not ligne:
                ligne = essai
            else:
                nombre += 1
                ligne = mot
        return nombre

    def mesurer(self, texte, taille=11, gras=False, semi=False):
        return self.d.textlength(texte, font=police(int(taille * self.ft * self.e), gras, semi)) / self.e

    def coller(self, autre: "Toile", x, y):
        self.image.paste(autre.image, (int(x * self.e), int(y * self.e)))

    def enregistrer(self, chemin: Path):
        chemin.parent.mkdir(parents=True, exist_ok=True)
        self.image.save(chemin, "PNG", optimize=True)


# --------------------------------------------------------------------------
# Composants communs
# --------------------------------------------------------------------------
L_PHONE, H_PHONE = 390, 780
H_PIEDS = 34


def cadre_phone(titre_ecran: str, retour: bool = True, action: str | None = None) -> Toile:
    """Toile de téléphone avec barre d'état et en-tête ; renvoie la toile prête à dessiner."""
    b = Toile(L_PHONE, H_PHONE)
    b.r(0, 0, L_PHONE, H_PHONE, contour=TRAIT)
    # barre d'état : icônes dessinées, aucun glyphe système
    b.t(18, 12, "14:32", 11, semi=True)
    for i in range(4):
        b.r(L_PHONE - 92 + i * 7, 22 - i * 3, 4, 3 + i * 3, remplissage=TEXTE_FAIBLE)
    b.r(L_PHONE - 56, 13, 20, 11, contour=TEXTE_FAIBLE, ep=1, arrondi=2)
    b.r(L_PHONE - 54, 15, 13, 7, remplissage=TEXTE_FAIBLE)
    b.ligne(0, 38, L_PHONE, 38, TRAIT)
    # en-tête
    b.r(0, 38, L_PHONE, 62, remplissage=BANDE)
    if retour:
        b.t(20, 60, "‹", 22, couleur=TEXTE, ancre="la")
    b.t(L_PHONE / 2, 70, titre_ecran, 14, semi=True, ancre="ma")
    if action:
        b.t(L_PHONE - 18, 60, action, 11, couleur=ACCENT, ancre="ra")
    b.ligne(0, 100, L_PHONE, 100, TRAIT)
    return b


def pied_ecran(b: Toile, code: str, nom: str):
    """Bandeau de pied identifiant l'écran."""
    y = H_PHONE - H_PIEDS
    b.ligne(0, y, L_PHONE, y, TRAIT)
    b.t(18, y + 11, code, 10, gras=True)
    b.t(18 + b.mesurer(code, 10, gras=True) + 8, y + 11, nom, 10, couleur=TEXTE_FAIBLE)


def onglets(b: Toile, y, entrees, actif=0, largeur=L_PHONE):
    b.ligne(0, y, largeur, y, TRAIT)
    pas = largeur // len(entrees)
    for i, e in enumerate(entrees):
        x = i * pas + pas / 2
        b.t(x, y + 14, e, 10, gras=(i == actif), couleur=TEXTE if i == actif else TEXTE_FAIBLE, ancre="ma")
        if i == actif:
            b.r(i * pas + 12, y + 1, pas - 24, 3, remplissage=ACCENT)


def bouton(b: Toile, x, y, w, h, libelle, principal=False, taille=12):
    if principal:
        b.r(x, y, w, h, remplissage=ACCENT, arrondi=6)
        b.t(x + w / 2, y + h / 2, libelle, taille, semi=True, couleur=BLANC, ancre="mm")
    else:
        b.r(x, y, w, h, contour=TRAIT_FORT, ep=1, arrondi=6)
        b.t(x + w / 2, y + h / 2, libelle, taille, semi=True, ancre="mm")


def champ(b: Toile, x, y, w, libelle, valeur, hauteur=44, aide=None):
    b.t(x, y, libelle, 9, couleur=TEXTE_FAIBLE)
    b.r(x, y + 13, w, hauteur, contour=TRAIT, ep=1, arrondi=5)
    b.t(x + 12, y + 13 + hauteur / 2, valeur, 11, ancre="lm")
    if aide:
        b.t(x, y + 13 + hauteur + 5, aide, 9, couleur=TEXTE_FAIBLE)
        return y + 13 + hauteur + 20
    return y + 13 + hauteur + 12


def carte(b: Toile, x, y, w, h, contour=TRAIT):
    b.r(x, y, w, h, contour=contour, ep=1, arrondi=8)


def barres(texte_toile: Toile, x, y, largeur, nb=3, hauteur=7, ecart=12):
    """Faux paragraphe : barres grises de longueurs décroissantes."""
    for i in range(nb):
        l = largeur * (1 - i * 0.12)
        texte_toile.r(x, y + i * ecart, l, hauteur, remplissage=REMPLI_FORT, arrondi=3)
    return y + nb * ecart


def qr(b: Toile, x, y, taille, graine=7):
    """Faux QR déterministe : trois repères d'angle et un motif stable."""
    b.r(x - 6, y - 6, taille + 12, taille + 12, contour=TRAIT_FORT, ep=1)
    modules = 25
    pas = taille / modules
    alea = random.Random(graine)
    for i in range(modules):
        for j in range(modules):
            if alea.random() < 0.45:
                b.r(x + i * pas, y + j * pas, pas, pas, remplissage=TEXTE)
    for (ci, cj) in ((0, 0), (modules - 7, 0), (0, modules - 7)):
        b.r(x + ci * pas, y + cj * pas, 7 * pas, 7 * pas, remplissage=BLANC)
        b.r(x + ci * pas, y + cj * pas, 7 * pas, 7 * pas, contour=TEXTE, ep=1.5)
        b.r(x + (ci + 2) * pas, y + (cj + 2) * pas, 3 * pas, 3 * pas, remplissage=TEXTE)


def photo(b: Toile, x, y, w, h, libelle="Photo"):
    b.r(x, y, w, h, remplissage=REMPLI)
    b.rp(x, y, w, h, contour=TRAIT_FORT, ep=1)
    b.ligne(x, y, x + w, y + h, TRAIT_FORT, 1, pointille=True)
    b.ligne(x + w, y, x, y + h, TRAIT_FORT, 1, pointille=True)
    b.t(x + w / 2, y + h / 2 + 4, libelle, 9, couleur=TEXTE_FAIBLE, ancre="ma")


def alerte(b: Toile, x, y, w, texte, hauteur=None):
    lignes = b.nb_lignes(texte, w - 28, 10)
    h = hauteur or (14 + lignes * 14)
    b.r(x, y, w, h, contour=ACCENT, ep=1.5, arrondi=6, remplissage=ACCENT_PALE)
    b.r(x, y, 4, h, remplissage=ACCENT)
    b.tl(x + 16, y + 9, w - 28, texte, 10, couleur=TEXTE, interligne=1.35)
    return y + h + 10


# --------------------------------------------------------------------------
# IF-01 — Application client
# --------------------------------------------------------------------------
def ecran_cli04() -> Toile:
    b = cadre_phone("Catalogue", retour=False, action="Profil")
    b.t(18, 118, "Bonjour, Kivu Trans", 15, semi=True)
    b.t(18, 140, "Compte vérifié · plafond 2 500 $ par transaction", 10, couleur=TEXTE_FAIBLE)

    y = 168
    for nom, sous, prix in (
        ("Ciment CEM II 42,5 — 50 kg", "Disponible à l'usine de Kimpese", "12,40 $ / sac"),
        ("Ciment CEM I 52,5 — 50 kg", "Disponible à l'usine de Kimpese", "13,80 $ / sac"),
    ):
        carte(b, 18, y, L_PHONE - 36, 92)
        b.r(30, y + 14, 64, 64, remplissage=REMPLI, arrondi=4)
        b.t(30 + 32, y + 46, "sac", 9, couleur=TEXTE_FAIBLE, ancre="ma")
        b.t(108, y + 18, nom, 11, semi=True)
        b.t(108, y + 38, sous, 9, couleur=TEXTE_FAIBLE)
        b.t(108, y + 58, prix, 12, semi=True)
        y += 104

    b.r(18, y + 4, L_PHONE - 36, 52, remplissage=BANDE, arrondi=6)
    b.tl(30, y + 18, L_PHONE - 60,
         "Les prix affichés dépendent de votre profil et de votre zone de livraison.",
         9, couleur=TEXTE_FAIBLE)

    # dernières commandes : remplit l'écran et rappelle la mémoire du compte
    y += 76
    b.t(18, y, "Vos dernières commandes", 11, semi=True)
    y += 22
    for code, etat in (("BON-2026-000451", "en livraison"),
                       ("BON-2026-000437", "livré le 04/11"),
                       ("BON-2026-000421", "livré le 28/10")):
        b.t(18, y, code, 10, semi=True)
        b.t(L_PHONE - 18, y, etat, 10, couleur=TEXTE_FAIBLE, ancre="ra")
        y += 24
        b.ligne(18, y - 8, L_PHONE - 18, y - 8, TRAIT)

    bouton(b, 18, H_PHONE - H_PIEDS - 132, L_PHONE - 36, 50, "Demander une cotation", principal=True)
    onglets(b, H_PHONE - H_PIEDS - 58, ["Catalogue", "Commandes", "Historique", "Profil"])
    pied_ecran(b, "CLI-04", "Catalogue et prix")
    return b


def ecran_cli07() -> Toile:
    b = cadre_phone("Votre demande")
    y = 120
    b.t(18, y, "Récapitulatif avant cotation", 11, couleur=TEXTE_FAIBLE)
    y += 22

    lignes = (
        ("Produit", "CEM II 42,5 — 50 kg"),
        ("Quantité", "200 sacs"),
        ("Destination", "Zone Gombe — 4e avenue"),
        ("Option", "Avec transport PPC"),
    )
    for lib, val in lignes:
        b.t(18, y, lib, 10, couleur=TEXTE_FAIBLE)
        b.t(L_PHONE - 18, y, val, 11, semi=True, ancre="ra")
        y += 24
        b.ligne(18, y - 6, L_PHONE - 18, y - 6, TRAIT)

    y += 10
    b.t(18, y, "Détail du prix", 11, semi=True)
    y += 22
    for lib, val, gras in (
        ("Ciment (200 sacs × 12,40 $)", "2 480,00 $", False),
        ("Transport — axe Kimpese / Gombe", "640,00 $", False),
        ("Frais annexes", "25,00 $", False),
        ("Total tout compris", "3 145,00 $", True),
    ):
        b.t(18, y, lib, 10 if not gras else 12, semi=gras, couleur=TEXTE if gras else TEXTE_FAIBLE)
        b.t(L_PHONE - 18, y, val, 10 if not gras else 12, semi=gras, ancre="ra")
        y += 22
    b.ligne(18, y - 4, L_PHONE - 18, y - 4, TRAIT_FORT)

    alerte(b, 18, y + 14, L_PHONE - 36,
           "3 145 $ dépasse le plafond de 2 500 $ du mobile money : le virement ou un échéancier sera proposé au paiement.")

    # ce qui se passe ensuite : le client sait qu'il ne paie pas encore
    y += 76
    b.t(18, y, "Ce qui se passe ensuite", 11, semi=True)
    y += 26
    for numero, titre, detail in (
        ("1", "PPC émet la cotation", "numéro unique, prix ferme, valable 48 h"),
        ("2", "Vous payez en la référençant", "le numéro de cotation est la référence de paiement"),
        ("3", "Le bon est émis automatiquement", "à l'encaissement, une seule fois"),
    ):
        b.r(18, y - 4, 22, 22, contour=TRAIT_FORT, ep=1, arrondi=11)
        b.t(29, y + 7, numero, 10, semi=True, ancre="mm")
        b.t(52, y, titre, 10, semi=True)
        b.t(52, y + 16, detail, 9, couleur=TEXTE_FAIBLE)
        y += 44

    bouton(b, 18, H_PHONE - H_PIEDS - 74, L_PHONE - 36, 50, "Recevoir ma cotation", principal=True)
    b.t(L_PHONE / 2, H_PHONE - H_PIEDS - 90, "Aucun paiement à cette étape", 9,
        couleur=TEXTE_FAIBLE, ancre="ma")
    pied_ecran(b, "CLI-07", "Demande de cotation")
    return b


def ecran_cli08() -> Toile:
    b = cadre_phone("Cotation")
    b.r(18, 116, L_PHONE - 36, 96, contour=TRAIT_FORT, ep=1.5, arrondi=8)
    b.t(34, 130, "COT-2026-000123", 11, semi=True, couleur=TEXTE_FAIBLE)
    b.t(34, 152, "3 145,00 $", 26, gras=True)
    b.t(34, 186, "Prix ferme — aucune ligne ne peut être ajoutée", 9, couleur=TEXTE_FAIBLE)

    b.r(L_PHONE - 150, 130, 116, 26, contour=ACCENT, ep=1.5, arrondi=13, remplissage=ACCENT_PALE)
    b.t(L_PHONE - 92, 143, "Expire dans 47:12:40", 9, semi=True, couleur=ACCENT, ancre="mm")

    y = 230
    b.t(18, y, "Détail", 11, semi=True)
    y += 20
    for lib, val in (("Ciment (200 sacs)", "2 480,00 $"), ("Transport", "640,00 $"), ("Frais annexes", "25,00 $")):
        b.t(18, y, lib, 10, couleur=TEXTE_FAIBLE)
        b.t(L_PHONE - 18, y, val, 10, ancre="ra")
        y += 22
        b.ligne(18, y - 6, L_PHONE - 18, y - 6, TRAIT)

    y += 8
    b.t(18, y, "Titulaire", 10, couleur=TEXTE_FAIBLE)
    b.t(18, y + 16, "Kivu Trans SARL — compte vérifié", 11, semi=True)
    b.t(18, y + 42, "Émise le 07/11/2026 à 14:32", 9, couleur=TEXTE_FAIBLE)

    alerte(b, 18, y + 66, L_PHONE - 36,
           "Passé ce délai, cette cotation ne peut plus être payée : une nouvelle sera calculée au prix en vigueur.")

    bouton(b, 18, H_PHONE - H_PIEDS - 74, L_PHONE - 36, 50, "Payer cette cotation", principal=True)
    b.t(L_PHONE / 2, H_PHONE - H_PIEDS - 90, "Référence de paiement : COT-2026-000123", 9,
        couleur=TEXTE_FAIBLE, ancre="ma")
    pied_ecran(b, "CLI-08", "Cotation certifiée")
    return b


def ecran_cli09() -> Toile:
    b = cadre_phone("Payer 3 145,00 $")
    b.t(18, 118, "Référence de paiement", 9, couleur=TEXTE_FAIBLE)
    b.r(18, 132, L_PHONE - 36, 40, remplissage=REMPLI, arrondi=5)
    b.t(30, 152, "COT-2026-000123", 12, semi=True, ancre="lm")
    b.t(L_PHONE - 30, 152, "liée", 9, couleur=TEXTE_FAIBLE, ancre="rm")

    y = 190
    b.t(18, y, "Moyens de paiement disponibles", 11, semi=True)
    y += 24

    # canal indisponible
    carte(b, 18, y, L_PHONE - 36, 62)
    b.t(32, y + 14, "Mobile money", 11, semi=True, couleur=TEXTE_FAIBLE)
    b.t(32, y + 34, "Indisponible au-delà de 2 500 $", 9, couleur=TEXTE_FAIBLE)
    b.r(L_PHONE - 92, y + 20, 56, 22, contour=TRAIT, ep=1, arrondi=11)
    b.t(L_PHONE - 64, y + 31, "non", 9, couleur=TEXTE_FAIBLE, ancre="mm")
    y += 72

    # canal recommandé
    carte(b, 18, y, L_PHONE - 36, 66, contour=ACCENT)
    b.t(32, y + 14, "Virement bancaire", 11, semi=True)
    b.t(32, y + 34, "Recommandé pour ce montant", 9, couleur=ACCENT)
    b.r(L_PHONE - 92, y + 22, 56, 22, contour=ACCENT, ep=1.5, arrondi=11, remplissage=ACCENT_PALE)
    b.t(L_PHONE - 64, y + 33, "choisi", 9, semi=True, couleur=ACCENT, ancre="mm")
    y += 76

    # échéancier
    carte(b, 18, y, L_PHONE - 36, 62)
    b.t(32, y + 14, "Échéancier en 2 versements", 11, semi=True)
    b.t(32, y + 34, "La commande reste bloquée jusqu'au paiement intégral", 9, couleur=TEXTE_FAIBLE)
    y += 74

    b.r(18, y, L_PHONE - 36, 60, remplissage=BANDE, arrondi=6)
    b.tl(30, y + 12, L_PHONE - 60,
         "Le fractionnement d'une même commande pour passer sous un plafond est refusé.",
         9, couleur=TEXTE_FAIBLE)

    bouton(b, 18, H_PHONE - H_PIEDS - 70, L_PHONE - 36, 50, "Continuer avec le virement", principal=True)
    pied_ecran(b, "CLI-09", "Choix du moyen de paiement")
    return b


def ecran_cli11() -> Toile:
    b = cadre_phone("Bon de commande")
    b.t(18, 118, "BON-2026-000456", 12, semi=True, couleur=TEXTE_FAIBLE)
    qr(b, 95, 146, 200, graine=11)
    b.t(L_PHONE / 2, 368, "À présenter au point de chargement", 10,
        couleur=TEXTE_FAIBLE, ancre="ma")

    y = 398
    for lib, val in (
        ("Titulaire", "Kivu Trans SARL"),
        ("Produit", "CEM II 42,5 — 200 sacs"),
        ("Point de chargement", "Usine de Kimpese"),
        ("Option", "Enlèvement par le client"),
    ):
        b.t(18, y, lib, 9, couleur=TEXTE_FAIBLE)
        b.t(L_PHONE - 18, y, val, 10, semi=True, ancre="ra")
        y += 22
        b.ligne(18, y - 6, L_PHONE - 18, y - 6, TRAIT)

    y += 12
    b.r(18, y, L_PHONE - 36, 62, contour=TRAIT_FORT, ep=1, arrondi=6)
    b.t(32, y + 12, "Code d'enlèvement du mandataire", 9, couleur=TEXTE_FAIBLE)
    b.t(32, y + 32, "481 902", 20, gras=True)
    b.t(L_PHONE - 32, y + 32, "usage unique", 9, couleur=ACCENT, ancre="ra")

    b.tl(18, H_PHONE - H_PIEDS - 56, L_PHONE - 36,
         "Le bon est nominatif : il ne peut être utilisé que par le titulaire du compte ou par un mandataire déclaré.",
         9, couleur=TEXTE_FAIBLE)
    pied_ecran(b, "CLI-11", "Bon de commande")
    return b


def ecran_cli13() -> Toile:
    b = cadre_phone("Réception")
    b.t(18, 116, "BON-2026-000456 — Zone Gombe", 10, couleur=TEXTE_FAIBLE)
    photo(b, 18, 138, L_PHONE - 36, 132, "Photo du chargement livré")

    y = 286
    for lib, val, etat in (
        ("Sacs constatés", "197 sur 200", "écart"),
        ("Scellé", "4471-B — conforme", "ok"),
        ("Poids constaté", "10 180 kg", "ok"),
    ):
        b.t(18, y, lib, 10, couleur=TEXTE_FAIBLE)
        b.t(L_PHONE - 18, y, val, 11, semi=True, ancre="ra")
        couleur = ACCENT if etat == "écart" else TEXTE_FAIBLE
        b.t(L_PHONE - 18, y + 16, "à vérifier" if etat == "écart" else "conforme", 9,
            couleur=couleur, ancre="ra")
        y += 40
        b.ligne(18, y - 12, L_PHONE - 18, y - 12, TRAIT)

    alerte(b, 18, y + 4, L_PHONE - 36,
           "Écart de 3 sacs : au-delà de la tolérance de 2 sacs, un litige est ouvert et la part contestée est gelée.")

    bouton(b, 18, H_PHONE - H_PIEDS - 116, L_PHONE - 36, 46, "Confirmer la réception", principal=True)
    bouton(b, 18, H_PHONE - H_PIEDS - 62, L_PHONE - 36, 46, "Refuser et ouvrir un litige")
    b.t(L_PHONE / 2, H_PHONE - H_PIEDS - 128, "La validation vous appartient, jamais au chauffeur", 9,
        couleur=TEXTE_FAIBLE, ancre="ma")
    pied_ecran(b, "CLI-13", "Validation de réception")
    return b


# --------------------------------------------------------------------------
# IF-03 — Application chauffeur
# --------------------------------------------------------------------------
def ecran_chf02() -> Toile:
    b = cadre_phone("Mes courses", retour=False, action="Compte")
    b.r(0, 100, L_PHONE, 30, remplissage=REMPLI_FORT)
    b.t(18, 110, "Hors ligne — 3 opérations en attente d'envoi", 9, couleur=TEXTE)
    onglets(b, 130, ["À venir", "En cours", "Terminées"])

    y = 180
    for code, trajet, heure, etat, accent in (
        ("BON-2026-000456", "Kimpese → Gombe", "Chargement 14:30", "À CHARGER", True),
        ("BON-2026-000451", "Kimpese → Limete", "Livraison 16:00", "EN ROUTE", False),
    ):
        carte(b, 18, y, L_PHONE - 36, 104, contour=ACCENT if accent else TRAIT)
        b.t(32, y + 12, code, 10, semi=True, couleur=TEXTE_FAIBLE)
        b.t(32, y + 32, trajet, 13, semi=True)
        b.t(32, y + 54, heure, 10, couleur=TEXTE_FAIBLE)
        b.r(L_PHONE - 128, y + 50, 96, 24, contour=TRAIT_FORT, ep=1, arrondi=12)
        b.t(L_PHONE - 80, y + 62, etat, 9, semi=True, ancre="mm")
        b.t(32, y + 78, "10 250 kg · 200 sacs · scellé 4471-B", 9, couleur=TEXTE_FAIBLE)
        y += 116

    carte(b, 18, y, L_PHONE - 36, 66)
    b.t(32, y + 14, "Aucune autre course assignée", 10, semi=True, couleur=TEXTE_FAIBLE)
    b.t(32, y + 34, "Le transporteur reçoit les propositions sur son portail.", 9, couleur=TEXTE_FAIBLE)

    bouton(b, 18, H_PHONE - H_PIEDS - 62, L_PHONE - 36, 46, "Synchroniser (3)")
    pied_ecran(b, "CHF-02", "Mes courses")
    return b


def ecran_chf04() -> Toile:
    b = cadre_phone("Chargement")
    b.t(18, 116, "BON-2026-000456", 11, semi=True)
    b.r(18, 138, L_PHONE - 36, 60, contour=TRAIT_FORT, ep=1, arrondi=6)
    b.t(30, 152, "Bon contrôlé — valide", 11, semi=True)
    b.t(30, 172, "Titulaire : Kivu Trans SARL · 200 sacs", 9, couleur=TEXTE_FAIBLE)

    y = 216
    y = champ(b, 18, y, L_PHONE - 36, "Poids réel chargé (kg)", "10 250")
    y = champ(b, 18, y, L_PHONE - 36, "Nombre de sacs chargés", "200")
    y = champ(b, 18, y, L_PHONE - 36, "Numéro de scellé", "4471-B")

    b.t(18, y, "Ticket de pesée", 9, couleur=TEXTE_FAIBLE)
    photo(b, 18, y + 16, L_PHONE - 36, 96, "Photo du ticket — obligatoire")
    y += 128

    alerte(b, 18, y, L_PHONE - 36,
           "Écart supérieur à la tolérance : la validation d'un superviseur sera demandée avant clôture.")

    bouton(b, 18, H_PHONE - H_PIEDS - 62, L_PHONE - 36, 46, "Valider le chargement", principal=True)
    pied_ecran(b, "CHF-04", "Enregistrement du chargement")
    return b


def ecran_chf06() -> Toile:
    b = cadre_phone("Livraison")
    b.t(18, 116, "BON-2026-000456 — Zone Gombe, 4e avenue", 10, couleur=TEXTE_FAIBLE)

    b.t(18, 148, "Faites scanner ce QR par le client", 12, semi=True)
    qr(b, 95, 176, 200, graine=23)
    b.t(L_PHONE / 2, 396, "La validation appartient au client", 10,
        couleur=TEXTE_FAIBLE, ancre="ma")

    y = 424
    b.r(18, y, L_PHONE - 36, 56, remplissage=REMPLI, arrondi=6)
    b.t(30, y + 12, "Position enregistrée", 10, semi=True)
    b.t(30, y + 32, "−4,3271 ; 15,3134 · 14:58", 9, couleur=TEXTE_FAIBLE)
    b.t(L_PHONE - 30, y + 28, "GPS", 9, couleur=TEXTE_FAIBLE, ancre="ra")

    b.r(18, y + 68, L_PHONE - 36, 56, remplissage=REMPLI, arrondi=6)
    b.t(30, y + 80, "Photo géolocalisée", 10, semi=True)
    b.t(30, y + 100, "Prise automatiquement à la validation", 9, couleur=TEXTE_FAIBLE)

    alerte(b, 18, y + 138, L_PHONE - 36,
           "Le chauffeur ne peut pas valider à la place du client, ni clôturer sans son accord.")

    bouton(b, 18, H_PHONE - H_PIEDS - 62, L_PHONE - 36, 46, "Synchroniser la livraison")
    pied_ecran(b, "CHF-06", "Livraison et preuve")
    return b


# --------------------------------------------------------------------------
# IF-05 — Console de chargement (tablette)
# --------------------------------------------------------------------------
def ecran_chg02() -> Toile:
    b = Toile(1024, 700, ft=1.2)
    b.r(0, 0, 1024, 56, remplissage=(14, 36, 54))
    b.t(24, 28, "Console de chargement — Usine de Kimpese", 15, semi=True, couleur=BLANC, ancre="lm")
    b.t(1000, 28, "Agent : M. Nsimba · poste 2", 11, couleur=(200, 210, 220), ancre="rm")

    # zone de scan
    b.r(24, 80, 470, 420, contour=TRAIT_FORT, ep=1.5, arrondi=8)
    b.rp(60, 116, 398, 316, contour=TRAIT, ep=1.5, fond=FOND)
    b.t(259, 250, "Scannez le QR du bon", 16, semi=True, couleur=TEXTE_FAIBLE, ancre="ma")
    b.t(259, 276, "ou saisissez le numéro BON-", 11, couleur=TEXTE_FAIBLE, ancre="ma")
    b.r(120, 316, 278, 44, contour=TRAIT_FORT, ep=1, arrondi=6, remplissage=BLANC)
    b.t(140, 338, "BON-2026-000456", 12, ancre="lm")
    b.t(259, 400, "Verdict en moins d'une seconde", 9, couleur=TEXTE_FAIBLE, ancre="ma")
    bouton(b, 60, 440, 398, 44, "Scanner un autre bon")

    # verdict
    b.r(518, 80, 482, 420, contour=ACCENT, ep=2, arrondi=8)
    b.r(518, 80, 482, 74, remplissage=ACCENT_PALE, arrondi=8)
    b.t(542, 116, "BON REFUSÉ", 24, gras=True, couleur=ACCENT, ancre="lm")
    b.t(542, 172, "Motif : bon déjà chargé", 12, semi=True)
    b.t(542, 196, "Le 06/11/2026 à 15:42, par l'agent M. Nsimba,", 10, couleur=TEXTE_FAIBLE)
    b.t(542, 214, "au point de chargement 2.", 10, couleur=TEXTE_FAIBLE)

    y = 250
    for lib, val in (
        ("Numéro", "BON-2026-000456"),
        ("Titulaire", "Kivu Trans SARL"),
        ("Quantité", "200 sacs — CEM II 42,5"),
        ("Option", "Avec transport PPC"),
    ):
        b.t(542, y, lib, 9, couleur=TEXTE_FAIBLE)
        b.t(976, y, val, 10, semi=True, ancre="ra")
        y += 24
        b.ligne(542, y - 8, 976, y - 8, TRAIT)

    b.tl(542, 360, 434,
         "Aucune sortie n'est possible sur un bon déjà utilisé. Une correction passe par un litige, jamais par une réécriture.",
         10, couleur=TEXTE_FAIBLE)
    bouton(b, 542, 430, 216, 46, "Ouvrir un litige")
    bouton(b, 770, 430, 206, 46, "Clôturer le poste")

    # journal
    b.t(24, 528, "Dernières opérations de mon poste", 11, semi=True)
    y = 552
    for h, code, etat in (("15:42", "BON-2026-000456", "chargé"),
                          ("15:20", "BON-2026-000441", "chargé"),
                          ("14:58", "BON-2026-000437", "refusé — expiré")):
        b.t(24, y, h, 10, couleur=TEXTE_FAIBLE)
        b.t(84, y, code, 10, semi=True)
        b.t(320, y, etat, 10, couleur=TEXTE_FAIBLE)
        y += 22
        b.ligne(24, y - 6, 996, y - 6, TRAIT)

    b.t(24, 660, "CHG-02 · Contrôle du bon — IF-05 Console de chargement", 10, couleur=TEXTE_FAIBLE)
    return b


# --------------------------------------------------------------------------
# IF-04 — Portail transporteur (bureau)
# --------------------------------------------------------------------------
def rail_lateral(b: Toile, entrees, actif=0, hauteur=760,
                 titre="APIX Transporteur", sous_titre="Kivu Logistique"):
    b.r(0, 0, 220, hauteur, remplissage=(14, 36, 54))
    b.t(24, 34, titre, 13, semi=True, couleur=BLANC)
    b.t(24, 54, sous_titre, 10, couleur=(160, 178, 195))
    y = 100
    for i, e in enumerate(entrees):
        if i == actif:
            b.r(12, y - 12, 196, 36, remplissage=(27, 58, 87), arrondi=6)
        b.t(28, y + 2, e, 11, couleur=BLANC if i == actif else (175, 190, 205), ancre="lm")
        y += 44


def ecran_trp03() -> Toile:
    b = Toile(1280, 760, ft=1.2)
    rail_lateral(b, ["Tableau de bord", "Courses proposées", "Mes chauffeurs", "Mes engins", "Règlements"])

    b.t(252, 40, "Course proposée", 20, gras=True)
    b.t(252, 70, "Proposition reçue le 07/11/2026 à 14:40 — réponse attendue avant 15:10", 10,
        couleur=TEXTE_FAIBLE)

    b.r(252, 100, 620, 330, contour=TRAIT, ep=1, arrondi=8)
    b.t(276, 122, "Détail de la course", 12, semi=True)
    y = 156
    for lib, val in (
        ("Numéro de bon", "BON-2026-000456"),
        ("Axe", "Kimpese → Gombe (38 km)"),
        ("Marchandise", "200 sacs CEM II 42,5 — 10 000 kg"),
        ("Engin requis", "Camion plateau 15 t, caisse bâchée"),
        ("Point de chargement", "Usine de Kimpese — quai 2"),
        ("Fenêtre de chargement", "Aujourd'hui entre 14:30 et 16:00"),
        ("Montant du transport", "640,00 $"),
    ):
        b.t(276, y, lib, 10, couleur=TEXTE_FAIBLE)
        gras = lib == "Montant du transport"
        b.t(848, y, val, 11 if not gras else 13, semi=True, ancre="ra")
        y += 32
        b.ligne(276, y - 12, 848, y - 12, TRAIT)

    b.r(892, 100, 356, 330, contour=TRAIT, ep=1, arrondi=8)
    b.t(916, 122, "Compatibilité de votre flotte", 12, semi=True)
    y = 158
    for lib, val in (("Engin proposé", "CAM-04 · 15 t"), ("Homologation", "valide jusqu'au 03/2027"),
                     ("Assurance", "valide jusqu'au 12/2026"), ("Chauffeur affecté", "J. Mbala")):
        b.t(916, y, lib, 9, couleur=TEXTE_FAIBLE)
        b.t(916, y + 16, val, 11, semi=True)
        y += 46

    b.tl(916, 336, 308,
         "Seuls les engins homologués et assurés sont proposés. L'acceptation est ferme : un désistement est tracé.",
         9, couleur=TEXTE_FAIBLE)

    bouton(b, 252, 456, 300, 52, "Accepter la course", principal=True)
    bouton(b, 568, 456, 200, 52, "Refuser")
    b.t(790, 482, "Refus motivé obligatoire", 9, couleur=TEXTE_FAIBLE, ancre="lm")

    b.t(252, 540, "Ce que vous ne voyez pas, et pourquoi", 11, semi=True)
    b.tl(252, 566, 996,
         "Le prix payé par le client, la marge de PPC et le détail de la cotation ne sont jamais affichés au transporteur : il négocie une course, pas la vente de ciment.",
         10, couleur=TEXTE_FAIBLE)

    b.t(252, 726, "TRP-03 · Course proposée — IF-04 Portail transporteur", 10, couleur=TEXTE_FAIBLE)
    return b


# --------------------------------------------------------------------------
# IF-06 — Back-office PPC (bureau)
# --------------------------------------------------------------------------
NAV_BKO = ["Pilotage", "Catalogue et prix", "Zones et barème", "Transporteurs",
           "Paiements sans cotation", "Provisions et règlements", "Litiges",
           "Comptes clients", "Journal d'audit", "Utilisateurs"]


def ecran_bko01() -> Toile:
    b = Toile(1280, 760, ft=1.2)
    rail_lateral(b, NAV_BKO, titre="APIX PPC", sous_titre="Administration PPC")

    b.t(252, 40, "Pilotage des opérations", 20, gras=True)
    b.t(252, 70, "PPC · semaine du 3 au 7 novembre 2026", 10, couleur=TEXTE_FAIBLE)

    cartes = (("Commandes du jour", "42", "+ 8 vs hier"),
              ("Encaissements du jour", "118 400 $", "+ 12 %"),
              ("Courses en cours", "17", "4 à affecter"),
              ("Litiges ouverts", "3", "dont 1 en retard"))
    x = 252
    for titre, valeur, sous in cartes:
        b.r(x, 100, 236, 96, contour=TRAIT, ep=1, arrondi=8)
        b.t(x + 16, 116, titre, 10, couleur=TEXTE_FAIBLE)
        b.t(x + 16, 136, valeur, 22, gras=True)
        b.t(x + 16, 168, sous, 9, couleur=TEXTE_FAIBLE)
        x += 248

    # graphique
    b.r(252, 216, 620, 210, contour=TRAIT, ep=1, arrondi=8)
    b.t(272, 234, "Encaissements par jour", 11, semi=True)
    b.rp(272, 262, 580, 144, contour=TRAIT, ep=1)
    alea = random.Random(3)
    for i in range(7):
        h = 30 + alea.randint(0, 100)
        b.r(292 + i * 80, 406 - h, 46, h, remplissage=REMPLI_FORT)
    for i, j in enumerate(["lun", "mar", "mer", "jeu", "ven", "sam", "dim"]):
        b.t(315 + i * 80, 412, j, 9, couleur=TEXTE_FAIBLE, ancre="ma")

    # répartition
    b.r(892, 216, 356, 210, contour=TRAIT, ep=1, arrondi=8)
    b.t(912, 234, "Canaux d'encaissement", 11, semi=True)
    y = 264
    for lib, part in (("Mobile money et carte", 18), ("Virement bancaire", 47),
                      ("Dépôt avec bordereau", 35)):
        b.t(912, y, lib, 10, couleur=TEXTE_FAIBLE)
        b.t(1228, y, f"{part} %", 10, semi=True, ancre="ra")
        b.r(912, y + 18, 316, 8, remplissage=REMPLI, arrondi=4)
        b.r(912, y + 18, 316 * part / 100, 8, remplissage=TRAIT_FORT, arrondi=4)
        y += 50
    b.t(912, 396, "15 à 20 % seulement passent par un canal intégré", 9, couleur=ACCENT)

    # table
    b.t(252, 448, "Dernières cotations", 11, semi=True)
    entetes = ["Cotation", "Client", "Montant", "État", "Émise"]
    largeurs = [200, 320, 160, 180, 132]
    x = 252
    b.r(252, 472, 992, 30, remplissage=REMPLI)
    for entete, larg in zip(entetes, largeurs):
        b.t(x + 12, 482, entete, 9, semi=True, couleur=TEXTE_FAIBLE)
        x += larg
    y = 502
    for ligne in (("COT-2026-000123", "Kivu Trans SARL", "3 145,00 $", "payée", "14:32"),
                  ("COT-2026-000122", "Dépôt Matadi", "860,00 $", "en attente", "13:07"),
                  ("COT-2026-000121", "Ets Lumière", "12 400,00 $", "virement", "11:45"),
                  ("COT-2026-000120", "Chantier Nord", "2 260,00 $", "expirée", "09:12")):
        x = 252
        for i, (val, larg) in enumerate(zip(ligne, largeurs)):
            b.t(x + 12, y, val, 10, semi=(i == 0))
            x += larg
        y += 30
        b.ligne(252, y - 10, 1244, y - 10, TRAIT)

    b.t(252, 726, "BKO-01 · Tableau de bord — IF-06 Back-office PPC", 10, couleur=TEXTE_FAIBLE)
    return b


def ecran_bko05() -> Toile:
    b = Toile(1280, 760, ft=1.2)
    rail_lateral(b, NAV_BKO, actif=4, titre="APIX PPC", sous_titre="Administration PPC")

    b.t(252, 40, "Paiements reçus sans cotation", 20, gras=True)
    b.t(252, 70, "2 dossiers en attente de rattachement — aucun n'est affecté d'office", 10,
        couleur=ACCENT)

    entetes = ["Dossier", "Référence reçue", "Client", "Montant", "Reçu le", "Statut"]
    largeurs = [150, 200, 220, 150, 140, 132]
    x = 252
    b.r(252, 100, 620, 30, remplissage=REMPLI)
    for entete, larg in zip(entetes, largeurs):
        b.t(x + 12, 110, entete, 9, semi=True, couleur=TEXTE_FAIBLE)
        x += larg
    y = 130
    for ligne in (("RAP-2026-0007", "VIR-88213", "Kivu Trans SARL", "3 145,00 $", "07/11 09:40", "à rattacher"),
                  ("RAP-2026-0006", "MM-55210", "Ets Lumière", "980,00 $", "06/11 16:12", "à rattacher")):
        x = 252
        for i, (val, larg) in enumerate(zip(ligne, largeurs)):
            b.t(x + 12, y, val, 10, semi=(i == 0), couleur=ACCENT if i == 5 else TEXTE)
            x += larg
        y += 34
        b.ligne(252, y - 12, 872, y - 12, TRAIT)

    b.tl(252, 230, 600,
         "Ces fonds sont arrivés sur un compte d'encaissement dédié sans cotation valide. La banque les a acceptés en attente ; le rattachement est la seule voie de régularisation.",
         10, couleur=TEXTE_FAIBLE)

    # panneau de rattachement
    b.r(892, 100, 356, 480, contour=TRAIT_FORT, ep=1.5, arrondi=8)
    b.t(916, 122, "Rattacher le dossier RAP-2026-0007", 11, semi=True)
    b.t(916, 144, "Kivu Trans SARL — 3 145,00 $", 10, couleur=TEXTE_FAIBLE)

    b.t(916, 180, "Cotation du même client", 9, couleur=TEXTE_FAIBLE)
    b.r(916, 196, 308, 42, contour=TRAIT, ep=1, arrondi=6)
    b.t(930, 217, "Rechercher par numéro ou montant", 10, couleur=TEXTE_FAIBLE, ancre="lm")

    for code, montant in (("COT-2026-000123", "3 145,00 $"), ("COT-2026-000119", "3 145,00 $")):
        b.r(916, 252, 308, 48, contour=TRAIT, ep=1, arrondi=6)
        b.t(930, 268, code, 10, semi=True)
        b.t(930, 286, montant, 9, couleur=TEXTE_FAIBLE)
        b.r(1186, 266, 24, 24, contour=TRAIT_FORT, ep=1, arrondi=12)

    b.t(916, 324, "Motif du rattachement (obligatoire)", 9, couleur=TEXTE_FAIBLE)
    b.r(916, 340, 308, 90, contour=TRAIT, ep=1, arrondi=6)
    for i in range(3):
        b.r(930, 356 + i * 18, 260 - i * 30, 7, remplissage=REMPLI_FORT, arrondi=3)

    alerte(b, 916, 448, 308, "Aucune affectation automatique : le rattachement est tracé et relu.", 62)

    bouton(b, 916, 524, 308, 46, "Rattacher et tracer", principal=True)

    b.t(252, 726, "BKO-05 · Paiements sans cotation — IF-06 Back-office PPC", 10, couleur=TEXTE_FAIBLE)
    return b


def ecran_bko07() -> Toile:
    b = Toile(1280, 760, ft=1.2)
    rail_lateral(b, NAV_BKO, actif=6, titre="APIX PPC", sous_titre="Administration PPC")

    b.t(252, 40, "Litige LIT-2026-000012", 20, gras=True)
    b.t(252, 70, "Kivu Trans SARL contre transporteur Kivu Logistique — écart de 3 sacs", 10,
        couleur=TEXTE_FAIBLE)

    # dossier
    b.r(252, 100, 300, 300, contour=TRAIT, ep=1, arrondi=8)
    b.t(272, 120, "Dossier", 11, semi=True)
    y = 150
    for lib, val in (("Ouvert le", "07/11/2026 15:05"), ("Montant contesté", "37,20 $"),
                     ("Part gelée", "37,20 $"), ("Délai de recours", "15 jours")):
        b.t(272, y, lib, 9, couleur=TEXTE_FAIBLE)
        b.t(272, y + 16, val, 10, semi=True)
        y += 44

    # preuves
    b.r(572, 100, 400, 300, contour=TRAIT, ep=1, arrondi=8)
    b.t(592, 120, "Dossier de preuve", 11, semi=True)
    for i, lib in enumerate(("Photo de livraison", "QR nominatif", "Ticket de pesée", "Scellé")):
        x = 592 + (i % 2) * 184
        yy = 148 + (i // 2) * 104
        photo(b, x, yy, 168, 76, lib)
    b.tl(592, 356, 360, "Toutes les pièces sont horodatées et signées ; aucune ne peut être modifiée.",
         9, couleur=TEXTE_FAIBLE)

    # décision
    b.r(992, 100, 256, 424, contour=TRAIT_FORT, ep=1.5, arrondi=8)
    b.t(1012, 118, "Décision", 11, semi=True)
    y = 144
    for lib in ("Faveur client", "Faveur transporteur", "Partage"):
        b.r(1012, y, 20, 20, contour=TRAIT_FORT, ep=1, arrondi=10)
        b.t(1042, y + 10, lib, 10, ancre="lm")
        y += 32
    b.t(1012, y + 2, "Montant retenu", 9, couleur=TEXTE_FAIBLE)
    b.r(1012, y + 18, 216, 36, contour=TRAIT, ep=1, arrondi=6)
    b.t(1026, y + 36, "37,20 $", 10, ancre="lm")
    b.t(1012, y + 66, "Montant libéré", 9, couleur=TEXTE_FAIBLE)
    b.r(1012, y + 82, 216, 36, contour=TRAIT, ep=1, arrondi=6)
    b.t(1026, y + 100, "602,80 $", 10, ancre="lm")
    b.t(1012, y + 128, "Motif (obligatoire)", 9, couleur=TEXTE_FAIBLE)
    b.r(1012, y + 144, 216, 52, contour=TRAIT, ep=1, arrondi=6)
    bouton(b, 1012, 478, 216, 40, "Enregistrer la décision", principal=True)

    # chronologie
    b.t(252, 428, "Chronologie", 11, semi=True)
    y = 456
    for h, texte in (("07/11 14:58", "Livraison déclarée par le chauffeur J. Mbala"),
                     ("07/11 15:02", "Client : 197 sacs constatés sur 200"),
                     ("07/11 15:05", "Litige ouvert, 37,20 $ gelés automatiquement"),
                     ("07/11 15:20", "Transporteur : conteste l'écart, demande la pesée d'arrivée")):
        b.t(252, y, h, 10, couleur=TEXTE_FAIBLE)
        b.t(372, y, texte, 10)
        y += 26
        b.ligne(252, y - 10, 872, y - 10, TRAIT)

    # ce que la décision déclenche : comble le vide et rappelle la règle
    b.r(252, 588, 720, 86, remplissage=BANDE, arrondi=6)
    b.t(272, 602, "Ce que la décision déclenche", 10, semi=True)
    b.tl(272, 622, 680,
         "Le montant retenu est déduit du règlement du transporteur ; le montant libéré lui est payé dès "
         "l'enregistrement. Les deux parties sont notifiées sur leur canal préféré.",
         9, couleur=TEXTE_FAIBLE)

    b.t(252, 726, "BKO-07 · Instruction d'un litige — IF-06 Back-office PPC", 10, couleur=TEXTE_FAIBLE)
    return b


# --------------------------------------------------------------------------
# IF-07 — Console dépôt (tablette)
# --------------------------------------------------------------------------
def ecran_dep01() -> Toile:
    b = Toile(1024, 700, ft=1.2)
    b.r(0, 0, 1024, 56, remplissage=(14, 36, 54))
    b.t(24, 28, "Console dépôt — Dépôt de Matadi", 15, semi=True, couleur=BLANC, ancre="lm")
    b.t(1000, 28, "Agent : Mme Lelo", 11, couleur=(200, 210, 220), ancre="rm")

    b.r(24, 80, 460, 400, contour=TRAIT_FORT, ep=1.5, arrondi=8)
    b.rp(60, 112, 388, 300, contour=TRAIT, ep=1.5, fond=FOND)
    b.t(254, 250, "Scannez le bon de sortie", 16, semi=True, couleur=TEXTE_FAIBLE, ancre="ma")
    b.t(254, 276, "ou saisissez son numéro", 11, couleur=TEXTE_FAIBLE, ancre="ma")
    b.r(110, 310, 288, 44, contour=TRAIT_FORT, ep=1, arrondi=6, remplissage=BLANC)
    b.t(130, 332, "BON-2026-000460", 12, ancre="lm")
    bouton(b, 60, 436, 388, 44, "Scanner un autre bon")

    b.r(508, 80, 492, 400, contour=TRAIT_FORT, ep=1.5, arrondi=8)
    b.r(508, 80, 492, 74, remplissage=REMPLI, arrondi=8)
    b.t(532, 116, "BON VALIDE", 24, gras=True, ancre="lm")
    b.t(532, 172, "Remise autorisée", 12, semi=True)
    y = 204
    for lib, val in (("Numéro", "BON-2026-000460"), ("Titulaire", "Kivu Trans SARL"),
                     ("Marchandise", "80 sacs CEM II 42,5"), ("Option", "Enlèvement par le client")):
        b.t(532, y, lib, 9, couleur=TEXTE_FAIBLE)
        b.t(976, y, val, 10, semi=True, ancre="ra")
        y += 26
        b.ligne(532, y - 10, 976, y - 10, TRAIT)

    b.t(532, 320, "Code d'enlèvement présenté : 481 902", 10)
    b.tl(532, 344, 444,
         "Le bon est à usage unique : après la remise, il disparaît définitivement de la file du dépôt.",
         10, couleur=TEXTE_FAIBLE)
    bouton(b, 532, 410, 444, 48, "Remettre la marchandise", principal=True)

    b.t(24, 512, "File du dépôt", 11, semi=True)
    y = 538
    for code, client, etat in (("BON-2026-000462", "Ets Lumière", "en attente"),
                               ("BON-2026-000461", "Chantier Nord", "en attente"),
                               ("BON-2026-000460", "Kivu Trans SARL", "sélectionné")):
        b.t(24, y, code, 10, semi=True)
        b.t(220, y, client, 10)
        b.t(460, y, etat, 10, couleur=TEXTE_FAIBLE)
        y += 26
        b.ligne(24, y - 10, 996, y - 10, TRAIT)

    b.t(24, 660, "DEP-01 · Réception d'un bon — IF-07 Console dépôt", 10, couleur=TEXTE_FAIBLE)
    return b


# --------------------------------------------------------------------------
# Planches
# --------------------------------------------------------------------------
PLANCHES = [
    ("p01-client-catalogue-cotation", "IF-01 · Application client — catalogue et demande de cotation",
     ["cli04", "cli07"]),
    ("p02-client-cotation-paiement", "IF-01 · Application client — cotation et choix du paiement",
     ["cli08", "cli09"]),
    ("p03-client-bon-reception", "IF-01 · Application client — bon de commande et réception",
     ["cli11", "cli13"]),
    ("p04-chauffeur", "IF-03 · Application chauffeur — courses, chargement, livraison",
     ["chf02", "chf04", "chf06"]),
    ("p05-chargement-controle", "IF-05 · Console de chargement — contrôle du bon", ["chg02"]),
    ("p06-transporteur-course", "IF-04 · Portail transporteur — course proposée", ["trp03"]),
    ("p07-backoffice-pilotage", "IF-06 · Back-office PPC — pilotage", ["bko01"]),
    ("p08-backoffice-sans-cotation", "IF-06 · Back-office PPC — paiements sans cotation", ["bko05"]),
    ("p09-backoffice-litige", "IF-06 · Back-office PPC — instruction d'un litige", ["bko07"]),
    ("p10-depot-reception", "IF-07 · Console dépôt — réception d'un bon", ["dep01"]),
]


def construire(nom_fichier: str, ecrans: list[str]) -> Path:
    toiles = [globals()[f"ecran_{cle}"]() for cle in ecrans]
    if len(toiles) == 1:
        planche = toiles[0]
    else:
        ecart = 28
        largeur = sum(t.largeur for t in toiles) + ecart * (len(toiles) - 1) + 2 * ecart
        hauteur = max(t.hauteur for t in toiles) + 2 * ecart
        planche = Toile(largeur, hauteur, fond=FOND)
        x = ecart
        for t in toiles:
            planche.coller(t, x, ecart)
            x += t.largeur + ecart
    chemin = SORTIE / f"{nom_fichier}.png"
    planche.enregistrer(chemin)
    return chemin


def main() -> int:
    analyseur = argparse.ArgumentParser(description="Dessine les wireframes du MVP.")
    analyseur.add_argument("--only", help="filtre sur le nom de planche")
    arguments = analyseur.parse_args()

    SORTIE.mkdir(parents=True, exist_ok=True)
    produites = 0
    for nom, titre, ecrans in PLANCHES:
        if arguments.only and arguments.only.lower() not in nom.lower():
            continue
        chemin = construire(nom, ecrans)
        poids = chemin.stat().st_size // 1024
        print(f"[OK] {chemin.relative_to(RACINE)} — {titre} ({poids} Ko)")
        produites += 1
    print(f"{produites} planche(s) produite(s) dans {SORTIE.relative_to(RACINE)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
