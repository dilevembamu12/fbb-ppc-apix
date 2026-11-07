# 05 — Présentation du MVP et de ses interfaces

**Extension APIX — Plateforme Clients Finaux & Logistique Ciment**
FBB pour PPC · pièce jointe au dossier « Extension APIX », version 1.0

> Convention : `IF-xx` désigne une interface, `CLI-xx`, `WCL-xx`, `CHF-xx`, `TRP-xx`, `CHG-xx`, `BKO-xx`, `DEP-xx` et `EXP-xx` un écran, `US-xx-yy` un récit utilisateur (document 02), `RG-…` une règle de gestion (annexe A1), `Q-xx` une question ouverte à trancher avec PPC (annexe A2).

> **Statut du document.** Il décrit ce que chaque acteur voit, saisit et déclenche. Il ne remplace ni les spécifications fonctionnelles détaillées (document 02) ni les règles de gestion (annexe A1) : il les met en scène, écran par écran. En cas de divergence, le document 02 fait foi sur le comportement attendu, l'annexe A1 sur les règles opposables, et le présent document sur la présentation.

---

## 1. Ce que ce document tranche, et ce qu'il ne tranche pas

| Sujet | Traité ici | Référence |
|---|---|---|
| Comportement fonctionnel détaillé de chaque module | Non | Document 02 — Spécifications fonctionnelles |
| Règles opposables et paramètres à valider | Non | Annexe A1 — Règles de gestion |
| Découpage en interfaces, inventaire des écrans | **Oui** | Sections 3 et 4 |
| Parcours de bout en bout, écran par écran | **Oui** | Section 5 |
| Contraintes de terrain et conséquences ergonomiques | **Oui** | Section 7 |
| Charte graphique détaillée (couleurs, typographies, composants) | Non | Livrée avec les maquettes de la présentation commerciale |
| Choix technologiques d'implémentation | Non | Document 03 — Architecture technique |

---

## 2. Périmètre du MVP

### 2.1 La définition retenue

Le MVP n'est pas un prototype de démonstration. C'est **la plus petite chaîne complète qui produise une preuve opposable de bout en bout, pour un client réel, avec de l'argent réel** : de la création du compte jusqu'au reçu, en passant par la cotation, l'encaissement, le chargement et la livraison prouvée.

Trois conséquences directes :

1. Tout ce qui ne produit pas de preuve est reporté, même si c'est visible et séduisant.
2. Tout ce qui permet de contourner une preuve est interdit dans l'interface, y compris dans le back-office.
3. Un écran qui ne sert qu'un seul cas marginal n'entre pas dans le MVP : le cas marginal passe par une décision tracée de PPC.

### 2.2 Ce qui est dans le MVP

| Jalon de la chaîne de preuve | Ce que l'acteur peut faire | Interfaces concernées | Modules |
|---|---|---|---|
| **J1 — Compte et vérification d'identité** | Ouvrir un compte avec un numéro vérifié, déposer ses pièces, connaître son plafond | IF-01, IF-02, IF-06 | M1 |
| **J2 — Cotation certifiée** | Consulter les prix de son profil, demander une cotation numérotée et datée, la recevoir avec sa durée de validité | IF-01, IF-02, IF-06 | M2, M3 |
| **J3 — Paiement encaissé** | Payer en référençant la cotation, voir les canaux compatibles avec le montant, suivre la confirmation | IF-01, IF-02, IF-06 | M4 |
| **J4 — Bon de commande émis** | Recevoir un bon nominatif à usage unique avec QR signé, le présenter au chargement | IF-01, IF-02, IF-05 | M3, M5 |
| **J5 — Chargement et transport** | Contrôler le bon, enregistrer poids, sacs et scellé, publier et suivre la course | IF-03, IF-04, IF-05 | M5, M6, M7, M10 |
| **J6 — Livraison prouvée** | Valider la réception sur son téléphone, produire le dossier de preuve, ouvrir un litige si nécessaire | IF-01, IF-03, IF-06 | M8 |
| **J7 — Reçu et historique** | Retrouver ses commandes, télécharger un reçu vérifiable | IF-01, IF-02 | M9 |

> Les présentations commerciales n'affichent que les six premiers jalons : le septième est documentaire, il ne produit pas de preuve de terrain mais il conditionne la comptabilité du client.

### 2.3 Ce qui est explicitement hors MVP

