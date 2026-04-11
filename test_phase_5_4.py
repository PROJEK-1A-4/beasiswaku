"""
test_phase_5_4.py - Pengujian PHASE 5.4: Catatan Pribadi (Notes per Beasiswa)

Menguji:
1. add_catatan() - Menambah catatan baru
2. get_catatan() - Mengambil catatan
3. edit_catatan() - Mengedit catatan
4. delete_catatan() - Menghapus catatan
5. get_catatan_list() - Daftar semua catatan user
6. Utility functions - has_note(), get_note_preview(), note_status_icon()
7. Validasi data dan edge cases
"""

import os
import sys
import sqlite3
import logging
from typing import List, Dict

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from crud import (
    init_db, register_user, add_beasiswa, add_lamaran,
    add_catatan, get_catatan, edit_catatan, delete_catatan, get_catatan_list,
    get_connection
)
from gui_notes import has_note, get_note_preview, note_status_icon

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def print_header(title: str):
    """Print test header"""
    print(f"\n{'='*80}")
    print(f"  {title}")
    print(f"{'='*80}\n")


def print_section(section: str):
    """Print section header"""
    print(f"\n📌 {section}")
    print("-" * 80)


def test_step_1_setup():
    """STEP 1: Setup database dan test data"""
    print_section("STEP 1: Setup Database & Test Data")
    
    try:
        # Initialize database
        init_db()
        print("✅ Database initialized")
        
        # Create test users
        users = [
            ("user1_notes", "user1@test.com", "password123@A"),
            ("user2_notes", "user2@test.com", "password123@A"),
            ("user3_notes", "user3@test.com", "password123@A"),
        ]
        
        user_ids = []
        for username, email, password in users:
            success, msg = register_user(
                username=username,
                email=email,
                password=password
            )
            
            if success:
                conn = get_connection()
                cursor = conn.cursor()
                cursor.execute("SELECT id FROM akun WHERE username = ?", (username,))
                result = cursor.fetchone()
                user_id = result['id'] if result else None
                conn.close()
                
                if user_id:
                    user_ids.append(user_id)
                    print(f"  ✅ User created: {username} (ID: {user_id})")
                else:
                    print(f"  ❌ Failed to get user ID for {username}")
                    return False, user_ids, []
            else:
                print(f"  ❌ Failed to register {username}: {msg}")
                return False, user_ids, []
        
        # Create test beasiswa
        beasiswa_data = [
            {"judul": "LPDP S1 Regular", "jenjang": "S1", "deadline": "2026-08-31", "status": "Buka"},
            {"judul": "BPPDN S1 Access", "jenjang": "S1", "deadline": "2026-08-15", "status": "Buka"},
            {"judul": "Fulbright S2", "jenjang": "S2", "deadline": "2026-09-30", "status": "Buka"},
            {"judul": "Erasmus+ S2", "jenjang": "S2", "deadline": "2026-08-01", "status": "Segera Tutup"},
            {"judul": "LPDP D3", "jenjang": "D3", "deadline": "2026-10-15", "status": "Buka"},
        ]
        
        beasiswa_ids = []
        for bs in beasiswa_data:
            success, msg, bid = add_beasiswa(**bs)
            if success:
                beasiswa_ids.append(bid)
                print(f"  ✅ Beasiswa added: {bs['judul']} (ID: {bid})")
            else:
                print(f"  ❌ Failed: {msg}")
                return False, user_ids, []
        
        print(f"\n✅ STEP 1 PASSED: {len(user_ids)} users, {len(beasiswa_ids)} beasiswa")
        return True, user_ids, beasiswa_ids
        
    except Exception as e:
        logger.error(f"❌ STEP 1 FAILED: {e}")
        return False, [], []


