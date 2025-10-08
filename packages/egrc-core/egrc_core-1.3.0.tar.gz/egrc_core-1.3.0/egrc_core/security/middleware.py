"""
Security Middleware for EGRC Platform.

This module provides middleware for Flask and FastAPI applications to handle
JWT authentication, user context attachment, and security headers.
"""

import logging
import uuid
from typing import Any, Callable, Dict, Optional

from .audit import AuditContext, get_audit_logger
from .auth import get_jwt_verifier
from .exceptions import AuthenticationError, AuthorizationError


logger = logging.getLogger(__name__)


class AuthMiddleware:
    """
    Base authentication middleware that extracts and validates JWT tokens.
    """

    def __init__(
        self,
        jwt_verifier=None,
        audit_logger=None,
        skip_paths: Optional[list] = None,
        skip_methods: Optional[list] = None,
    ):
        """
        Initialize authentication middleware.

        Args:
            jwt_verifier: JWT verifier instance
            audit_logger: Audit logger instance
            skip_paths: List of paths to skip authentication
            skip_methods: List of HTTP methods to skip authentication
        """
        self.jwt_verifier = jwt_verifier or get_jwt_verifier()
        self.audit_logger = audit_logger or get_audit_logger()
        self.skip_paths = skip_paths or [
            "/health",
            "/metrics",
            "/docs",
            "/openapi.json",
        ]
        self.skip_methods = skip_methods or ["OPTIONS"]

    def _should_skip_auth(self, path: str, method: str) -> bool:
        """
        Check if authentication should be skipped for this request.

        Args:
            path: Request path
            method: HTTP method

        Returns:
            True if authentication should be skipped
        """
        # Skip based on method
        if method in self.skip_methods:
            return True

        # Skip based on path
        for skip_path in self.skip_paths:
            if path.startswith(skip_path):
                return True

        return False

    def _extract_token(self, headers: Dict[str, str]) -> Optional[str]:
        """
        Extract JWT token from request headers.

        Args:
            headers: Request headers

        Returns:
            JWT token or None
        """
        # Try Authorization header with Bearer token
        auth_header = headers.get("Authorization") or headers.get("authorization")
        if auth_header and auth_header.startswith("Bearer "):
            return auth_header[7:]  # Remove "Bearer " prefix

        # Try X-Access-Token header
        return headers.get("X-Access-Token") or headers.get("x-access-token")

    def _create_audit_context(
        self,
        user_info: Dict[str, Any],
        request_info: Dict[str, Any],
    ) -> AuditContext:
        """
        Create audit context from user info and request info.

        Args:
            user_info: User information from JWT
            request_info: Request information

        Returns:
            Audit context
        """
        return AuditContext(
            user_id=user_info["user_id"],
            username=user_info["username"],
            tenant_id=user_info["tenant_id"],
            session_id=request_info.get("session_id"),
            request_id=request_info.get("request_id"),
            ip_address=request_info.get("ip_address"),
            user_agent=request_info.get("user_agent"),
            endpoint=request_info.get("endpoint"),
            method=request_info.get("method"),
        )


