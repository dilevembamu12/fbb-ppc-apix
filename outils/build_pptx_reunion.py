#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
build_pptx_reunion.py — Version « réunion » de la présentation : 12 diapositives + annexes.

Conçue selon la règle 10/20/30 de Guy Kawasaki : une seule idée par diapositive,
peu de texte, des visuels qui portent le propos, et des annexes que l'on ne montre
que si la question est posée.

    Diapositives 1 à 12  : présentation principale
    Annexes A1 à A5      : à ouvrir sur question, jamais en séquence

Les maquettes d'interface (client, chauffeur, back-office) sont dessinées avec des
formes natives : aucune capture d'écran tierce n'est utilisée, ni aucun nom de
produit existant.

Usage :
    python outils/build_pptx_reunion.py
"""

from __future__ import annotations

import sys
from pathlib import Path

RACINE = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(Path(__file__).resolve().parent))

from pptx import Presentation                          # noqa: E402
from pptx.dml.color import RGBColor                       # noqa: E402
from pptx.enum.shapes import MSO_SHAPE                      # noqa: E402
from pptx.enum.text import MSO_ANCHOR, PP_ALIGN             # noqa: E402
from pptx.util import Inches, Pt                            # noqa: E402

from build_pptx import (                                     # noqa: E402
    BLANC, GRIS, GRIS_CLAIR, HAUTEUR, LARGEUR, LARGEUR_UTILE, MARGE,
    NUIT, NUIT_MOYEN, ORANGE, ORANGE_PALE, POLICE, POLICE_TITRE, SABLE, VERT,
    carte, contour, fond, forme, liste, notes, photo, pied, rectangle, tableau, texte, voile,
)

SORTIE = RACINE / "dist" / "pptx" / "APIX-All-In-One-12-slides-PPC.pptx"
TOTAL = 12


# ---------------------------------------------------------------------------
# Habillage commun
# ---------------------------------------------------------------------------
def en_tete(diapo, surtitre: str, titre: str, numero: int, sombre: bool = False):
    couleur = BLANC if sombre else NUIT
    if not sombre:
        rectangle(diapo, 0, 0, LARGEUR, Inches(0.11), ORANGE)
    texte(diapo, MARGE, Inches(0.55), LARGEUR_UTILE, Inches(0.28), surtitre.upper(),
          taille=11, couleur=ORANGE, gras=True)
    texte(diapo, MARGE, Inches(0.88), LARGEUR_UTILE, Inches(0.9), titre,
          taille=32, couleur=couleur, gras=True, police=POLICE_TITRE, interligne=1.03)
    etiquette = f"{numero} / {TOTAL}" if numero <= TOTAL else f"Annexe {numero - TOTAL}"
    texte(diapo, LARGEUR - MARGE - Inches(1.4), Inches(0.55), Inches(1.4), Inches(0.25),
          etiquette, taille=10, couleur=GRIS, alignement=PP_ALIGN.RIGHT)


def source(diapo, contenu: str):
    """Mention de source, en bas de diapositive."""
    texte(diapo, MARGE, HAUTEUR - Inches(0.72), LARGEUR_UTILE, Inches(0.25), contenu,
          taille=9, couleur=GRIS, italique=True)


# ---------------------------------------------------------------------------
# Maquettes d'interface — formes natives uniquement
# ---------------------------------------------------------------------------
def cadre_telephone(diapo, x, y, w, h):
    """Coque de téléphone et écran ; retourne le rectangle utile de l'écran."""
    coque = forme(diapo, MSO_SHAPE.ROUNDED_RECTANGLE, x, y, w, h)
    coque.fill.solid()
    coque.fill.fore_color.rgb = NUIT
    coque.line.fill.background()
    coque.adjustments[0] = 0.09

    inset = Inches(0.085)
    ecran = forme(diapo, MSO_SHAPE.ROUNDED_RECTANGLE, x + inset, y + inset, w - 2 * inset, h - 2 * inset)
    ecran.fill.solid()
    ecran.fill.fore_color.rgb = BLANC
    ecran.line.fill.background()
    ecran.adjustments[0] = 0.08
    return x + inset, y + inset, w - 2 * inset, h - 2 * inset


def barre_ecran(diapo, ex, ey, ew, titre: str, precision: str = ""):
    rectangle(diapo, ex, ey, ew, Inches(0.42), NUIT)
    texte(diapo, ex + Inches(0.12), ey + Inches(0.11), ew - Inches(0.24), Inches(0.22),
          titre, taille=8, couleur=BLANC, gras=True)
    if precision:
        texte(diapo, ex + Inches(0.12), ey + Inches(0.26), ew - Inches(0.24), Inches(0.16),
              precision, taille=5.5, couleur=GRIS_CLAIR)


def puce_statut(diapo, x, y, libelle: str, couleur, largeur=Inches(0.92), taille=5.5):
    rectangle(diapo, x, y, largeur, Inches(0.19), couleur, arrondi=True)
    texte(diapo, x, y + Inches(0.045), largeur, Inches(0.12), libelle,
          taille=taille, couleur=BLANC, gras=True, alignement=PP_ALIGN.CENTER)


def maquette_client(diapo, x, y, w, h):
    ex, ey, ew, eh = cadre_telephone(diapo, x, y, w, h)
    barre_ecran(diapo, ex, ey, ew, "Ma commande", "APIX · client final")

    puce_statut(diapo, ex + Inches(0.12), ey + Inches(0.55), "EN ROUTE", ORANGE)
    texte(diapo, ex + Inches(0.12), ey + Inches(0.83), ew - Inches(0.24), Inches(0.14),
          "BON N° PPC-2026-0448", taille=6, couleur=GRIS, gras=True)
    texte(diapo, ex + Inches(0.12), ey + Inches(1.02), ew - Inches(0.24), Inches(0.3),
          "1 046 $", taille=19, couleur=NUIT, gras=True, police=POLICE_TITRE)
    texte(diapo, ex + Inches(0.12), ey + Inches(1.38), ew - Inches(0.24), Inches(0.14),
          "100 sacs · ciment 42,5", taille=6.5, couleur=GRIS)

    # Détail du prix
    lignes = [("Ciment", "880 $"), ("Transport calculé", "150 $"), ("Total payé", "1 046 $")]
    yy = ey + Inches(1.62)
    for index, (libelle, montant) in enumerate(lignes):
        gras = index == 2
        rectangle(diapo, ex + Inches(0.1), yy - Inches(0.02), ew - Inches(0.2), Inches(0.005), GRIS_CLAIR)
        texte(diapo, ex + Inches(0.12), yy + Inches(0.02), Inches(1.2), Inches(0.14), libelle,
              taille=6.5, couleur=NUIT if gras else GRIS, gras=gras)
        texte(diapo, ex + Inches(1.0), yy + Inches(0.02), ew - Inches(1.12), Inches(0.14), montant,
              taille=6.5, couleur=NUIT if gras else GRIS, gras=gras, alignement=PP_ALIGN.RIGHT)
        yy += Inches(0.24)

    # Progression
    etapes = ["Payée", "Chargée", "En route", "Livrée"]
    xx = ex + Inches(0.14)
    for index, etape in enumerate(etapes):
        couleur = VERT if index < 2 else (ORANGE if index == 2 else GRIS_CLAIR)
        cercle = forme(diapo, MSO_SHAPE.OVAL, xx, ey + Inches(2.42), Inches(0.09), Inches(0.09))
        cercle.fill.solid()
        cercle.fill.fore_color.rgb = couleur
        cercle.line.fill.background()
        texte(diapo, xx - Inches(0.14), ey + Inches(2.55), Inches(0.38), Inches(0.12), etape,
              taille=4.8, couleur=GRIS, alignement=PP_ALIGN.CENTER)
        xx += Inches(0.47)

    # Zone carte
    rectangle(diapo, ex + Inches(0.1), ey + Inches(2.78), ew - Inches(0.2), Inches(1.05),
              RGBColor(0xEC, 0xF0, 0xEE), arrondi=True)
    for decalage, longueur in ((0, 0.9), (0.55, 0.75)):
        trait = forme(diapo, MSO_SHAPE.RECTANGLE, ex + Inches(0.22 + decalage * 0.1),
                      ey + Inches(3.05 + decalage), Inches(longueur), Inches(0.02))
        trait.fill.solid()
        trait.fill.fore_color.rgb = RGBColor(0xB9, 0xC6, 0xCC)
        trait.line.fill.background()
    marqueur = forme(diapo, MSO_SHAPE.OVAL, ex + Inches(1.28), ey + Inches(3.36), Inches(0.1), Inches(0.1))
    marqueur.fill.solid()
    marqueur.fill.fore_color.rgb = ORANGE
    marqueur.line.fill.background()
    texte(diapo, ex + Inches(0.2), ey + Inches(3.62), ew - Inches(0.4), Inches(0.12),
          "Dernière position : il y a 4 min", taille=5, couleur=GRIS, italique=True)

    # Bouton
    rectangle(diapo, ex + Inches(0.1), ey + Inches(3.96), ew - Inches(0.2), Inches(0.32),
              NUIT, arrondi=True)
    texte(diapo, ex + Inches(0.1), ey + Inches(4.04), ew - Inches(0.2), Inches(0.16),
          "Suivre le camion", taille=7, couleur=BLANC, gras=True, alignement=PP_ALIGN.CENTER)


