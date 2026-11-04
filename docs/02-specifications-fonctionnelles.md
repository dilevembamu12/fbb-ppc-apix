# 02 — Spécifications fonctionnelles détaillées

**Extension APIX — Plateforme Clients Finaux & Logistique Ciment**
FBB pour PPC · version 1.0 · 4 novembre 2026

> Convention : `US-xx-yy` désigne un récit utilisateur, `RF-xx-yy` une exigence fonctionnelle, `RG-…` une règle de gestion référencée en annexe A1. Les priorités sont `MVP`, `V1`, `V2`.

---

## Sommaire des modules

| Module | Intitulé | Priorité |
|---|---|---|
| M1 | Compte client final et vérification d'identité | MVP |
| M2 | Catalogue, prix et disponibilité | MVP |
| M3 | Bon de commande certifié | MVP |
| M4 | Paiement, séquestre et libération | MVP |
| M5 | Option A — Enlèvement et chargement | MVP |
| M6 | Option B — Transport, barème et affectation | MVP |
| M7 | Suivi, notifications et incidents | MVP |
| M8 | Preuve de livraison et litiges | MVP |
| M9 | Historique, reçus et facturation | MVP |
| M10 | Portail transporteur et application chauffeur | MVP |
| M11 | Back-office PPC (homologation, barèmes, pilotage) | MVP |
| M12 | Groupage logistique | V1 |

---

## M1 — Compte client final et vérification d'identité

### Objectif

Permettre à un client final de créer un compte utilisable immédiatement, tout en plafonnant les usages non vérifiés et en satisfaisant les obligations de connaissance du client.

### Références croisées

Règles : `RG-KYC-01` à `RG-KYC-06`.

### Récits utilisateurs

**US-M1-01 — Création de compte par un particulier** *(MVP)*
En tant que particulier, je veux créer un compte avec mon numéro de téléphone afin de commander sans passer par un dépôt.

*Critères d'acceptation :*
- Le numéro de téléphone est vérifié par un code à usage unique, valable 5 minutes, limité à 3 tentatives.
- Le compte est créé à l'état **« non vérifié »** avec un plafond de commande réduit.
- Aucune commande ne peut être payée en espèces au-delà du plafond non vérifié.

**US-M1-02 — Vérification d'identité (KYC)** *(MVP)*
En tant que client, je veux téléverser ma pièce d'identité pour relever mon plafond de commande.

*Critères d'acceptation :*
- Le téléversement accepte une photo ou un PDF, taille maximale 5 Mo.
- Pour un **particulier** : pièce d'identité en cours de validité, nom, prénom, date de naissance, adresse.
- Pour une **entreprise** : numéro d'identification nationale d'entreprise, attestation fiscale, identité du représentant légal.
- Pour un **dépôt / revendeur** : pièces de l'entreprise **et** justificatif du point de vente.
- Le statut est visible en clair : *en attente*, *validé*, *rejeté avec motif*.
- Une vérification validée ne peut être défaite que par un administrateur PPC, avec motif obligatoire et trace d'audit.

**US-M1-03 — Profils de compte et plafonds** *(MVP)*
En tant qu'administrateur PPC, je veux définir des plafonds par profil de compte afin de contenir le risque commercial.

*Critères d'acceptation :*
- Trois profils minimum : **particulier**, **entreprise / chantier**, **dépôt / revendeur**.
- Les plafonds sont paramétrables : montant par commande, montant cumulé par jour, montant cumulé par mois, nombre de commandes en cours.
- Le dépassement est bloqué avec un message explicite et une proposition d'action (vérification, contact commercial).

**US-M1-04 — Gestion des utilisateurs rattachés** *(V1)*
En tant qu'entreprise, je veux rattacher plusieurs utilisateurs à un même compte afin que mes chefs de chantier commandent sans partager un identifiant.

*Critères d'acceptation :*
- Un compte entreprise possède un titulaire et des utilisateurs secondaires.
- Chaque utilisateur secondaire a un rôle : *commandeur*, *approbateur*, *lecture seule*.
- Le titulaire ne peut pas être supprimé, seulement transféré avec validation PPC.

### Exigences fonctionnelles

| Réf. | Exigence | Priorité |
|---|---|---|
| RF-M1-01 | Authentification par numéro de téléphone + code à usage unique ; mot de passe optionnel | MVP |
| RF-M1-02 | Authentification par courriel en complément, obligatoire pour les comptes entreprise | MVP |
| RF-M1-03 | Session par jeton courte durée, renouvellement par jeton de rafraîchissement | MVP |
| RF-M1-04 | Liaison de l'appareil : changement d'appareil notifié au titulaire | V1 |
| RF-M1-05 | Suppression du compte à la demande, avec conservation des pièces comptables et de preuve | V1 |
| RF-M1-06 | Notifications de sécurité (nouvelle connexion, changement de numéro) | V1 |

---

## M2 — Catalogue, prix et disponibilité

### Objectif

Afficher un prix fiable et à jour, sans jamais exposer de tarif non validé par PPC.

### Récits utilisateurs

**US-M2-01 — Consultation du catalogue** *(MVP)*
En tant que client, je veux voir les produits disponibles avec leur prix afin de préparer ma commande.

