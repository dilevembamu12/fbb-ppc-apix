#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
build_pptx.py — Génère la présentation « APIX All In One » destinée aux dirigeants de PPC.

Le fichier produit est un .pptx autonome (16:9), entièrement généré : aucune
retouche manuelle n'est nécessaire, et une correction de texte se fait ici puis
on relance le script.

Usage :
    python outils/build_pptx.py
    python outils/build_pptx.py --sortie "dist/pptx/ma-variante.pptx"

Prérequis : les images de assets/images, récupérées par outils/fetch_images.py.
Si une image manque, la diapositive se rabat sur un fond uni : la présentation
reste complète et lisible.
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

from PIL import Image
from pptx import Presentation
from pptx.dml.color import RGBColor
from pptx.enum.shapes import MSO_SHAPE
from pptx.enum.text import MSO_ANCHOR, PP_ALIGN
from pptx.oxml.ns import qn
from pptx.util import Emu, Inches, Pt
from pptx.oxml import parse_xml
from lxml import etree

RACINE = Path(__file__).resolve().parent.parent
IMAGES = RACINE / "assets" / "images"
SORTIE_DEFAUT = RACINE / "dist" / "pptx" / "APIX-All-In-One-Presentation-PPC.pptx"

try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
except (AttributeError, ValueError):
    pass

# ---------------------------------------------------------------------------
# Charte graphique
# ---------------------------------------------------------------------------
NUIT = RGBColor(0x0E, 0x24, 0x36)
NUIT_MOYEN = RGBColor(0x1B, 0x3A, 0x57)
ORANGE = RGBColor(0xE0, 0x6B, 0x2D)
ORANGE_PALE = RGBColor(0xF6, 0xDF, 0xD2)
SABLE = RGBColor(0xF4, 0xF1, 0xEA)
BLANC = RGBColor(0xFF, 0xFF, 0xFF)
GRIS = RGBColor(0x5A, 0x6B, 0x7A)
GRIS_CLAIR = RGBColor(0xDF, 0xE3, 0xE6)
VERT = RGBColor(0x2E, 0x7D, 0x5B)

POLICE = "Segoe UI"
POLICE_TITRE = "Segoe UI Semibold"

LARGEUR = Inches(13.333)
HAUTEUR = Inches(7.5)
MARGE = Inches(0.85)
LARGEUR_UTILE = LARGEUR - 2 * MARGE

SUJET_TOTAL = 22


# ---------------------------------------------------------------------------
# Utilitaires de bas niveau
# ---------------------------------------------------------------------------
def hexa(couleur: RGBColor) -> str:
    return str(couleur)


def _alpha(element_srgb, opacite: float) -> None:
    """Ajoute un canal alpha (0 à 1) à une couleur de remplissage."""
    if element_srgb is None:
        return
    valeur = etree.SubElement(element_srgb, qn("a:alpha"))
    valeur.set("val", str(int(max(0.0, min(1.0, opacite)) * 100000)))


def fond(diapo, couleur: RGBColor) -> None:
    remplissage = diapo.background.fill
    remplissage.solid()
    remplissage.fore_color.rgb = couleur


def forme(diapo, type_forme, x, y, w, h):
    objet = diapo.shapes.add_shape(type_forme, Emu(int(x)), Emu(int(y)), Emu(int(w)), Emu(int(h)))
    objet.shadow.inherit = False
    return objet


def rectangle(diapo, x, y, w, h, couleur, opacite: float | None = None, arrondi: bool = False):
    type_forme = MSO_SHAPE.ROUNDED_RECTANGLE if arrondi else MSO_SHAPE.RECTANGLE
    objet = forme(diapo, type_forme, x, y, w, h)
    objet.fill.solid()
    objet.fill.fore_color.rgb = couleur
    objet.line.fill.background()
    if opacite is not None:
        _alpha(objet._element.spPr.find(qn("a:solidFill")).find(qn("a:srgbClr")), opacite)
    if arrondi:
        try:
            objet.adjustments[0] = 0.06
        except (IndexError, ValueError):
            pass
    return objet


def contour(diapo, x, y, w, h, couleur, epaisseur=Pt(1.25), arrondi: bool = False):
    type_forme = MSO_SHAPE.ROUNDED_RECTANGLE if arrondi else MSO_SHAPE.RECTANGLE
    objet = forme(diapo, type_forme, x, y, w, h)
    objet.fill.background()
    objet.line.color.rgb = couleur
    objet.line.width = epaisseur
    if arrondi:
        try:
            objet.adjustments[0] = 0.06
        except (IndexError, ValueError):
            pass
    return objet


def photo(diapo, nom: str, x, y, w, h, opacite_voile: float | None = None):
    """Place une photo en mode « couverture » : elle remplit la zone sans déformation."""
    chemin = IMAGES / f"{nom}.jpg"
    if not chemin.exists():
        rectangle(diapo, x, y, w, h, NUIT_MOYEN)
        return None
    largeur_source, hauteur_source = Image.open(chemin).size
    ratio_cible = w / h
    ratio_source = largeur_source / hauteur_source
    image = diapo.shapes.add_picture(str(chemin), Emu(int(x)), Emu(int(y)), Emu(int(w)), Emu(int(h)))
    if ratio_source > ratio_cible:
        fraction = (1 - ratio_cible / ratio_source) / 2
        image.crop_left = fraction
        image.crop_right = fraction
    else:
        fraction = (1 - ratio_source / ratio_cible) / 2
        image.crop_top = fraction
        image.crop_bottom = fraction
    return image


def voile(diapo, x, y, w, h, couleur=NUIT, opacite=0.62):
    return rectangle(diapo, x, y, w, h, couleur, opacite=opacite)


def texte(diapo, x, y, w, h, contenu, taille=16, couleur=NUIT, gras=False, italique=False,
          police=POLICE, alignement=PP_ALIGN.LEFT, interligne=1.12, ancre=MSO_ANCHOR.TOP,
          espace_apres=0, marge=0):
    cadre = diapo.shapes.add_textbox(Emu(int(x)), Emu(int(y)), Emu(int(w)), Emu(int(h)))
    cadre.text_frame.word_wrap = True
    cadre.text_frame.vertical_anchor = ancre
    cadre.text_frame.margin_left = Emu(0)
    cadre.text_frame.margin_right = Emu(0)
    cadre.text_frame.margin_top = Emu(0)
    cadre.text_frame.margin_bottom = Emu(0)
    morceaux = contenu if isinstance(contenu, list) else [(contenu, {})]
    premier = True
    for morceau in morceaux:
        if isinstance(morceau, str):
            libelle, options = morceau, {}
        elif isinstance(morceau, dict):
            # Paragraphe décrit par ses options seules (souvent une liste de runs).
            libelle, options = "", morceau
        else:
            libelle, options = morceau
        paragraphe = cadre.text_frame.paragraphs[0] if premier else cadre.text_frame.add_paragraph()
        premier = False
        paragraphe.alignment = options.get("alignement", alignement)
        paragraphe.line_spacing = options.get("interligne", interligne)
        paragraphe.space_after = Pt(options.get("espace_apres", espace_apres))
        paragraphe.space_before = Pt(options.get("espace_avant", 0))
        morceaux_run = options.get("runs")
        if morceaux_run:
            for libelle_run, options_run in morceaux_run:
                run = paragraphe.add_run()
                run.text = libelle_run
                run.font.name = options_run.get("police", police)
                run.font.size = Pt(options_run.get("taille", options.get("taille", taille)))
                run.font.bold = options_run.get("gras", options.get("gras", gras))
                run.font.italic = options_run.get("italique", options.get("italique", italique))
                run.font.color.rgb = options_run.get("couleur", options.get("couleur", couleur))
        else:
            run = paragraphe.add_run()
            run.text = libelle
            run.font.name = options.get("police", police)
            run.font.size = Pt(options.get("taille", taille))
            run.font.bold = options.get("gras", gras)
            run.font.italic = options.get("italique", italique)
            run.font.color.rgb = options.get("couleur", couleur)
    return cadre