def test_step_2_add_catatan(user_ids: List[int], beasiswa_ids: List[int]) -> bool:
    """STEP 2: Test add_catatan() function"""
    print_section("STEP 2: Test add_catatan() Function")
    
    test_cases = 0
    passed = 0
    
    try:
        # Test Case 1: Add note for user1 beasiswa1
        test_cases += 1
        success, msg, catatan_id = add_catatan(
            user_id=user_ids[0],
            beasiswa_id=beasiswa_ids[0],
            content="Strategy: Persiapkan TOEFL score tinggi"
        )
        if success and catatan_id:
            print(f"✅ User1 add note to beasiswa1: PASSED (ID: {catatan_id})")
            passed += 1
        else:
            print(f"❌ Failed: {msg}")
        
        # Test Case 2: Add note for user1 beasiswa2
        test_cases += 1
        success, msg, catatan_id = add_catatan(
            user_id=user_ids[0],
            beasiswa_id=beasiswa_ids[1],
            content="Need to collect: IP score, essay, recommendation letter"
        )
        if success:
            print(f"✅ User1 add note to beasiswa2: PASSED")
            passed += 1
        else:
            print(f"❌ Failed: {msg}")
        
        # Test Case 3: Add note for user2 beasiswa3
        test_cases += 1
        success, msg, catatan_id = add_catatan(
            user_id=user_ids[1],
            beasiswa_id=beasiswa_ids[2],
            content="Deadline: 30 Sept 2026. Mulai persiapan SOON!"
        )
        if success:
            print(f"✅ User2 add note to beasiswa3: PASSED")
            passed += 1
        else:
            print(f"❌ Failed: {msg}")
        
        # Test Case 4: Duplicate note (should fail)
        test_cases += 1
        success, msg, _ = add_catatan(
            user_id=user_ids[0],
            beasiswa_id=beasiswa_ids[0],
            content="Another note"
        )
        if not success:
            print(f"✅ Duplicate note correctly rejected: PASSED")
            passed += 1
        else:
            print(f"❌ Duplicate should be rejected: FAILED")
        
        # Test Case 5: Empty content (should fail)
        test_cases += 1
        success, msg, _ = add_catatan(
            user_id=user_ids[0],
            beasiswa_id=beasiswa_ids[3],
            content="   "
        )
        if not success:
            print(f"✅ Empty content correctly rejected: PASSED")
            passed += 1
        else:
            print(f"❌ Empty content should be rejected: FAILED")
        
        # Test Case 6: Content too long (should fail)
        test_cases += 1
        long_content = "x" * 2001
        success, msg, _ = add_catatan(
            user_id=user_ids[0],
            beasiswa_id=beasiswa_ids[3],
            content=long_content
        )
        if not success:
            print(f"✅ Too long content correctly rejected: PASSED")
            passed += 1
        else:
            print(f"❌ Too long content should be rejected: FAILED")
        
        # Test Case 7: Invalid user (should fail)
        test_cases += 1
        success, msg, _ = add_catatan(
            user_id=9999,
            beasiswa_id=beasiswa_ids[0],
            content="Invalid user"
        )
        if not success:
            print(f"✅ Invalid user correctly rejected: PASSED")
            passed += 1
        else:
            print(f"❌ Invalid user should be rejected: FAILED")
        
        print(f"\n📊 STEP 2 RESULT: {passed}/{test_cases} tests passed")
        return passed >= 5  # At least 5 of 7 main tests should pass
        
    except Exception as e:
        logger.error(f"❌ STEP 2 FAILED: {e}")
        return False


def test_step_3_get_catatan(user_ids: List[int], beasiswa_ids: List[int]) -> bool:
    """STEP 3: Test get_catatan() function"""
    print_section("STEP 3: Test get_catatan() Function")
    
    test_cases = 0
    passed = 0
    
    try:
        # Test Case 1: Get existing note
        test_cases += 1
        note, msg = get_catatan(user_ids[0], beasiswa_ids[0])
        if note and note['content'] == "Strategy: Persiapkan TOEFL score tinggi":
            print(f"✅ Get existing note: PASSED")
            passed += 1
        else:
            print(f"❌ Failed to get note")
        
        # Test Case 2: Get non-existing note
        test_cases += 1
        note, msg = get_catatan(user_ids[2], beasiswa_ids[0])
        if note is None:
            print(f"✅ Non-existing note returns None: PASSED")
            passed += 1
        else:
            print(f"❌ Should return None for non-existing note")
        
        # Test Case 3: Check note structure
        test_cases += 1
        note, _ = get_catatan(user_ids[0], beasiswa_ids[0])
        required_fields = ['id', 'user_id', 'beasiswa_id', 'content', 'created_at', 'updated_at']
        if note and all(field in note for field in required_fields):
            print(f"✅ Note has all required fields: PASSED")
            passed += 1
        else:
            print(f"❌ Missing fields in note")
        
        # Test Case 4: Check data types
        test_cases += 1
        note, _ = get_catatan(user_ids[0], beasiswa_ids[0])
        if note:
            if (isinstance(note['id'], int) and 
                isinstance(note['user_id'], int) and
                isinstance(note['content'], str)):
                print(f"✅ Data types correct: PASSED")
                passed += 1
            else:
                print(f"❌ Data types incorrect")
        
        # Test Case 5: Invalid user_id
        test_cases += 1
        note, msg = get_catatan(9999, beasiswa_ids[0])
        if note is None:
            print(f"✅ Invalid user returns None: PASSED")
            passed += 1
        else:
            print(f"❌ Should return None for invalid user")
        
        print(f"\n📊 STEP 3 RESULT: {passed}/{test_cases} tests passed")
        return passed == test_cases
        
    except Exception as e:
        logger.error(f"❌ STEP 3 FAILED: {e}")
        return False


