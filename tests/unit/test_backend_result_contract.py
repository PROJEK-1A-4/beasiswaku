#!/usr/bin/env python3
"""Tests for standardized BackendResult contract wrappers."""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from src.core.config import Config
from src.core.database import DatabaseManager
from src.database.crud import (
    BackendResult,
    add_beasiswa_result,
    add_lamaran_result,
    login_user_result,
    register_user_result,
)


def _close_and_reset_database_manager() -> None:
    """Close all open DB connections and reset singleton instance."""
    instance = DatabaseManager._instance
    if instance is not None:
        try:
            instance.close_all_connections()
        except Exception:
            pass
    DatabaseManager._instance = None


def test_backend_result_contract_auth_and_beasiswa(tmp_path):
    """Auth and beasiswa wrappers should return stable BackendResult contracts."""
    test_db_path = tmp_path / "backend_result_contract.db"

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

        register_ok = register_user_result(
            username="result_user",
            email="result_user@test.local",
            password="password123",
            nama_lengkap="Result User",
            jenjang="S1",
        )
        assert isinstance(register_ok, BackendResult)
        assert register_ok.success is True
        assert register_ok.code == "REGISTER_USER_SUCCESS"
        assert register_ok.payload is None
        assert register_ok.to_tuple2()[0] is True

        register_dup = register_user_result(
            username="result_user",
            email="another_email@test.local",
            password="password123",
            nama_lengkap="Duplicate",
            jenjang="S1",
        )
        assert register_dup.success is False
        assert register_dup.code == "REGISTER_USER_CONFLICT_ALREADY_EXISTS"

        login_ok = login_user_result("result_user", "password123")
        assert login_ok.success is True
        assert login_ok.code == "LOGIN_USER_SUCCESS"
        assert isinstance(login_ok.payload, dict)
        assert login_ok.payload.get("username") == "result_user"

        login_wrong = login_user_result("result_user", "wrong_password")
        assert login_wrong.success is False
        assert login_wrong.code == "LOGIN_USER_AUTH_INVALID_PASSWORD"

        beasiswa_result = add_beasiswa_result(
            judul="Beasiswa Result Contract",
            jenjang="S1",
            deadline="2026-12-31",
            status="Buka",
        )
        assert beasiswa_result.success is True
        assert beasiswa_result.code == "ADD_BEASISWA_SUCCESS"
        assert isinstance(beasiswa_result.payload, int)
        assert beasiswa_result.to_tuple3()[2] == beasiswa_result.payload

        lamaran_invalid_user = add_lamaran_result(
            user_id=99999,
            beasiswa_id=beasiswa_result.payload,
        )
        assert lamaran_invalid_user.success is False
        assert lamaran_invalid_user.code == "ADD_LAMARAN_NOT_FOUND"

    finally:
        _close_and_reset_database_manager()
        Config.DATABASE_PATH = old_database_path
        Config.DATABASE_CHECK_SAME_THREAD = old_check_same_thread
        Config.DATABASE_BUSY_TIMEOUT_MS = old_busy_timeout_ms
        _close_and_reset_database_manager()
