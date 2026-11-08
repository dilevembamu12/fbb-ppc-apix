# A3 — Plafonds des canaux de paiement en République Démocratique du Congo

> **Statut des données.** Grilles publiques des opérateurs, susceptibles d'évoluer. Elles doivent être **confirmées par contrat** avant d'être paramétrées : un plafond mal saisi produit un refus au pire moment.
> Les montants en francs congolais sont les montants réglementaires. Les équivalents en dollars sont **indicatifs, à 2 800 FC pour 1 USD** — ce taux est à arrêter avec PPC.

---

## 1. Pourquoi cette annexe existe

Le dossier a longtemps reposé sur une phrase simple : « au-delà de 2 500 $ par transaction, aucun canal mobile ne passe ». Cette phrase est utile en réunion, mais **elle est fausse en général**.

En République Démocratique du Congo, le plafond d'un paiement mobile money dépend de **deux paliers qui se cumulent** :

1. le **palier de vérification du compte client** — basique, intermédiaire, vérifié, marchand ;
2. le **palier du compte marchand de PPC** — celui qui reçoit l'argent.

Un paiement passe si les deux le permettent. Autrement dit, le plafond qui bloque une commande est **le plus contraignant des deux**, et il change d'un client à l'autre.

> **Conséquence immédiate pour le dossier :** le plafond de 2 500 $ constaté chez PPC relève très probablement du **compte marchand**, pas du client. Aucun palier client courant n'atteint 2 500 $ par transaction chez Airtel ou Orange. C'est donc un sujet de **contrat**, pas de conception.

---

## 2. Grilles par opérateur et par palier

### 2.1 M-Pesa (Vodacom)

| Palier | Solde maximum | Par transaction | Cumul journalier | Ce que cela permet chez APIX |
|---|---|---|---|---|
| Basique — auto-souscription `*1222#` | 100 000 à 200 000 FC (≈ 36 à 71 $) | Non publié | 100 000 à 200 000 FC | Rien : inférieur au prix d'une course |
| Intermédiaire — carte d'électeur enregistrée | 500 000 FC (≈ 179 $) | Non publié | 500 000 FC | Quelques sacs, jamais un camion |
| Vérifié — contrôle en agence, passeport | 5 000 000 FC (≈ 1 786 $) | Non publié | 5 000 000 FC ; compte Premium en devises : 7 500 $ | **La zone utile** : deux portefeuilles couvrent ≈ 3 570 $ |
| Marchand — numéro RCCM | Non publié | 10 000 000 FC (≈ 3 571 $) | 20 000 000 FC (≈ 7 143 $) | **Le palier à viser pour PPC** |

### 2.2 Airtel Money

| Palier | Solde maximum | Par transaction | Cumul journalier | Ce que cela permet chez APIX |
|---|---|---|---|---|
| Basique | 300 000 FC (≈ 107 $) | 100 000 FC (≈ 36 $) | Non publié | Insuffisant |
| Intermédiaire — pièce d'identité | 1 000 000 FC (≈ 357 $) | 300 000 FC (≈ 107 $) | Non publié | Insuffisant pour un camion |
| Vérifié — contrôle en agence | 7 000 000 FC (≈ 2 500 $) | 2 500 000 FC (≈ 893 $) | Non publié | Trois portefeuilles couvrent ≈ 2 679 $ |
| Marchand — numéro RCCM | Non publié | 10 000 000 FC (≈ 3 571 $) | 25 000 000 FC (≈ 8 929 $) | **Le palier à viser pour PPC** |

### 2.3 Orange Money

| Palier | Solde maximum | Par transaction | Cumul journalier | Ce que cela permet chez APIX |
|---|---|---|---|---|
| Standard | 750 $ | 1 000 $ par dépôt (≈ 2 500 000 FC) | Non publié | Une commande moyenne |
| Premium — identifié légalement | 7 500 $ | Non publié | Réception internationale : 7 500 $ par mois | Confortable |

---

## 3. Ce que ces grilles changent dans le raisonnement

### 3.1 Le vrai plafond n'est pas 2 500 $, c'est le palier du client

Un client au palier **basique** ne peut pas payer un camion de ciment, quel que soit le nombre de portefeuilles qu'il possède : il lui faudrait des dizaines de comptes, et chacun serait refusé séparément. Le multi-portefeuilles ne le sauve pas.

Un client au palier **vérifié** peut, lui, régler une commande de 2 500 à 3 500 $ avec deux ou trois portefeuilles. C'est exactement la tranche que le plafond marchand bloque aujourd'hui.

