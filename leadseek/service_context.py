"""Service context loading for LLM enrichment."""

from __future__ import annotations

import logging
import os
import time
from typing import Any

import requests


NOTION_VERSION = "2022-06-28"
NOTION_BLOCKS_URL = "https://api.notion.com/v1/blocks/{page_id}/children"
DEFAULT_SERVICE_CONTEXT = """
Services sold:
- North Star & Financial Outcomes Workshop: Aligns leadership around one North Star metric, its input metrics, and the financial outcomes product should optimize for. Best for feature factories, roadmap politics, unclear priorities, and product orgs seen as cost centers.
- Agentic Scrum & Automated Prototyping Workshop: Uses AI agents to automate scrum rituals, prototype flows, validation loops, data checks, and experiment execution. Best for bloated agile, slow delivery, large team coordination drag, and teams hijacked by process or technical throughput.
Operating stack:
- Claude Code / AI agents for execution automation.
- Notion for operating system documentation and strategy memory.
- Google Sheets for financial models, scoring, reporting, and prioritization.
- Scrum/Kanban boards wired to North Star and validation criteria.
""".strip()

_CACHE_TTL_SECONDS = 600
_cached_context: str | None = None
_cached_at = 0.0
logger = logging.getLogger(__name__)


class ServiceContextError(RuntimeError):
    """Raised when external service context cannot be loaded."""


def get_service_context() -> str:
    """Return service context from env/Notion, with a safe default fallback."""

    global _cached_context, _cached_at
    now = time.time()
    if _cached_context and now - _cached_at < _CACHE_TTL_SECONDS:
        return _cached_context

    inline_context = os.getenv("SERVICE_CONTEXT_TEXT")
    if inline_context and inline_context.strip():
        _cached_context = inline_context.strip()
        _cached_at = now
        logger.info("Loaded service context from SERVICE_CONTEXT_TEXT.")
        return _cached_context

    notion_token = os.getenv("NOTION_TOKEN")
    notion_page_id = os.getenv("NOTION_PAGE_ID")
    if notion_token and notion_page_id:
        try:
            _cached_context = _load_notion_page_text(notion_token, notion_page_id)
            _cached_at = now
            logger.info("Loaded service context from Notion page.")
            return _cached_context
        except ServiceContextError as exc:
            logger.warning("Could not load Notion service context: %s", exc)

    _cached_context = DEFAULT_SERVICE_CONTEXT
    _cached_at = now
    logger.info("Loaded default service context.")
    return _cached_context


def _load_notion_page_text(token: str, page_id: str) -> str:
    headers = {
        "Authorization": f"Bearer {token}",
        "Notion-Version": NOTION_VERSION,
    }
    chunks: list[str] = []
    cursor: str | None = None

    while True:
        params = {"page_size": "100"}
        if cursor:
            params["start_cursor"] = cursor

        try:
            response = requests.get(
                NOTION_BLOCKS_URL.format(page_id=page_id),
                headers=headers,
                params=params,
                timeout=20,
            )
        except requests.RequestException as exc:
            raise ServiceContextError(f"Notion request failed: {exc}") from exc

        if response.status_code >= 400:
            raise ServiceContextError(
                f"Notion returned HTTP {response.status_code}: {response.text[:300]}"
            )

        payload = response.json()
        for block in payload.get("results", []):
            text = _extract_block_text(block)
            if text:
                chunks.append(text)

        if not payload.get("has_more"):
            break
        cursor = payload.get("next_cursor")
        if not cursor:
            break

    text = "\n".join(chunks).strip()
    if not text:
        raise ServiceContextError("Notion page did not contain readable text blocks.")
    return text[:20_000]


def _extract_block_text(block: dict[str, Any]) -> str:
    block_type = block.get("type")
    if not isinstance(block_type, str):
        return ""
    content = block.get(block_type)
    if not isinstance(content, dict):
        return ""
    rich_text = content.get("rich_text") or []
    pieces = []
    for item in rich_text:
        plain_text = item.get("plain_text")
        if isinstance(plain_text, str):
            pieces.append(plain_text)
    return "".join(pieces).strip()
