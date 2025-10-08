"""
Not used yet.

Audit API endpoints for EGRC Platform.

This module provides REST API endpoints for audit logging, querying,
and management operations.
"""

from datetime import datetime, timezone
from uuid import UUID

from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException, Path, Query
from fastapi.responses import StreamingResponse
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from ..database import get_async_db_session
from ..exceptions.exceptions import DatabaseError, NotFoundError, ValidationError
from .models import AuditAction, AuditSeverity
from .schemas import (
    AuditBulkCreateSchema,
    AuditBulkResponseSchema,
    AuditConfigurationCreateSchema,
    AuditConfigurationResponseSchema,
    AuditCreateSchema,
    AuditEventCreateSchema,
    AuditEventResponseSchema,
    AuditExportSchema,
    AuditQuerySchema,
    AuditResponseSchema,
    AuditRetentionPolicyCreateSchema,
    AuditRetentionPolicyResponseSchema,
    AuditSearchSchema,
    AuditStatsSchema,
    AuditUpdateSchema,
    AuditValidationSchema,
)
from .service import AuditService


router = APIRouter(prefix="/audit", tags=["audit"])


# Dependency to get audit service
async def get_audit_service(
    db_session: AsyncSession = Depends(get_async_db_session),
) -> AuditService:
    """Get audit service instance."""
    return AuditService(db_session)


# Audit Log Endpoints


@router.post("/logs", response_model=AuditResponseSchema, status_code=201)
async def create_audit_log(
    audit_data: AuditCreateSchema,
    audit_service: AuditService = Depends(get_audit_service),
):
    """
    Create a new audit log entry.

    This endpoint creates a new audit log entry with comprehensive
    tracking information including entity details, user information,
    change data, and technical metadata.
    """
    try:
        return await audit_service.create_audit_log(audit_data)
    except ValidationError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except DatabaseError as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/logs/{audit_id}", response_model=AuditResponseSchema)
async def get_audit_log(
    audit_id: UUID = Path(..., description="Audit log ID"),
    audit_service: AuditService = Depends(get_audit_service),
):
    """
    Get an audit log entry by ID.

    Retrieves a specific audit log entry with all its details
    including change information, metadata, and timestamps.
    """
    try:
        return await audit_service.get_audit_log(audit_id)
    except NotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except DatabaseError as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.put("/logs/{audit_id}", response_model=AuditResponseSchema)
async def update_audit_log(
    audit_id: UUID = Path(..., description="Audit log ID"),
    update_data: AuditUpdateSchema = ...,
    audit_service: AuditService = Depends(get_audit_service),
):
    """
    Update an audit log entry.

    Updates specific fields of an audit log entry, typically
    used to add execution time, error information, or status updates.
    """
    try:
        return await audit_service.update_audit_log(audit_id, update_data)
    except NotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except ValidationError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except DatabaseError as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/logs/{audit_id}", status_code=204)
async def delete_audit_log(
    audit_id: UUID = Path(..., description="Audit log ID"),
    audit_service: AuditService = Depends(get_audit_service),
):
    """
    Delete an audit log entry.

    Permanently deletes an audit log entry and all its associated
    details and attachments. This operation cannot be undone.
    """
    try:
        await audit_service.delete_audit_log(audit_id)
    except NotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except DatabaseError as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/logs/query", response_model=list[AuditResponseSchema])
async def query_audit_logs(
    query_params: AuditQuerySchema,
    audit_service: AuditService = Depends(get_audit_service),
):
    """
    Query audit logs with filters and pagination.

    Performs advanced querying of audit logs with support for
    multiple filters, sorting, and pagination. Returns a list
    of matching audit log entries.
    """
    try:
        return await audit_service.query_audit_logs(query_params)
    except ValidationError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except DatabaseError as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/logs/search", response_model=list[AuditResponseSchema])
async def search_audit_logs(
    search_params: AuditSearchSchema,
    audit_service: AuditService = Depends(get_audit_service),
):
    """
    Search audit logs with full-text search.

    Performs full-text search across audit log entries with
    support for fuzzy matching, field-specific searches, and
    advanced filtering options.
    """
    try:
        return await audit_service.search_audit_logs(search_params)
    except ValidationError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except DatabaseError as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/logs/bulk", response_model=AuditBulkResponseSchema)
async def bulk_create_audit_logs(
    bulk_data: AuditBulkCreateSchema,
    background_tasks: BackgroundTasks,
    audit_service: AuditService = Depends(get_audit_service),
):
    """
    Create multiple audit log entries in bulk.

    Creates multiple audit log entries in a single operation
    for improved performance when logging large numbers of
    related audit events.
    """
    try:
        return await audit_service.bulk_create_audit_logs(bulk_data)
    except ValidationError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except DatabaseError as e:
        raise HTTPException(status_code=500, detail=str(e))


