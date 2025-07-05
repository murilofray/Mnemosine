"""
Prompts module for managing system and user prompts.
"""

import os
from pathlib import Path
from typing import Any, Dict, Optional

from app.config.settings import settings
from jinja2 import Template


def get_system_prompt(context: Optional[Dict[str, Any]] = None) -> str:
    """
    Load and render the system prompt template.

    Args:
        context: Optional context variables for template rendering

    Returns:
        Rendered system prompt
    """
    try:
        # Get the system prompt file path
        prompt_file = Path(__file__).parent / "system.md"

        if not prompt_file.exists():
            return DEFAULT_SYSTEM_PROMPT

        # Read the template
        with open(prompt_file, "r", encoding="utf-8") as f:
            template_content = f.read()

        # Render with Jinja2
        template = Template(template_content)

        # Default context
        default_context = {
            "app_name": settings.APP_NAME,
            "version": settings.APP_VERSION,
        }

        if context:
            default_context.update(context)

        return template.render(**default_context)

    except Exception as e:
        # Fallback to default prompt if template loading fails
        return DEFAULT_SYSTEM_PROMPT


# Default system prompt as fallback
DEFAULT_SYSTEM_PROMPT = """
You are Mnemosine, an AI assistant designed to help users with various tasks.

How can I assist you today?
"""