| Élément écarté | Pourquoi il est écarté du MVP | Version cible | Ce que l'interface prévoit déjà |
|---|---|---|---|
| Groupage logistique | Dépend de la constitution de lots, donc d'un volume réel ; ne sert à rien sur les premiers clients | V1 | L'écran de choix d'option annonce « groupage à venir » plutôt que de le simuler |
| WhatsApp Business | Exige un compte marchand validé et une modération de messages | V1 | Les services sont exposés sans état d'écran, pour être branchés sur un canal conversationnel |
| Commande par USSD et repli SMS | Dépend d'un opérateur et d'un menu à faire valider | V2 | Les libellés d'état sont courts et numérotables (`1` à `6`), réutilisables en menu USSD |
| Chatbot avec intelligence artificielle locale | PPC n'a pas arbitré entre IA locale et menus numérotés | V1 | Le parcours est déjà une suite de questions fermées, donc jouable en menus numérotés |
| Facture normalisée | Exige un connecteur fiscal validé par le conseil fiscal de PPC | V1 | Le reçu certifié occupe la place, avec les mêmes numéros de pièce |
| Score de fiabilité transporteur | Sans historique, le score n'a aucune valeur | V1 | Le portail affiche les courses et les règlements, pas encore de note |
| Feuille de route multi-arrêts | Suppose le groupage | V1 | La feuille de route accepte une liste d'arrêts, à un seul élément au MVP |
| Litige partiel automatique sur écart de poids | L'écart ouvre un litige manuel au MVP ; l'automatisation vient après stabilisation de la tolérance | V1 | L'écran de réception affiche déjà l'écart calculé et le compare à la tolérance |
| Utilisateurs rattachés à un compte entreprise | Les premiers clients sont des particuliers et des dépôts mono-utilisateur | V1 | Le modèle de compte prévoit plusieurs utilisateurs et trois rôles |
| Estimation de stock d'un dépôt | Suppose un historique de ventes déclarées | V2 | Rien n'est affiché : mieux vaut pas d'estimation qu'une estimation fausse |
| Agrégateur de paiement (Araka ou banque agrégateur) | Décision commerciale non prise, frais non négociés | À trancher | L'écran de paiement liste des canaux, pas des fournisseurs : le choix reste invisible au client |

### 2.4 Les trois options d'achat et leur effet sur les écrans

| Option | Ce que le client voit | Écrans supplémentaires | Ce qui n'existe pas dans cette option |
|---|---|---|---|
| **Option A — Enlèvement** | Le prix du ciment seul, la mention « vous organisez le transport », un bon de sortie nominatif | Le code d'enlèvement du mandataire (CLI-11) | Aucune course, aucune provision de transport, aucun suivi de position |
| **Option B — Transport par PPC** | Le prix du ciment, le prix du transport calculé au barème, le total | Le suivi de course (CLI-12), la validation de réception (CLI-13) | Aucune souplesse sur l'itinéraire : la zone est choisie avant la cotation |
| **Option C — Cas particulier** | Un message explicite : « votre demande est étudiée par PPC » | Aucun écran client supplémentaire | Aucun prix affiché tant que PPC n'a pas validé |

> L'option C n'est pas un fourre-tout : elle sert à ne pas perdre une commande réelle dont le cas n'est pas encore paramétré. Elle exige une dérogation nominative, motivée et limitée dans le temps (RG-TAR-08).

---

## 3. Les huit interfaces

### 3.1 Vue d'ensemble

| Code | Interface | Acteur(s) | Support | Mode | Écrans | Modules servis |
|---|---|---|---|---|---|---|
| **IF-01** | Application client | AC-CLI — client final PPC | Android et iOS | En ligne, avec reprise hors coupure | 16 | M1 à M4, M7 à M9 |
| **IF-02** | Web client | AC-CLI — client final équipé d'un poste | Navigateur, mise en page large | En ligne | 16 repris + 3 propres | M1 à M4, M9 |
| **IF-03** | Application chauffeur | AC-CHF — chauffeur du transporteur | Android | **Hors ligne d'abord**, 72 heures | 8 | M5, M7, M8, M10 |
| **IF-04** | Portail transporteur | AC-TRP — transporteur partenaire | Navigateur | En ligne | 5 | M6, M10 |
| **IF-05** | Console de chargement | AC-EXP — agent d'expédition PPC | Navigateur, tablette au point de chargement | **Hors ligne toléré** | 5 | M5 |
| **IF-06** | Back-office PPC | AC-ADM — administrateur, AC-FIN — contrôleur financier | Navigateur, écran large | En ligne | 10 | M2, M3, M4, M6, M8, M11 |
| **IF-07** | Console dépôt | AC-DEP — dépôt ou point de retrait agréé | Navigateur, tablette ou téléphone | En ligne | 3 | M5, M9 |
| **IF-08** | Console d'exploitation APIX | AC-FBB — super-administrateur | Navigateur | En ligne | 3 | Transverse |

Total : **53 écrans**, dont 16 mutualisés entre l'application et le web client.

> L'interface bancaire (AC-BNK) n'est pas une interface utilisateur : c'est une intégration. Elle n'apparaît donc pas dans cet inventaire, mais elle conditionne trois écrans (CLI-09, CLI-10, BKO-06).

### 3.2 Principes communs aux huit interfaces

1. **Aucun prix sans identité.** Un visiteur non identifié ne voit ni grille, ni total, ni même un ordre de grandeur (RG-COT-01).
2. **Un écran, un objectif, une action principale.** Si un écran demande deux décisions, il est coupé en deux.
3. **Trois états obligatoires** : chargement, vide, erreur. Un écran vide explique ce qu'il faut faire pour le remplir ; un écran en erreur propose une action, jamais un code technique (RF-TR-04).
4. **Des identifiants lisibles.** Une cotation s'appelle `COT-2026-000123`, un bon `BON-2026-000456`, un litige `LIT-2026-000012`. Le client peut les dicter au téléphone.
5. **Une couleur par état**, partout la même : brouillon, valide, expiré, payé, en cours, litige, clos.
6. **Le canal ne décide de rien.** L'interface n'affiche que les canaux capables d'encaisser le montant, dès la création de la cotation (RG-PAY-14).
7. **Rien ne se supprime.** Toute action produit un événement ; une correction référence l'événement précédent au lieu de l'effacer.
8. **Le hors-ligne est un mode normal**, pas une panne : file d'attente visible, estampille locale conservée et estampille serveur ajoutée à la réception (RG-CHG-06, RG-POD-07).
9. **Le back-office est soumis aux mêmes règles que le terrain.** Un administrateur ne peut pas créer un bon sans cotation, ni saisir un prix hors barème sans dérogation nominative.
10. **Terminologie validée par PPC** (RF-TR-03) : « cotation », « bon de commande », « point de chargement », « dépôt ». Aucun anglicisme dans l'interface.
11. **Cibles tactiles de 44 points minimum**, contraste conforme, taille de police adaptable (RF-TR-05 pour le niveau renforcé).
12. **Aucune donnée personnelle superflue** : le numéro de téléphone est la clé d'usage, l'adresse électronique est facultative.

