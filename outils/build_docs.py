#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
build_docs.py — Export des documents Markdown du dossier APIX/PPC vers Word (.docx).

Usage :
    python outils/build_docs.py                # tous les documents
    python outils/build_docs.py --only 01      # un seul document (filtre sur le nom)
    python outils/build_docs.py --check        # vérifie la structure sans écrire

Le script prend les fichiers Markdown comme source de vérité et produit des
fichiers Word mis en forme : page de garde, titres, listes, tableaux,
blocs de code et formules. Aucune retouche manuelle du .docx n'est attendue :
toute correction se fait dans le Markdown, puis on relance le script.
"""

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

from docx import Document
from docx.enum.section import WD_ORIENT, WD_SECTION
from docx.enum.table import WD_TABLE_ALIGNMENT
from docx.enum.text import WD_ALIGN_PARAGRAPH, WD_BREAK
from docx.oxml import OxmlElement
from docx.oxml.ns import qn
from docx.shared import Cm, Mm, Pt, RGBColor

RACINE = Path(__file__).resolve().parent.parent
DOSSIER_SORTIE = RACINE / "dist" / "docs"

# --------------------------------------------------------------------------
# Manifeste des documents à produire
# --------------------------------------------------------------------------
DOCUMENTS = [
    {
        "source": "docs/00-synthese-executive.md",
        "sortie": "00-Synthese-executive.docx",
        "titre": "Synthèse exécutive",
        "sous_titre": "Extension APIX — Plateforme Clients Finaux & Logistique Ciment",
    },
    {
        "source": "docs/01-note-de-cadrage.md",
        "sortie": "01-Note-de-cadrage.docx",
        "titre": "Note de cadrage",
        "sous_titre": "Extension APIX — Plateforme Clients Finaux & Logistique Ciment",
    },
    {
        "source": "docs/02-specifications-fonctionnelles.md",
        "sortie": "02-Specifications-fonctionnelles.docx",
        "titre": "Spécifications fonctionnelles détaillées",
        "sous_titre": "Extension APIX — Plateforme Clients Finaux & Logistique Ciment",
    },
    {
        "source": "docs/03-architecture-technique.md",
        "sortie": "03-Architecture-technique.docx",
        "titre": "Architecture technique",
        "sous_titre": "Extension APIX — Plateforme Clients Finaux & Logistique Ciment",
    },
    {
        "source": "docs/04-argumentaire-commercial.md",
        "sortie": "04-Argumentaire-commercial.docx",
        "titre": "Argumentaire commercial",
        "sous_titre": "APIX étendu face à Digiciment — dossier de conviction pour PPC",
    },
    {
        "source": "docs/05-presentation-mvp-interfaces.md",
        "sortie": "05-Presentation-MVP-interfaces.docx",
        "titre": "Présentation du MVP et de ses interfaces",
        "sous_titre": "69 écrans, 11 interfaces, 4 parcours et 2 flux conversationnels",
    },
    {
        "source": "annexes/regles-de-gestion.md",
        "sortie": "A1-Regles-de-gestion.docx",
        "titre": "Annexe A1 — Règles de gestion",
        "sous_titre": "Règles opposables, versionnées et testables",
    },
    {
        "source": "annexes/questions-ouvertes-ppc.md",
        "sortie": "A2-Questions-ouvertes-PPC.docx",
        "titre": "Annexe A2 — Questions ouvertes à trancher avec PPC",
        "sous_titre": "Liste de cadrage et décisions attendues",
    },
    {
        "source": "annexes/plafonds-canaux-paiement.md",
        "sortie": "A3-Plafonds-canaux-paiement.docx",
        "titre": "Annexe A3 — Plafonds des canaux de paiement en RDC",
        "sous_titre": "Grilles par opérateur et par palier de vérification, et conséquences pour le routage",
    },
    {
        "source": "annexes/parite-des-canaux.md",
        "sortie": "A4-Parite-des-canaux.docx",
        "titre": "Annexe A4 — Parité des canaux",
        "sous_titre": "Cotation, paiement et bon sur WhatsApp, Telegram, e-mail, SMS et USSD",
    },
]

# --------------------------------------------------------------------------
# Expression de mise en forme en ligne
# --------------------------------------------------------------------------
MOTIF_EN_LIGNE = re.compile(
    r"(\*\*.+?\*\*"          # gras
    r"|__.+?__"              # gras alternatif
    r"|`[^`]+`"              # code
    r"|\*[^*\n]+?\*"         # italique
    r"|\[[^\]]*\]\([^)]*\)"  # lien
    r")"
)

COULEUR_TITRE = RGBColor(0x1F, 0x3A, 0x5F)
COULEUR_SOUS_TITRE = RGBColor(0x44, 0x44, 0x44)
COULEUR_GRIS = RGBColor(0x66, 0x66, 0x66)


# --------------------------------------------------------------------------
# Utilitaires de bas niveau
# --------------------------------------------------------------------------
def _ombre_cellule(cellule, couleur_hex: str) -> None:
    """Applique une couleur de fond à une cellule de tableau."""
    fond = OxmlElement("w:shd")
    fond.set(qn("w:val"), "clear")
    fond.set(qn("w:color"), "auto")
    fond.set(qn("w:fill"), couleur_hex)
    cellule._tc.get_or_add_tcPr().append(fond)


def _ombre_paragraphe(paragraphe, couleur_hex: str) -> None:
    """Applique une couleur de fond à un paragraphe entier."""
    props = paragraphe._p.get_or_add_pPr()
    fond = OxmlElement("w:shd")
    fond.set(qn("w:val"), "clear")
    fond.set(qn("w:color"), "auto")
    fond.set(qn("w:fill"), couleur_hex)
    props.append(fond)


def _ligne_entete_repetee(ligne) -> None:
    """Répète la ligne d'en-tête d'un tableau sur chaque page."""
    props = ligne._tr.get_or_add_trPr()
    entete = OxmlElement("w:tblHeader")
    entete.set(qn("w:val"), "true")
    props.append(entete)


def _bordure_bas(paragraphe, couleur_hex: str = "D0D0D0") -> None:
    """Trace un filet horizontal sous un paragraphe, en substitut de règle Markdown."""
    props = paragraphe._p.get_or_add_pPr()
    bordures = OxmlElement("w:pBdr")
    bas = OxmlElement("w:bottom")
    bas.set(qn("w:val"), "single")
    bas.set(qn("w:sz"), "6")
    bas.set(qn("w:space"), "1")
    bas.set(qn("w:color"), couleur_hex)
    bordures.append(bas)
    props.append(bordures)


def _case_a_cocher(contenu: str) -> str | None:
    """Traduit la syntaxe de case à cocher Markdown en symbole lisible."""
    if contenu.startswith("[ ] "):
        return "☐  " + contenu[4:]
    if contenu.startswith("[x] ") or contenu.startswith("[X] "):
        return "☑  " + contenu[4:]
    return None


STYLE_PUCE = {1: "List Bullet", 2: "List Bullet 2", 3: "List Bullet 3"}


def ajouter_runs(paragraphe, texte: str, taille: float | None = None, gras: bool = False) -> None:
    """Ajoute du texte à un paragraphe en interprétant la mise en forme Markdown simple."""
    if not texte:
        return
    position = 0
    for trouve in MOTIF_EN_LIGNE.finditer(texte):
        if trouve.start() > position:
            _run(paragraphe, texte[position:trouve.start()], taille=taille, gras=gras)
        fragment = trouve.group(0)
        if fragment.startswith("**") and fragment.endswith("**") and len(fragment) > 4:
            _run(paragraphe, fragment[2:-2], taille=taille, gras=True)
        elif fragment.startswith("__") and fragment.endswith("__") and len(fragment) > 4:
            _run(paragraphe, fragment[2:-2], taille=taille, gras=True)
        elif fragment.startswith("`") and fragment.endswith("`") and len(fragment) > 2:
            _run(paragraphe, fragment[1:-1], taille=taille, gras=gras, monospace=True)
        elif fragment.startswith("*") and fragment.endswith("*") and len(fragment) > 2:
            _run(paragraphe, fragment[1:-1], taille=taille, gras=gras, italique=True)
        elif fragment.startswith("["):
            libelle = fragment[1:fragment.index("]")]
            _run(paragraphe, libelle, taille=taille, gras=gras)
        else:
            _run(paragraphe, fragment, taille=taille, gras=gras)
        position = trouve.end()
    if position < len(texte):
        _run(paragraphe, texte[position:], taille=taille, gras=gras)


def _run(paragraphe, texte, taille=None, gras=False, italique=False, monospace=False):
    if not texte:
        return
    run = paragraphe.add_run(texte)
    run.bold = gras
    run.italic = italique
    if taille is not None:
        run.font.size = Pt(taille)
    if monospace:
        run.font.name = "Consolas"
        run._element.rPr.rFonts.set(qn("w:eastAsia"), "Consolas")
        run.font.size = Pt(taille if taille else 9)
    return run


# --------------------------------------------------------------------------
# Styles du document
# --------------------------------------------------------------------------
def preparer_document() -> Document:
    doc = Document()

    section = doc.sections[0]
    section.top_margin = Cm(2.0)
    section.bottom_margin = Cm(2.0)
    section.left_margin = Cm(2.0)
    section.right_margin = Cm(2.0)

    normal = doc.styles["Normal"]
    normal.font.name = "Calibri"
    normal.font.size = Pt(10.5)
    normal.element.rPr.rFonts.set(qn("w:eastAsia"), "Calibri")
    normal.paragraph_format.space_after = Pt(6)
    normal.paragraph_format.line_spacing = 1.08

    for niveau, taille in ((1, 18), (2, 14), (3, 12), (4, 11)):
        style = doc.styles[f"Heading {niveau}"]
        style.font.name = "Calibri"
        style.font.size = Pt(taille)
        style.font.bold = True
        style.font.color.rgb = COULEUR_TITRE
        style.paragraph_format.space_before = Pt(14 if niveau == 1 else 10)
        style.paragraph_format.space_after = Pt(6)
        style.paragraph_format.keep_with_next = True

    return doc


def page_de_garde(doc: Document, titre: str, sous_titre: str, source: Path) -> None:
    for _ in range(4):
        doc.add_paragraph()

    p = doc.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.LEFT
    run = p.add_run("FBB  ·  APIX")
    run.bold = True
    run.font.size = Pt(11)
    run.font.color.rgb = COULEUR_GRIS

    p = doc.add_paragraph()
    run = p.add_run(titre)
    run.bold = True
    run.font.size = Pt(26)
    run.font.color.rgb = COULEUR_TITRE

    p = doc.add_paragraph()
    run = p.add_run(sous_titre)
    run.font.size = Pt(13)
    run.font.color.rgb = COULEUR_SOUS_TITRE

    doc.add_paragraph()

    for ligne in (
        "Maître d'ouvrage : FBB — concepteur d'APIX",
        "Client cible : PPC (cimentier, République Démocratique du Congo)",
        "Version : 1.0 — 4 novembre 2026",
        f"Fichier source : {source.name}",
    ):
        p = doc.add_paragraph()
        run = p.add_run(ligne)
        run.font.size = Pt(9.5)
        run.font.color.rgb = COULEUR_GRIS

    p = doc.add_paragraph()
    p.add_run().add_break(WD_BREAK.PAGE)


# --------------------------------------------------------------------------
# Analyse du Markdown
# --------------------------------------------------------------------------
def decouper_lignes(texte: str) -> list[str]:
    return texte.replace("\r\n", "\n").replace("\r", "\n").split("\n")


def est_separateur_tableau(ligne: str) -> bool:
    return bool(re.fullmatch(r"\s*\|?[\s:\-|]+\|[\s:\-|]*\s*", ligne)) and "-" in ligne


def cellules(ligne: str) -> list[str]:
    ligne = ligne.strip()
    if ligne.startswith("|"):
        ligne = ligne[1:]
    if ligne.endswith("|"):
        ligne = ligne[:-1]
    return [c.strip() for c in ligne.split("|")]


def changer_orientation(doc: Document, paysage: bool) -> None:
    """Ouvre une nouvelle section en changeant l'orientation de la page."""
    section = doc.add_section(WD_SECTION.NEW_PAGE)
    if paysage:
        section.orientation = WD_ORIENT.LANDSCAPE
        section.page_width, section.page_height = Mm(297), Mm(210)
    else:
        section.orientation = WD_ORIENT.PORTRAIT
        section.page_width, section.page_height = Mm(210), Mm(297)
    section.top_margin = Cm(1.8)
    section.bottom_margin = Cm(1.8)
    section.left_margin = Cm(2.0)
    section.right_margin = Cm(2.0)


