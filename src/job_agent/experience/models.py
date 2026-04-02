from __future__ import annotations

from dataclasses import dataclass, field
from typing import Literal


@dataclass(slots=True)
class ExperienceEntry:
    """Single grounded experience record from the Experience Lake."""

    id: str
    title: str
    company: str | None = None
    years: float | None = None
    summary: str = ""
    skills: list[str] = field(default_factory=list)
    evidence: list[str] = field(default_factory=list)
    category: Literal["work", "project", "education", "certification", "other"] = "work"


@dataclass(slots=True)
class ExperienceLake:
    """Container for all experiences used as the agent's ground-truth profile."""

    owner_name: str
    experiences: list[ExperienceEntry]
