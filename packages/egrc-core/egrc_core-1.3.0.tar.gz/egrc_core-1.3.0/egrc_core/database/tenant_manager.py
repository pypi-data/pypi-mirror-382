"""
Tenant Database Manager for EGRC Platform.

This module provides comprehensive tenant database management including:
- Tenant database creation and deletion
- Migration management for tenant databases
- Database connection management
- Tenant isolation and security
"""

from contextlib import asynccontextmanager
from datetime import datetime
from typing import Any

from sqlalchemy import Engine, create_engine, text
from sqlalchemy.engine.url import make_url
from sqlalchemy.pool import QueuePool

from ..config.settings import Settings
from ..exceptions.exceptions import ConfigurationError, DatabaseError, ValidationError
from ..logging.utils import get_logger


logger = get_logger(__name__)


class TenantDatabaseManager:
    """Manages tenant database operations."""

    def __init__(self, settings: Settings | None = None):
        """Initialize tenant database manager.

        Args:
            settings: Application settings instance
        """
        self.settings = settings or Settings()
        self.master_engine = None
        self.tenant_engines: dict[str, Engine] = {}
        self._initialize_master_connection()

    def _initialize_master_connection(self) -> None:
        """Initialize master database connection."""
        try:
            master_url = self.settings.database_url
            if not master_url:
                raise ConfigurationError("Master database URL not configured")

            self.master_engine = create_engine(
                master_url,
                poolclass=QueuePool,
                pool_size=5,
                max_overflow=10,
                pool_pre_ping=True,
                pool_recycle=3600,
                echo=self.settings.environment == "development",
            )

            logger.info("Initialized master database connection")

        except Exception as e:
            logger.error(f"Failed to initialize master database connection: {e}")
            raise DatabaseError(f"Master database connection failed: {e}")

    def get_tenant_database_name(self, tenant_id: str) -> str:
        """Get tenant database name.

        Args:
            tenant_id: Unique tenant identifier

        Returns:
            Database name for the tenant
        """
        if not tenant_id or not tenant_id.strip():
            raise ValidationError("Tenant ID cannot be empty")

        # Sanitize tenant ID for database name
        sanitized_id = tenant_id.lower().replace("-", "_").replace(" ", "_")
        return f"{sanitized_id}_egrc"

    def get_tenant_database_url(self, tenant_id: str) -> str:
        """Get tenant database URL.

        Args:
            tenant_id: Unique tenant identifier

        Returns:
            Database URL for the tenant
        """
        try:
            # Get master database URL
            master_url = self.settings.database_url
            if not master_url:
                raise ConfigurationError("Master database URL not configured")

            # Parse master URL
            url_obj = make_url(master_url)

            # Create tenant database URL
            tenant_db_name = self.get_tenant_database_name(tenant_id)
            tenant_url = master_url.replace(
                f"/{url_obj.database}", f"/{tenant_db_name}"
            )

            return tenant_url

        except Exception as e:
            logger.error(f"Failed to get tenant database URL for {tenant_id}: {e}")
            raise DatabaseError(f"Failed to get tenant database URL: {e}")

    def create_tenant_database(
        self, tenant_id: str, with_migrations: bool = True
    ) -> bool:
        """Create a new tenant database.

        Args:
            tenant_id: Unique tenant identifier
            with_migrations: Whether to run initial migrations

        Returns:
            True if successful, False otherwise
        """
        try:
            if not tenant_id or not tenant_id.strip():
                raise ValidationError("Tenant ID cannot be empty")

            tenant_db_name = self.get_tenant_database_name(tenant_id)

            # Check if database already exists
            if self.tenant_database_exists(tenant_id):
                logger.info(f"Tenant database {tenant_db_name} already exists")
                return True

            # Create database
            with self.master_engine.connect() as conn:
                # Set autocommit for database creation
                conn.execute(text("COMMIT"))

                # Create database
                conn.execute(text(f'CREATE DATABASE "{tenant_db_name}"'))
                conn.commit()

                logger.info(f"Successfully created tenant database: {tenant_db_name}")

            # Run initial migrations if requested
            if with_migrations:
                self.run_tenant_migrations(tenant_id)

            return True

        except Exception as e:
            logger.error(f"Failed to create tenant database for {tenant_id}: {e}")
            return False

    def delete_tenant_database(self, tenant_id: str) -> bool:
        """Delete a tenant database.

        Args:
            tenant_id: Unique tenant identifier

        Returns:
            True if successful, False otherwise
        """
        try:
            if not tenant_id or not tenant_id.strip():
                raise ValidationError("Tenant ID cannot be empty")

            tenant_db_name = self.get_tenant_database_name(tenant_id)

            # Check if database exists
            if not self.tenant_database_exists(tenant_id):
                logger.info(f"Tenant database {tenant_db_name} does not exist")
                return True

            # Terminate all connections to the database
            with self.master_engine.connect() as conn:
                conn.execute(
                    text(
                        """
                    SELECT pg_terminate_backend(pid)
                    FROM pg_stat_activity
                    WHERE datname = '{tenant_db_name}' AND pid <> pg_backend_pid()
                """
                    )
                )
                conn.commit()

            # Drop database
            with self.master_engine.connect() as conn:
                conn.execute(text("COMMIT"))
                conn.execute(text(f'DROP DATABASE "{tenant_db_name}"'))
                conn.commit()

                logger.info(f"Successfully deleted tenant database: {tenant_db_name}")

            # Remove from cache
            if tenant_id in self.tenant_engines:
                del self.tenant_engines[tenant_id]

            return True

        except Exception as e:
            logger.error(f"Failed to delete tenant database for {tenant_id}: {e}")
            return False

    def tenant_database_exists(self, tenant_id: str) -> bool:
        """Check if tenant database exists.

        Args:
            tenant_id: Unique tenant identifier

        Returns:
            True if database exists, False otherwise
        """
        try:
            tenant_db_name = self.get_tenant_database_name(tenant_id)

            with self.master_engine.connect() as conn:
                result = conn.execute(
                    text("SELECT 1 FROM pg_database WHERE datname = :db_name"),
                    {"db_name": tenant_db_name},
                )

                return result.fetchone() is not None

        except Exception as e:
            logger.error(
                f"Failed to check tenant database existence for {tenant_id}: {e}"
            )
            return False

    def get_tenant_engine(self, tenant_id: str) -> Engine:
        """Get database engine for tenant.

        Args:
            tenant_id: Unique tenant identifier

        Returns:
            SQLAlchemy engine for the tenant
        """
        try:
            # Return cached engine if available
            if tenant_id in self.tenant_engines:
                return self.tenant_engines[tenant_id]

            # Create new engine
            tenant_url = self.get_tenant_database_url(tenant_id)

            engine = create_engine(
                tenant_url,
                poolclass=QueuePool,
                pool_size=10,
                max_overflow=20,
                pool_pre_ping=True,
                pool_recycle=3600,
                echo=self.settings.environment == "development",
            )

            # Cache the engine
            self.tenant_engines[tenant_id] = engine

            logger.debug(f"Created database engine for tenant: {tenant_id}")
            return engine

        except Exception as e:
            logger.error(f"Failed to get tenant engine for {tenant_id}: {e}")
            raise DatabaseError(f"Failed to get tenant engine: {e}")

    def run_tenant_migrations(self, tenant_id: str) -> bool:
        """Run migrations for a tenant database.

        Args:
            tenant_id: Unique tenant identifier

        Returns:
            True if successful, False otherwise
        """
        try:
            import os
            import subprocess

            # Set environment variables for migration
            env = os.environ.copy()
            env["TENANT_ID"] = tenant_id
            env["DATABASE_URL"] = self.get_tenant_database_url(tenant_id)

            # Run alembic upgrade
            result = subprocess.run(
                ["alembic", "upgrade", "head"],
                env=env,
                capture_output=True,
                text=True,
                cwd=os.path.dirname(os.path.dirname(__file__)),
            )

            if result.returncode == 0:
                logger.info(f"Successfully ran migrations for tenant: {tenant_id}")
                return True
            else:
                logger.error(
                    f"Migration failed for tenant {tenant_id}: {result.stderr}"
                )
                return False

        except Exception as e:
            logger.error(f"Failed to run migrations for tenant {tenant_id}: {e}")
            return False

    def list_tenant_databases(self) -> list[str]:
        """List all tenant databases.

        Returns:
            List of tenant database names
        """
        try:
            with self.master_engine.connect() as conn:
                result = conn.execute(
                    text(
                        """
                    SELECT datname
                    FROM pg_database
                    WHERE datname LIKE '%_egrc'
                    AND datname != 'egrc_core'
                    ORDER BY datname
                """
                    )
                )

                return [row[0] for row in result.fetchall()]

        except Exception as e:
            logger.error(f"Failed to list tenant databases: {e}")
            return []

    def get_tenant_database_info(self, tenant_id: str) -> dict[str, Any]:
        """Get information about a tenant database.

        Args:
            tenant_id: Unique tenant identifier

        Returns:
            Dictionary with database information
        """
        try:
            tenant_db_name = self.get_tenant_database_name(tenant_id)

            with self.master_engine.connect() as conn:
                # Get database size
                size_result = conn.execute(
                    text(
                        """
                    SELECT pg_size_pretty(pg_database_size(:db_name)) as size
                """
                    ),
                    {"db_name": tenant_db_name},
                )

                # Get table count
                table_result = conn.execute(
                    text(
                        """
                    SELECT COUNT(*) as table_count
                    FROM information_schema.tables
                    WHERE table_schema = 'public'
                """
                    )
                )

                size_row = size_result.fetchone()
                table_row = table_result.fetchone()

                return {
                    "tenant_id": tenant_id,
                    "database_name": tenant_db_name,
                    "size": size_row[0] if size_row else "Unknown",
                    "table_count": table_row[0] if table_row else 0,
                    "exists": self.tenant_database_exists(tenant_id),
                    "created_at": datetime.now().isoformat(),
                }

        except Exception as e:
            logger.error(f"Failed to get tenant database info for {tenant_id}: {e}")
            return {
                "tenant_id": tenant_id,
                "database_name": self.get_tenant_database_name(tenant_id),
                "error": str(e),
                "exists": False,
            }

    def cleanup_tenant_engines(self) -> None:
        """Clean up tenant database engines."""
        try:
            for tenant_id, engine in self.tenant_engines.items():
                try:
                    engine.dispose()
                    logger.debug(f"Disposed engine for tenant: {tenant_id}")
                except Exception as e:
                    logger.warning(
                        f"Failed to dispose engine for tenant {tenant_id}: {e}"
                    )

            self.tenant_engines.clear()
            logger.info("Cleaned up all tenant database engines")

        except Exception as e:
            logger.error(f"Failed to cleanup tenant engines: {e}")

    def __del__(self):
        """Cleanup on destruction."""
        try:
            self.cleanup_tenant_engines()
            if self.master_engine:
                self.master_engine.dispose()
        except Exception:
            pass


