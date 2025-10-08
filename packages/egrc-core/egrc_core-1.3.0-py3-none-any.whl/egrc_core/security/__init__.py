"""
Security module for EGRC Platform.

This module provides comprehensive security utilities including:
- JWT verification and validation
- Permission-based authorization
- ABAC (Attribute-Based Access Control) support
- Token caching and revocation
- Audit logging for access decisions
"""

from .audit import AccessAuditLogger, AuditContext, AuditEvent
from .auth import JWKSCache, JWTVerifier, TokenRevocationManager, TokenValidator
from .cache import PermissionCache, SecurityCache, TokenCache
from .decorators import (
    abac_check,
    require_permission,
    require_permissions,
    require_role,
    require_tenant,
)
from .exceptions import (
    AuthenticationError,
    AuthorizationError,
    PermissionDeniedError,
    TenantAccessDeniedError,
    TokenExpiredError,
    TokenRevokedError,
)
from .middleware import AuthMiddleware, PermissionMiddleware, TenantMiddleware
from .permissions import (
    ABACEngine,
    PermissionChecker,
    PermissionContext,
    RolePermissionManager,
)


__all__ = [
    # Authentication
    "JWTVerifier",
    "TokenValidator",
    "JWKSCache",
    "TokenRevocationManager",
    # Permissions
    "PermissionChecker",
    "RolePermissionManager",
    "ABACEngine",
    "PermissionContext",
    # Decorators
    "require_permission",
    "require_permissions",
    "require_role",
    "require_tenant",
    "abac_check",
    # Middleware
    "AuthMiddleware",
    "PermissionMiddleware",
    "TenantMiddleware",
    # Exceptions
    "AuthenticationError",
    "AuthorizationError",
    "TokenExpiredError",
    "TokenRevokedError",
    "PermissionDeniedError",
    "TenantAccessDeniedError",
    # Audit
    "AccessAuditLogger",
    "AuditEvent",
    "AuditContext",
    # Cache
    "SecurityCache",
    "TokenCache",
    "PermissionCache",
]
