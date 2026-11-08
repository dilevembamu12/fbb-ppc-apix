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
# Composants conversationnels (WhatsApp) et diagrammes de flux
# --------------------------------------------------------------------------
def entete_whatsapp(b: Toile, nom="PPC Ciment", sous="Compte professionnel"):
    b.r(0, 38, L_PHONE, 64, remplissage=(240, 240, 240))
    b.t(18, 66, "‹", 24)
    b.r(46, 50, 40, 40, remplissage=REMPLI_FORT, arrondi=20)
    b.t(66, 70, "PPC", 10, semi=True, couleur=TEXTE_FAIBLE, ancre="mm")
    b.t(98, 60, nom, 12, semi=True)
    b.t(98, 80, sous, 9, couleur=TEXTE_FAIBLE)
    b.r(L_PHONE - 42, 60, 24, 24, contour=TRAIT_FORT, ep=1, arrondi=12)
    b.ligne(0, 102, L_PHONE, 102, TRAIT)


def bulle(b: Toile, y, texte, sortante=False, largeur_max=286, taille=10):
    """Message conversationnel ; renvoie l'ordonnée suivante."""
    largeur = min(largeur_max, b.mesurer(texte, taille) + 28)
    lignes = b.nb_lignes(texte, largeur - 26, taille)
    hauteur = 14 + lignes * (taille * 1.35)
    x = L_PHONE - 16 - largeur if sortante else 16
    b.r(x, y, largeur, hauteur, remplissage=REMPLI if sortante else BLANC,
        contour=None if sortante else TRAIT, ep=1, arrondi=8)
    b.tl(x + 13, y + 7, largeur - 26, texte, taille, interligne=1.35)
    return y + hauteur + 8


def boutons_rapides(b: Toile, y, libelles, largeur=286, principal=0):
    """Réponses rapides façon WhatsApp : pastilles empilées sous le message."""
    for i, libelle in enumerate(libelles):
        if i == principal:
            b.r(16, y, largeur, 32, contour=ACCENT, ep=1.5, arrondi=8, remplissage=ACCENT_PALE)
            b.t(16 + largeur / 2, y + 16, libelle, 10, semi=True, couleur=ACCENT, ancre="mm")
        else:
            b.r(16, y, largeur, 32, contour=TRAIT_FORT, ep=1, arrondi=8)
            b.t(16 + largeur / 2, y + 16, libelle, 10, ancre="mm")
        y += 40
    return y + 4


def carte_dans_bulle(b: Toile, y, titre, lignes, action, largeur=286, note=None):
    """Carte de cotation, de bon ou de reçu, insérée dans la conversation."""
    hauteur = 58 + len(lignes) * 20 + 46 + (18 if note else 0)
    b.r(16, y, largeur, hauteur, remplissage=BLANC, contour=TRAIT_FORT, ep=1, arrondi=8)
    b.t(30, y + 16, titre, 10, semi=True)
    yy = y + 40
    for libelle, valeur in lignes:
        b.t(30, yy, libelle, 9, couleur=TEXTE_FAIBLE)
        b.t(16 + largeur - 16, yy, valeur, 9, semi=True, ancre="ra")
        yy += 20
    if note:
        b.t(30, yy + 2, note, 9, couleur=TEXTE_FAIBLE)
        yy += 18
    bouton(b, 30, yy + 10, largeur - 28, 34, action, principal=True, taille=10)
    return y + hauteur + 10


def bandeau_systeme(b: Toile, y, texte):
    """Ligne de système centrée, comme dans une conversation."""
    largeur = b.mesurer(texte, 9) + 24
    b.r((L_PHONE - largeur) / 2, y, largeur, 24, remplissage=REMPLI, arrondi=12)
    b.t(L_PHONE / 2, y + 12, texte, 9, couleur=TEXTE_FAIBLE, ancre="mm")
    return y + 32


def barre_saisie(b: Toile):
    y = H_PHONE - H_PIEDS - 50
    b.r(0, y, L_PHONE, 50, remplissage=(240, 240, 240))
    b.ligne(0, y, L_PHONE, y, TRAIT)
    b.r(12, y + 9, L_PHONE - 64, 32, remplissage=BLANC, contour=TRAIT, ep=1, arrondi=16)
    b.t(28, y + 25, "Écrivez un message", 10, couleur=TEXTE_FAIBLE, ancre="lm")
    b.r(L_PHONE - 44, y + 11, 30, 30, remplissage=TEXTE_FAIBLE, arrondi=15)
    b.d.polygon([((L_PHONE - 32) * b.e, (y + 20) * b.e),
                 ((L_PHONE - 32) * b.e, (y + 32) * b.e),
                 ((L_PHONE - 22) * b.e, (y + 26) * b.e)], fill=BLANC)


def noeud(b: Toile, x, y, w, h, titre, sous=None, accent=False, taille=11):
    b.r(x, y, w, h, contour=ACCENT if accent else TRAIT_FORT, ep=1.5, arrondi=8,
        remplissage=ACCENT_PALE if accent else BLANC)
    if sous:
        b.tl(x + 14, y + 12, w - 28, titre, taille, semi=True, interligne=1.25)
        b.tl(x + 14, y + h - 28, w - 28, sous, 9, couleur=TEXTE_FAIBLE, interligne=1.25)
    else:
        b.tl(x + 14, y + h / 2 - 9, w - 28, titre, taille, semi=True, interligne=1.25)


def fleche(b: Toile, x1, y1, x2, y2, couleur=TRAIT_FORT):
    import math
    b.ligne(x1, y1, x2, y2, couleur, 1.5)
    angle = math.atan2(y2 - y1, x2 - x1)
    longueur, ouverture = 9.0, 0.42
    points = [((x2 + longueur * math.cos(angle + d)) * b.e,
               (y2 + longueur * math.sin(angle + d)) * b.e)
              for d in (0, math.pi - ouverture, math.pi + ouverture)]
    b.d.polygon(points, fill=couleur)


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
    b.t(252, 70, "PPC · cette semaine", 10, couleur=TEXTE_FAIBLE)

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


def lien(b: Toile, points, couleur=TRAIT_FORT):
    """Polyligne fléchée : segments droits, pointe sur le dernier."""
    for (x1, y1), (x2, y2) in zip(points, points[1:-1]):
        b.ligne(x1, y1, x2, y2, couleur, 1.5)
    fleche(b, points[-2][0], points[-2][1], points[-1][0], points[-1][1], couleur)


def decision(b: Toile, x, y, w, h, question):
    """Losange de décision, dessiné comme un hexagone aplati pour rester lisible."""
    b.r(x, y, w, h, contour=TRAIT_FORT, ep=1.5, arrondi=10)
    b.tl(x + 16, y + h / 2 - 9, w - 32, question, 10, semi=True, interligne=1.25)


# --------------------------------------------------------------------------
# IF-09 — Console d'automatisation et de configuration des canaux
# --------------------------------------------------------------------------
NAV_CNL = ["Vue d'ensemble", "Canaux", "Modèles de messages", "Règles de routage",
           "Conversations", "Bac à sable", "Journal d'envoi"]


def ecran_cnl01() -> Toile:
    b = Toile(1280, 760, ft=1.2)
    rail_lateral(b, NAV_CNL, actif=1, titre="APIX Canaux", sous_titre="Administration PPC")

    b.t(252, 40, "Canaux externes", 20, gras=True)
    b.t(252, 70, "6 canaux déclarés · 4 actifs · 1 en préparation · 1 non ouvert", 10,
        couleur=TEXTE_FAIBLE)

    entetes = ["Canal", "Usage", "État", "Volume 7 j", "Coût unitaire", "Dernier incident"]
    largeurs = [190, 250, 150, 120, 130, 152]
    x = 252
    b.r(252, 100, 992, 30, remplissage=REMPLI)
    for entete, larg in zip(entetes, largeurs):
        b.t(x + 12, 110, entete, 9, semi=True, couleur=TEXTE_FAIBLE)
        x += larg

    lignes = (
        ("WhatsApp Business", "cotation, paiement, bon", "actif", "812 messages", "0,04 $ / conv.", "—"),
        ("E-mail", "reçus, dossier de preuve", "actif", "340 envois", "0,01 $", "—"),
        ("SMS", "notifications critiques", "actif", "1 240 envois", "0,03 $", "—"),
        ("Notification applicative", "changement d'état", "actif", "2 100", "inclus", "—"),
        ("USSD", "zones sans internet", "en préparation", "—", "à négocier", "—"),
        ("Telegram", "canal complémentaire", "non ouvert", "—", "0,00 $", "—"),
    )
    y = 130
    for ligne in lignes:
        x = 252
        for i, (val, larg) in enumerate(zip(ligne, largeurs)):
            couleur = TEXTE
            if i == 2:
                couleur = ACCENT if val in ("non ouvert", "en préparation") else TEXTE
            b.t(x + 12, y, val, 10, semi=(i == 0), couleur=couleur)
            x += larg
        y += 34
        b.ligne(252, y - 12, 1244, y - 12, TRAIT)

    # panneau latéral : ce que la console ne permet pas
    b.r(252, 380, 470, 250, contour=TRAIT_FORT, ep=1.5, arrondi=8)
    b.t(272, 400, "Ce que cette console ne peut pas faire", 11, semi=True)
    y = 430
    for interdit in ("Modifier un prix ou un barème",
                     "Créer un bon de commande",
                     "Désactiver le SMS d'un événement critique",
                     "Écrire un message hors modèle approuvé",
                     "Répondre à un client sans identité vérifiée"):
        b.r(272, y - 3, 14, 14, contour=TRAIT_FORT, ep=1, arrondi=3)
        b.ligne(275, y, 283, y + 8, ACCENT, 1.5)
        b.ligne(283, y, 275, y + 8, ACCENT, 1.5)
        b.t(296, y, interdit, 10)
        y += 30

    b.r(742, 380, 502, 250, contour=TRAIT, ep=1, arrondi=8)
    b.t(762, 400, "Conditions d'ouverture d'un canal", 11, semi=True)
    y = 430
    for etape in ("1. Compte marchand validé et numéro d'entreprise vérifié",
                  "2. Modèles de messages soumis et approuvés par le canal",
                  "3. Test de bout en bout réussi dans le bac à sable",
                  "4. Plafond de messages et budget quotidien renseignés",
                  "5. Astreinte de reprise humaine désignée"):
        b.t(762, y, etape, 10, couleur=TEXTE_FAIBLE)
        y += 30

    b.t(252, 660, "Un canal ne s'active pas par un bouton : il s'active quand ses cinq conditions sont réunies.",
        10, couleur=ACCENT)
    b.t(252, 726, "CNL-01 · Tableau des canaux — IF-09 Console des canaux", 10, couleur=TEXTE_FAIBLE)
    return b


