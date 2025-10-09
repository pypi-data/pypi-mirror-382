"""Hashing utilities for prompt fingerprinting."""

import hashlib


def compute_prompt_hash(text: str, algorithm: str = "sha256") -> str:
    """
    Compute a cryptographic hash of a prompt.

    Useful for tracking prompt versions and detecting changes.

    Args:
        text: The prompt text to hash
        algorithm: Hash algorithm (sha256, sha1, md5)

    Returns:
        Hex-encoded hash digest

    Example:
        >>> compute_prompt_hash("You are a helpful assistant")
        'a3f5e9...'
    """
    hasher = hashlib.new(algorithm)
    hasher.update(text.encode("utf-8"))
    return hasher.hexdigest()
