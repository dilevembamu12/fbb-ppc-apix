# 06 — Note de positionnement : une boutique en ligne, pas une place de marché

> **Objet.** Deux propositions techniques sont aujourd'hui sur la table pour répondre au même besoin exprimé par PPC. Cette note expose pourquoi celle que nous portons — une **boutique en ligne PPC, cross-canal, branchée sur l'ERP existant** — répond mieux à la demande, au calendrier et à l'organisation de PPC que la proposition d'architecture étendue. Elle n'oppose pas des personnes : elle compare deux périmètres et deux moments.

---

## 1. Ce que PPC demande

Trois phrases, qui viennent de ses propres mots :

1. **Vendre en ligne**, pas héberger des vendeurs : PPC veut maîtriser sa boutique, son prix, son bon.
2. **Faire baisser le manuel.** Le traitement d'une commande est aujourd'hui massivement manuel ; l'objectif est d'en automatiser la moitié au moins. *(Le 90 % actuel est une estimation à mesurer avant d'être inscrite dans un engagement.)*
3. **Ne pas perdre la preuve.** Un client qui paie doit pouvoir prouver qu'il a payé, et PPC doit pouvoir prouver ce qui est sorti de l'usine.

Aucune de ces trois phrases ne demande une place de marché. Aucune ne demande de remplacer l'ERP.

---

## 2. Deux lectures du même besoin

| | **Boutique en ligne PPC** *(notre proposition)* | **Place de marché étendue** *(proposition à arbitrer)* |
|---|---|---|
| Qui vend | PPC | PPC **et** des vendeurs tiers |
| Qui encaisse | PPC, sur son compte | La plateforme, **pour le compte** de tiers |
| Qui est responsable du produit livré | PPC | Le vendeur tiers ; la plateforme n'est qu'intermédiaire |
| Système de référence | **L'ERP de PPC reste le registre** | Une nouvelle plateforme devient le registre |
| Ce qu'il faut construire | une chaîne de vente et une preuve | une chaîne de vente, une preuve, **et** un modèle d'intermédiation |
| Ce que PPC doit décider | ses prix, ses canaux | ses prix, ses canaux, **son statut, ses commissions, ses responsabilités** |

Le point décisif est la troisième ligne du bas : la place de marché ne change pas seulement la technique, elle change **la nature juridique et financière** de PPC dans la transaction. Ce n'est pas une décision d'architecte.

---

## 3. Ce qu'une place de marché exige réellement

Voici ce qu'il faut avoir avant d'ouvrir une place de marché — et qui n'a rien à voir avec le code.

| Exigence | Ce qu'elle impose à PPC | Ce qu'elle nous impose |
|---|---|---|
| **Statut d'intermédiaire** | Passer de vendeur à intermédiaire sur une partie des flux : mandat, responsabilité, assurances | Une rédaction contractuelle par un juriste, et l'accord écrit de PPC |
| **Encaissement pour autrui** | Compte séquestre, répartition vers les vendeurs, rapprochement multi-parties | Un circuit financier entièrement différent de celui du MVP |
| **KYC des vendeurs** | Vérifier l'identité, le RCCM et la solvabilité de chaque vendeur, pas seulement des acheteurs | Un second parcours de vérification, un second palier de plafonds |
| **Commissions** | Fixer un taux, le facturer, le déclarer — et donc facturer PPC à PPC | Facturation de commission, TVA, écritures dédiées |
| **Facturation du produit** | La facture doit être émise **par le vendeur**, jamais par la plateforme | Un modèle de facturation multi-émetteurs |
| **Litiges tripartites** | Arbitrer entre un acheteur et un vendeur tiers, pas entre un client et soi-même | Un module de litige à trois parties, avec preuve de chaque côté |
| **Catalogue et stock par vendeur** | Prix concurrents sur sa propre plateforme | Isolation des données par vendeur (« multi-tenant ») |
| **Notation et modération** | Porter la réputation de vendeurs qu'il n'emploie pas | Avis, modération, signalement |
| **Effet réseau** | Attirer des vendeurs avant d'avoir des acheteurs | Un problème commercial, pas technique : une place vide n'a aucune valeur |

**Neuf exigences, dont sept sont juridiques, financières ou commerciales.** Les traiter demande des mois et des signatures, pas des développeurs.

Une boutique en ligne, à l'inverse, n'en demande **aucune** : PPC vend, PPC encaisse, PPC est responsable, PPC décide. C'est précisément ce qu'il demande.

---

## 4. Le sur-périmètre de la proposition technique

Le schéma d'architecture présenté ajoute, au-delà de la chaîne de vente, l'ensemble suivant :

| Composant ou fonction ajoutés | Demandé par PPC ? | Utile au pilote ? |
|---|---|---|
| Bus d'événements (Kafka) et sa console | Non | **Non** — le volume d'un pilote ne le justifie pas |
| Stockage objet (MinIO) | Non | **Oui, à terme** — pour archiver les documents commerciaux |
| Cache et files (Redis) | Non | Marginal au pilote |
| Collaboration documentaire (Nextcloud) | Non | **Non** — hors du besoin |
| Annuaire et authentification unique (Keycloak) | Non | Utile en V2, superflu au pilote |
| Modèle de langage local (Ollama) et base de connaissances | **Non tranché par PPC** (Q-57) | **Non** — la décision n'appartient pas à FBB |
| Orchestrateur de workflows (n8n) | Non | Oui, si des reprises sur incident sont nécessaires |
| Pesage, portique, Factur-X, géolocalisation, anti-fraude, programmes de fidélité | Non | **Non** — ce sont des projets distincts |

Sur treize briques, **deux seulement sont utiles au pilote**. Les autres ne sont pas mauvaises : elles sont **prematurées**. La différence entre « utile un jour » et « utile maintenant » est exactement ce qui sépare un pilote livré d'un chantier sans fin.

---

## 5. Le coût réel d'un composant de plus

Chaque brique supplémentaire n'est pas une ligne sur un schéma. C'est :

- **une compétence à trouver** — et à garder ;
- **une sauvegarde à vérifier** ;
- **une faille à corriger** chaque mois ;
- **un coût d'exploitation** récurrent ;
- **un point de panne de plus** le jour de la démonstration.

Un exemple concret, observé sur la machine cible : le disque est à **88 % d'occupation**. Un bus d'événements dont la rétention n'est pas bornée, un stockage objet et des images de conteneurs remplissent les quelques dizaines de gigaoctets restants — pendant un pilote, c'est-à-dire au pire moment.

**Une architecture ne se juge pas à ce qu'elle permet, mais à ce qu'elle coûte à maintenir quand personne ne regarde.**

---

## 6. Le point le plus lourd : remplacer l'ERP de PPC

C'est ici que la proposition devient un autre projet.

### 6.1 Techniquement

Un ERP n'est pas une application parmi d'autres : il porte la comptabilité, les stocks, la fiscalité, les créances. Le remplacer suppose la reprise des données historiques, la réconciliation des soldes, la reconstruction des interfaces, la formation des équipes et un audit de sortie. Ce sont des années, pas des semaines.

### 6.2 Administrativement

Le registre comptable d'une entreprise ne se change pas sur décision technique : il engage la direction financière, les auditeurs et, en pratique, le fisc. Aucun de ces acteurs n'est dans la salle où l'architecture a été dessinée.

### 6.3 Le protocole dit déjà le contraire

L'accord en préparation entre PPC, FBB et Altius est explicite : **la proforma est générée dans SAP**, **la confirmation de paiement revient dans SAP** (article 2), et PPC met à disposition l'accès technique à son ERP (article 4.1). SAP y est le registre ; APIX y est le **middleware**.

Proposer de remplacer SAP, c'est donc proposer de renégocier un document que PPC est en train de signer. Ce n'est pas impossible — c'est un autre projet, avec d'autres signatures.

### 6.4 Le risque humain, qui est le vrai risque

Un projet qui retire à une direction la maîtrise de son outil n'est pas reçu comme un projet technique : il est reçu comme **une redistribution d'attributions**. Dans une organisation où chaque direction défend son périmètre, ce sont les porteurs internes qui en paient le prix.

Concrètement : notre interlocuteur chez PPC serait celui qui présente à ses collègues un projet qui leur retire leur ERP. S'il échoue, il échoue pour des raisons qui ne sont pas les nôtres — et nous aurons perdu un allié sans avoir rien livré.

**Nous n'avons aucun intérêt à mettre notre propre interlocuteur en danger.** C'est un argument commercial autant qu'humain : un projet porté par quelqu'un qui le défend vaut dix projets imposés.

---

## 7. Cinq autres raisons

**1. Le calendrier.** L'échéance est fixée, et elle est proche. Une place de marché et un remplacement d'ERP se comptent en années ; une chaîne de vente se compte en semaines. La proposition technique n'est pas fausse, elle est **hors du temps disponible**.

**2. La démonstration.** Un modèle de langage ou un bus d'événements peut tomber en panne pendant une séance, et ne se répare pas devant un comité de direction. La chaîne de preuve se démontre avec une cotation, un bon et un code — elle ne dépend d'aucun service externe.

**3. L'adoption.** Le vrai enjeu de PPC n'est pas la technologie, c'est l'usage : passer d'un processus manuel à un processus outillé. Une pile plus lourde ne fait jamais adopter un outil ; un parcours plus court, si.

**4. La mesure.** On ne peut pas promettre « 50 % d'automatisation » sans avoir mesuré le point de départ. Notre proposition commence par instrumenter le processus existant ; la sienne commence par le remplacer, donc sans référence.

**5. La réversibilité.** Notre approche laisse PPC libre : données exportables, ERP inchangé, aucun verrou. C'est un argument de confiance, et il se retourne en notre faveur le jour où PPC compare.

---

## 8. Ce que nous proposons

| | |
|---|---|
| **Quoi** | Une boutique en ligne PPC : catalogue, cotation numérotée, paiement référencé, bon nominatif, chargement, livraison prouvée, litige, reçu vérifiable |
| **Où** | Application, web, et cinq canaux conversationnels — un seul dossier, plusieurs entrées |
| **Avec quoi** | Le strict nécessaire : une base de données, un moteur de règles, un adaptateur vers l'ERP de PPC |
| **Sans** | Ni bus d'événements, ni modèle de langage, ni collaboration documentaire, ni remplacement d'ERP |
| **Pour prouver quoi** | Qu'une commande de ciment peut être payée et retirée sans qu'aucun des deux côtés ne perde la preuve |

---

## 9. Ce qu'il faut demander à PPC

| Réf. | Question | Pourquoi elle est bloquante |
|---|---|---|
| **Q-62** | Quel mode d'échange avec SAP : IDoc, service web ou API ? | Sans lui, le raccordement reste une intention |
| **Q-63** | Quel mandant de test, et sous quel délai ? | Sans lui, aucune recette n'est possible |
| **Q-66** | PPC veut-il vendre lui-même, ou accueillir des vendeurs tiers ? | C'est la question qui sépare une boutique d'une place de marché |
| **Q-67** | Quel est le volume réel de commandes traitées manuellement aujourd'hui ? | Sans point de départ, « 50 % d'automatisation » n'est pas mesurable |

---

## 10. Ce que cette note ne dit pas

Trois choses, pour rester honnête :

- **La proposition technique voit juste sur le fond.** La traçabilité, l'automatisation des tâches répétitives, la souveraineté des données et l'utilité d'une intelligence locale sont de vraies questions. Elles ne sont pas fausses : elles sont **prématurées**.
- **Rien n'est perdu.** MinIO, un orchestrateur de workflows et l'authentification unique trouveront leur place en V2, quand le volume et les partenaires le justifieront. Les écarter aujourd'hui ne les condamne pas.
- **La décision appartient à PPC**, pas à FBB ni à son directeur technique. Notre rôle est de lui poser la question qui tranche — vendre soi-même, ou accueillir des vendeurs — et de lui montrer ce que chacune des deux réponses engage.
