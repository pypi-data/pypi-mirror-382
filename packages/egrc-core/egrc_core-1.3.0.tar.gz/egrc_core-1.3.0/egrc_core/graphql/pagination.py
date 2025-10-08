"""
GraphQL pagination implementation.

This module provides pagination functionality for GraphQL queries
with support for cursor-based and offset-based pagination.
"""

from typing import Any, Generic, TypeVar

import strawberry
from sqlalchemy import func
from sqlalchemy.orm import Query


T = TypeVar("T")


@strawberry.type
class PageInfo:
    """Page information for pagination."""

    has_next_page: bool = strawberry.field(description="Whether there is a next page")
    has_previous_page: bool = strawberry.field(
        description="Whether there is a previous page"
    )
    start_cursor: str | None = strawberry.field(description="Cursor for the first item")
    end_cursor: str | None = strawberry.field(description="Cursor for the last item")


@strawberry.type
class Edge(Generic[T]):
    """Edge type for cursor-based pagination."""

    node: T = strawberry.field(description="The item")
    cursor: str = strawberry.field(description="Cursor for this item")


@strawberry.type
class Connection(Generic[T]):
    """Connection type for cursor-based pagination."""

    edges: list[Edge[T]] = strawberry.field(description="List of edges")
    page_info: PageInfo = strawberry.field(description="Page information")
    total_count: int | None = strawberry.field(description="Total number of items")


@strawberry.input
class PaginationArgs:
    """Pagination arguments input type."""

    first: int | None = strawberry.field(
        default=None, description="Number of items to return from the beginning"
    )
    last: int | None = strawberry.field(
        default=None, description="Number of items to return from the end"
    )
    after: str | None = strawberry.field(
        default=None, description="Cursor to start after"
    )
    before: str | None = strawberry.field(
        default=None, description="Cursor to end before"
    )


@strawberry.input
class OffsetPaginationArgs:
    """Offset-based pagination arguments input type."""

    page: int = strawberry.field(default=1, description="Page number (1-based)")
    limit: int = strawberry.field(default=50, description="Number of items per page")
    max_limit: int = strawberry.field(default=1000, description="Maximum limit allowed")


@strawberry.type
class OffsetPageInfo:
    """Page information for offset-based pagination."""

    page: int = strawberry.field(description="Current page number")
    limit: int = strawberry.field(description="Items per page")
    total_count: int = strawberry.field(description="Total number of items")
    total_pages: int = strawberry.field(description="Total number of pages")
    has_next_page: bool = strawberry.field(description="Whether there is a next page")
    has_previous_page: bool = strawberry.field(
        description="Whether there is a previous page"
    )


@strawberry.type
class OffsetConnection(Generic[T]):
    """Connection type for offset-based pagination."""

    items: list[T] = strawberry.field(description="List of items")
    page_info: OffsetPageInfo = strawberry.field(description="Page information")


