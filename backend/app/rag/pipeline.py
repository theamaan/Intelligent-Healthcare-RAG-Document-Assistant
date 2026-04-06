from langchain_core.prompts import PromptTemplate

from backend.app.core.history_store import append_history
from backend.app.core.llm_provider import get_llm
from backend.app.core.retriever import get_retriever
from backend.app.models.schemas import Citation, QueryResponse
from backend.app.rag.prompts import RAG_PROMPT


def _build_context(docs) -> str:
    sections = []
    for doc in docs:
        page = doc.metadata.get("page_number")
        section = doc.metadata.get("section")
        sections.append(
            f"[source={doc.metadata.get('source')}; page={page}; section={section}]\n{doc.page_content}"
        )
    return "\n\n".join(sections)


def _build_citations(docs) -> list[Citation]:
    citations: list[Citation] = []
    seen: set[tuple[str, int | None, int | None]] = set()
    for doc in docs:
        source = str(doc.metadata.get("source", "unknown"))
        page_number = doc.metadata.get("page_number")
        chunk_index = doc.metadata.get("chunk_index")
        key = (source, page_number, chunk_index)
        if key in seen:
            continue
        seen.add(key)
        citations.append(
            Citation(
                source=source,
                page_number=page_number,
                chunk_index=chunk_index,
                excerpt=doc.page_content[:220],
            )
        )
    return citations


def answer_query(doc_id: str, question: str) -> QueryResponse:
    retriever = get_retriever(doc_id)
    docs = retriever.invoke(question)

    if not docs:
        answer = "Not found in document."
        append_history(doc_id, question, answer)
        return QueryResponse(doc_id=doc_id, question=question, answer=answer, citations=[], confidence=0.0)

    context = _build_context(docs)
    prompt = PromptTemplate.from_template(RAG_PROMPT)
    llm = get_llm()
    message = llm.invoke(prompt.format(context=context, question=question))
    answer = message.content if hasattr(message, "content") else str(message)

    if not answer.strip():
        answer = "Not found in document."

    citations = _build_citations(docs)
    confidence = min(1.0, max(0.1, len(citations) / 5.0))

    append_history(doc_id, question, answer)
    return QueryResponse(
        doc_id=doc_id,
        question=question,
        answer=answer,
        citations=citations,
        confidence=confidence,
    )
