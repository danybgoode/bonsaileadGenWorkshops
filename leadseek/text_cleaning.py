"""Text preparation helpers for LLM diagnosis."""

from __future__ import annotations

import re


MAX_GEMINI_DESCRIPTION_CHARS = 12_000

_NOISE_PATTERNS = [
    re.compile(r"^apply now$", re.IGNORECASE),
    re.compile(r"^share this job$", re.IGNORECASE),
    re.compile(r"^save job$", re.IGNORECASE),
    re.compile(r"^posted\s+\d+.*$", re.IGNORECASE),
    re.compile(r"^job id[:\s].*$", re.IGNORECASE),
    re.compile(r"^ref(?:erence)?[:\s].*$", re.IGNORECASE),
    re.compile(r"^cookie(s)?\s+.*$", re.IGNORECASE),
    re.compile(r"^privacy policy$", re.IGNORECASE),
    re.compile(r"^terms of use$", re.IGNORECASE),
    re.compile(r"^equal opportunity employer$", re.IGNORECASE),
]

_URL_RE = re.compile(r"https?://\S+|www\.\S+", re.IGNORECASE)
_EMAIL_RE = re.compile(r"\b\S+@\S+\.\S+\b")
_CONTROL_RE = re.compile(r"[\x00-\x08\x0b\x0c\x0e-\x1f\x7f]")
_REPEATED_SYMBOL_RE = re.compile(r"([^\w\s])\1{2,}")
_WHITESPACE_RE = re.compile(r"[ \t]+")
_BLANK_LINES_RE = re.compile(r"\n{3,}")


def prepare_job_description_for_gemini(text: str) -> str:
    """Clean fetched JD text enough for diagnosis while preserving content.

    SerpApi's Google Jobs `description` field is already plain job-description
    text in normal cases. This function is deliberately conservative: it strips
    obvious transport/UI noise, normalizes whitespace, and bounds token spend.
    """

    text = _CONTROL_RE.sub(" ", text)
    text = _URL_RE.sub(" ", text)
    text = _EMAIL_RE.sub(" ", text)
    text = _REPEATED_SYMBOL_RE.sub(r"\1\1", text)

    cleaned_lines: list[str] = []
    seen_lines: set[str] = set()

    for raw_line in text.splitlines():
        line = _WHITESPACE_RE.sub(" ", raw_line).strip()
        if not line:
            cleaned_lines.append("")
            continue
        if any(pattern.match(line) for pattern in _NOISE_PATTERNS):
            continue

        normalized = line.casefold()
        if normalized in seen_lines and len(line) < 120:
            continue
        seen_lines.add(normalized)
        cleaned_lines.append(line)

    cleaned = "\n".join(cleaned_lines)
    cleaned = _BLANK_LINES_RE.sub("\n\n", cleaned).strip()
    return cleaned[:MAX_GEMINI_DESCRIPTION_CHARS].strip()
