"""
Models module with SQLAlchemy models and Pydantic schemas.

Base schemas for API requests and responses.
"""

from datetime import datetime
from typing import Any, Generic, TypeVar
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field

# Type variable for generic responses
T = TypeVar("T")


class BaseSchema(BaseModel):
    """Base schema with common configuration."""

    model_config = ConfigDict(
        from_attributes=True,
        populate_by_name=True,
        str_strip_whitespace=True,
    )


class TimestampMixin(BaseModel):
    """Mixin for models with timestamp fields."""

    created_at: datetime
    updated_at: datetime | None = None


class UUIDMixin(BaseModel):
    """Mixin for models with UUID primary key."""

    id: UUID


class PaginatedResponse(BaseModel, Generic[T]):
    """Generic paginated response wrapper."""

    items: list[T]
    total: int
    page: int = Field(ge=1)
    page_size: int = Field(ge=1, le=100)
    has_next: bool
    has_prev: bool


class ErrorResponse(BaseModel):
    """Standard error response."""

    error: str
    detail: str | None = None
    code: str | None = None


class SuccessResponse(BaseModel):
    """Standard success response."""

    success: bool = True
    message: str | None = None
    data: dict[str, Any] | None = None


# Export SQLAlchemy models
from src.models.session import UserSession

__all__ = [
    "BaseSchema",
    "TimestampMixin",
    "UUIDMixin",
    "PaginatedResponse",
    "ErrorResponse",
    "SuccessResponse",
    "UserSession",
]
