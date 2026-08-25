from fastapi.testclient import TestClient

from job_agent.api.server import ApiContext, build_app
from job_agent.core.config import AgentConfig
from job_agent.discovery.engine import DiscoveryEngine
from job_agent.workflows.graph import build_job_agent_graph


def test_ingest_requires_configured_token():
    discovery = DiscoveryEngine()
    app = build_app(ApiContext(AgentConfig(extension_api_token="secret"), discovery))
    client = TestClient(app)

    assert client.post("/ingest/job-url", json={"url": "https://example.com/job"}).status_code == 401
    response = client.post(
        "/ingest/job-url",
        json={"url": "https://example.com/job"},
        headers={"X-API-Token": "secret"},
    )

    assert response.status_code == 200
    assert response.json()["status"] == "queued"


def test_queued_job_runs_through_workflow():
    discovery = DiscoveryEngine()
    discovery.queue_external_job_url("https://example.com/job")
    graph = build_job_agent_graph(
        discovery_engine=discovery,
        experience_lake_path="data/experience_lake.example.json",
    )

    result = graph.invoke({"query": "software engineer"})

    assert len(result["discovered_jobs"]) == 1
    assert result["discovered_jobs"][0].id.startswith("ext::")
    assert result["assessments"]
    assert result["tailored_packages"] == []