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
DEFAULT_TIMEOUT_SECONDS = 30
logger = logging.getLogger(__name__)


@dataclass
class QueryState:
    role: str
    location: str
    next_page_token: str | None = None
    exhausted: bool = False
    buffer: list[tuple[str, JobPosting]] = field(default_factory=list)


class IngestionError(RuntimeError):
    """Raised when live job postings cannot be loaded from the API provider."""


def fetch_live_jobs(roles: list, locations: list, limit: int = 10) -> list[dict]:
    """Fetch live job postings from SerpApi Google Jobs.

    Args:
        roles: Target role queries, for example ["VP Product", "Head of Product"].
        locations: Target locations, for example ["US", "Canada", "Mexico"].
        limit: Maximum number of normalized postings to return across all queries.

    Returns:
        A list of dictionaries with company_name, job_title,
        job_description_text, and job_url keys.

    Raises:
        IngestionError: Missing API key, rate limit, HTTP/API failure, bad input,
        or no usable job descriptions found.
    """

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

    api_key = os.getenv("SERPAPI_API_KEY")
    if not api_key:
        raise IngestionError("Missing SERPAPI_API_KEY in environment.")

    postings: list[JobPosting] = []
    seen_keys: set[str] = set()
    query_errors: list[str] = []
    states = [
        QueryState(role=role, location=location)
        for role in normalized_roles
        for location in normalized_locations
    ]

    logger.info(
        "Starting SerpApi Google Jobs fetch roles=%s locations=%s limit=%s query_pairs=%s",
        normalized_roles,
        normalized_locations,
        limit,
        len(states),
    )

    while len(postings) < limit and any(not state.exhausted for state in states):
        added_this_round = 0
        for state in states:
            if state.exhausted or len(postings) >= limit:
                continue

            if not state.buffer:
                try:
                    _fill_query_buffer(
                        state=state,
                        api_key=api_key,
                    )
                except IngestionError as exc:
                    state.exhausted = True
                    message = f"{state.role} in {state.location}: {exc}"
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
                    "Added posting role=%r location=%r total=%s buffer_remaining=%s",
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

    logger.info("Completed SerpApi fetch usable_jobs=%s", len(postings))
    return [_posting_to_public_dict(posting) for posting in postings]


def iter_live_job_postings(
    *,
    roles: list[str],
    locations: list[str],
    limit: int = 10,
) -> list[JobPosting]:
    """Return validated JobPosting models for pipeline use."""

    raw_jobs = fetch_live_jobs(roles=roles, locations=locations, limit=limit)
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


def _fill_query_buffer(*, state: QueryState, api_key: str) -> None:
    payload = _fetch_google_jobs_page(
        api_key=api_key,
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