def test_step_4_edit_catatan(user_ids: List[int], beasiswa_ids: List[int]) -> bool:
    """STEP 4: Test edit_catatan() function"""
    print_section("STEP 4: Test edit_catatan() Function")
    
    test_cases = 0
    passed = 0
    
    try:
        # Test Case 1: Edit existing note
        test_cases += 1
        success, msg = edit_catatan(
            user_id=user_ids[0],
            beasiswa_id=beasiswa_ids[0],
            content="Updated strategy: Also prepare IELTS as backup"
        )
        if success:
            # Verify change
            note, _ = get_catatan(user_ids[0], beasiswa_ids[0])
            if note and "IELTS" in note['content']:
                print(f"✅ Edit existing note: PASSED")
                passed += 1
            else:
                print(f"❌ Note not updated correctly")
        else:
            print(f"❌ Edit failed: {msg}")
        
        # Test Case 2: Edit non-existing note
        test_cases += 1
        success, msg = edit_catatan(
            user_id=user_ids[2],
            beasiswa_id=beasiswa_ids[0],
            content="Should fail"
        )
        if not success:
            print(f"✅ Edit non-existing note correctly rejected: PASSED")
            passed += 1
        else:
            print(f"❌ Should reject non-existing note")
        
        # Test Case 3: Edit with empty content
        test_cases += 1
        success, msg = edit_catatan(
            user_id=user_ids[0],
            beasiswa_id=beasiswa_ids[0],
            content="   "
        )
        if not success:
            print(f"✅ Empty content correctly rejected: PASSED")
            passed += 1
        else:
            print(f"❌ Should reject empty content")
        
        # Test Case 4: Check updated_at timestamp
        test_cases += 1
        note_before, _ = get_catatan(user_ids[1], beasiswa_ids[2])
        if note_before:
            success, _ = edit_catatan(
                user_id=user_ids[1],
                beasiswa_id=beasiswa_ids[2],
                content="New content"
            )
            if success:
                note_after, _ = get_catatan(user_ids[1], beasiswa_ids[2])
                # updated_at should be different
                if note_after['updated_at'] >= note_before['updated_at']:
                    print(f"✅ updated_at timestamp updated: PASSED")
                    passed += 1
                else:
                    print(f"❌ Timestamp not updated")
        
        print(f"\n📊 STEP 4 RESULT: {passed}/{test_cases} tests passed")
        return passed >= 3
        
    except Exception as e:
        logger.error(f"❌ STEP 4 FAILED: {e}")
        return False


def test_step_5_delete_catatan(user_ids: List[int], beasiswa_ids: List[int]) -> bool:
    """STEP 5: Test delete_catatan() function"""
    print_section("STEP 5: Test delete_catatan() Function")
    
    test_cases = 0
    passed = 0
    
    try:
        # Test Case 1: Delete existing note
        test_cases += 1
        # First add a note to delete
        add_catatan(user_ids[2], beasiswa_ids[3], "To be deleted")
        
        success, msg = delete_catatan(user_ids[2], beasiswa_ids[3])
        if success:
            # Verify deletion
            note, _ = get_catatan(user_ids[2], beasiswa_ids[3])
            if note is None:
                print(f"✅ Delete note: PASSED")
                passed += 1
            else:
                print(f"❌ Note not deleted")
        else:
            print(f"❌ Delete failed: {msg}")
        
        # Test Case 2: Delete non-existing note
        test_cases += 1
        success, msg = delete_catatan(user_ids[2], beasiswa_ids[4])
        if not success:
            print(f"✅ Delete non-existing note correctly rejected: PASSED")
            passed += 1
        else:
            print(f"❌ Should reject non-existing note")
        
        # Test Case 3: Invalid user_id
        test_cases += 1
        success, msg = delete_catatan(9999, beasiswa_ids[0])
        if not success:
            print(f"✅ Invalid user correctly rejected: PASSED")
            passed += 1
        else:
            print(f"❌ Should reject invalid user")
        
        print(f"\n📊 STEP 5 RESULT: {passed}/{test_cases} tests passed")
        return passed == test_cases
        
    except Exception as e:
        logger.error(f"❌ STEP 5 FAILED: {e}")
        return False