def ecran_cnl03() -> Toile:
    b = Toile(1280, 760, ft=1.2)
    rail_lateral(b, NAV_CNL, actif=3, titre="APIX Canaux", sous_titre="Administration PPC")

    b.t(252, 40, "Règles de routage des messages", 20, gras=True)
    b.t(252, 70, "Un événement, plusieurs canaux : l'ordre et le repli sont décidés ici, une seule fois", 10,
        couleur=TEXTE_FAIBLE)

    entetes = ["Événement", "WhatsApp", "SMS", "E-mail", "Appli", "Délai", "Repli"]
    largeurs = [230, 120, 100, 100, 100, 110, 232]
    x = 252
    b.r(252, 100, 992, 30, remplissage=REMPLI)
    for entete, larg in zip(entetes, largeurs):
        b.t(x + 10, 110, entete, 9, semi=True, couleur=TEXTE_FAIBLE)
        x += larg

    lignes = (
        ("Cotation émise", "oui", "non", "oui", "oui", "immédiat", "SMS à 5 min"),
        ("Paiement confirmé", "oui", "oui", "oui", "oui", "immédiat", "SMS à 2 min"),
        ("Bon de commande émis", "oui", "non", "oui", "oui", "immédiat", "e-mail à 5 min"),
        ("Chargement certifié", "oui", "non", "non", "oui", "immédiat", "SMS si 2 échecs"),
        ("Livraison prouvée", "oui", "oui", "oui", "oui", "immédiat", "SMS à 5 min"),
        ("Litige ouvert", "oui", "oui", "oui", "oui", "immédiat", "agent sous 1 h"),
        ("Décision de litige", "oui", "oui", "oui", "oui", "immédiat", "agent sous 1 h"),
    )
    y = 130
    for ligne in lignes:
        x = 252
        for i, (val, larg) in enumerate(zip(ligne, largeurs)):
            couleur = TEXTE_FAIBLE if val == "non" else TEXTE
            b.t(x + 10, y, val, 10, semi=(i == 0), couleur=couleur)
            x += larg
        y += 32
        b.ligne(252, y - 11, 1244, y - 11, TRAIT)

    b.r(252, 372, 470, 240, contour=TRAIT, ep=1, arrondi=8)
    b.t(272, 392, "Règles de priorité appliquées avant l'envoi", 11, semi=True)
    y = 422
    for regle in ("Canal préféré déclaré par le client, sinon WhatsApp",
                  "Langue du dernier échange : français ou lingala",
                  "Heures calmes 21 h – 6 h : mise en file, sauf paiement et litige",
                  "Plafond de 3 messages par client et par jour",
                  "Un message de sécurité n'est jamais désactivable"):
        b.t(272, y, regle, 10, couleur=TEXTE_FAIBLE)
        y += 30

    b.r(742, 372, 502, 240, contour=TRAIT_FORT, ep=1.5, arrondi=8)
    b.t(762, 392, "Test de la règle « Litige ouvert »", 11, semi=True)
    b.t(762, 420, "Simulation du 07/11/2026 à 15 h 05", 9, couleur=TEXTE_FAIBLE)
    y = 448
    for canal, detail in (("WhatsApp Business", "envoyé · 15:05:02"),
                          ("SMS", "envoyé · 15:05:03"),
                          ("E-mail", "envoyé · 15:05:04"),
                          ("Reprise humaine", "ticket ouvert si non délivré sous 1 h")):
        b.t(762, y, canal, 10, semi=True)
        b.t(1224, y, detail, 9, couleur=TEXTE_FAIBLE, ancre="ra")
        y += 28
        b.ligne(762, y - 10, 1224, y - 10, TRAIT)

    b.t(252, 640, "Le routage est vérifié par un test avant publication : une règle non testée n'est jamais active.",
        10, couleur=ACCENT)
    b.t(252, 726, "CNL-03 · Règles de routage — IF-09 Console des canaux", 10, couleur=TEXTE_FAIBLE)
    return b


def ecran_cnl04() -> Toile:
    b = Toile(1280, 760, ft=1.2)
    rail_lateral(b, NAV_CNL, actif=4, titre="APIX Canaux", sous_titre="Administration PPC")

    b.t(252, 40, "Conversations", 20, gras=True)
    b.t(252, 70, "2 conversations demandent une reprise humaine", 10, couleur=ACCENT)

    # liste des conversations
    b.r(252, 96, 320, 500, contour=TRAIT, ep=1, arrondi=8)
    y = 112
    for numero, apercu, etat in (("+243 ••• 412", "Je veux payer autrement", "à reprendre"),
                                 ("+243 ••• 907", "Où est mon camion ?", "à reprendre"),
                                 ("+243 ••• 331", "Cotation payée", "bot"),
                                 ("+243 ••• 118", "Merci", "clos")):
        if etat == "à reprendre":
            b.r(252, y - 6, 320, 92, remplissage=ACCENT_PALE)
        b.t(268, y + 4, numero, 10, semi=True)
        b.t(268, y + 26, apercu, 10, couleur=TEXTE_FAIBLE)
        b.t(268, y + 48, etat, 9, couleur=ACCENT if etat == "à reprendre" else TEXTE_FAIBLE)
        y += 100
        b.ligne(252, y - 12, 572, y - 12, TRAIT)

    # fil de conversation
    b.r(600, 96, 420, 500, contour=TRAIT, ep=1, arrondi=8)
    b.t(618, 112, "+243 ••• 412 — Kivu Trans SARL", 10, semi=True)
    b.ligne(600, 132, 1020, 132, TRAIT)
    y = 150
    b.r(618, y, 300, 44, remplissage=REMPLI, arrondi=8)
    b.tl(630, y + 8, 276, "Votre cotation COT-2026-000123 attend un paiement de 3 145 $.", 9, interligne=1.3)
    y += 54
    b.r(720, y, 282, 44, remplissage=BLANC, contour=TRAIT, ep=1, arrondi=8)
    b.tl(732, y + 8, 258, "Je veux payer autrement, le virement prend trop de temps.", 9, interligne=1.3)
    y += 54
    b.r(618, y, 344, 56, remplissage=REMPLI, arrondi=8)
    b.tl(630, y + 8, 320,
         "Je transmets à un agent PPC : ce montant dépasse ce que je peux régler ici.", 9, interligne=1.3)
    y += 66
    b.r(600, y, 420, 40, remplissage=BANDE)
    b.t(618, y + 14, "Le bot a passé la main — motif : demande hors périmètre", 9, couleur=ACCENT)
    y += 54
    b.r(618, y, 300, 40, remplissage=REMPLI, arrondi=8)
    b.tl(630, y + 8, 276, "Bonjour, je suis Nadine, je m'occupe de votre dossier.", 9, interligne=1.3)

    # panneau contexte
    b.r(1044, 96, 200, 500, contour=TRAIT_FORT, ep=1.5, arrondi=8)
    b.t(1060, 112, "Contexte", 10, semi=True)
    y = 140
    for lib, val in (("Client", "Kivu Trans SARL"), ("Vérifié", "oui"),
                     ("Plafond", "2 500 $"), ("Cotation", "COT-2026-000123"),
                     ("Montant", "3 145,00 $"), ("Bon", "non émis")):
        b.t(1060, y, lib, 9, couleur=TEXTE_FAIBLE)
        b.t(1060, y + 15, val, 10, semi=True)
        y += 42
    bouton(b, 1060, 412, 168, 36, "Reprendre la main", principal=True, taille=10)
    bouton(b, 1060, 456, 168, 36, "Renvoyer au bot", taille=10)
    b.tl(1060, 502, 168, "La reprise ne permet ni de changer un prix, ni de créer un bon.", 9,
         couleur=TEXTE_FAIBLE)

    b.r(252, 616, 992, 74, remplissage=BANDE, arrondi=6)
    b.t(272, 630, "Ce que l'agent peut faire", 10, semi=True)
    b.tl(272, 650, 950,
         "Renseigner, rassurer, relancer un paiement, ouvrir un litige. Il ne peut pas accorder de remise, "
         "ni contourner un plafond : ces décisions passent par une dérogation nominative tracée.",
         9, couleur=TEXTE_FAIBLE)

    b.t(252, 726, "CNL-04 · Reprise humaine d'une conversation — IF-09 Console des canaux", 10,
        couleur=TEXTE_FAIBLE)
    return b


