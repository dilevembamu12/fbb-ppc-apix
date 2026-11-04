#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
build_xlsx.py — Génération des classeurs de travail du dossier APIX / PPC.

Produit dans dist/xlsx :
    01-Backlog-APIX-Logistique.xlsx      épopées, récits, estimations, cycles
    02-Matrice-roles-droits.xlsx         droits par rôle et par fonction
    03-Grille-tarifaire-logistique.xlsx  référentiel d'axes et simulateur de prix
    04-Simulateur-groupage.xlsx          répartition des frais d'une course groupée

Toutes les valeurs chiffrées sont des propositions de travail marquées comme
telles. Elles doivent être remplacées par les données réelles de PPC.
"""

from __future__ import annotations

import sys
from pathlib import Path

from openpyxl import Workbook
from openpyxl.styles import Alignment, Border, Font, PatternFill, Side
from openpyxl.utils import get_column_letter
from openpyxl.worksheet.worksheet import Worksheet

RACINE = Path(__file__).resolve().parent.parent
SORTIE = RACINE / "dist" / "xlsx"

# --------------------------------------------------------------------------
# Charte de mise en forme
# --------------------------------------------------------------------------
BLEU = "1F3A5F"
BLEU_CLAIR = "E8EEF6"
CREME = "F7F4EC"
GRIS = "F2F2F2"
VERT = "E4EFDF"
ORANGE = "FBEDD9"

POLICE_TITRE = Font(name="Calibri", size=16, bold=True, color=BLEU)
POLICE_SOUS_TITRE = Font(name="Calibri", size=10, italic=True, color="555555")
POLICE_ENTETE = Font(name="Calibri", size=10, bold=True, color="FFFFFF")
POLICE_NORMALE = Font(name="Calibri", size=10)
POLICE_GRAS = Font(name="Calibri", size=10, bold=True)
POLICE_PETITE = Font(name="Calibri", size=9, italic=True, color="666666")

BORD_FIN = Side(style="thin", color="BFBFBF")
BORDURE = Border(left=BORD_FIN, right=BORD_FIN, top=BORD_FIN, bottom=BORD_FIN)

GAUCHE = Alignment(horizontal="left", vertical="top", wrap_text=True)
CENTRE = Alignment(horizontal="center", vertical="center", wrap_text=True)


# --------------------------------------------------------------------------
# Utilitaires
# --------------------------------------------------------------------------
def feuille_lecture(classeur: Workbook, titre: str, objet: str, source: str, points: list[str]) -> Worksheet:
    feuille = classeur.active
    feuille.title = "Lecture"
    feuille.sheet_view.showGridLines = False
    feuille["B2"] = titre
    feuille["B2"].font = POLICE_TITRE
    feuille["B4"] = objet
    feuille["B4"].font = POLICE_NORMALE
    feuille["B4"].alignment = GAUCHE
    feuille.merge_cells("B4:H8")
    feuille["B10"] = f"Document de référence : {source}"
    feuille["B10"].font = POLICE_PETITE
    feuille["B12"] = "Points d'attention"
    feuille["B12"].font = POLICE_GRAS
    ligne = 13
    for point in points:
        feuille.cell(row=ligne, column=2, value=f"•  {point}").font = POLICE_NORMALE
        feuille.cell(row=ligne, column=2).alignment = GAUCHE
        ligne += 1
    feuille.column_dimensions["A"].width = 2
    feuille.column_dimensions["B"].width = 110
    return feuille


def ecrire_entetes(feuille: Worksheet, ligne: int, entetes: list[str], largeurs: list[int]) -> None:
    for index, (entete, largeur) in enumerate(zip(entetes, largeurs), start=1):
        cellule = feuille.cell(row=ligne, column=index, value=entete)
        cellule.font = POLICE_ENTETE
        cellule.fill = PatternFill("solid", fgColor=BLEU)
        cellule.alignment = CENTRE
        cellule.border = BORDURE
        feuille.column_dimensions[get_column_letter(index)].width = largeur
    feuille.row_dimensions[ligne].height = 34


def ecrire_lignes(feuille: Worksheet, depart: int, lignes: list[list], zebre: bool = True) -> int:
    for decalage, contenu in enumerate(lignes):
        ligne = depart + decalage
        for index, valeur in enumerate(contenu, start=1):
            cellule = feuille.cell(row=ligne, column=index, value=valeur)
            cellule.font = POLICE_NORMALE
            cellule.alignment = GAUCHE
            cellule.border = BORDURE
            if zebre and decalage % 2 == 1:
                cellule.fill = PatternFill("solid", fgColor=GRIS)
    return depart + len(lignes)


def cadrer(feuille: Worksheet, ligne_entete: int, derniere_ligne: int, derniere_colonne: int) -> None:
    feuille.freeze_panes = feuille.cell(row=ligne_entete + 1, column=1)
    feuille.auto_filter.ref = (
        f"A{ligne_entete}:{get_column_letter(derniere_colonne)}{derniere_ligne}"
    )


# --------------------------------------------------------------------------
# 01 — Backlog
# --------------------------------------------------------------------------
EPOPEES = [
    ("E01", "Compte client et vérification d'identité", "M1", "MVP", "Permettre à tout client d'ouvrir un compte utilisable immédiatement, avec plafonds progressifs.", 30),
    ("E02", "Catalogue, prix et disponibilité", "M2", "MVP", "Afficher un prix fiable, daté et dépendant du profil et de la zone, jamais un prix non validé par PPC.", 22),
    ("E03", "Bon de commande certifié", "M3", "MVP", "Produire un document unique, nominatif, signé et non réutilisable, support de tous les jalons suivants.", 34),
    ("E04", "Paiement et séquestre", "M4", "MVP", "Encaisser de façon certaine, cantonner les fonds et ne les libérer que sur preuve ou décision.", 48),
    ("E05", "Enlèvement et chargement certifiés", "M5", "MVP", "Constater la remise physique au point de chargement et clôturer le bon définitivement.", 32),
    ("E06", "Transport, barème et affectation", "M6", "MVP", "Calculer un prix opposable, choisir un transporteur homologué compatible et organiser la course.", 52),
    ("E07", "Suivi, notifications et incidents", "M7", "MVP", "Donner au client la visibilité sur sa commande et à PPC la capacité de réagir avant le litige.", 30),
    ("E08", "Preuve de livraison et litiges", "M8", "MVP", "Rendre la livraison prouvable et le litige arbitrable sans parole contre parole.", 46),
    ("E09", "Historique, reçus et facturation", "M9", "MVP", "Donner au client la mémoire de ses achats et les pièces utiles à sa comptabilité.", 28),
    ("E10", "Portail transporteur et application chauffeur", "M10", "MVP", "Rendre les transporteurs partenaires plus rentables avec APIX qu'en dehors, et outiller les chauffeurs.", 56),
    ("E11", "Back-office PPC", "M11", "MVP", "Donner à PPC la main sur qui transporte, à quel prix, et comment se règlent les litiges.", 44),
    ("E12", "Groupage logistique", "M12", "V1", "Rendre livrable le client qui commande 20 sacs sans lui faire payer un camion.", 40),
    ("E13", "Socle technique et industrialisation", "Transverse", "MVP", "Sécurité, journal d'audit, hors-ligne, observabilité, environnements et déploiement.", 60),
]

RECITS = [
    # (code, épopée, libellé, priorité, estimation j·h, cycle, critère de recette)
    ("US-M1-01", "E01", "Création de compte par un particulier", "MVP", 5, "C1", "Compte créé après code à usage unique valide, plafond de premier niveau appliqué"),
    ("US-M1-02", "E01", "Vérification d'identité selon le profil", "MVP", 10, "C1", "Pièces exigées par profil, statut lisible, rejet motivé"),
    ("US-M1-03", "E01", "Profils de compte et plafonds paramétrables", "MVP", 8, "C1", "Dépassement bloqué avec message explicite et action proposée"),
    ("US-M1-04", "E01", "Utilisateurs rattachés à un compte entreprise", "V1", 7, "C4", "Rôles commandeur, approbateur, lecture seule opérationnels"),
    ("US-M2-01", "E02", "Consultation du catalogue", "MVP", 6, "C1", "Prix daté, dépendant du profil et de la zone, jamais de prix expiré"),
    ("US-M2-02", "E02", "Prix tout compris avant paiement", "MVP", 8, "C2", "Lignes séparées ciment / transport / annexes, chacune explicable"),
    ("US-M2-03", "E02", "Gestion du catalogue par PPC", "MVP", 8, "C1", "Publication versionnée, retrait sans effet sur les commandes payées"),
    ("US-M3-01", "E03", "Création d'un bon de commande", "MVP", 10, "C2", "Prix de transport figé à la création, expiration libérant le stock"),
    ("US-M3-02", "E03", "Certification du bon", "MVP", 12, "C2", "QR signé vérifiable hors ligne, code à 8 caractères, usage unique"),
    ("US-M3-03", "E03", "Modification d'un bon non payé", "MVP", 5, "C2", "Recalcul et réémission de version, blocage après paiement"),
    ("US-M3-04", "E03", "Trois options d'achat", "MVP", 7, "C2", "Option C en validation manuelle avec motif obligatoire"),
    ("US-M3-05", "E03", "Mandataire pour l'enlèvement", "MVP", 6, "C3", "Code d'enlèvement à usage unique transmis au mandataire"),
    ("US-M4-01", "E04", "Paiement par mobile money", "MVP", 14, "C3", "Deux opérateurs, confirmation sur notification authentifiée uniquement"),
    ("US-M4-02", "E04", "Paiement en espèces via agent agréé", "MVP", 10, "C3", "Référence de dépôt liée au bon, rapprochement tracé"),
    ("US-M4-03", "E04", "Séquestre et cantonnement", "MVP", 14, "C3", "Aucune libération sans fait générateur, écritures idempotentes"),
    ("US-M4-04", "E04", "Libération des fonds par jalons", "MVP", 10, "C4", "Matrice de libération respectée, pièce justificative générée"),
    ("US-M4-05", "E04", "Remboursement total ou partiel", "MVP", 9, "C4", "Remboursement sur moyen d'origine, délai affiché et suivi"),
    ("US-M5-01", "E05", "Contrôle du bon au chargement", "MVP", 8, "C3", "Bon invalide, expiré, utilisé ou hors point de chargement refusé avec motif"),
    ("US-M5-02", "E05", "Enregistrement du chargement", "MVP", 12, "C3", "Poids, sacs, scellé et photo obligatoires, validation superviseur hors tolérance"),
    ("US-M5-03", "E05", "Clôture du bon", "MVP", 5, "C3", "Toute nouvelle présentation refusée, notification client envoyée"),
    ("US-M6-01", "E06", "Calcul du prix de transport", "MVP", 14, "C2", "Calcul issu du barème PPC uniquement, explication en langage clair"),
    ("US-M6-02", "E06", "Choix de la zone de livraison", "MVP", 9, "C2", "Zone normalisée plus point de repère obligatoire, GPS optionnel"),
    ("US-M6-03", "E06", "Affectation d'un transporteur", "MVP", 16, "C4", "Transporteurs homologués et assurés uniquement, escalade après délai"),
    ("US-M6-04", "E06", "Typologie des engins", "MVP", 8, "C2", "Charge utile, caisse et gabarit contrôlés à l'affectation"),
    ("US-M6-05", "E06", "Feuille de route multi-arrêts", "V1", 12, "C5", "Ordre de chargement inverse de l'ordre de livraison"),
    ("US-M6-06", "E06", "Traitement des cas « Autre »", "MVP", 7, "C4", "Catalogue de cas paramétrés, dérogation nominative et limitée"),
    ("US-M7-01", "E07", "Suivi de la commande", "MVP", 8, "C4", "Quatre états lisibles, dernière position horodatée, jamais de position inventée"),
    ("US-M7-02", "E07", "Notifications multi-canal", "MVP", 9, "C4", "SMS, WhatsApp et notification applicative, traces d'envoi"),
    ("US-M7-03", "E07", "Déclaration d'incident", "MVP", 7, "C4", "Incident géant la libération automatique des fonds"),
    ("US-M7-04", "E07", "Repli SMS et USSD", "V2", 16, "C6", "Consultation de commande et d'état de livraison par menu USSD"),
    ("US-M8-01", "E08", "Validation de réception par le client", "MVP", 12, "C4", "QR de livraison plus contrôle de scellé, ouverture de litige immédiate si refus"),
    ("US-M8-02", "E08", "Dossier de preuve à plusieurs éléments", "MVP", 12, "C4", "Dossier téléchargeable en PDF avec empreinte d'intégrité"),
    ("US-M8-03", "E08", "Ouverture d'un litige", "MVP", 8, "C4", "Types de litige, gel des fonds concernés, numéro de dossier"),
    ("US-M8-04", "E08", "Instruction et décision de litige", "MVP", 14, "C5", "Décision motivée, montants retenu et libéré, notification des parties"),
    ("US-M8-05", "E08", "Litige partiel automatique sur écart de poids", "V1", 10, "C5", "Écart hors tolérance détecté, retenue calculée au prorata"),
    ("US-M9-01", "E09", "Historique des achats", "MVP", 8, "C4", "Filtres, export tableur, récapitulatif mensuel"),
    ("US-M9-02", "E09", "Reçu certifié vérifiable", "MVP", 8, "C4", "Vérification publique d'un reçu par son numéro"),
    ("US-M9-03", "E09", "Facture normalisée", "V1", 14, "C5", "Mentions fiscales complètes, connecteur validé par le conseil fiscal de PPC"),
    ("US-M9-04", "E09", "Estimation de stock pour un dépôt", "V2", 10, "C6", "Croisement achats / ventes déclarées et alerte de seuil"),
    ("US-M10-01", "E10", "Candidature d'un transporteur", "MVP", 12, "C3", "Pièces téléversées, échéances suivies, motif de rejet communiqué"),
    ("US-M10-02", "E10", "Réception et acceptation d'une course", "MVP", 12, "C4", "Acceptation ferme, contrôle de compatibilité d'engin"),
    ("US-M10-03", "E10", "Application chauffeur hors ligne", "MVP", 22, "C5", "Feuille de route et preuves disponibles 72 heures sans réseau"),
    ("US-M10-04", "E10", "Score de fiabilité transporteur", "V1", 10, "C5", "Détail des composantes visible par le transporteur"),
    ("US-M10-05", "E10", "Relevé des courses et paiements", "MVP", 8, "C5", "Statut de paiement explicite et export tableur"),
    ("US-M11-01", "E11", "Homologation d'un transporteur", "MVP", 12, "C3", "Décision motivée, durée de validité, révocation immédiate"),
    ("US-M11-02", "E11", "Publication du barème", "MVP", 14, "C2", "Simulation d'impact obligatoire avant publication, versions datées"),
    ("US-M11-03", "E11", "Tableau de bord de pilotage", "MVP", 12, "C5", "Indicateurs filtrables, comparaison à la période précédente"),
    ("US-M11-04", "E11", "File de traitement des litiges", "MVP", 8, "C5", "Dossier de preuve complet dans un seul écran"),
    ("US-M11-05", "E11", "Gestion des zones et des axes", "MVP", 8, "C2", "Coefficient de détour, points de rendez-vous, désactivation sans perte"),
    ("US-M12-01", "E12", "Proposition de groupage au client", "V1", 8, "C5", "Comparaison explicite camion dédié / groupage avec délais"),
    ("US-M12-02", "E12", "Constitution d'un lot", "V1", 14, "C5", "Compatibilité axe, produit, point de chargement, fenêtre"),
    ("US-M12-03", "E12", "Arbitrage à l'expiration du délai", "V1", 10, "C6", "Trois issues : engin plus petit, report jusqu'au remplissage, remboursement sur demande"),
    ("US-M12-04", "E12", "Répartition des frais mutualisés", "V1", 10, "C6", "Calcul au prorata poids × distance plus quote-part fixe"),
    ("US-M12-05", "E12", "Fiche de chargement ordonnée", "V1", 8, "C6", "Ordre de chargement inverse de la tournée, étiquettes par arrêt"),
    ("TR-01", "E13", "Journal d'audit en chaîne d'empreintes", "MVP", 12, "C1", "Toute action sensible journalisée, empreinte chaînée vérifiable"),
    ("TR-02", "E13", "Signature des bons et des preuves", "MVP", 10, "C2", "Génération et vérification hors ligne de la signature"),
    ("TR-03", "E13", "Abstraction des opérateurs de paiement", "MVP", 12, "C3", "Bascule de fournisseur sans changement métier"),
    ("TR-04", "E13", "Synchronisation hors ligne générique", "MVP", 16, "C3", "Files idempotentes, reprise sur acquittement, aucun doublon"),
    ("TR-05", "E13", "Observabilité et alertes", "MVP", 8, "C5", "Corrélation par commande, alertes sur commande payée non affectée"),
    ("TR-06", "E13", "Environnements et déploiement continu", "MVP", 10, "C1", "Recette et production isolées, retour arrière en une opération"),
]


def construire_backlog(chemin: Path) -> None:
    classeur = Workbook()
    feuille_lecture(
        classeur,
        "Backlog produit — Extension APIX (PPC)",
        "Ce classeur décrit le découpage de réalisation de la plateforme. Les épopées regroupent "
        "les récits utilisateurs par domaine métier ; les estimations sont exprimées en jours-homme "
        "et constituent des ordres de grandeur à recalibrer après le cadrage.",
        "docs/02-specifications-fonctionnelles.md",
        [
            "Les estimations supposent une équipe de 4 à 6 personnes (2 développeurs mobile, 2 développeurs back, 1 concepteur, 1 chef de produit à temps partiel).",
            "Les cycles C1 à C6 correspondent à des itérations de deux semaines ; le MVP couvre C1 à C5.",
            "Aucun récit n'intègre la charge de recette métier côté PPC, qui doit être planifiée séparément.",
            "Les récits marqués V1 et V2 ne sont pas nécessaires à la mise en service du pilote.",
        ],
    )

    feuille = classeur.create_sheet("Épopées")
    entetes = ["Code", "Épopée", "Module", "Priorité", "Objectif", "Estimation (jours-homme)", "Nombre de récits"]
    ecrire_entetes(feuille, 1, entetes, [8, 42, 10, 10, 70, 16, 12])
    lignes = [
        [code, libelle, module, priorite, objectif, estimation,
         sum(1 for r in RECITS if r[1] == code)]
        for code, libelle, module, priorite, objectif, estimation in EPOPEES
    ]
    derniere = ecrire_lignes(feuille, 2, lignes)
    total = sum(r[5] for r in lignes)
    feuille.cell(row=derniere, column=1, value="TOTAL").font = POLICE_GRAS
    feuille.cell(row=derniere, column=6, value=total).font = POLICE_GRAS
    feuille.cell(row=derniere, column=7, value=sum(r[6] for r in lignes)).font = POLICE_GRAS
    cadrer(feuille, 1, derniere - 1, len(entetes))

    feuille = classeur.create_sheet("Récits utilisateurs")
    entetes = ["Réf.", "Épopée", "Récit", "Priorité", "Estimation (jours-homme)", "Cycle proposé", "Critère de recette"]
    ecrire_entetes(feuille, 1, entetes, [12, 9, 46, 10, 16, 12, 66])
    lignes = [[code, epopee, libelle, priorite, estimation, cycle, recette]
              for code, epopee, libelle, priorite, estimation, cycle, recette in RECITS]
    derniere = ecrire_lignes(feuille, 2, lignes)
    total = sum(r[4] for r in lignes)
    feuille.cell(row=derniere, column=1, value="TOTAL").font = POLICE_GRAS
    feuille.cell(row=derniere, column=5, value=total).font = POLICE_GRAS
    cadrer(feuille, 1, derniere - 1, len(entetes))

    feuille = classeur.create_sheet("Charge par cycle")
    entetes = ["Cycle", "Périmètre", "Charge (jours-homme)", "Commentaire"]
    ecrire_entetes(feuille, 1, entetes, [12, 40, 20, 70])
    cycles = sorted({r[5] for r in RECITS})
    commentaires = {
        "C1": "Socle technique, comptes, catalogue : rien n'est visible par le client final.",
        "C2": "Bon de commande, barème, zones : première démonstration possible.",
        "C3": "Paiement, séquestre, homologation transporteurs, chargement.",
        "C4": "Affectation, suivi, livraison, historique : chaîne complète.",
        "C5": "Back-office, application chauffeur hors ligne, score, parcours de pilotage.",
        "C6": "Groupage et extensions : hors périmètre du pilote.",
    }
    lignes = []
    for cycle in cycles:
        charge = sum(r[4] for r in RECITS if r[5] == cycle)
        perimetre = "MVP" if cycle in {"C1", "C2", "C3", "C4", "C5"} else "V1 / V2"
        lignes.append([cycle, perimetre, charge, commentaires.get(cycle, "")])
    derniere = ecrire_lignes(feuille, 2, lignes)
    feuille.cell(row=derniere, column=1, value="TOTAL").font = POLICE_GRAS
    feuille.cell(row=derniere, column=3, value=sum(l[2] for l in lignes)).font = POLICE_GRAS
    cadrer(feuille, 1, derniere - 1, len(entetes))

    classeur.save(chemin)
    print(f"[OK] {chemin.relative_to(RACINE)}")


# --------------------------------------------------------------------------
# 02 — Matrice des rôles et des droits
# --------------------------------------------------------------------------
ROLES = [
    "Client final",
    "Transporteur partenaire",
    "Chauffeur",
    "Agent d'expédition PPC",
    "Administrateur PPC",
    "Contrôleur financier PPC",
    "Dépôt / point de retrait",
    "Super-administrateur APIX",
    "Banque partenaire",
]

# L = lecture, C = création, M = modification, V = validation ou décision, N = aucun droit
FONCTIONS = [
    ("Créer et gérer son compte client", ["C", "N", "N", "N", "L", "L", "C", "L", "N"]),
    ("Vérifier l'identité d'un client", ["N", "N", "N", "N", "V", "L", "N", "L", "L"]),
    ("Consulter le catalogue et les prix", ["L", "L", "N", "L", "M", "L", "L", "L", "N"]),
    ("Créer un bon de commande", ["C", "N", "N", "N", "N", "N", "C", "N", "N"]),
    ("Payer une commande", ["C", "N", "N", "N", "N", "N", "C", "N", "L"]),
    ("Annuler une commande payée", ["C", "N", "N", "N", "V", "V", "C", "N", "N"]),
    ("Simuler un tarif de transport", ["L", "L", "N", "L", "L", "L", "L", "L", "N"]),
    ("Publier un barème logistique", ["N", "N", "N", "N", "V", "L", "N", "L", "N"]),
    ("Gérer les zones et les axes", ["N", "N", "N", "N", "M", "L", "N", "L", "N"]),
    ("Gérer la typologie des engins", ["N", "N", "N", "N", "M", "L", "N", "L", "N"]),
    ("Déposer une candidature transporteur", ["N", "C", "N", "N", "L", "N", "N", "L", "N"]),
    ("Homologuer un transporteur", ["N", "N", "N", "N", "V", "L", "N", "L", "N"]),
    ("Révoquer une homologation", ["N", "N", "N", "N", "V", "L", "N", "L", "N"]),
    ("Publier une course", ["N", "N", "N", "N", "C", "N", "N", "N", "N"]),
    ("Accepter une course", ["N", "C", "N", "N", "N", "N", "N", "N", "N"]),
    ("Enregistrer un chargement", ["N", "N", "N", "C", "L", "N", "C", "L", "N"]),
    ("Enregistrer une preuve de livraison", ["C", "N", "C", "N", "L", "L", "N", "L", "N"]),
    ("Ouvrir un litige", ["C", "C", "N", "N", "C", "N", "C", "N", "N"]),
    ("Instruire un litige", ["N", "L", "N", "N", "V", "V", "N", "L", "N"]),
    ("Décider d'une libération de fonds", ["N", "N", "N", "N", "V", "V", "N", "L", "L"]),
    ("Déclencher un remboursement", ["N", "N", "N", "N", "V", "V", "N", "L", "L"]),
    ("Consulter le dossier de preuve complet", ["L", "L", "L", "L", "L", "L", "N", "L", "N"]),
    ("Exporter l'historique d'achat", ["C", "N", "N", "N", "L", "L", "C", "L", "N"]),
    ("Émettre une facture", ["N", "N", "N", "N", "C", "L", "N", "L", "N"]),
    ("Consulter le tableau de bord de pilotage", ["N", "L", "N", "L", "L", "L", "L", "L", "N"]),
    ("Consulter le journal d'audit", ["N", "N", "N", "N", "L", "L", "N", "L", "N"]),
    ("Gérer les comptes utilisateurs PPC", ["N", "N", "N", "N", "M", "N", "N", "L", "N"]),
    ("Définir les plafonds client", ["N", "N", "N", "N", "M", "L", "N", "L", "N"]),
    ("Gérer un lot de groupage", ["L", "L", "N", "L", "M", "L", "N", "L", "N"]),
    ("Superviser la plateforme et les intégrations", ["N", "N", "N", "N", "L", "N", "N", "M", "N"]),
]

LEGENDE = [
    ("C", "Création"),
    ("L", "Lecture"),
    ("M", "Modification ou paramétrage"),
    ("V", "Validation ou décision"),
    ("N", "Aucun droit"),
]


def construire_matrice(chemin: Path) -> None:
    classeur = Workbook()
    feuille_lecture(
        classeur,
        "Matrice des rôles et des droits",
        "Ce classeur fixe, fonction par fonction, ce que chaque acteur peut voir et faire. "
        "Il sert de référence unique pour la conception des interfaces et pour les tests d'habilitations.",
        "docs/01-note-de-cadrage.md (section 4) et docs/02-specifications-fonctionnelles.md",
        [
            "Le principe appliqué est le moindre privilège : un rôle ne reçoit que ce qui lui est strictement nécessaire.",
            "Un transporteur ne voit jamais les données d'un autre transporteur ; un dépôt ne voit que ses propres clients.",
            "La consultation du journal d'audit est elle-même journalisée.",
            "Toute décision financière au-delà du seuil paramétré exige une double validation.",
        ],
    )

    feuille = classeur.create_sheet("Matrice")
    feuille["A1"] = "Fonction"
    feuille["A1"].font = POLICE_ENTETE
    feuille["A1"].fill = PatternFill("solid", fgColor=BLEU)
    feuille["A1"].alignment = CENTRE
    feuille["A1"].border = BORDURE
    feuille.column_dimensions["A"].width = 46

    for index, role in enumerate(ROLES, start=2):
        cellule = feuille.cell(row=1, column=index, value=role)
        cellule.font = POLICE_ENTETE
        cellule.fill = PatternFill("solid", fgColor=BLEU)
        cellule.alignment = CENTRE
        cellule.border = BORDURE
        feuille.column_dimensions[get_column_letter(index)].width = 13
    feuille.row_dimensions[1].height = 44

    couleurs = {"C": "DCE9F5", "L": "FFFFFF", "M": "FBEDD9", "V": "E4EFDF", "N": "F2F2F2"}

    ligne = 2
    for fonction, droits in FONCTIONS:
        cellule = feuille.cell(row=ligne, column=1, value=fonction)
        cellule.font = POLICE_NORMALE
        cellule.alignment = GAUCHE
        cellule.border = BORDURE
        for index, droit in enumerate(droits, start=2):
            cellule = feuille.cell(row=ligne, column=index, value=droit)
            cellule.font = POLICE_GRAS
            cellule.alignment = CENTRE
            cellule.border = BORDURE
            cellule.fill = PatternFill("solid", fgColor=couleurs.get(droit, "FFFFFF"))
        ligne += 1

    feuille.freeze_panes = "B2"
    feuille.auto_filter.ref = f"A1:{get_column_letter(len(ROLES) + 1)}{ligne - 1}"

    feuille = classeur.create_sheet("Légende")
    ecrire_entetes(feuille, 1, ["Code", "Signification"], [10, 60])
    ecrire_lignes(feuille, 2, [[code, sens] for code, sens in LEGENDE])

    classeur.save(chemin)
    print(f"[OK] {chemin.relative_to(RACINE)}")


# --------------------------------------------------------------------------
# 03 — Grille tarifaire et simulateur
# --------------------------------------------------------------------------
AXES = [
    # (code, origine, destination, distance km, coefficient détour, coût fixe USD, coût tonne-km USD, observation)
    ("AX-01", "Usine de Kimpese", "Kinshasa (zone urbaine)", 200, 1.00, 180, 0.055, "Hypothèse de travail : point de chargement principal à confirmer par PPC"),
    ("AX-02", "Usine de Kimpese", "Matadi", 160, 1.00, 150, 0.052, "Axe court, forte fréquence"),
    ("AX-03", "Usine de Kimpese", "Boma", 180, 1.08, 165, 0.054, "Coefficient de détour à valider"),
    ("AX-04", "Usine de Kimpese", "Mbanza-Ngungu", 60, 1.00, 90, 0.058, "Axe de proximité"),
    ("AX-05", "Usine de Kimpese", "Kikwit", 530, 1.12, 420, 0.062, "Route nationale, tronçons dégradés"),
    ("AX-06", "Usine de Kimpese", "Mbandaka", 600, 1.20, 520, 0.066, "Option fluviale à évaluer en V2"),
    ("AX-07", "Usine de Kimpese", "Kananga", 940, 1.15, 780, 0.068, "Longue distance, majoration d'immobilisation"),
    ("AX-08", "Usine de Kimpese", "Lubumbashi", 1900, 1.20, 1500, 0.072, "Traversée du pays, à valider"),
]

ENGINS = [
    # (code, libellé, charge utile kg, type de caisse, coefficient tarifaire)
    ("EN-01", "Camionnette fourgon 3,5 t", 3500, "Fourgon bâché", 1.25),
    ("EN-02", "Porteur 10 t plateau", 10000, "Plateau", 1.00),
    ("EN-03", "Porteur 15 t bâché", 15000, "Bâché", 0.95),
    ("EN-04", "Semi-remorque 30 t bâché", 30000, "Bâché", 0.88),
    ("EN-05", "Semi-remorque 34 t plateau", 34000, "Plateau", 0.86),
    ("EN-06", "Benne 20 t", 20000, "Benne", 0.92),
    ("EN-07", "Triporteur dernier kilomètre", 750, "Plateau ouvert", 1.60),
]


def construire_grille(chemin: Path) -> None:
    classeur = Workbook()
    feuille_lecture(
        classeur,
        "Grille tarifaire logistique et simulateur",
        "Ce classeur fournit un référentiel d'axes et d'engins, ainsi qu'un simulateur de prix "
        "appliquant la formule retenue : (coût fixe de l'axe + coût à la tonne-kilomètre × poids × distance) "
        "× coefficient de saison × coefficient de détour.",
        "annexes/regles-de-gestion.md (RG-TAR-01 à RG-TAR-10)",
        [
            "Toutes les distances et tous les montants de cet onglet sont des propositions de travail : ils doivent être remplacés par les données de PPC.",
            "Le coût fixe de l'axe n'est pas multiplié par le poids : il correspond aux frais engagés dès qu'un camion part.",
            "Le barème doit être versionné et daté ; une commande conserve le barème en vigueur à sa certification.",
            "Aucune saisie de prix libre n'est admise, ni par le client, ni par le transporteur.",
        ],
    )

    feuille = classeur.create_sheet("Axes")
    entetes = ["Code axe", "Origine", "Destination", "Distance (km)",
               "Coefficient de détour", "Coût fixe de l'axe (USD)", "Coût à la tonne-kilomètre (USD)",
               "Observation"]
    ecrire_entetes(feuille, 1, entetes, [10, 22, 26, 14, 18, 18, 20, 52])
    lignes = [list(a) for a in AXES]
    derniere = ecrire_lignes(feuille, 2, lignes)
    for ligne in range(2, derniere):
        feuille.cell(row=ligne, column=4).number_format = "#,##0"
        feuille.cell(row=ligne, column=5).number_format = "0.00"
        feuille.cell(row=ligne, column=6).number_format = '"$"#,##0.00'
        feuille.cell(row=ligne, column=7).number_format = '"$"0.000'
    cadrer(feuille, 1, derniere - 1, len(entetes))

    feuille = classeur.create_sheet("Engins")
    entetes = ["Code engin", "Libellé", "Charge utile (kg)", "Type de caisse",
               "Coefficient tarifaire", "Observation"]
    ecrire_entetes(feuille, 1, entetes, [12, 34, 18, 22, 18, 46])
    lignes = [list(e) + ["Coefficient appliqué au coût variable ; à valider par PPC"] for e in ENGINS]
    derniere = ecrire_lignes(feuille, 2, lignes)
    for ligne in range(2, derniere):
        feuille.cell(row=ligne, column=3).number_format = "#,##0"
        feuille.cell(row=ligne, column=5).number_format = "0.00"
    cadrer(feuille, 1, derniere - 1, len(entetes))

    feuille = classeur.create_sheet("Simulateur")
    feuille.sheet_view.showGridLines = False
    feuille["B2"] = "Simulateur de prix de transport"
    feuille["B2"].font = POLICE_TITRE
    feuille["B3"] = "Modifier les valeurs des colonnes C et D ; les colonnes F à J se recalculent automatiquement."
    feuille["B3"].font = POLICE_SOUS_TITRE

    entetes = ["Code axe", "Poids (tonnes)", "Coefficient de saison", "Coefficient de détour",
               "Coût fixe (USD)", "Coût tonne-km (USD)", "Distance (km)", "Coût variable (USD)",
               "Coût transport (USD)", "Prix par tonne (USD)"]
    for index, entete in enumerate(entetes, start=2):
        cellule = feuille.cell(row=5, column=index, value=entete)
        cellule.font = POLICE_ENTETE
        cellule.fill = PatternFill("solid", fgColor=BLEU)
        cellule.alignment = CENTRE
        cellule.border = BORDURE
        feuille.column_dimensions[get_column_letter(index)].width = 18
    feuille.row_dimensions[5].height = 40

    exemples = [
        ("AX-01", 10, 1.00, 1.00),
        ("AX-01", 30, 1.00, 1.00),
        ("AX-01", 2, 1.10, 1.00),
        ("AX-05", 15, 1.10, 1.12),
        ("AX-05", 30, 1.00, 1.12),
        ("AX-07", 30, 1.00, 1.15),
    ]

    ligne = 6
    for code, poids, saison, detour in exemples:
        feuille.cell(row=ligne, column=2, value=code)
        feuille.cell(row=ligne, column=3, value=poids)
        feuille.cell(row=ligne, column=4, value=saison)
        feuille.cell(row=ligne, column=5, value=detour)
        # Le tableau Axes est organisé ainsi : A code, B origine, C destination,
        # D distance, E coefficient de détour, F coût fixe, G coût à la tonne-kilomètre.
        feuille.cell(row=ligne, column=6, value=f'=VLOOKUP($B{ligne},Axes!$A$2:$G${len(AXES)+1},6,FALSE)')
        feuille.cell(row=ligne, column=7, value=f'=VLOOKUP($B{ligne},Axes!$A$2:$G${len(AXES)+1},7,FALSE)')
        feuille.cell(row=ligne, column=8, value=f'=VLOOKUP($B{ligne},Axes!$A$2:$G${len(AXES)+1},4,FALSE)')
        feuille.cell(row=ligne, column=9, value=f'=ROUND($G{ligne}*$H{ligne}*$C{ligne},2)')
        feuille.cell(row=ligne, column=10, value=f'=ROUND(($F{ligne}+$I{ligne})*$D{ligne}*$E{ligne},2)')
        feuille.cell(row=ligne, column=11, value=f'=IF($C{ligne}>0,ROUND($J{ligne}/$C{ligne},2),0)')
        formats = {
            3: "0.00",       # poids en tonnes
            4: "0.00",       # coefficient de saison
            5: "0.00",       # coefficient de détour
            6: '"$"#,##0.00',  # coût fixe
            7: '"$"0.000',   # coût à la tonne-kilomètre
            8: "#,##0",      # distance
            9: '"$"#,##0.00',  # coût variable
            10: '"$"#,##0.00',  # coût transport
            11: '"$"#,##0.00',  # prix par tonne
        }
        for colonne in range(2, 12):
            cellule = feuille.cell(row=ligne, column=colonne)
            cellule.font = POLICE_NORMALE
            cellule.border = BORDURE
            cellule.alignment = CENTRE
            if colonne in formats:
                cellule.number_format = formats[colonne]
        ligne += 1

    feuille.cell(row=ligne + 2, column=2,
                 value="Rappel : le prix par tonne baisse quand le camion est plein. C'est ce que le groupage exploite.")
    feuille.cell(row=ligne + 2, column=2).font = POLICE_PETITE
    feuille.cell(row=ligne + 3, column=2,
                 value="Le prix par sac s'obtient en divisant le prix par tonne par 20 (sac de 50 kg).")
    feuille.cell(row=ligne + 3, column=2).font = POLICE_PETITE

    classeur.save(chemin)
    print(f"[OK] {chemin.relative_to(RACINE)}")


# --------------------------------------------------------------------------
# 04 — Simulateur de groupage
# --------------------------------------------------------------------------
def construire_groupage(chemin: Path) -> None:
    classeur = Workbook()
    feuille_lecture(
        classeur,
        "Simulateur de répartition des frais de groupage",
        "Ce classeur montre comment les frais d'une course groupée sont répartis entre plusieurs petits "
        "acheteurs. Il applique la règle RG-GRP-07 : répartition au prorata du poids multiplié par la "
        "distance parcourue, complétée par une quote-part des frais fixes au prorata du poids.",
        "annexes/regles-de-gestion.md (RG-GRP-01 à RG-GRP-14)",
        [
            "Le principe : chacun paie ce qu'il consomme effectivement en transport, sans subventionner les autres.",
            "La composante fixe est indispensable : sans elle, les gros acheteurs financent les petits.",
            "Le détail du calcul doit rester consultable par le client, avant et après paiement.",
            "En cas de modification de la composition du lot, le recalcul doit être affiché et accepté.",
            "Comparer avec la ligne « camion dédié » pour démontrer l'économie au client final.",
        ],
    )

    feuille = classeur.create_sheet("Simulation")
    feuille.sheet_view.showGridLines = False

    feuille["B2"] = "Paramètres de la course groupée"
    feuille["B2"].font = POLICE_TITRE

    parametres = [
        ("Axe de référence", "AX-01 — Usine de Kimpese vers Kinshasa", None),
        ("Coût total de la course (USD)", 900, '"$"#,##0.00'),
        ("dont frais fixes de la course (USD)", 250, '"$"#,##0.00'),
        ("Poids d'un sac (tonnes)", 0.05, "0.000"),
        ("Capacité du camion (tonnes)", 30, "0"),
        ("Seuil de déclenchement du lot", 0.85, "0%"),
    ]
    ligne = 4
    for libelle, valeur, format_nombre in parametres:
        feuille.cell(row=ligne, column=2, value=libelle).font = POLICE_GRAS
        cellule = feuille.cell(row=ligne, column=3, value=valeur)
        cellule.font = POLICE_NORMALE
        cellule.fill = PatternFill("solid", fgColor=CREME)
        cellule.border = BORDURE
        if format_nombre:
            cellule.number_format = format_nombre
        ligne += 1

    feuille.column_dimensions["A"].width = 2
    feuille.column_dimensions["B"].width = 40
    feuille.column_dimensions["C"].width = 42

    depart = 12
    entetes = ["Client", "Zone de livraison", "Distance depuis l'usine (km)", "Sacs commandés",
               "Poids (tonnes)", "Poids × distance", "Part du coût variable", "Quote-part des frais fixes",
               "Total à payer (USD)", "Prix par sac (USD)"]
    for index, entete in enumerate(entetes, start=2):
        cellule = feuille.cell(row=depart, column=index, value=entete)
        cellule.font = POLICE_ENTETE
        cellule.fill = PatternFill("solid", fgColor=BLEU)
        cellule.alignment = CENTRE
        cellule.border = BORDURE
        largeur = 26 if index == 2 else 16
        if index == 3:
            largeur = 30
        feuille.column_dimensions[get_column_letter(index)].width = largeur
    feuille.row_dimensions[depart].height = 46

    clients = [
        ("Dépôt Ngaliema", "Kinshasa — Ngaliema", 205, 60),
        ("Chantier Limete", "Kinshasa — Limete", 212, 200),
        ("Dépôt Matete", "Kinshasa — Matete", 218, 120),
        ("Artisan Kintambo", "Kinshasa — Kintambo", 208, 20),
        ("Dépôt Masina", "Kinshasa — Masina", 225, 120),
    ]

    premiere = depart + 1
    derniere = premiere + len(clients) - 1

    ligne = premiere
    for nom, zone, distance, sacs in clients:
        feuille.cell(row=ligne, column=2, value=nom)
        feuille.cell(row=ligne, column=3, value=zone)
        feuille.cell(row=ligne, column=4, value=distance)
        feuille.cell(row=ligne, column=5, value=sacs)
        # Rappel des colonnes de la grille : D = distance depuis l'usine, E = sacs commandés,
        # F = poids total, G = poids × distance, H = part du coût variable,
        # I = quote-part des frais fixes, J = total à payer, K = prix par sac.
        feuille.cell(row=ligne, column=6, value=f"=ROUND(E{ligne}*$C$7,4)")
        feuille.cell(row=ligne, column=7, value=f"=ROUND(F{ligne}*D{ligne},2)")
        feuille.cell(row=ligne, column=8,
                     value=f"=IF($G${derniere+1}=0,0,ROUND(($C$5-$C$6)*G{ligne}/$G${derniere+1},2))")
        feuille.cell(row=ligne, column=9, value=f"=IF($F${derniere+1}=0,0,ROUND($C$6*F{ligne}/$F${derniere+1},2))")
        feuille.cell(row=ligne, column=10, value=f"=ROUND(H{ligne}+I{ligne},2)")
        feuille.cell(row=ligne, column=11, value=f"=IF(E{ligne}>0,ROUND(J{ligne}/E{ligne},2),0)")
        for colonne in range(2, 12):
            cellule = feuille.cell(row=ligne, column=colonne)
            cellule.font = POLICE_NORMALE
            cellule.border = BORDURE
            cellule.alignment = CENTRE if colonne > 3 else GAUCHE
            format_colonne = {
                4: "#,##0",          # distance depuis l'usine
                5: "0",              # sacs commandés
                6: "0.00",           # poids total en tonnes
                7: "#,##0.00",       # poids × distance
                8: '"$"#,##0.00',    # part du coût variable
                9: '"$"#,##0.00',    # quote-part des frais fixes
                10: '"$"#,##0.00',   # total à payer
                11: '"$"#,##0.00',   # prix par sac
            }.get(colonne)
            if format_colonne:
                cellule.number_format = format_colonne
        ligne += 1

    # Ligne de totaux
    total = derniere + 1
    feuille.cell(row=total, column=2, value="TOTAL DU LOT").font = POLICE_GRAS
    for colonne, formule in (
        (5, f"=SUM(E{premiere}:E{derniere})"),
        (6, f"=ROUND(SUM(F{premiere}:F{derniere}),4)"),
        (7, f"=ROUND(SUM(G{premiere}:G{derniere}),2)"),
        (8, f"=ROUND(SUM(H{premiere}:H{derniere}),2)"),
        (9, f"=ROUND(SUM(I{premiere}:I{derniere}),2)"),
        (10, f"=ROUND(SUM(J{premiere}:J{derniere}),2)"),
    ):
        cellule = feuille.cell(row=total, column=colonne, value=formule)
        cellule.font = POLICE_GRAS
        cellule.number_format = '"$"#,##0.00' if colonne >= 8 else "#,##0.00"
    for colonne in range(2, 12):
        cellule = feuille.cell(row=total, column=colonne)
        cellule.border = BORDURE
        cellule.fill = PatternFill("solid", fgColor=BLEU_CLAIR)
        cellule.alignment = CENTRE if colonne > 3 else GAUCHE

    # Contrôles
    controle = total + 2
    feuille.cell(row=controle, column=2, value="Contrôles").font = POLICE_GRAS
    feuille.cell(row=controle + 1, column=2, value="Somme répartie = coût total de la course ?")
    feuille.cell(row=controle + 1, column=3,
                 value=f'=IF(ABS(J{total}-$C$5)<0.01,"Oui — répartition juste","Non — écart de "&TEXT(J{total}-$C$5,"0.00")&" USD")')
    feuille.cell(row=controle + 2, column=2, value="Taux de remplissage du camion")
    feuille.cell(row=controle + 2, column=3, value=f"=F{total}/$C$8")
    feuille.cell(row=controle + 2, column=3).number_format = "0%"
    feuille.cell(row=controle + 3, column=2, value="Le lot est-il déclenchable ?")
    feuille.cell(row=controle + 3, column=3,
                 value=f'=IF(F{total}/$C$8>=$C$9,"Oui — seuil atteint","Non — il manque "&TEXT(ROUND(($C$9*$C$8-F{total})/$C$7,0),"0")&" sacs")')

    for ligne_controle in range(controle, controle + 4):
        feuille.cell(row=ligne_controle, column=2).font = POLICE_GRAS
    for ligne_controle in range(controle + 1, controle + 4):
        feuille.cell(row=ligne_controle, column=2).font = POLICE_NORMALE
        feuille.cell(row=ligne_controle, column=3).font = POLICE_NORMALE
        feuille.cell(row=ligne_controle, column=3).fill = PatternFill("solid", fgColor=VERT)

    # Comparaison avec un camion dédié
    comparaison = controle + 6
    feuille.cell(row=comparaison, column=2, value="Comparaison avec un camion dédié").font = POLICE_GRAS
    feuille.cell(row=comparaison + 1, column=2, value="Coût d'un camion dédié au même axe (USD)")
    feuille.cell(row=comparaison + 1, column=3, value=900).number_format = '"$"#,##0.00'
    feuille.cell(row=comparaison + 1, column=3).fill = PatternFill("solid", fgColor=CREME)
    feuille.cell(row=comparaison + 1, column=3).border = BORDURE

    feuille.cell(row=comparaison + 3, column=2, value="Client")
    feuille.cell(row=comparaison + 3, column=3, value="Coût en camion dédié (USD)").font = POLICE_GRAS
    feuille.cell(row=comparaison + 3, column=4, value="Coût en groupage (USD)").font = POLICE_GRAS
    feuille.cell(row=comparaison + 3, column=5, value="Économie (USD)").font = POLICE_GRAS
    feuille.cell(row=comparaison + 3, column=6, value="Économie (%)").font = POLICE_GRAS
    for colonne in range(2, 7):
        cellule = feuille.cell(row=comparaison + 3, column=colonne)
        cellule.font = POLICE_ENTETE
        cellule.fill = PatternFill("solid", fgColor=BLEU)
        cellule.border = BORDURE
        cellule.alignment = CENTRE

    for decalage in range(len(clients)):
        source = premiere + decalage
        cible = comparaison + 4 + decalage
        feuille.cell(row=cible, column=2, value=f"=B{source}")
        feuille.cell(row=cible, column=3, value=f"=ROUND($C${comparaison+1},2)")
        feuille.cell(row=cible, column=4, value=f"=J{source}")
        feuille.cell(row=cible, column=5, value=f"=ROUND(C{cible}-D{cible},2)")
        feuille.cell(row=cible, column=6, value=f"=IF(C{cible}>0,ROUND(E{cible}/C{cible},3),0)")
        for colonne in range(2, 7):
            cellule = feuille.cell(row=cible, column=colonne)
            cellule.font = POLICE_NORMALE
            cellule.border = BORDURE
            cellule.alignment = CENTRE if colonne > 2 else GAUCHE
            if colonne in (3, 4, 5):
                cellule.number_format = '"$"#,##0.00'
            elif colonne == 6:
                cellule.number_format = "0.0%"

    feuille.cell(row=comparaison + 5 + len(clients), column=2,
                 value="Note de lecture : dans le scénario d'un camion dédié, chaque client supporte le coût "
                       "entier d'un camion pour sa seule commande. Le groupage divise ce coût par le nombre "
                       "d'acheteurs du lot, ce qui rend livrable une commande de 10 sacs.")
    feuille.cell(row=comparaison + 5 + len(clients), column=2).font = POLICE_PETITE

    classeur.save(chemin)
    print(f"[OK] {chemin.relative_to(RACINE)}")


# --------------------------------------------------------------------------
# Programme principal
# --------------------------------------------------------------------------
def main() -> int:
    SORTIE.mkdir(parents=True, exist_ok=True)
    try:
        construire_backlog(SORTIE / "01-Backlog-APIX-Logistique.xlsx")
        construire_matrice(SORTIE / "02-Matrice-roles-droits.xlsx")
        construire_grille(SORTIE / "03-Grille-tarifaire-logistique.xlsx")
        construire_groupage(SORTIE / "04-Simulateur-groupage.xlsx")
    except Exception as erreur:  # noqa: BLE001
        print(f"[ERREUR] {erreur}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
