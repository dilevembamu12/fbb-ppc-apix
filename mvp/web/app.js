/* APIX · MVP — logique d'écran sur les sept jalons du document 05.
   Aucun framework : un parcours, quelques écrans, et les règles du serveur. */

const etat = {
  referentiel: null,
  client: null,
  client_id: Number(localStorage.getItem("apix_client") || 0) || null,
  cotation: null,
  bon: null,
  etape: 1,
};

const $ = (sel) => document.querySelector(sel);
const argent = (n) =>
  new Intl.NumberFormat("fr-FR", { minimumFractionDigits: 2, maximumFractionDigits: 2 }).format(n) + " $";
const heure = (iso) => (iso ? iso.replace("T", " à ") : "—");

/* ---------------------------------------------------------------- réseau */
async function appel(methode, chemin, corps) {
  const reponse = await fetch(chemin, {
    method: methode,
    headers: { "Content-Type": "application/json" },
    body: corps ? JSON.stringify(corps) : undefined,
  });
  const donnees = await reponse.json().catch(() => ({}));
  if (!reponse.ok) {
    const erreur = new Error(donnees.motif || "Erreur inattendue.");
    erreur.code = donnees.erreur;
    throw erreur;
  }
  return donnees;
}

const erreur = (zone, message) => {
  $(zone).innerHTML = message ? `<div class="erreur">${message}</div>` : "";
};

/* ------------------------------------------------------------ référentiel */
async function chargerReferentiel() {
  etat.referentiel = await appel("GET", "/api/referentiel");
  $("#produit").innerHTML = etat.referentiel.produits
    .map((p) => `<option value="${p.nom}">${p.nom} — ${argent(p.prix_sac)} le sac</option>`)
    .join("");
  $("#zone").innerHTML = etat.referentiel.zones
    .map((z) => `<option value="${z.nom}">${z.nom}</option>`)
    .join("");
}

/* =============================================================== J1 */
function dessinerClient() {
  const c = etat.client;
  const zone = $("#compte-courant");
  if (!c) {
    zone.innerHTML = "";
    $("#bandeau-client").innerHTML =
      `<span class="note" style="margin:0">Aucun compte sélectionné — ouvrez un compte dans l'onglet 1.</span>`;
    return;
  }
  const verifie = c.statut === "verifie";
  zone.innerHTML = `
    <div class="carte">
      <div style="display:flex;justify-content:space-between;align-items:baseline;gap:16px;flex-wrap:wrap">
        <h2>${c.nom}</h2>
        <span class="pastille ${verifie ? "" : "simule"}">${c.palier_libelle}</span>
      </div>
      <div class="ligne"><span class="cle">Téléphone</span><span class="val">${c.telephone}</span></div>
      <div class="ligne"><span class="cle">Plafond par cotation</span><span class="val">${
        c.plafond ? argent(c.plafond) : "aucun — identité non vérifiée"}</span></div>
      <div class="ligne"><span class="cle">Pièces déposées</span><span class="val">${
        c.pieces.length ? c.pieces.map((p) => `${p.type_piece} (recto + verso)`).join(", ") : "aucune"}</span></div>
      ${verifie ? "" : `
      <div class="actions">
        <button class="action" id="btn-pieces">Déposer mes pièces d'identité</button>
        <span class="note" style="margin:0">Vérification simulée : un dépôt complet suffit.</span>
      </div>`}
    </div>`;
  const bouton = $("#btn-pieces");
  if (bouton) bouton.addEventListener("click", deposerPieces);

  $("#bandeau-client").innerHTML = `
    <div style="display:flex;justify-content:space-between;gap:16px;flex-wrap:wrap;align-items:center">
      <span><strong>${c.nom}</strong> · ${c.palier_libelle} · plafond ${
        c.plafond ? argent(c.plafond) : "nul"}</span>
      <span class="note" style="margin:0">Compte n° ${c.id}</span>
    </div>`;
}

