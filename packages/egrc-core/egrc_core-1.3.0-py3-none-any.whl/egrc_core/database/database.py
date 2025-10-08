from sqlalchemy import text
from sqlalchemy.pool import NullPool


"""
Database configuration and utilities for EGRC Platform.

This module provides database connection management, session handling,
and utilities for multi-tenant database operations.
"""

from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager
from typing import Any

from sqlalchemy import create_engine
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import QueuePool
from sqlalchemy.pool.impl import AsyncAdaptedQueuePool

from ..config.settings import settings
from ..exceptions.exceptions import DatabaseError
from ..logging.utils import get_logger


logger = get_logger(__name__)


# Global engine and session maker instances
_async_engines: dict[str, Any] = {}
_async_session_makers: dict[str, Any] = {}
_sync_engines: dict[str, Any] = {}
_sync_session_makers: dict[str, Any] = {}


def get_database_url(
    tenant_name: str | None = None, service_name: str | None = None
) -> str:
    """Get database URL for a specific tenant and service.

    Args:
        tenant_name: Tenant name (optional, defaults to main database)
        service_name: Service name (optional, defaults to main database)

    Returns:
        Database URL string
    """
    if tenant_name and service_name:
        return settings.get_tenant_database_url(tenant_name, service_name)
    return settings.database.url


def create_async_engine_for_tenant(tenant_name: str, service_name: str):
    """Create async engine for a specific tenant and service.

    Args:
        tenant_name: Tenant name
        service_name: Service name

    Returns:
        AsyncEngine instance
    """
    db_url = get_database_url(tenant_name, service_name)
    engine_key = f"{tenant_name}_{service_name}"

    if engine_key not in _async_engines:
        _async_engines[engine_key] = create_async_engine(
            db_url,
            poolclass=AsyncAdaptedQueuePool,
            pool_size=settings.database.pool_size,
            max_overflow=settings.database.max_overflow,
            pool_timeout=settings.database.pool_timeout,
            pool_recycle=settings.database.pool_recycle,
            echo=settings.database.echo,
            future=True,
        )

        _async_session_makers[engine_key] = async_sessionmaker(
            _async_engines[engine_key],
            class_=AsyncSession,
            expire_on_commit=False,
        )

    return _async_engines[engine_key]


def create_sync_engine_for_tenant(tenant_name: str, service_name: str):
    """Create sync engine for a specific tenant and service.

    Args:
        tenant_name: Tenant name
        service_name: Service name

    Returns:
        Engine instance
    """
    db_url = get_database_url(tenant_name, service_name).replace("+asyncpg", "")
    engine_key = f"{tenant_name}_{service_name}_sync"

    if engine_key not in _sync_engines:
        _sync_engines[engine_key] = create_engine(
            db_url,
            poolclass=QueuePool,
            pool_size=settings.database.pool_size,
            max_overflow=settings.database.max_overflow,
            pool_timeout=settings.database.pool_timeout,
            pool_recycle=settings.database.pool_recycle,
            echo=settings.database.echo,
            future=True,
        )

        _sync_session_makers[engine_key] = sessionmaker(
            _sync_engines[engine_key],
            expire_on_commit=False,
        )

    return _sync_engines[engine_key]


def get_async_session_maker(tenant_name: str, service_name: str):
    """Get async session maker for a specific tenant and service.

    Args:
        tenant_name: Tenant name
        service_name: Service name

    Returns:
        AsyncSessionMaker instance
    """
    engine_key = f"{tenant_name}_{service_name}"

    if engine_key not in _async_session_makers:
        create_async_engine_for_tenant(tenant_name, service_name)

    return _async_session_makers[engine_key]


def get_sync_session_maker(tenant_name: str, service_name: str):
    """Get sync session maker for a specific tenant and service.

    Args:
        tenant_name: Tenant name
        service_name: Service name

    Returns:
        SessionMaker instance
    """
    engine_key = f"{tenant_name}_{service_name}_sync"

    if engine_key not in _sync_session_makers:
        create_sync_engine_for_tenant(tenant_name, service_name)

    return _sync_session_makers[engine_key]


@asynccontextmanager
async def get_async_session(
    tenant_name: str, service_name: str
) -> AsyncGenerator[AsyncSession, None]:
    """Get async database session for a specific tenant and service.

    Args:
        tenant_name: Tenant name
        service_name: Service name

    Yields:
        AsyncSession instance
    """
    session_maker = get_async_session_maker(tenant_name, service_name)

    async with session_maker() as session:
        try:
            yield session
            await session.commit()
        except Exception as e:
            await session.rollback()
            logger.error(
                "Database session error",
                tenant_name=tenant_name,
                service_name=service_name,
                error=str(e),
            )
            raise DatabaseError(f"Database operation failed: {str(e)}") from e
        finally:
            await session.close()


async def create_tenant_database(tenant_name: str, service_name: str) -> None:
    """Create database for a specific tenant and service.

    Args:
        tenant_name: Tenant name
        service_name: Service name
    """
    db_name = settings.get_tenant_database_name(tenant_name, service_name)

    # Connect to default database to create new database
    default_engine = create_async_engine(
        settings.database.sync_url,
        poolclass=NullPool,
    )

    try:
        async with default_engine.begin() as conn:
            # Check if database exists
            result = await conn.execute(
                text("SELECT 1 FROM pg_database WHERE datname = :db_name"),
                {"db_name": db_name},
            )

            if not result.fetchone():
                # Create database
                await conn.execute(text(f'CREATE DATABASE "{db_name}"'))
                logger.info(
                    "Created tenant database",
                    tenant_name=tenant_name,
                    service_name=service_name,
                    database_name=db_name,
                )
            else:
                logger.info(
                    "Tenant database already exists",
                    tenant_name=tenant_name,
                    service_name=service_name,
                    database_name=db_name,
                )
    except Exception as e:
        logger.error(
            "Failed to create tenant database",
            tenant_name=tenant_name,
            service_name=service_name,
            database_name=db_name,
            error=str(e),
        )
        raise DatabaseError(f"Failed to create database {db_name}: {str(e)}") from e
    finally:
        await default_engine.dispose()


