"""
Conversation service for LLM operations.

This module provides conversation management functionality including
creating, updating, and retrieving conversation history.
"""

from datetime import datetime
from typing import Any
from uuid import UUID

from sqlalchemy import desc, select

from ...database import get_async_db_session
from ...exceptions.exceptions import NotFoundError, ValidationError
from ...logging.utils import get_logger
from ..models.database import LLMConversationModel
from ..models.schemas import LLMConversation, LLMConversationCreate


logger = get_logger(__name__)


class ConversationService:
    """Service for managing LLM conversations."""

    def __init__(self):
        """Initialize conversation service."""
        self.logger = get_logger(
            f"{self.__class__.__module__}.{self.__class__.__name__}"
        )

    async def create_conversation(
        self,
        title: str | None = None,
        provider: str = "openai",
        model: str = "gpt-4",
        messages: list[dict[str, str]] | None = None,
        llm_metadata: dict[str, Any] | None = None,
        tenant_id: str | None = None,
        service_name: str | None = None,
    ) -> LLMConversation:
        """
        Create a new conversation.

        Args:
            title: Conversation title
            provider: LLM provider
            model: Model name
            messages: Initial messages
            llm_metadata: Additional metadata
            tenant_id: Tenant ID
            service_name: Service name

        Returns:
            Created conversation
        """
        try:
            conversation_data = LLMConversationCreate(
                title=title,
                provider=provider,
                model=model,
                messages=messages or [],
                llm_metadata=llm_metadata,
                tenant_id=tenant_id,
                service_name=service_name,
            )

            async with get_async_db_session() as db:
                db_conversation = LLMConversationModel(
                    title=conversation_data.title,
                    provider=conversation_data.provider,
                    model=conversation_data.model,
                    messages=conversation_data.messages,
                    llm_metadata=conversation_data.llm_metadata,
                    tenant_id=conversation_data.tenant_id,
                    service_name=conversation_data.service_name,
                )

                db.add(db_conversation)
                await db.commit()
                await db.refresh(db_conversation)

                self.logger.info(
                    f"Created conversation {db_conversation.id}",
                    extra={
                        "conversation_id": str(db_conversation.id),
                        "provider": provider,
                        "model": model,
                        "tenant_id": tenant_id,
                        "service_name": service_name,
                    },
                )

                return self._db_to_schema(db_conversation)

        except Exception as e:
            self.logger.error(f"Failed to create conversation: {e}")
            raise

    async def get_conversation(
        self,
        conversation_id: UUID,
        tenant_id: str | None = None,
        service_name: str | None = None,
    ) -> LLMConversation:
        """
        Get a conversation by ID.

        Args:
            conversation_id: Conversation ID
            tenant_id: Tenant ID
            service_name: Service name

        Returns:
            Conversation data

        Raises:
            NotFoundError: If conversation not found
        """
        try:
            async with get_async_db_session() as db:
                query = select(LLMConversationModel).where(
                    LLMConversationModel.id == conversation_id
                )

                # Add tenant/service filters if provided
                if tenant_id:
                    query = query.where(LLMConversationModel.tenant_id == tenant_id)
                if service_name:
                    query = query.where(
                        LLMConversationModel.service_name == service_name
                    )

                result = await db.execute(query)
                db_conversation = result.scalar_one_or_none()

                if not db_conversation:
                    raise NotFoundError(
                        resource="LLMConversation", identifier=str(conversation_id)
                    )

                return self._db_to_schema(db_conversation)

        except NotFoundError:
            raise
        except Exception as e:
            self.logger.error(f"Failed to get conversation {conversation_id}: {e}")
            raise

    async def update_conversation(
        self,
        conversation_id: UUID,
        title: str | None = None,
        messages: list[dict[str, str]] | None = None,
        llm_metadata: dict[str, Any] | None = None,
        is_active: bool | None = None,
        tenant_id: str | None = None,
        service_name: str | None = None,
    ) -> LLMConversation:
        """
        Update a conversation.

        Args:
            conversation_id: Conversation ID
            title: New title
            messages: Updated messages
            llm_metadata: Updated metadata
            is_active: Active status
            tenant_id: Tenant ID
            service_name: Service name

        Returns:
            Updated conversation

        Raises:
            NotFoundError: If conversation not found
        """
        try:
            async with get_async_db_session() as db:
                query = select(LLMConversationModel).where(
                    LLMConversationModel.id == conversation_id
                )

                # Add tenant/service filters if provided
                if tenant_id:
                    query = query.where(LLMConversationModel.tenant_id == tenant_id)
                if service_name:
                    query = query.where(
                        LLMConversationModel.service_name == service_name
                    )

                result = await db.execute(query)
                db_conversation = result.scalar_one_or_none()

                if not db_conversation:
                    raise NotFoundError(
                        resource="LLMConversation", identifier=str(conversation_id)
                    )

                # Update fields
                if title is not None:
                    db_conversation.title = title
                if messages is not None:
                    db_conversation.messages = messages
                if llm_metadata is not None:
                    db_conversation.llm_metadata = llm_metadata
                if is_active is not None:
                    db_conversation.is_active = is_active

                db_conversation.updated_at = datetime.utcnow()

                await db.commit()
                await db.refresh(db_conversation)

                self.logger.info(
                    f"Updated conversation {conversation_id}",
                    extra={
                        "conversation_id": str(conversation_id),
                        "tenant_id": tenant_id,
                        "service_name": service_name,
                    },
                )

                return self._db_to_schema(db_conversation)

        except NotFoundError:
            raise
        except Exception as e:
            self.logger.error(f"Failed to update conversation {conversation_id}: {e}")
            raise

    async def add_message_to_conversation(
        self,
        conversation_id: UUID,
        role: str,
        content: str,
        tenant_id: str | None = None,
        service_name: str | None = None,
    ) -> LLMConversation:
        """
        Add a message to a conversation.

        Args:
            conversation_id: Conversation ID
            role: Message role (system, user, assistant)
            content: Message content
            tenant_id: Tenant ID
            service_name: Service name

        Returns:
            Updated conversation
        """
        if role not in ["system", "user", "assistant"]:
            raise ValidationError(
                f"Invalid role: {role}. Must be 'system', 'user', or 'assistant'"
            )

        try:
            async with get_async_db_session() as db:
                query = select(LLMConversationModel).where(
                    LLMConversationModel.id == conversation_id
                )

                # Add tenant/service filters if provided
                if tenant_id:
                    query = query.where(LLMConversationModel.tenant_id == tenant_id)
                if service_name:
                    query = query.where(
                        LLMConversationModel.service_name == service_name
                    )

                result = await db.execute(query)
                db_conversation = result.scalar_one_or_none()

                if not db_conversation:
                    raise NotFoundError(
                        resource="LLMConversation", identifier=str(conversation_id)
                    )

                # Add new message
                new_message = {"role": role, "content": content}
                db_conversation.messages.append(new_message)
                db_conversation.updated_at = datetime.utcnow()

                await db.commit()
                await db.refresh(db_conversation)

                self.logger.info(
                    f"Added message to conversation {conversation_id}",
                    extra={
                        "conversation_id": str(conversation_id),
                        "role": role,
                        "content_length": len(content),
                        "tenant_id": tenant_id,
                        "service_name": service_name,
                    },
                )

                return self._db_to_schema(db_conversation)

        except (NotFoundError, ValidationError):
            raise
        except Exception as e:
            self.logger.error(
                f"Failed to add message to conversation {conversation_id}: {e}"
            )
            raise

    async def list_conversations(
        self,
        tenant_id: str | None = None,
        service_name: str | None = None,
        provider: str | None = None,
        model: str | None = None,
        is_active: bool | None = None,
        limit: int = 50,
        offset: int = 0,
    ) -> list[LLMConversation]:
        """
        List conversations with optional filters.

        Args:
            tenant_id: Tenant ID filter
            service_name: Service name filter
            provider: Provider filter
            model: Model filter
            is_active: Active status filter
            limit: Maximum number of results
            offset: Number of results to skip

        Returns:
            List of conversations
        """
        try:
            async with get_async_db_session() as db:
                query = select(LLMConversationModel)

                # Apply filters
                if tenant_id:
                    query = query.where(LLMConversationModel.tenant_id == tenant_id)
                if service_name:
                    query = query.where(
                        LLMConversationModel.service_name == service_name
                    )
                if provider:
                    query = query.where(LLMConversationModel.provider == provider)
                if model:
                    query = query.where(LLMConversationModel.model == model)
                if is_active is not None:
                    query = query.where(LLMConversationModel.is_active == is_active)

                # Order by updated_at descending
                query = query.order_by(desc(LLMConversationModel.updated_at))

                # Apply pagination
                query = query.offset(offset).limit(limit)

                result = await db.execute(query)
                db_conversations = result.scalars().all()

                return [self._db_to_schema(conv) for conv in db_conversations]

        except Exception as e:
            self.logger.error(f"Failed to list conversations: {e}")
            raise

    async def delete_conversation(
        self,
        conversation_id: UUID,
        tenant_id: str | None = None,
        service_name: str | None = None,
    ) -> bool:
        """
        Delete a conversation (soft delete by setting is_active=False).

        Args:
            conversation_id: Conversation ID
            tenant_id: Tenant ID
            service_name: Service name

        Returns:
            True if deleted successfully

        Raises:
            NotFoundError: If conversation not found
        """
        try:
            async with get_async_db_session() as db:
                query = select(LLMConversationModel).where(
                    LLMConversationModel.id == conversation_id
                )

                # Add tenant/service filters if provided
                if tenant_id:
                    query = query.where(LLMConversationModel.tenant_id == tenant_id)
                if service_name:
                    query = query.where(
                        LLMConversationModel.service_name == service_name
                    )

                result = await db.execute(query)
                db_conversation = result.scalar_one_or_none()

                if not db_conversation:
                    raise NotFoundError(
                        resource="LLMConversation", identifier=str(conversation_id)
                    )

                # Soft delete
                db_conversation.is_active = False
                db_conversation.updated_at = datetime.utcnow()

                await db.commit()

                self.logger.info(
                    f"Deleted conversation {conversation_id}",
                    extra={
                        "conversation_id": str(conversation_id),
                        "tenant_id": tenant_id,
                        "service_name": service_name,
                    },
                )

                return True

        except NotFoundError:
            raise
        except Exception as e:
            self.logger.error(f"Failed to delete conversation {conversation_id}: {e}")
            raise

    def _db_to_schema(self, db_conversation: LLMConversationModel) -> LLMConversation:
        """Convert database model to schema."""
        return LLMConversation(
            id=db_conversation.id,
            title=db_conversation.title,
            provider=db_conversation.provider,
            model=db_conversation.model,
            messages=db_conversation.messages,
            total_tokens=db_conversation.total_tokens,
            total_cost=db_conversation.total_cost,
            llm_metadata=db_conversation.llm_metadata,
            tenant_id=db_conversation.tenant_id,
            service_name=db_conversation.service_name,
            is_active=db_conversation.is_active,
            created_at=db_conversation.created_at,
            updated_at=db_conversation.updated_at,
        )


# Global service instance
_conversation_service: ConversationService | None = None


def get_conversation_service() -> ConversationService:
    """Get global conversation service instance."""
    global _conversation_service
    if _conversation_service is None:
        _conversation_service = ConversationService()
    return _conversation_service