def maquette_chauffeur(diapo, x, y, w, h):
    ex, ey, ew, eh = cadre_telephone(diapo, x, y, w, h)
    barre_ecran(diapo, ex, ey, ew, "Course 118", "APIX · chauffeur")

    puce_statut(diapo, ex + Inches(0.12), ey + Inches(0.55), "HORS LIGNE", GRIS, largeur=Inches(0.82))
    texte(diapo, ex + Inches(0.12), ey + Inches(0.8), ew - Inches(0.24), Inches(0.14),
          "2 preuves en attente de réseau", taille=5, couleur=GRIS, italique=True)

    cartes = [
        ("Photo géolocalisée", "−4,3276 ; 15,3136", VERT, "Prise à 14 h 22"),
        ("Scellé 44821", "Conforme au départ", VERT, "Vérifié à l'arrivée"),
        ("Poids constaté", "4 960 kg", ORANGE, "Écart 1,0 % — dans la tolérance"),
    ]
    yy = ey + Inches(1.02)
    for titre, valeur, couleur, precision in cartes:
        rectangle(diapo, ex + Inches(0.1), yy, ew - Inches(0.2), Inches(0.82), SABLE, arrondi=True)
        texte(diapo, ex + Inches(0.2), yy + Inches(0.08), Inches(1.25), Inches(0.14), titre,
              taille=6, couleur=GRIS, gras=True)
        texte(diapo, ex + Inches(0.2), yy + Inches(0.25), Inches(1.35), Inches(0.18), valeur,
              taille=8, couleur=NUIT, gras=True)
        texte(diapo, ex + Inches(0.2), yy + Inches(0.46), Inches(1.4), Inches(0.22), precision,
              taille=4.8, couleur=GRIS)
        pastille = forme(diapo, MSO_SHAPE.OVAL, ex + Inches(1.62), yy + Inches(0.11),
                         Inches(0.12), Inches(0.12))
        pastille.fill.solid()
        pastille.fill.fore_color.rgb = couleur
        pastille.line.fill.background()
        yy += Inches(0.88)

    rectangle(diapo, ex + Inches(0.1), ey + Inches(3.72), ew - Inches(0.2), Inches(0.34),
              ORANGE, arrondi=True)
    texte(diapo, ex + Inches(0.1), ey + Inches(3.81), ew - Inches(0.2), Inches(0.16),
          "Valider la livraison", taille=7, couleur=BLANC, gras=True, alignement=PP_ALIGN.CENTER)


def panneau_backoffice(diapo, x, y, w, h):
    rectangle(diapo, x, y, w, h, BLANC, arrondi=True)
    contour(diapo, x, y, w, h, GRIS_CLAIR, Pt(1), arrondi=True)

    # Barre de navigateur
    rectangle(diapo, x, y, w, Inches(0.3), RGBColor(0xEA, 0xEE, 0xF1))
    for index, couleur in enumerate((RGBColor(0xE0, 0x6B, 0x2D), RGBColor(0xC9, 0xB4, 0x6A), RGBColor(0x8C, 0xB5, 0x9E))):
        point = forme(diapo, MSO_SHAPE.OVAL, x + Inches(0.14 + index * 0.16), y + Inches(0.1),
                      Inches(0.09), Inches(0.09))
        point.fill.solid()
        point.fill.fore_color.rgb = couleur
        point.line.fill.background()
    rectangle(diapo, x + Inches(0.65), y + Inches(0.07), w - Inches(0.85), Inches(0.16),
              BLANC, arrondi=True)
    texte(diapo, x + Inches(0.74), y + Inches(0.09), w - Inches(1.0), Inches(0.12),
          "backoffice · transporteurs homologués", taille=5, couleur=GRIS)

    # Indicateurs
    indicateurs = [("142", "commandes"), ("87 %", "à l'heure"), ("3", "litiges")]
    xx = x + Inches(0.16)
    for valeur, libelle in indicateurs:
        rectangle(diapo, xx, y + Inches(0.42), Inches(0.78), Inches(0.5), SABLE, arrondi=True)
        texte(diapo, xx, y + Inches(0.47), Inches(0.78), Inches(0.2), valeur,
              taille=10, couleur=NUIT, gras=True, alignement=PP_ALIGN.CENTER)
        texte(diapo, xx, y + Inches(0.68), Inches(0.78), Inches(0.14), libelle,
              taille=5, couleur=GRIS, alignement=PP_ALIGN.CENTER)
        xx += Inches(0.86)

    # Tableau
    entetes = ["Transporteur", "Engin", "Statut"]
    positions = [x + Inches(0.16), x + Inches(1.62), x + Inches(2.85)]
    for index, entete in enumerate(entetes):
        texte(diapo, positions[index], y + Inches(1.04), Inches(1.2), Inches(0.12), entete,
              taille=5, couleur=GRIS, gras=True)

    lignes = [
        ("Trans-Kongo", "Porteur 15 t", "Homologué", VERT),
        ("Sanga Logistique", "Semi 30 t", "Assurance expirée", RGBColor(0xC0, 0x39, 0x2B)),
        ("Mbala Transit", "Porteur 10 t", "Homologué", VERT),
    ]
    yy = y + Inches(1.22)
    for nom, engin, statut, couleur in lignes:
        rectangle(diapo, x + Inches(0.12), yy - Inches(0.03), w - Inches(0.24), Inches(0.005), GRIS_CLAIR)
        texte(diapo, positions[0], yy + Inches(0.04), Inches(1.4), Inches(0.12), nom, taille=5.5, couleur=NUIT)
        texte(diapo, positions[1], yy + Inches(0.04), Inches(1.15), Inches(0.12), engin, taille=5.5, couleur=GRIS)
        puce_statut(diapo, positions[2], yy + Inches(0.01), statut, couleur,
                    largeur=Inches(0.92) if len(statut) < 12 else Inches(0.98), taille=4.5)
        yy += Inches(0.3)


