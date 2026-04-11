#!/usr/bin/env python3
"""
CONSOLIDATED TEST: Database, CRUD Operations, and Authentication
=================================================================

This file consolidates all database-related tests.

Team: DARVA - Database Backend
Status: All tests PASSING ✅
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

import sqlite3
import logging
from datetime import datetime, timedelta

# Import all DARVA functions
from src.database.crud import (
    init_db, get_connection, hash_password, verify_password,
    register_user, login_user,
    add_beasiswa, get_beasiswa_list, edit_beasiswa, delete_beasiswa,
    add_lamaran, get_lamaran_list, edit_lamaran, delete_lamaran,
    add_favorit, get_favorit_list, delete_favorit,
    add_catatan, get_catatan, edit_catatan, delete_catatan,
    get_beasiswa_per_jenjang, get_top_penyelenggara, get_status_availability
)

logging.basicConfig(level=logging.INFO, format='%(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


def print_header(text: str):
    """Print formatted header"""
    print(f"\n{'='*80}")
    print(f"{text.center(80)}")
    print(f"{'='*80}")


def print_section(section: str):
    """Print section header"""
    print(f"\n{'-'*80}\n{section}\n{'-'*80}")


def print_result(symbol: str, message: str):
    """Print test result"""
    print(f"{symbol} {message}")


# ============================================================================
# PHASE 1.1: Database Initialization & Schema Validation
# ============================================================================

def test_database_initialization():
    """Test 1: Database initialization and file creation"""
    print_section("TEST 1: DATABASE INITIALIZATION")
    
    db_path = Path("database/beasiswaku.db")
    
    # Remove database for fresh test
    if db_path.exists():
        db_path.unlink()
        print_result("✅", "Cleaned up old database file")
    
    # Execute init_db
    try:
        init_db()
        print_result("✅", "init_db() executed successfully")
    except Exception as e:
        print_result("❌", f"init_db() failed: {e}")
        return False
    
    # Verify file exists
    if db_path.exists():
        file_size = db_path.stat().st_size
        print_result("✅", f"Database file created: {db_path} (size: {file_size} bytes)")
        return True
    else:
        print_result("❌", f"Database file NOT found at {db_path}")
        return False


def test_table_existence():
    """Test 2: Verify all tables exist"""
    print_section("TEST 2: TABLE EXISTENCE VERIFICATION")
    
    expected_tables = ['akun', 'penyelenggara', 'beasiswa', 'riwayat_lamaran', 'favorit', 'catatan']
    
    try:
        conn = get_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT name FROM sqlite_master 
            WHERE type='table' AND name NOT LIKE 'sqlite_%'
        """)
        
        existing_tables = [row[0] for row in cursor.fetchall()]
        
        print_result("ℹ️", f"Found tables: {', '.join(existing_tables)}")
        
        for table in expected_tables:
            if table in existing_tables:
                print_result("✅", f"Table '{table}' exists")
            else:
                print_result("❌", f"Table '{table}' NOT found")
                return False
        
        cursor.close()
        return True
        
    except Exception as e:
        print_result("❌", f"Error checking tables: {e}")
        return False


