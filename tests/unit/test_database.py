#!/usr/bin/env python3
"""Assertion-based database tests with isolated SQLite per test."""

import sys
import sqlite3
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from src.core.config import Config
from src.database.crud import (
    add_beasiswa,
    add_catatan,
    add_favorit,
    add_lamaran,
    delete_beasiswa,
    delete_catatan,
    delete_favorit,
    delete_lamaran,
    edit_beasiswa,
    edit_catatan,
    edit_lamaran,
    get_beasiswa_list,
    get_beasiswa_per_jenjang,
    get_catatan,
    get_connection,
    get_favorit_list,
    get_lamaran_list,
    get_status_availability,
    get_top_penyelenggara,
    hash_password,
    init_db,
    login_user,
    register_user,
    update_user_password,
    update_user_profile,
    verify_password,
)


EXPECTED_TABLES = {
    "akun",
    "penyelenggara",
    "beasiswa",
    "riwayat_lamaran",
    "favorit",
    "catatan",
}


def _table_columns(cursor, table_name: str):
    cursor.execute(f"PRAGMA table_info({table_name})")
    return {row[1] for row in cursor.fetchall()}


def test_database_initialization_creates_file(isolated_database):
    """init_db should be idempotent and keep a valid DB file."""
    init_db()

    assert str(isolated_database) == Config.DATABASE_PATH
    assert isolated_database.exists()
    assert isolated_database.stat().st_size > 0


def test_core_tables_exist(isolated_database):
    """All required tables should exist after schema initialization."""
    conn = get_connection()
    cursor = conn.cursor()
    try:
        cursor.execute(
            """
            SELECT name
            FROM sqlite_master
            WHERE type='table' AND name NOT LIKE 'sqlite_%'
            """
        )
        existing_tables = {row[0] for row in cursor.fetchall()}
    finally:
        cursor.close()

    assert EXPECTED_TABLES.issubset(existing_tables)


def test_table_schema_contains_required_columns(isolated_database):
    """Critical columns should exist in each primary table."""
    expected_columns = {
        "akun": {"id", "username", "email", "password_hash", "created_at", "updated_at"},
        "penyelenggara": {"id", "nama", "created_at"},
        "beasiswa": {"id", "judul", "jenjang", "deadline", "status", "created_at", "updated_at"},
        "riwayat_lamaran": {"id", "user_id", "beasiswa_id", "status", "tanggal_daftar"},
        "favorit": {"id", "user_id", "beasiswa_id", "created_at"},
        "catatan": {"id", "user_id", "beasiswa_id", "content", "created_at", "updated_at"},
    }

    conn = get_connection()
    cursor = conn.cursor()
    try:
        for table_name, required in expected_columns.items():
            actual = _table_columns(cursor, table_name)
            assert required.issubset(actual), f"Missing columns in {table_name}: {required - actual}"
    finally:
        cursor.close()


def test_unique_and_foreign_key_constraints(isolated_database):
    """UNIQUE and FOREIGN KEY constraints should be enforced by SQLite."""
    conn = get_connection()
    cursor = conn.cursor()
    try:
        cursor.execute(
            """
            INSERT INTO akun (username, email, password_hash, nama_lengkap, jenjang)
            VALUES (?, ?, ?, ?, ?)
            """,
            ("constraint_user", "constraint@test.local", hash_password("pass1234"), "Constraint", "S1"),
        )
        conn.commit()

        with pytest.raises(sqlite3.IntegrityError):
            cursor.execute(
                """
                INSERT INTO akun (username, email, password_hash, nama_lengkap, jenjang)
                VALUES (?, ?, ?, ?, ?)
                """,
                ("constraint_user", "other@test.local", hash_password("pass1234"), "Dup", "S1"),
            )

        with pytest.raises(sqlite3.IntegrityError):
            cursor.execute("INSERT INTO favorit (user_id, beasiswa_id) VALUES (?, ?)", (99999, 99999))
    finally:
        conn.rollback()
        cursor.close()


