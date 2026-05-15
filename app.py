"""FastAPI web UI for Leadseek."""

from __future__ import annotations

import logging
import uuid
from typing import Any

from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException
from fastapi.responses import HTMLResponse, Response
from pydantic import BaseModel, Field

from leadseek.config import AppConfig, ConfigError
from leadseek.ingestion import IngestionError, fetch_serpapi_account_usage
from leadseek.models import JobPosting
from leadseek.output import CSV_HEADERS, records_to_csv_text
from leadseek.pipeline import (
    PipelineRunError,
    enrich_posting,
    fetch_job_candidates,
    generate_leads,
)
from leadseek.sheets import SheetsExportError, export_rows_to_google_sheets
from leadseek.search_options import (
    LOCATION_PRESETS,
    MAX_LIMIT,
    MAX_LOCATIONS,
    MAX_ROLES,
    ROLE_PRESETS,
    normalize_search_terms,
)
from leadseek.web_assets import APP_JS, INDEX_HTML, STYLES_CSS


load_dotenv()
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(name)s %(message)s",
)
logger = logging.getLogger(__name__)

app = FastAPI(title="Leadseek")


class RunLeadsRequest(BaseModel):
    roles: list[str] = Field(min_length=1)
    locations: list[str] = Field(min_length=1)
    limit: int = Field(default=10, ge=1, le=MAX_LIMIT)


class EnrichLeadRequest(BaseModel):
    job: dict[str, Any]


class ExportSheetsRequest(BaseModel):
    rows: list[dict[str, Any]] = Field(min_length=1)


@app.get("/")
def index() -> HTMLResponse:
    return HTMLResponse(INDEX_HTML)


@app.get("/styles.css", include_in_schema=False)
def styles() -> Response:
    return Response(STYLES_CSS, media_type="text/css")


@app.get("/app.js", include_in_schema=False)
def frontend_script() -> Response:
    return Response(APP_JS, media_type="application/javascript")


@app.get("/api/health")
def health() -> dict[str, str]:
    return {"status": "ok"}


@app.get("/api/options")
def options() -> dict[str, Any]:
    return {
        "roles": ROLE_PRESETS,
        "locations": LOCATION_PRESETS,
        "max_roles": MAX_ROLES,
        "max_locations": MAX_LOCATIONS,
        "max_limit": MAX_LIMIT,
    }


@app.get("/api/serpapi-usage")
def serpapi_usage() -> dict[str, Any]:
    try:
        usage = fetch_serpapi_account_usage()
    except IngestionError as exc:
        logger.warning("SerpApi usage lookup failed: %s", exc)
        raise HTTPException(
            status_code=400,
            detail={"message": str(exc), "run_id": "usage"},
        ) from exc
    return {"usage": usage}


def _validated_search_inputs(request: RunLeadsRequest) -> tuple[list[str], list[str]]:
    roles = normalize_search_terms(
        request.roles,
        label="roles",
        max_items=MAX_ROLES,
    )
    locations = normalize_search_terms(
        request.locations,
        label="locations",
        max_items=MAX_LOCATIONS,
    )
    return roles, locations


@app.post("/api/fetch-jobs")
def fetch_jobs(request: RunLeadsRequest) -> dict[str, Any]:
    run_id = uuid.uuid4().hex[:10]
    try:
        roles, locations = _validated_search_inputs(request)
        logger.info(
            "UI fetch requested run_id=%s roles=%s locations=%s limit=%s",
            run_id,
            roles,
            locations,
            request.limit,
        )
        config = AppConfig.from_env()
        result = fetch_job_candidates(
            roles=roles,
            locations=locations,
            config=config,
            limit=request.limit,
        )
    except (ConfigError, PipelineRunError) as exc:
        logger.exception("UI fetch failed run_id=%s error=%s", run_id, exc)
        raise HTTPException(
            status_code=400,
            detail={"message": str(exc), "run_id": run_id},
        ) from exc
    except ValueError as exc:
        logger.warning("UI validation failed run_id=%s error=%s", run_id, exc)
        raise HTTPException(
            status_code=422,
            detail={"message": str(exc), "run_id": run_id},
        ) from exc

    jobs = [posting.model_dump(mode="json") for posting in result.postings]
    logger.info(
        "UI fetch completed run_id=%s jobs=%s serpapi_searches_used=%s",
        run_id,
        len(jobs),
        result.stats.serpapi_searches_used,
    )
    return {
        "run_id": run_id,
        "jobs": jobs,
        "summary": {
            "jobs": len(jobs),
            "serpapi_searches_used": result.stats.serpapi_searches_used,
            "query_errors": result.stats.query_errors,
        },
    }


