from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from job_agent.experience.models import ExperienceEntry, ExperienceLake


@dataclass(slots=True)
class ExperienceDocument:
    page_content: str
    metadata: dict[str, Any]


class ExperienceLakeLoader:
    """Loads and normalizes a local JSON Experience Lake."""

    def __init__(self, path: str | Path) -> None:
        self.path = Path(path)

    def load(self) -> ExperienceLake:
        payload = json.loads(self.path.read_text(encoding="utf-8"))
        experiences = [ExperienceEntry(**item) for item in payload.get("experiences", [])]
        return ExperienceLake(owner_name=payload["owner_name"], experiences=experiences)

    def to_documents(self, lake: ExperienceLake) -> list[ExperienceDocument]:
        """Converts experiences into retrieval-ready documents."""
        documents: list[ExperienceDocument] = []
        for exp in lake.experiences:
            content = "\n".join(
                [
                    f"Title: {exp.title}",
                    f"Company: {exp.company or 'N/A'}",
                    f"Summary: {exp.summary}",
                    f"Skills: {', '.join(exp.skills)}",
                    f"Evidence: {' | '.join(exp.evidence)}",
                ]
            )
            documents.append(
                ExperienceDocument(
                    page_content=content,
                    metadata={
                        "experience_id": exp.id,
                        "category": exp.category,
                        "years": exp.years,
                    },
                )
            )
        return documents
