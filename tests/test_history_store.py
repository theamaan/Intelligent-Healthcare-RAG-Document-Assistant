from backend.app.config import get_settings
from backend.app.core.history_store import append_history, get_history


def test_history_roundtrip(tmp_path, monkeypatch) -> None:
    monkeypatch.setenv("HISTORY_DIR", str(tmp_path))
    get_settings.cache_clear()

    append_history("doc_abc", "What is covered?", "Hospitalization is covered")
    items = get_history("doc_abc")

    assert len(items) == 1
    assert items[0]["question"] == "What is covered?"
