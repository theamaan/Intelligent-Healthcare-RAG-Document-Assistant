from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from backend.app.api.routes.health import router as health_router
from backend.app.api.routes.history import router as history_router
from backend.app.api.routes.query import router as query_router
from backend.app.api.routes.upload import router as upload_router
from backend.app.config import get_settings

settings = get_settings()

app = FastAPI(title="Intelligent Healthcare RAG Assistant", version="0.1.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.allowed_origins(),
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(upload_router)
app.include_router(query_router)
app.include_router(history_router)
app.include_router(health_router)
