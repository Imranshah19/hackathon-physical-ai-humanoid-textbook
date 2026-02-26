"""
Token bucket rate limiting middleware per session.
"""

import time
from collections import defaultdict
from dataclasses import dataclass, field
from typing import Callable

from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import JSONResponse

from src.config import get_settings


@dataclass
class TokenBucket:
    """Token bucket for rate limiting."""

    capacity: int
    tokens: float = field(default=0.0)
    last_update: float = field(default_factory=time.time)
    refill_rate: float = field(default=0.5)  # tokens per second

    def __post_init__(self) -> None:
        self.tokens = float(self.capacity)

    def consume(self, tokens: int = 1) -> bool:
        """
        Attempt to consume tokens from the bucket.

        Args:
            tokens: Number of tokens to consume.

        Returns:
            True if tokens were consumed, False if rate limited.
        """
        now = time.time()
        elapsed = now - self.last_update
        self.last_update = now

        # Refill tokens based on elapsed time
        self.tokens = min(self.capacity, self.tokens + elapsed * self.refill_rate)

        if self.tokens >= tokens:
            self.tokens -= tokens
            return True
        return False

    @property
    def remaining(self) -> int:
        """Get remaining tokens."""
        return int(self.tokens)

    @property
    def reset_time(self) -> float:
        """Get time until bucket is full again."""
        tokens_needed = self.capacity - self.tokens
        return tokens_needed / self.refill_rate if self.refill_rate > 0 else 0


class RateLimitMiddleware(BaseHTTPMiddleware):
    """
    Rate limiting middleware using token bucket algorithm.

    Limits requests per session token to prevent abuse.
    """

    def __init__(self, app: Callable, **kwargs) -> None:
        super().__init__(app)
        settings = get_settings()
        self.capacity = settings.rate_limit_requests
        self.window_seconds = settings.rate_limit_window_seconds
        self.refill_rate = self.capacity / self.window_seconds
        self._buckets: dict[str, TokenBucket] = defaultdict(
            lambda: TokenBucket(
                capacity=self.capacity,
                refill_rate=self.refill_rate,
            )
        )

    def _get_session_key(self, request: Request) -> str:
        """
        Extract session key from request.

        Falls back to IP address if no session token.
        """
        session_token = request.headers.get("X-Session-Token")
        if session_token:
            return f"session:{session_token}"

        # Fallback to IP
        forwarded = request.headers.get("X-Forwarded-For")
        if forwarded:
            ip = forwarded.split(",")[0].strip()
        else:
            ip = request.client.host if request.client else "unknown"
        return f"ip:{ip}"

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        """
        Process request with rate limiting.

        Args:
            request: Incoming request.
            call_next: Next middleware/handler.

        Returns:
            Response with rate limit headers.
        """
        # Skip rate limiting for health checks
        if request.url.path.endswith("/health"):
            return await call_next(request)

        key = self._get_session_key(request)
        bucket = self._buckets[key]

        if not bucket.consume():
            return JSONResponse(
                status_code=429,
                content={
                    "error": "Rate limit exceeded",
                    "detail": "Too many requests. Please try again later.",
                    "retry_after": int(bucket.reset_time),
                },
                headers={
                    "X-RateLimit-Limit": str(self.capacity),
                    "X-RateLimit-Remaining": "0",
                    "X-RateLimit-Reset": str(int(time.time() + bucket.reset_time)),
                    "Retry-After": str(int(bucket.reset_time)),
                },
            )

        response = await call_next(request)

        # Add rate limit headers
        response.headers["X-RateLimit-Limit"] = str(self.capacity)
        response.headers["X-RateLimit-Remaining"] = str(bucket.remaining)
        response.headers["X-RateLimit-Reset"] = str(int(time.time() + bucket.reset_time))

        return response
