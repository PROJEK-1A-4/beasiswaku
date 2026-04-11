"""
Configuration Management Module
Owner: DARVA
Provides centralized configuration for all modules
"""

import os
from pathlib import Path
from typing import Dict, Any
import logging

logger = logging.getLogger(__name__)


class Config:
    """
    Centralized configuration management for BeasiswaKu application.
    Loads configuration from environment variables and defaults.
    
    Usage:
        config = Config()
        db_path = config.DATABASE_PATH
        app_name = config.APP_NAME
    """

    # ==================== Database Configuration ====================
    DATABASE_PATH: str = os.getenv("DATABASE_PATH", "database/beasiswaku.db")
    DATABASE_BACKUP_PATH: str = os.getenv("DATABASE_BACKUP_PATH", "database/backup/beasiswaku_backup.db")
    DATABASE_TIMEOUT: int = 30
    DATABASE_CHECK_SAME_THREAD: bool = False

    # ==================== Application Configuration ====================
    APP_NAME: str = os.getenv("APP_NAME", "BeasiswaKu")
    APP_VERSION: str = os.getenv("APP_VERSION", "2.0.0")
    DEBUG_MODE: bool = os.getenv("DEBUG_MODE", "False").lower() == "true"

    # ==================== GUI Configuration ====================
    WINDOW_WIDTH: int = int(os.getenv("WINDOW_WIDTH", "1200"))
    WINDOW_HEIGHT: int = int(os.getenv("WINDOW_HEIGHT", "800"))
    WINDOW_TITLE: str = f"{APP_NAME} v{APP_VERSION}"
    THEME: str = os.getenv("THEME", "light")

    # ==================== Scraper Configuration (KEMAL) ====================
    SCRAPER_TIMEOUT: int = int(os.getenv("SCRAPER_TIMEOUT", "30"))
    SCRAPER_RETRIES: int = int(os.getenv("SCRAPER_RETRIES", "3"))
    SCRAPER_USER_AGENT: str = os.getenv(
        "SCRAPER_USER_AGENT",
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
    )

    # ==================== Logging Configuration ====================
    LOG_LEVEL: str = os.getenv("LOG_LEVEL", "INFO")
    LOG_FILE: str = os.getenv("LOG_FILE", "logs/beasiswa.log")
    LOG_FORMAT: str = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"

    # ==================== Team Ownership ====================
    TEAM_STRUCTURE: Dict[str, str] = {
        "KEMAL": "src/scraper/ - Web Scraping & Data Collection",
        "DARVA": "src/database/ - Database & CRUD Operations",
        "KYLA": "src/gui/tab_*.py - GUI Tabs & Dialogs",
        "AULIA": "src/gui/main_window.py, login_window.py - Main Window & Auth",
        "RICHARD": "src/visualization/ - Charts & Analytics",
    }

    # ==================== Paths ====================
    DATA_DIR: Path = Path(os.getenv("DATA_DIR", "data"))
    LOGS_DIR: Path = Path(os.getenv("LOGS_DIR", "logs"))
    BACKUP_DIR: Path = Path(os.getenv("BACKUP_DIR", "data/backup"))
    DOCS_DIR: Path = Path(os.getenv("DOCS_DIR", "docs"))

    @classmethod
    def setup(cls) -> None:
        """Initialize configuration and create necessary directories."""
        cls.DATA_DIR.mkdir(parents=True, exist_ok=True)
        cls.LOGS_DIR.mkdir(parents=True, exist_ok=True)
        cls.BACKUP_DIR.mkdir(parents=True, exist_ok=True)
        cls.DOCS_DIR.mkdir(parents=True, exist_ok=True)

        # Initialize logging
        logging.basicConfig(
            level=cls.LOG_LEVEL,
            format=cls.LOG_FORMAT,
            handlers=[
                logging.FileHandler(cls.LOG_FILE),
                logging.StreamHandler(),
            ]
        )
        logger.info(f"Configuration initialized - {cls.APP_NAME} v{cls.APP_VERSION}")
        logger.info(f"Debug Mode: {cls.DEBUG_MODE}, Theme: {cls.THEME}")

    @classmethod
    def get_all(cls) -> Dict[str, Any]:
        """Return all configuration as a dictionary."""
        return {
            key: getattr(cls, key)
            for key in dir(cls)
            if not key.startswith("_") and not callable(getattr(cls, key))
        }

    @classmethod
    def __repr__(cls) -> str:
        """String representation of configuration."""
        return f"<Config {cls.APP_NAME} v{cls.APP_VERSION}>"


# Initialize configuration on module import
Config.setup()
