"""Utility functions for Observatory SDK."""

import hashlib
import json
import time
import uuid
from datetime import datetime
from typing import Any


def generate_id(prefix: str = "") -> str:
    """Generate a unique identifier.

    Args:
        prefix: Optional prefix for the ID

    Returns:
        Unique identifier string
    """
    unique_id = str(uuid.uuid4()).replace("-", "")
    return f"{prefix}_{unique_id}" if prefix else unique_id


def hash_string(value: str, algorithm: str = "sha256") -> str:
    """Hash a string value.

    Args:
        value: String to hash
        algorithm: Hash algorithm (sha256, md5, etc.)

    Returns:
        Hexadecimal hash string
    """
    hash_obj = hashlib.new(algorithm)
    hash_obj.update(value.encode("utf-8"))
    return hash_obj.hexdigest()


def get_message_size(data: Any) -> int:
    """Calculate size of a message in bytes.

    Args:
        data: Data to measure

    Returns:
        Size in bytes
    """
    try:
        return len(json.dumps(data).encode("utf-8"))
    except (TypeError, ValueError):
        return 0


def truncate_message(data: dict[str, Any], max_size: int) -> dict[str, Any]:
    """Truncate message to maximum size.

    Args:
        data: Message data
        max_size: Maximum size in bytes

    Returns:
        Truncated message data
    """
    serialized = json.dumps(data)
    if len(serialized) <= max_size:
        return data

    # Truncate and add indicator
    truncated = serialized[:max_size]
    try:
        result = json.loads(truncated)
        result["_truncated"] = True
        return result  # type: ignore[no-any-return]
    except json.JSONDecodeError:
        # If truncation broke JSON, return minimal info
        return {
            "_truncated": True,
            "_original_size": len(serialized),
            "_message": "Message too large and could not be truncated safely",
        }


def current_timestamp() -> datetime:
    """Get current UTC timestamp.

    Returns:
        Current datetime in UTC
    """
    from datetime import timezone

    return datetime.now(timezone.utc)


def calculate_duration_ns(start_time: float, end_time: float | None = None) -> int:
    """Calculate duration in nanoseconds.

    Args:
        start_time: Start time from time.time()
        end_time: End time from time.time() (defaults to now)

    Returns:
        Duration in nanoseconds
    """
    if end_time is None:
        end_time = time.time()
    return int((end_time - start_time) * 1_000_000_000)


def safe_get(data: dict[str, Any], *keys: str, default: Any = None) -> Any:
    """Safely get nested dictionary value.

    Args:
        data: Dictionary to search
        *keys: Keys to traverse
        default: Default value if not found

    Returns:
        Value or default
    """
    current = data
    for key in keys:
        if not isinstance(current, dict):
            return default
        current = current.get(key)  # type: ignore[assignment]
        if current is None:
            return default
    return current


def merge_dicts(*dicts: dict[str, Any]) -> dict[str, Any]:
    """Merge multiple dictionaries.

    Args:
        *dicts: Dictionaries to merge

    Returns:
        Merged dictionary
    """
    result = {}
    for d in dicts:
        if d:
            result.update(d)
    return result


def get_error_info(exception: Exception) -> dict[str, Any]:
    """Extract error information from exception.

    Args:
        exception: Exception object

    Returns:
        Dictionary with error details
    """
    return {
        "error_type": type(exception).__name__,
        "error_message": str(exception),
        "error_class": exception.__class__.__module__ + "." + exception.__class__.__name__,
    }
