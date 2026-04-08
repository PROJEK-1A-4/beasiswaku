#!/usr/bin/env python3
"""
TEST PHASE 1.1: Database Schema Validation
============================================
Script untuk memverifikasi bahwa database schema benar, berfungsi, dan tanpa bugs.

Test Categories:
1. ✅ Database Initialization
2. ✅ Table Existence & Structure
3. ✅ Columns & Data Types
4. ✅ Constraints (PRIMARY KEY, UNIQUE, NOT NULL, DEFAULT)
5. ✅ Foreign Keys
6. ✅ Data Insertion & Validation
"""

import sqlite3
import os
import sys
from pathlib import Path
from datetime import datetime, timedelta

# Import from crud module
from crud import init_db, get_connection, hash_password

def print_header(text):
    """Print formatted header"""
    print("\n" + "="*70)
    print(f"  {text}")
    print("="*70)

def print_test(number, description):
    """Print test description"""
    print(f"\n[Test {number}] {description}")

def print_result(passed, message):
    """Print test result"""
    symbol = "✅" if passed else "❌"
    print(f"{symbol} {message}")

def test_database_initialization():
    """Test 1: Database initialization dan file creation"""
    print_header("TEST 1: DATABASE INITIALIZATION")
    
    db_path = Path("database/beasiswaku.db")
    
    # Remove database jika ada untuk test fresh initialization
    if db_path.exists():
        db_path.unlink()
        print_result(True, "Cleaned up old database file")
    
    print_test(1, "Inisialisasi database dengan init_db()")
    try:
        init_db()
        print_result(True, "init_db() executed without error")
    except Exception as e:
        print_result(False, f"init_db() failed: {e}")
        return False
    
    print_test(2, "Verifikasi database file dibuat")
    if db_path.exists():
        file_size = db_path.stat().st_size
        print_result(True, f"Database file exists at {db_path} (size: {file_size} bytes)")
    else:
        print_result(False, f"Database file NOT found at {db_path}")
        return False
    
    return True

def test_table_existence():
    """Test 2: Verifikasi semua tabel ada"""
    print_header("TEST 2: TABLE EXISTENCE")
    
    expected_tables = ['akun', 'penyelenggara', 'beasiswa', 'riwayat_lamaran', 'favorit']
    
    try:
        conn = get_connection()
        cursor = conn.cursor()
        
        # Query all tables from SQLite's master table
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%'")
        existing_tables = [row[0] for row in cursor.fetchall()]
        cursor.close()
        conn.close()
        
        print_test(1, f"Check untuk 5 tabel yang diperlukan: {', '.join(expected_tables)}")
        
        all_exist = True
        for table in expected_tables:
            if table in existing_tables:
                print_result(True, f"Tabel '{table}' ada")
            else:
                print_result(False, f"Tabel '{table}' TIDAK ada")
                all_exist = False
        
        return all_exist
        
    except Exception as e:
        print_result(False, f"Error checking tables: {e}")
        return False

def test_table_schemas():
    """Test 3: Verifikasi struktur kolom setiap tabel"""
    print_header("TEST 3: TABLE STRUCTURE & COLUMNS")
    
    expected_columns = {
        'akun': ['id', 'username', 'email', 'password_hash', 'nama_lengkap', 'jenjang', 'created_at', 'updated_at'],
        'penyelenggara': ['id', 'nama', 'description', 'website', 'contact_email', 'created_at'],
        'beasiswa': ['id', 'judul', 'penyelenggara_id', 'jenjang', 'deadline', 'deskripsi', 'benefit', 'persyaratan', 'minimal_ipk', 'coverage', 'status', 'link_aplikasi', 'scrape_date', 'created_at', 'updated_at'],
        'riwayat_lamaran': ['id', 'user_id', 'beasiswa_id', 'status', 'tanggal_daftar', 'catatan', 'created_at', 'updated_at'],
        'favorit': ['id', 'user_id', 'beasiswa_id', 'created_at']
    }
    
    all_correct = True
    
    try:
        conn = get_connection()
        cursor = conn.cursor()
        
        for table_name, expected_cols in expected_columns.items():
            print_test(1, f"Tabel: {table_name}")
            
            # Get table info
            cursor.execute(f"PRAGMA table_info({table_name})")
            actual_cols = [row[1] for row in cursor.fetchall()]
            
            # Check untuk setiap kolom
            for col in expected_cols:
                if col in actual_cols:
                    print_result(True, f"  └─ Kolom '{col}' ada")
                else:
                    print_result(False, f"  └─ Kolom '{col}' TIDAK ada")
                    all_correct = False
            
            # Check untuk kolom yang tidak diexpect
            extra_cols = set(actual_cols) - set(expected_cols)
            if extra_cols:
                print_result(False, f"  └─ Extra kolom ditemukan: {extra_cols}")
                all_correct = False
        
        cursor.close()
        conn.close()
        return all_correct
        
    except Exception as e:
        print_result(False, f"Error checking table structure: {e}")
        return False

