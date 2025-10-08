"""
Permission-based Authorization System for EGRC Platform.

This module provides comprehensive permission checking, role management,
and ABAC (Attribute-Based Access Control) support for fine-grained authorization.
"""

import logging
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Callable, Dict, List, Optional, Set

from ..cache import SecurityCache


logger = logging.getLogger(__name__)


@dataclass
class PermissionContext:
    """
    Context for permission checking including user, resource, and environment attributes.
    """

    user_id: str
    username: str
    tenant_id: str
    roles: List[str] = field(default_factory=list)
    permissions: List[str] = field(default_factory=list)
    resource_id: Optional[str] = None
    resource_type: Optional[str] = None
    resource_attributes: Dict[str, Any] = field(default_factory=dict)
    environment_attributes: Dict[str, Any] = field(default_factory=dict)
    request_attributes: Dict[str, Any] = field(default_factory=dict)
    timestamp: datetime = field(default_factory=datetime.utcnow)


@dataclass
class Permission:
    """
    Represents a permission with its metadata.
    """

    name: str
    description: str
    resource_type: Optional[str] = None
    actions: List[str] = field(default_factory=list)
    conditions: List[str] = field(default_factory=list)


@dataclass
class Role:
    """
    Represents a role with its permissions.
    """

    name: str
    description: str
    permissions: List[str] = field(default_factory=list)
    tenant_id: Optional[str] = None
    is_system_role: bool = False


