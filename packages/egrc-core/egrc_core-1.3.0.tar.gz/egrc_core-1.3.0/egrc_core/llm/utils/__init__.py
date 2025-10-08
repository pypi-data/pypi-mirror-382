"""
LLM utilities for EGRC Platform.

This module provides utility functions for common LLM operations including
prompt templates, text processing, and helper functions.
"""

from .helpers import (
    create_message,
    estimate_cost,
    format_llm_response,
    parse_llm_response,
    validate_messages,
)
from .prompt_templates import (
    PromptTemplate,
    create_conversation_prompt,
    get_system_prompt,
    get_user_prompt,
)
from .text_processing import (
    clean_text,
    count_tokens,
    extract_keywords,
    summarize_text,
    truncate_text,
)


__all__ = [
    # Prompt templates
    "PromptTemplate",
    "get_system_prompt",
    "get_user_prompt",
    "create_conversation_prompt",
    # Text processing
    "count_tokens",
    "truncate_text",
    "extract_keywords",
    "summarize_text",
    "clean_text",
    # Helpers
    "format_llm_response",
    "parse_llm_response",
    "validate_messages",
    "create_message",
    "estimate_cost",
]
