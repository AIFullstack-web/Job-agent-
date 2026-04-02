from __future__ import annotations

import logging
from collections import deque
from dataclasses import dataclass, field

import httpx
from tenacity import retry, stop_after_attempt, wait_exponential

from job_agent.parsing.job_parser import ExternalJobParser
from job_agent.schemas.jobs import JobPosting

logger = logging.getLogger(__name__)


@dataclass(slots=True)
class DiscoveryEngine:
    app_id: str | None = None
    app_key: str | None = None
    country: str = "us"
    queued_urls: deque[str] = field(default_factory=deque)
    parser: ExternalJobParser = field(default_factory=ExternalJobParser)
    seen_urls: set[str] = field(default_factory=set)

    def queue_external_job_url(self, url: str) -> None:
        if url not in self.seen_urls:
            self.queued_urls.append(url)
            self.seen_urls.add(url)

    def poll(self, query: str, limit: int = 20) -> list[JobPosting]:
        jobs: list[JobPosting] = []
        jobs.extend(self._poll_queued_urls())
        if self.app_id and self.app_key:
            jobs.extend(self._poll_adzuna(query=query, limit=limit))
        logger.info("Discovery returned %s jobs", len(jobs))
        return jobs

    def _poll_queued_urls(self) -> list[JobPosting]:
        queued: list[JobPosting] = []
        while self.queued_urls:
            url = self.queued_urls.popleft()
            try:
                html = self.parser.fetch(url)
                description = self.parser.extract_description(html)
            except Exception as exc:
                logger.warning("Failed to parse external URL %s: %s", url, exc)
                description = ""
            queued.append(
                JobPosting(
                    id=f"ext::{abs(hash(url))}",
                    title="External URL submission",
                    company="Unknown",
                    location="Unknown",
                    description=description,
                    apply_url=url,
                    source="extension",
                )
            )
        return queued

    @retry(wait=wait_exponential(min=1, max=8), stop=stop_after_attempt(3), reraise=True)
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
            apply_url = result.get("redirect_url", "")
            if not apply_url or apply_url in self.seen_urls:
                continue
            self.seen_urls.add(apply_url)
            postings.append(
                JobPosting(
                    id=result.get("id", "unknown"),
                    title=result.get("title", "Unknown Title"),
                    company=(result.get("company") or {}).get("display_name", "Unknown"),
                    location=(result.get("location") or {}).get("display_name", "Unknown"),
                    description=result.get("description", ""),
                    apply_url=apply_url,
                    source="adzuna",
                )
            )
        return postings