### 3.3 Correspondance avec les canaux demandés par PPC

| Canal | Statut au MVP | Ce qui est prévu | Condition de mise en service |
|---|---|---|---|
| Application Android | **MVP** | Application complète, mode économie de données | Validation des maquettes par PPC |
| Application iOS | **MVP** | Même périmètre fonctionnel | Compte développeur Apple de PPC |
| Web client (navigateur) | **MVP** | Même parcours, mise en page large, export tableur | — |
| Notifications SMS | **MVP** | Envoi sortant sur changement d'état et sur décision de litige | Contrat passerelle SMS de PPC |
| Courriel | **MVP** | Reçu et dossier de preuve en pièce jointe | — |
| WhatsApp Business | V1 | Cotation, paiement et bon depuis une conversation | Compte marchand validé, modèles de messages approuvés |
| USSD | V2 | Consultation de l'état d'une commande, sans internet | Ouverture d'un code court auprès de chaque opérateur |
| Telegram | Non retenu | — | Canal sans base installée chez les clients de PPC |
| Chatbot avec IA locale | V1 | Interprétation d'une demande en langage libre, avec repli sur menus numérotés | Arbitrage de PPC sur l'hébergement de l'IA |

---

## 4. Fiches d'interface

### 4.1 IF-01 — Application client (Android et iOS)

**Acteur :** AC-CLI, client final PPC (particulier, entreprise ou chantier, dépôt ou revendeur).
**Objectif :** obtenir un prix ferme, payer, et détenir une preuve — sans appeler personne.
**Mode :** en ligne ; les écrans de consultation restent lisibles après une coupure, les actions sont rejouées au retour du réseau.

| Écran | Nom | Ce que le client y fait | Point de contrôle |
|---|---|---|---|
| CLI-01 | Ouverture de session par numéro | Saisit son numéro, reçoit un code à usage unique | Code valable 5 minutes, 3 tentatives (RG-KYC-01) |
| CLI-02 | Création de compte | Choisit son profil, renseigne son nom ou sa raison sociale | Trois profils seulement (RG-KYC-02) |
| CLI-03 | Vérification d'identité | Photographie ses pièces, suit le statut de la vérification | Pièces différentes selon le profil (RG-KYC-04) |
| CLI-04 | Catalogue et prix | Consulte les produits disponibles et son prix | **Aucun prix** pour un compte non vérifié au-delà du premier niveau |
| CLI-05 | Quantité et destination | Choisit la quantité, la zone de livraison et un point de repère | Zone normalisée obligatoire, GPS facultatif |
| CLI-06 | Choix de l'option | Choisit entre enlèvement, transport PPC et cas particulier | Option C sans prix affiché |
| CLI-07 | Demande de cotation | Vérifie le détail ligne par ligne avant de demander la cotation | Lignes ciment, transport et annexes séparées (RG-COT-03) |
| CLI-08 | Cotation certifiée | Lit le numéro, la date, la durée de validité et le total | Compte à rebours visible ; cotation expirée non payable (RG-COT-05) |
| CLI-09 | Choix du moyen de paiement | Sélectionne un canal compatible avec le montant | Seuls les canaux capables d'encaisser sont proposés (RG-PAY-14) |
| CLI-10 | Attente et confirmation | Suit la confirmation émise par l'établissement | Confirmation sur notification authentifiée uniquement (RG-PAY-01) |
| CLI-11 | Bon de commande | Affiche le QR signé, le détail et le code d'enlèvement | Bon nominatif et à usage unique (RG-CMD-04, RG-CMD-05) |
| CLI-12 | Suivi de la commande | Voit l'état, la dernière position horodatée et le transporteur | Jamais de position inventée : l'absence de position est affichée comme telle |
| CLI-13 | Réception | Valide la quantité, l'état et le scellé à l'arrivée | Écart hors tolérance ou scellé rompu : litige immédiat (RG-POD-04, RG-POD-05) |
| CLI-14 | Dossier de preuve et litige | Télécharge le dossier, ouvre ou consulte un litige | Déclaration possible 48 heures après livraison (RG-LIT-02) |
| CLI-15 | Historique et reçus | Filtre ses commandes, télécharge un reçu vérifiable | Reçu vérifiable par son numéro (US-M9-02) |
| CLI-16 | Profil et plafonds | Consulte son palier, ses limites et ses pièces | Montée de palier par vérification, jamais par dérogation orale (RG-PAY-19) |

**Garde-fous de cette interface**

