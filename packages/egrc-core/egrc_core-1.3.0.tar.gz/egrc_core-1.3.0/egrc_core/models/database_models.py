from ..core.types import TenantMixin


"""
Base models and mixins for EGRC Platform.

This module provides base model classes and mixins that can be used
across all EGRC services for consistent data modeling.
"""

import uuid
from datetime import datetime
from typing import Any

from sqlalchemy import DateTime, String, Text, func
from sqlalchemy.ext.declarative import declared_attr
from sqlalchemy.orm import Mapped, mapped_column

from ..database.declarative import Base


class TimestampMixin:
    """Mixin to add timestamp fields to models."""

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
        comment="Record creation timestamp",
    )

    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
        comment="Record last update timestamp",
    )

    """Mixin to add tenant support to models."""

    tenant_id: Mapped[str] = mapped_column(
        String(255), nullable=False, index=True, comment="Tenant identifier"
    )

    @declared_attr
    def __table_args__(cls) -> dict[str, Any]:
        """Add tenant-specific table constraints."""
        return {"comment": f"Table for {cls.__name__} with tenant isolation"}


class AuditMixin:
    """Mixin to add audit fields to models."""

    created_by: Mapped[str | None] = mapped_column(
        String(255), nullable=True, comment="User ID who created the record"
    )

    updated_by: Mapped[str | None] = mapped_column(
        String(255), nullable=True, comment="User ID who last updated the record"
    )

    version: Mapped[int] = mapped_column(
        default=1, nullable=False, comment="Record version for optimistic locking"
    )


class SoftDeleteMixin:
    """Mixin to add soft delete functionality to models."""

    is_deleted: Mapped[bool] = mapped_column(
        default=False, nullable=False, index=True, comment="Soft delete flag"
    )

    deleted_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True, comment="Soft delete timestamp"
    )

    deleted_by: Mapped[str | None] = mapped_column(
        String(255), nullable=True, comment="User ID who deleted the record"
    )


class BaseModel(Base, TimestampMixin):
    """Base model class with common fields."""

    __abstract__ = True

    id: Mapped[str] = mapped_column(
        String(255),
        primary_key=True,
        default=lambda: str(uuid.uuid4()),
        comment="Unique identifier",
    )

    def to_dict(self) -> dict[str, Any]:
        """Convert model instance to dictionary.

        Returns:
            Dictionary representation of the model
        """
        return {
            column.name: getattr(self, column.name) for column in self.__table__.columns
        }

    def update_from_dict(self, data: dict[str, Any]) -> None:
        """Update model instance from dictionary.

        Args:
            data: Dictionary with field values to update
        """
        for key, value in data.items():
            if hasattr(self, key):
                setattr(self, key, value)


class TenantModel(BaseModel, TenantMixin, AuditMixin):
    """Base model for tenant-specific entities."""

    __abstract__ = True

    @declared_attr
    def __table_args__(cls) -> dict[str, Any]:
        """Add tenant-specific table constraints."""
        return {"comment": f"Tenant-specific table for {cls.__name__}"}


class SoftDeleteModel(BaseModel, SoftDeleteMixin):
    """Base model with soft delete functionality."""

    __abstract__ = True

    def soft_delete(self, deleted_by: str | None = None) -> None:
        """Perform soft delete on the model instance.

        Args:
            deleted_by: User ID who is performing the delete
        """
        self.is_deleted = True
        self.deleted_at = datetime.utcnow()
        self.deleted_by = deleted_by

    def restore(self) -> None:
        """Restore a soft-deleted model instance."""
        self.is_deleted = False
        self.deleted_at = None
        self.deleted_by = None


class TenantSoftDeleteModel(TenantModel, SoftDeleteMixin):
    """Base model for tenant-specific entities with soft delete."""

    __abstract__ = True

    def soft_delete(self, deleted_by: str | None = None) -> None:
        """Perform soft delete on the model instance.

        Args:
            deleted_by: User ID who is performing the delete
        """
        self.is_deleted = True
        self.deleted_at = datetime.utcnow()
        self.deleted_by = deleted_by

    def restore(self) -> None:
        """Restore a soft-deleted model instance."""
        self.is_deleted = False
        self.deleted_at = None
        self.deleted_by = None