@app.post("/api/enrich-lead")
def enrich_lead(request: EnrichLeadRequest) -> dict[str, Any]:
    run_id = uuid.uuid4().hex[:10]
    try:
        config = AppConfig.from_env()
        posting = JobPosting.model_validate(request.job)
        logger.info(
            "UI enrichment requested run_id=%s company=%r title=%r",
            run_id,
            posting.company_name,
            posting.job_title,
        )
        record = enrich_posting(posting=posting, config=config)
    except (ConfigError, PipelineRunError, ValueError) as exc:
        logger.exception("UI enrichment failed run_id=%s error=%s", run_id, exc)
        raise HTTPException(
            status_code=400,
            detail={"message": str(exc), "run_id": run_id},
        ) from exc

    logger.info("UI enrichment completed run_id=%s", run_id)
    return {"run_id": run_id, "record": record.model_dump(mode="json")}


@app.post("/api/run")
def run_leads(request: RunLeadsRequest) -> dict[str, Any]:
    run_id = uuid.uuid4().hex[:10]
    try:
        roles, locations = _validated_search_inputs(request)
        logger.info(
            "Legacy UI run requested run_id=%s roles=%s locations=%s limit=%s",
            run_id,
            roles,
            locations,
            request.limit,
        )
        config = AppConfig.from_env()
        result = generate_leads(
            roles=roles,
            locations=locations,
            config=config,
            limit=request.limit,
            fail_fast=False,
        )
    except (ConfigError, PipelineRunError) as exc:
        logger.exception("Legacy UI run failed run_id=%s error=%s", run_id, exc)
        raise HTTPException(
            status_code=400,
            detail={"message": str(exc), "run_id": run_id},
        ) from exc
    except ValueError as exc:
        logger.warning("Legacy UI validation failed run_id=%s error=%s", run_id, exc)
        raise HTTPException(
            status_code=422,
            detail={"message": str(exc), "run_id": run_id},
        ) from exc

    rows = [record.model_dump(mode="json") for record in result.records]
    logger.info(
        "UI run completed run_id=%s total=%s succeeded=%s failed=%s",
        run_id,
        result.summary.total,
        result.summary.succeeded,
        result.summary.failed,
    )
    return {
        "run_id": run_id,
        "headers": CSV_HEADERS,
        "rows": rows,
        "csv": records_to_csv_text(result.records),
        "summary": {
            "total": result.summary.total,
            "succeeded": result.summary.succeeded,
            "failed": result.summary.failed,
            "failures": [failure.__dict__ for failure in result.summary.failures],
        },
    }


@app.post("/api/export/google-sheets")
def export_google_sheets(request: ExportSheetsRequest) -> dict[str, str]:
    export_id = uuid.uuid4().hex[:10]
    logger.info("Sheets export requested export_id=%s rows=%s", export_id, len(request.rows))
    try:
        url = export_rows_to_google_sheets(request.rows)
    except SheetsExportError as exc:
        logger.exception("Sheets export failed export_id=%s error=%s", export_id, exc)
        raise HTTPException(
            status_code=400,
            detail={"message": str(exc), "run_id": export_id},
        ) from exc
    logger.info("Sheets export completed export_id=%s url=%s", export_id, url)
    return {"url": url, "run_id": export_id}