async function creerCompte() {
  erreur("#compte-erreur", "");
  try {
    const client = await appel("POST", "/api/clients", {
      nom: $("#c-nom").value, telephone: $("#c-tel").value, type: $("#c-type").value,
    });
    etat.client = client;
    etat.client_id = client.id;
    localStorage.setItem("apix_client", client.id);
    dessinerClient();
  } catch (e) { erreur("#compte-erreur", e.message); }
}

async function deposerPieces() {
  erreur("#compte-erreur", "");
  try {
    etat.client = await appel("POST", `/api/clients/${etat.client_id}/pieces`,
      { type_piece: "carte_identite", recto: true, verso: true });
    dessinerClient();
  } catch (e) { erreur("#compte-erreur", e.message); }
}

async function listerComptes() {
  const donnees = await appel("GET", "/api/clients");
  const lignes = donnees.clients.map((c) => `
    <div class="ligne">
      <span class="cle">n° ${c.id} · ${c.nom} · ${c.telephone}</span>
      <span class="val">${c.palier_libelle} — ${c.plafond ? argent(c.plafond) : "aucun plafond"}</span>
    </div>`).join("");
  $("#liste-comptes").innerHTML = `<div class="carte"><h2>Comptes</h2>${
    lignes || '<p class="note">Aucun compte.</p>'}</div>`;
}

async function rechargerClient() {
  if (!etat.client_id) return;
  try {
    etat.client = await appel("GET", `/api/clients/${etat.client_id}`);
  } catch { etat.client = null; etat.client_id = null; localStorage.removeItem("apix_client"); }
  dessinerClient();
}

/* =============================================================== J2 */
function majEtapes() {
  document.querySelectorAll("#etapes .etape").forEach((element) => {
    const numero = Number(element.dataset.etape);
    element.classList.toggle("faite", numero < etat.etape);
    element.classList.toggle("courante", numero === etat.etape);
  });
  for (let i = 1; i <= 6; i += 1) {
    const bloc = $(`#bloc-${i}`);
    if (bloc) bloc.style.display = i === etat.etape ? "block" : "none";
  }
}

$("#btn-cotation").addEventListener("click", async () => {
  erreur("#client-erreur", "");
  if (!etat.client_id) {
    erreur("#client-erreur", "Ouvrez d'abord un compte dans l'onglet 1.");
    return;
  }
  try {
    etat.cotation = await appel("POST", "/api/cotations", {
      client_id: etat.client_id,
      produit: $("#produit").value,
      quantite: Number($("#quantite").value),
      zone: $("#zone").value,
      option: $("#option").value,
    });
    etat.etape = 2;
    dessinerCotation();
    majEtapes();
  } catch (e) { erreur("#client-erreur", e.message); }
});

function dessinerCotation() {
  const c = etat.cotation;
  $("#bloc-2").innerHTML = `
    <div class="carte sombre">
      <div style="display:flex;justify-content:space-between;align-items:start;gap:20px;flex-wrap:wrap">
        <div>
          <div class="surtitre" style="color:var(--orange)">Cotation certifiée</div>
          <div style="font-size:30px;font-weight:700;letter-spacing:-0.01em;margin-top:4px">${c.numero}</div>
        </div>
        <div style="text-align:right">
          <div class="cle" style="font-size:13px">Valable jusqu'à</div>
          <div style="font-weight:600">${heure(c.valide_jusqua)}</div>
          <div class="chrono" id="chrono">—</div>
        </div>
      </div>
      <div style="margin-top:22px">
        <div class="ligne"><span class="cle">${c.produit} — ${c.quantite} sacs</span><span class="val">${argent(c.prix_unitaire * c.quantite)}</span></div>
        <div class="ligne"><span class="cle">Transport ${c.option === "A" ? "(enlèvement)" : "— " + c.zone}</span><span class="val">${c.transport ? argent(c.transport) : "—"}</span></div>
        <div class="ligne total"><span class="cle">Total</span><span class="val">${argent(c.total)}</span></div>
      </div>
    </div>
    <div class="carte">
      <h2>Prix ferme, numéro unique</h2>
      <p class="note">Cette cotation est la seule référence acceptée par le paiement. Passé le délai,
      elle ne sera plus payable : il faudra en demander une autre.</p>
      <div class="actions"><button class="action" id="btn-payer">Payer ${argent(c.total)}</button></div>
    </div>`;
  demarrerChrono();
  $("#btn-payer").addEventListener("click", () => {
    etat.etape = 3;
    dessinerPaiement();
    majEtapes();
  });
}

