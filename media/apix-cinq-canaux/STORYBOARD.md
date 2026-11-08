---
format: 1920x1080
duration: 90s
message: "Une seule cotation, un seul bon — quel que soit le canal utilisé par le client"
arc: "Douleur → Règle → Les canaux → La preuve → Clôture"
audience: "Direction générale de PPC, responsables commerciaux et logistique"
mode: collaborative
---

## Système visuel — valeurs opposables

Extrait de `frame.md`, converti en valeurs de film (1920×1080, tailles en pixels réels).

**Rythme des fonds.** Alterne pour que le film respire : nuit (1) · sable (2) · sable (3) · nuit (4) ·
sable (5) · sable (6) · nuit (7). Trois fonds sombres, quatre clairs, jamais deux sombres de suite.

**Couleurs.** Sable `#F4F1EA` (fond clair), Nuit `#0E2436` (fond sombre et encre sur sable),
Nuit moyen `#1B3A57` (texte secondaire sur sable), Gris `#5A6B7A` (légendes), Orange `#E06B2D`.
Sur fond nuit, l'encre claire est le sable lui-même à 92 %, les légendes à 55 %.

**L'orange est un budget, pas une couleur.** Un seul élément orange par cadre, jamais deux. Il désigne
l'action ou le chiffre qui compte : la tuile du canal en cours, le code de retrait, le bouton de
paiement, le verdict. Si un cadre en réclame deux, c'est que le cadre a deux sujets — donc il est faux.

**Cartes.** Fond `rgba(224,107,45,.04)`, bordure `1,5 px rgba(224,107,45,.2)`, rayon 14 px,
**aucune ombre**. Sur fond nuit : fond `rgba(244,241,234,.05)`, bordure `1 px rgba(244,241,234,.14)`.
Les planches de wireframes sont posées comme des documents : même rayon, bordure nuit à 14 %, fond blanc.

**Échelle typographique.** Surtitre 22 px / 600 / interlettrage .14 em / majuscules / orange.
Titre 92 px / 700 / −.02 em. Sous-titre 64 px / 600. Conducteur 34 px / 400 / ligne 1,5.
Légende 24 px / 400 / 60 % d'opacité. Chiffre-clé ou code 132 px / 700 / interlettrage .12 em.
Tout en Segoe UI ; les codes en Segoe UI avec interlettrage large, jamais de police à chasse fixe.

**Marges.** 120 px à gauche et à droite, 96 px en haut. Aucun texte ne descend sous y = 960.

**Barre de progression.** Filet de 2 px en bas, orange à 45 % d'opacité, avec un fond nuit à 10 %.
Elle court sur les 90 secondes : chaque cadre n'en remplit que sa tranche (cadre *n* de *t₁* à *t₂*,
soit `t₁/90` à `t₂/90` de la largeur). Elle relie les sept compositions en un seul film.

**Mouvement.** Entrées de 0,5 à 0,9 s en `power3.out`, sorties en fondu simple, jamais en mouvement.
Une seule chose bouge à la fois dans une zone donnée. Pas de rebond, pas d'élasticité, pas de rotation.
Les valeurs de départ sont toujours déclarées (`fromTo`), jamais héritées d'un `from`.

## Frame 1 — Trois questions sans réponse

- scene: Les douleurs de la réunion en typographie plein cadre, sur deux photos de route et de chargement
- duration: 9s
- poster: 6s
- transition_in: cut
- status: rendered
- voiceover: "Où est mon camion ? Combien de sacs sont arrivés ? Qui paie les manquants ? Trois questions. Aucune preuve."
- asset_candidates: images/route.jpg, images/chargement.jpg
- src: compositions/frames/01-douleur.html
- fond: nuit sur photo — `douleur_route.jpg` puis `douleur_manutention.jpg`, voile nuit 80 %, vignette
- typo: questions 76 px à gauche x=140, y=300/450/600 ; index 01·02·03 en 20 px orange à 60 %
- orange: « Aucune preuve. » seulement
- rythme: 0,5 s · 2,3 s · 4,0 s (les trois impacts), bascule photo à 4,9 s, verdict à 5,9 s

Ouvrir froid sur la douleur, sans présenter le produit. Trois questions qui tombent une par une, en gros
caractères, sur un fond photographique désaturé. La quatrième phrase — « aucune preuve » — reste seule à
l'écran une seconde de plus que les autres : c'est le vrai sujet du film.

