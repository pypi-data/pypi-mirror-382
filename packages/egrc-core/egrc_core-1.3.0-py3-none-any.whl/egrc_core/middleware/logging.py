"""
Logging middleware for EGRC Core Service.

This middleware provides request/response logging and performance monitoring.
"""

import time

from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware

from ..logging.utils import get_logger


logger = get_logger(__name__)


class LoggingMiddleware(BaseHTTPMiddleware):
    """Middleware for request/response logging."""

    def __init__(self, app, log_requests: bool = True, log_responses: bool = False):
        """Initialize logging middleware.

        Args:
            app: FastAPI application
            log_requests: Whether to log requests
            log_responses: Whether to log responses
        """
        super().__init__(app)
        self.log_requests = log_requests
        self.log_responses = log_responses

    async def dispatch(self, request: Request, call_next) -> Response:
        """Process request and log details.

        Args:
            request: Incoming request
            call_next: Next middleware/handler

        Returns:
            Response
        """
        start_time = time.time()

        # Log request
        if self.log_requests:
            await self._log_request(request)

        # Process request
        response = await call_next(request)

        # Calculate duration
        duration = time.time() - start_time

        # Log response
        if self.log_responses:
            await self._log_response(request, response, duration)

        # Add performance headers
        response.headers["X-Process-Time"] = str(duration)

        return response

    async def _log_request(self, request: Request) -> None:
        """Log incoming request details.

        Args:
            request: HTTP request
        """
        try:
            # Extract request information
            request_info = {
                "method": request.method,
                "url": str(request.url),
                "path": request.url.path,
                "query_params": dict(request.query_params),
                "headers": self._filter_headers(dict(request.headers)),
                "client_ip": request.client.host if request.client else None,
                "user_agent": request.headers.get("user-agent"),
                "tenant_id": getattr(request.state, "tenant_id", None),
                "user_id": (
                    getattr(request.state, "user", {}).get("id")
                    if hasattr(request.state, "user")
                    else None
                ),
            }

            # Log request body for non-GET requests (be careful with sensitive data)
            if request.method in ["POST", "PUT", "PATCH"]:
                try:
                    body = await request.body()
                    if body:
                        # Only log if not too large and doesn't contain sensitive data
                        if len(body) < 10000 and not self._contains_sensitive_data(
                            body
                        ):
                            request_info["body_size"] = len(body)
                        else:
                            request_info["body_size"] = len(body)
                            request_info["body_truncated"] = True
                except Exception:
                    request_info["body_error"] = "Failed to read request body"

            logger.info("Incoming request", **request_info)

        except Exception as e:
            logger.error("Failed to log request", error=str(e))

    async def _log_response(
        self, request: Request, response: Response, duration: float
    ) -> None:
        """Log response details.

        Args:
            request: HTTP request
            response: HTTP response
            duration: Request duration in seconds
        """
        try:
            response_info = {
                "method": request.method,
                "url": str(request.url),
                "status_code": response.status_code,
                "duration": duration,
                "response_size": response.headers.get("content-length"),
                "tenant_id": getattr(request.state, "tenant_id", None),
                "user_id": (
                    getattr(request.state, "user", {}).get("id")
                    if hasattr(request.state, "user")
                    else None
                ),
            }

            # Log response headers (filtered)
            response_info["response_headers"] = self._filter_headers(
                dict(response.headers)
            )

            # Log based on status code
            if response.status_code >= 500:
                logger.error("Request completed with server error", **response_info)
            elif response.status_code >= 400:
                logger.warning("Request completed with client error", **response_info)
            else:
                logger.info("Request completed successfully", **response_info)

        except Exception as e:
            logger.error("Failed to log response", error=str(e))

    def _filter_headers(self, headers: dict[str, str]) -> dict[str, str]:
        """Filter sensitive headers from logging.

        Args:
            headers: Request/response headers

        Returns:
            Filtered headers
        """
        sensitive_headers = {
            "authorization",
            "cookie",
            "x-api-key",
            "x-auth-token",
            "x-access-token",
            "x-refresh-token",
        }

        filtered_headers = {}
        for key, value in headers.items():
            if key.lower() in sensitive_headers:
                filtered_headers[key] = "[REDACTED]"
            else:
                filtered_headers[key] = value

        return filtered_headers

    def _contains_sensitive_data(self, body: bytes) -> bool:
        """Check if request body contains sensitive data.

        Args:
            body: Request body bytes

        Returns:
            True if body contains sensitive data
        """
        try:
            body_str = body.decode("utf-8").lower()
            sensitive_keywords = [
                "password",
                "token",
                "secret",
                "key",
                "credential",
                "auth",
                "login",
            ]

            return any(keyword in body_str for keyword in sensitive_keywords)
        except Exception:
            return True  # Assume sensitive if we can't decode