let minuteur = null;
function demarrerChrono() {
  if (minuteur) clearInterval(minuteur);
  const cible = $("#chrono");
  if (!cible) return;
  let reste = etat.cotation.expire_dans_s;
  const rendre = () => {
    const h = Math.floor(reste / 3600);
    const m = Math.floor((reste % 3600) / 60);
    const s = reste % 60;
    cible.textContent = reste > 0
      ? `expire dans ${h} h ${String(m).padStart(2, "0")} min ${String(s).padStart(2, "0")} s`
      : "expirée";
    cible.style.color = reste <= 0 ? "var(--rouge)" : "";
  };
  rendre();
  minuteur = setInterval(() => {
    reste -= 1;
    rendre();
    if (reste <= 0) clearInterval(minuteur);
  }, 1000);
}

/* =============================================================== J3 */
const CANAUX = [
  { code: "m_pesa", nom: "M-Pesa", type: "Portefeuille mobile" },
  { code: "airtel", nom: "Airtel Money", type: "Portefeuille mobile" },
  { code: "orange", nom: "Orange Money", type: "Portefeuille mobile" },
  { code: "carte", nom: "Carte bancaire", type: "Visa, Mastercard" },
  { code: "virement", nom: "Virement bancaire", type: "Compte PPC" },
];

function dessinerPaiement() {
  const c = etat.cotation;
  $("#bloc-3").innerHTML = `
    <div class="carte">
      <div style="display:flex;justify-content:space-between;align-items:baseline;gap:16px;flex-wrap:wrap">
        <h2>Choisir le moyen de paiement</h2><span class="pastille simule">Simulateur</span>
      </div>
      <p class="note" style="margin-top:4px">Montant : <strong>${argent(c.total)}</strong> —
      référence obligatoire : <strong>${c.numero}</strong></p>
      <div class="grille" style="margin-top:20px">
        ${CANAUX.map((canal) => `
          <button class="discret" data-canal="${canal.code}" style="text-align:left;padding:18px 20px">
            <div style="font-weight:700;font-size:16px">${canal.nom}</div>
            <div style="font-size:13px;color:var(--gris)">${canal.type}</div>
          </button>`).join("")}
      </div>
    </div>`;
  document.querySelectorAll("[data-canal]").forEach((bouton) =>
    bouton.addEventListener("click", () => payer(bouton.dataset.canal)));
}

async function payer(canal) {
  erreur("#client-erreur", "");
  try {
    etat.bon = await appel("POST", "/api/paiements", { cotation: etat.cotation.numero, canal });
    etat.etape = 4;
    dessinerBon();
    majEtapes();
  } catch (e) { erreur("#client-erreur", e.message); }
}

/* =============================================================== J4 */
function dessinerBon() {
  const b = etat.bon;
  $("#bloc-4").innerHTML = `
    <div class="carte">
      <div style="display:flex;justify-content:space-between;align-items:baseline;gap:16px;flex-wrap:wrap">
        <h2>Bon de commande</h2><span class="pastille">Nominatif · usage unique</span>
      </div>
      <div class="ligne"><span class="cle">Numéro</span><span class="val">${b.numero}</span></div>
      <div class="ligne"><span class="cle">Titulaire</span><span class="val">${b.client}</span></div>
      <div class="ligne"><span class="cle">Marchandise</span><span class="val">${b.quantite} sacs de ${b.produit} — ${b.zone}</span></div>
      <div class="ligne"><span class="cle">Émis le</span><span class="val">${heure(b.emis_le)}</span></div>
      <div style="margin-top:22px;text-align:center">
        <div class="surtitre" style="color:var(--gris)">Code de retrait</div>
        <div class="code-retrait">${b.code}</div>
      </div>
      <div style="margin-top:16px">
        <label>Contenu du QR (signé)</label>
        <div class="qr-contenu">${b.qr}</div>
      </div>
      <div class="actions">
        <button class="action" id="btn-vers-console">Passer au chargement</button>
        <button class="discret" id="btn-simuler-reception">Simuler la livraison complète</button>
      </div>
      <p class="note">Le chargement se fait dans l'onglet 3, par un autre agent : c'est la séparation
      des rôles qui rend le contrôle crédible.</p>
    </div>`;
  $("#btn-vers-console").addEventListener("click", () => {
    basculerMode("console");
    $("#saisie").value = b.code;
  });
  $("#btn-simuler-reception").addEventListener("click", simulerReceptionComplete);
}

