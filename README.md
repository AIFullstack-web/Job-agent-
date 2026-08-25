# Personal Job Agent

A self-hosted Python agent for personal job discovery, matching, tailoring, and human-reviewed application submission.

The Experience Lake is the source of truth. Copy the example profile to a private file, replace the sample data, and keep that file out of version control.

## Features

- **Experience Lake**: local JSON profile source of truth + retrieval-ready document conversion.
- **RAG layer**: local TF-IDF style index to ground resume and cover-letter generation.
- **Discovery engine**:
  - Poll Adzuna API for jobs.
  - Accept LinkedIn/other URLs from a Chrome extension through FastAPI ingestion endpoint.
- **Matcher**: computes a 1-5 match score, strengths alignment, and critical gaps.
- **Tailoring agent**: creates grounded resume and cover letter snippets + structured fill plan.
- **Workflow orchestration**: LangGraph pipeline with Discovery -> Scoring -> Tailoring -> Submission nodes.
- **Browser execution module**: optional SeleniumBase UC mode, CDP bridge for browser-use, human-like typing delays and captcha click hook. Review generated fill plans before enabling browser submission.

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
python -m pip install -e ".[dev]"
pytest
job-agent
```

For browser automation, install `python -m pip install -e ".[browser]"`. LLM packages are available with `python -m pip install -e ".[llm]"`.

## Personal configuration

```bash
cp data/experience_lake.example.json data/experience_lake.json
export EXPERIENCE_LAKE_PATH=data/experience_lake.json
export MIN_MATCH_SCORE=3
export EXTENSION_API_TOKEN="replace-with-a-long-random-token"
export ADZUNA_APP_ID="..."        # optional
export ADZUNA_APP_KEY="..."       # optional
```

The default API token is unset, so ingestion is disabled until you configure one. Start the local API with `job-agent-api`; it listens on `127.0.0.1:8000`.

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

## Publish your project

Create an empty repository under your personal GitHub account, review the profile data, then run:

```bash
git remote add origin https://github.com/<your-user>/<your-repository>.git
git add .
git commit -m "Prepare personal job agent for release"
git push -u origin main
```

Never commit API keys, browser session data, or your private Experience Lake.
