"""Pipeline orchestration for ingestion, diagnosis, and persistence."""

from __future__ import annotations

import os
from dataclasses import dataclass, field
from datetime import UTC, datetime
from pathlib import Path

from leadseek.config import AppConfig
from leadseek.diagnostics import DiagnosisError, GeminiDiagnostician
from leadseek.ingestion import IngestionError, iter_live_job_postings
from leadseek.models import LeadRecord
from leadseek.output import OutputError, save_leads
from leadseek.text_cleaning import prepare_job_description_for_gemini


class PipelineRunError(RuntimeError):
    """Raised when the pipeline cannot start or persist results."""


@dataclass(frozen=True)
class ProcessingFailure:
    job_url: str
    error: str


@dataclass(frozen=True)
class ProcessSummary:
    total: int
    succeeded: int
    failed: int
    failures: list[ProcessingFailure] = field(default_factory=list)


@dataclass(frozen=True)
class PipelineResult:
    records: list[LeadRecord]
    summary: ProcessSummary


def generate_leads(
    *,
    roles: list[str],
    locations: list[str],
    config: AppConfig,
    limit: int | None = None,
    fail_fast: bool = False,
) -> PipelineResult:
    """Run live ingestion and diagnosis, returning records without persistence."""

    if limit is not None and limit < 1:
        raise PipelineRunError("--limit must be greater than zero when provided.")

    fetch_limit = limit or 10
    os.environ.setdefault("SERPAPI_API_KEY", config.serpapi_api_key)

    try:
        postings = iter_live_job_postings(
            roles=roles,
            locations=locations,
            limit=fetch_limit,
        )
    except IngestionError as exc:
        raise PipelineRunError(str(exc)) from exc

    records: list[LeadRecord] = []
    failures: list[ProcessingFailure] = []

    with GeminiDiagnostician(
        api_key=config.gemini_api_key,
        model=config.gemini_model,
    ) as diagnostician:
        for posting in postings:
            try:
                gemini_input = prepare_job_description_for_gemini(
                    posting.job_description_text
                )
                if not gemini_input:
                    raise DiagnosisError("Job description was empty after cleaning.")

                diagnosis = diagnostician.diagnose(gemini_input)
                records.append(
                    LeadRecord.from_diagnosis(
                        posting=posting,
                        diagnosis=diagnosis,
                        processed_at_utc=datetime.now(UTC).isoformat(),
                    )
                )
            except DiagnosisError as exc:
                failure = ProcessingFailure(
                    job_url=posting.job_url,
                    error=str(exc),
                )
                failures.append(failure)
                if fail_fast:
                    break

    return PipelineResult(
        records=records,
        summary=ProcessSummary(
            total=len(postings),
            succeeded=len(records),
            failed=len(failures),
            failures=failures,
        ),
    )


def process_leads(
    *,
    roles: list[str],
    locations: list[str],
    output_path: Path,
    config: AppConfig,
    limit: int | None = None,
    fail_fast: bool = False,
) -> ProcessSummary:
    """Run the full lead diagnosis pipeline."""

    result = generate_leads(
        roles=roles,
        locations=locations,
        config=config,
        limit=limit,
        fail_fast=fail_fast,
    )

    try:
        save_leads(result.records, output_path)
    except OutputError as exc:
        raise PipelineRunError(str(exc)) from exc

    return result.summary
