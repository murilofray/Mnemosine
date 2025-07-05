"""
LLM utilities - simple helpers without factory pattern.
"""

from app.config.settings import settings


def convert_model_name(model: str) -> str:
    """
    Convert model name to Pydantic AI format.
    
    Args:
        model: Model name (e.g., "gpt-4o", "gemini-2.0-flash")
        
    Returns:
        Pydantic AI formatted model name
    """
    # If already in correct format, return as is
    if ":" in model:
        return model
        
    # Convert based on model name patterns
    if model.startswith("gemini"):
        return f"google-gla:{model}"
    elif model.startswith("gpt") or model.startswith("o1"):
        return f"openai:{model}"
    elif model.startswith("claude"):
        return f"anthropic:{model}"
    else:
        # Default to settings provider
        if settings.DEFAULT_PROVIDER == "gemini":
            return f"google-gla:{model}"
        elif settings.DEFAULT_PROVIDER == "openai":
            return f"openai:{model}"
        else:
            return f"openai:{model}"  # Ultimate fallback


def validate_api_key(model: str) -> None:
    """
    Validate that required API key is available for the model.
    
    Args:
        model: Pydantic AI formatted model name
        
    Raises:
        ValueError: If API key is missing
    """
    if model.startswith("google-gla:"):
        if not settings.GEMINI_API_KEY:
            raise ValueError("Gemini API key not configured")
    elif model.startswith("openai:"):
        if not settings.OPENAI_API_KEY:
            raise ValueError("OpenAI API key not configured")
    elif model.startswith("anthropic:"):
        if not settings.ANTHROPIC_API_KEY:
            raise ValueError("Anthropic API key not configured")
    else:
        raise ValueError(f"Unsupported model format: {model}")


def get_available_models() -> dict[str, bool]:
    """
    Get list of available models based on configured API keys.
    
    Returns:
        Dict with model providers and their availability
    """
    return {
        "openai": bool(settings.OPENAI_API_KEY),
        "gemini": bool(settings.GEMINI_API_KEY),
        "anthropic": bool(settings.ANTHROPIC_API_KEY),
    }


def get_default_model() -> str:
    """
    Get the default model in Pydantic AI format.
    
    Returns:
        Default model name
    """
    base_model = settings.DEFAULT_MODEL
    
    if settings.DEFAULT_PROVIDER == "gemini" and settings.GEMINI_API_KEY:
        return f"google-gla:{base_model}"
    elif settings.DEFAULT_PROVIDER == "openai" and settings.OPENAI_API_KEY:
        return f"openai:{base_model}"
    elif settings.OPENAI_API_KEY:
        return f"openai:{base_model}"
    elif settings.GEMINI_API_KEY:
        return f"google-gla:{base_model}"
    else:
        raise ValueError("No LLM API key configured") 