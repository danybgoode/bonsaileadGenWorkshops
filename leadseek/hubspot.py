"""Optional HubSpot CRM integration for seller leads."""

from __future__ import annotations

import logging
import os

import requests

from leadseek.seller_models import SellerLead

HUBSPOT_BASE = "https://api.hubapi.com"

logger = logging.getLogger(__name__)


def upsert_deal(lead: SellerLead) -> str | None:
    """Create a HubSpot deal for a seller lead. Returns deal_id or None if HUBSPOT_API_KEY not set."""
    api_key = os.getenv("HUBSPOT_API_KEY")
    if not api_key:
        return None

    deal_name = f"{lead.business_name} — miyagisanchez.com"

    description_parts = []
    if lead.diagnosis:
        description_parts.append(f"Pain: {lead.diagnosis.pain_summary}")
        description_parts.append(f"Suggested outreach: {lead.diagnosis.suggested_outreach}")
        description_parts.append(f"Fit score: {lead.diagnosis.fit_score}/100")
    if lead.city:
        description_parts.append(f"City: {lead.city}")
    if lead.business_type:
        description_parts.append(f"Type: {lead.business_type}")

    properties: dict[str, str] = {
        "dealname": deal_name,
        "dealstage": "appointmentscheduled",
        "pipeline": "default",
    }
    if description_parts:
        properties["description"] = "\n".join(description_parts)

    url = f"{HUBSPOT_BASE}/crm/v3/objects/deals"
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
    }
    payload = {"properties": properties}

    try:
        resp = requests.post(url, json=payload, headers=headers, timeout=15)
        resp.raise_for_status()
        data = resp.json()
        return str(data.get("id", ""))
    except Exception as exc:  # noqa: BLE001
        logger.warning("HubSpot deal creation failed for %r: %s", lead.business_name, exc)
        return None
