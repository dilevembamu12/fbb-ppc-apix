# A5 — Reprise du périmètre Digiciment et raccordement à SAP ECC

> **Objet.** APIX ne sera « All-In-One » que le jour où il couvrira, à l'identique et sans régression, ce que Digiciment rend déjà aux clients de PPC — puis ce que Digiciment ne rend pas. Cette annexe établit cette couverture fonction par fonction, fixe la place de SAP ECC dans l'ensemble, et décrit la reprise des comptes et de l'historique.

---

## 1. Ce que cette annexe tranche

1. **Le périmètre à égaler**, établi sur deux sources : le protocole d'accord PKM et ce que l'application publiée fait réellement.
2. **La place de SAP ECC.** Ce qu'APIX lui laisse, ce qu'il lui demande, et ce qui se passe quand les deux ne sont pas d'accord.
3. **La reprise.** Comptes, historique, coexistence, bascule.
4. **La formulation commerciale** à employer devant PPC, et celle à éviter.

---

## 2. Ce que Digiciment fait aujourd'hui

### 2.1 Les sources

| Source | Ce qu'elle établit |
|---|---|
| Protocole d'accord PKM, articles 1, 2 et 4.3 | Le cadre contractuel : commande, proforma, paiement, confirmation, bon de commande |
| Fiche Play Store de l'application (éditeur Altius Technology, mise à jour du 19 avril 2025, plus de 1 000 téléchargements, 4,5/5 sur 8 avis) | Le service tel qu'il est annoncé : « passer vos commandes de ciment » |
| Neuf écrans publiés sur la fiche | Le parcours réel, écran par écran |

### 2.2 Le parcours observé

| Fonction rendue au client | Détail observé | Conséquence pour APIX |
|---|---|---|
| **Deux profils à la connexion** | *Agent commercial* et *Responsable Entrepôt*, choisis avant la saisie du numéro | Deux rôles à prévoir dès l'ouverture, pas seulement le client final |
| **Inscription en quatre étapes** | Information personnelle, adresses, autres informations, photos d'identité | Le même découpage que CLI-02 et CLI-03 |
| **Pièces d'identité** | Recto et verso, par galerie ou appareil photo | Notre CLI-03 est aligné ; à confirmer sur les pièces admises (RG-KYC-04) |
| **Vérification par SMS** | Code à six chiffres saisi dans un écran dédié, avec renvoi possible | Identique à notre CLI-01 à code à usage unique |
| **Rattachement à un dépôt** | « Seul un dépôt validé par PPC peut effectuer des commandes » ; création de dépôt possible depuis l'application | Notre IF-07 console dépôt joue ce rôle côté PPC ; la validation devient un acte tracé, pas une simple case |
| **Tableau de bord** | Commandes en cours, commandes reçues, mes dépôts | Équivalent de notre historique CLI-15, avec des compteurs |
| **Catalogue et panier** | Produits avec prix au sac (par exemple Surecem 9,5 $, Surecast 8 $), quantité, sous-total par ligne | Notre CLI-04 à CLI-07, avec une différence de fond : la cotation numérotée à durée de validité |
| **Option de livraison chiffrée** | Choix « sans livraison » ou « avec livraison », coût affiché, total | Notre option A / option B, avec barème opposable par zone |
| **Paiement** | Carte bancaire (Visa, Mastercard) **et** portefeuilles mobiles (M-Pesa, Airtel Money, Orange Money) | Le point d'égalité à atteindre : nous ne pouvons pas arriver en deçà |
| **Bilingue** | Sélecteur français / anglais | À prévoir côté interface cliente |

### 2.3 Ce que le parcours observé ne montre pas

Ces constats portent sur neuf écrans publiés et sur la description officielle. Ils doivent être confirmés par PPC et Altius avant d'être présentés comme acquis (Q-30 et Q-65).

