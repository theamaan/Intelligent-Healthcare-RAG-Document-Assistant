import pytest

from backend.app.config import get_settings


@pytest.fixture(autouse=True)
def clear_settings_cache():
    """Clear the LRU-cached Settings object before and after every test.

    This ensures that monkeypatch.setenv / monkeypatch.setattr changes
    take effect cleanly and do not leak between tests.
    """
    get_settings.cache_clear()
    yield
    get_settings.cache_clear()
