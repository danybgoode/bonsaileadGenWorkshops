"""Pipeline orchestration for ingestion, diagnosis, and persistence."""

from __future__ import annotations

import logging
import os
from dataclasses import dataclass, field
from datetime import UTC, datetime
from pathlib import Path

from leadseek.config import AppConfig
from leadseek.diagnostics import DiagnosisError, GeminiDiagnostician
from leadseek.ingestion import (
    FetchStats,
    IngestionError,
    iter_live_job_postings,
    iter_live_job_postings_with_stats,
)
from leadseek.models import JobPosting, LeadRecord
from leadseek.output import OutputError, save_leads
from leadseek.service_context import get_service_context
from leadseek.text_cleaning import prepare_job_description_for_gemini


class PipelineRunError(RuntimeError):
    """Raised when the pipeline cannot start or persist results."""


logger = logging.getLogger(__name__)


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


@dataclass(frozen=True)
class FetchJobsResult:
    postings: list[JobPosting]
    stats: FetchStats


def fetch_job_candidates(
    *,
    roles: list[str],
    locations: list[str],
    config: AppConfig,
    limit: int | None = None,
    providers: list[str] | None = None,
) -> FetchJobsResult:
    """Fetch live jobs without Gemini enrichment."""

    if limit is not None and limit < 1:
        raise PipelineRunError("--limit must be greater than zero when provided.")

    fetch_limit = limit or 10
    if config.serpapi_api_key:
        os.environ.setdefault("SERPAPI_API_KEY", config.serpapi_api_key)
    logger.info(
        "Job fetch started providers=%s roles=%s locations=%s limit=%s",
        providers or ["serpapi"],
        roles,
        locations,
        fetch_limit,
    )

    try:
        postings, stats = iter_live_job_postings_with_stats(
            roles=roles,
            locations=locations,
            limit=fetch_limit,
            providers=providers,
        )
    except IngestionError as exc:
        raise PipelineRunError(str(exc)) from exc

    logger.info(
        "Job fetch finished postings=%s serpapi_searches_used=%s adzuna_searches_used=%s",
        len(postings),
        stats.serpapi_searches_used,
        stats.adzuna_searches_used,
    )
    return FetchJobsResult(postings=postings, stats=stats)


def enrich_posting(
    *,
    posting: JobPosting,
    config: AppConfig,
    service_context: str | None = None,
) -> LeadRecord:
    """Run Gemini enrichment for one curated job posting."""

    gemini_input = prepare_job_description_for_gemini(posting.job_description_text)
    if not gemini_input:
        raise PipelineRunError("Job description was empty after cleaning.")

    context = service_context if service_context is not None else get_service_context()
    with GeminiDiagnostician(
        api_key=config.gemini_api_key,
        model=config.gemini_model,
    ) as diagnostician:
        try:
            diagnosis = diagnostician.diagnose(
                gemini_input,
                service_context=context,
            )
        except DiagnosisError as exc:
            raise PipelineRunError(str(exc)) from exc

    return LeadRecord.from_diagnosis(
        posting=posting,
        diagnosis=diagnosis,
        processed_at_utc=datetime.now(UTC).isoformat(),
    )


def generate_leads(
    *,
    roles: list[str],
    locations: list[str],
    config: AppConfig,
    limit: int | None = None,
    fail_fast: bool = False,
    providers: list[str] | None = None,
) -> PipelineResult:
    """Run live ingestion and diagnosis, returning records without persistence."""

    if limit is not None and limit < 1:
        raise PipelineRunError("--limit must be greater than zero when provided.")

    fetch_limit = limit or 10
    if config.serpapi_api_key:
        os.environ.setdefault("SERPAPI_API_KEY", config.serpapi_api_key)
    logger.info(
        "Lead generation started providers=%s roles=%s locations=%s limit=%s fail_fast=%s",
        providers or ["serpapi"],
        roles,
        locations,
        fetch_limit,
        fail_fast,
    )

    try:
        postings = iter_live_job_postings(
            roles=roles,
            locations=locations,
            limit=fetch_limit,
            providers=providers,
        )
    except IngestionError as exc:
        raise PipelineRunError(str(exc)) from exc

    records: list[LeadRecord] = []
    failures: list[ProcessingFailure] = []
    service_context = get_service_context()

    with GeminiDiagnostician(
        api_key=config.gemini_api_key,
        model=config.gemini_model,
    ) as diagnostician:
        for posting in postings:
            try:
                logger.info(
                    "Diagnosing posting company=%r title=%r country=%r url=%s",
                    posting.company_name,
                    posting.job_title,
                    posting.country,
                    posting.job_url,
                )
                gemini_input = prepare_job_description_for_gemini(
                    posting.job_description_text
                )
                if not gemini_input:
                    raise DiagnosisError("Job description was empty after cleaning.")

                diagnosis = diagnostician.diagnose(
                    gemini_input,
                    service_context=service_context,
                )
                records.append(
                    LeadRecord.from_diagnosis(
                        posting=posting,
                        diagnosis=diagnosis,
                        processed_at_utc=datetime.now(UTC).isoformat(),
                    )
                )
                logger.info(
                    "Diagnosis succeeded company=%r title=%r",
                    posting.company_name,
                    posting.job_title,
                )
            except DiagnosisError as exc:
                failure = ProcessingFailure(
                    job_url=posting.job_url,
                    error=str(exc),
                )
                failures.append(failure)
                logger.warning("Diagnosis failed url=%s error=%s", posting.job_url, exc)
                if fail_fast:
                    break

    logger.info(
        "Lead generation finished total=%s succeeded=%s failed=%s",
        len(postings),
        len(records),
        len(failures),
    )
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
    providers: list[str] | None = None,
) -> ProcessSummary:
    """Run the full lead diagnosis pipeline."""

    result = generate_leads(
        roles=roles,
        locations=locations,
        config=config,
        limit=limit,
        fail_fast=fail_fast,
        providers=providers,
    )

    try:
        save_leads(result.records, output_path)
    except OutputError as exc:
        raise PipelineRunError(str(exc)) from exc

    return result.summary
