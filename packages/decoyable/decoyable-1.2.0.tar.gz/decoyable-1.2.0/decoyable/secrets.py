"""
decoyable.secrets - Simple secret management utilities

This module provides basic utilities for loading and managing secrets
from environment variables and other sources.
"""

import os
from typing import Optional


def load_secret(name: str, default: Optional[str] = None, fallback: Optional[str] = None) -> Optional[str]:
    """
    Load a secret from environment variables.

    Args:
        name: The name of the environment variable
        default: Default value if not found
        fallback: Alternative variable name to try

    Returns:
        The secret value or default
    """
    value = os.getenv(name)
    if value is not None:
        return value

    if fallback:
        value = os.getenv(fallback)
        if value is not None:
            return value

    return default


def load(name: str, default: Optional[str] = None) -> Optional[str]:
    """
    Alias for load_secret for compatibility.
    """
    return load_secret(name, default)


def redact_secret(secret: str, visible_chars: int = 4) -> str:
    """
    Redact a secret by showing only the first few characters.

    Args:
        secret: The secret to redact
        visible_chars: Number of characters to show at the end

    Returns:
        Redacted secret string
    """
    if not secret or len(secret) <= visible_chars:
        return "*" * len(secret)

    return "*" * (len(secret) - visible_chars) + secret[-visible_chars:]


def mask_secret(secret: str) -> str:
    """
    Alias for redact_secret for compatibility.
    """
    return redact_secret(secret)


def looks_like_secret(value: str) -> bool:
    """
    Check if a string looks like it might be a secret.

    This uses heuristics to detect common secret patterns.
    """
    if not value or len(value) < 8:
        return False

    # Check for patterns that look like secrets
    # AWS access keys (AKIA...)
    if value.startswith("AKIA") and len(value) >= 16:
        return True

    # JWT tokens (header.payload.signature)
    if "." in value and len(value.split(".")) == 3:
        parts = value.split(".")
        if all(len(part) > 10 for part in parts):  # rough check for JWT structure
            return True

    # Long hex strings (API keys, hashes)
    if len(value) >= 32 and all(c in "0123456789abcdefABCDEF" for c in value):
        return True

    # Base64-like strings (long, with typical base64 chars)
    if len(value) >= 20 and "=" in value[-3:]:
        base64_chars = set("ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789+/=")
        if all(c in base64_chars for c in value):
            return True

    # Tokens with dots or underscores (must have multiple separators or be longer)
    if any(sep in value for sep in [".", "_", "-"]) and len(value) >= 15:
        return True

    # Check for keyword indicators in longer strings (avoid false positives on short words)
    if len(value) >= 12:
        secret_indicators = [
            "key", "token", "secret", "auth", "api", "credential", "private", "bearer"
        ]
        value_lower = value.lower()
        if any(indicator in value_lower for indicator in secret_indicators):
            return True

    return False


def is_secret(value: str) -> bool:
    """
    Alias for looks_like_secret for compatibility.
    """
    return looks_like_secret(value)