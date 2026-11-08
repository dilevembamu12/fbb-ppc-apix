# Annexe A2 — Questions ouvertes à trancher avec PPC

**Extension APIX — Liste de cadrage**
FBB pour PPC · version 1.0 · 4 novembre 2026

> Chaque question porte un identifiant, un statut et un caractère bloquant ou non. **Bloquant** signifie qu'aucune ligne de code ne doit être écrite avant réponse. Les réponses doivent être consignées par écrit et signées par le référent PPC désigné.

---

## 1. Questions bloquantes

Ces questions conditionnent la faisabilité du produit. Elles doivent être traitées **avant** le démarrage du développement.

| N° | Question | Pourquoi c'est bloquant | Réponse attendue | Réponse obtenue |
|---|---|---|---|---|
| **Q-01** | Le client final ou PPC est-il le donneur d'ordre du transport ? | Détermine le contrat, la responsabilité en cas de sinistre, et le circuit de paiement | Décision écrite de PPC | |
| **Q-02** | Comment PPC règle-t-il ses transporteurs aujourd'hui : délai, moyen, traitement des litiges ? | Le circuit cible doit reproduire le circuit réel ; l'argent du client va à PPC avant le chargement, il n'y a pas de séquestre | Description chiffrée du circuit actuel : délai moyen constaté, moyen de paiement, qui émet l'ordre, avances carburant, retenues pratiquées | |
| **Q-03** | PPC dispose-t-il d'un barème logistique par axe et par engin, ou faut-il le construire ? | Sans barème, aucun prix ne peut être calculé ni opposé | Barème existant ou validation d'un barème proposé | |
| **Q-04** | Quel est le circuit réel d'encaissement des clients finaux aujourd'hui ? | Détermine les moyens de paiement du MVP et le circuit espèces | Description chiffrée par moyen de paiement | |
| **Q-05** | Quel est le statut juridique exact de l'homologation prononcée par PPC ? | Détermine la rédaction du contrat tripartite et l'exposition de PPC | Avis du conseil juridique de PPC | |
| **Q-06** | Quels sont les points de chargement utilisables (usine, dépôts, autres) ? | Détermine le référentiel des points de chargement | Liste et adresses | |
| **Q-07** | Quelles interfaces APIX existent déjà pour la certification CIMA, et sous quel format ? | Détermine l'adaptateur de certification | Spécification d'interface documentée | |
| **Q-08** | Le réseau de dépôts et revendeurs est-il protégé commercialement ou concurrencé par l'application ? | Décision structurante, avec risque de rejet interne | Décision écrite de la direction commerciale | |

---

## 2. Questions structurantes non bloquantes

| N° | Question | Impact | Échéance souhaitée | Réponse obtenue |
|---|---|---|---|---|
| **Q-09** | Quels sont les volumes mensuels de commandes, de courses et de tonnes par axe ? | Dimensionnement, choix d'hébergement | Cadrage | |
| **Q-10** | Quels produits et conditionnements sont vendus (sacs de 50 kg, vrac, autres) ? | Référentiel produit | Cadrage | |
| **Q-11** | Combien de transporteurs partenaires PPC compte-t-il, et combien sont réellement actifs ? | Dimensionnement du pilote, nombre d'engins | Cadrage | |
| **Q-12** | Quels types d'engins sont réellement utilisés sur chaque axe ? | Référentiel engins, règles de compatibilité | Cadrage | |
| **Q-13** | Quels sont les axes prioritaires pour le pilote ? | Choix de l'axe pilote | Cadrage | |
| **Q-14** | Existe-t-il une flotte propre à PPC, et doit-elle être intégrée ? | Périmètre du référentiel transporteurs | Cadrage | |
| **Q-15** | Quels opérateurs de paiement mobile sont pertinents par région ? | Choix des intégrations du MVP | Conception | |
| **Q-16** | Existe-t-il un dispositif de facture normalisée en vigueur, et quel est son format ? | Module de facturation, conformité fiscale | Conception | |
| **Q-17** | Quelles sont les exigences de conservation des documents comptables et de preuve ? | Politique d'archivage, coût de stockage | Conception | |
| **Q-18** | PPC accepte-t-il un hébergement hors du territoire national, ou l'exige-t-il localement ? | Choix d'architecture et de fournisseur | Conception | |
| **Q-19** | Quel est le niveau de service attendu par PPC sur la disponibilité ? | Engagement de service, coût d'infrastructure | Conception | |
| **Q-20** | Qui assure le support de premier niveau aux clients finaux et aux transporteurs ? | Modèle d'exploitation, coût récurrent | Conception | |
| **Q-21** | Quel est le délai de paiement acceptable pour les transporteurs ? | Argument d'adhésion, besoin de trésorerie | Conception | |
| **Q-22** | Existe-t-il des accords de niveau de service avec les transporteurs aujourd'hui ? | Base contractuelle du dispositif | Conception | |
| **Q-23** | Comment les litiges sont-ils traités aujourd'hui, et par qui ? | Conception du module de litige, charge de travail | Conception | |
| **Q-24** | Y a-t-il des périodes de forte activité (saison des pluies, pics de chantier) à anticiper ? | Coefficients de saison, capacité | Conception | |

