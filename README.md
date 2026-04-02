# Autonomous Job Agent

A self-hosted Python agent for job discovery, matching, and assisted application workflows.

## Current scaffold

- LangGraph-ready module layout
- Experience Lake loader for grounded profile retrieval
- Matcher agent for JD scoring with strengths and critical gaps output

## Quick start

```bash
python -m venv .venv
source .venv/bin/activate
pip install -e .[dev]
pytest
```
