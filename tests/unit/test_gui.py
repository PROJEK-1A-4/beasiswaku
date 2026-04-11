#!/usr/bin/env python3
"""
GUI TESTS - KYLA & AULIA
========================

This file consolidates GUI-related tests from previous phases.

Team: KYLA (Tab Components) & AULIA (Main Window)
Status: Tests for GUI integration with DARVA's backend
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

import logging
from typing import List
from src.database.crud import (
    init_db, register_user, add_beasiswa, 
    add_favorit, get_favorit_list, delete_favorit,
    add_catatan, get_catatan, edit_catatan, delete_catatan,
    get_connection
)

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def print_header(title: str):
    """Print test header"""
    print(f"\n{'='*80}")
    print(f"{title.center(80)}")
    print(f"{'='*80}")


def print_section(section: str):
    """Print section header"""
    print(f"\n{'-'*80}\n{section}\n{'-'*80}")


def test_favorites_functionality():
    """Test favorites CRUD operations for GUI (KYLA)"""
    print_section("TEST 1: FAVORITES MANAGEMENT (KYLA)")
    
    try:
        init_db()
        print("✅ Database initialized")
        
        # Create test user
        success, msg = register_user("gui_user_fav", "gui_fav@test.com", "password123@A")
        if success:
            conn = get_connection()
            cursor = conn.cursor()
            cursor.execute("SELECT id FROM akun WHERE username = ?", ("gui_user_fav",))
            result = cursor.fetchone()
            user_id = result[0] if result else None
            cursor.close()
            if user_id:
                print(f"✅ User created (id={user_id})")
        else:
            print(f"❌ User creation failed: {msg}")
            return False
        
        # Create test beasiswa
        success, msg, bid = add_beasiswa("Test Beasiswa GUI", 1, "S1", "2025-12-31", "Full", "3.0", "open")
        if success and bid:
            print(f"✅ Beasiswa created (id={bid})")
        else:
            print(f"❌ Beasiswa creation failed: {msg}")
            return False
        
        # Test add favorit
        success, msg, fav_id = add_favorit(user_id, bid)
        print(f"{'✅' if success else '❌'} Add favorit: {msg}")
        
        # Test get favorit list
        favs, count = get_favorit_list(user_id)
        print(f"✅ Favorites list: {count} found")
        
        # Test delete favorit
        success, msg = delete_favorit(user_id, bid)
        print(f"{'✅' if success else '⚠️'} Delete favorit: {msg}")
        
        return success
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        return False


def test_catatan_functionality():
    """Test notes/catatan CRUD operations (AULIA)"""
    print_section("TEST 2: NOTES/CATATAN MANAGEMENT (AULIA)")
    
    try:
        init_db()
        print("✅ Database ready")
        
        # Create test user
        success, msg = register_user("gui_user_notes", "gui_notes@test.com", "password123@A")
        if success:
            conn = get_connection()
            cursor = conn.cursor()
            cursor.execute("SELECT id FROM akun WHERE username = ?", ("gui_user_notes",))
            result = cursor.fetchone()
            user_id = result[0] if result else None
            cursor.close()
            if user_id:
                print(f"✅ User created (id={user_id})")
        else:
            print(f"❌ User creation failed: {msg}")
            return False
        
        # Create test beasiswa
        success, msg, bid = add_beasiswa("Test Beasiswa Notes", 1, "S1", "2025-12-31", "Full", "3.5", "open")
        if success and bid:
            print(f"✅ Beasiswa created (id={bid})")
        else:
            print(f"❌ Beasiswa creation failed: {msg}")
            return False
        
        # Test add catatan
        success, msg, cid = add_catatan(user_id, bid, "Ini adalah catatan pembelajaran")
        print(f"{'✅' if success else '❌'} Add catatan: {msg}")
        
        # Test get catatan
        catatan, count = get_catatan(user_id, bid)
        print(f"✅ Catatan retrieved: {count} found")
        
        # Test edit catatan
        if cid:
            success, msg = edit_catatan(cid, "Catatan yang sudah diupdate")
            print(f"{'✅' if success else '⚠️'} Edit catatan: {msg}")
        
        # Test delete catatan
        if cid:
            success, msg = delete_catatan(cid)
            print(f"{'✅' if success else '⚠️'} Delete catatan: {msg}")
        
        return bool(cid)
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        return False


if __name__ == "__main__":
    print_header("GUI TEST SUITE - KYLA & AULIA")
    
    tests = [
        ("Favorites Management", test_favorites_functionality()),
        ("Catatan Management", test_catatan_functionality()),
    ]
    
    print_header("TEST SUMMARY")
    passed = sum(1 for _, result in tests if result)
    print(f"\n✅ Passed: {passed}/{len(tests)}")
    
    sys.exit(0 if passed == len(tests) else 1)
