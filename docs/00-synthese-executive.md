# 00 — Synthèse exécutive

**Extension APIX : du paiement certifié à la logistique certifiée du ciment**
FBB · version 1.0

---

## 1. En une page

APIX certifie aujourd'hui les **transactions de paiement CIMA** sur les comptes de PPC. C'est une brique **financière** : elle prouve qu'un paiement a eu lieu et qu'il est conforme. Elle ne sait rien de ce qui se passe **après** le paiement : qui charge le ciment, dans quel camion, sur quel axe, à quel prix, avec quelle preuve de livraison.

Or la valeur perçue par le client final de PPC ne se joue pas au moment du paiement. Elle se joue au moment où **le camion arrive** — ou n'arrive pas, ou arrive incomplet.

**La proposition :** transformer APIX en chaîne de preuve unique qui relie cinq étapes aujourd'hui séparées — **cotation → paiement → bon de commande → chargement → livraison** — dans une seule application, pour Android, iOS et Web.

> **Précision de circuit, vérifiée sur le terrain :** le client demande d'abord un prix, reçoit une **cotation**, paie en la référençant, et la cotation encaissée devient le **bon de commande**. Les comptes d'encaissement de PPC refusent les fonds sans cotation valide. Ce n'est pas un détail de parcours : c'est la condition pour que chaque franc reçu soit rattachable à une commande.

> **Le chiffre qui commande tout le reste :** **15 à 20 %** seulement des encaissements de PPC passent aujourd'hui par le digital — quatre cinquièmes des flux échappent donc à toute traçabilité automatique. Deux causes se cumulent : le **plafond de 2 500 $ par transaction** sur mobile money et carte (or c'est la tranche des distributeurs et des grands comptes), et la **couverture bancaire** — trois banques seulement sont connectées au dispositif d'encaissement, le reste est rapproché à la main.

| Aujourd'hui (constat) | Avec APIX étendu (cible) |
|---|---|
| Le paiement est certifié, la marchandise ne l'est pas | Le paiement **et** la livraison sont certifiés sur la même chaîne |
| Le prix du transport se négocie au bord du camion | Le prix du transport est fixé par un **barème publié par PPC** |
| Le transporteur est un tiers non documenté | Le transporteur est **homologué par PPC**, noté et suivi |
| Un litige de livraison opposé à un paiement déjà encaissé | Un litige instruit sur preuve, avec **retenue partielle sur le règlement du transport** |
| Petites commandes impossibles à livrer (coût unitaire prohibitif) | **Groupage logistique** : plusieurs petits acheteurs, un seul camion |

---

## 2. Ce que PPC y gagne — et pourquoi c'est difficile à refuser

1. **Contrôle du dernier kilomètre.** Les transporteurs sont des partenaires tiers : en fixant le barème et l'homologation, PPC reprend la main sur le prix final perçu par le client.
2. **Protection de la marque.** Un sac volé, mouillé ou détourné se retourne contre le logo PPC, pas contre le transporteur. La preuve de livraison à trois preuves déplace la responsabilité vers celui qui la porte réellement.
3. **Désengorgement des sites de chargement.** Le groupage remplace quinze camionnettes par un porteur rempli à 85 %, et transforme des commandes éparses en **carnet de commandes prépayé**.
4. **Visibilité sur la demande finale.** Pour la première fois, PPC voit les achats de ses clients finaux en temps réel, par axe, par produit, par période — un signal direct sur la production.
5. **Verrouillage de l'écosystème.** Digiciment fait des transactions. APIX fait des transactions **et** la chaîne physique, dans le même identifiant client.

---

## 3. Ce que le client final y gagne

- Commander du bon pied depuis son téléphone, sans intermédiaire opaque.
- **Connaître le prix total avant de payer**, transport inclus.
- **Savoir exactement ce qu'il a payé**, et pouvoir le prouver en cas de livraison non conforme.
- **Suivre le camion** et être alerté par SMS, WhatsApp ou notification.
- **Acheter en petite quantité sans être puni par le transport**, grâce au groupage.
- **Détenir une preuve** de ce qu'il a acheté : reçu certifié, historique, justificatif comptable.

---

## 4. Ce que le transporteur partenaire y gagne

- Des courses **réglées par PPC sur preuve**, dans le délai qu'il aura fixé : aucun impayé côté client.
- Des rotations **pleines**, jamais des retours à vide subis.
- Une **grille tarifaire claire**, connue à l'avance.
- Un **règlement prévisible** : déclenché par la preuve de livraison, dans le délai que PPC aura fixé.
- Un **score de fiabilité** qui, avec le temps, lui donne accès aux meilleures courses.

> Conséquence à assumer devant PPC : APIX devient le **donneur d'ordre préféré** des meilleurs transporteurs de la place. Un transporteur qui refuse APIX se prive de rotations garanties.

---

## 5. La différenciation face à Digiciment

La bonne réponse n'est pas « nous gérons aussi les petites transactions ». La bonne réponse est structurelle :

