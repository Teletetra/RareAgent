from app.core.mcts import MCTS, uct, Node


def test_uct_unvisited_is_explored():
    root = Node(candidate={})
    child = Node(candidate={}, parent=root)
    assert uct(child) == float("inf")


def test_mcts_selects_high_factuality_candidate():
    candidates = [
        {"action": "A6", "answer": "supported", "evidence": [], "summary": ""},
        {"action": "A7", "answer": "unsupported", "evidence": [], "summary": ""},
    ]

    class FakeScorer:
        def score(self, answer):
            return (1.0, [{"statement": answer, "supported": True, "evidence_ids": []}]) if answer == "supported" else (0.0, [{"statement": answer, "supported": False, "evidence_ids": []}])

    selected, ranked = MCTS(candidates, FakeScorer(), iterations=4).run()
    assert selected["answer"] == "supported"
    assert ranked[0]["factuality_score"] == 1.0