def panneau_calculateur(diapo, x, y, w, h):
    rectangle(diapo, x, y, w, h, NUIT, arrondi=True)
    texte(diapo, x + Inches(0.22), y + Inches(0.18), w - Inches(0.44), Inches(0.16),
          "CALCULATEUR DE TRANSPORT", taille=7, couleur=ORANGE, gras=True)
    texte(diapo, x + Inches(0.22), y + Inches(0.4), w - Inches(0.44), Inches(0.2),
          "Kimpese → Kinshasa · 200 km · 8 tonnes", taille=9, couleur=BLANC, gras=True)

    lignes = [
        ("Coût fixe de l'axe", "180 $"),
        ("0,055 $ × 200 km × 8 t", "88 $"),
        ("Coefficient de saison", "× 1,00"),
    ]
    yy = y + Inches(0.75)
    for libelle, valeur in lignes:
        texte(diapo, x + Inches(0.22), yy, Inches(1.9), Inches(0.14), libelle, taille=6.5,
              couleur=RGBColor(0xA8, 0xBA, 0xC8))
        texte(diapo, x + Inches(2.1), yy, w - Inches(2.32), Inches(0.14), valeur, taille=6.5,
              couleur=BLANC, alignement=PP_ALIGN.RIGHT)
        yy += Inches(0.24)

    rectangle(diapo, x + Inches(0.22), y + Inches(1.5), w - Inches(0.44), Inches(0.01), RGBColor(0x3A, 0x56, 0x70))
    texte(diapo, x + Inches(0.22), y + Inches(1.6), Inches(1.9), Inches(0.14), "Prix calculé",
          taille=7, couleur=BLANC, gras=True)
    texte(diapo, x + Inches(1.9), y + Inches(1.52), w - Inches(2.12), Inches(0.24), "268 $",
          taille=13, couleur=ORANGE, gras=True, alignement=PP_ALIGN.RIGHT)
    texte(diapo, x + Inches(0.22), y + Inches(1.94), w - Inches(0.44), Inches(0.14),
          "Soit 33,50 $ la tonne — et non un forfait identique quel que soit le trajet.",
          taille=6, couleur=RGBColor(0xA8, 0xBA, 0xC8), italique=True)


# ---------------------------------------------------------------------------
# Diapositives principales
# ---------------------------------------------------------------------------
def s01_titre(prs):
    diapo = prs.slides.add_slide(prs.slide_layouts[6])
    fond(diapo, NUIT)
    photo(diapo, "couverture", 0, 0, LARGEUR, HAUTEUR)
    voile(diapo, 0, 0, LARGEUR, HAUTEUR, NUIT, 0.68)
    rectangle(diapo, 0, 0, Inches(0.16), HAUTEUR, ORANGE)

    texte(diapo, MARGE, Inches(1.5), Inches(9), Inches(0.3), "F B B   ·   A P I X",
          taille=12, couleur=ORANGE_PALE, gras=True)
    texte(diapo, MARGE, Inches(1.95), Inches(11.5), Inches(1.4), "APIX All In One",
          taille=64, couleur=BLANC, gras=True, police=POLICE_TITRE, interligne=0.95)
    texte(diapo, MARGE, Inches(3.3), Inches(9.6), Inches(1.2),
          "Le ciment est payé avant d'être livré.\nLa preuve, elle, n'arrive jamais.",
          taille=28, couleur=BLANC, interligne=1.2)
    rectangle(diapo, MARGE, Inches(4.75), Inches(1.5), Inches(0.045), ORANGE)
    texte(diapo, MARGE, Inches(5.05), Inches(10.6), Inches(0.8),
          ["Smartphone, web, hors connexion : une seule plateforme, du bon de commande à la facture.",
           "Direction générale de PPC  ·  4 novembre 2026"],
          taille=14, couleur=RGBColor(0xC3, 0xD0, 0xDA), interligne=1.5)
    notes(diapo, "20 minutes, 12 diapositives, un seul message : après le paiement, il faut une preuve. "
                 "Ne pas présenter le produit ici, poser l'accroche et passer au problème.")


def s02_probleme(prs):
    diapo = prs.slides.add_slide(prs.slide_layouts[6])
    fond(diapo, SABLE)
    photo(diapo, "douleur_route", Inches(7.1), 0, LARGEUR - Inches(7.1), HAUTEUR)
    voile(diapo, Inches(7.1), 0, LARGEUR - Inches(7.1), HAUTEUR, NUIT, 0.2)

    texte(diapo, MARGE, Inches(0.95), Inches(5.5), Inches(0.28), "LE PROBLÈME",
          taille=11, couleur=ORANGE, gras=True)
    texte(diapo, MARGE, Inches(1.35), Inches(5.7), Inches(2.0),
          ["Le paiement est", "certifié.", "La marchandise, non."],
          taille=38, couleur=NUIT, gras=True, police=POLICE_TITRE, interligne=1.0)
    liste(diapo, MARGE, Inches(3.75), Inches(5.6), Inches(2.3), [
        ("Le client paie, ", "puis attend. Sans information."),
        ("Le transporteur livre, ", "sans constat contradictoire."),
        ("PPC arbitre les litiges ", "sans preuve à produire."),
    ], taille=14, couleur=GRIS, interligne=1.2, espace=14)
    texte(diapo, MARGE, Inches(6.15), Inches(5.7), Inches(0.5),
          "C'est votre marque qui répond de ce qu'elle ne contrôle pas.",
          taille=13, couleur=NUIT, gras=True, italique=True)
    pied(diapo)
    notes(diapo, "Ne pas accuser les transporteurs : ils sont partenaires tiers, pas fautifs. "
                 "Le problème est l'absence de preuve partagée.")


