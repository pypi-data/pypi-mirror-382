"""
Audit service for EGRC Platform.

This module provides comprehensive audit logging services including
synchronous and asynchronous audit entry creation, ORM hooks, and
event-driven audit processing.
"""

import asyncio
import logging
import time
from collections.abc import Callable
from datetime import datetime, timedelta, timezone
from functools import wraps
from typing import Any
from uuid import UUID

from sqlalchemy import and_, delete, func, or_, select, update
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession

from ..database import get_async_db_session
from ..exceptions.exceptions import (
    ConfigurationError,
    DatabaseError,
    EGRCException,
    NotFoundError,
)
from .models import AuditAction, AuditEvent, AuditLog, AuditSeverity, AuditStatus
from .schemas import (
    AuditBulkCreateSchema,
    AuditBulkResponseSchema,
    AuditCreateSchema,
    AuditEventCreateSchema,
    AuditQuerySchema,
    AuditResponseSchema,
    AuditSearchSchema,
    AuditStatsSchema,
    AuditUpdateSchema,
)


logger = logging.getLogger(__name__)


class AuditService:
    """
    Comprehensive audit service for EGRC Platform.

    Provides both synchronous and asynchronous audit logging capabilities
    with support for event-driven processing, bulk operations, and
    advanced querying and analytics.
    """

    def __init__(self, db_session: AsyncSession | None = None):
        self.db_session = db_session
        self._event_queue = asyncio.Queue()
        self._processing_tasks = []
        self._is_processing = False

    # Core audit logging methods

    async def create_audit_log(
        self, audit_data: AuditCreateSchema, db_session: AsyncSession | None = None
    ) -> AuditResponseSchema:
        """
        Create a new audit log entry.

        Args:
            audit_data: Audit data to log
            db_session: Database session (optional)

        Returns:
            Created audit log entry

        Raises:
            ValidationError: If audit data is invalid
            DatabaseError: If database operation fails
        """
        session = db_session or self.db_session
        if not session:
            raise ConfigurationError("No database session available")

        try:
            # Create audit log entry
            audit_log = AuditLog(
                # entity_name=audit_data.entity_name,
                # entity_id=audit_data.entity_id,
                entity_type=audit_data.entity_type,
                # action=audit_data.action.value,
                action_category=audit_data.action_category,
                user_id=audit_data.user_id,
                user_name=audit_data.user_name,
                user_email=audit_data.user_email,
                session_id=audit_data.session_id,
                request_id=audit_data.request_id,
                correlation_id=audit_data.correlation_id,
                # old_values=audit_data.old_values,
                # new_values=audit_data.new_values,
                changed_fields=audit_data.changed_fields,
                change_summary=audit_data.change_summary,
                tenant_id=audit_data.tenant_id,
                organization_id=audit_data.organization_id,
                department_id=audit_data.department_id,
                ip_address=audit_data.ip_address,
                user_agent=audit_data.user_agent,
                endpoint=audit_data.endpoint,
                method=audit_data.method,
                # severity=audit_data.severity.value,
                # status=audit_data.status.value,
                # error_message=audit_data.error_message,
                error_code=audit_data.error_code,
                # execution_time_ms=audit_data.execution_time_ms,
                memory_usage_mb=audit_data.memory_usage_mb,
                tags=audit_data.tags,
                metadata=audit_data.metadata,
                custom_fields=audit_data.custom_fields,
            )

            session.add(audit_log)
            await session.commit()
            await session.refresh(audit_log)

            logger.info(f"Created audit log: {audit_log.id}")
            return AuditResponseSchema.from_orm(audit_log)

        except SQLAlchemyError as e:
            await session.rollback()
            logger.error(f"Failed to create audit log: {e}")
            raise DatabaseError(f"Failed to create audit log: {e}")
        except Exception as e:
            await session.rollback()
            logger.error(f"Unexpected error creating audit log: {e}")
            raise EGRCException(f"Unexpected error: {e}")

    async def get_audit_log(
        self, audit_id: UUID, db_session: AsyncSession | None = None
    ) -> AuditResponseSchema:
        """
        Get an audit log entry by ID.

        Args:
            audit_id: Audit log ID
            db_session: Database session (optional)

        Returns:
            Audit log entry

        Raises:
            NotFoundError: If audit log not found
        """
        session = db_session or self.db_session
        if not session:
            raise ConfigurationError("No database session available")

        result = await session.execute(select(AuditLog).where(AuditLog.id == audit_id))
        audit_log = result.scalar_one_or_none()

        if not audit_log:
            raise NotFoundError(f"Audit log with ID {audit_id} not found")

        return AuditResponseSchema.from_orm(audit_log)

    async def update_audit_log(
        self,
        audit_id: UUID,
        update_data: AuditUpdateSchema,
        db_session: AsyncSession | None = None,
    ) -> AuditResponseSchema:
        """
        Update an audit log entry.

        Args:
            audit_id: Audit log ID
            update_data: Update data
            db_session: Database session (optional)

        Returns:
            Updated audit log entry
        """
        session = db_session or self.db_session
        if not session:
            raise ConfigurationError("No database session available")

        try:
            # Build update dict
            update_dict = {}
            for field, value in update_data.dict(exclude_unset=True).items():
                if hasattr(AuditLog, field):
                    update_dict[field] = value

            if update_dict:
                update_dict["updated_at"] = datetime.now(timezone.utc)

                await session.execute(
                    update(AuditLog)
                    .where(AuditLog.id == audit_id)
                    .values(**update_dict)
                )
                await session.commit()

            return await self.get_audit_log(audit_id, session)

        except SQLAlchemyError as e:
            await session.rollback()
            logger.error(f"Failed to update audit log: {e}")
            raise DatabaseError(f"Failed to update audit log: {e}")

    async def delete_audit_log(
        self, audit_id: UUID, db_session: AsyncSession | None = None
    ) -> bool:
        """
        Delete an audit log entry.

        Args:
            audit_id: Audit log ID
            db_session: Database session (optional)

        Returns:
            True if deleted successfully
        """
        session = db_session or self.db_session
        if not session:
            raise ConfigurationError("No database session available")

        try:
            result = await session.execute(
                delete(AuditLog).where(AuditLog.id == audit_id)
            )
            await session.commit()

            if result.rowcount == 0:
                raise NotFoundError(f"Audit log with ID {audit_id} not found")

            logger.info(f"Deleted audit log: {audit_id}")
            return True

        except SQLAlchemyError as e:
            await session.rollback()
            logger.error(f"Failed to delete audit log: {e}")
            raise DatabaseError(f"Failed to delete audit log: {e}")

    # Query and search methods

    async def query_audit_logs(
        self, query_params: AuditQuerySchema, db_session: AsyncSession | None = None
    ) -> list[AuditResponseSchema]:
        """
        Query audit logs with filters and pagination.

        Args:
            query_params: Query parameters
            db_session: Database session (optional)

        Returns:
            List of audit log entries
        """
        session = db_session or self.db_session
        if not session:
            raise ConfigurationError("No database session available")

        try:
            # Build query
            query = select(AuditLog)
            conditions = []

            # Add filters
            if query_params.entity_name:
                conditions.append(AuditLog.entity_name == query_params.entity_name)
            if query_params.entity_id:
                conditions.append(AuditLog.entity_id == query_params.entity_id)
            if query_params.entity_type:
                conditions.append(AuditLog.entity_type == query_params.entity_type)
            if query_params.action:
                conditions.append(AuditLog.action == query_params.action.value)
            if query_params.user_id:
                conditions.append(AuditLog.user_id == query_params.user_id)
            if query_params.tenant_id:
                conditions.append(AuditLog.tenant_id == query_params.tenant_id)
            if query_params.severity:
                conditions.append(AuditLog.severity == query_params.severity.value)
            if query_params.status:
                conditions.append(AuditLog.status == query_params.status.value)
            if query_params.start_date:
                conditions.append(AuditLog.created_at >= query_params.start_date)
            if query_params.end_date:
                conditions.append(AuditLog.created_at <= query_params.end_date)
            if query_params.correlation_id:
                conditions.append(
                    AuditLog.correlation_id == query_params.correlation_id
                )
            if query_params.request_id:
                conditions.append(AuditLog.request_id == query_params.request_id)
            if query_params.session_id:
                conditions.append(AuditLog.session_id == query_params.session_id)

            if conditions:
                query = query.where(and_(*conditions))

            # Add sorting
            sort_column = getattr(AuditLog, query_params.sort_by, AuditLog.created_at)
            if query_params.sort_order == "desc":
                query = query.order_by(sort_column.desc())
            else:
                query = query.order_by(sort_column.asc())

            # Add pagination
            offset = (query_params.page - 1) * query_params.per_page
            query = query.offset(offset).limit(query_params.per_page)

            # Execute query
            result = await session.execute(query)
            audit_logs = result.scalars().all()

            return [AuditResponseSchema.from_orm(log) for log in audit_logs]

        except SQLAlchemyError as e:
            logger.error(f"Failed to query audit logs: {e}")
            raise DatabaseError(f"Failed to query audit logs: {e}")

    async def search_audit_logs(
        self,
        search_params: AuditSearchSchema,
        db_session: AsyncSession | None = None,
    ) -> list[AuditResponseSchema]:
        """
        Search audit logs with full-text search capabilities.

        Args:
            search_params: Search parameters
            db_session: Database session (optional)

        Returns:
            List of matching audit log entries
        """
        session = db_session or self.db_session
        if not session:
            raise ConfigurationError("No database session available")

        try:
            # Build base query
            query = select(AuditLog)
            conditions = []

            # Add basic filters
            if search_params.entity_name:
                conditions.append(
                    AuditLog.entity_name.ilike(f"%{search_params.entity_name}%")
                )
            if search_params.action:
                conditions.append(AuditLog.action == search_params.action.value)
            if search_params.user_id:
                conditions.append(AuditLog.user_id == search_params.user_id)
            if search_params.tenant_id:
                conditions.append(AuditLog.tenant_id == search_params.tenant_id)
            if search_params.severity:
                conditions.append(AuditLog.severity == search_params.severity.value)
            if search_params.status:
                conditions.append(AuditLog.status == search_params.status.value)
            if search_params.start_date:
                conditions.append(AuditLog.created_at >= search_params.start_date)
            if search_params.end_date:
                conditions.append(AuditLog.created_at <= search_params.end_date)

            # Add full-text search
            if search_params.query:
                search_conditions = []
                search_term = search_params.query

                if not search_params.case_sensitive:
                    search_term = search_term.lower()

                # Search in various fields
                search_fields = search_params.search_fields or [
                    "entity_name",
                    "entity_id",
                    "user_name",
                    "user_email",
                    "change_summary",
                    "error_message",
                ]

                for field in search_fields:
                    if hasattr(AuditLog, field):
                        column = getattr(AuditLog, field)
                        if search_params.case_sensitive:
                            search_conditions.append(column.ilike(f"%{search_term}%"))
                        else:
                            search_conditions.append(
                                func.lower(column).ilike(f"%{search_term}%")
                            )

                if search_conditions:
                    conditions.append(or_(*search_conditions))

            # Add tag filters
            if search_params.tags:
                for key, value in search_params.tags.items():
                    conditions.append(AuditLog.tags.op("->>")(key) == str(value))

            if conditions:
                query = query.where(and_(*conditions))

            # Add sorting
            sort_column = getattr(AuditLog, search_params.sort_by, AuditLog.created_at)
            if search_params.sort_order == "desc":
                query = query.order_by(sort_column.desc())
            else:
                query = query.order_by(sort_column.asc())

            # Add pagination
            offset = (search_params.page - 1) * search_params.per_page
            query = query.offset(offset).limit(search_params.per_page)

            # Execute query
            result = await session.execute(query)
            audit_logs = result.scalars().all()

            return [AuditResponseSchema.from_orm(log) for log in audit_logs]

        except SQLAlchemyError as e:
            logger.error(f"Failed to search audit logs: {e}")
            raise DatabaseError(f"Failed to search audit logs: {e}")

    # Bulk operations

    async def bulk_create_audit_logs(
        self,
        bulk_data: AuditBulkCreateSchema,
        db_session: AsyncSession | None = None,
    ) -> AuditBulkResponseSchema:
        """
        Create multiple audit log entries in bulk.

        Args:
            bulk_data: Bulk audit data
            db_session: Database session (optional)

        Returns:
            Bulk operation result
        """
        session = db_session or self.db_session
        if not session:
            raise ConfigurationError("No database session available")

        start_time = time.time()
        created_ids = []
        failed_audits = []

        try:
            for audit_data in bulk_data.audits:
                try:
                    audit_log = AuditLog(
                        entity_name=audit_data.entity_name,
                        entity_id=audit_data.entity_id,
                        entity_type=audit_data.entity_type,
                        action=audit_data.action.value,
                        action_category=audit_data.action_category,
                        user_id=audit_data.user_id,
                        user_name=audit_data.user_name,
                        user_email=audit_data.user_email,
                        session_id=audit_data.session_id,
                        request_id=audit_data.request_id,
                        correlation_id=bulk_data.correlation_id
                        or audit_data.correlation_id,
                        old_values=audit_data.old_values,
                        new_values=audit_data.new_values,
                        changed_fields=audit_data.changed_fields,
                        change_summary=audit_data.change_summary,
                        tenant_id=audit_data.tenant_id,
                        organization_id=audit_data.organization_id,
                        department_id=audit_data.department_id,
                        ip_address=audit_data.ip_address,
                        user_agent=audit_data.user_agent,
                        endpoint=audit_data.endpoint,
                        method=audit_data.method,
                        severity=audit_data.severity.value,
                        status=audit_data.status.value,
                        error_message=audit_data.error_message,
                        error_code=audit_data.error_code,
                        execution_time_ms=audit_data.execution_time_ms,
                        memory_usage_mb=audit_data.memory_usage_mb,
                        tags=audit_data.tags,
                        metadata=audit_data.metadata,
                        custom_fields=audit_data.custom_fields,
                    )

                    session.add(audit_log)
                    await session.flush()  # Get the ID without committing
                    created_ids.append(audit_log.id)

                except Exception as e:
                    failed_audits.append(
                        {"audit_data": audit_data.dict(), "error": str(e)}
                    )

            await session.commit()

            processing_time = int((time.time() - start_time) * 1000)

            return AuditBulkResponseSchema(
                batch_id=bulk_data.batch_id,
                correlation_id=bulk_data.correlation_id,
                total_created=len(created_ids),
                total_failed=len(failed_audits),
                created_ids=created_ids,
                failed_audits=failed_audits,
                processing_time_ms=processing_time,
            )

        except SQLAlchemyError as e:
            await session.rollback()
            logger.error(f"Failed to bulk create audit logs: {e}")
            raise DatabaseError(f"Failed to bulk create audit logs: {e}")

    # Statistics and analytics

    async def get_audit_stats(
        self,
        start_date: datetime | None = None,
        end_date: datetime | None = None,
        tenant_id: str | None = None,
        db_session: AsyncSession | None = None,
    ) -> AuditStatsSchema:
        """
        Get audit statistics and analytics.

        Args:
            start_date: Start date for statistics
            end_date: End date for statistics
            tenant_id: Tenant ID filter
            db_session: Database session (optional)

        Returns:
            Audit statistics
        """
        session = db_session or self.db_session
        if not session:
            raise ConfigurationError("No database session available")

        try:
            # Build base query
            base_query = select(AuditLog)
            conditions = []

            if start_date:
                conditions.append(AuditLog.created_at >= start_date)
            if end_date:
                conditions.append(AuditLog.created_at <= end_date)
            if tenant_id:
                conditions.append(AuditLog.tenant_id == tenant_id)

            if conditions:
                base_query = base_query.where(and_(*conditions))

            # Get total count
            total_result = await session.execute(
                select(func.count(AuditLog.id)).select_from(base_query.subquery())
            )
            total_audits = total_result.scalar()

            # Get counts by action
            action_result = await session.execute(
                select(AuditLog.action, func.count(AuditLog.id))
                .select_from(base_query.subquery())
                .group_by(AuditLog.action)
            )
            audits_by_action = dict(action_result.fetchall())

            # Get counts by entity
            entity_result = await session.execute(
                select(AuditLog.entity_name, func.count(AuditLog.id))
                .select_from(base_query.subquery())
                .group_by(AuditLog.entity_name)
            )
            audits_by_entity = dict(entity_result.fetchall())

            # Get counts by user
            user_result = await session.execute(
                select(AuditLog.user_id, func.count(AuditLog.id))
                .select_from(base_query.subquery())
                .where(AuditLog.user_id.isnot(None))
                .group_by(AuditLog.user_id)
            )
            audits_by_user = dict(user_result.fetchall())

            # Get counts by severity
            severity_result = await session.execute(
                select(AuditLog.severity, func.count(AuditLog.id))
                .select_from(base_query.subquery())
                .group_by(AuditLog.severity)
            )
            audits_by_severity = dict(severity_result.fetchall())

            # Get counts by status
            status_result = await session.execute(
                select(AuditLog.status, func.count(AuditLog.id))
                .select_from(base_query.subquery())
                .group_by(AuditLog.status)
            )
            audits_by_status = dict(status_result.fetchall())

            # Get counts by tenant
            tenant_result = await session.execute(
                select(AuditLog.tenant_id, func.count(AuditLog.id))
                .select_from(base_query.subquery())
                .where(AuditLog.tenant_id.isnot(None))
                .group_by(AuditLog.tenant_id)
            )
            audits_by_tenant = dict(tenant_result.fetchall())

            # Get hourly distribution
            hour_result = await session.execute(
                select(
                    func.extract("hour", AuditLog.created_at), func.count(AuditLog.id)
                )
                .select_from(base_query.subquery())
                .group_by(func.extract("hour", AuditLog.created_at))
            )
            audits_by_hour = {
                str(int(hour)): count for hour, count in hour_result.fetchall()
            }

            # Get daily distribution
            day_result = await session.execute(
                select(func.date(AuditLog.created_at), func.count(AuditLog.id))
                .select_from(base_query.subquery())
                .group_by(func.date(AuditLog.created_at))
            )
            audits_by_day = {str(day): count for day, count in day_result.fetchall()}

            # Get average execution time
            avg_time_result = await session.execute(
                select(func.avg(AuditLog.execution_time_ms))
                .select_from(base_query.subquery())
                .where(AuditLog.execution_time_ms.isnot(None))
            )
            average_execution_time = avg_time_result.scalar()

            # Calculate error rate
            error_count_result = await session.execute(
                select(func.count(AuditLog.id))
                .select_from(base_query.subquery())
                .where(AuditLog.status == AuditStatus.FAILED.value)
            )
            error_count = error_count_result.scalar()
            error_rate = (error_count / total_audits * 100) if total_audits > 0 else 0

            return AuditStatsSchema(
                total_audits=total_audits,
                audits_by_action=audits_by_action,
                audits_by_entity=audits_by_entity,
                audits_by_user=audits_by_user,
                audits_by_severity=audits_by_severity,
                audits_by_status=audits_by_status,
                audits_by_tenant=audits_by_tenant,
                audits_by_hour=audits_by_hour,
                audits_by_day=audits_by_day,
                average_execution_time=(
                    float(average_execution_time) if average_execution_time else None
                ),
                error_rate=error_rate,
            )

        except SQLAlchemyError as e:
            logger.error(f"Failed to get audit stats: {e}")
            raise DatabaseError(f"Failed to get audit stats: {e}")

    # Event-driven audit logging

    async def create_audit_event(
        self,
        event_data: AuditEventCreateSchema,
        db_session: AsyncSession | None = None,
    ) -> UUID:
        """
        Create an audit event for asynchronous processing.

        Args:
            event_data: Event data
            db_session: Database session (optional)

        Returns:
            Event ID
        """
        session = db_session or self.db_session
        if not session:
            raise ConfigurationError("No database session available")

        try:
            audit_event = AuditEvent(
                event_type=event_data.event_type,
                event_data=event_data.event_data,
                event_metadata=event_data.event_metadata,
                priority=event_data.priority,
                max_retries=event_data.max_retries,
            )

            session.add(audit_event)
            await session.commit()
            await session.refresh(audit_event)

            # Add to processing queue
            await self._event_queue.put(audit_event.id)

            logger.info(f"Created audit event: {audit_event.id}")
            return audit_event.id

        except SQLAlchemyError as e:
            await session.rollback()
            logger.error(f"Failed to create audit event: {e}")
            raise DatabaseError(f"Failed to create audit event: {e}")

    async def start_event_processing(self, num_workers: int = 3):
        """
        Start event processing workers.

        Args:
            num_workers: Number of worker tasks to start
        """
        if self._is_processing:
            logger.warning("Event processing is already running")
            return

        self._is_processing = True

        for i in range(num_workers):
            task = asyncio.create_task(self._event_worker(f"worker-{i}"))
            self._processing_tasks.append(task)

        logger.info(f"Started {num_workers} event processing workers")

    async def stop_event_processing(self):
        """Stop event processing workers."""
        if not self._is_processing:
            return

        self._is_processing = False

        # Cancel all processing tasks
        for task in self._processing_tasks:
            task.cancel()

        # Wait for tasks to complete
        await asyncio.gather(*self._processing_tasks, return_exceptions=True)
        self._processing_tasks.clear()

        logger.info("Stopped event processing workers")

    async def _event_worker(self, worker_name: str):
        """
        Event processing worker.

        Args:
            worker_name: Name of the worker
        """
        logger.info(f"Event worker {worker_name} started")

        while self._is_processing:
            try:
                # Get event from queue with timeout
                event_id = await asyncio.wait_for(self._event_queue.get(), timeout=1.0)

                await self._process_audit_event(event_id)

            except TimeoutError:
                # No events in queue, continue
                continue
            except Exception as e:
                logger.error(f"Error in event worker {worker_name}: {e}")
                await asyncio.sleep(1)  # Brief pause before retrying

        logger.info(f"Event worker {worker_name} stopped")

    async def _process_audit_event(self, event_id: UUID):
        """
        Process a single audit event.

        Args:
            event_id: Event ID to process
        """
        async with get_async_db_session() as session:
            try:
                # Get event
                result = await session.execute(
                    select(AuditEvent).where(AuditEvent.id == event_id)
                )
                event = result.scalar_one_or_none()

                if not event:
                    logger.warning(f"Audit event {event_id} not found")
                    return

                # Update status to processing
                await session.execute(
                    update(AuditEvent)
                    .where(AuditEvent.id == event_id)
                    .values(status="PROCESSING")
                )
                await session.commit()

                # Process the event based on type
                if event.event_type == "AUDIT_LOG":
                    await self._process_audit_log_event(event, session)
                elif event.event_type == "BULK_AUDIT":
                    await self._process_bulk_audit_event(event, session)
                else:
                    logger.warning(f"Unknown event type: {event.event_type}")

                # Mark as completed
                await session.execute(
                    update(AuditEvent)
                    .where(AuditEvent.id == event_id)
                    .values(status="COMPLETED", processed_at=datetime.now(timezone.utc))
                )
                await session.commit()

                logger.info(f"Processed audit event: {event_id}")

            except Exception as e:
                logger.error(f"Failed to process audit event {event_id}: {e}")

                # Update retry count and status
                await session.execute(
                    update(AuditEvent)
                    .where(AuditEvent.id == event_id)
                    .values(
                        status=(
                            "FAILED"
                            if event.retry_count >= event.max_retries
                            else "RETRY"
                        ),
                        retry_count=event.retry_count + 1,
                        error_message=str(e),
                        failed_at=datetime.now(timezone.utc),
                        next_retry_at=datetime.now(timezone.utc) + timedelta(minutes=5),
                    )
                )
                await session.commit()

    async def _process_audit_log_event(self, event: AuditEvent, session: AsyncSession):
        """Process audit log event."""
        # audit_data = AuditCreateSchema(**event.event_data)
        # await self.create_audit_log(audit_data, session)

    async def _process_bulk_audit_event(self, event: AuditEvent, session: AsyncSession):
        """Process bulk audit event."""
        bulk_data = AuditBulkCreateSchema(**event.event_data)
        await self.bulk_create_audit_logs(bulk_data, session)


