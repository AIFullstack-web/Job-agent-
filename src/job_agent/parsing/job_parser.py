from __future__ import annotations

import re
from html.parser import HTMLParser

import httpx
from tenacity import retry, stop_after_attempt, wait_exponential


class _TextExtractor(HTMLParser):
    def __init__(self) -> None:
        super().__init__()
        self.parts: list[str] = []

    def handle_data(self, data: str) -> None:
        if data.strip():
            self.parts.append(data.strip())


class ExternalJobParser:
    @retry(wait=wait_exponential(min=1, max=8), stop=stop_after_attempt(3), reraise=True)
    def fetch(self, url: str) -> str:
        with httpx.Client(timeout=20.0, follow_redirects=True) as client:
            response = client.get(url)
            response.raise_for_status()
            return response.text

    def extract_description(self, html: str) -> str:
        # Prefer semantic markers in raw HTML chunks first.
        markers = ["description", "responsibilities", "requirements", "qualifications"]
        lowered = html.lower()
        collected: list[str] = []
        for marker in markers:
            idx = lowered.find(marker)
            if idx != -1:
                snippet = html[max(0, idx - 1200) : idx + 4800]
                collected.append(self._strip_html(snippet))

        if collected:
            return "\n\n".join(self._clean_text(x) for x in collected if x)[:6000]

        return self._clean_text(self._strip_html(html))[:6000]

    def _strip_html(self, html: str) -> str:
        parser = _TextExtractor()
        parser.feed(html)
        return " ".join(parser.parts)

    @staticmethod
    def _clean_text(text: str) -> str:
        return re.sub(r"\s+", " ", text).strip()
