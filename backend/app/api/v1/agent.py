"""
Agent API endpoints for LLM interactions.
"""
from typing import Any, Dict

from app.core.security.limiter import limiter
from app.dependencies import CurrentUserDep
from app.schemas.agent import (AgentResponse, ConversationRequest,
                               PromptRequest, PromptResponse)
from app.services.agent import agent_service
from app.utils.sanitize import validate_model_name
from fastapi import APIRouter, HTTPException, Request, status

# Import direct agent functions
from app.core.agents import conduct_research
from app.core.langgraph.example_graph_agent import process_with_workflow
from app.core.llm_factory import get_available_models

router = APIRouter(prefix="/agent", tags=["agent"])


@router.post("/prompt", response_model=PromptResponse)
@limiter.limit("30/minute")
async def process_prompt(
    request: Request,
    prompt_request: PromptRequest,
    current_user: CurrentUserDep,
) -> PromptResponse:
    """
    Process a single prompt request with the AI agent.

    - **message**: The user's message/prompt
    - **model**: Optional model to use (defaults to configured model)
    - **temperature**: Optional temperature setting (0.0 to 2.0)
    - **max_tokens**: Optional maximum tokens for response
    - **system_prompt**: Optional custom system prompt
    - **context**: Optional additional context

    Requires authentication. Returns the AI response with metadata.
    """
    # Validate model name if provided
    if prompt_request.model and not validate_model_name(prompt_request.model):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid model name"
        )

    try:
        response = await agent_service.process_prompt(prompt_request)
        return response
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error processing prompt: {str(e)}",
        )


@router.post("/conversation", response_model=AgentResponse)
@limiter.limit("20/minute")
async def process_conversation(
    request: Request,
    conversation_request: ConversationRequest,
    current_user: CurrentUserDep,
) -> AgentResponse:
    """
    Process a conversation with multiple messages.

    - **messages**: List of conversation messages with roles (user/assistant/system)
    - **model**: Optional model to use
    - **temperature**: Optional temperature setting
    - **max_tokens**: Optional maximum tokens for response

    Requires authentication. Returns comprehensive response with metadata.
    """
    # Validate model name if provided
    if conversation_request.model and not validate_model_name(
        conversation_request.model
    ):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid model name"
        )

    # Validate messages
    if not conversation_request.messages:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="At least one message is required",
        )

    try:
        response = await agent_service.process_conversation(conversation_request)
        return response
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error processing conversation: {str(e)}",
        )


@router.post("/research")
@limiter.limit("10/minute")
async def research_topic(
    request: Request,
    topic: str,
    model: str = None,
    current_user: CurrentUserDep = None,
) -> Dict[str, Any]:
    """
    Research a topic using the specialized research agent.
    
    Example of using core agents directly.
    
    - **topic**: Topic to research
    - **model**: Optional model override
    
    Returns research results.
    """
    try:
        result = await conduct_research(topic, model)
        return {"topic": topic, "research": result, "model": model}
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Research failed: {str(e)}",
        )


@router.post("/workflow")
@limiter.limit("5/minute")
async def process_workflow(
    request: Request,
    text: str,
    model: str = None,
    current_user: CurrentUserDep = None,
) -> Dict[str, Any]:
    """
    Process text using the example workflow agent.
    
    Example of using LangGraph-style agents directly.
    
    - **text**: Text to process
    - **model**: Optional model override
    
    Returns workflow results with analysis and summary.
    """
    try:
        result = await process_with_workflow(text, model)
        return result
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Workflow failed: {str(e)}",
        )


@router.get("/health")
async def agent_health() -> Dict[str, Any]:
    """
    Check agent service health.

    Returns basic health information about the agent service.
    """
    return {
        "status": "healthy",
        "service": "agent",
        "available_models": get_available_models(),
    }