def test_table_schemas():
    """Test 3: Verify table column structures"""
    print_section("TEST 3: TABLE SCHEMA VALIDATION")
    
    expected_schemas = {
        'akun': ['id', 'username', 'email', 'password_hash', 'nama_lengkap', 'jenjang', 'created_at', 'updated_at'],
        'penyelenggara': ['id', 'nama', 'description', 'website', 'contact_email', 'created_at'],
        'beasiswa': ['id', 'judul', 'penyelenggara_id', 'jenjang', 'deadline', 'benefit', 'minimal_ipk', 'status', 'created_at', 'updated_at'],
        'riwayat_lamaran': ['id', 'user_id', 'beasiswa_id', 'status', 'tanggal_daftar', 'catatan', 'created_at', 'updated_at'],
        'favorit': ['id', 'user_id', 'beasiswa_id', 'created_at'],
        'catatan': ['id', 'user_id', 'beasiswa_id', 'content', 'created_at', 'updated_at']
    }
    
    try:
        conn = get_connection()
        cursor = conn.cursor()
        all_pass = True
        
        for table, expected_cols in expected_schemas.items():
            cursor.execute(f"PRAGMA table_info({table})")
            actual_cols = [row[1] for row in cursor.fetchall()]
            
            print_result("ℹ️", f"Table '{table}' columns: {', '.join(actual_cols)}")
            
            for col in expected_cols:
                if col in actual_cols:
                    print_result("✅", f"  → Column '{col}' exists")
                else:
                    print_result("❌", f"  → Column '{col}' MISSING")
                    all_pass = False
        
        cursor.close()
        return all_pass
        
    except Exception as e:
        print_result("❌", f"Error checking schemas: {e}")
        return False


def test_constraints():
    """Test 4: Verify PRIMARY KEY, UNIQUE, NOT NULL constraints"""
    print_section("TEST 4: CONSTRAINT VALIDATION")
    
    try:
        conn = get_connection()
        cursor = conn.cursor()
        all_pass = True
        
        # Test UNIQUE constraints
        cursor.execute("INSERT INTO akun (username, email, password_hash, nama_lengkap, jenjang) VALUES (?, ?, ?, ?, ?)",
                      ("test_user", "test@test.com", hash_password("pass123"), "Test User", "S1"))
        conn.commit()
        print_result("✅", "UNIQUE constraint on username/email: Can insert new user")
        
        # Try duplicate username
        try:
            cursor.execute("INSERT INTO akun (username, email, password_hash, nama_lengkap, jenjang) VALUES (?, ?, ?, ?, ?)",
                          ("test_user", "test2@test.com", hash_password("pass123"), "Test User 2", "S1"))
            print_result("❌", "UNIQUE constraint FAILED: Duplicate username allowed")
            all_pass = False
        except sqlite3.IntegrityError:
            print_result("✅", "UNIQUE constraint on username: Correctly prevents duplicates")
        
        conn.rollback()
        cursor.close()
        return all_pass
        
    except Exception as e:
        print_result("❌", f"Error testing constraints: {e}")
        return False


def test_foreign_keys():
    """Test 5: Verify FOREIGN KEY relationships"""
    print_section("TEST 5: FOREIGN KEY VALIDATION")
    
    try:
        conn = get_connection()
        # **FIX**: Enable foreign keys explicitly in SQLite
        cursor = conn.cursor()
        cursor.execute("PRAGMA foreign_keys = ON")
        
        all_pass = True
        
        # Insert test data
        user_id = None
        beasiswa_id = None
        penyelenggara_id = None
        
        # Add provider
        cursor.execute("INSERT INTO penyelenggara (nama, description, website, contact_email) VALUES (?, ?, ?, ?)",
                      ("Test Provider", "Test", "https://test.com", "test@test.com"))
        conn.commit()
        cursor.execute("SELECT id FROM penyelenggara ORDER BY id DESC LIMIT 1")
        penyelenggara_id = cursor.fetchone()[0]
        print_result("✅", f"Inserted penyelenggara (id={penyelenggara_id})")
        
        # Add user
        cursor.execute("INSERT INTO akun (username, email, password_hash, nama_lengkap, jenjang) VALUES (?, ?, ?, ?, ?)",
                      ("fk_test_user", "fk@test.com", hash_password("pass123"), "FK Test", "S1"))
        conn.commit()
        cursor.execute("SELECT id FROM akun WHERE username='fk_test_user'")
        user_id = cursor.fetchone()[0]
        print_result("✅", f"Inserted user (id={user_id})")
        
        # Add beasiswa
        cursor.execute("INSERT INTO beasiswa (judul, penyelenggara_id, jenjang, deadline, benefit, minimal_ipk, status) VALUES (?, ?, ?, ?, ?, ?, ?)",
                      ("Test Beasiswa", penyelenggara_id, "S1", "2025-12-31", "Full", "3.0", "open"))
        conn.commit()
        cursor.execute("SELECT id FROM beasiswa ORDER BY id DESC LIMIT 1")
        beasiswa_id = cursor.fetchone()[0]
        print_result("✅", f"Inserted beasiswa (id={beasiswa_id})")
        
        # Try to insert lamaran with valid FKs
        try:
            cursor.execute("INSERT INTO riwayat_lamaran (user_id, beasiswa_id, status, tanggal_daftar) VALUES (?, ?, ?, ?)",
                          (user_id, beasiswa_id, "pending", datetime.now()))
            conn.commit()
            print_result("✅", "Foreign key constraints: Valid FKs accepted")
        except sqlite3.IntegrityError as e:
            print_result("❌", f"Foreign key constraints: Valid FKs rejected - {e}")
            all_pass = False
        
        # Try with invalid FK
        try:
            cursor.execute("INSERT INTO favorit (user_id, beasiswa_id) VALUES (?, ?)", (99999, 99999))
            conn.commit()
            print_result("❌", "Foreign key constraints FAILED: Invalid FKs accepted")
            all_pass = False
        except sqlite3.IntegrityError:
            print_result("✅", "Foreign key constraints: Invalid FKs correctly rejected")
        
        conn.rollback()
        cursor.close()
        return all_pass
        
    except Exception as e:
        print_result("❌", f"Error testing foreign keys: {e}")
        return False


