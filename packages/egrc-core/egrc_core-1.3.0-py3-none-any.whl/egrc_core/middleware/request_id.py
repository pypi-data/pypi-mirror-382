"""
Request ID middleware for EGRC Platform.

This module provides middleware for generating and managing request IDs
for better request tracing across all EGRC services.
"""

import uuid
from collections.abc import Callable

from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.types import ASGIApp

from ..constants.constants import Headers
from ..logging.filters import set_correlation_id, set_request_id


class RequestIDMiddleware(BaseHTTPMiddleware):
    """
    Middleware for generating and managing request IDs.

    This middleware generates unique request IDs and correlation IDs
    for better request tracing and debugging.
    """

    def __init__(self, app: ASGIApp):
        """
        Initialize request ID middleware.

        Args:
            app: ASGI application
        """
        super().__init__(app)

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        """
        Process request with request ID generation.

        Args:
            request: HTTP request
            call_next: Next middleware/handler

        Returns:
            HTTP response
        """
        # Generate or extract request ID
        request_id = request.headers.get(Headers.X_REQUEST_ID, str(uuid.uuid4()))

        # Generate or extract correlation ID
        correlation_id = request.headers.get(
            Headers.X_CORRELATION_ID, str(uuid.uuid4())
        )

        # Set context variables
        set_request_id(request_id)
        set_correlation_id(correlation_id)

        # Add to request state
        request.state.request_id = request_id
        request.state.correlation_id = correlation_id

        # Process request
        response = await call_next(request)

        # Add headers to response
        response.headers[Headers.X_REQUEST_ID] = request_id
        response.headers[Headers.X_CORRELATION_ID] = correlation_id

        return response
