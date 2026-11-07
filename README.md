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
├── assets/
│   ├── images/                    photographies de la présentation (licences libres)
│   └── credits.json               auteur, licence et page source de chaque image
├── outils/
│   ├── build_docs.py              export Markdown -> Word (.docx)
│   ├── build_xlsx.py              génération des classeurs de travail (.xlsx)
│   ├── build_pptx.py              génération de la présentation détaillée (.pptx, 22 diapos)
│   ├── build_pptx_reunion.py      génération de la version réunion (.pptx, 12 diapos + annexes)
│   ├── build_fiche.py             fiche A4 à remettre à PPC (une page, à compléter)
│   ├── fetch_images.py            récupération des images libres (Wikimedia Commons)
│   └── requirements.txt
└── dist/                          livrables générés (créé par les scripts)
    ├── docs/
    ├── xlsx/
    └── pptx/
```

---

## 4. Régénérer les livrables

```powershell
cd 'e:\DILEVE\DILEVE\BUSINESS\PROJECTS\FBB\PPC'
python -m pip install -r outils\requirements.txt
python outils\fetch_images.py    # -> assets/images/*.jpg (une seule fois, ou --force)
python outils\build_docs.py      # -> dist/docs/*.docx
python outils\build_xlsx.py      # -> dist/xlsx/*.xlsx
python outils\build_pptx_reunion.py   # -> dist/pptx/*12-slides*.pptx
python outils\build_pptx.py      # -> dist/pptx/*Presentation*.pptx
python outils\build_fiche.py     # -> dist/docs/F1-Fiche-cadrage-reglement-PPC.docx
python outils\build_web.py       # -> dist/web/index.html (+ images)
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
| `dist/docs/05-Presentation-MVP-interfaces.docx` | 8 interfaces, 53 écrans, 4 parcours, recette du MVP | Conception, développement, recette |
| `dist/docs/A1-Regles-de-gestion.docx` | Règles numérotées et paramètres | Métier, développement, juridique |
| `dist/docs/A2-Questions-ouvertes-PPC.docx` | Questions et décisions attendues | Chef de projet |
| `dist/xlsx/01-Backlog-APIX-Logistique.xlsx` | 13 épopées, 60 récits estimés, charge par cycle | Planification |
| `dist/xlsx/02-Matrice-roles-droits.xlsx` | 30 fonctions × 9 rôles | Sécurité et conception des écrans |
| `dist/xlsx/03-Grille-tarifaire-logistique.xlsx` | Référentiel d'axes, engins, simulateur de prix | Atelier barème avec PPC |
| `dist/xlsx/04-Simulateur-groupage.xlsx` | Répartition des frais d'une course groupée | Démonstration client |
| `dist/pptx/APIX-All-In-One-12-slides-PPC.pptx` | **Version réunion** : 12 diapositives + 6 annexes (règle 10/20/30) | Rendez-vous avec la direction générale |
| `dist/pptx/APIX-All-In-One-Presentation-PPC.pptx` | Version détaillée : 22 diapositives | Dossier de fond, réunion technique |
| `dist/docs/F1-Fiche-cadrage-reglement-PPC.docx` | Fiche A4 d'une page : cinq questions sur le règlement des transporteurs, à compléter par PPC | À laisser en fin de réunion |

> Les valeurs numériques des classeurs (distances, coûts, seuils) sont des **propositions de travail** à remplacer par les données de PPC.

### Présentation commerciale « APIX All In One »

Deux fichiers, deux usages :

| Version | Script | Format | Usage |
|---|---|---|---|
| Réunion | `outils/build_pptx_reunion.py` | 12 diapositives + 6 annexes | 20 minutes, règle 10/20/30 de Guy Kawasaki |
| Détaillée | `outils/build_pptx.py` | 22 diapositives | Dossier de fond, questions techniques |

Séquence de la version réunion — les douleurs d'abord, le produit ensuite :

