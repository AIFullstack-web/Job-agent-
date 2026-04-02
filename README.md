# Autonomous Job Agent

A self-hosted Python agent for job discovery, LLM-based matching, grounded tailoring, and stealth-capable application submission.

## What is now implemented

- **LLM integration** for semantic match scoring and tailoring (OpenAI via LangChain wrappers).
- **Discovery** from Adzuna + extension URL ingestion + external URL parsing.
- **Grounded RAG** using Experience Lake documents.
- **Persistence** with SQLite for discovered jobs, match results, and submission records.
- **Submission execution** wired in workflow (dry-run switch available).
- **FastAPI endpoint** for browser extension URL push.
- **PDF generation** for tailored resume and cover letter outputs.
- **Observability** through structured logging.

## Directory structure

```text
src/job_agent/
  api/           # FastAPI endpoint for extension URL ingestion
  cli/           # Run entrypoint
  core/          # Env config
  discovery/     # Adzuna + queued URL discovery
  experience/    # Experience Lake models and loader
  llm/           # LLM client/retry wrapper
  matching/      # Match scoring logic
  observability/ # logging setup
  parsing/       # External job page parser
  persistence/   # SQLite store
  rag/           # Grounding retrieval index
  schemas/       # Fill plan + domain schemas
  submission/    # Stealth browser execution
  tailoring/     # Resume/cover generation + PDF output
  workflows/     # LangGraph orchestration
extension/       # Chrome extension to push active job URL
```

## Setup

1. Use Python 3.11+.
2. Create virtualenv and install dependencies.
3. Copy `.env.example` to `.env` and fill keys.

```bash
python -m venv .venv
source .venv/bin/activate
pip install -e .[dev]
cp .env.example .env
```

## Run

### 1) Start API for extension URL ingestion
```bash
PYTHONPATH=src uvicorn job_agent.api.app:app --reload
```

### 2) Run agent workflow
```bash
PYTHONPATH=src python -m job_agent.cli.run_agent
```

### 3) Run tests
```bash
pytest
```

## Chrome extension

Load `extension/` as an unpacked extension in Chrome developer mode, then click the extension button on a job page to push URL to `/ingest/job-url`.
