#!/usr/bin/env python3
"""Stress tests for thread-safe database writes."""

import sys
import threading
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from src.core.config import Config
from src.core.database import DatabaseManager
from src.database.crud import add_beasiswa


def _close_and_reset_database_manager() -> None:
    """Close all open DB connections and reset singleton instance."""
    instance = DatabaseManager._instance
    if instance is not None:
        try:
            instance.close_all_connections()
        except Exception:
            pass
    DatabaseManager._instance = None


def test_multithread_multiwrite_stress(tmp_path):
    """Concurrent writes from multiple threads should complete without random DB failures."""
    test_db_path = tmp_path / "thread_stress_beasiswaku.db"

    old_database_path = Config.DATABASE_PATH
    old_check_same_thread = Config.DATABASE_CHECK_SAME_THREAD
    old_busy_timeout_ms = Config.DATABASE_BUSY_TIMEOUT_MS

    worker_count = 6
    inserts_per_worker = 20
    expected_total_rows = worker_count * inserts_per_worker

    errors = []
    errors_lock = threading.Lock()
    start_barrier = threading.Barrier(worker_count)

    try:
        Config.DATABASE_PATH = str(test_db_path)
        Config.DATABASE_CHECK_SAME_THREAD = True
        Config.DATABASE_BUSY_TIMEOUT_MS = 30000

        _close_and_reset_database_manager()
        db = DatabaseManager()
        db.init_schema()

        def worker(worker_id: int) -> None:
            try:
                start_barrier.wait(timeout=5)
            except threading.BrokenBarrierError:
                with errors_lock:
                    errors.append(f"worker-{worker_id}: barrier broken")
                return

            for iteration in range(inserts_per_worker):
                title = f"Stress Thread {worker_id} Row {iteration}"
                success, message, _ = add_beasiswa(
                    judul=title,
                    jenjang="S1",
                    deadline="2026-12-31",
                    status="Buka",
                )
                if not success:
                    with errors_lock:
                        errors.append(f"worker-{worker_id} iter-{iteration}: {message}")

        threads = [
            threading.Thread(target=worker, args=(idx,), name=f"db-stress-{idx}")
            for idx in range(worker_count)
        ]

        for thread in threads:
            thread.start()

        for thread in threads:
            thread.join(timeout=20)

        hanging_threads = [thread.name for thread in threads if thread.is_alive()]
        assert not hanging_threads, f"Threads did not finish: {hanging_threads}"

        assert not errors, f"Concurrent write errors detected: {errors[:5]}"

        conn = db.get_connection()
        cursor = conn.cursor()
        try:
            cursor.execute("SELECT COUNT(*) FROM beasiswa")
            total_rows = cursor.fetchone()[0]
        finally:
            cursor.close()

        assert total_rows == expected_total_rows, (
            f"Expected {expected_total_rows} inserted rows, got {total_rows}"
        )

    finally:
        _close_and_reset_database_manager()
        Config.DATABASE_PATH = old_database_path
        Config.DATABASE_CHECK_SAME_THREAD = old_check_same_thread
        Config.DATABASE_BUSY_TIMEOUT_MS = old_busy_timeout_ms
        _close_and_reset_database_manager()
