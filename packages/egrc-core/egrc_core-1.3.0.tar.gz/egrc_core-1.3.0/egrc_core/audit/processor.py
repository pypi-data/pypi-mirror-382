from sqlalchemy import select


"""
Audit event processor for EGRC Platform.

This module provides event processing capabilities for asynchronous
audit logging, including queue management, worker coordination,
and event processing strategies.
"""

import asyncio
import logging
import time
from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from enum import Enum
from typing import Any
from uuid import UUID

from sqlalchemy import and_, delete, update
from sqlalchemy.ext.asyncio import AsyncSession

from ..database import get_async_db_session
from ..exceptions.exceptions import EGRCException
from .models import AuditEvent
from .schemas import AuditBulkCreateSchema, AuditCreateSchema
from .service import AuditService


logger = logging.getLogger(__name__)


class EventStatus(Enum):
    """Event processing status."""

    PENDING = "PENDING"
    PROCESSING = "PROCESSING"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"
    RETRY = "RETRY"
    CANCELLED = "CANCELLED"


class EventPriority(Enum):
    """Event processing priority."""

    LOW = 1
    NORMAL = 5
    HIGH = 8
    CRITICAL = 10


@dataclass
class ProcessingResult:
    """Result of event processing."""

    success: bool
    event_id: UUID
    processing_time_ms: int
    error_message: str | None = None
    retry_count: int = 0


