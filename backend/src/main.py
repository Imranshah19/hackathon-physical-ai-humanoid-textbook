"""
FastAPI application entry point with lifespan management.
"""

import logging
from contextlib import asynccontextmanager
from typing import AsyncGenerator

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

from src.api.middleware.cors import setup_cors
from src.api.middleware.rate_limit import RateLimitMiddleware
from src.api.middleware import auth as auth_middleware  # Auth dependencies available
from src.api.routes import chat, content, health, profile, translate
from src.config import get_settings
from src.db.postgres import close_db, init_db
from src.db.qdrant import close_qdrant, init_qdrant

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    """
    Application lifespan manager.

    Initializes and cleans up database connections.
    """
    settings = get_settings()
    logger.info(f"Starting application in {settings.environment} mode")

    # Initialize databases (graceful - app can work without them for basic chat)
    try:
        await init_db()
        logger.info("Database connection initialized")
    except Exception as e:
        logger.warning(f"Database init failed (chat will work without persistence): {e}")

    try:
        await init_qdrant()
        logger.info("Qdrant client initialized")
    except Exception as e:
        logger.warning(f"Qdrant init failed (chat will work without RAG): {e}")

    yield

    # Cleanup
    logger.info("Shutting down application")
    await close_db()
    await close_qdrant()
    logger.info("Database connections closed")


def create_app() -> FastAPI:
    """
    Create and configure the FastAPI application.

    Returns:
        FastAPI: Configured application instance.
    """
    settings = get_settings()

    app = FastAPI(
        title="RAG Documentation Chatbot API",
        description="AI-powered documentation assistant with citation support",
        version="1.0.0",
        docs_url=f"{settings.api_prefix}/docs" if settings.debug else None,
        redoc_url=f"{settings.api_prefix}/redoc" if settings.debug else None,
        openapi_url=f"{settings.api_prefix}/openapi.json" if settings.debug else None,
        lifespan=lifespan,
    )

    # Setup middleware
    setup_cors(app)
    app.add_middleware(RateLimitMiddleware)

    # Register routes
    app.include_router(health.router, prefix=settings.api_prefix, tags=["health"])
    app.include_router(chat.router, prefix=settings.api_prefix, tags=["chat"])
    app.include_router(content.router, tags=["content"])  # Content routes at /api/content
    app.include_router(profile.router, prefix=settings.api_prefix, tags=["profile"])
    app.include_router(translate.router, prefix=settings.api_prefix, tags=["translate"])

    # Global exception handler
    @app.exception_handler(Exception)
    async def global_exception_handler(request: Request, exc: Exception) -> JSONResponse:
        logger.error(f"Unhandled exception: {exc}", exc_info=True)
        return JSONResponse(
            status_code=500,
            content={
                "error": "Internal server error",
                "detail": str(exc) if settings.debug else None,
            },
        )

    return app


app = create_app()


if __name__ == "__main__":
    import uvicorn

    settings = get_settings()
    uvicorn.run(
        "src.main:app",
        host=settings.api_host,
        port=settings.api_port,
        reload=settings.environment == "development",
    )