def ecran_cnl02() -> Toile:
    b = Toile(1280, 760, ft=1.2)
    rail_lateral(b, NAV_CNL, actif=2, titre="APIX Canaux", sous_titre="Administration PPC")

    b.t(252, 40, "Modèles de messages", 20, gras=True)
    b.t(252, 70, "12 modèles · 9 approuvés · 2 en attente d'approbation · 1 rejeté", 10,
        couleur=TEXTE_FAIBLE)

    # liste des modèles
    b.r(252, 100, 420, 500, contour=TRAIT, ep=1, arrondi=8)
    y = 116
    modeles = (
        ("MSG-COT-01", "Cotation émise", "WhatsApp · français", "approuvé"),
        ("MSG-COT-02", "Cotation émise", "WhatsApp · lingala", "en attente"),
        ("MSG-PAY-01", "Paiement confirmé", "WhatsApp · français", "approuvé"),
        ("MSG-BON-01", "Bon de commande émis", "WhatsApp · français", "approuvé"),
        ("MSG-LIV-01", "Livraison prouvée", "E-mail · français", "approuvé"),
        ("MSG-LIT-01", "Litige ouvert", "SMS · français", "approuvé"),
        ("MSG-DEC-01", "Décision de litige", "WhatsApp · français", "rejeté"),
    )
    for code, nom, canal, statut in modeles:
        if statut != "approuvé":
            b.r(252, y - 8, 420, 58, remplissage=ACCENT_PALE if statut == "rejeté" else REMPLI)
        b.t(268, y, code, 9, semi=True, couleur=TEXTE_FAIBLE)
        b.t(268, y + 18, nom, 11, semi=True)
        b.t(268, y + 36, canal, 9, couleur=TEXTE_FAIBLE)
        b.t(656, y + 22, statut, 9, semi=True,
            couleur=ACCENT if statut != "approuvé" else TEXTE_FAIBLE, ancre="ra")
        y += 62
        b.ligne(252, y - 10, 672, y - 10, TRAIT)

    # aperçu du modèle
    b.r(700, 100, 544, 500, contour=TRAIT_FORT, ep=1.5, arrondi=8)
    b.t(720, 118, "MSG-COT-01 — Cotation émise", 11, semi=True)
    b.t(1224, 118, "WhatsApp Business", 9, couleur=TEXTE_FAIBLE, ancre="ra")
    b.r(720, 142, 92, 26, contour=TRAIT_FORT, ep=1, arrondi=13, remplissage=BLANC)
    b.t(766, 155, "Français", 9, semi=True, ancre="mm")
    b.r(818, 142, 92, 26, contour=TRAIT, ep=1, arrondi=13)
    b.t(864, 155, "Lingala", 9, couleur=TEXTE_FAIBLE, ancre="mm")

    b.r(720, 186, 504, 150, remplissage=REMPLI, arrondi=8)
    b.tl(738, 202, 468,
         "Bonjour {{client}}, voici votre cotation {{cotation}} d'un montant de {{montant}}, "
         "valable jusqu'au {{date_validite}}. Elle est votre référence de paiement : indiquez-la "
         "lors de votre virement.", 10, interligne=1.45)

    b.t(720, 352, "Variables disponibles", 9, couleur=TEXTE_FAIBLE)
    y = 372
    for nom_var, source in (("{{client}}", "nom du compte vérifié"),
                            ("{{cotation}}", "numéro COT-…"),
                            ("{{montant}}", "total de la cotation"),
                            ("{{date_validite}}", "fin de validité, 48 h")):
        b.r(720, y - 3, 236, 26, contour=TRAIT, ep=1, arrondi=4)
        b.t(732, y + 10, nom_var, 9, semi=True, ancre="lm")
        b.t(970, y + 10, source, 9, couleur=TEXTE_FAIBLE, ancre="lm")
        y += 32

    bouton(b, 720, 520, 240, 44, "Soumettre à l'approbation", principal=True, taille=10)
    bouton(b, 976, 520, 248, 44, "Envoyer un test au bac à sable", taille=10)

    b.r(252, 622, 992, 80, remplissage=BANDE, arrondi=6)
    b.t(272, 636, "Trois règles que la console applique sans exception", 10, semi=True)
    b.tl(272, 656, 950,
         "Un message part toujours d'un modèle approuvé. Une variable non renseignée bloque l'envoi "
         "au lieu d'envoyer un blanc. Un modèle rejeté reste consultable mais inutilisable.",
         9, couleur=TEXTE_FAIBLE)

    b.t(252, 726, "CNL-02 · Modèles de messages — IF-09 Console des canaux", 10, couleur=TEXTE_FAIBLE)
    return b


def ecran_cnl05() -> Toile:
    b = Toile(1280, 760, ft=1.2)
    rail_lateral(b, NAV_CNL, actif=5, titre="APIX Canaux", sous_titre="Administration PPC")

    b.t(252, 40, "Bac à sable", 20, gras=True)
    b.t(252, 70, "Simuler un parcours complet avant d'ouvrir un canal à de vrais clients", 10,
        couleur=TEXTE_FAIBLE)

    # scénario
    b.r(252, 100, 320, 440, contour=TRAIT, ep=1, arrondi=8)
    b.t(272, 118, "Scénario de test", 11, semi=True)
    y = 150
    for libelle, valeur in (("Canal", "WhatsApp Business"), ("Événement", "Cotation émise"),
                            ("Profil client", "compte vérifié"), ("Langue", "français"),
                            ("Montant", "3 145,00 $")):
        b.t(272, y, libelle, 9, couleur=TEXTE_FAIBLE)
        b.r(272, y + 16, 280, 36, contour=TRAIT, ep=1, arrondi=5)
        b.t(286, y + 34, valeur, 10, ancre="lm")
        y += 64
    bouton(b, 272, 480, 280, 44, "Lancer le test", principal=True, taille=10)

    # conversation simulée
    b.r(600, 100, 400, 440, contour=TRAIT, ep=1, arrondi=8)
    b.r(600, 100, 400, 34, remplissage=REMPLI_FORT)
    b.t(618, 117, "MODE TEST — aucun message n'est réellement envoyé", 9, semi=True)
    y = 150
    for texte, sortante in (("Bonjour Kivu Trans, voici votre cotation COT-2026-000123…", False),
                            ("Merci. Je paie par virement.", True),
                            ("Référence à indiquer : COT-2026-000123.", False)):
        largeur = 320
        lignes = b.nb_lignes(texte, largeur - 26, 9)
        hauteur = 14 + lignes * 12
        x = 970 - largeur if sortante else 618
        b.r(x, y, largeur, hauteur, remplissage=REMPLI if sortante else BLANC,
            contour=None if sortante else TRAIT, ep=1, arrondi=8)
        b.tl(x + 13, y + 7, largeur - 26, texte, 9, interligne=1.35)
        y += hauteur + 12
    b.tl(618, 400, 364,
         "La conversation de test suit exactement les règles publiées : mêmes modèles, même routage.",
         9, couleur=TEXTE_FAIBLE)

    # résultat
    b.r(1024, 100, 220, 440, contour=TRAIT_FORT, ep=1.5, arrondi=8)
    b.t(1042, 118, "Résultat", 11, semi=True)
    y = 148
    for libelle, valeur in (("Messages envoyés", "4"), ("Échecs", "0"),
                            ("Délai moyen", "1,2 s")):
        b.t(1042, y, libelle, 9, couleur=TEXTE_FAIBLE)
        b.t(1226, y, valeur, 12, semi=True, ancre="ra")
        y += 30

    b.ligne(1042, y + 2, 1226, y + 2, TRAIT)
    y += 18
    b.t(1042, y, "Conditions d'ouverture", 9, semi=True)
    y += 22
    for condition in ("Compte marchand validé", "Modèles approuvés",
                      "Test de bout en bout réussi", "Plafonds renseignés",
                      "Astreinte humaine désignée"):
        b.r(1042, y - 2, 14, 14, contour=TRAIT_FORT, ep=1, arrondi=3)
        b.ligne(1045, y + 5, 1048, y + 9, TEXTE, 1.5)
        b.ligne(1048, y + 9, 1054, y - 1, TEXTE, 1.5)
        b.t(1064, y, condition, 9)
        y += 30

    b.r(252, 570, 992, 120, remplissage=BANDE, arrondi=6)
    b.t(272, 586, "Ce que le test doit prouver, avant toute ouverture", 10, semi=True)
    y = 608
    for preuve in ("Le message part avec toutes ses variables renseignées, sans blanc ni erreur technique.",
                   "Le client reçoit la bonne information au bon moment, dans sa langue.",
                   "En cas d'échec d'envoi, le repli prévu par la règle se déclenche réellement.",
                   "Le journal d'envoi conserve la trace, y compris pour le test."):
        b.t(272, y, "· " + preuve, 9, couleur=TEXTE_FAIBLE)
        y += 20

    b.t(252, 726, "CNL-05 · Bac à sable — IF-09 Console des canaux", 10, couleur=TEXTE_FAIBLE)
    return b