*Critères d'acceptation :*
- Le catalogue affiche : désignation du produit, conditionnement (sacs de 50 kg, vrac), prix unitaire, unité de vente.
- Le prix affiché dépend du **profil de compte** et de la **zone de livraison** du client.
- Un prix est toujours accompagné de sa **date d'entrée en vigueur** ; un prix expiré n'est jamais affiché.
- Un produit indisponible est affiché comme tel, avec une date de retour si elle est connue.

**US-M2-02 — Prix tout compris avant paiement** *(MVP)*
En tant que client, je veux voir le prix total (ciment + transport) avant de payer afin de décider en connaissance de cause.

*Critères d'acceptation :*
- L'écran de récapitulatif présente, en lignes séparées : prix du ciment, prix du transport, frais annexes, total.
- Chaque ligne est **cliquable** et affiche son mode de calcul en langage clair (distances, poids, coefficient de saison).
- Aucun frais ne peut apparaître après la validation du paiement.

**US-M2-03 — Gestion du catalogue par PPC** *(MVP)*
En tant qu'administrateur PPC, je veux publier et retirer des produits afin de garder le catalogue exact.

*Critères d'acceptation :*
- Chaque publication est **versionnée** et datée ; l'historique est consultable.
- Le retrait d'un produit n'affecte pas les commandes déjà payées.

### Exigences fonctionnelles

| Réf. | Exigence | Priorité |
|---|---|---|
| RF-M2-01 | Grille de prix par produit, profil et zone, versionnée et horodatée | MVP |
| RF-M2-02 | Devise de référence unique, montants arrondis selon une règle paramétrée | MVP |
| RF-M2-03 | Simulation de prix sans engagement, accessible avant création de compte | V1 |
| RF-M2-04 | Affichage des promotions et remises volume, si PPC en dispose | V1 |

---

## M3 — Bon de commande certifié

### Objectif

Produire un document numérique unique, nominatif, infalsifiable et non réutilisable, qui matérialise l'engagement réciproque.

### Références croisées

Règles : `RG-CMD-01` à `RG-CMD-08`.

### Récits utilisateurs

**US-M3-01 — Création d'un bon de commande** *(MVP)*
En tant que client, je veux créer un bon de commande en choisissant produit, quantité, option d'achat et zone de livraison.

*Critères d'acceptation :*
- Les champs obligatoires sont : produit, quantité, option d'achat, zone de livraison (sauf option A).
- La quantité est saisie en sacs ou en tonnes, avec conversion automatique affichée.
- Pour l'option B, le prix du transport est calculé **avant** validation et reste figé à la création.
- Le bon reçoit un numéro unique lisible et un identifiant technique.
- Un bon non payé expire au bout d'un délai paramétrable (proposition : 2 heures) et libère la réservation de stock.

**US-M3-02 — Certification du bon** *(MVP)*
En tant que client, je veux recevoir un bon de commande certifié APIX afin de pouvoir le présenter au chargement.

*Critères d'acceptation :*
- Le bon est **nominatif** : il porte le nom du titulaire du compte et son numéro de compte.
- Il porte un **QR code signé** cryptographiquement, vérifiable hors ligne par la console d'expédition.
- Il porte un **code de contrôle à 8 caractères** lisible à voix haute, utilisable en cas de panne de scanner.
- Il est **à usage unique** : après premier usage au chargement, tout nouvel usage est refusé.
- Il est consultable et téléchargeable (PDF) dans l'application.

**US-M3-03 — Modification d'un bon** *(MVP)*
En tant que client, je veux corriger une commande non encore payée afin de ne pas recommencer la saisie.

*Critères d'acceptation :*
- Modification possible uniquement à l'état **brouillon** ou **en attente de paiement**.
- Toute modification recalcule le prix et réémet le numéro de version.
- Après paiement, aucune modification n'est possible : seule une **annulation avec remboursement** ou une **nouvelle commande** est admise.

**US-M3-04 — Options d'achat** *(MVP)*
En tant que client, je veux choisir entre *sans transporteur*, *avec transporteur* et *autre* afin de commander selon ma situation réelle.

*Critères d'acceptation :*
- **Option A — Sans transporteur** : génère un bon de sortie ; le client ou son mandataire retire au point de chargement.
- **Option B — Avec transporteur** : exige une zone de livraison et calcule le barème.
- **Option C — Autre** : propose une **liste de cas paramétrés par PPC** ; le motif est obligatoire ; le bon est placé en **validation manuelle** avant paiement.
- Le changement d'option après paiement est impossible.

**US-M3-05 — Mandataire pour l'enlèvement (option A)** *(MVP)*
En tant que client, je veux désigner une personne pour retirer ma marchandise afin de pouvoir mandater mon propre transporteur.

*Critères d'acceptation :*
- Le mandataire est renseigné par nom, pièce d'identité et numéro de téléphone.
- Un code d'enlèvement à usage unique est transmis au mandataire par SMS.
- L'agent d'expédition contrôle la pièce d'identité et le code avant chargement.
- Toute substitution de mandataire est journalisée.

### Exigences fonctionnelles

