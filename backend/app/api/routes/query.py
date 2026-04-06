from fastapi import APIRouter, HTTPException

from backend.app.core.vector_store import store_exists
from backend.app.models.schemas import QueryRequest, QueryResponse
from backend.app.rag.pipeline import answer_query

router = APIRouter(prefix="/query", tags=["query"])


@router.post("", response_model=QueryResponse)
def query_document(request: QueryRequest) -> QueryResponse:
    if not store_exists(request.doc_id):
        raise HTTPException(status_code=404, detail="Document index not found")

    return answer_query(request.doc_id, request.question)