def test_register_and_login_flow(isolated_database):
    """Register/login flow should return consistent success and failure states."""
    success_register, register_message = register_user(
        "flow_user",
        "flow_user@test.local",
        "FlowPass123",
        "Flow User",
        "S1",
    )
    assert success_register is True
    assert "berhasil" in register_message.lower()

    dup_success, dup_message = register_user(
        "flow_user",
        "dup_email@test.local",
        "FlowPass123",
        "Duplicate",
        "S1",
    )
    assert dup_success is False
    assert "sudah" in dup_message.lower()

    login_success, _, user_data = login_user("flow_user", "FlowPass123")
    assert login_success is True
    assert user_data is not None
    assert user_data["username"] == "flow_user"

    wrong_success, wrong_message, _ = login_user("flow_user", "wrong")
    assert wrong_success is False
    assert "password" in wrong_message.lower()


def test_update_user_profile_persists_changes(isolated_database):
    """Profile update helper should persist username, email, name, and jenjang."""
    ok_register, register_message = register_user(
        "profile_user",
        "profile_user@test.local",
        "ProfilePass123",
        "Profile User",
        "S1",
    )
    assert ok_register is True, register_message

    ok_login, _, user_data = login_user("profile_user", "ProfilePass123")
    assert ok_login is True
    user_id = user_data["id"]

    ok_update, update_message = update_user_profile(
        user_id,
        "profile_user_updated",
        "profile_user_updated@test.local",
        "Profile User Updated",
        "S2",
    )
    assert ok_update is True, update_message

    conn = get_connection()
    cursor = conn.cursor()
    try:
        cursor.execute(
            """
            SELECT username, email, nama_lengkap, jenjang
            FROM akun
            WHERE id = ?
            """,
            (user_id,),
        )
        row = cursor.fetchone()
    finally:
        cursor.close()

    assert row is not None
    assert row["username"] == "profile_user_updated"
    assert row["email"] == "profile_user_updated@test.local"
    assert row["nama_lengkap"] == "Profile User Updated"
    assert row["jenjang"] == "S2"


def test_update_user_password_requires_current_password(isolated_database):
    """Password update helper should reject wrong current password and accept the correct one."""
    ok_register, register_message = register_user(
        "password_user",
        "password_user@test.local",
        "OldPass123",
        "Password User",
        "S1",
    )
    assert ok_register is True, register_message

    ok_login, _, user_data = login_user("password_user", "OldPass123")
    assert ok_login is True
    user_id = user_data["id"]

    wrong_ok, wrong_message = update_user_password(user_id, "wrong-current", "NewPass123")
    assert wrong_ok is False
    assert "password" in wrong_message.lower()

    ok_update, update_message = update_user_password(user_id, "OldPass123", "NewPass123")
    assert ok_update is True, update_message

    old_login_ok, old_login_message, _ = login_user("password_user", "OldPass123")
    assert old_login_ok is False
    assert "password" in old_login_message.lower()

    new_login_ok, new_login_message, new_user_data = login_user("password_user", "NewPass123")
    assert new_login_ok is True, new_login_message
    assert new_user_data is not None


def test_beasiswa_crud_flow(isolated_database):
    """Create, read, update, delete lifecycle should work for beasiswa."""
    created, message, beasiswa_id = add_beasiswa(
        judul="Beasiswa CRUD",
        jenjang="S1",
        deadline="2026-12-31",
        benefit="Full",
        minimal_ipk=3.0,
        status="Buka",
    )
    assert created is True, message
    assert isinstance(beasiswa_id, int)

    beasiswa_list, total = get_beasiswa_list(search_judul="CRUD")
    assert total >= 1
    assert any(item["id"] == beasiswa_id for item in beasiswa_list)

    updated, update_message = edit_beasiswa(beasiswa_id, judul="Beasiswa CRUD Updated")
    assert updated is True, update_message

    updated_list, _ = get_beasiswa_list(search_judul="Updated")
    assert any(item["id"] == beasiswa_id for item in updated_list)

    deleted, delete_message = delete_beasiswa(beasiswa_id)
    assert deleted is True, delete_message

    after_delete_list, _ = get_beasiswa_list(search_judul="Updated")
    assert all(item["id"] != beasiswa_id for item in after_delete_list)


