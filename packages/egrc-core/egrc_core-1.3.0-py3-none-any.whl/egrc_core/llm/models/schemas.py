"""
Pydantic schemas for LLM operations.

This module provides Pydantic models for LLM request/response validation,
conversation management, and provider configuration.
"""

from datetime import datetime
from typing import Any
from uuid import UUID

from pydantic import BaseModel, Field, field_validator


class LLMUsage(BaseModel):
    """LLM usage statistics."""

    prompt_tokens: int = Field(ge=0, description="Number of prompt tokens")
    completion_tokens: int = Field(ge=0, description="Number of completion tokens")
    total_tokens: int = Field(ge=0, description="Total number of tokens")
    cost: float | None = Field(None, ge=0, description="Cost in USD")


class LLMError(BaseModel):
    """LLM error information."""

    error_type: str = Field(description="Type of error")
    error_message: str = Field(description="Error message")
    error_code: str | None = Field(None, description="Error code")
    details: dict[str, Any] | None = Field(None, description="Additional error details")


class LLMProvider(BaseModel):
    """LLM provider information."""

    name: str = Field(description="Provider name (openai, deepseek, llama, anthropic)")
    version: str | None = Field(None, description="Provider version")
    base_url: str = Field(description="Provider base URL")
    api_key: str | None = Field(None, description="API key (masked)")
    models: list[str] = Field(default_factory=list, description="Available models")
    capabilities: list[str] = Field(
        default_factory=list, description="Provider capabilities"
    )
    is_active: bool = Field(default=True, description="Whether provider is active")


class LLMModel(BaseModel):
    """LLM model information."""

    name: str = Field(description="Model name")
    provider: str = Field(description="Provider name")
    version: str | None = Field(None, description="Model version")
    max_tokens: int = Field(ge=1, description="Maximum tokens")
    context_length: int = Field(ge=1, description="Context length")
    capabilities: list[str] = Field(
        default_factory=list, description="Model capabilities"
    )
    cost_per_token: float | None = Field(None, ge=0, description="Cost per token")
    is_active: bool = Field(default=True, description="Whether model is active")


class LLMRequest(BaseModel):
    """LLM request model."""

    id: UUID = Field(description="Request ID")
    conversation_id: UUID | None = Field(None, description="Conversation ID")
    provider: str = Field(description="LLM provider")
    model: str = Field(description="Model name")
    messages: list[dict[str, str]] = Field(description="Chat messages")
    temperature: float = Field(ge=0.0, le=2.0, description="Temperature")
    max_tokens: int = Field(ge=1, description="Maximum tokens")
    top_p: float | None = Field(None, ge=0.0, le=1.0, description="Top-p value")
    frequency_penalty: float | None = Field(
        None, ge=-2.0, le=2.0, description="Frequency penalty"
    )
    presence_penalty: float | None = Field(
        None, ge=-2.0, le=2.0, description="Presence penalty"
    )
    stop: list[str] | None = Field(None, description="Stop sequences")
    stream: bool = Field(default=False, description="Whether to stream response")
    user: str | None = Field(None, description="User identifier")
    metadata: dict[str, Any] | None = Field(None, description="Additional metadata")
    tenant_id: str | None = Field(None, description="Tenant ID")
    service_name: str | None = Field(None, description="Service name")
    created_at: datetime = Field(description="Creation timestamp")
    updated_at: datetime = Field(description="Last update timestamp")


class LLMResponse(BaseModel):
    """LLM response model."""

    id: UUID = Field(description="Response ID")
    request_id: UUID = Field(description="Request ID")
    content: str = Field(description="Response content")
    finish_reason: str | None = Field(None, description="Finish reason")
    usage: LLMUsage | None = Field(None, description="Usage statistics")
    error: LLMError | None = Field(None, description="Error information")
    metadata: dict[str, Any] | None = Field(None, description="Additional metadata")
    created_at: datetime = Field(description="Creation timestamp")
    updated_at: datetime = Field(description="Last update timestamp")


class LLMConversation(BaseModel):
    """LLM conversation model."""

    id: UUID = Field(description="Conversation ID")
    title: str | None = Field(None, description="Conversation title")
    provider: str = Field(description="LLM provider")
    model: str = Field(description="Model name")
    messages: list[dict[str, str]] = Field(
        default_factory=list, description="All messages"
    )
    total_tokens: int = Field(default=0, ge=0, description="Total tokens used")
    total_cost: float | None = Field(None, ge=0, description="Total cost")
    metadata: dict[str, Any] | None = Field(None, description="Additional metadata")
    tenant_id: str | None = Field(None, description="Tenant ID")
    service_name: str | None = Field(None, description="Service name")
    is_active: bool = Field(default=True, description="Whether conversation is active")
    created_at: datetime = Field(description="Creation timestamp")
    updated_at: datetime = Field(description="Last update timestamp")


# Create schemas
class LLMRequestCreate(BaseModel):
    """Schema for creating LLM requests."""

    conversation_id: UUID | None = None
    provider: str = Field(description="LLM provider")
    model: str = Field(description="Model name")
    messages: list[dict[str, str]] = Field(description="Chat messages")
    temperature: float = Field(default=0.7, ge=0.0, le=2.0)
    max_tokens: int = Field(default=4000, ge=1)
    top_p: float | None = Field(None, ge=0.0, le=1.0)
    frequency_penalty: float | None = Field(None, ge=-2.0, le=2.0)
    presence_penalty: float | None = Field(None, ge=-2.0, le=2.0)
    stop: list[str] | None = None
    stream: bool = False
    user: str | None = None
    llm_metadata: dict[str, Any] | None = None
    tenant_id: str | None = None
    service_name: str | None = None

    @field_validator("messages")
    @classmethod
    def validate_messages(cls, v: list[dict[str, str]]) -> list[dict[str, str]]:
        """Validate messages format."""
        if not v:
            raise ValueError("Messages cannot be empty")

        for message in v:
            if not isinstance(message, dict):
                raise ValueError("Each message must be a dictionary")
            if "role" not in message or "content" not in message:
                raise ValueError("Each message must have 'role' and 'content' keys")
            if message["role"] not in ["system", "user", "assistant"]:
                raise ValueError("Role must be 'system', 'user', or 'assistant'")

        return v


class LLMResponseCreate(BaseModel):
    """Schema for creating LLM responses."""

    request_id: UUID = Field(description="Request ID")
    content: str = Field(description="Response content")
    finish_reason: str | None = None
    usage: LLMUsage | None = None
    error: LLMError | None = None
    llm_metadata: dict[str, Any] | None = None


class LLMConversationCreate(BaseModel):
    """Schema for creating LLM conversations."""

    title: str | None = None
    provider: str = Field(description="LLM provider")
    model: str = Field(description="Model name")
    messages: list[dict[str, str]] = Field(default_factory=list)
    llm_metadata: dict[str, Any] | None = None
    tenant_id: str | None = None
    service_name: str | None = None


# Update schemas
class LLMRequestUpdate(BaseModel):
    """Schema for updating LLM requests."""

    llm_metadata: dict[str, Any] | None = None


class LLMResponseUpdate(BaseModel):
    """Schema for updating LLM responses."""

    content: str | None = None
    finish_reason: str | None = None
    usage: LLMUsage | None = None
    error: LLMError | None = None
    llm_metadata: dict[str, Any] | None = None


class LLMConversationUpdate(BaseModel):
    """Schema for updating LLM conversations."""

    title: str | None = None
    messages: list[dict[str, str]] | None = None
    llm_metadata: dict[str, Any] | None = None
    is_active: bool | None = None