# --------------------------------------------------------------------------
# IF-10 — Chatbot WhatsApp côté client
# --------------------------------------------------------------------------
def ecran_wab01() -> Toile:
    b = Toile(L_PHONE, H_PHONE)
    b.r(0, 0, L_PHONE, H_PHONE, contour=TRAIT)
    b.t(18, 12, "14:32", 11, semi=True)
    for i in range(4):
        b.r(L_PHONE - 92 + i * 7, 22 - i * 3, 4, 3 + i * 3, remplissage=TEXTE_FAIBLE)
    entete_whatsapp(b)
    y = 116
    y = bandeau_systeme(b, y, "Aujourd'hui")
    y = bulle(b, y, "Bonjour ! Ici l'assistant PPC Ciment. Pour afficher des prix, je dois vérifier votre numéro.")
    y = boutons_rapides(b, y, ["Recevoir un code par SMS", "Je suis déjà client", "Parler à un agent"], principal=-1)
    y = bandeau_systeme(b, y, "Code envoyé au +243 ••• ••• 412")
    y = bulle(b, y, "482 913", sortante=True)
    y = bulle(b, y, "Numéro vérifié. Que souhaitez-vous faire ?")
    y = boutons_rapides(b, y, ["Commander du ciment", "Suivre ma commande", "Poser une question"], principal=-1)
    barre_saisie(b)
    pied_ecran(b, "WAB-01", "Accueil et identification")
    return b


def ecran_wab02() -> Toile:
    b = Toile(L_PHONE, H_PHONE)
    b.r(0, 0, L_PHONE, H_PHONE, contour=TRAIT)
    b.t(18, 12, "14:35", 11, semi=True)
    for i in range(4):
        b.r(L_PHONE - 92 + i * 7, 22 - i * 3, 4, 3 + i * 3, remplissage=TEXTE_FAIBLE)
    entete_whatsapp(b)
    y = 116
    y = bulle(b, y, "Quel produit ?")
    y = boutons_rapides(b, y, ["CEM II 42,5 — 50 kg", "CEM I 52,5 — 50 kg"], principal=-1)
    y = bulle(b, y, "CEM II 42,5", sortante=True)
    y = bulle(b, y, "Quelle quantité, en sacs de 50 kg ?")
    y = bulle(b, y, "200 sacs", sortante=True)
    y = bulle(b, y, "Où livrer ?")
    y = boutons_rapides(b, y, ["Gombe", "Limete", "Autre zone"], principal=-1)
    y = bulle(b, y, "Avec le transport PPC ou vous organisez l'enlèvement ?")
    y = boutons_rapides(b, y, ["Avec transport PPC", "Enlèvement par mes soins"], principal=-1)
    barre_saisie(b)
    pied_ecran(b, "WAB-02", "Commande guidée par menus")
    return b


def ecran_wab03() -> Toile:
    b = Toile(L_PHONE, H_PHONE)
    b.r(0, 0, L_PHONE, H_PHONE, contour=TRAIT)
    b.t(18, 12, "14:41", 11, semi=True)
    for i in range(4):
        b.r(L_PHONE - 92 + i * 7, 22 - i * 3, 4, 3 + i * 3, remplissage=TEXTE_FAIBLE)
    entete_whatsapp(b)
    y = 116
    y = bulle(b, y, "Voici votre cotation. Le prix est ferme pendant 48 heures.")
    y = carte_dans_bulle(
        b, y, "Cotation COT-2026-000123",
        [("Ciment · 200 sacs", "2 480,00 $"), ("Transport · Gombe", "640,00 $"),
         ("Total tout compris", "3 145,00 $")],
        "Payer cette cotation", note="Valable jusqu'au 09/11 à 14 h 35",
    )
    y = bulle(b, y, "3 145 $ dépasse le plafond du mobile money (2 500 $). Deux solutions :")
    y = boutons_rapides(b, y, ["Virement bancaire", "Échéancier en 2 versements"], principal=-1)
    y = bulle(b, y, "Virement bancaire", sortante=True)
    y = carte_dans_bulle(
        b, y, "Référence de virement",
        [("Référence à indiquer", "COT-2026-000123"), ("Montant", "3 145,00 $")],
        "Copier la référence", note="Aucun virement sans cette référence n'est accepté",
    )
    barre_saisie(b)
    pied_ecran(b, "WAB-03", "Cotation et paiement")
    return b


def ecran_wab04() -> Toile:
    b = Toile(L_PHONE, H_PHONE)
    b.r(0, 0, L_PHONE, H_PHONE, contour=TRAIT)
    b.t(18, 12, "15:12", 11, semi=True)
    for i in range(4):
        b.r(L_PHONE - 92 + i * 7, 22 - i * 3, 4, 3 + i * 3, remplissage=TEXTE_FAIBLE)
    entete_whatsapp(b)
    y = 116
    y = bandeau_systeme(b, y, "Paiement confirmé par la banque")
    y = bulle(b, y, "Paiement reçu. Votre bon de commande est émis, une seule fois.")
    b.r(16, y, 286, 132, remplissage=BLANC, contour=TRAIT_FORT, ep=1, arrondi=8)
    b.t(30, y + 14, "Bon BON-2026-000456", 10, semi=True)
    qr(b, 30, y + 34, 68, graine=11)
    b.t(112, y + 40, "200 sacs CEM II 42,5", 9)
    b.t(112, y + 58, "Usine de Kimpese", 9, couleur=TEXTE_FAIBLE)
    b.t(112, y + 76, "Nominatif · usage unique", 9, couleur=ACCENT)
    bouton(b, 30, y + 92, 258, 32, "Afficher le QR", principal=True, taille=10)
    y += 142
    y = bulle(b, y, "Transporteur affecté : Kivu Logistique. Camion en chargement à 15 h 40.")
    y = bulle(b, y, "Votre commande est chargée. Livraison prévue aujourd'hui avant 18 h.")
    y = bulle(b, y, "À la livraison, validez la réception vous-même : le chauffeur ne peut pas le faire à votre place.")
    y = boutons_rapides(b, y, ["Valider la réception", "Signaler un problème"], principal=-1)
    barre_saisie(b)
    pied_ecran(b, "WAB-04", "Bon de commande et suivi")
    return b