def liste(diapo, x, y, w, h, elements, taille=15, couleur=NUIT, puce=ORANGE,
          interligne=1.15, espace=10, symbole="—"):
    """Liste à puces : chaque élément est un texte, ou un couple (gras, suite)."""
    paragraphes = []
    for element in elements:
        if isinstance(element, tuple):
            gras, suite = element
            runs = [
                {"runs": [
                    (f"{symbole}  ", {"couleur": puce, "gras": True, "taille": taille}),
                    (gras, {"couleur": couleur, "gras": True, "taille": taille}),
                    (suite, {"couleur": couleur, "taille": taille}),
                ]},
            ]
            paragraphes.append(runs[0])
        else:
            paragraphes.append({
                "runs": [
                    (f"{symbole}  ", {"couleur": puce, "gras": True, "taille": taille}),
                    (element, {"couleur": couleur, "taille": taille}),
                ]
            })
    for paragraphe in paragraphes:
        paragraphe["espace_apres"] = espace
        paragraphe["interligne"] = interligne
    return texte(diapo, x, y, w, h, paragraphes, taille=taille, couleur=couleur)


def en_tete(diapo, surtitre: str, titre: str, numero: int, sombre: bool = False):
    """Bandeau de titre commun à toutes les diapositives de contenu."""
    couleur_texte = BLANC if sombre else NUIT
    if not sombre:
        rectangle(diapo, 0, 0, LARGEUR, Inches(0.11), ORANGE)
    texte(diapo, MARGE, Inches(0.55), LARGEUR_UTILE, Inches(0.28), surtitre.upper(),
          taille=11, couleur=ORANGE, gras=True)
    texte(diapo, MARGE, Inches(0.86), LARGEUR_UTILE, Inches(0.85), titre,
          taille=33, couleur=couleur_texte, gras=True, police=POLICE_TITRE, interligne=1.02)
    texte(diapo, LARGEUR - MARGE - Inches(1.2), Inches(0.55), Inches(1.2), Inches(0.25),
          f"{numero:02d} / {SUJET_TOTAL}", taille=10, couleur=GRIS, alignement=PP_ALIGN.RIGHT)


def pied(diapo, mention: str = "APIX All In One  ·  FBB  ·  Novembre 2026", sombre: bool = False):
    texte(diapo, MARGE, HAUTEUR - Inches(0.48), LARGEUR_UTILE, Inches(0.22), mention,
          taille=9, couleur=GRIS if not sombre else RGBColor(0x9A, 0xA8, 0xB4))


def notes(diapo, contenu: str):
    diapo.notes_slide.notes_text_frame.text = contenu


def carte(diapo, x, y, w, h, numero: str, titre: str, corps: str,
          couleur_fond=BLANC, couleur_numero=ORANGE, couleur_titre=NUIT, couleur_corps=GRIS,
          taille_titre=15, taille_corps=12.5):
    rectangle(diapo, x, y, w, h, couleur_fond, arrondi=True)
    texte(diapo, x + Inches(0.26), y + Inches(0.22), Inches(1.2), Inches(0.3),
          numero, taille=11, couleur=couleur_numero, gras=True)
    texte(diapo, x + Inches(0.26), y + Inches(0.52), w - Inches(0.52), Inches(0.62),
          titre, taille=taille_titre, couleur=couleur_titre, gras=True,
          police=POLICE_TITRE, interligne=1.05)
    texte(diapo, x + Inches(0.26), y + Inches(1.18), w - Inches(0.52), h - Inches(1.4),
          corps, taille=taille_corps, couleur=couleur_corps, interligne=1.18)


def tableau_neutre(tableau):
    """Supprime le style par défaut (bordures blanches, bandes) pour un rendu maîtrisé."""
    tbl = tableau._tbl
    tblPr = tbl.tblPr
    for element in tblPr.findall(qn("a:tableStyleId")):
        tblPr.remove(element)
    style = etree.SubElement(tblPr, qn("a:tableStyleId"))
    style.text = "{2D5ABB26-0587-4C30-8999-92F81FD0307C}"


def tableau(diapo, x, y, w, donnees, largeurs, hauteur_ligne=Inches(0.42),
            taille=12, entete_fond=NUIT, entete_couleur=BLANC,
            fond_paire=BLANC, fond_impaire=SABLE, couleur_texte=NUIT,
            colonne_forte=0):
    lignes, colonnes = len(donnees), len(donnees[0])
    objet = diapo.shapes.add_table(lignes, colonnes, Emu(int(x)), Emu(int(y)),
                                   Emu(int(w)), Emu(int(hauteur_ligne * lignes))).table
    tableau_neutre(objet)
    objet.first_row = False
    objet.horz_banding = False
    for index, largeur in enumerate(largeurs):
        objet.columns[index].width = Emu(int(largeur))
    for index_ligne, ligne in enumerate(donnees):
        objet.rows[index_ligne].height = Emu(int(hauteur_ligne))
        for index_colonne, valeur in enumerate(ligne):
            cellule = objet.cell(index_ligne, index_colonne)
            cellule.margin_left = Inches(0.14)
            cellule.margin_right = Inches(0.1)
            cellule.margin_top = Inches(0.03)
            cellule.margin_bottom = Inches(0.03)
            cellule.vertical_anchor = MSO_ANCHOR.MIDDLE
            cellule.fill.solid()
            if index_ligne == 0:
                cellule.fill.fore_color.rgb = entete_fond
            else:
                cellule.fill.fore_color.rgb = fond_paire if index_ligne % 2 == 0 else fond_impaire
            cadre = cellule.text_frame
            cadre.word_wrap = True
            paragraphe = cadre.paragraphs[0]
            paragraphe.line_spacing = 1.05
            run = paragraphe.add_run()
            run.text = valeur
            run.font.name = POLICE
            run.font.size = Pt(taille)
            if index_ligne == 0:
                run.font.bold = True
                run.font.color.rgb = entete_couleur
            else:
                run.font.bold = index_colonne == colonne_forte
                run.font.color.rgb = couleur_texte
    return objet


# ---------------------------------------------------------------------------
# Diapositives
# ---------------------------------------------------------------------------
def d01_couverture(prs):
    diapo = prs.slides.add_slide(prs.slide_layouts[6])
    fond(diapo, NUIT)
    photo(diapo, "couverture", 0, 0, LARGEUR, HAUTEUR)
    voile(diapo, 0, 0, LARGEUR, HAUTEUR, NUIT, 0.72)
    rectangle(diapo, 0, 0, Inches(0.16), HAUTEUR, ORANGE)

    texte(diapo, MARGE, Inches(1.55), Inches(9), Inches(0.3), "F B B   ·   A P I X",
          taille=12, couleur=ORANGE_PALE, gras=True)
    texte(diapo, MARGE, Inches(2.0), Inches(11.5), Inches(1.5), "APIX All In One",
          taille=66, couleur=BLANC, gras=True, police=POLICE_TITRE, interligne=0.95)
    texte(diapo, MARGE, Inches(3.35), Inches(10.4), Inches(1.1),
          "Du paiement certifié au sac livré : une seule chaîne, une seule preuve.",
          taille=24, couleur=RGBColor(0xE8, 0xEE, 0xF4), interligne=1.2)
    rectangle(diapo, MARGE, Inches(4.55), Inches(1.5), Inches(0.045), ORANGE)
    texte(diapo, MARGE, Inches(4.85), Inches(10.8), Inches(0.9),
          ["Une plateforme ubiquitaire : smartphone, web, et hors connexion.",
           "Dossier de présentation aux dirigeants de PPC — 4 novembre 2026."],
          taille=14, couleur=RGBColor(0xC3, 0xD0, 0xDA), interligne=1.5)
    notes(diapo, "Ouvrir sans commenter le produit. Une seule phrase : « Nous venons parler de ce qui se passe "
                 "après le paiement, parce que c'est là que vos clients vous jugent. » Puis enchaîner sur la diapositive 2.")


