# A5 — Reprise du périmètre Digicement et raccordement à SAP ECC

> **Objet.** APIX ne sera « All-In-One » que le jour où il couvrira, à l'identique et sans régression, ce que Digicement fait déjà pour les clients de PPC — puis tout ce que Digicement ne fait pas. Cette annexe établit cette couverture fonction par fonction, fixe la place de SAP ECC dans l'ensemble, et décrit la reprise des comptes et de l'historique. Elle tranche aussi une question de formulation, qui n'est pas cosmétique.

---

## 1. Ce que cette annexe tranche

1. **Le périmètre à égaler.** La liste des fonctions que Digicement rend aujourd'hui, établie sur le seul document qui fait foi : le protocole d'accord PKM.
2. **La place de SAP ECC.** Ce qu'APIX lui laisse, ce qu'il lui demande, et ce qui se passe quand les deux ne sont pas d'accord.
3. **La reprise.** Comptes, historique, coexistence, bascule.
4. **La formulation.** Couvrir le périmètre de Digicement est nécessaire ; l'annoncer comme une éjection ne l'est pas, et nous affaiblit.

---

## 2. Ce que Digicement fait aujourd'hui

Le MoU PKM est le seul document contractuel disponible. Ses articles 1, 2 et 4.3 décrivent précisément le service rendu aux clients de PPC.

| Fonction rendue au client | Ce que dit le MoU | Ce que cela impose à APIX |
|---|---|---|
| Passer une commande de ciment | « permettant aux clients de PPC de passer des commandes de ciment » (préambule) | Un catalogue consultable, par profil de prix, depuis le mobile et le web |
| Créer une demande de proforma | « Créer une demande de proforma » (art. 2) | Un formulaire produit, quantité, zone, avec calcul de prix côté serveur |
| Obtenir une proforma numérotée | « Générer automatiquement la proforma dans SAP ECC » (art. 2) | Une cotation référencée, avec durée de validité, répercutée dans SAP |
| Payer en ligne | « en ligne via les canaux bancaires intégrés » (art. 2) | Un choix de moyen de paiement et un suivi de statut |
| Payer au guichet | « ou au guichet d'une banque partenaire » (art. 2) | Une référence de paiement et un rapprochement sur relevé |
| Recevoir la confirmation | « Recevoir la confirmation de paiement dans SAP » (art. 2) | Un statut de paiement tracé, répercuté dans SAP |
| Obtenir son bon de commande | « Générer, exporter en PDF ou imprimer le bon de commande » (art. 2) | Un bon nominatif, en PDF et imprimable |
| Utiliser mobile **et** web | « l'expérience utilisateur côté mobile et côté web » (art. 4.3) | Deux interfaces clientes, pas une |

**Ce que le MoU ne dit pas**, et qu'il faut demander à PPC avant de promettre quoi que ce soit : gestion des remises et barèmes, compte entreprise multi-utilisateurs, historique des commandes, consultation de stock, gestion des litiges, notifications. Ce sont les questions Q-30 à Q-33, déjà ouvertes dans l'annexe A2.

> **Hypothèse à confirmer.** Tout ce qui précède est déduit d'un protocole d'accord, pas d'une spécification Digicement. Tant que PPC et ALTUS n'ont pas remis la liste réelle des fonctions utilisées (Q-30), notre couverture est juste sur le papier et non prouvée sur le terrain.

---

## 3. Le constat : le périmètre est déjà couvert

Le périmètre décrit ci-dessus est exactement celui de l'interface client d'APIX. Il n'y a rien à inventer, il y a à nommer.

| Fonction Digicement | Où APIX la rend | Planche |
|---|---|---|
| Catalogue et prix du profil | IF-01 Application client · IF-02 Web client | A.1 |
| Demande de cotation | IF-01 · IF-02 | A.1 |
| Cotation numérotée avec validité | IF-01 · IF-02 · IF-06 back-office | A.2 |
| Choix du moyen de paiement, plafonds compatibles | IF-01 · IF-02 | A.2 |
| Suivi de la confirmation de paiement | IF-01 · IF-02 | A.2 |
| Bon de commande nominatif, QR signé, PDF | IF-01 · IF-03 chargement · IF-05 console de chargement | A.3 |

**La couverture est donc acquise.** Le travail restant n'est pas de construire ces fonctions : c'est de **reprendre les comptes** (§7) et de **les raccorder à SAP** (§5 et §6).

---

## 4. Ce qu'APIX ajoute, et qui justifie le nom « All-In-One »

C'est ici que l'argument se tient ou s'effondre. Face à Digicement, la différence n'est pas le nombre d'écrans : c'est la chaîne complète.

