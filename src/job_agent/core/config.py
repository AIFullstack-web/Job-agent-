from __future__ import annotations

import os
from dataclasses import dataclass


@dataclass(slots=True)
class AgentConfig:
    experience_lake_path: str = os.getenv("EXPERIENCE_LAKE_PATH", "data/experience_lake.example.json")
    min_match_score: int = int(os.getenv("MIN_MATCH_SCORE", "3"))
    adzuna_app_id: str | None = os.getenv("ADZUNA_APP_ID")
    adzuna_app_key: str | None = os.getenv("ADZUNA_APP_KEY")
    adzuna_country: str = os.getenv("ADZUNA_COUNTRY", "us")
    openai_model: str = os.getenv("OPENAI_MODEL", "gpt-4o")
    extension_api_token: str = os.getenv("EXTENSION_API_TOKEN", "dev-token")
    cdp_url: str = os.getenv("CDP_URL", "http://127.0.0.1:9222")
    headless: bool = os.getenv("HEADLESS", "false").lower() == "true"
