"""
Tests for the chat API endpoints.

Focuses on request validation (422) and feedback validation (400/404).
Full integration tests require a real database; those are exercised via
dependency overrides for DB and session.
"""

import pytest
from uuid import uuid4
from unittest.mock import AsyncMock, MagicMock


# ---------------------------------------------------------------------------
# /api/v1/chat — request validation (pydantic, no auth needed)
# ---------------------------------------------------------------------------

async def test_chat_missing_message_returns_422(client):
    """Request without 'message' field should be rejected."""
    response = await client.post(
        "/api/v1/chat",
        json={"page_url": "http://example.com"},
    )
    assert response.status_code == 422


async def test_chat_missing_page_url_returns_422(client):
    """Request without 'page_url' field should be rejected."""
    response = await client.post(
        "/api/v1/chat",
        json={"message": "Hello"},
    )
    assert response.status_code == 422


async def test_chat_empty_message_returns_422(client):
    """Empty string message should fail min_length=1 validation."""
    response = await client.post(
        "/api/v1/chat",
        json={"message": "", "page_url": "http://example.com"},
    )
    assert response.status_code == 422


async def test_chat_message_too_long_returns_422(client):
    """Message exceeding 4000 characters should fail max_length validation."""
    response = await client.post(
        "/api/v1/chat",
        json={"message": "x" * 4001, "page_url": "http://example.com"},
    )
    assert response.status_code == 422


async def test_chat_message_at_max_length_passes_validation(client, app):
    """A 4000-character message is exactly at the limit and should pass validation.
    It will fail later (auth/db), but the 422 validation should NOT fire.
    """
    response = await client.post(
        "/api/v1/chat",
        json={"message": "x" * 4000, "page_url": "http://example.com"},
    )
    # 422 means pydantic rejected it; any other code means it passed validation
    assert response.status_code != 422


async def test_chat_accepts_optional_fields(client):
    """Optional fields should not cause 422 when omitted."""
    response = await client.post(
        "/api/v1/chat",
        json={
            "message": "Hello",
            "page_url": "http://example.com",
            # conversation_id, page_title, selected_text all omitted
        },
    )
    assert response.status_code != 422


async def test_chat_selected_text_too_long_returns_422(client):
    """selected_text over 5000 characters should fail max_length."""
    response = await client.post(
        "/api/v1/chat",
        json={
            "message": "Hello",
            "page_url": "http://example.com",
            "selected_text": "t" * 5001,
        },
    )
    assert response.status_code == 422


# ---------------------------------------------------------------------------
# /api/v1/chat/stream — request validation
# ---------------------------------------------------------------------------

async def test_stream_missing_message_returns_422(client):
    response = await client.post(
        "/api/v1/chat/stream",
        json={"page_url": "http://example.com"},
    )
    assert response.status_code == 422


async def test_stream_missing_page_url_returns_422(client):
    response = await client.post(
        "/api/v1/chat/stream",
        json={"message": "Hello"},
    )
    assert response.status_code == 422


# ---------------------------------------------------------------------------
# /api/v1/messages/{id}/feedback — validation with dependency overrides
# ---------------------------------------------------------------------------

def _override_deps(app, session_id=None):
    """Override get_session_id and get_db_session on the app."""
    from src.api.routes.chat import get_session_id
    from src.db.postgres import get_db_session

    _session_id = session_id or uuid4()

    async def mock_session_id():
        return _session_id

    async def mock_db():
        db = AsyncMock()
        result = MagicMock()
        result.scalar_one_or_none.return_value = None
        db.execute = AsyncMock(return_value=result)
        db.commit = AsyncMock()
        yield db

    app.dependency_overrides[get_session_id] = mock_session_id
    app.dependency_overrides[get_db_session] = mock_db
    return _session_id


async def test_feedback_invalid_value_returns_400(client, app):
    """Feedback values other than 'up'/'down' should return 400."""
    _override_deps(app)
    try:
        fake_id = str(uuid4())
        response = await client.post(
            f"/api/v1/messages/{fake_id}/feedback?feedback=invalid",
        )
        assert response.status_code == 400
    finally:
        app.dependency_overrides.clear()


async def test_feedback_up_passes_validation(client, app):
    """'up' is a valid feedback value; should get 404 (msg not found), not 400."""
    _override_deps(app)
    try:
        fake_id = str(uuid4())
        response = await client.post(
            f"/api/v1/messages/{fake_id}/feedback?feedback=up",
        )
        # 404 because the mock DB returns None for message lookup
        assert response.status_code == 404
    finally:
        app.dependency_overrides.clear()


async def test_feedback_down_passes_validation(client, app):
    """'down' is a valid feedback value; should get 404, not 400."""
    _override_deps(app)
    try:
        fake_id = str(uuid4())
        response = await client.post(
            f"/api/v1/messages/{fake_id}/feedback?feedback=down",
        )
        assert response.status_code == 404
    finally:
        app.dependency_overrides.clear()


async def test_feedback_invalid_uuid_returns_422(client):
    """A non-UUID message_id should fail FastAPI path validation."""
    response = await client.post(
        "/api/v1/messages/not-a-uuid/feedback?feedback=up",
    )
    assert response.status_code == 422
