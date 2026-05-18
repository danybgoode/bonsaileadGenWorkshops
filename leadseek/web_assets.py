"""Embedded web UI assets for Vercel's Python function bundle."""

INDEX_HTML = """<!doctype html>
<html lang="en">
  <head>
    <meta charset="utf-8" />
    <meta name="viewport" content="width=device-width, initial-scale=1" />
    <title>Leadseek</title>
    <link rel="stylesheet" href="/styles.css" />
  </head>
  <body>
    <main class="app-shell">
      <aside class="status-island" id="statusIsland" aria-live="polite">
        <div class="mascot-wrap">
          <img src="/snowball.svg" alt="" class="mascot" />
          <span class="mascot-fallback"></span>
        </div>
        <div class="island-copy">
          <strong id="islandTitle">Ready</strong>
          <span id="islandDetail">Choose providers, roles, and locations.</span>
          <div class="progress-track"><div id="progressFill" class="progress-fill"></div></div>
        </div>
        <button id="toggleLogButton" class="log-toggle" type="button">Logs</button>
        <div id="activityLog" class="activity-log"></div>
      </aside>

      <section class="hero">
        <div>
          <p class="eyebrow">B2B Lead Generation</p>
          <h1>Find senior product teams showing buying intent.</h1>
          <p class="hero-copy">
            Search live product leadership roles, diagnose the hidden product
            dysfunction, and export workshop-ready leads in one flow.
          </p>
        </div>
        <div class="status-card">
          <span>Pipeline</span>
          <strong>Jobs -> Diagnosis -> CSV -> Sheets</strong>
          <small id="usageStatus">Checking SerpApi usage...</small>
        </div>
      </section>

      <section class="control-panel">
        <div class="field-group">
          <div class="label-row">
            <label>Job data sources</label>
            <small>Use one or both</small>
          </div>
          <div class="preset-grid" id="providerButtons"></div>
        </div>

        <div class="field-group">
          <div class="label-row">
            <label>Target roles</label>
            <small id="rolesHint">Choose up to 5</small>
          </div>
          <div class="preset-grid" id="roleButtons"></div>
          <div class="custom-row">
            <input id="customRole" type="text" placeholder="Add custom role" autocomplete="off" />
            <button class="button compact" id="addRoleButton" type="button">Add</button>
          </div>
        </div>

        <div class="field-group">
          <div class="label-row">
            <label>Locations</label>
            <small id="locationsHint">Choose up to 6</small>
          </div>
          <div class="preset-grid" id="locationButtons"></div>
          <div class="custom-row">
            <input id="customLocation" type="text" placeholder="Add custom location" autocomplete="off" />
            <button class="button compact" id="addLocationButton" type="button">Add</button>
          </div>
        </div>

        <div class="selected-panel">
          <div>
            <span>Selected roles</span>
            <div class="chip-input" id="selectedRoles"></div>
          </div>
          <div>
            <span>Selected locations</span>
            <div class="chip-input" id="selectedLocations"></div>
          </div>
        </div>

        <div class="control-row">
          <label class="limit-control" for="limit">
            <span>Lead limit</span>
            <input id="limit" type="number" min="1" max="25" value="10" />
          </label>
          <div class="run-note">
            Results are mixed across every selected role/location pair before
            paging deeper into any one country.
          </div>
        </div>

        <div class="actions">
          <button id="runButton" class="button primary" type="button">Fetch jobs</button>
          <button id="enrichButton" class="button" type="button" disabled>Enrich selected</button>
          <button id="csvButton" class="button" type="button" disabled>Download CSV</button>
          <button id="sheetsButton" class="button" type="button" disabled>Export to Google Sheets</button>
        </div>
        <p id="message" class="message" role="status"></p>
      </section>

      <section class="results-panel">
        <div class="results-heading">
          <div>
            <p class="eyebrow">Results</p>
            <h2 id="resultsTitle">No run yet</h2>
          </div>
          <div class="summary-grid" aria-label="Run summary">
            <div><span id="totalCount">0</span><small>Total</small></div>
            <div><span id="successCount">0</span><small>Ready</small></div>
            <div><span id="failedCount">0</span><small>Skipped</small></div>
          </div>
        </div>

        <div class="table-wrap">
          <table>
            <thead>
              <tr>
                <th>Select</th>
                <th>Company</th>
                <th>Role</th>
                <th>Country</th>
                <th>Summary</th>
                <th>Status</th>
                <th>Illness</th>
                <th>Workshop</th>
                <th>Pitch angle</th>
              </tr>
            </thead>
            <tbody id="resultsBody">
              <tr>
                <td colspan="9" class="empty">Fetch jobs to generate your first lead set.</td>
              </tr>
            </tbody>
          </table>
        </div>
      </section>

      <section class="control-panel" id="merchantSection">
        <h2 style="margin:0 0 4px">🏪 Merchant Acquisition</h2>
        <p style="margin:0 0 20px;color:var(--text-muted,#888);font-size:.9rem">Find businesses for despachobonsai.com</p>

        <div class="field-group">
          <div class="label-row"><label>Data source</label></div>
          <div class="preset-grid">
            <label class="preset-btn" style="display:flex;align-items:center;gap:6px;cursor:pointer">
              <input type="radio" name="sellerSource" value="serpapi" checked id="sellerSourceSerpapi" />
              SerpAPI Google Local
            </label>
            <label class="preset-btn" style="display:flex;align-items:center;gap:6px;cursor:pointer">
              <input type="radio" name="sellerSource" value="unclaimed" id="sellerSourceUnclaimed" />
              Unclaimed Miyagisanchez Shops
            </label>
          </div>
        </div>

        <div class="field-group" id="sellerSerpFields">
          <div class="label-row"><label>Search query</label></div>
          <input id="sellerQuery" type="text" placeholder="taller mecánico" style="width:100%;box-sizing:border-box" autocomplete="off" />

          <div class="label-row" style="margin-top:12px"><label>Location</label></div>
          <input id="sellerLocation" type="text" value="Ciudad de México, Mexico" style="width:100%;box-sizing:border-box" autocomplete="off" />

          <div class="label-row" style="margin-top:12px"><label>State</label></div>
          <input id="sellerState" type="text" value="Ciudad de México" style="width:100%;box-sizing:border-box" autocomplete="off" />
        </div>

        <div class="control-row" style="margin-top:12px">
          <label class="limit-control" for="sellerLimit">
            <span>Limit</span>
            <input id="sellerLimit" type="number" min="1" max="100" value="20" />
          </label>
          <label style="display:flex;align-items:center;gap:8px;cursor:pointer">
            <input type="checkbox" id="sellerEnrich" checked />
            <span>Enrich with Gemini</span>
          </label>
        </div>

        <div class="actions" style="margin-top:16px">
          <button id="sellerRunButton" class="button primary" type="button">Run</button>
          <button id="sellerExportButton" class="button" type="button" style="display:none">Export CSV</button>
        </div>

        <div id="sellerStatus" style="margin-top:12px;font-size:.85rem;color:var(--text-muted,#888)"></div>

        <div class="results-panel" id="sellerResultsPanel" style="display:none;margin-top:16px;overflow-x:auto">
          <table class="results-table">
            <thead>
              <tr>
                <th>Business</th>
                <th>Type</th>
                <th>City</th>
                <th>Rating</th>
                <th>Pain Category</th>
                <th>Urgency</th>
                <th>Outreach Angle</th>
                <th>Fit Score</th>
                <th>Actions</th>
              </tr>
            </thead>
            <tbody id="sellerResultsBody">
              <tr><td colspan="9" class="empty">Run to find merchant leads.</td></tr>
            </tbody>
          </table>
        </div>
      </section>
    </main>
    <script src="/app.js"></script>
    <script>
(function () {
  // Merchant Acquisition section — self-contained, no shared state with job leads JS

  var lastSellerCsv = "";

  function setSellerStatus(msg) {
    document.getElementById("sellerStatus").textContent = msg;
  }

  function sourceChanged() {
    var isSerpapi = document.getElementById("sellerSourceSerpapi").checked;
    document.getElementById("sellerSerpFields").style.display = isSerpapi ? "" : "none";
  }

  document.querySelectorAll("input[name='sellerSource']").forEach(function (el) {
    el.addEventListener("change", sourceChanged);
  });
  sourceChanged();

  document.getElementById("sellerRunButton").addEventListener("click", function () {
    var source = document.querySelector("input[name='sellerSource']:checked").value;
    var query = document.getElementById("sellerQuery").value.trim();
    var location = document.getElementById("sellerLocation").value.trim();
    var state = document.getElementById("sellerState").value.trim();
    var limit = parseInt(document.getElementById("sellerLimit").value, 10) || 20;
    var enrich = document.getElementById("sellerEnrich").checked;

    if (source === "serpapi" && !query) {
      setSellerStatus("Please enter a search query.");
      return;
    }

    var btn = document.getElementById("sellerRunButton");
    btn.disabled = true;
    btn.textContent = "Running…";
    setSellerStatus("Fetching leads…");
    document.getElementById("sellerExportButton").style.display = "none";

    fetch("/api/seller-leads/run", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ source: source, query: query, location: location, state: state, limit: limit, enrich: enrich })
    })
      .then(function (r) { return r.json(); })
      .then(function (data) {
        btn.disabled = false;
        btn.textContent = "Run";
        if (data.error) {
          setSellerStatus("Error: " + data.error);
          return;
        }
        var leads = data.leads || [];
        lastSellerCsv = data.csv || "";
        setSellerStatus("Found " + leads.length + " leads (" + (data.summary && data.summary.enriched || 0) + " enriched).");
        renderSellerTable(leads);
        document.getElementById("sellerResultsPanel").style.display = "";
        if (lastSellerCsv) document.getElementById("sellerExportButton").style.display = "";
      })
      .catch(function (err) {
        btn.disabled = false;
        btn.textContent = "Run";
        setSellerStatus("Request failed: " + err.message);
      });
  });

  document.getElementById("sellerExportButton").addEventListener("click", function () {
    if (!lastSellerCsv) return;
    var blob = new Blob([lastSellerCsv], { type: "text/csv" });
    var url = URL.createObjectURL(blob);
    var a = document.createElement("a");
    a.href = url;
    a.download = "seller_leads.csv";
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    URL.revokeObjectURL(url);
  });

  function painBadge(category) {
    var labels = {
      "single_channel_trap": "Single Channel",
      "offline_only": "Offline Only",
      "fragmented_ops": "Fragmented Ops",
      "no_online_presence": "No Online Presence"
    };
    return labels[category] || category || "—";
  }

  function renderSellerTable(leads) {
    var tbody = document.getElementById("sellerResultsBody");
    if (!leads || !leads.length) {
      tbody.innerHTML = "<tr><td colspan='9' class='empty'>No leads found.</td></tr>";
      return;
    }
    var rows = leads.map(function (lead) {
      var diag = lead.diagnosis || {};
      var shopLink = lead.miyagisanchez_shop_url
        ? "<a href='" + lead.miyagisanchez_shop_url + "' target='_blank' rel='noreferrer'>View Shop</a>"
        : "—";
      var fitScore = diag.fit_score != null ? diag.fit_score : "—";
      var fitColor = diag.fit_score >= 70 ? "color:#22c55e" : diag.fit_score >= 40 ? "color:#f59e0b" : "";
      return "<tr>" +
        "<td>" + esc(lead.business_name) + "</td>" +
        "<td>" + esc(lead.business_type || "—") + "</td>" +
        "<td>" + esc(lead.city || "—") + "</td>" +
        "<td>" + (lead.rating != null ? lead.rating + " ⭐" : "—") + "</td>" +
        "<td>" + esc(painBadge(diag.pain_category)) + "</td>" +
        "<td style='text-align:center'>" + (diag.urgency != null ? diag.urgency + "/5" : "—") + "</td>" +
        "<td style='max-width:220px;white-space:normal'>" + esc(diag.suggested_outreach || "—") + "</td>" +
        "<td style='text-align:center;" + fitColor + "'>" + fitScore + "</td>" +
        "<td>" + shopLink + "</td>" +
        "</tr>";
    });
    tbody.innerHTML = rows.join("");
  }

  function esc(str) {
    return String(str).replace(/&/g, "&amp;").replace(/</g, "&lt;").replace(/>/g, "&gt;").replace(/"/g, "&quot;");
  }
})();
    </script>
  </body>
</html>
"""

