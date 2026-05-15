const rolesInput = document.querySelector("#roles");
const locationsInput = document.querySelector("#locations");
const rolesChips = document.querySelector("#rolesChips");
const locationsChips = document.querySelector("#locationsChips");
const limitInput = document.querySelector("#limit");
const modelInput = document.querySelector("#model");
const runButton = document.querySelector("#runButton");
const csvButton = document.querySelector("#csvButton");
const sheetsButton = document.querySelector("#sheetsButton");
const message = document.querySelector("#message");
const resultsTitle = document.querySelector("#resultsTitle");
const totalCount = document.querySelector("#totalCount");
const successCount = document.querySelector("#successCount");
const failedCount = document.querySelector("#failedCount");
const resultsBody = document.querySelector("#resultsBody");

let latestRows = [];
let latestCsv = "";

function splitValues(value) {
  return value
    .split(",")
    .map((part) => part.trim())
    .filter(Boolean);
}

function renderChips(input, target) {
  target.innerHTML = "";
  for (const value of splitValues(input.value)) {
    const chip = document.createElement("span");
    chip.className = "chip";
    chip.textContent = value;
    target.appendChild(chip);
  }
}

function setMessage(text, isError = false) {
  message.textContent = text;
  message.classList.toggle("error", isError);
}

function setLoading(isLoading) {
  runButton.disabled = isLoading;
  runButton.textContent = isLoading ? "Running..." : "Run lead search";
}

function renderResults(payload) {
  latestRows = payload.rows;
  latestCsv = payload.csv;
  const summary = payload.summary;

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
  const roles = splitValues(rolesInput.value);
  const locations = splitValues(locationsInput.value);

  if (!roles.length || !locations.length) {
    setMessage("Add at least one role and one location.", true);
    return;
  }

  setLoading(true);
  setMessage("Searching live jobs and diagnosing signals. This can take a minute.");

  try {
    const response = await fetch("/api/run", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        roles,
        locations,
        limit: Number(limitInput.value || 10),
        model: modelInput.value || null,
      }),
    });

    const payload = await response.json();
    if (!response.ok) {
      throw new Error(payload.detail || "Lead run failed.");
    }

    renderResults(payload);
    setMessage(`Generated ${payload.summary.succeeded} lead rows.`);
  } catch (error) {
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

  try {
    const response = await fetch("/api/export/google-sheets", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ rows: latestRows }),
    });

    const payload = await response.json();
    if (!response.ok) {
      throw new Error(payload.detail || "Google Sheets export failed.");
    }

    setMessage("Google Sheet created. Opening it now.");
    window.open(payload.url, "_blank", "noreferrer");
  } catch (error) {
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

rolesInput.addEventListener("input", () => renderChips(rolesInput, rolesChips));
locationsInput.addEventListener("input", () =>
  renderChips(locationsInput, locationsChips),
);
runButton.addEventListener("click", runLeads);
csvButton.addEventListener("click", downloadCsv);
sheetsButton.addEventListener("click", exportSheets);

renderChips(rolesInput, rolesChips);
renderChips(locationsInput, locationsChips);
