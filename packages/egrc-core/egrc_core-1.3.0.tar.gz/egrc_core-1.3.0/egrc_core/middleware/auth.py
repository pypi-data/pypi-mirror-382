"""
Authentication and authorization middleware for EGRC Platform.

This module provides middleware for handling authentication and authorization
across all EGRC services.
"""

from collections.abc import Callable
from typing import Any

import jwt
from fastapi import HTTPException, Request, Response, status
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.types import ASGIApp

from ..constants.constants import Headers, SecurityConstants
from ..logging.utils import get_logger


class AuthenticationMiddleware(BaseHTTPMiddleware):
    """
    Middleware for JWT token authentication.

    This middleware validates JWT tokens and extracts user information
    from the token payload.
    """

    def __init__(
        self,
        app: ASGIApp,
        secret_key: str,
        algorithm: str = SecurityConstants.JWT_ALGORITHM,
        exclude_paths: list[str] | None = None,
        auto_error: bool = True,
    ):
        """
        Initialize authentication middleware.

        Args:
            app: ASGI application
            secret_key: JWT secret key
            algorithm: JWT algorithm
            exclude_paths: List of paths to exclude from authentication
            auto_error: Whether to automatically raise errors for invalid tokens
        """
        super().__init__(app)
        self.secret_key = secret_key
        self.algorithm = algorithm
        self.exclude_paths = exclude_paths or [
            "/health",
            "/metrics",
            "/docs",
            "/openapi.json",
            "/auth/login",
            "/auth/register",
        ]
        self.auto_error = auto_error
        self.logger = get_logger("egrc_core.auth")

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        """
        Process request with authentication.

        Args:
            request: HTTP request
            call_next: Next middleware/handler

        Returns:
            HTTP response
        """
        # Skip authentication for excluded paths
        if self._should_skip_auth(request):
            return await call_next(request)

        # Extract token from request
        token = self._extract_token(request)

        if not token:
            if self.auto_error:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Authentication token required",
                    headers={"WWW-Authenticate": "Bearer"},
                )
            return await call_next(request)

        try:
            # Validate and decode token
            payload = self._validate_token(token)

            # Add user information to request state
            request.state.user = payload
            request.state.user_id = payload.get("sub")
            request.state.tenant_id = payload.get("tenant_id")
            request.state.roles = payload.get("roles", [])
            request.state.permissions = payload.get("permissions", [])

            # Log successful authentication
            self.logger.info(
                "User authenticated",
                user_id=payload.get("sub"),
                tenant_id=payload.get("tenant_id"),
                method=request.method,
                url=str(request.url),
            )

        except jwt.ExpiredSignatureError:
            if self.auto_error:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Token has expired",
                    headers={"WWW-Authenticate": "Bearer"},
                )
        except jwt.InvalidTokenError:
            if self.auto_error:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Invalid token",
                    headers={"WWW-Authenticate": "Bearer"},
                )
        except Exception as e:
            self.logger.error(
                "Authentication error",
                error=str(e),
                method=request.method,
                url=str(request.url),
                exc_info=True,
            )
            if self.auto_error:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Authentication failed",
                    headers={"WWW-Authenticate": "Bearer"},
                )

        return await call_next(request)

    def _should_skip_auth(self, request: Request) -> bool:
        """
        Check if authentication should be skipped for this request.

        Args:
            request: HTTP request

        Returns:
            True if authentication should be skipped
        """
        path = request.url.path
        return any(path.startswith(excluded) for excluded in self.exclude_paths)

    def _extract_token(self, request: Request) -> str | None:
        """
        Extract JWT token from request.

        Args:
            request: HTTP request

        Returns:
            JWT token or None
        """
        # Try Authorization header first
        auth_header = request.headers.get(Headers.AUTHORIZATION)
        if auth_header and auth_header.startswith("Bearer "):
            return auth_header[7:]

        # Try custom header
        token = request.headers.get(Headers.X_API_KEY)
        if token:
            return token

        # Try query parameter
        token = request.query_params.get("token")
        if token:
            return token

        return None

    def _validate_token(self, token: str) -> dict[str, Any]:
        """
        Validate and decode JWT token.

        Args:
            token: JWT token

        Returns:
            Token payload

        Raises:
            jwt.ExpiredSignatureError: If token has expired
            jwt.InvalidTokenError: If token is invalid
        """
        try:
            payload = jwt.decode(token, self.secret_key, algorithms=[self.algorithm])
            return payload
        except jwt.ExpiredSignatureError:
            raise
        except jwt.InvalidTokenError:
            raise