def s03_solution(prs):
    diapo = prs.slides.add_slide(prs.slide_layouts[6])
    fond(diapo, NUIT)
    en_tete(diapo, "La solution", "Chaque étape produit une preuve, et ouvre la suivante", 3, sombre=True)

    jalons = [
        ("J1", "Compte vérifié", "Identité et plafonds"),
        ("J2", "Bon certifié", "Numéro unique, QR signé"),
        ("J3", "Paiement séquestré", "Fonds cantonnés"),
        ("J4", "Chargement", "Pesée, scellé, photo"),
        ("J5", "Transport suivi", "Positions et incidents"),
        ("J6", "Livraison prouvée", "Validation et litige tranché"),
    ]
    largeur = Inches(2.02)
    pas = Inches(1.96)
    x = MARGE
    for index, (code, titre, preuve) in enumerate(jalons):
        chevron = forme(diapo, MSO_SHAPE.CHEVRON, x, Inches(2.45), largeur, Inches(0.8))
        chevron.fill.solid()
        chevron.fill.fore_color.rgb = ORANGE if index % 2 == 0 else RGBColor(0xC9, 0x57, 0x1F)
        chevron.line.fill.background()
        paragraphe = chevron.text_frame.paragraphs[0]
        paragraphe.alignment = PP_ALIGN.CENTER
        run = paragraphe.add_run()
        run.text = code
        run.font.name = POLICE
        run.font.size = Pt(15)
        run.font.bold = True
        run.font.color.rgb = BLANC

        texte(diapo, x + Inches(0.18), Inches(3.42), largeur - Inches(0.24), Inches(0.5),
              titre, taille=12, couleur=BLANC, gras=True, interligne=1.1)
        texte(diapo, x + Inches(0.18), Inches(3.98), largeur - Inches(0.24), Inches(0.7),
              preuve, taille=9.5, couleur=RGBColor(0x9F, 0xB2, 0xC2), interligne=1.25)
        x += pas

    texte(diapo, MARGE, Inches(5.05), LARGEUR_UTILE, Inches(0.6),
          "Un seul identifiant client, du bon de commande à la facture. La preuve ne se reconstitue pas après coup : elle se produit.",
          taille=15, couleur=ORANGE_PALE, italique=True, interligne=1.25)
    pied(diapo, sombre=True)
    notes(diapo, "Ne pas détailler les six jalons. Le message est la dépendance : sans la preuve du jalon "
                 "précédent, le suivant ne s'ouvre pas.")


def s04_marche(prs):
    diapo = prs.slides.add_slide(prs.slide_layouts[6])
    fond(diapo, SABLE)
    en_tete(diapo, "Le marché", "Trois acheteurs, deux populations à équiper, un même socle", 4)

    profils = [
        ("Dépôt / revendeur", "50 à 500 sacs", "Réapprovisionnement rapide, prix stable, crédit."),
        ("Entreprise / chantier", "200 à 3 000 sacs", "Facture conforme, traçabilité, respect du planning."),
        ("Particulier / artisan", "5 à 50 sacs", "Prix total connu d'avance, livraison simple, preuve d'achat."),
    ]
    largeur = (LARGEUR_UTILE - Inches(0.6)) / 3
    x = MARGE
    for titre, volume, attente in profils:
        rectangle(diapo, x, Inches(2.3), largeur, Inches(1.95), BLANC, arrondi=True)
        texte(diapo, x + Inches(0.26), Inches(2.5), largeur - Inches(0.5), Inches(0.5),
              titre, taille=14, couleur=NUIT, gras=True, interligne=1.05)
        texte(diapo, x + Inches(0.26), Inches(3.02), largeur - Inches(0.5), Inches(0.25),
              volume, taille=10, couleur=ORANGE, gras=True)
        texte(diapo, x + Inches(0.26), Inches(3.34), largeur - Inches(0.5), Inches(0.75),
              attente, taille=11, couleur=GRIS, interligne=1.2)
        x += largeur + Inches(0.3)

    rectangle(diapo, MARGE, Inches(4.55), LARGEUR_UTILE, Inches(1.35), NUIT, arrondi=True)
    texte(diapo, MARGE + Inches(0.35), Inches(4.75), Inches(4.2), Inches(0.3),
          "DEUX POPULATIONS À ÉQUIPER", taille=9, couleur=ORANGE, gras=True)
    texte(diapo, MARGE + Inches(0.35), Inches(5.05), Inches(4.8), Inches(0.7),
          ["Transporteurs partenaires", "homologués par PPC, et non flotte propre"],
          taille=12, couleur=BLANC, gras=True, interligne=1.2)
    texte(diapo, MARGE + Inches(5.6), Inches(5.05), Inches(4.8), Inches(0.7),
          ["Administration PPC", "homologation, barème, litiges, pilotage"],
          taille=12, couleur=BLANC, gras=True, interligne=1.2)

    source(diapo, "Segmentation à confirmer avec les volumes réels de PPC : aucun chiffre de marché n'est avancé ici.")
    notes(diapo, "Assumer l'absence de chiffre : proposer de remplir cette diapositive avec leurs volumes "
                 "pendant l'atelier de cadrage. C'est plus crédible qu'un chiffre inventé.")


def s05_modele(prs):
    diapo = prs.slides.add_slide(prs.slide_layouts[6])
    fond(diapo, SABLE)
    en_tete(diapo, "Le modèle économique", "Quatre sources de valeur, trois façons de la facturer", 5)

    sources = [
        ("Certification", "Bons et preuves signés, vérifiables, opposables."),
        ("Coût logistique évité", "Remplissage, litiges, impayés : trois postes qui se mesurent."),
        ("Paiement accéléré", "Le transporteur est payé après preuve, sans avance de trésorerie."),
        ("Donnée de demande", "Volume par axe, produit et période — un actif pour la production."),
    ]
    largeur = Inches(2.72)
    x = MARGE
    for index, (titre, corps) in enumerate(sources, start=1):
        carte(diapo, x, Inches(2.3), largeur, Inches(2.15), f"0{index}", titre, corps,
              taille_titre=13, taille_corps=10.5)
        x += largeur + Inches(0.29)

    rectangle(diapo, MARGE, Inches(4.85), LARGEUR_UTILE, Inches(1.5), BLANC, arrondi=True)
    texte(diapo, MARGE + Inches(0.32), Inches(5.02), Inches(10.9), Inches(0.3),
          "TROIS MODÈLES POSSIBLES — RECOMMANDATION : LE MIXTE", taille=9, couleur=ORANGE, gras=True)
    modeles = [
        ("Frais par course", "Simple, aligné sur l'usage"),
        ("Abonnement PPC", "Prévisible, finance l'exploitation"),
        ("Mixte", "Base fixe + frais dégressifs"),
    ]
    x = MARGE + Inches(0.32)
    for titre, precision in modeles:
        texte(diapo, x, Inches(5.38), Inches(3.4), Inches(0.25), titre, taille=12, couleur=NUIT, gras=True)
        texte(diapo, x, Inches(5.65), Inches(3.4), Inches(0.25), precision, taille=10, couleur=GRIS)
        x += Inches(3.55)

    source(diapo, "Aucun prix n'est avancé : le modèle se cale sur les volumes et le barème réels de PPC.")
    notes(diapo, "Si la question du prix arrive, répondre par la méthode : part variable indexée sur le volume "
                 "traité, part fixe pour l'exploitation. Les chiffres se posent après le cadrage.")


def s06_opportunite(prs):
    diapo = prs.slides.add_slide(prs.slide_layouts[6])
    fond(diapo, NUIT)
    en_tete(diapo, "L'opportunité", "Quatre briques que personne d'autre ne réunit", 6, sombre=True)

    briques = [
        ("Ubiquité",
         "Android, iOS, web, plus le mode hors connexion 72 heures et le repli SMS / USSD."),
        ("Séquestre",
         "Les fonds sont cantonnés chez une banque habilitée et libérés par jalons, jamais à la commande."),
        ("Preuve géolocalisée",
         "Photo horodatée et géolocalisée, QR nominatif à usage unique, pesée contradictoire, numéro de scellé."),
        ("Prix calculé",
         "Aujourd'hui un forfait identique quel que soit le trajet. Demain, un prix à l'axe et au poids, publié par PPC."),
    ]
    largeur = (LARGEUR_UTILE - Inches(0.6)) / 2
    for index, (titre, corps) in enumerate(briques):
        colonne = index % 2
        ligne = index // 2
        x = MARGE + colonne * (largeur + Inches(0.6))
        y = Inches(2.35) + ligne * Inches(1.85)
        rectangle(diapo, x, y, largeur, Inches(1.62), NUIT_MOYEN, arrondi=True)
        rectangle(diapo, x, y, Inches(0.07), Inches(1.62), ORANGE)
        texte(diapo, x + Inches(0.35), y + Inches(0.2), largeur - Inches(0.6), Inches(0.3),
              titre, taille=15, couleur=BLANC, gras=True)
        texte(diapo, x + Inches(0.35), y + Inches(0.58), largeur - Inches(0.6), Inches(0.9),
              corps, taille=11, couleur=RGBColor(0xB6, 0xC6, 0xD4), interligne=1.25)

    pied(diapo, sombre=True)
    notes(diapo, "Les deux briques à marteler : la preuve géolocalisée, qui rend le litige arbitrable, et le prix "
                 "calculé, qui remplace un forfait aveugle. Les deux autres sécurisent l'adoption.")