# ORM Hooks and Decorators


def audit_hook(
    entity_name: str,
    action: AuditAction,
    capture_old_values: bool = True,
    capture_new_values: bool = True,
    severity: AuditSeverity = AuditSeverity.LOW,
):
    """
    Decorator for automatic audit logging of function calls.

    Args:
        entity_name: Name of the entity being audited
        action: Action being performed
        capture_old_values: Whether to capture old values
        capture_new_values: Whether to capture new values
        severity: Severity level of the audit
    """

    def decorator(func: Callable):
        @wraps(func)
        async def async_wrapper(*args, **kwargs):
            time.time()
            # status = AuditStatus.SUCCESS
            #             try:
            # Capture old values if needed
            # if capture_old_values and len(args) > 0:
            #     # Try to extract entity data from first argument
            #     entity = args[0]
            #     if hasattr(entity, "__dict__"):
            # old_values = {
            #                             k: v
            #                             for k, v in entity.__dict__.items()
            #                             if not k.startswith("_")
            #                         }

            # Execute the function
            #                 result = await func(*args, **kwargs)
            #
            #                 # Capture new values if needed
            #                 if capture_new_values and len(args) > 0:
            #                     entity = args[0]
            #                     if hasattr(entity, "__dict__"):
            #                         # new_values = {
            #                             k: v
            #                             for k, v in entity.__dict__.items()
            #                             if not k.startswith("_")
            #                         }

            #                 return result

            #             except Exception as e:
            #                 # error_message = str(e)
            #                 # status = AuditStatus.FAILED
            #                 raise
            #
            #             finally:
            #                 # Create audit log
            #                 try:
            #                     # execution_time = int((time.time() - start_time) * 1000)
            #
            #                     # audit_data = AuditCreateSchema(
            #     entity_name=entity_name,
            #     entity_id=str(uuid4()),  # Generate or extract from context
            #     action=action,
            #     old_values=old_values,
            #     new_values=new_values,
            #     severity=severity,
            #     status=status,
            #     error_message=error_message,
            #     execution_time_ms=execution_time,
            # )

            # Create audit event for async processing
            #                     event_data = AuditEventCreateSchema(
            #                         event_type="AUDIT_LOG", event_data={}  # audit_data.dict()
            #                     )
            #
            #                     async with get_async_db_session() as session:
            #                         audit_service = AuditService(session)
            #                         await audit_service.create_audit_event(event_data, session)
            #
            #                 except Exception as audit_error:
            #                     logger.error(f"Failed to create audit log: {audit_error}")
            #
            #         @wraps(func)
            #         def sync_wrapper(*args, **kwargs):
            #             start_time = time.time()
            #             old_values = None
            #             new_values = None
            #             error_message = None
            #             status = AuditStatus.SUCCESS

            #             try:
            #                 # Capture old values if needed
            #                 if capture_old_values and len(args) > 0:
            #                     entity = args[0]
            #                     if hasattr(entity, "__dict__"):
            #                         # old_values = {
            #                             k: v
            #                             for k, v in entity.__dict__.items()
            #                             if not k.startswith("_")
            # }

            # Execute the function
            #                 result = func(*args, **kwargs)

            # Capture new values if needed
            #                 if capture_new_values and len(args) > 0:
            #                     entity = args[0]
            #                     if hasattr(entity, "__dict__"):
            #                         new_values = {
            #                             k: v
            #                             for k, v in entity.__dict__.items()
            #                             if not k.startswith("_")
            #                         # }
            #
            #                 return result
            #
            #             except Exception as e:
            #                 # error_message = str(e)
            #                 status = AuditStatus.FAILED
            #                 raise
            #             finally:
            # Create audit log (sync version)
            #                 try:
            #                     # execution_time = int((time.time() - start_time) * 1000)
            #
            #                     # audit_data = AuditCreateSchema(
            #                     #     entity_name=entity_name,
            #                     #     entity_id=str(uuid4()),
            #                     #     action=action,
            #                     #     old_values=old_values,
            #     new_values=new_values,
            #     severity=severity,
            #     status=status,
            #     error_message=error_message,
            #     execution_time_ms=execution_time,
            # )

            # For sync functions, we'll create the audit log directly
            # This is a simplified version - in production, you might want
            # to use a background task queue
            #                     logger.info(
            #                         f"Audit: {entity_name} - {action.value} - {status.value}"
            #                     )
            #
            #                 except Exception as audit_error:
            #                     logger.error(f"Failed to create audit log: {audit_error}")
            #
            #         # Return appropriate wrapper based on function type
            #         if asyncio.iscoroutinefunction(func):
            #             return async_wrapper
            #         else:
            # return sync_wrapper
            pass

    return decorator


