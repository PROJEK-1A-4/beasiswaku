#!/usr/bin/env python3
"""Tests for optimized get_beasiswa_list_for_user query path."""

import sys
from pathlib import Path
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from src.core.config import Config
from src.core.database import DatabaseManager
from src.database.crud import get_beasiswa_list_for_user, hash_password


def _close_and_reset_database_manager() -> None:
    """Close all open DB connections and reset singleton instance."""
    instance = DatabaseManager._instance
    if instance is not None:
        try:
            instance.close_all_connections()
        except Exception:
            pass
    DatabaseManager._instance = None


def test_get_beasiswa_list_for_user_without_n_plus_one(tmp_path):
    """The optimized list function should not call check_user_applied per row."""
    test_db_path = tmp_path / "beasiswa_user_list.db"

    old_database_path = Config.DATABASE_PATH
    old_check_same_thread = Config.DATABASE_CHECK_SAME_THREAD
    old_busy_timeout_ms = Config.DATABASE_BUSY_TIMEOUT_MS

    try:
        Config.DATABASE_PATH = str(test_db_path)
        Config.DATABASE_CHECK_SAME_THREAD = True
        Config.DATABASE_BUSY_TIMEOUT_MS = 30000

        _close_and_reset_database_manager()
        db = DatabaseManager()
        db.init_schema()

        conn = db.get_connection()
        cursor = conn.cursor()

        cursor.execute(
            """
            INSERT INTO akun (username, email, password_hash, nama_lengkap, jenjang)
            VALUES (?, ?, ?, ?, ?)
            """,
            ("user_list_test", "user_list@test.local", hash_password("password123"), "User List", "S1"),
        )
        user_id = cursor.lastrowid

        cursor.execute(
            """
            INSERT INTO beasiswa (judul, jenjang, deadline, status, benefit)
            VALUES (?, ?, ?, ?, ?)
            """,
            ("Beasiswa Alpha", "S1", "2026-12-31", "Buka", "Full"),
        )
        beasiswa_alpha_id = cursor.lastrowid

        cursor.execute(
            """
            INSERT INTO beasiswa (judul, jenjang, deadline, status, benefit)
            VALUES (?, ?, ?, ?, ?)
            """,
            ("Beasiswa Beta", "S1", "2026-11-30", "Buka", "Partial"),
        )
        beasiswa_beta_id = cursor.lastrowid

        cursor.execute(
            """
            INSERT INTO riwayat_lamaran (user_id, beasiswa_id, status, tanggal_daftar, catatan)
            VALUES (?, ?, ?, ?, ?)
            """,
            (user_id, beasiswa_alpha_id, "Submitted", "2026-01-01", "Applied"),
        )

        conn.commit()
        cursor.close()

        with patch(
            "src.database.crud.check_user_applied",
            side_effect=AssertionError("N+1 helper should not be called"),
        ):
            beasiswa_list, total_count = get_beasiswa_list_for_user(
                user_id=user_id,
                filter_jenjang="S1",
                filter_status="Buka",
                sort_by="id",
                sort_order="ASC",
            )

        assert total_count == 2
        assert len(beasiswa_list) == 2

        by_id = {item["id"]: item for item in beasiswa_list}
        assert by_id[beasiswa_alpha_id]["sudah_daftar"] is True
        assert by_id[beasiswa_beta_id]["sudah_daftar"] is False

    finally:
        _close_and_reset_database_manager()
        Config.DATABASE_PATH = old_database_path
        Config.DATABASE_CHECK_SAME_THREAD = old_check_same_thread
        Config.DATABASE_BUSY_TIMEOUT_MS = old_busy_timeout_ms
        _close_and_reset_database_manager()
