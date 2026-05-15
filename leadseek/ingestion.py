"""Live job ingestion adapters.

The production adapter uses SerpApi's Google Jobs API instead of scraping job
boards directly. The rest of the pipeline depends only on normalized
JobPosting objects, so another provider can replace this module without
touching Gemini diagnosis or output persistence.
"""

from __future__ import annotations

import os
import time
from typing import Any

import requests
from pydantic import ValidationError

from leadseek.models import JobPosting


SERPAPI_SEARCH_URL = "https://serpapi.com/search.json"
DEFAULT_TIMEOUT_SECONDS = 30


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

    normalized_roles = _normalize_terms(roles, "roles")
    normalized_locations = _normalize_terms(locations, "locations")
    if limit < 1:
        raise IngestionError("limit must be greater than zero.")

    api_key = os.getenv("SERPAPI_API_KEY")
    if not api_key:
        raise IngestionError("Missing SERPAPI_API_KEY in environment.")

    postings: list[JobPosting] = []
    seen_keys: set[str] = set()

    for role in normalized_roles:
        for location in normalized_locations:
            next_page_token: str | None = None

            while len(postings) < limit:
                payload = _fetch_google_jobs_page(
                    api_key=api_key,
                    role=role,
                    location=location,
                    next_page_token=next_page_token,
                )

                for result in payload.get("jobs_results", []):
                    posting = _normalize_serpapi_job(result, location=location)
                    if posting is None:
                        continue

                    dedupe_key = _dedupe_key(result, posting)
                    if dedupe_key in seen_keys:
                        continue

                    seen_keys.add(dedupe_key)
                    postings.append(posting)
                    if len(postings) >= limit:
                        break

                if len(postings) >= limit:
                    break

                next_page_token = (
                    payload.get("serpapi_pagination", {}) or {}
                ).get("next_page_token")
                if not next_page_token:
                    break

                # Keep provider calls polite when paging through multiple query pairs.
                time.sleep(0.25)

    if not postings:
        raise IngestionError(
            "No job postings with non-empty descriptions were returned for the "
            "requested roles and locations."
        )

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


def _normalize_terms(values: list, label: str) -> list[str]:
    normalized = [str(value).strip() for value in values if str(value).strip()]
    if not normalized:
        raise IngestionError(f"At least one {label} value is required.")
    return normalized


def _clean_text(value: Any) -> str:
    if not isinstance(value, str):
        return ""
    return " ".join(value.split())


def _country_from_location(location: str) -> str:
    parts = [part.strip() for part in location.split(",") if part.strip()]
    return parts[-1] if parts else location.strip()