class AuditContext:
    """
    # Context manager for audit logging with automatic cleanup.
    """

    def __init__(
        self,
        entity_name: str,
        entity_id: str,
        action: AuditAction,
        user_id: str | None = None,
        tenant_id: str | None = None,
        **kwargs,
    ):
        self.entity_name = entity_name
        self.entity_id = entity_id
        self.action = action
        self.user_id = user_id
        self.tenant_id = tenant_id
        self.kwargs = kwargs
        self.start_time = None
        self.audit_service = None

    async def __aenter__(self):
        self.start_time = time.time()
        self.audit_service = AuditService()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self.audit_service:
            pass
            # execution_time = int((time.time() - self.start_time) * 1000)
            # status = AuditStatus.FAILED if exc_type else AuditStatus.SUCCESS
            # error_message = str(exc_val) if exc_val else None

            # audit_data = AuditCreateSchema(
            #                 entity_name=self.entity_name,
            #                 entity_id=self.entity_id,
            #                 action=self.action,
            #                 user_id=self.user_id,
            #                 tenant_id=self.tenant_id,
            #                 severity=AuditSeverity.LOW,
            #                 status=status,
            #                 error_message=error_message,
            #                 execution_time_ms=execution_time,
            #                 **self.kwargs,
            #             )
            #
            #             try:
            #                 await self.audit_service.create_audit_log(audit_data)
            #             except Exception as e:
            #                 logger.error(
            #                     f"Failed to create audit log in context: {e}"
            #                 )
            #
            #


