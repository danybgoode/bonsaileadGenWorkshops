"""Validated data contracts shared across pipeline modules."""

from __future__ import annotations

from enum import Enum

from pydantic import BaseModel, ConfigDict, Field


class CoreIllness(str, Enum):
    """The only organizational illnesses the diagnosis may return."""

    FEATURE_FACTORY = "The Feature Factory (Cost Center)"
    BLOATED_AGILE = "Bloated Agile (Hijacked by Tech)"


class WorkshopPitch(str, Enum):
    """The only workshop pitches the LLM may select."""

    NORTH_STAR_FINANCIAL = "North Star & Financial Outcomes Workshop"
    AGENTIC_SCRUM = "Agentic Scrum & Automated Prototyping Workshop"


class LeadDiagnosis(BaseModel):
    """Strict JSON object expected from Gemini for each job description."""

    model_config = ConfigDict(extra="forbid")

    company_name: str = Field(
        min_length=1,
        description="The hiring company named in the job description.",
    )
    job_title: str = Field(
        min_length=1,
        description="The exact product-management job title from the job description.",
    )
    core_illness: CoreIllness = Field(
        description="The inferred organizational illness behind the job description.",
    )
    workshop_pitch: WorkshopPitch = Field(
        description="The consulting workshop pitch best matched to the illness.",
    )
    pitch_angle: str = Field(
        min_length=1,
        description="A one-sentence personalized outbound email hook.",
    )


class JobPosting(BaseModel):
    """A normalized live job posting from the ingestion layer."""

    company_name: str = Field(min_length=1)
    job_title: str = Field(min_length=1)
    job_description_text: str = Field(min_length=1)
    job_url: str = Field(min_length=1)
    country: str = Field(min_length=1)
    source: str = Field(default="serpapi_google_jobs")


class LeadRecord(BaseModel):
    """A diagnosis enriched with local pipeline metadata for persistence."""

    source: str
    job_url: str
    job_description_text: str
    country: str
    company_name: str
    job_title: str
    core_illness: CoreIllness
    workshop_pitch: WorkshopPitch
    pitch_angle: str
    processed_at_utc: str

    @classmethod
    def from_diagnosis(
        cls,
        *,
        posting: JobPosting,
        diagnosis: LeadDiagnosis,
        processed_at_utc: str,
    ) -> "LeadRecord":
        return cls(
            source=posting.source,
            job_url=posting.job_url,
            job_description_text=posting.job_description_text,
            country=posting.country,
            company_name=posting.company_name,
            job_title=posting.job_title,
            core_illness=diagnosis.core_illness,
            workshop_pitch=diagnosis.workshop_pitch,
            pitch_angle=diagnosis.pitch_angle,
            processed_at_utc=processed_at_utc,
        )
