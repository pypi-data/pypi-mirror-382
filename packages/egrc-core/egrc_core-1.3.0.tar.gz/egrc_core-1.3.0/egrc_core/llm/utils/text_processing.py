"""
Text processing utilities for LLM operations.

This module provides utilities for text processing, token counting,
and content manipulation for LLM operations.
"""

import re


def count_tokens(text: str, model: str = "gpt-4") -> int:
    """
    Estimate token count for text.

    This is a rough estimation. For accurate counts, use the actual
    tokenizer for the specific model.

    Args:
        text: Text to count tokens for
        model: Model name (affects estimation)

    Returns:
        Estimated token count
    """
    if not text:
        return 0

    # Rough estimation: 1 token ≈ 4 characters for English text
    # This varies by model and language
    base_estimate = len(text) // 4

    # Adjust for different models
    if "gpt-4" in model.lower():
        # GPT-4 is more efficient
        return int(base_estimate * 0.8)
    elif "gpt-3.5" in model.lower():
        # GPT-3.5 is less efficient
        return int(base_estimate * 1.2)
    elif "claude" in model.lower():
        # Claude is similar to GPT-4
        return int(base_estimate * 0.8)
    else:
        # Default estimation
        return base_estimate


def truncate_text(text: str, max_tokens: int, model: str = "gpt-4") -> str:
    """
    Truncate text to fit within token limit.

    Args:
        text: Text to truncate
        max_tokens: Maximum number of tokens
        model: Model name for token estimation

    Returns:
        Truncated text
    """
    if not text:
        return text

    # Estimate characters per token
    chars_per_token = 4  # Rough estimate

    # Calculate max characters
    max_chars = max_tokens * chars_per_token

    if len(text) <= max_chars:
        return text

    # Truncate and add ellipsis
    truncated = text[: max_chars - 3] + "..."

    # Try to break at word boundary
    last_space = truncated.rfind(" ")
    if last_space > max_chars * 0.8:  # If we can break at a reasonable point
        truncated = truncated[:last_space] + "..."

    return truncated


def extract_keywords(text: str, max_keywords: int = 10) -> list[str]:
    """
    Extract keywords from text.

    Args:
        text: Text to extract keywords from
        max_keywords: Maximum number of keywords to return

    Returns:
        List of keywords
    """
    if not text:
        return []

    # Simple keyword extraction using word frequency
    # Remove common stop words
    stop_words = {
        "the",
        "a",
        "an",
        "and",
        "or",
        "but",
        "in",
        "on",
        "at",
        "to",
        "for",
        "of",
        "with",
        "by",
        "is",
        "are",
        "was",
        "were",
        "be",
        "been",
        "have",
        "has",
        "had",
        "do",
        "does",
        "did",
        "will",
        "would",
        "could",
        "should",
        "may",
        "might",
        "must",
        "can",
        "this",
        "that",
        "these",
        "those",
        "i",
        "you",
        "he",
        "she",
        "it",
        "we",
        "they",
        "me",
        "him",
        "her",
        "us",
        "them",
        "my",
        "your",
        "his",
        "her",
        "its",
        "our",
        "their",
    }

    # Clean and split text
    words = re.findall(r"\b[a-zA-Z]+\b", text.lower())

    # Filter out stop words and short words
    keywords = [word for word in words if word not in stop_words and len(word) > 2]

    # Count frequency
    word_freq = {}
    for word in keywords:
        word_freq[word] = word_freq.get(word, 0) + 1

    # Sort by frequency and return top keywords
    sorted_keywords = sorted(word_freq.items(), key=lambda x: x[1], reverse=True)

    return [word for word, freq in sorted_keywords[:max_keywords]]


def summarize_text(text: str, max_length: int = 200) -> str:
    """
    Create a simple summary of text.

    Args:
        text: Text to summarize
        max_length: Maximum length of summary

    Returns:
        Text summary
    """
    if not text:
        return ""

    if len(text) <= max_length:
        return text

    # Find sentences
    sentences = re.split(r"[.!?]+", text)
    sentences = [s.strip() for s in sentences if s.strip()]

    if not sentences:
        return text[:max_length] + "..."

    # Start with first sentence
    summary = sentences[0]

    # Add more sentences until we reach max length
    for sentence in sentences[1:]:
        if len(summary + " " + sentence) <= max_length:
            summary += " " + sentence
        else:
            break

    # Ensure we don't exceed max length
    if len(summary) > max_length:
        summary = summary[: max_length - 3] + "..."

    return summary


