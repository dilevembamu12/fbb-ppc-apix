Monsieur,

Le 1er décembre, PPC attend une démonstration de bout en bout de l'extension APIX : un client qui obtient un prix, paie, reçoit son bon de commande, se fait livrer et détient une preuve vérifiable. Nous sommes le 25 novembre. Il reste six jours.

Cette lettre a un seul objet : exposer pourquoi l'architecture étendue proposée par notre direction technique ne peut pas répondre à cette échéance, et pourquoi le périmètre que nous portons le peut. Elle ne met pas en cause la qualité de cette proposition. Elle constate une incompatibilité de calendrier, et en tire les conséquences pendant qu'il est encore temps de le faire.

**Ce que l'échéance exige.** Une démonstration de bout en bout n'est pas une projection de diapositives. C'est une chaîne qui fonctionne devant des gens qui achètent du ciment tous les jours : une cotation numérotée, un paiement référencé, un bon nominatif, un chargement contrôlé, une livraison confirmée. Chaque maillon doit tenir — y compris si le réseau tombe, y compris si le client n'a pas de smartphone.

**Ce que l'approche étendue suppose de construire.** Trois chantiers y figurent, et aucun ne se démontre en six jours.

Le premier est une place de marché. Ouvrir une place de marché ne consiste pas à ajouter des vendeurs à un catalogue : il faut un statut d'intermédiaire, un encaissement pour le compte de tiers, une vérification d'identité des vendeurs, un barème de commissions, une facturation multi-émetteurs, un traitement des litiges à trois parties, une isolation des données par vendeur et une modération. Neuf exigences, dont sept sont juridiques, financières ou commerciales. Aucune ne relève du développement : elles demandent des mois et des signatures, pas des développeurs.

Le second est une pile technique de treize briques, dont deux seulement servent au pilote. Un bus d'événements, un cache, une collaboration documentaire, un annuaire unique, un modèle de langage local, du pesage, de la facturation normalisée, de la géolocalisation : chacun est défendable un jour. Aucun n'est nécessaire le 1er décembre. Chacun ajoute en revanche une sauvegarde à vérifier, une mise à jour à suivre et un point de panne supplémentaire le jour de la démonstration.

Le troisième est le remplacement de l'ERP. C'est le point le plus lourd, et il faut le dire sans détour : un ERP ne se change pas sur décision technique. Il porte la comptabilité, les stocks, la fiscalité et les créances. Le remplacer engage la direction financière, les auditeurs et, en pratique, l'administration fiscale — aucun de ces acteurs n'est dans la salle où l'architecture se dessine. Le protocole en préparation entre PPC, FBB et Altius prévoit d'ailleurs l'inverse : la proforma naît dans SAP, la confirmation de paiement y revient (article 2), et PPC en ouvre l'accès (article 4.1). SAP y est le registre ; APIX y est le middleware.

**Le point qui rend la démonstration impossible.** Une chaîne de preuve se démontre avec une cotation, un bon et un code : elle ne dépend d'aucun service externe, et elle tient même quand le réseau tombe. Une place de marché, elle, ne se démontre pas sans vendeurs, sans statut et sans circuit d'encaissement pour autrui. Une démonstration appuyée sur des composants non encore installés s'expose à une panne devant le comité — au pire moment, et sur le sujet même où nous devons inspirer confiance.

**Une considération qui n'est pas technique.** Remplacer l'ERP d'un partenaire n'est pas reçu, en interne, comme un projet d'architecture : c'est reçu comme une redistribution d'attributions. Celui qui le présenterait à ses collègues est notre interlocuteur chez PPC. S'il échouait, il échouerait pour des raisons qui ne sont pas les nôtres — et nous aurions perdu un allié sans avoir rien livré. Nous n'avons aucun intérêt à le mettre dans cette position.

**Ce que le temps restant permet encore de tenir.** Une boutique en ligne PPC, cross-canal, branchée sur l'ERP existant : catalogue et prix, cotation numérotée, paiement par l'intégrateur fourni par PPC, bon nominatif, chargement contrôlé, livraison prouvée, litige et reçu vérifiable. Le tout accessible depuis l'application, le web, WhatsApp, Telegram, l'e-mail, le SMS et l'USSD — un seul dossier, plusieurs entrées. C'est ce que nous avons documenté, maquetté et filmé. C'est ce que nous pouvons montrer le 1er décembre.

**L'objectif de PPC, enfin, tient dans une ligne.** Dix à vingt pour cent des transactions passent déjà par le canal numérique, et sont donc traitées sans agent. Porter plus de la moitié des clients vers ce canal fait mécaniquement baisser le travail de back-office. C'est un objectif de part de clientèle, non une refonte du système d'information — et il se mesure sur un indicateur simple que personne ne conteste.

**Ce que nous demandons.** Trois choses, et elles sont simples :

- un arbitrage écrit avant le 27 novembre sur le périmètre engagé pour le 1er décembre ;
- un seul périmètre présenté à PPC ce jour-là : deux discours le même jour donneraient à PPC l'image d'un fournisseur divisé ;
- une revue de la proposition étendue après le 1er décembre, à froid, avec le recul de la démonstration.

Les briques écartées ne sont pas abandonnées : elles sont datées. Le stockage objet et l'orchestrateur viendront avec les premières reprises sur incident, l'annuaire unique avec la montée en charge, le groupage et le multi-arrêts avec le volume qui les justifie. Nous n'avons rien contre cette architecture. Nous constatons qu'elle n'a pas le temps.

Nous restons à votre disposition pour en débattre avant la fin de la semaine.

Veuillez agréer, Monsieur, l'expression de nos salutations distinguées.