def d02_probleme(prs):
    diapo = prs.slides.add_slide(prs.slide_layouts[6])
    fond(diapo, SABLE)
    photo(diapo, "douleur_route", Inches(6.9), 0, LARGEUR - Inches(6.9), HAUTEUR)
    voile(diapo, Inches(6.9), 0, Inches(1.2), HAUTEUR, SABLE, 0.0)

    texte(diapo, MARGE, Inches(0.9), Inches(5.6), Inches(0.3), "LE CONSTAT",
          taille=11, couleur=ORANGE, gras=True)
    texte(diapo, MARGE, Inches(1.3), Inches(5.6), Inches(1.9),
          ["Le paiement est", "certifié.", "La marchandise, non."],
          taille=40, couleur=NUIT, gras=True, police=POLICE_TITRE, interligne=1.0)
    texte(diapo, MARGE, Inches(3.6), Inches(5.4), Inches(2.4),
          "APIX prouve aujourd'hui qu'une transaction est authentique. Mais entre le paiement et le sac posé "
          "sur le chantier, il n'existe aucune preuve partagée : ni par votre client, ni par le transporteur, "
          "ni par vous.",
          taille=15, couleur=GRIS, interligne=1.35)
    rectangle(diapo, MARGE, Inches(5.9), Inches(5.4), Inches(0.9), BLANC, arrondi=True)
    texte(diapo, MARGE + Inches(0.3), Inches(6.05), Inches(4.9), Inches(0.6),
          [{"runs": [("Résultat : ", {"gras": True, "couleur": NUIT, "taille": 13}),
                     ("c'est votre marque qui répond de ce qu'elle ne contrôle pas.",
                      {"couleur": GRIS, "taille": 13})]}], interligne=1.2)
    pied(diapo)
    notes(diapo, "Ne pas accuser les transporteurs : ils sont partenaires. Le problème est l'absence de preuve "
                 "partagée, pas la mauvaise foi de quiconque.")


def d03_questions(prs):
    diapo = prs.slides.add_slide(prs.slide_layouts[6])
    fond(diapo, NUIT)
    en_tete(diapo, "Le constat", "Quatre questions auxquelles personne ne peut répondre aujourd'hui", 3, sombre=True)

    questions = [
        ("01", "Où est mon camion, maintenant ?", "Le client appelle. Personne ne sait."),
        ("02", "Combien de sacs sont réellement arrivés ?", "95, 98, 100 ? Aucun constat contradictoire."),
        ("03", "Qui paie les sacs manquants ?", "Le transporteur accuse le client. Le client accuse l'usine."),
        ("04", "Pourquoi le ciment paraît-il cher au quartier ?", "Le prix ex-usine n'est pas le prix payé."),
    ]
    y = Inches(2.35)
    for numero, question, precision in questions:
        rectangle(diapo, MARGE, y, LARGEUR_UTILE, Inches(1.02), NUIT_MOYEN, arrondi=True)
        texte(diapo, MARGE + Inches(0.32), y + Inches(0.3), Inches(0.8), Inches(0.4),
              numero, taille=20, couleur=ORANGE, gras=True)
        texte(diapo, MARGE + Inches(1.25), y + Inches(0.22), Inches(6.2), Inches(0.5),
              question, taille=17, couleur=BLANC, gras=True)
        texte(diapo, MARGE + Inches(7.6), y + Inches(0.3), Inches(3.4), Inches(0.5),
              precision, taille=12, couleur=RGBColor(0x9F, 0xB2, 0xC2), italique=True)
        y += Inches(1.16)
    pied(diapo, sombre=True)
    notes(diapo, "Poser ces questions à voix haute et laisser un silence. Elles décrivent le quotidien de "
                 "leurs équipes commerciales et logistiques ; personne dans la salle ne peut y répondre avec une preuve.")


def d04_douleurs_ppc(prs):
    diapo = prs.slides.add_slide(prs.slide_layouts[6])
    fond(diapo, SABLE)
    en_tete(diapo, "Les douleurs de PPC", "Trois fuites qui coûtent, sans figurer dans aucun rapport", 4)

    donnees = [
        ("01", "Le camion part à moitié vide",
         "Une course décidée dans l'urgence part à 60 %. Le transporteur partenaire perd de l'argent, "
         "se décourage, et va travailler ailleurs. Le coût de la tonne transportée monte mécaniquement."),
        ("02", "Le litige se règle sans preuve",
         "Un client reçoit moins de sacs qu'il n'en a payé. Le transporteur accuse le client, le client "
         "accuse l'usine. Sans constat contradictoire, l'usine tranche à l'aveugle — et paie en image."),
        ("03", "Le prix final échappe à PPC",
         "Le prix ex-usine est compétitif. Entre l'usine et le chantier, des frais s'ajoutent sans "
         "justification. Le client conclut que le ciment PPC est cher. Votre marque paie la différence."),
    ]
    largeur = (LARGEUR_UTILE - Inches(0.6)) / 3
    x = MARGE
    for numero, titre, corps in donnees:
        carte(diapo, x, Inches(2.35), largeur, Inches(3.35), numero, titre, corps)
        x += largeur + Inches(0.3)
    texte(diapo, MARGE, Inches(6.05), LARGEUR_UTILE, Inches(0.5),
          [{"runs": [("Aucune de ces trois fuites ne se voit dans un état financier. ",
                      {"gras": True, "couleur": NUIT, "taille": 13}),
                     ("Toutes les trois sortent de votre trésorerie, et toutes les trois atteignent votre image.",
                      {"couleur": GRIS, "taille": 13})]}], interligne=1.2)
    pied(diapo)
    notes(diapo, "Si possible, demander avant la réunion un ordre de grandeur au directeur logistique. "
                 "Sans chiffre, ces trois fuites restent des mécanismes reconnus — et c'est déjà suffisant pour convaincre.")


def d05_section_marche(prs):
    diapo = prs.slides.add_slide(prs.slide_layouts[6])
    fond(diapo, NUIT)
    photo(diapo, "usine", 0, 0, LARGEUR, HAUTEUR)
    voile(diapo, 0, 0, LARGEUR, HAUTEUR, NUIT, 0.75)
    texte(diapo, MARGE, Inches(2.5), Inches(2), Inches(1.4), "I", taille=110, couleur=ORANGE, gras=True,
          police=POLICE_TITRE, interligne=0.9)
    texte(diapo, MARGE, Inches(4.0), Inches(9.5), Inches(1.1), "Le marché tel qu'il est",
          taille=44, couleur=BLANC, gras=True, police=POLICE_TITRE)
    texte(diapo, MARGE, Inches(5.15), Inches(8.6), Inches(0.9),
          "Trois acteurs, trois réalités que l'application actuelle ne relie pas.",
          taille=17, couleur=RGBColor(0xC3, 0xD0, 0xDA), interligne=1.3)
    pied(diapo, sombre=True)


def d06_client_final(prs):
    diapo = prs.slides.add_slide(prs.slide_layouts[6])
    fond(diapo, SABLE)
    photo(diapo, "douleur_manutention", 0, 0, Inches(5.6), HAUTEUR)
    voile(diapo, 0, 0, Inches(5.6), HAUTEUR, NUIT, 0.25)
    texte(diapo, Inches(0.55), HAUTEUR - Inches(1.1), Inches(4.6), Inches(0.8),
          "Le sac se porte encore à dos d'homme. Le logiciel doit en tenir compte.",
          taille=11.5, couleur=BLANC, italique=True, interligne=1.25)

    texte(diapo, Inches(6.35), Inches(0.95), Inches(6.2), Inches(0.3), "LE CLIENT FINAL",
          taille=11, couleur=ORANGE, gras=True)
    texte(diapo, Inches(6.35), Inches(1.3), Inches(6.2), Inches(1.0),
          "Il n'achète pas une application.\nIl achète une certitude.",
          taille=26, couleur=NUIT, gras=True, police=POLICE_TITRE, interligne=1.1)
    liste(diapo, Inches(6.35), Inches(2.7), Inches(6.3), Inches(4.0), [
        ("Prix opaque : ", "« je ne sais jamais combien je vais payer au total »."),
        ("Transport aléatoire : ", "le prix se négocie au bord du camion."),
        ("Aucune preuve : ", "rien à montrer si la livraison est contestée."),
        ("Marchandise incomplète : ", "payé 100 sacs, reçu 95, sans recours."),
        ("Aucune visibilité : ", "le camion est parti, il n'y a plus d'information."),
        ("Achat minimum imposé : ", "20 sacs ne justifient pas un camion."),
    ], taille=14, couleur=GRIS)
    pied(diapo)
    notes(diapo, "Insister sur le dernier point : c'est celui qui justifie le groupage, et c'est l'argument "
                 "le plus difficile à contourner pour un concurrent.")