# --------------------------------------------------------------------------
# Diagrammes de flux
# --------------------------------------------------------------------------
def flux_conversation() -> Toile:
    b = Toile(1400, 860, ft=1.0, fond=FOND)
    b.t(40, 26, "Parcours conversationnel WhatsApp — de la question au bon de commande", 18, gras=True)
    b.t(40, 54, "Le bot ne calcule rien : il interroge les mêmes services que l'application mobile.", 10,
        couleur=TEXTE_FAIBLE)

    xg, wg = 60, 300
    y = 96
    noeud(b, xg, y, wg, 56, "Client écrit au numéro d'entreprise")
    lien(b, [(xg + wg / 2, y + 56), (xg + wg / 2, y + 78)])
    y += 78
    noeud(b, xg, y, wg, 56, "Menu numéroté\ncommander · suivre · agent", accent=False)
    lien(b, [(xg + wg / 2, y + 56), (xg + wg / 2, y + 78)])
    y += 78
    decision(b, xg, y, wg, 60, "Numéro vérifié ?")
    # branche « non »
    lien(b, [(xg + wg, y + 30), (xg + wg + 60, y + 30)])
    noeud(b, xg + wg + 70, y + 4, 250, 52, "Code à usage unique par SMS", "5 minutes, 3 tentatives")
    lien(b, [(xg + wg + 195, y + 4), (xg + wg + 195, y - 30), (xg + wg, y - 30)])
    b.t(xg + wg + 62, y + 8, "non", 9, couleur=ACCENT)
    b.t(xg + wg / 2 + 8, y + 44, "oui", 9, couleur=ACCENT)
    lien(b, [(xg + wg / 2, y + 60), (xg + wg / 2, y + 82)])
    y += 82
    noeud(b, xg, y, wg, 56, "Produit, quantité, zone de livraison", "questions fermées, une à la fois")
    lien(b, [(xg + wg / 2, y + 56), (xg + wg / 2, y + 78)])
    y += 78
    noeud(b, xg, y, wg, 64, "Cotation émise — COT-2026-000123", "prix ferme, valable 48 heures", accent=True)
    lien(b, [(xg + wg / 2, y + 64), (xg + wg / 2, y + 86)])
    y += 86
    decision(b, xg, y, wg, 60, "Paiement reçu et référencé ?")
    lien(b, [(xg + wg, y + 30), (xg + wg + 60, y + 30)])
    noeud(b, xg + wg + 70, y + 4, 250, 52, "Rappel puis repli sur un agent", "jamais de relance sans référence")
    b.t(xg + wg + 62, y + 8, "non", 9, couleur=ACCENT)
    b.t(xg + wg / 2 + 8, y + 44, "oui", 9, couleur=ACCENT)
    lien(b, [(xg + wg / 2, y + 60), (xg + wg / 2, y + 82)])
    y += 82
    noeud(b, xg, y, wg, 64, "Bon de commande émis — BON-2026-000456", "automatiquement, une seule fois",
          accent=True)
    lien(b, [(xg + wg / 2, y + 64), (xg + wg / 2, y + 86)])
    y += 86
    noeud(b, xg, y, wg, 56, "Chargement, livraison, reçu certifié")

    # annotations
    xa = 730
    b.r(xa, 96, 610, 690, contour=TRAIT, ep=1, arrondi=8, remplissage=BLANC)
    b.t(xa + 22, 116, "Ce que ce parcours garantit", 12, semi=True)
    y = 152
    for titre, texte in (
        ("Aucun prix avant vérification",
         "Un visiteur non identifié ne reçoit ni grille, ni ordre de grandeur."),
        ("Aucun prix calculé par le bot",
         "La cotation est produite par le service de cotation, avec son numéro et sa durée de validité."),
        ("Le paiement référence la cotation",
         "Le message de paiement transporte le numéro de cotation ; sans lui, aucun encaissement."),
        ("Le bon naît de l'encaissement",
         "Le bot ne crée jamais un bon : il annonce celui que le système a émis."),
        ("Repli humain à tout moment",
         "« Parler à un agent » est offert dès le premier message, et proposé après deux échecs."),
        ("L'IA est facultative",
         "Le parcours est une suite de questions fermées : les menus numérotés suffisent si PPC "
         "n'autorise pas l'IA locale."),
        ("Langue du client",
         "Français ou lingala, choisi sur le dernier échange ; les modèles existent dans les deux langues."),
        ("Tout est journalisé",
         "Chaque message envoyé, reçu ou rejeté figure au journal d'envoi, consultable par PPC."),
    ):
        b.t(xa + 22, y, titre, 11, semi=True)
        hauteur = b.tl(xa + 22, y + 20, 566, texte, 10, couleur=TEXTE_FAIBLE)
        y += 20 + hauteur + 20

    b.t(40, 826, "Flux 1 · Parcours conversationnel — IF-10 Chatbot WhatsApp", 10, couleur=TEXTE_FAIBLE)
    return b


def flux_automatisation() -> Toile:
    b = Toile(1400, 860, ft=1.0, fond=FOND)
    b.t(40, 26, "Automatisation des messages sortants — un événement, plusieurs canaux", 18, gras=True)
    b.t(40, 54, "L'ordre des canaux et le repli sont décidés une seule fois, dans les règles de routage.", 10,
        couleur=TEXTE_FAIBLE)

    # colonne des événements
    b.t(60, 96, "Événements", 11, semi=True, couleur=TEXTE_FAIBLE)
    evenements = ["Cotation émise", "Paiement confirmé", "Bon de commande émis",
                  "Chargement certifié", "Livraison prouvée", "Litige ouvert", "Décision de litige"]
    y = 118
    positions = []
    for e in evenements:
        b.r(60, y, 260, 44, contour=TRAIT_FORT, ep=1, arrondi=6, remplissage=BLANC)
        b.t(74, y + 22, e, 10, semi=True, ancre="lm")
        positions.append(y + 22)
        y += 56

    # bus vertical puis routeur
    b.ligne(320, positions[0], 360, positions[0], TRAIT_FORT, 1.5)
    b.ligne(360, positions[0], 360, positions[-1], TRAIT_FORT, 1.5)
    for py in positions:
        b.ligne(320, py, 360, py, TRAIT_FORT, 1.5)
    fleche(b, 360, positions[3], 430, positions[3], TRAIT_FORT)

    b.r(430, 190, 280, 130, contour=TRAIT_FORT, ep=1.5, arrondi=8, remplissage=BLANC)
    b.t(452, 208, "Moteur de routage", 12, semi=True)
    for regle in ("canal préféré du client", "langue du dernier échange",
                  "heures calmes 21 h – 6 h", "plafond de 3 messages / jour"):
        b.t(452, 234 + 20 * ("canal préféré du client", "langue du dernier échange",
                             "heures calmes 21 h – 6 h", "plafond de 3 messages / jour").index(regle),
            "· " + regle, 9.5, couleur=TEXTE_FAIBLE)

    # canaux
    b.t(790, 96, "Canaux", 11, semi=True, couleur=TEXTE_FAIBLE)
    canaux = ["WhatsApp Business", "SMS", "E-mail", "Notification applicative"]
    y = 118
    cibles = []
    for i, c in enumerate(canaux):
        accent = i == 0
        b.r(790, y, 250, 44, contour=ACCENT if accent else TRAIT_FORT, ep=1.5, arrondi=6,
            remplissage=ACCENT_PALE if accent else BLANC)
        b.t(804, y + 22, c, 10, semi=True, ancre="lm")
        cibles.append(y + 22)
        y += 56
        fleche(b, 710, 255, 786, cibles[-1], TRAIT_FORT)

    # suite : accusé de réception
    ysf = 470
    b.r(430, ysf, 280, 80, contour=TRAIT_FORT, ep=1.5, arrondi=8, remplissage=BLANC)
    b.tl(452, ysf + 26, 236, "Accusé de réception dans les 5 minutes ?", 10, semi=True)
    fleche(b, 570, 320, 570, ysf - 4, TRAIT_FORT)

    b.r(790, ysf, 250, 80, contour=TRAIT_FORT, ep=1, arrondi=6, remplissage=BLANC)
    b.tl(804, ysf + 26, 222, "Repli sur le canal suivant de la règle", 10, interligne=1.3)
    fleche(b, 710, ysf + 40, 786, ysf + 40, TRAIT_FORT)
    b.t(716, ysf + 22, "non", 9, couleur=ACCENT)

    b.r(430, ysf + 118, 610, 86, contour=ACCENT, ep=1.5, arrondi=8, remplissage=ACCENT_PALE)
    b.tl(452, ysf + 134, 566,
         "Deux échecs consécutifs ouvrent un ticket de reprise humaine dans la console des canaux : "
         "l'agent voit le message non délivré et le contexte du dossier.", 10, interligne=1.35)
    fleche(b, 915, ysf + 80, 915, ysf + 114, TRAIT_FORT)

    b.r(60, 698, 1280, 92, contour=TRAIT, ep=1, arrondi=8, remplissage=BLANC)
    b.t(80, 712, "Ce que l'automatisation ne fait jamais", 11, semi=True)
    b.tl(80, 734, 1240,
         "Elle n'envoie pas de prix, ni de montant de marge, ni de données d'un autre client. Elle ne relance "
         "jamais un paiement sans référence de cotation. Elle ne désactive pas un message de sécurité "
         "(paiement confirmé, litige ouvert, décision de litige).", 10, couleur=TEXTE_FAIBLE)

    b.t(40, 826, "Flux 2 · Automatisation des messages sortants — IF-09 Console des canaux", 10,
        couleur=TEXTE_FAIBLE)
    return b


def carte_mini(b: Toile, x, y, w, h,
               route=((0.08, 0.80), (0.32, 0.62), (0.50, 0.68), (0.76, 0.34), (0.90, 0.22)),
               position=None, libelle_position="Dernière position connue", graine=5):
    """Fond de carte schématique : grille, îlots, itinéraire, repères. Aucune donnée réelle."""
    b.r(x, y, w, h, remplissage=(246, 247, 248), contour=TRAIT, ep=1)
    for i in range(1, 6):
        yy = y + h * i / 6
        b.ligne(x + 2, yy, x + w - 2, yy, (231, 235, 239), 1)
    for i in range(1, 8):
        xx = x + w * i / 8
        b.ligne(xx, y + 2, xx, y + h - 2, (231, 235, 239), 1)

    alea = random.Random(graine)
    for _ in range(4):
        bx = x + w * alea.uniform(0.05, 0.72)
        by = y + h * alea.uniform(0.06, 0.66)
        bw = w * alea.uniform(0.08, 0.16)
        bh = h * alea.uniform(0.08, 0.16)
        b.r(bx, by, bw, bh, remplissage=(235, 238, 241))

    points = [(x + px * w, y + py * h) for px, py in route]
    for (x1, y1), (x2, y2) in zip(points, points[1:]):
        b.ligne(x1, y1, x2, y2, TRAIT_FORT, 2.5)

    depart = points[0]
    b.r(depart[0] - 4, depart[1] - 4, 8, 8, remplissage=TEXTE_FAIBLE, arrondi=4, contour=BLANC, ep=1.5)

    arrivee = points[-1]
    b.r(arrivee[0] - 7, arrivee[1] - 7, 14, 14, contour=TEXTE, ep=2, arrondi=7)
    b.r(arrivee[0] - 2, arrivee[1] - 2, 4, 4, remplissage=TEXTE, arrondi=2)

    if position:
        px, py = x + position[0] * w, y + position[1] * h
        b.r(px - 9, py - 9, 18, 18, remplissage=BLANC, arrondi=9)
        b.r(px - 5, py - 5, 10, 10, remplissage=TEXTE, arrondi=5)
        if libelle_position:
            largeur = b.mesurer(libelle_position, 8) + 16
            bx = min(max(px - largeur / 2, x + 4), x + w - largeur - 4)
            by = py - 30 if py - 30 > y + 4 else py + 12
            b.r(bx, by, largeur, 18, remplissage=BLANC, contour=TRAIT, arrondi=4)
            b.t(bx + 8, by + 9, libelle_position, 8, couleur=TEXTE_FAIBLE, ancre="lm")


