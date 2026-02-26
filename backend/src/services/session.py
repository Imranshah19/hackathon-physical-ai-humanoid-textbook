"""
Session management service for anonymous user sessions.
"""

import secrets
from datetime import datetime, timedelta
from typing import Optional
from uuid import UUID

from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession

from src.config import get_settings
from src.models.session import UserSession


class SessionService:
    """
    Service for managing user sessions.

    Handles session creation, retrieval, and updates.
    """

    def __init__(self, db: AsyncSession) -> None:
        """
        Initialize session service.

        Args:
            db: Async database session.
        """
        self.db = db
        self.settings = get_settings()

    def _generate_token(self) -> str:
        """Generate a secure session token."""
        return secrets.token_hex(self.settings.session_token_length // 2)

    async def create_session(
        self,
        preferences: Optional[dict] = None,
    ) -> UserSession:
        """
        Create a new user session.

        Args:
            preferences: Initial user preferences.

        Returns:
            Created UserSession instance.
        """
        session = UserSession(
            session_token=self._generate_token(),
            preferences=preferences or {},
        )
        self.db.add(session)
        await self.db.flush()
        return session

    async def get_session_by_token(
        self,
        token: str,
    ) -> Optional[UserSession]:
        """
        Get a session by its token.

        Args:
            token: Session token from cookie/header.

        Returns:
            UserSession if found and not expired, None otherwise.
        """
        expiry_threshold = datetime.utcnow() - timedelta(
            days=self.settings.session_expiry_days
        )

        result = await self.db.execute(
            select(UserSession).where(
                UserSession.session_token == token,
                UserSession.last_active_at >= expiry_threshold,
            )
        )
        return result.scalar_one_or_none()

    async def get_session_by_id(
        self,
        session_id: UUID,
    ) -> Optional[UserSession]:
        """
        Get a session by its ID.

        Args:
            session_id: Session UUID.

        Returns:
            UserSession if found, None otherwise.
        """
        result = await self.db.execute(
            select(UserSession).where(UserSession.id == session_id)
        )
        return result.scalar_one_or_none()

    async def update_activity(
        self,
        session: UserSession,
    ) -> UserSession:
        """
        Update session last activity timestamp.

        Args:
            session: Session to update.

        Returns:
            Updated UserSession.
        """
        session.last_active_at = datetime.utcnow()
        await self.db.flush()
        return session

    async def update_preferences(
        self,
        session: UserSession,
        preferences: dict,
    ) -> UserSession:
        """
        Update session preferences.

        Args:
            session: Session to update.
            preferences: New preferences (merged with existing).

        Returns:
            Updated UserSession.
        """
        current_prefs = session.preferences or {}
        current_prefs.update(preferences)
        session.preferences = current_prefs
        session.last_active_at = datetime.utcnow()
        await self.db.flush()
        return session

    async def get_or_create_session(
        self,
        token: Optional[str] = None,
    ) -> tuple[UserSession, bool]:
        """
        Get existing session or create a new one.

        Args:
            token: Optional existing session token.

        Returns:
            Tuple of (session, created) where created is True if new.
        """
        if token:
            session = await self.get_session_by_token(token)
            if session:
                await self.update_activity(session)
                return session, False

        # Create new session
        session = await self.create_session()
        return session, True

    async def cleanup_expired_sessions(self) -> int:
        """
        Remove expired sessions from database.

        Returns:
            Number of sessions deleted.
        """
        expiry_threshold = datetime.utcnow() - timedelta(
            days=self.settings.session_expiry_days
        )

        # Note: This should be run as a background task, not on every request
        from sqlalchemy import delete

        result = await self.db.execute(
            delete(UserSession).where(UserSession.last_active_at < expiry_threshold)
        )
        return result.rowcount
