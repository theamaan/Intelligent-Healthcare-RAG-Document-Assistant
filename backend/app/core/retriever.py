from langchain_core.retrievers import BaseRetriever

from backend.app.config import get_settings
from backend.app.core.vector_store import load_store


def get_retriever(doc_id: str) -> BaseRetriever:
    settings = get_settings()
    store = load_store(doc_id)
    return store.as_retriever(
        search_type="mmr",
        search_kwargs={"k": settings.retrieval_k, "fetch_k": settings.retrieval_fetch_k},
    )
