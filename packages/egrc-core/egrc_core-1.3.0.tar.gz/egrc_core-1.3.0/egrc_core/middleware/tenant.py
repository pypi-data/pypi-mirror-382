"""
Tenant middleware for EGRC Platform.

This module provides middleware for multi-tenant support
across all EGRC services.
"""

from collections.abc import Callable

from fastapi import HTTPException, Request, Response, status
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.types import ASGIApp

from ..constants.constants import Headers
from ..logging.filters import set_tenant_id, set_user_id


class TenantMiddleware(BaseHTTPMiddleware):
    """
    Middleware for multi-tenant support.

    This middleware extracts tenant and user information from headers
    and sets them in the request context.
    """

    def __init__(
        self,
        app: ASGIApp,
        require_tenant: bool = True,
        exclude_paths: list | None = None,
    ):
        """
        Initialize tenant middleware.

        Args:
            app: ASGI application
            require_tenant: Whether tenant ID is required
            exclude_paths: List of paths to exclude from tenant validation
        """
        super().__init__(app)
        self.require_tenant = require_tenant
        self.exclude_paths = exclude_paths or [
            "/health",
            "/metrics",
            "/docs",
            "/openapi.json",
            "/auth/login",
        ]

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        """
        Process request with tenant context.

        Args:
            request: HTTP request
            call_next: Next middleware/handler

        Returns:
            HTTP response
        """
        # Skip tenant validation for excluded paths
        if self._should_skip_tenant_validation(request):
            return await call_next(request)

        # Extract tenant ID from headers
        tenant_id = request.headers.get(Headers.X_TENANT_ID)
        user_id = request.headers.get(Headers.X_USER_ID)

        # Validate tenant ID if required
        if self.require_tenant and not tenant_id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, detail="Tenant ID is required"
            )

        # Set context variables
        if tenant_id:
            set_tenant_id(tenant_id)
            request.state.tenant_id = tenant_id

        if user_id:
            set_user_id(user_id)
            request.state.user_id = user_id

        return await call_next(request)

    def _should_skip_tenant_validation(self, request: Request) -> bool:
        """
        Check if tenant validation should be skipped for this request.

        Args:
            request: HTTP request

        Returns:
            True if tenant validation should be skipped
        """
        path = request.url.path
        return any(path.startswith(excluded) for excluded in self.exclude_paths)
