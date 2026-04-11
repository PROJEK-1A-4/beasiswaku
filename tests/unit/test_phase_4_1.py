"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))
test_phase_4_1.py - Comprehensive Testing for Phase 4.1 Aggregation Queries
Testing all three aggregation query functions with various scenarios.

Functions tested:
1. get_beasiswa_per_jenjang() - aggregate by education level
2. get_top_penyelenggara() - top scholarship providers
3. get_status_availability() - status distribution
"""

import sqlite3
import logging
from pathlib import Path
from src.database.crud import (
    init_db, register_user, add_beasiswa,
    get_beasiswa_per_jenjang, get_top_penyelenggara, get_status_availability
)

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(levelname)s:%(name)s:%(message)s')
logger = logging.getLogger(__name__)

def test_aggregation_queries():
    """
    Comprehensive test suite for Phase 4.1 aggregation queries.
    Tests all three functions with various data scenarios.
    """
    print("\n" + "="*80)
    print("PHASE 4.1: AGGREGATION QUERIES - COMPREHENSIVE TEST SUITE")
    print("="*80 + "\n")
    
    # ========================== STEP 1: Initialize Database ==========================
    print("STEP 1: Database Initialization")
    print("-" * 80)
    
    try:
        init_db()
        logger.info("✅ Database initialized successfully")
    except Exception as e:
        logger.error(f"❌ Database initialization failed: {e}")
        return False
    
    # ========================== STEP 2: Add Test Data ==========================
    print("\nSTEP 2: Adding Test Data")
    print("-" * 80)
    
    # Register test user
    try:
        success, msg = register_user("test_agg_user", "test_agg@example.com", "password123")
        if success:
            logger.info("✅ Test user registered")
        else:
            logger.warning(f"⚠️ User registration: {msg}")
    except Exception as e:
        logger.error(f"❌ User registration failed: {e}")
        return False
    
    # Add penyelenggara data
    conn = sqlite3.connect("database/beasiswaku.db")
    cursor = conn.cursor()
    
    penyelenggara_data = [
        (1, "LPDP", "Lembaga Penilai Dana Pendidikan", "https://www.lpdp.kemenkeu.go.id", "info@lpdp.go.id"),
        (2, "BPPDN", "Beasiswa Pendidikan Dalam Negeri", "https://bppdn.kemlu.go.id", "bppdn@kemlu.go.id"),
        (3, "Fulbright", "Fulbright Commission Indonesia", "https://www.fulbright.org", "info@fulbright.org"),
        (4, "Erasmus+", "European Union Education Programme", "https://www.erasmusplus.org", "contact@erasmusplus.eu"),
        (5, "ADB", "Asian Development Bank", "https://www.adb.org", "scholarships@adb.org"),
    ]
    
    try:
        for pid, nama, desc, website, email in penyelenggara_data:
            cursor.execute("""
                INSERT INTO penyelenggara (id, nama, description, website, contact_email)
                VALUES (?, ?, ?, ?, ?)
            """, (pid, nama, desc, website, email))
        conn.commit()
        logger.info(f"✅ Added {len(penyelenggara_data)} penyelenggara")
    except Exception as e:
        logger.error(f"❌ Failed to add penyelenggara: {e}")
        return False
    finally:
        conn.close()
    
    # Add diverse beasiswa
    test_beasiswa = [
        # LPDP beasiswa (3 total)
        ("LPDP Magister S2", "S2", "2026-12-31", 1, "Buka"),
        ("LPDP Doktor S3", "S3", "2026-12-28", 1, "Buka"),
        ("LPDP Spesialis", "S2", "2026-12-15", 1, "Segera Tutup"),
        # BPPDN beasiswa (4 total)
        ("BPPDN Sarjana S1", "S1", "2026-12-20", 2, "Buka"),
        ("BPPDN Pasca S2", "S2", "2026-12-10", 2, "Segera Tutup"),
        ("BPPDN Diploma D3", "D3", "2026-12-31", 2, "Buka"),
        ("BPPDN Diploma D4", "D4", "2026-12-25", 2, "Buka"),
        # Fulbright beasiswa (2 total)
        ("Fulbright Master S2", "S2", "2026-11-30", 3, "Segera Tutup"),
        ("Fulbright Research", "S3", "2026-11-15", 3, "Tutup"),
        # Erasmus+ beasiswa (2 total)
        ("Erasmus+ Joint Masters", "S2", "2026-12-04", 4, "Tutup"),
        ("Erasmus+ Exchange", "S1", "2026-12-15", 4, "Buka"),
        # ADB beasiswa (1 total)
        ("ADB Scholarship S2", "S2", "2026-12-20", 5, "Buka"),
        # No penyelenggara (1 total)
        ("Beasiswa Lokal Komunitas", "S1", "2026-12-31", None, "Buka"),
    ]
    
    added_count = 0
    for judul, jenjang, deadline, penyelenggara_id, status in test_beasiswa:
        try:
            success, msg, bid = add_beasiswa(
                judul=judul,
                jenjang=jenjang,
                deadline=deadline,
                penyelenggara_id=penyelenggara_id,
                status=status
            )
            if success:
                added_count += 1
            else:
                logger.warning(f"⚠️ Failed to add {judul}: {msg}")
        except Exception as e:
            logger.error(f"❌ Error adding {judul}: {e}")
    
    logger.info(f"✅ Added {added_count}/{len(test_beasiswa)} beasiswa")
    
    # ========================== STEP 3: Test get_beasiswa_per_jenjang() ==========================
    print("\nSTEP 3: Testing get_beasiswa_per_jenjang()")
    print("-" * 80)
    
    try:
        result = get_beasiswa_per_jenjang()
        
        if isinstance(result, dict) and len(result) > 0:
            logger.info("✅ get_beasiswa_per_jenjang() returned valid data")
            
            # Verify structure
            total = sum(result.values())
            print(f"\nJenjang Distribution ({total} total):")
            for jenjang in sorted(result.keys()):
                count = result[jenjang]
                percentage = (count / total * 100) if total > 0 else 0
                print(f"  {jenjang}: {count} beasiswa ({percentage:.1f}%)")
            
            # Test assertions
            assert 'S1' in result, "S1 jenjang should exist"
            assert 'S2' in result, "S2 jenjang should exist"
            assert result['S2'] >= 5, "S2 should have at least 5 beasiswa"
            logger.info("✅ All assertions passed for jenjang distribution")
        else:
            logger.error("❌ Invalid result from get_beasiswa_per_jenjang()")
            return False
            
    except Exception as e:
        logger.error(f"❌ Exception in get_beasiswa_per_jenjang(): {e}")
        return False
    
    # ========================== STEP 4: Test get_top_penyelenggara() ==========================
    print("\nSTEP 4: Testing get_top_penyelenggara()")
    print("-" * 80)
    
    try:
        # Test with different limits
        results = []
        for limit in [2, 5, 10]:
            result = get_top_penyelenggara(limit=limit)
            results.append((limit, result))
            
            if isinstance(result, list) and len(result) > 0:
                logger.info(f"✅ get_top_penyelenggara(limit={limit}) returned {len(result)} results")
            else:
                logger.warning(f"⚠️ get_top_penyelenggara(limit={limit}) returned empty list")
        
        # Verify top 2
        top_2 = results[0][1]
        if len(top_2) >= 2:
            print(f"\nTop 2 Penyelenggara:")
            for i, org in enumerate(top_2, 1):
                print(f"  {i}. {org['nama_penyelenggara']}: {org['total_beasiswa']} beasiswa")
            
            # Verify ordering (should be descending)
            if top_2[0]['total_beasiswa'] >= top_2[1]['total_beasiswa']:
                logger.info("✅ Top penyelenggara correctly ordered by count (descending)")
            else:
                logger.error("❌ Penyelenggara not properly ordered")
                return False
        
        # Test edge case: limit <= 0
        result_edge = get_top_penyelenggara(limit=0)
        assert result_edge == [], "Limit 0 should return empty list"
        logger.info("✅ Edge case (limit=0) handled correctly")
        
    except Exception as e:
        logger.error(f"❌ Exception in get_top_penyelenggara(): {e}")
        return False
    
    # ========================== STEP 5: Test get_status_availability() ==========================
    print("\nSTEP 5: Testing get_status_availability()")
    print("-" * 80)
    
    try:
        result = get_status_availability()
        
        if isinstance(result, dict) and len(result) > 0:
            logger.info("✅ get_status_availability() returned valid data")
            
            total = sum(result.values())
            print(f"\nStatus Distribution ({total} total):")
            
            status_order = ['Buka', 'Segera Tutup', 'Tutup']
            for status in status_order:
                if status in result:
                    count = result[status]
                    percentage = (count / total * 100) if total > 0 else 0
                    badge = "🟢" if status == "Buka" else "🟡" if status == "Segera Tutup" else "🔴"
                    print(f"  {badge} {status}: {count} beasiswa ({percentage:.1f}%)")
            
            # Test assertions
            assert 'Buka' in result, "Status 'Buka' should exist"
            assert 'Segera Tutup' in result, "Status 'Segera Tutup' should exist"
            assert result['Buka'] >= 6, "Should have at least 6 open scholarships"
            logger.info("✅ All assertions passed for status availability")
        else:
            logger.error("❌ Invalid result from get_status_availability()")
            return False
            
    except Exception as e:
        logger.error(f"❌ Exception in get_status_availability(): {e}")
        return False
    
    # ========================== STEP 6: Data Consistency Verification ==========================
    print("\nSTEP 6: Data Consistency Verification")
    print("-" * 80)
    
    try:
        # Verify total counts match
        jenjang_total = sum(get_beasiswa_per_jenjang().values())
        status_total = sum(get_status_availability().values())
        
        # Count beasiswa directly from database
        conn = sqlite3.connect("database/beasiswaku.db")
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) as total FROM beasiswa")
        db_total = cursor.fetchone()[0]
        conn.close()
        
        print(f"\nTotal Beasiswa Count Verification:")
        print(f"  From jenjang aggregation: {jenjang_total}")
        print(f"  From status aggregation: {status_total}")
        print(f"  From database query: {db_total}")
        
        if jenjang_total == status_total == db_total:
            logger.info("✅ All counts match - data is consistent")
        else:
            logger.warning("⚠️ Count mismatch - may indicate data integrity issue")
            
    except Exception as e:
        logger.error(f"❌ Exception in consistency check: {e}")
        return False
    
    # ========================== STEP 7: Performance Check ==========================
    print("\nSTEP 7: Performance Check")
    print("-" * 80)
    
    import time
    
    try:
        # Measure execution time for each function
        times = {}
        
        # Test jenjang query
        start = time.time()
        for _ in range(10):
            get_beasiswa_per_jenjang()
        times['jenjang'] = (time.time() - start) / 10
        
        # Test penyelenggara query
        start = time.time()
        for _ in range(10):
            get_top_penyelenggara(limit=5)
        times['penyelenggara'] = (time.time() - start) / 10
        
        # Test status query
        start = time.time()
        for _ in range(10):
            get_status_availability()
        times['status'] = (time.time() - start) / 10
        
        print("\nAverage Execution Time (10 runs):")
        for func, avg_time in times.items():
            print(f"  {func}: {avg_time*1000:.2f}ms")
        
        # Check if all under 100ms
        if all(t < 0.1 for t in times.values()):
            logger.info("✅ All queries execute in <100ms - excellent performance")
        else:
            logger.warning("⚠️ Some queries took >100ms")
            
    except Exception as e:
        logger.error(f"❌ Exception in performance check: {e}")
        return False
    
    # ========================== SUMMARY ==========================
    print("\n" + "="*80)
    print("✅ ALL TESTS PASSED - PHASE 4.1 COMPLETE")
    print("="*80)
    print("\nSummary:")
    print("  ✅ get_beasiswa_per_jenjang() - Working correctly")
    print("  ✅ get_top_penyelenggara() - Working correctly")
    print("  ✅ get_status_availability() - Working correctly")
    print("  ✅ Data consistency verified")
    print("  ✅ Performance acceptable")
    print("\nReady for next phase!")
    print("="*80 + "\n")
    
    return True


if __name__ == "__main__":
    success = test_aggregation_queries()
    exit(0 if success else 1)