- Aucun écran ne permet de créer un bon de commande : le bon naît de la cotation encaissée (RG-CMD-01).
- Aucun écran n'affiche un prix pour un visiteur anonyme, y compris l'écran d'accueil et le comparateur de zones.
- L'écran de paiement ne peut pas être atteint sans cotation valide : le bouton n'est pas masqué, il est expliqué (RG-PAY-21).
- Le fractionnement d'une commande pour passer sous un plafond est refusé avec un message qui propose le virement (RG-PAY-16, RG-PAY-15).
- Un refus d'opérateur est présenté comme une alternative de canal, jamais comme une panne (RG-PAY-20).

### 4.2 IF-02 — Web client

**Acteur :** AC-CLI travaillant depuis un poste fixe — dépôts, entreprises de construction, services achats.
**Objectif :** le même parcours que l'application, avec la densité d'information d'un écran large.

L'interface reprend les seize écrans `CLI-01` à `CLI-16` en mise en page large. Trois écrans n'existent qu'en web :

| Écran | Nom | Ce que le client y fait | Point de contrôle |
|---|---|---|---|
| WCL-01 | Commande en série | Saisit ou importe une liste de lignes de commande | Chaque ligne produit sa propre cotation ; aucune cotation groupée implicite |
| WCL-02 | Export de l'historique | Exporte commandes, reçus et litiges au format tableur | Export horodaté et signé, pour la comptabilité du client |
| WCL-03 | Utilisateurs du compte | Ajoute des utilisateurs et leur donne un rôle | Rôles commandeur, approbateur, lecture seule ; version V1 du récit US-M1-04 |

### 4.3 IF-03 — Application chauffeur

**Acteur :** AC-CHF, chauffeur d'un transporteur homologué.
**Objectif :** exécuter la course et produire les preuves de chargement et de livraison, même sans réseau.
**Mode :** **hors ligne d'abord**. La feuille de route et les preuves restent disponibles 72 heures ; tout est transmis au retour du réseau (US-M10-03).

| Écran | Nom | Ce que le chauffeur y fait | Point de contrôle |
|---|---|---|---|
| CHF-01 | Connexion | Se connecte une fois en ligne, puis travaille hors ligne | Session locale chiffrée, expiration à 72 heures |
| CHF-02 | Mes courses | Voit les courses acceptées, en cours et terminées | Trois onglets, un seul geste par course |
| CHF-03 | Détail de la course | Lit l'adresse, le point de repère, le contact et la fenêtre de livraison | Le numéro de téléphone du client est le seul contact autorisé |
| CHF-04 | Chargement | Scanne le bon, saisit le poids, les sacs et le scellé, photographie | Quatre champs obligatoires, photo et ticket de pesée (RG-CHG-02, RG-CHG-05) |
| CHF-05 | Route et événements | Signale un départ, un incident, une arrivée | Positions horodatées localement puis côté serveur (RG-CHG-06) |
| CHF-06 | Livraison | Fait flasher le QR du client, prend la photo géolocalisée, fait signer | La validation appartient au client, jamais au chauffeur (RG-POD-01) |
| CHF-07 | Synchronisation | Voit la file d'opérations en attente et relance l'envoi | Aucune preuve perdue, aucune duplication (RG-PAY-02) |
| CHF-08 | Relevé des courses | Consulte les courses de la période et leur statut de paiement | Statut explicite, sans montant de marge |

**Garde-fous de cette interface**

- Le chauffeur ne peut pas clôturer une livraison sans la validation du client sur son propre téléphone : c'est la protection contre l'auto-certification.
- Le chauffeur ne voit ni le prix payé par le client, ni la marge du transporteur.
- Un écart de poids hors tolérance ne peut pas être validé par le chauffeur : il déclenche une demande de validation superviseur (RG-CHG-03).

### 4.4 IF-04 — Portail transporteur

**Acteur :** AC-TRP, entreprise de transport tierce.
**Objectif :** recevoir des courses compatibles avec sa flotte, les accepter d'un geste, et suivre ses règlements.

| Écran | Nom | Ce que le transporteur y fait | Point de contrôle |
|---|---|---|---|
| TRP-01 | Candidature et pièces | Dépose ses documents d'entreprise, d'assurance et ses engins | Échéances suivies, motif de rejet communiqué (US-M10-01) |
| TRP-02 | Tableau de bord | Voit les courses proposées, acceptées, livrées, à régler | Filtres par axe et par période |
| TRP-03 | Course proposée | Lit le détail et accepte ou refuse | Seuls les engins homologués sont proposés ; acceptation ferme (RG-AFF-06) |
| TRP-04 | Chauffeurs et engins | Déclare ses chauffeurs et ses engins, met à jour les pièces | Charge utile, type de caisse et gabarit contrôlés (RG-AFF-02) |
| TRP-05 | Relevé et règlements | Consulte les courses et leur statut de règlement, exporte | Aucune date de règlement affichée tant que PPC ne l'a pas arrêtée |

**Garde-fous de cette interface**

- Un transporteur dont l'homologation ou l'assurance est expirée ne reçoit plus de course, mais une course en cours n'est pas interrompue (RG-AFF-01, RG-AFF-07).
- Le désistement est possible et tracé : il réduit le score de fiabilité (V1) plutôt que d'être bloqué.

### 4.5 IF-05 — Console de chargement

**Acteur :** AC-EXP, agent d'expédition PPC au point de chargement (usine ou dépôt).
**Objectif :** certifier la remise physique en moins de 90 secondes par camion, sans jamais laisser sortir un bon invalide.

