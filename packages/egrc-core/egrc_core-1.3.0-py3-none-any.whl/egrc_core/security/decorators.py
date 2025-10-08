"""
Security Decorators for EGRC Platform.

This module provides decorators for permission checking, role validation,
tenant isolation, and ABAC rule evaluation that can be used with Flask
and FastAPI endpoints.
"""

import functools
import logging
from typing import Any, Callable, Dict, List, Optional

from .audit import AuditContext, get_audit_logger
from .auth import get_jwt_verifier
from .exceptions import (
    ABACRuleViolationError,
    AuthenticationError,
    AuthorizationError,
    PermissionDeniedError,
    RoleRequiredError,
    TenantAccessDeniedError,
)
from .permissions import PermissionContext, get_permission_checker


logger = logging.getLogger(__name__)


def require_permission(
    permission: str,
    resource_type: Optional[str] = None,
    resource_id_param: Optional[str] = None,
    abac_rules: Optional[List[Callable]] = None,
    audit: bool = True,
):
    """
    Decorator to require a specific permission for endpoint access.

    Args:
        permission: Required permission
        resource_type: Type of resource being accessed
        resource_id_param: Parameter name containing resource ID
        abac_rules: List of ABAC rule functions
        audit: Whether to audit the permission check

    Returns:
        Decorated function
    """

    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        async def async_wrapper(*args, **kwargs):
            return await _check_permission_async(
                func,
                permission,
                resource_type,
                resource_id_param,
                abac_rules,
                audit,
                *args,
                **kwargs,
            )

        @functools.wraps(func)
        def sync_wrapper(*args, **kwargs):
            return _check_permission_sync(
                func,
                permission,
                resource_type,
                resource_id_param,
                abac_rules,
                audit,
                *args,
                **kwargs,
            )

        # Return appropriate wrapper based on function type
        if _is_async_function(func):
            return async_wrapper
        else:
            return sync_wrapper

    return decorator


def require_permissions(
    permissions: List[str],
    require_all: bool = True,
    resource_type: Optional[str] = None,
    resource_id_param: Optional[str] = None,
    abac_rules: Optional[List[Callable]] = None,
    audit: bool = True,
):
    """
    Decorator to require multiple permissions for endpoint access.

    Args:
        permissions: List of required permissions
        require_all: If True, all permissions must be granted
        resource_type: Type of resource being accessed
        resource_id_param: Parameter name containing resource ID
        abac_rules: List of ABAC rule functions
        audit: Whether to audit the permission check

    Returns:
        Decorated function
    """

    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        async def async_wrapper(*args, **kwargs):
            return await _check_permissions_async(
                func,
                permissions,
                require_all,
                resource_type,
                resource_id_param,
                abac_rules,
                audit,
                *args,
                **kwargs,
            )

        @functools.wraps(func)
        def sync_wrapper(*args, **kwargs):
            return _check_permissions_sync(
                func,
                permissions,
                require_all,
                resource_type,
                resource_id_param,
                abac_rules,
                audit,
                *args,
                **kwargs,
            )

        if _is_async_function(func):
            return async_wrapper
        else:
            return sync_wrapper

    return decorator


def require_role(
    role: str,
    tenant_id_param: Optional[str] = None,
    audit: bool = True,
):
    """
    Decorator to require a specific role for endpoint access.

    Args:
        role: Required role
        tenant_id_param: Parameter name containing tenant ID
        audit: Whether to audit the role check

    Returns:
        Decorated function
    """

    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        async def async_wrapper(*args, **kwargs):
            return await _check_role_async(
                func, role, tenant_id_param, audit, *args, **kwargs
            )

        @functools.wraps(func)
        def sync_wrapper(*args, **kwargs):
            return _check_role_sync(func, role, tenant_id_param, audit, *args, **kwargs)

        if _is_async_function(func):
            return async_wrapper
        else:
            return sync_wrapper

    return decorator


