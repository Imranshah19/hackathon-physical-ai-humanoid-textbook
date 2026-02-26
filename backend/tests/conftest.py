"""
Shared test configuration and fixtures.

Sets required environment variables BEFORE any src.* imports to satisfy
pydantic Settings validation.
"""

import os
import sys
from unittest.mock import MagicMock

# Required env vars - must be set before importing any src.* module
os.environ.setdefault("DATABASE_URL", "postgresql+asyncpg://test:test@localhost/testdb")
os.environ.setdefault("QDRANT_URL", "http://localhost:6333")
os.environ.setdefault("QDRANT_API_KEY", "test-qdrant-key")
os.environ.setdefault(
    "ANTHROPIC_API_KEY",
    "sk-ant-test-00000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000",
)
os.environ.setdefault("OPENAI_API_KEY", "sk-test-00000000000000000000000000000000000000000000000000")

# Stub heavy optional dependencies that are not installed in the test environment.
# These must be in sys.modules before any src.* import triggers them.
_st_mock = MagicMock()
_st_mock.SentenceTransformer = MagicMock()
sys.modules.setdefault("sentence_transformers", _st_mock)
sys.modules.setdefault("torch", MagicMock())
sys.modules.setdefault("transformers", MagicMock())

from uuid import uuid4
from unittest.mock import AsyncMock, patch

import pytest
from httpx import AsyncClient, ASGITransport


@pytest.fixture
async def app():
    """FastAPI application with mocked DB and Qdrant startup.

    Also overrides the get_db_session and get_session_id dependencies so that
    every request gets a mock DB session without touching a real database.
    """
    with (
        patch("src.db.postgres.init_db", new_callable=AsyncMock),
        patch("src.db.qdrant.init_qdrant", new_callable=AsyncMock),
        patch("src.db.postgres.close_db", new_callable=AsyncMock),
        patch("src.db.qdrant.close_qdrant", new_callable=AsyncMock),
    ):
        from src.main import create_app
        from src.db.postgres import get_db_session
        from src.api.routes.chat import get_session_id

        application = create_app()

        # Default DB override — tests can replace this per-test if needed
        async def _mock_db():
            yield make_mock_db()

        async def _mock_session_id():
            return uuid4()

        application.dependency_overrides[get_db_session] = _mock_db
        application.dependency_overrides[get_session_id] = _mock_session_id

        yield application

        application.dependency_overrides.clear()


@pytest.fixture
async def client(app):
    """Async HTTP test client backed by the test app."""
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        yield ac


@pytest.fixture
def test_session_id():
    """A predictable UUID for session tests."""
    return uuid4()


def make_mock_db():
    """Return a mock AsyncSession with sane defaults."""
    db = AsyncMock()
    result = MagicMock()
    result.scalar_one_or_none.return_value = None
    result.scalars.return_value.all.return_value = []
    db.execute = AsyncMock(return_value=result)
    db.flush = AsyncMock()
    db.commit = AsyncMock()
    db.rollback = AsyncMock()
    db.add = MagicMock()
    return db