Chaque question arrive avec un impact sonore sec, de plus en plus grave. Pas de musique encore.

## Frame 2 — Une seule cotation, un seul bon

- scene: La règle en trois temps — cotation, paiement, bon — puis la bande des cinq canaux
- duration: 11s
- poster: 8s
- transition_in: crossfade
- status: rendered
- voiceover: "Une seule cotation, un seul bon de commande. Sur l'application, mais aussi sur WhatsApp, Telegram, par e-mail, par SMS et par USSD."
- asset_candidates: (aucun asset externe — typographie et formes)
- src: compositions/frames/02-regle.html
- fond: sable, grille de points orange 3×3 à 6 % en haut à droite
- composition: trois cartes de 440×210 à y=430 (x=200/740/1280), puis six tuiles de 250×92 à y=760
- tuiles: Application · WhatsApp · Telegram · E-mail · SMS · USSD — WhatsApp seule en orange
- orange: la tuile WhatsApp, et le trait de force qui remonte vers le bon
- rythme: cartes 0,6–2,4 s · flèches 2,6–4,2 s · tuiles 5,4–7,4 s · trait de force 7,8–9,2 s

La musique entre ici, discrète. Trois blocs s'allument dans l'ordre : cotation, paiement, bon — avec la
flèche qui va de la cotation vers le paiement, jamais l'inverse. Puis cinq tuiles de canal se déploient
sous les trois blocs, et la ligne de force les relie toutes au même bon.

Réserver l'orange à la seule tuile active : celle du canal en cours de démonstration dans les frames suivantes.

## Frame 3 — WhatsApp

- scene: Les deux écrans WhatsApp entrent, la cotation puis le bon avec son QR
- duration: 14s
- poster: 10s
- transition_in: wipe
- status: rendered
- voiceover: "Sur WhatsApp, le client demande un prix, reçoit sa cotation, paie en la référençant — et le bon arrive dans la conversation, avec son QR."
- asset_candidates: p14-whatsapp-identification-cotation.png, p15-whatsapp-paiement-bon.png
- src: compositions/frames/03-whatsapp.html
- fond: sable ; les deux planches posées en documents, rayon 14, bordure nuit 14 %
- composition: colonne de gauche 120–820 (surtitre, titre, quatre étapes) ; planche 940–1800, haut 120
- étapes: Demande de prix · Cotation émise · Paiement référencé · Bon et QR — s'allument une à une
- orange: l'étape active, puis le cadre de mise en avant qui glisse sur le QR
- rythme: p14 entrée 0,4 s · étapes 1,6 → 7,4 s · bascule p14→p15 à 7,6 s · pulse du QR à 9,8 s

Les planches entrent par la droite et se posent côte à côte. Un cadre de mise en avant passe de la
cotation au bon. Le QR pulse une fois quand la voix dit « avec son QR » — un seul pulse, pas trois.

Le bon porte la mention « nominatif, usage unique » : la laisser lisible, c'est la promesse de non-revente.

## Frame 4 — SMS et USSD : le bon devient un code

- scene: SMS puis USSD ; le QR se transforme en code de retrait
- duration: 14s
- poster: 10s
- transition_in: crossfade
- status: rendered
- voiceover: "Sur SMS, trois mots suffisent. Sur USSD, un menu, sans internet. Le paiement passe, et le bon devient un code de retrait que l'agent saisit."
- asset_candidates: p23-parite-sms.png, p22-parite-ussd.png
- src: compositions/frames/04-sms-ussd.html
- fond: nuit — la frame la plus sombre du film, pour que la transformation se voie
- composition: p23 en haut à gauche (640×620), p22 en haut à droite (640×620), deux légendes dessous
- surimpression: `COT 200 GOMBE` puis `*144#` en 52 px orange sous chaque planche — la planche donne
  le contexte, la typographie donne la lisibilité
- transformation: à 7,0 s les deux planches reculent à 18 % et un QR de 220 px se dissout en six
  chiffres 132 px ; à 11,0 s la phrase de sens, en bas
- orange: le code de retrait, seul élément chaud du cadre

C'est le moment le plus important du film. Sur SMS, montrer la commande réduite à l'essentiel —
`COT 200 GOMBE` — puis le message qui porte le code 481902. Sur USSD, le menu `*144#` et la cotation
dans la session.

