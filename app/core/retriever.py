from __future__ import annotations

import json
import math
import re
from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class Document:
    id: str
    title: str
    text: str


class Retriever:
    """Small dependency-free lexical retriever for local-first development."""

    def __init__(self, path: str):
        data = json.loads(Path(path).read_text(encoding="utf-8"))
        self.documents = [Document(**item) for item in data]
        self._tokens = {doc.id: self._tokenize(doc.text + " " + doc.title) for doc in self.documents}
        self._idf = self._build_idf()

    @staticmethod
    def _tokenize(text: str) -> list[str]:
        return [t for t in re.findall(r"[a-zA-Z0-9]+", text.lower()) if len(t) > 1]

    def _build_idf(self) -> dict[str, float]:
        n = len(self.documents)
        df: dict[str, int] = {}
        for tokens in self._tokens.values():
            for token in set(tokens):
                df[token] = df.get(token, 0) + 1
        return {token: math.log((n + 1) / (freq + 1)) + 1 for token, freq in df.items()}

    def search(self, query: str, k: int = 4) -> list[dict]:
        q_tokens = self._tokenize(query)
        if not q_tokens:
            return []
        q_set = set(q_tokens)
        q_weights = {t: self._idf.get(t, 1.0) for t in q_set}
        q_norm = math.sqrt(sum(v * v for v in q_weights.values())) or 1.0
        ranked = []
        for doc in self.documents:
            counts: dict[str, int] = {}
            for token in self._tokens[doc.id]:
                counts[token] = counts.get(token, 0) + 1
            weights = {t: counts.get(t, 0) * self._idf.get(t, 1.0) for t in q_set}
            dot = sum(q_weights[t] * weights[t] for t in q_set)
            d_norm = math.sqrt(sum(v * v for v in weights.values())) or 1.0
            score = dot / (q_norm * d_norm)
            if score > 0:
                ranked.append((score, doc))
        ranked.sort(key=lambda x: x[0], reverse=True)
        return [
            {"id": doc.id, "title": doc.title, "text": doc.text, "score": round(float(score), 4)}
            for score, doc in ranked[:k]
        ]
