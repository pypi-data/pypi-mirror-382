"""
Error handler middleware for EGRC Platform.

This module provides middleware for centralized error handling
across all EGRC services.
"""

from collections.abc import Callable

from fastapi import HTTPException, Request, Response
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.types import ASGIApp

from ..exceptions.exceptions import EGRCException
from ..logging.utils import get_logger


class ErrorHandlerMiddleware(BaseHTTPMiddleware):
    """
    Middleware for centralized error handling.

    This middleware catches and handles all unhandled exceptions,
    providing consistent error responses across the application.
    """

    def __init__(self, app: ASGIApp):
        """
        Initialize error handler middleware.

        Args:
            app: ASGI application
        """
        super().__init__(app)
        self.logger = get_logger("egrc_core.error_handler")

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        """
        Process request with error handling.

        Args:
            request: HTTP request
            call_next: Next middleware/handler

        Returns:
            HTTP response
        """
        try:
            return await call_next(request)
        except HTTPException:
            # Re-raise HTTP exceptions as they are already handled
            raise
        except EGRCException as e:
            # Handle custom EGRC exceptions
            self.logger.error(
                "EGRC exception occurred",
                error=str(e),
                error_code=e.error_code,
                status_code=e.status_code,
                method=request.method,
                url=str(request.url),
                exc_info=True,
            )
            return JSONResponse(
                status_code=e.status_code,
                content={
                    "error": {
                        "message": e.message,
                        "code": e.error_code,
                        "details": e.details,
                    }
                },
            )
        except Exception as e:
            # Handle all other exceptions
            self.logger.error(
                "Unhandled exception occurred",
                error=str(e),
                error_type=type(e).__name__,
                method=request.method,
                url=str(request.url),
                exc_info=True,
            )
            return JSONResponse(
                status_code=500,
                content={
                    "error": {
                        "message": "Internal server error",
                        "code": "INTERNAL_ERROR",
                        "details": {},
                    }
                },
            )
