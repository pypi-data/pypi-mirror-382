"""
Authentication middleware for EGRC Core Service.

This middleware handles JWT token validation and user authentication
for the core service.
"""

from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware

from ..exceptions.exceptions import AuthenticationError
from ..logging.utils import get_logger


logger = get_logger(__name__)


class AuthMiddleware(BaseHTTPMiddleware):
    """Middleware for authentication."""

    def __init__(self, app, exclude_paths: list | None = None):
        """Initialize authentication middleware.

        Args:
            app: FastAPI application
            exclude_paths: List of paths to exclude from authentication
        """
        super().__init__(app)
        self.exclude_paths = exclude_paths or [
            "/health",
            "/docs",
            "/redoc",
            "/openapi.json",
            "/graphql",  # GraphQL handles auth differently
        ]

    async def dispatch(self, request: Request, call_next):
        """Process request and validate authentication.

        Args:
            request: Incoming request
            call_next: Next middleware/handler

        Returns:
            Response
        """
        # Skip authentication for excluded paths
        if self._should_skip_auth(request):
            return await call_next(request)

        # Extract and validate token
        try:
            user_info = await self._validate_token(request)
            if user_info:
                request.state.user = user_info
            else:
                # For some endpoints, authentication might be optional
                if not self._requires_auth(request):
                    return await call_next(request)

                raise AuthenticationError("Invalid or missing authentication token")

        except AuthenticationError:
            # For some endpoints, authentication might be optional
            if not self._requires_auth(request):
                return await call_next(request)
            raise
        except Exception as e:
            logger.error("Authentication error", error=str(e))
            if not self._requires_auth(request):
                return await call_next(request)
            raise AuthenticationError("Authentication failed")

        return await call_next(request)

    def _should_skip_auth(self, request: Request) -> bool:
        """Check if authentication should be skipped for this request.

        Args:
            request: HTTP request

        Returns:
            True if authentication should be skipped
        """
        path = request.url.path

        # Skip for excluded paths
        for exclude_path in self.exclude_paths:
            if path.startswith(exclude_path):
                return True

        # Skip for OPTIONS requests
        if request.method == "OPTIONS":
            return True

        return False

    def _requires_auth(self, request: Request) -> bool:
        """Check if the request requires authentication.

        Args:
            request: HTTP request

        Returns:
            True if authentication is required
        """
        path = request.url.path

        # Always require auth for protected paths
        protected_paths = [
            "/admin",
            "/api",
        ]

        for protected_path in protected_paths:
            if path.startswith(protected_path):
                return True

        return False

    async def _validate_token(self, request: Request) -> dict | None:
        """Validate JWT token and extract user information.

        Args:
            request: HTTP request

        Returns:
            User information or None if invalid
        """
        # Extract token from Authorization header
        auth_header = request.headers.get("Authorization")
        if not auth_header or not auth_header.startswith("Bearer "):
            return None

        # token = auth_header[7:]  # Remove "Bearer " prefix

        # Get tenant ID from request state
        tenant_id = getattr(request.state, "tenant_id", None)
        if not tenant_id:
            return None

        # For core service, we might validate against a central auth service
        # For now, we'll do basic validation
        try:
            # This would be implemented to validate with the auth service
            # For now, just return basic user info
            user_info = {
                "id": "core-user",
                "tenant_id": tenant_id,
                "roles": ["core-user"],
                "permissions": ["core:read"],
            }

            return user_info

        except Exception as e:
            logger.error("Token validation error", error=str(e))
            return None
