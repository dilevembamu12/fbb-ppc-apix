/* APIX · MVP — logique d'écran.
   Aucun framework : le parcours tient en cinq gestes, il n'a pas besoin de plus. */

const etat = {
  referentiel: null,
  cotation: null,
  bon: null,
  etape: 1,
};

const $ = (sel) => document.querySelector(sel);
const argent = (n) =>
  new Intl.NumberFormat("fr-FR", { minimumFractionDigits: 2, maximumFractionDigits: 2 }).format(n) + " $";

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
    erreur.statut = reponse.status;
    throw erreur;
  }
  return donnees;
}

function afficherErreur(zone, message) {
  const cible = $(zone);
  cible.innerHTML = message ? `<div class="erreur">${message}</div>` : "";
}

/* --------------------------------------------------------------- étapes */
function majEtapes() {
  document.querySelectorAll("#etapes .etape").forEach((element) => {
    const numero = Number(element.dataset.etape);
    element.classList.toggle("faite", numero < etat.etape);
    element.classList.toggle("courante", numero === etat.etape);
  });
  for (let i = 1; i <= 5; i += 1) {
    const bloc = $(`#bloc-${i}`);
    if (bloc) bloc.style.display = i === etat.etape ? "block" : "none";
  }
}

/* ------------------------------------------------------------ 1. demande */
async function chargerReferentiel() {
  etat.referentiel = await appel("GET", "/api/referentiel");
  const produits = $("#produit");
  produits.innerHTML = etat.referentiel.produits
    .map((p) => `<option value="${p.nom}">${p.nom} — ${argent(p.prix_sac)} le sac</option>`)
    .join("");
  const zones = $("#zone");
  zones.innerHTML = etat.referentiel.zones.map((z) => `<option value="${z.nom}">${z.nom}</option>`).join("");
}

$("#btn-cotation").addEventListener("click", async () => {
  afficherErreur("#client-erreur", "");
  const bouton = $("#btn-cotation");
  bouton.disabled = true;
  try {
    etat.cotation = await appel("POST", "/api/cotations", {
      client: $("#client").value,
      telephone: $("#telephone").value,
      produit: $("#produit").value,
      quantite: Number($("#quantite").value),
      zone: $("#zone").value,
      option: $("#option").value,
    });
    etat.etape = 2;
    dessinerCotation();
    majEtapes();
  } catch (erreur) {
    afficherErreur("#client-erreur", erreur.message);
  } finally {
    bouton.disabled = false;
  }
});

/* ----------------------------------------------------------- 2. cotation */
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
          <div style="font-weight:600">${c.valide_jusqua.replace("T", " à ")}</div>
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
      <p class="note">
        Cette cotation est la seule référence acceptée par le paiement. Passé le délai de validité,
        elle ne sera plus payable : il faudra en demander une autre.
      </p>
      <div class="actions">
        <button class="action" id="btn-payer">Payer ${argent(c.total)}</button>
      </div>
    </div>`;
  $("#btn-payer").addEventListener("click", () => {
    etat.etape = 3;
    dessinerPaiement();
    majEtapes();
  });
}

/* ---------------------------------------------------------- 3. paiement */
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
        <h2>Choisir le moyen de paiement</h2>
        <span class="pastille simule">Simulateur</span>
      </div>
      <p class="note" style="margin-top:4px">
        Montant à régler : <strong>${argent(c.total)}</strong> — référence obligatoire : <strong>${c.numero}</strong>
      </p>
      <div class="grille" style="margin-top:20px">
        ${CANAUX.map(
          (canal) => `
          <button class="discret" data-canal="${canal.code}" style="text-align:left;padding:18px 20px">
            <div style="font-weight:700;font-size:16px">${canal.nom}</div>
            <div style="font-size:13px;color:var(--gris)">${canal.type}</div>
          </button>`
        ).join("")}
      </div>
    </div>`;
  document.querySelectorAll("[data-canal]").forEach((bouton) => {
    bouton.addEventListener("click", () => payer(bouton.dataset.canal));
  });
}

async function payer(canal) {
  afficherErreur("#client-erreur", "");
  try {
    etat.bon = await appel("POST", "/api/paiements", { cotation: etat.cotation.numero, canal });
    etat.etape = 4;
    dessinerBon();
    majEtapes();
  } catch (erreur) {
    afficherErreur("#client-erreur", erreur.message);
  }
}

/* --------------------------------------------------------------- 4. bon */
function dessinerBon() {
  const b = etat.bon;
  $("#bloc-4").innerHTML = `
    <div class="carte">
      <div style="display:flex;justify-content:space-between;align-items:baseline;gap:16px;flex-wrap:wrap">
        <h2>Bon de commande</h2>
        <span class="pastille">Nominatif · usage unique</span>
      </div>
      <div class="ligne"><span class="cle">Numéro</span><span class="val">${b.numero}</span></div>
      <div class="ligne"><span class="cle">Titulaire</span><span class="val">${b.client}</span></div>
      <div class="ligne"><span class="cle">Marchandise</span><span class="val">${b.quantite} sacs de ${b.produit} — ${b.zone}</span></div>
      <div class="ligne"><span class="cle">Émis le</span><span class="val">${b.emis_le.replace("T", " à ")}</span></div>

      <div style="margin-top:22px;text-align:center">
        <div class="surtitre" style="color:var(--gris)">Code de retrait</div>
        <div class="code-retrait">${b.code}</div>
        <div class="note" style="margin-top:0">À présenter au chargement, ou à scanner via le QR.</div>
      </div>

      <div style="margin-top:20px">
        <label>Contenu du QR (signé)</label>
        <div class="qr-contenu">${b.qr}</div>
      </div>

      <div class="actions">
        <button class="action" id="btn-vers-console">Passer au chargement</button>
        <button class="discret" id="btn-reception">Enregistrer la réception</button>
      </div>
    </div>`;
  $("#btn-vers-console").addEventListener("click", () => {
    basculerMode("console");
    $("#saisie").value = b.code;
    $("#saisie").focus();
  });
  $("#btn-reception").addEventListener("click", () => {
    etat.etape = 5;
    dessinerReception();
    majEtapes();
  });
}

