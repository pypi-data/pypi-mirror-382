"""
Logging middleware for EGRC Platform.

This module provides middleware for automatic request/response logging
and context management across all EGRC services.
"""

import time
import uuid
from collections.abc import Callable

from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.types import ASGIApp

from .filters import (
    get_request_id,
    get_tenant_id,
    get_user_id,
    set_correlation_id,
    set_request_id,
    set_tenant_id,
    set_user_id,
)
from .utils import get_logger


class LoggingMiddleware(BaseHTTPMiddleware):
    """
    Middleware for automatic request/response logging.

    This middleware automatically logs HTTP requests and responses
    with context information for better tracing and debugging.
    """

    def __init__(
        self,
        app: ASGIApp,
        log_requests: bool = True,
        log_responses: bool = True,
        log_body: bool = False,
        max_body_size: int = 1024,
        exclude_paths: list | None = None,
        include_headers: bool = True,
        include_query_params: bool = True,
    ):
        """
        Initialize logging middleware.

        Args:
            app: ASGI application
            log_requests: Whether to log requests
            log_responses: Whether to log responses
            log_body: Whether to log request/response bodies
            max_body_size: Maximum body size to log
            exclude_paths: List of paths to exclude from logging
            include_headers: Whether to include headers in logs
            include_query_params: Whether to include query parameters
        """
        super().__init__(app)
        self.log_requests = log_requests
        self.log_responses = log_responses
        self.log_body = log_body
        self.max_body_size = max_body_size
        self.exclude_paths = exclude_paths or [
            "/health",
            "/metrics",
            "/docs",
            "/openapi.json",
        ]
        self.include_headers = include_headers
        self.include_query_params = include_query_params
        self.logger = get_logger("egrc_core.middleware")

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        """
        Process request and response with logging.

        Args:
            request: HTTP request
            call_next: Next middleware/handler

        Returns:
            HTTP response
        """
        # Skip logging for excluded paths
        if self._should_skip_logging(request):
            return await call_next(request)

        # Generate request ID and set context
        request_id = str(uuid.uuid4())
        set_request_id(request_id)

        # Extract context from headers
        tenant_id = request.headers.get("X-Tenant-ID")
        user_id = request.headers.get("X-User-ID")
        correlation_id = request.headers.get("X-Correlation-ID", str(uuid.uuid4()))

        if tenant_id:
            set_tenant_id(tenant_id)
        if user_id:
            set_user_id(user_id)
        set_correlation_id(correlation_id)

        # Log request
        if self.log_requests:
            await self._log_request(request, request_id)

        # Process request
        start_time = time.time()
        try:
            response = await call_next(request)
            process_time = time.time() - start_time

            # Log response
            if self.log_responses:
                await self._log_response(request, response, process_time, request_id)

            return response

        except Exception as e:
            process_time = time.time() - start_time

            # Log error
            self.logger.error(
                "Request processing failed",
                method=request.method,
                url=str(request.url),
                request_id=request_id,
                process_time=process_time,
                error=str(e),
                exc_info=True,
            )

            raise

    def _should_skip_logging(self, request: Request) -> bool:
        """
        Check if logging should be skipped for this request.

        Args:
            request: HTTP request

        Returns:
            True if logging should be skipped
        """
        path = request.url.path
        return any(path.startswith(excluded) for excluded in self.exclude_paths)

    async def _log_request(self, request: Request, request_id: str) -> None:
        """
        Log HTTP request.

        Args:
            request: HTTP request
            request_id: Request ID
        """
        log_data = {
            "method": request.method,
            "url": str(request.url),
            "path": request.url.path,
            "request_id": request_id,
            "client_ip": request.client.host if request.client else None,
            "user_agent": request.headers.get("User-Agent"),
        }

        # Add query parameters
        if self.include_query_params and request.query_params:
            log_data["query_params"] = dict(request.query_params)

        # Add headers
        if self.include_headers:
            log_data["headers"] = dict(request.headers)

        # Add body (if enabled and not too large)
        if self.log_body and request.method in ["POST", "PUT", "PATCH"]:
            try:
                body = await request.body()
                if len(body) <= self.max_body_size:
                    log_data["body"] = body.decode("utf-8")
                else:
                    log_data["body"] = f"<body too large: {len(body)} bytes>"
            except Exception:
                log_data["body"] = "<body read error>"

        self.logger.info("HTTP Request", **log_data)

    async def _log_response(
        self, request: Request, response: Response, process_time: float, request_id: str
    ) -> None:
        """
        Log HTTP response.

        Args:
            request: HTTP request
            response: HTTP response
            process_time: Request processing time
            request_id: Request ID
        """
        log_data = {
            "method": request.method,
            "url": str(request.url),
            "path": request.url.path,
            "status_code": response.status_code,
            "process_time": round(process_time, 4),
            "request_id": request_id,
        }

        # Add response headers
        if self.include_headers:
            log_data["response_headers"] = dict(response.headers)

        # Log level based on status code
        if response.status_code >= 500:
            self.logger.error("HTTP Response", **log_data)
        elif response.status_code >= 400:
            self.logger.warning("HTTP Response", **log_data)
        else:
            self.logger.info("HTTP Response", **log_data)


