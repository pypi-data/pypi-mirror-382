"""
🏗️ Base SQLAlchemy models for EGRC Platform.

This module provides base SQLAlchemy models and mixins that can be
used across all EGRC services.
"""

import uuid
from datetime import datetime
from typing import Any

from sqlalchemy import JSON, Boolean, Column, DateTime, Integer, String, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.ext.declarative import declared_attr

from ..database.declarative import Base


class BaseModel(Base):
    """
    🏗️ Base model with common fields.

    This model provides common fields and methods for all EGRC models.
    """

    __abstract__ = True

    id = Column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        unique=True,
        nullable=False,
        index=True,
    )

    created_at = Column(
        DateTime(timezone=True), default=datetime.utcnow, nullable=False, index=True
    )

    updated_at = Column(
        DateTime(timezone=True),
        default=datetime.utcnow,
        onupdate=datetime.utcnow,
        nullable=False,
    )

    @declared_attr
    def __tablename__(cls):
        """🔧 Generate table name from class name."""
        return cls.__name__.lower()

    def to_dict(self) -> dict[str, Any]:
        """
        📊 Convert model to dictionary.

        Returns:
            Dictionary representation of the model
        """
        return {
            column.name: getattr(self, column.name) for column in self.__table__.columns
        }

    def update_from_dict(self, data: dict[str, Any]) -> None:
        """
        🔄 Update model from dictionary.

        Args:
            data: Dictionary with data to update
        """
        for key, value in data.items():
            if hasattr(self, key):
                setattr(self, key, value)

    def __repr__(self) -> str:
        """📝 String representation of the model."""
        return f"<{self.__class__.__name__}(id={self.id})>"


class TimestampMixin:
    """
    Mixin for models that include timestamp fields.

    This mixin adds created_at and updated_at timestamp fields
    to models.
    """

    created_at = Column(
        DateTime(timezone=True), default=datetime.utcnow, nullable=False, index=True
    )

    updated_at = Column(
        DateTime(timezone=True),
        default=datetime.utcnow,
        onupdate=datetime.utcnow,
        nullable=False,
    )


class SoftDeleteMixin:
    """
    Mixin for models that support soft deletion.

    This mixin adds soft deletion fields to models.
    """

    is_deleted = Column(Boolean, default=False, nullable=False, index=True)

    deleted_at = Column(DateTime(timezone=True), nullable=True)

    def soft_delete(self) -> None:
        """Mark the record as deleted."""
        self.is_deleted = True
        self.deleted_at = datetime.utcnow()

    def restore(self) -> None:
        """Restore a soft-deleted record."""
        self.is_deleted = False
        self.deleted_at = None

    """
    Mixin for models that are tenant-specific.

    This mixin adds tenant_id field to models.
    """

    tenant_id = Column(UUID(as_uuid=True), nullable=False, index=True)


class UserMixin:
    """
    Mixin for models that track user information.

    This mixin adds created_by and updated_by fields to models.
    """

    created_by = Column(UUID(as_uuid=True), nullable=True, index=True)

    updated_by = Column(UUID(as_uuid=True), nullable=True, index=True)


class VersionMixin:
    """
    Mixin for models that support versioning.

    This mixin adds version field to models.
    """

    version = Column(Integer, default=1, nullable=False)


class MetadataMixin:
    """
    Mixin for models that include metadata.

    This mixin adds metadata field to models.
    """

    metadata = Column(JSON, nullable=True, default=dict)


class StatusMixin:
    """
    Mixin for models that have status fields.

    This mixin adds status field to models.
    """

    status = Column(String(50), default="active", nullable=False, index=True)


class NameMixin:
    """
    Mixin for models that have name fields.

    This mixin adds name and description fields to models.
    """

    name = Column(String(255), nullable=False, index=True)

    description = Column(Text, nullable=True)


class CodeMixin:
    """
    Mixin for models that have code fields.

    This mixin adds code field to models.
    """

    code = Column(String(100), nullable=False, unique=True, index=True)


class SlugMixin:
    """
    Mixin for models that have slug fields.

    This mixin adds slug field to models.
    """

    slug = Column(String(255), nullable=False, unique=True, index=True)


class OrderMixin:
    """
    Mixin for models that have ordering.

    This mixin adds order field to models.
    """

    order = Column(Integer, default=0, nullable=False, index=True)


class AuditMixin:
    """
    Mixin for models that support audit logging.

    This mixin adds audit fields to models.
    """

    audit_id = Column(String(255), nullable=True, index=True)

    audit_action = Column(String(50), nullable=True)

    audit_timestamp = Column(DateTime(timezone=True), nullable=True)


class ValidationMixin:
    """
    Mixin for models that support validation.

    This mixin adds validation fields to models.
    """

    is_valid = Column(Boolean, default=True, nullable=False)

    validation_errors = Column(JSON, nullable=True, default=dict)

    validated_at = Column(DateTime(timezone=True), nullable=True)


class CacheMixin:
    """
    Mixin for models that support caching.

    This mixin adds cache-related fields to models.
    """

    cache_key = Column(String(255), nullable=True, unique=True, index=True)

    cache_expires_at = Column(DateTime(timezone=True), nullable=True)

    cache_version = Column(Integer, default=1, nullable=False)


class SearchMixin:
    """
    Mixin for models that support full-text search.

    This mixin adds search-related fields to models.
    """

    search_vector = Column(Text, nullable=True)

    search_rank = Column(Integer, default=0, nullable=False)

    search_updated_at = Column(DateTime(timezone=True), nullable=True)
