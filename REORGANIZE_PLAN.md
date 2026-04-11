# Test Reorganization Plan

## Current Structure (10 files)
- test_phase_1_1.py  → DARVA (Database initialization)
- test_phase_1_3.py  → DARVA (Config management)
- test_phase_2_2.py  → DARVA (DatabaseManager)
- test_phase_3_1.py  → ?? (Old phase tests)
- test_phase_3_2.py  → ?? (Old phase tests)
- test_phase_4_1.py  → ?? (Old phase tests)
- test_phase_5_2.py  → ?? (Old phase tests)
- test_phase_5_3.py  → KYLA (GUI - broken imports)
- test_phase_5_4.py  → AULIA (GUI - broken imports)
- test_auth_demo.py  → DARVA (Authentication)

## Target Structure (5 files)
✓ test_init.py              → Initialization & setup tests
✓ test_database.py          → DARVA (database/CRUD/auth)
✓ test_scraper.py           → KEMAL (scraper - empty placeholder)
✓ test_gui.py               → KYLA & AULIA (GUI tests)
✓ test_visualization.py     → RICHARD (visualization - empty placeholder)

## Consolidation Plan
1. test_init.py           ← Nothing currently (setup tests)
2. test_database.py       ← test_phase_1_1.py + test_phase_1_3.py + test_phase_2_2.py + test_auth_demo.py
3. test_scraper.py        ← New empty file (placeholder for KEMAL)
4. test_gui.py            ← test_phase_5_3.py + test_phase_5_4.py (fixed + cleaned)
5. test_visualization.py  ← New empty file (placeholder for RICHARD)

## Cleanup
- Remove: test_phase_*.py (all 10 files)
- Remove: test_auth_demo.py
- Keep: conftest.py (shared fixtures)
- Keep: __init__.py files
