from __future__ import annotations

import os
from dataclasses import dataclass


@dataclass(frozen=True)
class Settings:
    app_name: str = "RARE Agent"
    openai_api_key: str | None = os.getenv("OPENAI_API_KEY")
    openai_model: str = os.getenv("OPENAI_MODEL", "gpt-4o-mini")
    corpus_path: str = os.getenv("CORPUS_PATH", "app/data/knowledge.json")
    default_candidates: int = int(os.getenv("RARE_CANDIDATES", "4"))
    default_iterations: int = int(os.getenv("RARE_ITERATIONS", "8"))


settings = Settings()
