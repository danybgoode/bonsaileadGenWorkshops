"""Live job ingestion adapters.

The production adapter uses SerpApi's Google Jobs API instead of scraping job
boards directly. The rest of the pipeline depends only on normalized
JobPosting objects, so another provider can replace this module without
touching Gemini diagnosis or output persistence.
"""

from __future__ import annotations

import logging
import os
import time
from dataclasses import dataclass, field
from typing import Any

import requests
from pydantic import ValidationError

from leadseek.models import JobPosting
from leadseek.search_options import MAX_LOCATIONS, MAX_ROLES, normalize_search_terms


SERPAPI_SEARCH_URL = "https://serpapi.com/search.json"
SERPAPI_ACCOUNT_URL = "https://serpapi.com/account.json"
ADZUNA_SEARCH_URL = "https://api.adzuna.com/v1/api/jobs/{country_code}/search/{page}"
DEFAULT_TIMEOUT_SECONDS = 30
logger = logging.getLogger(__name__)


@dataclass
class QueryState:
    provider: str
    role: str
    location: str
    next_page_token: str | None = None
    exhausted: bool = False
    buffer: list[tuple[str, JobPosting]] = field(default_factory=list)


@dataclass(frozen=True)
class FetchStats:
    serpapi_searches_used: int
    adzuna_searches_used: int
    query_errors: list[str]


@dataclass(frozen=True)
class LiveJobsResult:
    jobs: list[dict]
    stats: FetchStats


class IngestionError(RuntimeError):
    """Raised when live job postings cannot be loaded from the API provider."""


def fetch_serpapi_account_usage() -> dict[str, Any]:
    """Return SerpApi account usage details without consuming search credits."""

    api_key = os.getenv("SERPAPI_API_KEY")
    if not api_key:
        raise IngestionError("Missing SERPAPI_API_KEY in environment.")

    try:
        response = requests.get(
            SERPAPI_ACCOUNT_URL,
            params={"api_key": api_key},
            timeout=DEFAULT_TIMEOUT_SECONDS,
        )
    except requests.RequestException as exc:
        raise IngestionError(f"SerpApi account request failed: {exc}") from exc

    if response.status_code >= 400:
        raise IngestionError(f"SerpApi account API returned HTTP {response.status_code}.")

    payload = response.json()
    payload.pop("api_key", None)
    return payload


def fetch_live_jobs(
    roles: list,
    locations: list,
    limit: int = 10,
    providers: list[str] | None = None,
) -> list[dict]:
    """Fetch live job postings from configured job data providers.

    Args:
        roles: Target role queries, for example ["VP Product", "Head of Product"].
        locations: Target locations, for example ["US", "Canada", "Mexico"].
        limit: Maximum number of normalized postings to return across all queries.
        providers: Optional provider names, currently "serpapi" and "adzuna".

    Returns:
        A list of dictionaries with company_name, job_title,
        job_description_text, and job_url keys.

    Raises:
        IngestionError: Missing API key, rate limit, HTTP/API failure, bad input,
        or no usable job descriptions found.
    """

    return fetch_live_jobs_with_stats(roles, locations, limit, providers).jobs