# --------------------------------------------------------------------------
# Géolocalisation — suivi et preuve
# --------------------------------------------------------------------------
def ecran_cli12() -> Toile:
    b = cadre_phone("Suivi de la commande")
    b.t(18, 116, "BON-2026-000456 — Kivu Logistique", 10, couleur=TEXTE_FAIBLE)
    carte_mini(b, 18, 136, L_PHONE - 36, 186, position=(0.55, 0.50),
               libelle_position="16 h 42", graine=5)

    b.t(18, 334, "Dernière position transmise il y a 3 minutes", 9, couleur=TEXTE_FAIBLE)

    y = 362
    for heure, etape, fait in (("14:41", "Cotation payée et bon émis", True),
                               ("15:40", "Chargement certifié — 200 sacs, scellé 4471-B", True),
                               ("16:05", "En route vers Gombe", True),
                               ("—", "Livraison attendue avant 18 h", False)):
        b.r(24, y + 2, 9, 9, remplissage=TEXTE if fait else BLANC,
            contour=TEXTE if fait else TRAIT_FORT, ep=1, arrondi=5)
        if y < 480:
            b.ligne(28, y + 13, 28, y + 30, TRAIT, 1)
        b.t(46, y, heure, 9, couleur=TEXTE_FAIBLE)
        b.tl(90, y - 1, 270, etape, 10, interligne=1.25)
        y += 44

    b.r(18, 548, L_PHONE - 36, 62, contour=TRAIT, ep=1, arrondi=8)
    b.t(32, 560, "Chauffeur J. Mbala", 10, semi=True)
    b.t(32, 578, "Camion CAM-04 · 15 tonnes", 9, couleur=TEXTE_FAIBLE)
    b.r(L_PHONE - 132, 562, 96, 30, contour=TRAIT_FORT, ep=1, arrondi=15)
    b.t(L_PHONE - 84, 577, "Appeler", 9, semi=True, ancre="mm")

    bouton(b, 18, H_PHONE - H_PIEDS - 96, L_PHONE - 36, 44, "Voir le dossier de preuve")
    b.tl(18, H_PHONE - H_PIEDS - 44, L_PHONE - 36,
         "La position n'est affichée que si le chauffeur l'a transmise : aucune position n'est inventée.",
         8.5, couleur=TEXTE_FAIBLE)
    pied_ecran(b, "CLI-12", "Suivi de la commande")
    return b


def ecran_cli14() -> Toile:
    b = cadre_phone("Dossier de preuve")
    b.t(18, 116, "BON-2026-000456 — livré le 07/11 à 17 h 52", 9, couleur=TEXTE_FAIBLE)

    photo(b, 18, 136, L_PHONE - 36, 150, "Photo du chargement livré")
    b.r(28, 146, 200, 20, remplissage=BLANC, contour=TRAIT, ep=1, arrondi=4)
    b.t(38, 156, "Photo géolocalisée · 17 h 52", 8, couleur=TEXTE_FAIBLE, ancre="lm")

    b.t(18, 300, "Position relevée au moment de la prise", 9, couleur=TEXTE_FAIBLE)
    b.r(18, 316, L_PHONE - 36, 38, remplissage=REMPLI, arrondi=6)
    b.t(30, 335, "−4,3271 ; 15,3134 — précision 12 m", 10, semi=True, ancre="lm")
    b.t(L_PHONE - 30, 335, "GPS", 8, couleur=TEXTE_FAIBLE, ancre="rm")

    y = 372
    for libelle, detail in (("QR nominatif", "flashé par le chauffeur, usage unique"),
                            ("Pesée contradictoire", "10 250 kg annoncés · 10 180 kg constatés"),
                            ("Scellé", "4471-B vérifié à l'arrivée"),
                            ("Validation client", "signée le 07/11 à 17 h 51")):
        b.r(18, y, 16, 16, contour=TRAIT_FORT, ep=1, arrondi=3)
        b.ligne(21, y + 8, 24, y + 12, TEXTE, 1.5)
        b.ligne(24, y + 12, 30, y + 3, TEXTE, 1.5)
        b.t(42, y - 1, libelle, 10, semi=True)
        b.t(42, y + 15, detail, 8.5, couleur=TEXTE_FAIBLE)
        y += 40

    b.r(18, y + 4, L_PHONE - 36, 40, remplissage=BANDE, arrondi=6)
    b.t(30, y + 18, "Dossier signé · empreinte a3f2…9c — vérifiable hors ligne", 9,
        couleur=TEXTE_FAIBLE)

    bouton(b, 18, H_PHONE - H_PIEDS - 96, L_PHONE - 36, 44, "Télécharger le dossier (PDF)", principal=True)
    bouton(b, 18, H_PHONE - H_PIEDS - 44, L_PHONE - 36, 36, "Ouvrir un litige", taille=10)
    pied_ecran(b, "CLI-14", "Dossier de preuve")
    return b


def ecran_chf03() -> Toile:
    b = cadre_phone("Détail de la course")
    b.t(18, 116, "BON-2026-000456", 11, semi=True)
    b.t(18, 136, "Kivu Trans SARL — 200 sacs CEM II 42,5", 9, couleur=TEXTE_FAIBLE)

    carte_mini(b, 18, 160, L_PHONE - 36, 170,
               route=((0.06, 0.86), (0.28, 0.70), (0.46, 0.74), (0.72, 0.40), (0.94, 0.16)),
               position=None, graine=13)
    b.t(18, 340, "Point de repère : marché central, après la station", 10, semi=True)
    b.t(18, 358, "Zone Gombe — 4e avenue · GPS facultatif", 9, couleur=TEXTE_FAIBLE)

    y = 392
    for libelle, valeur in (("Fenêtre de livraison", "aujourd'hui avant 18 h"),
                            ("Contact sur place", "+243 ••• ••• 412"),
                            ("Poids et scellé", "10 250 kg · scellé 4471-B")):
        b.t(18, y, libelle, 9, couleur=TEXTE_FAIBLE)
        b.t(L_PHONE - 18, y, valeur, 10, semi=True, ancre="ra")
        y += 26
        b.ligne(18, y - 9, L_PHONE - 18, y - 9, TRAIT)

    b.r(18, y + 10, L_PHONE - 36, 66, remplissage=BANDE, arrondi=6)
    b.tl(30, y + 22, L_PHONE - 60,
         "Le point de repère fait foi pour l'arrivée. La position GPS est un confort, jamais une condition de livraison.",
         9, couleur=TEXTE_FAIBLE)

    bouton(b, 18, H_PHONE - H_PIEDS - 96, L_PHONE - 36, 44, "Appeler le client")
    bouton(b, 18, H_PHONE - H_PIEDS - 44, L_PHONE - 36, 36, "Démarrer le trajet", taille=10)
    pied_ecran(b, "CHF-03", "Détail de la course")
    return b


def ecran_chf05() -> Toile:
    b = cadre_phone("Route et événements", action="SOS")
    b.r(0, 100, L_PHONE, 28, remplissage=REMPLI_FORT)
    b.t(18, 110, "Hors ligne — les positions sont mises en file", 9)

    carte_mini(b, 18, 142, L_PHONE - 36, 180, position=(0.62, 0.46),
               libelle_position="Position enregistrée à 16 h 42", graine=21)
    b.t(18, 332, "Dernière position transmise : 16 h 30", 9, couleur=TEXTE_FAIBLE)

    y = 360
    for libelle, detail in (("Départ", "quitter le point de chargement"),
                            ("Incident", "panne, contrôle, route coupée"),
                            ("Arrivée", "se présenter chez le client")):
        b.r(18, y, L_PHONE - 36, 52, contour=TRAIT_FORT, ep=1, arrondi=8)
        b.t(34, y + 16, libelle, 11, semi=True)
        b.t(34, y + 34, detail, 8.5, couleur=TEXTE_FAIBLE)
        b.r(L_PHONE - 54, y + 16, 20, 20, contour=TRAIT, ep=1, arrondi=10)
        y += 62

    b.r(18, y + 6, L_PHONE - 36, 74, contour=ACCENT, ep=1.5, arrondi=8, remplissage=ACCENT_PALE)
    b.t(32, y + 18, "2 positions en attente d'envoi", 10, semi=True, couleur=ACCENT)
    b.tl(32, y + 38, L_PHONE - 64,
         "Chaque position est horodatée sur le téléphone ; l'horodatage serveur est ajouté à la réception.",
         8.5, couleur=TEXTE_FAIBLE)

    bouton(b, 18, H_PHONE - H_PIEDS - 44, L_PHONE - 36, 36, "Synchroniser maintenant", taille=10)
    pied_ecran(b, "CHF-05", "Route et événements")
    return b


