# Leadseek

A modular Python CLI for fetching live product-management job postings and
turning them into structured outbound consulting leads.

## Project Structure

```text
.
├── main.py
├── requirements.txt
├── .env.example
└── leadseek/
    ├── config.py
    ├── diagnostics.py
    ├── ingestion.py
    ├── models.py
    ├── output.py
    ├── pipeline.py
    └── prompts.py
```

## Setup

1. Create a Gemini API key in Google AI Studio.
2. Create a SerpApi API key for Google Jobs search.
3. Create and activate a virtual environment.
4. Install dependencies.
5. Copy `.env.example` to `.env` and set both API keys.

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
cp .env.example .env
```

## Usage

Fetch live jobs by role and location, diagnose them with Gemini, and append CSV
rows:

```bash
python main.py process-leads \
  --roles "VP Product, Head of Product" \
  --locations "US, Canada, Mexico" \
  --output leads.csv
```

Optional flags:

```bash
python main.py process-leads \
  --roles "VP Product, Head of Product" \
  --locations "US, Canada, Mexico" \
  --output leads.csv \
  --model gemini-2.5-flash \
  --limit 5 \
  --fail-fast
```

## Web UI

Run the local web interface:

```bash
uvicorn app:app --reload
```

Then open:

```text
http://127.0.0.1:8000
```

The UI lets you set roles, locations, and lead limit, then fetch candidate jobs,
select the best-fit leads, enrich only those leads with Gemini, download CSV, or
export the enriched result set to a new Google Sheet.
The Gemini model is read from `GEMINI_MODEL`; the UI intentionally does not
override it.

Searches are balanced across selected role/location pairs. For example, a run
with two roles, three countries, and a limit of 10 will take one result from
each pair before paging deeper into any single country.

## Google Sheets Export

Sheets export is optional. Create a Google Cloud service account with Google
Sheets and Drive API access, then set one of these environment variables:

```bash
GOOGLE_SERVICE_ACCOUNT_JSON='{"type":"service_account", ... }'
```

or, easier for hosted deploys:

```bash
GOOGLE_SERVICE_ACCOUNT_JSON_B64=base64_encoded_service_account_json
```

If you want each created sheet shared back to your normal Google account, set:

```bash
GOOGLE_SHEETS_SHARE_WITH=you@example.com
```

## Vercel Deploy

This project includes `app.py`, `requirements.txt`, `.python-version`, and
`vercel.json` for a FastAPI deployment on Vercel.

Set these Vercel environment variables:

```bash
GEMINI_API_KEY=...
GEMINI_MODEL=gemini-2.5-flash
SERPAPI_API_KEY=...
GOOGLE_SERVICE_ACCOUNT_JSON_B64=...
GOOGLE_SHEETS_SHARE_WITH=you@example.com
```

Small runs are the right fit for Vercel serverless execution. Keep `--limit` or
the UI lead limit around 5-10 for responsive mobile use.

## Service Context For Gemini

Gemini enrichment can use a richer consulting reference context. The app checks
these sources in order:

```bash
SERVICE_CONTEXT_TEXT="Your services, frameworks, proof points, and operating stack..."
```

or:

```bash
NOTION_TOKEN=secret_...
NOTION_PAGE_ID=...
```

If neither is set, the app uses the built-in default service context.

## Swapping Adapters

- Replace SerpApi ingestion by changing `fetch_live_jobs` or adding another
  function that yields `JobPosting` objects in `leadseek/ingestion.py`.
- Replace CSV persistence by changing only `save_leads` in
  `leadseek/output.py`. The rest of the pipeline passes validated
  `LeadRecord` objects into that function.

## Output CSV Columns

- `source`
- `job_url`
- `job_description_text`
- `country`
- `company_name`
- `job_title`
- `core_illness`
- `workshop_pitch`
- `pitch_angle`
- `processed_at_utc`