---

## 3. Questions sur l'existant APIX

| N° | Question | Impact | Réponse obtenue |
|---|---|---|---|
| **Q-25** | Combien de comptes PPC sont aujourd'hui couverts par la certification APIX ? | Base de clients à migrer | |
| **Q-26** | Quel identifiant relie un compte APIX à un client PPC ? | Clé de rapprochement | |
| **Q-27** | Quelles garanties de disponibilité APIX offre-t-il aujourd'hui ? | Stratégie de dégradation | |
| **Q-28** | Existe-t-il des contraintes de marque ou de charte graphique imposées par PPC ? | Conception de l'interface | |
| **Q-29** | Qui administre les comptes dans APIX aujourd'hui : FBB, PPC, ou les deux ? | Modèle de rôles et de gouvernance | |

---

## 4. Questions sur Digiciment

Ces questions sont sensibles et doivent être posées avec tact. Elles visent à comprendre le terrain, pas à attaquer un partenaire de PPC.

| N° | Question | Utilité | Réponse obtenue |
|---|---|---|---|
| **Q-30** | Quelles fonctions de Digiciment sont réellement utilisées par les clients PPC aujourd'hui ? | Savoir ce qu'il faut égaler, et ce qu'il faut dépasser | |
| **Q-31** | Digiciment est-il intégré à des systèmes PPC (facturation, comptabilité, stocks) ? | Éviter une rupture d'intégration | |
| **Q-32** | Y a-t-il un engagement contractuel entre PPC et Digiciment, et jusqu'à quand ? | Calendrier de substitution possible | |
| **Q-33** | Quels retours les clients finaux font-ils sur Digiciment ? | Identifier les douleurs non couvertes | |

---

## 5. Questions à poser aux transporteurs

À conduire lors d'entretiens individuels, avec 5 à 8 transporteurs représentatifs, avant la conception détaillée.

| N° | Question | Ce que l'on cherche à comprendre | Réponse obtenue |
|---|---|---|---|
| **Q-34** | Comment trouvez-vous vos courses aujourd'hui ? | Le canal de substitution à battre | |
| **Q-35** | Combien de temps attendez-vous au chargement, en moyenne ? | Le coût caché à éliminer | |
| **Q-36** | Quels frais engagez-vous en route qui ne sont pas refacturés ? | Le contenu réel du coût fixe d'axe | |
| **Q-37** | Quand êtes-vous payés, et avec quel retard ? | Mesurer le point de départ : c'est ce délai qui détermine la cible, pas l'inverse | |
| **Q-38** | Quels litiges vous oppose-t-on le plus souvent ? | Priorités du module de litige | |
| **Q-39** | Quel téléphone utilisez-vous ? Avez-vous de la data en permanence ? | Contraintes techniques réelles | |
| **Q-40** | Acceptez-vous un prix fixé par PPC sans négociation ? À quelles conditions ? | Faisabilité du barème | |
| **Q-41** | Que faudrait-il vous offrir pour refuser une course hors APIX ? | Le levier d'adhésion | |

---

## 6. Questions à poser aux clients finaux

À conduire sur le terrain, sur les trois profils, avant la conception détaillée.

| N° | Question | Ce que l'on cherche à comprendre | Réponse obtenue |
|---|---|---|---|
| **Q-42** | Comment commandez-vous du ciment aujourd'hui, concrètement ? | Le parcours réel à remplacer | |
| **Q-43** | Comment payez-vous ? | Faisabilité du circuit d'encaissement | |
| **Q-44** | Comment faites-vous venir le ciment chez vous ? | La place du transport dans la décision | |
| **Q-45** | Qu'est-ce qui vous a déjà coûté de l'argent lors d'une livraison ? | Priorités du module de preuve | |
| **Q-46** | Que faites-vous si vous recevez moins de sacs que prévu ? | Le litige réel, avant automatisation | |
| **Q-47** | Quel prix payez-vous réellement, transport inclus ? | Référence de comparaison pour l'argument de réduction du coût | |
| **Q-48** | Utilisez-vous un smartphone ? Lequel ? | Contraintes de conception | |
| **Q-49** | Avez-vous besoin d'une facture ? Pour quoi faire ? | Priorité du module de facturation | |

---

## 6 bis. Questions issues des entretiens des 5 et 6 novembre 2026

Ces points ont été soulevés en entretien et n'ont pas encore de réponse arrêtée. Ils sont plus précis que les précédents : ils portent sur des mécanismes déjà observés, pas sur des principes.

