"""
GraphQL schema for EGRC Core Service.

This module defines the main GraphQL schema with queries and mutations
for core EGRC functionality.
"""

from typing import Any

import strawberry
from strawberry.types import Info

from ..core.global_id import GlobalID


# Base types
@strawberry.type
class HealthStatus:
    """Health status type."""

    status: str = strawberry.field(description="Service status")
    timestamp: str = strawberry.field(description="Check timestamp")
    service: str = strawberry.field(description="Service name")
    version: str = strawberry.field(description="Service version")
    environment: str = strawberry.field(description="Environment")


@strawberry.type
class SystemInfo:
    """System information type."""

    service_name: str = strawberry.field(description="Service name")
    version: str = strawberry.field(description="Service version")
    environment: str = strawberry.field(description="Environment")
    uptime: str = strawberry.field(description="Service uptime")
    dependencies: list[str] = strawberry.field(description="Service dependencies")


# Input types
@strawberry.input
class HealthCheckInput:
    """Health check input type."""

    include_dependencies: bool = strawberry.field(
        default=False, description="Include dependency status"
    )


@strawberry.input
class SystemInfoInput:
    """System info input type."""

    include_metrics: bool = strawberry.field(
        default=False, description="Include system metrics"
    )


# Query type
@strawberry.type
class Query:
    """Main query type for EGRC Core."""

    @strawberry.field(description="Get health status")
    async def health(
        self, info: Info, input: HealthCheckInput | None = None
    ) -> HealthStatus:
        """Get service health status."""
        from datetime import datetime

        return HealthStatus(
            status="healthy",
            timestamp=datetime.utcnow().isoformat(),
            service="egrc-core",
            version="1.0.0",
            environment="development",
        )

    @strawberry.field(description="Get system information")
    async def system_info(
        self, info: Info, input: SystemInfoInput | None = None
    ) -> SystemInfo:
        """Get system information."""
        return SystemInfo(
            service_name="egrc-core",
            version="1.0.0",
            environment="development",
            uptime="N/A",
            dependencies=["database", "redis", "rabbitmq"],
        )

    @strawberry.field(description="Get service configuration")
    async def configuration(self, info: Info) -> dict[str, Any]:
        """Get service configuration."""
        from ..config import settings

        return {
            "service_name": settings.service_name,
            "version": settings.service_version,
            "environment": settings.environment,
            "debug": settings.debug,
            "database_host": settings.database.host,
            "redis_host": settings.redis.host,
            "rabbitmq_host": settings.rabbitmq.host,
        }

    @strawberry.field(description="Get available filters for a type")
    async def available_filters(self, info: Info, type_name: str) -> list[str]:
        """Get available filters for a specific type."""
        # This would be implemented based on the type
        common_filters = ["id", "created_at", "updated_at"]

        if type_name.lower() == "user":
            return common_filters + [
                "email",
                "username",
                "first_name",
                "last_name",
                "is_active",
            ]
        elif type_name.lower() == "tenant":
            return common_filters + [
                "name",
                "display_name",
                "domain",
                "subdomain",
                "is_active",
            ]
        elif type_name.lower() == "role":
            return common_filters + ["name", "display_name", "is_system_role"]

        return common_filters

    @strawberry.field(description="Get available sort fields for a type")
    async def available_sort_fields(self, info: Info, type_name: str) -> list[str]:
        """Get available sort fields for a specific type."""
        # This would be implemented based on the type
        common_sort_fields = ["id", "created_at", "updated_at"]

        if type_name.lower() == "user":
            return common_sort_fields + ["email", "username", "first_name", "last_name"]
        elif type_name.lower() == "tenant":
            return common_sort_fields + ["name", "display_name", "domain", "subdomain"]
        elif type_name.lower() == "role":
            return common_sort_fields + ["name", "display_name"]

        return common_sort_fields

    @strawberry.field(description="Get pagination info")
    async def pagination_info(self, info: Info) -> dict[str, Any]:
        """Get pagination information."""
        return {
            "default_page_size": 50,
            "max_page_size": 1000,
            "supported_pagination_types": ["cursor", "offset"],
            "cursor_based": True,
            "offset_based": True,
        }


# Mutation type
@strawberry.type
class Mutation:
    """Main mutation type for EGRC Core."""

    @strawberry.field(description="Test mutation")
    async def test_mutation(self, info: Info, input: str) -> str:
        """Test mutation endpoint."""
        return f"Test mutation received: {input}"

    @strawberry.field(description="Update configuration")
    async def update_configuration(self, info: Info, key: str, value: str) -> bool:
        """Update configuration value."""
        # This would be implemented to update configuration
        # For now, just return success
        return True

    @strawberry.field(description="Clear cache")
    async def clear_cache(self, info: Info, cache_type: str | None = None) -> bool:
        """Clear cache."""
        # This would be implemented to clear cache
        # For now, just return success
        return True


# Schema creation
def create_schema() -> strawberry.Schema:
    """Create the GraphQL schema."""
    return strawberry.Schema(
        query=Query,
        mutation=Mutation,
        types=[
            HealthStatus,
            SystemInfo,
            GlobalID,
        ],
    )


# Export schema
# schema = create_schema()  # Commented out to avoid import errors