| Ce que Digicement fait | Ce qu'APIX fait en plus |
|---|---|
| Le client commande | Le client commande et **prouve** : le bon porte un QR ou un code, il est nominatif et à usage unique |
| Le client paie | Le paiement est **référencé à la cotation**, contrôlé contre les plafonds de son palier, et rapproché |
| Une transaction | Une **chaîne de responsabilité** : chargement pesé et scellé, course suivie, livraison confirmée, écart traité en litige |
| Un canal, l'application | **Cinq canaux** : application, WhatsApp, Telegram, e-mail, SMS et USSD — dont un canal qui fonctionne **sans internet** |
| Un client | Un client avec **une identité vérifiée et un plafond connu**, ce qui est la condition d'accès au crédit et à l'escrow |
| Des commandes | Un **reçu vérifiable** et un historique opposable en cas de contentieux |

C'est la phrase qui doit rester : **ce n'est pas la transaction qu'on vous demandera de produire en cas de contentieux sur 500 sacs, c'est la preuve.**

---

## 5. La place de SAP ECC : deux registres, deux rôles

La question à trancher était : *qui détient la cotation, APIX ou SAP ?* Répondre « les deux » condamne le projet, parce que PPC tiendrait deux registres de ses propres documents commerciaux.

**Réponse retenue : deux registres, deux rôles, jamais la même donnée en double.**

| | SAP ECC | APIX |
|---|---|---|
| Ce qu'il détient | Le document commercial et comptable : prix, taxes, document de vente, facture, créance, encaissement comptable | La preuve d'exécution : cotation émise, paiement encaissé et rapproché, bon émis, chargement, livraison, litige, reçu vérifiable |
| Qui fait foi | Sur le commercial et le comptable | Sur le terrain et la preuve |
| Qui décide du prix | **SAP**, toujours | APIX le reçoit, ne le calcule jamais et ne l'invente jamais |

### 5.1 Les quatre flux du raccordement

| Réf. | Sens | Contenu | Fréquence |
|---|---|---|---|
| **F1** | SAP → APIX | Produits, prix par profil, conditions, disponibilité | À la demande, avec cache horodaté |
| **F2** | APIX → SAP | Demande de proforma : client, produit, quantité, zone, canal d'origine | À chaque demande de cotation |
| **F3** | APIX → SAP | Confirmation de paiement : référence de cotation, montant, canal, date, identifiant bancaire | À chaque encaissement confirmé |
| **F4** | SAP → APIX | Avoir, annulation, correction de prix | À chaque correction |

### 5.2 La règle en cas de désaccord

- Si SAP ne confirme pas un prix, **APIX n'affiche pas ce prix**. Il affiche « prix indisponible, réessayez » — jamais un prix estimé.
- Si SAP refuse la création de la proforma, **aucune cotation n'est émise**. Le client voit un message explicite, pas une cotation orpheline.
- Si SAP ne confirme pas un paiement, **le bon n'est pas émis** (RG-CMD-01).
- Tout écart entre les deux registres ouvre un **incident tracé**, jamais une correction silencieuse.

---

## 6. Les contraintes techniques du raccordement

| Point | Exigence |
|---|---|
| Mode d'échange | IDoc, service web ou API : **à arrêter avec la DSI de PPC** (art. 4.1 du MoU). Nous ne présumons aucun mode. |
| Idempotence | Chaque appel porte une clé unique ; un rejeu ne crée pas de doublon de proforma ni de bon |
| Boîte d'envoi transactionnelle | Un événement est enregistré avant d'être envoyé ; rien ne se perd si SAP est indisponible |
| Nouvelle tentative | Reprise avec intervalle croissant, puis file de rebut consultable par l'exploitation (IF-08) |
| Rapprochement | Contrôle quotidien automatique des proformas et paiements entre les deux registres |
| Réseau | Échanges restreints par liste d'adresses ou tunnel privé ; aucun accès direct exposé sur internet |
| Journalisation | Chaque appel conservé avec sa réponse, son code et sa durée |

**Fenêtre d'indisponibilité SAP.** Si SAP est arrêté, APIX continue d'accepter les demandes de cotation mais **ne les certifie pas** : elles sont mises en attente, le client le voit, et elles sont certifiées au rétablissement. C'est un état d'interface à prévoir dans IF-01 et IF-02, pas une exception.

---

## 7. La reprise des comptes et de l'historique

| Élément | Décision | Motif |
|---|---|---|
| Identités clients (nom, téléphone, adresse, pièces) | **Repris** | Sans identité, pas de plafond, et le client ne peut pas commander |
| Historique des commandes | **Repris en lecture seule** | Le client doit retrouver ses commandes passées ; on ne les réécrit pas |
| Soldes et créances en cours | **Non repris** : restent dans SAP | Ce sont des écritures comptables, pas des données applicatives |
| Panier ou brouillon en cours | **Non repris** | Sans valeur contractuelle, et impossible à dater |
| Comptes inactifs depuis 12 mois | **Repris, non notifiés** | Existent, mais on ne relance pas des clients dormants lors d'une bascule |

