from langchain_core.documents import Document

from backend.app.core.chunker import chunk_documents


def test_chunker_preserves_metadata_and_adds_chunk_index() -> None:
    docs = [
        Document(
            page_content="Coverage details " * 200,
            metadata={"doc_id": "doc_test", "source": "policy.pdf", "page_number": 1},
        )
    ]

    chunks = chunk_documents(docs, chunk_size=300, chunk_overlap=50)

    assert len(chunks) > 1
    assert all("chunk_index" in chunk.metadata for chunk in chunks)
    assert chunks[0].metadata["source"] == "policy.pdf"
