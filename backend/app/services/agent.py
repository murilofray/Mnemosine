"""
Agent service - simplified delegation to core agents.
"""

from app.schemas.agent import PromptRequest, PromptResponse, ConversationRequest, AgentResponse
from app.core.agents.simple_agent import process_simple_prompt, process_simple_conversation


class AgentService:
    """Simplified service that delegates to core agents."""

    async def process_prompt(self, request: PromptRequest) -> PromptResponse:
        """
        Process a single prompt request.
        
        Args:
            request: Prompt request
            
        Returns:
            Prompt response
        """
        return await process_simple_prompt(request)

    async def process_conversation(self, request: ConversationRequest) -> AgentResponse:
        """
        Process a conversation request.
        
        Args:
            request: Conversation request
            
        Returns:
            Agent response
        """
        return await process_simple_conversation(request)


# Global agent service instance
agent_service = AgentService()
