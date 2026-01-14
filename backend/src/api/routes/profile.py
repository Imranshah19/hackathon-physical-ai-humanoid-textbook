"""Profile API routes for user personalization.

Endpoints:
- GET /api/profile - Get current user's profile
- PATCH /api/profile - Update profile fields
- POST /api/profile/complete - Complete profile wizard
- POST /api/profile/skip - Skip profile completion
- GET /api/profile/options - Get available profile options
"""

from typing import Optional
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, Field
from sqlalchemy.ext.asyncio import AsyncSession

from src.api.middleware.auth import AuthState, require_auth
from src.db.postgres import get_db
from src.services.profile import (
    ProfileService,
    ProfileNotFoundError,
    ProfileValidationError,
)

router = APIRouter(prefix="/profile", tags=["profile"])


# Request/Response schemas
class ProfileResponse(BaseModel):
    """Profile response schema."""

    id: UUID
    user_id: UUID
    software_background: list[str]
    hardware_access: list[str]
    experience_level: Optional[str]
    profile_completed: bool
    completed_at: Optional[str]
    needs_reminder: bool
    created_at: str
    updated_at: str

    class Config:
        from_attributes = True


class ProfileCompleteRequest(BaseModel):
    """Request to complete profile wizard."""

    software_background: list[str] = Field(
        ..., min_length=1, description="At least one software background required"
    )
    hardware_access: list[str] = Field(
        ..., min_length=1, description="At least one hardware option required"
    )
    experience_level: str = Field(..., description="Experience level selection")


class ProfileUpdateRequest(BaseModel):
    """Request to update profile fields."""

    software_background: Optional[list[str]] = None
    hardware_access: Optional[list[str]] = None
    experience_level: Optional[str] = None


class ProfileSkipResponse(BaseModel):
    """Response after skipping profile."""

    success: bool
    next_reminder: Optional[str]


class ProfileOptionsResponse(BaseModel):
    """Available profile options for the wizard."""

    software_background: list[dict]
    hardware_access: list[dict]
    experience_level: list[dict]


# Helper to convert profile to response
def profile_to_response(profile, service: ProfileService) -> ProfileResponse:
    """Convert UserProfile model to response schema."""
    return ProfileResponse(
        id=profile.id,
        user_id=profile.user_id,
        software_background=profile.software_background or [],
        hardware_access=profile.hardware_access or [],
        experience_level=profile.experience_level,
        profile_completed=profile.profile_completed,
        completed_at=profile.completed_at.isoformat() if profile.completed_at else None,
        needs_reminder=service.needs_reminder(profile),
        created_at=profile.created_at.isoformat(),
        updated_at=profile.updated_at.isoformat(),
    )


@router.get("", response_model=ProfileResponse)
async def get_profile(
    auth: AuthState = Depends(require_auth),
    db: AsyncSession = Depends(get_db),
) -> ProfileResponse:
    """Get current user's profile.

    Returns the user's personalization profile including software background,
    hardware access, and experience level.
    """
    service = ProfileService(db)
    profile = await service.get_or_create_profile(auth.user.id)
    return profile_to_response(profile, service)


@router.patch("", response_model=ProfileResponse)
async def update_profile(
    request: ProfileUpdateRequest,
    auth: AuthState = Depends(require_auth),
    db: AsyncSession = Depends(get_db),
) -> ProfileResponse:
    """Update user profile fields.

    Allows partial updates to profile. Only provided fields are updated.
    """
    service = ProfileService(db)

    try:
        profile = await service.update_profile(
            user_id=auth.user.id,
            software_background=request.software_background,
            hardware_access=request.hardware_access,
            experience_level=request.experience_level,
        )
        return profile_to_response(profile, service)
    except ProfileNotFoundError:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Profile not found",
        )
    except ProfileValidationError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )


@router.post("/complete", response_model=ProfileResponse)
async def complete_profile(
    request: ProfileCompleteRequest,
    auth: AuthState = Depends(require_auth),
    db: AsyncSession = Depends(get_db),
) -> ProfileResponse:
    """Complete the profile wizard.

    Submits all profile fields at once during registration flow.
    All fields are required for completion.
    """
    service = ProfileService(db)

    try:
        profile = await service.complete_profile(
            user_id=auth.user.id,
            software_background=request.software_background,
            hardware_access=request.hardware_access,
            experience_level=request.experience_level,
        )
        return profile_to_response(profile, service)
    except ProfileValidationError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )


@router.post("/skip", response_model=ProfileSkipResponse)
async def skip_profile(
    auth: AuthState = Depends(require_auth),
    db: AsyncSession = Depends(get_db),
) -> ProfileSkipResponse:
    """Skip profile completion with reminder.

    Marks the profile as skipped and sets a reminder for later.
    User will be prompted again after 24 hours.
    """
    service = ProfileService(db)
    profile = await service.skip_profile(auth.user.id)
    next_reminder = service.get_next_reminder_time(profile)

    return ProfileSkipResponse(
        success=True,
        next_reminder=next_reminder.isoformat() if next_reminder else None,
    )


@router.get("/options", response_model=ProfileOptionsResponse)
async def get_profile_options() -> ProfileOptionsResponse:
    """Get available profile options.

    Returns all available options for software background, hardware access,
    and experience level fields. Used to populate the profile wizard UI.

    This endpoint does not require authentication.
    """
    options = ProfileService.get_profile_options()
    return ProfileOptionsResponse(**options)
