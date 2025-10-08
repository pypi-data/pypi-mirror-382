"""
EGRC Core - Monitoring Integration for Individual Services

This module provides standardized logging and monitoring integration for all EGRC services.
Each service uses this to send structured logs, metrics, and security events to external systems.
"""

import asyncio
import logging
import os
from datetime import datetime, timezone
from typing import Any

import aiohttp
from pydantic import BaseModel, Field


# from .structured_logging import StructuredLogger


class LogEvent(BaseModel):
    """Standardized log event structure"""

    timestamp: datetime
    service: str
    level: str
    message: str
    fields: dict[str, Any] = Field(default_factory=dict)
    hostname: str | None = None
    environment: str | None = None
    version: str | None = None
    build_id: str | None = None
    commit_sha: str | None = None
    trace_id: str | None = None
    span_id: str | None = None


class MetricEvent(BaseModel):
    """Standardized metric event structure"""

    timestamp: datetime
    service: str
    metric_name: str
    value: int | float
    tags: dict[str, str] = Field(default_factory=dict)
    hostname: str | None = None
    environment: str | None = None
    trace_id: str | None = None


class SecurityEvent(BaseModel):
    """Standardized security event structure"""

    timestamp: datetime
    event_type: str
    severity: str
    source: str
    target: str
    action: str
    result: str
    details: dict[str, Any] = Field(default_factory=dict)
    user_id: str | None = None
    session_id: str | None = None
    ip_address: str | None = None
    trace_id: str | None = None