def s07_interfaces(prs):
    diapo = prs.slides.add_slide(prs.slide_layouts[6])
    fond(diapo, SABLE)
    en_tete(diapo, "Les interfaces", "Trois usages, un seul socle de données", 7)

    hauteur_telephone = Inches(4.4)
    largeur_telephone = Inches(2.25)

    maquette_client(diapo, Inches(1.15), Inches(1.95), largeur_telephone, hauteur_telephone)
    texte(diapo, Inches(1.15), Inches(6.42), largeur_telephone, Inches(0.35),
          ["Client final", "Commander, payer, suivre"], taille=9, couleur=GRIS,
          alignement=PP_ALIGN.CENTER, interligne=1.2)

    maquette_chauffeur(diapo, Inches(3.85), Inches(1.95), largeur_telephone, hauteur_telephone)
    texte(diapo, Inches(3.85), Inches(6.42), largeur_telephone, Inches(0.35),
          ["Chauffeur", "Livrer et prouver, même sans réseau"], taille=9, couleur=GRIS,
          alignement=PP_ALIGN.CENTER, interligne=1.2)

    panneau_backoffice(diapo, Inches(6.85), Inches(1.95), Inches(5.0), Inches(2.15))
    texte(diapo, Inches(6.85), Inches(4.18), Inches(5.0), Inches(0.3),
          ["Back-office PPC", "Homologuer, publier le barème, trancher les litiges"],
          taille=9, couleur=GRIS, interligne=1.2)

    panneau_calculateur(diapo, Inches(6.85), Inches(4.55), Inches(5.0), Inches(1.85))

    source(diapo, "Maquettes schématiques, non contractuelles : elles illustrent le parcours, pas la charte définitive.")
    notes(diapo, "Diapositive de respiration : laisser regarder. Insister sur le calculateur, qui répond "
                 "directement au forfait actuel, et sur l'écran chauffeur qui fonctionne hors réseau.")


def s08_groupage(prs):
    diapo = prs.slides.add_slide(prs.slide_layouts[6])
    fond(diapo, NUIT)
    en_tete(diapo, "La démonstration", "Cinq petits acheteurs, un seul camion", 8, sombre=True)
    texte(diapo, MARGE, Inches(1.88), Inches(11.4), Inches(0.35),
          "Simulation sur un axe de 210 km, cinq clients, cinq points de livraison.",
          taille=13, couleur=RGBColor(0xB6, 0xC6, 0xD4), italique=True)

    clients = [("Dépôt Ngaliema", "60 sacs · 3,0 t"), ("Chantier Limete", "200 sacs · 10,0 t"),
               ("Dépôt Matete", "120 sacs · 6,0 t"), ("Artisan Kintambo", "20 sacs · 1,0 t"),
               ("Dépôt Masina", "120 sacs · 6,0 t")]
    y = Inches(2.4)
    for nom, detail in clients:
        rectangle(diapo, MARGE, y, Inches(4.55), Inches(0.55), NUIT_MOYEN, arrondi=True)
        texte(diapo, MARGE + Inches(0.26), y + Inches(0.15), Inches(2.5), Inches(0.28),
              nom, taille=11.5, couleur=BLANC, gras=True)
        texte(diapo, MARGE + Inches(2.95), y + Inches(0.17), Inches(1.45), Inches(0.28),
              detail, taille=10, couleur=RGBColor(0xA8, 0xBA, 0xC8))
        y += Inches(0.64)

    fleche = forme(diapo, MSO_SHAPE.RIGHT_ARROW, Inches(5.62), Inches(3.95), Inches(0.85), Inches(0.4))
    fleche.fill.solid()
    fleche.fill.fore_color.rgb = ORANGE
    fleche.line.fill.background()

    rectangle(diapo, Inches(6.75), Inches(2.4), Inches(5.75), Inches(2.75), ORANGE, arrondi=True)
    texte(diapo, Inches(7.15), Inches(2.68), Inches(5.0), Inches(0.4), "1 CAMION · 26 TONNES",
          taille=17, couleur=BLANC, gras=True)
    lignes = [("Transport total", "900 $ répartis au prorata du poids × distance"),
              ("Prix par sac", "entre 1,67 $ et 1,79 $ selon la zone"),
              ("Remplissage", "86,7 % — le lot se déclenche"),
              ("Sans groupage", "5 commandes, 5 camions, 5 tournées")]
    yy = Inches(3.28)
    for libelle, valeur in lignes:
        texte(diapo, Inches(7.15), yy, Inches(1.75), Inches(0.28), libelle, taille=10,
              couleur=RGBColor(0xFF, 0xE7, 0xD9))
        texte(diapo, Inches(8.95), yy, Inches(3.4), Inches(0.28), valeur, taille=11,
              couleur=BLANC, gras=True)
        yy += Inches(0.42)

    rectangle(diapo, MARGE, Inches(5.68), LARGEUR_UTILE, Inches(1.05), NUIT_MOYEN, arrondi=True)
    texte(diapo, MARGE + Inches(0.3), Inches(5.82), Inches(10.8), Inches(0.85),
          [{"runs": [("Et si le lot ne se remplit pas ? ", {"gras": True, "couleur": ORANGE_PALE, "taille": 12.5}),
                     ("Trois issues sont écrites : la poursuite avec un engin plus petit, le report accepté par le client "
                      "jusqu'au remplissage du lot, ou le remboursement à sa demande. Aucun client ne reste bloqué.",
                      {"couleur": RGBColor(0xC3, 0xD0, 0xDA), "taille": 12.5})]}], interligne=1.3)
    pied(diapo, sombre=True)
    notes(diapo, "Chiffres recalculables devant eux dans le simulateur joint. C'est la seule diapositive avec des "
                 "montants : les assumer comme une simulation, pas comme une prévision.")