| Écran | Nom | Ce que l'agent y fait | Point de contrôle |
|---|---|---|---|
| CHG-01 | File du point de chargement | Voit les bons attendus pour son point, dans l'ordre d'arrivée | Aucun bon d'un autre point de chargement (RG-CMD-08) |
| CHG-02 | Contrôle du bon | Scanne le QR et obtient un verdict immédiat | Bon invalide, expiré, déjà utilisé : refus motivé (RG-CHG-01) |
| CHG-03 | Enregistrement du chargement | Saisit poids réel, nombre de sacs, numéro de scellé, photo | Écart hors tolérance : validation superviseur obligatoire (RG-CHG-03) |
| CHG-04 | Clôture | Clôture le bon et remet le bon de sortie | Clôture irréversible (RG-CHG-04) |
| CHG-05 | Journal du poste | Consulte les dernières opérations de son poste | Traçable par agent, horodaté, non modifiable |

**Garde-fous de cette interface**

- L'écran de contrôle n'affiche jamais le prix payé : l'agent n'a pas à connaître le montant de la transaction.
- Un bon déjà chargé ne peut pas être rouvert ; l'écran propose de créer un litige, pas de corriger.
- Aucune saisie libre de poids n'est acceptée sans photo du ticket de pesée.

### 4.6 IF-06 — Back-office PPC

**Acteurs :** AC-ADM, administrateur PPC ; AC-FIN, contrôleur financier.
**Objectif :** garder la main sur qui transporte, à quel prix, comment se règlent les litiges, et ne jamais laisser une écriture sans justification.

| Écran | Nom | Ce que l'utilisateur PPC y fait | Point de contrôle |
|---|---|---|---|
| BKO-01 | Tableau de bord de pilotage | Suit commandes, encaissements, courses, litiges et délais | Indicateurs filtrables, comparaison à la période précédente (US-M11-03) |
| BKO-02 | Catalogue et prix | Publie produits, prix et disponibilités | Publication versionnée, retrait sans effet sur les commandes payées |
| BKO-03 | Zones, axes et barème | Définit zones, axes et coefficients, publie le barème | **Simulation d'impact obligatoire** avant publication (RG-TAR-02) |
| BKO-04 | Transporteurs | Homologue, renouvelle, révoque | Décision motivée, durée de validité, révocation immédiate (US-M11-01) |
| BKO-05 | Paiements sans cotation | Rattrape un paiement arrivé sans cotation | Aucune affectation d'office, motif et trace obligatoires (RG-COT-07) |
| BKO-06 | Provisions et règlements du transport | Instruit les règlements sur preuve, applique les retenues | Aucun règlement sans fait générateur (RG-PAY-05) |
| BKO-07 | File des litiges | Instruit le dossier complet sur un seul écran | Décision motivée : sens, montant retenu, montant libéré (RG-LIT-05) |
| BKO-08 | Comptes clients | Consulte profils, paliers et plafonds, valide les cas sensibles | Validation des profils sensibles, jamais de plafond saisi hors palier |
| BKO-09 | Journal d'audit | Recherche une action, un dossier, un agent | Écriture en ajout seul, conservée dix ans |
| BKO-10 | Utilisateurs PPC et annuaire | Gère les accès internes par annuaire d'entreprise | Connexion par annuaire, aucun mot de passe local (US-M11-06) |

**Garde-fous de cette interface**

- Le back-office ne propose aucune action « créer un bon de commande » : la seule voie est l'encaissement (RG-CMD-01).
- Le contrôleur financier voit les provisions et les règlements, mais ne peut ni publier un barème, ni homologuer un transporteur.
- L'écran de litige affiche le dossier de preuve complet avant toute décision : impossible de trancher à l'aveugle.

### 4.7 IF-07 — Console dépôt

**Acteur :** AC-DEP, dépôt ou point de retrait agréé.
**Objectif :** servir un bon enlèvement sans jamais en accepter deux fois le même.

| Écran | Nom | Ce que l'agent du dépôt y fait | Point de contrôle |
|---|---|---|---|
| DEP-01 | Réception d'un bon | Scanne le bon de sortie et remet la marchandise | Bon à usage unique, contrôle du point de chargement autorisé |
| DEP-02 | File du dépôt | Voit les bons attendus et ceux déjà servis | Un bon servi disparaît de la file |
| DEP-03 | Historique du dépôt | Consulte les remises de la journée ou du mois | Trace par agent, export possible |

### 4.8 IF-08 — Console d'exploitation APIX

**Acteur :** AC-FBB, super-administrateur APIX.
**Objectif :** exploiter la plateforme sans jamais toucher aux fonds ni aux décisions de PPC.

| Écran | Nom | Ce que l'exploitant FBB y fait | Point de contrôle |
|---|---|---|---|
| EXP-01 | Supervision | Suit la santé des intégrations bancaires, des files et des envois | Alerte sur file bloquée ou intégration muette |
| EXP-02 | Configuration | Règle paramètres techniques, canaux, plafonds par canal | Les plafonds sont saisis, jamais codés en dur (RG-PAY-13) |
| EXP-03 | Support | Recherche un dossier, rejoue une opération en toute sécurité | Rejeu idempotent, aucune écriture financière manuelle possible (RG-PAY-02) |

**Garde-fous de cette interface**

- Aucun écran FBB ne permet de modifier un montant, un bon ou une décision de litige.
- Toute action de support laisse une trace visible par PPC.

---

## 5. Parcours de bout en bout

### 5.1 Parcours nominal — commande avec transporteur

