from ..logging.utils import log_request


"""
Tenant resolution middleware for EGRC Core Service.

This middleware extracts tenant information from requests and makes it
available to route handlers.
"""

import time

from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware

from ..logging.utils import get_logger


logger = get_logger(__name__)


class TenantMiddleware(BaseHTTPMiddleware):
    """Middleware for tenant resolution."""

    async def dispatch(self, request: Request, call_next) -> Response:
        """Process request and extract tenant information.

        Args:
            request: Incoming request
            call_next: Next middleware/handler

        Returns:
            Response
        """
        start_time = time.time()

        # Extract tenant information from various sources
        tenant_id = self._extract_tenant_id(request)
        request.state.tenant_id = tenant_id

        # Process request
        response = await call_next(request)

        # Calculate duration
        duration = time.time() - start_time

        # Log request
        log_request(
            method=request.method,
            url=str(request.url),
            status_code=response.status_code,
            duration=duration,
            tenant_id=tenant_id,
            user_agent=request.headers.get("user-agent"),
            ip_address=request.client.host if request.client else None,
        )

        return response

    def _extract_tenant_id(self, request: Request) -> str | None:
        """Extract tenant ID from request.

        Args:
            request: HTTP request

        Returns:
            Tenant ID or None
        """
        # 1. Check X-Tenant-ID header
        tenant_id = request.headers.get("X-Tenant-ID")
        if tenant_id:
            return tenant_id

        # 2. Check subdomain
        host = request.headers.get("host", "")
        if "." in host:
            subdomain = host.split(".")[0]
            if subdomain and subdomain != "www":
                return subdomain

        # 3. Check path parameter
        if hasattr(request, "path_params") and "tenant_id" in request.path_params:
            return request.path_params["tenant_id"]

        # 4. Check query parameter
        tenant_id = request.query_params.get("tenant_id")
        if tenant_id:
            return tenant_id

        # 5. Check JWT token (if available)
        # This would be implemented after authentication middleware

        return None
