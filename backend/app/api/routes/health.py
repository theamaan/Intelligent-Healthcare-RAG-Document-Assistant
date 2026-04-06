from fastapi import APIRouter

from backend.app.core.llm_provider import check_ollama_health

router = APIRouter(tags=["health"])


@router.get("/health")
def health() -> dict:
    return {"status": "ok", "ollama_connected": check_ollama_health()}
