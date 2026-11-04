# Annexe A1 — Règles de gestion

**Extension APIX — Règles opposables, versionnées et testables**
FBB pour PPC · version 1.0 · 4 novembre 2026

> Chaque règle porte un identifiant stable, citable en réunion et repérable dans le code. Une règle ne peut être modifiée que par une nouvelle version documentée. Les paramètres marqués `[À VALIDER PPC]` doivent être fixés au cadrage.

---

## Sommaire

1. [Règles de compte et de vérification d'identité](#1-règles-de-compte-et-de-vérification-didentité)
2. [Règles de bon de commande](#2-règles-de-bon-de-commande)
3. [Règles de paiement, d'encaissement et de règlement](#3-règles-de-paiement-dencaissement-et-de-règlement)
4. [Règles de tarification du transport](#4-règles-de-tarification-du-transport)
5. [Règles d'affectation des courses](#5-règles-daffectation-des-courses)
6. [Règles de groupage](#6-règles-de-groupage)
7. [Règles de chargement](#7-règles-de-chargement)
8. [Règles de preuve de livraison](#8-règles-de-preuve-de-livraison)
9. [Règles de litige](#9-règles-de-litige)
10. [Règles de transporteur](#10-règles-de-transporteur)
11. [Tableau récapitulatif des paramètres](#11-tableau-récapitulatif-des-paramètres)

---

## 1. Règles de compte et de vérification d'identité

| Code | Règle | Paramètre | Justification |
|---|---|---|---|
| **RG-KYC-01** | Un compte est créé à l'état « non vérifié » après validation du numéro de téléphone par code à usage unique | Validité du code : 5 minutes ; 3 tentatives | Empêche la création de comptes fictifs en masse |
| **RG-KYC-02** | Trois profils de compte : *particulier*, *entreprise ou chantier*, *dépôt ou revendeur* | — | Les besoins et les risques diffèrent radicalement |
| **RG-KYC-03** | Un compte « non vérifié » ne peut pas dépasser le plafond de premier niveau | Plafond : `[À VALIDER PPC]` | Contient le risque tant que l'identité n'est pas établie |
| **RG-KYC-04** | La vérification d'identité exige des pièces différentes selon le profil | Voir tableau 1.1 | Proportionnalité et conformité |
| **RG-KYC-05** | Une vérification validée ne peut être retirée que par un administrateur PPC, avec motif obligatoire et trace d'audit | — | Évite les dévalidations arbitraires |
| **RG-KYC-06** | Une pièce expirée fait basculer le compte en « vérification à renouveler » sans bloquer les commandes en cours, mais bloque toute nouvelle commande au-delà du plafond de premier niveau | Préavis : 30 jours | Équilibre entre conformité et continuité d'activité |

### Tableau 1.1 — Pièces exigées par profil

| Profil de compte | Pièces d'identité | Pièces d'entreprise | Justificatif d'activité | Plafond applicable |
|---|---|---|---|---|
| Particulier | Pièce d'identité en cours de validité | Sans objet | Sans objet | Plafond particulier |
| Entreprise ou chantier | Pièce du représentant légal | Registre du commerce, identifiant fiscal | Attestation de marché si commande importante | Plafond entreprise |
| Dépôt ou revendeur | Pièce du représentant légal | Registre du commerce, identifiant fiscal, patente | Justificatif du point de vente (photo, titre d'occupation) | Plafond dépôt |

---

## 2. Règles de bon de commande

| Code | Règle | Paramètre | Justification |
|---|---|---|---|
| **RG-CMD-01** | Un bon de commande est créé à l'état « brouillon » ; il n'engage personne | — | Permet la reprise sans réservation de stock |
| **RG-CMD-02** | La certification intervient après paiement confirmé et produit un numéro unique séquentiel par exercice | — | Traçabilité comptable |
| **RG-CMD-03** | Le contenu signé du bon comprend : identification du titulaire, produit, quantité, poids, option d'achat, prix total, zone de livraison, version | — | Toute altération invalide la signature |
| **RG-CMD-04** | Le bon est nominatif : il ne peut être utilisé que par le titulaire du compte ou par un mandataire déclaré | — | Empêche la revente de bons |
| **RG-CMD-05** | Le bon est à usage unique : le premier chargement validé le clôture définitivement | — | Empêche le double enlèvement |
| **RG-CMD-06** | Un bon non payé expire et libère la réservation de stock | Expiration : 2 heures `[À VALIDER PPC]` | Évite l'immobilisation de stock par des paniers abandonnés |
| **RG-CMD-07** | Après paiement, aucune modification n'est possible : seules l'annulation avec remboursement ou la création d'un nouveau bon sont admises | — | Intégrité comptable |
| **RG-CMD-08** | Un bon ne peut être exécuté que sur le point de chargement prévu lors de sa certification | — | Empêche les sorties non contrôlées |

---

## 3. Règles de paiement, d'encaissement et de règlement

> Principe de base, aligné sur le circuit réel : **le client paie PPC**, avant le chargement. La part transport est identifiée dans la commande, puis réglée au transporteur **sur preuve de livraison**. Il n'existe pas de séquestre des fonds du client.

| Code | Règle | Paramètre | Justification |
|---|---|---|---|
| **RG-PAY-01** | Un paiement n'est réputé confirmé qu'après notification authentifiée de l'établissement émetteur | Délai d'attente maximal : 15 minutes avant passage en revue manuelle | Évite les validations sur promesse |
| **RG-PAY-02** | Toute opération financière porte une clé d'idempotence ; un rejeu ne produit jamais de second mouvement | — | Garantit l'intégrité des comptes |
| **RG-PAY-03** | Le paiement est encaissé par PPC dès confirmation ; les fonds ne transitent jamais par APIX ni par le transporteur | — | Circuit réel du marché, et FBB n'a pas à porter les fonds d'autrui |
| **RG-PAY-04** | Lorsque l'offre vendue comprend le transport, la part correspondante est isolée dans la commande et provisionnée pour la course ; elle n'est réglée au transporteur qu'après preuve de livraison conforme. Une offre sans transport ne crée aucune provision | Rétention : 24 heures `[À VALIDER PPC]` | Le règlement devient un levier de qualité, sans toucher au paiement du client |
| **RG-PAY-05** | Le règlement du transporteur ne peut être déclenché que par un fait générateur enregistré : preuve de livraison conforme ou décision explicite de PPC | — | Aucun versement sans preuve opposable |
| **RG-PAY-06** | Un litige ouvert gèle la part contestée des fonds, et elle seule | — | Évite de pénaliser la totalité de la course |
| **RG-PAY-07** | Le remboursement d'un bon non chargé est intégral, sans frais | — | Protège le client en cas de défaillance |
| **RG-PAY-08** | Le remboursement d'un bon partiellement livré porte sur la part non livrée, au prix réellement payé | — | Proportionnalité |
| **RG-PAY-09** | Le remboursement suit le moyen de paiement d'origine lorsque l'émetteur le permet | Sinon virement ou avoir | Évite le blanchiment par changement de canal |
| **RG-PAY-10** | Un paiement confirmé deux fois pour le même bon est remboursé automatiquement ou signalé sous 24 heures | — | Erreur fréquente des opérateurs |
| **RG-PAY-11** | Les dépôts en espèces sont plafonnés par client et par période, et déclenchent une alerte au-delà du seuil | Seuil : `[À VALIDER PPC]` | Conformité anti-blanchiment |
| **RG-PAY-12** | Une libération supérieure à un seuil exige une double validation | Seuil : `[À VALIDER PPC]` | Lutte contre la fraude interne |

### Tableau 3.1 — Matrice du règlement du transport

| Situation constatée | Versement au transporteur |
|---|---|
| Bon non payé | Aucun |
| Payé, non chargé, non annulé | Aucun — provision en attente |
| Payé, chargé, en cours de transport | Aucun |
| Livraison prouvée conforme | Règlement intégral après rétention |
| Livraison prouvée avec écart dans la tolérance | Règlement intégral après rétention |
| Livraison prouvée avec écart hors tolérance | Retenue calculée au prorata, solde réglé |
| Non-livraison constatée | Aucun règlement ; remboursement ou avoir au client par PPC |
| Annulation avant chargement | Aucun règlement ; remboursement ou avoir au client |

---

## 4. Règles de tarification du transport

| Code | Règle | Paramètre | Justification |
|---|---|---|---|
| **RG-TAR-01** | Le prix du transport est calculé exclusivement à partir d'un barème publié par PPC ; aucune saisie libre n'est possible | — | Empêche la spéculation |
| **RG-TAR-02** | Le barème est versionné et daté ; un bon conserve le barème en vigueur à sa certification | — | Rejouabilité et équité |
| **RG-TAR-03** | Le calcul de base est : coût fixe de l'axe + coût à la tonne-kilomètre × poids × distance de l'axe | — | Modèle lisible et vérifiable |
| **RG-TAR-04** | Un coefficient de détour s'applique aux zones hors axe | Coefficient par zone | Le détour a un coût réel |
| **RG-TAR-05** | Un coefficient de saison s'applique aux périodes de pluie | Plage et coefficient par période | Détérioration des pistes |
| **RG-TAR-06** | Les frais annexes (péages, accès, manutention) sont intégrés au barème, jamais ajoutés en cours de route | — | Supprime les frais surprise |
| **RG-TAR-07** | Le prix affiché au client est ferme dès la certification du bon | — | Confiance du client |
| **RG-TAR-08** | Toute dérogation tarifaire est nominative, motivée, datée et limitée dans le temps | — | Traçabilité |
| **RG-TAR-09** | Le barème est révisé selon une périodicité fixée et peut l'être en cas de variation majeure du carburant | Périodicité : trimestrielle `[À VALIDER PPC]` | Évite l'obsolescence |
| **RG-TAR-10** | Un indicateur d'écart entre prix du barème et coût réel déclaré par les transporteurs est suivi mensuellement | Seuil d'alerte : `[À VALIDER PPC]` | Détecte un barème irréaliste avant la fuite des transporteurs |

### Formule de référence

$$\text{Coût}_{transport} = \left( CF_{axe} + CTK_{axe} \times D_{axe} \times P_{tonnes} \right) \times K_{saison} \times K_{detour}$$

| Symbole | Signification | Unité |
|---|---|---|
| $CF_{axe}$ | Coût fixe de l'axe (péages, immobilisation, tracasseries) | Unité monétaire |
| $CTK_{axe}$ | Coût à la tonne-kilomètre validé par PPC pour l'axe | Unité monétaire par tonne-kilomètre |
| $D_{axe}$ | Distance de référence de l'axe | Kilomètre |
| $P_{tonnes}$ | Poids total transporté | Tonne |
| $K_{saison}$ | Coefficient de saison (1,00 hors pluie) | Sans dimension |
| $K_{detour}$ | Coefficient de détour de la zone de livraison (1,00 si sur l'axe) | Sans dimension |

> Le coût fixe de l'axe n'est pas multiplié par le poids : il correspond aux frais engagés dès qu'un camion part, quelle que soit sa charge. C'est précisément ce coût fixe que le groupage permet de mutualiser.

---

## 5. Règles d'affectation des courses

| Code | Règle | Paramètre | Justification |
|---|---|---|---|
| **RG-AFF-01** | Seuls les transporteurs homologués, dont l'homologation et l'assurance sont valides, reçoivent des courses | — | Protège la marque PPC |
| **RG-AFF-02** | L'engin affecté doit satisfaire simultanément : charge utile suffisante, type de caisse compatible, gabarit autorisé sur l'axe | — | Évite les livraisons impossibles |
| **RG-AFF-03** | L'affectation suit deux étapes : proposition ciblée au transporteur le mieux noté, puis diffusion aux transporteurs disponibles de l'axe | Délai avant diffusion : 30 minutes | Concilie qualité et réactivité |
| **RG-AFF-04** | Si aucune course n'est acceptée dans le délai, la commande passe en « transport à arbitrer » et PPC est alerté | Délai : 4 heures `[À VALIDER PPC]` | Empêche l'enlisement silencieux |
| **RG-AFF-05** | L'acceptation d'une course est ferme ; un désistement est tracé et réduit le score du transporteur | — | Responsabilise |
| **RG-AFF-06** | Un transporteur ne peut pas accepter une course incompatible avec l'un de ses engins homologués | — | Empêche les engagements impossibles |
| **RG-AFF-07** | Une révocation d'homologation en cours de course n'interrompt pas la course, mais elle est signalée à PPC et interdit toute nouvelle affectation | — | Évite l'abandon de marchandise en route |

---

## 6. Règles de groupage

| Code | Règle | Paramètre | Justification |
|---|---|---|---|
| **RG-GRP-01** | Le groupage est proposé lorsque le poids commandé est inférieur au seuil de rentabilité d'un camion dédié sur l'axe | Seuil par axe : `[À VALIDER PPC]` | Le petit volume n'est pas livrable autrement |
| **RG-GRP-02** | L'acceptation du groupage est explicite et mentionne le délai d'attente possible et les conditions d'annulation | — | Consentement éclairé |
| **RG-GRP-03** | Les commandes d'un même lot doivent partager : axe, produit, point de chargement, et une fenêtre de livraison compatible | Fenêtre : 72 heures | Cohérence du chargement et de la tournée |
| **RG-GRP-04** | Le lot se déclenche lorsque la charge atteint le seuil de remplissage défini pour l'axe | Seuil : 85 % de la capacité `[À VALIDER PPC]` | Équilibre rentabilité / attente |
| **RG-GRP-05** | Le lot possède une durée de vie ; à son expiration, trois issues sont possibles : poursuite avec un engin plus petit, report accepté par le client jusqu'au remplissage du lot, remboursement à la demande explicite du client | Durée de vie : 48 heures `[À VALIDER PPC]` | Aucun client ne reste bloqué |
| **RG-GRP-06** | En l'absence de réponse du client à l'expiration, le report lui est appliqué et il en est informé ; le remboursement sans frais reste possible à tout moment sur demande | Délai de réponse : 12 heures | Le report est la solution par défaut, le remboursement reste un droit |
| **RG-GRP-07** | Les frais sont répartis au prorata du poids multiplié par la distance parcourue, plus une quote-part des frais fixes au prorata du poids | — | Chacun paie ce qu'il consomme |
| **RG-GRP-08** | Le détail du calcul est consultable par le client avant et après paiement | — | Confiance et contestabilité |
| **RG-GRP-09** | Toute modification de la composition du lot après engagement entraîne un recalcul affiché et accepté | Acceptation sous 24 heures | Aucune surprise à la livraison |
| **RG-GRP-10** | L'ordre de chargement est l'inverse de l'ordre de livraison | — | Le déchargement doit être possible |
| **RG-GRP-11** | Une annulation après verrouillage du lot entraîne une pénalité dégressive | Barème de pénalité `[À VALIDER PPC]` | Évite les annulations opportunistes |
| **RG-GRP-12** | Un lot non complété et livré par un engin plus petit est re-tarifé au prorata réel, sans dépasser le prix annoncé au client | — | Le client ne paie pas l'échec du remplissage |
| **RG-GRP-13** | Un arrêt non livré n'empêche pas la validation des autres arrêts du lot | — | Proportionnalité du règlement |
| **RG-GRP-14** | Le chauffeur ne peut pas clôturer un arrêt sans validation de réception par le client de cet arrêt | — | Empêche la validation globale abusive |

### Formule de répartition du coût mutualisé

$$\text{Part}_{i} = \text{Coût}_{course} \times \frac{P_i \times D_i}{\sum_{j=1}^{n} \left( P_j \times D_j \right)}$$

| Symbole | Signification |
|---|---|
| $\text{Part}_{i}$ | Montant dû par le client $i$ |
| $\text{Coût}_{course}$ | Coût total de la course groupée selon le barème |
| $P_i$ | Poids commandé par le client $i$ |
| $D_i$ | Distance parcourue depuis le point de chargement jusqu'au point de livraison du client $i$ |
| $n$ | Nombre de clients du lot |

> Limite connue : cette formule répartit correctement les coûts variables mais sous-estime la quote-part des frais fixes pour les petits volumes. C'est pourquoi une composante fixe répartie au prorata du poids doit être ajoutée en second terme (RG-GRP-07), sous peine de voir les gros clients subventionner les petits.

---

## 7. Règles de chargement

| Code | Règle | Paramètre | Justification |
|---|---|---|---|
| **RG-CHG-01** | Un chargement ne peut être enregistré que sur un bon valide, non expiré, non utilisé, et rattaché au point de chargement courant | — | Empêche les sorties non autorisées |
| **RG-CHG-02** | Le poids réel chargé, le nombre de sacs et le numéro de scellé sont obligatoires | Scellé obligatoire pour l'option avec transporteur | Base de la preuve |
| **RG-CHG-03** | Un écart entre quantité commandée et quantité chargée supérieur à la tolérance exige une validation superviseur | Tolérance : 1 % ou 2 sacs `[À VALIDER PPC]` | Empêche les sorties partielles non autorisées |
| **RG-CHG-04** | Le chargement validé clôture le bon de façon irréversible | — | Usage unique |
| **RG-CHG-05** | Une photo du chargement et le ticket de pesée sont joints au dossier de preuve | — | Opposabilité |
| **RG-CHG-06** | Un chargement enregistré hors ligne est transmis dès le retour du réseau et horodaté côté serveur en plus de l'horodatage local | — | Détection des horodatages incohérents |

---

## 8. Règles de preuve de livraison

| Code | Règle | Paramètre | Justification |
|---|---|---|---|
| **RG-POD-01** | La livraison est constatée par le client, jamais par le transporteur seul | — | Évite l'auto-certification |
| **RG-POD-02** | Le constat comprend : validation du client, photo du chargement livré, poids ou compte constaté, contrôle du scellé | — | Preuve à plusieurs éléments |
| **RG-POD-03** | La photo est horodatée et géolocalisée ; l'absence de position est acceptée mais signalée | — | Contexte de la preuve |
| **RG-POD-04** | Un écart entre poids chargé et poids constaté supérieur à la tolérance ouvre automatiquement un litige | Tolérance : 1 % ou 2 sacs `[À VALIDER PPC]` | Détection objective |
| **RG-POD-05** | Un scellé rompu ou différent de celui du chargement ouvre automatiquement un litige | — | Indice fort d'intervention en route |
| **RG-POD-06** | La preuve de livraison est signée et son intégrité est vérifiable | — | Opposabilité technique |
| **RG-POD-07** | Le constat est possible hors ligne ; il est transmis dès le retour du réseau | — | Réalité du terrain |
| **RG-POD-08** | En cas de refus de validation par le client, une déclaration de litige est ouverte immédiatement, et la preuve est conservée en l'état | — | Aucune perte d'information |
| **RG-POD-09** | Un constat de livraison ne peut être modifié ; une correction est un nouvel événement qui référence le précédent | — | Trace complète |

---

## 9. Règles de litige

| Code | Règle | Paramètre | Justification |
|---|---|---|---|
| **RG-LIT-01** | Un litige peut être déclaré par le client, le transporteur ou PPC | — | Toutes les parties doivent pouvoir saisir |
| **RG-LIT-02** | La déclaration est possible pendant un délai défini après la livraison | Délai : 48 heures `[À VALIDER PPC]` | Évite les contestations tardives |
| **RG-LIT-03** | Un litige ouvre un dossier avec numéro unique, pièces jointes et échanges horodatés | — | Instruction contradictoire |
| **RG-LIT-04** | L'ouverture d'un litige gèle la part contestée des fonds | — | Protège le demandeur |
| **RG-LIT-05** | La décision est prise par un administrateur PPC et comporte : sens de la décision, montant retenu, montant libéré, motif | — | Traçabilité et opposabilité |
| **RG-LIT-06** | Les décisions possibles sont : faveur client, faveur transporteur, partage, complément d'information | — | Cadre fermé |
| **RG-LIT-07** | Les parties sont notifiées de la décision par leur canal préféré | — | Transparence |
| **RG-LIT-08** | Une décision peut être revue sur production d'éléments nouveaux, dans un délai défini | Délai de recours : 15 jours `[À VALIDER PPC]` | Équilibre entre fermeté et équité |
| **RG-LIT-09** | La retenue financière en cas de marchandise manquante est calculée sur la valeur de la marchandise au prix payé, majorée des frais de transport correspondants | — | Réparation juste |
| **RG-LIT-10** | L'indemnisation est plafonnée à la valeur de la marchandise concernée | Plafond : valeur totale du bon | Évite les demandes disproportionnées |

---

## 10. Règles de transporteur

| Code | Règle | Paramètre | Justification |
|---|---|---|---|
| **RG-TRP-01** | L'homologation est prononcée par un administrateur PPC, sur dossier complet, avec motif en cas de refus | — | Souveraineté de PPC |
| **RG-TRP-02** | L'homologation a une durée de validité et doit être renouvelée | Durée : 12 mois `[À VALIDER PPC]` | Actualisation des garanties |
| **RG-TRP-03** | Une pièce expirée (assurance, visite technique, permis) bloque immédiatement toute nouvelle affectation | Préavis d'alerte : 30 jours | Sécurité juridique |
| **RG-TRP-04** | L'assurance responsabilité civile marchandises est obligatoire et son montant minimal est fixé par PPC | Montant : `[À VALIDER PPC]` | Couverture des sinistres |
| **RG-TRP-05** | La révocation est immédiate et n'interrompt pas les courses en cours, qui sont signalées à PPC | — | Évite l'abandon en route |
| **RG-TRP-06** | Le score de fiabilité agrège : respect des délais, taux de litige, qualité des preuves, taux d'acceptation, désistements | Pondération : `[À VALIDER PPC]` | Oriente les courses vers les fiables |
| **RG-TRP-07** | Le score est communiqué au transporteur avec le détail de ses composantes | — | Amélioration possible |
| **RG-TRP-08** | Un score inférieur au seuil critique déclenche une revue de l'homologation | Seuil : `[À VALIDER PPC]` | Sortie progressive des défaillants |

---

## 11. Tableau récapitulatif des paramètres

Tous les paramètres ci-dessous doivent être fixés au cadrage, consignés dans un document contractuel, puis saisis dans le back-office. **Aucun de ces paramètres ne doit être codé en dur.**

| Paramètre | Règle associée | Valeur proposée | Valeur retenue par PPC |
|---|---|---|---|
| Validité du code à usage unique | RG-KYC-01 | 5 minutes | |
| Nombre de tentatives de code | RG-KYC-01 | 3 | |
| Préavis d'expiration de pièce | RG-KYC-06 | 30 jours | |
| Expiration d'un bon non payé | RG-CMD-06 | 2 heures | |
| Délai d'attente d'une confirmation de paiement | RG-PAY-01 | 15 minutes | |
| Délai de rétention avant libération | RG-PAY-04 | 24 heures | |
| Seuil d'alerte sur dépôt en espèces | RG-PAY-11 | À définir | |
| Seuil de double validation d'une libération | RG-PAY-12 | À définir | |
| Périodicité de révision du barème | RG-TAR-09 | Trimestrielle | |
| Délai avant diffusion d'une course | RG-AFF-03 | 30 minutes | |
| Délai de passage en « transport à arbitrer » | RG-AFF-04 | 4 heures | |
| Seuil de rentabilité pour proposer le groupage | RG-GRP-01 | Par axe | |
| Fenêtre de livraison compatible dans un lot | RG-GRP-03 | 72 heures | |
| Seuil de remplissage d'un lot | RG-GRP-04 | 85 % | |
| Durée de vie d'un lot | RG-GRP-05 | 48 heures | |
| Délai de réponse du client à l'expiration | RG-GRP-06 | 12 heures | |
| Tolérance d'écart de quantité au chargement | RG-CHG-03 | 1 % ou 2 sacs | |
| Tolérance d'écart de quantité à la livraison | RG-POD-04 | 1 % ou 2 sacs | |
| Délai de déclaration d'un litige | RG-LIT-02 | 48 heures | |
| Délai de recours sur une décision | RG-LIT-08 | 15 jours | |
| Durée de validité d'une homologation | RG-TRP-02 | 12 mois | |
| Montant minimal d'assurance marchandises | RG-TRP-04 | À définir | |
| Seuil critique de score transporteur | RG-TRP-08 | À définir | |
