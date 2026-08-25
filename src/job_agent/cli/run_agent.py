from __future__ import annotations

import json

from job_agent.core.config import AgentConfig
from job_agent.discovery.engine import DiscoveryEngine
from job_agent.workflows.graph import build_job_agent_graph


def run(query: str = "software engineer", config: AgentConfig | None = None) -> dict:
    config = config or AgentConfig()
    discovery = DiscoveryEngine(
        app_id=config.adzuna_app_id,
        app_key=config.adzuna_app_key,
        country=config.adzuna_country,
    )
    graph = build_job_agent_graph(
        discovery_engine=discovery,
        experience_lake_path=config.experience_lake_path,
        min_match_score=config.min_match_score,
    )
    return graph.invoke({"query": query})


def main() -> None:
    result = run()
    print(json.dumps(result, indent=2, default=str))


if __name__ == "__main__":
    main()
