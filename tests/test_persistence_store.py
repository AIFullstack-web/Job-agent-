from job_agent.persistence.store import SQLiteStore
from job_agent.schemas.jobs import ApplicationPackage, JobPosting, MatchAssessment


def test_sqlite_store_roundtrip(tmp_path):
    db = tmp_path / "agent.db"
    store = SQLiteStore(str(db))

    job = JobPosting(
        id="j1",
        title="Engineer",
        company="Acme",
        location="Remote",
        description="Python role",
        apply_url="https://example.com/apply",
        source="test",
    )
    assessment = MatchAssessment(
        job_id="j1",
        score=4,
        strengths_alignment=["python"],
        critical_gaps=["kubernetes"],
        rationale="good fit",
    )
    package = ApplicationPackage(
        job_id="j1",
        resume_markdown="# Resume",
        cover_letter_markdown="# Cover",
        fill_plan={"job_url": "https://example.com/apply", "actions": []},
    )

    store.save_job(job)
    store.save_assessment(assessment)
    store.save_package(package)
    store.mark_submitted("j1")

    assert db.exists()