def fetch_live_jobs_with_stats(
    roles: list,
    locations: list,
    limit: int = 10,
    providers: list[str] | None = None,
) -> LiveJobsResult:
    """Fetch live job postings with SerpApi usage metadata."""

    try:
        normalized_roles = normalize_search_terms(
            roles,
            label="roles",
            max_items=MAX_ROLES,
        )
        normalized_locations = normalize_search_terms(
            locations,
            label="locations",
            max_items=MAX_LOCATIONS,
        )
    except ValueError as exc:
        raise IngestionError(str(exc)) from exc

    if limit < 1:
        raise IngestionError("limit must be greater than zero.")

    normalized_providers = _normalize_providers(providers)
    serpapi_key = os.getenv("SERPAPI_API_KEY")
    adzuna_app_id = os.getenv("ADZUNA_APP_ID")
    adzuna_app_key = os.getenv("ADZUNA_APP_KEY")
    if "serpapi" in normalized_providers and not serpapi_key:
        raise IngestionError("Missing SERPAPI_API_KEY in environment.")
    if "adzuna" in normalized_providers and (not adzuna_app_id or not adzuna_app_key):
        raise IngestionError("Missing ADZUNA_APP_ID or ADZUNA_APP_KEY in environment.")

    postings: list[JobPosting] = []
    seen_keys: set[str] = set()
    query_errors: list[str] = []
    serpapi_searches_used = 0
    adzuna_searches_used = 0
    states = [
        QueryState(provider=provider, role=role, location=location)
        for provider in normalized_providers
        for role in normalized_roles
        for location in normalized_locations
    ]

    logger.info(
        "Starting job fetch providers=%s roles=%s locations=%s limit=%s query_pairs=%s",
        normalized_providers,
        normalized_roles,
        normalized_locations,
        limit,
        len(states),
    )

    while len(postings) < limit and any(state.buffer or not state.exhausted for state in states):
        added_this_round = 0
        for state in states:
            if len(postings) >= limit or (state.exhausted and not state.buffer):
                continue

            if not state.buffer:
                try:
                    _fill_query_buffer(
                        state=state,
                        serpapi_key=serpapi_key or "",
                        adzuna_app_id=adzuna_app_id or "",
                        adzuna_app_key=adzuna_app_key or "",
                    )
                    if state.provider == "serpapi":
                        serpapi_searches_used += 1
                    if state.provider == "adzuna":
                        adzuna_searches_used += 1
                except IngestionError as exc:
                    state.exhausted = True
                    message = f"{state.provider} {state.role} in {state.location}: {exc}"
                    query_errors.append(message)
                    logger.warning("Skipping failed search query: %s", message)
                    continue

            added_posting = _drain_one_buffered_posting(
                state=state,
                postings=postings,
                seen_keys=seen_keys,
                limit=limit,
            )

            if added_posting:
                added_this_round += 1
                logger.info(
                    "Added posting provider=%r role=%r location=%r total=%s buffer_remaining=%s",
                    state.provider,
                    state.role,
                    state.location,
                    len(postings),
                    len(state.buffer),
                )

            # Keep provider calls polite when paging through multiple query pairs.
            if not state.buffer and not state.exhausted:
                time.sleep(0.15)

        if added_this_round == 0 and all(state.exhausted for state in states):
            break

    if not postings:
        if query_errors:
            raise IngestionError(
                "No usable jobs were returned. Query errors: "
                + " | ".join(query_errors[:5])
            )
        raise IngestionError(
            "No job postings with non-empty descriptions were returned for the "
            "requested roles and locations."
        )

    if query_errors:
        logger.warning("Completed with partial query errors: %s", query_errors[:5])

    logger.info(
        "Completed job fetch usable_jobs=%s serpapi_searches_used=%s adzuna_searches_used=%s",
        len(postings),
        serpapi_searches_used,
        adzuna_searches_used,
    )
    return LiveJobsResult(
        jobs=[_posting_to_public_dict(posting) for posting in postings],
        stats=FetchStats(
            serpapi_searches_used=serpapi_searches_used,
            adzuna_searches_used=adzuna_searches_used,
            query_errors=query_errors,
        ),
    )


def iter_live_job_postings(
    *,
    roles: list[str],
    locations: list[str],
    limit: int = 10,
    providers: list[str] | None = None,
) -> list[JobPosting]:
    """Return validated JobPosting models for pipeline use."""

    raw_jobs = fetch_live_jobs(
        roles=roles,
        locations=locations,
        limit=limit,
        providers=providers,
    )
    return _validate_live_jobs(raw_jobs)


def iter_live_job_postings_with_stats(
    *,
    roles: list[str],
    locations: list[str],
    limit: int = 10,
    providers: list[str] | None = None,
) -> tuple[list[JobPosting], FetchStats]:
    """Return validated JobPosting models plus fetch stats for web UI."""

    result = fetch_live_jobs_with_stats(
        roles=roles,
        locations=locations,
        limit=limit,
        providers=providers,
    )
    return _validate_live_jobs(result.jobs), result.stats


def _validate_live_jobs(raw_jobs: list[dict]) -> list[JobPosting]:
    postings: list[JobPosting] = []
    for raw_job in raw_jobs:
        try:
            postings.append(JobPosting.model_validate(raw_job))
        except ValidationError as exc:
            raise IngestionError(f"Live job payload failed validation: {exc}") from exc
    return postings


