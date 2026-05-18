"""Ingestion adapters for merchant acquisition leads.

SerpApiLocalAdapter — fetches local businesses via SerpAPI google_local engine.
SupabaseUnclaimedAdapter — reads unclaimed shops from miyagisanchez Supabase.
"""

from __future__ import annotations

import os

import requests

SERPAPI_URL = "https://serpapi.com/search.json"


def fetch_serpapi_local(query: str, location: str, limit: int = 20) -> list[dict]:
    """Fetch local businesses via SerpAPI google_local engine. Returns raw result dicts."""
    params = {
        "engine": "google_local",
        "q": query,
        "location": location,
        "hl": "es",
        "gl": "mx",
        "api_key": os.environ["SERPAPI_API_KEY"],
    }
    resp = requests.get(SERPAPI_URL, params=params, timeout=30)
    resp.raise_for_status()
    data = resp.json()
    if "error" in data:
        raise RuntimeError(f"SerpAPI error: {data['error']}")
    return (data.get("local_results") or [])[:limit]


def fetch_unclaimed_shops(limit: int = 50) -> list[dict]:
    """Fetch unclaimed shops from miyagisanchez Supabase DB (source='scraped', clerk_user_id IS NULL)."""
    url = f"{os.environ['SUPABASE_URL']}/rest/v1/marketplace_shops"
    headers = {
        "apikey": os.environ["SUPABASE_SERVICE_ROLE_KEY"],
        "Authorization": f"Bearer {os.environ['SUPABASE_SERVICE_ROLE_KEY']}",
    }
    params = {
        "select": "id,slug,name,location,source_url,source",
        "source": "eq.scraped",
        "clerk_user_id": "is.null",
        "limit": str(limit),
        "order": "created_at.desc",
    }
    resp = requests.get(url, headers=headers, params=params, timeout=30)
    resp.raise_for_status()
    return resp.json()
