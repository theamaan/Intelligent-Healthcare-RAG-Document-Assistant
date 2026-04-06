import json
from datetime import datetime, timezone
from pathlib import Path

from backend.app.config import get_settings


def _history_path(doc_id: str) -> Path:
    settings = get_settings()
    return settings.history_dir / f"{doc_id}.json"


def append_history(doc_id: str, question: str, answer: str) -> None:
    path = _history_path(doc_id)
    items = []
    if path.exists():
        items = json.loads(path.read_text(encoding="utf-8"))
    items.append(
        {
            "question": question,
            "answer": answer,
            "timestamp": datetime.now(timezone.utc).isoformat(),
        }
    )
    path.write_text(json.dumps(items, indent=2), encoding="utf-8")


def get_history(doc_id: str) -> list[dict]:
    path = _history_path(doc_id)
    if not path.exists():
        return []
    return json.loads(path.read_text(encoding="utf-8"))