- **Aucune cotation numérotée à durée de validité.** Le panier affiche un sous-total, pas un prix ferme référencé. C'est la pièce que PPC exige aujourd'hui pour accepter un paiement (Q-51, Q-52).
- **Aucun bon nominatif à usage unique ni QR de chargement.** Rien ne relie la commande au sac qui sort de l'usine.
- **Aucun suivi de course, aucune preuve de livraison, aucun traitement du litige.** La chaîne s'arrête au paiement.
- **Aucun canal sans internet.** L'application suppose une connexion de données.
- **Aucune notion de palier ni de plafond affiché** au client.

> **Point d'attention tiré des avis publics.** Deux avis, espacés de deux ans, signalent une difficulté à finaliser l'inscription. Ce n'est pas un jugement sur le produit : c'est un rappel que l'entrée dans le service est le premier point de renoncement, et que CLI-02 et CLI-03 doivent être traités avec un soin particulier.

---

## 3. Le constat : le périmètre est déjà couvert

| Fonction Digiciment | Où APIX la rend | Planche |
|---|---|---|
| Connexion par numéro, code à usage unique | IF-01 Application client · IF-02 Web client | A.1 |
| Inscription et pièces d'identité | IF-01 · IF-02 | A.1 |
| Rattachement et validation d'un dépôt | IF-01 · IF-07 console dépôt | A.1 |
| Catalogue et prix du profil | IF-01 · IF-02 | A.1 |
| Quantité, option de livraison chiffrée | IF-01 · IF-02 | A.1 |
| Demande de cotation | IF-01 · IF-02 | A.1 |
| Cotation numérotée avec validité | IF-01 · IF-02 · IF-06 back-office | A.2 |
| Choix du moyen de paiement, plafonds compatibles | IF-01 · IF-02 | A.2 |
| Suivi de la confirmation de paiement | IF-01 · IF-02 | A.2 |
| Bon de commande nominatif, QR signé, PDF | IF-01 · IF-03 · IF-05 console de chargement | A.3 |

**La couverture est acquise.** Le travail restant n'est donc pas de construire ces fonctions : c'est de **reprendre les comptes** (§7) et de **les raccorder à SAP** (§5 et §6).

---

## 4. Ce que nous ajoutons, et qui justifie le nom « All-In-One »

C'est ici que l'argument se tient ou s'effondre. Face à Digiciment, la différence n'est pas le nombre d'écrans : c'est la chaîne complète.

| Le service actuel | Ce qu'APIX ajoute |
|---|---|
| Le client commande et paie | Le client commande, paie **et détient une preuve** : bon nominatif à usage unique, chargement pesé et scellé, livraison confirmée, écart traité en litige |
| Un panier avec un sous-total | Une **cotation numérotée, datée, à durée de validité**, qui devient la référence du paiement |
| Un paiement carte ou mobile money | Un paiement **contrôlé contre le palier du client et le plafond du compte marchand**, rapproché, puis transformé en bon |
| Une application mobile | **Cinq canaux** : application, WhatsApp, Telegram, e-mail, SMS et USSD — dont un canal qui fonctionne **sans internet** |
| Un client identifié | Un client **vérifié, gradué, avec un plafond connu** — condition d'accès au crédit et à l'escrow |
| Des commandes | Un **reçu vérifiable** et un historique opposable en cas de contentieux |

La phrase qui doit rester : **ce n'est pas la transaction qu'on vous demandera de produire en cas de contentieux sur 500 sacs, c'est la preuve.**

---

## 5. La place de SAP ECC : deux registres, deux rôles

La question à trancher était : *qui détient la cotation, APIX ou SAP ?* Répondre « les deux » condamne le projet, parce que PPC tiendrait deux registres de ses propres documents commerciaux.

**Réponse retenue : deux registres, deux rôles, jamais la même donnée en double.**

| | SAP ECC | APIX |
|---|---|---|
| Ce qu'il détient | Le document commercial et comptable : prix, taxes, document de vente, facture, créance, encaissement comptable | La preuve d'exécution : cotation émise, paiement encaissé et rapproché, bon émis, chargement, livraison, litige, reçu vérifiable |
| Qui fait foi | Sur le commercial et le comptable | Sur le terrain et la preuve |
| Qui décide du prix | **SAP**, toujours | APIX le reçoit : il ne le calcule jamais et ne l'invente jamais |

