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

@pytest.fixture(scope="session")
def test_db_path():
    """Provide test database path"""
    return "test_beasiswa.db"

@pytest.fixture(autouse=True)
def cleanup_test_db(test_db_path):
    """Clean up test database after each test"""
    yield
    # Cleanup happens after test
    test_db = Path(test_db_path)
    if test_db.exists():
        test_db.unlink()