**Coexistence.** Une seule règle, simple et vérifiable : **un client est actif sur un seul canal de commande à la fois.** Aucune double saisie, aucun client à cheval sur les deux systèmes — sinon les deux registres divergent dès le premier jour.

**Critères de bascule** (tous obligatoires) : identités reprises et contrôlées à 100 % · historique consultable · une commande réelle passée de bout en bout avec paiement et bon · réconciliation SAP à zéro écart sur sept jours consécutifs · procédure de retour arrière écrite et testée.

---

## 8. Ce que la substitution suppose, et qui n'est pas technique

Le MoU fait d'ALTUS **une partie au protocole**, avec ses propres engagements (art. 4.3 : adapter et maintenir Digicement, implémenter les appels vers APIX, garantir l'expérience mobile et web). Retirer Digicement de l'équation ne se décrète donc pas dans un document d'architecture :

1. il faut connaître la durée de l'engagement entre PPC et ALTUS (**Q-32**, non tranchée à ce jour) ;
2. il faut un avenant au protocole, signé des trois parties ;
3. il faut qu'ALTUS remette un export des comptes et la documentation de son API actuelle — sans quoi la reprise du §7 n'a pas de source.

**Tant que ces trois points ne sont pas réglés, APIX ne peut pas être le seul canal : il doit coexister.** C'est une contrainte de calendrier, pas de volonté.

---

## 9. La formulation : couvrir n'est pas annoncer

Le dossier affirme, dans son argumentaire, que la couverture fonctionnelle est nécessaire. Il affirme aussi l'inverse d'une annonce d'éjection, et il a raison :

| Ce qu'il ne faut pas dire | Ce qu'il faut dire |
|---|---|
| « Nous allons remplacer Digicement » | « APIX couvre la chaîne complète, du prix jusqu'au sac livré » |

La première formule met PPC en position d'arbitre entre deux fournisseurs, et donne à Digicement un statut d'égal qu'il n'a pas. La seconde ne parle que de ce que PPC obtient. **C'est le même travail, présenté du bon côté.**

---

## 10. Ce que cette annexe change dans nos documents

| Document | Modification attendue |
|---|---|
| 03 — Architecture technique | Ajouter le chapitre « Raccordement à l'ERP de PPC » : les quatre flux du §5.1, les règles du §5.2, les contraintes du §6 |
| 05 — Présentation du MVP | Nommer la reprise : IF-01 et IF-02 couvrent le périmètre Digicement, et le dire dans la fiche d'interface |
| 04 — Argumentaire | Conserver la différenciation par la preuve ; retirer toute formulation d'éjection |
| Tous | Orthographe : **Digicement** — et non la variante en « -ciment » employée jusqu'ici dans nos documents. Le nom du produit est celui du protocole d'accord. |
| A2 — Questions ouvertes | Q-30 à Q-33 deviennent bloquantes pour la reprise ; ajouter Q-62 à Q-64 ci-dessous |

---

## 11. Ce qui reste à trancher

| Réf. | Question | Qui décide | Effet si non tranchée |
|---|---|---|---|
| **Q-62** | Quel mode d'échange SAP : IDoc, service web ou API ? | DSI de PPC | Aucun raccordement possible ; le §6 reste une intention |
| **Q-63** | Quel mandant SAP pour les tests, et sous quel délai ? | PPC | Pas de recette possible avant la production |
| **Q-64** | ALTUS fournira-t-il un export des comptes et la documentation de son API ? | PPC et ALTUS | La reprise du §7 n'a pas de source |
| Q-30 à Q-33 | Périmètre réellement utilisé, intégrations existantes, engagement contractuel, retours clients | PPC | La couverture reste déduite, non prouvée |

---

## 12. Recette de la reprise

| Critère | Preuve attendue |
|---|---|
| Aucune fonction perdue | Chaque ligne du tableau §2 a été exercée sur APIX, en présence d'un utilisateur de Digicement |
| Prix jamais inventé | Test : SAP indisponible ⇒ aucun prix affiché, aucune cotation émise |
| Pas de doublon | Le rejeu du même message F2 dix fois produit une seule proforma |
| Paiement réconcilié | Un paiement en ligne et un paiement au guichet aboutissent au même bon, avec la même traçabilité |
| Historique consultable | Un client retrouve ses trois dernières commandes Digicement dans APIX |
| Bascule réversible | Retour arrière exécuté une fois, chronométré, documenté |
