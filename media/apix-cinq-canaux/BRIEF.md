---
workflow: product-launch-video
flow: automation
storyboard: yes
message: "Une seule cotation, un seul bon — quel que soit le canal utilisé par le client"
destination: embed
aspect: 1920x1080
language: fr
audience: "Direction générale de PPC, et responsables commerciaux et logistique"
length: 90s
angle: parite-cinq-canaux
---

## Intent

Un film de cadrage de 90 secondes qui **montre** la plateforme APIX étendue, interface par
interface, autour d'une seule idée : la même cotation et le même bon de commande sont accessibles
sur cinq canaux — application, WhatsApp, Telegram, e-mail, SMS et USSD.

Ce n'est pas une promo : c'est une visite guidée. Les douleurs relevées en réunion servent de fil
rouge discret — « où est mon camion », « combien de sacs sont arrivés », « qui paie les manquants » —
et chaque écran montre comment la chaîne de preuve y répond.

Ton demandé par le client : motion design performant et captivant, voix off, sonorités d'attention
et effets sonores. Registre sobre et institutionnel : on parle à une direction générale, pas à un
public réseaux sociaux.

## Assets

- `../../PPC/assets/wireframes/p22-parite-ussd.png` — USSD : menu principal, cotation et paiement dans la session
- `../../PPC/assets/wireframes/p23-parite-sms.png` — SMS : commande, paiement, bon en code de retrait
- `../../PPC/assets/wireframes/p24-parite-telegram.png` — Telegram : commande par bot, cotation et bon
- `../../PPC/assets/wireframes/p25-parite-email.png` — e-mail : cotation et lien de paiement signé
- `../../PPC/assets/wireframes/p14-whatsapp-identification-cotation.png` — WhatsApp : identification et commande guidée
- `../../PPC/assets/wireframes/p15-whatsapp-paiement-bon.png` — WhatsApp : paiement et bon de commande
- `../../PPC/assets/wireframes/p03-client-bon-reception.png` — client : bon de commande QR et validation de réception
- `../../PPC/assets/wireframes/p05-chargement-controle.png` — console de chargement : contrôle du bon, cas d'un bon déjà chargé
- `../../PPC/assets/wireframes/p20-geolocalisation-suivi-preuve.png` — suivi géolocalisé et dossier de preuve
- `../../PPC/assets/wireframes/p11-canaux-tableau.png` — console des canaux : vue d'ensemble, coûts et états
- `../../PPC/assets/images/` — 8 photographies libres de droits (route, chargement, mobile money)

## Customizations

- **Voix off française**, timbre à choisir parmi deux ou trois identités après le premier assemblage.
- **Sound design** : drones d'attention sur les bascules d'écran, effets sur les validations et les
  refus (bon accepté / bon refusé), nappe discrète sous la voix, silence marqué avant la clôture.
- **Motion design** : transitions maîtrisées entre canaux, compteur qui s'incrémente sur le montant,
  apparition du QR, transformation du QR en code de retrait sur SMS et USSD.
- **Charte du dossier** : NUIT `#0E2436`, ORANGE `#E06B2D`, SABLE `#F4F1EA`, Segoe UI — le film doit
  appartenir visuellement au dossier déjà remis à PPC.
- **Six écrans retenus** dans un ordre de 90 secondes : douleurs (0–8 s), la règle (8–20 s),
  WhatsApp (20–34 s), SMS et USSD (34–48 s), Telegram et e-mail (48–62 s), côté PPC (62–78 s),
  clôture (78–90 s).

## Notes

- **Format 16:9 horizontal**, alors que la préférence mémorisée de l'utilisateur est 1080x1920 : le
  film doit montrer des écrans bureau (back-office, console de chargement, e-mail) que le vertical
  recadre durement, et il sera projeté en réunion. La version verticale peut être tirée plus tard.
- **Pas de capture de site** : la matière est constituée de nos propres planches de wireframes. Le
  site publié sert de référence de charte, pas de source d'images.
- **Le bon n'a pas la même forme selon le canal** : QR sur application, WhatsApp, Telegram et e-mail ;
  code de retrait sur SMS et USSD. C'est le point que le film doit rendre évident, et c'est aussi ce
  qui a conduit la console de chargement à accepter un QR **ou** un code.
- **Aucune musique de fond, par décision du client.** Le catalogue musical exige le CLI HeyGen,
  absent ; aucun moteur de musique local n'est exposé. Le film tient sur la voix off et six effets
  sonores, ce qui fait ressortir les deux seuls impacts graves : l'ouverture et le verdict REFUSÉ.
- **Aucun prix affiché avant vérification de l'identité** : règle à ne jamais contredire à l'image.
- **Aucun délai de règlement transporteur annoncé** : il n'est pas connu à ce stade du dossier.
- Consommation HyperFrames inconnue sur ce poste (`usage --json` → `unsupported_harness`) ; espace
  disque disponible 1,4 Go.