def require_tenant(
    tenant_id_param: str = "tenant_id",
    audit: bool = True,
):
    """
    Decorator to require tenant access validation.

    Args:
        tenant_id_param: Parameter name containing tenant ID
        audit: Whether to audit the tenant check

    Returns:
        Decorated function
    """

    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        async def async_wrapper(*args, **kwargs):
            return await _check_tenant_async(
                func, tenant_id_param, audit, *args, **kwargs
            )

        @functools.wraps(func)
        def sync_wrapper(*args, **kwargs):
            return _check_tenant_sync(func, tenant_id_param, audit, *args, **kwargs)

        if _is_async_function(func):
            return async_wrapper
        else:
            return sync_wrapper

    return decorator


def abac_check(
    rule_function: Callable[[PermissionContext], bool],
    rule_description: str,
    audit: bool = True,
):
    """
    Decorator to apply ABAC rule checking.

    Args:
        rule_function: Function that evaluates the ABAC rule
        rule_description: Human-readable description of the rule
        audit: Whether to audit the ABAC check

    Returns:
        Decorated function
    """

    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        async def async_wrapper(*args, **kwargs):
            return await _check_abac_async(
                func, rule_function, rule_description, audit, *args, **kwargs
            )

        @functools.wraps(func)
        def sync_wrapper(*args, **kwargs):
            return _check_abac_sync(
                func, rule_function, rule_description, audit, *args, **kwargs
            )

        if _is_async_function(func):
            return async_wrapper
        else:
            return sync_wrapper

    return decorator


# Helper functions for permission checking


async def _check_permission_async(
    func: Callable,
    permission: str,
    resource_type: Optional[str],
    resource_id_param: Optional[str],
    abac_rules: Optional[List[Callable]],
    audit: bool,
    *args,
    **kwargs,
):
    """Async permission check implementation."""
    try:
        # Extract request context
        request_context = _extract_request_context(*args, **kwargs)
        if not request_context:
            raise AuthenticationError("Unable to extract request context")

        # Get user info from token
        jwt_verifier = get_jwt_verifier()
        user_info = jwt_verifier.get_user_info(request_context["token"])

        # Create permission context
        permission_context = PermissionContext(
            user_id=user_info["user_id"],
            username=user_info["username"],
            tenant_id=user_info["tenant_id"],
            roles=user_info["roles"],
            resource_type=resource_type,
            resource_id=kwargs.get(resource_id_param) if resource_id_param else None,
            request_attributes=request_context,
        )

        # Get resource attributes if needed
        resource_attributes = None
        if resource_id_param and resource_id_param in kwargs:
            resource_attributes = await _get_resource_attributes(
                resource_type, kwargs[resource_id_param], user_info["tenant_id"]
            )

        # Check permission
        permission_checker = get_permission_checker()
        has_permission = permission_checker.check_permission(
            permission_context, permission, resource_attributes
        )

        if not has_permission:
            if audit:
                audit_logger = get_audit_logger()
                audit_context = _create_audit_context(user_info, request_context)
                await audit_logger.log_authorization_failure(
                    audit_context, permission, "Permission denied"
                )
            raise PermissionDeniedError(permission)

        # Apply ABAC rules if provided
        if abac_rules:
            for rule_func in abac_rules:
                if not rule_func(permission_context):
                    if audit:
                        audit_logger = get_audit_logger()
                        audit_context = _create_audit_context(
                            user_info, request_context
                        )
                        await audit_logger.log_abac_rule_evaluation(
                            audit_context, permission, rule_func.__name__, False
                        )
                    raise ABACRuleViolationError(
                        f"ABAC rule failed: {rule_func.__name__}"
                    )

        # Log successful authorization
        if audit:
            audit_logger = get_audit_logger()
            audit_context = _create_audit_context(user_info, request_context)
            await audit_logger.log_authorization_success(
                audit_context, permission, resource_attributes
            )

        # Call the original function
        return await func(*args, **kwargs)

    except (AuthenticationError, AuthorizationError):
        raise
    except Exception as e:
        logger.error(f"Unexpected error in permission check: {e}")
        raise AuthorizationError(f"Permission check failed: {e}")


