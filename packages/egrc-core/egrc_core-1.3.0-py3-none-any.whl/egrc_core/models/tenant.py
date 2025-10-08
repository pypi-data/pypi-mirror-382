from ..core.types import TenantMixin


"""
Tenant-related SQLAlchemy models for EGRC Platform.

This module provides SQLAlchemy models for multi-tenant support
across all EGRC services.
"""

from datetime import datetime

from sqlalchemy import JSON, Boolean, Column, DateTime, ForeignKey, Integer, String
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from .base import BaseModel, NameMixin, SoftDeleteMixin, TimestampMixin


class Tenant(BaseModel, TimestampMixin, SoftDeleteMixin, NameMixin):
    """
    Tenant model for EGRC platform.

    This model represents tenants in the multi-tenant EGRC system.
    """

    __tablename__ = "tenants"

    code = Column(String(100), nullable=False, unique=True, index=True)

    domain = Column(String(255), nullable=True, unique=True, index=True)

    is_active = Column(Boolean, default=True, nullable=False, index=True)

    subscription_plan = Column(String(50), default="basic", nullable=False)

    max_users = Column(Integer, default=10, nullable=False)

    max_storage_gb = Column(Integer, default=1, nullable=False)

    settings = Column(JSON, default=dict, nullable=False)

    contact_email = Column(String(255), nullable=True)

    contact_phone = Column(String(20), nullable=True)

    address = Column(JSON, nullable=True)

    # Relationships
    users = relationship("TenantUser", back_populates="tenant")

    @property
    def is_subscription_active(self) -> bool:
        """Check if tenant subscription is active."""
        return self.is_active and self.subscription_plan != "expired"


class TenantUser(BaseModel, TimestampMixin, TenantMixin):
    """
    Tenant-User relationship model for EGRC platform.

    This model represents the many-to-many relationship between
    tenants and users.
    """

    __tablename__ = "tenant_users"

    user_id = Column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    role = Column(String(50), default="user", nullable=False)

    permissions = Column(JSON, default=list, nullable=False)

    is_active = Column(Boolean, default=True, nullable=False, index=True)

    joined_at = Column(DateTime(timezone=True), default=datetime.utcnow, nullable=False)

    invited_by = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=True)

    # Relationships
    tenant = relationship("Tenant", back_populates="users")
    user = relationship("User", foreign_keys=[user_id])
    inviter = relationship("User", foreign_keys=[invited_by])