class FlaskAuthMiddleware(AuthMiddleware):
    """
    Flask-specific authentication middleware.
    """

    def __init__(self, app=None, **kwargs):
        """
        Initialize Flask authentication middleware.

        Args:
            app: Flask application instance
            **kwargs: Additional middleware options
        """
        super().__init__(**kwargs)
        if app:
            self.init_app(app)

    def init_app(self, app):
        """
        Initialize middleware with Flask app.

        Args:
            app: Flask application instance
        """
        app.before_request(self.before_request)
        app.after_request(self.after_request)

    def before_request(self):
        """Flask before_request handler."""
        from flask import g, request

        try:
            # Skip authentication for certain paths/methods
            if self._should_skip_auth(request.path, request.method):
                return

            # Extract token
            token = self._extract_token(dict(request.headers))
            if not token:
                raise AuthenticationError("No authentication token provided")

            # Verify token
            user_info = self.jwt_verifier.get_user_info(token)

            # Attach user context to Flask's g object
            g.user = user_info
            g.token = token
            g.request_id = str(uuid.uuid4())

            # Log successful authentication
            # request_info = {
            #                 "session_id": getattr(g, "session_id", None),
            #                 "request_id": g.request_id,
            #                 "ip_address": request.remote_addr,
            #                 "user_agent": request.headers.get("User-Agent"),
            #                 "endpoint": request.endpoint,
            #                 "method": request.method,
            #             }
            #
            #             # audit_context = self._create_audit_context(user_info, request_info)
            # Note: In a real implementation, you'd await this
            # For Flask, you might want to use a sync audit logger
            # or run this in a background task

        except AuthenticationError as e:
            logger.warning(f"Authentication failed: {e}")
            from flask import jsonify

            return jsonify({"error": "Authentication failed", "message": str(e)}), 401
        except Exception as e:
            logger.error(f"Unexpected error in authentication middleware: {e}")
            from flask import jsonify

            return jsonify({"error": "Internal server error"}), 500

    def after_request(self, response):
        """Flask after_request handler."""
        from flask import g

        # Add security headers
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-Frame-Options"] = "DENY"
        response.headers["X-XSS-Protection"] = "1; mode=block"
        response.headers["Strict-Transport-Security"] = (
            "max-age=31536000; includeSubDomains"
        )

        # Add request ID to response headers
        if hasattr(g, "request_id"):
            response.headers["X-Request-ID"] = g.request_id

        return response


class FastAPIAuthMiddleware(AuthMiddleware):
    """
    FastAPI-specific authentication middleware.
    """

    def __init__(self, **kwargs):
        """
        Initialize FastAPI authentication middleware.

        Args:
            **kwargs: Additional middleware options
        """
        super().__init__(**kwargs)

    async def __call__(self, request, call_next):
        """
        FastAPI middleware callable.

        Args:
            request: FastAPI request object
            call_next: Next middleware/handler

        Returns:
            Response
        """
        from fastapi.responses import JSONResponse

        try:
            # Skip authentication for certain paths/methods
            if self._should_skip_auth(request.url.path, request.method):
                return await call_next(request)

            # Extract token
            token = self._extract_token(dict(request.headers))
            if not token:
                return JSONResponse(
                    status_code=401,
                    content={
                        "error": "Authentication failed",
                        "message": "No authentication token provided",
                    },
                )

            # Verify token
            user_info = self.jwt_verifier.get_user_info(token)

            # Attach user context to request state
            request.state.user = user_info
            request.state.token = token
            request.state.request_id = str(uuid.uuid4())

            # Log successful authentication
            # request_info = {
            #                 "session_id": getattr(request.state, "session_id", None),
            #                 "request_id": request.state.request_id,
            #                 "ip_address": request.client.host if request.client else None,
            #                 "user_agent": request.headers.get("user-agent"),
            #                 "endpoint": request.url.path,
            #                 "method": request.method,
            #             }
            #
            #             # audit_context = self._create_audit_context(user_info, request_info)
            # await self.audit_logger.log_authentication_success(audit_context, user_info)
            pass

        except AuthenticationError:
            # logger.warning(f"Authentication failed: {_e}")
            # return JSONResponse(
            # status_code = (401,)
            # content = ({"error": "Authentication failed", "message": str(e)},)
            #             )
            # except Exception as e:
            # logger.error(f"Unexpected error in authentication middleware: {e}")
            return JSONResponse(
                status_code=500, content={"error": "Internal server error"}
            )

        # Process request
        response = await call_next(request)

        # Add security headers
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-Frame-Options"] = "DENY"
        response.headers["X-XSS-Protection"] = "1; mode=block"
        response.headers["Strict-Transport-Security"] = (
            "max-age=31536000; includeSubDomains"
        )

        # Add request ID to response headers
        if hasattr(request.state, "request_id"):
            response.headers["X-Request-ID"] = request.state.request_id

        return response


