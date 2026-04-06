from pathlib import Path

from langchain_community.vectorstores import FAISS
from langchain_core.documents import Document

from backend.app.config import get_settings
from backend.app.core.embeddings import get_embeddings


def _doc_store_path(doc_id: str) -> Path:
    settings = get_settings()
    return settings.vector_store_dir / doc_id


def store_exists(doc_id: str) -> bool:
    store_path = _doc_store_path(doc_id)
    return (store_path / "index.faiss").exists() and (store_path / "index.pkl").exists()


def create_and_persist_store(doc_id: str, chunks: list[Document]) -> int:
    if not chunks:
        raise ValueError("No chunks found for indexing.")

    store_path = _doc_store_path(doc_id)
    store_path.mkdir(parents=True, exist_ok=True)

    embeddings = get_embeddings()
    vector_store = FAISS.from_documents(chunks, embeddings)
    vector_store.save_local(str(store_path))
    return len(chunks)


def load_store(doc_id: str) -> FAISS:
    if not store_exists(doc_id):
        raise FileNotFoundError("Vector store not found for doc_id")

    embeddings = get_embeddings()
    return FAISS.load_local(
        str(_doc_store_path(doc_id)),
        embeddings,
        allow_dangerous_deserialization=True,
    )
