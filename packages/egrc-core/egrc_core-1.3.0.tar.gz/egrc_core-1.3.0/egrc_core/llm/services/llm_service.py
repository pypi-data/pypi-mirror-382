"""
Main LLM service for EGRC Platform.

This module provides the main LLM service that orchestrates LLM operations,
handles database integration, caching, and provides a unified interface
for all microservices.
"""

from datetime import datetime
from typing import Any
from uuid import UUID, uuid4

from ...cache import get_redis_client
from ...config.settings import LLMSettings, get_settings
from ...database import get_async_db_session
from ...logging.utils import get_logger
from ..models.database import LLMRequestModel, LLMResponseModel
from ..models.schemas import LLMRequestCreate, LLMResponse, LLMResponseCreate, LLMUsage
from ..providers import LLMProviderFactory
from ..providers.base import BaseLLMProvider, LLMProviderError


logger = get_logger(__name__)


class LLMService:
    """Main LLM service for handling AI operations."""

    def __init__(
        self,
        settings: LLMSettings | None = None,
        provider: BaseLLMProvider | None = None,
    ):
        """
        Initialize LLM service.

        Args:
            settings: LLM settings configuration
            provider: Pre-configured LLM provider
        """
        self.settings = settings or get_settings().llm
        self.provider = provider or self._create_provider()
        self.logger = get_logger(
            f"{self.__class__.__module__}.{self.__class__.__name__}"
        )

        # Initialize cache client
        self.cache_client = None
        if self.settings.enable_caching:
            try:
                self.cache_client = get_redis_client()
            except Exception as e:
                self.logger.warning(f"Failed to initialize cache client: {e}")

    def _create_provider(self) -> BaseLLMProvider:
        """Create LLM provider based on settings."""
        try:
            return LLMProviderFactory.create_provider(
                provider_name=self.settings.provider,
                settings=self.settings,
            )
        except Exception as e:
            self.logger.error(f"Failed to create LLM provider: {e}")
            raise

    async def chat_completion(
        self,
        messages: list[dict[str, str]],
        model: str | None = None,
        temperature: float = 0.7,
        max_tokens: int = 4000,
        top_p: float | None = None,
        frequency_penalty: float | None = None,
        presence_penalty: float | None = None,
        stop: list[str] | None = None,
        stream: bool = False,
        user: str | None = None,
        tenant_id: str | None = None,
        service_name: str | None = None,
        conversation_id: UUID | None = None,
        llm_metadata: dict[str, Any] | None = None,
        **kwargs: Any,
    ) -> LLMResponse:
        """
        Generate a chat completion with full database integration.

        Args:
            messages: List of chat messages
            model: Model to use (defaults to provider default)
            temperature: Sampling temperature
            max_tokens: Maximum tokens to generate
            top_p: Top-p sampling parameter
            frequency_penalty: Frequency penalty
            presence_penalty: Presence penalty
            stop: Stop sequences
            stream: Whether to stream the response
            user: User identifier
            tenant_id: Tenant ID
            service_name: Service name
            conversation_id: Conversation ID
            llm_metadata: Additional metadata
            **kwargs: Additional provider-specific parameters

        Returns:
            LLM response with database tracking
        """
        try:
            # Use default model if not specified
            if not model:
                model = self._get_default_model()

            # Create request record
            request_data = LLMRequestCreate(
                conversation_id=conversation_id,
                provider=self.settings.provider,
                model=model,
                messages=messages,
                temperature=temperature,
                max_tokens=max_tokens,
                top_p=top_p,
                frequency_penalty=frequency_penalty,
                presence_penalty=presence_penalty,
                stop=stop,
                stream=stream,
                user=user,
                llm_metadata=llm_metadata,
                tenant_id=tenant_id,
                service_name=service_name,
            )

            # Check cache first
            cache_key = None
            if self.settings.enable_caching and self.cache_client:
                cache_key = self._generate_cache_key(request_data)
                cached_response = await self._get_cached_response(cache_key)
                if cached_response:
                    self.logger.info("Returning cached LLM response")
                    return cached_response

            # Log request to database if enabled
            request_id = None
            if self.settings.enable_db_integration and self.settings.log_requests:
                request_id = await self._log_request(request_data)

            # Make LLM request
            self.logger.info(
                f"Making LLM request to {self.settings.provider}/{model}",
                extra={
                    "provider": self.settings.provider,
                    "model": model,
                    "messages_count": len(messages),
                    "tenant_id": tenant_id,
                    "service_name": service_name,
                },
            )

            provider_response = await self.provider.chat_completion(
                messages=messages,
                model=model,
                temperature=temperature,
                max_tokens=max_tokens,
                top_p=top_p,
                frequency_penalty=frequency_penalty,
                presence_penalty=presence_penalty,
                stop=stop,
                stream=stream,
                user=user,
                **kwargs,
            )

            # Create response record
            response_data = LLMResponseCreate(
                request_id=request_id or uuid4(),
                content=provider_response.content,
                finish_reason=provider_response.finish_reason,
                usage=(
                    LLMUsage(**provider_response.usage)
                    if provider_response.usage
                    else None
                ),
                llm_metadata={
                    **(llm_metadata or {}),
                    "provider_response_id": provider_response.id,
                    "provider_metadata": provider_response.metadata,
                },
            )

            # Log response to database if enabled
            if self.settings.enable_db_integration and self.settings.log_responses:
                await self._log_response(response_data)

            # Cache response if enabled
            if self.settings.enable_caching and self.cache_client and cache_key:
                await self._cache_response(cache_key, response_data)

            # Create final response
            llm_response = LLMResponse(
                id=response_data.request_id,
                request_id=response_data.request_id,
                content=response_data.content,
                finish_reason=response_data.finish_reason,
                usage=response_data.usage,
                llm_metadata=response_data.llm_metadata,
                created_at=datetime.utcnow(),
                updated_at=datetime.utcnow(),
            )

            self.logger.info(
                "LLM request completed successfully",
                extra={
                    "provider": self.settings.provider,
                    "model": model,
                    "content_length": len(provider_response.content),
                    "tokens_used": (
                        provider_response.usage.get("total_tokens", 0)
                        if provider_response.usage
                        else 0
                    ),
                    "tenant_id": tenant_id,
                    "service_name": service_name,
                },
            )

            return llm_response

        except LLMProviderError as e:
            self.logger.error(f"LLM provider error: {e}")
            # Log error to database if enabled
            if self.settings.enable_db_integration:
                await self._log_error(e, tenant_id, service_name, request_id)
            raise
        except Exception as e:
            self.logger.error(f"LLM service error: {e}")
            raise

    def _get_default_model(self) -> str:
        """Get default model for the current provider."""
        if self.settings.provider == "openai":
            return self.settings.openai_model
        elif self.settings.provider == "deepseek":
            return self.settings.deepseek_model
        elif self.settings.provider == "llama":
            return self.settings.llama_model
        elif self.settings.provider == "anthropic":
            return self.settings.anthropic_model
        else:
            return "gpt-4"  # Fallback

    def _generate_cache_key(self, request_data: LLMRequestCreate) -> str:
        """Generate cache key for request."""
        import hashlib
        import json

        cache_data = {
            "provider": request_data.provider,
            "model": request_data.model,
            "messages": request_data.messages,
            "temperature": request_data.temperature,
            "max_tokens": request_data.max_tokens,
            "top_p": request_data.top_p,
            "frequency_penalty": request_data.frequency_penalty,
            "presence_penalty": request_data.presence_penalty,
            "stop": request_data.stop,
            "user": request_data.user,
        }

        cache_str = json.dumps(cache_data, sort_keys=True)
        return f"llm_cache:{hashlib.md5(cache_str.encode()).hexdigest()}"

    async def _get_cached_response(self, cache_key: str) -> LLMResponse | None:
        """Get cached response if available."""
        if not self.cache_client:
            return None

        try:
            cached_data = await self.cache_client.get(cache_key)
            if cached_data:
                import json

                data = json.loads(cached_data)
                return LLMResponse(**data)
        except Exception as e:
            self.logger.warning(f"Failed to get cached response: {e}")

        return None

    async def _cache_response(
        self, cache_key: str, response_data: LLMResponseCreate
    ) -> None:
        """Cache response data."""
        if not self.cache_client:
            return

        try:
            import json

            cache_data = {
                "id": str(response_data.request_id),
                "request_id": str(response_data.request_id),
                "content": response_data.content,
                "finish_reason": response_data.finish_reason,
                "usage": response_data.usage.dict() if response_data.usage else None,
                "metadata": response_data.metadata,
                "created_at": datetime.utcnow().isoformat(),
                "updated_at": datetime.utcnow().isoformat(),
            }

            await self.cache_client.setex(
                cache_key,
                self.settings.cache_ttl,
                json.dumps(cache_data),
            )
        except Exception as e:
            self.logger.warning(f"Failed to cache response: {e}")

    async def _log_request(self, request_data: LLMRequestCreate) -> UUID:
        """Log request to database."""
        try:
            async with get_async_db_session() as db:
                db_request = LLMRequestModel(
                    conversation_id=request_data.conversation_id,
                    provider=request_data.provider,
                    model=request_data.model,
                    messages=request_data.messages,
                    temperature=request_data.temperature,
                    max_tokens=request_data.max_tokens,
                    top_p=request_data.top_p,
                    frequency_penalty=request_data.frequency_penalty,
                    presence_penalty=request_data.presence_penalty,
                    stop=request_data.stop,
                    stream=request_data.stream,
                    user=request_data.user,
                    metadata=request_data.metadata,
                    tenant_id=request_data.tenant_id,
                    service_name=request_data.service_name,
                )

                db.add(db_request)
                await db.commit()
                await db.refresh(db_request)

                return db_request.id
        except Exception as e:
            self.logger.error(f"Failed to log request to database: {e}")
            return uuid4()  # Return random UUID if logging fails

    async def _log_response(self, response_data: LLMResponseCreate) -> None:
        """Log response to database."""
        try:
            async with get_async_db_session() as db:
                db_response = LLMResponseModel(
                    request_id=response_data.request_id,
                    content=response_data.content,
                    finish_reason=response_data.finish_reason,
                    prompt_tokens=(
                        response_data.usage.prompt_tokens
                        if response_data.usage
                        else None
                    ),
                    completion_tokens=(
                        response_data.usage.completion_tokens
                        if response_data.usage
                        else None
                    ),
                    total_tokens=(
                        response_data.usage.total_tokens
                        if response_data.usage
                        else None
                    ),
                    cost=response_data.usage.cost if response_data.usage else None,
                    llm_metadata=response_data.llm_metadata,
                )

                db.add(db_response)
                await db.commit()
        except Exception as e:
            self.logger.error(f"Failed to log response to database: {e}")

    async def _log_error(
        self,
        error: LLMProviderError,
        tenant_id: str | None = None,
        service_name: str | None = None,
        request_id: UUID | None = None,
    ) -> None:
        """Log error to database."""
        try:
            async with get_async_db_session() as db:
                from ..models.database import LLMErrorModel

                db_error = LLMErrorModel(
                    provider=error.provider,
                    model="unknown",  # We don't have model info in error
                    error_type=type(error).__name__,
                    error_message=str(error),
                    error_code=error.error_code,
                    error_details=error.details,
                    tenant_id=tenant_id,
                    service_name=service_name,
                    request_id=request_id,
                )

                db.add(db_error)
                await db.commit()
        except Exception as e:
            self.logger.error(f"Failed to log error to database: {e}")

    async def list_models(self) -> list[dict[str, Any]]:
        """List available models for the current provider."""
        try:
            return await self.provider.list_models()
        except Exception as e:
            self.logger.error(f"Failed to list models: {e}")
            raise

    async def get_model_info(self, model: str) -> dict[str, Any]:
        """Get information about a specific model."""
        try:
            return await self.provider.get_model_info(model)
        except Exception as e:
            self.logger.error(f"Failed to get model info for {model}: {e}")
            raise

    async def health_check(self) -> dict[str, Any]:
        """Perform health check on the LLM service."""
        try:
            provider_health = await self.provider.health_check()

            return {
                "status": "healthy",
                "service": "llm",
                "provider": provider_health,
                "settings": {
                    "provider": self.settings.provider,
                    "caching_enabled": self.settings.enable_caching,
                    "db_integration_enabled": self.settings.enable_db_integration,
                },
                "timestamp": datetime.utcnow().isoformat(),
            }
        except Exception as e:
            return {
                "status": "unhealthy",
                "service": "llm",
                "error": str(e),
                "timestamp": datetime.utcnow().isoformat(),
            }


# Global service instance
_llm_service: LLMService | None = None


def get_llm_service() -> LLMService:
    """Get global LLM service instance."""
    global _llm_service
    if _llm_service is None:
        _llm_service = LLMService()
    return _llm_service
