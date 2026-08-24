# RARE — Retrieval-Augmented Reasoning Enhancement

A practical, research-oriented implementation inspired by **RARE: Retrieval-Augmented Reasoning Enhancement for Large Language Models**.

Paper: https://arxiv.org/abs/2412.02830

This project adapts the paper's core ideas into a self-contained application:

- **A6 retrieval action**: generate search queries from the original question and retrieve evidence.
- **A7 retrieval action**: decompose into sub-questions, retrieve evidence for each, and re-answer with context.
- **MCTS reasoning search**: explore multiple candidate reasoning trajectories and balance exploration/exploitation with UCT.
- **RAFS-style factuality scoring**: split candidate answers into statements, retrieve evidence for each, and score support.
- **FastAPI service**: expose a clean `/api/v1/reason` endpoint.
- **React client**: inspect the selected answer, candidate trajectories, retrieval evidence, and factuality score.
- **Local-first retrieval**: works with a small bundled knowledge corpus; optional OpenAI generation is enabled through environment variables.

> This is an independent implementation inspired by the paper, not the authors' official code.

## Architecture

```text
                           ┌──────────────────────────┐
                           │        User Query        │
                           └────────────┬─────────────┘
                                        │
                                        ▼
                           ┌──────────────────────────┐
                           │  Retrieval-Augmented     │
                           │       Generator          │
                           └────────────┬─────────────┘
                                        │
               ┌────────────────────────┼────────────────────────┐
               │                        │                        │
               ▼                        ▼                        ▼
          A1/A2 Reasoning          A6 Retrieval             A7 Retrieval
          candidate actions       query + evidence        sub-Q + evidence
               │                        │                        │
               └────────────────────────┼────────────────────────┘
                                        ▼
                              ┌───────────────────┐
                              │       MCTS        │
                              │   UCT selection   │
                              └────────┬──────────┘
                                       │ candidates
                                       ▼
                              ┌───────────────────┐
                              │       RAFS        │
                              │ statement-level   │
                              │ evidence scoring  │
                              └────────┬──────────┘
                                       │
                                       ▼
                              Highest factuality
                                  trajectory
```

## Project layout

```text
RareAgent/
├── app/
│   ├── api.py
│   ├── config.py
│   ├── models.py
│   ├── main.py
│   ├── core/
│   │   ├── generator.py
│   │   ├── mcts.py
│   │   ├── prompts.py
│   │   ├── rafs.py
│   │   └── retriever.py
│   └── data/
│       └── knowledge.json
├── tests/
│   ├── test_mcts.py
│   ├── test_retriever.py
│   └── test_pipeline.py
├── frontend/
│   ├── package.json
│   ├── index.html
│   └── src/
│       ├── App.jsx
│       └── main.jsx
├── .env.example
├── .gitignore
├── Dockerfile
├── docker-compose.yml
└── requirements.txt
```

## Quick start

### Backend

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload
```

Open `http://localhost:8000/docs`.

The system runs without an API key using the bundled corpus and deterministic generation fallback. To enable LLM-assisted candidate generation, set:

```bash
export OPENAI_API_KEY=...
export OPENAI_MODEL=gpt-4o-mini
```

### Frontend

```bash
cd frontend
npm install
npm run dev
```

The Vite client expects the API at `http://localhost:8000` by default.

### Docker

```bash
docker compose up --build
```

## API

`POST /api/v1/reason`

```json
{
  "question": "Why can a higher temperature increase evaporation?",
  "max_iterations": 8,
  "candidate_count": 4
}
```

The response includes:

- selected answer
- selected reasoning trajectory
- factuality score
- statement-level support labels
- retrieved evidence
- candidate trajectory scores
- search diagnostics

## Implementation notes

The paper describes RARE as extending rStar with two retrieval-augmented actions and a retrieval-augmented factuality scorer. This implementation follows those conceptual components while using a lightweight local vector-style lexical retriever so that the repository remains runnable without paid services or a separate vector database.

The code intentionally keeps chain-of-thought private. The API returns concise reasoning summaries, actions, evidence, and scores rather than exposing hidden model reasoning tokens.

## Development

```bash
pytest -q
```

## Reference

Tran et al., *RARE: Retrieval-Augmented Reasoning Enhancement for Large Language Models*, arXiv:2412.02830v3.
