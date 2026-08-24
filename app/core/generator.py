from __future__ import annotations

import json
from typing import Any

from app.core.prompts import SYSTEM_PROMPT
from app.core.retriever import Retriever
from app.config import settings


class Generator:
    def __init__(self, retriever: Retriever):
        self.retriever = retriever
        self.client = None
        if settings.openai_api_key:
            try:
                from openai import OpenAI
                self.client = OpenAI(api_key=settings.openai_api_key)
            except Exception:
                self.client = None

    def _fallback(self, question: str, evidence: list[dict]) -> str:
        if not evidence:
            return "The local evidence corpus does not contain enough information to answer this question reliably."
        lead = evidence[0]["text"]
        return f"Based on the retrieved evidence: {lead}"

    def _llm(self, prompt: str) -> str | None:
        if not self.client:
            return None
        response = self.client.chat.completions.create(
            model=settings.openai_model,
            temperature=0.1,
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": prompt},
            ],
        )
        return response.choices[0].message.content.strip()

    def a6(self, question: str, k: int = 4) -> tuple[str, list[dict], str]:
        evidence = self.retriever.search(question, k=k)
        queries = [question]
        if self.client:
            query_prompt = f"Generate 2 concise retrieval queries for this question. Return only a JSON array.\nQuestion: {question}"
            raw = self._llm(query_prompt)
            if raw:
                try:
                    queries = json.loads(raw)
                except json.JSONDecodeError:
                    queries = [question]
        merged = {}
        for query in queries[:3]:
            for item in self.retriever.search(query, k=k):
                merged[item["id"]] = max(merged.get(item["id"], item), item, key=lambda x: x["score"])
        evidence = sorted(merged.values(), key=lambda x: x["score"], reverse=True)[:k]
        context = "\n".join(f"[{e['id']}] {e['text']}" for e in evidence)
        prompt = f"Answer the question using only the evidence.\nQuestion: {question}\nEvidence:\n{context}\nKeep the answer concise and cite evidence IDs in brackets."
        answer = self._llm(prompt) or self._fallback(question, evidence)
        return answer, evidence, "A6"

    def a7(self, question: str, k: int = 4) -> tuple[str, list[dict], str]:
        subquestions = [question]
        if self.client:
            raw = self._llm(f"Decompose this into up to 3 concise sub-questions. Return only a JSON array.\nQuestion: {question}")
            if raw:
                try:
                    subquestions = json.loads(raw)
                except json.JSONDecodeError:
                    subquestions = [question]
        all_evidence: dict[str, dict] = {}
        subanswers: list[str] = []
        for subq in subquestions[:3]:
            evidence = self.retriever.search(subq, k=k)
            for item in evidence:
                all_evidence[item["id"]] = item
            context = "\n".join(f"[{e['id']}] {e['text']}" for e in evidence)
            answer = self._llm(f"Re-answer this sub-question using only the evidence.\nSub-question: {subq}\nEvidence:\n{context}") or self._fallback(subq, evidence)
            subanswers.append(answer)
        evidence = sorted(all_evidence.values(), key=lambda x: x["score"], reverse=True)[:k]
        if self.client:
            context = "\n".join(f"[{e['id']}] {e['text']}" for e in evidence)
            answer = self._llm(f"Synthesize a concise final answer.\nOriginal question: {question}\nIntermediate answers:\n" + "\n".join(subanswers) + f"\nEvidence:\n{context}")
        else:
            answer = " ".join(subanswers)[:1200]
        return answer or "Insufficient evidence.", evidence, "A7"

    def generate_candidates(self, question: str, count: int) -> list[dict[str, Any]]:
        candidates: list[dict[str, Any]] = []
        a6_answer, a6_evidence, _ = self.a6(question)
        a7_answer, a7_evidence, _ = self.a7(question)
        candidates.extend([
            {"action": "A6", "answer": a6_answer, "evidence": a6_evidence, "summary": "Direct query-driven retrieval from the original question."},
            {"action": "A7", "answer": a7_answer, "evidence": a7_evidence, "summary": "Sub-question retrieval followed by evidence-based re-answering."},
        ])
        base_evidence = a6_evidence or a7_evidence
        if base_evidence:
            context = base_evidence[:3]
            candidates.append({"action": "A1", "answer": self._fallback(question, context), "evidence": context, "summary": "Single-step evidence-grounded candidate."})
            candidates.append({"action": "A5", "answer": self._fallback(question, context), "evidence": context, "summary": "Rephrased-question candidate using retrieved evidence."})
        return candidates[:count]
