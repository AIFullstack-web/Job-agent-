from __future__ import annotations

import sqlite3
from dataclasses import dataclass
from pathlib import Path

from job_agent.schemas.jobs import ApplicationPackage, JobPosting, MatchAssessment


@dataclass(slots=True)
class SQLiteStore:
    path: str

    def __post_init__(self) -> None:
        Path(self.path).parent.mkdir(parents=True, exist_ok=True)
        self._init_db()

    def _connect(self) -> sqlite3.Connection:
        return sqlite3.connect(self.path)

    def _init_db(self) -> None:
        with self._connect() as con:
            con.execute(
                """
                CREATE TABLE IF NOT EXISTS discovered_jobs (
                    job_id TEXT PRIMARY KEY,
                    title TEXT,
                    company TEXT,
                    apply_url TEXT UNIQUE,
                    source TEXT,
                    description TEXT
                )
                """
            )
            con.execute(
                """
                CREATE TABLE IF NOT EXISTS match_assessments (
                    job_id TEXT PRIMARY KEY,
                    score INTEGER,
                    strengths TEXT,
                    gaps TEXT,
                    rationale TEXT
                )
                """
            )
            con.execute(
                """
                CREATE TABLE IF NOT EXISTS submissions (
                    job_id TEXT PRIMARY KEY,
                    resume_markdown TEXT,
                    cover_letter_markdown TEXT,
                    fill_plan_json TEXT,
                    submitted INTEGER DEFAULT 0
                )
                """
            )

    def save_job(self, job: JobPosting) -> None:
        with self._connect() as con:
            con.execute(
                """
                INSERT OR IGNORE INTO discovered_jobs (job_id, title, company, apply_url, source, description)
                VALUES (?, ?, ?, ?, ?, ?)
                """,
                (job.id, job.title, job.company, job.apply_url, job.source, job.description),
            )

    def save_assessment(self, assessment: MatchAssessment) -> None:
        with self._connect() as con:
            con.execute(
                """
                INSERT OR REPLACE INTO match_assessments (job_id, score, strengths, gaps, rationale)
                VALUES (?, ?, ?, ?, ?)
                """,
                (
                    assessment.job_id,
                    assessment.score,
                    ",".join(assessment.strengths_alignment),
                    ",".join(assessment.critical_gaps),
                    assessment.rationale,
                ),
            )

    def save_package(self, package: ApplicationPackage) -> None:
        with self._connect() as con:
            con.execute(
                """
                INSERT OR REPLACE INTO submissions (job_id, resume_markdown, cover_letter_markdown, fill_plan_json, submitted)
                VALUES (?, ?, ?, ?, COALESCE((SELECT submitted FROM submissions WHERE job_id = ?), 0))
                """,
                (
                    package.job_id,
                    package.resume_markdown,
                    package.cover_letter_markdown,
                    str(package.fill_plan),
                    package.job_id,
                ),
            )

    def mark_submitted(self, job_id: str) -> None:
        with self._connect() as con:
            con.execute("UPDATE submissions SET submitted = 1 WHERE job_id = ?", (job_id,))
