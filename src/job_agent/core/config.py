from __future__ import annotations

import os
from dataclasses import dataclass

from dotenv import load_dotenv

load_dotenv()


@dataclass(slots=True)
class AgentConfig:
    experience_lake_path: str = os.getenv("EXPERIENCE_LAKE_PATH", "data/experience_lake.example.json")
    min_match_score: int = int(os.getenv("MIN_MATCH_SCORE", "3"))

    adzuna_app_id: str | None = os.getenv("ADZUNA_APP_ID")
    adzuna_app_key: str | None = os.getenv("ADZUNA_APP_KEY")
    adzuna_country: str = os.getenv("ADZUNA_COUNTRY", "us")

    openai_api_key: str | None = os.getenv("OPENAI_API_KEY")
    openai_model: str = os.getenv("OPENAI_MODEL", "gpt-4o")

    extension_api_token: str = os.getenv("EXTENSION_API_TOKEN", "dev-token")
    cdp_url: str = os.getenv("CDP_URL", "http://127.0.0.1:9222")
    headless: bool = os.getenv("HEADLESS", "false").lower() == "true"
    dry_run_submission: bool = os.getenv("DRY_RUN_SUBMISSION", "true").lower() == "true"

    sqlite_path: str = os.getenv("SQLITE_PATH", "data/job_agent.db")
    output_dir: str = os.getenv("OUTPUT_DIR", "output")
