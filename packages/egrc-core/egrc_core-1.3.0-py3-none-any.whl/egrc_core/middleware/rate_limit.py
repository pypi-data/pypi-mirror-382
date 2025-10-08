"""
Rate limiting middleware for EGRC Platform.

This module provides rate limiting middleware to prevent abuse
and ensure fair usage across all EGRC services.
"""

import time
from collections.abc import Callable
from typing import Any

from fastapi import HTTPException, Request, Response, status
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.types import ASGIApp

from ..constants.constants import SecurityConstants
from ..logging.utils import get_logger


class RateLimitMiddleware(BaseHTTPMiddleware):
    """
    Middleware for rate limiting requests.

    This middleware implements token bucket algorithm for rate limiting
    to prevent abuse and ensure fair usage.
    """

    def __init__(
        self,
        app: ASGIApp,
        requests_per_minute: int = SecurityConstants.DEFAULT_RATE_LIMIT,
        burst_size: int | None = None,
        key_func: Callable[[Request], str] | None = None,
        exclude_paths: list | None = None,
    ):
        """
        Initialize rate limit middleware.

        Args:
            app: ASGI application
            requests_per_minute: Maximum requests per minute
            burst_size: Maximum burst size (defaults to requests_per_minute)
            key_func: Function to generate rate limit key from request
            exclude_paths: List of paths to exclude from rate limiting
        """
        super().__init__(app)
        self.requests_per_minute = requests_per_minute
        self.burst_size = burst_size or requests_per_minute
        self.key_func = key_func or self._default_key_func
        self.exclude_paths = exclude_paths or [
            "/health",
            "/metrics",
            "/docs",
            "/openapi.json",
        ]
        self.logger = get_logger("egrc_core.rate_limit")

        # Token bucket storage: {key: {'tokens': int, 'last_refill': float}}
        self.buckets: dict[str, dict[str, Any]] = {}

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        """
        Process request with rate limiting.

        Args:
            request: HTTP request
            call_next: Next middleware/handler

        Returns:
            HTTP response
        """
        # Skip rate limiting for excluded paths
        if self._should_skip_rate_limit(request):
            return await call_next(request)

        # Generate rate limit key
        key = self.key_func(request)

        # Check rate limit
        if not self._check_rate_limit(key):
            self.logger.warning(
                "Rate limit exceeded",
                key=key,
                method=request.method,
                url=str(request.url),
                client_ip=request.client.host if request.client else None,
            )
            raise HTTPException(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                detail="Rate limit exceeded",
                headers={
                    "X-RateLimit-Limit": str(self.requests_per_minute),
                    "X-RateLimit-Remaining": "0",
                    "X-RateLimit-Reset": str(int(time.time() + 60)),
                    "Retry-After": "60",
                },
            )

        # Process request
        response = await call_next(request)

        # Add rate limit headers
        bucket = self.buckets.get(key, {})
        remaining = bucket.get("tokens", 0)

        response.headers["X-RateLimit-Limit"] = str(self.requests_per_minute)
        response.headers["X-RateLimit-Remaining"] = str(max(0, remaining - 1))
        response.headers["X-RateLimit-Reset"] = str(int(time.time() + 60))

        return response

    def _should_skip_rate_limit(self, request: Request) -> bool:
        """
        Check if rate limiting should be skipped for this request.

        Args:
            request: HTTP request

        Returns:
            True if rate limiting should be skipped
        """
        path = request.url.path
        return any(path.startswith(excluded) for excluded in self.exclude_paths)

    def _default_key_func(self, request: Request) -> str:
        """
        Default function to generate rate limit key.

        Args:
            request: HTTP request

        Returns:
            Rate limit key
        """
        # Use client IP as default key
        client_ip = request.client.host if request.client else "unknown"
        return f"rate_limit:{client_ip}"

    def _check_rate_limit(self, key: str) -> bool:
        """
        Check if request is within rate limit using token bucket algorithm.

        Args:
            key: Rate limit key

        Returns:
            True if request is allowed
        """
        current_time = time.time()

        # Get or create bucket
        if key not in self.buckets:
            self.buckets[key] = {"tokens": self.burst_size, "last_refill": current_time}

        bucket = self.buckets[key]

        # Calculate tokens to add based on time elapsed
        time_elapsed = current_time - bucket["last_refill"]
        tokens_to_add = (time_elapsed / 60.0) * self.requests_per_minute

        # Refill tokens
        bucket["tokens"] = min(self.burst_size, bucket["tokens"] + tokens_to_add)
        bucket["last_refill"] = current_time

        # Check if we have enough tokens
        if bucket["tokens"] >= 1:
            bucket["tokens"] -= 1
            return True

        return False

    def _cleanup_old_buckets(self) -> None:
        """Clean up old buckets to prevent memory leaks."""
        current_time = time.time()
        cutoff_time = current_time - 3600  # Remove buckets older than 1 hour

        keys_to_remove = []
        for key, bucket in self.buckets.items():
            if bucket["last_refill"] < cutoff_time:
                keys_to_remove.append(key)

        for key in keys_to_remove:
            del self.buckets[key]
