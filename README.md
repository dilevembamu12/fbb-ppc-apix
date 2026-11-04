# Extension APIX — Plateforme Clients Finaux & Logistique Ciment (PPC)

> **Maître d'ouvrage :** FBB — concepteur d'APIX
> **Client cible :** PPC (cimentier, République Démocratique du Congo)
> **Concurrent identifié :** **Digiciment** (application de petites transactions + module logistique léger)
> **Statut :** Cadrage — version 1.0
> **Date :** 4 novembre 2026

---

## 1. Objet du dossier

Ce dossier formalise l'extension d'**APIX** (aujourd'hui plateforme de certification des transactions de paiement CIMA sur les comptes PPC) vers une **plateforme complète de commande, de paiement et de logistique du ciment**, destinée :

1. aux **clients finaux de PPC** (dépôts et revendeurs, entreprises et chantiers, particuliers) ;
2. aux **transporteurs partenaires** homologués par PPC (flotte tierce, et non flotte propre PPC) ;
3. aux **équipes administratives PPC** (homologation, barèmes, litiges, pilotage).

L'objectif stratégique est double : **verrouiller la relation PPC ↔ client final** et **rendre APIX indispensable** face à Digiciment, en unifiant sur une seule chaîne la finance certifiée et la logistique physique.

---

## 2. Sommaire des livrables

| Réf. | Document | Contenu | Public visé |
|---|---|---|---|
| 00 | [Synthèse exécutive](docs/00-synthese-executive.md) | Le problème, la proposition, les décisions à prendre | Direction PPC / FBB |
| 01 | [Note de cadrage](docs/01-note-de-cadrage.md) | Revue critique, périmètre, acteurs, risques, jalons, KPI | Comité de pilotage |
| 02 | [Spécifications fonctionnelles](docs/02-specifications-fonctionnelles.md) | 12 modules, récits utilisateurs, critères d'acceptation | Produit, métier PPC, développement |
| 03 | [Architecture technique](docs/03-architecture-technique.md) | Vue d'ensemble, stack, données, API, hors-ligne, sécurité | Direction technique, DSI PPC |
| 04 | [Argumentaire commercial](docs/04-argumentaire-commercial.md) | Positionnement, grille comparative, objections, modèle économique | Direction commerciale FBB |
| A1 | [Règles de gestion](annexes/regles-de-gestion.md) | Règles numérotées et opposables (paiement, groupage, litiges) | Métier, développement, juridique |
| A2 | [Questions ouvertes PPC](annexes/questions-ouvertes-ppc.md) | Points à trancher avec PPC avant engagement | Chef de projet |

---

## 3. Arborescence du dépôt

```
PPC/
├── README.md                      ce fichier (index du dossier)
├── docs/                          livrables rédigés en Markdown (source de vérité)
│   ├── 00-synthese-executive.md
│   ├── 01-note-de-cadrage.md
│   ├── 02-specifications-fonctionnelles.md
│   ├── 03-architecture-technique.md
│   └── 04-argumentaire-commercial.md
├── annexes/
│   ├── regles-de-gestion.md
│   └── questions-ouvertes-ppc.md
├── outils/
│   ├── build_docs.py              export Markdown -> Word (.docx)
│   ├── build_xlsx.py              génération des classeurs de travail (.xlsx)
│   └── requirements.txt
└── dist/                          livrables générés (créé par les scripts)
```

---

## 4. Régénérer les livrables

```powershell
cd 'e:\DILEVE\DILEVE\BUSINESS\PROJECTS\FBB\PPC'
python -m pip install -r outils\requirements.txt
python outils\build_docs.py      # -> dist/docs/*.docx
python outils\build_xlsx.py      # -> dist/xlsx/*.xlsx
```

Options utiles :

```powershell
python outils\build_docs.py --only 01        # un seul document
python outils\build_docs.py --check          # vérifie les tableaux Markdown sans écrire
```

### Livrables générés

| Fichier produit | Contenu | Usage |
|---|---|---|
| `dist/docs/00-Synthese-executive.docx` | Synthèse pour décideur | Réunion de direction |
| `dist/docs/01-Note-de-cadrage.docx` | Cadrage complet et revue critique | Comité de pilotage |
| `dist/docs/02-Specifications-fonctionnelles.docx` | 12 modules, récits, critères de recette | Équipe produit et développement |
| `dist/docs/03-Architecture-technique.docx` | Architecture, données, sécurité | Direction technique |
| `dist/docs/04-Argumentaire-commercial.docx` | Positionnement et objections | Direction commerciale |
| `dist/docs/A1-Regles-de-gestion.docx` | Règles numérotées et paramètres | Métier, développement, juridique |
| `dist/docs/A2-Questions-ouvertes-PPC.docx` | Questions et décisions attendues | Chef de projet |
| `dist/xlsx/01-Backlog-APIX-Logistique.xlsx` | 13 épopées, 60 récits estimés, charge par cycle | Planification |
| `dist/xlsx/02-Matrice-roles-droits.xlsx` | 30 fonctions × 9 rôles | Sécurité et conception des écrans |
| `dist/xlsx/03-Grille-tarifaire-logistique.xlsx` | Référentiel d'axes, engins, simulateur de prix | Atelier barème avec PPC |
| `dist/xlsx/04-Simulateur-groupage.xlsx` | Répartition des frais d'une course groupée | Démonstration client |

> Les valeurs numériques des classeurs (distances, coûts, seuils) sont des **propositions de travail** à remplacer par les données de PPC.


---

## 5. Conventions du dossier

- **Langue :** français. Les noms de champs, codes et identifiants techniques sont écrits **sans accents**.
- **Codes de règles :** chaque règle de gestion porte un identifiant stable (`RG-PAY-03`), citable en réunion et traçable dans le code.
- **Tableaux :** en-têtes et légendes explicites, codes complets, sigles systématiquement explicités. Un tableau doit être lisible sans commentaire oral.
- **Hypothèses :** toute valeur non confirmée par PPC est marquée `[À VALIDER PPC]`.

---

## 6. Avertissement

Les éléments financiers, tarifaires, réglementaires et de conformité contenus dans ce dossier sont des **propositions de travail**. Ils ne valent pas avis juridique ni engagement contractuel. Les distances, coûts et délais doivent être confirmés par PPC et par ses conseils (juridique, fiscal, bancaire) avant toute mise en production.

---

## 7. Versionnement

Dépôt distant : **`https://github.com/dilevembamu12/fbb-ppc-apix`** (privé, branche par défaut `main`).
La branche `main` locale suit `origin/main` ; un `git push` suffit donc à publier.

Aucune identité git n'étant configurée sur le poste au moment de l'initialisation, une **identité locale provisoire** a été posée (`FBB Data Science <fbb@local>`). Elle ne concerne que ce dépôt et n'affecte pas la configuration de la machine. Pour la remplacer par la vraie identité :

```powershell
cd 'e:\DILEVE\DILEVE\BUSINESS\PROJECTS\FBB\PPC'
git config --local user.name "Nom Prénom"
git config --local user.email "prenom.nom@fbb.example"
git commit --amend --reset-author --no-edit
git push --force-with-lease
```

Les fichiers de `dist/` sont versionnés volontairement, car ils constituent le livrable présenté à PPC. Pour alléger le dépôt, décommenter la ligne `# dist/` dans `.gitignore`.