| Critère | Digiciment | APIX étendu |
|---|---|---|
| Périmètre | Petites transactions, module logistique léger | Certificat **APIX** + commande + paiement + transport + livraison |
| Source de vérité | Finance d'un côté, logistique de l'autre | **Un identifiant client, un flux, une réconciliation** |
| Validation des transporteurs | Locale, au cas par cas | **Homologation administrative par PPC**, documentée et révocable |
| Prix du transport | Négocié | **Barème PPC** opposable, calculé au poids et à la distance |
| Preuve de livraison | Reçu simple | **QR nominatif + photo géolocalisée + pesée contradictoire + scellé** |
| Sécurité du règlement | Paiement direct, sans preuve | **Règlement du transport déclenché par la preuve** |
| Petits volumes | Traités isolément | **Groupage multi-clients avec TTL et prorata** |
| Réseau dégradé | Dépendance totale à Internet | **Mode hors-ligne transporteur, repli SMS / USSD** |

**Argument de clôture :** *« Digiciment numérise des transactions. APIX certifie une chaîne de responsabilité. Le jour où un contentieux arrive sur 500 sacs, ce n'est pas la transaction qu'on vous demandera de produire, c'est la preuve. »*

---

## 6. Périmètre proposé pour le MVP

Faire les quatre premiers jalons de la chaîne de preuve très bien, plutôt que sept approximativement.

**Dans le MVP (12 à 16 semaines après cadrage) :**

- Application client final (Android, iOS, Web) : inscription, KYC léger, **demande de cotation**, paiement, réception du bon de commande, historique.
- Trois options d'achat : **sans transport**, **avec transport**, **autre**.
- Barème logistique publié par PPC, appliqué automatiquement.
- Application chauffeur / transporteur avec mode hors-ligne.
- Homologation des transporteurs dans le back-office PPC.
- Preuve de livraison : QR nominatif, photo géolocalisée, horodatage, validation de conformité.
- Encaissement certifié, ventilation de la part transport, règlement du transporteur sur preuve.
- **Virement bancaire dès le MVP** : au-delà de 2 500 $ par transaction, c'est le seul canal possible — et c'est le segment B2B que PPC veut capter.
- **Commande et suivi par WhatsApp Business**, avec menus numérotés : le canal fonctionne même sans intelligence artificielle.
- Back-office PPC : transporteurs, barèmes, litiges, tableau de bord, comptes internes par annuaire d'entreprise.

**Hors MVP, en V1 :**

- Groupage inter-clients avec TTL et prorata.
- Multi-enlèvements sur un même trajet (itinéraire multi-arrêts).
- Score de fiabilité transporteur et arbitrage des courses.
- Intégration facturation normalisée DGI.
- Menu USSD complet et agent de proximité pour les clients sans smartphone.

**Hors périmètre (assumé) :**

- La gestion de la flotte propre de PPC, si elle existe.
- Le pilotage du processus de production usine.
- Le crédit à la consommation (sauf préparation des données).

---

## 7. Les cinq décisions à obtenir de PPC avant de développer

Ces cinq points ne sont pas techniques : ils conditionnent la faisabilité et la valeur du produit.

| N° | Décision attendue | Pourquoi c'est bloquant |
|---|---|---|
| D1 | **Qui est le donneur d'ordre du transport ?** Le client final ou PPC ? | Détermine le contrat, la responsabilité en cas de casse, et le circuit de paiement |
| D2 | **Comment PPC règle-t-il ses transporteurs aujourd'hui** : délai, moyen, traitement des litiges ? | Le modèle cible doit reproduire ce circuit réel, en le conditionnant à la preuve de livraison |
| D3 | **Le barème logistique existe-t-il déjà**, et qui le publie ? | Sans barème opposable, le produit ne peut pas calculer le prix — et le prix est le cœur de la valeur |
| D4 | **Comment le client final paie-t-il réellement**, en pratique, aujourd'hui ? | Si le cash reste majoritaire et n'est pas canalisé, l'adoption plafonne |
| D5 | **Le canal des dépôts et revendeurs est-il protégé ou remplacé ?** | Le risque de conflit de canal peut faire capoter l'adhésion commerciale de PPC |

---

## 8. Économie du projet — principes, pas chiffres

Les chiffres exacts dépendent de D1 à D5. Quatre modèles sont possibles, à choisir avec PPC :

1. **Frais de certification logistique** prélevés par course (modèle le plus proche d'APIX aujourd'hui).
2. **Abonnement PPC** par volume de commandes traitées.
3. **Commission de groupage** sur les courses mutualisées.
4. **Licence + intégration**, avec rémunération au succès sur les indicateurs de performance.

Recommandation FBB : combiner (1) et (2) pour le MVP — un revenu variable qui suit le succès opérationnel, un revenu fixe qui finance l'exploitation. Le modèle (3) ne se justifie qu'une fois le groupage en production.

---

## 9. Ce que nous demandons pour la phase suivante

| Jalon | Durée | Livrable attendu |
|---|---|---|
| Cadrage et ateliers métier | 3 semaines | Décisions D1 à D5 arrêtées, barème initial, référentiel transporteurs |
| Conception détaillée et maquettes | 3 semaines | Parcours validés, maquettes client / chauffeur / back-office |
| Développement MVP | 10 à 12 semaines | Produit utilisable sur un axe pilote |
| Pilote contrôlé | 4 semaines | Un axe, un type de produit, 5 à 10 transporteurs homologués |
| Bascule progressive | à définir | Généralisation par axe |

**Recommandation forte :** démarrer le pilote sur **un seul axe géographique** et **un seul type de ciment**, avec des transporteurs déjà connus de PPC. Un pilote propre sur un axe vaut mieux qu'un lancement national qui produit des litiges non traités.