class PermissionMiddleware:
    """
    Middleware for permission-based access control.
    """

    def __init__(self, permission_checker=None, audit_logger=None):
        """
        Initialize permission middleware.

        Args:
            permission_checker: Permission checker instance
            audit_logger: Audit logger instance
        """
        from .audit import get_audit_logger
        from .permissions import get_permission_checker

        self.permission_checker = permission_checker or get_permission_checker()
        self.audit_logger = audit_logger or get_audit_logger()

    def check_permission(
        self,
        permission: str,
        resource_type: Optional[str] = None,
        resource_id: Optional[str] = None,
    ):
        """
        Decorator to check permission for endpoint.

        Args:
            permission: Required permission
            resource_type: Type of resource
            resource_id: Resource identifier

        Returns:
            Decorator function
        """

        def decorator(func):
            async def async_wrapper(*args, **kwargs):
                return await self._check_permission_async(
                    func, permission, resource_type, resource_id, *args, **kwargs
                )

            def sync_wrapper(*args, **kwargs):
                return self._check_permission_sync(
                    func, permission, resource_type, resource_id, *args, **kwargs
                )

            # Return appropriate wrapper based on function type
            import asyncio

            if asyncio.iscoroutinefunction(func):
                return async_wrapper
            else:
                return sync_wrapper

        return decorator

    async def _check_permission_async(
        self,
        func: Callable,
        permission: str,
        resource_type: Optional[str],
        resource_id: Optional[str],
        *args,
        **kwargs,
    ):
        """Async permission check implementation."""
        try:
            # Extract user context from request
            user_context = self._extract_user_context(*args, **kwargs)
            if not user_context:
                raise AuthenticationError("User context not found")

            # Create permission context
            from .permissions import PermissionContext

            permission_context = PermissionContext(
                user_id=user_context["user_id"],
                username=user_context["username"],
                tenant_id=user_context["tenant_id"],
                roles=user_context["roles"],
                resource_type=resource_type,
                resource_id=resource_id,
            )

            # Check permission
            has_permission = self.permission_checker.check_permission(
                permission_context, permission
            )

            if not has_permission:
                # Log failed authorization
                # from .audit import AuditContext

                # audit_context = AuditContext(
                #                     user_id=user_context["user_id"],
                #                     username=user_context["username"],
                #                     tenant_id=user_context["tenant_id"],
                #                 )
                # await self.audit_logger.log_authorization_failure(
                #     audit_context, permission, "Permission denied"
                # )
                raise AuthorizationError(f"Permission denied: {permission}")

            # Call the original function
            return await func(*args, **kwargs)

        except (AuthenticationError, AuthorizationError):
            raise
        except Exception as e:
            logger.error(f"Unexpected error in permission check: {e}")
            raise AuthorizationError(f"Permission check failed: {e}")

    def _check_permission_sync(
        self,
        func: Callable,
        permission: str,
        resource_type: Optional[str],
        resource_id: Optional[str],
        *args,
        **kwargs,
    ):
        """Sync permission check implementation."""
        import asyncio

        async def async_check():
            return await self._check_permission_async(
                func, permission, resource_type, resource_id, *args, **kwargs
            )

        return asyncio.run(async_check())

    def _extract_user_context(self, *args, **kwargs) -> Optional[Dict[str, Any]]:
        """
        Extract user context from request.

        This method needs to be adapted based on your framework.
        """
        # For Flask: from flask import g; return getattr(g, 'user', None)
        # For FastAPI: from fastapi import Request; return getattr(request.state,
        # 'user', None)

        # This is a placeholder implementation
        return kwargs.get("user_context")