def _check_permission_sync(
    func: Callable,
    permission: str,
    resource_type: Optional[str],
    resource_id_param: Optional[str],
    abac_rules: Optional[List[Callable]],
    audit: bool,
    *args,
    **kwargs,
):
    """Sync permission check implementation."""
    import asyncio

    async def async_check():
        return await _check_permission_async(
            func,
            permission,
            resource_type,
            resource_id_param,
            abac_rules,
            audit,
            *args,
            **kwargs,
        )

    return asyncio.run(async_check())


async def _check_permissions_async(
    func: Callable,
    permissions: List[str],
    require_all: bool,
    resource_type: Optional[str],
    resource_id_param: Optional[str],
    abac_rules: Optional[List[Callable]],
    audit: bool,
    *args,
    **kwargs,
):
    """Async multiple permissions check implementation."""
    try:
        # Extract request context
        request_context = _extract_request_context(*args, **kwargs)
        if not request_context:
            raise AuthenticationError("Unable to extract request context")

        # Get user info from token
        jwt_verifier = get_jwt_verifier()
        user_info = jwt_verifier.get_user_info(request_context["token"])

        # Create permission context
        permission_context = PermissionContext(
            user_id=user_info["user_id"],
            username=user_info["username"],
            tenant_id=user_info["tenant_id"],
            roles=user_info["roles"],
            resource_type=resource_type,
            resource_id=kwargs.get(resource_id_param) if resource_id_param else None,
            request_attributes=request_context,
        )

        # Get resource attributes if needed
        resource_attributes = None
        if resource_id_param and resource_id_param in kwargs:
            resource_attributes = await _get_resource_attributes(
                resource_type, kwargs[resource_id_param], user_info["tenant_id"]
            )

        # Check permissions
        permission_checker = get_permission_checker()
        results = permission_checker.check_permissions(
            permission_context, permissions, resource_attributes, require_all
        )

        # Check if all required permissions are granted
        if require_all and not all(results.values()):
            denied_permissions = [p for p, granted in results.items() if not granted]
            if audit:
                audit_logger = get_audit_logger()
                audit_context = _create_audit_context(user_info, request_context)
                await audit_logger.log_authorization_failure(
                    audit_context,
                    f"permissions: {denied_permissions}",
                    "Not all permissions granted",
                )
            raise PermissionDeniedError(f"Required permissions: {denied_permissions}")

        # Apply ABAC rules if provided
        if abac_rules:
            for rule_func in abac_rules:
                if not rule_func(permission_context):
                    if audit:
                        audit_logger = get_audit_logger()
                        audit_context = _create_audit_context(
                            user_info, request_context
                        )
                        await audit_logger.log_abac_rule_evaluation(
                            audit_context,
                            f"permissions: {permissions}",
                            rule_func.__name__,
                            False,
                        )
                    raise ABACRuleViolationError(
                        f"ABAC rule failed: {rule_func.__name__}"
                    )

        # Log successful authorization
        if audit:
            audit_logger = get_audit_logger()
            audit_context = _create_audit_context(user_info, request_context)
            await audit_logger.log_authorization_success(
                audit_context, f"permissions: {permissions}", resource_attributes
            )

        # Call the original function
        return await func(*args, **kwargs)

    except (AuthenticationError, AuthorizationError):
        raise
    except Exception as e:
        logger.error(f"Unexpected error in permissions check: {e}")
        raise AuthorizationError(f"Permissions check failed: {e}")


def _check_permissions_sync(
    func: Callable,
    permissions: List[str],
    require_all: bool,
    resource_type: Optional[str],
    resource_id_param: Optional[str],
    abac_rules: Optional[List[Callable]],
    audit: bool,
    *args,
    **kwargs,
):
    """Sync multiple permissions check implementation."""
    import asyncio

    async def async_check():
        return await _check_permissions_async(
            func,
            permissions,
            require_all,
            resource_type,
            resource_id_param,
            abac_rules,
            audit,
            *args,
            **kwargs,
        )

    return asyncio.run(async_check())


