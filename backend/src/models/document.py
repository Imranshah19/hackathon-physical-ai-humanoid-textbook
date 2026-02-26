"""
Document chunk model and schemas for RAG retrieval.
"""

from datetime import datetime
from typing import Optional
from uuid import UUID

from pydantic import Field
from sqlalchemy import DateTime, Integer, String, Text, func
from sqlalchemy.dialects.postgresql import JSONB, UUID as PG_UUID
from sqlalchemy.orm import Mapped, mapped_column

from src.db.postgres import Base
from src.models import BaseSchema, UUIDMixin


class DocumentChunk(Base):
    """
    Postgres metadata for indexed documentation chunks.

    The actual vectors are stored in Qdrant with matching IDs.

    Attributes:
        id: Unique chunk identifier.
        source_url: Source documentation URL.
        section_title: Section heading.
        content: Chunk text content.
        content_hash: SHA-256 for change detection.
        chunk_index: Position within document.
        metadata: Additional metadata.
        created_at: Index time.
        updated_at: Last update time.
    """

    __tablename__ = "document_chunks"

    id: Mapped[UUID] = mapped_column(
        PG_UUID(as_uuid=True),
        primary_key=True,
        server_default=func.uuid_generate_v4(),
    )
    source_url: Mapped[str] = mapped_column(
        String(512),
        nullable=False,
        index=True,
    )
    section_title: Mapped[Optional[str]] = mapped_column(String(256))
    content: Mapped[str] = mapped_column(Text, nullable=False)
    content_hash: Mapped[str] = mapped_column(
        String(64),
        nullable=False,
        index=True,
    )
    chunk_index: Mapped[int] = mapped_column(Integer, nullable=False)
    metadata: Mapped[dict] = mapped_column(
        JSONB,
        nullable=False,
        server_default="{}",
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
        onupdate=func.now(),
        index=True,
    )

    __table_args__ = (
        {"sqlite_autoincrement": True},
    )

    def __repr__(self) -> str:
        return f"<DocumentChunk {self.id} url={self.source_url[:30]}... idx={self.chunk_index}>"


# Pydantic Schemas


class DocumentChunkSchema(BaseSchema, UUIDMixin):
    """Document chunk response schema."""

    source_url: str
    section_title: Optional[str] = None
    content: str
    content_hash: str
    chunk_index: int
    metadata: dict = {}
    created_at: datetime
    updated_at: datetime


class Citation(BaseSchema):
    """
    Citation from documentation source.

    Used in chat responses to reference source material.
    """

    text: str = Field(..., description="Quoted passage from documentation")
    source_url: str = Field(..., description="Documentation page URL")
    section_title: Optional[str] = Field(None, description="Section heading")
    relevance: float = Field(
        default=1.0,
        ge=0.0,
        le=1.0,
        description="Relevance score (0-1)",
    )
