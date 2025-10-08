from sqlalchemy import select


"""
Repository pattern implementation for EGRC Platform.

This module provides repository classes that implement the repository pattern
for data access across all EGRC services.
"""

from typing import Any, TypeVar
from uuid import UUID

from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import Session

from .base_crud import BaseCRUD
from ..database.base import PaginatedResult, PaginationParams, BaseModel as SQLAlchemyBaseModel
from ..exceptions.exceptions import NotFoundError
from .filters import FilterParams
from .sorting import SortParams


# Type variables
ModelType = TypeVar("ModelType", bound=SQLAlchemyBaseModel)
CreateSchemaType = TypeVar("CreateSchemaType", bound=BaseModel)
UpdateSchemaType = TypeVar("UpdateSchemaType", bound=BaseModel)


class Repository(BaseCRUD[ModelType, CreateSchemaType, UpdateSchemaType]):
    """
    Synchronous repository implementation.

    This class provides synchronous CRUD operations using SQLAlchemy sessions.
    """

    def __init__(self, model: type[ModelType]):
        """
        Initialize repository.

        Args:
            model: SQLAlchemy model class
        """
        super().__init__(model)

    def create(self, db: Session, obj_in: CreateSchemaType, **kwargs: Any) -> ModelType:
        """
        Create a new record.

        Args:
            db: Database session
            obj_in: Data to create
            **kwargs: Additional parameters

        Returns:
            Created model instance
        """
        if isinstance(obj_in, dict):
            create_data = obj_in
        else:
            create_data = obj_in.dict(exclude_unset=True)

        # Add any additional data from kwargs
        create_data.update(kwargs)

        db_obj = self.model(**create_data)
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj

    def get(self, db: Session, id: int | str | UUID, **kwargs: Any) -> ModelType | None:
        """
        Get a record by ID.

        Args:
            db: Database session
            id: Record ID
            **kwargs: Additional parameters

        Returns:
            Model instance or None
        """
        return db.query(self.model).filter(self.model.id == id).first()

    def get_multi(
        self, db: Session, skip: int = 0, limit: int = 100, **kwargs: Any
    ) -> list[ModelType]:
        """
        Get multiple records with pagination.

        Args:
            db: Database session
            skip: Number of records to skip
            limit: Maximum number of records to return
            **kwargs: Additional parameters

        Returns:
            List of model instances
        """
        return db.query(self.model).offset(skip).limit(limit).all()

    def update(
        self,
        db: Session,
        db_obj: ModelType,
        obj_in: UpdateSchemaType | dict[str, Any],
        **kwargs: Any,
    ) -> ModelType:
        """
        Update a record.

        Args:
            db: Database session
            db_obj: Existing model instance
            obj_in: Data to update
            **kwargs: Additional parameters

        Returns:
            Updated model instance
        """
        if isinstance(obj_in, dict):
            update_data = obj_in
        else:
            update_data = obj_in.dict(exclude_unset=True)

        # Add any additional data from kwargs
        update_data.update(kwargs)

        for field, value in update_data.items():
            if hasattr(db_obj, field):
                setattr(db_obj, field, value)

        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj

    def delete(self, db: Session, id: int | str | UUID, **kwargs: Any) -> ModelType:
        """
        Delete a record.

        Args:
            db: Database session
            id: Record ID
            **kwargs: Additional parameters

        Returns:
            Deleted model instance
        """
        obj = self.get_one(db, id, **kwargs)
        if obj is None:
            raise NotFoundError(resource=self.model.__name__, identifier=str(id))

        db.delete(obj)
        db.commit()
        return obj

    def count(self, db: Session, **kwargs: Any) -> int:
        """
        Count total number of records.

        Args:
            db: Database session
            **kwargs: Additional parameters

        Returns:
            Total count
        """
        return db.query(self.model).count()

    def search(
        self,
        db: Session,
        query: str,
        fields: list[str],
        skip: int = 0,
        limit: int = 100,
        **kwargs: Any,
    ) -> list[ModelType]:
        """
        Search records by text query.

        Args:
            db: Database session
            query: Search query
            fields: Fields to search in
            skip: Number of records to skip
            limit: Maximum number of records to return
            **kwargs: Additional parameters

        Returns:
            List of matching model instances
        """
        search_conditions = []

        for field in fields:
            if hasattr(self.model, field):
                column = getattr(self.model, field)
                search_conditions.append(column.ilike(f"%{query}%"))

        if not search_conditions:
            return []

        return (
            db.query(self.model)
            # .filter(func.or_(*search_conditions))
            .offset(skip)
            .limit(limit)
            .all()
        )

    def get_paginated(
        self,
        db: Session,
        pagination: PaginationParams,
        filters: FilterParams | None = None,
        sort_params: SortParams | None = None,
        **kwargs: Any,
    ) -> PaginatedResult[ModelType]:
        """
        Get paginated results with filters and sorting.

        Args:
            db: Database session
            pagination: Pagination parameters
            filters: Filter parameters
            sort_params: Sort parameters
            **kwargs: Additional parameters

        Returns:
            Paginated result
        """
        query = db.query(self.model)

        # Apply filters
        if filters:
            filter_builder = filters.to_filter_builder(self.model)
            condition = filter_builder.build(self.model)
            if condition is not None:
                query = query.filter(condition)

        # Apply sorting
        if sort_params:
            for field, direction in sort_params.items():
                if hasattr(self.model, field):
                    column = getattr(self.model, field)
                    if direction.value == "desc":
                        query = query.order_by(column.desc())
                    else:
                        query = query.order_by(column.asc())

        # Get total count
        total = query.count()

        # Apply pagination
        items = query.offset(pagination.skip).limit(pagination.limit).all()

        return PaginatedResult(
            items=items,
            total=total,
            page=pagination.page,
            page_size=pagination.page_size,
        )


