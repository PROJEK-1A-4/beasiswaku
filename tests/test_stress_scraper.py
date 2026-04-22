import sys
import io
import os
import time
import unittest
import tempfile
import sqlite3
from pathlib import Path
from unittest.mock import Mock, patch
from concurrent.futures import ThreadPoolExecutor, as_completed
from threading import Lock, Event

# UTF-8 encoding for Windows terminal
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

# Adjust path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.scraper.scraper import save_beasiswa_to_database
from src.core.logging_config import setup_logging, get_logger


logger = get_logger(__name__)


class MockCRUDModule:
    """Mock CRUD module with configurable behavior for stress testing."""
    
    def __init__(self, success_rate=1.0, failure_pattern=None, delay_ms=0):
        """
        Args:
            success_rate (float): Probability of success (0-1)
            failure_pattern (list): Indices that should fail (if None, use success_rate)
            delay_ms (int): Simulated DB operation delay in milliseconds
        """
        self.success_rate = success_rate
        self.failure_pattern = failure_pattern or []
        self.delay_ms = delay_ms
        self.call_count = 0
        self.lock = Lock()
        self.calls_log = []
    
    def add_beasiswa(self, **kwargs):
        """Mock add_beasiswa with configurable behavior."""
        # Extract judul for logging/tracking
        judul = kwargs.get('judul', 'Unknown')
        
        with self.lock:
            current_call = self.call_count
            self.call_count += 1
            self.calls_log.append({
                'judul': judul,
                'call_num': current_call,
                'thread_id': id(Mock()),
                'timestamp': time.time()
            })
        
        # Simulate DB operation delay
        if self.delay_ms > 0:
            time.sleep(self.delay_ms / 1000.0)
        
        # Check if this call should fail
        if current_call in self.failure_pattern:
            return (False, f"Simulated error at call {current_call}", None)
        
        # Use success_rate
        if self.success_rate < 1.0:
            import random
            if random.random() > self.success_rate:
                return (False, "Random failure", None)
        
        return (True, "Success", current_call)


def create_isolated_test_db():
    """Create isolated test database in temp directory."""
    temp_dir = tempfile.mkdtemp(prefix="beasiswaku_stress_test_")
    db_path = os.path.join(temp_dir, "test_beasiswa.db")
    
    # Create schema
    conn = sqlite3.connect(db_path, check_same_thread=False, timeout=30)
    cursor = conn.cursor()
    
    # Basic beasiswa table (matching CRUD expectations)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS beasiswa (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            judul TEXT NOT NULL,
            jenjang TEXT NOT NULL,
            deadline DATE,
            penyelenggara_id INTEGER,
            deskripsi TEXT,
            benefit TEXT,
            persyaratan TEXT,
            minimal_ipk REAL,
            coverage TEXT,
            status TEXT,
            link_aplikasi TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    
    conn.commit()
    return db_path, conn, temp_dir



def run_stress_tests():
    """Run all stress tests with detailed reporting."""
    print("\n" + "="*70)
    print("🧪 STRESS TEST SUITE: Scraper Sync Robustness (P0-04/P2-04)")
    print("="*70)
    
    # Create test suite
    loader = unittest.TestLoader()
    suite = loader.loadTestsFromTestCase(TestStressScraper)
    
    # Run with verbose output
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    # Print summary
    print("\n" + "="*70)
    print("📊 STRESS TEST SUMMARY")
    print("="*70)
    print(f"✅ Tests run: {result.testsRun}")
    print(f"✅ Passed: {result.testsRun - len(result.failures) - len(result.errors)}")
    print(f"❌ Failed: {len(result.failures)}")
    print(f"❌ Errors: {len(result.errors)}")
    print("="*70)
    
    return result


if __name__ == "__main__":
    result = run_stress_tests()
    sys.exit(0 if result.wasSuccessful() else 1)