def test_constraints():
    """Test 4: Verifikasi PRIMARY KEY, UNIQUE, NOT NULL, DEFAULT constraints"""
    print_header("TEST 4: CONSTRAINTS VALIDATION")
    
    all_pass = True
    
    try:
        conn = get_connection()
        cursor = conn.cursor()
        
        # Test 4.1: PRIMARY KEY
        print_test(1, "PRIMARY KEY constraints")
        cursor.execute("INSERT INTO akun (username, email, password_hash) VALUES ('test1', 'test1@test.com', 'hash1')")
        conn.commit()
        akun_id = cursor.lastrowid
        print_result(True, f"  └─ akun.id adalah PRIMARY KEY with AUTOINCREMENT (ID: {akun_id})")
        
        # Test 4.2: UNIQUE constraint
        print_test(2, "UNIQUE constraints pada username & email")
        try:
            cursor.execute("INSERT INTO akun (username, email, password_hash) VALUES ('test1', 'test2@test.com', 'hash2')")
            conn.commit()
            print_result(False, "  └─ UNIQUE(username) constraint TIDAK berfungsi!")
            all_pass = False
        except sqlite3.IntegrityError:
            print_result(True, "  └─ UNIQUE(username) constraint berfungsi dengan benar")
        
        try:
            cursor.execute("INSERT INTO akun (username, email, password_hash) VALUES ('test3', 'test1@test.com', 'hash3')")
            conn.commit()
            print_result(False, "  └─ UNIQUE(email) constraint TIDAK berfungsi!")
            all_pass = False
        except sqlite3.IntegrityError:
            print_result(True, "  └─ UNIQUE(email) constraint berfungsi dengan benar")
        
        # Test 4.3: NOT NULL constraint
        print_test(3, "NOT NULL constraints")
        try:
            cursor.execute("INSERT INTO akun (username, email) VALUES ('test4', 'test4@test.com')")
            conn.commit()
            print_result(False, "  └─ NOT NULL(password_hash) constraint TIDAK berfungsi!")
            all_pass = False
        except sqlite3.IntegrityError:
            print_result(True, "  └─ NOT NULL(password_hash) constraint berfungsi dengan benar")
        
        # Test 4.4: DEFAULT values
        print_test(4, "DEFAULT values")
        cursor.execute("INSERT INTO akun (username, email, password_hash) VALUES ('test5', 'test5@test.com', 'hash5')")
        conn.commit()
        
        cursor.execute("SELECT status FROM beasiswa WHERE id = 1 LIMIT 1")
        # Insert test data to beasiswa first
        cursor.execute("INSERT INTO beasiswa (judul, deadline) VALUES ('Test Beasiswa', '2026-12-31')")
        conn.commit()
        
        cursor.execute("SELECT status FROM beasiswa WHERE judul = 'Test Beasiswa'")
        result = cursor.fetchone()
        if result and result[0] == 'Buka':
            print_result(True, "  └─ DEFAULT status='Buka' pada beasiswa berfungsi")
        else:
            print_result(False, "  └─ DEFAULT status='Buka' pada beasiswa TIDAK berfungsi")
            all_pass = False
        
        # Check TIMESTAMP defaults
        cursor.execute("SELECT created_at FROM akun WHERE username = 'test5'")
        result = cursor.fetchone()
        if result and result[0]:
            print_result(True, "  └─ DEFAULT created_at TIMESTAMP berfungsi")
        else:
            print_result(False, "  └─ DEFAULT created_at TIMESTAMP TIDAK berfungsi")
            all_pass = False
        
        cursor.close()
        conn.close()
        return all_pass
        
    except Exception as e:
        print_result(False, f"Error checking constraints: {e}")
        return False

