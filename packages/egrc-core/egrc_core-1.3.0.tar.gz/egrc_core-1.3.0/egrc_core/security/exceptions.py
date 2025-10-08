"""
Security-specific exceptions for EGRC Platform.

This module defines custom exceptions for authentication and authorization
scenarios with detailed error information and context.
"""

from typing import Any, Dict, Optional


class SecurityError(Exception):
    """Base exception for all security-related errors."""

    def __init__(
        self,
        message: str,
        error_code: Optional[str] = None,
        details: Optional[Dict[str, Any]] = None,
    ):
        """
        Initialize security error.

        Args:
            message: Error message
            error_code: Error code for programmatic handling
            details: Additional error details
        """
        super().__init__(message)
        self.message = message
        self.error_code = error_code
        self.details = details or {}


class AuthenticationError(SecurityError):
    """Exception raised when authentication fails."""

    def __init__(
        self,
        message: str = "Authentication failed",
        error_code: str = "AUTH_FAILED",
        details: Optional[Dict[str, Any]] = None,
    ):
        """
        Initialize authentication error.

        Args:
            message: Error message
            error_code: Error code
            details: Additional error details
        """
        super().__init__(message, error_code, details)


class AuthorizationError(SecurityError):
    """Exception raised when authorization fails."""

    def __init__(
        self,
        message: str = "Authorization failed",
        error_code: str = "AUTHZ_FAILED",
        details: Optional[Dict[str, Any]] = None,
    ):
        """
        Initialize authorization error.

        Args:
            message: Error message
            error_code: Error code
            details: Additional error details
        """
        super().__init__(message, error_code, details)


class TokenExpiredError(AuthenticationError):
    """Exception raised when JWT token is expired."""

    def __init__(
        self,
        message: str = "Token has expired",
        error_code: str = "TOKEN_EXPIRED",
        details: Optional[Dict[str, Any]] = None,
    ):
        """
        Initialize token expired error.

        Args:
            message: Error message
            error_code: Error code
            details: Additional error details
        """
        super().__init__(message, error_code, details)


class TokenRevokedError(AuthenticationError):
    """Exception raised when JWT token is revoked."""

    def __init__(
        self,
        message: str = "Token has been revoked",
        error_code: str = "TOKEN_REVOKED",
        details: Optional[Dict[str, Any]] = None,
    ):
        """
        Initialize token revoked error.

        Args:
            message: Error message
            error_code: Error code
            details: Additional error details
        """
        super().__init__(message, error_code, details)


class InvalidTokenError(AuthenticationError):
    """Exception raised when JWT token is invalid."""

    def __init__(
        self,
        message: str = "Invalid token",
        error_code: str = "INVALID_TOKEN",
        details: Optional[Dict[str, Any]] = None,
    ):
        """
        Initialize invalid token error.

        Args:
            message: Error message
            error_code: Error code
            details: Additional error details
        """
        super().__init__(message, error_code, details)


class PermissionDeniedError(AuthorizationError):
    """Exception raised when user lacks required permission."""

    def __init__(
        self,
        permission: str,
        message: Optional[str] = None,
        error_code: str = "PERMISSION_DENIED",
        details: Optional[Dict[str, Any]] = None,
    ):
        """
        Initialize permission denied error.

        Args:
            permission: Required permission
            message: Error message
            error_code: Error code
            details: Additional error details
        """
        if message is None:
            message = f"Permission denied: {permission} required"

        error_details = details or {}
        error_details["required_permission"] = permission

        super().__init__(message, error_code, error_details)
        self.permission = permission


class RoleRequiredError(AuthorizationError):
    """Exception raised when user lacks required role."""

    def __init__(
        self,
        role: str,
        message: Optional[str] = None,
        error_code: str = "ROLE_REQUIRED",
        details: Optional[Dict[str, Any]] = None,
    ):
        """
        Initialize role required error.

        Args:
            role: Required role
            message: Error message
            error_code: Error code
            details: Additional error details
        """
        if message is None:
            message = f"Role required: {role}"

        error_details = details or {}
        error_details["required_role"] = role

        super().__init__(message, error_code, error_details)
        self.role = role


class TenantAccessDeniedError(AuthorizationError):
    """Exception raised when user lacks access to tenant."""

    def __init__(
        self,
        tenant_id: str,
        message: Optional[str] = None,
        error_code: str = "TENANT_ACCESS_DENIED",
        details: Optional[Dict[str, Any]] = None,
    ):
        """
        Initialize tenant access denied error.

        Args:
            tenant_id: Tenant identifier
            message: Error message
            error_code: Error code
            details: Additional error details
        """
        if message is None:
            message = f"Access denied to tenant: {tenant_id}"

        error_details = details or {}
        error_details["tenant_id"] = tenant_id

        super().__init__(message, error_code, error_details)
        self.tenant_id = tenant_id


class ResourceAccessDeniedError(AuthorizationError):
    """Exception raised when user lacks access to specific resource."""

    def __init__(
        self,
        resource_type: str,
        resource_id: str,
        message: Optional[str] = None,
        error_code: str = "RESOURCE_ACCESS_DENIED",
        details: Optional[Dict[str, Any]] = None,
    ):
        """
        Initialize resource access denied error.

        Args:
            resource_type: Type of resource
            resource_id: Resource identifier
            message: Error message
            error_code: Error code
            details: Additional error details
        """
        if message is None:
            message = f"Access denied to {resource_type}: {resource_id}"

        error_details = details or {}
        error_details["resource_type"] = resource_type
        error_details["resource_id"] = resource_id

        super().__init__(message, error_code, error_details)
        self.resource_type = resource_type
        self.resource_id = resource_id


class ABACRuleViolationError(AuthorizationError):
    """Exception raised when ABAC rule is violated."""

    def __init__(
        self,
        rule_description: str,
        message: Optional[str] = None,
        error_code: str = "ABAC_RULE_VIOLATION",
        details: Optional[Dict[str, Any]] = None,
    ):
        """
        Initialize ABAC rule violation error.

        Args:
            rule_description: Description of violated rule
            message: Error message
            error_code: Error code
            details: Additional error details
        """
        if message is None:
            message = f"ABAC rule violation: {rule_description}"

        error_details = details or {}
        error_details["rule_description"] = rule_description

        super().__init__(message, error_code, error_details)
        self.rule_description = rule_description


class SecurityConfigurationError(SecurityError):
    """Exception raised when security configuration is invalid."""

    def __init__(
        self,
        message: str = "Security configuration error",
        error_code: str = "SECURITY_CONFIG_ERROR",
        details: Optional[Dict[str, Any]] = None,
    ):
        """
        Initialize security configuration error.

        Args:
            message: Error message
            error_code: Error code
            details: Additional error details
        """
        super().__init__(message, error_code, details)


class CacheError(SecurityError):
    """Exception raised when security cache operations fail."""

    def __init__(
        self,
        message: str = "Security cache error",
        error_code: str = "CACHE_ERROR",
        details: Optional[Dict[str, Any]] = None,
    ):
        """
        Initialize cache error.

        Args:
            message: Error message
            error_code: Error code
            details: Additional error details
        """
        super().__init__(message, error_code, details)


class AuditError(SecurityError):
    """Exception raised when audit logging fails."""

    def __init__(
        self,
        message: str = "Audit logging error",
        error_code: str = "AUDIT_ERROR",
        details: Optional[Dict[str, Any]] = None,
    ):
        """
        Initialize audit error.

        Args:
            message: Error message
            error_code: Error code
            details: Additional error details
        """
        super().__init__(message, error_code, details)
