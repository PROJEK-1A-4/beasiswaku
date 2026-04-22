"""
Test untuk P0-02 (Error Handling) dan P2-03 (Logging)
File: tests/test_p0_p2_features.py

Run dengan: python -m pytest tests/test_p0_p2_features.py -v
"""

import sys
import logging
import json
from pathlib import Path
from unittest.mock import Mock, MagicMock, patch

# Setup path untuk import
sys.path.insert(0, str(Path(__file__).parent.parent))

# Setup stdout encoding untuk Windows
import io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

# Import directly from modules (avoid __init__.py circular import)
import importlib.util
spec = importlib.util.spec_from_file_location("scraper", 
    Path(__file__).parent.parent / "src" / "scraper" / "scraper.py")
scraper_module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(scraper_module)

save_beasiswa_to_database = scraper_module.save_beasiswa_to_database
auto_scrape_on_startup = scraper_module.auto_scrape_on_startup

from src.core.logging_config import setup_logging, get_logger


# ============================================================================
# TEST DATA & FIXTURES
# ============================================================================

def create_mock_beasiswa(judul="Beasiswa Test", jenjang="S1", deadline="2026-06-10"):
    """Create mock beasiswa dict"""
    return {
        "nama": judul,
        "jenjang": jenjang,
        "deadline": deadline,
        "deskripsi": "Test deskripsi",
        "link": "https://example.com/beasiswa",
        "status": "Buka",
        "penyelenggara": "Test Org"
    }


def create_mock_crud_module(success_count=None, fail_on_indices=None):
    """
    Create mock CRUD module
    
    Args:
        success_count: Jumlah items yang berhasil (None = semua berhasil)
        fail_on_indices: List of indices yang fail (0-based)
    """
    crud = Mock()
    fail_on_indices = fail_on_indices or []
    
    def add_beasiswa_impl(*args, **kwargs):
        # Determine call count
        call_index = add_beasiswa_impl.call_count - 1
        
        if call_index in fail_on_indices:
            return (False, f"Database error at index {call_index}", None)
        elif success_count is not None and call_index >= success_count:
            return (False, "Exceeds success limit", None)
        else:
            return (True, "Success", call_index + 1)
    
    add_beasiswa_impl.call_count = 0
    crud.add_beasiswa = Mock(side_effect=lambda *args, **kwargs: (
        add_beasiswa_impl(*args, **kwargs),
        setattr(add_beasiswa_impl, 'call_count', add_beasiswa_impl.call_count + 1)
    )[0])
    
    return crud


# ============================================================================
# P0-02 TESTS: Error Handling in save_beasiswa_to_database
# ============================================================================

def test_p0_02_all_success():
    """Test P0-02: All beasiswa saved successfully"""
    print("\n" + "="*70)
    print("TEST P0-02-01: All beasiswa saved successfully")
    print("="*70)
    
    # Setup
    beasiswa_list = [
        create_mock_beasiswa(f"Beasiswa {i}") 
        for i in range(5)
    ]
    crud = create_mock_crud_module()
    
    # Execute
    result = save_beasiswa_to_database(beasiswa_list, crud)
    
    # Validate
    assert result["total"] == 5, f"Expected total=5, got {result['total']}"
    assert result["saved"] == 5, f"Expected saved=5, got {result['saved']}"
    assert result["failed"] == 0, f"Expected failed=0, got {result['failed']}"
    assert len(result["errors"]) == 0, f"Expected no errors, got {result['errors']}"
    
    print(f"✅ Result: {result['saved']}/{result['total']} beasiswa berhasil disimpan")
    return True


def test_p0_02_partial_failure():
    """Test P0-02: Some beasiswa fail, others succeed"""
    print("\n" + "="*70)
    print("TEST P0-02-02: Partial failure - error handling")
    print("="*70)
    
    # Setup
    beasiswa_list = [
        create_mock_beasiswa(f"Beasiswa {i}") 
        for i in range(10)
    ]
    crud = create_mock_crud_module(fail_on_indices=[2, 5, 8])
    
    # Execute
    result = save_beasiswa_to_database(beasiswa_list, crud)
    
    # Validate
    assert result["total"] == 10, f"Expected total=10, got {result['total']}"
    assert result["saved"] == 7, f"Expected saved=7, got {result['saved']}"
    assert result["failed"] == 3, f"Expected failed=3, got {result['failed']}"
    assert len(result["errors"]) == 3, f"Expected 3 errors, got {len(result['errors'])}"
    
    # Validate error structure
    for error in result["errors"]:
        assert "judul" in error, "Error must have 'judul' field"
        assert "alasan" in error, "Error must have 'alasan' field"
    
    print(f"✅ Result: {result['saved']}/{result['total']} berhasil, {result['failed']} gagal")
    print(f"   Errors: {[e['judul'] for e in result['errors']]}")
    return True