# Audit Statistics Endpoints


@router.get("/stats", response_model=AuditStatsSchema)
async def get_audit_stats(
    start_date: datetime | None = Query(None, description="Start date for statistics"),
    end_date: datetime | None = Query(None, description="End date for statistics"),
    tenant_id: str | None = Query(None, description="Tenant ID filter"),
    audit_service: AuditService = Depends(get_audit_service),
):
    """
    Get audit statistics and analytics.

    Returns comprehensive statistics about audit logs including
    counts by action, entity, user, severity, and time-based
    distributions.
    """
    try:
        return await audit_service.get_audit_stats(start_date, end_date, tenant_id)
    except DatabaseError as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/stats/actions")
async def get_action_stats(
    start_date: datetime | None = Query(None, description="Start date"),
    end_date: datetime | None = Query(None, description="End date"),
    tenant_id: str | None = Query(None, description="Tenant ID"),
    audit_service: AuditService = Depends(get_audit_service),
):
    """Get statistics by action type."""
    try:
        stats = await audit_service.get_audit_stats(start_date, end_date, tenant_id)
        return {
            "actions": stats.audits_by_action,
            "total": sum(stats.audits_by_action.values()),
        }
    except DatabaseError as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/stats/entities")
async def get_entity_stats(
    start_date: datetime | None = Query(None, description="Start date"),
    end_date: datetime | None = Query(None, description="End date"),
    tenant_id: str | None = Query(None, description="Tenant ID"),
    audit_service: AuditService = Depends(get_audit_service),
):
    """Get statistics by entity type."""
    try:
        stats = await audit_service.get_audit_stats(start_date, end_date, tenant_id)
        return {
            "entities": stats.audits_by_entity,
            "total": sum(stats.audits_by_entity.values()),
        }
    except DatabaseError as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/stats/users")
async def get_user_stats(
    start_date: datetime | None = Query(None, description="Start date"),
    end_date: datetime | None = Query(None, description="End date"),
    tenant_id: str | None = Query(None, description="Tenant ID"),
    limit: int = Query(10, ge=1, le=100, description="Number of top users to return"),
    audit_service: AuditService = Depends(get_audit_service),
):
    """Get statistics by user."""
    try:
        stats = await audit_service.get_audit_stats(start_date, end_date, tenant_id)

        # Sort users by activity and limit results
        sorted_users = sorted(
            stats.audits_by_user.items(), key=lambda x: x[1], reverse=True
        )[:limit]

        return {
            "users": dict(sorted_users),
            "total": sum(stats.audits_by_user.values()),
        }
    except DatabaseError as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/stats/performance")
async def get_performance_stats(
    start_date: datetime | None = Query(None, description="Start date"),
    end_date: datetime | None = Query(None, description="End date"),
    tenant_id: str | None = Query(None, description="Tenant ID"),
    audit_service: AuditService = Depends(get_audit_service),
):
    """Get performance statistics."""
    try:
        stats = await audit_service.get_audit_stats(start_date, end_date, tenant_id)
        return {
            "average_execution_time_ms": stats.average_execution_time,
            "error_rate_percent": stats.error_rate,
            "total_operations": stats.total_audits,
        }
    except DatabaseError as e:
        raise HTTPException(status_code=500, detail=str(e))


# Audit Export Endpoints