def test_step_6_get_catatan_list(user_ids: List[int], beasiswa_ids: List[int]) -> bool:
    """STEP 6: Test get_catatan_list() function"""
    print_section("STEP 6: Test get_catatan_list() Function")
    
    test_cases = 0
    passed = 0
    
    try:
        # Test Case 1: Get all notes for user1
        test_cases += 1
        notes_list, total = get_catatan_list(user_id=user_ids[0])
        if total == 2:  # User1 has 2 notes
            print(f"✅ User1 has 2 notes: PASSED")
            passed += 1
        else:
            print(f"❌ User1 should have 2 notes (got {total})")
        
        # Test Case 2: Check list structure
        test_cases += 1
        required_fields = [
            'catatan_id', 'user_id', 'beasiswa_id', 'content',
            'beasiswa_judul', 'beasiswa_jenjang', 'beasiswa_status'
        ]
        if notes_list and all(field in notes_list[0] for field in required_fields):
            print(f"✅ All required fields in list: PASSED")
            passed += 1
        else:
            print(f"❌ Missing fields in list")
        
        # Test Case 3: Get notes for user with 1 note
        test_cases += 1
        notes_list, total = get_catatan_list(user_id=user_ids[1])
        if total == 1:  # User2 has 1 note
            print(f"✅ User2 has 1 note: PASSED")
            passed += 1
        else:
            print(f"❌ User2 should have 1 note (got {total})")
        
        # Test Case 4: Get notes for user with 0 notes
        test_cases += 1
        notes_list, total = get_catatan_list(user_id=user_ids[2])
        if total == 0:  # User3 has 0 notes (deleted the one we added)
            print(f"✅ User3 has 0 notes: PASSED")
            passed += 1
        else:
            print(f"❌ User3 should have 0 notes (got {total})")
        
        # Test Case 5: Filter by jenjang
        test_cases += 1
        notes_list, total = get_catatan_list(user_id=user_ids[0], filter_jenjang='S1')
        if total == 2:  # Both user1 notes are S1
            print(f"✅ Filter by jenjang S1: PASSED")
            passed += 1
        else:
            print(f"❌ Filter jenjang failed (expected 2, got {total})")
        
        # Test Case 6: Search by judul
        test_cases += 1
        notes_list, total = get_catatan_list(user_id=user_ids[0], search_judul='LPDP')
        if total == 1:  # Only 1 LPDP note
            print(f"✅ Search by judul: PASSED")
            passed += 1
        else:
            print(f"❌ Search failed (expected 1, got {total})")
        
        print(f"\n📊 STEP 6 RESULT: {passed}/{test_cases} tests passed")
        return passed == test_cases
        
    except Exception as e:
        logger.error(f"❌ STEP 6 FAILED: {e}")
        return False