def s09_marketing(prs):
    diapo = prs.slides.add_slide(prs.slide_layouts[6])
    fond(diapo, SABLE)
    en_tete(diapo, "Le déploiement", "Comment on démarre, et pourquoi cela prend", 9)

    etapes = [
        ("1", "Un axe pilote", "Un produit, un axe, cinq à dix transporteurs déjà connus de PPC. On mesure avant d'étendre."),
        ("2", "Les dépôts deviennent points de retrait", "Le réseau existant est renforcé, pas contourné : c'est lui qui amène les petits acheteurs."),
        ("3", "Les transporteurs vendent", "Un transporteur payé en 24 heures parle de la plateforme à ses propres clients."),
        ("4", "Généralisation par axe", "On ouvre un axe quand les indicateurs du précédent sont tenus, pas avant."),
    ]
    y = Inches(2.25)
    for code, titre, corps in etapes:
        rectangle(diapo, MARGE, y, LARGEUR_UTILE, Inches(1.02), BLANC, arrondi=True)
        cercle = forme(diapo, MSO_SHAPE.OVAL, MARGE + Inches(0.26), y + Inches(0.31), Inches(0.4), Inches(0.4))
        cercle.fill.solid()
        cercle.fill.fore_color.rgb = ORANGE
        cercle.line.fill.background()
        texte(diapo, MARGE + Inches(0.26), y + Inches(0.38), Inches(0.4), Inches(0.25), code,
              taille=12, couleur=BLANC, gras=True, alignement=PP_ALIGN.CENTER)
        texte(diapo, MARGE + Inches(0.85), y + Inches(0.2), Inches(4.2), Inches(0.3),
              titre, taille=13, couleur=NUIT, gras=True)
        texte(diapo, MARGE + Inches(5.3), y + Inches(0.22), Inches(6.0), Inches(0.6),
              corps, taille=11, couleur=GRIS, interligne=1.2)
        y += Inches(1.12)

    texte(diapo, MARGE, Inches(6.75), LARGEUR_UTILE, Inches(0.3),
          "Ce qui ne dépend pas de FBB : la vitesse d'homologation des transporteurs et la publication du barème.",
          taille=10, couleur=GRIS, italique=True)
    notes(diapo, "Point d'honnêteté à assumer : deux facteurs de calendrier ne nous appartiennent pas. "
                 "Le dire avant qu'on ne nous l'oppose.")


def s10_concurrence(prs):
    diapo = prs.slides.add_slide(prs.slide_layouts[6])
    fond(diapo, SABLE)
    en_tete(diapo, "La concurrence", "Une différence de nature, pas de fonctionnalités", 10)

    donnees = [
        ["Critère", "Digiciment", "APIX All In One"],
        ["Nature", "Application de transactions", "Chaîne de preuve, du paiement au sac livré"],
        ["Unité de référence", "La transaction", "Le bon de commande certifié"],
        ["Transporteurs", "Gestion locale, non documentée", "Homologation par PPC, datée et révocable"],
        ["Prix du transport", "Forfaitaire", "Calculé à l'axe et au poids, barème PPC"],
        ["Preuve de livraison", "Reçu simple", "QR, photo géolocalisée, pesée, scellé"],
        ["Sécurité des fonds", "Paiement direct", "Séquestre libéré par jalons"],
        ["Hors connexion", "Connexion requise", "72 heures pour le chauffeur"],
    ]
    tableau(diapo, MARGE, Inches(2.25), LARGEUR_UTILE, donnees,
            [Inches(2.35), Inches(4.05), Inches(5.25)], hauteur_ligne=Inches(0.45), taille=11,
            colonne_forte=2)
    texte(diapo, MARGE, Inches(6.45), LARGEUR_UTILE, Inches(0.6),
          "Comparaison établie sur le périmètre fonctionnel annoncé. Toute correction de votre part est bienvenue : "
          "elle sera intégrée avant la démonstration.",
          taille=9.5, couleur=GRIS, italique=True)
    notes(diapo, "Ne jamais ironiser. Laisser le tableau parler, puis enchaîner : « ce n'est pas un match, "
                 "c'est une différence de nature ». Rester factuel, c'est ce qui convainc une direction générale.")


def s11_equipe(prs):
    diapo = prs.slides.add_slide(prs.slide_layouts[6])
    fond(diapo, SABLE)
    en_tete(diapo, "L'équipe", "Qui porte le projet", 11)

    roles = [
        ("Direction de projet", "Pilotage, arbitrages de périmètre, relation PPC."),
        ("Ingénierie plateforme", "Applications mobile et web, séquestre, sécurité, hors-ligne."),
        ("Métier logistique", "Barème, homologation, traitement des litiges."),
    ]
    largeur = (LARGEUR_UTILE - Inches(0.6)) / 3
    x = MARGE
    for titre, corps in roles:
        rectangle(diapo, x, Inches(2.3), largeur, Inches(1.75), BLANC, arrondi=True)
        texte(diapo, x + Inches(0.26), Inches(2.52), largeur - Inches(0.5), Inches(0.3),
              titre, taille=13, couleur=NUIT, gras=True)
        texte(diapo, x + Inches(0.26), Inches(2.88), largeur - Inches(0.5), Inches(0.9),
              corps, taille=10.5, couleur=GRIS, interligne=1.2)
        texte(diapo, x + Inches(0.26), Inches(3.62), largeur - Inches(0.5), Inches(0.25),
              "Nom et parcours à compléter", taille=9, couleur=RGBColor(0x8E, 0x9B, 0xA5), italique=True)
        x += largeur + Inches(0.3)

    rectangle(diapo, MARGE, Inches(4.3), LARGEUR_UTILE, Inches(1.55), NUIT, arrondi=True)
    texte(diapo, MARGE + Inches(0.35), Inches(4.5), Inches(10.8), Inches(0.3),
          "POURQUOI FBB", taille=9, couleur=ORANGE, gras=True)
    liste(diapo, MARGE + Inches(0.35), Inches(4.82), Inches(10.6), Inches(0.9), [
        ("APIX est déjà en production ", "sur les comptes de PPC : nous ne partons pas d'une page blanche."),
        ("Nous ne touchons ni au transport ni à la vente : ", "nous outillons ceux qui les font."),
    ], taille=12, couleur=BLANC, puce=ORANGE, interligne=1.2, espace=8)
    source(diapo, "Cette diapositive doit être complétée avec les noms et références réelles avant toute présentation.")
    notes(diapo, "Diapositive à personnaliser impérativement : une direction générale achète une équipe autant "
                 "qu'un produit. Prévoir une référence client ou un chiffre d'exploitation APIX.")


def s12_conclusion(prs):
    diapo = prs.slides.add_slide(prs.slide_layouts[6])
    fond(diapo, NUIT)
    en_tete(diapo, "La suite", "Cinq décisions, et nous commençons", 12, sombre=True)

    decisions = [
        ("D1", "Qui est le donneur d'ordre du transport ?"),
        ("D2", "Quelle banque porte le compte de cantonnement ?"),
        ("D3", "Sur quelle base construire le barème ?"),
        ("D4", "Quel circuit pour l'encaissement en espèces ?"),
        ("D5", "Quel rôle pour le réseau de dépôts ?"),
    ]
    y = Inches(2.3)
    for code, question in decisions:
        rectangle(diapo, MARGE, y, Inches(7.0), Inches(0.62), NUIT_MOYEN, arrondi=True)
        texte(diapo, MARGE + Inches(0.28), y + Inches(0.16), Inches(0.6), Inches(0.3),
              code, taille=12, couleur=ORANGE, gras=True)
        texte(diapo, MARGE + Inches(1.0), y + Inches(0.17), Inches(5.8), Inches(0.3),
              question, taille=12.5, couleur=BLANC, gras=True)
        y += Inches(0.74)

    rectangle(diapo, Inches(8.25), Inches(2.3), Inches(4.25), Inches(3.3), ORANGE, arrondi=True)
    texte(diapo, Inches(8.55), Inches(2.55), Inches(3.7), Inches(0.3), "CE QUE NOUS DEMANDONS",
          taille=9, couleur=RGBColor(0x5A, 0x24, 0x0C), gras=True)
    liste(diapo, Inches(8.55), Inches(2.9), Inches(3.65), Inches(2.5), [
        "Un accord de principe sur un axe pilote",
        "Un référent métier nommé côté PPC",
        "Une date d'atelier de cadrage",
        "L'ouverture du dossier bancaire",
    ], taille=11.5, couleur=BLANC, puce=RGBColor(0x5A, 0x24, 0x0C), interligne=1.2, espace=10)

    texte(diapo, MARGE, Inches(6.25), LARGEUR_UTILE, Inches(0.5),
          "Seize semaines séparent ces décisions d'un axe pilote opérationnel.",
          taille=14, couleur=ORANGE_PALE, gras=True)
    pied(diapo, sombre=True)
    notes(diapo, "Ne pas sortir de la salle sans un référent nommé et une date d'atelier. C'est le seul "
                 "indicateur de succès de la réunion. Les annexes restent fermées sauf question.")


