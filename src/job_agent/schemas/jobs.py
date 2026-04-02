from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime


@dataclass(slots=True)
class JobPosting:
    id: str
    title: str
    company: str
    location: str
    description: str
    apply_url: str
    source: str
    discovered_at: datetime = field(default_factory=datetime.utcnow)


@dataclass(slots=True)
class MatchAssessment:
    job_id: str
    score: int
    strengths_alignment: list[str]
    critical_gaps: list[str]
    rationale: str


@dataclass(slots=True)
class ApplicationPackage:
    job_id: str
    resume_markdown: str
    cover_letter_markdown: str
    fill_plan: dict