class RolePermissionManager:
    """
    Manages role-permission mappings with caching for performance.
    """

    def __init__(self, cache: SecurityCache):
        """
        Initialize role permission manager.

        Args:
            cache: Security cache instance
        """
        self.cache = cache
        self.role_permissions: Dict[str, Set[str]] = {}
        self.permission_roles: Dict[str, Set[str]] = {}
        self.cache_prefix = "role_permissions:"

    def load_role_permissions(self, tenant_id: str) -> None:
        """
        Load role-permission mappings for a tenant.

        Args:
            tenant_id: Tenant identifier
        """
        try:
            # Try to load from cache first
            cached_data = self.cache.get(f"{self.cache_prefix}{tenant_id}")
            if cached_data:
                self.role_permissions.update(cached_data.get("role_permissions", {}))
                self.permission_roles.update(cached_data.get("permission_roles", {}))
                logger.debug(
                    f"Loaded role permissions from cache for tenant: {tenant_id}"
                )
                return

            # Load from database or configuration
            self._load_from_source(tenant_id)

            # Cache the loaded data
            self._cache_role_permissions(tenant_id)

        except Exception as e:
            logger.error(f"Failed to load role permissions for tenant {tenant_id}: {e}")
            raise

    def _load_from_source(self, tenant_id: str) -> None:
        """
        Load role-permission mappings from source (database, config, etc.).

        Args:
            tenant_id: Tenant identifier
        """
        # This would typically load from a database or configuration
        # For now, we'll use a default mapping
        default_mappings = {
            "admin": {
                "action_plan.create",
                "action_plan.read",
                "action_plan.update",
                "action_plan.delete",
                "action_plan.approve",
                "action_plan.close",
                "user.create",
                "user.read",
                "user.update",
                "user.delete",
                "audit.read",
                "tenant.manage",
            },
            "manager": {
                "action_plan.create",
                "action_plan.read",
                "action_plan.update",
                "action_plan.approve",
                "action_plan.close",
                "user.read",
                "user.update",
                "audit.read",
            },
            "maker": {
                "action_plan.create",
                "action_plan.read",
                "action_plan.update",
                "user.read",
            },
            "viewer": {
                "action_plan.read",
                "user.read",
                "audit.read",
            },
        }

        # Build role-permission and permission-role mappings
        for role, permissions in default_mappings.items():
            role_key = f"{tenant_id}:{role}"
            self.role_permissions[role_key] = permissions

            for permission in permissions:
                if permission not in self.permission_roles:
                    self.permission_roles[permission] = set()
                self.permission_roles[permission].add(role_key)

    def _cache_role_permissions(self, tenant_id: str) -> None:
        """
        Cache role-permission mappings.

        Args:
            tenant_id: Tenant identifier
        """
        try:
            # Filter mappings for this tenant
            tenant_role_permissions = {
                k: v
                for k, v in self.role_permissions.items()
                if k.startswith(f"{tenant_id}:")
            }
            tenant_permission_roles = {
                k: v
                for k, v in self.permission_roles.items()
                if any(role.startswith(f"{tenant_id}:") for role in v)
            }

            cache_data = {
                "role_permissions": tenant_role_permissions,
                "permission_roles": tenant_permission_roles,
            }

            self.cache.set(
                f"{self.cache_prefix}{tenant_id}",
                cache_data,
                ttl=3600,  # Cache for 1 hour
            )

        except Exception as e:
            logger.warning(f"Failed to cache role permissions: {e}")

    def get_permissions_for_roles(self, tenant_id: str, roles: List[str]) -> Set[str]:
        """
        Get all permissions for given roles.

        Args:
            tenant_id: Tenant identifier
            roles: List of role names

        Returns:
            Set of permissions
        """
        permissions = set()
        for role in roles:
            role_key = f"{tenant_id}:{role}"
            if role_key in self.role_permissions:
                permissions.update(self.role_permissions[role_key])
        return permissions

    def get_roles_for_permission(self, permission: str) -> Set[str]:
        """
        Get all roles that have a specific permission.

        Args:
            permission: Permission name

        Returns:
            Set of role keys
        """
        return self.permission_roles.get(permission, set())

    def has_permission(self, tenant_id: str, roles: List[str], permission: str) -> bool:
        """
        Check if roles have a specific permission.

        Args:
            tenant_id: Tenant identifier
            roles: List of role names
            permission: Permission to check

        Returns:
            True if permission is granted, False otherwise
        """
        user_permissions = self.get_permissions_for_roles(tenant_id, roles)
        return permission in user_permissions

    def add_role_permission(self, tenant_id: str, role: str, permission: str) -> None:
        """
        Add a permission to a role.

        Args:
            tenant_id: Tenant identifier
            role: Role name
            permission: Permission to add
        """
        role_key = f"{tenant_id}:{role}"
        if role_key not in self.role_permissions:
            self.role_permissions[role_key] = set()

        self.role_permissions[role_key].add(permission)

        if permission not in self.permission_roles:
            self.permission_roles[permission] = set()
        self.permission_roles[permission].add(role_key)

        # Invalidate cache
        self.cache.delete(f"{self.cache_prefix}{tenant_id}")

    def remove_role_permission(
        self, tenant_id: str, role: str, permission: str
    ) -> None:
        """
        Remove a permission from a role.

        Args:
            tenant_id: Tenant identifier
            role: Role name
            permission: Permission to remove
        """
        role_key = f"{tenant_id}:{role}"
        if role_key in self.role_permissions:
            self.role_permissions[role_key].discard(permission)

        if permission in self.permission_roles:
            self.permission_roles[permission].discard(role_key)

        # Invalidate cache
        self.cache.delete(f"{self.cache_prefix}{tenant_id}")


class ABACRule(ABC):
    """
    Abstract base class for ABAC rules.
    """

    @abstractmethod
    def evaluate(self, context: PermissionContext) -> bool:
        """
        Evaluate the ABAC rule against the given context.

        Args:
            context: Permission context

        Returns:
            True if rule allows access, False otherwise
        """
        pass

    @abstractmethod
    def get_description(self) -> str:
        """
        Get human-readable description of the rule.

        Returns:
            Rule description
        """
        pass


class OwnershipRule(ABACRule):
    """
    ABAC rule that checks resource ownership.
    """

    def __init__(self, owner_field: str = "created_by"):
        """
        Initialize ownership rule.

        Args:
            owner_field: Field name that contains the owner ID
        """
        self.owner_field = owner_field

    def evaluate(self, context: PermissionContext) -> bool:
        """
        Check if user owns the resource.

        Args:
            context: Permission context

        Returns:
            True if user owns the resource, False otherwise
        """
        if not context.resource_attributes:
            return False

        owner_id = context.resource_attributes.get(self.owner_field)
        return owner_id == context.user_id

    def get_description(self) -> str:
        """Get rule description."""
        return f"User must own the resource (owner field: {self.owner_field})"


