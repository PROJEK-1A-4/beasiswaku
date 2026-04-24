#!/usr/bin/env python3
"""GUI integration tests in pure unittest class style."""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.parent))

import logging
import time
import unittest

from src.database.crud import (
    add_beasiswa,
    add_catatan,
    add_favorit,
    delete_catatan,
    delete_favorit,
    edit_catatan,
    get_catatan,
    get_connection,
    get_favorit_list,
    init_db,
    register_user,
)

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class BaseGuiCrudTestCase(unittest.TestCase):
    """Shared fixtures/helpers for GUI-facing CRUD tests."""

    created_user_ids = []
    created_beasiswa_ids = []

    @classmethod
    def setUpClass(cls):
        init_db()

    @classmethod
    def tearDownClass(cls):
        """Cleanup records created by this test module to keep DB tidy."""
        try:
            conn = get_connection()
            cursor = conn.cursor()
            cursor.execute("PRAGMA foreign_keys = ON")

            if cls.created_beasiswa_ids:
                ids = [(bid,) for bid in cls.created_beasiswa_ids]
                cursor.executemany("DELETE FROM catatan WHERE beasiswa_id = ?", ids)
                cursor.executemany("DELETE FROM favorit WHERE beasiswa_id = ?", ids)
                cursor.executemany("DELETE FROM riwayat_lamaran WHERE beasiswa_id = ?", ids)
                cursor.executemany("DELETE FROM beasiswa WHERE id = ?", ids)

            if cls.created_user_ids:
                ids = [(uid,) for uid in cls.created_user_ids]
                cursor.executemany("DELETE FROM catatan WHERE user_id = ?", ids)
                cursor.executemany("DELETE FROM favorit WHERE user_id = ?", ids)
                cursor.executemany("DELETE FROM riwayat_lamaran WHERE user_id = ?", ids)
                cursor.executemany("DELETE FROM akun WHERE id = ?", ids)

            conn.commit()
            cursor.close()
        except Exception as exc:
            logger.warning("Cleanup warning in GUI tests: %s", exc)

    def _make_unique_identity(self, prefix: str):
        suffix = str(time.time_ns())
        username = f"{prefix}_{suffix}"
        email = f"{prefix}_{suffix}@test.local"
        return username, email

    def _get_user_id_by_username(self, username: str):
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT id FROM akun WHERE username = ?", (username,))
        row = cursor.fetchone()
        cursor.close()

        if not row:
            return None
        if hasattr(row, "keys"):
            return row["id"]
        return row[0]

    def _create_test_user(self, prefix: str = "gui_user"):
        username, email = self._make_unique_identity(prefix)
        success, message = register_user(username, email, "password123@A")
        self.assertTrue(success, f"User registration failed: {message}")

        user_id = self._get_user_id_by_username(username)
        self.assertIsNotNone(user_id, "User ID should exist after successful register")
        self.__class__.created_user_ids.append(user_id)
        return user_id

    def _create_test_beasiswa(self, title_prefix: str = "Test Beasiswa GUI"):
        unique_title = f"{title_prefix} {time.time_ns()}"
        success, message, beasiswa_id = add_beasiswa(
            judul=unique_title,
            jenjang="S1",
            deadline="2026-12-31",
            benefit="Full",
            minimal_ipk=3.0,
            status="Buka",
        )
        self.assertTrue(success, f"Beasiswa creation failed: {message}")
        self.assertIsNotNone(beasiswa_id, "Beasiswa ID should not be None")
        self.__class__.created_beasiswa_ids.append(beasiswa_id)
        return beasiswa_id


class TestFavoritesCrud(BaseGuiCrudTestCase):
    def test_add_and_list_favorit(self):
        user_id = self._create_test_user("gui_user_fav")
        beasiswa_id = self._create_test_beasiswa("Test Beasiswa Favorite")

        success, message, favorit_id = add_favorit(user_id, beasiswa_id)
        self.assertTrue(success, message)
        self.assertIsNotNone(favorit_id)

        favorit_list, total = get_favorit_list(user_id)
        self.assertGreaterEqual(total, 1)
        self.assertTrue(any(item.get("beasiswa_id") == beasiswa_id for item in favorit_list))

    def test_duplicate_favorit_rejected(self):
        user_id = self._create_test_user("gui_user_dup_fav")
        beasiswa_id = self._create_test_beasiswa("Test Beasiswa Duplicate Favorite")

        success_first, _, _ = add_favorit(user_id, beasiswa_id)
        success_second, msg_second, _ = add_favorit(user_id, beasiswa_id)

        self.assertTrue(success_first)
        self.assertFalse(success_second)
        self.assertIn("favorit", msg_second.lower())

    def test_delete_favorit(self):
        user_id = self._create_test_user("gui_user_del_fav")
        beasiswa_id = self._create_test_beasiswa("Test Beasiswa Delete Favorite")

        success_add, _, _ = add_favorit(user_id, beasiswa_id)
        self.assertTrue(success_add)

        success_delete, delete_message = delete_favorit(user_id, beasiswa_id)
        self.assertTrue(success_delete, delete_message)

        favorit_list, _ = get_favorit_list(user_id)
        self.assertFalse(any(item.get("beasiswa_id") == beasiswa_id for item in favorit_list))


class TestCatatanCrud(BaseGuiCrudTestCase):
    def test_add_get_edit_delete_catatan(self):
        user_id = self._create_test_user("gui_user_note")
        beasiswa_id = self._create_test_beasiswa("Test Beasiswa Notes")

        success_add, add_message, catatan_id = add_catatan(user_id, beasiswa_id, "Catatan awal")
        self.assertTrue(success_add, add_message)
        self.assertIsNotNone(catatan_id)

        catatan, get_message = get_catatan(user_id, beasiswa_id)
        self.assertIsNotNone(catatan, get_message)
        self.assertEqual(catatan.get("content"), "Catatan awal")

        success_edit, edit_message = edit_catatan(user_id, beasiswa_id, "Catatan update")
        self.assertTrue(success_edit, edit_message)

        catatan_updated, _ = get_catatan(user_id, beasiswa_id)
        self.assertEqual(catatan_updated.get("content"), "Catatan update")

        success_delete, delete_message = delete_catatan(user_id, beasiswa_id)
        self.assertTrue(success_delete, delete_message)

        catatan_after_delete, _ = get_catatan(user_id, beasiswa_id)
        self.assertIsNone(catatan_after_delete)

    def test_duplicate_catatan_rejected(self):
        user_id = self._create_test_user("gui_user_note_dup")
        beasiswa_id = self._create_test_beasiswa("Test Beasiswa Notes Duplicate")

        success_first, _, _ = add_catatan(user_id, beasiswa_id, "Catatan pertama")
        success_second, message_second, _ = add_catatan(user_id, beasiswa_id, "Catatan kedua")

        self.assertTrue(success_first)
        self.assertFalse(success_second)
        self.assertIn("sudah ada", message_second.lower())

    def test_edit_and_delete_missing_catatan(self):
        user_id = self._create_test_user("gui_user_note_missing")
        beasiswa_id = self._create_test_beasiswa("Test Beasiswa Notes Missing")

        success_edit, edit_message = edit_catatan(user_id, beasiswa_id, "Tidak akan tersimpan")
        self.assertFalse(success_edit)
        self.assertIn("tidak ditemukan", edit_message.lower())

        success_delete, delete_message = delete_catatan(user_id, beasiswa_id)
        self.assertFalse(success_delete)
        self.assertIn("tidak ditemukan", delete_message.lower())


if __name__ == "__main__":
    unittest.main(verbosity=2)