| N° | Question | Ce qui est déjà acquis | Ce qu'il reste à trancher |
|---|---|---|---|
| **Q-50** | Le plafond de 2 500 $ s'applique-t-il par transaction, par jour ou par mois ? | Un plafond de **2 500 $ par transaction** est constaté sur les canaux mobiles et carte | La périodicité exacte, et le plafond applicable aux comptes marchands |
| **Q-51** | Combien de temps une cotation reste-t-elle valide ? | La cotation est la référence exigée pour accepter un paiement | La durée : 48 heures proposées, à confirmer |
| **Q-52** | Quel traitement PPC applique-t-il aujourd'hui à un virement reçu sans cotation ? | Le compte d'encaissement refuse les fonds sans cotation valide ; une cotation manuelle est alors établie | Le délai de régularisation acceptable, et qui en porte la responsabilité |
| **Q-53** | Quelles banques doivent être connectées en priorité pour couvrir le B2B ? | Trois banques seulement sont connectées aujourd'hui | La liste des banques à intégrer, et l'ordre de priorité |
| **Q-54** | PPC veut-il négocier un agrégateur unique pour tous les mobile money, ou conserver plusieurs contrats ? | La question du coût des frais est ouverte | Le choix de l'agrégateur, et la comparaison de coût à instruire |
| **Q-55** | Quel annuaire d'entreprise PPC utilise-t-il pour ses collaborateurs ? | Le SSO est souhaité pour les utilisateurs internes | La technologie (Active Directory, OpenID Connect) et les règles de rôle |
| **Q-56** | Le canal WhatsApp doit-il être un canal de commande complet, ou seulement de notification et de suivi ? | La demande est explicite côté PPC | Le périmètre : notification seule, ou parcours de cotation et de paiement complet |
| **Q-57** | Une intelligence artificielle locale est-elle une exigence, ou une préférence ? | La préférence pour une IA souveraine est exprimée ; le fonctionnement sans IA est exigé | Le caractère contractuel ou non de cette préférence |
| **Q-58** | Le contrat marchand de PPC autorise-t-il plusieurs portefeuilles d'un même titulaire pour régler une même commande ? | Le fractionnement est souvent interdit par les conditions des opérateurs ; les paliers vérifiés plafonnent bien au-dessous des commandes de ciment | L'autorisation écrite, et le nombre de portefeuilles admis par commande |
| **Q-59** | PPC peut-il ouvrir un compte marchand business (avec RCCM) chez Vodacom, Airtel et Orange ? | Les paliers marchands autorisent 10 000 000 FC par transaction, contre 2 500 000 FC au mieux pour un compte vérifié | Le coût, les pièces exigées et le délai d'ouverture — c'est la réponse de fond au plafond |
| **Q-60** | Quel prestataire encaisse les paiements initiés par USSD et par SMS ? | Africa's Talking fournit l'USSD et le SMS mais ne collecte pas les fonds ; un PSP ou un agrégateur est nécessaire derrière | Sans PSP raccordé, le menu USSD affiche un prix et ne peut pas être payé |
| **Q-61** | PPC veut-il les cinq canaux en V1, ou un déploiement progressif ? | La parité complète est demandée ; elle représente cinq adaptateurs et un moteur de session | Le chiffrage, le calendrier, et le choix des deux premiers canaux |

---

## 7. Synthèse des décisions à obtenir

| N° | Décision | Instance décisionnaire | Date cible |
|---|---|---|---|
| **D-01** | Périmètre exact du MVP et de l'axe pilote | Comité de pilotage | Fin du cadrage |
| **D-02** | Donneur d'ordre du transport | Direction PPC | Fin du cadrage |
| **D-03** | Circuit de règlement du transport et validation juridique | Direction financière PPC | Fin du cadrage |
| **D-04** | Barème logistique initial | Direction commerciale PPC | Fin du cadrage |
| **D-05** | Rôle commercial des dépôts | Direction commerciale PPC | Fin du cadrage |
| **D-06** | Modèle économique retenu | Direction PPC et FBB | Fin du cadrage |
| **D-07** | Choix d'hébergement et cadre juridique des données | DSI et conseil juridique PPC | Conception |
| **D-08** | Calendrier de généralisation après pilote | Comité de pilotage | Après pilote |

---

## 8. Règles de tenue de cette liste

1. Une question sans réponse à la date prévue est **remontée au comité de pilotage**, pas traitée par défaut.
2. Une réponse orale n'est **pas une réponse** : elle doit être consignée par écrit dans la colonne prévue.
3. Toute réponse qui contredit une hypothèse du dossier de cadrage déclenche une **révision documentée** des documents concernés.
4. Les questions bloquantes restées ouvertes **suspendent le développement**, pas la conception.
