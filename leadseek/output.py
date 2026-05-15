"""Output adapters for diagnosed leads.

To replace CSV with Google Sheets, Airtable, or another sink, change only the
implementation of save_leads while keeping the LeadRecord contract intact.
"""

from __future__ import annotations

import csv
import io
from pathlib import Path

from leadseek.models import LeadRecord


CSV_HEADERS = [
    "source",
    "job_url",
    "job_description_text",
    "country",
    "company_name",
    "job_title",
    "core_illness",
    "workshop_pitch",
    "pitch_angle",
    "fit_score",
    "urgency_score",
    "alignment_pain_score",
    "financial_pain_score",
    "execution_pain_score",
    "evidence",
    "nuance_summary",
    "recommended_strategy",
    "processed_at_utc",
]

LEGACY_HEADER_MAP = {
    "target_company_name": "company_name",
    "workshop_hook": "workshop_pitch",
}


class OutputError(RuntimeError):
    """Raised when diagnosed leads cannot be persisted."""


def save_leads(records: list[LeadRecord], output_path: Path) -> None:
    """Append lead records to a CSV file, creating headers when needed."""

    if not records:
        return

    output_path.parent.mkdir(parents=True, exist_ok=True)
    should_write_header = not output_path.exists() or output_path.stat().st_size == 0

    try:
        if output_path.exists() and not should_write_header:
            _upgrade_header_if_needed(output_path)

        with output_path.open("a", newline="", encoding="utf-8") as csv_file:
            writer = csv.DictWriter(csv_file, fieldnames=CSV_HEADERS)
            if should_write_header:
                writer.writeheader()
            for record in records:
                writer.writerow(_record_to_csv_row(record))
    except OSError as exc:
        raise OutputError(f"Could not write CSV output {output_path}: {exc}") from exc


def _record_to_csv_row(record: LeadRecord) -> dict[str, str]:
    data = record.model_dump(mode="json")
    if isinstance(data.get("evidence"), list):
        data["evidence"] = " | ".join(str(item) for item in data["evidence"])
    return {header: str(data[header]) for header in CSV_HEADERS}


def records_to_csv_text(records: list[LeadRecord]) -> str:
    """Render lead records to CSV text for web downloads."""

    csv_buffer = io.StringIO()
    writer = csv.DictWriter(csv_buffer, fieldnames=CSV_HEADERS)
    writer.writeheader()
    for record in records:
        writer.writerow(_record_to_csv_row(record))
    return csv_buffer.getvalue()


def _upgrade_header_if_needed(output_path: Path) -> None:
    with output_path.open("r", newline="", encoding="utf-8") as csv_file:
        reader = csv.DictReader(csv_file)
        existing_headers = reader.fieldnames or []
        if existing_headers == CSV_HEADERS:
            return
        rows = list(reader)

    migrated_headers = [LEGACY_HEADER_MAP.get(header, header) for header in existing_headers]

    if any(header not in CSV_HEADERS for header in migrated_headers):
        raise OutputError(
            f"Existing CSV {output_path} has unsupported columns: "
            f"{', '.join(existing_headers)}. Use a new output file."
        )

    with output_path.open("w", newline="", encoding="utf-8") as csv_file:
        writer = csv.DictWriter(csv_file, fieldnames=CSV_HEADERS)
        writer.writeheader()
        for row in rows:
            migrated_row = {
                LEGACY_HEADER_MAP.get(header, header): value
                for header, value in row.items()
                if header is not None
            }
            writer.writerow(
                {header: migrated_row.get(header, "") for header in CSV_HEADERS}
            )
