"""
Utility functions for EGRC Platform.

This module provides common utility functions used across all EGRC services
for data processing, validation, formatting, and other common operations.
"""

import hashlib
import json
import re
import secrets
import string
import unicodedata
from datetime import datetime, timezone
from typing import Any
from uuid import UUID, uuid4

import bcrypt
from passlib.context import CryptContext


# Password hashing context
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def generate_uuid() -> str:
    """Generate a new UUID string.

    Returns:
        UUID string
    """
    return str(uuid4())


def generate_secure_token(length: int = 32) -> str:
    """Generate a secure random token.

    Args:
        length: Token length

    Returns:
        Secure random token
    """
    alphabet = string.ascii_letters + string.digits
    return "".join(secrets.choice(alphabet) for _ in range(length))


def generate_api_key() -> str:
    """Generate a secure API key.

    Returns:
        Secure API key
    """
    return f"egrc_{generate_secure_token(40)}"


def hash_password(password: str) -> str:
    """Hash a password using bcrypt.

    Args:
        password: Plain text password

    Returns:
        Hashed password
    """
    return pwd_context.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a password against its hash.

    Args:
        plain_password: Plain text password
        hashed_password: Hashed password

    Returns:
        True if password matches, False otherwise
    """
    return pwd_context.verify(plain_password, hashed_password)


def generate_password_hash(password: str, salt_rounds: int = 12) -> str:
    """Generate password hash with custom salt rounds.

    Args:
        password: Plain text password
        salt_rounds: Number of salt rounds (defaults to 12)

    Returns:
        Hashed password
    """
    salt = bcrypt.gensalt(rounds=salt_rounds)
    return bcrypt.hashpw(password.encode("utf-8"), salt).decode("utf-8")


def verify_password_hash(password: str, hashed_password: str) -> bool:
    """Verify password against hash.

    Args:
        password: Plain text password
        hashed_password: Hashed password

    Returns:
        True if password matches, False otherwise
    """
    return bcrypt.checkpw(password.encode("utf-8"), hashed_password.encode("utf-8"))


def generate_checksum(data: str | bytes) -> str:
    """Generate SHA-256 checksum for data.

    Args:
        data: Data to generate checksum for

    Returns:
        SHA-256 checksum
    """
    if isinstance(data, str):
        data = data.encode("utf-8")

    return hashlib.sha256(data).hexdigest()


def mask_sensitive_data(data: str, visible_chars: int = 4) -> str:
    """Mask sensitive data for logging.

    Args:
        data: Sensitive data to mask
        visible_chars: Number of characters to show at the end

    Returns:
        Masked data
    """
    if len(data) <= visible_chars:
        return "*" * len(data)

    return "*" * (len(data) - visible_chars) + data[-visible_chars:]


def sanitize_string(text: str) -> str:
    """Sanitize string by removing potentially dangerous characters.

    Args:
        text: Text to sanitize

    Returns:
        Sanitized text
    """
    return text.strip().replace("<", "&lt;").replace(">", "&gt;")


def validate_email(email: str) -> bool:
    """Validate email format.

    Args:
        email: Email address to validate

    Returns:
        True if valid, False otherwise
    """
    pattern = r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$"
    return bool(re.match(pattern, email))


def validate_password_strength(
    password: str,
    min_length: int = 8,
    require_uppercase: bool = True,
    require_lowercase: bool = True,
    require_numbers: bool = True,
    require_special: bool = True,
) -> dict[str, Any]:
    """Validate password strength.

    Args:
        password: Password to validate
        min_length: Minimum password length
        require_uppercase: Whether to require uppercase letters
        require_lowercase: Whether to require lowercase letters
        require_numbers: Whether to require numbers
        require_special: Whether to require special characters

    Returns:
        Validation result with details
    """
    result = {
        "is_valid": True,
        "errors": [],
        "score": 0,
    }

    # Length check
    if len(password) < min_length:
        result["errors"].append(
            f"Password must be at least {min_length} characters long"
        )
        result["is_valid"] = False
    else:
        result["score"] += 1

    # Uppercase check
    if require_uppercase and not any(c.isupper() for c in password):
        result["errors"].append("Password must contain at least one uppercase letter")
        result["is_valid"] = False
    else:
        result["score"] += 1

    # Lowercase check
    if require_lowercase and not any(c.islower() for c in password):
        result["errors"].append("Password must contain at least one lowercase letter")
        result["is_valid"] = False
    else:
        result["score"] += 1

    # Numbers check
    if require_numbers and not any(c.isdigit() for c in password):
        result["errors"].append("Password must contain at least one number")
        result["is_valid"] = False
    else:
        result["score"] += 1

    # Special characters check
    if require_special:
        special_chars = '!@#$%^&*(),.?":{}|<>'
        if not any(c in special_chars for c in password):
            result["errors"].append(
                "Password must contain at least one special character"
            )
            result["is_valid"] = False
        else:
            result["score"] += 1

    return result


def format_bytes(bytes_value: int, decimals: int = 2) -> str:
    """Format bytes to human readable format.

    Args:
        bytes_value: Number of bytes
        decimals: Number of decimal places

    Returns:
        Formatted string
    """
    if bytes_value == 0:
        return "0 Bytes"

    k = 1024
    sizes = ["Bytes", "KB", "MB", "GB", "TB", "PB", "EB", "ZB", "YB"]

    i = 0
    while bytes_value >= k and i < len(sizes) - 1:
        bytes_value /= k
        i += 1

    return f"{bytes_value:.{decimals}f} {sizes[i]}"


def format_duration(seconds: float) -> str:
    """Format duration in seconds to human readable format.

    Args:
        seconds: Duration in seconds

    Returns:
        Formatted duration string
    """
    if seconds < 1:
        return f"{seconds * 1000:.0f}ms"

    if seconds < 60:
        return f"{seconds:.1f}s"

    if seconds < 3600:
        minutes = seconds / 60
        return f"{minutes:.1f}m"

    hours = seconds / 3600
    return f"{hours:.1f}h"


def deep_merge_dicts(dict1: dict[str, Any], dict2: dict[str, Any]) -> dict[str, Any]:
    """Deep merge two dictionaries.

    Args:
        dict1: First dictionary
        dict2: Second dictionary

    Returns:
        Merged dictionary
    """
    result = dict1.copy()

    for key, value in dict2.items():
        if key in result and isinstance(result[key], dict) and isinstance(value, dict):
            result[key] = deep_merge_dicts(result[key], value)
        else:
            result[key] = value

    return result


def remove_none_values(data: dict[str, Any]) -> dict[str, Any]:
    """Remove None values from dictionary recursively.

    Args:
        data: Dictionary to clean

    Returns:
        Cleaned dictionary
    """
    if not isinstance(data, dict):
        return data

    result = {}
    for key, value in data.items():
        if value is not None:
            if isinstance(value, dict):
                cleaned_value = remove_none_values(value)
                if cleaned_value:  # Only add if not empty after cleaning
                    result[key] = cleaned_value
            elif isinstance(value, list):
                cleaned_list = [
                    remove_none_values(item) for item in value if item is not None
                ]
                if cleaned_list:  # Only add if not empty after cleaning
                    result[key] = cleaned_list
            else:
                result[key] = value

    return result


def flatten_dict(
    data: dict[str, Any], parent_key: str = "", sep: str = "."
) -> dict[str, Any]:
    """Flatten nested dictionary.

    Args:
        data: Dictionary to flatten
        parent_key: Parent key for recursion
        sep: Separator for keys

    Returns:
        Flattened dictionary
    """
    items = []

    for key, value in data.items():
        new_key = f"{parent_key}{sep}{key}" if parent_key else key

        if isinstance(value, dict):
            items.extend(flatten_dict(value, new_key, sep=sep).items())
        else:
            items.append((new_key, value))

    return dict(items)


def unflatten_dict(data: dict[str, Any], sep: str = ".") -> dict[str, Any]:
    """Unflatten dictionary with dot notation.

    Args:
        data: Flattened dictionary
        sep: Separator for keys

    Returns:
        Unflattened dictionary
    """
    result = {}

    for key, value in data.items():
        keys = key.split(sep)
        current = result

        for k in keys[:-1]:
            if k not in current:
                current[k] = {}
            current = current[k]

        current[keys[-1]] = value

    return result


def convert_to_snake_case(text: str) -> str:
    """Convert text to snake_case.

    Args:
        text: Text to convert

    Returns:
        Snake case text
    """
    # Insert underscore before uppercase letters
    text = re.sub(r"([a-z0-9])([A-Z])", r"\1_\2", text)
    # Convert to lowercase
    text = text.lower()
    # Replace spaces and hyphens with underscores
    text = re.sub(r"[\s\-]+", "_", text)
    # Remove multiple underscores
    text = re.sub(r"_+", "_", text)
    # Remove leading/trailing underscores
    text = text.strip("_")

    return text


def convert_to_camel_case(text: str) -> str:
    """Convert text to camelCase.

    Args:
        text: Text to convert

    Returns:
        Camel case text
    """
    # Split by underscores, spaces, and hyphens
    words = re.split(r"[\s_\-]+", text)

    if not words:
        return ""

    # First word lowercase, rest capitalize
    result = words[0].lower()
    for word in words[1:]:
        result += word.capitalize()

    return result


def convert_to_pascal_case(text: str) -> str:
    """Convert text to PascalCase.

    Args:
        text: Text to convert

    Returns:
        Pascal case text
    """
    # Split by underscores, spaces, and hyphens
    words = re.split(r"[\s_\-]+", text)

    if not words:
        return ""

    # Capitalize all words
    result = ""
    for word in words:
        result += word.capitalize()

    return result


def truncate_string(text: str, max_length: int, suffix: str = "...") -> str:
    """Truncate string to maximum length.

    Args:
        text: Text to truncate
        max_length: Maximum length
        suffix: Suffix to add if truncated

    Returns:
        Truncated text
    """
    if len(text) <= max_length:
        return text

    return text[: max_length - len(suffix)] + suffix


def extract_domain_from_email(email: str) -> str | None:
    """Extract domain from email address.

    Args:
        email: Email address

    Returns:
        Domain or None if invalid
    """
    if not validate_email(email):
        return None

    return email.split("@")[1].lower()


def generate_slug(text: str, max_length: int = 50) -> str:
    """Generate a URL-friendly slug from text.

    Args:
        text: Text to convert to slug
        max_length: Maximum slug length

    Returns:
        URL-friendly slug
    """
    # Convert to lowercase
    text = text.lower()

    # Remove accents
    text = unicodedata.normalize("NFD", text)
    text = "".join(c for c in text if unicodedata.category(c) != "Mn")

    # Replace spaces and special characters with hyphens
    text = re.sub(r"[^\w\s-]", "", text)
    text = re.sub(r"[\s_-]+", "-", text)

    # Remove leading/trailing hyphens
    text = text.strip("-")

    # Truncate if too long
    if len(text) > max_length:
        text = text[:max_length].rstrip("-")

    return text


def is_valid_uuid(uuid_string: str) -> bool:
    """Check if string is a valid UUID.

    Args:
        uuid_string: String to check

    Returns:
        True if valid UUID, False otherwise
    """
    try:
        UUID(uuid_string)
        return True
    except ValueError:
        return False


def get_current_timestamp() -> datetime:
    """Get current UTC timestamp.

    Returns:
        Current UTC datetime
    """
    return datetime.now(timezone.utc)


def parse_datetime(date_string: str) -> datetime | None:
    """Parse datetime string with multiple format support.

    Args:
        date_string: Date string to parse

    Returns:
        Parsed datetime or None if invalid
    """
    formats = [
        "%Y-%m-%d %H:%M:%S",
        "%Y-%m-%dT%H:%M:%S",
        "%Y-%m-%dT%H:%M:%SZ",
        "%Y-%m-%dT%H:%M:%S.%f",
        "%Y-%m-%dT%H:%M:%S.%fZ",
        "%Y-%m-%d",
    ]

    for fmt in formats:
        try:
            return datetime.strptime(date_string, fmt)
        except ValueError:
            continue

    return None


def safe_json_loads(json_string: str, default: Any = None) -> Any:
    """Safely parse JSON string.

    Args:
        json_string: JSON string to parse
        default: Default value if parsing fails

    Returns:
        Parsed JSON or default value
    """
    try:
        return json.loads(json_string)
    except (json.JSONDecodeError, TypeError):
        return default


def safe_json_dumps(data: Any, default: str = "{}") -> str:
    """Safely serialize data to JSON string.

    Args:
        data: Data to serialize
        default: Default value if serialization fails

    Returns:
        JSON string or default value
    """
    try:
        return json.dumps(data, default=str)
    except (TypeError, ValueError):
        return default
