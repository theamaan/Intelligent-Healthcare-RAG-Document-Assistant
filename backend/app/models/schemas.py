from pydantic import BaseModel, Field


class Citation(BaseModel):
    source: str
    page_number: int | None = None
    chunk_index: int | None = None
    excerpt: str


class UploadResponse(BaseModel):
    doc_id: str
    filename: str
    chunk_count: int
    message: str


class QueryRequest(BaseModel):
    doc_id: str = Field(min_length=1)
    question: str = Field(min_length=3)


class QueryResponse(BaseModel):
    doc_id: str
    question: str
    answer: str
    citations: list[Citation]
    confidence: float = Field(ge=0.0, le=1.0)


class HistoryItem(BaseModel):
    question: str
    answer: str
    timestamp: str


class HistoryResponse(BaseModel):
    doc_id: str
    items: list[HistoryItem]