**Conclusion :** le paiement multi-portefeuilles n'est pas un service pour tous les clients. C'est un service pour les clients **déjà vérifiés**, et il ne remplace pas la montée en palier.

### 3.2 L'action de fond coûte moins cher que le contournement

| Action | Effet | Coût |
|---|---|---|
| Faire passer PPC en **compte marchand business** (RCCM) chez les trois opérateurs | Plafond par transaction multiplié par 3 à 4, cumul journalier de 20 à 25 millions de FC | Administratif : pièces, délai d'ouverture |
| Faire monter les clients réguliers en **palier vérifié** | Plafond du client multiplié par 10 à 20 | Une pièce d'identité et un passage en agence |
| Construire le **paiement multi-portefeuilles** | Couvre la tranche 2 500 à 3 500 $ sans changer de canal | Développement, support, litiges, frais multipliés |

L'ordre de priorité s'impose de lui-même : négocier les paliers d'abord, outiller le multi-portefeuilles ensuite, et seulement s'il reste des clients bloqués.

### 3.3 Ce que l'application doit dire au client

Un plafond n'est pas une panne : c'est une information. L'application doit afficher **le motif et l'action de déblocage**, au moment du choix du moyen de paiement et non après l'échec :

> « Votre compte est vérifié : il plafonne à 893 $ par transaction. Cette commande coûte 3 145 $. **Trois options** : passer en compte marchand, payer par virement, ou régler avec deux portefeuilles. »

Cela suppose que l'application connaisse, pour chaque opérateur : le palier du client, le plafond par transaction, le plafond journalier et le plafond du compte marchand. Ces valeurs sont **saisies dans le back-office, jamais codées en dur**.

---

## 4. Le paiement multi-portefeuilles du même titulaire — proposition à trancher

### 4.1 Ce que c'est, et ce que ce n'est pas

| Mécanisme | Définition | Statut |
|---|---|---|
| Fractionnement sur un même portefeuille | Découper 3 000 $ en deux fois 1 500 $ sur le même compte pour passer sous le plafond | **Interdit** (RG-PAY-16) — l'opérateur y voit un contournement |
| Échéancier | Plusieurs versements dans le temps, commande bloquée jusqu'au paiement intégral | **Autorisé** (RG-PAY-18) |
| Paiement multi-portefeuilles | Le même titulaire règle une commande avec deux ou trois de ses propres comptes, chacun sous son plafond | **Proposé, non tranché** |

### 4.2 Les cinq conditions sans lesquelles il ne faut pas l'ouvrir

1. **Preuve de contrôle de chaque portefeuille** : un code envoyé sur chaque numéro ajouté. Il ne s'agit pas d'un dossier KYC, mais de prouver que le titulaire maîtrise le compte.
2. **Une part par portefeuille, jamais deux sur le même**, et trois portefeuilles au maximum. C'est la ligne qui sépare le service du contournement.
3. **Un plafond global par client et par jour**, indépendant du nombre de portefeuilles — sinon le plafond se multiplie par le nombre de comptes.
4. **Tout ou rien** : le bon n'est émis que si la somme des parts égale le total ; sinon, chaque part est remboursée sur son portefeuille d'origine.
5. **Référence suffixée** `COT-2026-000123-P1`, `-P2`, `-P3`, pour que le rapprochement reste automatique.

### 4.3 Ce qu'il faut vérifier avant de promettre quoi que ce soit

- **Le plafond de 2 500 $ est-il par transaction ou par jour, côté client ou côté marchand ?** C'est la question Q-50. Si le plafond est journalier par titulaire, le multi-portefeuilles **ne sert à rien**.
- **Le contrat marchand autorise-t-il plusieurs portefeuilles pour une même commande ?** C'est la question Q-58. Sans autorisation écrite, le dispositif expose le compte de PPC à une suspension — donc toute la plateforme.
- **Qui supporte les frais de trois transactions ?** Trois paiements, trois jeux de commissions. Cette question, non traitée, suffit à faire tomber le dispositif en réunion.

---

## 5. Questions à enregistrer

| Réf. | Question | Effet si la réponse est négative |
|---|---|---|
| **Q-50** précisée | Le plafond s'applique-t-il par transaction ou par jour, et côté client ou côté marchand ? | Le multi-portefeuilles devient inutile |
| **Q-58** | Le contrat marchand autorise-t-il plusieurs portefeuilles d'un même titulaire pour une même commande ? | Le dispositif ne peut pas être ouvert |
| **Q-59** | PPC peut-il ouvrir un compte marchand business (RCCM) chez les trois opérateurs, et à quel coût ? | Le plafond par transaction reste bloquant à 2 500 $ |
