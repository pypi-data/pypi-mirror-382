"""
Global ID implementation for GraphQL.

This module provides GlobalID functionality for GraphQL Relay-style
global identification across microservices.
"""

import base64

import strawberry


@strawberry.type
class GlobalID:
    """Global ID type for GraphQL Relay-style identification."""

    id: str = strawberry.field(description="The global ID string")

    def __init__(self, id: str):
        self.id = id

    @classmethod
    def from_id(cls, type_name: str, id: str) -> "GlobalID":
        """Create a GlobalID from type name and ID.

        Args:
            type_name: The GraphQL type name
            id: The entity ID

        Returns:
            GlobalID instance
        """
        encoded_id = encode_global_id(type_name, id)
        return cls(id=encoded_id)

    def decode(self) -> tuple[str, str]:
        """Decode the global ID into type name and ID.

        Returns:
            Tuple of (type_name, id)
        """
        return decode_global_id(self.id)


def encode_global_id(type_name: str, id: str) -> str:
    """Encode a type name and ID into a global ID.

    Args:
        type_name: The GraphQL type name
        id: The entity ID

    Returns:
        Encoded global ID string
    """
    # Format: "type:id"
    combined = f"{type_name}:{id}"

    # Base64 encode
    encoded = base64.b64encode(combined.encode("utf-8")).decode("utf-8")

    return encoded


def decode_global_id(global_id: str) -> tuple[str, str]:
    """Decode a global ID into type name and ID.

    Args:
        global_id: The encoded global ID

    Returns:
        Tuple of (type_name, id)

    Raises:
        ValueError: If the global ID is invalid
    """
    try:
        # Base64 decode
        decoded = base64.b64decode(global_id.encode("utf-8")).decode("utf-8")

        # Split on first colon
        if ":" not in decoded:
            raise ValueError("Invalid global ID format")

        type_name, id = decoded.split(":", 1)
        return type_name, id

    except Exception as e:
        raise ValueError(f"Invalid global ID: {global_id}") from e


def resolve_global_id(global_id: str) -> tuple[str, str] | None:
    """Safely resolve a global ID.

    Args:
        global_id: The global ID to resolve

    Returns:
        Tuple of (type_name, id) or None if invalid
    """
    try:
        return decode_global_id(global_id)
    except ValueError:
        return None


class GlobalIDField:
    """Field for handling GlobalID in GraphQL resolvers."""

    @staticmethod
    def encode(type_name: str, id: str) -> GlobalID:
        """Encode an ID as a GlobalID.

        Args:
            type_name: The GraphQL type name
            id: The entity ID

        Returns:
            GlobalID instance
        """
        return GlobalID.from_id(type_name, id)

    @staticmethod
    def decode(global_id: GlobalID) -> tuple[str, str]:
        """Decode a GlobalID.

        Args:
            global_id: The GlobalID to decode

        Returns:
            Tuple of (type_name, id)
        """
        return global_id.decode()

    @staticmethod
    def get_type_name(global_id: GlobalID) -> str:
        """Get the type name from a GlobalID.

        Args:
            global_id: The GlobalID

        Returns:
            The type name
        """
        type_name, _ = global_id.decode()
        return type_name

    @staticmethod
    def get_id(global_id: GlobalID) -> str:
        """Get the ID from a GlobalID.

        Args:
            global_id: The GlobalID

        Returns:
            The ID
        """
        _, id = global_id.decode()
        return id


# Utility functions for common operations
def create_global_id_for_user(user_id: str) -> GlobalID:
    """Create a GlobalID for a user.

    Args:
        user_id: The user ID

    Returns:
        GlobalID for the user
    """
    return GlobalID.from_id("User", user_id)


def create_global_id_for_tenant(tenant_id: str) -> GlobalID:
    """Create a GlobalID for a tenant.

    Args:
        tenant_id: The tenant ID

    Returns:
        GlobalID for the tenant
    """
    return GlobalID.from_id("Tenant", tenant_id)


def create_global_id_for_role(role_id: str) -> GlobalID:
    """Create a GlobalID for a role.

    Args:
        role_id: The role ID

    Returns:
        GlobalID for the role
    """
    return GlobalID.from_id("Role", role_id)


def create_global_id_for_audit_log(audit_log_id: str) -> GlobalID:
    """Create a GlobalID for an audit log.

    Args:
        audit_log_id: The audit log ID

    Returns:
        GlobalID for the audit log
    """
    return GlobalID.from_id("AuditLog", audit_log_id)


# Custom scalar for GlobalID
@strawberry.scalar
class GlobalIDScalar:
    """Custom scalar for GlobalID."""

    @staticmethod
    def serialize(value: GlobalID) -> str:
        """Serialize GlobalID to string."""
        return value.id

    @staticmethod
    def parse_value(value: str) -> GlobalID:
        """Parse string to GlobalID."""
        return GlobalID(id=value)

    @staticmethod
    def parse_literal(ast) -> GlobalID:
        """Parse AST literal to GlobalID."""
        if hasattr(ast, "value"):
            return GlobalID(id=ast.value)
        raise ValueError("Invalid GlobalID literal")