STYLES_CSS = """
:root {
  --ink: #101510;
  --muted: #627064;
  --line: rgba(16, 21, 16, 0.12);
  --panel: rgba(255, 255, 255, 0.62);
  --panel-strong: rgba(255, 255, 255, 0.8);
  --primary: #173f35;
  --primary-ink: #f7fff7;
  --shadow: 0 24px 70px rgba(34, 49, 37, 0.14),
    inset 0 1px 0 rgba(255, 255, 255, 0.7);
}
* { box-sizing: border-box; }
body {
  margin: 0;
  min-width: 320px;
  background:
    linear-gradient(120deg, rgba(183, 215, 206, 0.48), transparent 34%),
    linear-gradient(285deg, rgba(241, 197, 157, 0.45), transparent 34%),
    linear-gradient(145deg, #f8f8f3 0%, #edf4ef 50%, #f8f2e9 100%);
  color: var(--ink);
  font-family: ui-sans-serif, -apple-system, BlinkMacSystemFont, "SF Pro Display", "Segoe UI", sans-serif;
  letter-spacing: 0;
}
button, input { font: inherit; }
.app-shell {
  width: min(calc(100% - 2rem), 1180px);
  margin: 0 auto;
  padding: clamp(1rem, 3vw, 1.5rem) 0 3rem;
}
.status-island {
  position: sticky;
  top: 0.75rem;
  z-index: 20;
  display: grid;
  grid-template-columns: 48px minmax(0, 1fr) auto;
  gap: 0.75rem;
  align-items: center;
  border: 1px solid rgba(255, 255, 255, 0.78);
  border-radius: 28px;
  padding: 0.7rem;
  background: rgba(16, 21, 16, 0.84);
  color: #f7fff7;
  box-shadow: 0 24px 70px rgba(16, 21, 16, 0.22);
  backdrop-filter: blur(26px) saturate(1.2);
}
.mascot-wrap {
  position: relative;
  display: grid;
  width: 44px;
  height: 44px;
  place-items: center;
}
.mascot {
  width: 42px;
  height: 42px;
  object-fit: contain;
  animation: mascot-hop 900ms ease-in-out infinite;
}
.mascot-fallback {
  display: none;
  width: 26px;
  height: 26px;
  border-radius: 999px;
  background: linear-gradient(135deg, #fdd14f, #ed488b 60%, #4b7bb2);
  animation: mascot-hop 900ms ease-in-out infinite;
}
.mascot:not([src]), .mascot[src=""] { display: none; }
.mascot:not([src]) + .mascot-fallback, .mascot[src=""] + .mascot-fallback { display: block; }
@keyframes mascot-hop {
  0%, 100% { transform: translateY(2px) rotate(-3deg); }
  50% { transform: translateY(-7px) rotate(4deg); }
}
.island-copy {
  display: grid;
  gap: 0.25rem;
  min-width: 0;
}
.island-copy strong {
  font-size: 0.95rem;
}
.island-copy span {
  overflow: hidden;
  color: rgba(247, 255, 247, 0.72);
  font-size: 0.82rem;
  text-overflow: ellipsis;
  white-space: nowrap;
}
.progress-track {
  height: 5px;
  overflow: hidden;
  border-radius: 999px;
  background: rgba(255, 255, 255, 0.14);
}
.progress-fill {
  width: 0%;
  height: 100%;
  border-radius: inherit;
  background: linear-gradient(90deg, #b7d7ce, #f1c59d, #bad7ec);
  transition: width 240ms ease;
}
.log-toggle {
  border: 1px solid rgba(255, 255, 255, 0.2);
  border-radius: 999px;
  padding: 0.55rem 0.7rem;
  background: rgba(255, 255, 255, 0.1);
  color: #f7fff7;
  cursor: pointer;
  font-weight: 760;
}
.activity-log {
  display: none;
  grid-column: 1 / -1;
  max-height: 180px;
  overflow: auto;
  border-top: 1px solid rgba(255, 255, 255, 0.12);
  padding-top: 0.6rem;
  color: rgba(247, 255, 247, 0.76);
  font-size: 0.78rem;
  line-height: 1.45;
}
.status-island.open .activity-log {
  display: grid;
  gap: 0.35rem;
}
.activity-log div::before {
  content: "•";
  margin-right: 0.45rem;
  color: #f1c59d;
}
.hero {
  display: grid;
  gap: 1.25rem;
  align-items: end;
  min-height: 34svh;
  padding: clamp(2.5rem, 8vw, 5rem) 0 2rem;
}
.eyebrow {
  margin: 0 0 0.75rem;
  color: var(--primary);
  font-size: 0.78rem;
  font-weight: 760;
  letter-spacing: 0.08em;
  text-transform: uppercase;
}
h1, h2 {
  margin: 0;
  line-height: 0.98;
  letter-spacing: 0;
  text-wrap: balance;
}
h1 { max-width: 880px; font-size: clamp(3rem, 7vw, 6rem); }
h2 { font-size: clamp(1.7rem, 4vw, 3.3rem); }
.hero-copy {
  max-width: 760px;
  margin: 1.2rem 0 0;
  color: var(--muted);
  font-size: clamp(1.06rem, 2.2vw, 1.35rem);
  line-height: 1.5;
}
.status-card, .control-panel, .results-panel {
  border: 1px solid rgba(255, 255, 255, 0.68);
  background: linear-gradient(145deg, var(--panel-strong), rgba(255, 255, 255, 0.36)), var(--panel);
  box-shadow: var(--shadow);
  backdrop-filter: blur(24px) saturate(1.25);
}
.status-card { border-radius: 24px; padding: 1rem; }
.status-card span { display: block; color: var(--muted); font-size: 0.82rem; }
.status-card strong { display: block; margin-top: 0.35rem; }
.control-panel, .results-panel {
  border-radius: 30px;
  padding: clamp(1rem, 3vw, 1.5rem);
}
.field-group { display: grid; gap: 0.75rem; margin-bottom: 1.2rem; }
.label-row {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 1rem;
}
label, .limit-control span, .selected-panel span {
  color: rgba(16, 21, 16, 0.72);
  font-size: 0.9rem;
  font-weight: 760;
}
small, .run-note {
  color: var(--muted);
  font-size: 0.86rem;
  line-height: 1.45;
}
input {
  width: 100%;
  min-height: 50px;
  border: 1px solid var(--line);
  border-radius: 16px;
  padding: 0.85rem 0.9rem;
  background: rgba(255, 255, 255, 0.68);
  color: var(--ink);
  outline: none;
}
input:focus {
  border-color: rgba(23, 63, 53, 0.42);
  box-shadow: 0 0 0 4px rgba(183, 215, 206, 0.35);
}
.preset-grid, .chip-input, .actions {
  display: flex;
  flex-wrap: wrap;
  gap: 0.55rem;
}
.preset-button, .chip, .button {
  border: 1px solid rgba(255, 255, 255, 0.72);
  border-radius: 999px;
  background: rgba(255, 255, 255, 0.54);
  color: var(--ink);
  font-weight: 760;
}
.preset-button {
  min-height: 42px;
  padding: 0.65rem 0.85rem;
  cursor: pointer;
}
.preset-button.selected {
  border-color: rgba(23, 63, 53, 0.2);
  background: var(--primary);
  color: var(--primary-ink);
}
.chip {
  padding: 0.45rem 0.65rem;
  color: var(--primary);
  font-size: 0.84rem;
}
.chip button {
  margin-left: 0.4rem;
  border: 0;
  background: transparent;
  color: inherit;
  cursor: pointer;
  font-weight: 900;
}
.custom-row, .control-row, .selected-panel {
  display: grid;
  gap: 0.75rem;
}
.selected-panel {
  grid-template-columns: repeat(2, minmax(0, 1fr));
  margin: 0 0 1.2rem;
}
.selected-panel > div {
  border: 1px solid var(--line);
  border-radius: 18px;
  padding: 0.8rem;
  background: rgba(244, 246, 242, 0.42);
}
.selected-panel span { display: block; margin-bottom: 0.55rem; }
.button {
  min-height: 50px;
  padding: 0.85rem 1.05rem;
  cursor: pointer;
  box-shadow: var(--shadow);
}
.button.compact {
  min-height: 50px;
  box-shadow: none;
}
.button.primary {
  border-color: rgba(23, 63, 53, 0.2);
  background: var(--primary);
  color: var(--primary-ink);
}
.button:disabled { cursor: not-allowed; opacity: 0.45; }
.message {
  min-height: 1.4rem;
  margin: 1rem 0 0;
  color: var(--muted);
  line-height: 1.45;
}
.message.error { color: #9f2f22; }
.results-panel { margin-top: 1.2rem; }
.results-heading {
  display: grid;
  gap: 1rem;
  align-items: end;
  margin-bottom: 1rem;
}
.summary-grid {
  display: grid;
  grid-template-columns: repeat(3, minmax(0, 1fr));
  gap: 0.55rem;
}
.summary-grid div {
  border: 1px solid var(--line);
  border-radius: 16px;
  padding: 0.75rem;
  background: rgba(244, 246, 242, 0.48);
}
.summary-grid span, .summary-grid small { display: block; }
.summary-grid span { font-size: 1.5rem; font-weight: 800; }
.table-wrap {
  overflow-x: auto;
  border: 1px solid var(--line);
  border-radius: 20px;
}
table {
  width: 100%;
  min-width: 920px;
  border-collapse: collapse;
  background: rgba(255, 255, 255, 0.36);
}
th, td {
  border-bottom: 1px solid var(--line);
  padding: 0.85rem;
  text-align: left;
  vertical-align: top;
}
th {
  color: rgba(16, 21, 16, 0.68);
  font-size: 0.78rem;
  letter-spacing: 0.05em;
  text-transform: uppercase;
}
td { color: rgba(16, 21, 16, 0.84); font-size: 0.92rem; line-height: 1.45; }
td.empty { color: var(--muted); text-align: center; }
@media (min-width: 760px) {
  .hero { grid-template-columns: minmax(0, 1fr) 300px; }
  .custom-row { grid-template-columns: minmax(0, 1fr) 90px; }
  .control-row { grid-template-columns: 180px minmax(0, 1fr); align-items: center; }
  .results-heading { grid-template-columns: minmax(0, 1fr) 320px; }
}
@media (max-width: 680px) {
  .selected-panel { grid-template-columns: 1fr; }
  .actions, .button { width: 100%; }
}
"""