### 5.1 Les quatre flux du raccordement

| Réf. | Sens | Contenu | Fréquence |
|---|---|---|---|
| **F1** | SAP → APIX | Produits, prix par profil, conditions, disponibilité | À la demande, avec cache horodaté |
| **F2** | APIX → SAP | Demande de proforma : client, produit, quantité, zone, canal d'origine | À chaque demande de cotation |
| **F3** | APIX → SAP | Confirmation de paiement : référence de cotation, montant, canal, date, identifiant bancaire | À chaque encaissement confirmé |
| **F4** | SAP → APIX | Avoir, annulation, correction de prix | À chaque correction |

### 5.2 Les quatre règles de désaccord

- Si SAP ne confirme pas un prix, **APIX n'affiche pas ce prix**. Il affiche « prix indisponible, réessayez » — jamais un prix estimé.
- Si SAP refuse la création de la proforma, **aucune cotation n'est émise**. Le client voit un message explicite, pas une cotation orpheline.
- Si SAP ne confirme pas un paiement, **le bon n'est pas émis** (RG-CMD-01).
- Tout écart entre les deux registres ouvre un **incident tracé**, jamais une correction silencieuse.

---

## 6. Les contraintes techniques du raccordement

| Point | Exigence |
|---|---|
| Mode d'échange | IDoc, service web ou API : **à arrêter avec la DSI de PPC** (art. 4.1 du protocole). Nous ne présumons aucun mode. |
| Idempotence | Chaque appel porte une clé unique ; un rejeu ne crée pas de doublon de proforma ni de bon |
| Boîte d'envoi transactionnelle | Un événement est enregistré avant d'être envoyé ; rien ne se perd si SAP est indisponible |
| Nouvelle tentative | Reprise avec intervalle croissant, puis file de rebut consultable par l'exploitation (IF-08) |
| Rapprochement | Contrôle quotidien automatique des proformas et des paiements entre les deux registres |
| Réseau | Échanges restreints par liste d'adresses ou tunnel privé ; aucun accès direct exposé sur internet |
| Journalisation | Chaque appel conservé avec sa réponse, son code et sa durée |

**Fenêtre d'indisponibilité de l'ERP.** Si SAP est arrêté, APIX continue d'accepter les demandes de cotation mais **ne les certifie pas** : elles sont mises en attente, le client le voit, et elles sont certifiées au rétablissement. C'est un état d'interface à prévoir dans IF-01 et IF-02, pas une exception.

---

## 7. La reprise des comptes et de l'historique

| Élément | Décision | Motif |
|---|---|---|
| Identités clients (nom, téléphone, adresse, pièces) | **Repris** | Sans identité, pas de plafond, et le client ne peut pas commander |
| Rattachement au dépôt | **Repris** | C'est la condition d'accès à la commande dans le service actuel |
| Historique des commandes | **Repris en lecture seule** | Le client doit retrouver ses commandes passées ; on ne les réécrit pas |
| Soldes et créances en cours | **Non repris** : restent dans SAP | Ce sont des écritures comptables, pas des données applicatives |
| Panier ou brouillon en cours | **Non repris** | Sans valeur contractuelle, et impossible à dater |
| Comptes inactifs depuis 12 mois | **Repris, non notifiés** | Existent, mais on ne relance pas des clients dormants lors d'une bascule |

**Coexistence.** Une seule règle, simple et vérifiable : **un client est actif sur un seul canal de commande à la fois.** Aucune double saisie, aucun client à cheval sur les deux systèmes — sinon les deux registres divergent dès le premier jour.

**Critères de bascule** (tous obligatoires) : identités reprises et contrôlées à 100 % · historique consultable · une commande réelle passée de bout en bout avec paiement et bon · réconciliation SAP à zéro écart sur sept jours consécutifs · procédure de retour arrière écrite et testée.

---

## 8. Ce que la reprise du service suppose

Le protocole d'accord fait d'Altius **une partie à l'accord**, avec ses propres engagements (art. 4.3 : adapter et maintenir Digiciment, implémenter les appels vers APIX, garantir l'expérience mobile et web). La reprise du service par APIX ne se décrète donc pas dans un document d'architecture. Trois actes sont nécessaires :

