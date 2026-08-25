from __future__ import annotations

from dataclasses import dataclass

from fastapi import FastAPI, Header, HTTPException
from pydantic import BaseModel, HttpUrl

from job_agent.core.config import AgentConfig
from job_agent.discovery.engine import DiscoveryEngine


class JobUrlPayload(BaseModel):
    url: HttpUrl


@dataclass(slots=True)
class ApiContext:
    config: AgentConfig
    discovery: DiscoveryEngine


def create_default_app() -> FastAPI:
    config = AgentConfig()
    discovery = DiscoveryEngine(
        app_id=config.adzuna_app_id,
        app_key=config.adzuna_app_key,
        country=config.adzuna_country,
    )
    return build_app(ApiContext(config=config, discovery=discovery))


def main() -> None:
    import uvicorn

    uvicorn.run("job_agent.api.server:app", host="127.0.0.1", port=8000)


def build_app(context: ApiContext) -> FastAPI:
    app = FastAPI(title="Autonomous Job Agent API", version="0.1.0")

    @app.get("/health")
    def health() -> dict[str, str]:
        return {"status": "ok"}

    @app.post("/ingest/job-url")
    def ingest_job_url(payload: JobUrlPayload, x_api_token: str = Header(default="")) -> dict[str, str]:
        if not context.config.extension_api_token or x_api_token != context.config.extension_api_token:
            raise HTTPException(status_code=401, detail="Unauthorized")
        context.discovery.queue_external_job_url(str(payload.url))
        return {"status": "queued", "url": str(payload.url)}

    return app


app = create_default_app()
