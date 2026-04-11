"""
Core module - Shared database manager, config, and utilities
Owner: DARVA (initial setup), shared by all
"""

from .config import Config
from .database import DatabaseManager

__all__ = ["Config", "DatabaseManager"]
