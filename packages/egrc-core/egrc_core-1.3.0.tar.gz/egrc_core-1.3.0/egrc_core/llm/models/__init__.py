"""
LLM models and schemas for EGRC Platform.

This module provides Pydantic models and SQLAlchemy models for LLM operations,
including request/response tracking, conversation management, and provider
configuration.
"""

from .database import (
    LLMConversationModel,
    LLMErrorModel,
    LLMModelModel,
    LLMProviderModel,
    LLMRequestModel,
    LLMResponseModel,
    LLMUsageModel,
)
from .schemas import (
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


__all__ = [
    # Schemas
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
    # Database Models
    "LLMRequestModel",
    "LLMResponseModel",
    "LLMConversationModel",
    "LLMProviderModel",
    "LLMModelModel",
    "LLMUsageModel",
    "LLMErrorModel",
]
