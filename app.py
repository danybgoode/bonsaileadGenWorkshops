"""FastAPI web UI for Leadseek."""

from __future__ import annotations

from typing import Any

from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException
from fastapi.responses import HTMLResponse, Response
from pydantic import BaseModel, Field

from leadseek.config import AppConfig, ConfigError
from leadseek.output import CSV_HEADERS, records_to_csv_text
from leadseek.pipeline import PipelineRunError, generate_leads
from leadseek.sheets import SheetsExportError, export_rows_to_google_sheets
from leadseek.web_assets import APP_JS, INDEX_HTML, STYLES_CSS


load_dotenv()

app = FastAPI(title="Leadseek")


class RunLeadsRequest(BaseModel):
    roles: list[str] = Field(min_length=1)
    locations: list[str] = Field(min_length=1)
    limit: int = Field(default=10, ge=1, le=25)
    model: str | None = None


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


@app.post("/api/run")
def run_leads(request: RunLeadsRequest) -> dict[str, Any]:
    try:
        config = AppConfig.from_env(model_override=request.model)
        result = generate_leads(
            roles=request.roles,
            locations=request.locations,
            config=config,
            limit=request.limit,
            fail_fast=False,
        )
    except (ConfigError, PipelineRunError) as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc

    rows = [record.model_dump(mode="json") for record in result.records]
    return {
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
    try:
        url = export_rows_to_google_sheets(request.rows)
    except SheetsExportError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    return {"url": url}
