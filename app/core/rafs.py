from __future__ import annotations

import re

from app.core.retriever import Retriever


class RAFS:
    """Lightweight Retrieval-Augmented Factuality Scorer inspired by RARE."""

    def __init__(self, retriever: Retriever):
        self.retriever = retriever

    @staticmethod
    def split_statements(answer: str) -> list[str]:
        parts = re.split(r"(?<=[.!?])\s+", answer.strip())
        return [p.strip() for p in parts if p.strip()]

    def score(self, answer: str) -> tuple[float, list[dict]]:
        statements = self.split_statements(answer)
        if not statements:
            return 0.0, []
        checks = []
        for statement in statements:
            evidence = self.retriever.search(statement, k=3)
            best = evidence[0]["score"] if evidence else 0.0
            supported = best >= 0.18
            checks.append({
                "statement": statement,
                "supported": supported,
                "evidence_ids": [item["id"] for item in evidence[:2]],
            })
        score = sum(1 for c in checks if c["supported"]) / len(checks)
        return round(score, 4), checks
