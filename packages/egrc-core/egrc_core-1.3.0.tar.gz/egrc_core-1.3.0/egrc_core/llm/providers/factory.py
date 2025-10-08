"""
LLM provider factory.

This module provides a factory for creating LLM providers based on configuration,
ensuring easy switching between different AI providers.
"""

from typing import Any

from ...config.settings import LLMSettings
from ...exceptions.exceptions import ConfigurationError
from ...logging.utils import get_logger
from .anthropic import AnthropicProvider
from .base import BaseLLMProvider
from .deepseek import DeepSeekProvider
from .llama import LlamaProvider
from .openai import OpenAIProvider


logger = get_logger(__name__)


class LLMProviderFactory:
    """Factory for creating LLM providers."""

    _providers: dict[str, type] = {
        "openai": OpenAIProvider,
        "deepseek": DeepSeekProvider,
        "llama": LlamaProvider,
        "anthropic": AnthropicProvider,
    }

    @classmethod
    def create_provider(
        cls,
        provider_name: str,
        settings: LLMSettings | None = None,
        **kwargs: Any,
    ) -> BaseLLMProvider:
        """
        Create an LLM provider instance.

        Args:
            provider_name: Name of the provider to create
            settings: LLM settings configuration
            **kwargs: Additional provider-specific parameters

        Returns:
            LLM provider instance

        Raises:
            ConfigurationError: If provider is not supported or configuration is invalid
        """
        if provider_name not in cls._providers:
            raise ConfigurationError(
                f"Unsupported LLM provider: {provider_name}. "
                f"Supported providers: {list(cls._providers.keys())}"
            )

        provider_class = cls._providers[provider_name]

        # Get provider-specific configuration
        provider_config = cls._get_provider_config(provider_name, settings)

        # Merge with any additional kwargs
        provider_config.update(kwargs)

        try:
            provider = provider_class(**provider_config)
            logger.info(f"Created {provider_name} provider successfully")
            return provider
        except Exception as e:
            logger.error(f"Failed to create {provider_name} provider: {str(e)}")
            raise ConfigurationError(
                f"Failed to create {provider_name} provider: {str(e)}"
            )

    @classmethod
    def _get_provider_config(
        cls, provider_name: str, settings: LLMSettings | None
    ) -> dict[str, Any]:
        """
        Get provider-specific configuration from settings.

        Args:
            provider_name: Name of the provider
            settings: LLM settings configuration

        Returns:
            Provider configuration dictionary
        """
        if not settings:
            return {}

        config = {
            "timeout": settings.timeout,
            "max_retries": settings.max_retries,
            "retry_delay": settings.retry_delay,
        }

        if provider_name == "openai":
            config.update(
                {
                    "api_key": settings.openai_api_key,
                    "base_url": settings.openai_base_url,
                }
            )
        elif provider_name == "deepseek":
            config.update(
                {
                    "api_key": settings.deepseek_api_key,
                    "base_url": settings.deepseek_base_url,
                }
            )
        elif provider_name == "llama":
            config.update(
                {
                    "api_key": None,  # Llama doesn't require API key
                    "base_url": settings.llama_base_url,
                }
            )
        elif provider_name == "anthropic":
            config.update(
                {
                    "api_key": settings.anthropic_api_key,
                    "base_url": "https://api.anthropic.com",
                    # Anthropic doesn't support custom base URLs
                }
            )

        return config

    @classmethod
    def get_supported_providers(cls) -> list[str]:
        """
        Get list of supported providers.

        Returns:
            List of supported provider names
        """
        return list(cls._providers.keys())

    @classmethod
    def register_provider(cls, name: str, provider_class: type) -> None:
        """
        Register a new provider.

        Args:
            name: Provider name
            provider_class: Provider class
        """
        if not issubclass(provider_class, BaseLLMProvider):
            raise ValueError("Provider class must inherit from BaseLLMProvider")

        cls._providers[name] = provider_class
        logger.info(f"Registered new LLM provider: {name}")

    @classmethod
    def unregister_provider(cls, name: str) -> None:
        """
        Unregister a provider.

        Args:
            name: Provider name
        """
        if name in cls._providers:
            del cls._providers[name]
            logger.info(f"Unregistered LLM provider: {name}")

    @classmethod
    def validate_provider_config(
        cls, provider_name: str, settings: LLMSettings
    ) -> bool:
        """
        Validate provider configuration.

        Args:
            provider_name: Name of the provider
            settings: LLM settings configuration

        Returns:
            True if configuration is valid

        Raises:
            ConfigurationError: If configuration is invalid
        """
        if provider_name not in cls._providers:
            raise ConfigurationError(f"Unsupported provider: {provider_name}")

        # Check required configuration for each provider
        if provider_name == "openai":
            if not settings.openai_api_key:
                raise ConfigurationError("OpenAI API key is required")
        elif provider_name == "deepseek":
            if not settings.deepseek_api_key:
                raise ConfigurationError("DeepSeek API key is required")
        elif provider_name == "anthropic":
            if not settings.anthropic_api_key:
                raise ConfigurationError("Anthropic API key is required")
        # Llama doesn't require API key

        return True


def get_llm_provider(
    provider_name: str,
    settings: LLMSettings | None = None,
    **kwargs: Any,
) -> BaseLLMProvider:
    """
    Convenience function to get an LLM provider.

    Args:
        provider_name: Name of the provider to create
        settings: LLM settings configuration
        **kwargs: Additional provider-specific parameters

    Returns:
        LLM provider instance
    """
    return LLMProviderFactory.create_provider(provider_name, settings, **kwargs)
