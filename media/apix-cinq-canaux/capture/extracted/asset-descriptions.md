# Inventaire des assets — matière fournie par le client

Aucune capture de site : toutes les images sont nos propres planches de wireframes, dessinées en
Python, en niveaux de gris avec un seul accent orange. Elles sont au format 2× (rendu net en 1080p).

## Canaux — le cœur du film (planches de parité)

| Fichier | Ce que c'est | Où il sert |
|---|---|---|
| `p22-parite-ussd.png` | Deux écrans USSD côte à côte : menu `*144#` et cotation dans la session | Séquence USSD : le canal sans internet |
| `p23-parite-sms.png` | Deux écrans SMS : `COT 200 GOMBE` puis le bon en code de retrait 481902 | Séquence SMS : le bon devient un code |
| `p24-parite-telegram.png` | Deux écrans Telegram : bot avec claviers, puis bon en fichier avec QR | Séquence Telegram |
| `p25-parite-email.png` | Écran de messagerie large : e-mail de cotation, lien signé, PDF joint | Séquence e-mail, et seul écran large des canaux |
| `p14-whatsapp-identification-cotation.png` | WhatsApp : identification par code, commande guidée par boutons | Séquence WhatsApp, ouverture |
| `p15-whatsapp-paiement-bon.png` | WhatsApp : carte de cotation, choix du canal de paiement, bon | Séquence WhatsApp, résolution |

## Application client — la preuve

| Fichier | Ce que c'est | Où il sert |
|---|---|---|
| `p03-client-bon-reception.png` | Bon de commande avec QR, puis validation de réception | Le bon et la validation par le client |
| `p01-client-catalogue-cotation.png` | Catalogue avec prix et demande de cotation | Contexte : le prix vient avant l'argent |
| `p02-client-cotation-paiement.png` | Cotation certifiée avec compte à rebours, puis choix du moyen de paiement | Le plafond de 2 500 $ et l'alternative |
| `p20-geolocalisation-suivi-preuve.png` | Suivi sur carte et dossier de preuve géolocalisé | Réponse à « où est mon camion » |

## Côté PPC — la main et le contrôle

| Fichier | Ce que c'est | Où il sert |
|---|---|---|
| `p05-chargement-controle.png` | Console de chargement : contrôle du bon, verdict REFUSÉ motivé | La console accepte un QR **ou** un code |
| `p11-canaux-tableau.png` | Console des canaux : états, volumes, coûts, conditions d'ouverture | Le pilotage des cinq canaux |
| `p12-canaux-routage.png` | Règles de routage événement × canal × délai × repli | L'automatisation des messages |
| `p13-canaux-conversations.png` | Reprise humaine d'une conversation par un agent | Le repli humain |
| `p07-backoffice-pilotage.png` | Tableau de bord PPC : commandes, encaissements, litiges | Le pilotage |
| `p09-backoffice-litige.png` | Instruction d'un litige avec montants retenu et libéré | La réponse à « qui paie les manquants » |
| `p18-canaux-modeles.png` | Modèles de messages par canal et par langue | Configuration des canaux |
| `p19-canaux-bac-a-sable.png` | Bac à sable : test de bout en bout avant ouverture | Condition d'ouverture d'un canal |

## Chauffeur et dépôt

| Fichier | Ce que c'est | Où il sert |
|---|---|---|
| `p04-chauffeur.png` | Trois écrans chauffeur : courses, chargement, livraison hors ligne | Le terrain, sans réseau |
| `p21-geolocalisation-chauffeur.png` | Détail de course et positions transmises hors ligne | La géolocalisation côté chauffeur |
| `p10-depot-reception.png` | Console dépôt : réception d'un bon, remise de marchandise | Le dépôt |

## Divers (probablement non utilisés)

`p06-transporteur-course.png`, `p08-backoffice-sans-cotation.png`, `p16-flux-conversation.png`,
`p17-flux-automatisation.png` — utiles si le film a besoin d'un schéma de flux plutôt que d'un écran.

## Photographies — 8 fichiers dans ce dossier

Images libres de droits (Wikimedia, CC ou domaine public) : route et transport, chargement de sacs,
paiement mobile dans la rue, kiosque. Elles servent de fonds d'ambiance pour les inserts de douleur,
jamais de preuve produit. Les crédits figurent dans le dossier PPC (`assets/credits.json`).
