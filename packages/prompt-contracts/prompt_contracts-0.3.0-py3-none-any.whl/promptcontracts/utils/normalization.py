"""Output normalization utilities for auto-repair."""

import json
import re
from typing import Any


def strip_code_fences(text: str) -> tuple[str, bool]:
    """
    Remove Markdown code fences from text.

    Handles patterns like:
    - ```json\n{...}\n```
    - ```\n{...}\n```

    Args:
        text: Raw text potentially containing code fences

    Returns:
        Tuple of (cleaned_text, was_stripped)
    """
    original = text.strip()

    # Pattern: ```json or ``` at start, ``` at end
    fence_pattern = re.compile(r"^```(?:json)?\s*\n(.*)\n```$", re.DOTALL)
    match = fence_pattern.match(original)

    if match:
        return match.group(1).strip(), True

    return original, False


def lowercase_jsonpath_fields(json_text: str, paths: list[str]) -> tuple[str, list[str]]:
    """
    Lowercase specific JSONPath fields in a JSON string.

    Currently supports only simple top-level paths like "$.field".

    Args:
        json_text: JSON string
        paths: List of JSONPath expressions (e.g., ["$.priority", "$.status"])

    Returns:
        Tuple of (modified_json_text, list_of_modified_paths)
    """
    if not paths:
        return json_text, []

    try:
        data = json.loads(json_text)
    except json.JSONDecodeError:
        # Can't parse, return unchanged
        return json_text, []

    modified_paths = []

    for path in paths:
        # Simple top-level support: "$.field" or "field"
        if path.startswith("$."):
            field = path[2:]
        else:
            field = path

        if field in data and isinstance(data[field], str):
            original_value = data[field]
            data[field] = original_value.lower()
            if original_value != data[field]:
                modified_paths.append(path)

    return json.dumps(data, ensure_ascii=False), modified_paths


def normalize_output(
    raw_text: str, auto_repair_config: dict[str, Any]
) -> tuple[str, dict[str, Any]]:
    """
    Apply all auto-repair transformations.

    Args:
        raw_text: Raw LLM output
        auto_repair_config: Dict with keys:
            - strip_markdown_fences: bool (default True)
            - lowercase_fields: List[str] (JSONPath expressions)

    Returns:
        Tuple of (normalized_text, repair_details)

    repair_details contains:
        - stripped_fences: bool
        - lowercased_fields: List[str]
    """
    normalized = raw_text
    details = {"stripped_fences": False, "lowercased_fields": []}

    # Step 1: Strip code fences
    if auto_repair_config.get("strip_markdown_fences", True):
        normalized, stripped = strip_code_fences(normalized)
        details["stripped_fences"] = stripped

    # Step 2: Lowercase fields
    lowercase_fields = auto_repair_config.get("lowercase_fields", [])
    if lowercase_fields:
        normalized, lowered = lowercase_jsonpath_fields(normalized, lowercase_fields)
        details["lowercased_fields"] = lowered

    return normalized, details
