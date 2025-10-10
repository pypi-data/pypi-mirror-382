"""Timestamp utilities for consistent datetime handling."""

from datetime import datetime, timezone


def get_iso_timestamp() -> str:
    """
    Get current UTC timestamp in ISO 8601 format.

    Returns:
        ISO 8601 formatted timestamp string (e.g., "2025-10-08T14:30:00.123456Z")

    Example:
        >>> get_iso_timestamp()
        '2025-10-08T14:30:00.123456Z'
    """
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")


def get_unix_timestamp() -> float:
    """
    Get current UTC timestamp as Unix epoch time.

    Returns:
        Unix timestamp (seconds since epoch)
    """
    return datetime.now(timezone.utc).timestamp()
