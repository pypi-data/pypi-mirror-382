"""
SQLAlchemy database models for LLM operations.

This module provides SQLAlchemy models for storing LLM requests, responses,
conversations, and provider information in the database.
"""

from datetime import datetime
from uuid import uuid4

from sqlalchemy import JSON, Boolean, Column, DateTime, Float, Integer, String, Text
from sqlalchemy.dialects.postgresql import UUID as PostgresUUID

from ...database.declarative import Base


class LLMProviderModel(Base):
    """LLM provider database model."""

    __tablename__ = "llm_providers"

    id = Column(PostgresUUID(as_uuid=True), primary_key=True, default=uuid4)
    name = Column(String(100), nullable=False, unique=True, index=True)
    version = Column(String(50), nullable=True)
    base_url = Column(String(500), nullable=False)
    api_key_hash = Column(String(255), nullable=True)  # Hashed API key for security
    models = Column(JSON, nullable=True, default=list)
    capabilities = Column(JSON, nullable=True, default=list)
    is_active = Column(Boolean, default=True, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(
        DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False
    )


class LLMModelModel(Base):
    """LLM model database model."""

    __tablename__ = "llm_models"

    id = Column(PostgresUUID(as_uuid=True), primary_key=True, default=uuid4)
    name = Column(String(200), nullable=False, index=True)
    provider_id = Column(PostgresUUID(as_uuid=True), nullable=False, index=True)
    version = Column(String(50), nullable=True)
    max_tokens = Column(Integer, nullable=False)
    context_length = Column(Integer, nullable=False)
    capabilities = Column(JSON, nullable=True, default=list)
    cost_per_token = Column(Float, nullable=True)
    is_active = Column(Boolean, default=True, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(
        DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False
    )


class LLMConversationModel(Base):
    """LLM conversation database model."""

    __tablename__ = "llm_conversations"

    id = Column(PostgresUUID(as_uuid=True), primary_key=True, default=uuid4)
    title = Column(String(500), nullable=True)
    provider = Column(String(100), nullable=False, index=True)
    model = Column(String(200), nullable=False, index=True)
    messages = Column(JSON, nullable=False, default=list)
    total_tokens = Column(Integer, default=0, nullable=False)
    total_cost = Column(Float, nullable=True)
    llm_metadata = Column(JSON, nullable=True)
    tenant_id = Column(String(100), nullable=True, index=True)
    service_name = Column(String(100), nullable=True, index=True)
    is_active = Column(Boolean, default=True, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(
        DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False
    )


class LLMRequestModel(Base):
    """LLM request database model."""

    __tablename__ = "llm_requests"

    id = Column(PostgresUUID(as_uuid=True), primary_key=True, default=uuid4)
    conversation_id = Column(PostgresUUID(as_uuid=True), nullable=True, index=True)
    provider = Column(String(100), nullable=False, index=True)
    model = Column(String(200), nullable=False, index=True)
    messages = Column(JSON, nullable=False)
    temperature = Column(Float, nullable=False)
    max_tokens = Column(Integer, nullable=False)
    top_p = Column(Float, nullable=True)
    frequency_penalty = Column(Float, nullable=True)
    presence_penalty = Column(Float, nullable=True)
    stop = Column(JSON, nullable=True)
    stream = Column(Boolean, default=False, nullable=False)
    user = Column(String(100), nullable=True)
    llm_metadata = Column(JSON, nullable=True)
    tenant_id = Column(String(100), nullable=True, index=True)
    service_name = Column(String(100), nullable=True, index=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(
        DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False
    )


class LLMResponseModel(Base):
    """LLM response database model."""

    __tablename__ = "llm_responses"

    id = Column(PostgresUUID(as_uuid=True), primary_key=True, default=uuid4)
    request_id = Column(PostgresUUID(as_uuid=True), nullable=False, index=True)
    content = Column(Text, nullable=False)
    finish_reason = Column(String(100), nullable=True)
    prompt_tokens = Column(Integer, nullable=True)
    completion_tokens = Column(Integer, nullable=True)
    total_tokens = Column(Integer, nullable=True)
    cost = Column(Float, nullable=True)
    error_type = Column(String(100), nullable=True)
    error_message = Column(Text, nullable=True)
    error_code = Column(String(100), nullable=True)
    error_details = Column(JSON, nullable=True)
    llm_metadata = Column(JSON, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(
        DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False
    )


class LLMUsageModel(Base):
    """LLM usage tracking database model."""

    __tablename__ = "llm_usage"

    id = Column(PostgresUUID(as_uuid=True), primary_key=True, default=uuid4)
    provider = Column(String(100), nullable=False, index=True)
    model = Column(String(200), nullable=False, index=True)
    tenant_id = Column(String(100), nullable=True, index=True)
    service_name = Column(String(100), nullable=True, index=True)
    date = Column(DateTime, nullable=False, index=True)
    prompt_tokens = Column(Integer, default=0, nullable=False)
    completion_tokens = Column(Integer, default=0, nullable=False)
    total_tokens = Column(Integer, default=0, nullable=False)
    cost = Column(Float, default=0.0, nullable=False)
    request_count = Column(Integer, default=0, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(
        DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False
    )


class LLMErrorModel(Base):
    """LLM error tracking database model."""

    __tablename__ = "llm_errors"

    id = Column(PostgresUUID(as_uuid=True), primary_key=True, default=uuid4)
    provider = Column(String(100), nullable=False, index=True)
    model = Column(String(200), nullable=False, index=True)
    error_type = Column(String(100), nullable=False, index=True)
    error_message = Column(Text, nullable=False)
    error_code = Column(String(100), nullable=True)
    error_details = Column(JSON, nullable=True)
    tenant_id = Column(String(100), nullable=True, index=True)
    service_name = Column(String(100), nullable=True, index=True)
    request_id = Column(PostgresUUID(as_uuid=True), nullable=True, index=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