class TenantIsolationRule(ABACRule):
    """
    ABAC rule that enforces tenant isolation.
    """

    def evaluate(self, context: PermissionContext) -> bool:
        """
        Check if resource belongs to user's tenant.

        Args:
            context: Permission context

        Returns:
            True if resource belongs to user's tenant, False otherwise
        """
        if not context.resource_attributes:
            return False

        resource_tenant = context.resource_attributes.get("tenant_id")
        return resource_tenant == context.tenant_id

    def get_description(self) -> str:
        """Get rule description."""
        return "Resource must belong to user's tenant"


class TimeBasedRule(ABACRule):
    """
    ABAC rule that checks time-based conditions.
    """

    def __init__(
        self, start_time: Optional[datetime] = None, end_time: Optional[datetime] = None
    ):
        """
        Initialize time-based rule.

        Args:
            start_time: Access allowed from this time
            end_time: Access allowed until this time
        """
        self.start_time = start_time
        self.end_time = end_time

    def evaluate(self, context: PermissionContext) -> bool:
        """
        Check if current time is within allowed range.

        Args:
            context: Permission context

        Returns:
            True if time is within range, False otherwise
        """
        now = context.timestamp

        if self.start_time and now < self.start_time:
            return False

        if self.end_time and now > self.end_time:
            return False

        return True

    def get_description(self) -> str:
        """Get rule description."""
        return f"Access allowed between {self.start_time} and {self.end_time}"


class CustomRule(ABACRule):
    """
    Custom ABAC rule using a callable function.
    """

    def __init__(
        self, rule_function: Callable[[PermissionContext], bool], description: str
    ):
        """
        Initialize custom rule.

        Args:
            rule_function: Function that evaluates the rule
            description: Human-readable description
        """
        self.rule_function = rule_function
        self.description = description

    def evaluate(self, context: PermissionContext) -> bool:
        """
        Evaluate custom rule.

        Args:
            context: Permission context

        Returns:
            Result of rule function
        """
        try:
            return self.rule_function(context)
        except Exception as e:
            logger.error(f"Error evaluating custom rule: {e}")
            return False

    def get_description(self) -> str:
        """Get rule description."""
        return self.description


class ABACEngine:
    """
    ABAC engine that evaluates multiple rules for authorization decisions.
    """

    def __init__(self):
        """Initialize ABAC engine."""
        self.rules: Dict[str, List[ABACRule]] = {}

    def add_rule(self, permission: str, rule: ABACRule) -> None:
        """
        Add an ABAC rule for a permission.

        Args:
            permission: Permission name
            rule: ABAC rule to add
        """
        if permission not in self.rules:
            self.rules[permission] = []
        self.rules[permission].append(rule)

    def remove_rule(self, permission: str, rule: ABACRule) -> None:
        """
        Remove an ABAC rule for a permission.

        Args:
            permission: Permission name
            rule: ABAC rule to remove
        """
        if permission in self.rules:
            self.rules[permission].remove(rule)

    def evaluate_permission(self, permission: str, context: PermissionContext) -> bool:
        """
        Evaluate all ABAC rules for a permission.

        Args:
            permission: Permission name
            context: Permission context

        Returns:
            True if all rules pass, False otherwise
        """
        if permission not in self.rules:
            return True  # No rules means permission is granted

        for rule in self.rules[permission]:
            if not rule.evaluate(context):
                logger.debug(
                    f"ABAC rule failed for permission {permission}: {
                        rule.get_description()}"
                )
                return False

        return True

    def get_rules_for_permission(self, permission: str) -> List[ABACRule]:
        """
        Get all rules for a permission.

        Args:
            permission: Permission name

        Returns:
            List of ABAC rules
        """
        return self.rules.get(permission, [])


