#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
build_fiche.py — Fiche A4 d'une page à remettre à PPC après la présentation.

Objet : obtenir par écrit le circuit réel de règlement des transporteurs, qui
conditionne le délai, le mode et les conditions auxquels APIX pourra lier le
paiement à la preuve de livraison.

Ce document est volontairement *à remplir* : il transforme une inconnue en
questions fermées, et donne à PPC une raison légitime de réunir ses équipes.

Usage :
    python outils/build_fiche.py
"""

from __future__ import annotations

import sys
from pathlib import Path

from docx import Document
from docx.enum.table import WD_ALIGN_VERTICAL
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.oxml import OxmlElement
from docx.oxml.ns import qn
from docx.shared import Cm, Pt, RGBColor

RACINE = Path(__file__).resolve().parent.parent
SORTIE = RACINE / "dist" / "docs" / "F1-Fiche-cadrage-reglement-PPC.docx"

try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
except (AttributeError, ValueError):
    pass

NUIT = RGBColor(0x0E, 0x24, 0x36)
ORANGE = RGBColor(0xE0, 0x6B, 0x2D)
GRIS = RGBColor(0x5A, 0x6B, 0x7A)
GRIS_CLAIR = RGBColor(0x9A, 0xA5, 0xAE)

LARGEUR_UTILE = Cm(21) - Cm(1.6) * 2


# ---------------------------------------------------------------------------
# Utilitaires
# ---------------------------------------------------------------------------
def paragraphe(conteneur, texte="", taille=9.5, gras=False, italique=False,
               couleur=NUIT, apres=4, avant=0, alignement=None, interligne=1.1):
    p = conteneur.add_paragraph()
    p.paragraph_format.space_after = Pt(apres)
    p.paragraph_format.space_before = Pt(avant)
    p.paragraph_format.line_spacing = interligne
    if alignement is not None:
        p.alignment = alignement
    if texte:
        run = p.add_run(texte)
        run.font.name = "Calibri"
        run.font.size = Pt(taille)
        run.font.bold = gras
        run.font.italic = italique
        run.font.color.rgb = couleur
    return p


def ombre(cellule, couleur_hex: str) -> None:
    fond = OxmlElement("w:shd")
    fond.set(qn("w:val"), "clear")
    fond.set(qn("w:color"), "auto")
    fond.set(qn("w:fill"), couleur_hex)
    cellule._tc.get_or_add_tcPr().append(fond)


def bordure_bas(paragraphe_, couleur="D8D8D8", epaisseur="8"):
    props = paragraphe_._p.get_or_add_pPr()
    bordures = OxmlElement("w:pBdr")
    bas = OxmlElement("w:bottom")
    bas.set(qn("w:val"), "single")
    bas.set(qn("w:sz"), epaisseur)
    bas.set(qn("w:space"), "2")
    bas.set(qn("w:color"), couleur)
    bordures.append(bas)
    props.append(bordures)


# ---------------------------------------------------------------------------
# Contenu
# ---------------------------------------------------------------------------
QUESTIONS = [
    (
        "Quel est le délai réel entre la livraison et le règlement du transporteur ?",
        "Délai moyen constaté, minimum et maximum, et ce qui explique les écarts (mois de pointe, "
        "dossiers incomplets, arbitrage d’un litige).",
    ),
    (
        "Par quel moyen le transporteur est-il payé ?",
        "Espèces, virement bancaire, mobile money, ou compensation sur une autre course. "
        "Préciser si plusieurs moyens coexistent selon la zone.",
    ),
    (
        "Qui émet l’ordre de paiement, et qui le valide ?",
        "Siège, usine, dépôt ou direction logistique. Nombre de validations successives et délai "
        "de chacune. C’est ce circuit qu’APIX devra respecter.",
    ),
    (
        "Existe-t-il des avances au transporteur, et comment sont-elles récupérées ?",
        "Avance carburant ou péage, montant habituel, mode de déduction sur le règlement, "
        "garantie éventuellement demandée.",
    ),
    (
        "Quelles retenues sont déjà pratiquées, et sur quelle base ?",
        "Pénalités de retard, casse, sacs manquants, litiges en cours. Qui décide, selon quelle "
        "pièce, et avec quel recours pour le transporteur.",
    ),
]

PRECISIONS = [
    "Le transport est-il compris dans le prix du ciment facturé au client, ou facturé sur une ligne "
    "séparée ? Le traitement comptable diffère, donc la traçabilité aussi.",
    "Le transporteur est-il réglé à la course, à la période (semaine, quinzaine, mois), ou à la fin "
    "d’un chantier ? C’est ce rythme qui détermine le délai que nous pourrons proposer.",
]


def construire() -> int:
    doc = Document()

    section = doc.sections[0]
    section.page_width = Cm(21)
    section.page_height = Cm(29.7)
    section.left_margin = Cm(1.6)
    section.right_margin = Cm(1.6)
    section.top_margin = Cm(1.4)
    section.bottom_margin = Cm(1.1)

    normal = doc.styles["Normal"]
    normal.font.name = "Calibri"
    normal.font.size = Pt(9.5)
    normal.element.rPr.rFonts.set(qn("w:eastAsia"), "Calibri")

    # En-tête
    bandeau = paragraphe(doc, "F B B   ·   A P I X", taille=8.5, gras=True, couleur=ORANGE, apres=2)
    bordure_bas(bandeau, couleur="E06B2D", epaisseur="12")

    paragraphe(doc, "Le règlement des transporteurs : cinq questions à établir",
               taille=17, gras=True, apres=2, avant=8)
    paragraphe(doc, "Fiche à compléter par PPC avant l’atelier de cadrage — Direction générale, "
                    "direction logistique et direction financière",
               taille=9, italique=True, couleur=GRIS, apres=10)

    paragraphe(doc, "Nous ne connaissons pas, à ce jour, le circuit de règlement de PPC. Or c’est lui qui "
                    "détermine le délai, le mode et les conditions auxquels APIX pourra lier le paiement du "
                    "transport à la preuve de livraison. Nous préférons poser la question que supposer la réponse.",
               taille=9.5, couleur=GRIS, apres=10, interligne=1.15)

    # Tableau des questions
    tableau = doc.add_table(rows=1, cols=3)
    tableau.style = "Table Grid"
    tableau.autofit = False
    largeurs = [Cm(0.9), Cm(9.0), Cm(7.9)]

    entetes = ["N°", "Question", "Réponse de PPC"]
    for index, (cellule, libelle, largeur) in enumerate(zip(tableau.rows[0].cells, entetes, largeurs)):
        cellule.width = largeur
        ombre(cellule, "0E2436")
        p = cellule.paragraphs[0]
        p.paragraph_format.space_after = Pt(1)
        p.paragraph_format.space_before = Pt(1)
        run = p.add_run(libelle)
        run.font.name = "Calibri"
        run.font.size = Pt(8.5)
        run.font.bold = True
        run.font.color.rgb = RGBColor(0xFF, 0xFF, 0xFF)

    for numero, (question, precision) in enumerate(QUESTIONS, start=1):
        ligne = tableau.add_row()
        for cellule, largeur in zip(ligne.cells, largeurs):
            cellule.width = largeur
            cellule.vertical_alignment = WD_ALIGN_VERTICAL.TOP
        ligne.height = Cm(2.15)

        p = ligne.cells[0].paragraphs[0]
        p.alignment = WD_ALIGN_PARAGRAPH.CENTER
        run = p.add_run(str(numero))
        run.font.name = "Calibri"
        run.font.size = Pt(11)
        run.font.bold = True
        run.font.color.rgb = ORANGE

        p = ligne.cells[1].paragraphs[0]
        p.paragraph_format.space_after = Pt(2)
        run = p.add_run(question)
        run.font.name = "Calibri"
        run.font.size = Pt(9.5)
        run.font.bold = True
        run.font.color.rgb = NUIT

        p = ligne.cells[1].add_paragraph()
        p.paragraph_format.space_after = Pt(1)
        run = p.add_run("Ce que nous cherchons : " + precision)
        run.font.name = "Calibri"
        run.font.size = Pt(8)
        run.font.italic = True
        run.font.color.rgb = GRIS

    # Deux précisions complémentaires
    paragraphe(doc, "Deux précisions qui changent le calcul", taille=11, gras=True, avant=12, apres=4)

    for texte in PRECISIONS:
        p = doc.add_paragraph(style="List Bullet")
        p.paragraph_format.space_after = Pt(3)
        run = p.add_run(texte)
        run.font.name = "Calibri"
        run.font.size = Pt(9)
        run.font.color.rgb = NUIT

    # Encadré de clôture
    paragraphe(doc, "Nous n’annoncerons aucun délai de règlement avant d’avoir ces réponses. Ce qui sera écrit "
                    "dans le contrat sera ce que votre circuit permet réellement, pas une promesse commerciale.",
               taille=9.5, gras=True, couleur=NUIT, avant=12, apres=10, interligne=1.15)

    # Bloc de signature
    tableau_signature = doc.add_table(rows=1, cols=3)
    tableau_signature.autofit = False
    for cellule, libelle in zip(tableau_signature.rows[0].cells,
                                ["Fiche complétée par", "Fonction", "Date"]):
        cellule.width = Cm(5.9)
        p = cellule.paragraphs[0]
        p.paragraph_format.space_after = Pt(0)
        run = p.add_run(libelle)
        run.font.name = "Calibri"
        run.font.size = Pt(8)
        run.font.color.rgb = GRIS_CLAIR
        bordure_bas(p, couleur="BBBBBB", epaisseur="6")

    paragraphe(doc, "Document de travail FBB · APIX", taille=7.5,
               couleur=GRIS_CLAIR, avant=14, apres=0, alignement=WD_ALIGN_PARAGRAPH.CENTER)

    doc.core_properties.title = "Le règlement des transporteurs : cinq questions à établir"
    doc.core_properties.author = "FBB"
    doc.core_properties.subject = "Fiche de cadrage à compléter par PPC"

    SORTIE.parent.mkdir(parents=True, exist_ok=True)
    doc.save(SORTIE)
    return len(QUESTIONS)


def main() -> int:
    nombre = construire()
    print(f"[OK] {SORTIE.relative_to(RACINE)} — {nombre} questions, une page A4")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
