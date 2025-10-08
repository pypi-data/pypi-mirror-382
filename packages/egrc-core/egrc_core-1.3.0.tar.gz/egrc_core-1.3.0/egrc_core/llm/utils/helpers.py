"""
Helper functions for LLM operations.

This module provides utility functions for common LLM operations including
response formatting, message validation, and cost estimation.
"""

import json
import re
from typing import Any

from ...exceptions.exceptions import ValidationError
from ...logging.utils import get_logger


logger = get_logger(__name__)


def format_llm_response(
    content: str,
    format_type: str = "text",
    **kwargs: Any,
) -> str | dict[str, Any] | list[dict[str, Any]]:
    """
    Format LLM response based on specified format type.

    Args:
        content: Raw LLM response content
        format_type: Format type (text, json, list, markdown)
        **kwargs: Additional formatting options

    Returns:
        Formatted response
    """
    try:
        if format_type == "text":
            return content.strip()

        elif format_type == "json":
            # Try to extract JSON from the content
            json_match = re.search(r"\{.*\}", content, re.DOTALL)
            if json_match:
                return json.loads(json_match.group())
            else:
                # If no JSON found, try to parse the entire content
                return json.loads(content)

        elif format_type == "list":
            # Try to extract list items
            lines = content.strip().split("\n")
            items = []
            for line in lines:
                line = line.strip()
                if line and not line.startswith("#"):
                    # Remove common list markers
                    line = re.sub(r"^[-*•]\s*", "", line)
                    line = re.sub(r"^\d+\.\s*", "", line)
                    if line:
                        items.append(line)
            return items

        elif format_type == "markdown":
            return content.strip()

        else:
            logger.warning(f"Unknown format type: {format_type}")
            return content.strip()

    except json.JSONDecodeError as e:
        logger.error(f"Failed to parse JSON response: {e}")
        raise ValidationError(f"Invalid JSON response: {e}")
    except Exception as e:
        logger.error(f"Failed to format response: {e}")
        return content.strip()


def parse_llm_response(
    content: str,
    expected_format: str = "text",
    **kwargs: Any,
) -> Any:
    """
    Parse LLM response with error handling.

    Args:
        content: LLM response content
        expected_format: Expected format (text, json, list, markdown)
        **kwargs: Additional parsing options

    Returns:
        Parsed response
    """
    try:
        return format_llm_response(content, expected_format, **kwargs)
    except Exception as e:
        logger.error(f"Failed to parse LLM response: {e}")
        return content


def validate_messages(messages: list[dict[str, str]]) -> bool:
    """
    Validate message format for LLM requests.

    Args:
        messages: List of messages to validate

    Returns:
        True if valid

    Raises:
        ValidationError: If messages are invalid
    """
    if not messages:
        raise ValidationError("Messages cannot be empty")

    for i, message in enumerate(messages):
        if not isinstance(message, dict):
            raise ValidationError(f"Message {i} must be a dictionary")

        if "role" not in message:
            raise ValidationError(f"Message {i} missing 'role' field")

        if "content" not in message:
            raise ValidationError(f"Message {i} missing 'content' field")

        if message["role"] not in ["system", "user", "assistant"]:
            raise ValidationError(
                f"Message {i} has invalid role '{message['role']}'. "
                "Must be 'system', 'user', or 'assistant'"
            )

        if not isinstance(message["content"], str):
            raise ValidationError(f"Message {i} content must be a string")

        if not message["content"].strip():
            raise ValidationError(f"Message {i} content cannot be empty")

    return True


def create_message(role: str, content: str, **kwargs: Any) -> dict[str, Any]:
    """
    Create a properly formatted message.

    Args:
        role: Message role (system, user, assistant)
        content: Message content
        **kwargs: Additional message fields

    Returns:
        Formatted message dictionary
    """
    if role not in ["system", "user", "assistant"]:
        raise ValidationError(f"Invalid role: {role}")

    message = {
        "role": role,
        "content": content.strip(),
    }

    # Add any additional fields
    message.update(kwargs)

    return message


