from __future__ import annotations

from collections import deque
from dataclasses import dataclass, field
from hashlib import sha256

import httpx

from job_agent.schemas.jobs import JobPosting


@dataclass(slots=True)
class DiscoveryEngine:
    app_id: str | None = None
    app_key: str | None = None
    country: str = "us"
    queued_urls: deque[str] = field(default_factory=deque)

    def queue_external_job_url(self, url: str) -> None:
        self.queued_urls.append(url)

    def poll(self, query: str, limit: int = 20) -> list[JobPosting]:
        if limit < 1:
            raise ValueError("limit must be at least 1")
        jobs: list[JobPosting] = []
        jobs.extend(self._poll_queued_urls())
        if self.app_id and self.app_key:
            jobs.extend(self._poll_adzuna(query=query, limit=limit))
        return jobs

    def _poll_queued_urls(self) -> list[JobPosting]:
        queued: list[JobPosting] = []
        while self.queued_urls:
            url = self.queued_urls.popleft()
            queued.append(
                JobPosting(
                    id=f"ext::{sha256(url.encode('utf-8')).hexdigest()[:16]}",
                    title="External URL submission",
                    company="Unknown",
                    location="Unknown",
                    description="Fetch and parse this JD at runtime from URL.",
                    apply_url=url,
                    source="extension",
                )
            )
        return queued

    def _poll_adzuna(self, query: str, limit: int) -> list[JobPosting]:
        endpoint = f"https://api.adzuna.com/v1/api/jobs/{self.country}/search/1"
        params = {
            "app_id": self.app_id,
            "app_key": self.app_key,
            "results_per_page": limit,
            "what": query,
            "content-type": "application/json",
        }
        with httpx.Client(timeout=15.0) as client:
            response = client.get(endpoint, params=params)
            response.raise_for_status()
            payload = response.json()

        postings: list[JobPosting] = []
        for result in payload.get("results", []):
            postings.append(
                JobPosting(
                    id=result.get("id", "unknown"),
                    title=result.get("title", "Unknown Title"),
                    company=(result.get("company") or {}).get("display_name", "Unknown"),
                    location=(result.get("location") or {}).get("display_name", "Unknown"),
                    description=result.get("description", ""),
                    apply_url=result.get("redirect_url", ""),
                    source="adzuna",
                )
            )
        return postings
