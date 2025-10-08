"""
Common Pydantic schemas for EGRC Platform.

This module provides reusable Pydantic schemas that can be used
across all EGRC services and microservices.
"""

from .audit import AuditLogBase, AuditLogCreate, AuditLogResponse
from .base import BaseSchema, IDMixin, TimestampMixin
from .common import ErrorResponse, HealthCheckResponse, SuccessResponse
from .filters import FilterRequest, FilterResponse
from .pagination import PaginationRequest, PaginationResponse
from .sorting import SortRequest, SortResponse
from .tenant import TenantBase, TenantCreate, TenantResponse, TenantUpdate
from .user import UserBase, UserCreate, UserResponse, UserUpdate


__all__ = [
    "BaseSchema",
    "TimestampMixin",
    "IDMixin",
    "PaginationRequest",
    "PaginationResponse",
    "SortRequest",
    "SortResponse",
    "FilterRequest",
    "FilterResponse",
    "UserBase",
    "UserCreate",
    "UserUpdate",
    "UserResponse",
    "TenantBase",
    "TenantCreate",
    "TenantUpdate",
    "TenantResponse",
    "AuditLogBase",
    "AuditLogCreate",
    "AuditLogResponse",
    "ErrorResponse",
    "SuccessResponse",
    "HealthCheckResponse",
]
