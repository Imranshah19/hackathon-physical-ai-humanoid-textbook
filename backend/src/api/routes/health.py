"""
Health check endpoint for service monitoring.
"""

from datetime import datetime, timezone
from typing import Literal

from fastapi import APIRouter
from pydantic import BaseModel
from sqlalchemy import text

from src.db.postgres import get_db
from src.db.qdrant import get_qdrant

router = APIRouter()


class HealthStatus(BaseModel):
    """Health check response model."""

    status: Literal["healthy", "degraded", "unhealthy"]
    timestamp: datetime
    version: str = "1.0.0"
    checks: dict[str, dict[str, str | bool]]


@router.get("/health", response_model=HealthStatus)
async def health_check() -> HealthStatus:
    """
    Check service health including database connectivity.

    Returns:
        HealthStatus: Current health status with component checks.
    """
    checks: dict[str, dict[str, str | bool]] = {}
    overall_healthy = True

    # Check PostgreSQL
    try:
        async with get_db() as session:
            await session.execute(text("SELECT 1"))
        checks["postgres"] = {"status": "healthy", "connected": True}
    except Exception as e:
        checks["postgres"] = {"status": "unhealthy", "connected": False, "error": str(e)}
        overall_healthy = False

    # Check Qdrant
    try:
        client = get_qdrant()
        collections = client.get_collections()
        checks["qdrant"] = {
            "status": "healthy",
            "connected": True,
            "collections": len(collections.collections),
        }
    except Exception as e:
        checks["qdrant"] = {"status": "unhealthy", "connected": False, "error": str(e)}
        overall_healthy = False

    return HealthStatus(
        status="healthy" if overall_healthy else "degraded",
        timestamp=datetime.now(timezone.utc),
        checks=checks,
    )


@router.get("/health/live")
async def liveness() -> dict[str, str]:
    """
    Kubernetes liveness probe endpoint.

    Returns 200 if the service is running.
    """
    return {"status": "alive"}


@router.get("/health/ready")
async def readiness() -> dict[str, str]:
    """
    Kubernetes readiness probe endpoint.

    Returns 200 if the service is ready to accept traffic.
    """
    # Could add more checks here (e.g., warm caches, connections)
    return {"status": "ready"}