def clean_text(text: str) -> str:
    """
    Clean text for LLM processing.

    Args:
        text: Text to clean

    Returns:
        Cleaned text
    """
    if not text:
        return ""

    # Remove excessive whitespace
    text = re.sub(r"\s+", " ", text.strip())

    # Remove control characters
    text = re.sub(r"[\x00-\x08\x0b\x0c\x0e-\x1f\x7f-\x9f]", "", text)

    # Normalize quotes
    text = text.replace('"', '"').replace('"', '"')
    text = text.replace(""", "'").replace(""", "'")

    # Remove excessive punctuation
    text = re.sub(r"[.]{3,}", "...", text)
    text = re.sub(r"[!]{2,}", "!", text)
    text = re.sub(r"[?]{2,}", "?", text)

    return text


def extract_sections(text: str, section_markers: list[str] = None) -> dict[str, str]:
    """
    Extract sections from structured text.

    Args:
        text: Text to extract sections from
        section_markers: List of section markers (default: common headers)

    Returns:
        Dictionary of section names and content
    """
    if not text:
        return {}

    if section_markers is None:
        section_markers = [
            "introduction",
            "summary",
            "overview",
            "background",
            "analysis",
            "findings",
            "recommendations",
            "conclusion",
            "appendix",
            "references",
            "methodology",
            "results",
            "discussion",
            "limitations",
            "future work",
        ]

    sections = {}
    current_section = "main"
    current_content = []

    lines = text.split("\n")

    for line in lines:
        line = line.strip()
        if not line:
            continue

        # Check if line is a section header
        is_section = False
        for marker in section_markers:
            if line.lower().startswith(marker):
                # Save previous section
                if current_content:
                    sections[current_section] = "\n".join(current_content)

                # Start new section
                current_section = marker
                current_content = []
                is_section = True
                break

        if not is_section:
            current_content.append(line)

    # Save last section
    if current_content:
        sections[current_section] = "\n".join(current_content)

    return sections


def format_for_llm(text: str, max_tokens: int = 4000, model: str = "gpt-4") -> str:
    """
    Format text for LLM processing.

    Args:
        text: Text to format
        max_tokens: Maximum tokens allowed
        model: Model name for token estimation

    Returns:
        Formatted text ready for LLM
    """
    if not text:
        return ""

    # Clean the text
    text = clean_text(text)

    # Truncate if necessary
    text = truncate_text(text, max_tokens, model)

    return text


def extract_entities(text: str) -> dict[str, list[str]]:
    """
    Extract basic entities from text.

    Args:
        text: Text to extract entities from

    Returns:
        Dictionary of entity types and values
    """
    if not text:
        return {}

    entities = {
        "emails": [],
        "urls": [],
        "phone_numbers": [],
        "dates": [],
        "amounts": [],
    }

    # Extract emails
    email_pattern = r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b"
    entities["emails"] = re.findall(email_pattern, text)

    # Extract URLs
    url_pattern = (
        r"http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\\(\\),]|"
        r"(?:%[0-9a-fA-F][0-9a-fA-F]))+"
    )
    entities["urls"] = re.findall(url_pattern, text)

    # Extract phone numbers
    phone_pattern = r"\b\d{3}[-.]?\d{3}[-.]?\d{4}\b"
    entities["phone_numbers"] = re.findall(phone_pattern, text)

    # Extract dates (basic patterns)
    date_pattern = r"\b\d{1,2}[/-]\d{1,2}[/-]\d{2,4}\b"
    entities["dates"] = re.findall(date_pattern, text)

    # Extract monetary amounts
    amount_pattern = r"\$\d+(?:,\d{3})*(?:\.\d{2})?"
    entities["amounts"] = re.findall(amount_pattern, text)

    # Remove empty lists
    entities = {k: v for k, v in entities.items() if v}

    return entities


def calculate_text_similarity(text1: str, text2: str) -> float:
    """
    Calculate simple text similarity using Jaccard similarity.

    Args:
        text1: First text
        text2: Second text

    Returns:
        Similarity score between 0 and 1
    """
    if not text1 or not text2:
        return 0.0

    # Convert to lowercase and split into words
    words1 = set(text1.lower().split())
    words2 = set(text2.lower().split())

    # Calculate Jaccard similarity
    intersection = len(words1.intersection(words2))
    union = len(words1.union(words2))

    if union == 0:
        return 0.0

    return intersection / union