async def _check_role_async(
    func: Callable,
    role: str,
    tenant_id_param: Optional[str],
    audit: bool,
    *args,
    **kwargs,
):
    """Async role check implementation."""
    try:
        # Extract request context
        request_context = _extract_request_context(*args, **kwargs)
        if not request_context:
            raise AuthenticationError("Unable to extract request context")

        # Get user info from token
        jwt_verifier = get_jwt_verifier()
        user_info = jwt_verifier.get_user_info(request_context["token"])

        # Check if user has the required role
        if role not in user_info["roles"]:
            if audit:
                audit_logger = get_audit_logger()
                audit_context = _create_audit_context(user_info, request_context)
                await audit_logger.log_authorization_failure(
                    audit_context, f"role: {role}", "Required role not found"
                )
            raise RoleRequiredError(role)

        # Log successful authorization
        if audit:
            audit_logger = get_audit_logger()
            audit_context = _create_audit_context(user_info, request_context)
            await audit_logger.log_authorization_success(audit_context, f"role: {role}")

        # Call the original function
        return await func(*args, **kwargs)

    except (AuthenticationError, AuthorizationError):
        raise
    except Exception as e:
        logger.error(f"Unexpected error in role check: {e}")
        raise AuthorizationError(f"Role check failed: {e}")


def _check_role_sync(
    func: Callable,
    role: str,
    tenant_id_param: Optional[str],
    audit: bool,
    *args,
    **kwargs,
):
    """Sync role check implementation."""
    import asyncio

    async def async_check():
        return await _check_role_async(
            func, role, tenant_id_param, audit, *args, **kwargs
        )

    return asyncio.run(async_check())


async def _check_tenant_async(
    func: Callable,
    tenant_id_param: str,
    audit: bool,
    *args,
    **kwargs,
):
    """Async tenant check implementation."""
    try:
        # Extract request context
        request_context = _extract_request_context(*args, **kwargs)
        if not request_context:
            raise AuthenticationError("Unable to extract request context")

        # Get user info from token
        jwt_verifier = get_jwt_verifier()
        user_info = jwt_verifier.get_user_info(request_context["token"])

        # Get target tenant ID from parameters
        target_tenant_id = kwargs.get(tenant_id_param)
        if not target_tenant_id:
            raise AuthorizationError(f"Missing tenant ID parameter: {tenant_id_param}")

        # Check tenant access
        if user_info["tenant_id"] != target_tenant_id:
            if audit:
                audit_logger = get_audit_logger()
                audit_context = _create_audit_context(user_info, request_context)
                await audit_logger.log_tenant_access(
                    audit_context, target_tenant_id, False, "Tenant access denied"
                )
            raise TenantAccessDeniedError(target_tenant_id)

        # Log successful tenant access
        if audit:
            audit_logger = get_audit_logger()
            audit_context = _create_audit_context(user_info, request_context)
            await audit_logger.log_tenant_access(audit_context, target_tenant_id, True)

        # Call the original function
        return await func(*args, **kwargs)

    except (AuthenticationError, AuthorizationError):
        raise
    except Exception as e:
        logger.error(f"Unexpected error in tenant check: {e}")
        raise AuthorizationError(f"Tenant check failed: {e}")


def _check_tenant_sync(
    func: Callable,
    tenant_id_param: str,
    audit: bool,
    *args,
    **kwargs,
):
    """Sync tenant check implementation."""
    import asyncio

    async def async_check():
        return await _check_tenant_async(func, tenant_id_param, audit, *args, **kwargs)

    return asyncio.run(async_check())