# Utility functions


async def log_audit(
    entity_name: str,
    entity_id: str,
    action: AuditAction,
    user_id: str | None = None,
    tenant_id: str | None = None,
    old_values: dict[str, Any] | None = None,
    new_values: dict[str, Any] | None = None,
    **kwargs,
) -> UUID:
    """
    Quick utility function to log an audit entry.

    Args:
        entity_name: Name of the entity
        entity_id: ID of the entity
        action: Action performed
        user_id: User ID
        tenant_id: Tenant ID
        old_values: Previous values
        new_values: New values
        **kwargs: Additional audit data

    Returns:
        Audit log ID
    """
    async with get_async_db_session() as session:
        audit_service = AuditService(session)

        audit_data = AuditCreateSchema(
                    entity_name=entity_name,
                    entity_id=entity_id,
                    action=action,
                    user_id=user_id,
                    tenant_id=tenant_id,
                    old_values=old_values,
                    new_values=new_values,
                    **kwargs,
                )

        audit_log = await audit_service.create_audit_log(audit_data, session)
        return audit_log.id



async def log_audit_event(
    event_type: str, event_data: dict[str, Any], priority: int = 5
) -> UUID:
    """
    Quick utility function to log an audit event.

    Args:
        # event_type: Type of event
        event_data: Event data
        priority: Processing priority

    Returns:
        Event ID
    """
    async with get_async_db_session() as session:
        audit_service = AuditService(session)

        event_schema = AuditEventCreateSchema(
            event_type=event_type, event_data=event_data, priority=priority
        )

        return await audit_service.create_audit_event(event_schema, session)
