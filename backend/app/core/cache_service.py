"""
Caching service for performance optimization.
"""

import asyncio
import json
import hashlib
from typing import Optional, Any, Dict
from app.config.settings import settings


class MemoryCache:
    """In-memory cache implementation for when Redis is not available."""
    
    def __init__(self, default_ttl: int = 3600):
        self.cache: Dict[str, Dict[str, Any]] = {}
        self.default_ttl = default_ttl
        self.lock = asyncio.Lock()
    
    async def get(self, key: str) -> Optional[str]:
        """Get cached value."""
        async with self.lock:
            if key in self.cache:
                item = self.cache[key]
                if item["expires"] > asyncio.get_event_loop().time():
                    return item["value"]
                else:
                    del self.cache[key]
            return None
    
    async def set(self, key: str, value: str, ttl: Optional[int] = None) -> None:
        """Set cached value with TTL."""
        ttl = ttl or self.default_ttl
        expires = asyncio.get_event_loop().time() + ttl
        
        async with self.lock:
            self.cache[key] = {
                "value": value,
                "expires": expires
            }
    
    async def delete(self, key: str) -> None:
        """Delete cached value."""
        async with self.lock:
            self.cache.pop(key, None)
    
    async def clear(self) -> None:
        """Clear all cached values."""
        async with self.lock:
            self.cache.clear()
    
    async def cleanup_expired(self) -> None:
        """Clean up expired entries."""
        current_time = asyncio.get_event_loop().time()
        async with self.lock:
            expired_keys = [
                key for key, item in self.cache.items()
                if item["expires"] <= current_time
            ]
            for key in expired_keys:
                del self.cache[key]


class CacheService:
    """Main cache service with fallback to memory cache."""
    
    def __init__(self):
        self.cache = MemoryCache(default_ttl=settings.CACHE_TTL)
        self.enabled = True
    
    def _generate_cache_key(self, prefix: str, data: Any) -> str:
        """Generate consistent cache key."""
        if isinstance(data, dict):
            data_str = json.dumps(data, sort_keys=True)
        else:
            data_str = str(data)
        
        hash_obj = hashlib.md5(data_str.encode())
        return f"{prefix}:{hash_obj.hexdigest()}"
    
    async def get_prompt_response(self, prompt: str, model: str) -> Optional[str]:
        """Get cached prompt response."""
        if not self.enabled:
            return None
        
        cache_key = self._generate_cache_key("prompt", {
            "prompt": prompt,
            "model": model
        })
        return await self.cache.get(cache_key)
    
    async def cache_prompt_response(
        self, 
        prompt: str, 
        model: str, 
        response: str, 
        ttl: Optional[int] = None
    ) -> None:
        """Cache prompt response."""
        if not self.enabled:
            return
        
        cache_key = self._generate_cache_key("prompt", {
            "prompt": prompt,
            "model": model
        })
        await self.cache.set(cache_key, response, ttl)
    
    async def get_conversation_response(self, conversation_data: dict) -> Optional[str]:
        """Get cached conversation response."""
        if not self.enabled:
            return None
        
        cache_key = self._generate_cache_key("conversation", conversation_data)
        return await self.cache.get(cache_key)
    
    async def cache_conversation_response(
        self, 
        conversation_data: dict, 
        response: str, 
        ttl: Optional[int] = None
    ) -> None:
        """Cache conversation response."""
        if not self.enabled:
            return
        
        cache_key = self._generate_cache_key("conversation", conversation_data)
        await self.cache.set(cache_key, response, ttl)
    
    async def clear_cache(self) -> None:
        """Clear all cache."""
        await self.cache.clear()
    
    async def cleanup_expired_entries(self) -> None:
        """Clean up expired cache entries."""
        await self.cache.cleanup_expired()
    
    def disable_cache(self) -> None:
        """Disable caching."""
        self.enabled = False
    
    def enable_cache(self) -> None:
        """Enable caching."""
        self.enabled = True


# Global cache service instance
cache_service = CacheService()


async def get_cache_service() -> CacheService:
    """Get the global cache service instance."""
    return cache_service