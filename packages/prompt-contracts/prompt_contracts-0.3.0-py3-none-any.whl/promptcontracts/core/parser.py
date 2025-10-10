"""
Parsing utilities for extracting structured data from LLM outputs.

Provides json_loose() for fault-tolerant JSON extraction and
regex_extract() for pattern-based extraction.
"""

import json
import re
from typing import Any


class ParseError(Exception):
    """Raised when parsing fails."""

    pass


def json_loose(text: str) -> Any:
    """
    Extract JSON from text with fault-tolerant parsing.

    Attempts multiple strategies:
    1. Direct JSON parsing
    2. Extract JSON from markdown code fences
    3. Find first {...} or [...] block
    4. Strip common prefixes/suffixes

    Args:
        text: Text potentially containing JSON

    Returns:
        Parsed JSON object

    Raises:
        ParseError: If no valid JSON can be extracted
    """
    # Strategy 1: Try direct parse
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        pass

    # Strategy 2: Extract from markdown code fences
    fence_pattern = r"```(?:json)?\s*\n(.*?)\n```"
    fence_matches = re.findall(fence_pattern, text, re.DOTALL | re.IGNORECASE)
    for match in fence_matches:
        try:
            return json.loads(match.strip())
        except json.JSONDecodeError:
            continue

    # Strategy 3: Find first {...} or [...] block
    # Try to find balanced braces/brackets
    for start_char, end_char in [("{", "}"), ("[", "]")]:
        start_idx = text.find(start_char)
        if start_idx != -1:
            # Find matching closing brace
            depth = 0
            for i, char in enumerate(text[start_idx:], start=start_idx):
                if char == start_char:
                    depth += 1
                elif char == end_char:
                    depth -= 1
                    if depth == 0:
                        candidate = text[start_idx : i + 1]
                        try:
                            return json.loads(candidate)
                        except json.JSONDecodeError:
                            break

    # Strategy 4: Strip common prefixes/suffixes and retry
    stripped = text.strip()

    # Remove common prefixes
    prefixes = [
        "Here is the JSON:",
        "Here's the JSON:",
        "JSON:",
        "Response:",
        "Output:",
    ]
    for prefix in prefixes:
        if stripped.lower().startswith(prefix.lower()):
            stripped = stripped[len(prefix) :].strip()
            try:
                return json.loads(stripped)
            except json.JSONDecodeError:
                pass

    # If all strategies fail, raise error
    raise ParseError(f"Could not extract valid JSON from text: {text[:100]}...")


def regex_extract(
    text: str,
    pattern: str,
    group: int = 0,
    flags: int = 0,
) -> str | None:
    """
    Extract text using regex pattern.

    Args:
        text: Input text
        pattern: Regex pattern
        group: Capture group to extract (0 for full match)
        flags: Regex flags (e.g., re.IGNORECASE)

    Returns:
        Extracted text or None if no match
    """
    match = re.search(pattern, text, flags)
    if match:
        return match.group(group)
    return None


def regex_extract_all(
    text: str,
    pattern: str,
    group: int = 0,
    flags: int = 0,
) -> list[str]:
    """
    Extract all matches using regex pattern.

    Args:
        text: Input text
        pattern: Regex pattern
        group: Capture group to extract (0 for full match)
        flags: Regex flags

    Returns:
        List of extracted strings
    """
    matches = re.finditer(pattern, text, flags)
    return [m.group(group) for m in matches]


def extract_json_field(
    data: dict[str, Any] | list | Any,
    field_path: str,
    default: Any = None,
) -> Any:
    """
    Extract nested field from JSON using dot notation.

    Args:
        data: Parsed JSON data
        field_path: Dot-separated path (e.g., "user.name")
        default: Default value if field not found

    Returns:
        Field value or default

    Examples:
        >>> extract_json_field({"user": {"name": "Alice"}}, "user.name")
        'Alice'
        >>> extract_json_field({"items": [{"id": 1}]}, "items.0.id")
        1
    """
    if not field_path:
        return data

    parts = field_path.split(".")
    current = data

    for part in parts:
        if current is None:
            return default

        # Handle list indexing
        if isinstance(current, list):
            try:
                idx = int(part)
                current = current[idx]
            except (ValueError, IndexError):
                return default
        # Handle dict access
        elif isinstance(current, dict):
            current = current.get(part, default)
        else:
            return default

    return current


def normalize_whitespace(text: str) -> str:
    """
    Normalize whitespace in text.

    Args:
        text: Input text

    Returns:
        Text with normalized whitespace
    """
    # Replace multiple whitespace with single space
    text = re.sub(r"\s+", " ", text)
    # Trim
    return text.strip()


def strip_markdown_fences(text: str) -> str:
    """
    Remove markdown code fences from text.

    Args:
        text: Text potentially wrapped in code fences

    Returns:
        Text with fences removed
    """
    # Match ```language\n...\n``` or ```\n...\n```
    pattern = r"^```(?:\w+)?\s*\n(.*?)\n```\s*$"
    match = re.match(pattern, text.strip(), re.DOTALL)
    if match:
        return match.group(1)
    return text
