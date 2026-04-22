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

class TestStressScraper(unittest.TestCase):
    """Stress tests for scraper sync robustness."""
    
    @classmethod
    def setUpClass(cls):
        """Setup test logging."""
        setup_logging(log_level='WARNING', log_file=False)  # Quiet logs for stress test
    
    def setUp(self):
        """Create isolated test database for each test."""
        self.db_path, self.conn, self.temp_dir = create_isolated_test_db()
    
    def tearDown(self):
        """Clean up test database."""
        try:
            self.conn.close()
        except:
            pass
        
        # Cleanup temp directory
        import shutil
        try:
            shutil.rmtree(self.temp_dir)
        except:
            pass
    
    def create_beasiswa_list(self, count):
        """Helper: Create list of mock beasiswa data."""
        return [
            {
                'nama': f'Beasiswa Stress Test {i}',
                'jenjang': 'S1',
                'deadline': '2026-12-31',
                'penyelenggara_id': 1,
                'deskripsi': f'Test beasiswa {i}',
                'benefit': 'Tuition',
                'persyaratan': 'GPA >= 3.0',
                'minimal_ipk': 3.0,
                'coverage': 'Full',
                'status': 'open',
                'link_aplikasi': f'https://example.com/{i}'
            }
            for i in range(count)
        ]
    
    # ===================== STRESS TEST SCENARIOS =====================
    
    def test_stress_01_high_volume_sync(self):
        """Test: High volume beasiswa sync (100 items)"""
        print("\n" + "="*70)
        print("TEST STRESS-01: High volume sync (100 items)")
        print("="*70)
        
        # Setup
        beasiswa_list = self.create_beasiswa_list(100)
        crud = MockCRUDModule(success_rate=0.95, delay_ms=1)  # 95% success, 1ms delay per item
        
        # Execute
        start_time = time.time()
        result = save_beasiswa_to_database(beasiswa_list, crud)
        elapsed = time.time() - start_time
        
        # Validate
        assert result['total'] == 100, f"Expected 100 items, got {result['total']}"
        # Allow some variance in success rate due to randomness
        assert result['saved'] >= 90, f"Expected >=90 saved (90%), got {result['saved']}"
        assert 'telemetry' in result, "Should have telemetry tracking"
        
        telemetry = result['telemetry']
        assert telemetry['success_rate'] >= 0.89, f"Success rate too low: {telemetry['success_rate']}"
        
        print(f"✅ High volume test passed:")
        print(f"   Total: {result['total']}")
        print(f"   Saved: {result['saved']} ({telemetry['success_rate']*100:.1f}%)")
        print(f"   Failed: {result['failed']}")
        print(f"   Time: {elapsed:.2f}s ({telemetry['total_time_ms']:.1f}ms per operation)")
    
    def test_stress_02_concurrent_reads_writes(self):
        """Test: Concurrent reads while scraper writes"""
        print("\n" + "="*70)
        print("TEST STRESS-02: Concurrent reads/writes")
        print("="*70)
        
        # Setup
        beasiswa_list = self.create_beasiswa_list(50)
        crud = MockCRUDModule(success_rate=1.0, delay_ms=2)
        errors = []
        
        def read_operation():
            """Simulate reading from database."""
            try:
                cursor = self.conn.cursor()
                cursor.execute("SELECT COUNT(*) FROM beasiswa")
                count = cursor.fetchone()[0]
                return count
            except Exception as e:
                errors.append(f"Read error: {str(e)}")
                return -1
        
        def write_operation():
            """Simulate scraper write operation."""
            try:
                result = save_beasiswa_to_database(beasiswa_list, crud)
                return result['saved']
            except Exception as e:
                errors.append(f"Write error: {str(e)}")
                return -1
        
        # Execute concurrent operations
        with ThreadPoolExecutor(max_workers=4) as executor:
            futures = []
            
            # Submit write operation
            write_future = executor.submit(write_operation)
            futures.append(('write', write_future))
            
            # Submit read operations while write is happening
            for i in range(3):
                read_future = executor.submit(read_operation)
                futures.append(('read', read_future))
            
            # Collect results
            results = {}
            for op_type, future in futures:
                try:
                    result = future.result(timeout=30)
                    if op_type not in results:
                        results[op_type] = []
                    results[op_type].append(result)
                except Exception as e:
                    errors.append(f"{op_type} timeout/error: {str(e)}")
        
        # Validate
        assert len(errors) == 0, f"Concurrent operations had errors: {errors}"
        assert 'write' in results, "Write operation should complete"
        assert 'read' in results, "Read operations should complete"
        
        print(f"✅ Concurrent read/write test passed:")
        print(f"   Write operations completed: {len(results['write'])}")
        print(f"   Read operations completed: {len(results['read'])}")
        print(f"   Errors: {len(errors)}")
    
    def test_stress_03_failure_resilience(self):
        """Test: System resilience with partial failures"""
        print("\n" + "="*70)
        print("TEST STRESS-03: Failure resilience")
        print("="*70)
        
        # Setup - fail every 3rd item
        beasiswa_list = self.create_beasiswa_list(30)
        failure_indices = [i for i in range(30) if i % 3 == 0]  # 10 failures out of 30
        crud = MockCRUDModule(failure_pattern=failure_indices)
        
        # Execute
        result = save_beasiswa_to_database(beasiswa_list, crud)
        
        # Validate
        assert result['total'] == 30, f"Expected 30 items, got {result['total']}"
        assert result['saved'] == 20, f"Expected 20 saved, got {result['saved']}"
        assert result['failed'] == 10, f"Expected 10 failed, got {result['failed']}"
        assert len(result['errors']) == 10, f"Expected 10 error records, got {len(result['errors'])}"
        
        # Verify error details have context
        for error in result['errors']:
            assert 'judul' in error, "Error should have judul context"
            assert 'alasan' in error, "Error should have alasan (reason)"
        
        print(f"✅ Failure resilience test passed:")
        print(f"   Total: {result['total']}")
        print(f"   Saved: {result['saved']}")
        print(f"   Failed: {result['failed']} (expected: 10)")
        print(f"   Error tracking: {len(result['errors'])} detailed records")
        print(f"   Sample error: {result['errors'][0]}")
    
    def test_stress_04_telemetry_under_load(self):
        """Test: Telemetry accuracy under load"""
        print("\n" + "="*70)
        print("TEST STRESS-04: Telemetry tracking accuracy")
        print("="*70)
        
        # Setup
        beasiswa_list = self.create_beasiswa_list(50)
        crud = MockCRUDModule(success_rate=0.92, delay_ms=5)
        
        # Execute
        result = save_beasiswa_to_database(beasiswa_list, crud)
        telemetry = result['telemetry']
        
        # Validate telemetry completeness
        required_metrics = [
            'success_rate', 'failure_rate',
            'total_time_ms', 'avg_time_per_item_ms',
            'fastest_item_ms', 'slowest_item_ms',
            'error_types'
        ]
        
        for metric in required_metrics:
            assert metric in telemetry, f"Missing metric: {metric}"
        
        # Validate metric relationships
        assert 0 <= telemetry['success_rate'] <= 1, "Invalid success_rate"
        assert 0 <= telemetry['failure_rate'] <= 1, "Invalid failure_rate"
        assert abs((telemetry['success_rate'] + telemetry['failure_rate']) - 1.0) < 0.01, \
            "Success + Failure rates should sum to 1.0"
        
        assert telemetry['total_time_ms'] > 0, "Total time should be > 0"
        assert telemetry['avg_time_per_item_ms'] > 0, "Avg time should be > 0"
        assert telemetry['fastest_item_ms'] <= telemetry['slowest_item_ms'], \
            "Fastest should be <= slowest"
        
        print(f"✅ Telemetry tracking verified:")
        print(f"   Success rate: {telemetry['success_rate']*100:.1f}%")
        print(f"   Total time: {telemetry['total_time_ms']:.1f}ms")
        print(f"   Avg/item: {telemetry['avg_time_per_item_ms']:.2f}ms")
        print(f"   Range: {telemetry['fastest_item_ms']:.2f}ms - {telemetry['slowest_item_ms']:.2f}ms")
        print(f"   Error types tracked: {telemetry['error_types']}")
    
    def test_stress_05_no_deadlock(self):
        """Test: No deadlock during parallel sync cycles"""
        print("\n" + "="*70)
        print("TEST STRESS-05: Deadlock detection (parallel sync cycles)")
        print("="*70)
        
        # Setup
        beasiswa_list_1 = self.create_beasiswa_list(25)
        beasiswa_list_2 = self.create_beasiswa_list(25)
        
        crud1 = MockCRUDModule(success_rate=0.98)
        crud2 = MockCRUDModule(success_rate=0.98)
        
        completion_event = Event()
        errors = []
        
        def sync_operation(beasiswa_list, crud, operation_id):
            """Execute sync operation with timeout."""
            try:
                result = save_beasiswa_to_database(beasiswa_list, crud)
                logger.debug(f"Operation {operation_id} completed: {result['saved']}/{result['total']}")
                return result
            except Exception as e:
                errors.append(f"Operation {operation_id} error: {str(e)}")
                return None
        
        # Execute parallel sync operations
        with ThreadPoolExecutor(max_workers=2, thread_name_prefix="SyncWorker") as executor:
            futures = [
                executor.submit(sync_operation, beasiswa_list_1, crud1, 1),
                executor.submit(sync_operation, beasiswa_list_2, crud2, 2),
            ]
            
            try:
                results = [f.result(timeout=15) for f in as_completed(futures, timeout=15)]
            except Exception as e:
                errors.append(f"Timeout (possible deadlock): {str(e)}")
                results = []
        
        # Validate
        assert len(errors) == 0, f"Parallel sync had errors: {errors}"
        assert len(results) == 2, "Both operations should complete"
        assert all(r is not None for r in results), "All results should be valid"
        
        total_saved = sum(r['saved'] for r in results)
        print(f"✅ No deadlock detected - parallel sync completed:")
        print(f"   Operation 1: {results[0]['saved']}/{results[0]['total']} saved")
        print(f"   Operation 2: {results[1]['saved']}/{results[1]['total']} saved")
        print(f"   Total saved: {total_saved}")
    
    def test_stress_06_error_context_detail(self):
        """Test: Error context includes all debugging info"""
        print("\n" + "="*70)
        print("TEST STRESS-06: Error context completeness")
        print("="*70)
        
        # Setup - mixed failures
        beasiswa_list = [
            {'nama': 'Valid 1', 'jenjang': 'S1', 'deadline': '2026-12-31',
             'penyelenggara_id': 1, 'deskripsi': 'Test', 'benefit': 'Tuition',
             'persyaratan': 'GPA >= 3.0', 'minimal_ipk': 3.0, 'coverage': 'Full',
             'status': 'open', 'link_aplikasi': 'https://example.com/1'},
            {'nama': '', 'jenjang': 'S1', 'deadline': '2026-12-31',  # Missing judul
             'penyelenggara_id': 1, 'deskripsi': 'Test', 'benefit': 'Tuition',
             'persyaratan': 'GPA >= 3.0', 'minimal_ipk': 3.0, 'coverage': 'Full',
             'status': 'open', 'link_aplikasi': 'https://example.com/2'},
            {'nama': 'Valid 2', 'jenjang': '', 'deadline': '2026-12-31',  # Missing jenjang
             'penyelenggara_id': 1, 'deskripsi': 'Test', 'benefit': 'Tuition',
             'persyaratan': 'GPA >= 3.0', 'minimal_ipk': 3.0, 'coverage': 'Full',
             'status': 'open', 'link_aplikasi': 'https://example.com/3'},
        ]
        
        crud = Mock()
        crud.add_beasiswa = Mock(return_value=(True, "Success", 1))
        
        # Execute
        result = save_beasiswa_to_database(beasiswa_list, crud)
        
        # Validate error context
        assert result['failed'] == 2, f"Expected 2 failures, got {result['failed']}"
        assert len(result['errors']) == 2, "Should have 2 error records"
        
        for error in result['errors']:
            assert isinstance(error, dict), "Error should be dict"
            assert 'judul' in error, "Error should have judul"
            assert 'alasan' in error, "Error should have alasan"
            # alasan should be descriptive
            assert len(error['alasan']) > 0, "Alasan should not be empty"
        
        print(f"✅ Error context completeness verified:")
        print(f"   Error records: {len(result['errors'])}")
        for i, error in enumerate(result['errors']):
            print(f"   Error {i+1}: judul='{error['judul']}', alasan='{error['alasan']}'")

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
