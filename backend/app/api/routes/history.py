from fastapi import APIRouter

from backend.app.core.history_store import get_history
from backend.app.models.schemas import HistoryItem, HistoryResponse

router = APIRouter(prefix="/history", tags=["history"])


@router.get("/{doc_id}", response_model=HistoryResponse)
def get_document_history(doc_id: str) -> HistoryResponse:
    items = [HistoryItem(**item) for item in get_history(doc_id)]
    return HistoryResponse(doc_id=doc_id, items=items)
