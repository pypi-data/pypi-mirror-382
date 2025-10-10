"""
Semantic checks for prompt contracts.

Provides contains_all, contains_any, regex_present, and similarity checks
for more flexible validation beyond exact matching.
"""

import re
from typing import Any


def contains_all_check(
    response_text: str, check_spec: dict[str, Any], **kwargs
) -> tuple[bool, str]:
    """
    Check that response contains all required substrings.

    Args:
        response_text: Response text to check
        check_spec: Check specification with 'required' list and optional 'case_sensitive'
        **kwargs: Additional arguments

    Returns:
        Tuple of (passed, message)
    """
    required = check_spec.get("required", [])
    case_sensitive = check_spec.get("case_sensitive", True)

    if not isinstance(required, list):
        return False, f"'required' must be a list, got {type(required)}"

    text_to_check = response_text if case_sensitive else response_text.lower()
    missing = []

    for item in required:
        item_str = str(item)
        search_str = item_str if case_sensitive else item_str.lower()
        if search_str not in text_to_check:
            missing.append(item_str)

    if missing:
        return False, f"Missing required strings: {missing}"

    return True, f"All {len(required)} required strings present"


def contains_any_check(
    response_text: str, check_spec: dict[str, Any], **kwargs
) -> tuple[bool, str]:
    """
    Check that response contains at least one of the required substrings.

    Args:
        response_text: Response text to check
        check_spec: Check specification with 'options' list and optional 'case_sensitive'
        **kwargs: Additional arguments

    Returns:
        Tuple of (passed, message)
    """
    options = check_spec.get("options", [])
    case_sensitive = check_spec.get("case_sensitive", True)

    if not isinstance(options, list):
        return False, f"'options' must be a list, got {type(options)}"

    if not options:
        return False, "No options specified"

    text_to_check = response_text if case_sensitive else response_text.lower()

    for option in options:
        option_str = str(option)
        search_str = option_str if case_sensitive else option_str.lower()
        if search_str in text_to_check:
            return True, f"Found option: '{option_str}'"

    return False, f"None of the {len(options)} options found in response"


def regex_present_check(
    response_text: str, check_spec: dict[str, Any], **kwargs
) -> tuple[bool, str]:
    """
    Check that response matches a regex pattern.

    Args:
        response_text: Response text to check
        check_spec: Check specification with 'pattern' and optional 'flags'
        **kwargs: Additional arguments

    Returns:
        Tuple of (passed, message)
    """
    pattern = check_spec.get("pattern")
    if not pattern:
        return False, "No pattern specified"

    flags_str = check_spec.get("flags", "")
    flags = 0
    if "i" in flags_str.lower():
        flags |= re.IGNORECASE
    if "m" in flags_str.lower():
        flags |= re.MULTILINE
    if "s" in flags_str.lower():
        flags |= re.DOTALL

    try:
        match = re.search(pattern, response_text, flags)
        if match:
            matched_text = match.group(0)
            preview = matched_text[:50] + "..." if len(matched_text) > 50 else matched_text
            return True, f"Pattern matched: '{preview}'"
        else:
            return False, f"Pattern not found: {pattern}"
    except re.error as e:
        return False, f"Invalid regex pattern: {e}"


def similarity_check(response_text: str, check_spec: dict[str, Any], **kwargs) -> tuple[bool, str]:
    """
    Check semantic similarity using embeddings.

    Args:
        response_text: Response text to check
        check_spec: Check specification with 'reference' and 'threshold'
        **kwargs: Must include 'embedding_adapter'

    Returns:
        Tuple of (passed, message)
    """
    reference = check_spec.get("reference")
    threshold = check_spec.get("threshold", 0.7)
    embedding_adapter = kwargs.get("embedding_adapter")

    if not reference:
        return False, "No reference text specified"

    if not embedding_adapter:
        return (
            False,
            "Similarity check requires embedding_adapter in kwargs",
        )

    try:
        # Get embeddings
        response_emb = embedding_adapter.embed(response_text)
        reference_emb = embedding_adapter.embed(reference)

        # Compute cosine similarity
        similarity = _cosine_similarity(response_emb, reference_emb)

        if similarity >= threshold:
            return (
                True,
                f"Similarity {similarity:.3f} >= threshold {threshold}",
            )
        else:
            return (
                False,
                f"Similarity {similarity:.3f} < threshold {threshold}",
            )

    except Exception as e:
        return False, f"Similarity computation failed: {e}"


def _cosine_similarity(vec1: list[float], vec2: list[float]) -> float:
    """Compute cosine similarity between two vectors."""
    if len(vec1) != len(vec2):
        raise ValueError("Vectors must have same length")

    dot_product = sum(a * b for a, b in zip(vec1, vec2, strict=False))
    norm1 = sum(a * a for a in vec1) ** 0.5
    norm2 = sum(b * b for b in vec2) ** 0.5

    if norm1 == 0 or norm2 == 0:
        return 0.0

    return dot_product / (norm1 * norm2)