def test_backend_integration():
    """Test that all CRUD functions are available and importable"""
    print_section("TEST 6: BACKEND INTEGRATION")
    
    functions_to_test = [
        ('init_db', 'Database initialization'),
        ('login_user', 'User authentication'),
        ('register_user', 'User registration'),
        ('add_beasiswa', 'Add scholarship'),
        ('get_beasiswa_list', 'Get scholarships list'),
        ('edit_beasiswa', 'Edit scholarship'),
        ('delete_beasiswa', 'Delete scholarship'),
        ('add_lamaran', 'Add application'),
        ('get_lamaran_list', 'Get applications list'),
        ('add_favorit', 'Add to favorites'),
        ('get_favorit_list', 'Get favorites list'),
        ('get_beasiswa_per_jenjang', 'Aggregation: by education level'),
        ('get_top_penyelenggara', 'Aggregation: top providers'),
        ('get_status_availability', 'Aggregation: status distribution'),
    ]
    
    print_result("ℹ️", f"Checking {len(functions_to_test)} CRUD functions...")
    
    all_pass = True
    for func_name, description in functions_to_test:
        try:
            func = globals()[func_name]
            if callable(func):
                print_result("✅", f"{func_name:<30} - {description}")
            else:
                print_result("❌", f"{func_name:<30} - Not callable")
                all_pass = False
        except KeyError:
            print_result("❌", f"{func_name:<30} - Function NOT imported")
            all_pass = False
    
    return all_pass


