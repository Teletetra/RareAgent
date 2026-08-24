from __future__ import annotations

from pydantic import BaseModel, Field


class ReasonRequest(BaseModel):
    question: str = Field(min_length=3, max_length=4000)
    max_iterations: int = Field(default=8, ge=1, le=50)
    candidate_count: int = Field(default=4, ge=1, le=12)


class Evidence(BaseModel):
    id: str
    title: str
    text: str
    score: float


class StatementCheck(BaseModel):
    statement: str
    supported: bool
    evidence_ids: list[str] = []


class Candidate(BaseModel):
    id: str
    action: str
    answer: str
    summary: str
    evidence: list[Evidence]
    factuality_score: float
    statement_checks: list[StatementCheck]
    value: float


class ReasonResponse(BaseModel):
    question: str
    answer: str
    action: str
    factuality_score: float
    statement_checks: list[StatementCheck]
    evidence: list[Evidence]
    candidate_trajectories: list[Candidate]
    iterations: int