def _fetch_google_jobs_page(
    *,
    api_key: str,
    role: str,
    location: str,
    next_page_token: str | None,
) -> dict[str, Any]:
    params = {
        "engine": "google_jobs",
        "q": role,
        "location": location,
        "hl": "en",
        "api_key": api_key,
    }
    if next_page_token:
        params["next_page_token"] = next_page_token

    try:
        response = requests.get(
            SERPAPI_SEARCH_URL,
            params=params,
            timeout=DEFAULT_TIMEOUT_SECONDS,
        )
    except requests.RequestException as exc:
        raise IngestionError(
            f"SerpApi request failed for {role!r} in {location!r}: {exc}"
        ) from exc

    if response.status_code == 429:
        raise IngestionError(
            "SerpApi rate limit reached. Wait for quota reset or reduce --limit."
        )
    if response.status_code in {401, 403}:
        raise IngestionError(
            "SerpApi rejected the request. Check SERPAPI_API_KEY and account access."
        )
    if response.status_code >= 400:
        raise IngestionError(
            f"SerpApi returned HTTP {response.status_code} for {role!r} in {location!r}."
        )

    try:
        payload = response.json()
    except ValueError as exc:
        raise IngestionError("SerpApi returned a non-JSON response.") from exc

    if payload.get("error"):
        raise IngestionError(f"SerpApi error: {payload['error']}")

    metadata = payload.get("search_metadata", {}) or {}
    if metadata.get("status") == "Error":
        raise IngestionError(
            f"SerpApi search failed: {metadata.get('error') or 'unknown provider error'}"
        )

    return payload


def _fill_query_buffer(
    *,
    state: QueryState,
    serpapi_key: str,
    adzuna_app_id: str,
    adzuna_app_key: str,
) -> None:
    if state.provider == "adzuna":
        page = int(state.next_page_token or "1")
        postings, has_more = _fetch_adzuna_jobs(
            app_id=adzuna_app_id,
            app_key=adzuna_app_key,
            role=state.role,
            location=state.location,
            page=page,
        )
        state.buffer.extend(
            (_dedupe_key({}, posting), posting)
            for posting in postings
        )
        state.next_page_token = str(page + 1) if has_more else None
        state.exhausted = not has_more
        logger.info(
            "Fetched Adzuna query role=%r location=%r page=%s buffered=%s has_more=%s",
            state.role,
            state.location,
            page,
            len(state.buffer),
            has_more,
        )
        return

    payload = _fetch_google_jobs_page(
        api_key=serpapi_key,
        role=state.role,
        location=state.location,
        next_page_token=state.next_page_token,
    )

    for result in payload.get("jobs_results", []):
        posting = _normalize_serpapi_job(result, location=state.location)
        if posting is None:
            continue
        state.buffer.append((_dedupe_key(result, posting), posting))

    state.next_page_token = (
        payload.get("serpapi_pagination", {}) or {}
    ).get("next_page_token")
    if not state.next_page_token and not state.buffer:
        state.exhausted = True

    logger.info(
        "Fetched query page role=%r location=%r buffered=%s has_next=%s",
        state.role,
        state.location,
        len(state.buffer),
        bool(state.next_page_token),
    )


def _drain_one_buffered_posting(
    *,
    state: QueryState,
    postings: list[JobPosting],
    seen_keys: set[str],
    limit: int,
) -> bool:
    while state.buffer and len(postings) < limit:
        dedupe_key, posting = state.buffer.pop(0)
        if dedupe_key in seen_keys:
            continue
        seen_keys.add(dedupe_key)
        postings.append(posting)
        if not state.buffer and not state.next_page_token:
            state.exhausted = True
        return True

    if not state.buffer and not state.next_page_token:
        state.exhausted = True
    return False


def _normalize_serpapi_job(
    result: dict[str, Any],
    *,
    location: str,
) -> JobPosting | None:
    description = _clean_text(result.get("description"))
    if not description:
        return None

    company_name = _clean_text(result.get("company_name")) or "Unknown"
    job_title = _clean_text(result.get("title")) or "Unknown Product Role"
    job_url = _extract_job_url(result)

    return JobPosting(
        company_name=company_name,
        job_title=job_title,
        job_description_text=description,
        job_url=job_url,
        country=_country_from_location(location),
    )