1. **Connaître la durée de l'engagement** entre PPC et Altius (**Q-32**, non tranchée à ce jour).
2. **Établir un avenant** au protocole, signé des trois parties, précisant le périmètre repris et le calendrier.
3. **Obtenir d'Altius l'export des comptes et la documentation de son API** — sans quoi la reprise du §7 n'a pas de source.

**Tant que ces trois points ne sont pas réglés, APIX ne peut pas être le seul canal : il doit coexister.** C'est une contrainte de calendrier, pas de volonté.

---

## 9. La formulation à employer

Le sujet se défend sur la couverture, jamais sur l'éviction. La nuance n'est pas cosmétique : elle détermine qui doit arbitrer.

| Ce qui affaiblit la position | Ce qui la tient |
|---|---|
| Parler de remplacement d'un fournisseur en place | Parler de **couverture de la chaîne complète**, du prix jusqu'au sac livré |
| Comparer deux applications sur leurs écrans | Comparer **ce que PPC obtient** : une preuve opposable en cas de contentieux |
| Poser PPC en arbitre entre deux prestataires | Laisser PPC constater lui-même ce qui manque au service actuel |

**Le principe, en une ligne : quand nous parlons de remplacement, nous demandons à PPC de choisir entre deux fournisseurs. Quand nous parlons de couverture, nous lui demandons de constater ce qui lui manque.** La seconde position ne dépend d'aucun arbitrage.

---

## 10. Ce que cette annexe change dans nos documents

| Document | Modification |
|---|---|
| 03 — Architecture technique | Chapitre « Raccordement à l'ERP de PPC » : les quatre flux du §5.1, les règles du §5.2, les contraintes du §6 |
| 05 — Présentation du MVP | Nommer la reprise dans les fiches IF-01 et IF-02 |
| 04 — Argumentaire | Conserver la différenciation par la preuve, sans vocabulaire d'éviction |
| A2 — Questions ouvertes | Q-62 à Q-65 ajoutées ; Q-30 à Q-33 deviennent bloquantes pour la reprise |
| Protocole d'accord PKM | Le protocole écrit « Digicement » ; le nom publié est **Digiciment**. À corriger avant signature. |

---

## 11. Ce qui reste à trancher

| Réf. | Question | Qui décide | Effet si non tranchée |
|---|---|---|---|
| **Q-62** | Quel mode d'échange SAP : IDoc, service web ou API ? | DSI de PPC | Aucun raccordement possible ; le §6 reste une intention |
| **Q-63** | Quel mandant SAP pour les tests, et sous quel délai ? | PPC | Pas de recette possible avant la mise en production |
| **Q-64** | Altius fournira-t-il un export des comptes et la documentation de son API ? | PPC et Altius | La reprise du §7 n'a pas de source |
| **Q-65** | Digiciment dispose-t-il d'une version web, et sera-t-elle maintenue ? | PPC et Altius | Le positionnement d'IF-02 reste imprécis |
| Q-30 à Q-33 | Périmètre réellement utilisé, intégrations existantes, engagement contractuel, retours clients | PPC | La couverture reste déduite, non prouvée |

---

## 12. Recette de la reprise

| Critère | Preuve attendue |
|---|---|
| Aucune fonction perdue | Chaque ligne du tableau §2.2 a été exercée sur APIX, en présence d'un utilisateur de Digiciment |
| Prix jamais inventé | Test : SAP indisponible ⇒ aucun prix affiché, aucune cotation émise |
| Pas de doublon | Le rejeu du même message F2 dix fois produit une seule proforma |
| Paiement réconcilié | Un paiement par carte et un paiement par portefeuille mobile aboutissent au même bon, avec la même traçabilité |
| Dépôt validé | Un dépôt non validé par PPC ne peut pas commander, et l'écran explique pourquoi |
| Historique consultable | Un client retrouve ses trois dernières commandes dans APIX |
| Bascule réversible | Retour arrière exécuté une fois, chronométré, documenté |
