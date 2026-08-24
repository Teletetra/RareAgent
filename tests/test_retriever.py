from app.core.retriever import Retriever


def test_retriever_returns_relevant_document():
    retriever = Retriever("app/data/knowledge.json")
    results = retriever.search("Monte Carlo Tree Search UCT", k=2)
    assert results
    assert results[0]["id"] == "ai-1"
    assert results[0]["score"] > 0
