from __future__ import annotations

from job_agent.api.server import ApiContext, build_app
from job_agent.core.config import AgentConfig
from job_agent.discovery.engine import DiscoveryEngine

_config = AgentConfig()
_context = ApiContext(
    config=_config,
    discovery=DiscoveryEngine(
        app_id=_config.adzuna_app_id,
        app_key=_config.adzuna_app_key,
        country=_config.adzuna_country,
    ),
)

app = build_app(_context)
