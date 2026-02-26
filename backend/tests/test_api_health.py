"""
Tests for health check API endpoints.
"""

import pytest
from unittest.mock import AsyncMock, MagicMock, patch


# ---------------------------------------------------------------------------
# Liveness probe
# ---------------------------------------------------------------------------

async def test_liveness_returns_200(client):
    response = await client.get("/api/v1/health/live")
    assert response.status_code == 200


async def test_liveness_returns_alive_status(client):
    response = await client.get("/api/v1/health/live")
    assert response.json() == {"status": "alive"}


# ---------------------------------------------------------------------------
# Readiness probe
# ---------------------------------------------------------------------------

async def test_readiness_returns_200(client):
    response = await client.get("/api/v1/health/ready")
    assert response.status_code == 200


async def test_readiness_returns_ready_status(client):
    response = await client.get("/api/v1/health/ready")
    assert response.json() == {"status": "ready"}


# ---------------------------------------------------------------------------
# Full health check — helpers
# ---------------------------------------------------------------------------

def _healthy_db_ctx():
    """Return a mock async context manager that succeeds for DB execute."""
    mock_session = AsyncMock()
    mock_session.execute = AsyncMock()
    ctx = MagicMock()
    ctx.__aenter__ = AsyncMock(return_value=mock_session)
    ctx.__aexit__ = AsyncMock(return_value=None)
    return ctx


def _healthy_qdrant():
    """Return a mock Qdrant client with an empty collection list."""
    qdrant = MagicMock()
    collections = MagicMock()
    collections.collections = []
    qdrant.get_collections.return_value = collections
    return qdrant


def _failing_db_ctx(exc: Exception):
    """Return a mock async context manager that raises on enter."""
    ctx = MagicMock()
    ctx.__aenter__ = AsyncMock(side_effect=exc)
    ctx.__aexit__ = AsyncMock(return_value=None)
    return ctx


# ---------------------------------------------------------------------------
# Full health check — tests
# ---------------------------------------------------------------------------

async def test_health_returns_200_when_both_services_healthy(client):
    with (
        patch("src.api.routes.health.get_db", return_value=_healthy_db_ctx()),
        patch("src.api.routes.health.get_qdrant", return_value=_healthy_qdrant()),
    ):
        response = await client.get("/api/v1/health")
    assert response.status_code == 200


async def test_health_status_healthy_when_all_ok(client):
    with (
        patch("src.api.routes.health.get_db", return_value=_healthy_db_ctx()),
        patch("src.api.routes.health.get_qdrant", return_value=_healthy_qdrant()),
    ):
        data = (await client.get("/api/v1/health")).json()
    assert data["status"] == "healthy"


async def test_health_includes_postgres_and_qdrant_checks(client):
    with (
        patch("src.api.routes.health.get_db", return_value=_healthy_db_ctx()),
        patch("src.api.routes.health.get_qdrant", return_value=_healthy_qdrant()),
    ):
        data = (await client.get("/api/v1/health")).json()
    assert "postgres" in data["checks"]
    assert "qdrant" in data["checks"]


async def test_health_postgres_check_shows_healthy(client):
    with (
        patch("src.api.routes.health.get_db", return_value=_healthy_db_ctx()),
        patch("src.api.routes.health.get_qdrant", return_value=_healthy_qdrant()),
    ):
        data = (await client.get("/api/v1/health")).json()
    assert data["checks"]["postgres"]["status"] == "healthy"
    assert data["checks"]["postgres"]["connected"] is True


async def test_health_qdrant_check_shows_healthy(client):
    with (
        patch("src.api.routes.health.get_db", return_value=_healthy_db_ctx()),
        patch("src.api.routes.health.get_qdrant", return_value=_healthy_qdrant()),
    ):
        data = (await client.get("/api/v1/health")).json()
    assert data["checks"]["qdrant"]["status"] == "healthy"
    assert data["checks"]["qdrant"]["connected"] is True


async def test_health_includes_timestamp(client):
    with (
        patch("src.api.routes.health.get_db", return_value=_healthy_db_ctx()),
        patch("src.api.routes.health.get_qdrant", return_value=_healthy_qdrant()),
    ):
        data = (await client.get("/api/v1/health")).json()
    assert "timestamp" in data


async def test_health_includes_version(client):
    with (
        patch("src.api.routes.health.get_db", return_value=_healthy_db_ctx()),
        patch("src.api.routes.health.get_qdrant", return_value=_healthy_qdrant()),
    ):
        data = (await client.get("/api/v1/health")).json()
    assert "version" in data


async def test_health_degraded_when_db_down(client):
    with (
        patch(
            "src.api.routes.health.get_db",
            return_value=_failing_db_ctx(Exception("Connection refused")),
        ),
        patch("src.api.routes.health.get_qdrant", return_value=_healthy_qdrant()),
    ):
        data = (await client.get("/api/v1/health")).json()
    assert data["status"] == "degraded"
    assert data["checks"]["postgres"]["status"] == "unhealthy"
    assert data["checks"]["postgres"]["connected"] is False


async def test_health_degraded_when_qdrant_down(client):
    qdrant = MagicMock()
    qdrant.get_collections.side_effect = Exception("Qdrant timeout")
    with (
        patch("src.api.routes.health.get_db", return_value=_healthy_db_ctx()),
        patch("src.api.routes.health.get_qdrant", return_value=qdrant),
    ):
        data = (await client.get("/api/v1/health")).json()
    assert data["status"] == "degraded"
    assert data["checks"]["qdrant"]["status"] == "unhealthy"
    assert data["checks"]["qdrant"]["connected"] is False


async def test_health_error_message_included_when_service_down(client):
    with (
        patch(
            "src.api.routes.health.get_db",
            return_value=_failing_db_ctx(Exception("ECONNREFUSED")),
        ),
        patch("src.api.routes.health.get_qdrant", return_value=_healthy_qdrant()),
    ):
        data = (await client.get("/api/v1/health")).json()
    assert "error" in data["checks"]["postgres"]
    assert "ECONNREFUSED" in data["checks"]["postgres"]["error"]
