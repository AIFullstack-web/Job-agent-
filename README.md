# Autonomous Job Agent

A self-hosted Python agent for job discovery, matching, tailoring, and semi-autonomous application submission.

## Features completed

- **Experience Lake**: local JSON profile source of truth + retrieval-ready document conversion.
- **RAG layer**: local TF-IDF style index to ground resume and cover-letter generation.
- **Discovery engine**:
  - Poll Adzuna API for jobs.
  - Accept LinkedIn/other URLs from a Chrome extension through FastAPI ingestion endpoint.
- **Matcher**: computes a 1-5 match score, strengths alignment, and critical gaps.
- **Tailoring agent**: creates grounded resume and cover letter snippets + structured fill plan.
- **Workflow orchestration**: LangGraph pipeline with Discovery -> Scoring -> Tailoring -> Submission nodes.
- **Stealth execution module**: SeleniumBase UC mode, CDP bridge for browser-use, human-like typing delays and captcha click hook.

## Directory structure

```text
src/job_agent/
  api/           # FastAPI endpoint for extension URL ingestion
  cli/           # Run entrypoint
  core/          # Config and shared primitives
  discovery/     # Job discovery providers and queueing
  experience/    # Experience Lake models and loader
  matching/      # Match scoring logic
  rag/           # Grounding retrieval index
  schemas/       # Fill plan and job/app schemas
  submission/    # Stealth browser execution
  tailoring/     # Resume/cover generation from grounded context
  workflows/     # LangGraph orchestration
```

## Quick start

```bash
python -m venv .venv
source .venv/bin/activate
pip install -e .[dev]
pytest
python -m job_agent.cli.run_agent
```

## FastAPI endpoint for Chrome extension URL push

```python
from job_agent.api.server import ApiContext, build_app
from job_agent.core.config import AgentConfig
from job_agent.discovery.engine import DiscoveryEngine

config = AgentConfig()
ctx = ApiContext(config=config, discovery=DiscoveryEngine())
app = build_app(ctx)
```

Use header `X-API-Token: <EXTENSION_API_TOKEN>` and `POST /ingest/job-url` with `{"url": "https://..."}`.
