"""Met en page la lettre d'arbitrage technique.

Contrairement au reste du dossier, une lettre n'a ni page de garde ni titres
numerotes : elle a un en-tete, un destinataire, une date, un objet, un corps
et une signature. C'est pourquoi elle a son propre script plutot que d'entrer
dans le manifeste de build_docs.py.

Usage : python outils\\build_lettre.py
"""
from __future__ import annotations

import sys
from datetime import date
from pathlib import Path

from docx import Document
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.oxml.ns import qn
from docx.shared import Cm, Pt, RGBColor

RACINE = Path(__file__).resolve().parent.parent
SOURCE = RACINE / "docs" / "07-lettre-arbitrage-technique.md"
SORTIE = RACINE / "dist" / "docs" / "07-Lettre-arbitrage-technique.docx"

NUIT = RGBColor(0x0E, 0x24, 0x36)
ORANGE = RGBColor(0xE0, 0x6B, 0x2D)
GRIS = RGBColor(0x5A, 0x6B, 0x7A)

EXPEDITEUR = "FBB — Équipe projet APIX"
SUJET_EXPEDITEUR = "Extension APIX · PPC"
DESTINATAIRE = ["Monsieur Eloge"]
OBJET = ("Ce que l'échéance du 1er décembre permet encore de présenter, "
         "et pourquoi l'architecture étendue ne peut pas y répondre")
DATE_TEXTE = "Le 25 novembre 2026"
SIGNATURE = ["Pour FBB,", "L'équipe projet APIX"]


def police(document: Document) -> None:
    style = document.styles["Normal"]
    style.font.name = "Segoe UI"
    style.font.size = Pt(10.5)
    style.element.rPr.rFonts.set(qn("w:eastAsia"), "Segoe UI")
    style.paragraph_format.space_after = Pt(7)
    style.paragraph_format.line_spacing = 1.15


def filet(paragraphe) -> None:
    """Trait orange sous l'en-tete."""
    from docx.oxml import OxmlElement

    bordures = OxmlElement("w:pBdr")
    bas = OxmlElement("w:bottom")
    bas.set(qn("w:val"), "single")
    bas.set(qn("w:sz"), "12")
    bas.set(qn("w:space"), "4")
    bas.set(qn("w:color"), "E06B2D")
    bordures.append(bas)
    paragraphe._p.get_or_add_pPr().append(bordures)


def ajouter_texte(paragraphe, texte: str, taille: float | None = None,
                  couleur: RGBColor | None = None, gras_par_defaut: bool = False) -> None:
    """Ecrit un texte en respectant les segments **gras**."""
    morceaux = texte.split("**")
    for index, morceau in enumerate(morceaux):
        if not morceau:
            continue
        run = paragraphe.add_run(morceau)
        run.bold = gras_par_defaut or (index % 2 == 1)
        if taille:
            run.font.size = Pt(taille)
        if couleur:
            run.font.color.rgb = couleur


def main() -> int:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    document = Document()

    section = document.sections[0]
    section.page_width, section.page_height = Cm(21), Cm(29.7)
    for cote in ("top_margin", "bottom_margin"):
        setattr(section, cote, Cm(2.0))
    for cote in ("left_margin", "right_margin"):
        setattr(section, cote, Cm(2.4))
    police(document)

    # --- en-tete ------------------------------------------------------------
    entete = document.add_paragraph()
    entete.paragraph_format.space_after = Pt(2)
    ajouter_texte(entete, EXPEDITEUR, taille=12, couleur=NUIT, gras_par_defaut=True)
    detail = document.add_paragraph()
    ajouter_texte(detail, SUJET_EXPEDITEUR, taille=9, couleur=GRIS)
    filet(detail)
    detail.paragraph_format.space_after = Pt(16)

    # --- destinataire et date ----------------------------------------------
    for ligne in DESTINATAIRE:
        bloc = document.add_paragraph()
        bloc.paragraph_format.space_after = Pt(0)
        ajouter_texte(bloc, ligne, taille=11, couleur=NUIT, gras_par_defaut=True)
    for _ in range(2):
        document.add_paragraph().paragraph_format.space_after = Pt(0)

    quand = document.add_paragraph()
    quand.alignment = WD_ALIGN_PARAGRAPH.RIGHT
    ajouter_texte(quand, DATE_TEXTE, taille=10, couleur=GRIS)
    quand.paragraph_format.space_after = Pt(18)

    # --- objet --------------------------------------------------------------
    objet = document.add_paragraph()
    objet.paragraph_format.space_after = Pt(4)
    ajouter_texte(objet, "Objet : ", taille=10.5, couleur=NUIT, gras_par_defaut=True)
    ajouter_texte(objet, OBJET, taille=10.5)
    filet(objet)
    objet.paragraph_format.space_after = Pt(16)

    # --- corps --------------------------------------------------------------
    lignes = SOURCE.read_text(encoding="utf-8").split("\n")
    paragraphes, puces, courant = [], [], []
    for ligne in lignes:
        depouillee = ligne.rstrip()
        if not depouillee:
            if courant:
                paragraphes.append((" ".join(courant), puces))
                courant, puces = [], []
            continue
        if depouillee.startswith("- "):
            puces.append(depouillee[2:].strip())
            continue
        courant.append(depouillee.strip())
    if courant:
        paragraphes.append((" ".join(courant), puces))

    for texte, liste in paragraphes:
        if texte:
            bloc = document.add_paragraph()
            bloc.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
            ajouter_texte(bloc, texte)
        for element in liste:
            puce = document.add_paragraph(style="List Bullet")
            puce.paragraph_format.left_indent = Cm(0.9)
            puce.paragraph_format.space_after = Pt(4)
            ajouter_texte(puce, element)

    # --- signature ----------------------------------------------------------
    document.add_paragraph()
    for ligne in SIGNATURE:
        bloc = document.add_paragraph()
        bloc.paragraph_format.space_after = Pt(0)
        ajouter_texte(bloc, ligne, taille=10.5, couleur=NUIT if ligne is SIGNATURE[0] else None,
                      gras_par_defaut=(ligne is SIGNATURE[0]))

    document.core_properties.title = "Lettre d'arbitrage technique"
    document.core_properties.author = "FBB"
    document.core_properties.subject = "Extension APIX — PPC"
    SORTIE.parent.mkdir(parents=True, exist_ok=True)
    document.save(SORTIE)

    mots = sum(len(t.split()) for t, _ in paragraphes)
    taille = SORTIE.stat().st_size / 1024
    print(f"[OK] {SORTIE.relative_to(RACINE)} — {len(paragraphes)} paragraphes, {mots} mots, "
          f"{taille:.0f} Ko")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
