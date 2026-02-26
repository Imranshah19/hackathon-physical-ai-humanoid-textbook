"""Profile service for user personalization management.

Source: FR-007, FR-008, FR-009, FR-010, FR-011, FR-012
"""

from datetime import datetime, timedelta, timezone
from typing import Optional
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.models.user_profile import UserProfile
from src.models.enums import (
    validate_software_background,
    validate_hardware_access,
    validate_experience_level,
    get_all_profile_options,
)


class ProfileServiceError(Exception):
    """Base exception for profile service errors."""

    pass


class ProfileNotFoundError(ProfileServiceError):
    """Profile not found for user."""

    pass


class ProfileValidationError(ProfileServiceError):
    """Profile data validation error."""

    pass


class ProfileService:
    """Service for managing user profiles and personalization settings."""

    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_profile(self, user_id: UUID) -> Optional[UserProfile]:
        """Get user profile by user ID.

        Args:
            user_id: The user's UUID

        Returns:
            UserProfile if found, None otherwise
        """
        result = await self.db.execute(
            select(UserProfile).where(UserProfile.user_id == user_id)
        )
        return result.scalar_one_or_none()

    async def get_or_create_profile(self, user_id: UUID) -> UserProfile:
        """Get existing profile or create a new empty one.

        Args:
            user_id: The user's UUID

        Returns:
            UserProfile (existing or newly created)
        """
        profile = await self.get_profile(user_id)
        if profile:
            return profile

        # Create new profile
        profile = UserProfile(user_id=user_id)
        self.db.add(profile)
        await self.db.commit()
        await self.db.refresh(profile)
        return profile

    async def complete_profile(
        self,
        user_id: UUID,
        software_background: list[str],
        hardware_access: list[str],
        experience_level: str,
    ) -> UserProfile:
        """Complete user profile with all required fields.

        Args:
            user_id: The user's UUID
            software_background: List of software/programming backgrounds
            hardware_access: List of hardware platforms accessible
            experience_level: User's experience level

        Returns:
            Updated UserProfile

        Raises:
            ProfileValidationError: If validation fails
        """
        # Validate inputs
        if not software_background:
            raise ProfileValidationError("At least one software background required")
        if not validate_software_background(software_background):
            raise ProfileValidationError("Invalid software background option")

        if not hardware_access:
            raise ProfileValidationError("At least one hardware option required")
        if not validate_hardware_access(hardware_access):
            raise ProfileValidationError("Invalid hardware access option")

        if not validate_experience_level(experience_level):
            raise ProfileValidationError("Invalid experience level")

        # Get or create profile
        profile = await self.get_or_create_profile(user_id)

        # Update fields
        profile.software_background = software_background
        profile.hardware_access = hardware_access
        profile.experience_level = experience_level
        profile.profile_completed = True
        profile.completed_at = datetime.now(timezone.utc)

        await self.db.commit()
        await self.db.refresh(profile)
        return profile

    async def update_profile(
        self,
        user_id: UUID,
        software_background: Optional[list[str]] = None,
        hardware_access: Optional[list[str]] = None,
        experience_level: Optional[str] = None,
    ) -> UserProfile:
        """Update user profile fields (FR-011).

        Args:
            user_id: The user's UUID
            software_background: Optional new software backgrounds
            hardware_access: Optional new hardware access
            experience_level: Optional new experience level

        Returns:
            Updated UserProfile

        Raises:
            ProfileNotFoundError: If profile doesn't exist
            ProfileValidationError: If validation fails
        """
        profile = await self.get_profile(user_id)
        if not profile:
            raise ProfileNotFoundError(f"Profile not found for user {user_id}")

        # Validate and update fields
        if software_background is not None:
            if not validate_software_background(software_background):
                raise ProfileValidationError("Invalid software background option")
            profile.software_background = software_background

        if hardware_access is not None:
            if not validate_hardware_access(hardware_access):
                raise ProfileValidationError("Invalid hardware access option")
            profile.hardware_access = hardware_access

        if experience_level is not None:
            if not validate_experience_level(experience_level):
                raise ProfileValidationError("Invalid experience level")
            profile.experience_level = experience_level

        # Check if profile is now complete
        if profile.is_complete() and not profile.profile_completed:
            profile.profile_completed = True
            profile.completed_at = datetime.now(timezone.utc)

        await self.db.commit()
        await self.db.refresh(profile)
        return profile

    async def skip_profile(self, user_id: UUID) -> UserProfile:
        """Mark profile as skipped with reminder timestamp (FR-010).

        Args:
            user_id: The user's UUID

        Returns:
            Updated UserProfile
        """
        profile = await self.get_or_create_profile(user_id)
        profile.last_reminded_at = datetime.now(timezone.utc)
        await self.db.commit()
        await self.db.refresh(profile)
        return profile

    def needs_reminder(self, profile: UserProfile) -> bool:
        """Check if user needs a profile completion reminder.

        Reminds once per day if profile is incomplete.
        """
        if profile.profile_completed:
            return False

        if not profile.last_reminded_at:
            return True

        # Remind once per day
        return datetime.now(timezone.utc) - profile.last_reminded_at > timedelta(days=1)

    def get_next_reminder_time(self, profile: UserProfile) -> Optional[datetime]:
        """Get next reminder time if applicable."""
        if profile.profile_completed:
            return None

        if not profile.last_reminded_at:
            return datetime.now(timezone.utc)

        return profile.last_reminded_at + timedelta(days=1)

    @staticmethod
    def get_profile_options() -> dict:
        """Get all available profile options for the UI."""
        return get_all_profile_options()