class PermissionChecker:
    """
    Main permission checker that combines role-based and attribute-based authorization.
    """

    def __init__(self, cache: SecurityCache):
        """
        Initialize permission checker.

        Args:
            cache: Security cache instance
        """
        self.cache = cache
        self.role_manager = RolePermissionManager(cache)
        self.abac_engine = ABACEngine()
        self._setup_default_rules()

    def _setup_default_rules(self) -> None:
        """Setup default ABAC rules."""
        # Add ownership rule for action plan approval
        self.abac_engine.add_rule(
            "action_plan.approve",
            CustomRule(
                lambda ctx: ctx.resource_attributes.get("created_by") != ctx.user_id,
                "User cannot approve their own action plan",
            ),
        )

        # Add tenant isolation rule for all permissions
        tenant_rule = TenantIsolationRule()
        for permission in [
            "action_plan.create",
            "action_plan.read",
            "action_plan.update",
            "action_plan.delete",
            "action_plan.approve",
            "action_plan.close",
            "user.create",
            "user.read",
            "user.update",
            "user.delete",
        ]:
            self.abac_engine.add_rule(permission, tenant_rule)

    def check_permission(
        self,
        context: PermissionContext,
        permission: str,
        resource_attributes: Optional[Dict[str, Any]] = None,
    ) -> bool:
        """
        Check if user has permission with ABAC rules.

        Args:
            context: Permission context
            permission: Permission to check
            resource_attributes: Additional resource attributes

        Returns:
            True if permission is granted, False otherwise
        """
        try:
            # Update context with resource attributes
            if resource_attributes:
                context.resource_attributes.update(resource_attributes)

            # Load role permissions for tenant
            self.role_manager.load_role_permissions(context.tenant_id)

            # Check role-based permission
            has_rbac_permission = self.role_manager.has_permission(
                context.tenant_id, context.roles, permission
            )

            if not has_rbac_permission:
                logger.debug(
                    f"RBAC permission denied for user {context.username} "
                    f"permission {permission}"
                )
                return False

            # Check ABAC rules
            abac_allowed = self.abac_engine.evaluate_permission(permission, context)

            if not abac_allowed:
                logger.debug(
                    f"ABAC permission denied for user {context.username} "
                    f"permission {permission}"
                )
                return False

            logger.debug(
                f"Permission granted for user {
                    context.username} permission {permission}"
            )
            return True

        except Exception as e:
            logger.error(f"Error checking permission: {e}")
            return False

    def check_permissions(
        self,
        context: PermissionContext,
        permissions: List[str],
        resource_attributes: Optional[Dict[str, Any]] = None,
        require_all: bool = True,
    ) -> Dict[str, bool]:
        """
        Check multiple permissions.

        Args:
            context: Permission context
            permissions: List of permissions to check
            resource_attributes: Additional resource attributes
            require_all: If True, all permissions must be granted

        Returns:
            Dictionary mapping permission to result
        """
        results = {}
        for permission in permissions:
            results[permission] = self.check_permission(
                context, permission, resource_attributes
            )

        if require_all and not all(results.values()):
            return results

        return results

    def get_user_permissions(
        self,
        tenant_id: str,
        roles: List[str],
        resource_type: Optional[str] = None,
    ) -> Set[str]:
        """
        Get all permissions for a user.

        Args:
            tenant_id: Tenant identifier
            roles: User roles
            resource_type: Optional resource type filter

        Returns:
            Set of permissions
        """
        self.role_manager.load_role_permissions(tenant_id)
        permissions = self.role_manager.get_permissions_for_roles(tenant_id, roles)

        if resource_type:
            permissions = {p for p in permissions if p.startswith(f"{resource_type}.")}

        return permissions

    def add_abac_rule(self, permission: str, rule: ABACRule) -> None:
        """
        Add an ABAC rule for a permission.

        Args:
            permission: Permission name
            rule: ABAC rule to add
        """
        self.abac_engine.add_rule(permission, rule)

    def remove_abac_rule(self, permission: str, rule: ABACRule) -> None:
        """
        Remove an ABAC rule for a permission.

        Args:
            permission: Permission name
            rule: ABAC rule to remove
        """
        self.abac_engine.remove_rule(permission, rule)


# Global permission checker instance
_permission_checker: Optional[PermissionChecker] = None


def get_permission_checker() -> PermissionChecker:
    """
    Get global permission checker instance.

    Returns:
        Permission checker instance
    """
    global _permission_checker
    if _permission_checker is None:
        from ..cache import SecurityCache

        _permission_checker = PermissionChecker(SecurityCache())
    return _permission_checker