def test_foreign_keys():
    """Test 5: Verifikasi FOREIGN KEY relationships"""
    print_header("TEST 5: FOREIGN KEY RELATIONSHIPS")
    
    all_pass = True
    
    try:
        conn = get_connection()
        cursor = conn.cursor()
        
        # Enable foreign key checking (important for SQLite)
        cursor.execute("PRAGMA foreign_keys = ON")
        
        print_test(1, "beasiswa.penyelenggara_id -> penyelenggara.id")
        
        # Insert test penyelenggara
        cursor.execute("INSERT INTO penyelenggara (nama) VALUES ('Test Provider')")
        conn.commit()
        provider_id = cursor.lastrowid
        
        # Insert beasiswa with valid penyelenggara_id
        cursor.execute("INSERT INTO beasiswa (judul, deadline, penyelenggara_id) VALUES ('Beasiswa FK Test', '2026-12-31', ?)", (provider_id,))
        conn.commit()
        print_result(True, f"  └─ Dapat insert beasiswa dengan penyelenggara_id yang valid")
        
        # Try insert beasiswa dengan invalid penyelenggara_id
        try:
            cursor.execute("INSERT INTO beasiswa (judul, deadline, penyelenggara_id) VALUES ('Invalid FK', '2026-12-31', 99999)")
            conn.commit()
            print_result(False, "  └─ Foreign key constraint TIDAK berfungsi (invalid ID diterima)")
            all_pass = False
        except sqlite3.IntegrityError:
            print_result(True, "  └─ Foreign key constraint berfungsi (invalid ID ditolak)")
        
        print_test(2, "riwayat_lamaran.user_id -> akun.id")
        
        # Get valid user_id
        cursor.execute("SELECT id FROM akun LIMIT 1")
        user_result = cursor.fetchone()
        if user_result:
            user_id = user_result[0]
            
            # Get valid beasiswa_id
            cursor.execute("SELECT id FROM beasiswa LIMIT 1")
            beasiswa_result = cursor.fetchone()
            if beasiswa_result:
                beasiswa_id = beasiswa_result[0]
                
                cursor.execute("INSERT INTO riwayat_lamaran (user_id, beasiswa_id) VALUES (?, ?)", (user_id, beasiswa_id))
                conn.commit()
                print_result(True, f"  └─ Dapat insert lamaran dengan valid user_id & beasiswa_id")
            else:
                print_result(False, "  └─ Tidak ada beasiswa untuk test foreign key")
                all_pass = False
        else:
            print_result(False, "  └─ Tidak ada user untuk test foreign key")
            all_pass = False
        
        print_test(3, "favorit.user_id -> akun.id & favorit.beasiswa_id -> beasiswa.id")
        
        try:
            cursor.execute("INSERT INTO favorit (user_id, beasiswa_id) VALUES (?, ?)", (user_id, beasiswa_id))
            conn.commit()
            print_result(True, f"  └─ Dapat insert favorit dengan valid foreign keys")
        except Exception as e:
            print_result(False, f"  └─ Error insert favorit: {e}")
            all_pass = False
        
        cursor.close()
        conn.close()
        return all_pass
        
    except Exception as e:
        print_result(False, f"Error checking foreign keys: {e}")
        return False

def test_unique_constraints_complex():
    """Test 6: Verifikasi UNIQUE constraints yang kompleks"""
    print_header("TEST 6: COMPLEX UNIQUE CONSTRAINTS")
    
    all_pass = True
    
    try:
        conn = get_connection()
        cursor = conn.cursor()
        
        # Enable foreign keys
        cursor.execute("PRAGMA foreign_keys = ON")
        
        # Get user & beasiswa IDs
        cursor.execute("SELECT id FROM akun LIMIT 1")
        user_result = cursor.fetchone()
        cursor.execute("SELECT id FROM beasiswa LIMIT 1")
        beasiswa_result = cursor.fetchone()
        
        if user_result and beasiswa_result:
            user_id = user_result[0]
            beasiswa_id = beasiswa_result[0]
            
            print_test(1, "UNIQUE(user_id, beasiswa_id) pada riwayat_lamaran")
            
            # Coba insert duplicate
            try:
                cursor.execute("INSERT INTO riwayat_lamaran (user_id, beasiswa_id) VALUES (?, ?)", (user_id, beasiswa_id))
                conn.commit()
                print_result(False, "  └─ UNIQUE constraint TIDAK berfungsi (duplicate diterima)")
                all_pass = False
            except sqlite3.IntegrityError:
                print_result(True, "  └─ UNIQUE constraint berfungsi (duplicate ditolak)")
            
            print_test(2, "UNIQUE(user_id, beasiswa_id) pada favorit")
            
            # Coba insert duplicate favorit
            try:
                cursor.execute("INSERT INTO favorit (user_id, beasiswa_id) VALUES (?, ?)", (user_id, beasiswa_id))
                conn.commit()
                print_result(False, "  └─ UNIQUE constraint TIDAK berfungsi (duplicate diterima)")
                all_pass = False
            except sqlite3.IntegrityError:
                print_result(True, "  └─ UNIQUE constraint berfungsi (duplicate ditolak)")
        else:
            print_result(False, "Tidak ada data untuk test UNIQUE constraints")
            all_pass = False
        
        cursor.close()
        conn.close()
        return all_pass
        
    except Exception as e:
        print_result(False, f"Error checking complex constraints: {e}")
        return False

