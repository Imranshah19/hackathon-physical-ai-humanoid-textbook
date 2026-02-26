"""
Tests for application configuration (Settings).
"""

import pytest


def test_settings_default_values():
    """Optional settings should resolve to documented defaults."""
    from src.config import get_settings

    s = get_settings()

    assert s.api_host == "0.0.0.0"
    assert s.api_port == 8000
    assert s.api_prefix == "/api/v1"
    assert s.environment == "development"
    assert s.debug is False
    assert s.qdrant_collection == "documentation"
    assert s.embedding_model == "all-MiniLM-L6-v2"
    assert s.rate_limit_requests == 30
    assert s.rate_limit_window_seconds == 60
    assert s.session_token_length == 64
    assert s.session_expiry_days == 30
    assert s.log_level == "INFO"
    assert s.anthropic_model == "claude-sonnet-4-20250514"
    assert s.anthropic_max_tokens == 1024
    assert s.openai_model == "gpt-4o-mini"
    assert s.openai_max_tokens == 1024
    assert s.auth_service_url == "http://localhost:3001"


def test_settings_required_fields_populated():
    """Required fields should be set from conftest env vars."""
    from src.config import get_settings

    s = get_settings()

    assert s.database_url
    assert s.qdrant_url
    assert s.qdrant_api_key
    assert s.anthropic_api_key


def test_settings_cors_origins_is_list():
    """cors_origins should be a list of strings."""
    from src.config import get_settings

    s = get_settings()

    assert isinstance(s.cors_origins, list)
    assert len(s.cors_origins) >= 1
    for origin in s.cors_origins:
        assert isinstance(origin, str)


def test_settings_debug_env_override(monkeypatch):
    """DEBUG env var should override the default False value."""
    from src.config import get_settings

    monkeypatch.setenv("DEBUG", "true")
    get_settings.cache_clear()

    s = get_settings()
    assert s.debug is True

    get_settings.cache_clear()


def test_settings_log_level_override(monkeypatch):
    """LOG_LEVEL env var should be respected."""
    from src.config import get_settings

    monkeypatch.setenv("LOG_LEVEL", "DEBUG")
    get_settings.cache_clear()

    s = get_settings()
    assert s.log_level == "DEBUG"

    get_settings.cache_clear()


def test_settings_api_port_override(monkeypatch):
    """API_PORT env var should be cast to int."""
    from src.config import get_settings

    monkeypatch.setenv("API_PORT", "9000")
    get_settings.cache_clear()

    s = get_settings()
    assert s.api_port == 9000

    get_settings.cache_clear()


def test_settings_session_expiry_days_override(monkeypatch):
    """SESSION_EXPIRY_DAYS env var should be respected."""
    from src.config import get_settings

    monkeypatch.setenv("SESSION_EXPIRY_DAYS", "7")
    get_settings.cache_clear()

    s = get_settings()
    assert s.session_expiry_days == 7

    get_settings.cache_clear()


def test_settings_missing_database_url_raises(monkeypatch):
    """Missing DATABASE_URL should raise a validation error."""
    from src.config import get_settings

    monkeypatch.delenv("DATABASE_URL", raising=False)
    get_settings.cache_clear()

    with pytest.raises(Exception):
        get_settings()

    get_settings.cache_clear()


def test_settings_missing_anthropic_key_raises(monkeypatch):
    """Missing ANTHROPIC_API_KEY should raise a validation error."""
    from src.config import get_settings

    monkeypatch.delenv("ANTHROPIC_API_KEY", raising=False)
    get_settings.cache_clear()

    with pytest.raises(Exception):
        get_settings()

    get_settings.cache_clear()


def test_settings_openai_key_optional(monkeypatch):
    """OPENAI_API_KEY should default to empty string when not set."""
    from src.config import get_settings

    monkeypatch.delenv("OPENAI_API_KEY", raising=False)
    get_settings.cache_clear()

    # Should not raise; openai_api_key defaults to ""
    s = get_settings()
    assert s.openai_api_key == ""

    get_settings.cache_clear()