def test_p0_02_validation_error():
    """Test P0-02: Validation error (missing required fields)"""
    print("\n" + "="*70)
    print("TEST P0-02-03: Validation error handling")
    print("="*70)
    
    # Setup - missing jenjang
    beasiswa_list = [
        {
            "nama": "Beasiswa Test",
            "deadline": "2026-06-10",
            "deskripsi": "Test"
            # Missing: jenjang
        }
    ]
    crud = create_mock_crud_module()
    
    # Execute
    result = save_beasiswa_to_database(beasiswa_list, crud)
    
    # Validate - should fail with validation error
    assert result["total"] == 1
    assert result["saved"] == 0
    assert result["failed"] == 1
    assert len(result["errors"]) == 1
    assert "jenjang" in result["errors"][0]["alasan"].lower() or "kosong" in result["errors"][0]["alasan"]
    
    print(f"✅ Validation error caught: {result['errors'][0]['alasan']}")
    return True


def test_p0_02_missing_title():
    """Test P0-02: Missing title error"""
    print("\n" + "="*70)
    print("TEST P0-02-04: Missing title validation")
    print("="*70)
    
    # Setup - empty title
    beasiswa_list = [
        {
            "nama": "",  # Empty!
            "jenjang": "S1",
            "deadline": "2026-06-10"
        }
    ]
    crud = create_mock_crud_module()
    
    # Execute
    result = save_beasiswa_to_database(beasiswa_list, crud)
    
    # Validate
    assert result["saved"] == 0
    assert result["failed"] == 1
    assert "judul" in result["errors"][0]["alasan"].lower() or "kosong" in result["errors"][0]["alasan"]
    
    print(f"✅ Empty title validation works: {result['errors'][0]['alasan']}")
    return True


def test_p0_02_error_collection():
    """Test P0-02: Error collection doesn't stop processing"""
    print("\n" + "="*70)
    print("TEST P0-02-05: Don't-stop-on-error behavior")
    print("="*70)
    
    # Setup
    beasiswa_list = [
        create_mock_beasiswa("OK 1"),
        {"nama": "", "jenjang": "S1", "deadline": "2026-06-10"},  # Fail validation
        create_mock_beasiswa("OK 2"),
        {"nama": "Valid", "jenjang": "", "deadline": "2026-06-10"},  # Fail validation
        create_mock_beasiswa("OK 3"),
    ]
    
    # Create a simple mock that returns success for valid items
    crud = Mock()
    crud.add_beasiswa = Mock(return_value=(True, "Success", 1))
    
    # Execute
    result = save_beasiswa_to_database(beasiswa_list, crud)
    
    # Validate - should process all items
    assert result["total"] == 5, "Should process all 5 items"
    assert result["saved"] == 3, f"Expected 3 saved, got {result['saved']}"
    assert result["failed"] == 2, f"Expected 2 failed, got {result['failed']}"
    
    print(f"✅ Processing didn't stop: {result['saved']} saved, {result['failed']} failed")
    print(f"   Processed all {result['total']} items as expected")
    return True


# ============================================================================
# P2-03 TESTS: Logging Configuration
# ============================================================================

def test_p2_03_setup_logging():
    """Test P2-03: setup_logging() creates handlers correctly"""
    print("\n" + "="*70)
    print("TEST P2-03-01: Logging setup and handlers")
    print("="*70)
    
    # Execute
    root_logger = setup_logging()
    
    # Validate
    assert root_logger is not None, "setup_logging() should return logger"
    assert len(root_logger.handlers) > 0, "Logger should have at least one handler"
    
    # Check handler types
    handler_types = [type(h).__name__ for h in root_logger.handlers]
    assert any("StreamHandler" in ht or "Console" in ht for ht in handler_types), \
        f"Should have StreamHandler, got {handler_types}"
    
    print(f"✅ Logger setup successful")
    print(f"   Handlers: {', '.join(handler_types)}")
    return True