class AsyncRepository(BaseCRUD[ModelType, CreateSchemaType, UpdateSchemaType]):
    """
    Asynchronous repository implementation.

    This class provides asynchronous CRUD operations using SQLAlchemy async sessions.
    """

    def __init__(self, model: type[ModelType]):
        """
        Initialize async repository.

        Args:
            model: SQLAlchemy model class
        """
        super().__init__(model)

    async def create(
        self, db: AsyncSession, obj_in: CreateSchemaType, **kwargs: Any
    ) -> ModelType:
        """
        Create a new record.

        Args:
            db: Async database session
            obj_in: Data to create
            **kwargs: Additional parameters

        Returns:
            Created model instance
        """
        if isinstance(obj_in, dict):
            create_data = obj_in
        else:
            create_data = obj_in.dict(exclude_unset=True)

        # Add any additional data from kwargs
        create_data.update(kwargs)

        db_obj = self.model(**create_data)
        db.add(db_obj)
        await db.commit()
        await db.refresh(db_obj)
        return db_obj

    async def get(
        self, db: AsyncSession, id: int | str | UUID, **kwargs: Any
    ) -> ModelType | None:
        """
        Get a record by ID.

        Args:
            db: Async database session
            id: Record ID
            **kwargs: Additional parameters

        Returns:
            Model instance or None
        """
        result = await db.execute(select(self.model).filter(self.model.id == id))
        return result.scalar_one_or_none()

    async def get_multi(
        self, db: AsyncSession, skip: int = 0, limit: int = 100, **kwargs: Any
    ) -> list[ModelType]:
        """
        Get multiple records with pagination.

        Args:
            db: Async database session
            skip: Number of records to skip
            limit: Maximum number of records to return
            **kwargs: Additional parameters

        Returns:
            List of model instances
        """
        result = await db.execute(select(self.model).offset(skip).limit(limit))
        return result.scalars().all()

    async def update(
        self,
        db: AsyncSession,
        db_obj: ModelType,
        obj_in: UpdateSchemaType | dict[str, Any],
        **kwargs: Any,
    ) -> ModelType:
        """
        Update a record.

        Args:
            db: Async database session
            db_obj: Existing model instance
            obj_in: Data to update
            **kwargs: Additional parameters

        Returns:
            Updated model instance
        """
        if isinstance(obj_in, dict):
            update_data = obj_in
        else:
            update_data = obj_in.dict(exclude_unset=True)

        # Add any additional data from kwargs
        update_data.update(kwargs)

        for field, value in update_data.items():
            if hasattr(db_obj, field):
                setattr(db_obj, field, value)

        db.add(db_obj)
        await db.commit()
        await db.refresh(db_obj)
        return db_obj

    async def delete(
        self, db: AsyncSession, id: int | str | UUID, **kwargs: Any
    ) -> ModelType:
        """
        Delete a record.

        Args:
            db: Async database session
            id: Record ID
            **kwargs: Additional parameters

        Returns:
            Deleted model instance
        """
        obj = await self.get_one(db, id, **kwargs)
        if obj is None:
            raise NotFoundError(resource=self.model.__name__, identifier=str(id))

        await db.delete(obj)
        await db.commit()
        return obj

    async def count(self, db: AsyncSession, **kwargs: Any) -> int:
        """
        Count total number of records.

        Args:
            db: Async database session
            **kwargs: Additional parameters

        Returns:
            Total count
        """
        # result = await db.execute(select(func.count(self.model.id)))
        # return result.scalar()

    async def search(
        self,
        db: AsyncSession,
        query: str,
        fields: list[str],
        skip: int = 0,
        limit: int = 100,
        **kwargs: Any,
    ) -> list[ModelType]:
        """
        Search records by text query.

        Args:
            db: Async database session
            query: Search query
            fields: Fields to search in
            skip: Number of records to skip
            limit: Maximum number of records to return
            **kwargs: Additional parameters

        Returns:
            List of matching model instances
        """
        search_conditions = []

        for field in fields:
            if hasattr(self.model, field):
                column = getattr(self.model, field)
                search_conditions.append(column.ilike(f"%{query}%"))

        if not search_conditions:
            return []

        result = await db.execute(
            select(self.model)
            # .filter(func.or_(*search_conditions))
            .offset(skip).limit(limit)
        )
        return result.scalars().all()

    async def get_paginated(
        self,
        db: AsyncSession,
        pagination: PaginationParams,
        filters: FilterParams | None = None,
        sort_params: SortParams | None = None,
        **kwargs: Any,
    ) -> PaginatedResult[ModelType]:
        """
        Get paginated results with filters and sorting.

        Args:
            db: Async database session
            pagination: Pagination parameters
            filters: Filter parameters
            sort_params: Sort parameters
            **kwargs: Additional parameters

        Returns:
            Paginated result
        """
        query = select(self.model)

        # Apply filters
        if filters:
            filter_builder = filters.to_filter_builder(self.model)
            condition = filter_builder.build(self.model)
            if condition is not None:
                query = query.filter(condition)

        # Apply sorting
        if sort_params:
            for field, direction in sort_params.items():
                if hasattr(self.model, field):
                    column = getattr(self.model, field)
                    if direction.value == "desc":
                        query = query.order_by(column.desc())
                    else:
                        query = query.order_by(column.asc())

        # Get total count
        # count_query = select(func.count(self.model.id))
        if filters:
            filter_builder = filters.to_filter_builder(self.model)
            condition = filter_builder.build(self.model)
            if condition is not None:
                pass
                # count_query = count_query.filter(condition)

                #         total_result = await db.execute(count_query)
                #         total = total_result.scalar()
                #
                #         # Apply pagination
                #         result = await db.execute(query.offset(pagination.skip).limit(pagination.limit))
                #         items = result.scalars().all()
                #
                #         return PaginatedResult(
                #             items=items,
                #             total=total,
                #             page=pagination.page,
                #             page_size=pagination.page_size,
                #                 #         )