class MonitoringIntegration:
    """Monitoring integration for individual services"""

    def __init__(self, service_name: str, environment: str | None = None):
        self.service_name = service_name
        self.environment = environment or os.getenv("ENVIRONMENT", "development")
        self.hostname = os.getenv("HOSTNAME", "localhost")
        self.version = os.getenv("SERVICE_VERSION", "1.0.0")
        self.build_id = os.getenv("BUILD_ID", "unknown")
        self.commit_sha = os.getenv("COMMIT_SHA", "unknown")

        # Infrastructure service endpoint
        self.infra_endpoint = os.getenv("EGRC_INFRA_ENDPOINT", "http://egrc-infra:8009")

        # Session for HTTP requests
        self.session: aiohttp.ClientSession | None = None

        # Event queues for batching
        self.log_queue: list[LogEvent] = []
        self.metric_queue: list[MetricEvent] = []
        self.security_queue: list[SecurityEvent] = []

        # Batch processing settings
        self.batch_size = int(os.getenv("MONITORING_BATCH_SIZE", "100"))
        self.batch_timeout = float(os.getenv("MONITORING_BATCH_TIMEOUT", "5.0"))

        # Background task
        self._batch_task: asyncio.Task | None = None
        self._running = False

        # Logger
        self.logger = logging.getLogger(f"{service_name}.monitoring")

    async def __aenter__(self):
        """Async context manager entry"""
        self.session = aiohttp.ClientSession(
            timeout=aiohttp.ClientTimeout(total=30),
            connector=aiohttp.TCPConnector(limit=10),
        )
        await self.start()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit"""
        await self.stop()
        if self.session:
            await self.session.close()

    async def start(self):
        """Start the monitoring integration"""
        if not self._running:
            self._running = True
            self._batch_task = asyncio.create_task(self._batch_processor())
            self.logger.info("Monitoring integration started")

    async def stop(self):
        """Stop the monitoring integration"""
        if self._running:
            self._running = False
            if self._batch_task:
                self._batch_task.cancel()
                try:
                    await self._batch_task
                except asyncio.CancelledError:
                    pass

            # Send remaining events
            await self._flush_queues()
            self.logger.info("Monitoring integration stopped")

    async def _batch_processor(self):
        """Process batched events"""
        while self._running:
            try:
                await asyncio.sleep(self.batch_timeout)
                await self._flush_queues()
            except asyncio.CancelledError:
                break
            except Exception as e:
                self.logger.error(f"Error in batch processor: {e}")

    async def _flush_queues(self):
        """Flush all event queues"""
        if self.log_queue:
            await self._send_log_events(self.log_queue.copy())
            self.log_queue.clear()

        if self.metric_queue:
            await self._send_metric_events(self.metric_queue.copy())
            self.metric_queue.clear()

        if self.security_queue:
            await self._send_security_events(self.security_queue.copy())
            self.security_queue.clear()

    async def _send_log_events(self, events: list[LogEvent]):
        """Send log events to infrastructure service"""
        try:
            endpoint = (
                f"{self.infra_endpoint}/api/v1/monitoring-integration/events/logs"
            )

            for event in events:
                payload = {
                    "service": event.service,
                    "level": event.level,
                    "message": event.message,
                    "fields": event.fields,
                    "hostname": event.hostname,
                    "environment": event.environment,
                    "version": event.version,
                    "build_id": event.build_id,
                    "commit_sha": event.commit_sha,
                }

                async with self.session.post(endpoint, json=payload) as response:
                    if response.status != 200:
                        self.logger.error(
                            f"Failed to send log event: {response.status}"
                        )
        except Exception as e:
            self.logger.error(f"Error sending log events: {e}")

    async def _send_metric_events(self, events: list[MetricEvent]):
        """Send metric events to infrastructure service"""
        try:
            endpoint = (
                f"{self.infra_endpoint}/api/v1/monitoring-integration/events/metrics"
            )

            for event in events:
                payload = {
                    "service": event.service,
                    "metric_name": event.metric_name,
                    "value": event.value,
                    "tags": event.tags,
                    "hostname": event.hostname,
                    "environment": event.environment,
                }

                async with self.session.post(endpoint, json=payload) as response:
                    if response.status != 200:
                        self.logger.error(
                            f"Failed to send metric event: {response.status}"
                        )
        except Exception as e:
            self.logger.error(f"Error sending metric events: {e}")

    async def _send_security_events(self, events: list[SecurityEvent]):
        """Send security events to infrastructure service"""
        try:
            endpoint = (
                f"{self.infra_endpoint}/api/v1/monitoring-integration/events/security"
            )

            for event in events:
                payload = {
                    "event_type": event.event_type,
                    "severity": event.severity,
                    "source": event.source,
                    "target": event.target,
                    "action": event.action,
                    "result": event.result,
                    "details": event.details,
                    "user_id": event.user_id,
                    "session_id": event.session_id,
                    "ip_address": event.ip_address,
                }

                async with self.session.post(endpoint, json=payload) as response:
                    if response.status != 200:
                        self.logger.error(
                            f"Failed to send security event: {response.status}"
                        )
        except Exception as e:
            self.logger.error(f"Error sending security events: {e}")

    # Public API methods
    async def log_event(
        self,
        level: str,
        message: str,
        fields: dict[str, Any] | None = None,
        trace_id: str | None = None,
        span_id: str | None = None,
    ):
        """Log an event"""
        event = LogEvent(
            timestamp=datetime.now(timezone.utc),
            service=self.service_name,
            level=level,
            message=message,
            fields=fields or {},
            hostname=self.hostname,
            environment=self.environment,
            version=self.version,
            build_id=self.build_id,
            commit_sha=self.commit_sha,
            trace_id=trace_id,
            span_id=span_id,
        )

        self.log_queue.append(event)

        # Flush if queue is full
        if len(self.log_queue) >= self.batch_size:
            await self._flush_queues()

    async def metric_event(
        self,
        metric_name: str,
        value: int | float,
        tags: dict[str, str] | None = None,
        trace_id: str | None = None,
    ):
        """Send a metric event"""
        event = MetricEvent(
            timestamp=datetime.now(timezone.utc),
            service=self.service_name,
            metric_name=metric_name,
            value=value,
            tags=tags or {},
            hostname=self.hostname,
            environment=self.environment,
            trace_id=trace_id,
        )

        self.metric_queue.append(event)

        # Flush if queue is full
        if len(self.metric_queue) >= self.batch_size:
            await self._flush_queues()

    async def security_event(
        self,
        event_type: str,
        severity: str,
        source: str,
        target: str,
        action: str,
        result: str,
        details: dict[str, Any] | None = None,
        user_id: str | None = None,
        session_id: str | None = None,
        ip_address: str | None = None,
        trace_id: str | None = None,
    ):
        """Send a security event"""
        event = SecurityEvent(
            timestamp=datetime.now(timezone.utc),
            event_type=event_type,
            severity=severity,
            source=source,
            target=target,
            action=action,
            result=result,
            details=details or {},
            user_id=user_id,
            session_id=session_id,
            ip_address=ip_address,
            trace_id=trace_id,
        )

        self.security_queue.append(event)

        # Flush if queue is full
        if len(self.security_queue) >= self.batch_size:
            await self._flush_queues()

    # Convenience methods
    async def log_info(self, message: str, **kwargs):
        """Log info level message"""
        await self.log_event("INFO", message, kwargs)

    async def log_warning(self, message: str, **kwargs):
        """Log warning level message"""
        await self.log_event("WARNING", message, kwargs)

    async def log_error(self, message: str, **kwargs):
        """Log error level message"""
        await self.log_event("ERROR", message, kwargs)

    async def log_critical(self, message: str, **kwargs):
        """Log critical level message"""
        await self.log_event("CRITICAL", message, kwargs)

    async def counter(self, name: str, value: int = 1, **tags):
        """Send a counter metric"""
        await self.metric_event(f"counter.{name}", value, tags)

    async def gauge(self, name: str, value: int | float, **tags):
        """Send a gauge metric"""
        await self.metric_event(f"gauge.{name}", value, tags)

    async def histogram(self, name: str, value: int | float, **tags):
        """Send a histogram metric"""
        await self.metric_event(f"histogram.{name}", value, tags)

    async def timer(self, name: str, duration: float, **tags):
        """Send a timer metric"""
        await self.metric_event(f"timer.{name}", duration, tags)

    async def security_alert(
        self,
        event_type: str,
        severity: str,
        source: str,
        target: str,
        action: str,
        result: str,
        **kwargs,
    ):
        """Send a security alert"""
        await self.security_event(
            event_type=event_type,
            severity=severity,
            source=source,
            target=target,
            action=action,
            result=result,
            **kwargs,
        )


class MonitoringLogger:
    """Enhanced logger with monitoring integration"""

    def __init__(self, service_name: str, environment: str | None = None):
        self.service_name = service_name
        self.environment = environment or os.getenv("ENVIRONMENT", "development")
        self.monitoring = MonitoringIntegration(service_name, environment)
        self.logger = logging.getLogger(service_name)

    async def __aenter__(self):
        """Async context manager entry"""
        await self.monitoring.__aenter__()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit"""
        await self.monitoring.__aexit__(exc_type, exc_val, exc_tb)

    def info(self, message: str, **kwargs):
        """Log info message"""
        self.logger.info(message, extra=kwargs)
        asyncio.create_task(self.monitoring.log_info(message, **kwargs))

    def warning(self, message: str, **kwargs):
        """Log warning message"""
        self.logger.warning(message, extra=kwargs)
        asyncio.create_task(self.monitoring.log_warning(message, **kwargs))

    def error(self, message: str, **kwargs):
        """Log error message"""
        self.logger.error(message, extra=kwargs)
        asyncio.create_task(self.monitoring.log_error(message, **kwargs))

    def critical(self, message: str, **kwargs):
        """Log critical message"""
        self.logger.critical(message, extra=kwargs)
        asyncio.create_task(self.monitoring.log_critical(message, **kwargs))

    async def metric(self, name: str, value: int | float, **tags):
        """Send metric"""
        await self.monitoring.metric_event(name, value, tags)

    async def security(
        self,
        event_type: str,
        severity: str,
        source: str,
        target: str,
        action: str,
        result: str,
        **kwargs,
    ):
        """Send security event"""
        await self.monitoring.security_event(
            event_type, severity, source, target, action, result, **kwargs
        )


# Global monitoring instance
_monitoring_instance: MonitoringIntegration | None = None


def get_monitoring(
    service_name: str, environment: str | None = None
) -> MonitoringIntegration:
    """Get or create global monitoring instance"""
    global _monitoring_instance
    if _monitoring_instance is None:
        _monitoring_instance = MonitoringIntegration(service_name, environment)
    return _monitoring_instance


def get_monitoring_logger(
    service_name: str, environment: str | None = None
) -> MonitoringLogger:
    """Get monitoring logger instance"""
    return MonitoringLogger(service_name, environment)