class AuthorizationMiddleware(BaseHTTPMiddleware):
    """
    Middleware for role-based access control (RBAC).

    This middleware checks user permissions and roles for accessing
    protected resources.
    """

    def __init__(
        self,
        app: ASGIApp,
        required_permissions: dict[str, list[str]] | None = None,
        required_roles: dict[str, list[str]] | None = None,
        exclude_paths: list[str] | None = None,
    ):
        """
        Initialize authorization middleware.

        Args:
            app: ASGI application
            required_permissions: Dictionary mapping paths to required permissions
            required_roles: Dictionary mapping paths to required roles
            exclude_paths: List of paths to exclude from authorization
        """
        super().__init__(app)
        self.required_permissions = required_permissions or {}
        self.required_roles = required_roles or {}
        self.exclude_paths = exclude_paths or [
            "/health",
            "/metrics",
            "/docs",
            "/openapi.json",
        ]
        self.logger = get_logger("egrc_core.auth")

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        """
        Process request with authorization.

        Args:
            request: HTTP request
            call_next: Next middleware/handler

        Returns:
            HTTP response
        """
        # Skip authorization for excluded paths
        if self._should_skip_auth(request):
            return await call_next(request)

        # Check if user is authenticated
        if not hasattr(request.state, "user") or not request.state.user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Authentication required",
                headers={"WWW-Authenticate": "Bearer"},
            )

        # Check permissions
        if not self._check_permissions(request):
            self.logger.warning(
                "Access denied - insufficient permissions",
                user_id=getattr(request.state, "user_id", None),
                tenant_id=getattr(request.state, "tenant_id", None),
                method=request.method,
                url=str(request.url),
                required_permissions=self.required_permissions.get(
                    request.url.path, []
                ),
                user_permissions=getattr(request.state, "permissions", []),
            )
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN, detail="Insufficient permissions"
            )

        # Check roles
        if not self._check_roles(request):
            self.logger.warning(
                "Access denied - insufficient roles",
                user_id=getattr(request.state, "user_id", None),
                tenant_id=getattr(request.state, "tenant_id", None),
                method=request.method,
                url=str(request.url),
                required_roles=self.required_roles.get(request.url.path, []),
                user_roles=getattr(request.state, "roles", []),
            )
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN, detail="Insufficient roles"
            )

        return await call_next(request)

    def _should_skip_auth(self, request: Request) -> bool:
        """
        Check if authorization should be skipped for this request.

        Args:
            request: HTTP request

        Returns:
            True if authorization should be skipped
        """
        path = request.url.path
        return any(path.startswith(excluded) for excluded in self.exclude_paths)

    def _check_permissions(self, request: Request) -> bool:
        """
        Check if user has required permissions.

        Args:
            request: HTTP request

        Returns:
            True if user has required permissions
        """
        path = request.url.path
        required_permissions = self.required_permissions.get(path, [])

        if not required_permissions:
            return True

        user_permissions = getattr(request.state, "permissions", [])
        return any(perm in user_permissions for perm in required_permissions)

    def _check_roles(self, request: Request) -> bool:
        """
        Check if user has required roles.

        Args:
            request: HTTP request

        Returns:
            True if user has required roles
        """
        path = request.url.path
        required_roles = self.required_roles.get(path, [])

        if not required_roles:
            return True

        user_roles = getattr(request.state, "roles", [])
        return any(role in user_roles for role in required_roles)


class APIKeyMiddleware(BaseHTTPMiddleware):
    """
    Middleware for API key authentication.

    This middleware validates API keys for service-to-service
    communication.
    """

    def __init__(
        self,
        app: ASGIApp,
        valid_api_keys: set[str],
        header_name: str = Headers.X_API_KEY,
        exclude_paths: list[str] | None = None,
    ):
        """
        Initialize API key middleware.

        Args:
            app: ASGI application
            valid_api_keys: Set of valid API keys
            header_name: Header name containing API key
            exclude_paths: List of paths to exclude from API key validation
        """
        super().__init__(app)
        self.valid_api_keys = valid_api_keys
        self.header_name = header_name
        self.exclude_paths = exclude_paths or [
            "/health",
            "/metrics",
            "/docs",
            "/openapi.json",
        ]
        self.logger = get_logger("egrc_core.auth")

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        """
        Process request with API key validation.

        Args:
            request: HTTP request
            call_next: Next middleware/handler

        Returns:
            HTTP response
        """
        # Skip API key validation for excluded paths
        if self._should_skip_validation(request):
            return await call_next(request)

        # Extract API key
        api_key = request.headers.get(self.header_name)

        if not api_key:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED, detail="API key required"
            )

        # Validate API key
        if api_key not in self.valid_api_keys:
            self.logger.warning(
                "Invalid API key",
                api_key=api_key[:8] + "..." if len(api_key) > 8 else api_key,
                method=request.method,
                url=str(request.url),
                client_ip=request.client.host if request.client else None,
            )
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid API key"
            )

        # Add API key info to request state
        request.state.api_key = api_key
        request.state.authenticated = True

        return await call_next(request)

    def _should_skip_validation(self, request: Request) -> bool:
        """
        Check if API key validation should be skipped for this request.

        Args:
            request: HTTP request

        Returns:
            True if validation should be skipped
        """
        path = request.url.path
        return any(path.startswith(excluded) for excluded in self.exclude_paths)
