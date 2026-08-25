from __future__ import annotations

import os
from dataclasses import dataclass


@dataclass(slots=True)
class AgentConfig:
    experience_lake_path: str = "data/experience_lake.example.json"
    min_match_score: int = 3
    adzuna_app_id: str | None = None
    adzuna_app_key: str | None = None
    adzuna_country: str = "us"
    openai_model: str = "gpt-4o"
    extension_api_token: str | None = None
    cdp_url: str = "http://127.0.0.1:9222"
    headless: bool = False

    def __post_init__(self) -> None:
        """Apply environment overrides when each config instance is created."""
        self.experience_lake_path = os.getenv(
            "EXPERIENCE_LAKE_PATH", self.experience_lake_path
        )
        self.min_match_score = int(os.getenv("MIN_MATCH_SCORE", str(self.min_match_score)))
        self.adzuna_app_id = os.getenv("ADZUNA_APP_ID", self.adzuna_app_id)
        self.adzuna_app_key = os.getenv("ADZUNA_APP_KEY", self.adzuna_app_key)
        self.adzuna_country = os.getenv("ADZUNA_COUNTRY", self.adzuna_country)
        self.openai_model = os.getenv("OPENAI_MODEL", self.openai_model)
        self.extension_api_token = os.getenv("EXTENSION_API_TOKEN", self.extension_api_token)
        self.cdp_url = os.getenv("CDP_URL", self.cdp_url)
        self.headless = os.getenv("HEADLESS", str(self.headless)).lower() in {"1", "true", "yes"}