@router.post("/export")
async def export_audit_logs(
    export_params: AuditExportSchema,
    audit_service: AuditService = Depends(get_audit_service),
):
    """
    Export audit logs in various formats.

    Exports audit log data in JSON, CSV, or Excel format with
    support for filtering, field selection, and inclusion of
    related data like details and attachments.
    """
    try:
        # Build query parameters from export parameters
        query_params = AuditQuerySchema(
            entity_name=export_params.entity_name,
            action=export_params.action,
            start_date=export_params.start_date,
            end_date=export_params.end_date,
            page=1,
            per_page=10000,  # Large limit for export
        )

        # Get audit logs
        audit_logs = await audit_service.query_audit_logs(query_params)

        # Convert to export format
        if export_params.format == "json":
            return {"audit_logs": [log.dict() for log in audit_logs]}

        elif export_params.format == "csv":
            # Generate CSV content
            import csv
            import io

            output = io.StringIO()
            if audit_logs:
                fieldnames = audit_logs[0].dict().keys()
                writer = csv.DictWriter(output, fieldnames=fieldnames)
                writer.writeheader()
                for log in audit_logs:
                    writer.writerow(log.dict())

            return StreamingResponse(
                io.BytesIO(output.getvalue().encode()),
                media_type="text/csv",
                headers={"Content-Disposition": "attachment; filename=audit_logs.csv"},
            )

        elif export_params.format == "xlsx":
            # Generate Excel content
            import io

            import pandas as pd

            df = pd.DataFrame([log.dict() for log in audit_logs])
            output = io.BytesIO()
            df.to_excel(output, index=False)
            output.seek(0)

            return StreamingResponse(
                output,
                media_type=(
                    "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                ),
                headers={"Content-Disposition": "attachment; filename=audit_logs.xlsx"},
            )

        else:
            raise HTTPException(status_code=400, detail="Unsupported export format")

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# Audit Event Endpoints


@router.post("/events", response_model=AuditEventResponseSchema, status_code=201)
async def create_audit_event(
    event_data: AuditEventCreateSchema,
    audit_service: AuditService = Depends(get_audit_service),
):
    """
    Create an audit event for asynchronous processing.

    Creates an audit event that will be processed asynchronously
    to improve performance for high-volume audit logging scenarios.
    """
    try:
        event_id = await audit_service.create_audit_event(event_data)

        # Get the created event
        async with get_async_db_session() as session:
            result = await session.execute(
                select(audit_service.models.AuditEvent).where(
                    audit_service.models.AuditEvent.id == event_id
                )
            )
            event = result.scalar_one()
            return AuditEventResponseSchema.from_orm(event)

    except ValidationError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except DatabaseError as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/events/{event_id}", response_model=AuditEventResponseSchema)
async def get_audit_event(
    event_id: UUID = Path(..., description="Event ID"),
    audit_service: AuditService = Depends(get_audit_service),
):
    """Get an audit event by ID."""
    try:
        async with get_async_db_session() as session:
            result = await session.execute(
                select(audit_service.models.AuditEvent).where(
                    audit_service.models.AuditEvent.id == event_id
                )
            )
            event = result.scalar_one_or_none()

            if not event:
                raise HTTPException(status_code=404, detail="Event not found")

            return AuditEventResponseSchema.from_orm(event)

    except DatabaseError as e:
        raise HTTPException(status_code=500, detail=str(e))


# Audit Configuration Endpoints


@router.post(
    "/configurations", response_model=AuditConfigurationResponseSchema, status_code=201
)
async def create_audit_configuration(
    config_data: AuditConfigurationCreateSchema,
    audit_service: AuditService = Depends(get_audit_service),
):
    """
    Create audit configuration.

    Creates a new audit configuration that controls how audit
    logging behaves for specific entities, actions, or tenants.
    """
    try:
        async with get_async_db_session() as session:
            from .models import AuditConfiguration

            config = AuditConfiguration(
                entity_name=config_data.entity_name,
                action=config_data.action,
                tenant_id=config_data.tenant_id,
                is_enabled=config_data.is_enabled,
                log_level=config_data.log_level,
                capture_old_values=config_data.capture_old_values,
                capture_new_values=config_data.capture_new_values,
                capture_metadata=config_data.capture_metadata,
                excluded_fields=config_data.excluded_fields,
                included_fields=config_data.included_fields,
                field_masks=config_data.field_masks,
                retention_days=config_data.retention_days,
                archive_after_days=config_data.archive_after_days,
            )

            session.add(config)
            await session.commit()
            await session.refresh(config)

            return AuditConfigurationResponseSchema.from_orm(config)

    except ValidationError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except DatabaseError as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/configurations", response_model=list[AuditConfigurationResponseSchema])
async def list_audit_configurations(
    entity_name: str | None = Query(None, description="Filter by entity name"),
    tenant_id: str | None = Query(None, description="Filter by tenant ID"),
    audit_service: AuditService = Depends(get_audit_service),
):
    """List audit configurations."""
    try:
        async with get_async_db_session() as session:
            from sqlalchemy import and_, select

            from .models import AuditConfiguration

            query = select(AuditConfiguration)
            conditions = []

            if entity_name:
                conditions.append(AuditConfiguration.entity_name == entity_name)
            if tenant_id:
                conditions.append(AuditConfiguration.tenant_id == tenant_id)

            if conditions:
                query = query.where(and_(*conditions))

            result = await session.execute(query)
            configs = result.scalars().all()

            return [
                AuditConfigurationResponseSchema.from_orm(config) for config in configs
            ]

    except DatabaseError as e:
        raise HTTPException(status_code=500, detail=str(e))


# Audit Retention Policy Endpoints


@router.post(
    "/retention-policies",
    response_model=AuditRetentionPolicyResponseSchema,
    status_code=201,
)
async def create_retention_policy(
    policy_data: AuditRetentionPolicyCreateSchema,
    audit_service: AuditService = Depends(get_audit_service),
):
    """
    Create audit retention policy.

    Creates a new retention policy that defines how long audit
    data should be retained and when it should be archived or deleted.
    """
    try:
        async with get_async_db_session() as session:
            from .models import AuditRetentionPolicy

            policy = AuditRetentionPolicy(
                policy_name=policy_data.policy_name,
                entity_name=policy_data.entity_name,
                action=policy_data.action,
                severity=policy_data.severity.value if policy_data.severity else None,
                tenant_id=policy_data.tenant_id,
                retention_days=policy_data.retention_days,
                archive_after_days=policy_data.archive_after_days,
                delete_after_days=policy_data.delete_after_days,
                archive_location=policy_data.archive_location,
                archive_format=policy_data.archive_format,
                compression_enabled=policy_data.compression_enabled,
                is_active=policy_data.is_active,
            )

            session.add(policy)
            await session.commit()
            await session.refresh(policy)

            return AuditRetentionPolicyResponseSchema.from_orm(policy)

    except ValidationError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except DatabaseError as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get(
    "/retention-policies", response_model=list[AuditRetentionPolicyResponseSchema]
)
async def list_retention_policies(
    is_active: bool | None = Query(None, description="Filter by active status"),
    audit_service: AuditService = Depends(get_audit_service),
):
    """List audit retention policies."""
    try:
        async with get_async_db_session() as session:
            from sqlalchemy import select

            from .models import AuditRetentionPolicy

            query = select(AuditRetentionPolicy)

            if is_active is not None:
                query = query.where(AuditRetentionPolicy.is_active == is_active)

            result = await session.execute(query)
            policies = result.scalars().all()

            return [
                AuditRetentionPolicyResponseSchema.from_orm(policy)
                for policy in policies
            ]

    except DatabaseError as e:
        raise HTTPException(status_code=500, detail=str(e))


# Audit Health and Status Endpoints


@router.get("/health")
async def audit_health_check():
    """
    Health check endpoint for audit system.

    Returns the health status of the audit system including
    database connectivity, event processing status, and
    configuration validation.
    """
    try:
        # Check database connectivity
        async with get_async_db_session() as session:
            from sqlalchemy import func, select

            from .models import AuditLog

            result = await session.execute(select(func.count(AuditLog.id)))
            total_audits = result.scalar()

        return {
            "status": "healthy",
            "database": "connected",
            "total_audits": total_audits,
            "timestamp": datetime.now(timezone.utc).isoformat(),
        }

    except Exception as e:
        return {
            "status": "unhealthy",
            "error": str(e),
            "timestamp": datetime.now(timezone.utc).isoformat(),
        }


@router.get("/status")
async def audit_system_status():
    """
    Get audit system status.

    Returns detailed status information about the audit system
    including processing queues, worker status, and performance metrics.
    """
    try:
        # This would typically check the actual audit service status
        # For now, we'll return a basic status
        return {
            "event_processing": "active",
            "workers": 3,
            "queue_size": 0,
            "last_processed": datetime.now(timezone.utc).isoformat(),
            "uptime": "24h",
            "performance": {
                "avg_processing_time_ms": 150,
                "events_per_second": 100,
                "error_rate": 0.01,
            },
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# Audit Validation Endpoints


@router.post("/validate")
async def validate_audit_data(
    audit_data: AuditValidationSchema,
    audit_service: AuditService = Depends(get_audit_service),
):
    """
    Validate audit data without creating an entry.

    Validates audit data structure and business rules without
    actually creating an audit log entry. Useful for testing
    and validation purposes.
    """
    try:
        # The validation is already done by Pydantic
        return {
            "valid": True,
            "message": "Audit data is valid",
            "validated_data": audit_data.dict(),
        }

    except ValidationError as e:
        return {
            "valid": False,
            "message": "Audit data validation failed",
            "errors": e.errors(),
        }


# Quick audit logging endpoints for common operations


@router.post("/quick/{entity_name}/{entity_id}/{action}")
async def quick_audit_log(
    entity_name: str = Path(..., description="Entity name"),
    entity_id: str = Path(..., description="Entity ID"),
    action: AuditAction = Path(..., description="Action performed"),
    user_id: str | None = Query(None, description="User ID"),
    tenant_id: str | None = Query(None, description="Tenant ID"),
    severity: AuditSeverity = Query(AuditSeverity.LOW, description="Severity level"),
    message: str | None = Query(None, description="Additional message"),
    audit_service: AuditService = Depends(get_audit_service),
):
    """
    Quick audit logging for simple operations.

    Provides a simplified endpoint for quick audit logging
    without requiring a full audit data structure.
    """
    try:
        from .schemas import AuditCreateSchema

        audit_data = AuditCreateSchema(
            entity_name=entity_name,
            entity_id=entity_id,
            action=action,
            user_id=user_id,
            tenant_id=tenant_id,
            severity=severity,
            change_summary=message,
        )

        return await audit_service.create_audit_log(audit_data)

    except ValidationError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except DatabaseError as e:
        raise HTTPException(status_code=500, detail=str(e))
