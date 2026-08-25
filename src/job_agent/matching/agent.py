from __future__ import annotations

import re
from dataclasses import dataclass

from job_agent.experience.models import ExperienceLake

STOPWORDS = {
    "and",
    "the",
    "with",
    "for",
    "you",
    "are",
    "our",
    "this",
    "that",
    "will",
    "from",
    "your",
    "have",
    "has",
    "job",
    "role",
    "team",
    "into",
    "using",
    "must",
    "plus",
    "years",
    "experience",
}


@dataclass(slots=True)
class MatchResult:
    score: int
    strengths_alignment: list[str]
    critical_gaps: list[str]
    rationale: str


class MatcherAgent:
    """Grounded JD matcher using only known Experience Lake evidence."""

    def __init__(self, lake: ExperienceLake) -> None:
        self.lake = lake
        self._skill_inventory = self._build_skill_inventory()

    def score_job(self, job_description: str) -> MatchResult:
        required_terms = self._extract_required_terms(job_description)
        strengths = [term for term in required_terms if term in self._skill_inventory]
        gaps = [term for term in required_terms if term not in self._skill_inventory]

        coverage = len(strengths) / max(1, len(required_terms))
        score = self._coverage_to_score(coverage)

        rationale = (
            f"Matched {len(strengths)} out of {len(required_terms)} key terms "
            f"({coverage:.0%} coverage) from grounded profile evidence."
        )
        return MatchResult(
            score=score,
            strengths_alignment=sorted(strengths),
            critical_gaps=sorted(gaps),
            rationale=rationale,
        )

    def _build_skill_inventory(self) -> set[str]:
        inventory: set[str] = set()
        for exp in self.lake.experiences:
            inventory.update(self._normalize_token(skill) for skill in exp.skills)
            inventory.update(self._normalize_token(word) for word in exp.summary.split())
        return {item for item in inventory if item}

    def _extract_required_terms(self, jd: str) -> set[str]:
        tokens = [self._normalize_token(token) for token in re.split(r"\W+", jd.lower())]
        return {token for token in tokens if token and token not in STOPWORDS and len(token) > 2}

    @staticmethod
    def _normalize_token(text: str) -> str:
        return re.sub(r"[^a-z0-9+#.]", "", text.lower()).strip()

    @staticmethod
    def _coverage_to_score(coverage: float) -> int:
        if coverage >= 0.8:
            return 5
        if coverage >= 0.6:
            return 4
        if coverage >= 0.4:
            return 3
        if coverage >= 0.2:
            return 2
        return 1