def d07_transporteur(prs):
    diapo = prs.slides.add_slide(prs.slide_layouts[6])
    fond(diapo, SABLE)
    en_tete(diapo, "Le transporteur partenaire", "Il n'est pas PPC. Et c'est précisément le problème à traiter", 7)

    photo(diapo, "douleur_attente", Inches(8.3), Inches(1.95), Inches(4.2), Inches(2.36))
    voile(diapo, Inches(8.3), Inches(1.95), Inches(4.2), Inches(2.36), NUIT, 0.15)
    texte(diapo, Inches(8.3), Inches(4.42), Inches(4.2), Inches(0.8),
          "Un camion immobile ne rapporte rien. Un partenaire qui perd de l'argent "
          "finit par travailler pour quelqu'un d'autre.",
          taille=11, couleur=GRIS, italique=True, interligne=1.3)

    liste(diapo, MARGE, Inches(2.0), Inches(7.0), Inches(4.0), [
        ("Camion à moitié vide", " : la course part quand même, la perte est pour lui."),
        ("Attente au chargement", " : des heures immobilisées, jamais refacturées."),
        ("Paiement tardif", " : il avance le carburant et attend."),
        ("Frais de route non couverts", " : péages et tracasseries sortis de sa poche."),
        ("Litiges tranchés à charge", " : il n'a aucun moyen de prouver sa livraison."),
    ], taille=14, couleur=GRIS, interligne=1.2, espace=14)
    rectangle(diapo, MARGE, Inches(6.05), Inches(7.0), Inches(0.75), NUIT, arrondi=True)
    texte(diapo, MARGE + Inches(0.3), Inches(6.19), Inches(6.4), Inches(0.5),
          "Un transporteur qui gagne sa vie chez vous est un transporteur qui ne part pas.",
          taille=13, couleur=BLANC, gras=True)
    pied(diapo)
    notes(diapo, "Rappeler explicitement que PPC ne possède pas ces camions : le produit doit donc "
                 "rendre le partenariat rentable, sinon il sera contourné.")


def d08_cout_inaction(prs):
    diapo = prs.slides.add_slide(prs.slide_layouts[6])
    fond(diapo, SABLE)
    en_tete(diapo, "Le coût de l'inaction", "Ce que la situation actuelle prélève, silencieusement", 8)

    donnees = [
        ["Ce qui se passe aujourd'hui", "Où cela coûte", "Ce que cela produit"],
        ["Courses décidées sans consolidation", "Coût à la tonne transportée", "Marge logistique érodée"],
        ["Litiges sans constat contradictoire", "Temps commercial et direction", "Décisions prises à l'aveugle"],
        ["Sorties de stock non nominatives", "Stock et distribution parallèle", "Volume livré inexpliqué"],
        ["Prix du transport négocié", "Positionnement tarifaire", "Marque perçue comme chère"],
        ["Paiement après livraison", "Trésorerie et recouvrement", "Encours et impayés"],
    ]
    tableau(diapo, MARGE, Inches(2.15), LARGEUR_UTILE, donnees,
            [Inches(4.9), Inches(3.6), Inches(3.15)], hauteur_ligne=Inches(0.62), taille=12.5)
    texte(diapo, MARGE, Inches(6.15), LARGEUR_UTILE, Inches(0.7),
          "Aucune ligne de ce tableau n'est un problème informatique. Toutes se mesurent, et toutes "
          "se corrigent dès lors que la même preuve est partagée par le client, le transporteur et vous.",
          taille=13, couleur=GRIS, interligne=1.3)
    pied(diapo)
    notes(diapo, "Proposer de remplir la colonne du milieu avec leurs propres chiffres pendant l'atelier de "
                 "cadrage : c'est la meilleure façon d'obtenir un mandat.")


def d09_section_reponse(prs):
    diapo = prs.slides.add_slide(prs.slide_layouts[6])
    fond(diapo, NUIT)
    photo(diapo, "ville", 0, 0, LARGEUR, HAUTEUR)
    voile(diapo, 0, 0, LARGEUR, HAUTEUR, NUIT, 0.78)
    texte(diapo, MARGE, Inches(2.5), Inches(2), Inches(1.4), "II", taille=110, couleur=ORANGE, gras=True,
          police=POLICE_TITRE, interligne=0.9)
    texte(diapo, MARGE, Inches(4.0), Inches(10.5), Inches(1.1), "La réponse : APIX All In One",
          taille=42, couleur=BLANC, gras=True, police=POLICE_TITRE)
    texte(diapo, MARGE, Inches(5.15), Inches(8.8), Inches(0.9),
          "Une plateforme, trois applications, une seule chaîne de preuve.",
          taille=17, couleur=RGBColor(0xC3, 0xD0, 0xDA))
    pied(diapo, sombre=True)


def d10_all_in_one(prs):
    diapo = prs.slides.add_slide(prs.slide_layouts[6])
    fond(diapo, SABLE)
    en_tete(diapo, "L'architecture d'ensemble", "Un socle, trois applications, six métiers reliés", 10)

    # Bloc central
    rectangle(diapo, Inches(4.55), Inches(2.35), Inches(4.2), Inches(2.8), NUIT, arrondi=True)
    texte(diapo, Inches(4.55), Inches(3.35), Inches(4.2), Inches(0.9),
          ["APIX All In One", "socle de certification"],
          taille=16, couleur=BLANC, gras=True, alignement=PP_ALIGN.CENTER, interligne=1.2,
          ancre=MSO_ANCHOR.MIDDLE)
    texte(diapo, Inches(4.55), Inches(5.35), Inches(4.2), Inches(0.4),
          "commande · paiement · transport · preuve · litige · facture",
          taille=10, couleur=GRIS, alignement=PP_ALIGN.CENTER, italique=True, interligne=1.2)

    # Applications
    applications = [
        ("Application client", "Android · iOS · Web", Inches(0.85), Inches(1.95)),
        ("Application chauffeur", "Android · iOS · hors ligne", Inches(0.85), Inches(4.15)),
        ("Back-office PPC", "Web · homologation · litiges", Inches(9.35), Inches(1.95)),
    ]
    for titre, precision, x, y in applications:
        rectangle(diapo, x, y, Inches(3.05), Inches(0.95), BLANC, arrondi=True)
        contour(diapo, x, y, Inches(3.05), Inches(0.95), GRIS_CLAIR, Pt(1), arrondi=True)
        texte(diapo, x + Inches(0.22), y + Inches(0.16), Inches(2.6), Inches(0.35),
              titre, taille=13, couleur=NUIT, gras=True)
        texte(diapo, x + Inches(0.22), y + Inches(0.52), Inches(2.6), Inches(0.3),
              precision, taille=10.5, couleur=GRIS)

    # Portail transporteur
    rectangle(diapo, Inches(9.35), Inches(4.15), Inches(3.05), Inches(0.95), BLANC, arrondi=True)
    contour(diapo, Inches(9.35), Inches(4.15), Inches(3.05), Inches(0.95), GRIS_CLAIR, Pt(1), arrondi=True)
    texte(diapo, Inches(9.57), Inches(4.31), Inches(2.6), Inches(0.35), "Portail transporteur",
          taille=13, couleur=NUIT, gras=True)
    texte(diapo, Inches(9.57), Inches(4.67), Inches(2.6), Inches(0.3), "Web · courses · relevés",
          taille=10.5, couleur=GRIS)

    # Liens
    for x_depart, x_arrivee, y in (
        (Inches(3.9), Inches(4.55), Inches(2.42)),
        (Inches(3.9), Inches(4.55), Inches(4.62)),
        (Inches(8.75), Inches(9.35), Inches(2.42)),
        (Inches(8.75), Inches(9.35), Inches(4.62)),
    ):
        fleche = forme(diapo, MSO_SHAPE.LEFT_RIGHT_ARROW, x_depart, y + Inches(0.28),
                       x_arrivee - x_depart, Inches(0.14))
        fleche.fill.solid()
        fleche.fill.fore_color.rgb = ORANGE
        fleche.line.fill.background()

    texte(diapo, MARGE, Inches(6.15), LARGEUR_UTILE, Inches(0.8),
          "Aucune application ne travaille seule : le bon de commande est la même donnée dans les quatre "
          "interfaces. C'est ce qui rend la réconciliation impossible à perdre.",
          taille=13, couleur=GRIS, interligne=1.3)
    pied(diapo)
    notes(diapo, "Message clé : ce n'est pas trois produits, c'est un produit vu de quatre endroits. "
                 "C'est ce que des applications séparées ne peuvent pas offrir.")