| Réf. | Exigence | Priorité |
|---|---|---|
| RF-M3-01 | Réservation de stock à la création du bon, libérée à expiration ou annulation | MVP |
| RF-M3-02 | Numérotation séquentielle par exercice, non modifiable | MVP |
| RF-M3-03 | Signature cryptographique du bon et du QR code | MVP |
| RF-M3-04 | Vérification du bon hors ligne par la console d'expédition | MVP |
| RF-M3-05 | Duplication d'un bon antérieur en brouillon (commande récurrente) | V1 |
| RF-M3-06 | Commande récurrente programmée (abonnement d'approvisionnement) | V1 |
| RF-M3-07 | Devis sans engagement transformable en bon de commande | V2 |

---

## M4 — Paiement, séquestre et libération

### Objectif

Encaisser de façon certaine, cantonner les fonds, et ne les libérer que sur preuve ou décision explicite.

### Références croisées

Règles : `RG-PAY-01` à `RG-PAY-12`.

### Récits utilisateurs

**US-M4-01 — Paiement par mobile money** *(MVP)*
En tant que client, je veux payer par mobile money afin de commander depuis mon téléphone.

*Critères d'acceptation :*
- Au moins deux opérateurs pris en charge.
- Le bon reste **en attente de paiement** jusqu'à confirmation effective par l'opérateur, jamais sur simple promesse.
- En cas de délai supérieur à 2 minutes, un écran d'attente explique la situation et permet de reprendre la main.
- Un paiement confirmé en double est remboursé automatiquement ou signalé au service financier sous 24 heures.

**US-M4-02 — Paiement en espèces via agent** *(MVP)*
En tant que client, je veux payer en espèces chez un agent agréé afin de commander sans compte mobile money.

*Critères d'acceptation :*
- Le client génère une **référence de dépôt** liée au bon de commande.
- L'agent saisit la référence et le montant ; un reçu lui est délivré.
- Le bon passe à l'état payé **après rapprochement** (automatique si l'agent est intégré, manuel sinon).
- Le plafond de dépôt en espèces par client et par période est paramétrable (conformité anti-blanchiment).

**US-M4-03 — Séquestre** *(MVP)*
En tant que client, je veux que mon argent soit conservé et non versé au transporteur avant livraison.

*Critères d'acceptation :*
- À la confirmation du paiement, les fonds sont **cantonnés** sur un compte dédié chez l'établissement partenaire.
- Le client voit en clair : *payé*, *sous séquestre*, *libéré*.
- Aucune libération n'est possible sans un **fait générateur** enregistré : preuve de livraison conforme, décision de PPC, ou expiration du délai de réclamation.
- Toute écriture est **idempotente** : un rejeu technique ne produit jamais de double mouvement.

**US-M4-04 — Libération des fonds** *(MVP)*
En tant que système, je veux libérer les fonds selon des règles explicites afin que transporteur et PPC soient payés au bon moment.

*Critères d'acceptation :*
- **Transport** : libéré à la preuve de livraison conforme (ou au prorata en cas de litige partiel).
- **Ciment** : libéré à PPC à la sortie certifiée du stock, sauf disposition contraire de PPC.
- Un délai de rétention paramétrable est possible avant libération effective (proposition : 24 heures après preuve).
- Toute libération produit une pièce justificative téléchargeable.

**US-M4-05 — Remboursement** *(MVP)*
En tant que client, je veux être remboursé lorsqu'une commande n'est pas honorée.

*Critères d'acceptation :*
- Le remboursement est possible en totalité si aucun chargement n'a eu lieu.
- Le remboursement partiel est possible sur la part non livrée d'une commande.
- Le remboursement suit le moyen de paiement d'origine lorsque cela est possible.
- Le délai de remboursement est affiché et suivi (« sous 5 jours ouvrés »).

### Exigences fonctionnelles

| Réf. | Exigence | Priorité |
|---|---|---|
| RF-M4-01 | Abstraction des fournisseurs de paiement : au moins deux opérateurs mobiles + virement bancaire | MVP |
| RF-M4-02 | Réconciliation automatique des paiements (rapprochement opérateur / commande) | MVP |
| RF-M4-03 | Journal financier en partie double pour tout mouvement de séquestre | MVP |
| RF-M4-04 | Blocage anti-blanchiment : seuils et alertes sur dépôts en espèces | MVP |
| RF-M4-05 | Paiement par carte bancaire | V1 |
| RF-M4-06 | Échelonnement du paiement (acompte / solde) | V2 |
| RF-M4-07 | Avance de carburant au transporteur, déduite du règlement final | V1 |

---

## M5 — Option A : enlèvement et chargement

### Objectif

Certifier la remise physique de la marchandise au point de chargement, pour toutes les options d'achat.

### Récits utilisateurs

**US-M5-01 — Contrôle du bon au chargement** *(MVP)*
En tant qu'agent d'expédition PPC, je veux scanner le bon afin de vérifier qu'il est valide et non déjà utilisé.

*Critères d'acceptation :*
- La console de chargement fonctionne avec un scan optique **ou** une saisie manuelle du code à 8 caractères.
- Le contrôle affiche : statut du bon, nom du client, produit, quantité, option d'achat, transporteur éventuel.
- Un bon déjà utilisé, expiré, annulé ou appartenant à un autre point de chargement est **refusé** avec un motif clair.
- Le refus est journalisé et consultable par l'administrateur PPC.