def _fetch_adzuna_jobs(
    *,
    app_id: str,
    app_key: str,
    role: str,
    location: str,
    page: int = 1,
) -> tuple[list[JobPosting], bool]:
    country_code = _adzuna_country_code(location)
    params = {
        "app_id": app_id,
        "app_key": app_key,
        "what": role,
        "where": location,
        "results_per_page": 10,
        "content-type": "application/json",
    }
    try:
        response = requests.get(
            ADZUNA_SEARCH_URL.format(country_code=country_code, page=page),
            params=params,
            timeout=DEFAULT_TIMEOUT_SECONDS,
        )
    except requests.RequestException as exc:
        raise IngestionError(f"Adzuna request failed: {exc}") from exc

    if response.status_code >= 400:
        raise IngestionError(f"Adzuna returned HTTP {response.status_code}: {response.text[:240]}")

    payload = response.json()
    postings: list[JobPosting] = []
    for result in payload.get("results", []):
        description = _clean_text(result.get("description"))
        if not description:
            continue
        company = result.get("company") or {}
        postings.append(
            JobPosting(
                company_name=_clean_text(company.get("display_name")) or "Unknown",
                job_title=_clean_text(result.get("title")) or "Unknown Product Role",
                job_description_text=description,
                job_url=_clean_text(result.get("redirect_url")) or "Unavailable",
                country=_country_from_location(location),
                source="adzuna",
            )
        )
    total_count = int(payload.get("count") or 0)
    has_more = bool(postings) and page * params["results_per_page"] < total_count
    return postings, has_more


def _extract_job_url(result: dict[str, Any]) -> str:
    apply_options = result.get("apply_options") or []
    for option in apply_options:
        link = option.get("link")
        if isinstance(link, str) and link.strip():
            return link.strip()

    for key in ("share_link", "via_link", "link"):
        value = result.get(key)
        if isinstance(value, str) and value.strip():
            return value.strip()

    job_id = result.get("job_id")
    if isinstance(job_id, str) and job_id.strip():
        return f"https://www.google.com/search?q={job_id.strip()}"

    return "Unavailable"


def _posting_to_public_dict(posting: JobPosting) -> dict[str, str]:
    return {
        "source": posting.source,
        "company_name": posting.company_name,
        "job_title": posting.job_title,
        "job_description_text": posting.job_description_text,
        "job_url": posting.job_url,
        "country": posting.country,
    }


def _dedupe_key(result: dict[str, Any], posting: JobPosting) -> str:
    job_id = result.get("job_id")
    if isinstance(job_id, str) and job_id.strip():
        return f"job_id:{job_id.strip()}"
    return (
        f"url:{posting.job_url}|title:{posting.job_title}|"
        f"company:{posting.company_name}"
    )


def _clean_text(value: Any) -> str:
    if not isinstance(value, str):
        return ""
    return " ".join(value.split())


def _country_from_location(location: str) -> str:
    parts = [part.strip() for part in location.split(",") if part.strip()]
    return parts[-1] if parts else location.strip()


def _normalize_providers(providers: list[str] | None) -> list[str]:
    normalized = []
    supported = {"serpapi", "adzuna"}
    for provider in providers or ["serpapi"]:
        value = provider.strip().casefold()
        if value not in supported:
            raise IngestionError(f"Unsupported job data provider: {provider}.")
        if value not in normalized:
            normalized.append(value)
    if not normalized:
        raise IngestionError("Select at least one job data provider.")
    return normalized


def _adzuna_country_code(location: str) -> str:
    normalized = _country_from_location(location).casefold()
    mapping = {
        "united states": "us",
        "us": "us",
        "usa": "us",
        "canada": "ca",
        "ca": "ca",
        "united kingdom": "gb",
        "uk": "gb",
        "gb": "gb",
        "germany": "de",
        "de": "de",
        "france": "fr",
        "fr": "fr",
        "spain": "es",
        "es": "es",
        "australia": "au",
        "au": "au",
        "netherlands": "nl",
        "nl": "nl",
    }
    return mapping.get(normalized, normalized[:2] or "us")