# ---------------------------------------------------------------------------
# Annexes — à ouvrir sur question uniquement
# ---------------------------------------------------------------------------
def a01_route(prs):
    diapo = prs.slides.add_slide(prs.slide_layouts[6])
    fond(diapo, SABLE)
    en_tete(diapo, "Annexe A1 · Feuille de route",
            "Seize semaines jusqu'au pilote, deux facteurs hors de notre contrôle", 13)

    etapes = [
        ("S1 – S3", "Cadrage", "Décisions D1 à D5, barème initial, référentiel transporteurs"),
        ("S4 – S6", "Conception", "Parcours, maquettes, architecture validée"),
        ("S7 – S18", "Développement", "Chaîne de preuve complète, back-office, application chauffeur"),
        ("S19 – S22", "Pilote", "Un axe, un produit, cinq à dix transporteurs"),
        ("Ensuite", "Généralisation", "Deuxième axe, puis groupage"),
    ]
    ligne_y = Inches(3.15)
    rectangle(diapo, MARGE, ligne_y, LARGEUR_UTILE, Inches(0.03), RGBColor(0xCF, 0xD6, 0xDB))
    pas = LARGEUR_UTILE / len(etapes)
    x = MARGE
    for periode, titre, corps in etapes:
        cercle = forme(diapo, MSO_SHAPE.OVAL, x + pas / 2 - Inches(0.1), ligne_y - Inches(0.07),
                       Inches(0.2), Inches(0.2))
        cercle.fill.solid()
        cercle.fill.fore_color.rgb = ORANGE
        cercle.line.fill.background()
        texte(diapo, x, Inches(2.5), pas - Inches(0.15), Inches(0.3), periode,
              taille=11, couleur=ORANGE, gras=True, alignement=PP_ALIGN.CENTER)
        texte(diapo, x, Inches(3.5), pas - Inches(0.15), Inches(0.35), titre,
              taille=13, couleur=NUIT, gras=True, alignement=PP_ALIGN.CENTER)
        texte(diapo, x, Inches(3.95), pas - Inches(0.15), Inches(1.2), corps,
              taille=9.5, couleur=GRIS, alignement=PP_ALIGN.CENTER, interligne=1.25)
        x += pas

    rectangle(diapo, MARGE, Inches(5.5), LARGEUR_UTILE, Inches(1.0), NUIT, arrondi=True)
    texte(diapo, MARGE + Inches(0.32), Inches(5.68), Inches(10.8), Inches(0.7),
          [{"runs": [("Hors de notre contrôle : ", {"gras": True, "couleur": ORANGE_PALE, "taille": 12}),
                     ("la vitesse d'homologation des transporteurs et la publication du barème. "
                      "Ce sont les deux seuls risques de calendrier.",
                      {"couleur": BLANC, "taille": 12})]}], interligne=1.3)
    pied(diapo)
    notes(diapo, "Annexe : ne s'ouvre que si l'on demande un calendrier ou un engagement de délai.")


def a02_bareme(prs):
    diapo = prs.slides.add_slide(prs.slide_layouts[6])
    fond(diapo, SABLE)
    en_tete(diapo, "Annexe A2 · Barème", "Du forfait au prix calculé : la formule et un exemple", 14)

    texte(diapo, MARGE, Inches(2.05), Inches(6.4), Inches(0.35),
          "Prix = (coût fixe de l'axe + coût à la tonne-kilomètre × distance × poids)"
          " × coefficient de saison × coefficient de détour",
          taille=12, couleur=NUIT, gras=True, interligne=1.3)

    tableau(diapo, MARGE, Inches(2.95), Inches(6.4), [
        ["Paramètre", "Symbole", "Exemple"],
        ["Coût fixe de l'axe", "CF", "180 $"],
        ["Coût à la tonne-kilomètre", "CTK", "0,055 $"],
        ["Distance de l'axe", "D", "200 km"],
        ["Poids transporté", "P", "8 t"],
        ["Coefficient de saison", "Ks", "1,00"],
        ["Coefficient de détour", "Kd", "1,00"],
    ], [Inches(2.9), Inches(1.0), Inches(1.5)], hauteur_ligne=Inches(0.4), taille=11)

    panneau_calculateur(diapo, Inches(7.6), Inches(2.15), Inches(4.9), Inches(2.4))
    texte(diapo, Inches(7.6), Inches(4.75), Inches(4.9), Inches(1.6),
          ["Ce que le forfait actuel ne dit pas :", 
           "— pourquoi deux trajets de longueurs différentes coûtent le même prix ;",
           "— qui supporte l'écart quand la zone réelle diffère de la zone facturée ;",
           "— comment un client de 20 sacs peut être servi sans payer un camion."],
          taille=10.5, couleur=GRIS, interligne=1.35)
    source(diapo, "Montants indicatifs, repris du classeur de barème : ils doivent être remplacés par les valeurs de PPC.")
    notes(diapo, "Annexe chiffrée : à ouvrir si l'on conteste le prix ou si l'on demande comment il est construit.")


def a03_preuve(prs):
    diapo = prs.slides.add_slide(prs.slide_layouts[6])
    fond(diapo, SABLE)
    en_tete(diapo, "Annexe A3 · Preuve et litige", "Quatre preuves, une décision motivée", 15)

    elements = [
        ("QR nominatif", "Remis au client, à usage unique, signé. Une seconde présentation est refusée."),
        ("Photo géolocalisée", "Prise à la remise, horodatée, non modifiable, avec coordonnées."),
        ("Pesée contradictoire", "Poids au chargement confronté au poids constaté, tolérance contractuelle."),
        ("Numéro de scellé", "Relevé au départ, vérifié à l'arrivée. Une rupture ouvre un litige automatique."),
    ]
    y = Inches(2.25)
    for titre, corps in elements:
        rectangle(diapo, MARGE, y, Inches(6.5), Inches(0.95), BLANC, arrondi=True)
        texte(diapo, MARGE + Inches(0.28), y + Inches(0.16), Inches(5.9), Inches(0.28),
              titre, taille=12.5, couleur=NUIT, gras=True)
        texte(diapo, MARGE + Inches(0.28), y + Inches(0.5), Inches(5.9), Inches(0.38),
              corps, taille=10.5, couleur=GRIS, interligne=1.2)
        y += Inches(1.05)

    rectangle(diapo, Inches(7.7), Inches(2.25), Inches(4.8), Inches(2.05), NUIT, arrondi=True)
    texte(diapo, Inches(7.98), Inches(2.44), Inches(4.2), Inches(0.3), "TRAITEMENT DU LITIGE",
          taille=9, couleur=ORANGE, gras=True)
    liste(diapo, Inches(7.98), Inches(2.75), Inches(4.2), Inches(1.4), [
        "Gel de la part contestée, et d'elle seule",
        "Instruction sur dossier de preuve",
        "Décision motivée par PPC",
        "Retenue au prorata, libération du solde",
    ], taille=10.5, couleur=BLANC, interligne=1.2, espace=7)

    texte(diapo, Inches(7.7), Inches(4.5), Inches(4.8), Inches(1.8),
          "Le litige le plus fréquent n'est pas le retard : c'est l'écart de poids. "
          "Sans pesée contradictoire et sans scellé, il se règle à la parole.",
          taille=10.5, couleur=GRIS, interligne=1.35)
    pied(diapo)
    notes(diapo, "Annexe : à ouvrir si l'on demande comment un litige se traite concrètement.")


