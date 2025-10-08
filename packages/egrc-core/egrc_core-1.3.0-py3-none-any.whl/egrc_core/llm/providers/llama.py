"""
Llama provider implementation.

This module provides the Llama provider implementation for the LLM service,
supporting local Llama models via Ollama or similar APIs.
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


class LlamaProvider(BaseLLMProvider):
    """Llama provider implementation for local models."""

    def __init__(
        self,
        api_key: str | None = None,
        base_url: str = "http://localhost:11434",
        timeout: int = 30,
        max_retries: int = 3,
        retry_delay: float = 1.0,
    ):
        """
        Initialize Llama provider.

        Args:
            api_key: API key (not required for local Llama)
            base_url: Llama API base URL (default: Ollama)
            timeout: Request timeout in seconds
            max_retries: Maximum number of retries
            retry_delay: Delay between retries in seconds
        """
        super().__init__(api_key, base_url, timeout, max_retries, retry_delay)

        self.headers = {
            "Content-Type": "application/json",
        }

        # Add API key if provided
        if self.api_key:
            self.headers["Authorization"] = f"Bearer {self.api_key}"

    @property
    def provider_name(self) -> str:
        """Get the provider name."""
        return "llama"

    @property
    def supported_models(self) -> list[str]:
        """Get list of supported models."""
        return [
            "llama3",
            "llama3:8b",
            "llama3:70b",
            "llama2",
            "llama2:7b",
            "llama2:13b",
            "llama2:70b",
            "codellama",
            "codellama:7b",
            "codellama:13b",
            "codellama:34b",
            "mistral",
            "mistral:7b",
            "mixtral",
            "mixtral:8x7b",
            "phi",
            "phi:3b",
            "gemma",
            "gemma:2b",
            "gemma:7b",
        ]

    @property
    def capabilities(self) -> list[str]:
        """Get list of provider capabilities."""
        return [
            "chat_completion",
            "streaming",
            "local_inference",
            "code_generation",
            "text_generation",
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
        Generate a chat completion using Llama.

        Args:
            messages: List of chat messages
            model: Model to use
            temperature: Sampling temperature
            max_tokens: Maximum tokens to generate
            top_p: Top-p sampling parameter
            frequency_penalty: Frequency penalty (not supported by Llama)
            presence_penalty: Presence penalty (not supported by Llama)
            stop: Stop sequences
            stream: Whether to stream the response
            user: User identifier
            **kwargs: Additional Llama-specific parameters

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

            # Convert messages to Llama format
            llama_messages = []
            for message in messages:
                llama_messages.append(
                    {"role": message["role"], "content": message["content"]}
                )

            # Prepare request payload for Ollama API
            payload = {
                "model": model,
                "messages": llama_messages,
                "stream": stream,
                "options": {
                    "temperature": temperature,
                    "num_predict": max_tokens,
                },
            }

            # Add optional parameters
            if top_p is not None:
                payload["options"]["top_p"] = top_p
            if stop is not None:
                payload["options"]["stop"] = stop

            # Add any additional parameters
            if kwargs:
                payload["options"].update(kwargs)

            self.logger.info(
                f"Making Llama request to model {model}",
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
                    f"{self.base_url}/api/chat",
                    headers=self.headers,
                    json=payload,
                )

                response.raise_for_status()
                response_data = response.json()

            # Process response
            if stream:
                # Handle streaming response
                content_parts = []
                finish_reason = None
                usage = None

                # For streaming, we'd need to handle the SSE stream
                # This is a simplified implementation
                if "message" in response_data:
                    content_parts.append(response_data["message"].get("content", ""))
                    finish_reason = response_data.get("done", False) and "stop" or None

                content = "".join(content_parts)
            else:
                # Handle non-streaming response
                content = response_data.get("message", {}).get("content", "")
                finish_reason = "stop" if response_data.get("done", False) else None

                # Estimate usage (Llama doesn't provide exact token counts)
                estimated_prompt_tokens = sum(
                    len(msg.get("content", "").split()) for msg in messages
                )
                estimated_completion_tokens = len(content.split())
                usage = {
                    "prompt_tokens": estimated_prompt_tokens,
                    "completion_tokens": estimated_completion_tokens,
                    "total_tokens": estimated_prompt_tokens
                    + estimated_completion_tokens,
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
                    "llama_done": response_data.get("done"),
                    "llama_total_duration": response_data.get("total_duration"),
                    "llama_load_duration": response_data.get("load_duration"),
                    "llama_prompt_eval_duration": response_data.get(
                        "prompt_eval_duration"
                    ),
                    "llama_eval_duration": response_data.get("eval_duration"),
                },
            )

            self.logger.info(
                "Llama request completed successfully",
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
                f"Llama HTTP error: {e.response.status_code} - {e.response.text}"
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
            error_msg = f"Llama request failed: {str(e)}"
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
        List available Llama models.

        Returns:
            List of available models with their information
        """
        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.get(
                    f"{self.base_url}/api/tags",
                    headers=self.headers,
                )

                response.raise_for_status()
                response_data = response.json()

            models = []
            for model in response_data.get("models", []):
                model_info = {
                    "id": model.get("name"),
                    "object": "model",
                    "created": model.get("modified_at"),
                    "owned_by": "llama",
                    "permission": [],
                    "root": model.get("name"),
                    "parent": None,
                    "size": model.get("size"),
                    "digest": model.get("digest"),
                }
                models.append(model_info)

            return models

        except Exception as e:
            error_msg = f"Failed to list Llama models: {str(e)}"
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
        Get information about a specific Llama model.

        Args:
            model: Model name

        Returns:
            Model information
        """
        try:
            # For Llama, we'll get model info from the list
            models = await self.list_models()

            for model_info in models:
                if model_info["id"] == model:
                    return model_info

            # If model not found, return basic info
            return {
                "id": model,
                "object": "model",
                "created": None,
                "owned_by": "llama",
                "permission": [],
                "root": model,
                "parent": None,
            }

        except Exception as e:
            error_msg = f"Failed to get Llama model info for {model}: {str(e)}"
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
