"""
Tools for the LangGraph agent.
"""

from typing import Any, Callable, Dict, List

from pydantic import BaseModel, Field


class ToolDefinition(BaseModel):
    """Definition of an agent tool."""

    name: str
    description: str
    function: Callable[..., Any]
    parameters: Dict[str, Any] = {}


def search_tool(query: str) -> str:
    """
    Search tool for information retrieval.

    Args:
        query: The search query

    Returns:
        Search results (simulated)
    """
    # This is a placeholder - implement actual search functionality
    return f"Search results for: {query}"


def calculator_tool(expression: str) -> str:
    """
    Calculator tool for mathematical operations.

    Args:
        expression: Mathematical expression to evaluate

    Returns:
        Calculation result
    """
    try:
        # Basic safety check - only allow basic math operations
        allowed_chars = set("0123456789+-*/.()")
        if not all(c in allowed_chars or c.isspace() for c in expression):
            return "Error: Invalid characters in expression"

        # Evaluate safely
        result = eval(expression)
        return f"Result: {result}"
    except Exception as e:
        return f"Calculation error: {str(e)}"


def text_analyzer_tool(text: str) -> Dict[str, Any]:
    """
    Text analysis tool.

    Args:
        text: Text to analyze

    Returns:
        Analysis results
    """
    words = text.split()
    return {
        "word_count": len(words),
        "character_count": len(text),
        "sentence_count": text.count(".") + text.count("!") + text.count("?"),
        "average_word_length": (
            sum(len(word) for word in words) / len(words) if words else 0
        ),
    }


def code_formatter_tool(code: str, language: str = "python") -> str:
    """
    Code formatting tool.

    Args:
        code: Code to format
        language: Programming language

    Returns:
        Formatted code
    """
    # This is a placeholder - implement actual code formatting
    return f"Formatted {language} code:\n```{language}\n{code}\n```"


def get_available_tools() -> Dict[str, ToolDefinition]:
    """
    Get all available tools for the agent.

    Returns:
        Dictionary of available tools
    """
    tools = {
        "search": ToolDefinition(
            name="search",
            description="Search for information on a given topic",
            function=search_tool,
            parameters={"query": {"type": "string", "description": "The search query"}},
        ),
        "calculator": ToolDefinition(
            name="calculator",
            description="Perform mathematical calculations",
            function=calculator_tool,
            parameters={
                "expression": {
                    "type": "string",
                    "description": "Mathematical expression to evaluate",
                }
            },
        ),
        "text_analyzer": ToolDefinition(
            name="text_analyzer",
            description="Analyze text for word count, character count, etc.",
            function=text_analyzer_tool,
            parameters={"text": {"type": "string", "description": "Text to analyze"}},
        ),
        "code_formatter": ToolDefinition(
            name="code_formatter",
            description="Format code in various programming languages",
            function=code_formatter_tool,
            parameters={
                "code": {"type": "string", "description": "Code to format"},
                "language": {
                    "type": "string",
                    "description": "Programming language",
                    "default": "python",
                },
            },
        ),
    }

    return tools


def execute_tool(tool_name: str, **kwargs: Any) -> Any:
    """
    Execute a tool by name with given parameters.

    Args:
        tool_name: Name of the tool to execute
        **kwargs: Tool parameters

    Returns:
        Tool execution result
    """
    tools = get_available_tools()

    if tool_name not in tools:
        return f"Error: Tool '{tool_name}' not found"

    try:
        tool = tools[tool_name]
        return tool.function(**kwargs)
    except Exception as e:
        return f"Error executing tool '{tool_name}': {str(e)}"