| Étape | Acteur | Écran | Ce qu'il fait | Preuve produite |
|---|---|---|---|---|
| 1 | Client | CLI-01 à CLI-03 | Crée son compte et fait vérifier son identité | Compte identifié, palier et plafond |
| 2 | Client | CLI-04, CLI-05 | Consulte les prix de son profil, choisit quantité et zone | — |
| 3 | Client | CLI-06, CLI-07 | Choisit le transport PPC, vérifie le détail tout compris | — |
| 4 | Client | CLI-08 | Reçoit la cotation numérotée, datée, valable 48 heures | **Cotation certifiée** |
| 5 | Client | CLI-09 | Paie en référençant la cotation | Ordre de paiement portant le numéro de cotation |
| 6 | Client, PPC | CLI-10, BKO-01 | Suit la confirmation ; PPC voit l'encaissement | **Encaissement certifié**, part transport provisionnée |
| 7 | Système | CLI-11 | Le bon est émis automatiquement, une seule fois | **Bon de commande** nominatif, QR signé |
| 8 | Transporteur | TRP-03 | Reçoit la course et l'accepte | Acceptation ferme, engin compatible |
| 9 | Client | CLI-12 | Voit le transporteur affecté et le suivi activé | — |
| 10 | Agent d'expédition | CHG-02, CHG-03 | Contrôle le bon, pèse, scelle, photographie | **Chargement certifié** |
| 11 | Agent d'expédition | CHG-04 | Clôture le bon et remet le bon de sortie | Bon clôturé, usage unique consommé |
| 12 | Chauffeur | CHF-05 | Signale les événements de route et les positions | Positions horodatées |
| 13 | Client | CLI-13 | Valide la quantité, l'état et le scellé | **Preuve de livraison** |
| 14 | PPC | BKO-06 | Instruit le règlement du transporteur sur preuve | Ordre de règlement motivé |
| 15 | Client | CLI-14, CLI-15 | Télécharge le dossier de preuve et le reçu | **Reçu certifié** vérifiable |

### 5.2 Parcours B — enlèvement sans transporteur (option A)

| Étape | Acteur | Écran | Ce qu'il fait | Preuve produite |
|---|---|---|---|---|
| 1 | Client | CLI-06, CLI-07 | Choisit l'option A : il organise son transport | — |
| 2 | Client | CLI-08, CLI-09 | Reçoit la cotation puis paie | Cotation certifiée, encaissement |
| 3 | Système | CLI-11 | Émet le bon de sortie nominatif avec QR | Bon à usage unique |
| 4 | Client | CLI-11 | Transmet le code d'enlèvement à son mandataire | Mandataire déclaré (US-M3-06) |
| 5 | Agent d'expédition, dépôt | CHG-02, DEP-01 | Contrôle le bon et remet la marchandise | Chargement certifié |
| 6 | Client | CLI-15 | Retrouve la commande dans son historique | Reçu certifié |

> Aucune provision de transport n'est créée dans cette option : c'est la règle RG-PAY-04 et elle est visible dans l'interface — l'écran CLI-11 ne mentionne ni transporteur, ni course, ni suivi.

### 5.3 Paiement reçu sans cotation — le cas qui produit les incidents

| Étape | Acteur | Écran | Ce qu'il fait | Preuve produite |
|---|---|---|---|---|
| 1 | Système | EXP-01, BKO-05 | Détecte un encaissement sans référence de cotation valide | Alerte de rapprochement |
| 2 | Contrôleur financier | BKO-05 | Ouvre un dossier de rattrapage | Dossier `RAP-…`, aucune affectation d'office |
| 3 | Contrôleur financier | BKO-05 | Rattache le paiement à une cotation du même client, avec motif | Lien tracé, motif horodaté |
| 4 | Client | CLI-10, CLI-11 | Reçoit son bon de commande | Bon émis après régularisation |
| 5 | Contrôleur financier | BKO-09 | Vérifie la trace dans le journal d'audit | Trace complète et opposable |

> Cette procédure existe parce que les comptes d'encaissement dédiés de PPC refusent les fonds sans cotation valide. Elle est volontairement manuelle et tracée : la corriger dans l'interface est un progrès, la contourner en silence est la source des incidents constatés.

### 5.4 Litige sur écart de quantité

| Étape | Acteur | Écran | Ce qu'il fait | Preuve produite |
|---|---|---|---|---|
| 1 | Client | CLI-13 | Constate un écart ou un scellé rompu, refuse la validation | Refus motivé, preuve conservée en l'état (RG-POD-08) |
| 2 | Système | CLI-14 | Ouvre immédiatement un litige et gèle la part contestée | Dossier `LIT-…`, gel partiel (RG-LIT-04) |
| 3 | PPC | BKO-07 | Instruit : dossier de preuve complet sur un seul écran | Échanges horodatés |
| 4 | PPC | BKO-07 | Décide : faveur client, faveur transporteur ou partage | Décision motivée avec montants (RG-LIT-05) |
| 5 | Système | — | Libère la part non contestée au transporteur | Règlement partiel |
| 6 | Toutes parties | CLI-14, TRP-05 | Sont notifiées sur leur canal préféré | Notification tracée (RG-LIT-07) |

### 5.5 Ce que le MVP ne permet pas encore

Le groupage n'existe pas au MVP, et l'interface le dit. Un client qui commande une quantité inférieure au seuil de rentabilité d'un camion voit :

