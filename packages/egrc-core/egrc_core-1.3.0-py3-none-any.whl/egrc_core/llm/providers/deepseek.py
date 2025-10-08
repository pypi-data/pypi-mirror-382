"""
DeepSeek provider implementation.

This module provides the DeepSeek provider implementation for the LLM service,
supporting DeepSeek models with OpenAI-compatible API.
"""

import asyncio
from typing import Any

import httpx

from .base import (
    BaseLLMProvider,
    LLMProviderError,
    LLMProviderRequest,
    LLMProviderResponse,
)


class DeepSeekProvider(BaseLLMProvider):
    """DeepSeek provider implementation."""

    def __init__(
        self,
        api_key: str | None = None,
        base_url: str = "https://api.deepseek.com/v1",
        timeout: int = 30,
        max_retries: int = 3,
        retry_delay: float = 1.0,
    ):
        """
        Initialize DeepSeek provider.

        Args:
            api_key: DeepSeek API key
            base_url: DeepSeek API base URL
            timeout: Request timeout in seconds
            max_retries: Maximum number of retries
            retry_delay: Delay between retries in seconds
        """
        super().__init__(api_key, base_url, timeout, max_retries, retry_delay)

        if not self.api_key:
            raise ValueError("DeepSeek API key is required")

        self.headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }

    @property
    def provider_name(self) -> str:
        """Get the provider name."""
        return "deepseek"

    @property
    def supported_models(self) -> list[str]:
        """Get list of supported models."""
        return [
            "deepseek-chat",
            "deepseek-coder",
            "deepseek-math",
            "deepseek-reasoner",
        ]

    @property
    def capabilities(self) -> list[str]:
        """Get list of provider capabilities."""
        return [
            "chat_completion",
            "streaming",
            "function_calling",
            "code_generation",
            "mathematical_reasoning",
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
        Generate a chat completion using DeepSeek.

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
            **kwargs: Additional DeepSeek-specific parameters

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

            # Prepare request payload
            payload = {
                "model": model,
                "messages": messages,
                "temperature": temperature,
                "max_tokens": max_tokens,
                "stream": stream,
            }

            # Add optional parameters
            if top_p is not None:
                payload["top_p"] = top_p
            if frequency_penalty is not None:
                payload["frequency_penalty"] = frequency_penalty
            if presence_penalty is not None:
                payload["presence_penalty"] = presence_penalty
            if stop is not None:
                payload["stop"] = stop
            if user is not None:
                payload["user"] = user

            # Add any additional parameters
            payload.update(kwargs)

            self.logger.info(
                f"Making DeepSeek request to model {model}",
                extra={
                    "provider": self.provider_name,
                    "model": model,
                    "messages_count": len(messages),
                    "temperature": temperature,
                    "max_tokens": max_tokens,
                },
            )

            # Make the request
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.post(
                    f"{self.base_url}/chat/completions",
                    headers=self.headers,
                    json=payload,
                )

                response.raise_for_status()
                response_data = response.json()

            # Process response
            if stream:
                # Handle streaming response (simplified for now)
                content = ""
                finish_reason = None
                usage = None

                # For streaming, we'd need to handle the SSE stream
                # This is a simplified implementation
                if "choices" in response_data and response_data["choices"]:
                    choice = response_data["choices"][0]
                    content = choice.get("message", {}).get("content", "")
                    finish_reason = choice.get("finish_reason")

                if "usage" in response_data:
                    usage = {
                        "prompt_tokens": response_data["usage"].get("prompt_tokens", 0),
                        "completion_tokens": response_data["usage"].get(
                            "completion_tokens", 0
                        ),
                        "total_tokens": response_data["usage"].get("total_tokens", 0),
                    }
            else:
                # Handle non-streaming response
                choice = response_data["choices"][0]
                content = choice["message"]["content"]
                finish_reason = choice.get("finish_reason")
                usage = (
                    {
                        "prompt_tokens": response_data["usage"]["prompt_tokens"],
                        "completion_tokens": response_data["usage"][
                            "completion_tokens"
                        ],
                        "total_tokens": response_data["usage"]["total_tokens"],
                    }
                    if "usage" in response_data
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
                    "deepseek_response_id": response_data.get("id"),
                    "deepseek_created": response_data.get("created"),
                },
            )

            self.logger.info(
                "DeepSeek request completed successfully",
                extra={
                    "provider": self.provider_name,
                    "model": model,
                    "content_length": len(content),
                    "tokens_used": usage["total_tokens"] if usage else 0,
                },
            )

            return llm_response

        except httpx.HTTPStatusError as e:
            error_msg = (
                f"DeepSeek HTTP error: {e.response.status_code} - {e.response.text}"
            )
            self.logger.error(
                error_msg,
                extra={
                    "provider": self.provider_name,
                    "status_code": e.response.status_code,
                },
            )
            raise LLMProviderError(
                message=error_msg,
                provider=self.provider_name,
                error_code=str(e.response.status_code),
                details={"model": model, "status_code": e.response.status_code},
            )
        except Exception as e:
            error_msg = f"DeepSeek request failed: {str(e)}"
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
        List available DeepSeek models.

        Returns:
            List of available models with their information
        """
        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.get(
                    f"{self.base_url}/models",
                    headers=self.headers,
                )

                response.raise_for_status()
                response_data = response.json()

            models = []
            for model in response_data.get("data", []):
                model_info = {
                    "id": model.get("id"),
                    "object": model.get("object"),
                    "created": model.get("created"),
                    "owned_by": model.get("owned_by"),
                    "permission": model.get("permission"),
                    "root": model.get("root"),
                    "parent": model.get("parent"),
                }
                models.append(model_info)

            return models

        except Exception as e:
            error_msg = f"Failed to list DeepSeek models: {str(e)}"
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
        Get information about a specific DeepSeek model.

        Args:
            model: Model name

        Returns:
            Model information
        """
        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.get(
                    f"{self.base_url}/models/{model}",
                    headers=self.headers,
                )

                response.raise_for_status()
                response_data = response.json()

            return {
                "id": response_data.get("id"),
                "object": response_data.get("object"),
                "created": response_data.get("created"),
                "owned_by": response_data.get("owned_by"),
                "permission": response_data.get("permission"),
                "root": response_data.get("root"),
                "parent": response_data.get("parent"),
            }

        except Exception as e:
            error_msg = f"Failed to get DeepSeek model info for {model}: {str(e)}"
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
