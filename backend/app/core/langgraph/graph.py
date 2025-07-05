"""
LangGraph workflow for agent orchestration.
"""

from typing import Any, Dict, List, TypedDict

from app.config.settings import settings
from app.core.langgraph.tools import get_available_tools
from langgraph.graph import END, START, Graph
from langgraph.prebuilt import create_react_agent


class AgentState(TypedDict):
    """State structure for the agent workflow."""

    input: str
    output: str
    messages: List[Dict[str, Any]]
    tools_used: List[str]
    metadata: Dict[str, Any]


def create_agent_graph() -> Graph:
    """
    Create and configure the LangGraph agent workflow.

    Returns:
        Configured LangGraph workflow
    """

    def process_input(state: AgentState) -> AgentState:
        """Process and validate input."""
        from app.utils.sanitize import sanitize_prompt

        sanitized_input = sanitize_prompt(state["input"])

        return {
            **state,
            "input": sanitized_input,
            "messages": [{"role": "user", "content": sanitized_input}],
            "metadata": {"processed": True},
        }

    def execute_agent(state: AgentState) -> AgentState:
        """Execute the main agent logic."""
        # This is a simplified version - in practice, you'd integrate
        # with your chosen LLM and tools

        tools = get_available_tools()

        # Simulate agent execution
        response = f"Processed: {state['input']}"

        return {
            **state,
            "output": response,
            "messages": state["messages"]
            + [{"role": "assistant", "content": response}],
            "tools_used": list(tools.keys()) if tools else [],
        }

    def format_output(state: AgentState) -> AgentState:
        """Format the final output."""
        formatted_output = {
            "response": state["output"],
            "conversation": state["messages"],
            "tools_used": state["tools_used"],
            "metadata": state["metadata"],
        }

        return {**state, "output": formatted_output}

    # Create the graph
    workflow = Graph()

    # Add nodes
    workflow.add_node("process_input", process_input)
    workflow.add_node("execute_agent", execute_agent)
    workflow.add_node("format_output", format_output)

    # Add edges
    workflow.add_edge(START, "process_input")
    workflow.add_edge("process_input", "execute_agent")
    workflow.add_edge("execute_agent", "format_output")
    workflow.add_edge("format_output", END)

    return workflow.compile()


def create_conversation_graph() -> Graph:
    """
    Create a conversation-aware agent workflow.

    Returns:
        Configured conversation workflow
    """

    def process_conversation(state: AgentState) -> AgentState:
        """Process conversation context."""
        messages = state.get("messages", [])

        # Build conversation context
        context = "\n".join([f"{msg['role']}: {msg['content']}" for msg in messages])

        return {
            **state,
            "input": context,
            "metadata": {
                **state.get("metadata", {}),
                "conversation_length": len(messages),
            },
        }

    def respond_in_context(state: AgentState) -> AgentState:
        """Generate response considering conversation context."""
        # Simplified implementation
        conversation_length = state.get("metadata", {}).get("conversation_length", 0)

        response = f"Response considering {conversation_length} previous messages"

        return {**state, "output": response}

    # Create conversation workflow
    workflow = Graph()

    workflow.add_node("process_conversation", process_conversation)
    workflow.add_node("respond_in_context", respond_in_context)
    workflow.add_node("format_output", format_output)  # Reuse from above

    workflow.add_edge(START, "process_conversation")
    workflow.add_edge("process_conversation", "respond_in_context")
    workflow.add_edge("respond_in_context", "format_output")
    workflow.add_edge("format_output", END)

    return workflow.compile()


# Global graph instances
agent_graph = create_agent_graph()
conversation_graph = create_conversation_graph()
