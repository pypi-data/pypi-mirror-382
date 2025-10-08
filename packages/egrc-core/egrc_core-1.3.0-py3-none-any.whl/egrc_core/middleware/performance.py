"""
Performance middleware for EGRC Platform.

This module provides middleware for performance monitoring
across all EGRC services.
"""

import time
from collections.abc import Callable

from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.types import ASGIApp

from ..logging.utils import get_logger


class PerformanceMiddleware(BaseHTTPMiddleware):
    """
    Middleware for performance monitoring.

    This middleware tracks request performance metrics and logs
    slow requests for performance analysis.
    """

    def __init__(
        self,
        app: ASGIApp,
        slow_request_threshold: float = 1.0,
        log_slow_requests: bool = True,
    ):
        """
        Initialize performance middleware.

        Args:
            app: ASGI application
            slow_request_threshold: Threshold for slow requests (seconds)
            log_slow_requests: Whether to log slow requests
        """
        super().__init__(app)
        self.slow_request_threshold = slow_request_threshold
        self.log_slow_requests = log_slow_requests
        self.logger = get_logger("egrc_core.performance")

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        """
        Process request with performance monitoring.

        Args:
            request: HTTP request
            call_next: Next middleware/handler

        Returns:
            HTTP response
        """
        start_time = time.time()

        try:
            response = await call_next(request)
            process_time = time.time() - start_time

            # Log slow requests
            if self.log_slow_requests and process_time >= self.slow_request_threshold:
                self.logger.warning(
                    "Slow request detected",
                    method=request.method,
                    url=str(request.url),
                    process_time=round(process_time, 4),
                    status_code=response.status_code,
                )

            # Add performance headers
            response.headers["X-Process-Time"] = str(round(process_time, 4))

            return response

        except Exception as e:
            process_time = time.time() - start_time

            # Log error performance
            self.logger.error(
                "Request processing failed",
                method=request.method,
                url=str(request.url),
                process_time=round(process_time, 4),
                error=str(e),
            )

            raise
