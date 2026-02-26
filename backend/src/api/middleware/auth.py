"""Authentication middleware for validating better-auth sessions.

Validates session tokens from cookies or Authorization header
and attaches user info to request state.
"""

from typing import Optional
from uuid import UUID

import httpx
from fastapi import HTTPException, Request, status
from pydantic import BaseModel


class AuthUser(BaseModel):
    """Authenticated user info from better-auth session."""

    id: UUID
    email: str
    email_verified: bool
    name: Optional[str] = None
    image: Optional[str] = None


class AuthSession(BaseModel):
    """Session info from better-auth."""

    id: UUID
    user_id: UUID
    expires_at: str


class AuthState(BaseModel):
    """Combined auth state attached to request."""

    user: AuthUser
    session: AuthSession


# Auth service URL (configured via environment)
AUTH_SERVICE_URL = "http://localhost:3001"


async def get_session_from_auth_service(
    session_token: str,
) -> Optional[AuthState]:
    """Validate session token with auth service.

    Args:
        session_token: The session token from cookie or header

    Returns:
        AuthState if valid session, None otherwise
    """
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{AUTH_SERVICE_URL}/api/auth/session",
                cookies={"textbook-auth.session_token": session_token},
                timeout=5.0,
            )

            if response.status_code != 200:
                return None

            data = response.json()
            if not data.get("user") or not data.get("session"):
                return None

            return AuthState(
                user=AuthUser(**data["user"]),
                session=AuthSession(**data["session"]),
            )
    except Exception:
        return None


def get_session_token(request: Request) -> Optional[str]:
    """Extract session token from request.

    Checks cookies first, then Authorization header.
    """
    # Check cookie
    token = request.cookies.get("textbook-auth.session_token")
    if token:
        return token

    # Check Authorization header (Bearer token)
    auth_header = request.headers.get("Authorization")
    if auth_header and auth_header.startswith("Bearer "):
        return auth_header[7:]

    return None


async def require_auth(request: Request) -> AuthState:
    """Dependency to require authentication.

    Use as FastAPI dependency:
        @router.get("/protected")
        async def protected_route(auth: AuthState = Depends(require_auth)):
            return {"user": auth.user.email}

    Raises:
        HTTPException: 401 if not authenticated
    """
    token = get_session_token(request)
    if not token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authenticated",
            headers={"WWW-Authenticate": "Bearer"},
        )

    auth_state = await get_session_from_auth_service(token)
    if not auth_state:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired session",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # Attach to request state for access in route handlers
    request.state.auth = auth_state
    return auth_state


async def optional_auth(request: Request) -> Optional[AuthState]:
    """Dependency for optional authentication.

    Returns None if not authenticated instead of raising exception.
    """
    token = get_session_token(request)
    if not token:
        return None

    auth_state = await get_session_from_auth_service(token)
    if auth_state:
        request.state.auth = auth_state
    return auth_state


def get_current_user_id(request: Request) -> Optional[UUID]:
    """Get current user ID from request state if authenticated."""
    auth_state: Optional[AuthState] = getattr(request.state, "auth", None)
    return auth_state.user.id if auth_state else None


async def get_current_user(request: Request) -> dict:
    """Dependency to get current authenticated user as dict.

    Use as FastAPI dependency:
        @router.get("/me")
        async def get_me(user: dict = Depends(get_current_user)):
            return user

    Raises:
        HTTPException: 401 if not authenticated
    """
    auth_state = await require_auth(request)
    return {
        "id": str(auth_state.user.id),
        "email": auth_state.user.email,
        "name": auth_state.user.name,
        "image": auth_state.user.image,
        "emailVerified": auth_state.user.email_verified,
    }


async def get_optional_user(request: Request) -> Optional[dict]:
    """Dependency to get current user if authenticated, None otherwise.

    Use as FastAPI dependency:
        @router.get("/content")
        async def get_content(user: Optional[dict] = Depends(get_optional_user)):
            if user:
                # personalized content
            else:
                # anonymous content
    """
    auth_state = await optional_auth(request)
    if not auth_state:
        return None

    return {
        "id": str(auth_state.user.id),
        "email": auth_state.user.email,
        "name": auth_state.user.name,
        "image": auth_state.user.image,
        "emailVerified": auth_state.user.email_verified,
    }
