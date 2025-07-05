"""
Input sanitization utilities to prevent prompt injection and other security issues.
"""

import re


def sanitize_prompt(text: str) -> str:
    """
    Sanitize user input to prevent prompt injection attacks.

    Args:
        text: The input text to sanitize

    Returns:
        Sanitized text
    """
    if not text:
        return ""

    # Remove potential prompt injection patterns
    # Remove excessive whitespace and control characters
    text = re.sub(r"\s+", " ", text)
    text = re.sub(r"[\x00-\x1f\x7f-\x9f]", "", text)

    # Remove potential injection patterns
    injection_patterns = [
        r"```[\s\S]*?```",  # Code blocks
        r"<[^>]*>",  # HTML tags
        r"\[INST\]",  # Instruction tags
        r"\[/INST\]",  # Instruction end tags
        r"<\|.*?\|>",  # Special tokens
        r"\{.*?\}",  # Template variables (basic)
    ]

    for pattern in injection_patterns:
        text = re.sub(pattern, "", text, flags=re.IGNORECASE)

    # Limit length
    max_length = 10000
    if len(text) > max_length:
        text = text[:max_length] + "..."

    return text.strip()


def sanitize_filename(filename: str) -> str:
    """
    Sanitize filename to prevent directory traversal.

    Args:
        filename: The filename to sanitize

    Returns:
        Sanitized filename
    """
    if not filename:
        return "untitled"

    # Remove path separators and dangerous characters
    dangerous_chars = ["/", "\\", "..", "<", ">", ":", '"', "|", "?", "*"]
    for char in dangerous_chars:
        filename = filename.replace(char, "_")

    # Remove leading/trailing whitespace and dots
    filename = filename.strip(" .")

    # Ensure it's not empty
    if not filename:
        filename = "untitled"

    # Limit length
    if len(filename) > 255:
        filename = filename[:255]

    return filename


def validate_model_name(model_name: str) -> bool:
    """
    Validate that the model name is safe to use.

    Args:
        model_name: The model name to validate

    Returns:
        True if valid, False otherwise
    """
    if not model_name:
        return False

    # Allow only alphanumeric, hyphens, underscores, and dots
    pattern = r"^[a-zA-Z0-9\-_.]+$"
    return bool(re.match(pattern, model_name)) and len(model_name) <= 100