async def _check_abac_async(
    func: Callable,
    rule_function: Callable,
    rule_description: str,
    audit: bool,
    *args,
    **kwargs,
):
    """Async ABAC rule check implementation."""
    try:
        # Extract request context
        request_context = _extract_request_context(*args, **kwargs)
        if not request_context:
            raise AuthenticationError("Unable to extract request context")

        # Get user info from token
        jwt_verifier = get_jwt_verifier()
        user_info = jwt_verifier.get_user_info(request_context["token"])

        # Create permission context
        permission_context = PermissionContext(
            user_id=user_info["user_id"],
            username=user_info["username"],
            tenant_id=user_info["tenant_id"],
            roles=user_info["roles"],
            request_attributes=request_context,
        )

        # Evaluate ABAC rule
        rule_result = rule_function(permission_context)

        if not rule_result:
            if audit:
                audit_logger = get_audit_logger()
                audit_context = _create_audit_context(user_info, request_context)
                await audit_logger.log_abac_rule_evaluation(
                    audit_context, "custom_rule", rule_description, False
                )
            raise ABACRuleViolationError(rule_description)

        # Log successful ABAC evaluation
        if audit:
            audit_logger = get_audit_logger()
            audit_context = _create_audit_context(user_info, request_context)
            await audit_logger.log_abac_rule_evaluation(
                audit_context, "custom_rule", rule_description, True
            )

        # Call the original function
        return await func(*args, **kwargs)

    except (AuthenticationError, AuthorizationError):
        raise
    except Exception as e:
        logger.error(f"Unexpected error in ABAC check: {e}")
        raise AuthorizationError(f"ABAC check failed: {e}")


def _check_abac_sync(
    func: Callable,
    rule_function: Callable,
    rule_description: str,
    audit: bool,
    *args,
    **kwargs,
):
    """Sync ABAC rule check implementation."""
    import asyncio

    async def async_check():
        return await _check_abac_async(
            func, rule_function, rule_description, audit, *args, **kwargs
        )

    return asyncio.run(async_check())


# Utility functions


def _is_async_function(func: Callable) -> bool:
    """Check if function is async."""
    import asyncio

    return asyncio.iscoroutinefunction(func)


def _extract_request_context(*args, **kwargs) -> Optional[Dict[str, Any]]:
    """
    Extract request context from function arguments.

    This function needs to be adapted based on your framework (Flask/FastAPI).
    """
    # This is a placeholder implementation
    # In a real implementation, you would extract the request object
    # and get the JWT token from headers

    # For Flask: request.headers.get('Authorization')
    # For FastAPI: request.headers.get('authorization')

    # For now, we'll assume the token is passed as a parameter
    token = kwargs.get("token") or kwargs.get("access_token")
    if not token:
        return None

    return {
        "token": token,
        "ip_address": kwargs.get("ip_address"),
        "user_agent": kwargs.get("user_agent"),
        "endpoint": kwargs.get("endpoint"),
        "method": kwargs.get("method"),
    }


def _create_audit_context(
    user_info: Dict[str, Any], request_context: Dict[str, Any]
) -> AuditContext:
    """Create audit context from user info and request context."""
    return AuditContext(
        user_id=user_info["user_id"],
        username=user_info["username"],
        tenant_id=user_info["tenant_id"],
        ip_address=request_context.get("ip_address"),
        user_agent=request_context.get("user_agent"),
        endpoint=request_context.get("endpoint"),
        method=request_context.get("method"),
    )


async def _get_resource_attributes(
    resource_type: Optional[str],
    resource_id: str,
    tenant_id: str,
) -> Optional[Dict[str, Any]]:
    """
    Get resource attributes for ABAC evaluation.

    This function should be implemented to fetch resource attributes
    from your database or service layer.
    """
    # This is a placeholder implementation
    # In a real implementation, you would query your database
    # to get the resource attributes

    if not resource_type or not resource_id:
        return None

    # Example implementation:
    # from your_service_layer import get_resource_by_id
    # resource = await get_resource_by_id(resource_type, resource_id, tenant_id)
    # return resource.to_dict() if resource else None

    return {
        "id": resource_id,
        "type": resource_type,
        "tenant_id": tenant_id,
        "created_by": "user-123",  # This would come from the database
    }
