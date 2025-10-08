"""
Anthropic provider implementation.

This module provides the Anthropic provider implementation for the LLM service,
supporting Claude models via Anthropic API.
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
    import anthropic

    ANTHROPIC_AVAILABLE = True
except ImportError:
    ANTHROPIC_AVAILABLE = False


class AnthropicProvider(BaseLLMProvider):
    """Anthropic provider implementation."""

    def __init__(
        self,
        api_key: str | None = None,
        base_url: str = "https://api.anthropic.com",
        timeout: int = 30,
        max_retries: int = 3,
        retry_delay: float = 1.0,
    ):
        """
        Initialize Anthropic provider.

        Args:
            api_key: Anthropic API key
            base_url: Anthropic API base URL
            timeout: Request timeout in seconds
            max_retries: Maximum number of retries
            retry_delay: Delay between retries in seconds
        """
        super().__init__(api_key, base_url, timeout, max_retries, retry_delay)

        if not ANTHROPIC_AVAILABLE:
            raise ImportError(
                "Anthropic package is not installed. Install with: "
                "pip install anthropic"
            )

        if not self.api_key:
            raise ValueError("Anthropic API key is required")

        self.client = anthropic.AsyncAnthropic(
            api_key=self.api_key,
            base_url=self.base_url,
            timeout=self.timeout,
            max_retries=self.max_retries,
        )

    @property
    def provider_name(self) -> str:
        """Get the provider name."""
        return "anthropic"

    @property
    def supported_models(self) -> list[str]:
        """Get list of supported models."""
        return [
            "claude-3-opus-20240229",
            "claude-3-sonnet-20240229",
            "claude-3-haiku-20240307",
            "claude-3-5-sonnet-20241022",
            "claude-3-5-haiku-20241022",
        ]

    @property
    def capabilities(self) -> list[str]:
        """Get list of provider capabilities."""
        return [
            "chat_completion",
            "streaming",
            "function_calling",
            "vision",
            "long_context",
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
        Generate a chat completion using Anthropic.

        Args:
            messages: List of chat messages
            model: Model to use
            temperature: Sampling temperature
            max_tokens: Maximum tokens to generate
            top_p: Top-p sampling parameter (not supported by Anthropic)
            frequency_penalty: Frequency penalty (not supported by Anthropic)
            presence_penalty: Presence penalty (not supported by Anthropic)
            stop: Stop sequences
            stream: Whether to stream the response
            user: User identifier
            **kwargs: Additional Anthropic-specific parameters

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

            # Convert messages to Anthropic format
            system_message = None
            anthropic_messages = []

            for message in messages:
                if message["role"] == "system":
                    system_message = message["content"]
                else:
                    anthropic_messages.append(
                        {"role": message["role"], "content": message["content"]}
                    )

            # Prepare request parameters
            request_params = {
                "model": model,
                "messages": anthropic_messages,
                "temperature": temperature,
                "max_tokens": max_tokens,
                "stream": stream,
            }

            # Add system message if present
            if system_message:
                request_params["system"] = system_message

            # Add stop sequences if present
            if stop:
                request_params["stop_sequences"] = stop

            # Add user if present
            if user:
                request_params["metadata"] = {"user_id": user}

            # Add any additional parameters
            request_params.update(kwargs)

            self.logger.info(
                f"Making Anthropic request to model {model}",
                extra={
                    "provider": self.provider_name,
                    "model": model,
                    "messages_count": len(messages),
                    "temperature": temperature,
                    "max_tokens": max_tokens,
                },
            )

            # Make the request
            response = await self.client.messages.create(**request_params)

            # Process response
            if stream:
                # Handle streaming response
                content_parts = []
                finish_reason = None
                usage = None

                async for chunk in response:
                    if chunk.type == "content_block_delta":
                        content_parts.append(chunk.delta.text)
                    elif chunk.type == "message_stop":
                        finish_reason = "end_turn"
                    elif chunk.type == "message_start":
                        usage = {
                            "prompt_tokens": chunk.message.usage.input_tokens,
                            "completion_tokens": chunk.message.usage.output_tokens,
                            "total_tokens": chunk.message.usage.input_tokens
                            + chunk.message.usage.output_tokens,
                        }

                content = "".join(content_parts)
            else:
                # Handle non-streaming response
                content = response.content[0].text if response.content else ""
                finish_reason = response.stop_reason
                usage = {
                    "prompt_tokens": response.usage.input_tokens,
                    "completion_tokens": response.usage.output_tokens,
                    "total_tokens": response.usage.input_tokens
                    + response.usage.output_tokens,
                }

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
                    "anthropic_response_id": response.id,
                    "anthropic_type": response.type,
                    "anthropic_role": response.role,
                    "anthropic_stop_reason": response.stop_reason,
                },
            )

            self.logger.info(
                "Anthropic request completed successfully",
                extra={
                    "provider": self.provider_name,
                    "model": model,
                    "content_length": len(content),
                    "tokens_used": usage["total_tokens"] if usage else 0,
                },
            )

            return llm_response

        except Exception as e:
            error_msg = f"Anthropic request failed: {str(e)}"
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
        List available Anthropic models.

        Returns:
            List of available models with their information
        """
        # Anthropic doesn't have a models endpoint, so we return the supported models
        models = []
        for model_name in self.supported_models:
            model_info = {
                "id": model_name,
                "object": "model",
                "created": None,
                "owned_by": "anthropic",
                "permission": [],
                "root": model_name,
                "parent": None,
            }
            models.append(model_info)

        return models

    async def get_model_info(self, model: str) -> dict[str, Any]:
        """
        Get information about a specific Anthropic model.

        Args:
            model: Model name

        Returns:
            Model information
        """
        if model not in self.supported_models:
            raise LLMProviderError(
                message=f"Model {model} is not supported by Anthropic",
                provider=self.provider_name,
                error_code="MODEL_NOT_FOUND",
                details={"model": model},
            )

        return {
            "id": model,
            "object": "model",
            "created": None,
            "owned_by": "anthropic",
            "permission": [],
            "root": model,
            "parent": None,
        }
