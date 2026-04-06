from functools import lru_cache
from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    api_host: str = "0.0.0.0"
    api_port: int = 8000
    cors_origins: str = "http://localhost:8501"

    ollama_base_url: str = "http://localhost:11434"
    ollama_model: str = "llama3.2:3b"

    embedding_model: str = "sentence-transformers/all-MiniLM-L6-v2"

    upload_dir: Path = Path("data/uploads")
    vector_store_dir: Path = Path("data/vector_stores")
    history_dir: Path = Path("data/history")
    eval_results_dir: Path = Path("data/eval_results")

    retrieval_k: int = 5
    retrieval_fetch_k: int = 20
    max_file_size_mb: int = 15

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")

    def allowed_origins(self) -> list[str]:
        return [origin.strip() for origin in self.cors_origins.split(",") if origin.strip()]

    def ensure_directories(self) -> None:
        self.upload_dir.mkdir(parents=True, exist_ok=True)
        self.vector_store_dir.mkdir(parents=True, exist_ok=True)
        self.history_dir.mkdir(parents=True, exist_ok=True)
        self.eval_results_dir.mkdir(parents=True, exist_ok=True)


@lru_cache
def get_settings() -> Settings:
    settings = Settings()
    settings.ensure_directories()
    return settings
