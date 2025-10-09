"""Check: JSON validity."""

import json
from typing import Any


def json_valid_check(
    response_text: str, check_spec: dict[str, Any], **kwargs
) -> tuple[bool, str, Any]:
    """
    Validate that response is parseable JSON.

    Returns:
        (passed, message, parsed_json or None)
    """
    try:
        parsed = json.loads(response_text)
        return True, "Response is valid JSON", parsed
    except json.JSONDecodeError as e:
        return False, f"Response is not valid JSON: {e}", None
