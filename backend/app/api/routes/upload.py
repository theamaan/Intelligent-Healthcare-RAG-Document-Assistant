from pathlib import Path
from uuid import uuid4

from fastapi import APIRouter, File, HTTPException, UploadFile

from backend.app.config import get_settings
from backend.app.core.chunker import chunk_documents
from backend.app.core.document_loader import ALLOWED_EXTENSIONS, load_document
from backend.app.core.vector_store import create_and_persist_store
from backend.app.models.schemas import UploadResponse

router = APIRouter(prefix="/upload", tags=["upload"])


@router.post("", response_model=UploadResponse)
async def upload_document(file: UploadFile = File(...)) -> UploadResponse:
    settings = get_settings()
    if not file.filename:
        raise HTTPException(status_code=400, detail="Missing filename")

    extension = Path(file.filename).suffix.lower()
    if extension not in ALLOWED_EXTENSIONS:
        raise HTTPException(status_code=400, detail="Only PDF and DOCX files are supported")

    content = await file.read()
    max_size = settings.max_file_size_mb * 1024 * 1024
    if len(content) > max_size:
        raise HTTPException(status_code=400, detail=f"File exceeds {settings.max_file_size_mb}MB limit")

    doc_id = f"doc_{uuid4().hex[:10]}"
    target_dir = settings.upload_dir / doc_id
    target_dir.mkdir(parents=True, exist_ok=True)
    target_path = target_dir / file.filename
    target_path.write_bytes(content)

    documents = load_document(target_path, doc_id)
    if not documents:
        raise HTTPException(status_code=400, detail="No readable text found in document")

    chunks = chunk_documents(documents)
    chunk_count = create_and_persist_store(doc_id, chunks)

    return UploadResponse(
        doc_id=doc_id,
        filename=file.filename,
        chunk_count=chunk_count,
        message="Document uploaded and indexed successfully",
    )
