from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def test_reason_endpoint():
    response = client.post("/api/v1/reason", json={"question": "What is Monte Carlo Tree Search?", "max_iterations": 3, "candidate_count": 3})
    assert response.status_code == 200
    body = response.json()
    assert body["answer"]
    assert body["candidate_trajectories"]
    assert 0.0 <= body["factuality_score"] <= 1.0