def d11_chaine_preuve(prs):
    diapo = prs.slides.add_slide(prs.slide_layouts[6])
    fond(diapo, NUIT)
    en_tete(diapo, "Le cœur du produit", "La chaîne de preuve, en six jalons", 11, sombre=True)
    texte(diapo, MARGE, Inches(1.85), Inches(11.4), Inches(0.4),
          "Chaque jalon produit une preuve, et chaque preuve conditionne le suivant.",
          taille=14, couleur=RGBColor(0xB6, 0xC6, 0xD4), italique=True)

    jalons = [
        ("J1", "Compte vérifié", "Identité et plafonds"),
        ("J2", "Bon certifié", "Numéro unique, QR signé"),
        ("J3", "Paiement encaissé", "Encaissé par PPC, certifié"),
        ("J4", "Chargement", "Pesée, scellé, photo"),
        ("J5", "Transport suivi", "Positions et incidents"),
        ("J6", "Livraison prouvée", "Validation, litige tranché"),
    ]
    largeur = Inches(2.02)
    pas = Inches(1.96)
    x = MARGE
    for index, (code, titre, preuve) in enumerate(jalons):
        chevron = forme(diapo, MSO_SHAPE.CHEVRON, x, Inches(2.5), largeur, Inches(0.78))
        chevron.fill.solid()
        chevron.fill.fore_color.rgb = ORANGE if index % 2 == 0 else RGBColor(0xC9, 0x57, 0x1F)
        chevron.line.fill.background()
        cadre = chevron.text_frame
        cadre.word_wrap = False
        paragraphe = cadre.paragraphs[0]
        paragraphe.alignment = PP_ALIGN.CENTER
        run = paragraphe.add_run()
        run.text = code
        run.font.name = POLICE
        run.font.size = Pt(14)
        run.font.bold = True
        run.font.color.rgb = BLANC

        texte(diapo, x + Inches(0.16), Inches(3.45), largeur - Inches(0.2), Inches(0.5),
              titre, taille=11.5, couleur=BLANC, gras=True, interligne=1.1)
        texte(diapo, x + Inches(0.16), Inches(4.0), largeur - Inches(0.2), Inches(0.7),
              preuve, taille=9.5, couleur=RGBColor(0x9F, 0xB2, 0xC2), interligne=1.25)
        x += pas

    rectangle(diapo, MARGE, Inches(5.15), LARGEUR_UTILE, Inches(1.15), NUIT_MOYEN, arrondi=True)
    texte(diapo, MARGE + Inches(0.35), Inches(5.35), Inches(10.6), Inches(0.8),
          [{"runs": [("Ce que cela change : ", {"gras": True, "couleur": ORANGE_PALE, "taille": 14}),
                     ("le jour où un contentieux arrive sur 500 sacs, vous ne produisez pas une transaction — "
                      "vous produisez un dossier.", {"couleur": BLANC, "taille": 14})]}], interligne=1.25)
    pied(diapo, sombre=True)
    notes(diapo, "Ne pas détailler les six jalons un par un. Insister sur la logique : sans la preuve "
                 "du jalon précédent, le suivant ne s'ouvre pas.")


def d12_ubiquite(prs):
    diapo = prs.slides.add_slide(prs.slide_layouts[6])
    fond(diapo, SABLE)
    en_tete(diapo, "L'ubiquité", "Partout où le client se trouve, sur l'appareil qu'il possède déjà", 12)

    photo(diapo, "mobile", Inches(7.55), Inches(1.9), Inches(4.95), Inches(2.78))
    voile(diapo, Inches(7.55), Inches(1.9), Inches(4.95), Inches(2.78), NUIT, 0.12)
    texte(diapo, Inches(7.55), Inches(4.8), Inches(4.95), Inches(0.9),
          "Le paiement mobile n'est pas une option à créer : il est déjà dans la rue.",
          taille=11.5, couleur=GRIS, italique=True, interligne=1.3)

    blocs = [
        ("Smartphone", "Android 8 et plus, 2 Go de mémoire. Interface lisible en plein soleil."),
        ("Web", "Même compte, même données, depuis un cybercafé ou un bureau."),
        ("Hors connexion", "Le chauffeur travaille 72 heures sans réseau, sans perdre une preuve."),
        ("SMS et USSD", "Pour le client sans smartphone : notification, état de livraison, rappel."),
    ]
    y = Inches(2.05)
    for titre, corps in blocs:
        rectangle(diapo, MARGE, y, Inches(6.3), Inches(1.02), BLANC, arrondi=True)
        texte(diapo, MARGE + Inches(0.28), y + Inches(0.16), Inches(5.8), Inches(0.3),
              titre, taille=13, couleur=NUIT, gras=True)
        texte(diapo, MARGE + Inches(0.28), y + Inches(0.5), Inches(5.8), Inches(0.42),
              corps, taille=11, couleur=GRIS, interligne=1.2)
        y += Inches(1.14)

    rectangle(diapo, Inches(7.55), Inches(5.85), Inches(4.95), Inches(0.85), NUIT, arrondi=True)
    texte(diapo, Inches(7.85), Inches(6.02), Inches(4.4), Inches(0.55),
          "Une seule application, quatre façons d'y accéder.", taille=13, couleur=BLANC, gras=True)
    pied(diapo)
    notes(diapo, "Répondre d'avance à l'objection « nos clients n'ont pas de smartphone » : "
                 "USSD et SMS sont prévus, et le dépôt reste un point de contact humain.")


def d13_sequestre(prs):
    diapo = prs.slides.add_slide(prs.slide_layouts[6])
    fond(diapo, NUIT)
    en_tete(diapo, "Le circuit de l'argent", "Le client paie PPC. Le transporteur est payé sur preuve.", 13, sombre=True)
    texte(diapo, MARGE, Inches(1.9), Inches(11.4), Inches(0.4),
          "Encaissé avant le chargement. Le transport n'est réglé qu'après la livraison prouvée — et seulement s'il figure dans l'offre.",
          taille=14, couleur=RGBColor(0xB6, 0xC6, 0xD4), italique=True)

    etapes = [
        ("1", "Le client paie PPC", "Ciment, et transport si l'offre l'inclut. Paiement par mobile money, virement ou espèces via un agent agréé."),
        ("2", "APIX certifie et ventile", "La part transport est isolée dans la commande et provisionnée. Offre sans transport : aucune provision."),
        ("3", "Le ciment est livré", "Le client valide sur son téléphone : quantité, état, scellé. La preuve est signée."),
        ("4", "PPC règle le transporteur", "Sur preuve conforme, dans le délai que PPC arrêtera. Retenue partielle en cas d'écart constaté."),
    ]
    largeur = Inches(2.72)
    x = MARGE
    for index, (numero, titre, corps) in enumerate(etapes):
        rectangle(diapo, x, Inches(2.55), largeur, Inches(2.5), NUIT_MOYEN, arrondi=True)
        texte(diapo, x + Inches(0.26), Inches(2.75), Inches(0.6), Inches(0.4),
              numero, taille=26, couleur=ORANGE, gras=True)
        texte(diapo, x + Inches(0.26), Inches(3.28), largeur - Inches(0.52), Inches(0.6),
              titre, taille=13.5, couleur=BLANC, gras=True, interligne=1.1)
        texte(diapo, x + Inches(0.26), Inches(3.95), largeur - Inches(0.52), Inches(0.95),
              corps, taille=10.5, couleur=RGBColor(0xA8, 0xBA, 0xC8), interligne=1.25)
        if index < 3:
            fleche = forme(diapo, MSO_SHAPE.RIGHT_ARROW, x + largeur + Inches(0.04),
                           Inches(3.68), Inches(0.24), Inches(0.2))
            fleche.fill.solid()
            fleche.fill.fore_color.rgb = ORANGE
            fleche.line.fill.background()
        x += largeur + Inches(0.32)

    rectangle(diapo, MARGE, Inches(5.42), LARGEUR_UTILE, Inches(1.15), ORANGE, arrondi=True)
    texte(diapo, MARGE + Inches(0.35), Inches(5.62), Inches(10.5), Inches(0.8),
          ["« Le client paie PPC. PPC paie le transport — et seulement sur preuve. »",
           "Le client est protégé par un dossier de preuve, pas par un gel de ses fonds."],
          taille=13, couleur=BLANC, gras=True, interligne=1.3)
    pied(diapo, sombre=True)
    notes(diapo, "Correction de fond : l'argent quitte le compte du client vers PPC avant même que le transporteur "
                 "voie la commande. Il n'y a pas de séquestre des fonds du client. Ce qu'APIX garantit, c'est un "
                 "règlement du transport déclenché par la preuve, et une retenue possible sur la course concernée. "
                 "Ne jamais annoncer de délai de règlement : le circuit actuel de PPC n'est pas connu.")


