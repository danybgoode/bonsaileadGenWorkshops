"""Data contracts for the seller/merchant acquisition pipeline."""

from __future__ import annotations

from enum import Enum

from pydantic import BaseModel, ConfigDict, Field


class SellerPain(str, Enum):
    SINGLE_CHANNEL_TRAP = "single_channel_trap"      # on ML/etc but no multi-channel
    OFFLINE_ONLY = "offline_only"                     # physical biz, no online presence
    FRAGMENTED_OPS = "fragmented_ops"                 # tools all over the place
    NO_ONLINE_PRESENCE = "no_online_presence"         # google maps only, no website


class SellerDiagnosis(BaseModel):
    model_config = ConfigDict(extra="forbid")
    pain_category: SellerPain
    pain_summary: str = Field(min_length=1, description="One sentence, what's their specific problem")
    urgency: int = Field(ge=1, le=5, description="1=low, 5=critical")
    suggested_outreach: str = Field(min_length=1, description="Personalized first line for outreach email")
    fit_score: int = Field(ge=0, le=100)


class SellerLead(BaseModel):
    # Business data
    business_name: str
    business_type: str | None = None
    address: str | None = None
    phone: str | None = None
    state: str | None = None
    city: str | None = None
    rating: float | None = None
    reviews: int | None = None
    source: str  # 'serpapi_google_local' | 'miyagisanchez_unclaimed'
    source_url: str | None = None

    # Diagnosis
    diagnosis: SellerDiagnosis | None = None

    # Output
    miyagisanchez_shop_url: str | None = None  # e.g. https://miyagisanchez.vercel.app/s/{slug}
    hubspot_deal_id: str | None = None
    processed_at: str | None = None
