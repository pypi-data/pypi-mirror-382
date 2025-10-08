"""
Enhanced Abstract Base CRUD Class for EGRC Platform.

This module provides a comprehensive abstract base class for CRUD operations
that can be inherited by all microservices. It includes all common methods
like get_one, get_multi, create_one, create_multi, update_one, update_multi,
delete_one, delete_multi with full type safety and error handling.
"""

import logging
from abc import ABC
from datetime import datetime
from typing import Any, Dict, Generic, List, Optional, Type, TypeVar, Union

from pydantic import BaseModel
from sqlalchemy import and_, delete, func, select, update
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import Session

from ..database.base import PaginatedResult, PaginationParams
from ..exceptions.exceptions import (
    ConflictError,
    DatabaseError,
    NotFoundError,
)
from ..models.base import BaseModel as SQLAlchemyBaseModel


# Type variables for generic CRUD operations
ModelType = TypeVar("ModelType", bound=SQLAlchemyBaseModel)
CreateSchemaType = TypeVar("CreateSchemaType", bound=BaseModel)
UpdateSchemaType = TypeVar("UpdateSchemaType", bound=BaseModel)
IDType = Union[int, str]
FilterType = Dict[str, Any]
OrderByType = Union[str, List[str]]

# Session type union for both sync and async
DBSessionType = Union[Session, AsyncSession]


