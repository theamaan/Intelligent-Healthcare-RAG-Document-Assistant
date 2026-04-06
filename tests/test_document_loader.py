from backend.app.core.document_loader import clean_text


def test_clean_text_removes_extra_whitespace() -> None:
    raw = "Coverage\n\n  includes\t\troom rent   and surgery."
    cleaned = clean_text(raw)
    assert cleaned == "Coverage includes room rent and surgery."