1. le prix du camion dédié, sans détournement du regard ;
2. une mention explicite « groupage disponible prochainement » ;
3. aucune promesse de délai ni de prix réduit.

Présenter un groupage simulé serait la pire des options : il créerait une attente que la V1 ne tiendrait pas au moment où le client en a le plus besoin.

---

## 6. Matrice écrans par rôle

Légende : **L** lecture, **C** création ou saisie, **V** validation ou décision, **—** aucun accès.

| Interface | Client final | Transporteur | Chauffeur | Agent d'expédition | Administrateur PPC | Contrôleur financier | Dépôt agréé | Super-administrateur APIX |
|---|---|---|---|---|---|---|---|---|
| IF-01 Application client | **L C** | — | — | — | L | L | L | — |
| IF-02 Web client | **L C** | — | — | — | L | L | L | — |
| IF-03 Application chauffeur | — | L | **L C** | — | L | — | — | — |
| IF-04 Portail transporteur | — | **L C** | L | — | L V | L | — | — |
| IF-05 Console de chargement | — | — | — | **L C** | L | — | L | — |
| IF-06 Back-office PPC | — | — | — | — | **L C V** | L C V | — | L |
| IF-07 Console dépôt | — | — | — | L | L | — | **L C** | — |
| IF-08 Console d'exploitation APIX | — | — | — | — | L | — | — | **L C** |

> Le détail des 30 fonctions et des 9 rôles figure dans `dist/xlsx/02-Matrice-roles-droits.xlsx`. La présente matrice ne donne que la vue par interface, utile à la conception et à la recette.

---

## 7. Contraintes de terrain qui façonnent les écrans

| Contrainte constatée | Conséquence directe sur l'écran |
|---|---|
| Réseau lent, intermittent, parfois absent plusieurs heures | Écrans légers, aucune animation décorative, reprise après coupure, file d'attente visible |
| Téléphones d'entrée de gamme, 5 pouces, mémoire limitée | Une action principale par écran, trois boutons au maximum, pas de tableau de plus de trois colonnes |
| Chauffeur en plein soleil, parfois avec des gants | Boutons de 56 points, contraste élevé, libellés courts, une seule confirmation par étape |
| 90 secondes par camion au point de chargement | Quatre champs maximum à la saisie, scan unique, verdict de contrôle en moins d'une seconde |
| Coupure d'électricité à l'usine | Tablette sur batterie, 72 heures d'autonomie hors ligne, aucune preuve perdue au redémarrage |
| Noms de clients à l'orthographe variable | Recherche par numéro de téléphone, jamais par nom seul |
| Utilisateurs PPC sur écran large, traitement de files | Tableaux denses, raccourcis clavier, actions groupées, filtres sauvegardés |
| Méfiance vis-à-vis d'un prix « qui bouge » | Le prix ferme et la date de validité sont affichés ensemble, toujours au même endroit |
| Méfiance vis-à-vis d'un bon revendu | Le bon est nominatif, avec QR signé et numéro dictable ; l'écran explique pourquoi |

---

## 8. Points non tranchés qui changent l'écran

| Sujet | Question ouverte | Écran concerné | Ce qui change selon la réponse |
|---|---|---|---|
| Périodicité du plafond de 2 500 $ | Q-50 | CLI-09 | Affichage d'un plafond par transaction, par jour ou par mois ; le message d'alternative n'est pas le même |
| Durée de validité d'une cotation | Q-51 | CLI-08 | Le compte à rebours de 48 heures est une proposition : sa durée exacte vient de PPC |
| Délai de règlement des transporteurs | Q-02 | BKO-06, TRP-05 | Aucune date n'est affichée aujourd'hui ; dès que le délai est arrêté, il devient une promesse tenue à l'écran |
| Tolérance d'écart de quantité | RG-CHG-03, RG-POD-04 | CHG-03, CLI-13 | « 1 % ou 2 sacs » : le seuil affiché, et donc le déclenchement du litige, en dépend |
| Seuil haut de rapprochement manuel | RG-PAY-17 | CLI-09, BKO-05 | Détermine à partir de quel montant l'écran impose une référence de virement unique |
| Accès des utilisateurs PPC par annuaire | US-M11-06 | BKO-10 | Si l'annuaire n'est pas disponible, l'écran retombe sur une gestion locale de comptes |
| Agrégateur de paiement | Piste Araka ou banque agrégateur | CLI-09 | Le client ne voit que des canaux ; le choix du fournisseur ne modifie que les frais, pas l'écran |
| Nombre de versements d'un échéancier | RG-PAY-18 | CLI-09 | Un échéancier à deux versements ne se présente pas comme un échéancier à quatre |

---

## 9. Recette du MVP

### 9.1 Critères de recette, jalon par jalon

