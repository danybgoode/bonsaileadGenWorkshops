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
          <label for="roles">Target roles</label>
          <div class="chip-input" id="rolesChips"></div>
          <input id="roles" type="text" value="VP Product, Head of Product" autocomplete="off" />
        </div>

        <div class="field-group">
          <label for="locations">Locations</label>
          <div class="chip-input" id="locationsChips"></div>
          <input id="locations" type="text" value="US, Canada, Mexico" autocomplete="off" />
        </div>

        <div class="control-row">
          <label class="limit-control" for="limit">
            <span>Lead limit</span>
            <input id="limit" type="number" min="1" max="25" value="10" />
          </label>
          <label class="model-control" for="model">
            <span>Gemini model</span>
            <select id="model">
              <option value="">Use .env default</option>
              <option value="gemini-2.5-flash">gemini-2.5-flash</option>
              <option value="gemini-2.5-pro">gemini-2.5-pro</option>
              <option value="gemini-3.1-pro-preview">gemini-3.1-pro-preview</option>
            </select>
          </label>
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

STYLES_CSS = """:root{--ink:#101510;--muted:#627064;--line:rgba(16,21,16,.12);--panel:rgba(255,255,255,.62);--panel-strong:rgba(255,255,255,.8);--primary:#173f35;--primary-ink:#f7fff7;--shadow:0 24px 70px rgba(34,49,37,.14),inset 0 1px 0 rgba(255,255,255,.7)}*{box-sizing:border-box}body{margin:0;min-width:320px;background:linear-gradient(120deg,rgba(183,215,206,.48),transparent 34%),linear-gradient(285deg,rgba(241,197,157,.45),transparent 34%),linear-gradient(145deg,#f8f8f3 0%,#edf4ef 50%,#f8f2e9 100%);color:var(--ink);font-family:ui-sans-serif,-apple-system,BlinkMacSystemFont,"SF Pro Display","Segoe UI",sans-serif;letter-spacing:0}button,input,select{font:inherit}.app-shell{width:min(calc(100% - 2rem),1180px);margin:0 auto;padding:clamp(1rem,3vw,1.5rem) 0 3rem}.hero{display:grid;gap:1.25rem;align-items:end;min-height:38svh;padding:clamp(3rem,9vw,6rem) 0 2rem}.eyebrow{margin:0 0 .75rem;color:var(--primary);font-size:.78rem;font-weight:760;letter-spacing:.08em;text-transform:uppercase}h1,h2{margin:0;line-height:.98;letter-spacing:0;text-wrap:balance}h1{max-width:880px;font-size:clamp(3rem,7vw,6rem)}h2{font-size:clamp(1.7rem,4vw,3.3rem)}.hero-copy{max-width:760px;margin:1.2rem 0 0;color:var(--muted);font-size:clamp(1.06rem,2.2vw,1.35rem);line-height:1.5}.status-card,.control-panel,.results-panel{border:1px solid rgba(255,255,255,.68);background:linear-gradient(145deg,var(--panel-strong),rgba(255,255,255,.36)),var(--panel);box-shadow:var(--shadow);backdrop-filter:blur(24px) saturate(1.25)}.status-card{border-radius:24px;padding:1rem}.status-card span{display:block;color:var(--muted);font-size:.82rem}.status-card strong{display:block;margin-top:.35rem}.control-panel,.results-panel{border-radius:30px;padding:clamp(1rem,3vw,1.5rem)}.field-group{display:grid;gap:.65rem;margin-bottom:1rem}label,.limit-control span,.model-control span{color:rgba(16,21,16,.72);font-size:.9rem;font-weight:760}input,select{width:100%;min-height:50px;border:1px solid var(--line);border-radius:16px;padding:.85rem .9rem;background:rgba(255,255,255,.68);color:var(--ink);outline:none}input:focus,select:focus{border-color:rgba(23,63,53,.42);box-shadow:0 0 0 4px rgba(183,215,206,.35)}.chip-input{display:flex;flex-wrap:wrap;gap:.45rem}.chip{border:1px solid rgba(23,63,53,.14);border-radius:999px;padding:.45rem .65rem;background:rgba(255,255,255,.5);color:var(--primary);font-size:.84rem;font-weight:720}.control-row{display:grid;gap:1rem}.actions{display:flex;flex-wrap:wrap;gap:.7rem;margin-top:1.2rem}.button{min-height:50px;border:1px solid rgba(255,255,255,.72);border-radius:999px;padding:.85rem 1.05rem;background:rgba(255,255,255,.54);color:var(--ink);font-weight:780;cursor:pointer;box-shadow:var(--shadow)}.button.primary{border-color:rgba(23,63,53,.2);background:var(--primary);color:var(--primary-ink)}.button:disabled{cursor:not-allowed;opacity:.45}.message{min-height:1.4rem;margin:1rem 0 0;color:var(--muted);line-height:1.45}.message.error{color:#9f2f22}.results-panel{margin-top:1.2rem}.results-heading{display:grid;gap:1rem;align-items:end;margin-bottom:1rem}.summary-grid{display:grid;grid-template-columns:repeat(3,minmax(0,1fr));gap:.55rem}.summary-grid div{border:1px solid var(--line);border-radius:16px;padding:.75rem;background:rgba(244,246,242,.48)}.summary-grid span,.summary-grid small{display:block}.summary-grid span{font-size:1.5rem;font-weight:800}.summary-grid small{color:var(--muted)}.table-wrap{overflow-x:auto;border:1px solid var(--line);border-radius:20px}table{width:100%;min-width:920px;border-collapse:collapse;background:rgba(255,255,255,.36)}th,td{border-bottom:1px solid var(--line);padding:.85rem;text-align:left;vertical-align:top}th{color:rgba(16,21,16,.68);font-size:.78rem;letter-spacing:.05em;text-transform:uppercase}td{color:rgba(16,21,16,.84);font-size:.92rem;line-height:1.45}td.empty{color:var(--muted);text-align:center}@media (min-width:760px){.hero{grid-template-columns:minmax(0,1fr) 300px}.control-row{grid-template-columns:180px minmax(0,1fr)}.results-heading{grid-template-columns:minmax(0,1fr) 320px}}@media (max-width:560px){.actions,.button{width:100%}}"""