class PaginationHelper:
    """Helper class for pagination operations."""

    @staticmethod
    def create_cursor(item_id: str, sort_value: Any = None) -> str:
        """Create a cursor for an item.

        Args:
            item_id: Item ID
            sort_value: Sort value for cursor

        Returns:
            Cursor string
        """
        if sort_value is not None:
            return f"{item_id}:{sort_value}"
        return item_id

    @staticmethod
    def parse_cursor(cursor: str) -> tuple[str, Any | None]:
        """Parse a cursor into item ID and sort value.

        Args:
            cursor: Cursor string

        Returns:
            Tuple of (item_id, sort_value)
        """
        if ":" in cursor:
            item_id, sort_value = cursor.split(":", 1)
            return item_id, sort_value
        return cursor, None

    @staticmethod
    def apply_cursor_pagination(
        query: Query, pagination_args: PaginationArgs, sort_field: str = "id"
    ) -> Query:
        """Apply cursor-based pagination to query.

        Args:
            query: SQLAlchemy query
            pagination_args: Pagination arguments
            sort_field: Field to sort by for cursor

        Returns:
            Modified query
        """
        # Apply cursor filtering
        if pagination_args.after:
            item_id, sort_value = PaginationHelper.parse_cursor(pagination_args.after)
            sort_column = getattr(query.column_descriptions[0]["entity"], sort_field)
            if sort_value is not None:
                query = query.filter(sort_column > sort_value)
            else:
                query = query.filter(sort_column > item_id)

        if pagination_args.before:
            item_id, sort_value = PaginationHelper.parse_cursor(pagination_args.before)
            sort_column = getattr(query.column_descriptions[0]["entity"], sort_field)
            if sort_value is not None:
                query = query.filter(sort_column < sort_value)
            else:
                query = query.filter(sort_column < item_id)

        # Apply limit
        if pagination_args.first:
            query = query.limit(pagination_args.first)
        elif pagination_args.last:
            query = query.limit(pagination_args.last)

        return query

    @staticmethod
    def apply_offset_pagination(
        query: Query, pagination_args: OffsetPaginationArgs
    ) -> Query:
        """Apply offset-based pagination to query.

        Args:
            query: SQLAlchemy query
            pagination_args: Pagination arguments

        Returns:
            Modified query
        """
        # Validate and limit the limit
        limit = min(pagination_args.limit, pagination_args.max_limit)

        # Calculate offset
        offset = (pagination_args.page - 1) * limit

        # Apply pagination
        query = query.offset(offset).limit(limit)

        return query

    @staticmethod
    def get_total_count(query: Query) -> int:
        """Get total count for a query.

        Args:
            query: SQLAlchemy query

        Returns:
            Total count
        """
        # Create a count query
        count_query = query.statement.with_only_columns([func.count()])
        return query.session.execute(count_query).scalar()

    @staticmethod
    def create_page_info(
        items: list[Any],
        pagination_args: PaginationArgs,
        total_count: int | None = None,
    ) -> PageInfo:
        """Create page info for cursor-based pagination.

        Args:
            items: List of items
            pagination_args: Pagination arguments
            total_count: Total count (optional)

        Returns:
            PageInfo instance
        """
        has_next_page = False
        has_previous_page = False

        if pagination_args.first and len(items) == pagination_args.first:
            has_next_page = True

        if pagination_args.last and len(items) == pagination_args.last:
            has_previous_page = True

        if pagination_args.after:
            has_previous_page = True

        if pagination_args.before:
            has_next_page = True

        start_cursor = None
        end_cursor = None

        if items:
            start_cursor = PaginationHelper.create_cursor(items[0].id)
            end_cursor = PaginationHelper.create_cursor(items[-1].id)

        return PageInfo(
            has_next_page=has_next_page,
            has_previous_page=has_previous_page,
            start_cursor=start_cursor,
            end_cursor=end_cursor,
        )

    @staticmethod
    def create_offset_page_info(
        items: list[Any], pagination_args: OffsetPaginationArgs, total_count: int
    ) -> OffsetPageInfo:
        """Create page info for offset-based pagination.

        Args:
            items: List of items
            pagination_args: Pagination arguments
            total_count: Total count

        Returns:
            OffsetPageInfo instance
        """
        limit = min(pagination_args.limit, pagination_args.max_limit)
        total_pages = (total_count + limit - 1) // limit

        has_next_page = pagination_args.page < total_pages
        has_previous_page = pagination_args.page > 1

        return OffsetPageInfo(
            page=pagination_args.page,
            limit=limit,
            total_count=total_count,
            total_pages=total_pages,
            has_next_page=has_next_page,
            has_previous_page=has_previous_page,
        )


def create_connection(
    items: list[T], pagination_args: PaginationArgs, total_count: int | None = None
) -> Connection[T]:
    """Create a connection for cursor-based pagination.

    Args:
        items: List of items
        pagination_args: Pagination arguments
        total_count: Total count (optional)

    Returns:
        Connection instance
    """
    edges = [
        Edge(node=item, cursor=PaginationHelper.create_cursor(item.id))
        for item in items
    ]

    page_info = PaginationHelper.create_page_info(items, pagination_args, total_count)

    return Connection(edges=edges, page_info=page_info, total_count=total_count)


def create_offset_connection(
    items: list[T], pagination_args: OffsetPaginationArgs, total_count: int
) -> OffsetConnection[T]:
    """Create a connection for offset-based pagination.

    Args:
        items: List of items
        pagination_args: Pagination arguments
        total_count: Total count

    Returns:
        OffsetConnection instance
    """
    page_info = PaginationHelper.create_offset_page_info(
        items, pagination_args, total_count
    )

    return OffsetConnection(items=items, page_info=page_info)


# Utility functions for common pagination operations
def paginate_query(
    query: Query, pagination_args: PaginationArgs, sort_field: str = "id"
) -> tuple[Query, int | None]:
    """Paginate a query with cursor-based pagination.

    Args:
        query: SQLAlchemy query
        pagination_args: Pagination arguments
        sort_field: Field to sort by

    Returns:
        Tuple of (paginated_query, total_count)
    """
    # Get total count before pagination
    total_count = PaginationHelper.get_total_count(query)

    # Apply pagination
    paginated_query = PaginationHelper.apply_cursor_pagination(
        query, pagination_args, sort_field
    )

    return paginated_query, total_count


def paginate_query_offset(
    query: Query, pagination_args: OffsetPaginationArgs
) -> tuple[Query, int]:
    """Paginate a query with offset-based pagination.

    Args:
        query: SQLAlchemy query
        pagination_args: Pagination arguments

    Returns:
        Tuple of (paginated_query, total_count)
    """
    # Get total count before pagination
    total_count = PaginationHelper.get_total_count(query)

    # Apply pagination
    paginated_query = PaginationHelper.apply_offset_pagination(query, pagination_args)

    return paginated_query, total_count