**US-M5-02 — Enregistrement du chargement** *(MVP)*
En tant qu'agent d'expédition, je veux enregistrer le poids réel et le numéro de scellé afin de créer la preuve de départ.

*Critères d'acceptation :*
- Saisie du **poids au chargement** et du **nombre de sacs**, avec ticket de pesée photographié.
- Saisie du **numéro de scellé** (obligatoire pour l'option B).
- Photo du chargement, horodatage et identification de l'agent.
- Un écart entre quantité commandée et quantité chargée supérieur à la tolérance déclenche une **validation superviseur**.
- Un document de chargement certifié est généré et devient opposable.

**US-M5-03 — Clôture du bon** *(MVP)*
En tant que système, je veux clôturer le bon après chargement afin d'empêcher sa réutilisation.

*Critères d'acceptation :*
- Le bon passe à l'état **« chargé »** immédiatement après validation.
- Toute nouvelle présentation du même bon est refusée.
- Le client reçoit une notification avec le poids chargé et le numéro de scellé.

### Exigences fonctionnelles

| Réf. | Exigence | Priorité |
|---|---|---|
| RF-M5-01 | Console de chargement utilisable sur tablette et ordinateur, avec connexion instable | MVP |
| RF-M5-02 | Impression du bon de livraison et de la fiche de chargement | MVP |
| RF-M5-03 | Gestion de plusieurs points de chargement (usine, dépôts) | MVP |
| RF-M5-04 | File d'attente de chargement visible par le client (option B) | V1 |

---

## M6 — Option B : transport, barème et affectation

### Objectif

Calculer un prix de transport opposable, affecter un transporteur homologué, et organiser le déplacement.

### Références croisées

Règles : `RG-TAR-01` à `RG-TAR-10`, `RG-AFF-01` à `RG-AFF-07`.

### Récits utilisateurs

**US-M6-01 — Calcul du prix de transport** *(MVP)*
En tant que client, je veux connaître le prix exact du transport avant de payer.

*Critères d'acceptation :*
- Le prix est calculé à partir d'un **barème publié par PPC**, selon : axe, poids, type d'engin, période.
- Le calcul est expliqué en langage clair : *« Kinshasa → Kikwit, 8 tonnes, porteur 10 tonnes, coefficient saison des pluies 1,10 »*.
- Un coefficient de détour est appliqué si la zone de livraison est hors axe.
- Aucune saisie de prix libre n'est possible par le client ni par le transporteur.

**US-M6-02 — Choix de la zone de livraison** *(MVP)*
En tant que client, je veux indiquer simplement où livrer, même sans adresse formelle.

*Critères d'acceptation :*
- Sélection par **zone normalisée** (ville, commune, quartier) définie par PPC.
- **Point de repère libre obligatoire** en complément (texte).
- Position GPS **optionnelle** ; son absence ne bloque jamais la commande.
- Un numéro de contact joignable est obligatoire.
- Pour les zones non desservies, l'application propose un **point de rendez-vous logistique** défini par PPC.

**US-M6-03 — Affectation d'un transporteur** *(MVP)*
En tant que système, je veux affecter un transporteur homologué et compatible avec la charge.

*Critères d'acceptation :*
- Seuls les transporteurs **homologués, actifs et couverts par une assurance valide** reçoivent des courses.
- L'engin proposé doit satisfaire : charge utile ≥ poids total, type de caisse compatible avec le produit, gabarit autorisé sur l'axe.
- L'affectation suit l'ordre : **proposition ciblée** au transporteur le mieux noté, puis **diffusion** aux transporteurs disponibles de l'axe après un délai paramétrable.
- Si aucun transporteur n'accepte dans le délai, la commande passe en **« transport à arbitrer »** et PPC est alerté.
- Le client voit le nom du transporteur, l'immatriculation et le contact du chauffeur une fois la course acceptée.

**US-M6-04 — Engins et capacités** *(MVP)*
En tant qu'administrateur PPC, je veux gérer une typologie d'engins afin que l'affectation soit réaliste.

*Critères d'acceptation :*
- Chaque engin possède : libellé, charge utile maximale, volume, type de caisse, nombre d'essieux, gabarit, axes autorisés, coefficient tarifaire éventuel.
- Un engin peut être déclaré indisponible sur un axe donné.
- La typologie est versionnée ; une course existante conserve la typologie applicable à sa date de création.

**US-M6-05 — Multi-arrêts** *(V1)*
En tant que transporteur, je veux recevoir une feuille de route ordonnée afin de livrer plusieurs clients sur un même trajet.

*Critères d'acceptation :*
- La feuille de route liste les arrêts dans l'ordre de livraison.
- L'ordre de chargement affiché est l'**inverse** de l'ordre de livraison (dernier livré, premier chargé).
- Chaque arrêt possède son propre QR de réception et sa propre validation.
- Un arrêt non livré n'empêche pas la validation des autres.

**US-M6-06 — Cas « Autre »** *(MVP)*
En tant qu'administrateur PPC, je veux traiter les cas particuliers sans contourner le barème.

*Critères d'acceptation :*
- Liste de cas paramétrés : retrait en dépôt agréé, enlèvement par tiers mandaté, transport fourni par le client, livraison partielle autorisée.
- Motif obligatoire, pièce justificative possible.
- Validation manuelle avant paiement.
- Toute dérogation tarifaire est nominative, motivée et limitée dans le temps.

### Exigences fonctionnelles

| Réf. | Exigence | Priorité |
|---|---|---|
| RF-M6-01 | Moteur de barème paramétrable sans redéploiement | MVP |
| RF-M6-02 | Référentiel d'axes avec distances et points d'étape | MVP |
| RF-M6-03 | Référentiel de zones de livraison rattachées aux axes | MVP |
| RF-M6-04 | Règles de compatibilité engin / charge / axe | MVP |
| RF-M6-05 | Affectation automatique avec délai de repli et escalade | MVP |
| RF-M6-06 | Refus motivé d'une course par un transporteur, avec impact sur son score | V1 |
| RF-M6-07 | Optimisation de tournée multi-arrêts | V1 |
| RF-M6-08 | Transport fluvial ou ferroviaire sur les axes concernés | V2 |

---

## M7 — Suivi, notifications et incidents

### Objectif

Donner au client la visibilité qu'il n'a jamais eue, et à PPC la capacité de réagir avant que l'incident ne devienne un litige.

### Récits utilisateurs

**US-M7-01 — Suivi de la commande** *(MVP)*
En tant que client, je veux suivre l'avancement de ma commande afin de savoir quand recevoir.

*Critères d'acceptation :*
- Quatre états lisibles minimum : *payée*, *chargée*, *en route*, *livrée*.
- Position du camion affichée lorsque disponible, avec heure du dernier point.
- En l'absence de position récente, l'application affiche « dernière position connue » et non une position inventée.
- Le suivi reste consultable 90 jours.

**US-M7-02 — Notifications multi-canal** *(MVP)*
En tant que client, je veux être informé par le canal qui fonctionne chez moi.

*Critères d'acceptation :*
- Canaux disponibles : notification dans l'application, SMS, WhatsApp.
- Événements notifiés : bon certifié, paiement confirmé, transporteur affecté, chargement effectué, départ, approche (moins de 30 km), livraison, incident.
- Le client choisit son canal préféré ; le SMS reste le canal de repli.
- Chaque notification est tracée (envoyée, reçue, échec).

**US-M7-03 — Déclaration d'incident** *(MVP)*
En tant que client, je veux signaler un problème pendant le transport afin qu'il soit traité avant la livraison.

*Critères d'acceptation :*
- Motifs proposés : retard anormal, immobilisation, accident, suspicion de détournement, marchandise endommagée.
- La déclaration est horodatée et notifiée à PPC et au transporteur.
- Un incident ouvert bloque la libération automatique des fonds jusqu'à décision.

**US-M7-04 — Repli SMS / USSD** *(V2)*
En tant que client sans smartphone, je veux commander et suivre par SMS afin de ne pas être exclu.

*Critères d'acceptation :*
- Un menu USSD permet : consulter le solde de commande, l'état d'une livraison, demander un rappel.
- Le format SMS respecte la limite de caractères et reste lisible sur un téléphone à clavier.

### Exigences fonctionnelles

| Réf. | Exigence | Priorité |
|---|---|---|
| RF-M7-01 | Collecte de positions par l'application chauffeur, avec fréquence adaptative | MVP |
| RF-M7-02 | Repli de collecte par SMS de position en zone sans données | V1 |
| RF-M7-03 | Journal d'événements par commande, immuable | MVP |
| RF-M7-04 | Tableau de bord des incidents en cours pour PPC | MVP |
| RF-M7-05 | Lien de suivi partageable avec un tiers (destinataire final) | V1 |

---

## M8 — Preuve de livraison et litiges

### Objectif

Rendre la livraison **prouvable** et le litige **arbitrable** sans parole contre parole.

### Références croisées

Règles : `RG-POD-01` à `RG-POD-09`, `RG-LIT-01` à `RG-LIT-10`.

### Récits utilisateurs

**US-M8-01 — Validation de réception par le client** *(MVP)*
En tant que client, je veux valider la réception afin de débloquer le paiement du transporteur.

*Critères d'acceptation :*
- Le client flashe le **QR de livraison** présenté par le chauffeur, ou saisit le code à 8 caractères.
- Il confirme : quantité reçue, état de l'emballage, numéro de scellé vérifié.
- Une **photo du chargement livré** est prise par le chauffeur et horodatée / géolocalisée.
- En cas de refus de validation, l'application ouvre immédiatement une **déclaration de litige** structurée.

**US-M8-02 — Preuve de livraison à trois preuves** *(MVP)*
En tant que PPC, je veux disposer d'un dossier de preuve complet pour chaque livraison.

*Critères d'acceptation :*
- Le dossier contient : QR flashé (horodatage, identité), photo géolocalisée, poids au chargement vs poids constaté, numéro de scellé, signature ou validation du client, identité du chauffeur.
- Le dossier est téléchargeable en PDF et opposable.
- L'intégrité du dossier est garantie par une empreinte cryptographique.

**US-M8-03 — Ouverture d'un litige** *(MVP)*
En tant que client, je veux déclarer un litige afin d'obtenir réparation.

*Critères d'acceptation :*
- Types de litige : sacs manquants, marchandise endommagée, retard, non-livraison, erreur de produit.
- Le litige fige la libération des fonds correspondants.
- Un délai de déclaration est paramétrable (proposition : 48 heures après livraison).
- Un numéro de dossier est attribué et communiqué au client.

**US-M8-04 — Instruction et décision** *(MVP)*
En tant qu'administrateur PPC, je veux instruire un litige et rendre une décision traçable.

*Critères d'acceptation :*
- L'administrateur consulte le dossier de preuve complet et les échanges.
- Décisions possibles : *faveur client*, *faveur transporteur*, *partage*, *complément d'information*.
- La décision précise le montant retenu et le montant libéré ; elle est motivée.
- Le transporteur et le client sont notifiés ; la décision est irrévocable sauf recours documenté.

**US-M8-05 — Litige partiel automatique** *(V1)*
En tant que système, je veux détecter automatiquement les écarts de quantité afin de réduire les litiges manuels.

*Critères d'acceptation :*
- Si l'écart entre poids chargé et poids constaté dépasse la tolérance définie, un litige est ouvert automatiquement.
- La retenue financière est calculée au prorata de la valeur marchandise manquante.
- Le transporteur dispose d'un délai pour contester avec pièces.

### Exigences fonctionnelles

| Réf. | Exigence | Priorité |
|---|---|---|
| RF-M8-01 | Fonctionnement de la validation de réception hors ligne | MVP |
| RF-M8-02 | Signature électronique simple du client sur l'écran | MVP |
| RF-M8-03 | Calcul automatique des pénalités de retard selon barème contractuel | V1 |
| RF-M8-04 | Historique des litiges par client et par transporteur | MVP |
| RF-M8-05 | Provision pour litige comptabilisée automatiquement | V1 |

---

## M9 — Historique, reçus et facturation

### Objectif

Donner au client la mémoire de ses achats et les pièces dont il a besoin pour sa comptabilité.

### Récits utilisateurs

**US-M9-01 — Historique des achats** *(MVP)*
En tant que client, je veux consulter mes achats passés afin de suivre mes dépenses et mes stocks.

*Critères d'acceptation :*
- Filtres : période, produit, statut, zone de livraison.
- Chaque ligne affiche : date, numéro de bon, produit, quantité, montant total, statut, transporteur éventuel.
- Export au format tableur des lignes filtrées.
- Un récapitulatif mensuel des volumes achetés est disponible.

**US-M9-02 — Reçu certifié** *(MVP)*
En tant que client, je veux télécharger un reçu certifié afin de prouver mon achat.

*Critères d'acceptation :*
- Le reçu porte un numéro unique, la référence de certification APIX et un QR de vérification.
- La vérification d'un reçu est possible publiquement à partir de son numéro.
- Le reçu reste disponible pendant la durée de conservation légale.

**US-M9-03 — Facture normalisée** *(V1)*
En tant que client entreprise, je veux une facture conforme à la réglementation fiscale afin de la passer en comptabilité.

*Critères d'acceptation :*
- La facture porte les mentions légales exigées (identifiants fiscaux des deux parties, ventilation de la taxe sur la valeur ajoutée).
- Le format respecte les exigences du dispositif de facturation électronique en vigueur ; le connecteur est validé avec le conseil fiscal de PPC.
- Les factures sont exportables par lot sur une période.

**US-M9-04 — Récapitulatif de stock estimé** *(V2)*
En tant que client dépôt, je veux une estimation de mon stock afin d'anticiper mon réapprovisionnement.

*Critères d'acceptation :*
- L'estimation croise les quantités achetées et les quantités déclarées vendues.
- Le client peut saisir une quantité vendue manuellement ou laisser l'estimation indicative.
- Une alerte est proposée lorsque le stock estimé passe sous un seuil.

### Exigences fonctionnelles

| Réf. | Exigence | Priorité |
|---|---|---|
| RF-M9-01 | Génération de PDF certifiés, archivage à valeur probante | MVP |
| RF-M9-02 | Vérification publique d'un reçu par numéro | MVP |
| RF-M9-03 | Connecteur de facturation électronique | V1 |
| RF-M9-04 | Export comptable vers un format standard | V1 |

---

## M10 — Portail transporteur et application chauffeur

### Objectif

Rendre les transporteurs partenaires **plus rentables avec APIX qu'en dehors**, et outiller leurs chauffeurs dans des conditions réelles.

### Références croisées

Règles : `RG-TRP-01` à `RG-TRP-08`.

### Récits utilisateurs

**US-M10-01 — Candidature d'un transporteur** *(MVP)*
En tant que transporteur, je veux candidater auprès de PPC afin d'accéder aux courses.

*Critères d'acceptation :*
- Formulaire : raison sociale, identifiants légaux, coordonnées, liste des engins, zones desservies, attestation d'assurance.
- Téléversement de pièces : registre du commerce, patente, assurance responsabilité civile marchandises, cartes grises, visites techniques, permis des chauffeurs.
- Le dossier est horodaté ; les pièces expirées sont signalées et bloquent l'affectation.
- Le transporteur suit l'état de son dossier et reçoit un motif en cas de rejet.

**US-M10-02 — Réception et acceptation d'une course** *(MVP)*
En tant que transporteur, je veux voir les courses disponibles et en accepter une afin de remplir mes camions.

*Critères d'acceptation :*
- La course affiche : axe, point de chargement, poids, type d'engin requis, nombre d'arrêts, prix proposé, date souhaitée.
- L'acceptation est ferme et engage le transporteur ; un désistement est tracé et impacte son score.
- Un transporteur ne peut pas accepter une course incompatible avec la capacité d'un de ses engins homologués.
- Confirmation par notification au client dans les 5 minutes.

**US-M10-03 — Application chauffeur hors ligne** *(MVP)*
En tant que chauffeur, je veux utiliser l'application sans réseau afin de ne pas perdre ma course en route.

*Critères d'acceptation :*
- La feuille de route, les coordonnées des clients et les QR de livraison sont disponibles hors ligne.
- Les preuves (photos, validations, positions) sont stockées localement et transmises dès le retour du réseau.
- Aucune preuve n'est perdue en cas de fermeture de l'application ou de redémarrage du téléphone.
- L'interface est utilisable avec une seule main et des boutons de grande taille.

**US-M10-04 — Score de fiabilité** *(V1)*
En tant que PPC, je veux noter les transporteurs afin d'orienter les courses vers les plus fiables.

*Critères d'acceptation :*
- Le score agrège : respect des délais, taux de litige, qualité des preuves, taux d'acceptation, désistements.
- Le score est visible par le transporteur, avec le détail de ses composantes.
- Un score bas réduit la priorité de proposition de course ; un score critique déclenche une revue PPC.

**US-M10-05 — Encaissement et relevé** *(MVP)*
En tant que transporteur, je veux suivre mes courses et mes paiements afin de gérer ma trésorerie.

*Critères d'acceptation :*
- Relevé des courses : date, axe, poids, montant, statut du paiement.
- Statut de paiement explicite : *en séquestre*, *libéré*, *retenu pour litige*.
- Export au format tableur.

### Exigences fonctionnelles

| Réf. | Exigence | Priorité |
|---|---|---|
| RF-M10-01 | Portail transporteur Web responsive, application chauffeur Android et iOS | MVP |
| RF-M10-02 | Gestion de plusieurs chauffeurs par transporteur, avec attribution des engins | MVP |
| RF-M10-03 | Alertes d'expiration des pièces administratives 30 jours avant échéance | MVP |
| RF-M10-04 | Attestation de course téléchargeable (justificatif de revenu) | V1 |
| RF-M10-05 | Mode « équipage » : deux chauffeurs sur un même véhicule | V2 |

---

## M11 — Back-office PPC

### Objectif

Donner à PPC la main sur les trois leviers de contrôle : **qui transporte**, **à quel prix**, **comment se règlent les litiges**.

### Récits utilisateurs

**US-M11-01 — Homologation d'un transporteur** *(MVP)*
En tant qu'administrateur PPC, je veux approuver ou refuser un transporteur afin de protéger la chaîne.

*Critères d'acceptation :*
- Vue du dossier complet avec contrôle de validité de chaque pièce.
- Décision : *approuvé*, *approuvé sous conditions*, *refusé* — avec motif obligatoire.
- L'homologation a une **durée de validité** et doit être renouvelée.
- La révocation est immédiate et bloque toute nouvelle affectation, sans affecter les courses en cours (qui sont signalées).

**US-M11-02 — Publication du barème** *(MVP)*
En tant qu'administrateur PPC, je veux publier un barème afin qu'il s'applique automatiquement.

*Critères d'acceptation :*
- Saisie par axe et par type d'engin : coût fixe d'axe, coût à la tonne-kilomètre, frais annexes.
- Coefficients : saison, détour, majoration de nuit ou de week-end.
- Simulation obligatoire avant publication, montrant l'effet sur les prix en cours.
- Publication versionnée avec date d'effet ; les commandes déjà payées conservent l'ancien barème.

**US-M11-03 — Tableau de bord de pilotage** *(MVP)*
En tant que direction PPC, je veux voir les indicateurs clés afin de piloter l'activité.

*Critères d'acceptation :*
- Indicateurs : volume commandé, volume livré, taux de service, taux de litige, délai moyen de livraison, coût moyen au sac, remplissage moyen.
- Filtres : période, axe, produit, transporteur, profil de client.
- Export des données brutes.
- Comparaison possible avec la période précédente.

**US-M11-04 — Gestion des litiges** *(MVP)*
En tant qu'administrateur, je veux traiter les litiges dans une file dédiée.

*Critères d'acceptation :*
- File triée par ancienneté et montant, avec priorité aux dossiers proches de l'échéance.
- Vue du dossier de preuve complet dans un seul écran.
- Décision, motif, notification automatique aux parties.

**US-M11-05 — Gestion des zones et axes** *(MVP)*
En tant qu'administrateur, je veux définir les zones de livraison et les axes afin que le calcul tarifaire soit juste.

*Critères d'acceptation :*
- Création d'axes avec distance, points d'étape, points de rendez-vous logistiques.
- Rattachement des zones aux axes, avec coefficient de détour.
- Désactivation d'une zone sans perte d'historique.

### Exigences fonctionnelles

| Réf. | Exigence | Priorité |
|---|---|---|
| RF-M11-01 | Gestion fine des droits par rôle et par périmètre (point de chargement, axe, région) | MVP |
| RF-M11-02 | Journal d'audit inaltérable de toutes les décisions administratives | MVP |
| RF-M11-03 | Workflow d'approbation à deux niveaux pour les dérogations tarifaires | V1 |
| RF-M11-04 | Simulation d'impact avant modification d'un paramètre structurant | V1 |
| RF-M11-05 | Alertes automatiques sur dérive d'indicateurs (taux de litige, délai) | V1 |

---

## M12 — Groupage logistique (V1)

### Objectif

Rendre livrable le client qui commande 20 sacs, sans lui faire payer un camion.

### Références croisées

Règles : `RG-GRP-01` à `RG-GRP-14`.

### Récits utilisateurs

**US-M12-01 — Proposition de groupage** *(V1)*
En tant que client, je veux qu'on me propose le groupage lorsque ma commande est trop petite pour un camion dédié.

*Critères d'acceptation :*
- La proposition apparaît lorsque le poids commandé est inférieur au seuil de rentabilité défini pour l'axe.
- L'écran compare explicitement : prix en camion dédié, prix en groupage, délai estimé dans chaque cas.
- L'acceptation est explicite ; elle mentionne le délai d'attente possible et les conditions d'annulation.

**US-M12-02 — Constitution d'un lot** *(V1)*
En tant que système, je veux regrouper les commandes compatibles afin de remplir un camion.

*Critères d'acceptation :*
- Critères de compatibilité : même axe, même produit, fenêtre de livraison compatible, même point de chargement.
- Le lot affiche sa jauge de remplissage et le délai restant avant arbitrage.
- Le seuil de déclenchement est paramétrable par axe (proposition : 85 % de la capacité).

**US-M12-03 — Arbitrage à l'expiration du délai** *(V1)*
En tant que système, je veux traiter un lot incomplet afin qu'aucun client ne reste bloqué.

*Critères d'acceptation :*
- Trois issues possibles : *poursuite avec un engin plus petit*, *report accepté par le client jusqu'au remplissage du lot*, *remboursement à la demande explicite du client*.
- Le client est notifié et choisit ; à défaut de réponse de sa part, le report lui est appliqué et il en est informé.
- Le remboursement reste possible à tout moment sur demande du client, sans frais.

**US-M12-04 — Répartition des frais** *(V1)*
En tant que client, je veux payer ma juste part du transport mutualisé.

*Critères d'acceptation :*
- La répartition est proportionnelle au **poids × distance parcourue** de chaque client, plus une quote-part des frais fixes au prorata du poids.
- Le détail du calcul est consultable par le client.
- Une variation de la composition du lot après engagement entraîne une **révision affichée** du prix, jamais une surprise à la livraison.

**US-M12-05 — Ordre de chargement** *(V1)*
En tant qu'agent d'expédition, je veux connaître l'ordre de chargement afin que le déchargement soit possible.

*Critères d'acceptation :*
- La fiche de chargement liste les lots dans l'ordre inverse de la tournée.
- Chaque lot porte une étiquette avec le nom du client et l'arrêt correspondant.
- Le chauffeur ne peut pas clôturer un arrêt sans validation de réception.

### Exigences fonctionnelles

| Réf. | Exigence | Priorité |
|---|---|---|
| RF-M12-01 | Moteur de constitution de lots avec jauge et délai | V1 |
| RF-M12-02 | Répartition dynamique des frais avec recalcul contrôlé | V1 |
| RF-M12-03 | Feuille de route multi-arrêts et fiche de chargement ordonnée | V1 |
| RF-M12-04 | Groupage inter-axes avec point de rupture (hub de transit) | V2 |
| RF-M12-05 | Prédiction de remplissage pour annoncer un délai réaliste | V2 |

---

## Matrice de traçabilité MVP

| Jalon de la chaîne de preuve | Modules requis | Modules optionnels |
|---|---|---|
| J1 — Compte et KYC | M1 | — |
| J2 — Bon de commande certifié | M2, M3 | — |
| J3 — Paiement séquestré | M4 | — |
| J4 — Chargement certifié | M5, M10 | — |
| J5 — Transport suivi | M6, M7 | — |
| J6 — Livraison prouvée | M8 | — |
| J7 — Reçu et historique | M9 | — |
| Pilotage | M11 | — |
| Groupage | — | M12 (V1) |

## Exigences transverses

| Réf. | Exigence | Priorité |
|---|---|---|
| RF-TR-01 | Toute action sensible est journalisée avec identité, horodatage et appareil | MVP |
| RF-TR-02 | Toute preuve est signée et vérifiable hors ligne | MVP |
| RF-TR-03 | Interface en français, terminologie validée par PPC | MVP |
| RF-TR-04 | Messages d'erreur explicites, sans code technique visible par l'utilisateur | MVP |
| RF-TR-05 | Accessibilité : contrastes suffisants, tailles de police adaptables | V1 |
