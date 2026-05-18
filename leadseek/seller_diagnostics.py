"""Gemini-backed seller pain diagnosis for merchant acquisition."""

from __future__ import annotations

import json
from typing import Any

from google import genai
from google.genai import types
from pydantic import ValidationError

from leadseek.seller_models import SellerDiagnosis

SELLER_SYSTEM_PROMPT = """\
You are a merchant acquisition specialist for despachobonsai.com, a commerce platform for Mexican small businesses.

Our platform offers:
- Multi-channel selling: connect to MercadoLibre, Facebook Commerce, Amazon Mexico in one dashboard
- Point of Sale (POS) for physical stores
- Product catalog management with bulk import/export
- Financial dashboard with P&L by channel
- miyagisanchez.com: a marketplace where we feature our merchants' products

Target merchants: Small and medium Mexican businesses (restaurants, auto shops, real estate agencies, hardware stores, veterinaries, boutiques) that are either:
1. Offline-only (physical presence, Google Maps listing, but no e-commerce)
2. Single-channel (only on MercadoLibre or only Instagram, not diversified)
3. Fragmented (selling on multiple channels manually, lots of copy-paste)
4. Invisible online (no reviews, no website, just a Google Maps pin)

Given a business name, type, city, and any signals you can infer, diagnose:
- Which pain category fits best
- A specific one-sentence pain summary (what's THEIR problem today)
- Urgency (1-5): 1=nice to have, 5=they are losing money right now
- The first line of an outreach message that would resonate with THIS specific business
- A fit score 0-100 for how well despachobonsai solves their pain

Pain categories:
- single_channel_trap: business is on one platform, missing other channels, leaving money on the table
- offline_only: physical store or service with no online commerce channel
- fragmented_ops: manually managing inventory/orders across tools, lots of inefficiency
- no_online_presence: Google Maps listing but no website, no social, no reviews

Keep pitch angles specific to the business type (a dentist pitch differs from a car dealership pitch).
Return strict JSON matching the schema. No markdown.\
"""


class SellerDiagnosisError(RuntimeError):
    """Raised when the Gemini call or local validation fails."""


class GeminiSellerDiagnostician:
    """Thin adapter around the official Google Gen AI SDK for seller pain diagnosis."""

    def __init__(self, *, api_key: str, model: str) -> None:
        self._client = genai.Client(api_key=api_key)
        self._model = model

    def close(self) -> None:
        self._client.close()

    def __enter__(self) -> "GeminiSellerDiagnostician":
        return self

    def __exit__(self, exc_type: object, exc: object, tb: object) -> None:
        self.close()

    def diagnose(
        self,
        business_name: str,
        business_type: str | None,
        city: str | None,
        rating: float | None,
        reviews: int | None,
    ) -> SellerDiagnosis:
        """Call Gemini with business context, return structured SellerDiagnosis."""
        parts = [f"Business name: {business_name}"]
        if business_type:
            parts.append(f"Business type: {business_type}")
        if city:
            parts.append(f"City: {city}")
        if rating is not None:
            parts.append(f"Google rating: {rating}")
        if reviews is not None:
            parts.append(f"Number of reviews: {reviews}")

        user_prompt = "\n".join(parts)

        try:
            response = self._client.models.generate_content(
                model=self._model,
                contents=user_prompt,
                config=types.GenerateContentConfig(
                    system_instruction=SELLER_SYSTEM_PROMPT,
                    temperature=0.1,
                    response_mime_type="application/json",
                    response_json_schema=SellerDiagnosis.model_json_schema(),
                ),
            )
        except Exception as exc:  # noqa: BLE001
            raise SellerDiagnosisError(f"Gemini request failed: {exc}") from exc

        response_text = _response_text(response)
        try:
            return SellerDiagnosis.model_validate_json(response_text)
        except ValidationError as exc:
            raise SellerDiagnosisError(
                f"Gemini returned JSON that did not match the SellerDiagnosis schema: {exc}"
            ) from exc


def _response_text(response: Any) -> str:
    """Extract JSON text from a Gemini response with a clear failure mode."""
    text = getattr(response, "text", None)
    if isinstance(text, str) and text.strip():
        return text.strip()

    parsed = getattr(response, "parsed", None)
    if parsed is not None:
        return json.dumps(parsed)

    raise SellerDiagnosisError("Gemini response did not include text or parsed JSON.")
