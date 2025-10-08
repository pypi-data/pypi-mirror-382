"""
OpenAI provider implementation.

This module provides the OpenAI provider implementation for the LLM service,
supporting GPT models and OpenAI-compatible APIs.
"""

import asyncio
from typing import Any

from .base import (
    BaseLLMProvider,
    LLMProviderError,
    LLMProviderRequest,
    LLMProviderResponse,
)


try:
    from openai import AsyncOpenAI

    OPENAI_AVAILABLE = True
except ImportError:
    OPENAI_AVAILABLE = False


class OpenAIProvider(BaseLLMProvider):
    """OpenAI provider implementation."""

    def __init__(
        self,
        api_key: str | None = None,
        base_url: str = "https://api.openai.com/v1",
        timeout: int = 30,
        max_retries: int = 3,
        retry_delay: float = 1.0,
    ):
        """
        Initialize OpenAI provider.

        Args:
            api_key: OpenAI API key
            base_url: OpenAI API base URL
            timeout: Request timeout in seconds
            max_retries: Maximum number of retries
            retry_delay: Delay between retries in seconds
        """
        super().__init__(api_key, base_url, timeout, max_retries, retry_delay)

        if not OPENAI_AVAILABLE:
            raise ImportError(
                "OpenAI package is not installed. Install with: pip install openai"
            )

        if not self.api_key:
            raise ValueError("OpenAI API key is required")

        self.client = AsyncOpenAI(
            api_key=self.api_key,
            base_url=self.base_url,
            timeout=self.timeout,
            max_retries=self.max_retries,
        )

    @property
    def provider_name(self) -> str:
        """Get the provider name."""
        return "openai"

    @property
    def supported_models(self) -> list[str]:
        """Get list of supported models."""
        return [
            "gpt-5",
        ]

    @property
    def capabilities(self) -> list[str]:
        """Get list of provider capabilities."""
        return [
            "chat_completion",
            "streaming",
            "function_calling",
            "json_mode",
            "vision",
            "embeddings",
        ]

    async def chat_completion(
        self,
        messages: list[dict[str, str]],
        model: str,
        temperature: float = 0.7,
        max_tokens: int = 4000,
        top_p: float | None = None,
        frequency_penalty: float | None = None,
        presence_penalty: float | None = None,
        stop: list[str] | None = None,
        stream: bool = False,
        user: str | None = None,
        **kwargs: Any,
    ) -> LLMProviderResponse:
        """
        Generate a chat completion using OpenAI.

        Args:
            messages: List of chat messages
            model: Model to use
            temperature: Sampling temperature
            max_tokens: Maximum tokens to generate
            top_p: Top-p sampling parameter
            frequency_penalty: Frequency penalty
            presence_penalty: Presence penalty
            stop: Stop sequences
            stream: Whether to stream the response
            user: User identifier
            **kwargs: Additional OpenAI-specific parameters

        Returns:
            LLM provider response

        Raises:
            LLMProviderError: If the request fails
        """
        try:
            # Validate request
            request = LLMProviderRequest(
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
            )

            await self.validate_request(request)

            # Check rate limits
            estimated_tokens = (
                sum(len(msg.get("content", "").split()) for msg in messages)
                + max_tokens
            )
            await self.wait_for_rate_limit(estimated_tokens)

            # Prepare request parameters
            request_params = {
                "model": model,
                "messages": messages,
                "temperature": temperature,
                "max_tokens": max_tokens,
                "stream": stream,
            }

            # Add optional parameters
            if top_p is not None:
                request_params["top_p"] = top_p
            if frequency_penalty is not None:
                request_params["frequency_penalty"] = frequency_penalty
            if presence_penalty is not None:
                request_params["presence_penalty"] = presence_penalty
            if stop is not None:
                request_params["stop"] = stop
            if user is not None:
                request_params["user"] = user

            # Add any additional parameters
            request_params.update(kwargs)

            self.logger.info(
                f"Making OpenAI request to model {model}",
                extra={
                    "provider": self.provider_name,
                    "model": model,
                    "messages_count": len(messages),
                    "temperature": temperature,
                    "max_tokens": max_tokens,
                },
            )

            # Make the request
            response = await self.client.chat.completions.create(**request_params)

            # Process response
            if stream:
                # Handle streaming response
                content_parts = []
                finish_reason = None
                usage = None

                async for chunk in response:
                    if chunk.choices and chunk.choices[0].delta.content:
                        content_parts.append(chunk.choices[0].delta.content)
                    if chunk.choices and chunk.choices[0].finish_reason:
                        finish_reason = chunk.choices[0].finish_reason
                    if chunk.usage:
                        usage = {
                            "prompt_tokens": chunk.usage.prompt_tokens,
                            "completion_tokens": chunk.usage.completion_tokens,
                            "total_tokens": chunk.usage.total_tokens,
                        }

                content = "".join(content_parts)
            else:
                # Handle non-streaming response
                choice = response.choices[0]
                content = choice.message.content or ""
                finish_reason = choice.finish_reason
                usage = (
                    {
                        "prompt_tokens": response.usage.prompt_tokens,
                        "completion_tokens": response.usage.completion_tokens,
                        "total_tokens": response.usage.total_tokens,
                    }
                    if response.usage
                    else None
                )

            # Update rate limiting tracking
            if usage:
                self._token_usage.append(usage["total_tokens"])
            self._request_times.append(asyncio.get_event_loop().time())

            # Create response
            llm_response = LLMProviderResponse(
                content=content,
                finish_reason=finish_reason,
                usage=usage,
                model=model,
                provider=self.provider_name,
                metadata={
                    "openai_response_id": getattr(response, "id", None),
                    "openai_created": getattr(response, "created", None),
                },
            )

            self.logger.info(
                "OpenAI request completed successfully",
                extra={
                    "provider": self.provider_name,
                    "model": model,
                    "content_length": len(content),
                    "tokens_used": usage["total_tokens"] if usage else 0,
                },
            )

            return llm_response

        except Exception as e:
            error_msg = f"OpenAI request failed: {str(e)}"
            self.logger.error(
                error_msg, extra={"provider": self.provider_name, "error": str(e)}
            )
            raise LLMProviderError(
                message=error_msg,
                provider=self.provider_name,
                error_code=getattr(e, "code", None),
                details={"model": model, "error_type": type(e).__name__},
            )

    async def list_models(self) -> list[dict[str, Any]]:
        """
        List available OpenAI models.

        Returns:
            List of available models with their information
        """
        try:
            models = await self.client.models.list()

            model_list = []
            for model in models.data:
                model_info = {
                    "id": model.id,
                    "object": model.object,
                    "created": model.created,
                    "owned_by": model.owned_by,
                    "permission": model.permission,
                    "root": model.root,
                    "parent": model.parent,
                }
                model_list.append(model_info)

            return model_list

        except Exception as e:
            error_msg = f"Failed to list OpenAI models: {str(e)}"
            self.logger.error(
                error_msg, extra={"provider": self.provider_name, "error": str(e)}
            )
            raise LLMProviderError(
                message=error_msg,
                provider=self.provider_name,
                error_code=getattr(e, "code", None),
            )

    async def get_model_info(self, model: str) -> dict[str, Any]:
        """
        Get information about a specific OpenAI model.

        Args:
            model: Model name

        Returns:
            Model information
        """
        try:
            model_info = await self.client.models.retrieve(model)

            return {
                "id": model_info.id,
                "object": model_info.object,
                "created": model_info.created,
                "owned_by": model_info.owned_by,
                "permission": model_info.permission,
                "root": model_info.root,
                "parent": model_info.parent,
            }

        except Exception as e:
            error_msg = f"Failed to get OpenAI model info for {model}: {str(e)}"
            self.logger.error(
                error_msg,
                extra={"provider": self.provider_name, "model": model, "error": str(e)},
            )
            raise LLMProviderError(
                message=error_msg,
                provider=self.provider_name,
                error_code=getattr(e, "code", None),
                details={"model": model},
            )
