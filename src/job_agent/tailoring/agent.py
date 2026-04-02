from __future__ import annotations

from job_agent.experience.models import ExperienceLake
from job_agent.rag.index import ExperienceRAGIndex
from job_agent.schemas.fill_plan import FillPlan, FieldAction
from job_agent.schemas.jobs import ApplicationPackage, JobPosting, MatchAssessment


class TailoringAgent:
    """Builds grounded resume + cover letter snippets from Experience Lake evidence."""

    def __init__(self, lake: ExperienceLake, rag_index: ExperienceRAGIndex) -> None:
        self.lake = lake
        self.rag_index = rag_index

    def build_application_package(
        self,
        job: JobPosting,
        assessment: MatchAssessment,
    ) -> ApplicationPackage:
        supporting_docs = self.rag_index.search(f"{job.title} {job.description}", top_k=4)
        bullets = [
            f"- {doc.page_content.splitlines()[0].replace('Title: ', '')}: {doc.page_content.splitlines()[2].replace('Summary: ', '')}"
            for doc in supporting_docs
            if len(doc.page_content.splitlines()) >= 3
        ]

        resume = self._resume_template(job=job, bullets=bullets, assessment=assessment)
        cover = self._cover_letter_template(job=job, bullets=bullets)
        fill_plan = self._build_fill_plan(job)

        return ApplicationPackage(
            job_id=job.id,
            resume_markdown=resume,
            cover_letter_markdown=cover,
            fill_plan=fill_plan.model_dump(),
        )

    def _resume_template(self, job: JobPosting, bullets: list[str], assessment: MatchAssessment) -> str:
        strengths = ", ".join(assessment.strengths_alignment[:8])
        base = [
            f"# Tailored Resume for {job.title}",
            "",
            f"Target Company: **{job.company}**",
            f"Strength Alignment: {strengths}",
            "",
            "## Relevant Experience",
            *bullets,
        ]
        return "\n".join(base)

    def _cover_letter_template(self, job: JobPosting, bullets: list[str]) -> str:
        highlights = "\n".join(bullets[:3])
        return (
            f"# Cover Letter\n\n"
            f"Dear Hiring Team at {job.company},\n\n"
            f"I am applying for the {job.title} role. My background aligns with your needs:\n"
            f"{highlights}\n\n"
            "All statements above are grounded in my Experience Lake and verifiable metrics."
        )

    def _build_fill_plan(self, job: JobPosting) -> FillPlan:
        first = self.lake.experiences[0]
        return FillPlan(
            job_url=job.apply_url,
            actions=[
                FieldAction(label="Full Name", value=self.lake.owner_name, confidence=1.0),
                FieldAction(label="Current Role", value=first.title, confidence=0.9, source_experience_id=first.id),
                FieldAction(label="Most Relevant Skills", value=", ".join(first.skills[:5]), confidence=0.85, source_experience_id=first.id),
            ],
            requires_human_review=False,
        )
