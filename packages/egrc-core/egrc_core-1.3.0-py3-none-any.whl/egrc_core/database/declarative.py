"""
Declarative base for all database models.

This module provides the base class for all SQLAlchemy models
without any dependencies to avoid circular imports.
"""

from sqlalchemy.orm import DeclarativeBase


class Base(DeclarativeBase):
    """Base class for all database models."""
