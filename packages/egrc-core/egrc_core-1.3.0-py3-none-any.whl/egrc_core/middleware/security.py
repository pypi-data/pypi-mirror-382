"""
Security middleware for EGRC Platform.

This module provides middleware for security-related functionality
across all EGRC services.
"""

from collections.abc import Callable

from fastapi import HTTPException, Request, Response, status
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.types import ASGIApp

from ..logging.utils import get_logger


class SecurityMiddleware(BaseHTTPMiddleware):
    """
    Middleware for security-related functionality.

    This middleware provides security headers, request validation,
    and other security measures.
    """

    def __init__(
        self,
        app: ASGIApp,
        add_security_headers: bool = True,
        max_request_size: int = 10 * 1024 * 1024,  # 10MB
        allowed_hosts: list[str] | None = None,
    ):
        """
        Initialize security middleware.

        Args:
            app: ASGI application
            add_security_headers: Whether to add security headers
            max_request_size: Maximum request size in bytes
            allowed_hosts: List of allowed hosts
        """
        super().__init__(app)
        self.add_security_headers = add_security_headers
        self.max_request_size = max_request_size
        self.allowed_hosts = allowed_hosts
        self.logger = get_logger("egrc_core.security")

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        """
        Process request with security measures.

        Args:
            request: HTTP request
            call_next: Next middleware/handler

        Returns:
            HTTP response
        """
        # Check request size
        content_length = request.headers.get("content-length")
        if content_length and int(content_length) > self.max_request_size:
            raise HTTPException(
                status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
                detail="Request entity too large",
            )

        # Check allowed hosts
        if self.allowed_hosts:
            host = request.headers.get("host")
            if host and host not in self.allowed_hosts:
                self.logger.warning(
                    "Request from disallowed host",
                    host=host,
                    method=request.method,
                    url=str(request.url),
                )
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid host"
                )

        # Process request
        response = await call_next(request)

        # Add security headers
        if self.add_security_headers:
            self._add_security_headers(response)

        return response

    def _add_security_headers(self, response: Response) -> None:
        """
        Add security headers to response.

        Args:
            response: HTTP response
        """
        # Prevent clickjacking
        response.headers["X-Frame-Options"] = "DENY"

        # Prevent MIME type sniffing
        response.headers["X-Content-Type-Options"] = "nosniff"

        # Enable XSS protection
        response.headers["X-XSS-Protection"] = "1; mode=block"

        # Strict transport security
        response.headers["Strict-Transport-Security"] = (
            "max-age=31536000; includeSubDomains"
        )

        # Content security policy
        response.headers["Content-Security-Policy"] = "default-src 'self'"

        # Referrer policy
        response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