async function simulerReceptionComplete() {
  erreur("#client-erreur", "");
  try {
    await appel("POST", "/api/controles", {
      saisie: etat.bon.code, poids_kg: 5000,
      transporteur: $("#transporteur").value, plaque: $("#plaque").value,
    });
    etat.bon = await appel("GET", `/api/bons/${etat.bon.code}`);
    etat.etape = 5;
    dessinerReception();
    majEtapes();
  } catch (e) { erreur("#client-erreur", e.message); }
}

/* =============================================================== J6 */
function dessinerReception() {
  const b = etat.bon;
  $("#bloc-5").innerHTML = `
    <div class="carte">
      <h2>Réception de la marchandise</h2>
      <p class="note" style="margin-top:4px">Bon ${b.numero} — ${b.quantite} sacs attendus.
      Tolérance : ${etat.referentiel.tolerance_sacs} sacs.</p>
      <div class="grille" style="margin-top:18px">
        <div class="champ"><label for="sacs">Sacs reçus</label>
          <input id="sacs" type="number" value="${b.quantite}" min="0" step="1" /></div>
        <div class="champ"><label for="poids-recu">Poids reçu (kg)</label>
          <input id="poids-recu" type="number" value="5000" min="0" step="1" /></div>
        <div class="champ"><label for="scelle">Scellé</label>
          <select id="scelle"><option value="oui">Intact</option><option value="non">Rompu</option></select></div>
      </div>
      <div class="actions"><button class="action" id="btn-reception">Valider la réception</button></div>
    </div>
    <div id="resultat-reception"></div>`;
  $("#btn-reception").addEventListener("click", validerReception);
}

async function validerReception() {
  erreur("#client-erreur", "");
  try {
    const recu = await appel("POST", "/api/receptions", {
      code: etat.bon.code,
      sacs_recus: Number($("#sacs").value),
      poids_recu_kg: Number($("#poids-recu").value),
      etat: "conforme",
      scelle_ok: $("#scelle").value === "oui",
    });
    etat.bon = recu;
    const r = recu.reception;
    const litige = Boolean(recu.litige);
    $("#resultat-reception").innerHTML = `
      <div class="verdict ${litige ? "refuse" : "accepte"}">
        <div class="titre">${litige ? "Litige ouvert" : "Réception conforme"}</div>
        <div class="motif">Écart constaté : <strong>${r.ecart > 0 ? "+" : ""}${r.ecart} sacs</strong>.
        ${litige
          ? "L'écart dépasse la tolérance ou le scellé a été rompu. Le dossier de preuve est constitué et le litige attend instruction."
          : "L'écart reste dans la tolérance : la réception est enregistrée sans litige."}</div>
      </div>`;
    const bouton = $("#btn-reception");
    if (bouton) { bouton.disabled = true; bouton.textContent = "Réception enregistrée"; }
    etat.etape = 6;
    majEtapes();
    dessinerRecu();
  } catch (e) { erreur("#client-erreur", e.message); }
}

