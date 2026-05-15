"""Application configuration and environment loading."""

from __future__ import annotations

import os
from dataclasses import dataclass


DEFAULT_MODEL = "gemini-2.5-flash"


class ConfigError(RuntimeError):
    """Raised when required runtime configuration is missing."""


@dataclass(frozen=True)
class AppConfig:
    """Runtime settings for the lead generation pipeline."""

    gemini_api_key: str
    serpapi_api_key: str
    gemini_model: str = DEFAULT_MODEL

    @classmethod
    def from_env(
        cls,
        model_override: str | None = None,
        *,
        require_gemini: bool = True,
        require_serpapi: bool = True,
    ) -> "AppConfig":
        gemini_api_key = os.getenv("GEMINI_API_KEY") or os.getenv("GOOGLE_API_KEY")
        if require_gemini and not gemini_api_key:
            raise ConfigError(
                "Missing GEMINI_API_KEY. Create a Gemini API key in Google AI Studio, "
                "then add it to .env or your shell environment."
            )

        serpapi_api_key = os.getenv("SERPAPI_API_KEY")
        if require_serpapi and not serpapi_api_key:
            raise ConfigError(
                "Missing SERPAPI_API_KEY. Create a SerpApi API key, then add it to "
                ".env or your shell environment."
            )

        return cls(
            gemini_api_key=gemini_api_key or "",
            serpapi_api_key=serpapi_api_key or "",
            gemini_model=model_override or os.getenv("GEMINI_MODEL") or DEFAULT_MODEL,
        )