def test_p2_03_logging_format():
    """Test P2-03: Logging format is consistent"""
    print("\n" + "="*70)
    print("TEST P2-03-02: Log format consistency")
    print("="*70)
    
    # Setup
    setup_logging()
    logger = get_logger(__name__)
    
    # Check formatter
    has_proper_format = False
    for handler in logging.getLogger().handlers:
        if handler.formatter:
            fmt = handler.formatter._fmt
            # Check for required format elements
            if "%(asctime)s" in fmt and "%(name)s" in fmt and "%(levelname)s" in fmt:
                has_proper_format = True
                print(f"✅ Format found: {fmt}")
                break
    
    assert has_proper_format, "Logger should have proper format with asctime, name, levelname"
    return True


def test_p2_03_idempotent():
    """Test P2-03: setup_logging() is idempotent"""
    print("\n" + "="*70)
    print("TEST P2-03-03: Idempotent setup (multiple calls)")
    print("="*70)
    
    # Setup
    setup_logging()
    handler_count_1 = len(logging.getLogger().handlers)
    
    # Call again
    setup_logging()
    handler_count_2 = len(logging.getLogger().handlers)
    
    # Validate - should not increase handler count
    assert handler_count_1 == handler_count_2, \
        f"Calling setup twice should not add handlers: {handler_count_1} vs {handler_count_2}"
    
    print(f"✅ Idempotent verified: handler count stable at {handler_count_2}")
    return True


def test_p2_03_get_logger():
    """Test P2-03: get_logger() convenience function"""
    print("\n" + "="*70)
    print("TEST P2-03-04: get_logger() convenience function")
    print("="*70)
    
    # Setup
    setup_logging()
    
    # Execute
    logger1 = get_logger("test_module")
    logger2 = get_logger("test_module")
    
    # Validate
    assert logger1 is not None, "get_logger should return logger"
    assert logger1.name == "test_module", "Logger should have correct name"
    assert logger1 is logger2, "Same name should return same logger (singleton)"
    
    print(f"✅ get_logger() works correctly, logger name: {logger1.name}")
    return True


# ============================================================================
# AUTO SCRAPE TESTS
# ============================================================================

def test_auto_scrape_database_not_empty():
    """Test auto_scrape_on_startup: Database already has data"""
    print("\n" + "="*70)
    print("TEST AUTO-SCRAPE-01: Database not empty")
    print("="*70)
    
    # Setup
    crud = Mock()
    crud.get_beasiswa_list = Mock(return_value=[{"id": 1}, {"id": 2}])
    
    # Execute
    result = auto_scrape_on_startup(crud)
    
    # Validate
    assert result["triggered"] == False, "Should not trigger if data exists"
    assert result["success"] == True, "Should return success"
    assert "already populated" in result["message"].lower(), "Message should indicate data exists"
    
    print(f"✅ Result: {result['message']}")
    return True


# ============================================================================
# MAIN TEST RUNNER
# ============================================================================

if __name__ == "__main__":
    print("\n" + "="*70)
    print("TESTING P0-02 (Error Handling) & P2-03 (Logging)")
    print("="*70)
    
    tests = [
        # P0-02 Tests
        ("P0-02-01: All Success", test_p0_02_all_success),
        ("P0-02-02: Partial Failure", test_p0_02_partial_failure),
        ("P0-02-03: Validation Error", test_p0_02_validation_error),
        ("P0-02-04: Missing Title", test_p0_02_missing_title),
        ("P0-02-05: Don't-Stop-on-Error", test_p0_02_error_collection),
        
        # P2-03 Tests
        ("P2-03-01: Logging Setup", test_p2_03_setup_logging),
        ("P2-03-02: Log Format", test_p2_03_logging_format),
        ("P2-03-03: Idempotent", test_p2_03_idempotent),
        ("P2-03-04: get_logger()", test_p2_03_get_logger),
        
        # Auto-Scrape Tests
        ("AUTO-SCRAPE-01: Database Not Empty", test_auto_scrape_database_not_empty),
    ]
    
    passed = 0
    failed = 0
    
    for test_name, test_func in tests:
        try:
            if test_func():
                passed += 1
        except Exception as e:
            failed += 1
            print(f"\n❌ {test_name} FAILED:")
            print(f"   {str(e)}")
            import traceback
            traceback.print_exc()
    
    # Summary
    print("\n" + "="*70)
    print("TEST SUMMARY")
    print("="*70)
    print(f"✅ Passed: {passed}/{len(tests)}")
    print(f"❌ Failed: {failed}/{len(tests)}")
    print("="*70)
    
    sys.exit(0 if failed == 0 else 1)
