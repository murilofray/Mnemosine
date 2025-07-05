"""
LLM Factory for creating model instances.
Simple factory to initialize LLM models with given parameters.
"""

from typing import Optional
from pydantic_ai import Agent

from app.config.settings import settings


def create_llm_agent(
    model: Optional[str] = None,
    system_prompt: Optional[str] = None,
    **kwargs
) -> Agent:
    """
    Create a simple LLM agent with given parameters.
    
    Args:
        model: Model name (e.g., "gpt-4o", "gemini-2.0-flash")
        system_prompt: System prompt for the model
        **kwargs: Additional parameters for Agent initialization
    
    Returns:
        Configured Pydantic AI Agent
    
    Raises:
        ValueError: If model format is invalid or API key is missing
    """
    # Use default model if not provided
    selected_model = model or settings.DEFAULT_MODEL
    
    # Convert to Pydantic AI format
    pydantic_model = _convert_to_pydantic_format(selected_model)
    
    # Validate API key
    _validate_api_key(pydantic_model)
    
    # Create and return agent
    return Agent(
        pydantic_model,
        system_prompt=system_prompt,
        **kwargs
    )


def _convert_to_pydantic_format(model: str) -> str:
    """Convert model name to Pydantic AI format."""
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


def _validate_api_key(pydantic_model: str) -> None:
    """Validate that required API key is available."""
    if pydantic_model.startswith("google-gla:"):
        if not settings.GEMINI_API_KEY:
            raise ValueError("Gemini API key not configured")
    elif pydantic_model.startswith("openai:"):
        if not settings.OPENAI_API_KEY:
            raise ValueError("OpenAI API key not configured")
    elif pydantic_model.startswith("anthropic:"):
        if not settings.ANTHROPIC_API_KEY:
            raise ValueError("Anthropic API key not configured")
    else:
        raise ValueError(f"Unsupported model format: {pydantic_model}")


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