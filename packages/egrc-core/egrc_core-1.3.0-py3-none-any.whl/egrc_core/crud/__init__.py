"""
CRUD operations and abstract base classes for EGRC Platform.

This module provides abstract base classes and common CRUD operations
that can be used across all EGRC services and microservices.
"""

from ..database import (
    FilterBuilder,
    PaginatedResult,
    PaginationParams,
)
from .base import CRUDMixin
from .base_crud import BaseCRUD, CRUDBase
from .filters import QueryFilter
from .repository import AsyncRepository, Repository
from .sorting import SortDirection, SortParams


__all__ = [
    "BaseCRUD",  # Enhanced base CRUD class
    "CRUDBase",  # Concrete implementation
    "CRUDMixin",
    "Repository",
    "AsyncRepository",
    "FilterBuilder",
    "QueryFilter",
    "PaginationParams",
    "PaginatedResult",
    "SortParams",
    "SortDirection",
]
