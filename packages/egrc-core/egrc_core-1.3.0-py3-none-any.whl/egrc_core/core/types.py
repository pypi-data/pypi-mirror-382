"""
GraphQL types implementation.

This module provides base GraphQL types and mixins for all EGRC microservices.
"""

from datetime import datetime
from typing import Any

import strawberry
from strawberry.types import Info

from .global_id import GlobalID


@strawberry.type
class BaseNode:
    """Base node type for GraphQL entities."""

    id: GlobalID = strawberry.field(description="Global ID of the entity")
    created_at: datetime = strawberry.field(description="Creation timestamp")
    updated_at: datetime = strawberry.field(description="Last update timestamp")

    def __init__(self, id: str, created_at: datetime, updated_at: datetime):
        self.id = GlobalID(id=id)
        self.created_at = created_at
        self.updated_at = updated_at


@strawberry.type
class TimestampMixin:
    """Mixin for timestamp fields."""

    created_at: datetime = strawberry.field(description="Creation timestamp")
    updated_at: datetime = strawberry.field(description="Last update timestamp")


@strawberry.type
class TenantIdMixin:
    """Mixin for tenant-related fields."""
    tenant_id: str = strawberry.field(description="Tenant ID")


@strawberry.type
class AuditMixin:
    """Mixin for audit fields."""

    created_by: str | None = strawberry.field(
        description="User who created the record"
    )
    updated_by: str | None = strawberry.field(
        description="User who last updated the record"
    )
    version: int = strawberry.field(description="Record version")


@strawberry.type
class SoftDeleteMixin:
    """Mixin for soft delete fields."""

    is_deleted: bool = strawberry.field(description="Soft delete flag")
    deleted_at: datetime | None = strawberry.field(description="Deletion timestamp")
    deleted_by: str | None = strawberry.field(description="User who deleted the record")


@strawberry.type
class StatusMixin:
    """Mixin for status field."""

    status: str = strawberry.field(description="Entity status")


@strawberry.type
class NameMixin:
    """Mixin for name and description fields."""

    name: str = strawberry.field(description="Entity name")
    description: str | None = strawberry.field(description="Entity description")


@strawberry.type
class CodeMixin:
    """Mixin for code field."""

    code: str = strawberry.field(description="Entity code")


@strawberry.type
class ExternalIdMixin:
    """Mixin for external ID field."""

    external_id: str | None = strawberry.field(description="External system identifier")


@strawberry.type
class MetadataMixin:
    """Mixin for metadata field."""

    metadata: dict[str, Any] | None = strawberry.field(
        description="Additional metadata"
    )


@strawberry.type
class PriorityMixin:
    """Mixin for priority field."""

    priority: str = strawberry.field(description="Entity priority")


@strawberry.type
class CategoryMixin:
    """Mixin for category field."""

    category: str | None = strawberry.field(description="Entity category")


@strawberry.type
class TagsMixin:
    """Mixin for tags field."""

    tags: str | None = strawberry.field(description="Comma-separated tags")

    @strawberry.field
    def tags_list(self) -> list[str]:
        """Get tags as a list."""
        if not self.tags:
            return []
        return [tag.strip() for tag in self.tags.split(",") if tag.strip()]


@strawberry.type
class ExpiryMixin:
    """Mixin for expiry fields."""

    effective_date: datetime | None = strawberry.field(description="Effective date")
    expiry_date: datetime | None = strawberry.field(description="Expiry date")

    @strawberry.field
    def is_active(self) -> bool:
        """Check if entity is currently active."""
        now = datetime.utcnow()

        if self.effective_date and now < self.effective_date:
            return False

        if self.expiry_date and now > self.expiry_date:
            return False

        return True


@strawberry.type
class ApprovalMixin:
    """Mixin for approval fields."""

    is_approved: bool = strawberry.field(description="Approval status")
    approved_at: datetime | None = strawberry.field(description="Approval timestamp")
    approved_by: str | None = strawberry.field(description="User who approved")
    approval_notes: str | None = strawberry.field(description="Approval notes")



@strawberry.input
class TimestampInput:
    """Input type for timestamp fields."""

    created_at: datetime | None = strawberry.field(description="Creation timestamp")
    updated_at: datetime | None = strawberry.field(description="Last update timestamp")


@strawberry.input
class TenantInput:
    """Input type for tenant-related fields."""

    tenant_id: str = strawberry.field(description="Tenant ID")


@strawberry.input
class AuditInput:
    """Input type for audit fields."""

    created_by: str | None = strawberry.field(description="User who created the record")
    updated_by: str | None = strawberry.field(
        description="User who last updated the record"
    )
    version: int | None = strawberry.field(description="Record version")


