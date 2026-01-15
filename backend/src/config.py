"""
Application settings management using pydantic-settings.

Loads configuration from environment variables with type validation.
"""

from functools import lru_cache
from typing import Literal

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    # Environment
    environment: Literal["development", "staging", "production"] = "development"
    debug: bool = False

    # API Configuration
    api_host: str = "0.0.0.0"
    api_port: int = 8000
    api_prefix: str = "/api/v1"

    # Database - Neon Postgres
    database_url: str
    database_pool_size: int = 5
    database_max_overflow: int = 10

    # Vector Database - Qdrant Cloud
    qdrant_url: str
    qdrant_api_key: str
    qdrant_collection: str = "documentation"

    # Anthropic Claude
    anthropic_api_key: str
    anthropic_model: str = "claude-sonnet-4-20250514"
    anthropic_max_tokens: int = 1024

    # Embeddings (local sentence-transformers)
    embedding_model: str = "all-MiniLM-L6-v2"

    # Rate Limiting
    rate_limit_requests: int = 30
    rate_limit_window_seconds: int = 60

    # Session
    session_token_length: int = 64
    session_expiry_days: int = 30

    # CORS
    cors_origins: list[str] = ["http://localhost:3000", "http://localhost:3001"]

    # Logging
    log_level: str = "INFO"


@lru_cache
def get_settings() -> Settings:
    """
    Get cached application settings.

    Returns:
        Settings: Validated application settings.
    """
    return Settings()