class BaseCRUD(ABC, Generic[ModelType, CreateSchemaType, UpdateSchemaType]):
    """
    Abstract base class for CRUD operations.

    This class provides a comprehensive interface for database operations
    that can be implemented by all EGRC microservices. It includes:
    - Single and bulk operations for all CRUD operations
    - Advanced filtering, pagination, and sorting
    - Comprehensive error handling and logging
    - Type safety with generics
    - Support for both sync and async operations
    """

    def __init__(self, model: Type[ModelType]):
        """
        Initialize the CRUD instance.

        Args:
            model: The SQLAlchemy model class
        """
        self.model = model
        self.logger = logging.getLogger(
            f"{self.__class__.__module__}.{self.__class__.__name__}"
        )

    # ==================== CREATE OPERATIONS ====================

    async def create_one(
        self, db: DBSessionType, obj_in: CreateSchemaType, **kwargs: Any
    ) -> ModelType:
        """
        Create a single record.

        Args:
            db: Database session
            obj_in: Data to create
            **kwargs: Additional parameters

        Returns:
            Created model instance

        Raises:
            ValidationError: If validation fails
            ConflictError: If duplicate record exists
            DatabaseError: If database operation fails
        """
        try:
            # Convert Pydantic model to dict
            obj_data = obj_in.dict() if hasattr(obj_in, "dict") else obj_in

            # Add any additional fields
            obj_data.update(kwargs)

            # Create model instance
            db_obj = self.model(**obj_data)

            # Add to session
            db.add(db_obj)

            if isinstance(db, AsyncSession):
                await db.commit()
                await db.refresh(db_obj)
            else:
                db.commit()
                db.refresh(db_obj)

            self.logger.info(
                f"Created {
                    self.model.__name__} with ID: {
                    getattr(
                        db_obj,
                        'id',
                        'unknown')}"
            )
            return db_obj

        except IntegrityError as e:
            if isinstance(db, AsyncSession):
                await db.rollback()
            else:
                db.rollback()
            self.logger.error(f"Integrity error creating {self.model.__name__}: {e}")
            raise ConflictError(
                resource_type=self.model.__name__,
                field="id",
                value=obj_data.get("id", "unknown"),
                details={"error": str(e)},
            )
        except Exception as e:
            if isinstance(db, AsyncSession):
                await db.rollback()
            else:
                db.rollback()
            self.logger.error(f"Error creating {self.model.__name__}: {e}")
            raise DatabaseError("create_one", str(e))

    async def create_multi(
        self, db: DBSessionType, objs_in: List[CreateSchemaType], **kwargs: Any
    ) -> List[ModelType]:
        """
        Create multiple records in a single transaction.

        Args:
            db: Database session
            objs_in: List of data to create
            **kwargs: Additional parameters

        Returns:
            List of created model instances

        Raises:
            ValidationError: If validation fails
            ConflictError: If duplicate records exist
            DatabaseError: If database operation fails
        """
        try:
            db_objs = []
            for obj_in in objs_in:
                obj_data = obj_in.dict() if hasattr(obj_in, "dict") else obj_in
                obj_data.update(kwargs)
                db_obj = self.model(**obj_data)
                db_objs.append(db_obj)

            db.add_all(db_objs)

            if isinstance(db, AsyncSession):
                await db.commit()
                for db_obj in db_objs:
                    await db.refresh(db_obj)
            else:
                db.commit()
                for db_obj in db_objs:
                    db.refresh(db_obj)

            self.logger.info(f"Created {len(db_objs)} {self.model.__name__} records")
            return db_objs

        except Exception as e:
            if isinstance(db, AsyncSession):
                await db.rollback()
            else:
                db.rollback()
            self.logger.error(f"Error creating multiple {self.model.__name__}: {e}")
            raise DatabaseError("create_multi", str(e))

    # ==================== READ OPERATIONS ====================

    async def get_one(
        self, db: DBSessionType, id: IDType, include_deleted: bool = False
    ) -> Optional[ModelType]:
        """
        Get a single record by ID.

        Args:
            db: Database session
            id: Record ID
            include_deleted: Whether to include soft-deleted records

        Returns:
            Model instance or None if not found

        Raises:
            DatabaseError: If database operation fails
        """
        try:
            if isinstance(db, AsyncSession):
                query = select(self.model).where(self.model.id == id)

                # Handle soft deletes if model has deleted_at field
                if not include_deleted and hasattr(self.model, "deleted_at"):
                    query = query.where(self.model.deleted_at.is_(None))

                result = await db.execute(query)
                return result.scalar_one_or_none()
            else:
                query = db.query(self.model).filter(self.model.id == id)

                # Handle soft deletes if model has deleted_at field
                if not include_deleted and hasattr(self.model, "deleted_at"):
                    query = query.filter(self.model.deleted_at.is_(None))

                return query.first()

        except Exception as e:
            self.logger.error(f"Error getting {self.model.__name__} with ID {id}: {e}")
            raise DatabaseError("get_one", str(e))

    async def get_one_or_404(
        self, db: DBSessionType, id: IDType, include_deleted: bool = False
    ) -> ModelType:
        """
        Get a single record by ID or raise 404 error.

        Args:
            db: Database session
            id: Record ID
            include_deleted: Whether to include soft-deleted records

        Returns:
            Model instance

        Raises:
            NotFoundError: If record not found
            DatabaseError: If database operation fails
        """
        obj = await self.get_one(db, id, include_deleted)
        if obj is None:
            raise NotFoundError(resource_type=self.model.__name__, identifier=id)
        return obj

    async def get_multi(
        self,
        db: DBSessionType,
        skip: int = 0,
        limit: int = 100,
        filters: Optional[FilterType] = None,
        order_by: Optional[OrderByType] = None,
        include_deleted: bool = False,
    ) -> List[ModelType]:
        """
        Get multiple records with pagination and filtering.

        Args:
            db: Database session
            skip: Number of records to skip
            limit: Maximum number of records to return
            filters: Dictionary of filters
            order_by: Field(s) to order by
            include_deleted: Whether to include soft-deleted records

        Returns:
            List of model instances

        Raises:
            DatabaseError: If database operation fails
        """
        try:
            if isinstance(db, AsyncSession):
                query = select(self.model)

                # Apply filters
                if filters:
                    filter_expressions = self._build_filter_expressions(filters)
                    if filter_expressions:
                        query = query.where(and_(*filter_expressions))

                # Handle soft deletes
                if not include_deleted and hasattr(self.model, "deleted_at"):
                    query = query.where(self.model.deleted_at.is_(None))

                # Apply ordering
                query = self._apply_ordering(query, order_by)

                # Apply pagination
                query = query.offset(skip).limit(limit)

                result = await db.execute(query)
                return result.scalars().all()
            else:
                query = db.query(self.model)

                # Apply filters
                if filters:
                    filter_expressions = self._build_filter_expressions(filters)
                    if filter_expressions:
                        query = query.filter(and_(*filter_expressions))

                # Handle soft deletes
                if not include_deleted and hasattr(self.model, "deleted_at"):
                    query = query.filter(self.model.deleted_at.is_(None))

                # Apply ordering
                query = self._apply_ordering_sync(query, order_by)

                # Apply pagination
                return query.offset(skip).limit(limit).all()

        except Exception as e:
            self.logger.error(f"Error getting multiple {self.model.__name__}: {e}")
            raise DatabaseError("get_multi", str(e))

    async def get_paginated(
        self,
        db: DBSessionType,
        pagination: PaginationParams,
        filters: Optional[FilterType] = None,
        order_by: Optional[OrderByType] = None,
        include_deleted: bool = False,
    ) -> PaginatedResult[ModelType]:
        """
        Get paginated results with filtering and sorting.

        Args:
            db: Database session
            pagination: Pagination parameters
            filters: Dictionary of filters
            order_by: Field(s) to order by
            include_deleted: Whether to include soft-deleted records

        Returns:
            Paginated result

        Raises:
            DatabaseError: If database operation fails
        """
        try:
            if isinstance(db, AsyncSession):
                # Build base query
                query = select(self.model)

                # Apply filters
                if filters:
                    filter_expressions = self._build_filter_expressions(filters)
                    if filter_expressions:
                        query = query.where(and_(*filter_expressions))

                # Handle soft deletes
                if not include_deleted and hasattr(self.model, "deleted_at"):
                    query = query.where(self.model.deleted_at.is_(None))

                # Apply ordering
                query = self._apply_ordering(query, order_by)

                # Get total count
                total = await self._get_total_count_async(db, query)

                # Apply pagination
                offset = (pagination.page - 1) * pagination.size
                paginated_query = query.offset(offset).limit(pagination.size)

                # Execute query
                result = await db.execute(paginated_query)
                items = result.scalars().all()

                return PaginatedResult(
                    items=items, total=total, page=pagination.page, size=pagination.size
                )
            else:
                # Build base query
                query = db.query(self.model)

                # Apply filters
                if filters:
                    filter_expressions = self._build_filter_expressions(filters)
                    if filter_expressions:
                        query = query.filter(and_(*filter_expressions))

                # Handle soft deletes
                if not include_deleted and hasattr(self.model, "deleted_at"):
                    query = query.filter(self.model.deleted_at.is_(None))

                # Apply ordering
                query = self._apply_ordering_sync(query, order_by)

                # Get total count
                total = query.count()

                # Apply pagination
                offset = (pagination.page - 1) * pagination.size
                items = query.offset(offset).limit(pagination.size).all()

                return PaginatedResult(
                    items=items, total=total, page=pagination.page, size=pagination.size
                )

        except Exception as e:
            self.logger.error(f"Error getting paginated {self.model.__name__}: {e}")
            raise DatabaseError("get_paginated", str(e))

    async def count(
        self,
        db: DBSessionType,
        filters: Optional[FilterType] = None,
        include_deleted: bool = False,
    ) -> int:
        """
        Count records matching filters.

        Args:
            db: Database session
            filters: Dictionary of filters
            include_deleted: Whether to include soft-deleted records

        Returns:
            Number of matching records

        Raises:
            DatabaseError: If database operation fails
        """
        try:
            if isinstance(db, AsyncSession):
                query = select(func.count(self.model.id))

                # Apply filters
                if filters:
                    filter_expressions = self._build_filter_expressions(filters)
                    if filter_expressions:
                        query = query.where(and_(*filter_expressions))

                # Handle soft deletes
                if not include_deleted and hasattr(self.model, "deleted_at"):
                    query = query.where(self.model.deleted_at.is_(None))

                result = await db.execute(query)
                return result.scalar() or 0
            else:
                query = db.query(func.count(self.model.id))

                # Apply filters
                if filters:
                    filter_expressions = self._build_filter_expressions(filters)
                    if filter_expressions:
                        query = query.filter(and_(*filter_expressions))

                # Handle soft deletes
                if not include_deleted and hasattr(self.model, "deleted_at"):
                    query = query.filter(self.model.deleted_at.is_(None))

                return query.scalar() or 0

        except Exception as e:
            self.logger.error(f"Error counting {self.model.__name__}: {e}")
            raise DatabaseError("count", str(e))

    # ==================== UPDATE OPERATIONS ====================

    async def update_one(
        self,
        db: DBSessionType,
        db_obj: ModelType,
        obj_in: Union[UpdateSchemaType, Dict[str, Any]],
    ) -> ModelType:
        """
        Update a single record.

        Args:
            db: Database session
            db_obj: Existing model instance
            obj_in: Update data

        Returns:
            Updated model instance

        Raises:
            ValidationError: If validation fails
            DatabaseError: If database operation fails
        """
        try:
            # Convert to dict if Pydantic model
            if hasattr(obj_in, "dict"):
                update_data = obj_in.dict(exclude_unset=True)
            else:
                update_data = obj_in

            # Update fields
            for field, value in update_data.items():
                if hasattr(db_obj, field):
                    setattr(db_obj, field, value)

            # Update timestamp if model has updated_at field
            if hasattr(db_obj, "updated_at"):
                setattr(db_obj, "updated_at", datetime.utcnow())

            if isinstance(db, AsyncSession):
                await db.commit()
                await db.refresh(db_obj)
            else:
                db.commit()
                db.refresh(db_obj)

            self.logger.info(
                f"Updated {
                    self.model.__name__} with ID: {
                    getattr(
                        db_obj,
                        'id',
                        'unknown')}"
            )
            return db_obj

        except Exception as e:
            if isinstance(db, AsyncSession):
                await db.rollback()
            else:
                db.rollback()
            self.logger.error(f"Error updating {self.model.__name__}: {e}")
            raise DatabaseError("update_one", str(e))

    async def update_one_by_id(
        self,
        db: DBSessionType,
        id: IDType,
        obj_in: Union[UpdateSchemaType, Dict[str, Any]],
    ) -> Optional[ModelType]:
        """
        Update a record by ID.

        Args:
            db: Database session
            id: Record ID
            obj_in: Update data

        Returns:
            Updated model instance or None if not found

        Raises:
            ValidationError: If validation fails
            DatabaseError: If database operation fails
        """
        db_obj = await self.get_one(db, id)
        if db_obj:
            return await self.update_one(db, db_obj, obj_in)
        return None

    async def update_multi(
        self,
        db: DBSessionType,
        ids: List[IDType],
        obj_in: Union[UpdateSchemaType, Dict[str, Any]],
    ) -> int:
        """
        Update multiple records by IDs.

        Args:
            db: Database session
            ids: List of record IDs
            obj_in: Update data

        Returns:
            Number of updated records

        Raises:
            ValidationError: If validation fails
            DatabaseError: If database operation fails
        """
        try:
            # Convert to dict if Pydantic model
            if hasattr(obj_in, "dict"):
                update_data = obj_in.dict(exclude_unset=True)
            else:
                update_data = obj_in

            # Add updated_at timestamp if model has it
            if hasattr(self.model, "updated_at"):
                update_data["updated_at"] = datetime.utcnow()

            if isinstance(db, AsyncSession):
                query = (
                    update(self.model)
                    .where(self.model.id.in_(ids))
                    .values(**update_data)
                )
                result = await db.execute(query)
                await db.commit()
                return result.rowcount
            else:
                query = (
                    db.query(self.model)
                    .filter(self.model.id.in_(ids))
                    .update(update_data, synchronize_session=False)
                )
                db.commit()
                return query

        except Exception as e:
            if isinstance(db, AsyncSession):
                await db.rollback()
            else:
                db.rollback()
            self.logger.error(f"Error updating multiple {self.model.__name__}: {e}")
            raise DatabaseError("update_multi", str(e))

    # ==================== DELETE OPERATIONS ====================

    async def delete_one(
        self, db: DBSessionType, id: IDType, soft_delete: bool = True
    ) -> Optional[ModelType]:
        """
        Delete a single record.

        Args:
            db: Database session
            id: Record ID
            soft_delete: Whether to soft delete (if supported)

        Returns:
            Deleted model instance or None if not found

        Raises:
            DatabaseError: If database operation fails
        """
        try:
            db_obj = await self.get_one(db, id)
            if not db_obj:
                return None

            if soft_delete and hasattr(db_obj, "deleted_at"):
                # Soft delete
                setattr(db_obj, "deleted_at", datetime.utcnow())
                if isinstance(db, AsyncSession):
                    await db.commit()
                    await db.refresh(db_obj)
                else:
                    db.commit()
                    db.refresh(db_obj)
            else:
                # Hard delete
                if isinstance(db, AsyncSession):
                    await db.delete(db_obj)
                    await db.commit()
                else:
                    db.delete(db_obj)
                    db.commit()

            self.logger.info(f"Deleted {self.model.__name__} with ID: {id}")
            return db_obj

        except Exception as e:
            if isinstance(db, AsyncSession):
                await db.rollback()
            else:
                db.rollback()
            self.logger.error(f"Error deleting {self.model.__name__}: {e}")
            raise DatabaseError("delete_one", str(e))

    async def delete_multi(
        self, db: DBSessionType, ids: List[IDType], soft_delete: bool = True
    ) -> int:
        """
        Delete multiple records.

        Args:
            db: Database session
            ids: List of record IDs
            soft_delete: Whether to soft delete (if supported)

        Returns:
            Number of deleted records

        Raises:
            DatabaseError: If database operation fails
        """
        try:
            if soft_delete and hasattr(self.model, "deleted_at"):
                # Soft delete
                if isinstance(db, AsyncSession):
                    query = (
                        update(self.model)
                        .where(self.model.id.in_(ids))
                        .values(deleted_at=datetime.utcnow())
                    )
                    result = await db.execute(query)
                    await db.commit()
                    return result.rowcount
                else:
                    query = (
                        db.query(self.model)
                        .filter(self.model.id.in_(ids))
                        .update(
                            {"deleted_at": datetime.utcnow()}, synchronize_session=False
                        )
                    )
                    db.commit()
                    return query
            else:
                # Hard delete
                if isinstance(db, AsyncSession):
                    query = delete(self.model).where(self.model.id.in_(ids))
                    result = await db.execute(query)
                    await db.commit()
                    return result.rowcount
                else:
                    query = db.query(self.model).filter(self.model.id.in_(ids))
                    count = query.count()
                    query.delete(synchronize_session=False)
                    db.commit()
                    return count

        except Exception as e:
            if isinstance(db, AsyncSession):
                await db.rollback()
            else:
                db.rollback()
            self.logger.error(f"Error deleting multiple {self.model.__name__}: {e}")
            raise DatabaseError("delete_multi", str(e))

    # ==================== UTILITY METHODS ====================

    async def exists(
        self, db: DBSessionType, id: IDType, include_deleted: bool = False
    ) -> bool:
        """
        Check if a record exists.

        Args:
            db: Database session
            id: Record ID
            include_deleted: Whether to include soft-deleted records

        Returns:
            True if record exists, False otherwise

        Raises:
            DatabaseError: If database operation fails
        """
        try:
            if isinstance(db, AsyncSession):
                query = select(self.model.id).where(self.model.id == id)

                if not include_deleted and hasattr(self.model, "deleted_at"):
                    query = query.where(self.model.deleted_at.is_(None))

                result = await db.execute(query)
                return result.scalar_one_or_none() is not None
            else:
                query = db.query(self.model.id).filter(self.model.id == id)

                if not include_deleted and hasattr(self.model, "deleted_at"):
                    query = query.filter(self.model.deleted_at.is_(None))

                return query.first() is not None

        except Exception as e:
            self.logger.error(
                f"Error checking existence of {self.model.__name__} with ID {id}: {e}"
            )
            raise DatabaseError("exists", str(e))

    async def get_by_field(
        self,
        db: DBSessionType,
        field_name: str,
        value: Any,
        include_deleted: bool = False,
    ) -> Optional[ModelType]:
        """
        Get a record by a specific field.

        Args:
            db: Database session
            field_name: Name of the field
            value: Value to match
            include_deleted: Whether to include soft-deleted records

        Returns:
            Model instance or None if not found

        Raises:
            DatabaseError: If database operation fails
        """
        try:
            if isinstance(db, AsyncSession):
                query = select(self.model).where(
                    getattr(self.model, field_name) == value
                )

                if not include_deleted and hasattr(self.model, "deleted_at"):
                    query = query.where(self.model.deleted_at.is_(None))

                result = await db.execute(query)
                return result.scalar_one_or_none()
            else:
                query = db.query(self.model).filter(
                    getattr(self.model, field_name) == value
                )

                if not include_deleted and hasattr(self.model, "deleted_at"):
                    query = query.filter(self.model.deleted_at.is_(None))

                return query.first()

        except Exception as e:
            self.logger.error(
                f"Error getting {self.model.__name__} by {field_name}: {e}"
            )
            raise DatabaseError("get_by_field", str(e))

    async def search(
        self,
        db: DBSessionType,
        query: str,
        fields: List[str],
        skip: int = 0,
        limit: int = 100,
        include_deleted: bool = False,
    ) -> List[ModelType]:
        """
        Search records by text query across multiple fields.

        Args:
            db: Database session
            query: Search query string
            fields: List of fields to search in
            skip: Number of records to skip
            limit: Maximum number of records to return
            include_deleted: Whether to include soft-deleted records

        Returns:
            List of matching model instances

        Raises:
            DatabaseError: If database operation fails
        """
        try:
            search_conditions = []

            for field in fields:
                if hasattr(self.model, field):
                    column = getattr(self.model, field)
                    search_conditions.append(column.ilike(f"%{query}%"))

            if not search_conditions:
                return []

            if isinstance(db, AsyncSession):
                sql_query = select(self.model).filter(func.or_(*search_conditions))

                if not include_deleted and hasattr(self.model, "deleted_at"):
                    sql_query = sql_query.where(self.model.deleted_at.is_(None))

                sql_query = sql_query.offset(skip).limit(limit)

                result = await db.execute(sql_query)
                return result.scalars().all()
            else:
                db_query = db.query(self.model).filter(func.or_(*search_conditions))

                if not include_deleted and hasattr(self.model, "deleted_at"):
                    db_query = db_query.filter(self.model.deleted_at.is_(None))

                return db_query.offset(skip).limit(limit).all()

        except Exception as e:
            self.logger.error(f"Error searching {self.model.__name__}: {e}")
            raise DatabaseError("search", str(e))

    # ==================== HELPER METHODS ====================

    def _build_filter_expressions(self, filters: FilterType) -> List[Any]:
        """
        Build filter expressions from filters dictionary.

        Args:
            filters: Dictionary of filters

        Returns:
            List of filter expressions
        """
        expressions = []
        for field, value in filters.items():
            if hasattr(self.model, field):
                column = getattr(self.model, field)
                if isinstance(value, dict):
                    # Handle complex filters like {"gte": 10, "lte": 20}
                    for op, val in value.items():
                        if op == "eq":
                            expressions.append(column == val)
                        elif op == "ne":
                            expressions.append(column != val)
                        elif op == "gt":
                            expressions.append(column > val)
                        elif op == "gte":
                            expressions.append(column >= val)
                        elif op == "lt":
                            expressions.append(column < val)
                        elif op == "lte":
                            expressions.append(column <= val)
                        elif op == "like":
                            expressions.append(column.like(f"%{val}%"))
                        elif op == "ilike":
                            expressions.append(column.ilike(f"%{val}%"))
                        elif op == "in":
                            expressions.append(column.in_(val))
                        elif op == "not_in":
                            expressions.append(~column.in_(val))
                elif isinstance(value, list):
                    expressions.append(column.in_(value))
                else:
                    # Simple equality filter
                    expressions.append(column == value)
        return expressions

    def _apply_ordering(self, query: Any, order_by: Optional[OrderByType]) -> Any:
        """
        Apply ordering to async query.

        Args:
            query: SQLAlchemy query
            order_by: Field(s) to order by

        Returns:
            Query with ordering applied
        """
        if not order_by:
            return query

        if isinstance(order_by, str):
            order_by = [order_by]

        for field in order_by:
            if field.startswith("-"):
                # Descending order
                field_name = field[1:]
                column = getattr(self.model, field_name)
                query = query.order_by(column.desc())
            else:
                # Ascending order
                column = getattr(self.model, field)
                query = query.order_by(column.asc())

        return query

    def _apply_ordering_sync(self, query: Any, order_by: Optional[OrderByType]) -> Any:
        """
        Apply ordering to sync query.

        Args:
            query: SQLAlchemy query
            order_by: Field(s) to order by

        Returns:
            Query with ordering applied
        """
        if not order_by:
            return query

        if isinstance(order_by, str):
            order_by = [order_by]

        for field in order_by:
            if field.startswith("-"):
                # Descending order
                field_name = field[1:]
                column = getattr(self.model, field_name)
                query = query.order_by(column.desc())
            else:
                # Ascending order
                column = getattr(self.model, field)
                query = query.order_by(column.asc())

        return query

    async def _get_total_count_async(self, db: AsyncSession, query: Any) -> int:
        """
        Get total count for async query.

        Args:
            db: Async database session
            query: SQLAlchemy query

        Returns:
            Total count
        """
        count_query = select(func.count()).select_from(query.subquery())
        result = await db.execute(count_query)
        return result.scalar() or 0


class CRUDBase(BaseCRUD[ModelType, CreateSchemaType, UpdateSchemaType]):
    """
    Concrete implementation of BaseCRUD.

    This class can be used directly or as a base class for service-specific
    CRUD implementations. It provides all the common CRUD operations that
    microservices can inherit and use.
    """

    def __init__(self, model: Type[ModelType]):
        super().__init__(model)