class StatusMixin:
    """Mixin to add status field to models."""

    status: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
        default="active",
        index=True,
        comment="Entity status",
    )


class NameMixin:
    """Mixin to add name and description fields to models."""

    name: Mapped[str] = mapped_column(
        String(255), nullable=False, comment="Entity name"
    )

    description: Mapped[str | None] = mapped_column(
        Text, nullable=True, comment="Entity description"
    )


class CodeMixin:
    """Mixin to add code field to models."""

    code: Mapped[str] = mapped_column(
        String(100), nullable=False, unique=True, index=True, comment="Entity code"
    )


class ExternalIdMixin:
    """Mixin to add external ID field to models."""

    external_id: Mapped[str | None] = mapped_column(
        String(255), nullable=True, index=True, comment="External system identifier"
    )


class MetadataMixin:
    """Mixin to add metadata field to models."""

    metadata: Mapped[dict[str, Any] | None] = mapped_column(
        type_=Text, nullable=True, comment="Additional metadata as JSON"
    )


class PriorityMixin:
    """Mixin to add priority field to models."""

    priority: Mapped[str] = mapped_column(
        String(20),
        nullable=False,
        default="medium",
        index=True,
        comment="Entity priority (low, medium, high, critical)",
    )


class CategoryMixin:
    """Mixin to add category field to models."""

    category: Mapped[str | None] = mapped_column(
        String(100), nullable=True, index=True, comment="Entity category"
    )


class TagsMixin:
    """Mixin to add tags field to models."""

    tags: Mapped[str | None] = mapped_column(
        Text, nullable=True, comment="Comma-separated tags"
    )

    def get_tags_list(self) -> list[str]:
        """Get tags as a list.

        Returns:
            List of tags
        """
        if not self.tags:
            return []
        return [tag.strip() for tag in self.tags.split(",") if tag.strip()]

    def set_tags_list(self, tags: list[str]) -> None:
        """Set tags from a list.

        Args:
            tags: List of tags
        """
        self.tags = ",".join(tags) if tags else None


class ExpiryMixin:
    """Mixin to add expiry fields to models."""

    effective_date: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True, index=True, comment="Effective date"
    )

    expiry_date: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True, index=True, comment="Expiry date"
    )

    def is_active(self) -> bool:
        """Check if entity is currently active.

        Returns:
            True if entity is active, False otherwise
        """
        now = datetime.utcnow()

        if self.effective_date and now < self.effective_date:
            return False

        if self.expiry_date and now > self.expiry_date:
            return False

        return True


class ApprovalMixin:
    """Mixin to add approval fields to models."""

    is_approved: Mapped[bool] = mapped_column(
        default=False, nullable=False, index=True, comment="Approval status"
    )

    approved_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True, comment="Approval timestamp"
    )

    approved_by: Mapped[str | None] = mapped_column(
        String(255), nullable=True, comment="User ID who approved"
    )

    approval_notes: Mapped[str | None] = mapped_column(
        Text, nullable=True, comment="Approval notes"
    )

    def approve(self, approved_by: str, notes: str | None = None) -> None:
        """Approve the entity.

        Args:
            approved_by: User ID who is approving
            notes: Optional approval notes
        """
        self.is_approved = True
        self.approved_at = datetime.utcnow()
        self.approved_by = approved_by
        self.approval_notes = notes

    def reject(self, approved_by: str, notes: str | None = None) -> None:
        """Reject the entity.

        Args:
            approved_by: User ID who is rejecting
            notes: Optional rejection notes
        """
        self.is_approved = False
        self.approved_at = datetime.utcnow()
        self.approved_by = approved_by
        self.approval_notes = notes
