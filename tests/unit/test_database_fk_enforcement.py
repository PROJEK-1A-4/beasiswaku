#!/usr/bin/env python3
"""Tests for SQLite foreign key enforcement at connection level."""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from src.core.database import DatabaseManager


def test_database_connection_enables_foreign_keys():
    """Every new DB connection should enforce foreign keys automatically."""
    db = DatabaseManager()
    db.close_connection()

    conn = db.get_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("PRAGMA foreign_keys")
        fk_enabled = cursor.fetchone()[0]
    finally:
        cursor.close()

    assert fk_enabled == 1