/* =============================================================== J7 */
async function dessinerRecu() {
  const zone = $("#bloc-6");
  try {
    const recu = await appel("GET", `/api/recus/${etat.bon.code}`);
    zone.innerHTML = `
      <div class="carte">
        <div style="display:flex;justify-content:space-between;align-items:baseline;gap:16px;flex-wrap:wrap">
          <h2>Reçu vérifiable</h2><span class="pastille">${recu.numero}</span>
        </div>
        <div class="ligne"><span class="cle">Commande</span><span class="val">${recu.bon}</span></div>
        <div class="ligne"><span class="cle">Client</span><span class="val">${recu.client}</span></div>
        <div class="ligne"><span class="cle">Marchandise</span><span class="val">${recu.quantite} sacs de ${recu.produit} — ${recu.zone}</span></div>
        <div class="ligne"><span class="cle">Livré le</span><span class="val">${recu.livre_le}</span></div>
        <div style="margin-top:16px">
          <label>Empreinte</label><div class="qr-contenu">${recu.empreinte}</div>
        </div>
        <div class="actions"><button class="discret" id="btn-preuve">Voir le dossier de preuve</button></div>
      </div>
      <div id="dossier-preuve"></div>`;
    $("#btn-preuve").addEventListener("click", async () => {
      const preuve = await appel("GET", `/api/preuves/${etat.bon.code}`);
      $("#dossier-preuve").innerHTML = `<div class="carte"><h2>Dossier de preuve</h2>${
        preuve.etapes.map((e) => `
          <div class="ligne">
            <span class="cle"><strong>${e.etape}</strong> · ${e.quand}</span>
            <span class="val" style="font-weight:400;text-align:right">${e.detail}</span>
          </div>`).join("")}</div>`;
    });
  } catch (e) {
    zone.innerHTML = `<div class="carte"><p class="note">${e.message}</p></div>`;
  }
}

/* =============================================================== Console */
async function controler() {
  const saisie = $("#saisie").value.trim();
  if (!saisie) return;
  const zone = $("#resultat-controle");
  try {
    const bon = await appel("POST", "/api/controles", {
      saisie, poids_kg: Number($("#poids").value),
      transporteur: $("#transporteur").value, plaque: $("#plaque").value,
    });
    const ch = bon.chargement;
    zone.innerHTML = `
      <div class="verdict accepte">
        <div class="titre">Bon accepté — chargement autorisé</div>
        <div class="motif">${bon.numero} · ${bon.quantite} sacs de ${bon.produit} pour ${bon.client}.<br />
        ${ch.sacs} sacs · ${ch.poids_kg} kg · scellé ${ch.scelle} · ${ch.transporteur} (${ch.plaque})<br />
        posé le ${heure(ch.charge_le)}.</div>
      </div>
      <div class="carte"><p class="note" style="margin:0">Représentez ce bon une seconde fois :
      le système doit le refuser, parce qu'un bon est à usage unique.</p></div>`;
  } catch (e) {
    zone.innerHTML = `<div class="verdict refuse">
      <div class="titre">Chargement refusé</div><div class="motif">${e.message}</div></div>`;
  }
}

$("#btn-controle").addEventListener("click", controler);
$("#saisie").addEventListener("keydown", (ev) => { if (ev.key === "Enter") controler(); });
$("#btn-scan").addEventListener("click", () => { $("#saisie").value = etat.bon ? etat.bon.qr : ""; });
$("#btn-vider").addEventListener("click", () => {
  $("#saisie").value = "";
  $("#resultat-controle").innerHTML = "";
});

