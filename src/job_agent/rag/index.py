from __future__ import annotations

import math
import re
from collections import Counter

from job_agent.experience.loader import ExperienceDocument


class ExperienceRAGIndex:
    """Tiny local TF-IDF-like retrieval over experience documents."""

    def __init__(self, documents: list[ExperienceDocument]) -> None:
        self.documents = documents
        self._doc_terms = [self._terms(doc.page_content) for doc in documents]
        self._idf = self._compute_idf(self._doc_terms)

    def search(self, query: str, top_k: int = 5) -> list[ExperienceDocument]:
        query_terms = self._terms(query)
        if not query_terms:
            return self.documents[:top_k]

        scored: list[tuple[float, ExperienceDocument]] = []
        for doc_terms, doc in zip(self._doc_terms, self.documents):
            score = self._cosine_tfidf(query_terms, doc_terms)
            scored.append((score, doc))

        scored.sort(key=lambda x: x[0], reverse=True)
        return [doc for score, doc in scored[:top_k] if score > 0]

    def _cosine_tfidf(self, q: Counter[str], d: Counter[str]) -> float:
        vocab = set(q) | set(d)
        q_vec = [q[t] * self._idf.get(t, 1.0) for t in vocab]
        d_vec = [d[t] * self._idf.get(t, 1.0) for t in vocab]
        dot = sum(a * b for a, b in zip(q_vec, d_vec))
        q_norm = math.sqrt(sum(a * a for a in q_vec))
        d_norm = math.sqrt(sum(b * b for b in d_vec))
        if q_norm == 0 or d_norm == 0:
            return 0.0
        return dot / (q_norm * d_norm)

    @staticmethod
    def _terms(text: str) -> Counter[str]:
        words = re.findall(r"[a-zA-Z0-9+#.]{3,}", text.lower())
        return Counter(words)

    @staticmethod
    def _compute_idf(counters: list[Counter[str]]) -> dict[str, float]:
        df: Counter[str] = Counter()
        for c in counters:
            df.update(c.keys())
        total = max(1, len(counters))
        return {term: math.log((1 + total) / (1 + count)) + 1 for term, count in df.items()}
