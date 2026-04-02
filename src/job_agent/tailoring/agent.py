from __future__ import annotations

import json
from pathlib import Path

from fpdf import FPDF

from job_agent.experience.models import ExperienceLake
from job_agent.llm.client import LLMClient
from job_agent.rag.index import ExperienceRAGIndex
from job_agent.schemas.fill_plan import FillPlan, FieldAction
from job_agent.schemas.jobs import ApplicationPackage, JobPosting, MatchAssessment


class TailoringAgent:
    """Builds grounded resume + cover letter snippets from Experience Lake evidence."""

    def __init__(
        self,
        lake: ExperienceLake,
        rag_index: ExperienceRAGIndex,
        llm_client: LLMClient | None = None,
        output_dir: str = "output",
    ) -> None:
        self.lake = lake
        self.rag_index = rag_index
        self.llm_client = llm_client
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)

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

        if self.llm_client:
            resume, cover = self._llm_docs(job, assessment, bullets)
        else:
            resume = self._resume_template(job=job, bullets=bullets, assessment=assessment)
            cover = self._cover_letter_template(job=job, bullets=bullets)

        fill_plan = self._build_fill_plan(job)

        resume_pdf = self._to_pdf(filename=f"resume_{job.id}.pdf", title="Tailored Resume", content=resume)
        cover_pdf = self._to_pdf(filename=f"cover_{job.id}.pdf", title="Tailored Cover Letter", content=cover)

        payload = fill_plan.model_dump()
        payload["resume_pdf"] = str(resume_pdf)
        payload["cover_letter_pdf"] = str(cover_pdf)

        return ApplicationPackage(
            job_id=job.id,
            resume_markdown=resume,
            cover_letter_markdown=cover,
            fill_plan=payload,
        )

    def _llm_docs(self, job: JobPosting, assessment: MatchAssessment, bullets: list[str]) -> tuple[str, str]:
        context = {
            "job_title": job.title,
            "company": job.company,
            "job_description": job.description,
            "strengths": assessment.strengths_alignment,
            "gaps": assessment.critical_gaps,
            "grounded_bullets": bullets,
        }
        system_prompt = (
            "You are a resume writer. Use ONLY provided context. "
            "Return JSON with keys: resume_markdown and cover_letter_markdown."
        )
        user_prompt = json.dumps(context)
        raw = self.llm_client.invoke_json(system_prompt, user_prompt)
        parsed = json.loads(raw)
        return parsed["resume_markdown"], parsed["cover_letter_markdown"]

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
                FieldAction(
                    label="Most Relevant Skills",
                    value=", ".join(first.skills[:5]),
                    confidence=0.85,
                    source_experience_id=first.id,
                ),
            ],
            requires_human_review=False,
        )

    def _to_pdf(self, filename: str, title: str, content: str) -> Path:
        path = self.output_dir / filename
        pdf = FPDF()
        pdf.add_page()
        pdf.set_font("Arial", size=12)
        pdf.multi_cell(0, 8, title)
        pdf.ln(2)
        pdf.multi_cell(0, 6, content)
        pdf.output(str(path))
        return path