class TenantMiddleware:
    """
    Middleware for tenant isolation and validation.
    """

    def __init__(self, audit_logger=None):
        """
        Initialize tenant middleware.

        Args:
            audit_logger: Audit logger instance
        """
        from .audit import get_audit_logger

        self.audit_logger = audit_logger or get_audit_logger()

    def validate_tenant_access(self, tenant_id_param: str = "tenant_id"):
        """
        Decorator to validate tenant access.

        Args:
            tenant_id_param: Parameter name containing tenant ID

        Returns:
            Decorator function
        """

        def decorator(func):
            async def async_wrapper(*args, **kwargs):
                return await self._validate_tenant_async(
                    func, tenant_id_param, *args, **kwargs
                )

            def sync_wrapper(*args, **kwargs):
                return self._validate_tenant_sync(
                    func, tenant_id_param, *args, **kwargs
                )

            import asyncio

            if asyncio.iscoroutinefunction(func):
                return async_wrapper
            else:
                return sync_wrapper

        return decorator

    async def _validate_tenant_async(
        self,
        func: Callable,
        tenant_id_param: str,
        *args,
        **kwargs,
    ):
        """Async tenant validation implementation."""
        try:
            # Extract user context
            user_context = self._extract_user_context(*args, **kwargs)
            if not user_context:
                raise AuthenticationError("User context not found")

            # Get target tenant ID
            target_tenant_id = kwargs.get(tenant_id_param)
            if not target_tenant_id:
                raise AuthorizationError(
                    f"Missing tenant ID parameter: {tenant_id_param}"
                )

            # Validate tenant access
            if user_context["tenant_id"] != target_tenant_id:
                # Log failed tenant access
                # from .audit import AuditContext

                # audit_context = AuditContext(
                #                     user_id=user_context["user_id"],
                #                     username=user_context["username"],
                #                     tenant_id=user_context["tenant_id"],
                #                 )
                await self.audit_logger.log_tenant_access(
                    # audit_context, target_tenant_id, False, "Tenant access denied"
                )
                raise AuthorizationError(f"Access denied to tenant: {target_tenant_id}")

            # Call the original function
            return await func(*args, **kwargs)

        except (AuthenticationError, AuthorizationError):
            raise
        except Exception as e:
            logger.error(f"Unexpected error in tenant validation: {e}")
            raise AuthorizationError(f"Tenant validation failed: {e}")

    def _validate_tenant_sync(
        self,
        func: Callable,
        tenant_id_param: str,
        *args,
        **kwargs,
    ):
        """Sync tenant validation implementation."""
        import asyncio

        async def async_check():
            return await self._validate_tenant_async(
                func, tenant_id_param, *args, **kwargs
            )

        return asyncio.run(async_check())

    def _extract_user_context(self, *args, **kwargs) -> Optional[Dict[str, Any]]:
        """
        Extract user context from request.

        This method needs to be adapted based on your framework.
        """
        # This is a placeholder implementation
        return kwargs.get("user_context")


# Factory functions for easy middleware setup


def create_flask_auth_middleware(app, **kwargs):
    """
    Create and configure Flask authentication middleware.

    Args:
        app: Flask application instance
        **kwargs: Additional middleware options

    Returns:
        Configured FlaskAuthMiddleware instance
    """
    middleware = FlaskAuthMiddleware(**kwargs)
    middleware.init_app(app)
    return middleware


def create_fastapi_auth_middleware(**kwargs):
    """
    Create FastAPI authentication middleware.

    Args:
        **kwargs: Additional middleware options

    Returns:
        Configured FastAPIAuthMiddleware instance
    """
    return FastAPIAuthMiddleware(**kwargs)


def create_permission_middleware(**kwargs):
    """
    Create permission middleware.

    Args:
        **kwargs: Additional middleware options

    Returns:
        Configured PermissionMiddleware instance
    """
    return PermissionMiddleware(**kwargs)


def create_tenant_middleware(**kwargs):
    """
    Create tenant middleware.

    Args:
        **kwargs: Additional middleware options

    Returns:
        Configured TenantMiddleware instance
    """
    return TenantMiddleware(**kwargs)