# --------------------------------------------------------------------------
# Parité des canaux — USSD, SMS, Telegram, e-mail
# --------------------------------------------------------------------------
def cadre_ussd(titre: str) -> Toile:
    b = Toile(L_PHONE, H_PHONE)
    b.r(0, 0, L_PHONE, H_PHONE, contour=TRAIT)
    b.t(18, 12, "14:32", 11, semi=True)
    for i in range(4):
        b.r(L_PHONE - 92 + i * 7, 22 - i * 3, 4, 3 + i * 3, remplissage=TEXTE_FAIBLE)
    b.r(0, 38, L_PHONE, 30, remplissage=REMPLI_FORT)
    b.t(18, 53, "Session USSD · *144# · Vodacom", 9, couleur=TEXTE_FAIBLE, ancre="lm")
    b.r(14, 86, L_PHONE - 28, 420, contour=TRAIT_FORT, ep=1.5, arrondi=6)
    b.t(32, 102, titre, 11, semi=True)
    return b


def lignes_ussd(b: Toile, y, lignes, taille=10, pas=26):
    for ligne in lignes:
        if ligne == "-":
            b.ligne(32, y + 6, L_PHONE - 32, y + 6, TRAIT)
            y += 16
            continue
        b.t(32, y, ligne, taille, semi=ligne.isupper() or ligne[:2] in ("1.", "2.", "3."))
        y += pas
    return y


def reponse_ussd(b: Toile, y, texte, note=None):
    b.r(32, y, L_PHONE - 64, 40, contour=TRAIT_FORT, ep=1, arrondi=4, remplissage=BLANC)
    b.t(48, y + 20, texte, 12, semi=True, ancre="lm")
    b.t(32, y + 52, "Répondre", 9, couleur=TEXTE_FAIBLE)
    if note:
        b.tl(32, y + 70, L_PHONE - 64, note, 8.5, couleur=TEXTE_FAIBLE)


def ecran_ussd01() -> Toile:
    b = cadre_ussd("PPC Ciment")
    y = lignes_ussd(b, 136, [
        "Numéro vérifié : +243 ••• 412", "-",
        "1. Commander du ciment", "2. Suivre ma commande",
        "3. Parler à un agent", "-",
    ])
    reponse_ussd(b, y + 10, "1",
                 "Sans internet. La session expire après 20 secondes sans réponse, "
                 "et un code court est envoyé par SMS pour reprendre.")
    b.tl(32, 544, L_PHONE - 64,
         "Quatre écrans au maximum entre le menu et la cotation : au-delà, le client abandonne.",
         9, couleur=TEXTE_FAIBLE)
    pied_ecran(b, "USS-01", "Menu principal USSD")
    return b


def ecran_ussd02() -> Toile:
    b = cadre_ussd("Cotation COT-2026-000123")
    y = lignes_ussd(b, 136, [
        "CEM II 42,5 · 200 sacs", "Zone Gombe · avec transport", "-",
        "TOTAL 3 145,00 $", "Valable jusqu'au 09/11 à 14 h 35", "-",
        "1. Payer maintenant", "2. Recevoir le détail par SMS", "-",
    ])
    reponse_ussd(b, y + 6, "1",
                 "Le paiement ouvre une demande mobile money sur ce numéro : "
                 "aucun montant n'est saisi à la main.")
    b.tl(32, 544, L_PHONE - 64,
         "Le prix ne s'affiche qu'après vérification du numéro : un concurrent ne peut pas sonder la grille par USSD.",
         9, couleur=TEXTE_FAIBLE)
    pied_ecran(b, "USS-02", "Cotation et paiement USSD")
    return b


def ecran_sms01() -> Toile:
    b = Toile(L_PHONE, H_PHONE)
    b.r(0, 0, L_PHONE, H_PHONE, contour=TRAIT)
    b.t(18, 12, "14:35", 11, semi=True)
    for i in range(4):
        b.r(L_PHONE - 92 + i * 7, 22 - i * 3, 4, 3 + i * 3, remplissage=TEXTE_FAIBLE)
    b.r(0, 38, L_PHONE, 50, remplissage=BANDE)
    b.t(L_PHONE / 2, 63, "PPC Ciment — SMS", 12, semi=True, ancre="ma")
    b.ligne(0, 88, L_PHONE, 88, TRAIT)

    y = 104
    y = bandeau_systeme(b, y, "Numéro vérifié à 14 h 31")
    y = bulle(b, y, "COT 200 GOMBE", sortante=True)
    y = bulle(b, y, "Cotation COT-2026-000123 : 200 sacs CEM II, livraison Gombe. Total 3 145,00 $. "
                    "Valable jusqu'au 09/11. Repondez PAY pour payer.")
    y = bulle(b, y, "PAY", sortante=True)
    y = bulle(b, y, "Demande envoyee sur votre mobile money. Validez sur votre telephone, puis repondez OK.")
    y = bulle(b, y, "OK", sortante=True)
    barre_saisie(b)
    b.t(L_PHONE - 20, H_PHONE - H_PIEDS - 58, "112/160", 8, couleur=TEXTE_FAIBLE, ancre="ra")
    pied_ecran(b, "SMS-01", "Commande et paiement par SMS")
    return b


def ecran_sms02() -> Toile:
    b = Toile(L_PHONE, H_PHONE)
    b.r(0, 0, L_PHONE, H_PHONE, contour=TRAIT)
    b.t(18, 12, "14:47", 11, semi=True)
    for i in range(4):
        b.r(L_PHONE - 92 + i * 7, 22 - i * 3, 4, 3 + i * 3, remplissage=TEXTE_FAIBLE)
    b.r(0, 38, L_PHONE, 50, remplissage=BANDE)
    b.t(L_PHONE / 2, 63, "PPC Ciment — SMS", 12, semi=True, ancre="ma")
    b.ligne(0, 88, L_PHONE, 88, TRAIT)

    y = 104
    y = bulle(b, y, "Paiement recu. Code de retrait : 481902. Presentez ce code au point de chargement "
                    "de Kimpese. Repondez BON pour recevoir le detail.")
    y = bulle(b, y, "BON", sortante=True)
    y = bulle(b, y, "Bon BON-2026-000456 · 200 sacs CEM II · code 481902 · nominatif, usage unique, "
                    "valable 7 jours.")
    y = bulle(b, y, "ETAT", sortante=True)
    y = bulle(b, y, "En chargement a Kimpese depuis 15 h 40. Livraison prevue avant 18 h.")

    b.r(16, 600, L_PHONE - 32, 76, remplissage=BANDE, arrondi=6)
    b.t(30, 614, "Ce que le SMS ne peut pas faire", 9, semi=True)
    b.tl(30, 632, L_PHONE - 60,
         "Ni pièce jointe, ni QR, ni image. Le bon est un code : c'est la console de chargement qui le saisit.",
         8.5, couleur=TEXTE_FAIBLE)
    barre_saisie(b)
    b.t(L_PHONE - 20, H_PHONE - H_PIEDS - 58, "134/160", 8, couleur=TEXTE_FAIBLE, ancre="ra")
    pied_ecran(b, "SMS-02", "Bon et suivi par SMS")
    return b


def entete_telegram(b: Toile):
    b.r(0, 38, L_PHONE, 64, remplissage=(240, 242, 244))
    b.r(18, 52, 36, 36, remplissage=REMPLI_FORT, arrondi=18)
    b.t(36, 70, "P", 12, semi=True, couleur=TEXTE_FAIBLE, ancre="mm")
    b.t(66, 60, "Bot PPC Ciment", 12, semi=True)
    b.t(66, 78, "bot · en ligne", 9, couleur=TEXTE_FAIBLE)
    b.ligne(0, 102, L_PHONE, 102, TRAIT)


def clavier_inline(b: Toile, y, rangees, largeur=286):
    for rangee in rangees:
        pas = largeur // len(rangee)
        for i, libelle in enumerate(rangee):
            b.r(16 + i * pas, y, pas - 6, 34, contour=TRAIT_FORT, ep=1, arrondi=6, remplissage=BLANC)
            b.t(16 + i * pas + (pas - 6) / 2, y + 17, libelle, 9.5, semi=True, ancre="mm")
        y += 40
    return y + 4