def test_lamaran_favorit_catatan_flow(isolated_database):
    """Lamaran, favorit, and catatan flows should support create-update-delete paths."""
    ok_user, user_msg = register_user("flow_detail", "flow_detail@test.local", "FlowPass123", "Detail User", "S1")
    assert ok_user is True, user_msg

    ok_login, _, user_data = login_user("flow_detail", "FlowPass123")
    assert ok_login is True
    user_id = user_data["id"]

    ok_beasiswa, beasiswa_msg, beasiswa_id = add_beasiswa(
        judul="Beasiswa Detail Flow",
        jenjang="S1",
        deadline="2026-11-30",
        status="Buka",
    )
    assert ok_beasiswa is True, beasiswa_msg

    lamaran_ok, lamaran_msg, lamaran_id = add_lamaran(user_id=user_id, beasiswa_id=beasiswa_id, status="Pending")
    assert lamaran_ok is True, lamaran_msg
    assert isinstance(lamaran_id, int)

    lamaran_list, lamaran_total = get_lamaran_list(filter_user_id=user_id)
    assert lamaran_total >= 1
    assert any(item["id"] == lamaran_id for item in lamaran_list)

    lamaran_edit_ok, lamaran_edit_msg = edit_lamaran(lamaran_id, status="Submitted")
    assert lamaran_edit_ok is True, lamaran_edit_msg

    favorit_ok, favorit_msg, _ = add_favorit(user_id=user_id, beasiswa_id=beasiswa_id)
    assert favorit_ok is True, favorit_msg

    favorit_list, favorit_total = get_favorit_list(user_id)
    assert favorit_total >= 1
    assert any(item.get("beasiswa_id") == beasiswa_id for item in favorit_list)

    catatan_ok, catatan_msg, _ = add_catatan(user_id=user_id, beasiswa_id=beasiswa_id, content="Catatan awal")
    assert catatan_ok is True, catatan_msg

    catatan, _ = get_catatan(user_id=user_id, beasiswa_id=beasiswa_id)
    assert catatan is not None
    assert catatan["content"] == "Catatan awal"

    catatan_edit_ok, catatan_edit_msg = edit_catatan(user_id=user_id, beasiswa_id=beasiswa_id, content="Catatan update")
    assert catatan_edit_ok is True, catatan_edit_msg

    fav_delete_ok, fav_delete_msg = delete_favorit(user_id=user_id, beasiswa_id=beasiswa_id)
    assert fav_delete_ok is True, fav_delete_msg

    lamaran_delete_ok, lamaran_delete_msg = delete_lamaran(lamaran_id)
    assert lamaran_delete_ok is True, lamaran_delete_msg

    catatan_delete_ok, catatan_delete_msg = delete_catatan(user_id=user_id, beasiswa_id=beasiswa_id)
    assert catatan_delete_ok is True, catatan_delete_msg


def test_aggregation_queries_return_expected_shapes(isolated_database):
    """Aggregation helpers should return stable data shapes for dashboard usage."""
    ok_s1, msg_s1, _ = add_beasiswa(
        judul="Beasiswa Statistik S1",
        jenjang="S1",
        deadline="2026-12-31",
        status="Buka",
    )
    assert ok_s1 is True, msg_s1

    ok_s2, msg_s2, _ = add_beasiswa(
        judul="Beasiswa Statistik S2",
        jenjang="S2",
        deadline="2026-10-31",
        status="Segera Tutup",
    )
    assert ok_s2 is True, msg_s2

    by_jenjang = get_beasiswa_per_jenjang()
    assert isinstance(by_jenjang, dict)
    assert by_jenjang.get("S1", 0) >= 1
    assert by_jenjang.get("S2", 0) >= 1

    by_status = get_status_availability()
    assert isinstance(by_status, dict)
    assert by_status.get("Buka", 0) >= 1

    top_penyelenggara = get_top_penyelenggara(limit=5)
    assert isinstance(top_penyelenggara, list)
    assert len(top_penyelenggara) >= 1
    assert "nama_penyelenggara" in top_penyelenggara[0]


def test_password_hash_and_verify_helpers():
    """Password hashing helper should produce verifiable hashes."""
    hashed = hash_password("TestPassword123")
    assert isinstance(hashed, str)
    assert hashed

    assert verify_password("TestPassword123", hashed) is True
    assert verify_password("WrongPassword123", hashed) is False
