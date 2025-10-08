"""
Database module for EGRC Core.

This module provides database-related functionality including models,
base classes, pagination, sorting, and filtering capabilities.
"""

# Note: filters, models, pagination, and sorting modules are defined in base.py
from .base import (
    FilterBuilder,
    PaginatedResult,
    PaginationHelper,
    PaginationParams,
    parse_filter_dict,
)
from .database import (
    get_async_db_session,
    get_async_session,
    get_db_session,
    get_main_session,
    main_engine,
    main_session_maker,
)
from .declarative import Base


__all__ = [
    # Database
    "Base",
    "get_main_session",
    "get_async_session",
    "get_async_db_session",
    "get_db_session",
    "main_session_maker",
    "main_engine",
    # Pagination
    "PaginationParams",
    "PaginatedResult",
    "PaginationHelper",
    # Filtering
    "FilterBuilder",
    "parse_filter_dict",
]