APP_JS = """
const roleButtons = document.querySelector("#roleButtons");
const locationButtons = document.querySelector("#locationButtons");
const providerButtons = document.querySelector("#providerButtons");
const selectedRolesEl = document.querySelector("#selectedRoles");
const selectedLocationsEl = document.querySelector("#selectedLocations");
const customRole = document.querySelector("#customRole");
const customLocation = document.querySelector("#customLocation");
const addRoleButton = document.querySelector("#addRoleButton");
const addLocationButton = document.querySelector("#addLocationButton");
const limitInput = document.querySelector("#limit");
const runButton = document.querySelector("#runButton");
const enrichButton = document.querySelector("#enrichButton");
const csvButton = document.querySelector("#csvButton");
const sheetsButton = document.querySelector("#sheetsButton");
const message = document.querySelector("#message");
const resultsTitle = document.querySelector("#resultsTitle");
const totalCount = document.querySelector("#totalCount");
const successCount = document.querySelector("#successCount");
const failedCount = document.querySelector("#failedCount");
const resultsBody = document.querySelector("#resultsBody");
const usageStatus = document.querySelector("#usageStatus");
const statusIsland = document.querySelector("#statusIsland");
const islandTitle = document.querySelector("#islandTitle");
const islandDetail = document.querySelector("#islandDetail");
const progressFill = document.querySelector("#progressFill");
const activityLog = document.querySelector("#activityLog");
const toggleLogButton = document.querySelector("#toggleLogButton");
const mascot = document.querySelector(".mascot");
const mascotFallback = document.querySelector(".mascot-fallback");

const ROLE_PRESETS = ["VP Product", "Head of Product", "Chief Product Officer", "Director of Product", "Group Product Manager", "Product Operations Lead"];
const LOCATION_PRESETS = ["United States", "Canada", "Mexico", "United Kingdom", "Germany", "Spain"];
const PROVIDER_PRESETS = [
  { label: "SerpApi Google Jobs", value: "serpapi" },
  { label: "Adzuna", value: "adzuna" },
];
const CSV_HEADERS = ["source", "job_url", "job_description_text", "country", "company_name", "job_title", "core_illness", "workshop_pitch", "pitch_angle", "fit_score", "urgency_score", "alignment_pain_score", "financial_pain_score", "execution_pain_score", "evidence", "nuance_summary", "recommended_strategy", "processed_at_utc"];
const MAX_ROLES = 5;
const MAX_LOCATIONS = 6;
let selectedRoles = new Set(["VP Product", "Head of Product"]);
let selectedLocations = new Set(["United States", "Canada", "Mexico"]);
let selectedProviders = new Set(["serpapi"]);
let latestJobs = [];
let latestRows = [];
let latestCsv = "";

function renderPresetButtons(container, values, selectedSet, toggleFn) {
  container.innerHTML = "";
  for (const value of values) {
    const button = document.createElement("button");
    button.type = "button";
    button.className = `preset-button ${selectedSet.has(value) ? "selected" : ""}`;
    button.textContent = value;
    button.addEventListener("click", () => toggleFn(value));
    container.appendChild(button);
  }
}

function renderProviderButtons() {
  providerButtons.innerHTML = "";
  for (const provider of PROVIDER_PRESETS) {
    const button = document.createElement("button");
    button.type = "button";
    button.className = `preset-button ${selectedProviders.has(provider.value) ? "selected" : ""}`;
    button.textContent = provider.label;
    button.addEventListener("click", () => {
      if (selectedProviders.has(provider.value)) {
        selectedProviders.delete(provider.value);
      } else {
        selectedProviders.add(provider.value);
      }
      if (!selectedProviders.size) {
        selectedProviders.add(provider.value);
        setMessage("Keep at least one provider selected.", true);
      }
      renderControls();
    });
    providerButtons.appendChild(button);
  }
}

function renderSelected(container, selectedSet, removeFn) {
  container.innerHTML = "";
  for (const value of selectedSet) {
    const chip = document.createElement("span");
    chip.className = "chip";
    chip.innerHTML = `${escapeHtml(value)}<button type="button" aria-label="Remove ${escapeAttr(value)}">x</button>`;
    chip.querySelector("button").addEventListener("click", () => removeFn(value));
    container.appendChild(chip);
  }
}

function normalizeValue(value) {
  return value.trim().replace(/\\s+/g, " ");
}

function toggleRole(value) {
  if (selectedRoles.has(value)) {
    selectedRoles.delete(value);
  } else if (selectedRoles.size < MAX_ROLES) {
    selectedRoles.add(value);
  } else {
    setMessage(`Use at most ${MAX_ROLES} roles per run.`, true);
  }
  renderControls();
}

function toggleLocation(value) {
  if (selectedLocations.has(value)) {
    selectedLocations.delete(value);
  } else if (selectedLocations.size < MAX_LOCATIONS) {
    selectedLocations.add(value);
  } else {
    setMessage(`Use at most ${MAX_LOCATIONS} locations per run.`, true);
  }
  renderControls();
}

function addCustom(set, input, max, label) {
  const value = normalizeValue(input.value);
  if (!value) return;
  if (set.size >= max && !set.has(value)) {
    setMessage(`Use at most ${max} ${label} per run.`, true);
    return;
  }
  set.add(value);
  input.value = "";
  setMessage("");
  renderControls();
}

function renderControls() {
  renderPresetButtons(roleButtons, ROLE_PRESETS, selectedRoles, toggleRole);
  renderPresetButtons(locationButtons, LOCATION_PRESETS, selectedLocations, toggleLocation);
  renderProviderButtons();
  renderSelected(selectedRolesEl, selectedRoles, (value) => {
    selectedRoles.delete(value);
    renderControls();
  });
  renderSelected(selectedLocationsEl, selectedLocations, (value) => {
    selectedLocations.delete(value);
    renderControls();
  });
}

function setMessage(text, isError = false) {
  message.textContent = text;
  message.classList.toggle("error", isError);
}

function setLoading(isLoading) {
  runButton.disabled = isLoading;
  runButton.textContent = isLoading ? "Fetching..." : "Fetch jobs";
}

function updateIsland(title, detail, percent = 0) {
  islandTitle.textContent = title;
  islandDetail.textContent = detail;
  progressFill.style.width = `${Math.max(0, Math.min(100, percent))}%`;
}

function addLog(text) {
  const line = document.createElement("div");
  line.textContent = `${new Date().toLocaleTimeString()} ${text}`;
  activityLog.prepend(line);
  while (activityLog.children.length > 80) activityLog.lastChild.remove();
}

function detailMessage(payload) {
  if (!payload) return "Request failed.";
  if (typeof payload.detail === "string") return payload.detail;
  if (payload.detail?.message) {
    const runId = payload.detail.run_id ? ` Run ID: ${payload.detail.run_id}.` : "";
    return `${payload.detail.message}${runId}`;
  }
  return payload.message || "Request failed.";
}

function renderJobs() {
  const enriched = latestJobs.filter((job) => job.record).length;
  const failed = latestJobs.filter((job) => job.status === "Failed").length;
  resultsTitle.textContent = latestJobs.length ? "Curate and enrich leads" : "No run yet";
  totalCount.textContent = latestJobs.length;
  successCount.textContent = enriched;
  failedCount.textContent = failed;
  enrichButton.disabled = latestJobs.length === 0 || latestJobs.every((job) => !job.selected);
  latestRows = latestJobs.filter((job) => job.record).map((job) => job.record);
  latestCsv = rowsToCsv(latestRows);
  csvButton.disabled = latestRows.length === 0;
  sheetsButton.disabled = latestRows.length === 0;
  resultsBody.innerHTML = "";
  if (!latestJobs.length) {
    resultsBody.innerHTML = '<tr><td colspan="9" class="empty">Fetch jobs to generate your first lead set.</td></tr>';
    return;
  }
  latestJobs.forEach((job, index) => {
    const row = job.record || {};
    const tr = document.createElement("tr");
    tr.innerHTML = `
      <td><input type="checkbox" data-index="${index}" ${job.selected ? "checked" : ""}></td>
      <td><a href="${escapeAttr(job.job_url)}" target="_blank" rel="noreferrer">${escapeHtml(job.company_name)}</a></td>
      <td>${escapeHtml(job.job_title)}</td>
      <td>${escapeHtml(job.country)}</td>
      <td>${escapeHtml(job.job_text_summary || "")}</td>
      <td>${escapeHtml(job.status || "Fetched")}</td>
      <td>${escapeHtml(row.core_illness || "")}</td>
      <td>${escapeHtml(row.workshop_pitch || "")}</td>
      <td>${escapeHtml(row.pitch_angle || "")}</td>
    `;
    const checkbox = tr.querySelector("input[type='checkbox']");
    checkbox.addEventListener("change", () => {
      job.selected = checkbox.checked;
      renderJobs();
    });
    resultsBody.appendChild(tr);
  });
}

async function runLeads() {
  const roles = [...selectedRoles];
  const locations = [...selectedLocations];
  const providers = [...selectedProviders];

  if (!roles.length || !locations.length || !providers.length) {
    setMessage("Choose at least one provider, role, and location.", true);
    return;
  }

  setLoading(true);
  setMessage("Fetching live jobs. Gemini enrichment will happen only after you choose leads.");
  updateIsland("Fetching jobs", "Starting provider queries", 5);
  addLog(`Fetch requested: providers=${providers.join("+")} roles=${roles.join(" | ")} locations=${locations.join(" | ")} limit=${limitInput.value}`);
  console.info("Leadseek run started", { providers, roles, locations, limit: Number(limitInput.value || 10) });

  try {
    latestJobs = [];
    latestRows = [];
    latestCsv = "";
    renderJobs();
    const targetLimit = Number(limitInput.value || 10);
    const combos = [];
    for (const provider of providers) {
      for (const role of roles) {
        for (const location of locations) combos.push({ provider, role, location });
      }
    }
    const perSliceLimit = Math.max(1, Math.ceil(targetLimit / combos.length));
    const seenUrls = new Set();
    let serpapiSearches = 0;
    let adzunaSearches = 0;

    for (const [comboIndex, combo] of combos.entries()) {
      if (latestJobs.length >= targetLimit) break;
      const percent = 5 + Math.round((comboIndex / combos.length) * 30);
      updateIsland("Fetching jobs", `${combo.provider}: ${combo.role} in ${combo.location}`, percent);
      addLog(`Fetching ${combo.provider}: ${combo.role} in ${combo.location}.`);
      const response = await fetch("/api/fetch-jobs", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          roles: [combo.role],
          locations: [combo.location],
          providers: [combo.provider],
          limit: perSliceLimit,
        }),
      });
      const payload = await response.json();
      if (!response.ok) {
        addLog(`Fetch warning: ${detailMessage(payload)}`);
        continue;
      }
      serpapiSearches += payload.summary.serpapi_searches_used || 0;
      adzunaSearches += payload.summary.adzuna_searches_used || 0;
      for (const job of payload.jobs) {
        if (latestJobs.length >= targetLimit) break;
        const key = job.job_url || `${job.company_name}-${job.job_title}-${job.country}`;
        if (seenUrls.has(key)) continue;
        seenUrls.add(key);
        latestJobs.push({
          ...job,
          id: `${payload.run_id}-${latestJobs.length}`,
          selected: true,
          status: "Fetched",
          record: null,
        });
      }
      renderJobs();
      addLog(`Fetched ${payload.jobs.length} from ${combo.provider}. Total candidates: ${latestJobs.length}.`);
      if (payload.summary.query_errors?.length) {
        payload.summary.query_errors.forEach((error) => addLog(`Provider warning: ${error}`));
      }
    }
    updateIsland("Jobs fetched", `${latestJobs.length} candidates ready`, 35);
    addLog(`Fetch complete. SerpApi searches=${serpapiSearches}; Adzuna searches=${adzunaSearches}.`);
    setMessage(`Fetched ${latestJobs.length} jobs. SerpApi: ${serpapiSearches}, Adzuna: ${adzunaSearches}.`);
    loadSerpApiUsage();
  } catch (error) {
    console.error("Leadseek frontend error", error);
    setMessage(error.message, true);
  } finally {
    setLoading(false);
  }
}

async function loadSerpApiUsage() {
  try {
    const response = await fetch("/api/serpapi-usage");
    const payload = await response.json();
    const usage = payload.usage || {};
    const adzuna = payload.adzuna_configured ? "Adzuna ready" : "Adzuna not configured";
    if (!payload.usage) {
      usageStatus.textContent = `SerpApi usage unavailable. ${adzuna}.`;
      return;
    }
    const used = usage.this_month_usage ?? "?";
    const left = usage.total_searches_left ?? usage.plan_searches_left ?? "?";
    const allowance = usage.searches_per_month ?? "?";
    usageStatus.textContent = `SerpApi: ${used}/${allowance} used, ${left} left. ${adzuna}.`;
  } catch (error) {
    usageStatus.textContent = "SerpApi usage unavailable.";
    console.warn("SerpApi usage lookup failed", error);
  }
}

async function enrichSelected() {
  const selected = latestJobs.filter((job) => job.selected && !job.record);
  if (!selected.length) {
    setMessage("Select at least one unenriched job.", true);
    return;
  }
  enrichButton.disabled = true;
  setMessage(`Enriching ${selected.length} selected jobs, one at a time.`);
  addLog(`Enrichment requested for ${selected.length} selected leads.`);
  for (const [index, job] of selected.entries()) {
    updateIsland("Enriching leads", `${index + 1}/${selected.length}: ${job.company_name}`, 35 + Math.round((index / selected.length) * 60));
    addLog(`Gemini enrichment started: ${job.company_name} — ${job.job_title}.`);
    job.status = "Enriching";
    renderJobs();
    try {
      const response = await fetch("/api/enrich-lead", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ job }),
      });
      const payload = await response.json();
      if (!response.ok) {
        throw new Error(detailMessage(payload));
      }
      job.record = payload.record;
      job.status = `Enriched ${payload.record.fit_score}/100`;
      addLog(`Enriched ${job.company_name}: fit ${payload.record.fit_score}/100, ${payload.record.core_illness}.`);
      console.info("Lead enriched", payload);
    } catch (error) {
      job.status = "Failed";
      job.error = error.message;
      addLog(`Enrichment failed for ${job.company_name}: ${error.message}`);
      console.error("Lead enrichment failed", { job, error });
    }
    renderJobs();
  }
  const succeeded = latestJobs.filter((job) => job.record).length;
  const failed = latestJobs.filter((job) => job.status === "Failed").length;
  updateIsland("Ready", `${succeeded} enriched, ${failed} failed`, 100);
  setMessage(`Enrichment complete. ${succeeded} ready, ${failed} failed.`);
}

function downloadCsv() {
  const blob = new Blob([latestCsv], { type: "text/csv;charset=utf-8" });
  const url = URL.createObjectURL(blob);
  const link = document.createElement("a");
  link.href = url;
  link.download = `leadseek-${new Date().toISOString().slice(0, 10)}.csv`;
  document.body.appendChild(link);
  link.click();
  link.remove();
  URL.revokeObjectURL(url);
}

async function exportSheets() {
  if (!latestRows.length) return;
  sheetsButton.disabled = true;
  setMessage("Creating a new Google Sheet...");
  console.info("Sheets export started", { rows: latestRows.length });

  try {
    const response = await fetch("/api/export/google-sheets", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ rows: latestRows }),
    });

    const payload = await response.json();
    if (!response.ok) {
      console.error("Sheets export failed", payload);
      throw new Error(detailMessage(payload));
    }

    setMessage(`Google Sheet created. Run ID: ${payload.run_id}.`);
    window.open(payload.url, "_blank", "noreferrer");
  } catch (error) {
    console.error("Sheets frontend error", error);
    setMessage(error.message, true);
  } finally {
    sheetsButton.disabled = false;
  }
}

function rowsToCsv(rows) {
  if (!rows.length) return "";
  const lines = [CSV_HEADERS.join(",")];
  for (const row of rows) {
    lines.push(CSV_HEADERS.map((header) => csvCell(row[header])).join(","));
  }
  return `${lines.join("\\n")}\\n`;
}

function csvCell(value) {
  const text = Array.isArray(value) ? value.join(" | ") : String(value ?? "");
  return `"${text.replaceAll('"', '""')}"`;
}

function escapeHtml(value) {
  return String(value ?? "")
    .replaceAll("&", "&amp;")
    .replaceAll("<", "&lt;")
    .replaceAll(">", "&gt;")
    .replaceAll('"', "&quot;")
    .replaceAll("'", "&#039;");
}

function escapeAttr(value) {
  return escapeHtml(value).replaceAll("`", "&#096;");
}

addRoleButton.addEventListener("click", () => addCustom(selectedRoles, customRole, MAX_ROLES, "roles"));
addLocationButton.addEventListener("click", () => addCustom(selectedLocations, customLocation, MAX_LOCATIONS, "locations"));
customRole.addEventListener("keydown", (event) => {
  if (event.key === "Enter") addCustom(selectedRoles, customRole, MAX_ROLES, "roles");
});
customLocation.addEventListener("keydown", (event) => {
  if (event.key === "Enter") addCustom(selectedLocations, customLocation, MAX_LOCATIONS, "locations");
});
runButton.addEventListener("click", runLeads);
enrichButton.addEventListener("click", enrichSelected);
csvButton.addEventListener("click", downloadCsv);
sheetsButton.addEventListener("click", exportSheets);
toggleLogButton.addEventListener("click", () => statusIsland.classList.toggle("open"));
mascot.addEventListener("error", () => {
  mascot.style.display = "none";
  mascotFallback.style.display = "block";
});
renderControls();
loadSerpApiUsage();
"""