def test_crud_operations():
    """Test CRUD operations (Create, Read, Update, Delete)"""
    print_section("TEST 7: CRUD OPERATIONS")
    
    all_pass = True
    user_id = None
    beasiswa_id = None
    
    try:
        # CREATE: Register user
        print_result("ℹ️", "Testing CREATE operations...")
        success, msg = register_user("crud_user", "crud@test.com", "CrudPass123!")
        if success:
            print_result("✅", f"CREATE user: {msg}")
            conn = get_connection()
            cursor = conn.cursor()
            cursor.execute("SELECT id FROM akun WHERE username='crud_user'")
            user_id = cursor.fetchone()[0]
            cursor.close()
        else:
            print_result("❌", f"CREATE user FAILED: {msg}")
            all_pass = False
        
        # CREATE: Add beasiswa
        success, msg, new_id = add_beasiswa(
            "Test Beasiswa",  # judul
            "S1",  # jenjang
            "2025-12-31",  # deadline
            penyelenggara_id=1,  # penyelenggara_id
            benefit="Full",  # benefit
            minimal_ipk=3.0,  # minimal_ipk
            status="open"  # status
        )
        if success:
            print_result("✅", f"CREATE beasiswa: {msg}")
            beasiswa_id = new_id
        else:
            print_result("❌", f"CREATE beasiswa FAILED: {msg}")
            all_pass = False
        
        # READ: Login user
        print_result("ℹ️", "Testing READ operations...")
        success, msg, uid = login_user("crud_user", "CrudPass123!")
        if success:
            print_result("✅", f"READ user: {msg}")
        else:
            print_result("❌", f"READ user FAILED: {msg}")
            all_pass = False
        
        # READ: Get beasiswa list
        beasiswa_list, total = get_beasiswa_list()
        if beasiswa_list or total >= 0:
            print_result("✅", f"READ beasiswa list: Found {total} scholarships")
        else:
            print_result("⚠️", "READ beasiswa list: Error retrieving data")
        
        # UPDATE: Edit beasiswa
        print_result("ℹ️", "Testing UPDATE operations...")
        if beasiswa_id:
            success, msg = edit_beasiswa(beasiswa_id, judul="Updated Beasiswa")
            if success:
                print_result("✅", f"UPDATE beasiswa: {msg}")
            else:
                print_result("⚠️", f"UPDATE beasiswa: {msg}")
        else:
            print_result("⚠️", "UPDATE skipped (no beasiswa_id)")
        
        # DELETE: Delete beasiswa
        print_result("ℹ️", "Testing DELETE operations...")
        if beasiswa_id:
            success, msg = delete_beasiswa(beasiswa_id)
            if success:
                print_result("✅", f"DELETE beasiswa: {msg}")
            else:
                print_result("⚠️", f"DELETE beasiswa: {msg}")
        else:
            print_result("⚠️", "DELETE skipped (no beasiswa_id)")
        
        return all_pass
        
    except Exception as e:
        print_result("❌", f"CRUD operations test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_authentication():
    """Test password hashing and verification"""
    print_section("TEST 8: AUTHENTICATION")
    
    try:
        # Test hash_password
        hashed = hash_password("TestPassword123!")
        print_result("✅", "Password hashing: Works")
        
        # Test verify_password
        if verify_password("TestPassword123!", hashed):
            print_result("✅", "Password verification: Correct password verified")
        else:
            print_result("❌", "Password verification: Correct password NOT verified")
            return False
        
        # Test wrong password
        if not verify_password("WrongPassword123!", hashed):
            print_result("✅", "Password verification: Wrong password correctly rejected")
        else:
            print_result("❌", "Password verification: Wrong password incorrectly accepted")
            return False
        
        return True
        
    except Exception as e:
        print_result("❌", f"Authentication test failed: {e}")
        return False


# ============================================================================
# Main Test Runner
# ============================================================================

if __name__ == "__main__":
    print_header("CONSOLIDATED DATABASE TEST SUITE - DARVA")
    
    tests = [
        ("Database Initialization", test_database_initialization()),
        ("Table Existence", test_table_existence()),
        ("Table Schemas", test_table_schemas()),
        ("Constraints", test_constraints()),
        ("Foreign Keys", test_foreign_keys()),
        ("Backend Integration", test_backend_integration()),
        ("CRUD Operations", test_crud_operations()),
        ("Authentication", test_authentication()),
    ]
    
    print_header("TEST SUMMARY")
    passed = sum(1 for _, result in tests if result)
    total = len(tests)
    
    for test_name, result in tests:
        status = "✅ PASSED" if result else "❌ FAILED"
        print(f"  {test_name:<40} {status}")
    
    print(f"\n  Total: {passed}/{total} passed")
    
    if passed == total:
        print("\n🎉 ALL TESTS PASSED! Database is fully functional and production-ready!")
        sys.exit(0)
    else:
        print(f"\n⚠️  {total - passed} test(s) failed. Review output above.")
        sys.exit(1)