def a04_groupage(prs):
    diapo = prs.slides.add_slide(prs.slide_layouts[6])
    fond(diapo, SABLE)
    en_tete(diapo, "Annexe A4 · Groupage", "Règles d'arbitrage et répartition des frais", 16)

    texte(diapo, MARGE, Inches(2.1), Inches(6.2), Inches(0.3), "ARBITRAGE D'UN LOT INCOMPLET",
          taille=9, couleur=ORANGE, gras=True)
    tableau(diapo, MARGE, Inches(2.45), Inches(6.2), [
        ["Situation", "Réponse APIX"],
        ["Seuil de remplissage atteint", "Le lot est déclenché, la course est publiée"],
        ["Délai écoulé, lot incomplet", "Poursuite avec un engin plus petit"],
        ["Le client accepte d'attendre", "Report jusqu'au remplissage du lot"],
        ["Le client refuse", "Remboursement sans frais, sur sa demande"],
    ], [Inches(2.6), Inches(3.6)], hauteur_ligne=Inches(0.48), taille=10.5)

    texte(diapo, Inches(7.4), Inches(2.1), Inches(5.1), Inches(0.3), "RÉPARTITION DES FRAIS",
          taille=9, couleur=ORANGE, gras=True)
    texte(diapo, Inches(7.4), Inches(2.45), Inches(5.1), Inches(0.6),
          "Part du client = coût de la course × (poids × distance) ÷ somme des (poids × distance) du lot",
          taille=10.5, couleur=NUIT, gras=True, interligne=1.3)
    texte(diapo, Inches(7.4), Inches(3.15), Inches(5.1), Inches(1.6),
          ["À quoi s'ajoute une quote-part des frais fixes au prorata du poids.",
           "Sans cette composante, les gros acheteurs financeraient les petits — et le mécanisme serait rejeté dès la première facture."],
          taille=10.5, couleur=GRIS, interligne=1.35)
    texte(diapo, Inches(7.4), Inches(4.95), Inches(5.1), Inches(0.8),
          "Le détail du calcul reste consultable par le client, avant et après paiement.",
          taille=10.5, couleur=NUIT, italique=True, interligne=1.3)

    rectangle(diapo, MARGE, Inches(5.6), Inches(6.2), Inches(0.95), NUIT, arrondi=True)
    texte(diapo, MARGE + Inches(0.28), Inches(5.78), Inches(5.7), Inches(0.65),
          "Règle tenue : aucun client ne reste bloqué, et le remboursement reste un droit, jamais une sanction.",
          taille=11, couleur=BLANC, gras=True, interligne=1.25)
    pied(diapo)
    notes(diapo, "Annexe : à ouvrir si l'on demande ce qui se passe quand le camion ne se remplit pas.")


def a05_technique(prs):
    diapo = prs.slides.add_slide(prs.slide_layouts[6])
    fond(diapo, NUIT)
    en_tete(diapo, "Annexe A5 · Socle technique", "Ce qui protège l'argent et la preuve", 17, sombre=True)

    blocs = [
        ("Séquestre", "Compte de cantonnement chez un établissement habilité. FBB n'orchestre que les "
                      "instructions : il ne détient jamais les fonds."),
        ("Signature", "Bons et preuves signés cryptographiquement, vérifiables hors ligne par la console "
                      "de chargement, sans appel serveur."),
        ("Journal d'audit", "Écriture en ajout seul, chaînée par empreintes, conservée dix ans. "
                            "Rien ne se supprime : une correction est un nouvel événement."),
        ("Idempotence", "Toute opération financière porte une clé unique : un rejeu technique ne produit "
                        "jamais de double mouvement."),
        ("Hors connexion", "Base locale chiffrée, file d'opérations rejouables, 72 heures d'autonomie, "
                           "aucune preuve perdue en cas de coupure."),
        ("Réversibilité", "Données et référentiels exportables. Les interfaces sont documentées : "
                          "PPC n'est pas captif."),
    ]
    largeur = (LARGEUR_UTILE - Inches(0.5)) / 3
    for index, (titre, corps) in enumerate(blocs):
        colonne = index % 3
        ligne = index // 3
        x = MARGE + colonne * (largeur + Inches(0.25))
        y = Inches(2.15) + ligne * Inches(2.15)
        rectangle(diapo, x, y, largeur, Inches(1.95), NUIT_MOYEN, arrondi=True)
        texte(diapo, x + Inches(0.26), y + Inches(0.2), largeur - Inches(0.5), Inches(0.3),
              titre, taille=12.5, couleur=BLANC, gras=True)
        texte(diapo, x + Inches(0.26), y + Inches(0.56), largeur - Inches(0.5), Inches(1.25),
              corps, taille=9.5, couleur=RGBColor(0xAB, 0xBD, 0xCA), interligne=1.25)
    pied(diapo, sombre=True)
    notes(diapo, "Annexe : à ouvrir si la DSI ou le juridique entre dans la salle. C'est la diapositive "
                 "qui rassure sur le séquestre et sur la réversibilité.")


# ---------------------------------------------------------------------------
def construire(chemin: Path) -> int:
    prs = Presentation()
    prs.slide_width = LARGEUR
    prs.slide_height = HAUTEUR

    for constructeur in (
        s01_titre, s02_probleme, s03_solution, s04_marche, s05_modele, s06_opportunite,
        s07_interfaces, s08_groupage, s09_marketing, s10_concurrence, s11_equipe, s12_conclusion,
        a01_route, a02_bareme, a03_preuve, a04_groupage, a05_technique,
    ):
        constructeur(prs)

    prs.core_properties.title = "APIX All In One — 12 diapositives (version réunion)"
    prs.core_properties.author = "FBB"
    prs.core_properties.subject = "Extension APIX : clients finaux, paiement séquestré et logistique ciment"
    prs.core_properties.comments = "Généré par outils/build_pptx_reunion.py — 12 diapositives + 5 annexes"

    chemin.parent.mkdir(parents=True, exist_ok=True)
    prs.save(chemin)
    return len(prs.slides._sldIdLst)


def main() -> int:
    nom = construire(SORTIE)
    print(f"[OK] {SORTIE.relative_to(RACINE)} — {nom} diapositives (12 + 5 annexes)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