/* =============================================================== Litiges */
async function chargerLitiges() {
  const bureau = await appel("GET", "/api/backoffice");
  const zone = $("#liste-litiges");
  if (!bureau.litiges.length) {
    zone.innerHTML = `<div class="carte"><p class="note">Aucun litige. Un écart hors tolérance
      ou un scellé rompu en ouvre un automatiquement.</p></div>`;
    return;
  }
  zone.innerHTML = bureau.litiges.map((l) => `
    <div class="carte">
      <div style="display:flex;justify-content:space-between;align-items:baseline;gap:16px;flex-wrap:wrap">
        <h2>${l.bon_numero} — ${l.client}</h2>
        <span class="pastille ${l.statut === "ouvert" ? "" : "simule"}">${l.statut}</span>
      </div>
      <div class="ligne"><span class="cle">Motif</span><span class="val">${l.motif}</span></div>
      <div class="ligne"><span class="cle">Écart</span><span class="val">${l.ecart > 0 ? "+" : ""}${l.ecart} sacs</span></div>
      ${l.statut === "ouvert" ? `
      <div class="grille" style="margin-top:16px">
        <div class="champ"><label for="retenu-${l.id}">Montant retenu ($)</label>
          <input id="retenu-${l.id}" type="number" value="47.5" min="0" step="0.5" /></div>
        <div class="champ"><label for="libere-${l.id}">Montant libéré ($)</label>
          <input id="libere-${l.id}" type="number" value="0" min="0" step="0.5" /></div>
        <div class="champ"><label for="decision-${l.id}">Décision motivée</label>
          <input id="decision-${l.id}" value="Écart constaté, retenue appliquée au transporteur" /></div>
      </div>
      <div class="actions"><button class="action" data-instruire="${l.id}">Instruire</button></div>`
      : `<div class="ligne"><span class="cle">Décision</span><span class="val" style="font-weight:400">${l.decision || ""}</span></div>
         <div class="ligne"><span class="cle">Retenu / libéré</span><span class="val">${argent(l.retenu)} / ${argent(l.libere)}</span></div>`}
    </div>`).join("");
  document.querySelectorAll("[data-instruire]").forEach((bouton) =>
    bouton.addEventListener("click", () => instruire(Number(bouton.dataset.instruire))));
}

async function instruire(id) {
  try {
    await appel("POST", `/api/litiges/${id}/instruction`, {
      retenu: Number($(`#retenu-${id}`).value),
      libere: Number($(`#libere-${id}`).value),
      decision: $(`#decision-${id}`).value,
    });
    chargerLitiges();
  } catch (e) { alert(e.message); }
}

/* =============================================================== Pilotage */
async function chargerTableau() {
  const t = await appel("GET", "/api/tableau");
  const cases = [
    ["Comptes ouverts", t.clients],
    ["Comptes vérifiés", t.clients_verifies],
    ["Cotations", t.cotations],
    ["Paiements", t.paiements],
    ["Bons émis", t.bons],
    ["Chargements", t.chargements],
    ["Livraisons", t.livraisons],
    ["Litiges ouverts", t.litiges_ouverts],
    ["Montant encaissé", argent(t.encaisse)],
  ];
  $("#compteurs").innerHTML = cases.map(([libelle, valeur]) =>
    `<div class="compteur"><div class="valeur">${valeur}</div><div class="libelle">${libelle}</div></div>`).join("");

  if (etat.client_id) {
    const historique = await appel("GET", `/api/clients/${etat.client_id}/historique`);
    $("#historique-client").innerHTML = `
      <div class="carte"><h2>Historique de ${etat.client ? etat.client.nom : "ce compte"}</h2>
      ${historique.cotations.length
        ? historique.cotations.map((c) => `
          <div class="ligne">
            <span class="cle">${c.numero} · ${c.quantite} sacs de ${c.produit}</span>
            <span class="val">${argent(c.total)} — ${c.statut}</span>
          </div>`).join("")
        : '<p class="note">Aucune commande.</p>'}
      </div>`;
  }
}

/* =============================================================== Navigation */
function basculerMode(mode) {
  document.querySelectorAll(".modes button").forEach((b) =>
    b.classList.toggle("actif", b.dataset.mode === mode));
  document.querySelectorAll(".vue").forEach((v) => v.classList.remove("visible"));
  $(`#vue-${mode}`).classList.add("visible");
  if (mode === "pilotage") chargerTableau();
  if (mode === "litiges") chargerLitiges();
  if (mode === "compte") listerComptes();
}

document.querySelectorAll(".modes button").forEach((bouton) =>
  bouton.addEventListener("click", () => basculerMode(bouton.dataset.mode)));

$("#btn-compte").addEventListener("click", creerCompte);
$("#btn-lister").addEventListener("click", listerComptes);
$("#btn-rafraichir").addEventListener("click", chargerTableau);
$("#btn-rafraichir-litiges").addEventListener("click", chargerLitiges);

/* =============================================================== Départ */
chargerReferentiel()
  .then(rechargerClient)
  .then(() => majEtapes());