Puis la bascule visuelle : le QR de la frame précédente se décompose en un code à six chiffres. C'est la
phrase à faire comprendre sans l'expliquer — le bon n'a pas la même forme, mais il vaut la même chose.

Son : la décomposition du QR porte un effet de déconstruction, et le code s'affiche chiffre par chiffre.

## Frame 5 — Telegram et e-mail

- scene: Bot Telegram et e-mail de cotation avec lien signé
- duration: 12s
- poster: 8s
- transition_in: wipe
- status: rendered
- voiceover: "Telegram fait la même chose avec des boutons. Et par e-mail, la cotation arrive en PDF, avec un lien de paiement signé."
- asset_candidates: p24-parite-telegram.png, p25-parite-email.png
- src: compositions/frames/05-telegram-email.html
- fond: sable
- composition: p24 à gauche (x=110, 620×600), p25 à droite (x=800, 1010×690) — le seul écran large
- surimpression: pastille « Payer 3 145 $ » posée sur le bouton de l'e-mail, trait orange tiré dessous
- orange: le trait sous le bouton de paiement
- rythme: Telegram 0,4–4,0 s · e-mail 4,2–7,0 s · trait 7,4–8,6 s

Deux plans rapides, sans temps mort : le bot Telegram avec ses claviers, puis l'e-mail en écran large —
le seul écran large de la séquence des canaux, donc l'occasion de respirer et de montrer le lien signé.

Souligner d'un trait le bouton « Payer 3 145 $ » : c'est le point où le client quitte le message pour payer.

## Frame 6 — Côté PPC : QR ou code

- scene: Console de chargement, console des canaux, instruction d'un litige
- duration: 18s
- poster: 14s
- transition_in: crossfade
- status: rendered
- voiceover: "Côté PPC, rien ne change : la console de chargement contrôle le bon, QR ou code, et refuse un bon expiré ou déjà utilisé. Le back-office garde la main sur les canaux, les modèles et le routage."
- asset_candidates: p05-chargement-controle.png, p11-canaux-tableau.png, p09-backoffice-litige.png
- src: compositions/frames/06-ppc.html
- fond: sable, avec un bandeau nuit en haut qui porte les trois titres d'étape
- composition: un seul écran large à la fois, x=140, 1180×690, y=250 — jamais trois à la fois
- ordre: p05 chargement (0,6–7,2 s) · p11 canaux (7,4–12,4 s) · p09 litige (12,6–17,4 s)
- verdict: la plaque « BON REFUSÉ » tombe à 4,6 s sur p05, avec le seul impact grave du cadre
- orange: la plaque du verdict, puis le montant libéré sur le litige

Trois écrans en plans successifs, du plus opérationnel au plus stratégique. Commencer par la console de
chargement et son verdict REFUSÉ motivé : c'est la preuve que le contrôle existe vraiment.

Puis la console des canaux — états, volumes, coûts — et le litige avec ses montants retenu et libéré.
Cette dernière image répond directement à « qui paie les manquants » posée en ouverture.

Son : le verdict REFUSÉ porte un impact grave, le seul du film avec la frame 1.

## Frame 7 — Clôture

- scene: La phrase de clôture, seule, puis le logotype
- duration: 12s
- poster: 8s
- transition_in: cut
- status: rendered
- voiceover: "Un client peut commencer sur USSD et terminer sur WhatsApp. Même cotation, même bon, même preuve."
- asset_candidates: (aucun asset externe — typographie)
- src: compositions/frames/07-cloture.html
- fond: nuit ; trois cercles concentriques qui se referment, à 8 % d'opacité, jamais plus
- composition: trois phrases à gauche x=140, y=300/430/560, 96 px ; « Même preuve. » en orange
- logotype: FBB · APIX en 26 px, interlettrage .18 em, à droite en bas, posé à 8,6 s
- rythme: silence 0–0,5 s · filet 0,8 s · trois phrases 3,2/4,2/5,2 s · logotype 8,6 s

Silence musical d'une demi-seconde avant la première phrase — le film retient son souffle. Trois
expressions tombent en cadence : « même cotation », « même bon », « même preuve ». Puis l'orange se
referme sur le bleu nuit, et le logotype FBB · APIX se pose.

Ne pas ajouter d'appel à l'action commercial : le film est un cadrage, pas une offre.