@strawberry.input
class SoftDeleteInput:
    """Input type for soft delete fields."""

    is_deleted: bool | None = strawberry.field(description="Soft delete flag")
    deleted_at: datetime | None = strawberry.field(description="Deletion timestamp")
    deleted_by: str | None = strawberry.field(description="User who deleted the record")


@strawberry.input
class StatusInput:
    """Input type for status field."""

    status: str = strawberry.field(description="Entity status")


@strawberry.input
class NameInput:
    """Input type for name and description fields."""

    name: str = strawberry.field(description="Entity name")
    description: str | None = strawberry.field(description="Entity description")


@strawberry.input
class CodeInput:
    """Input type for code field."""

    code: str = strawberry.field(description="Entity code")


@strawberry.input
class ExternalIdInput:
    """Input type for external ID field."""

    external_id: str | None = strawberry.field(description="External system identifier")


@strawberry.input
class MetadataInput:
    """Input type for metadata field."""

    metadata: dict[str, Any] | None = strawberry.field(
        description="Additional metadata"
    )


@strawberry.input
class PriorityInput:
    """Input type for priority field."""

    priority: str = strawberry.field(description="Entity priority")


@strawberry.input
class CategoryInput:
    """Input type for category field."""

    category: str | None = strawberry.field(description="Entity category")


@strawberry.input
class TagsInput:
    """Input type for tags field."""

    tags: str | None = strawberry.field(description="Comma-separated tags")
    tags_list: list[str] | None = strawberry.field(description="Tags as a list")


@strawberry.input
class ExpiryInput:
    """Input type for expiry fields."""

    effective_date: datetime | None = strawberry.field(description="Effective date")
    expiry_date: datetime | None = strawberry.field(description="Expiry date")


@strawberry.input
class ApprovalInput:
    """Input type for approval fields."""

    is_approved: bool = strawberry.field(description="Approval status")
    approved_at: datetime | None = strawberry.field(description="Approval timestamp")
    approved_by: str | None = strawberry.field(description="User who approved")
    approval_notes: str | None = strawberry.field(description="Approval notes")


# Response types
@strawberry.type
class BaseResponse:
    """Base response type."""

    success: bool = strawberry.field(description="Success status")
    message: str | None = strawberry.field(description="Response message")


@strawberry.type
class ErrorResponse(BaseResponse):
    """Error response type."""

    error_code: str = strawberry.field(description="Error code")
    details: dict[str, Any] | None = strawberry.field(description="Error details")


@strawberry.type
class ValidationError:
    """Validation error type."""

    field: str = strawberry.field(description="Field name")
    message: str = strawberry.field(description="Error message")
    value: Any | None = strawberry.field(description="Invalid value")


@strawberry.type
class ValidationErrorResponse(BaseResponse):
    """Validation error response type."""

    errors: list[ValidationError] = strawberry.field(description="Validation errors")


# Utility functions for type conversion
def convert_model_to_graphql_type(model: Any, graphql_type: type) -> Any:
    """Convert a SQLAlchemy model to a GraphQL type.

    Args:
        model: SQLAlchemy model instance
        graphql_type: GraphQL type class

    Returns:
        GraphQL type instance
    """
    # Get all fields from the model
    model_dict = model.to_dict() if hasattr(model, "to_dict") else model.__dict__

    # Filter out SQLAlchemy internal fields
    filtered_dict = {k: v for k, v in model_dict.items() if not k.startswith("_")}

    # Create GraphQL type instance
    return graphql_type(**filtered_dict)


def convert_graphql_input_to_dict(input_obj: Any) -> dict[str, Any]:
    """Convert a GraphQL input object to a dictionary.

    Args:
        input_obj: GraphQL input object

    Returns:
        Dictionary representation
    """
    if hasattr(input_obj, "__dict__"):
        return {k: v for k, v in input_obj.__dict__.items() if v is not None}
    return {}


def get_global_id_from_info(info: Info, field_name: str = "id") -> str | None:
    """Get global ID from GraphQL info.

    Args:
        info: GraphQL info object
        field_name: Field name to get ID from

    Returns:
        Global ID string or None
    """
    if hasattr(info, "variable_values") and field_name in info.variable_values:
        return info.variable_values[field_name]
    return None


def get_tenant_id_from_info(info: Info) -> str | None:
    """Get tenant ID from GraphQL info.

    Args:
        info: GraphQL info object

    Returns:
        Tenant ID or None
    """
    if hasattr(info, "context") and hasattr(info.context, "tenant_id"):
        return info.context.tenant_id
    return None


def get_user_id_from_info(info: Info) -> str | None:
    """Get user ID from GraphQL info.

    Args:
        info: GraphQL info object

    Returns:
        User ID or None
    """
    if hasattr(info, "context") and hasattr(info.context, "user"):
        return info.context.user.get("id")
    return None
