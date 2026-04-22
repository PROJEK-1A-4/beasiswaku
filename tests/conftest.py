"""
Pytest configuration and fixtures for BeasiswaKu tests
Provides shared test utilities and database fixtures
"""
import pytest
import sys
from pathlib import Path

# Add project root to path for imports
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from src.core.config import Config
from src.core.database import DatabaseManager


def reset_database_manager() -> None:
    """Close all tracked connections and reset DatabaseManager singleton."""
    instance = DatabaseManager._instance
    if instance is not None:
        try:
            instance.close_all_connections()
        except Exception:
            pass
    DatabaseManager._instance = None


@pytest.fixture
def isolated_database(tmp_path):
    """Provide isolated sqlite database configuration per test."""
    old_database_path = Config.DATABASE_PATH
    old_check_same_thread = Config.DATABASE_CHECK_SAME_THREAD
    old_busy_timeout_ms = Config.DATABASE_BUSY_TIMEOUT_MS

    test_db_path = tmp_path / "beasiswaku_test.db"

    try:
        Config.DATABASE_PATH = str(test_db_path)
        Config.DATABASE_CHECK_SAME_THREAD = True
        Config.DATABASE_BUSY_TIMEOUT_MS = 30000

        reset_database_manager()
        db = DatabaseManager()
        db.init_schema()

        yield test_db_path
    finally:
        reset_database_manager()
        Config.DATABASE_PATH = old_database_path
        Config.DATABASE_CHECK_SAME_THREAD = old_check_same_thread
        Config.DATABASE_BUSY_TIMEOUT_MS = old_busy_timeout_ms
        reset_database_manager()


@pytest.fixture(autouse=True)
def cleanup_database_manager_after_test():
    """Ensure no test leaks open sqlite connections across test boundaries."""
    yield
    reset_database_manager()