def d14_preuve_livraison(prs):
    diapo = prs.slides.add_slide(prs.slide_layouts[6])
    fond(diapo, SABLE)
    photo(diapo, "livraison", Inches(7.0), 0, LARGEUR - Inches(7.0), HAUTEUR)
    voile(diapo, Inches(7.0), 0, LARGEUR - Inches(7.0), HAUTEUR, NUIT, 0.55)
    texte(diapo, Inches(7.35), Inches(5.5), Inches(5.3), Inches(1.1),
          "À la livraison, la preuve vaut mieux que la parole.",
          taille=17, couleur=BLANC, gras=True, interligne=1.2)

    texte(diapo, MARGE, Inches(0.95), Inches(5.7), Inches(0.3), "LA PREUVE DE LIVRAISON",
          taille=11, couleur=ORANGE, gras=True)
    texte(diapo, MARGE, Inches(1.3), Inches(5.7), Inches(1.0),
          "Quatre éléments, un seul dossier", taille=27, couleur=NUIT, gras=True,
          police=POLICE_TITRE, interligne=1.05)

    elements = [
        ("QR nominatif", "Remis au client, à usage unique, signé. Impossible à rejouer."),
        ("Photo géolocalisée", "Prise à la remise, horodatée, non modifiable."),
        ("Pesée contradictoire", "Poids au chargement confronté au poids constaté."),
        ("Numéro de scellé", "Relevé au départ, vérifié à l'arrivée. Une rupture ouvre un litige."),
    ]
    y = Inches(2.55)
    for titre, corps in elements:
        rectangle(diapo, MARGE, y, Inches(5.7), Inches(0.92), BLANC, arrondi=True)
        texte(diapo, MARGE + Inches(0.26), y + Inches(0.14), Inches(5.2), Inches(0.3),
              titre, taille=12.5, couleur=NUIT, gras=True)
        texte(diapo, MARGE + Inches(0.26), y + Inches(0.46), Inches(5.2), Inches(0.4),
              corps, taille=10.5, couleur=GRIS, interligne=1.2)
        y += Inches(1.02)
    pied(diapo)
    notes(diapo, "Le litige réel n'est pas le retard, c'est l'écart de poids. Insister sur la tolérance "
                 "contractuelle, qui doit être fixée avec PPC.")


def d15_bareme(prs):
    diapo = prs.slides.add_slide(prs.slide_layouts[6])
    fond(diapo, SABLE)
    en_tete(diapo, "Le prix", "Le transport cesse d'être un forfait : il devient un prix calculé", 15)

    colonnes = [
        ("Aujourd'hui", [
            "Un tarif forfaitaire, identique quel que soit le trajet.",
            "Ni la distance réelle ni le tonnage ne sont pris en compte.",
            "Le client connaît le total, mais le prix au sac reste approximatif.",
            "PPC ne maîtrise pas le prix final au quartier.",
        ], GRIS, BLANC),
        ("Avec APIX", [
            "Un barème publié par PPC, versionné et daté.",
            "Un prix calculé à l'axe et au poids, jamais forfaitaire.",
            "Le total annoncé est exactement celui qui sera payé.",
            "Aucune saisie libre, ni par le client ni par le transporteur.",
        ], NUIT, NUIT_MOYEN),
    ]
    largeur = (LARGEUR_UTILE - Inches(0.4)) / 2
    x = MARGE
    for titre, points, couleur_titre, couleur_fond in colonnes:
        rectangle(diapo, x, Inches(2.2), largeur, Inches(0.6), couleur_titre, arrondi=True)
        texte(diapo, x, Inches(2.36), largeur, Inches(0.35), titre, taille=14,
              couleur=BLANC if couleur_titre == NUIT else BLANC, gras=True, alignement=PP_ALIGN.CENTER)
        rectangle(diapo, x, Inches(2.86), largeur, Inches(2.5), couleur_fond, arrondi=True)
        liste(diapo, x + Inches(0.32), Inches(3.08), largeur - Inches(0.64), Inches(2.1),
              points, taille=12.5,
              couleur=BLANC if couleur_fond == NUIT_MOYEN else NUIT,
              puce=ORANGE if couleur_fond == NUIT_MOYEN else ORANGE, interligne=1.2, espace=12)
        x += largeur + Inches(0.4)

    rectangle(diapo, MARGE, Inches(5.65), LARGEUR_UTILE, Inches(0.95), BLANC, arrondi=True)
    contour(diapo, MARGE, Inches(5.65), LARGEUR_UTILE, Inches(0.95), GRIS_CLAIR, Pt(1), arrondi=True)
    texte(diapo, MARGE + Inches(0.32), Inches(5.82), Inches(10.9), Inches(0.6),
          [{"runs": [("La conséquence commerciale : ", {"gras": True, "couleur": NUIT, "taille": 13}),
                     ("le prix affiché au quartier redevient celui que PPC a décidé. "
                      "C'est un acte de contrôle de la marque, pas un réglage informatique.",
                      {"couleur": GRIS, "taille": 13})]}], interligne=1.25)
    pied(diapo)
    notes(diapo, "Point acquis auprès de PPC : le transport est aujourd'hui facturé au forfait, sans calculateur "
                 "intégrant le trajet et le poids. La question n'est donc pas « négociez-vous ? » mais "
                 "« sur quelle base ce forfait est-il construit, et qui supporte l'écart quand le trajet réel diffère ? »")


def d16_groupage(prs):
    diapo = prs.slides.add_slide(prs.slide_layouts[6])
    fond(diapo, NUIT)
    en_tete(diapo, "Le groupage", "Cinq petits acheteurs, un seul camion", 16, sombre=True)
    texte(diapo, MARGE, Inches(1.85), Inches(11.4), Inches(0.4),
          "Simulation sur un axe de 210 km, cinq clients, cinq points de livraison.",
          taille=13, couleur=RGBColor(0xB6, 0xC6, 0xD4), italique=True)

    clients = [
        ("Dépôt Ngaliema", "60 sacs", "3,0 t"),
        ("Chantier Limete", "200 sacs", "10,0 t"),
        ("Dépôt Matete", "120 sacs", "6,0 t"),
        ("Artisan Kintambo", "20 sacs", "1,0 t"),
        ("Dépôt Masina", "120 sacs", "6,0 t"),
    ]
    y = Inches(2.55)
    for nom, sacs, poids in clients:
        rectangle(diapo, MARGE, y, Inches(4.55), Inches(0.58), NUIT_MOYEN, arrondi=True)
        texte(diapo, MARGE + Inches(0.26), y + Inches(0.13), Inches(2.7), Inches(0.3),
              nom, taille=11.5, couleur=BLANC, gras=True)
        texte(diapo, MARGE + Inches(3.15), y + Inches(0.15), Inches(1.2), Inches(0.3),
              f"{sacs} · {poids}", taille=10.5, couleur=RGBColor(0xA8, 0xBA, 0xC8))
        y += Inches(0.68)

    fleche = forme(diapo, MSO_SHAPE.RIGHT_ARROW, Inches(5.62), Inches(4.05), Inches(0.85), Inches(0.42))
    fleche.fill.solid()
    fleche.fill.fore_color.rgb = ORANGE
    fleche.line.fill.background()

    rectangle(diapo, Inches(6.75), Inches(2.55), Inches(5.75), Inches(3.0), ORANGE, arrondi=True)
    texte(diapo, Inches(7.15), Inches(2.85), Inches(5.0), Inches(0.45), "1 CAMION · 26 TONNES",
          taille=17, couleur=BLANC, gras=True)
    lignes = [
        ("Transport total", "900 $ répartis au prorata du poids × distance"),
        ("Prix par sac", "entre 1,67 $ et 1,79 $ selon la zone"),
        ("Taux de remplissage", "86,7 % — le lot se déclenche"),
        ("Sans groupage", "5 commandes, 5 camions, 5 tournées"),
    ]
    y = Inches(3.48)
    for libelle, valeur in lignes:
        texte(diapo, Inches(7.15), y, Inches(1.75), Inches(0.3), libelle, taille=10,
              couleur=RGBColor(0xFF, 0xE7, 0xD9))
        texte(diapo, Inches(8.95), y, Inches(3.4), Inches(0.3), valeur, taille=11,
              couleur=BLANC, gras=True)
        y += Inches(0.44)

    texte(diapo, MARGE, Inches(6.15), Inches(11.4), Inches(0.8),
          [{"runs": [("Et si le lot ne se remplit pas ? ", {"gras": True, "couleur": ORANGE_PALE, "taille": 13}),
                     ("Trois issues sont prévues et écrites : la poursuite avec un engin plus petit, le report "
                      "accepté par le client jusqu'au remplissage du lot, ou le remboursement à sa demande. "
                      "Aucun client ne reste bloqué.",
                      {"couleur": RGBColor(0xC3, 0xD0, 0xDA), "taille": 13})]}], interligne=1.3)
    pied(diapo, sombre=True)
    notes(diapo, "C'est la diapositive qui répond à la concurrence sur les petits volumes. Les chiffres "
                 "viennent du simulateur joint au dossier : ils sont calculables devant eux.")


