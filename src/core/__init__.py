"""
Core module - Shared database manager, config, and utilities
Owner: DARVA (initial setup), shared by all
"""

from .config import Config
from .database import DatabaseManager
from .logging_config import setup_logging, get_logger

__all__ = ["Config", "DatabaseManager", "setup_logging", "get_logger"]
