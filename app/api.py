from fastapi import APIRouter

from app.config import settings
from app.core.generator import Generator
from app.core.mcts import MCTS
from app.core.rafs import RAFS
from app.core.retriever import Retriever
from app.models import Candidate, Evidence, ReasonRequest, ReasonResponse, StatementCheck

router = APIRouter(tags=["reasoning"])
retriever = Retriever(settings.corpus_path)
generator = Generator(retriever)
scorer = RAFS(retriever)


@router.post("/reason", response_model=ReasonResponse)
def reason(request: ReasonRequest) -> ReasonResponse:
    candidates = generator.generate_candidates(request.question, request.candidate_count)
    selected, ranked = MCTS(candidates, scorer, request.max_iterations).run()
    return ReasonResponse(
        question=request.question,
        answer=selected["answer"],
        action=selected["action"],
        factuality_score=selected["factuality_score"],
        statement_checks=[StatementCheck(**item) for item in selected["statement_checks"]],
        evidence=[Evidence(**item) for item in selected["evidence"]],
        candidate_trajectories=[Candidate(**item) for item in ranked],
        iterations=request.max_iterations,
    )