# Global tenant manager instance
_tenant_manager: TenantDatabaseManager | None = None


def get_tenant_manager() -> TenantDatabaseManager:
    """Get global tenant database manager instance."""
    global _tenant_manager
    if _tenant_manager is None:
        _tenant_manager = TenantDatabaseManager()
    return _tenant_manager


@asynccontextmanager
async def tenant_database_context(tenant_id: str):
    """Context manager for tenant database operations."""
    manager = get_tenant_manager()
    try:
        # Ensure tenant database exists
        if not manager.tenant_database_exists(tenant_id):
            manager.create_tenant_database(tenant_id)

        # Get tenant engine
        engine = manager.get_tenant_engine(tenant_id)
        yield engine

    except Exception as e:
        logger.error(f"Error in tenant database context for {tenant_id}: {e}")
        raise
    finally:
        # Cleanup if needed
        pass


# Convenience functions for other microservices
def create_tenant_database(tenant_id: str) -> bool:
    """Create a tenant database (convenience function)."""
    return get_tenant_manager().create_tenant_database(tenant_id)


def delete_tenant_database(tenant_id: str) -> bool:
    """Delete a tenant database (convenience function)."""
    return get_tenant_manager().delete_tenant_database(tenant_id)


def get_tenant_database_url(tenant_id: str) -> str:
    """Get tenant database URL (convenience function)."""
    return get_tenant_manager().get_tenant_database_url(tenant_id)


def list_tenant_databases() -> list[str]:
    """List all tenant databases (convenience function)."""
    return get_tenant_manager().list_tenant_databases()
