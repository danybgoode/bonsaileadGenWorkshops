"""Search option presets and validation helpers."""

from __future__ import annotations


ROLE_PRESETS = [
    "VP Product",
    "Head of Product",
    "Chief Product Officer",
    "Director of Product",
    "Group Product Manager",
    "Product Operations Lead",
]

LOCATION_PRESETS = [
    "United States",
    "Canada",
    "Mexico",
    "United Kingdom",
    "Germany",
    "Spain",
]

MAX_ROLES = 5
MAX_LOCATIONS = 6
MAX_LIMIT = 50


def normalize_search_terms(values: list[str], *, label: str, max_items: int) -> list[str]:
    """Trim, dedupe, and cap user-provided search terms."""

    normalized: list[str] = []
    seen: set[str] = set()
    for value in values:
        term = " ".join(str(value).split())
        if not term:
            continue
        key = term.casefold()
        if key in seen:
            continue
        seen.add(key)
        normalized.append(term)

    if not normalized:
        raise ValueError(f"At least one {label} is required.")
    if len(normalized) > max_items:
        raise ValueError(f"Use at most {max_items} {label} per run.")
    return normalized
