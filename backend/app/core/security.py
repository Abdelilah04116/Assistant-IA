"""
Security module for intelligent research assistant.
Handles rate limiting and other security primitives.
"""

from slowapi import Limiter
from slowapi.util import get_remote_address
from .config import settings

# Initialize Limiter
limiter = Limiter(
    key_func=get_remote_address, 
    default_limits=[settings.rate_limit]
)
