"""Check: Token budget (approximated by word count)."""

from typing import Any


def token_budget_check(
    response_text: str, check_spec: dict[str, Any], **kwargs
) -> tuple[bool, str, Any]:
    """
    Validate that response token count is within budget.

    MVP implementation: approximates tokens by word count.

    Args:
        response_text: Raw response text
        check_spec: Check configuration with 'max_out' integer

    Returns:
        (passed, message, approx_token_count)
    """
    max_tokens = check_spec.get("max_out", 0)

    # Approximate token count by splitting on whitespace
    approx_tokens = len(response_text.split())

    if approx_tokens <= max_tokens:
        return True, f"Token count ~{approx_tokens} <= {max_tokens}", approx_tokens
    else:
        return False, f"Token count ~{approx_tokens} > {max_tokens}", approx_tokens