def d17_comparaison(prs):
    diapo = prs.slides.add_slide(prs.slide_layouts[6])
    fond(diapo, SABLE)
    en_tete(diapo, "Comparaison", "Deux approches, deux natures différentes", 17)

    donnees = [
        ["Critère", "Digiciment", "APIX All In One"],
        ["Nature", "Application de transactions", "Chaîne de preuve du paiement au sac livré"],
        ["Unité de référence", "La transaction", "Le bon de commande certifié"],
        ["Transporteurs", "Gestion locale, non documentée", "Homologation administrative par PPC, datée et révocable"],
        ["Prix du transport", "Négocié", "Barème PPC appliqué automatiquement"],
        ["Preuve de livraison", "Reçu simple", "QR nominatif, photo géolocalisée, pesée, scellé"],
        ["Sécurité du règlement", "Paiement direct au bénéficiaire", "Règlement sur preuve de livraison"],
        ["Litige", "Traité au cas par cas", "Dossier de preuve, décision motivée, retenue partielle"],
        ["Connexion requise", "Permanente", "Hors ligne 72 heures pour le chauffeur"],
    ]
    tableau(diapo, MARGE, Inches(2.1), LARGEUR_UTILE, donnees,
            [Inches(2.35), Inches(4.05), Inches(5.25)], hauteur_ligne=Inches(0.47), taille=11.5,
            colonne_forte=2)
    texte(diapo, MARGE, Inches(6.45), LARGEUR_UTILE, Inches(0.4),
          "Comparaison établie sur le périmètre fonctionnel annoncé. Toute correction de votre part est bienvenue.",
          taille=9.5, couleur=GRIS, italique=True)
    notes(diapo, "Ne pas commenter cette diapositive avec ironie. La laisser parler, puis enchaîner sur "
                 "« ce n'est pas un match, c'est une différence de nature ». Rester factuel : c'est plus dévastateur.")


def d18_controle(prs):
    diapo = prs.slides.add_slide(prs.slide_layouts[6])
    fond(diapo, SABLE)
    en_tete(diapo, "La souveraineté", "PPC garde la main sur les trois décisions qui comptent", 18)

    leviers = [
        ("Qui transporte", "L'homologation est prononcée par vos équipes : pièces contrôlées, assurance vérifiée, "
                           "validité datée, révocation immédiate possible."),
        ("À quel prix", "Le barème est le vôtre. Versionné, daté, publié par PPC. APIX l'applique, il ne le décide pas."),
        ("Comment se règle un litige", "La décision appartient à vos administrateurs : sens de la décision, "
                                       "montant retenu, montant libéré, motif."),
    ]
    y = Inches(2.3)
    for index, (titre, corps) in enumerate(leviers, start=1):
        rectangle(diapo, MARGE, y, LARGEUR_UTILE, Inches(1.15), BLANC, arrondi=True)
        rectangle(diapo, MARGE, y, Inches(0.08), Inches(1.15), ORANGE)
        texte(diapo, MARGE + Inches(0.4), y + Inches(0.2), Inches(3.4), Inches(0.35),
              f"{index:02d}   {titre}", taille=15, couleur=NUIT, gras=True)
        texte(diapo, MARGE + Inches(4.1), y + Inches(0.2), Inches(7.2), Inches(0.8),
              corps, taille=12, couleur=GRIS, interligne=1.25)
        y += Inches(1.3)

    texte(diapo, MARGE, Inches(6.2), LARGEUR_UTILE, Inches(0.6),
          "APIX ne prend aucune décision commerciale à votre place. Il rend chacune de vos décisions "
          "exécutable, visible et opposable.",
          taille=13, couleur=NUIT, gras=True, interligne=1.25)
    pied(diapo)
    notes(diapo, "C'est la diapositive qui lève la crainte de perdre le contrôle. Les dirigeants doivent "
                 "sortir en se disant que le pouvoir reste chez eux.")


def d19_indicateurs(prs):
    diapo = prs.slides.add_slide(prs.slide_layouts[6])
    fond(diapo, SABLE)
    en_tete(diapo, "La valeur", "Huit douleurs, huit indicateurs que vous pourrez suivre", 19)

    donnees = [
        ["Douleur actuelle", "Ce que vous pourrez mesurer"],
        ["Camions mal remplis", "Taux de remplissage moyen, par axe et par engin"],
        ["Litiges non arbitrables", "Taux de litige et délai moyen de résolution"],
        ["Retards sans explication", "Taux de service logistique : complet et à l'heure"],
        ["Transporteurs non fiables", "Score de fiabilité, par transporteur"],
        ["Prix final incontrôlé", "Coût moyen du transport au sac, par axe"],
        ["Impayés et encours", "Part des commandes payées avant chargement"],
        ["Stock détourné", "Taux de bons non présentés au chargement"],
        ["Demande invisible", "Volume commandé par axe, produit et période"],
    ]
    tableau(diapo, MARGE, Inches(2.15), Inches(8.3), donnees,
            [Inches(3.5), Inches(4.8)], hauteur_ligne=Inches(0.47), taille=11.5)
    rectangle(diapo, Inches(9.5), Inches(2.15), Inches(3.0), Inches(3.93), NUIT, arrondi=True)
    texte(diapo, Inches(9.8), Inches(2.45), Inches(2.45), Inches(0.8),
          ["Pour la première fois,", "la logistique devient", "un chiffre."],
          taille=16, couleur=BLANC, gras=True, interligne=1.2)
    texte(diapo, Inches(9.8), Inches(4.05), Inches(2.45), Inches(1.8),
          "Ces indicateurs n'existent nulle part aujourd'hui. Ils se calculent seuls, "
          "dès que la chaîne de preuve est en place.",
          taille=11, couleur=RGBColor(0xA8, 0xBA, 0xC8), interligne=1.3)
    pied(diapo)
    notes(diapo, "Proposer de choisir ensemble trois indicateurs prioritaires : cela transforme la "
                 "présentation en engagement mesurable.")


def d20_calendrier(prs):
    diapo = prs.slides.add_slide(prs.slide_layouts[6])
    fond(diapo, NUIT)
    en_tete(diapo, "Le calendrier", "Un axe pilote opérationnel en seize semaines après cadrage", 20, sombre=True)

    etapes = [
        ("S1 – S3", "Cadrage", "Décisions prises, barème initial, référentiel transporteurs"),
        ("S4 – S6", "Conception", "Parcours, maquettes, architecture validée"),
        ("S7 – S18", "Développement", "Chaîne de preuve complète et back-office"),
        ("S19 – S22", "Pilote", "Un axe, un produit, cinq à dix transporteurs"),
        ("Ensuite", "Généralisation", "Ouverture au deuxième axe, puis groupage"),
    ]
    ligne_y = Inches(3.05)
    rectangle(diapo, MARGE, ligne_y, LARGEUR_UTILE, Inches(0.03), RGBColor(0x3A, 0x56, 0x70))
    pas = LARGEUR_UTILE / len(etapes)
    x = MARGE
    for index, (periode, titre, corps) in enumerate(etapes):
        cercle = forme(diapo, MSO_SHAPE.OVAL, x + pas / 2 - Inches(0.11), ligne_y - Inches(0.08),
                       Inches(0.22), Inches(0.22))
        cercle.fill.solid()
        cercle.fill.fore_color.rgb = ORANGE
        cercle.line.fill.background()
        texte(diapo, x, Inches(2.35), pas - Inches(0.15), Inches(0.3), periode,
              taille=11, couleur=ORANGE, gras=True, alignement=PP_ALIGN.CENTER)
        texte(diapo, x, Inches(3.4), pas - Inches(0.15), Inches(0.35), titre,
              taille=13.5, couleur=BLANC, gras=True, alignement=PP_ALIGN.CENTER)
        texte(diapo, x, Inches(3.9), pas - Inches(0.15), Inches(1.0), corps,
              taille=9.5, couleur=RGBColor(0x9F, 0xB2, 0xC2), alignement=PP_ALIGN.CENTER, interligne=1.25)
        x += pas

    rectangle(diapo, MARGE, Inches(5.35), LARGEUR_UTILE, Inches(1.1), NUIT_MOYEN, arrondi=True)
    texte(diapo, MARGE + Inches(0.35), Inches(5.55), Inches(10.6), Inches(0.75),
          [{"runs": [("Recommandation : ", {"gras": True, "couleur": ORANGE_PALE, "taille": 13}),
                     ("un axe, un produit, des transporteurs déjà connus de PPC. Un pilote propre sur un axe "
                      "vaut mieux qu'un lancement national qui produit des litiges non traités.",
                      {"couleur": BLANC, "taille": 13})]}], interligne=1.3)
    pied(diapo, sombre=True)
    notes(diapo, "Les deux facteurs qui ne dépendent pas de FBB : la vitesse d'homologation des transporteurs "
                 "et la publication du barème. Le dire avant qu'on ne nous l'oppose.")