def rendre_image(doc: Document, legende: str, chemin: str,
                 largeur_cm: float | None = None) -> None:
    """Insère une image centrée, suivie de sa légende en petits caractères."""
    fichier = (RACINE / chemin).resolve()
    if not fichier.exists():
        raise FileNotFoundError(f"Image introuvable : {chemin}")
    paragraphe = doc.add_paragraph()
    paragraphe.alignment = WD_ALIGN_PARAGRAPH.CENTER
    paragraphe.paragraph_format.space_before = Pt(4)
    paragraphe.paragraph_format.space_after = Pt(2)
    paragraphe.add_run().add_picture(str(fichier), width=Cm(largeur_cm or 16.0))
    if legende:
        texte_legende = doc.add_paragraph()
        texte_legende.alignment = WD_ALIGN_PARAGRAPH.CENTER
        texte_legende.paragraph_format.space_after = Pt(10)
        run = texte_legende.add_run(legende)
        run.italic = True
        run.font.size = Pt(8.5)
        run.font.color.rgb = COULEUR_GRIS


def rendre_tableau(doc: Document, entetes: list[str], lignes: list[list[str]]) -> None:
    colonnes = max(len(entetes), max((len(l) for l in lignes), default=0))
    tableau = doc.add_table(rows=1, cols=colonnes)
    tableau.style = "Table Grid"
    tableau.alignment = WD_TABLE_ALIGNMENT.CENTER
    tableau.autofit = True

    ligne_entete = tableau.rows[0]
    _ligne_entete_repetee(ligne_entete)
    for index in range(colonnes):
        cellule = ligne_entete.cells[index]
        texte = entetes[index] if index < len(entetes) else ""
        paragraphe = cellule.paragraphs[0]
        paragraphe.paragraph_format.space_after = Pt(0)
        ajouter_runs(paragraphe, texte, taille=8.5, gras=True)
        _ombre_cellule(cellule, "E8EEF6")

    for contenu in lignes:
        ligne = tableau.add_row()
        for index in range(colonnes):
            cellule = ligne.cells[index]
            texte = contenu[index] if index < len(contenu) else ""
            paragraphe = cellule.paragraphs[0]
            paragraphe.paragraph_format.space_after = Pt(0)
            ajouter_runs(paragraphe, texte, taille=8.5)

    doc.add_paragraph()


