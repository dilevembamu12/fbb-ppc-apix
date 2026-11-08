#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
build_pptx_reunion.py — Version « réunion » : 12 diapositives + 7 annexes.

Contrainte : règle 10/20/30 (12 diapositives maximum en séquence, 20 minutes).
Registre : celui du dossier détaillé — titres déclaratifs, phrases courtes, une
idée par diapositive, les douleurs avant le produit.

    Diapositives 1 à 12 : séquence présentée
    Annexes A1 à A7     : ouvertes uniquement sur question

Les maquettes d'interface sont dessinées avec des formes natives : aucune capture
d'écran tierce, aucun nom de produit existant.

Usage :
    python outils/build_pptx_reunion.py
"""

from __future__ import annotations

import sys
from pathlib import Path

RACINE = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(Path(__file__).resolve().parent))

from pptx import Presentation                          # noqa: E402
from pptx.dml.color import RGBColor                     # noqa: E402
from pptx.enum.shapes import MSO_SHAPE                  # noqa: E402
from pptx.enum.text import PP_ALIGN                     # noqa: E402
from pptx.util import Inches, Pt                        # noqa: E402

from build_pptx import (                                # noqa: E402
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
          taille=31, couleur=couleur, gras=True, police=POLICE_TITRE, interligne=1.04)
    etiquette = f"{numero} / {TOTAL}" if numero <= TOTAL else f"Annexe A{numero - TOTAL}"
    texte(diapo, LARGEUR - MARGE - Inches(1.5), Inches(0.55), Inches(1.5), Inches(0.25),
          etiquette, taille=10, couleur=GRIS, alignement=PP_ALIGN.RIGHT)


def source(diapo, contenu: str):
    texte(diapo, MARGE, HAUTEUR - Inches(0.72), LARGEUR_UTILE, Inches(0.25), contenu,
          taille=9, couleur=GRIS, italique=True)


# ---------------------------------------------------------------------------
# Maquettes d'interface — formes natives uniquement
# ---------------------------------------------------------------------------
def cadre_telephone(diapo, x, y, w, h):
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

    indicateurs = [("142", "commandes"), ("87 %", "à l'heure"), ("3", "litiges")]
    xx = x + Inches(0.16)
    for valeur, libelle in indicateurs:
        rectangle(diapo, xx, y + Inches(0.42), Inches(0.78), Inches(0.5), SABLE, arrondi=True)
        texte(diapo, xx, y + Inches(0.47), Inches(0.78), Inches(0.2), valeur,
              taille=10, couleur=NUIT, gras=True, alignement=PP_ALIGN.CENTER)
        texte(diapo, xx, y + Inches(0.68), Inches(0.78), Inches(0.14), libelle,
              taille=5, couleur=GRIS, alignement=PP_ALIGN.CENTER)
        xx += Inches(0.86)

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
# Séquence principale
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
          taille=62, couleur=BLANC, gras=True, police=POLICE_TITRE, interligne=0.95)
    texte(diapo, MARGE, Inches(3.3), Inches(9.8), Inches(1.2),
          "Du paiement certifié au sac livré :\nune seule chaîne, une seule preuve.",
          taille=27, couleur=BLANC, interligne=1.2)
    rectangle(diapo, MARGE, Inches(4.8), Inches(1.5), Inches(0.045), ORANGE)
    texte(diapo, MARGE, Inches(5.1), Inches(10.6), Inches(0.8),
          ["Une plateforme ubiquitaire : smartphone, web, et hors connexion.",
           "Direction générale de PPC  ·  4 novembre 2026"],
          taille=14, couleur=RGBColor(0xC3, 0xD0, 0xDA), interligne=1.5)
    notes(diapo, "Ouvrir sans commenter le produit. Une seule phrase : « Nous venons parler de ce qui se passe "
                 "après le paiement, parce que c'est là que vos clients vous jugent. » Puis enchaîner.")


def s02_probleme(prs):
    diapo = prs.slides.add_slide(prs.slide_layouts[6])
    fond(diapo, SABLE)
    photo(diapo, "douleur_route", Inches(6.95), 0, LARGEUR - Inches(6.95), HAUTEUR)
    voile(diapo, Inches(6.95), 0, LARGEUR - Inches(6.95), HAUTEUR, NUIT, 0.22)

    texte(diapo, MARGE, Inches(0.85), Inches(5.7), Inches(0.28), "LE PROBLÈME",
          taille=11, couleur=ORANGE, gras=True)
    texte(diapo, MARGE, Inches(1.22), Inches(5.8), Inches(1.35),
          ["Le paiement est certifié.", "La marchandise, non."],
          taille=33, couleur=NUIT, gras=True, police=POLICE_TITRE, interligne=1.05)
    texte(diapo, MARGE, Inches(2.42), Inches(5.6), Inches(0.5),
          "Quatre questions auxquelles personne, aujourd'hui, ne peut répondre :",
          taille=11.5, couleur=GRIS, italique=True, interligne=1.25)

    questions = [
        ("01", "Où est mon camion, maintenant ?", "Le client appelle. Personne ne sait."),
        ("02", "Combien de sacs sont réellement arrivés ?", "95, 98, 100 ? Aucun constat contradictoire."),
        ("03", "Qui paie les sacs manquants ?", "Le transporteur accuse le client. Le client accuse l'usine."),
        ("04", "Pourquoi le ciment paraît-il cher au quartier ?", "Le prix ex-usine n'est pas le prix payé."),
    ]
    y = Inches(2.95)
    for numero, question, precision in questions:
        texte(diapo, MARGE, y, Inches(0.5), Inches(0.25), numero, taille=12, couleur=ORANGE, gras=True)
        texte(diapo, MARGE + Inches(0.5), y - Inches(0.03), Inches(5.0), Inches(0.28), question,
              taille=12, couleur=NUIT, gras=True)
        texte(diapo, MARGE + Inches(0.5), y + Inches(0.25), Inches(5.1), Inches(0.25), precision,
              taille=9.5, couleur=GRIS)
        y += Inches(0.86)

    texte(diapo, MARGE, Inches(6.16), Inches(5.7), Inches(0.3),
          "15 à 20 % des encaissements passent par le digital.",
          taille=13, couleur=ORANGE, gras=True)
    texte(diapo, MARGE, Inches(6.52), Inches(5.9), Inches(0.4),
          "Résultat : c'est votre marque qui répond des 80 % restants.",
          taille=13, couleur=NUIT, gras=True, italique=True, interligne=1.2)
    pied(diapo)
    notes(diapo, "Poser ces quatre questions à voix haute, puis laisser un silence. Personne dans la salle ne "
                 "peut y répondre avec une preuve. Ne pas accuser les transporteurs : ils sont partenaires tiers.")


def s03_fuites(prs):
    diapo = prs.slides.add_slide(prs.slide_layouts[6])
    fond(diapo, SABLE)
    en_tete(diapo, "Ce que cela coûte", "Trois fuites qui coûtent, sans figurer dans aucun rapport", 3)

    donnees = [
        ("01", "Le camion part à moitié vide",
         "Une course décidée dans l'urgence part à 60 %. Le transporteur partenaire perd de l'argent, "
         "se décourage, et va travailler ailleurs. Le coût de la tonne transportée monte mécaniquement."),
        ("02", "Le litige se règle sans preuve",
         "Un client reçoit moins de sacs qu'il n'en a payé. Le transporteur accuse le client, le client "
         "accuse l'usine. Sans constat contradictoire, l'usine tranche à l'aveugle — et paie en image."),
        ("03", "Le prix final échappe à PPC",
         "Le prix ex-usine est compétitif. Entre l'usine et le chantier, le prix au sac ne reflète ni le "
         "trajet ni la charge. Le client conclut que le ciment PPC est cher. Votre marque paie la différence."),
    ]
    largeur = (LARGEUR_UTILE - Inches(0.6)) / 3
    x = MARGE
    for numero, titre, corps in donnees:
        carte(diapo, x, Inches(2.35), largeur, Inches(3.4), numero, titre, corps)
        x += largeur + Inches(0.3)

    texte(diapo, MARGE, Inches(6.1), LARGEUR_UTILE, Inches(0.5),
          [{"runs": [("Aucune de ces trois fuites ne se voit dans un état financier. ",
                      {"gras": True, "couleur": NUIT, "taille": 13}),
                     ("Toutes les trois sortent de votre trésorerie, et toutes les trois atteignent votre image.",
                      {"couleur": GRIS, "taille": 13})]}], interligne=1.2)
    pied(diapo)
    notes(diapo, "Demander au directeur logistique un ordre de grandeur pour chacune. Sans chiffre, ce sont des "
                 "mécanismes reconnus — et c'est déjà suffisant pour obtenir un mandat de cadrage.")


def s04_marche(prs):
    diapo = prs.slides.add_slide(prs.slide_layouts[6])
    fond(diapo, SABLE)
    en_tete(diapo, "Le marché", "Il n'achète pas une application. Il achète une certitude.", 4)

    profils = [
        ("Dépôt / revendeur de quartier", "50 à 500 sacs, récurrent",
         "Réapprovisionnement rapide, prix stable, crédit. Sa contrainte : la trésorerie et la rotation du stock."),
        ("Entreprise / chantier", "200 à 3 000 sacs, par projet",
         "Facture conforme, traçabilité, respect du planning. Sa contrainte : la comptabilité et les délais."),
        ("Particulier / artisan", "5 à 50 sacs, ponctuel",
         "Prix total connu d'avance, livraison simple, preuve d'achat. Sa contrainte : le cash et le téléphone."),
    ]
    largeur = (LARGEUR_UTILE - Inches(0.6)) / 3
    x = MARGE
    for titre, volume, attente in profils:
        rectangle(diapo, x, Inches(2.12), largeur, Inches(1.72), BLANC, arrondi=True)
        texte(diapo, x + Inches(0.26), Inches(2.28), largeur - Inches(0.5), Inches(0.5),
              titre, taille=12.5, couleur=NUIT, gras=True, interligne=1.05)
        texte(diapo, x + Inches(0.26), Inches(2.78), largeur - Inches(0.5), Inches(0.24),
              volume, taille=9.5, couleur=ORANGE, gras=True)
        texte(diapo, x + Inches(0.26), Inches(3.08), largeur - Inches(0.5), Inches(0.68),
              attente, taille=10, couleur=GRIS, interligne=1.2)
        x += largeur + Inches(0.3)

    chiffres = [
        ("15\u00a0à\u00a020\u00a0%", "des encaissements passent aujourd'hui par le digital"),
        ("3", "banques seulement sont connectées à l'encaissement"),
        ("2\u00a0500\u00a0$", "plafond par transaction sur mobile money et carte"),
    ]
    x = MARGE
    for valeur, libelle in chiffres:
        rectangle(diapo, x, Inches(4.0), largeur, Inches(1.05), NUIT, arrondi=True)
        texte(diapo, x + Inches(0.24), Inches(4.12), largeur - Inches(0.48), Inches(0.4),
              valeur, taille=19, couleur=ORANGE_PALE, gras=True)
        texte(diapo, x + Inches(0.24), Inches(4.58), largeur - Inches(0.48), Inches(0.44),
              libelle, taille=9, couleur=RGBColor(0xB6, 0xC6, 0xD4), interligne=1.15)
        x += largeur + Inches(0.3)

    texte(diapo, MARGE, Inches(5.28), LARGEUR_UTILE, Inches(0.8),
          [{"runs": [("Ce n'est pas un marché à créer : ", {"gras": True, "couleur": NUIT, "taille": 13}),
                     ("c'est une couverture à compléter sur des clients qui existent déjà. Quatre cinquièmes des flux "
                      "restent hors de toute traçabilité automatique.", {"couleur": GRIS, "taille": 13})]}],
          interligne=1.22)

    source(diapo, "Chiffres communiqués par PPC en entretien — à confirmer sur un exercice complet avant diffusion.")
    notes(diapo, "Ces trois chiffres viennent de PPC, pas de nous : c'est ce qui les rend difficiles à contester. "
                 "Les laisser commenter. Ne jamais nommer les banques non connectées : c'est leur affaire interne, "
                 "et le document circule.")


def s05_chaine(prs):
    diapo = prs.slides.add_slide(prs.slide_layouts[6])
    fond(diapo, NUIT)
    en_tete(diapo, "La solution", "La chaîne de preuve, en six jalons", 5, sombre=True)
    texte(diapo, MARGE, Inches(1.85), Inches(11.4), Inches(0.4),
          "Chaque jalon produit une preuve, et chaque preuve conditionne le suivant — la cotation d'abord, le bon de commande ensuite.",
          taille=13.5, couleur=RGBColor(0xB6, 0xC6, 0xD4), italique=True)

    jalons = [
        ("J1", "Compte vérifié", "Identité et plafonds"),
        ("J2", "Cotation certifiée", "Prix ferme, référence de paiement"),
        ("J3", "Paiement encaissé", "Rattaché à la cotation"),
        ("J4", "Bon émis", "Nominatif, QR signé"),
        ("J5", "Chargement et route", "Pesée, scellé, positions"),
        ("J6", "Livraison prouvée", "Validation, litige tranché"),
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

    rectangle(diapo, MARGE, Inches(5.05), LARGEUR_UTILE, Inches(1.1), NUIT_MOYEN, arrondi=True)
    texte(diapo, MARGE + Inches(0.35), Inches(5.24), Inches(10.7), Inches(0.75),
          [{"runs": [("Ce que cela change : ", {"gras": True, "couleur": ORANGE_PALE, "taille": 14}),
                     ("le jour où un contentieux arrive sur 500 sacs, vous ne produisez pas une transaction — "
                      "vous produisez un dossier.", {"couleur": BLANC, "taille": 14})]}], interligne=1.25)
    pied(diapo, sombre=True)
    notes(diapo, "Ne pas détailler les six jalons un par un. Insister sur deux choses : la dépendance — sans la "
                 "preuve du jalon précédent, le suivant ne s'ouvre pas — et l'ordre — la cotation précède le "
                 "paiement, le bon de commande le suit. C'est le circuit de PPC, pas le nôtre.")


def s06_ubiquite(prs):
    diapo = prs.slides.add_slide(prs.slide_layouts[6])
    fond(diapo, SABLE)
    en_tete(diapo, "L'ubiquité", "Partout où le client se trouve", 6)
    texte(diapo, MARGE, Inches(1.42), Inches(11.0), Inches(0.32),
          "sur l'appareil qu'il possède déjà — et sans réseau quand il n'y en a pas.",
          taille=15, couleur=GRIS, italique=True)

    maquette_client(diapo, Inches(0.95), Inches(1.9), Inches(2.3), Inches(4.45))
    texte(diapo, Inches(0.95), Inches(6.4), Inches(2.3), Inches(0.22),
          "Client final — commander, payer, suivre", taille=9, couleur=GRIS,
          alignement=PP_ALIGN.CENTER)

    maquette_chauffeur(diapo, Inches(3.55), Inches(1.9), Inches(2.3), Inches(4.45))
    texte(diapo, Inches(3.55), Inches(6.4), Inches(2.3), Inches(0.22),
          "Chauffeur — livrer, prouver, sans réseau", taille=9, couleur=GRIS,
          alignement=PP_ALIGN.CENTER)

    panneau_backoffice(diapo, Inches(6.3), Inches(1.9), Inches(4.95), Inches(2.15))
    texte(diapo, Inches(6.3), Inches(4.12), Inches(4.95), Inches(0.22),
          "Back-office PPC — c'est vous qui homologuez", taille=9, couleur=GRIS)

    texte(diapo, Inches(6.3), Inches(4.34), Inches(4.95), Inches(0.26),
          "Une seule cotation, un seul bon", taille=13, couleur=NUIT, gras=True,
          police=POLICE_TITRE)
    texte(diapo, Inches(6.3), Inches(4.6), Inches(4.95), Inches(0.2),
          "quel que soit le canal qu'utilise le client", taille=9.5, couleur=GRIS, italique=True)

    canaux = (
        ("WhatsApp", "bon en QR"),
        ("Telegram", "bon en QR"),
        ("E-mail", "bon en PDF"),
        ("SMS", "code de retrait"),
        ("USSD", "code de retrait"),
    )
    for index, (nom_canal, forme_bon) in enumerate(canaux):
        xx = Inches(6.3) + index * Inches(0.99)
        rectangle(diapo, xx, Inches(4.9), Inches(0.9), Inches(0.72), BLANC, arrondi=True)
        rectangle(diapo, xx, Inches(4.9), Inches(0.9), Inches(0.05),
                  ORANGE if index < 3 else GRIS, arrondi=True)
        texte(diapo, xx, Inches(4.99), Inches(0.9), Inches(0.2), nom_canal, taille=7.5,
              couleur=NUIT, gras=True, alignement=PP_ALIGN.CENTER)
        texte(diapo, xx, Inches(5.21), Inches(0.9), Inches(0.34), forme_bon, taille=6.5,
              couleur=GRIS, alignement=PP_ALIGN.CENTER, interligne=1.0)

    constats = (
        "Application, WhatsApp, Telegram et e-mail : le bon reste un QR.",
        "SMS et USSD : il devient un code de retrait, saisi par l'agent de chargement.",
        "Le chauffeur, lui, travaille 72 heures sans réseau sans perdre une preuve.",
    )
    yy = Inches(5.8)
    for constat in constats:
        texte(diapo, Inches(6.3), yy, Inches(4.95), Inches(0.32), constat, taille=8.5,
              couleur=GRIS, interligne=1.15)
        yy += Inches(0.27)

    source(diapo, "Maquettes schématiques, non contractuelles.")
    notes(diapo, "Répondre d'avance à « nos clients n'ont pas de smartphone » : USSD et SMS portent la cotation, "
                 "le paiement et le bon, comme les autres canaux — c'est le même dossier, pas un canal au rabais. "
                 "Deux précisions à dire à voix haute : sur SMS et USSD le bon est un code de retrait, pas un QR ; "
                 "et aucun canal n'affiche de prix avant vérification de l'identité, pour qu'un concurrent ne "
                 "puisse pas sonder la grille. Le dépôt reste un point de contact humain.")


def s07_sequestre(prs):
    diapo = prs.slides.add_slide(prs.slide_layouts[6])
    fond(diapo, NUIT)
    en_tete(diapo, "Le circuit de l'argent", "Le client paie PPC. Le transporteur est payé sur preuve.", 7, sombre=True)
    texte(diapo, MARGE, Inches(1.88), Inches(11.4), Inches(0.4),
          "Sur la référence d'une cotation, encaissée avant le chargement. Le transport n'est réglé qu'après la livraison prouvée — et seulement s'il figure dans l'offre.",
          taille=13.5, couleur=RGBColor(0xB6, 0xC6, 0xD4), italique=True)

    etapes = [
        ("1", "Cotation, puis paiement", "Le client reçoit une cotation ferme, puis paie en la référençant. Mobile money, virement ou espèces via un agent agréé."),
        ("2", "APIX certifie et ventile", "La cotation encaissée devient le bon de commande. La part transport est isolée et provisionnée."),
        ("3", "Le ciment est livré", "Le client valide sur son téléphone : quantité, état, scellé. La preuve est signée."),
        ("4", "PPC règle le transporteur", "Sur preuve conforme, dans le délai que PPC arrêtera. Retenue partielle en cas d'écart constaté."),
    ]
    largeur = Inches(2.72)
    x = MARGE
    for index, (numero, titre, corps) in enumerate(etapes):
        rectangle(diapo, x, Inches(2.5), largeur, Inches(2.45), NUIT_MOYEN, arrondi=True)
        texte(diapo, x + Inches(0.26), Inches(2.68), Inches(0.6), Inches(0.4),
              numero, taille=25, couleur=ORANGE, gras=True)
        texte(diapo, x + Inches(0.26), Inches(3.2), largeur - Inches(0.52), Inches(0.6),
              titre, taille=13, couleur=BLANC, gras=True, interligne=1.1)
        texte(diapo, x + Inches(0.26), Inches(3.86), largeur - Inches(0.52), Inches(0.95),
              corps, taille=10, couleur=RGBColor(0xA8, 0xBA, 0xC8), interligne=1.25)
        if index < 3:
            fleche = forme(diapo, MSO_SHAPE.RIGHT_ARROW, x + largeur + Inches(0.04),
                           Inches(3.62), Inches(0.24), Inches(0.2))
            fleche.fill.solid()
            fleche.fill.fore_color.rgb = ORANGE
            fleche.line.fill.background()
        x += largeur + Inches(0.32)

    rectangle(diapo, MARGE, Inches(5.32), LARGEUR_UTILE, Inches(1.15), ORANGE, arrondi=True)
    texte(diapo, MARGE + Inches(0.35), Inches(5.5), Inches(10.6), Inches(0.85),
          ["« Le client paie PPC. PPC paie le transport — et seulement sur preuve. »",
           "Le client est protégé par un dossier qu'il peut produire, pas par un gel de ses fonds."],
          taille=13, couleur=BLANC, gras=True, interligne=1.35)
    texte(diapo, MARGE, Inches(6.6), LARGEUR_UTILE, Inches(0.3),
          "Trois banques seulement sont connectées au dispositif d'encaissement : le reste des flux est "
          "rapproché à la main — d'où l'intérêt d'un registre de preuve plutôt que d'un formulaire de plus.",
          taille=10, couleur=RGBColor(0x9F, 0xB2, 0xC2), italique=True)
    pied(diapo, sombre=True)
    notes(diapo, "Correction de fond : l'argent quitte le compte du client vers PPC avant même que le transporteur "
                 "voie la commande. Il n'y a donc pas de séquestre des fonds du client. Ce qu'APIX garantit, c'est "
                 "un règlement du transport déclenché par la preuve, et une retenue possible sur la course concernée. "
                 "FBB n'exécute aucun paiement : il instruit et certifie. Ne JAMAIS annoncer de délai de règlement : "
                 "nous ne connaissons pas le circuit actuel de PPC. C'est précisément la décision D2.")


def s08_preuve(prs):
    diapo = prs.slides.add_slide(prs.slide_layouts[6])
    fond(diapo, SABLE)
    photo(diapo, "livraison", Inches(7.05), 0, LARGEUR - Inches(7.05), HAUTEUR)
    voile(diapo, Inches(7.05), 0, LARGEUR - Inches(7.05), HAUTEUR, NUIT, 0.5)
    texte(diapo, Inches(7.4), Inches(5.35), Inches(5.2), Inches(1.0),
          "À la livraison, la preuve vaut mieux que la parole.",
          taille=19, couleur=BLANC, gras=True, interligne=1.2)

    texte(diapo, MARGE, Inches(0.95), Inches(5.8), Inches(0.28), "LA PREUVE DE LIVRAISON",
          taille=11, couleur=ORANGE, gras=True)
    texte(diapo, MARGE, Inches(1.3), Inches(5.9), Inches(0.9),
          "Quatre éléments, un seul dossier", taille=28, couleur=NUIT, gras=True,
          police=POLICE_TITRE, interligne=1.05)

    elements = [
        ("Photo géolocalisée",
         "Prise à la remise, horodatée, non modifiable, avec coordonnées et identité du chauffeur.", True),
        ("QR nominatif", "Remis au client, à usage unique, signé. Impossible à rejouer.", False),
        ("Pesée contradictoire", "Poids au chargement confronté au poids constaté, tolérance contractuelle.", False),
        ("Numéro de scellé", "Relevé au départ, vérifié à l'arrivée. Une rupture ouvre un litige automatique.", False),
    ]
    y = Inches(2.45)
    for titre, corps, vedette in elements:
        rectangle(diapo, MARGE, y, Inches(5.9), Inches(0.98),
                  ORANGE_PALE if vedette else BLANC, arrondi=True)
        if vedette:
            contour(diapo, MARGE, y, Inches(5.9), Inches(0.98), ORANGE, Pt(1.5), arrondi=True)
            texte(diapo, MARGE + Inches(4.5), y + Inches(0.08), Inches(1.25), Inches(0.18),
                  "LE CŒUR", taille=6.5, couleur=ORANGE, gras=True, alignement=PP_ALIGN.RIGHT)
        texte(diapo, MARGE + Inches(0.28), y + Inches(0.15), Inches(5.3), Inches(0.28),
              titre, taille=12.5, couleur=NUIT, gras=True)
        texte(diapo, MARGE + Inches(0.28), y + Inches(0.47), Inches(5.35), Inches(0.42),
              corps, taille=9.5, couleur=GRIS, interligne=1.2)
        y += Inches(1.06)

    pied(diapo)
    notes(diapo, "Le litige réel n'est pas le retard, c'est l'écart de poids. Insister sur la tolérance contractuelle, "
                 "qui doit être fixée avec PPC. La photo géolocalisée est ce qui tranche en pratique.")


def s09_bareme(prs):
    diapo = prs.slides.add_slide(prs.slide_layouts[6])
    fond(diapo, SABLE)
    en_tete(diapo, "Le prix", "Le transport cesse d'être un forfait : il devient un prix calculé", 9)

    colonnes = [
        ("Aujourd'hui", [
            "Un tarif forfaitaire, identique quel que soit le trajet.",
            "Ni la distance réelle ni le tonnage ne sont pris en compte.",
            "PPC ne maîtrise pas le prix final au quartier.",
        ], GRIS, BLANC, NUIT),
        ("Avec APIX", [
            "Un barème publié par PPC, versionné et daté.",
            "Un prix calculé à l'axe et au poids, jamais forfaitaire.",
            "Le total annoncé est exactement celui qui sera payé.",
        ], NUIT, NUIT_MOYEN, BLANC),
    ]
    largeur = Inches(2.6)
    x = MARGE
    for titre, points, couleur_entete, couleur_fond, couleur_texte in colonnes:
        rectangle(diapo, x, Inches(2.35), largeur, Inches(0.42), couleur_entete, arrondi=True)
        texte(diapo, x, Inches(2.44), largeur, Inches(0.25), titre, taille=12,
              couleur=BLANC, gras=True, alignement=PP_ALIGN.CENTER)
        rectangle(diapo, x, Inches(2.77), largeur, Inches(2.0), couleur_fond, arrondi=True)
        liste(diapo, x + Inches(0.22), Inches(2.97), largeur - Inches(0.44), Inches(1.7),
              points, taille=10.5, couleur=couleur_texte, puce=ORANGE, interligne=1.22, espace=12)
        x += largeur + Inches(0.18)

    panneau_calculateur(diapo, Inches(6.55), Inches(2.35), Inches(5.0), Inches(2.4))

    rectangle(diapo, MARGE, Inches(5.15), LARGEUR_UTILE, Inches(0.95), BLANC, arrondi=True)
    contour(diapo, MARGE, Inches(5.15), LARGEUR_UTILE, Inches(0.95), GRIS_CLAIR, Pt(1), arrondi=True)
    texte(diapo, MARGE + Inches(0.32), Inches(5.32), Inches(10.9), Inches(0.62),
          [{"runs": [("La conséquence commerciale : ", {"gras": True, "couleur": NUIT, "taille": 12.5}),
                     ("le barème est le vôtre. APIX l'applique, il ne le décide pas. Le prix affiché au quartier "
                      "redevient celui que PPC a choisi.", {"couleur": GRIS, "taille": 12.5})]}], interligne=1.25)
    pied(diapo)
    notes(diapo, "Point acquis auprès de PPC : le transport est facturé au forfait, sans calculateur intégrant le "
                 "trajet et le poids. La question n'est donc pas « négociez-vous ? » mais « sur quelle base ce "
                 "forfait est-il construit, et qui supporte l'écart quand le trajet réel diffère ? »")


def s10_groupage(prs):
    diapo = prs.slides.add_slide(prs.slide_layouts[6])
    fond(diapo, NUIT)
    en_tete(diapo, "La démonstration", "Cinq petits acheteurs, un seul camion", 10, sombre=True)
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


def s11_concurrence(prs):
    diapo = prs.slides.add_slide(prs.slide_layouts[6])
    fond(diapo, SABLE)
    en_tete(diapo, "La concurrence", "Deux approches, deux natures différentes", 11)

    donnees = [
        ["Critère", "Digiciment", "APIX All In One"],
        ["Nature", "Application de transactions", "Chaîne de preuve du paiement au sac livré"],
        ["Unité de référence", "La transaction", "La cotation certifiée et son bon"],
        ["Transporteurs", "Gestion locale, non documentée", "Homologation par PPC, datée et révocable"],
        ["Prix du transport", "Forfaitaire", "Calculé à l'axe et au poids, barème PPC"],
        ["Preuve de livraison", "Reçu simple", "QR, photo géolocalisée, pesée, scellé"],
        ["Sécurité du règlement", "Paiement direct, sans preuve", "Règlement sur preuve de livraison"],
        ["Hors connexion", "Connexion requise", "72 heures pour le chauffeur"],
        ["Litige", "Traité au cas par cas", "Dossier de preuve, décision motivée par PPC"],
    ]
    tableau(diapo, MARGE, Inches(2.25), LARGEUR_UTILE, donnees,
            [Inches(2.3), Inches(3.95), Inches(5.4)], hauteur_ligne=Inches(0.44), taille=11,
            colonne_forte=2)
    texte(diapo, MARGE, Inches(6.55), LARGEUR_UTILE, Inches(0.5),
          "Comparaison établie sur le périmètre fonctionnel annoncé. Toute correction de votre part est bienvenue : "
          "elle sera intégrée avant la démonstration.",
          taille=9.5, couleur=GRIS, italique=True)
    notes(diapo, "Ne jamais ironiser. Laisser le tableau parler, puis enchaîner : « ce n'est pas un match, c'est "
                 "une différence de nature ». Rester factuel : c'est ce qui convainc une direction générale.")


def s12_decisions(prs):
    diapo = prs.slides.add_slide(prs.slide_layouts[6])
    fond(diapo, SABLE)
    en_tete(diapo, "La suite", "PPC garde la main — cinq décisions, et nous commençons", 12)

    rectangle(diapo, MARGE, Inches(2.15), LARGEUR_UTILE, Inches(0.95), NUIT, arrondi=True)
    texte(diapo, MARGE + Inches(0.32), Inches(2.32), Inches(10.9), Inches(0.62),
          [{"runs": [("Vous décidez qui transporte, à quel prix, et comment se règle un litige. ",
                      {"gras": True, "couleur": BLANC, "taille": 12.5}),
                     ("APIX rend chacune de ces décisions exécutable, visible et opposable.",
                      {"couleur": RGBColor(0xB6, 0xC6, 0xD4), "taille": 12.5})]}], interligne=1.25)

    decisions = [
        ("D1", "Qui est le donneur d'ordre du transport ?", "Le client final ou PPC ?"),
        ("D2", "Comment PPC règle-t-il le transporteur aujourd'hui ?", "À établir : délai, moyen, litiges."),
        ("D3", "Sur quelle base construire le barème ?", "Le forfait actuel, ou un calcul à l'axe ?"),
        ("D4", "Quel circuit pour l'encaissement en espèces ?", "Part du cash et du mobile money."),
        ("D5", "Quel rôle pour le réseau de dépôts ?", "Points de retrait, ou vente directe."),
    ]
    largeur = (LARGEUR_UTILE - Inches(0.35)) / 2
    for index, (code, question, precision) in enumerate(decisions):
        colonne = 0 if index < 3 else 1
        ligne = index if index < 3 else index - 3
        x = MARGE + colonne * (largeur + Inches(0.35))
        y = Inches(3.3) + ligne * Inches(1.1)
        rectangle(diapo, x, y, largeur, Inches(0.98), BLANC, arrondi=True)
        texte(diapo, x + Inches(0.26), y + Inches(0.14), Inches(0.6), Inches(0.25),
              code, taille=11, couleur=ORANGE, gras=True)
        texte(diapo, x + Inches(0.85), y + Inches(0.12), largeur - Inches(1.1), Inches(0.45),
              question, taille=11.5, couleur=NUIT, gras=True, interligne=1.1)
        texte(diapo, x + Inches(0.85), y + Inches(0.62), largeur - Inches(1.1), Inches(0.28),
              precision, taille=9.5, couleur=GRIS)

    texte(diapo, MARGE, Inches(6.72), LARGEUR_UTILE, Inches(0.3),
          "Trois semaines d'ateliers suffisent à trancher ces cinq points. Elles conditionnent tout le reste.",
          taille=11, couleur=NUIT, gras=True, italique=True)
    pied(diapo)
    notes(diapo, "Ne pas sortir de la salle sans un référent métier nommé côté PPC et une date d'atelier de "
                 "cadrage. C'est le seul indicateur de succès de la réunion.")


# ---------------------------------------------------------------------------
# Annexes
# ---------------------------------------------------------------------------
def a01_modele(prs):
    diapo = prs.slides.add_slide(prs.slide_layouts[6])
    fond(diapo, SABLE)
    en_tete(diapo, "Annexe A1 · Modèle économique", "Quatre sources de valeur, trois façons de la facturer", 13)

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
    modeles = [("Frais par course", "Simple, aligné sur l'usage"),
               ("Abonnement PPC", "Prévisible, finance l'exploitation"),
               ("Mixte", "Base fixe + frais dégressifs")]
    x = MARGE + Inches(0.32)
    for titre, precision in modeles:
        texte(diapo, x, Inches(5.38), Inches(3.4), Inches(0.25), titre, taille=12, couleur=NUIT, gras=True)
        texte(diapo, x, Inches(5.65), Inches(3.4), Inches(0.25), precision, taille=10, couleur=GRIS)
        x += Inches(3.55)

    source(diapo, "Aucun prix n'est avancé : le modèle se cale sur les volumes et le barème réels de PPC.")
    notes(diapo, "Annexe : à ouvrir si la question du prix ou du retour sur investissement est posée.")


def a02_equipe(prs):
    diapo = prs.slides.add_slide(prs.slide_layouts[6])
    fond(diapo, SABLE)
    en_tete(diapo, "Annexe A2 · L'équipe", "Qui porte le projet", 14)

    roles = [
        ("Direction de projet", "Pilotage, arbitrages de périmètre, relation PPC."),
        ("Ingénierie plateforme", "Applications mobile et web, encaissement, règlement, sécurité, hors-ligne."),
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
    source(diapo, "Cette annexe doit être complétée avec les noms et références réelles avant toute présentation.")


def a03_route(prs):
    diapo = prs.slides.add_slide(prs.slide_layouts[6])
    fond(diapo, SABLE)
    en_tete(diapo, "Annexe A3 · Feuille de route",
            "Seize semaines jusqu'au pilote, deux facteurs hors de notre contrôle", 15)

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
           "Sans cette composante, les gros acheteurs financeraient les petits — et le mécanisme serait rejeté "
           "dès la première facture."],
          taille=10.5, couleur=GRIS, interligne=1.35)
    texte(diapo, Inches(7.4), Inches(4.95), Inches(5.1), Inches(0.8),
          "Le détail du calcul reste consultable par le client, avant et après paiement.",
          taille=10.5, couleur=NUIT, italique=True, interligne=1.3)

    rectangle(diapo, MARGE, Inches(5.6), Inches(6.2), Inches(0.95), NUIT, arrondi=True)
    texte(diapo, MARGE + Inches(0.28), Inches(5.78), Inches(5.7), Inches(0.65),
          "Règle tenue : aucun client ne reste bloqué, et le remboursement reste un droit, jamais une sanction.",
          taille=11, couleur=BLANC, gras=True, interligne=1.25)
    pied(diapo)


def a05_preuve_detail(prs):
    diapo = prs.slides.add_slide(prs.slide_layouts[6])
    fond(diapo, SABLE)
    en_tete(diapo, "Annexe A5 · Preuve et litige", "Ce qui se passe quand la livraison ne correspond pas", 17)

    texte(diapo, MARGE, Inches(2.1), Inches(6.4), Inches(0.3), "OUVERTURE DU LITIGE",
          taille=9, couleur=ORANGE, gras=True)
    liste(diapo, MARGE, Inches(2.45), Inches(6.3), Inches(2.6), [
        ("Écart de poids hors tolérance", " : déclaré automatiquement par le système."),
        ("Scellé rompu ou différent", " de celui du chargement : litige automatique."),
        ("Refus de validation", " par le client : déclaration immédiate, preuves conservées."),
        ("Délai de déclaration", " : 48 heures après livraison pour les autres motifs."),
    ], taille=11, couleur=GRIS, interligne=1.2, espace=12)

    rectangle(diapo, Inches(7.6), Inches(2.1), Inches(4.9), Inches(2.15), NUIT, arrondi=True)
    texte(diapo, Inches(7.88), Inches(2.3), Inches(4.3), Inches(0.3), "TRAITEMENT ET DÉCISION",
          taille=9, couleur=ORANGE, gras=True)
    liste(diapo, Inches(7.88), Inches(2.62), Inches(4.3), Inches(1.5), [
        "Gel de la part contestée, et d'elle seule",
        "Instruction sur dossier de preuve",
        "Décision motivée par PPC",
        "Retenue au prorata, libération du solde",
    ], taille=10.5, couleur=BLANC, interligne=1.2, espace=6)

    texte(diapo, MARGE, Inches(5.35), Inches(11.5), Inches(0.8),
          "Le litige le plus fréquent n'est pas le retard : c'est l'écart de poids. Sans pesée contradictoire "
          "et sans numéro de scellé, il se règle à la parole — et c'est l'usine qui tranche à l'aveugle.",
          taille=12, couleur=NUIT, interligne=1.3)
    pied(diapo)


def a06_technique(prs):
    diapo = prs.slides.add_slide(prs.slide_layouts[6])
    fond(diapo, NUIT)
    en_tete(diapo, "Annexe A6 · Socle technique", "Ce qui protège l'argent et la preuve", 18, sombre=True)

    blocs = [
        ("Règlement conditionnel", "Le transport est provisionné à l'encaissement, puis libéré au transporteur sur "
                                    "preuve de livraison. FBB n'exécute aucun paiement : il instruit et certifie."),
        ("Signature", "Bons et preuves signés cryptographiquement, vérifiables hors ligne par la console "
                      "de chargement, sans appel serveur."),
        ("Journal d'audit", "Écriture en ajout seul, chaînée par empreintes, conservée dix ans. Rien ne se "
                            "supprime : une correction est un nouvel événement."),
        ("Idempotence", "Toute opération financière porte une clé unique : un rejeu technique ne produit jamais "
                        "de double mouvement."),
        ("Hors connexion", "Base locale chiffrée, file d'opérations rejouables, 72 heures d'autonomie, "
                           "aucune preuve perdue en cas de coupure."),
        ("Réversibilité", "Données et référentiels exportables, interfaces documentées : PPC n'est pas captif."),
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
    notes(diapo, "Annexe : à ouvrir si la DSI ou le juridique entre dans la salle.")


# ---------------------------------------------------------------------------
def a07_canaux(prs):
    diapo = prs.slides.add_slide(prs.slide_layouts[6])
    fond(diapo, SABLE)
    en_tete(diapo, "Annexe A7 · Parité des canaux", "Cinq canaux, un seul dossier", 19)

    texte(diapo, MARGE, Inches(1.44), LARGEUR_UTILE, Inches(0.26),
          "La cotation, le paiement et le bon sont accessibles sur les cinq — seul le rendu du bon change.",
          taille=13, couleur=GRIS, italique=True)

    largeur = (LARGEUR_UTILE - Inches(0.8)) / 5
    colonnes = [
        ("WhatsApp", "carte et boutons", "QR",
         "Gabarits de messages approuvés obligatoires. Le bon arrive en QR dans la conversation."),
        ("Telegram", "bot et claviers", "QR",
         "Aucun compte marchand à ouvrir : c'est le canal le plus rapide à mettre en service."),
        ("E-mail", "pièce jointe", "PDF",
         "Aucune session à tenir : tout passe par un lien signé, valable aussi longtemps que la cotation."),
        ("SMS", "texte seul", "code de retrait",
         "160 caractères par message. Le bon devient un code que l'agent de chargement saisit."),
        ("USSD", "sans internet", "code de retrait",
         "Quatre écrans maximum, pas d'image : le bon devient un code de retrait."),
    ]

    for index, (nom_canal, role, forme_bon, contrainte) in enumerate(colonnes):
        x = MARGE + index * (largeur + Inches(0.2))
        texte(diapo, x, Inches(1.92), largeur, Inches(0.28), nom_canal, taille=13.5,
              couleur=NUIT, gras=True, police=POLICE_TITRE)
        texte(diapo, x, Inches(2.2), largeur, Inches(0.2), role, taille=9, couleur=GRIS, italique=True)

        ex, ey, ew = x + Inches(0.06), Inches(2.46), largeur - Inches(0.12)
        rectangle(diapo, ex, ey, ew, Inches(2.2), BLANC, arrondi=True)

        if index == 0:      # WhatsApp : bulles + bouton
            rectangle(diapo, ex + Inches(0.12), ey + Inches(0.16), Inches(1.32), Inches(0.3), GRIS_CLAIR, arrondi=True)
            rectangle(diapo, ex + Inches(0.55), ey + Inches(0.54), Inches(1.45), Inches(0.3), SABLE, arrondi=True)
            rectangle(diapo, ex + Inches(0.12), ey + Inches(0.92), ew - Inches(0.24), Inches(0.44),
                      GRIS_CLAIR, arrondi=True)
            rectangle(diapo, ex + Inches(0.12), ey + Inches(1.62), ew - Inches(0.24), Inches(0.34),
                      ORANGE, arrondi=True)
            texte(diapo, ex + Inches(0.12), ey + Inches(1.69), ew - Inches(0.24), Inches(0.2),
                  "Payer 3 145 $", taille=7, couleur=BLANC, gras=True, alignement=PP_ALIGN.CENTER)
        elif index == 1:    # Telegram : bulles + claviers
            rectangle(diapo, ex + Inches(0.12), ey + Inches(0.16), Inches(1.3), Inches(0.3), GRIS_CLAIR, arrondi=True)
            rectangle(diapo, ex + Inches(0.5), ey + Inches(0.54), Inches(1.5), Inches(0.3), SABLE, arrondi=True)
            for ligne in range(2):
                for colonne in range(2):
                    rectangle(diapo, ex + Inches(0.12 + colonne * 1.0), ey + Inches(1.02 + ligne * 0.38),
                              Inches(0.94), Inches(0.3), GRIS_CLAIR, arrondi=True)
            rectangle(diapo, ex + Inches(0.12), ey + Inches(1.8), ew - Inches(0.24), Inches(0.3),
                      NUIT, arrondi=True)
            texte(diapo, ex + Inches(0.12), ey + Inches(1.85), ew - Inches(0.24), Inches(0.2),
                  "Payer", taille=7, couleur=BLANC, gras=True, alignement=PP_ALIGN.CENTER)
        elif index == 2:    # E-mail : en-tête, corps, bouton et pièce jointe
            for rang, longueur in enumerate((0.9, 1.3, 0.6)):
                rectangle(diapo, ex + Inches(0.14), ey + Inches(0.16 + rang * 0.16),
                          Inches(longueur), Inches(0.06), GRIS_CLAIR)
            for rang in range(3):
                rectangle(diapo, ex + Inches(0.14), ey + Inches(0.72 + rang * 0.16),
                          ew - Inches(0.28), Inches(0.05), RGBColor(0xE6, 0xE9, 0xEB))
            rectangle(diapo, ex + Inches(0.14), ey + Inches(1.34), Inches(1.3), Inches(0.3),
                      ORANGE, arrondi=True)
            texte(diapo, ex + Inches(0.14), ey + Inches(1.39), Inches(1.3), Inches(0.2),
                  "Payer", taille=7, couleur=BLANC, gras=True, alignement=PP_ALIGN.CENTER)
            rectangle(diapo, ex + Inches(0.14), ey + Inches(1.78), Inches(1.5), Inches(0.28),
                      GRIS_CLAIR, arrondi=True)
            texte(diapo, ex + Inches(0.22), ey + Inches(1.83), Inches(1.4), Inches(0.18),
                  "COT-2026-000123.pdf", taille=6, couleur=GRIS)
        elif index == 3:    # SMS : échange de texte
            lignes = ("COT 200 GOMBE", "Cotation 3 145,00 $", "PAY", "Code 481902")
            for rang, ligne in enumerate(lignes):
                sortante = rang % 2 == 0
                rectangle(diapo, ex + (Inches(0.42) if sortante else Inches(0.14)),
                          ey + Inches(0.2 + rang * 0.46), Inches(1.45), Inches(0.32),
                          SABLE if sortante else GRIS_CLAIR, arrondi=True)
                texte(diapo, ex + (Inches(0.5) if sortante else Inches(0.22)),
                      ey + Inches(0.27 + rang * 0.46), Inches(1.3), Inches(0.18),
                      ligne, taille=6.5, couleur=NUIT if sortante else GRIS)
        else:               # USSD : menu numéroté
            rectangle(diapo, ex + Inches(0.14), ey + Inches(0.18), ew - Inches(0.28), Inches(1.46),
                      RGBColor(0xF2, 0xF4, 0xF6), arrondi=True)
            for rang, ligne in enumerate(("1. Commander", "2. Suivre", "3. Agent")):
                texte(diapo, ex + Inches(0.26), ey + Inches(0.3 + rang * 0.34), Inches(1.7), Inches(0.2),
                      ligne, taille=7, couleur=NUIT, gras=rang == 0)
            texte(diapo, ex + Inches(0.26), ey + Inches(1.32), Inches(1.7), Inches(0.18),
                  "Répondre : 1", taille=6.5, couleur=GRIS, italique=True)
            rectangle(diapo, ex + Inches(0.14), ey + Inches(1.78), ew - Inches(0.28), Inches(0.3),
                      GRIS_CLAIR, arrondi=True)
            texte(diapo, ex + Inches(0.26), ey + Inches(1.83), Inches(1.7), Inches(0.18),
                  "Paiement ouvert", taille=6.5, couleur=GRIS)

        couleur_puce = ORANGE_PALE if forme_bon in ("QR", "PDF") else GRIS_CLAIR
        couleur_texte = ORANGE if forme_bon in ("QR", "PDF") else NUIT
        rectangle(diapo, x, Inches(4.8), Inches(1.5), Inches(0.28), couleur_puce, arrondi=True)
        texte(diapo, x, Inches(4.86), Inches(1.5), Inches(0.18), f"Bon : {forme_bon}", taille=7.5,
              couleur=couleur_texte, gras=True, alignement=PP_ALIGN.CENTER)

        texte(diapo, x, Inches(5.18), largeur, Inches(1.0), contrainte, taille=8.5,
              couleur=GRIS, interligne=1.2)

    rectangle(diapo, MARGE, Inches(6.34), LARGEUR_UTILE, Inches(0.56), NUIT, arrondi=True)
    texte(diapo, MARGE + Inches(0.28), Inches(6.46), LARGEUR_UTILE - Inches(0.56), Inches(0.32),
          "Un client peut commencer sur USSD et terminer sur WhatsApp : même cotation, même bon, même preuve.",
          taille=11, couleur=BLANC, gras=True)
    pied(diapo)
    notes(diapo, "Annexe : à ouvrir si PPC demande « et ceux qui n'ont pas de smartphone ? ». Insister sur le "
                 "point qui rassure un directeur financier : ce n'est pas un canal au rabais, c'est le même "
                 "dossier avec un autre rendu. Deux limites à dire si on les interroge : sur SMS et USSD le bon "
                 "est un code, pas un QR ; et le paiement par USSD suppose un prestataire de collecte raccordé "
                 "derrière la passerelle.")


# ---------------------------------------------------------------------------
def construire(chemin: Path) -> int:
    prs = Presentation()
    prs.slide_width = LARGEUR
    prs.slide_height = HAUTEUR

    for constructeur in (
        s01_titre, s02_probleme, s03_fuites, s04_marche, s05_chaine, s06_ubiquite,
        s07_sequestre, s08_preuve, s09_bareme, s10_groupage, s11_concurrence, s12_decisions,
        a01_modele, a02_equipe, a03_route, a04_groupage, a05_preuve_detail, a06_technique,
        a07_canaux,
    ):
        constructeur(prs)

    prs.core_properties.title = "APIX All In One — 12 diapositives (version réunion)"
    prs.core_properties.author = "FBB"
    prs.core_properties.subject = "Extension APIX : clients finaux, paiement séquestré et logistique ciment"
    prs.core_properties.comments = "Généré par outils/build_pptx_reunion.py — 12 diapositives + 7 annexes"

    chemin.parent.mkdir(parents=True, exist_ok=True)
    prs.save(chemin)
    return len(prs.slides._sldIdLst)


def main() -> int:
    nom = construire(SORTIE)
    print(f"[OK] {SORTIE.relative_to(RACINE)} — {nom} diapositives (12 + 7 annexes)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