def d21_decisions(prs):
    diapo = prs.slides.add_slide(prs.slide_layouts[6])
    fond(diapo, SABLE)
    en_tete(diapo, "La suite", "Cinq décisions à prendre, et nous commençons", 21)

    decisions = [
        ("D1", "Qui est le donneur d'ordre du transport ?", "Le client final ou PPC ? Cela fixe la responsabilité et le circuit de paiement."),
        ("D2", "Comment PPC règle-t-il le transporteur aujourd'hui ?", "Délai réel, moyen de paiement, litiges."),
        ("D3", "Le barème logistique existe-t-il ?", "S'il existe, nous l'appliquons. Sinon, nous le construisons avec vous."),
        ("D4", "Comment le client paie-t-il réellement ?", "Part du cash, part du mobile money. Cela définit le circuit d'encaissement."),
        ("D5", "Quel rôle pour le réseau de dépôts ?", "Points de retrait renforcés, ou vente directe. La décision vous revient."),
    ]
    colonne_gauche = decisions[:3]
    colonne_droite = decisions[3:]
    largeur = (LARGEUR_UTILE - Inches(0.35)) / 2
    for colonne, elements in ((MARGE, colonne_gauche), (MARGE + largeur + Inches(0.35), colonne_droite)):
        y = Inches(2.2)
        for code, question, corps in elements:
            rectangle(diapo, colonne, y, largeur, Inches(1.35), BLANC, arrondi=True)
            texte(diapo, colonne + Inches(0.28), y + Inches(0.18), Inches(0.7), Inches(0.3),
                  code, taille=12, couleur=ORANGE, gras=True)
            texte(diapo, colonne + Inches(0.95), y + Inches(0.15), largeur - Inches(1.2), Inches(0.45),
                  question, taille=12.5, couleur=NUIT, gras=True, interligne=1.1)
            texte(diapo, colonne + Inches(0.95), y + Inches(0.68), largeur - Inches(1.2), Inches(0.55),
                  corps, taille=10.5, couleur=GRIS, interligne=1.2)
            y += Inches(1.48)

    rectangle(diapo, MARGE, Inches(6.3), LARGEUR_UTILE, Inches(0.62), NUIT, arrondi=True)
    texte(diapo, MARGE + Inches(0.35), Inches(6.45), Inches(10.6), Inches(0.35),
          "Trois semaines d'ateliers suffisent à trancher ces cinq points. Elles conditionnent tout le reste.",
          taille=12.5, couleur=BLANC, gras=True)
    pied(diapo)
    notes(diapo, "Ne pas sortir de la salle sans un référent métier nommé et une date d'atelier de cadrage. "
                 "C'est le seul vrai indicateur de succès de la réunion.")


def d22_credits(prs):
    diapo = prs.slides.add_slide(prs.slide_layouts[6])
    fond(diapo, NUIT)
    texte(diapo, MARGE, Inches(0.9), Inches(6.0), Inches(0.35), "Crédits photographiques",
          taille=20, couleur=BLANC, gras=True, police=POLICE_TITRE)
    texte(diapo, MARGE, Inches(1.45), Inches(11.4), Inches(0.4),
          "Les photographies de cette présentation proviennent de Wikimedia Commons et sont réutilisables "
          "sous réserve de créditer leurs auteurs.",
          taille=11, couleur=RGBColor(0xB6, 0xC6, 0xD4), italique=True)

    credits = {
        "couverture": "Cement bags in Douma — CC BY 4.0",
        "douleur_manutention": "Father and son loading and unloading cement in Goma, Congo — CC BY-SA 4.0",
        "douleur_route": "Road to Boali — CC BY-SA 4.0",
        "douleur_attente": "Namanga (file de camions à un poste frontière) — CC BY-SA 4.0",
        "usine": "Rotary kilns, Sundon cement plant — CC BY-SA 2.0",
        "livraison": "Semi truck for cement transportation — CC BY-SA 4.0",
        "mobile": "Mobile Money Kiosk — CC BY-SA 4.0",
        "ville": "Construction site in Pretoria Central — CC BY-SA 4.0",
    }
    paragraphes = []
    for nom, mention in credits.items():
        paragraphes.append({"runs": [
            (f"{nom}  ·  ", {"couleur": ORANGE, "gras": True, "taille": 10.5}),
            (mention, {"couleur": RGBColor(0xB6, 0xC6, 0xD4), "taille": 10.5}),
        ], "espace_apres": 7})
    texte(diapo, MARGE, Inches(2.15), Inches(8.4), Inches(3.5), paragraphes, interligne=1.2)

    rectangle(diapo, MARGE, Inches(5.9), LARGEUR_UTILE, Inches(0.9), NUIT_MOYEN, arrondi=True)
    texte(diapo, MARGE + Inches(0.32), Inches(6.05), Inches(10.8), Inches(0.6),
          "Les détails complets — auteur, licence et page source — figurent dans assets/credits.json du dossier de projet.",
          taille=11, couleur=RGBColor(0xC3, 0xD0, 0xDA), interligne=1.2)
    pied(diapo, sombre=True)


# ---------------------------------------------------------------------------
# Programme principal
# ---------------------------------------------------------------------------
def construire(chemin: Path) -> int:
    prs = Presentation()
    prs.slide_width = LARGEUR
    prs.slide_height = HAUTEUR

    constructeurs = [
        d01_couverture, d02_probleme, d03_questions, d04_douleurs_ppc, d05_section_marche,
        d06_client_final, d07_transporteur, d08_cout_inaction, d09_section_reponse, d10_all_in_one,
        d11_chaine_preuve, d12_ubiquite, d13_sequestre, d14_preuve_livraison, d15_bareme,
        d16_groupage, d17_comparaison, d18_controle, d19_indicateurs, d20_calendrier,
        d21_decisions, d22_credits,
    ]
    for constructeur in constructeurs:
        constructeur(prs)

    prs.core_properties.title = "APIX All In One — présentation PPC"
    prs.core_properties.author = "FBB"
    prs.core_properties.subject = "Extension APIX : clients finaux, paiement séquestré et logistique ciment"
    prs.core_properties.comments = "Présentation générée par outils/build_pptx.py"

    chemin.parent.mkdir(parents=True, exist_ok=True)
    prs.save(chemin)
    return len(prs.slides._sldIdLst)


def main() -> int:
    analyseur = argparse.ArgumentParser(description="Génère la présentation APIX All In One.")
    analyseur.add_argument("--sortie", default=str(SORTIE_DEFAUT), help="Chemin du fichier .pptx à produire.")
    arguments = analyseur.parse_args()

    chemin = Path(arguments.sortie)
    if not chemin.is_absolute():
        chemin = RACINE / chemin

    try:
        nombre = construire(chemin)
    except Exception as erreur:  # noqa: BLE001
        print(f"[ERREUR] {erreur}", file=sys.stderr)
        raise
    print(f"[OK] {chemin.relative_to(RACINE)} — {nombre} diapositives")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