class PerformanceMiddleware(BaseHTTPMiddleware):
    """
    Middleware for performance monitoring and logging.

    This middleware tracks request performance metrics and logs
    slow requests for performance analysis.
    """

    def __init__(
        self,
        app: ASGIApp,
        slow_request_threshold: float = 1.0,
        log_slow_requests: bool = True,
        log_all_requests: bool = False,
    ):
        """
        Initialize performance middleware.

        Args:
            app: ASGI application
            slow_request_threshold: Threshold for slow requests (seconds)
            log_slow_requests: Whether to log slow requests
            log_all_requests: Whether to log all requests
        """
        super().__init__(app)
        self.slow_request_threshold = slow_request_threshold
        self.log_slow_requests = log_slow_requests
        self.log_all_requests = log_all_requests
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

            # Log performance metrics
            self._log_performance(request, response, process_time)

            return response

        except Exception as e:
            process_time = time.time() - start_time

            # Log error performance
            self._log_performance(request, None, process_time, error=str(e))

            raise

    def _log_performance(
        self,
        request: Request,
        response: Response | None,
        process_time: float,
        error: str | None = None,
    ) -> None:
        """
        Log performance metrics.

        Args:
            request: HTTP request
            response: HTTP response (if successful)
            process_time: Request processing time
            error: Error message (if failed)
        """
        should_log = self.log_all_requests or (
            self.log_slow_requests and process_time >= self.slow_request_threshold
        )

        if not should_log:
            return

        log_data = {
            "method": request.method,
            "url": str(request.url),
            "path": request.url.path,
            "process_time": round(process_time, 4),
            "request_id": get_request_id(),
            "tenant_id": get_tenant_id(),
            "user_id": get_user_id(),
        }

        if response:
            log_data["status_code"] = response.status_code

        if error:
            log_data["error"] = error

        if process_time >= self.slow_request_threshold:
            self.logger.warning("Slow request detected", **log_data)
        else:
            self.logger.info("Request performance", **log_data)


class SecurityMiddleware(BaseHTTPMiddleware):
    """
    Middleware for security logging and monitoring.

    This middleware logs security-related events and potential
    security threats for monitoring and alerting.
    """

    def __init__(
        self,
        app: ASGIApp,
        log_auth_attempts: bool = True,
        log_suspicious_activity: bool = True,
        rate_limit_threshold: int = 100,
    ):
        """
        Initialize security middleware.

        Args:
            app: ASGI application
            log_auth_attempts: Whether to log authentication attempts
            log_suspicious_activity: Whether to log suspicious activity
            rate_limit_threshold: Rate limit threshold for suspicious activity
        """
        super().__init__(app)
        self.log_auth_attempts = log_auth_attempts
        self.log_suspicious_activity = log_suspicious_activity
        self.rate_limit_threshold = rate_limit_threshold
        self.logger = get_logger("egrc_core.security")
        self.request_counts = {}  # Simple in-memory rate limiting

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        """
        Process request with security monitoring.

        Args:
            request: HTTP request
            call_next: Next middleware/handler

        Returns:
            HTTP response
        """
        client_ip = request.client.host if request.client else "unknown"

        # Track request counts for rate limiting
        current_time = time.time()
        if client_ip not in self.request_counts:
            self.request_counts[client_ip] = []

        # Clean old requests (older than 1 minute)
        self.request_counts[client_ip] = [
            req_time
            for req_time in self.request_counts[client_ip]
            if current_time - req_time < 60
        ]

        # Add current request
        self.request_counts[client_ip].append(current_time)

        # Check for suspicious activity
        if len(self.request_counts[client_ip]) > self.rate_limit_threshold:
            self.logger.warning(
                "Rate limit exceeded",
                client_ip=client_ip,
                request_count=len(self.request_counts[client_ip]),
                method=request.method,
                url=str(request.url),
                user_agent=request.headers.get("User-Agent"),
            )

        # Log authentication attempts
        if self.log_auth_attempts and self._is_auth_endpoint(request):
            self.logger.info(
                "Authentication attempt",
                method=request.method,
                url=str(request.url),
                client_ip=client_ip,
                user_agent=request.headers.get("User-Agent"),
            )

        try:
            response = await call_next(request)

            # Log failed authentication attempts
            if (
                self.log_auth_attempts
                and self._is_auth_endpoint(request)
                and response.status_code == 401
            ):
                self.logger.warning(
                    "Failed authentication attempt",
                    method=request.method,
                    url=str(request.url),
                    client_ip=client_ip,
                    user_agent=request.headers.get("User-Agent"),
                )

            return response

        except Exception as e:
            # Log security-related errors
            if self.log_suspicious_activity:
                self.logger.error(
                    "Security-related error",
                    method=request.method,
                    url=str(request.url),
                    client_ip=client_ip,
                    error=str(e),
                    exc_info=True,
                )

            raise

    def _is_auth_endpoint(self, request: Request) -> bool:
        """
        Check if request is to an authentication endpoint.

        Args:
            request: HTTP request

        Returns:
            True if authentication endpoint
        """
        auth_paths = ["/auth", "/login", "/logout", "/token", "/oauth"]
        return any(request.url.path.startswith(path) for path in auth_paths)