def estimate_cost(
    prompt_tokens: int,
    completion_tokens: int,
    model: str,
    provider: str = "openai",
) -> float:
    """
    Estimate cost for LLM usage.

    Args:
        prompt_tokens: Number of prompt tokens
        completion_tokens: Number of completion tokens
        model: Model name
        provider: Provider name

    Returns:
        Estimated cost in USD
    """
    # Cost per 1K tokens (approximate)
    cost_per_1k = {
        "openai": {
            "gpt-4": {"prompt": 0.03, "completion": 0.06},
            "gpt-4-turbo": {"prompt": 0.01, "completion": 0.03},
            "gpt-3.5-turbo": {"prompt": 0.0015, "completion": 0.002},
        },
        "deepseek": {
            "deepseek-chat": {"prompt": 0.0014, "completion": 0.0028},
            "deepseek-coder": {"prompt": 0.0014, "completion": 0.0028},
        },
        "anthropic": {
            "claude-3-opus-20240229": {"prompt": 0.015, "completion": 0.075},
            "claude-3-sonnet-20240229": {"prompt": 0.003, "completion": 0.015},
            "claude-3-haiku-20240307": {"prompt": 0.00025, "completion": 0.00125},
        },
        "llama": {
            "llama3": {"prompt": 0.0, "completion": 0.0},  # Local model
            "llama2": {"prompt": 0.0, "completion": 0.0},  # Local model
        },
    }

    try:
        provider_costs = cost_per_1k.get(provider, {})
        model_costs = provider_costs.get(model, {"prompt": 0.0, "completion": 0.0})

        prompt_cost = (prompt_tokens / 1000) * model_costs["prompt"]
        completion_cost = (completion_tokens / 1000) * model_costs["completion"]

        return prompt_cost + completion_cost

    except Exception as e:
        logger.warning(f"Failed to estimate cost: {e}")
        return 0.0


def extract_json_from_response(content: str) -> dict[str, Any] | None:
    """
    Extract JSON from LLM response content.

    Args:
        content: LLM response content

    Returns:
        Extracted JSON or None if not found
    """
    try:
        # Try to find JSON in the content
        json_patterns = [
            r"\{.*\}",  # Simple object
            r"\[.*\]",  # Simple array
            r"```json\s*(.*?)\s*```",  # JSON in code block
            r"```\s*(.*?)\s*```",  # Generic code block
        ]

        for pattern in json_patterns:
            matches = re.findall(pattern, content, re.DOTALL)
            for match in matches:
                try:
                    return json.loads(match)
                except json.JSONDecodeError:
                    continue

        # If no JSON found, try parsing the entire content
        return json.loads(content)

    except json.JSONDecodeError:
        return None
    except Exception as e:
        logger.warning(f"Failed to extract JSON from response: {e}")
        return None


def sanitize_content(content: str, max_length: int | None = None) -> str:
    """
    Sanitize LLM response content.

    Args:
        content: Content to sanitize
        max_length: Maximum length (truncate if longer)

    Returns:
        Sanitized content
    """
    # Remove excessive whitespace
    content = re.sub(r"\s+", " ", content.strip())

    # Remove potential security issues
    content = re.sub(
        r"<script.*?</script>", "", content, flags=re.DOTALL | re.IGNORECASE
    )
    content = re.sub(r"javascript:", "", content, flags=re.IGNORECASE)

    # Truncate if too long
    if max_length and len(content) > max_length:
        content = content[:max_length] + "..."

    return content


def create_conversation_summary(messages: list[dict[str, str]]) -> str:
    """
    Create a summary of conversation messages.

    Args:
        messages: List of conversation messages

    Returns:
        Conversation summary
    """
    if not messages:
        return "Empty conversation"

    user_messages = [msg for msg in messages if msg["role"] == "user"]
    assistant_messages = [msg for msg in messages if msg["role"] == "assistant"]

    summary = (
        f"Conversation with {len(user_messages)} user messages and "
        f"{len(assistant_messages)} assistant responses"
    )

    if user_messages:
        first_user_msg = user_messages[0]["content"][:100]
        summary += f". First user message: {first_user_msg}..."

    return summary