def ecran_tgm01() -> Toile:
    b = Toile(L_PHONE, H_PHONE)
    b.r(0, 0, L_PHONE, H_PHONE, contour=TRAIT)
    b.t(18, 12, "14:38", 11, semi=True)
    for i in range(4):
        b.r(L_PHONE - 92 + i * 7, 22 - i * 3, 4, 3 + i * 3, remplissage=TEXTE_FAIBLE)
    entete_telegram(b)

    y = 116
    y = bulle(b, y, "Bonjour. Je suis le bot PPC Ciment. Votre compte Telegram est rattaché au numéro "
                    "vérifié +243 ••• 412.")
    y = bulle(b, y, "Que souhaitez-vous faire ?")
    y = clavier_inline(b, y, [["Commander", "Suivre"], ["Parler à un agent"]])
    y = bulle(b, y, "Commander", sortante=True)
    y = bulle(b, y, "Produit ?")
    y = clavier_inline(b, y, [["CEM II 42,5", "CEM I 52,5"]])
    y = bulle(b, y, "CEM II 42,5", sortante=True)
    y = bulle(b, y, "Quantité en sacs de 50 kg — répondez par un nombre.")
    y = bulle(b, y, "200", sortante=True)
    b.tl(18, 640, L_PHONE - 36,
         "Même moteur que WhatsApp : seuls le rendu et les gabarits changent. Aucun compte marchand à ouvrir, "
         "mais une population plus étroite.", 8.5, couleur=TEXTE_FAIBLE)
    barre_saisie(b)
    pied_ecran(b, "TGM-01", "Commande par bot Telegram")
    return b


def ecran_tgm02() -> Toile:
    b = Toile(L_PHONE, H_PHONE)
    b.r(0, 0, L_PHONE, H_PHONE, contour=TRAIT)
    b.t(18, 12, "15:04", 11, semi=True)
    for i in range(4):
        b.r(L_PHONE - 92 + i * 7, 22 - i * 3, 4, 3 + i * 3, remplissage=TEXTE_FAIBLE)
    entete_telegram(b)

    y = 116
    y = bulle(b, y, "Cotation prête. Prix ferme pendant 48 heures.")
    b.r(16, y, 286, 158, contour=TRAIT_FORT, ep=1, arrondi=8, remplissage=BLANC)
    b.t(30, y + 14, "COT-2026-000123", 10, semi=True, couleur=TEXTE_FAIBLE)
    b.t(30, y + 36, "3 145,00 $", 20, gras=True)
    b.t(30, y + 66, "200 sacs · Gombe · avec transport", 9, couleur=TEXTE_FAIBLE)
    b.r(30, y + 86, 258, 30, contour=TRAIT, ep=1, arrondi=6)
    b.t(159, y + 101, "Télécharger le PDF", 9, semi=True, ancre="mm")
    bouton(b, 30, y + 122, 258, 28, "Payer maintenant", principal=True, taille=9.5)
    y += 168
    y = bulle(b, y, "Paiement reçu. Votre bon de commande est émis.")
    b.r(16, y, 286, 86, contour=TRAIT_FORT, ep=1, arrondi=8, remplissage=BLANC)
    b.t(30, y + 12, "BON-2026-000456.pdf", 9.5, semi=True)
    qr(b, 30, y + 30, 46, graine=17)
    b.t(90, y + 34, "200 sacs CEM II", 9)
    b.t(90, y + 50, "Code de retrait : 481902", 9, couleur=ACCENT)
    b.t(90, y + 66, "Nominatif · usage unique", 8.5, couleur=TEXTE_FAIBLE)
    y += 96
    y = clavier_inline(b, y, [["Valider la réception", "Signaler un problème"]])
    barre_saisie(b)
    pied_ecran(b, "TGM-02", "Cotation et bon par Telegram")
    return b


def ecran_mel01() -> Toile:
    b = Toile(1024, 700, ft=1.2)
    b.r(0, 0, 1024, 46, remplissage=(14, 36, 54))
    b.t(24, 23, "Messagerie — Boîte de réception", 13, semi=True, couleur=BLANC, ancre="lm")

    b.r(0, 46, 220, 654, remplissage=(246, 247, 248))
    b.t(24, 66, "Dossiers", 9, semi=True, couleur=TEXTE_FAIBLE)
    y = 92
    for dossier, actif in (("Boîte de réception", True), ("Envoyés", False), ("Archives", False),
                           ("Indésirables", False)):
        if actif:
            b.r(12, y - 12, 196, 30, remplissage=REMPLI_FORT, arrondi=4)
        b.t(24, y + 4, dossier, 10, semi=actif, ancre="lm")
        y += 36

    b.t(248, 66, "De : PPC Ciment <cotation@ppc.cd>", 9, couleur=TEXTE_FAIBLE)
    b.t(248, 86, "À : kivu.trans@exemple.cd", 9, couleur=TEXTE_FAIBLE)
    b.t(248, 106, "Objet : Votre cotation COT-2026-000123 — 3 145,00 $", 11, semi=True)
    b.ligne(248, 126, 1004, 126, TRAIT)

    y = 146
    b.tl(248, y, 500, "Bonjour Kivu Trans SARL,", 10)
    y += 26
    b.tl(248, y, 500,
         "Votre cotation est prête. Le prix est ferme jusqu'au 09/11/2026 à 14 h 35 : au-delà, "
         "une nouvelle cotation sera calculée au prix en vigueur.", 10, couleur=TEXTE_FAIBLE)
    y += 48
    b.tl(248, y, 500,
         "Pour payer, utilisez le bouton ci-dessous. Le lien est signé : il ouvre votre cotation "
         "déjà authentifiée, sans ressaisie de mot de passe.", 10, couleur=TEXTE_FAIBLE)
    y += 62

    bouton(b, 248, y, 240, 44, "Payer 3 145,00 $", principal=True, taille=11)
    b.r(500, y, 240, 44, contour=TRAIT_FORT, ep=1, arrondi=6)
    b.t(620, y + 22, "Télécharger la cotation", 10, ancre="mm")
    y += 60
    b.r(248, y, 300, 40, contour=TRAIT, ep=1, arrondi=6)
    b.t(264, y + 20, "COT-2026-000123.pdf · 84 Ko", 9, couleur=TEXTE_FAIBLE, ancre="lm")
    y += 56
    b.tl(248, y, 500,
         "Ce message ne contient aucun prix pour un autre destinataire : le lien est propre au client et expire "
         "avec la cotation.", 9, couleur=TEXTE_FAIBLE)

    b.r(772, 146, 232, 250, contour=TRAIT_FORT, ep=1.5, arrondi=8)
    b.t(790, 162, "Ce que l'e-mail change", 10, semi=True)
    yp = 188
    for point in ("Asynchrone : aucune session à tenir",
                  "Lien signé, valable 48 heures",
                  "Pièces jointes : cotation, reçu",
                  "Relance automatique à J+1"):
        b.tl(790, yp, 198, "· " + point, 9, couleur=TEXTE_FAIBLE, interligne=1.3)
        yp += 34
    b.tl(790, yp + 4, 198,
         "On ne promet pas de réponse instantanée : on promet un dossier complet.", 9, couleur=ACCENT)

    b.t(24, 660, "MEL-01 · E-mail de cotation avec lien signé — canal e-mail", 10, couleur=TEXTE_FAIBLE)
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
    ("p11-canaux-tableau", "IF-09 · Console des canaux — tableau des canaux", ["cnl01"]),
    ("p12-canaux-routage", "IF-09 · Console des canaux — règles de routage des messages", ["cnl03"]),
    ("p13-canaux-conversations", "IF-09 · Console des canaux — reprise humaine d'une conversation",
     ["cnl04"]),
    ("p14-whatsapp-identification-cotation",
     "IF-10 · Chatbot WhatsApp — identification et commande guidée", ["wab01", "wab02"]),
    ("p15-whatsapp-paiement-bon", "IF-10 · Chatbot WhatsApp — paiement et bon de commande",
     ["wab03", "wab04"]),
    ("p16-flux-conversation", "Flux 1 · Parcours conversationnel WhatsApp", ["flux_conversation"]),
    ("p17-flux-automatisation", "Flux 2 · Automatisation des messages sortants", ["flux_automatisation"]),
    ("p18-canaux-modeles", "IF-09 · Console des canaux — modèles de messages", ["cnl02"]),
    ("p19-canaux-bac-a-sable", "IF-09 · Console des canaux — bac à sable", ["cnl05"]),
    ("p20-geolocalisation-suivi-preuve",
     "Géolocalisation côté client — suivi de la commande et dossier de preuve", ["cli12", "cli14"]),
    ("p21-geolocalisation-chauffeur",
     "Géolocalisation côté chauffeur — détail de la course et positions", ["chf03", "chf05"]),
    ("p22-parite-ussd", "Parité des canaux · USSD — de la cotation au paiement", ["ussd01", "ussd02"]),
    ("p23-parite-sms", "Parité des canaux · SMS — commande, paiement et bon par code", ["sms01", "sms02"]),
    ("p24-parite-telegram", "Parité des canaux · Telegram — cotation et bon", ["tgm01", "tgm02"]),
    ("p25-parite-email", "Parité des canaux · E-mail — cotation et lien signé", ["mel01"]),
]


def construire(nom_fichier: str, ecrans: list[str]) -> Path:
    toiles = []
    for cle in ecrans:
        fonction = globals().get(f"ecran_{cle}") or globals()[cle]
        toiles.append(fonction())
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
