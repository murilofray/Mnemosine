"""
Simple agent for general API usage.
Creates Agent directly with full Pydantic AI flexibility.
"""

from pydantic_ai import Agent
from app.core.llm_utils import convert_model_name, validate_api_key, get_default_model
from app.core.prompts import get_system_prompt
from app.schemas.agent import PromptRequest, PromptResponse, ConversationRequest, AgentResponse
from app.utils.sanitize import sanitize_prompt
import time


async def process_simple_prompt(request: PromptRequest) -> PromptResponse:
    """
    Process a simple prompt request.
    Creates Agent directly with needed configuration.
    """
    start_time = time.time()
    
    # Sanitize input
    sanitized_message = sanitize_prompt(request.message)
    
    # Get model name
    model = convert_model_name(request.model) if request.model else get_default_model()
    validate_api_key(model)
    
    # Create agent directly with full Pydantic AI configuration
    agent = Agent(
        model,
        system_prompt=get_system_prompt(),
        # Add any other Pydantic AI configs you need here
        # retries=3,
        # deps_type=SomeDep,
        # output_type=SomeModel,
        # tools=[some_tool],
    )
    
    try:
        # Execute prompt
        result = await agent.run(sanitized_message)
        
        processing_time = time.time() - start_time
        tokens_used = 0
        
        if result.usage():
            tokens_used = result.usage().total_tokens or 0
            
        return PromptResponse(
            response=result.output,
            model_used=request.model or "default",
            tokens_used=tokens_used,
            processing_time=processing_time,
            conversation_id=None,
        )
        
    except Exception as e:
        processing_time = time.time() - start_time
        raise Exception(f"Error processing prompt: {str(e)}")


async def process_simple_conversation(request: ConversationRequest) -> AgentResponse:
    """
    Process a conversation request.
    Creates Agent directly with conversation handling.
    """
    start_time = time.time()
    
    # Get model name  
    model = convert_model_name(request.model) if request.model else get_default_model()
    validate_api_key(model)
    
    # Create agent with full configuration flexibility
    agent = Agent(
        model,
        system_prompt=get_system_prompt(),
        # Configure as needed for conversations
        # retries=2,
        # deps_type=ConversationDeps,
    )
    
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