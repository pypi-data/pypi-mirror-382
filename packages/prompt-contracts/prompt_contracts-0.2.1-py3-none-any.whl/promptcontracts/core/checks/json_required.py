"""Check: Required JSON fields."""

from typing import Any


def json_required_check(
    response_text: str, check_spec: dict[str, Any], parsed_json: Any = None, **kwargs
) -> tuple[bool, str, Any]:
    """
    Validate that all required fields are present in JSON response.

    Args:
        response_text: Raw response text
        check_spec: Check configuration with 'fields' array
        parsed_json: Pre-parsed JSON object (if available)

    Returns:
        (passed, message, None)
    """
    required_fields = check_spec.get("fields", [])

    if parsed_json is None:
        return False, "Cannot check required fields: response is not valid JSON", None

    if not isinstance(parsed_json, dict):
        return False, f"Expected JSON object, got {type(parsed_json).__name__}", None

    missing = [f for f in required_fields if f not in parsed_json]

    if not missing:
        return True, f"All required fields present: {required_fields}", None
    else:
        return False, f"Missing required fields: {missing}", None