async def drop_tenant_database(tenant_name: str, service_name: str) -> None:
    """Drop database for a specific tenant and service.

    Args:
        tenant_name: Tenant name
        service_name: Service name
    """
    db_name = settings.get_tenant_database_name(tenant_name, service_name)

    # Connect to default database to drop database
    default_engine = create_async_engine(
        settings.database.sync_url,
        poolclass=NullPool,
    )

    try:
        async with default_engine.begin() as conn:
            # Check if database exists
            result = await conn.execute(
                text("SELECT 1 FROM pg_database WHERE datname = :db_name"),
                {"db_name": db_name},
            )

            if result.fetchone():
                # Terminate connections to the database
                await conn.execute(
                    text(
                        """
                        SELECT pg_terminate_backend(pid)
                        FROM pg_stat_activity
                        WHERE datname = :db_name AND pid <> pg_backend_pid()
                    """
                    ),
                    {"db_name": db_name},
                )

                # Drop database
                await conn.execute(text(f'DROP DATABASE "{db_name}"'))
                logger.info(
                    "Dropped tenant database",
                    tenant_name=tenant_name,
                    service_name=service_name,
                    database_name=db_name,
                )
            else:
                logger.info(
                    "Tenant database does not exist",
                    tenant_name=tenant_name,
                    service_name=service_name,
                    database_name=db_name,
                )
    except Exception as e:
        logger.error(
            "Failed to drop tenant database",
            tenant_name=tenant_name,
            service_name=service_name,
            database_name=db_name,
            error=str(e),
        )
        raise DatabaseError(f"Failed to drop database {db_name}: {str(e)}") from e
    finally:
        await default_engine.dispose()


async def list_tenant_databases(tenant_name: str) -> list[str]:
    """List all databases for a specific tenant.

    Args:
        tenant_name: Tenant name

    Returns:
        List of database names
    """
    # Connect to default database to list databases
    default_engine = create_async_engine(
        settings.database.sync_url,
        poolclass=NullPool,
    )

    try:
        async with default_engine.begin() as conn:
            result = await conn.execute(
                text(
                    """
                    SELECT datname
                    FROM pg_database
                    WHERE datname LIKE :pattern
                    ORDER BY datname
                """
                ),
                {"pattern": f"{tenant_name}_%"},
            )

            databases = [row[0] for row in result.fetchall()]
            logger.info(
                "Listed tenant databases",
                tenant_name=tenant_name,
                databases=databases,
            )

            return databases
    except Exception as e:
        logger.error(
            "Failed to list tenant databases",
            tenant_name=tenant_name,
            error=str(e),
        )
        raise DatabaseError(
            f"Failed to list databases for tenant {tenant_name}: {str(e)}"
        ) from e
    finally:
        await default_engine.dispose()


async def check_database_connection(tenant_name: str, service_name: str) -> bool:
    """Check if database connection is working for a tenant and service.

    Args:
        tenant_name: Tenant name
        service_name: Service name

    Returns:
        True if connection is working, False otherwise
    """
    try:
        async with get_async_session(tenant_name, service_name) as session:
            await session.execute(text("SELECT 1"))
            return True
    except Exception as e:
        logger.error(
            "Database connection check failed",
            tenant_name=tenant_name,
            service_name=service_name,
            error=str(e),
        )
        return False


async def close_all_connections() -> None:
    """Close all database connections."""
    logger.info("Closing all database connections")

    # Close async engines
    for engine in _async_engines.values():
        await engine.dispose()

    # Close sync engines
    for engine in _sync_engines.values():
        engine.dispose()

    # Clear caches
    _async_engines.clear()
    _async_session_makers.clear()
    _sync_engines.clear()
    _sync_session_makers.clear()

    logger.info("All database connections closed")


# Initialize main database engine
main_engine = create_async_engine(
    settings.database.url,
    poolclass=AsyncAdaptedQueuePool,
    pool_size=settings.database.pool_size,
    max_overflow=settings.database.max_overflow,
    pool_timeout=settings.database.pool_timeout,
    pool_recycle=settings.database.pool_recycle,
    echo=settings.database.echo,
    future=True,
)

main_session_maker = async_sessionmaker(
    main_engine,
    class_=AsyncSession,
    expire_on_commit=False,
)


@asynccontextmanager
async def get_main_session() -> AsyncGenerator[AsyncSession, None]:
    """Get main database session.

    Yields:
        AsyncSession instance for main database
    """
    async with main_session_maker() as session:
        try:
            yield session
            await session.commit()
        except Exception as e:
            await session.rollback()
            logger.error("Main database session error", error=str(e))
            raise DatabaseError(f"Main database operation failed: {str(e)}") from e
        finally:
            await session.close()


# Compatibility function for existing code
@asynccontextmanager
async def get_async_db_session() -> AsyncGenerator[AsyncSession, None]:
    """Get async database session (compatibility function).

    This function provides compatibility with existing code that expects
    a session function without parameters.

    Yields:
        AsyncSession instance for main database
    """
    async with get_main_session() as session:
        yield session


# Compatibility function for sync sessions
def get_db_session():
    """Get sync database session (compatibility function).

    This function provides compatibility with existing code that expects
    a sync session function.

    Note: This is a placeholder function. In a real implementation,
    you would need to create a sync session maker.
    """
    raise NotImplementedError(
        "Sync sessions are not implemented in this version. Use async sessions instead."
    )
