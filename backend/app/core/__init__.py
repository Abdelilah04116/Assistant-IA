"""
Core module containing configuration, logging, and shared utilities.
"""

from .config import settings, Settings
from .logging import setup_logging, get_logger

__all__ = ["settings", "Settings", "setup_logging", "get_logger"]
