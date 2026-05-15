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
        </div>
      </section>

      <section class="control-panel">
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
          <button id="runButton" class="button primary" type="button">Run lead search</button>
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
                <th>Company</th>
                <th>Role</th>
                <th>Country</th>
                <th>Illness</th>
                <th>Workshop</th>
                <th>Pitch angle</th>
              </tr>
            </thead>
            <tbody id="resultsBody">
              <tr>
                <td colspan="6" class="empty">Run a search to generate your first lead set.</td>
              </tr>
            </tbody>
          </table>
        </div>
      </section>
    </main>
    <script src="/app.js"></script>
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
const selectedRolesEl = document.querySelector("#selectedRoles");
const selectedLocationsEl = document.querySelector("#selectedLocations");
const customRole = document.querySelector("#customRole");
const customLocation = document.querySelector("#customLocation");
const addRoleButton = document.querySelector("#addRoleButton");
const addLocationButton = document.querySelector("#addLocationButton");
const limitInput = document.querySelector("#limit");
const runButton = document.querySelector("#runButton");
const csvButton = document.querySelector("#csvButton");
const sheetsButton = document.querySelector("#sheetsButton");
const message = document.querySelector("#message");
const resultsTitle = document.querySelector("#resultsTitle");
const totalCount = document.querySelector("#totalCount");
const successCount = document.querySelector("#successCount");
const failedCount = document.querySelector("#failedCount");
const resultsBody = document.querySelector("#resultsBody");

const ROLE_PRESETS = [
  "VP Product",
  "Head of Product",
  "Chief Product Officer",
  "Director of Product",
  "Group Product Manager",
  "Product Operations Lead",
];
const LOCATION_PRESETS = [
  "United States",
  "Canada",
  "Mexico",
  "United Kingdom",
  "Germany",
  "Spain",
];
const MAX_ROLES = 5;
const MAX_LOCATIONS = 6;
let selectedRoles = new Set(["VP Product", "Head of Product"]);
let selectedLocations = new Set(["United States", "Canada", "Mexico"]);
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
  runButton.textContent = isLoading ? "Running..." : "Run lead search";
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

function renderResults(payload) {
  latestRows = payload.rows;
  latestCsv = payload.csv;
  const summary = payload.summary;
  console.info("Leadseek run completed", payload);

  resultsTitle.textContent =
    summary.succeeded > 0 ? "Workshop-ready leads" : "No leads generated";
  totalCount.textContent = summary.total;
  successCount.textContent = summary.succeeded;
  failedCount.textContent = summary.failed;
  csvButton.disabled = latestRows.length === 0;
  sheetsButton.disabled = latestRows.length === 0;

  resultsBody.innerHTML = "";
  if (!latestRows.length) {
    resultsBody.innerHTML =
      '<tr><td colspan="6" class="empty">No usable lead rows came back from this run.</td></tr>';
    return;
  }

  for (const row of latestRows) {
    const tr = document.createElement("tr");
    tr.innerHTML = `
      <td><a href="${escapeAttr(row.job_url)}" target="_blank" rel="noreferrer">${escapeHtml(row.company_name)}</a></td>
      <td>${escapeHtml(row.job_title)}</td>
      <td>${escapeHtml(row.country)}</td>
      <td>${escapeHtml(row.core_illness)}</td>
      <td>${escapeHtml(row.workshop_pitch)}</td>
      <td>${escapeHtml(row.pitch_angle)}</td>
    `;
    resultsBody.appendChild(tr);
  }
}

async function runLeads() {
  const roles = [...selectedRoles];
  const locations = [...selectedLocations];

  if (!roles.length || !locations.length) {
    setMessage("Choose at least one role and one location.", true);
    return;
  }

  setLoading(true);
  setMessage("Searching live jobs and diagnosing signals. This can take a minute.");
  console.info("Leadseek run started", { roles, locations, limit: Number(limitInput.value || 10) });

  try {
    const response = await fetch("/api/run", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        roles,
        locations,
        limit: Number(limitInput.value || 10),
      }),
    });

    const payload = await response.json();
    if (!response.ok) {
      console.error("Leadseek run failed", payload);
      throw new Error(detailMessage(payload));
    }

    renderResults(payload);
    setMessage(`Generated ${payload.summary.succeeded} lead rows. Run ID: ${payload.run_id}.`);
  } catch (error) {
    console.error("Leadseek frontend error", error);
    setMessage(error.message, true);
  } finally {
    setLoading(false);
  }
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
csvButton.addEventListener("click", downloadCsv);
sheetsButton.addEventListener("click", exportSheets);
renderControls();
"""
