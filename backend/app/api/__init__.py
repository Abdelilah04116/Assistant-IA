"""
API endpoints for the intelligent research assistant.
"""

from .chat import router as chat_router
from .ingestion import router as ingestion_router
from .health import router as health_router

__all__ = ["chat_router", "ingestion_router", "health_router"]