class EventProcessor:
    """
    Event processor for audit events.

    Handles asynchronous processing of audit events with support for
    priority queues, retry mechanisms, and error handling.
    """

    def __init__(
        self,
        max_workers: int = 5,
        max_retries: int = 3,
        retry_delay: int = 60,  # seconds
        batch_size: int = 100,
        processing_timeout: int = 300,  # seconds
    ):
        self.max_workers = max_workers
        self.max_retries = max_retries
        self.retry_delay = retry_delay
        self.batch_size = batch_size
        self.processing_timeout = processing_timeout

        # Processing queues by priority
        self.queues = {
            EventPriority.CRITICAL: asyncio.Queue(),
            EventPriority.HIGH: asyncio.Queue(),
            EventPriority.NORMAL: asyncio.Queue(),
            EventPriority.LOW: asyncio.Queue(),
        }

        # Worker tasks
        self.workers = []
        self.is_running = False

        # Statistics
        self.stats = {"processed": 0, "failed": 0, "retried": 0, "start_time": None}

        # Event handlers
        self.event_handlers = {}
        self._register_default_handlers()

    def _register_default_handlers(self):
        """Register default event handlers."""
        self.event_handlers = {
            "AUDIT_LOG": self._handle_audit_log_event,
            "BULK_AUDIT": self._handle_bulk_audit_event,
            "AUDIT_CONFIG": self._handle_audit_config_event,
            "RETENTION_POLICY": self._handle_retention_policy_event,
            "CLEANUP": self._handle_cleanup_event,
            "EXPORT": self._handle_export_event,
            "NOTIFICATION": self._handle_notification_event,
        }

    async def start(self):
        """Start the event processor."""
        if self.is_running:
            logger.warning("Event processor is already running")
            return

        self.is_running = True
        self.stats["start_time"] = datetime.now(timezone.utc)

        # Start worker tasks
        for i in range(self.max_workers):
            worker = asyncio.create_task(self._worker(f"worker-{i}"))
            self.workers.append(worker)

        # Start retry processor
        retry_processor = asyncio.create_task(self._retry_processor())
        self.workers.append(retry_processor)

        # Start cleanup processor
        cleanup_processor = asyncio.create_task(self._cleanup_processor())
        self.workers.append(cleanup_processor)

        logger.info(f"Started event processor with {self.max_workers} workers")

    async def stop(self):
        """Stop the event processor."""
        if not self.is_running:
            return

        self.is_running = False

        # Cancel all workers
        for worker in self.workers:
            worker.cancel()

        # Wait for workers to complete
        await asyncio.gather(*self.workers, return_exceptions=True)
        self.workers.clear()

        logger.info("Stopped event processor")

    async def submit_event(
        self,
        event_type: str,
        event_data: dict[str, Any],
        priority: EventPriority = EventPriority.NORMAL,
        max_retries: int | None = None,
        delay_seconds: int = 0,
    ) -> UUID:
        """
        Submit an event for processing.

        Args:
            event_type: Type of event
            event_data: Event data
            priority: Processing priority
            max_retries: Maximum retry attempts
            delay_seconds: Delay before processing

        Returns:
            Event ID
        """
        try:
            # Create audit event
            async with get_async_db_session() as session:
                audit_event = AuditEvent(
                    event_type=event_type,
                    event_data=event_data,
                    priority=priority.value,
                    max_retries=max_retries or self.max_retries,
                    status=EventStatus.PENDING.value,
                )

                session.add(audit_event)
                await session.commit()
                await session.refresh(audit_event)

                # Add to processing queue with delay
                if delay_seconds > 0:
                    asyncio.create_task(
                        self._delayed_queue_event(audit_event.id, delay_seconds)
                    )
                else:
                    await self.queues[priority].put(audit_event.id)

                logger.info(f"Submitted event {audit_event.id} of type {event_type}")
                return audit_event.id

        except Exception as e:
            logger.error(f"Failed to submit event: {e}")
            raise EGRCException(f"Failed to submit event: {e}")

    async def _delayed_queue_event(self, event_id: UUID, delay_seconds: int):
        """Queue an event after a delay."""
        await asyncio.sleep(delay_seconds)
        await self.queues[EventPriority.NORMAL].put(event_id)

    async def _worker(self, worker_name: str):
        """
        Worker task for processing events.

        Args:
            worker_name: Name of the worker
        """
        logger.info(f"Worker {worker_name} started")

        while self.is_running:
            try:
                # Get event from highest priority queue
                event_id = await self._get_next_event()

                if event_id:
                    await self._process_event(event_id, worker_name)

            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Error in worker {worker_name}: {e}")
                await asyncio.sleep(1)  # Brief pause before retrying

        logger.info(f"Worker {worker_name} stopped")

    async def _get_next_event(self) -> UUID | None:
        """
        Get the next event to process from priority queues.

        Returns:
            Event ID or None if no events available
        """
        # Check queues in priority order
        for priority in [
            EventPriority.CRITICAL,
            EventPriority.HIGH,
            EventPriority.NORMAL,
            EventPriority.LOW,
        ]:
            try:
                event_id = await asyncio.wait_for(
                    self.queues[priority].get(), timeout=1.0
                )
                return event_id
            except TimeoutError:
                continue

        return None

    async def _process_event(self, event_id: UUID, worker_name: str):
        """
        Process a single event.

        Args:
            event_id: Event ID to process
            worker_name: Name of the worker processing the event
        """
        start_time = time.time()

        try:
            async with get_async_db_session() as session:
                # Get event
                result = await session.execute(
                    select(AuditEvent).where(AuditEvent.id == event_id)
                )
                event = result.scalar_one_or_none()

                if not event:
                    logger.warning(f"Event {event_id} not found")
                    return

                # Check if event should be processed
                if event.status not in [
                    EventStatus.PENDING.value,
                    EventStatus.RETRY.value,
                ]:
                    logger.warning(
                        f"Event {event_id} is not in processable state: {event.status}"
                    )
                    return

                # Update status to processing
                await session.execute(
                    update(AuditEvent)
                    .where(AuditEvent.id == event_id)
                    .values(
                        status=EventStatus.PROCESSING.value,
                        retry_count=event.retry_count,
                    )
                )
                await session.commit()

                # Process the event
                handler = self.event_handlers.get(event.event_type)
                if not handler:
                    raise EGRCException(
                        f"No handler for event type: {event.event_type}"
                    )

                # Process with timeout
                await asyncio.wait_for(
                    handler(event, session), timeout=self.processing_timeout
                )

                # Mark as completed
                processing_time = int((time.time() - start_time) * 1000)
                await session.execute(
                    update(AuditEvent)
                    .where(AuditEvent.id == event_id)
                    .values(
                        status=EventStatus.COMPLETED.value,
                        processed_at=datetime.now(timezone.utc),
                    )
                )
                await session.commit()

                self.stats["processed"] += 1
                logger.info(
                    f"Worker {worker_name} processed event {event_id} "
                    f"in {processing_time}ms"
                )

        except TimeoutError:
            await self._handle_event_failure(
                event_id, f"Processing timeout after {self.processing_timeout}s"
            )
        except Exception as e:
            await self._handle_event_failure(event_id, str(e))

    async def _handle_event_failure(self, event_id: UUID, error_message: str):
        """
        Handle event processing failure.

        Args:
            event_id: Event ID that failed
            error_message: Error message
        """
        try:
            async with get_async_db_session() as session:
                # Get event
                result = await session.execute(
                    select(AuditEvent).where(AuditEvent.id == event_id)
                )
                event = result.scalar_one_or_none()

                if not event:
                    return

                new_retry_count = event.retry_count + 1

                if new_retry_count >= event.max_retries:
                    # Max retries exceeded, mark as failed
                    await session.execute(
                        update(AuditEvent)
                        .where(AuditEvent.id == event_id)
                        .values(
                            status=EventStatus.FAILED.value,
                            retry_count=new_retry_count,
                            error_message=error_message,
                            failed_at=datetime.now(timezone.utc),
                        )
                    )
                    self.stats["failed"] += 1
                    logger.error(
                        f"Event {event_id} failed permanently: {error_message}"
                    )
                else:
                    # Schedule retry
                    retry_delay = self.retry_delay * (
                        2 ** (new_retry_count - 1)
                    )  # Exponential backoff
                    next_retry = datetime.now(timezone.utc) + timedelta(
                        seconds=retry_delay
                    )

                    await session.execute(
                        update(AuditEvent)
                        .where(AuditEvent.id == event_id)
                        .values(
                            status=EventStatus.RETRY.value,
                            retry_count=new_retry_count,
                            error_message=error_message,
                            next_retry_at=next_retry,
                        )
                    )
                    self.stats["retried"] += 1
                    logger.warning(
                        f"Event {event_id} failed, will retry in {retry_delay}s: "
                        f"{error_message}"
                    )

                await session.commit()

        except Exception as e:
            logger.error(f"Failed to handle event failure for {event_id}: {e}")

    # Event handlers

    async def _handle_audit_log_event(self, event: AuditEvent, session: AsyncSession):
        """Handle audit log event."""
        try:
            audit_data = AuditCreateSchema(**event.event_data)
            audit_service = AuditService(session)
            await audit_service.create_audit_log(audit_data, session)
        except Exception as e:
            logger.error(f"Failed to process audit log event: {e}")
            raise

    async def _handle_bulk_audit_event(self, event: AuditEvent, session: AsyncSession):
        """Handle bulk audit event."""
        try:
            bulk_data = AuditBulkCreateSchema(**event.event_data)
            audit_service = AuditService(session)
            await audit_service.bulk_create_audit_logs(bulk_data, session)
        except Exception as e:
            logger.error(f"Failed to process bulk audit event: {e}")
            raise

    async def _handle_audit_config_event(
        self, event: AuditEvent, session: AsyncSession
    ):
        """Handle audit configuration event."""
        try:
            # Process audit configuration changes
            config_data = event.event_data
            logger.info(f"Processing audit config event: {config_data}")
            # Implementation would depend on specific configuration requirements
        except Exception as e:
            logger.error(f"Failed to process audit config event: {e}")
            raise

    async def _handle_retention_policy_event(
        self, event: AuditEvent, session: AsyncSession
    ):
        """Handle retention policy event."""
        try:
            # Process retention policy execution
            policy_data = event.event_data
            logger.info(f"Processing retention policy event: {policy_data}")
            # Implementation would execute retention policies
        except Exception as e:
            logger.error(f"Failed to process retention policy event: {e}")
            raise

    async def _handle_cleanup_event(self, event: AuditEvent, session: AsyncSession):
        """Handle cleanup event."""
        try:
            # Process cleanup operations
            cleanup_data = event.event_data
            logger.info(f"Processing cleanup event: {cleanup_data}")
            # Implementation would perform cleanup operations
        except Exception as e:
            logger.error(f"Failed to process cleanup event: {e}")
            raise

    async def _handle_export_event(self, event: AuditEvent, session: AsyncSession):
        """Handle export event."""
        try:
            # Process audit data export
            export_data = event.event_data
            logger.info(f"Processing export event: {export_data}")
            # Implementation would generate and send exports
        except Exception as e:
            logger.error(f"Failed to process export event: {e}")
            raise

    async def _handle_notification_event(
        self, event: AuditEvent, session: AsyncSession
    ):
        """Handle notification event."""
        try:
            # Process notifications
            notification_data = event.event_data
            logger.info(f"Processing notification event: {notification_data}")
            # Implementation would send notifications
        except Exception as e:
            logger.error(f"Failed to process notification event: {e}")
            raise

    # Background processors

    async def _retry_processor(self):
        """Process events that need to be retried."""
        logger.info("Retry processor started")

        while self.is_running:
            try:
                async with get_async_db_session() as session:
                    # Find events that need retry
                    result = await session.execute(
                        select(AuditEvent)
                        .where(
                            and_(
                                AuditEvent.status == EventStatus.RETRY.value,
                                AuditEvent.next_retry_at <= datetime.now(timezone.utc),
                            )
                        )
                        .limit(self.batch_size)
                    )
                    retry_events = result.scalars().all()

                    for event in retry_events:
                        # Determine priority
                        priority = EventPriority(event.priority)
                        await self.queues[priority].put(event.id)

                    if retry_events:
                        logger.info(f"Queued {len(retry_events)} events for retry")

                await asyncio.sleep(30)  # Check every 30 seconds

            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Error in retry processor: {e}")
                await asyncio.sleep(60)

        logger.info("Retry processor stopped")

    async def _cleanup_processor(self):
        """Clean up old completed and failed events."""
        logger.info("Cleanup processor started")

        while self.is_running:
            try:
                async with get_async_db_session() as session:
                    # Clean up old completed events (older than 7 days)
                    cutoff_date = datetime.now(timezone.utc) - timedelta(days=7)

                    result = await session.execute(
                        delete(AuditEvent).where(
                            and_(
                                AuditEvent.status.in_(
                                    [
                                        EventStatus.COMPLETED.value,
                                        EventStatus.FAILED.value,
                                    ]
                                ),
                                AuditEvent.processed_at < cutoff_date,
                            )
                        )
                    )

                    deleted_count = result.rowcount
                    if deleted_count > 0:
                        logger.info(f"Cleaned up {deleted_count} old events")

                await asyncio.sleep(3600)  # Run every hour

            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Error in cleanup processor: {e}")
                await asyncio.sleep(3600)

        logger.info("Cleanup processor stopped")

    # Statistics and monitoring

    def get_stats(self) -> dict[str, Any]:
        """Get processing statistics."""
        uptime = None
        if self.stats["start_time"]:
            uptime = (
                datetime.now(timezone.utc) - self.stats["start_time"]
            ).total_seconds()

        return {
            "is_running": self.is_running,
            "workers": len(self.workers),
            "uptime_seconds": uptime,
            "processed": self.stats["processed"],
            "failed": self.stats["failed"],
            "retried": self.stats["retried"],
            "queue_sizes": {
                priority.name: queue.qsize() for priority, queue in self.queues.items()
            },
        }

    async def get_queue_status(self) -> dict[str, Any]:
        """Get detailed queue status."""
        status = {}

        for priority, queue in self.queues.items():
            status[priority.name] = {"size": queue.qsize(), "maxsize": queue.maxsize}

        return status


# Global event processor instance
event_processor = EventProcessor()


async def start_event_processor(max_workers: int = 5):
    """
    Start the global event processor.

    Args:
        max_workers: Number of worker tasks
    """

    event_processor.max_workers = max_workers
    await event_processor.start()


async def stop_event_processor():
    """Stop the global event processor."""

    await event_processor.stop()


async def submit_audit_event(
    event_type: str,
    event_data: dict[str, Any],
    priority: EventPriority = EventPriority.NORMAL,
    delay_seconds: int = 0,
) -> UUID:
    """
    Submit an audit event for processing.

    Args:
        event_type: Type of event
        event_data: Event data
        priority: Processing priority
        delay_seconds: Delay before processing

    Returns:
        Event ID
    """

    return await event_processor.submit_event(
        event_type=event_type,
        event_data=event_data,
        priority=priority,
        delay_seconds=delay_seconds,
    )


def get_processor_stats() -> dict[str, Any]:
    """Get event processor statistics."""

    return event_processor.get_stats()


async def get_queue_status() -> dict[str, Any]:
    """Get queue status."""

    return await event_processor.get_queue_status()
