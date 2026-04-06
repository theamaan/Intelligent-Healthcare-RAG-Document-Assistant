import httpx
from langchain_ollama import ChatOllama

from backend.app.config import get_settings


def get_llm() -> ChatOllama:
    settings = get_settings()
    return ChatOllama(model=settings.ollama_model, base_url=settings.ollama_base_url, temperature=0)


def check_ollama_health() -> bool:
    settings = get_settings()
    try:
        response = httpx.get(f"{settings.ollama_base_url}/api/tags", timeout=10)
        return response.status_code == 200
    except httpx.HTTPError:
        return False
