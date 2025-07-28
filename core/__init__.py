"""
Core package initialization
"""

from .config import config, Config
from .database import DatabaseManager

__all__ = ["config", "Config", "DatabaseManager"]
