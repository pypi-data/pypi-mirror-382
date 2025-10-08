"""
LLM module for EGRC Platform.

This module provides comprehensive LLM integration for all EGRC microservices,
supporting multiple providers (OpenAI, DeepSeek, Llama, Anthropic) with unified
configuration, database integration, and conversation management.
"""

from .models import (
    LLMConversation,
    LLMConversationCreate,
    LLMConversationUpdate,
    LLMError,
    LLMModel,
    LLMProvider,
    LLMRequest,
    LLMRequestCreate,
    LLMRequestUpdate,
    LLMResponse,
    LLMResponseCreate,
    LLMResponseUpdate,
    LLMUsage,
)
from .providers import (
    AnthropicProvider,
    BaseLLMProvider,
    DeepSeekProvider,
    LlamaProvider,
    LLMProviderError,
    LLMProviderFactory,
    LLMProviderResponse,
    OpenAIProvider,
    get_llm_provider,
)
from .services import (
    ConversationService,
    LLMService,
    UsageService,
    get_conversation_service,
    get_llm_service,
    get_usage_service,
)
from .utils import (
    PromptTemplate,
    clean_text,
    count_tokens,
    create_conversation_prompt,
    create_message,
    estimate_cost,
    extract_keywords,
    format_llm_response,
    get_system_prompt,
    get_user_prompt,
    parse_llm_response,
    summarize_text,
    truncate_text,
    validate_messages,
)


__all__ = [
    # Models and Schemas
    "LLMRequest",
    "LLMResponse",
    "LLMConversation",
    "LLMProvider",
    "LLMModel",
    "LLMUsage",
    "LLMError",
    "LLMRequestCreate",
    "LLMResponseCreate",
    "LLMConversationCreate",
    "LLMRequestUpdate",
    "LLMResponseUpdate",
    "LLMConversationUpdate",
    # Providers
    "BaseLLMProvider",
    "LLMProviderError",
    "LLMProviderResponse",
    "OpenAIProvider",
    "DeepSeekProvider",
    "LlamaProvider",
    "AnthropicProvider",
    "LLMProviderFactory",
    "get_llm_provider",
    # Services
    "LLMService",
    "get_llm_service",
    "ConversationService",
    "get_conversation_service",
    "UsageService",
    "get_usage_service",
    # Utilities
    "PromptTemplate",
    "get_system_prompt",
    "get_user_prompt",
    "create_conversation_prompt",
    "count_tokens",
    "truncate_text",
    "extract_keywords",
    "summarize_text",
    "clean_text",
    "format_llm_response",
    "parse_llm_response",
    "validate_messages",
    "create_message",
    "estimate_cost",
]
