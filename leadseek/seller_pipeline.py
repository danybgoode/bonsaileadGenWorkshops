"""Pipeline orchestration for merchant acquisition leads."""

from __future__ import annotations

import logging
import os
from datetime import UTC, datetime
from pathlib import Path

from leadseek.config import AppConfig
from leadseek.seller_diagnostics import GeminiSellerDiagnostician, SellerDiagnosisError
from leadseek.seller_ingestion import fetch_serpapi_local, fetch_unclaimed_shops
from leadseek.seller_models import SellerLead
from leadseek.seller_output import save_seller_leads

logger = logging.getLogger(__name__)

SELLER_LEADS_CSV = Path(__file__).parent.parent / "seller_leads.csv"


def process_seller_leads(
    *,
    source: str,           # 'serpapi' | 'unclaimed'
    query: str = "",       # for serpapi source
    location: str = "",    # for serpapi source
    state: str = "",       # for serpapi source
    limit: int = 20,
    enrich: bool = True,   # whether to call Gemini
    push_hubspot: bool = False,  # whether to create HubSpot deals
    config: AppConfig,
) -> list[SellerLead]:
    """
    1. Fetch leads from the appropriate adapter.
    2. If enrich=True, call Gemini for each (graceful: failed diagnosis = lead still saved with diagnosis=None).
    3. Set miyagisanchez_shop_url from source data.
    4. If push_hubspot=True, create HubSpot deals.
    5. Save to seller_leads.csv (append).
    6. Return all SellerLead records.
    """
    # Ensure env keys are set
    if config.serpapi_api_key:
        os.environ.setdefault("SERPAPI_API_KEY", config.serpapi_api_key)

    # 1. Fetch raw data
    raw_leads: list[SellerLead] = []

    if source == "serpapi":
        logger.info("Fetching seller leads via SerpAPI query=%r location=%r limit=%s", query, location, limit)
        raw_results = fetch_serpapi_local(query=query, location=location, limit=limit)
        for item in raw_results:
            lead = _serpapi_result_to_lead(item, state=state)
            raw_leads.append(lead)

    elif source == "unclaimed":
        logger.info("Fetching unclaimed miyagisanchez shops limit=%s", limit)
        raw_results = fetch_unclaimed_shops(limit=limit)
        miyagisanchez_url = os.getenv("MIYAGISANCHEZ_URL", "https://miyagisanchez.vercel.app")
        for item in raw_results:
            lead = _unclaimed_shop_to_lead(item, base_url=miyagisanchez_url)
            raw_leads.append(lead)

    else:
        raise ValueError(f"Unknown source: {source!r}. Use 'serpapi' or 'unclaimed'.")

    logger.info("Fetched %s raw leads", len(raw_leads))

    # 2. Enrich with Gemini
    leads: list[SellerLead] = []
    if enrich and raw_leads:
        with GeminiSellerDiagnostician(
            api_key=config.gemini_api_key,
            model=config.gemini_model,
        ) as diagnostician:
            for lead in raw_leads:
                try:
                    diagnosis = diagnostician.diagnose(
                        business_name=lead.business_name,
                        business_type=lead.business_type,
                        city=lead.city,
                        rating=lead.rating,
                        reviews=lead.reviews,
                    )
                    lead = lead.model_copy(update={"diagnosis": diagnosis})
                    logger.info("Diagnosed %r: %s (fit=%s)", lead.business_name, diagnosis.pain_category, diagnosis.fit_score)
                except SellerDiagnosisError as exc:
                    logger.warning("Diagnosis failed for %r: %s", lead.business_name, exc)
                    # Keep lead with diagnosis=None
                leads.append(lead)
    else:
        leads = raw_leads

    # 3. Push to HubSpot if requested
    if push_hubspot:
        from leadseek.hubspot import upsert_deal  # noqa: PLC0415
        enriched_leads: list[SellerLead] = []
        for lead in leads:
            deal_id = upsert_deal(lead)
            if deal_id:
                lead = lead.model_copy(update={"hubspot_deal_id": deal_id})
                logger.info("HubSpot deal created for %r: %s", lead.business_name, deal_id)
            enriched_leads.append(lead)
        leads = enriched_leads

    # 4. Stamp processed_at
    now = datetime.now(UTC).isoformat()
    leads = [lead.model_copy(update={"processed_at": now}) for lead in leads]

    # 5. Save to CSV
    save_seller_leads(leads, SELLER_LEADS_CSV)
    logger.info("Saved %s seller leads to %s", len(leads), SELLER_LEADS_CSV)

    return leads


def _serpapi_result_to_lead(item: dict, state: str = "") -> SellerLead:
    """Convert a SerpAPI google_local result dict to a SellerLead."""
    gps = item.get("gps_coordinates") or {}
    address = item.get("address", "")

    # Try to extract city from address (last meaningful part before state/postal)
    city: str | None = None
    if address:
        parts = [p.strip() for p in address.split(",")]
        if len(parts) >= 2:
            city = parts[-2] if len(parts) > 1 else parts[0]

    return SellerLead(
        business_name=item.get("title", "Unknown"),
        business_type=item.get("type"),
        address=address or None,
        phone=item.get("phone"),
        state=state or None,
        city=city,
        rating=item.get("rating"),
        reviews=item.get("reviews"),
        source="serpapi_google_local",
        source_url=item.get("links", {}).get("website") or item.get("place_id_search"),
        miyagisanchez_shop_url=None,  # not on miyagisanchez yet
    )


def _unclaimed_shop_to_lead(item: dict, base_url: str) -> SellerLead:
    """Convert a miyagisanchez unclaimed shop dict to a SellerLead."""
    slug = item.get("slug", "")
    shop_url = f"{base_url}/s/{slug}" if slug else None

    location = item.get("location") or ""
    city: str | None = None
    if location:
        parts = [p.strip() for p in location.split(",")]
        city = parts[0] if parts else None

    return SellerLead(
        business_name=item.get("name", "Unknown"),
        business_type=None,
        address=location or None,
        phone=None,
        state=None,
        city=city,
        rating=None,
        reviews=None,
        source="miyagisanchez_unclaimed",
        source_url=item.get("source_url"),
        miyagisanchez_shop_url=shop_url,
    )
