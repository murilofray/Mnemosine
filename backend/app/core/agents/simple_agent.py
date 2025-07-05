"""
Simple agent for general API usage.
Uses agent pooling for improved performance.
"""

from pydantic_ai import Agent
from app.core.llm_utils import convert_model_name, validate_api_key, get_default_model
from app.core.prompts import get_system_prompt
from app.core.agent_pool import get_pooled_agent
from app.core.cache_service import cache_service
from app.schemas.agent import PromptRequest, PromptResponse, ConversationRequest, AgentResponse
from app.utils.sanitize import sanitize_prompt
import time
import json


async def process_simple_prompt(request: PromptRequest) -> PromptResponse:
    """
    Process a simple prompt request using pooled agents and caching.
    """
    start_time = time.time()
    
    # Sanitize input
    sanitized_message = sanitize_prompt(request.message)
    model_name = request.model or "default"
    
    # Check cache first
    cached_response = await cache_service.get_prompt_response(
        sanitized_message, model_name
    )
    
    if cached_response:
        # Return cached response
        cached_data = json.loads(cached_response)
        processing_time = time.time() - start_time
        cached_data["processing_time"] = processing_time  # Update with actual time
        cached_data["cached"] = True
        return PromptResponse(**cached_data)
    
    # Get pooled agent (much faster than creating new one)
    agent = await get_pooled_agent(request.model)
    
    try:
        # Execute prompt
        result = await agent.run(sanitized_message)
        
        processing_time = time.time() - start_time
        tokens_used = 0
        
        if result.usage():
            tokens_used = result.usage().total_tokens or 0
            
        response = PromptResponse(
            response=result.output,
            model_used=model_name,
            tokens_used=tokens_used,
            processing_time=processing_time,
            conversation_id=None,
        )
        
        # Cache the response for future use
        await cache_service.cache_prompt_response(
            sanitized_message, model_name, response.model_dump_json()
        )
        
        return response
        
    except Exception as e:
        processing_time = time.time() - start_time
        raise Exception(f"Error processing prompt: {str(e)}")


async def process_simple_conversation(request: ConversationRequest) -> AgentResponse:
    """
    Process a conversation request using pooled agents.
    """
    start_time = time.time()
    
    # Get pooled agent (much faster than creating new one)
    agent = await get_pooled_agent(request.model)
    
    try:
        # Build conversation prompt (or use message_history when properly formatted)
        messages = []
        for msg in request.messages[:-1]:
            messages.append(f"{msg.role}: {sanitize_prompt(msg.content)}")
        
        current_prompt = sanitize_prompt(request.messages[-1].content)
        
        if messages:
            conversation_context = "\n".join(messages)
            full_prompt = f"Previous conversation:\n{conversation_context}\n\nCurrent message: {current_prompt}"
        else:
            full_prompt = current_prompt
        
        # Execute conversation
        result = await agent.run(full_prompt)
        
        processing_time = time.time() - start_time
        tokens_used = 0
        
        if result.usage():
            tokens_used = result.usage().total_tokens or 0
            
        return AgentResponse(
            response=result.output,
            model_used=request.model or "default",
            tokens_used=tokens_used,
            processing_time=processing_time,
            tool_calls=[],
            conversation_id=None,
            metadata={"message_count": len(request.messages)},
        )
        
    except Exception as e:
        processing_time = time.time() - start_time
        raise Exception(f"Error processing conversation: {str(e)}") 