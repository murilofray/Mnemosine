"""
Agent pooling system for performance optimization.
Reuses AI agents instead of creating new ones for each request.
"""

import asyncio
import time
from typing import Dict, Optional, Any
from pydantic_ai import Agent
from app.core.llm_utils import convert_model_name, validate_api_key
from app.core.prompts import get_system_prompt
from app.config.settings import settings


class AgentPool:
    """Pool of reusable AI agents to improve performance."""
    
    def __init__(self, pool_size: int = 10):
        self.pool_size = pool_size
        self.agents: Dict[str, Agent] = {}
        self.agent_usage: Dict[str, int] = {}
        self.agent_last_used: Dict[str, float] = {}
        self.lock = asyncio.Lock()
        
    async def get_agent(self, model: Optional[str] = None) -> Agent:
        """
        Get an agent from the pool, creating if necessary.
        
        Args:
            model: Model name to use
            
        Returns:
            Reusable Agent instance
        """
        # Convert and validate model
        model_name = convert_model_name(model) if model else settings.DEFAULT_MODEL
        if ":" not in model_name:
            model_name = convert_model_name(model_name)
        
        validate_api_key(model_name)
        
        agent_key = f"agent_{model_name}"
        
        async with self.lock:
            # Return existing agent if available
            if agent_key in self.agents:
                self.agent_usage[agent_key] += 1
                self.agent_last_used[agent_key] = time.time()
                return self.agents[agent_key]
            
            # Create new agent if pool not full
            if len(self.agents) < self.pool_size:
                agent = Agent(
                    model_name,
                    system_prompt=get_system_prompt(),
                )
                
                self.agents[agent_key] = agent
                self.agent_usage[agent_key] = 1
                self.agent_last_used[agent_key] = time.time()
                return agent
            
            # Pool is full, evict least recently used agent
            lru_key = min(self.agent_last_used.keys(), key=lambda k: self.agent_last_used[k])
            del self.agents[lru_key]
            del self.agent_usage[lru_key]
            del self.agent_last_used[lru_key]
            
            # Create new agent
            agent = Agent(
                model_name,
                system_prompt=get_system_prompt(),
            )
            
            self.agents[agent_key] = agent
            self.agent_usage[agent_key] = 1
            self.agent_last_used[agent_key] = time.time()
            return agent
    
    async def cleanup_unused_agents(self, max_idle_time: int = 3600):
        """
        Clean up agents that haven't been used for a while.
        
        Args:
            max_idle_time: Maximum idle time in seconds
        """
        current_time = time.time()
        
        async with self.lock:
            expired_keys = [
                key for key, last_used in self.agent_last_used.items()
                if current_time - last_used > max_idle_time
            ]
            
            for key in expired_keys:
                del self.agents[key]
                del self.agent_usage[key]
                del self.agent_last_used[key]
    
    def get_stats(self) -> Dict[str, Any]:
        """Get pool statistics."""
        return {
            "pool_size": len(self.agents),
            "max_pool_size": self.pool_size,
            "agents": list(self.agents.keys()),
            "usage_stats": self.agent_usage.copy(),
            "last_used": {k: time.time() - v for k, v in self.agent_last_used.items()},
        }


# Global agent pool instance
agent_pool = AgentPool(pool_size=settings.AGENT_POOL_SIZE if hasattr(settings, 'AGENT_POOL_SIZE') else 10)


async def get_pooled_agent(model: Optional[str] = None) -> Agent:
    """
    Get an agent from the global pool.
    
    Args:
        model: Model name to use
        
    Returns:
        Reusable Agent instance
    """
    return await agent_pool.get_agent(model)