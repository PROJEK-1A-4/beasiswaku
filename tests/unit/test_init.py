#!/usr/bin/env python3
"""
INITIALIZATION TESTS
====================

Basic tests for project initialization and setup verification.
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def test_imports():
    """Test core modules import"""
    print("\n" + "="*80)
    print("TEST 1: IMPORT VERIFICATION".center(80))
    print("="*80)
    
    required_modules = [
        ('src.core.config', 'Configuration'),
        ('src.database.crud', 'CRUD operations'),
        ('sqlite3', 'Database'),
    ]
    
    all_pass = True
    for module_name, desc in required_modules:
        try:
            __import__(module_name)
            print(f"✅ {module_name:<30} - {desc}")
        except ImportError as e:
            print(f"❌ {module_name:<30} - {desc}")
            all_pass = False
    
    return all_pass


if __name__ == "__main__":
    print("\nINITIALIZATION TEST SUITE\n")
    test_imports()
    sys.exit(0)
