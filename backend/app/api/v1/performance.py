"""
Performance monitoring endpoints.
"""

import time
import psutil
from typing import Dict, Any
from fastapi import APIRouter, Depends
from app.core.agent_pool import agent_pool
from app.core.cache_service import cache_service
from app.dependencies import CurrentUserDep

router = APIRouter(prefix="/performance", tags=["performance"])


@router.get("/metrics")
async def get_performance_metrics(
    current_user: CurrentUserDep,
) -> Dict[str, Any]:
    """
    Get comprehensive performance metrics.
    """
    # System metrics
    cpu_percent = psutil.cpu_percent(interval=1)
    memory = psutil.virtual_memory()
    disk = psutil.disk_usage('/')
    
    # Agent pool metrics
    pool_stats = agent_pool.get_stats()
    
    # Process metrics
    process = psutil.Process()
    process_memory = process.memory_info()
    
    return {
        "timestamp": time.time(),
        "system": {
            "cpu_percent": cpu_percent,
            "memory": {
                "total": memory.total,
                "available": memory.available,
                "percent": memory.percent,
                "used": memory.used,
                "free": memory.free,
            },
            "disk": {
                "total": disk.total,
                "used": disk.used,
                "free": disk.free,
                "percent": (disk.used / disk.total) * 100,
            },
        },
        "process": {
            "memory_rss": process_memory.rss,
            "memory_vms": process_memory.vms,
            "memory_percent": process.memory_percent(),
            "cpu_percent": process.cpu_percent(),
            "num_threads": process.num_threads(),
            "create_time": process.create_time(),
        },
        "agent_pool": pool_stats,
        "cache": {
            "enabled": cache_service.enabled,
            "type": "memory",
        },
    }


@router.get("/health-detailed")
async def get_detailed_health() -> Dict[str, Any]:
    """
    Get detailed health information including performance indicators.
    """
    start_time = time.time()
    
    # Test agent pool
    try:
        agent = await agent_pool.get_agent()
        agent_available = True
    except Exception as e:
        agent_available = False
        
    # Test cache
    try:
        await cache_service.cache_prompt_response("test", "test", "test", 1)
        cached = await cache_service.get_prompt_response("test", "test")
        cache_available = cached == "test"
    except Exception:
        cache_available = False
    
    response_time = time.time() - start_time
    
    return {
        "status": "healthy",
        "checks": {
            "agent_pool": {
                "available": agent_available,
                "pool_size": len(agent_pool.agents),
                "max_pool_size": agent_pool.pool_size,
            },
            "cache": {
                "available": cache_available,
                "enabled": cache_service.enabled,
            },
            "response_time": {
                "value": response_time,
                "unit": "seconds",
                "threshold": 0.1,
                "healthy": response_time < 0.1,
            },
        },
        "performance": {
            "response_time_ms": response_time * 1000,
            "status": "optimal" if response_time < 0.05 else "acceptable" if response_time < 0.1 else "degraded",
        },
    }


@router.get("/agent-pool")
async def get_agent_pool_stats(
    current_user: CurrentUserDep,
) -> Dict[str, Any]:
    """
    Get agent pool statistics.
    """
    return {
        "pool_stats": agent_pool.get_stats(),
        "recommendations": _get_pool_recommendations(),
    }


@router.post("/agent-pool/cleanup")
async def cleanup_agent_pool(
    current_user: CurrentUserDep,
) -> Dict[str, Any]:
    """
    Clean up unused agents in the pool.
    """
    await agent_pool.cleanup_unused_agents()
    return {
        "message": "Agent pool cleanup completed",
        "new_stats": agent_pool.get_stats(),
    }


@router.get("/cache")
async def get_cache_stats(
    current_user: CurrentUserDep,
) -> Dict[str, Any]:
    """
    Get cache statistics.
    """
    return {
        "cache_enabled": cache_service.enabled,
        "cache_type": "memory",
        "recommendations": _get_cache_recommendations(),
    }


@router.post("/cache/clear")
async def clear_cache(
    current_user: CurrentUserDep,
) -> Dict[str, Any]:
    """
    Clear all cache entries.
    """
    await cache_service.clear_cache()
    return {
        "message": "Cache cleared successfully",
    }


@router.post("/cache/cleanup")
async def cleanup_cache(
    current_user: CurrentUserDep,
) -> Dict[str, Any]:
    """
    Clean up expired cache entries.
    """
    await cache_service.cleanup_expired_entries()
    return {
        "message": "Cache cleanup completed",
    }


def _get_pool_recommendations() -> list:
    """Get recommendations for agent pool optimization."""
    recommendations = []
    
    pool_stats = agent_pool.get_stats()
    pool_size = pool_stats["pool_size"]
    max_pool_size = pool_stats["max_pool_size"]
    
    if pool_size >= max_pool_size * 0.8:
        recommendations.append({
            "type": "warning",
            "message": "Agent pool is nearly full. Consider increasing pool size.",
            "metric": "pool_utilization",
            "value": pool_size / max_pool_size,
        })
    
    if pool_size == 0:
        recommendations.append({
            "type": "info",
            "message": "No agents in pool. Pool will create agents on demand.",
            "metric": "pool_size",
            "value": pool_size,
        })
    
    return recommendations


def _get_cache_recommendations() -> list:
    """Get recommendations for cache optimization."""
    recommendations = []
    
    if not cache_service.enabled:
        recommendations.append({
            "type": "warning",
            "message": "Cache is disabled. Enable caching for better performance.",
            "metric": "cache_enabled",
            "value": False,
        })
    
    recommendations.append({
        "type": "info",
        "message": "Using in-memory cache. Consider Redis for production.",
        "metric": "cache_type",
        "value": "memory",
    })
    
    return recommendations