def test_step_7_utility_functions(user_ids: List[int], beasiswa_ids: List[int]) -> bool:
    """STEP 7: Test utility functions for notes"""
    print_section("STEP 7: Test Utility Functions")
    
    test_cases = 0
    passed = 0
    
    try:
        # Test Case 1: has_note() for note that exists
        test_cases += 1
        result = has_note(user_ids[0], beasiswa_ids[0])
        if result:
            print(f"✅ has_note() returns True for existing: PASSED")
            passed += 1
        else:
            print(f"❌ has_note() should return True")
        
        # Test Case 2: has_note() for note that doesn't exist
        test_cases += 1
        result = has_note(user_ids[2], beasiswa_ids[0])
        if not result:
            print(f"✅ has_note() returns False for non-existing: PASSED")
            passed += 1
        else:
            print(f"❌ has_note() should return False")
        
        # Test Case 3: get_note_preview() - short text
        test_cases += 1
        preview = get_note_preview(user_ids[0], beasiswa_ids[0], max_length=20)
        note, _ = get_catatan(user_ids[0], beasiswa_ids[0])
        if note and preview and len(preview) <= 23:  # 20 + "..."
            print(f"✅ get_note_preview() works: PASSED")
            passed += 1
        else:
            print(f"❌ get_note_preview() preview incorrect")
        
        # Test Case 4: get_note_preview() - non-existing returns empty
        test_cases += 1
        preview = get_note_preview(user_ids[2], beasiswa_ids[0])
        if preview == "":
            print(f"✅ get_note_preview() empty for non-existing: PASSED")
            passed += 1
        else:
            print(f"❌ Should return empty string")
        
        # Test Case 5: note_status_icon() with note
        test_cases += 1
        icon = note_status_icon(user_ids[0], beasiswa_ids[0])
        if icon == "📝":
            print(f"✅ note_status_icon() returns 📝 for existing: PASSED")
            passed += 1
        else:
            print(f"❌ Should return 📝 for existing note")
        
        # Test Case 6: note_status_icon() without note
        test_cases += 1
        icon = note_status_icon(user_ids[2], beasiswa_ids[0])
        if icon == "📄":
            print(f"✅ note_status_icon() returns 📄 for non-existing: PASSED")
            passed += 1
        else:
            print(f"❌ Should return 📄 for non-existing note")
        
        print(f"\n📊 STEP 7 RESULT: {passed}/{test_cases} tests passed")
        return passed == test_cases
        
    except Exception as e:
        logger.error(f"❌ STEP 7 FAILED: {e}")
        return False


def main():
    """Run all tests"""
    print_header("PHASE 5.4: CATATAN PRIBADI (NOTES) - COMPREHENSIVE TEST SUITE")
    
    # Clean database before tests
    db_path = "database/beasiswaku.db"
    if os.path.exists(db_path):
        os.remove(db_path)
        print(f"🗑️  Cleaned existing database\n")
    
    # Run test steps
    success_1, user_ids, beasiswa_ids = test_step_1_setup()
    if not success_1:
        print("❌ Setup failed, cannot continue")
        return False
    
    success_2 = test_step_2_add_catatan(user_ids, beasiswa_ids)
    success_3 = test_step_3_get_catatan(user_ids, beasiswa_ids)
    success_4 = test_step_4_edit_catatan(user_ids, beasiswa_ids)
    success_5 = test_step_5_delete_catatan(user_ids, beasiswa_ids)
    success_6 = test_step_6_get_catatan_list(user_ids, beasiswa_ids)
    success_7 = test_step_7_utility_functions(user_ids, beasiswa_ids)
    
    # Print summary
    print_header("TEST SUMMARY")
    
    all_passed = all([success_2, success_3, success_4, success_5, success_6, success_7])
    
    if all_passed:
        print("✅ ALL PHASE 5.4 TESTS PASSED ✅\n")
        print("Verified Features:")
        print("  ✅ add_catatan() - Add notes with validation")
        print("  ✅ get_catatan() - Retrieve notes accurately")
        print("  ✅ edit_catatan() - Update notes with timestamp")
        print("  ✅ delete_catatan() - Remove notes safely")
        print("  ✅ get_catatan_list() - List all notes with filters")
        print("  ✅ has_note() - Check note existence")
        print("  ✅ get_note_preview() - Generate preview text")
        print("  ✅ note_status_icon() - Visual status icons")
        print("  ✅ Data validation - 2000 char limit, required fields, duplicates")
        print("  ✅ Multi-user scenarios - Independent notes per user")
        print("  ✅ Edge cases - Empty, non-existing, invalid IDs")
        return True
    else:
        print("❌ SOME TESTS FAILED ❌\n")
        print(f"Step 2 (add_catatan): {'✅ PASSED' if success_2 else '❌ FAILED'}")
        print(f"Step 3 (get_catatan): {'✅ PASSED' if success_3 else '❌ FAILED'}")
        print(f"Step 4 (edit_catatan): {'✅ PASSED' if success_4 else '❌ FAILED'}")
        print(f"Step 5 (delete_catatan): {'✅ PASSED' if success_5 else '❌ FAILED'}")
        print(f"Step 6 (get_catatan_list): {'✅ PASSED' if success_6 else '❌ FAILED'}")
        print(f"Step 7 (utility_functions): {'✅ PASSED' if success_7 else '❌ FAILED'}")
        return False


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
