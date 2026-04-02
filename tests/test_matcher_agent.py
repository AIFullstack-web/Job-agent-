from job_agent.experience.loader import ExperienceLakeLoader
from job_agent.matching.agent import MatcherAgent


def test_matcher_returns_strengths_and_gaps():
    lake = ExperienceLakeLoader("data/experience_lake.example.json").load()
    matcher = MatcherAgent(lake)

    jd = "Looking for Python FastAPI engineer with Kubernetes and AWS experience."
    result = matcher.score_job(jd)

    assert result.score >= 3
    assert "python" in result.strengths_alignment
    assert "aws" in result.strengths_alignment
    assert "kubernetes" in result.critical_gaps
