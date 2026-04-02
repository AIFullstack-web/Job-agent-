from __future__ import annotations

import json

from job_agent.core.config import AgentConfig
from job_agent.discovery.engine import DiscoveryEngine
from job_agent.observability.logging import configure_logging
from job_agent.workflows.graph import build_job_agent_graph


def run(query: str = "software engineer") -> dict:
    configure_logging()
    config = AgentConfig()
    discovery = DiscoveryEngine(
        app_id=config.adzuna_app_id,
        app_key=config.adzuna_app_key,
        country=config.adzuna_country,
    )
    graph = build_job_agent_graph(discovery_engine=discovery, config=config)
    return graph.invoke({"query": query})


if __name__ == "__main__":
    result = run()
    print(json.dumps(result, indent=2, default=str))
