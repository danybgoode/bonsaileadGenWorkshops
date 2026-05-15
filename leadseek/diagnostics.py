"""Gemini-backed signal extraction for organizational lead diagnosis."""

from __future__ import annotations

import json
from typing import Any

from google import genai
from google.genai import types
from pydantic import ValidationError

from leadseek.models import LeadDiagnosis
from leadseek.prompts import SYSTEM_PROMPT, build_user_prompt


class DiagnosisError(RuntimeError):
    """Raised when the LLM call or local validation fails."""


class GeminiDiagnostician:
    """Thin adapter around the official Google Gen AI SDK."""

    def __init__(self, *, api_key: str, model: str) -> None:
        self._client = genai.Client(api_key=api_key)
        self._model = model

    def close(self) -> None:
        self._client.close()

    def __enter__(self) -> "GeminiDiagnostician":
        return self

    def __exit__(self, exc_type: object, exc: object, tb: object) -> None:
        self.close()

    def diagnose(
        self,
        job_description: str,
        *,
        service_context: str | None = None,
    ) -> LeadDiagnosis:
        """Ask Gemini for a strict JSON diagnosis and validate it locally."""

        try:
            response = self._client.models.generate_content(
                model=self._model,
                contents=build_user_prompt(job_description, service_context),
                config=types.GenerateContentConfig(
                    system_instruction=SYSTEM_PROMPT,
                    temperature=0.1,
                    response_mime_type="application/json",
                    response_json_schema=LeadDiagnosis.model_json_schema(),
                ),
            )
        except Exception as exc:  # noqa: BLE001 - SDK exceptions vary by version.
            raise DiagnosisError(f"Gemini request failed: {exc}") from exc

        response_text = _response_text(response)
        try:
            return LeadDiagnosis.model_validate_json(response_text)
        except ValidationError as exc:
            raise DiagnosisError(
                f"Gemini returned JSON that did not match the LeadDiagnosis schema: {exc}"
            ) from exc


def _response_text(response: Any) -> str:
    """Extract JSON text from a Gemini response with a clear failure mode."""

    text = getattr(response, "text", None)
    if isinstance(text, str) and text.strip():
        return text.strip()

    # Some SDK versions expose parsed content directly when structured output is
    # configured. Normalize that back to JSON for one validation path.
    parsed = getattr(response, "parsed", None)
    if parsed is not None:
        return json.dumps(parsed)

    raise DiagnosisError("Gemini response did not include text or parsed JSON.")