| Jalon | Critère vérifiable | Écran(s) de vérification | Comment on vérifie |
|---|---|---|---|
| J1 | Un compte non vérifié ne peut pas dépasser le plafond de premier niveau | CLI-04, CLI-16 | Tentative de commande au-delà du plafond : refus explicite et action proposée |
| J2 | Aucun prix n'est produit pour un visiteur non identifié | CLI-04 | Appel direct du service de prix sans session : refus, sans valeur affichée |
| J2 | Une cotation expirée ne peut plus être payée | CLI-08, CLI-09 | Cotation antidatée de 49 heures : bouton de paiement remplacé par une explication |
| J3 | Un ordre de paiement sans numéro de cotation est refusé | CLI-09 | Tentative de paiement sans cotation : blocage côté service, pas seulement côté écran |
| J3 | Les canaux proposés correspondent au montant | CLI-09 | Commande de 3 000 $ : seuls le virement et l'échéancier sont proposés |
| J4 | Le bon est émis une seule fois, à l'encaissement | CLI-11 | Double notification d'encaissement : un seul bon produit |
| J5 | Aucun chargement sans bon valide et non utilisé | CHG-02 | Scan d'un bon déjà chargé : refus motivé, aucune écriture |
| J5 | Un chargement saisi hors ligne est transmis au retour du réseau | CHF-04, CHF-07 | Mode avion, saisie, retour réseau : transmission unique et horodatage serveur ajouté |
| J6 | Le chauffeur ne peut pas valider la réception à la place du client | CHF-06 | Tentative de clôture sans validation client : refus |
| J6 | Un écart hors tolérance ouvre un litige | CLI-13 | Réception avec 4 sacs manquants : litige ouvert, part contestée gelée |
| J7 | Un reçu est vérifiable par son numéro | CLI-15 | Vérification publique d'un reçu, sans compte |

### 9.2 Règles qu'aucun écran ne doit permettre de contourner

1. Créer un bon de commande sans cotation encaissée.
2. Afficher un prix à un visiteur non identifié.
3. Payer une cotation expirée.
4. Fractionner une commande pour passer sous un plafond de canal.
5. Valider une livraison à la place du client.
6. Régler un transporteur sans preuve de livraison ou décision explicite de PPC.
7. Modifier un bon, un chargement ou une preuve déjà enregistrés.
8. Supprimer une pièce du dossier de preuve.

---

## Annexe A — Wireframes des écrans

> **Comment lire ces planches.** Les traits gris donnent la structure, les barres grises représentent le contenu textuel, les croix en pointillés les emplacements d'image. **L'orange est réservé à l'action principale de l'écran** : s'il y en a deux, c'est que l'écran est mal découpé. Chaque écran porte son code et son nom en pied de planche.

| Planche | Interface et écrans représentés | Support |
|---|---|---|
| A.1 | IF-01 — CLI-04 catalogue et prix, CLI-07 demande de cotation | Téléphone |
| A.2 | IF-01 — CLI-08 cotation certifiée, CLI-09 choix du moyen de paiement | Téléphone |
| A.3 | IF-01 — CLI-11 bon de commande, CLI-13 validation de réception | Téléphone |
| A.4 | IF-03 — CHF-02 mes courses, CHF-04 chargement, CHF-06 livraison | Téléphone |
| A.5 | IF-05 — CHG-02 contrôle du bon, cas d'un bon refusé | Tablette |
| A.6 | IF-04 — TRP-03 course proposée | Bureau |
| A.7 | IF-06 — BKO-01 tableau de bord de pilotage | Bureau |
| A.8 | IF-06 — BKO-05 paiements reçus sans cotation | Bureau |
| A.9 | IF-06 — BKO-07 instruction d'un litige | Bureau |
| A.10 | IF-07 — DEP-01 réception d'un bon au dépôt | Tablette |

:::paysage

![Planche A.1 — IF-01 Application client : catalogue et demande de cotation|24](assets/wireframes/p01-client-catalogue-cotation.png)

![Planche A.2 — IF-01 Application client : cotation certifiée et choix du paiement|24](assets/wireframes/p02-client-cotation-paiement.png)

![Planche A.3 — IF-01 Application client : bon de commande et validation de réception|24](assets/wireframes/p03-client-bon-reception.png)

![Planche A.4 — IF-03 Application chauffeur : courses, chargement, livraison|24](assets/wireframes/p04-chauffeur.png)

![Planche A.5 — IF-05 Console de chargement : contrôle du bon, cas d'un bon déjà chargé|23](assets/wireframes/p05-chargement-controle.png)

![Planche A.6 — IF-04 Portail transporteur : course proposée et compatibilité de flotte|25](assets/wireframes/p06-transporteur-course.png)

![Planche A.7 — IF-06 Back-office PPC : tableau de bord de pilotage|25](assets/wireframes/p07-backoffice-pilotage.png)

![Planche A.8 — IF-06 Back-office PPC : paiements reçus sans cotation|25](assets/wireframes/p08-backoffice-sans-cotation.png)

![Planche A.9 — IF-06 Back-office PPC : instruction d'un litige|25](assets/wireframes/p09-backoffice-litige.png)

![Planche A.10 — IF-07 Console dépôt : réception d'un bon|23](assets/wireframes/p10-depot-reception.png)

:::portrait

## Annexe B — Glossaire des préfixes d'écran

| Préfixe | Interface | Acteur |
|---|---|---|
| `CLI-` | IF-01 Application client | Client final PPC |
| `WCL-` | IF-02 Web client | Client final sur poste fixe |
| `CHF-` | IF-03 Application chauffeur | Chauffeur du transporteur |
| `TRP-` | IF-04 Portail transporteur | Transporteur partenaire |
| `CHG-` | IF-05 Console de chargement | Agent d'expédition PPC |
| `BKO-` | IF-06 Back-office PPC | Administrateur et contrôleur financier PPC |
| `DEP-` | IF-07 Console dépôt | Dépôt ou point de retrait agréé |
| `EXP-` | IF-08 Console d'exploitation APIX | Super-administrateur APIX |
