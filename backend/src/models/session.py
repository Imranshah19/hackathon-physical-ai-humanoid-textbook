"""
UserSession SQLAlchemy model for anonymous session tracking.
"""

from datetime import datetime
from typing import TYPE_CHECKING
from uuid import UUID

from sqlalchemy import DateTime, String, func
from sqlalchemy.dialects.postgresql import JSONB, UUID as PG_UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.db.postgres import Base

if TYPE_CHECKING:
    from src.models.conversation import Conversation


class UserSession(Base):
    """
    Tracks anonymous user sessions for history and preferences.

    Attributes:
        id: Unique session identifier (UUID).
        session_token: Browser cookie token (64 char hex).
        created_at: Session creation timestamp.
        last_active_at: Last activity timestamp.
        preferences: User preferences (theme, language, etc.).
    """

    __tablename__ = "user_sessions"

    id: Mapped[UUID] = mapped_column(
        PG_UUID(as_uuid=True),
        primary_key=True,
        server_default=func.uuid_generate_v4(),
    )
    session_token: Mapped[str] = mapped_column(
        String(64),
        unique=True,
        nullable=False,
        index=True,
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
    )
    last_active_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
        index=True,
    )
    preferences: Mapped[dict] = mapped_column(
        JSONB,
        nullable=False,
        server_default="{}",
    )

    # Relationships
    conversations: Mapped[list["Conversation"]] = relationship(
        "Conversation",
        back_populates="session",
        cascade="all, delete-orphan",
        lazy="selectin",
    )

    def __repr__(self) -> str:
        return f"<UserSession {self.id} token={self.session_token[:8]}...>"