| # | Diapositive | Fonction |
|---|---|---|
| 1 | APIX All In One | Accroche |
| 2 | Le paiement est certifié. La marchandise, non. | Problème, quatre questions sans réponse |
| 3 | Trois fuites qui coûtent, sans figurer dans aucun rapport | Coût de l'inaction |
| 4 | Il n'achète pas une application. Il achète une certitude. | Marché et cible |
| 5 | La chaîne de preuve, en six jalons | Solution |
| 6 | Partout où le client se trouve | Ubiquité et maquettes |
| 7 | Le client paie PPC. Le transporteur est payé sur preuve. | Circuit de l'argent |
| 8 | Quatre éléments, un seul dossier | Preuve de livraison, photo géolocalisée |
| 9 | Le transport cesse d'être un forfait | Barème et calculateur |
| 10 | Cinq petits acheteurs, un seul camion | Groupage |
| 11 | Deux approches, deux natures différentes | Concurrence |
| 12 | PPC garde la main — cinq décisions | Souveraineté et appel à l'action |

Annexes : A1 modèle économique, A2 équipe, A3 feuille de route, A4 arbitrage du groupage, A5 preuve et litige, A6 socle technique. À n'ouvrir que sur question.

Points communs :

- **Chaque diapositive porte des notes de présentation** : ce qu'il faut dire, et parfois ce qu'il ne faut pas dire.
- **Aucun chiffre de marché n'est inventé.** Les seuls montants sont la simulation de groupage et l'exemple de barème, présentés comme tels et recalculables dans les classeurs.
- **Les maquettes d'interface** (client, chauffeur, back-office, calculateur) sont dessinées avec des formes natives. Aucune capture d'écran tierce n'est utilisée : les visuels des produits commerciaux repérés sur les places de marché sont sous copyright et leurs noms ne doivent pas apparaître dans nos documents.
- **Les wireframes du document 05** sont dessinés en Python avec Pillow (`outils/build_wireframes.py`) et produits dans `assets/wireframes/` : dix planches, niveaux de gris, orange réservé à l'action principale. Le convertisseur Word les insère via la syntaxe `![légende|largeur_cm](chemin)`, et les bascules d'orientation se font avec les marqueurs `:::paysage` / `:::portrait`.
- **Les photographies** proviennent de Wikimedia Commons (Creative Commons ou domaine public). La dernière diapositive crédite les auteurs ; le détail (auteur, licence, page source) est dans `assets/credits.json`, généré par `outils/fetch_images.py`.
- Pour changer une photographie, modifier le titre du fichier dans `THEMES` (`fetch_images.py`), supprimer le fichier dans `assets/images/`, puis relancer le script. Les textes et la mise en page se règlent dans le script de construction ; les constantes de charte sont en tête de `build_pptx.py`.
- **La diapositive « Équipe » reste à compléter** avec les noms et références réelles avant toute présentation.


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

---

## 8. Version web publiée

**URL :** <https://dilevembamu12.github.io/fbb-ppc-apix/>

Le site est servi depuis la branche `gh-pages` (racine : `index.html`, `images/`, `.nojekyll`), activée dans *Settings → Pages*.

### Mise à jour du site

```powershell
python outils\build_web.py
# puis recopier dist/web vers la branche gh-pages
```

La branche `gh-pages` est régénérée à partir de `dist/web` ; elle ne contient que le site, jamais les sources.

### Basculer public / privé

Points à connaître :

- **Un site GitHub Pages est toujours public.** L'accès restreint aux collaborateurs n'existe qu'en offre Enterprise.
- **Sur un compte gratuit, Pages n'est pas disponible pour un dépôt privé.** Le dépôt est donc `public` tant que le site doit être accessible.
- Conséquence utile : repasser le dépôt en privé **désactive le site automatiquement** (il renvoie 404). Une seule commande protège donc à la fois le code et la présentation.

```powershell
# Publier (repo public, site accessible)
gh repo edit dilevembamu12/fbb-ppc-apix --visibility public --accept-visibility-change-consequences

# Repasser en privé (le site passe hors ligne)
gh repo edit dilevembamu12/fbb-ppc-apix --visibility private --accept-visibility-change-consequences

# Vérifier
gh repo view dilevembamu12/fbb-ppc-apix --json visibility
gh api repos/dilevembamu12/fbb-ppc-apix/pages --jq '.html_url'
```

> **Attention :** rendre le dépôt public expose **tout son historique**, y compris les documents internes (note de cadrage, argumentaire, questions ouvertes, simulations). Pas seulement la présentation.

