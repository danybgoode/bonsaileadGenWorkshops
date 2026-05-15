"""Google Sheets export adapter for diagnosed lead records."""

from __future__ import annotations

import base64
import binascii
import json
import os
from datetime import UTC, datetime
from typing import Any

import gspread
from google.oauth2.service_account import Credentials

from leadseek.output import CSV_HEADERS


SHEETS_SCOPES = [
    "https://www.googleapis.com/auth/spreadsheets",
    "https://www.googleapis.com/auth/drive",
]


class SheetsExportError(RuntimeError):
    """Raised when Google Sheets export cannot be completed."""


def export_rows_to_google_sheets(rows: list[dict[str, Any]]) -> str:
    """Create a new Google Sheet and write lead rows into it."""

    if not rows:
        raise SheetsExportError("No rows were provided for Google Sheets export.")

    credentials_info = _load_service_account_info()
    credentials = Credentials.from_service_account_info(
        credentials_info,
        scopes=SHEETS_SCOPES,
    )
    client = gspread.authorize(credentials)

    title = f"Leadseek Leads {datetime.now(UTC).strftime('%Y-%m-%d %H%M%S UTC')}"
    spreadsheet = client.create(title)
    worksheet = spreadsheet.sheet1
    sheet_rows = [
        CSV_HEADERS,
        *[
            [_stringify(row.get(header, "")) for header in CSV_HEADERS]
            for row in rows
        ],
    ]
    worksheet.update(sheet_rows)

    share_with = os.getenv("GOOGLE_SHEETS_SHARE_WITH")
    if share_with:
        spreadsheet.share(share_with, perm_type="user", role="writer")

    return spreadsheet.url


def _load_service_account_info() -> dict[str, Any]:
    raw_json = os.getenv("GOOGLE_SERVICE_ACCOUNT_JSON")
    raw_b64 = os.getenv("GOOGLE_SERVICE_ACCOUNT_JSON_B64")

    if raw_b64:
        try:
            raw_json = base64.b64decode(raw_b64, validate=True).decode("utf-8")
        except (binascii.Error, UnicodeDecodeError) as exc:
            raise SheetsExportError(
                "GOOGLE_SERVICE_ACCOUNT_JSON_B64 is not valid base64."
            ) from exc

    if not raw_json:
        raise SheetsExportError(
            "Missing Google Sheets credentials. Set GOOGLE_SERVICE_ACCOUNT_JSON "
            "or GOOGLE_SERVICE_ACCOUNT_JSON_B64."
        )

    try:
        loaded = json.loads(raw_json)
    except json.JSONDecodeError as exc:
        raise SheetsExportError("Google service account JSON is invalid.") from exc

    if not isinstance(loaded, dict):
        raise SheetsExportError("Google service account credentials must be a JSON object.")
    return loaded


def _stringify(value: Any) -> str:
    if value is None:
        return ""
    return str(value)