APP_JS = """const rolesInput=document.querySelector("#roles");const locationsInput=document.querySelector("#locations");const rolesChips=document.querySelector("#rolesChips");const locationsChips=document.querySelector("#locationsChips");const limitInput=document.querySelector("#limit");const modelInput=document.querySelector("#model");const runButton=document.querySelector("#runButton");const csvButton=document.querySelector("#csvButton");const sheetsButton=document.querySelector("#sheetsButton");const message=document.querySelector("#message");const resultsTitle=document.querySelector("#resultsTitle");const totalCount=document.querySelector("#totalCount");const successCount=document.querySelector("#successCount");const failedCount=document.querySelector("#failedCount");const resultsBody=document.querySelector("#resultsBody");let latestRows=[];let latestCsv="";
function splitValues(value){return value.split(",").map((part)=>part.trim()).filter(Boolean)}
function renderChips(input,target){target.innerHTML="";for(const value of splitValues(input.value)){const chip=document.createElement("span");chip.className="chip";chip.textContent=value;target.appendChild(chip)}}
function setMessage(text,isError=false){message.textContent=text;message.classList.toggle("error",isError)}
function setLoading(isLoading){runButton.disabled=isLoading;runButton.textContent=isLoading?"Running...":"Run lead search"}
function renderResults(payload){latestRows=payload.rows;latestCsv=payload.csv;const summary=payload.summary;resultsTitle.textContent=summary.succeeded>0?"Workshop-ready leads":"No leads generated";totalCount.textContent=summary.total;successCount.textContent=summary.succeeded;failedCount.textContent=summary.failed;csvButton.disabled=latestRows.length===0;sheetsButton.disabled=latestRows.length===0;resultsBody.innerHTML="";if(!latestRows.length){resultsBody.innerHTML='<tr><td colspan="6" class="empty">No usable lead rows came back from this run.</td></tr>';return}for(const row of latestRows){const tr=document.createElement("tr");tr.innerHTML=`<td><a href="${escapeAttr(row.job_url)}" target="_blank" rel="noreferrer">${escapeHtml(row.company_name)}</a></td><td>${escapeHtml(row.job_title)}</td><td>${escapeHtml(row.country)}</td><td>${escapeHtml(row.core_illness)}</td><td>${escapeHtml(row.workshop_pitch)}</td><td>${escapeHtml(row.pitch_angle)}</td>`;resultsBody.appendChild(tr)}}
async function runLeads(){const roles=splitValues(rolesInput.value);const locations=splitValues(locationsInput.value);if(!roles.length||!locations.length){setMessage("Add at least one role and one location.",true);return}setLoading(true);setMessage("Searching live jobs and diagnosing signals. This can take a minute.");try{const response=await fetch("/api/run",{method:"POST",headers:{"Content-Type":"application/json"},body:JSON.stringify({roles,locations,limit:Number(limitInput.value||10),model:modelInput.value||null})});const payload=await response.json();if(!response.ok){throw new Error(payload.detail||"Lead run failed.")}renderResults(payload);setMessage(`Generated ${payload.summary.succeeded} lead rows.`)}catch(error){setMessage(error.message,true)}finally{setLoading(false)}}
function downloadCsv(){const blob=new Blob([latestCsv],{type:"text/csv;charset=utf-8"});const url=URL.createObjectURL(blob);const link=document.createElement("a");link.href=url;link.download=`leadseek-${new Date().toISOString().slice(0,10)}.csv`;document.body.appendChild(link);link.click();link.remove();URL.revokeObjectURL(url)}
async function exportSheets(){if(!latestRows.length)return;sheetsButton.disabled=true;setMessage("Creating a new Google Sheet...");try{const response=await fetch("/api/export/google-sheets",{method:"POST",headers:{"Content-Type":"application/json"},body:JSON.stringify({rows:latestRows})});const payload=await response.json();if(!response.ok){throw new Error(payload.detail||"Google Sheets export failed.")}setMessage("Google Sheet created. Opening it now.");window.open(payload.url,"_blank","noreferrer")}catch(error){setMessage(error.message,true)}finally{sheetsButton.disabled=false}}
function escapeHtml(value){return String(value??"").replaceAll("&","&amp;").replaceAll("<","&lt;").replaceAll(">","&gt;").replaceAll('"',"&quot;").replaceAll("'","&#039;")}
function escapeAttr(value){return escapeHtml(value).replaceAll("`","&#096;")}
rolesInput.addEventListener("input",()=>renderChips(rolesInput,rolesChips));locationsInput.addEventListener("input",()=>renderChips(locationsInput,locationsChips));runButton.addEventListener("click",runLeads);csvButton.addEventListener("click",downloadCsv);sheetsButton.addEventListener("click",exportSheets);renderChips(rolesInput,rolesChips);renderChips(locationsInput,locationsChips);"""
