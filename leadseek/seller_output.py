"""Output adapters for seller/merchant acquisition leads."""

from __future__ import annotations

import csv
import io
from pathlib import Path

from leadseek.seller_models import SellerLead


SELLER_CSV_HEADERS = [
    "source",
    "business_name",
    "business_type",
    "address",
    "phone",
    "state",
    "city",
    "rating",
    "reviews",
    "source_url",
    "miyagisanchez_shop_url",
    "pain_category",
    "pain_summary",
    "urgency",
    "suggested_outreach",
    "fit_score",
    "hubspot_deal_id",
    "processed_at",
]


class SellerOutputError(RuntimeError):
    """Raised when seller leads cannot be persisted."""


def save_seller_leads(leads: list[SellerLead], output_path: Path) -> None:
    """Append seller lead records to a CSV file, creating headers when needed."""
    if not leads:
        return

    output_path.parent.mkdir(parents=True, exist_ok=True)
    should_write_header = not output_path.exists() or output_path.stat().st_size == 0

    try:
        with output_path.open("a", newline="", encoding="utf-8") as csv_file:
            writer = csv.DictWriter(csv_file, fieldnames=SELLER_CSV_HEADERS)
            if should_write_header:
                writer.writeheader()
            for lead in leads:
                writer.writerow(_lead_to_csv_row(lead))
    except OSError as exc:
        raise SellerOutputError(f"Could not write CSV output {output_path}: {exc}") from exc


def _lead_to_csv_row(lead: SellerLead) -> dict[str, str]:
    data = lead.model_dump(mode="json")
    diag = data.pop("diagnosis") or {}
    row = {
        "source": data.get("source", ""),
        "business_name": data.get("business_name", ""),
        "business_type": data.get("business_type") or "",
        "address": data.get("address") or "",
        "phone": data.get("phone") or "",
        "state": data.get("state") or "",
        "city": data.get("city") or "",
        "rating": str(data.get("rating") or ""),
        "reviews": str(data.get("reviews") or ""),
        "source_url": data.get("source_url") or "",
        "miyagisanchez_shop_url": data.get("miyagisanchez_shop_url") or "",
        "pain_category": diag.get("pain_category", "") if diag else "",
        "pain_summary": diag.get("pain_summary", "") if diag else "",
        "urgency": str(diag.get("urgency", "")) if diag else "",
        "suggested_outreach": diag.get("suggested_outreach", "") if diag else "",
        "fit_score": str(diag.get("fit_score", "")) if diag else "",
        "hubspot_deal_id": data.get("hubspot_deal_id") or "",
        "processed_at": data.get("processed_at") or "",
    }
    return row


def seller_leads_to_csv_text(leads: list[SellerLead]) -> str:
    """Render seller leads to CSV text for web downloads."""
    csv_buffer = io.StringIO()
    writer = csv.DictWriter(csv_buffer, fieldnames=SELLER_CSV_HEADERS)
    writer.writeheader()
    for lead in leads:
        writer.writerow(_lead_to_csv_row(lead))
    return csv_buffer.getvalue()


def read_seller_leads_csv(output_path: Path, limit: int = 100) -> list[dict]:
    """Read the last N rows from the seller leads CSV."""
    if not output_path.exists():
        return []
    try:
        with output_path.open("r", newline="", encoding="utf-8") as csv_file:
            reader = csv.DictReader(csv_file)
            rows = list(reader)
        return rows[-limit:]
    except OSError:
        return []
