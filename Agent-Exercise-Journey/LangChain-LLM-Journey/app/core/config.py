from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[2]


@dataclass(frozen=True)
class Settings:
    app_name: str = "Journey Personal Agent"
    environment: str = os.getenv("JOURNEY_ENV", "local")
    llm_provider: str = os.getenv("JOURNEY_LLM_PROVIDER", "mock")
    openai_api_key: str = os.getenv("OPENAI_API_KEY", "")
    openai_base_url: str = os.getenv("OPENAI_BASE_URL", "https://api.openai.com/v1")
    openai_model: str = os.getenv("OPENAI_MODEL", "gpt-4o-mini")
    ollama_base_url: str = os.getenv("OLLAMA_BASE_URL", "http://127.0.0.1:11434")
    ollama_model: str = os.getenv("OLLAMA_MODEL", "llama3.1")
    data_dir: Path = PROJECT_ROOT / "data"
    knowledge_path: Path = PROJECT_ROOT / "data" / "knowledge.json"
    vector_store_path: Path = PROJECT_ROOT / "data" / "local_vector_store.json"
    calendar_path: Path = PROJECT_ROOT / "data" / "calendar_events.json"


settings = Settings()
