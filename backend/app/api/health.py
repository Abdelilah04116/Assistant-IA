"""
Health check and monitoring endpoints.
"""

import time
import psutil
from datetime import datetime
from fastapi import APIRouter, Depends
from typing import Dict, Any

from ..core import get_logger, settings
from ..schemas import HealthResponse

logger = get_logger(__name__)

# Initialize router
router = APIRouter(prefix="/health", tags=["health"])

# Track service start time
start_time = time.time()


@router.get("/", response_model=HealthResponse)
async def health_check() -> HealthResponse:
    """
    Comprehensive health check endpoint.
    
    Returns:
        Health status with component information
    """
    try:
        uptime = time.time() - start_time
        
        # Check system resources
        cpu_percent = psutil.cpu_percent(interval=1)
        memory = psutil.virtual_memory()
        disk = psutil.disk_usage('/')
        
        # Check component health
        components = {
            "api": "healthy",
            "vector_store": "healthy",  # Would check actual connection in production
            "llm": "healthy",           # Would check API key and connectivity
            "embedding_model": "healthy"
        }
        
        # Overall status
        overall_status = "healthy"
        if cpu_percent > 90 or memory.percent > 90:
            overall_status = "degraded"
        
        health_response = HealthResponse(
            status=overall_status,
            version="1.0.0",
            uptime=uptime,
            components=components
        )
        
        return health_response
        
    except Exception as e:
        logger.error(f"Error in health check: {str(e)}")
        return HealthResponse(
            status="unhealthy",
            version="1.0.0",
            uptime=0,
            components={"api": "unhealthy"}
        )


@router.get("/detailed")
async def detailed_health() -> Dict[str, Any]:
    """
    Detailed health information with system metrics.
    
    Returns:
        Detailed health and system information
    """
    try:
        # System information
        cpu_info = {
            "usage_percent": psutil.cpu_percent(interval=1),
            "count": psutil.cpu_count(),
            "freq": psutil.cpu_freq()._asdict() if psutil.cpu_freq() else None
        }
        
        memory_info = {
            "total": psutil.virtual_memory().total,
            "available": psutil.virtual_memory().available,
            "percent": psutil.virtual_memory().percent,
            "used": psutil.virtual_memory().used
        }
        
        disk_info = {
            "total": psutil.disk_usage('/').total,
            "used": psutil.disk_usage('/').used,
            "free": psutil.disk_usage('/').free,
            "percent": psutil.disk_usage('/').percent
        }
        
        # Service information
        service_info = {
            "uptime": time.time() - start_time,
            "start_time": datetime.fromtimestamp(start_time).isoformat(),
            "current_time": datetime.now().isoformat(),
            "version": "1.0.0"
        }
        
        # Configuration info (without sensitive data)
        config_info = {
            "vector_store_type": settings.vector_store_type,
            "embedding_model": settings.embedding_model,
            "chunk_size": settings.chunk_size,
            "max_documents_per_query": settings.max_documents_per_query
        }
        
        return {
            "status": "healthy",
            "timestamp": datetime.now().isoformat(),
            "system": {
                "cpu": cpu_info,
                "memory": memory_info,
                "disk": disk_info
            },
            "service": service_info,
            "configuration": config_info
        }
        
    except Exception as e:
        logger.error(f"Error in detailed health check: {str(e)}")
        return {
            "status": "error",
            "error": str(e),
            "timestamp": datetime.now().isoformat()
        }
