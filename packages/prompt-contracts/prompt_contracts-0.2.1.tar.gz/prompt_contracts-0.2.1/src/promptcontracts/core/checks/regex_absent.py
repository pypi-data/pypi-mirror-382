"""Check: Regex pattern absence."""

import re
from typing import Any


def regex_absent_check(
    response_text: str, check_spec: dict[str, Any], **kwargs
) -> tuple[bool, str, Any]:
    """
    Validate that a regex pattern is NOT present in the response.

    Args:
        response_text: Raw response text
        check_spec: Check configuration with 'pattern' string

    Returns:
        (passed, message, None)
    """
    pattern = check_spec.get("pattern", "")

    if not pattern:
        return True, "No pattern specified", None

    try:
        if re.search(pattern, response_text):
            return False, f"Forbidden pattern '{pattern}' found in response", None
        else:
            return True, f"Pattern '{pattern}' not found (as expected)", None
    except re.error as e:
        return False, f"Invalid regex pattern '{pattern}': {e}", None
