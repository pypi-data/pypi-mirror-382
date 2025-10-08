"""
Usage tracking service for LLM operations.

This module provides usage tracking and analytics for LLM operations,
including token usage, costs, and performance metrics.
"""

from datetime import datetime, timedelta
from typing import Any

from sqlalchemy import and_, desc, func, select

from ...database import get_async_db_session
from ...logging.utils import get_logger
from ..models.database import LLMUsageModel


logger = get_logger(__name__)


class UsageService:
    """Service for tracking LLM usage and analytics."""

    def __init__(self):
        """Initialize usage service."""
        self.logger = get_logger(
            f"{self.__class__.__module__}.{self.__class__.__name__}"
        )

    async def record_usage(
        self,
        provider: str,
        model: str,
        prompt_tokens: int,
        completion_tokens: int,
        cost: float | None = None,
        tenant_id: str | None = None,
        service_name: str | None = None,
    ) -> None:
        """
        Record usage statistics.

        Args:
            provider: LLM provider
            model: Model name
            prompt_tokens: Number of prompt tokens
            completion_tokens: Number of completion tokens
            cost: Cost in USD
            tenant_id: Tenant ID
            service_name: Service name
        """
        try:
            total_tokens = prompt_tokens + completion_tokens
            today = datetime.utcnow().date()

            async with get_async_db_session() as db:
                # Check if usage record exists for today
                query = select(LLMUsageModel).where(
                    and_(
                        LLMUsageModel.provider == provider,
                        LLMUsageModel.model == model,
                        LLMUsageModel.tenant_id == tenant_id,
                        LLMUsageModel.service_name == service_name,
                        LLMUsageModel.date == today,
                    )
                )

                result = await db.execute(query)
                usage_record = result.scalar_one_or_none()

                if usage_record:
                    # Update existing record
                    usage_record.prompt_tokens += prompt_tokens
                    usage_record.completion_tokens += completion_tokens
                    usage_record.total_tokens += total_tokens
                    usage_record.cost += cost or 0.0
                    usage_record.request_count += 1
                    usage_record.updated_at = datetime.utcnow()
                else:
                    # Create new record
                    usage_record = LLMUsageModel(
                        provider=provider,
                        model=model,
                        tenant_id=tenant_id,
                        service_name=service_name,
                        date=today,
                        prompt_tokens=prompt_tokens,
                        completion_tokens=completion_tokens,
                        total_tokens=total_tokens,
                        cost=cost or 0.0,
                        request_count=1,
                    )
                    db.add(usage_record)

                await db.commit()

                self.logger.info(
                    f"Recorded usage for {provider}/{model}",
                    extra={
                        "provider": provider,
                        "model": model,
                        "prompt_tokens": prompt_tokens,
                        "completion_tokens": completion_tokens,
                        "total_tokens": total_tokens,
                        "cost": cost,
                        "tenant_id": tenant_id,
                        "service_name": service_name,
                    },
                )

        except Exception as e:
            self.logger.error(f"Failed to record usage: {e}")
            # Don't raise exception to avoid breaking the main flow

    async def get_usage_stats(
        self,
        start_date: datetime | None = None,
        end_date: datetime | None = None,
        tenant_id: str | None = None,
        service_name: str | None = None,
        provider: str | None = None,
        model: str | None = None,
    ) -> dict[str, Any]:
        """
        Get usage statistics for a date range.

        Args:
            start_date: Start date (defaults to 30 days ago)
            end_date: End date (defaults to today)
            tenant_id: Tenant ID filter
            service_name: Service name filter
            provider: Provider filter
            model: Model filter

        Returns:
            Usage statistics
        """
        try:
            if not start_date:
                start_date = datetime.utcnow() - timedelta(days=30)
            if not end_date:
                end_date = datetime.utcnow()

            async with get_async_db_session() as db:
                query = select(LLMUsageModel).where(
                    and_(
                        LLMUsageModel.date >= start_date.date(),
                        LLMUsageModel.date <= end_date.date(),
                    )
                )

                # Apply filters
                if tenant_id:
                    query = query.where(LLMUsageModel.tenant_id == tenant_id)
                if service_name:
                    query = query.where(LLMUsageModel.service_name == service_name)
                if provider:
                    query = query.where(LLMUsageModel.provider == provider)
                if model:
                    query = query.where(LLMUsageModel.model == model)

                result = await db.execute(query)
                usage_records = result.scalars().all()

                # Calculate statistics
                total_prompt_tokens = sum(
                    record.prompt_tokens for record in usage_records
                )
                total_completion_tokens = sum(
                    record.completion_tokens for record in usage_records
                )
                total_tokens = sum(record.total_tokens for record in usage_records)
                total_cost = sum(record.cost for record in usage_records)
                total_requests = sum(record.request_count for record in usage_records)

                # Group by provider
                provider_stats = {}
                for record in usage_records:
                    if record.provider not in provider_stats:
                        provider_stats[record.provider] = {
                            "prompt_tokens": 0,
                            "completion_tokens": 0,
                            "total_tokens": 0,
                            "cost": 0.0,
                            "request_count": 0,
                        }

                    provider_stats[record.provider][
                        "prompt_tokens"
                    ] += record.prompt_tokens
                    provider_stats[record.provider][
                        "completion_tokens"
                    ] += record.completion_tokens
                    provider_stats[record.provider][
                        "total_tokens"
                    ] += record.total_tokens
                    provider_stats[record.provider]["cost"] += record.cost
                    provider_stats[record.provider][
                        "request_count"
                    ] += record.request_count

                # Group by model
                model_stats = {}
                for record in usage_records:
                    model_key = f"{record.provider}/{record.model}"
                    if model_key not in model_stats:
                        model_stats[model_key] = {
                            "prompt_tokens": 0,
                            "completion_tokens": 0,
                            "total_tokens": 0,
                            "cost": 0.0,
                            "request_count": 0,
                        }

                    model_stats[model_key]["prompt_tokens"] += record.prompt_tokens
                    model_stats[model_key][
                        "completion_tokens"
                    ] += record.completion_tokens
                    model_stats[model_key]["total_tokens"] += record.total_tokens
                    model_stats[model_key]["cost"] += record.cost
                    model_stats[model_key]["request_count"] += record.request_count

                return {
                    "period": {
                        "start_date": start_date.isoformat(),
                        "end_date": end_date.isoformat(),
                    },
                    "totals": {
                        "prompt_tokens": total_prompt_tokens,
                        "completion_tokens": total_completion_tokens,
                        "total_tokens": total_tokens,
                        "cost": total_cost,
                        "request_count": total_requests,
                    },
                    "by_provider": provider_stats,
                    "by_model": model_stats,
                    "filters": {
                        "tenant_id": tenant_id,
                        "service_name": service_name,
                        "provider": provider,
                        "model": model,
                    },
                }

        except Exception as e:
            self.logger.error(f"Failed to get usage stats: {e}")
            raise

    async def get_daily_usage(
        self,
        days: int = 30,
        tenant_id: str | None = None,
        service_name: str | None = None,
        provider: str | None = None,
    ) -> list[dict[str, Any]]:
        """
        Get daily usage for the last N days.

        Args:
            days: Number of days to retrieve
            tenant_id: Tenant ID filter
            service_name: Service name filter
            provider: Provider filter

        Returns:
            List of daily usage records
        """
        try:
            end_date = datetime.utcnow().date()
            start_date = end_date - timedelta(days=days)

            async with get_async_db_session() as db:
                query = select(LLMUsageModel).where(
                    and_(
                        LLMUsageModel.date >= start_date,
                        LLMUsageModel.date <= end_date,
                    )
                )

                # Apply filters
                if tenant_id:
                    query = query.where(LLMUsageModel.tenant_id == tenant_id)
                if service_name:
                    query = query.where(LLMUsageModel.service_name == service_name)
                if provider:
                    query = query.where(LLMUsageModel.provider == provider)

                # Order by date
                query = query.order_by(LLMUsageModel.date)

                result = await db.execute(query)
                usage_records = result.scalars().all()

                # Group by date
                daily_usage = {}
                for record in usage_records:
                    date_str = record.date.isoformat()
                    if date_str not in daily_usage:
                        daily_usage[date_str] = {
                            "date": date_str,
                            "prompt_tokens": 0,
                            "completion_tokens": 0,
                            "total_tokens": 0,
                            "cost": 0.0,
                            "request_count": 0,
                        }

                    daily_usage[date_str]["prompt_tokens"] += record.prompt_tokens
                    daily_usage[date_str][
                        "completion_tokens"
                    ] += record.completion_tokens
                    daily_usage[date_str]["total_tokens"] += record.total_tokens
                    daily_usage[date_str]["cost"] += record.cost
                    daily_usage[date_str]["request_count"] += record.request_count

                # Fill in missing dates with zeros
                result_list = []
                current_date = start_date
                while current_date <= end_date:
                    date_str = current_date.isoformat()
                    if date_str in daily_usage:
                        result_list.append(daily_usage[date_str])
                    else:
                        result_list.append(
                            {
                                "date": date_str,
                                "prompt_tokens": 0,
                                "completion_tokens": 0,
                                "total_tokens": 0,
                                "cost": 0.0,
                                "request_count": 0,
                            }
                        )
                    current_date += timedelta(days=1)

                return result_list

        except Exception as e:
            self.logger.error(f"Failed to get daily usage: {e}")
            raise

    async def get_top_models(
        self,
        limit: int = 10,
        start_date: datetime | None = None,
        end_date: datetime | None = None,
        tenant_id: str | None = None,
        service_name: str | None = None,
    ) -> list[dict[str, Any]]:
        """
        Get top models by usage.

        Args:
            limit: Maximum number of results
            start_date: Start date filter
            end_date: End date filter
            tenant_id: Tenant ID filter
            service_name: Service name filter

        Returns:
            List of top models with usage statistics
        """
        try:
            if not start_date:
                start_date = datetime.utcnow() - timedelta(days=30)
            if not end_date:
                end_date = datetime.utcnow()

            async with get_async_db_session() as db:
                query = select(
                    LLMUsageModel.provider,
                    LLMUsageModel.model,
                    func.sum(LLMUsageModel.total_tokens).label("total_tokens"),
                    func.sum(LLMUsageModel.cost).label("total_cost"),
                    func.sum(LLMUsageModel.request_count).label("total_requests"),
                ).where(
                    and_(
                        LLMUsageModel.date >= start_date.date(),
                        LLMUsageModel.date <= end_date.date(),
                    )
                )

                # Apply filters
                if tenant_id:
                    query = query.where(LLMUsageModel.tenant_id == tenant_id)
                if service_name:
                    query = query.where(LLMUsageModel.service_name == service_name)

                # Group by provider and model
                query = query.group_by(LLMUsageModel.provider, LLMUsageModel.model)

                # Order by total tokens descending
                query = query.order_by(desc("total_tokens"))

                # Limit results
                query = query.limit(limit)

                result = await db.execute(query)
                rows = result.fetchall()

                top_models = []
                for row in rows:
                    top_models.append(
                        {
                            "provider": row.provider,
                            "model": row.model,
                            "total_tokens": row.total_tokens,
                            "total_cost": float(row.total_cost),
                            "total_requests": row.total_requests,
                        }
                    )

                return top_models

        except Exception as e:
            self.logger.error(f"Failed to get top models: {e}")
            raise

    async def cleanup_old_usage_data(self, days_to_keep: int = 90) -> int:
        """
        Clean up old usage data.

        Args:
            days_to_keep: Number of days of data to keep

        Returns:
            Number of records deleted
        """
        try:
            cutoff_date = datetime.utcnow().date() - timedelta(days=days_to_keep)

            async with get_async_db_session() as db:
                from sqlalchemy import delete

                query = delete(LLMUsageModel).where(LLMUsageModel.date < cutoff_date)

                result = await db.execute(query)
                await db.commit()

                deleted_count = result.rowcount

                self.logger.info(
                    f"Cleaned up {deleted_count} old usage records",
                    extra={"cutoff_date": cutoff_date.isoformat()},
                )

                return deleted_count

        except Exception as e:
            self.logger.error(f"Failed to cleanup old usage data: {e}")
            raise


# Global service instance
_usage_service: UsageService | None = None


def get_usage_service() -> UsageService:
    """Get global usage service instance."""
    global _usage_service
    if _usage_service is None:
        _usage_service = UsageService()
    return _usage_service