/* ---------------------------------------------------------- 5. réception */
function dessinerReception() {
  const b = etat.bon;
  $("#bloc-5").innerHTML = `
    <div class="carte">
      <h2>Réception de la marchandise</h2>
      <p class="note" style="margin-top:4px">
        Bon ${b.numero} — ${b.quantite} sacs attendus. Tolérance : ${etat.referentiel.tolerance_sacs} sacs.
      </p>
      <div class="grille" style="margin-top:18px">
        <div class="champ">
          <label for="sacs">Sacs effectivement reçus</label>
          <input id="sacs" type="number" value="${b.quantite}" min="0" step="1" />
        </div>
        <div class="champ">
          <label for="scelle">Scellé intact</label>
          <select id="scelle">
            <option value="oui">Oui</option>
            <option value="non">Non — scellé rompu</option>
          </select>
        </div>
      </div>
      <div class="actions">
        <button class="action" id="btn-valider-reception">Valider la réception</button>
      </div>
    </div>
    <div id="resultat-reception"></div>`;
  $("#btn-valider-reception").addEventListener("click", async () => {
    afficherErreur("#client-erreur", "");
    try {
      const recu = await appel("POST", "/api/receptions", {
        code: etat.bon.code,
        sacs_recus: Number($("#sacs").value),
        etat: "conforme",
        scelle_ok: $("#scelle").value === "oui",
      });
      const r = recu.reception;
      const litige = r.litige === 1;
      $("#resultat-reception").innerHTML = `
        <div class="verdict ${litige ? "refuse" : "accepte"}">
          <div class="titre">${litige ? "Litige ouvert" : "Réception conforme"}</div>
          <div class="motif">
            Écart constaté : <strong>${r.ecart > 0 ? "+" : ""}${r.ecart} sacs</strong>.
            ${litige
              ? "L'écart dépasse la tolérance, ou le scellé a été rompu. Le dossier de preuve est constitué."
              : "L'écart reste dans la tolérance : la réception est enregistrée sans litige."}
          </div>
        </div>`;
      $("#btn-valider-reception").disabled = true;
    } catch (erreur) {
      afficherErreur("#client-erreur", erreur.message);
    }
  });
}

/* ------------------------------------------------------------- console */
async function controler() {
  const saisie = $("#saisie").value.trim();
  if (!saisie) return;
  const zone = $("#resultat-controle");
  try {
    const bon = await appel("POST", "/api/controles", { saisie, agent: "Agent de chargement" });
    zone.innerHTML = `
      <div class="verdict accepte">
        <div class="titre">Bon accepté — chargement autorisé</div>
        <div class="motif">
          ${bon.numero} · ${bon.quantite} sacs de ${bon.produit} pour ${bon.client}.
          Scellé ${bon.chargement ? bon.chargement.scelle : "—"} posé le
          ${bon.chargement ? bon.chargement.charge_le.replace("T", " à ") : "—"}.
        </div>
      </div>
      <div class="carte">
        <p class="note" style="margin:0">
          Représentez ce bon une seconde fois : le système doit le refuser, parce qu'un bon est à usage unique.
        </p>
      </div>`;
  } catch (erreur) {
    zone.innerHTML = `
      <div class="verdict refuse">
        <div class="titre">Chargement refusé</div>
        <div class="motif">${erreur.message}</div>
      </div>`;
  }
}

$("#btn-controle").addEventListener("click", controler);
$("#saisie").addEventListener("keydown", (evenement) => {
  if (evenement.key === "Enter") controler();
});
$("#btn-scan").addEventListener("click", () => {
  if (etat.bon) $("#saisie").value = etat.bon.qr;
  else $("#saisie").value = "";
});
$("#btn-vider").addEventListener("click", () => {
  $("#saisie").value = "";
  $("#resultat-controle").innerHTML = "";
});

/* ------------------------------------------------------------ pilotage */
async function chargerTableau() {
  const t = await appel("GET", "/api/tableau");
  const cases = [
    ["Cotations émises", t.cotations],
    ["Paiements encaissés", t.paiements],
    ["Bons émis", t.bons],
    ["Chargements", t.chargements],
    ["Livraisons", t.livraisons],
    ["Litiges ouverts", t.litiges],
    ["Montant encaissé", argent(t.encaisse)],
  ];
  $("#compteurs").innerHTML = cases
    .map(([libelle, valeur]) => `<div class="compteur"><div class="valeur">${valeur}</div><div class="libelle">${libelle}</div></div>`)
    .join("");
}
$("#btn-rafraichir").addEventListener("click", chargerTableau);

/* -------------------------------------------------------------- modes */
function basculerMode(mode) {
  document.querySelectorAll(".modes button").forEach((b) => b.classList.toggle("actif", b.dataset.mode === mode));
  document.querySelectorAll(".vue").forEach((v) => v.classList.remove("visible"));
  $(`#vue-${mode}`).classList.add("visible");
  if (mode === "pilotage") chargerTableau();
}
document.querySelectorAll(".modes button").forEach((bouton) => {
  bouton.addEventListener("click", () => basculerMode(bouton.dataset.mode));
});

/* ------------------------------------------------------------- départ */
chargerReferentiel().then(() => majEtapes());
