"""
Agent schemas for LLM prompt requests and responses.
"""

from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field


class PromptRequest(BaseModel):
    """Request schema for LLM prompts."""

    message: str = Field(..., min_length=1, max_length=10000)
    model: Optional[str] = None
    temperature: Optional[float] = Field(None, ge=0.0, le=2.0)
    max_tokens: Optional[int] = Field(None, ge=1, le=4000)
    system_prompt: Optional[str] = None
    context: Optional[Dict[str, Any]] = None


class PromptResponse(BaseModel):
    """Response schema for LLM prompts."""

    response: str
    model_used: str
    tokens_used: int
    processing_time: float
    conversation_id: Optional[str] = None


class ConversationMessage(BaseModel):
    """Individual message in a conversation."""

    role: str = Field(..., pattern="^(user|assistant|system)$")
    content: str
    timestamp: Optional[str] = None


class ConversationRequest(BaseModel):
    """Request schema for conversation-based prompts."""

    messages: List[ConversationMessage]
    model: Optional[str] = None
    temperature: Optional[float] = Field(None, ge=0.0, le=2.0)
    max_tokens: Optional[int] = Field(None, ge=1, le=4000)


class AgentToolCall(BaseModel):
    """Schema for agent tool calls."""

    tool_name: str
    parameters: Dict[str, Any]
    result: Optional[Any] = None


class AgentResponse(BaseModel):
    """Comprehensive agent response with tool calls."""

    response: str
    model_used: str
    tokens_used: int
    processing_time: float
    tool_calls: List[AgentToolCall] = []
    conversation_id: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None