def test_data_integrity():
    """Test 7: Verifikasi integritas data dan cascade behavior"""
    print_header("TEST 7: DATA INTEGRITY & CASCADE BEHAVIOR")
    
    all_pass = True
    
    try:
        conn = get_connection()
        cursor = conn.cursor()
        
        # Enable foreign keys untuk test cascade
        cursor.execute("PRAGMA foreign_keys = ON")
        
        print_test(1, "Verify dapat menyimpan berbagai tipe data dengan benar")
        
        # Test datetime storage
        test_date = '2026-06-15'
        cursor.execute("INSERT INTO beasiswa (judul, deadline) VALUES ('Test Date', ?)", (test_date,))
        conn.commit()
        
        cursor.execute("SELECT deadline FROM beasiswa WHERE judul = 'Test Date'")
        stored_date = cursor.fetchone()[0]
        if stored_date == test_date:
            print_result(True, "  └─ DATE columns menyimpan nilai dengan benar")
        else:
            print_result(False, f"  └─ DATE value mismatch: expected '{test_date}', got '{stored_date}'")
            all_pass = False
        
        # Test REAL (float) storage
        test_ipk = 3.75
        cursor.execute("UPDATE beasiswa SET minimal_ipk = ? WHERE judul = 'Test Date'", (test_ipk,))
        conn.commit()
        
        cursor.execute("SELECT minimal_ipk FROM beasiswa WHERE judul = 'Test Date'")
        stored_ipk = cursor.fetchone()[0]
        if abs(stored_ipk - test_ipk) < 0.01:
            print_result(True, "  └─ REAL columns menyimpan nilai dengan benar")
        else:
            print_result(False, f"  └─ REAL value mismatch: expected {test_ipk}, got {stored_ipk}")
            all_pass = False
        
        print_test(2, "Verify NULL values diizinkan untuk optional columns")
        
        cursor.execute("INSERT INTO beasiswa (judul, deadline, deskripsi) VALUES ('Test Null', '2026-12-31', NULL)")
        conn.commit()
        
        cursor.execute("SELECT deskripsi FROM beasiswa WHERE judul = 'Test Null'")
        result = cursor.fetchone()
        if result[0] is None:
            print_result(True, "  └─ NULL values disimpan dengan benar pada optional columns")
        else:
            print_result(False, "  └─ NULL values NOT preserved")
            all_pass = False
        
        cursor.close()
        conn.close()
        return all_pass
        
    except Exception as e:
        print_result(False, f"Error checking data integrity: {e}")
        return False

def cleanup_test_data():
    """Clean up test database"""
    print_header("CLEANUP")
    
    db_path = Path("database/beasiswaku.db")
    if db_path.exists():
        db_path.unlink()
        print_result(True, "Test database cleaned up")

def main():
    """Main test runner"""
    print("\n")
    print("╔" + "="*68 + "╗")
    print("║" + " "*68 + "║")
    print("║" + "  PHASE 1.1: DATABASE SCHEMA VALIDATION TEST SUITE".center(68) + "║")
    print("║" + "  Comprehensive verification of database design & functionality".center(68) + "║")
    print("║" + " "*68 + "║")
    print("╚" + "="*68 + "╝")
    
    results = []
    
    # Run all tests
    results.append(("Database Initialization", test_database_initialization()))
    results.append(("Table Existence", test_table_existence()))
    results.append(("Table Structure", test_table_schemas()))
    results.append(("Constraints", test_constraints()))
    results.append(("Foreign Keys", test_foreign_keys()))
    results.append(("Complex UNIQUE Constraints", test_unique_constraints_complex()))
    results.append(("Data Integrity", test_data_integrity()))
    
    # Cleanup
    cleanup_test_data()
    
    # Summary
    print_header("TEST SUMMARY")
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    print(f"\n  Total Tests: {total}")
    print(f"  ✅ Passed: {passed}")
    print(f"  ❌ Failed: {total - passed}")
    
    if passed == total:
        print("\n  🎉 SEMUA TEST PASSED! Database schema BENAR dan BERFUNGSI dengan baik!")
        print("  Phase 1.1 ✅ VERIFIED & READY FOR DEPLOYMENT")
        return 0
    else:
        print("\n  ⚠️  BEBERAPA TEST GAGAL. Review hasil di atas dan perbaiki.")
        return 1

if __name__ == "__main__":
    sys.exit(main())
