"""
Conversation and Message SQLAlchemy models.
"""

from datetime import datetime
from typing import TYPE_CHECKING, Literal, Optional
from uuid import UUID

from pydantic import BaseModel, Field
from sqlalchemy import DateTime, ForeignKey, Integer, String, Text, func
from sqlalchemy.dialects.postgresql import JSONB, UUID as PG_UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.db.postgres import Base
from src.models import BaseSchema, TimestampMixin, UUIDMixin

if TYPE_CHECKING:
    from src.models.session import UserSession


# SQLAlchemy Models


class Conversation(Base):
    """
    A chat session about selected documentation text.

    Attributes:
        id: Unique conversation identifier.
        session_id: Owning user session.
        page_url: Documentation page URL.
        page_title: Page title for display.
        selected_text: User-selected context text.
        created_at: Conversation start time.
        updated_at: Last message time.
    """

    __tablename__ = "conversations"

    id: Mapped[UUID] = mapped_column(
        PG_UUID(as_uuid=True),
        primary_key=True,
        server_default=func.uuid_generate_v4(),
    )
    session_id: Mapped[UUID] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("user_sessions.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    page_url: Mapped[str] = mapped_column(String(512), nullable=False)
    page_title: Mapped[Optional[str]] = mapped_column(String(256))
    selected_text: Mapped[Optional[str]] = mapped_column(Text)
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
    )

    # Relationships
    session: Mapped["UserSession"] = relationship(
        "UserSession",
        back_populates="conversations",
    )
    messages: Mapped[list["Message"]] = relationship(
        "Message",
        back_populates="conversation",
        cascade="all, delete-orphan",
        order_by="Message.created_at",
        lazy="selectin",
    )

    def __repr__(self) -> str:
        return f"<Conversation {self.id} page={self.page_url[:30]}...>"


class Message(Base):
    """
    Individual message within a conversation.

    Attributes:
        id: Unique message identifier.
        conversation_id: Parent conversation.
        role: Message author (user or assistant).
        content: Message text content.
        citations: Array of citation objects.
        tokens_used: Token count for cost tracking.
        latency_ms: Response generation time.
        feedback: User feedback (up/down).
        created_at: Message timestamp.
    """

    __tablename__ = "messages"

    id: Mapped[UUID] = mapped_column(
        PG_UUID(as_uuid=True),
        primary_key=True,
        server_default=func.uuid_generate_v4(),
    )
    conversation_id: Mapped[UUID] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("conversations.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    role: Mapped[str] = mapped_column(String(16), nullable=False)
    content: Mapped[str] = mapped_column(Text, nullable=False)
    citations: Mapped[list] = mapped_column(
        JSONB,
        nullable=False,
        server_default="[]",
    )
    tokens_used: Mapped[Optional[int]] = mapped_column(Integer)
    latency_ms: Mapped[Optional[int]] = mapped_column(Integer)
    feedback: Mapped[Optional[str]] = mapped_column(String(16))
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
    )

    # Relationships
    conversation: Mapped["Conversation"] = relationship(
        "Conversation",
        back_populates="messages",
    )

    def __repr__(self) -> str:
        return f"<Message {self.id} role={self.role}>"


# Pydantic Schemas


class Citation(BaseSchema):
    """Citation from documentation source."""

    text: str = Field(..., description="Quoted passage from documentation")
    source_url: str = Field(..., description="Documentation page URL")
    section_title: Optional[str] = Field(None, description="Section heading")
    relevance: float = Field(
        default=1.0, ge=0.0, le=1.0, description="Relevance score"
    )


class MessageSchema(BaseSchema, UUIDMixin):
    """Message response schema."""

    conversation_id: UUID
    role: Literal["user", "assistant"]
    content: str
    citations: list[Citation] = []
    tokens_used: Optional[int] = None
    latency_ms: Optional[int] = None
    feedback: Optional[Literal["up", "down"]] = None
    created_at: datetime


class ConversationSchema(BaseSchema, UUIDMixin, TimestampMixin):
    """Conversation response schema."""

    session_id: UUID
    page_url: str
    page_title: Optional[str] = None
    selected_text: Optional[str] = None
    messages: list[MessageSchema] = []


class ChatRequest(BaseSchema):
    """Chat request schema."""

    message: str = Field(..., min_length=1, max_length=4000)
    conversation_id: Optional[UUID] = Field(
        None, description="Existing conversation ID for follow-ups"
    )
    page_url: str = Field(..., description="Current documentation page URL")
    page_title: Optional[str] = Field(None, description="Page title")
    selected_text: Optional[str] = Field(
        None, max_length=5000, description="User-selected text context"
    )


class ChatResponse(BaseSchema):
    """Chat response schema."""

    message: MessageSchema
    conversation_id: UUID


class StreamChunk(BaseModel):
    """Server-Sent Event chunk for streaming responses."""

    type: Literal["content", "citation", "done", "error"]
    content: Optional[str] = None
    citation: Optional[Citation] = None
    message_id: Optional[UUID] = None
    error: Optional[str] = None