def rendre_bloc_code(doc: Document, lignes: list[str], langage: str) -> None:
    if langage == "mermaid":
        note = doc.add_paragraph()
        run = note.add_run("Schéma — source Mermaid (à rendre graphiquement dans la présentation)")
        run.italic = True
        run.font.size = Pt(9)
        run.font.color.rgb = COULEUR_GRIS

    for brute in lignes:
        p = doc.add_paragraph()
        p.paragraph_format.space_after = Pt(0)
        p.paragraph_format.space_before = Pt(0)
        p.paragraph_format.left_indent = Cm(0.4)
        run = p.add_run(brute if brute else " ")
        run.font.name = "Consolas"
        run._element.rPr.rFonts.set(qn("w:eastAsia"), "Consolas")
        run.font.size = Pt(8)
        _ombre_paragraphe(p, "F4F4F4")

    doc.add_paragraph()


def rendre_formule(doc: Document, contenu: str) -> None:
    p = doc.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    run = p.add_run(contenu)
    run.font.name = "Cambria Math"
    run._element.rPr.rFonts.set(qn("w:eastAsia"), "Cambria Math")
    run.font.size = Pt(11)
    run.italic = True


def convertir(chemin: Path, doc: Document) -> dict:
    """Convertit un fichier Markdown dans le document Word fourni. Retourne des statistiques."""
    lignes = decouper_lignes(chemin.read_text(encoding="utf-8"))
    stats = {"titres": 0, "tableaux": 0, "listes": 0, "paragraphes": 0, "blocs_code": 0, "images": 0}

    index = 0
    premier_titre_ignore = False
    premier_paragraphe_ignore = False
    separateur_initial_ignore = False

    while index < len(lignes):
        ligne = lignes[index]
        depouillee = ligne.strip()

        # Ligne vide
        if not depouillee:
            index += 1
            continue

        # Bloc de code
        if depouillee.startswith("```"):
            langage = depouillee[3:].strip().lower()
            index += 1
            bloc = []
            while index < len(lignes) and not lignes[index].strip().startswith("```"):
                bloc.append(lignes[index])
                index += 1
            index += 1
            rendre_bloc_code(doc, bloc, langage)
            stats["blocs_code"] += 1
            continue

        # Formule sur une seule ligne
        if depouillee.startswith("$$"):
            contenu = depouillee
            if contenu.count("$$") >= 2:
                rendre_formule(doc, contenu.strip("$").strip())
                index += 1
                continue
            index += 1
            bloc = [depouillee.strip("$")]
            while index < len(lignes) and "$$" not in lignes[index]:
                bloc.append(lignes[index])
                index += 1
            if index < len(lignes):
                bloc.append(lignes[index].replace("$$", ""))
                index += 1
            rendre_formule(doc, " ".join(b.strip() for b in bloc if b.strip()))
            continue

        # Règle horizontale
        if re.fullmatch(r"(\-\-\-|\*\*\*|___)\s*", depouillee):
            if premier_titre_ignore and not separateur_initial_ignore and stats["titres"] == 0:
                separateur_initial_ignore = True
                index += 1
                continue
            p = doc.add_paragraph()
            p.paragraph_format.space_before = Pt(2)
            p.paragraph_format.space_after = Pt(8)
            _bordure_bas(p)
            index += 1
            continue

        # Changement d'orientation de page
        if depouillee in (":::paysage", ":::portrait"):
            changer_orientation(doc, paysage=depouillee == ":::paysage")
            index += 1
            continue

        # Image avec légende : ![légende](chemin) ou ![légende|largeur_cm](chemin)
        correspondance = re.match(r"^!\[(.*?)\]\((.+?)\)\s*$", depouillee)
        if correspondance:
            legende, cible = correspondance.group(1), correspondance.group(2)
            largeur = None
            if "|" in legende:
                legende, _, valeur = legende.rpartition("|")
                try:
                    largeur = float(valeur)
                except ValueError:
                    legende, largeur = correspondance.group(1), None
            rendre_image(doc, legende.strip(), cible.strip(), largeur)
            stats["images"] += 1
            index += 1
            continue

        # Titres
        correspondance = re.match(r"^(#{1,6})\s+(.*)$", depouillee)
        if correspondance:
            niveau = len(correspondance.group(1))
            texte_titre = correspondance.group(2).strip()
            if niveau == 1 and not premier_titre_ignore:
                premier_titre_ignore = True
                index += 1
                continue
            doc.add_heading(texte_titre, level=min(niveau, 4))
            stats["titres"] += 1
            index += 1
            continue

        # Tableau
        if depouillee.startswith("|") and index + 1 < len(lignes) and est_separateur_tableau(lignes[index + 1]):
            entetes = cellules(lignes[index])
            index += 2
            corps = []
            while index < len(lignes) and lignes[index].strip().startswith("|"):
                corps.append(cellules(lignes[index]))
                index += 1
            rendre_tableau(doc, entetes, corps)
            stats["tableaux"] += 1
            continue

        # Citation
        if depouillee.startswith(">"):
            bloc = []
            while index < len(lignes) and lignes[index].strip().startswith(">"):
                bloc.append(lignes[index].strip().lstrip(">").strip())
                index += 1
            p = doc.add_paragraph()
            p.paragraph_format.left_indent = Cm(0.6)
            ajouter_runs(p, " ".join(b for b in bloc if b), taille=10, gras=False)
            for run in p.runs:
                run.italic = True
                run.font.color.rgb = COULEUR_SOUS_TITRE
            _ombre_paragraphe(p, "F7F4EC")
            continue

        # Listes à puces ou numérotées (avec imbrication)
        if re.match(r"^(\s*)([-*+]|\d+\.)\s+", ligne):
            while index < len(lignes) and re.match(r"^(\s*)([-*+]|\d+\.)\s+", lignes[index]):
                courante = lignes[index]
                correspondance = re.match(r"^(\s*)([-*+]|\d+\.)\s+(.*)$", courante)
                retrait = len(correspondance.group(1))
                marqueur = correspondance.group(2)
                contenu = correspondance.group(3)
                niveau = 1 if retrait < 2 else min(retrait // 2 + 1, 3)

                if marqueur[0].isdigit():
                    # On conserve le numéro du Markdown : la numérotation automatique
                    # de Word reprendrait la suite du sommaire, ce qui serait faux.
                    p = doc.add_paragraph()
                    p.paragraph_format.left_indent = Cm(0.4 * niveau + 0.4)
                    p.paragraph_format.first_line_indent = Cm(-0.4)
                    p.paragraph_format.space_after = Pt(2)
                    numero = p.add_run(f"{marqueur} ")
                    numero.bold = True
                    ajouter_runs(p, contenu)
                    stats["listes"] += 1
                    index += 1
                    continue

                coche = _case_a_cocher(contenu)
                if coche is not None:
                    p = doc.add_paragraph()
                    p.paragraph_format.left_indent = Cm(0.4 * niveau + 0.4)
                    p.paragraph_format.first_line_indent = Cm(-0.4)
                    p.paragraph_format.space_after = Pt(2)
                    ajouter_runs(p, coche)
                    stats["listes"] += 1
                    index += 1
                    continue

                style = STYLE_PUCE.get(niveau, "List Bullet")
                try:
                    p = doc.add_paragraph(style=style)
                except KeyError:
                    p = doc.add_paragraph(style="List Bullet")
                p.paragraph_format.space_after = Pt(2)
                ajouter_runs(p, contenu)
                stats["listes"] += 1
                index += 1
            continue

        # Paragraphe (regroupement des lignes consécutives)
        bloc = [depouillee]
        index += 1
        while index < len(lignes):
            suite = lignes[index].strip()
            if (not suite
                    or suite.startswith("#")
                    or suite.startswith("|")
                    or suite.startswith(">")
                    or suite.startswith("```")
                    or suite.startswith("$$")
                    or re.fullmatch(r"(\-\-\-|\*\*\*|___)\s*", suite)
                    or re.match(r"^(\s*)([-*+]|\d+\.)\s+", lignes[index])):
                break
            bloc.append(suite)
            index += 1

        if premier_titre_ignore and not premier_paragraphe_ignore:
            premier_paragraphe_ignore = True
            continue

        p = doc.add_paragraph()
        ajouter_runs(p, " ".join(bloc))
        stats["paragraphes"] += 1

    return stats


# --------------------------------------------------------------------------
# Programme principal
# --------------------------------------------------------------------------
def main() -> int:
    analyseur = argparse.ArgumentParser(description="Export Markdown -> Word du dossier APIX/PPC.")
    analyseur.add_argument("--only", default=None, help="Filtre sur le nom du fichier source.")
    analyseur.add_argument("--check", action="store_true", help="Analyse sans écrire de fichier.")
    arguments = analyseur.parse_args()

    selection = DOCUMENTS
    if arguments.only:
        selection = [d for d in DOCUMENTS if arguments.only.lower() in d["source"].lower()]
        if not selection:
            print(f"Aucun document ne correspond à « {arguments.only} ».", file=sys.stderr)
            return 1

    if not arguments.check:
        DOSSIER_SORTIE.mkdir(parents=True, exist_ok=True)

    total_erreurs = 0
    for entree in selection:
        source = RACINE / entree["source"]
        if not source.exists():
            print(f"[ERREUR] Source introuvable : {source}", file=sys.stderr)
            total_erreurs += 1
            continue

        doc = preparer_document()
        page_de_garde(doc, entree["titre"], entree["sous_titre"], source)
        stats = convertir(source, doc)

        if arguments.check:
            print(f"[OK] {entree['source']} — {stats}")
            continue

        destination = DOSSIER_SORTIE / entree["sortie"]
        doc.core_properties.title = entree["titre"]
        doc.core_properties.author = "FBB"
        doc.core_properties.subject = "Extension APIX — PPC"
        doc.save(destination)
        print(f"[OK] {destination.relative_to(RACINE)} — "
              f"{stats['titres']} titres, {stats['tableaux']} tableaux, "
              f"{stats['listes']} puces, {stats['paragraphes']} paragraphes, "
              f"{stats['images']} images")

    if total_erreurs:
        print(f"\n{total_erreurs} erreur(s).", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
