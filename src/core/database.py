"""
Database Manager Singleton
Owner: DARVA
Centralized database connection management using Singleton pattern.
All database operations should go through this module.
"""

import sqlite3
import logging
from pathlib import Path
from typing import Optional

logger = logging.getLogger(__name__)


class DatabaseManager:
    """
    Singleton class for managing database connections.
    Ensures only one connection is used throughout the application.
    
    Usage:
        db = DatabaseManager()
        conn = db.get_connection()
        # or
        db.execute("SELECT * FROM beasiswa")
    """

    _instance: Optional['DatabaseManager'] = None
    _connection: Optional[sqlite3.Connection] = None

    def __new__(cls):
        """Implement singleton pattern."""
        if cls._instance is None:
            cls._instance = super(DatabaseManager, cls).__new__(cls)
            cls._instance._initialized = False
        return cls._instance

    def __init__(self):
        """Initialize the database manager."""
        if self._initialized:
            return

        from .config import Config

        self.db_path = Path(Config.DATABASE_PATH)
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self._initialized = True
        logger.info(f"DatabaseManager initialized at {self.db_path}")

    def get_connection(self) -> sqlite3.Connection:
        """
        Get or create database connection.
        
        Returns:
            sqlite3.Connection: Active database connection
        """
        if self._connection is None:
            from .config import Config
            self._connection = sqlite3.connect(
                str(self.db_path),
                timeout=Config.DATABASE_TIMEOUT,
                check_same_thread=Config.DATABASE_CHECK_SAME_THREAD
            )
            self._connection.row_factory = sqlite3.Row
            logger.debug("New database connection created")
        return self._connection

    def close_connection(self) -> None:
        """Close the database connection."""
        if self._connection is not None:
            self._connection.close()
            self._connection = None
            logger.info("Database connection closed")

    def execute(self, query: str, params: tuple = None):
        """
        Execute a query and return results.
        
        Args:
            query: SQL query string
            params: Query parameters (optional)
            
        Returns:
            Cursor or results
        """
        conn = self.get_connection()
        cursor = conn.cursor()
        if params:
            cursor.execute(query, params)
        else:
            cursor.execute(query)
        return cursor

    def execute_commit(self, query: str, params: tuple = None) -> int:
        """
        Execute a query and commit changes.
        
        Args:
            query: SQL query string
            params: Query parameters (optional)
            
        Returns:
            int: Rows affected or last row id
        """
        conn = self.get_connection()
        cursor = conn.cursor()
        try:
            if params:
                cursor.execute(query, params)
            else:
                cursor.execute(query)
            conn.commit()
            return cursor.lastrowid
        except sqlite3.Error as e:
            conn.rollback()
            logger.error(f"Database error: {e}")
            raise

    def init_schema(self) -> None:
        """
        Initialize database schema with all required tables.
        This is called from src/database/crud.py
        """
        conn = self.get_connection()
        cursor = conn.cursor()

        try:
            # Tabel 1: AKUN (User Management & Authentication)
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS akun (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    username TEXT UNIQUE NOT NULL,
                    email TEXT UNIQUE NOT NULL,
                    password_hash TEXT NOT NULL,
                    nama_lengkap TEXT,
                    jenjang TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)

            # Tabel 2: PENYELENGGARA (Scholarship Provider)
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS penyelenggara (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    nama TEXT NOT NULL,
                    description TEXT,
                    website TEXT,
                    contact_email TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)

            # Tabel 3: BEASISWA (Scholarship Data)
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS beasiswa (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    judul TEXT NOT NULL,
                    penyelenggara_id INTEGER,
                    jenjang TEXT,
                    deadline DATE NOT NULL,
                    deskripsi TEXT,
                    benefit TEXT,
                    persyaratan TEXT,
                    minimal_ipk REAL,
                    coverage TEXT,
                    status TEXT DEFAULT 'Buka',
                    link_aplikasi TEXT,
                    scrape_date TIMESTAMP,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (penyelenggara_id) REFERENCES penyelenggara(id)
                )
            """)

            # Tabel 4: RIWAYAT_LAMARAN (Application Tracking)
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS riwayat_lamaran (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER NOT NULL,
                    beasiswa_id INTEGER NOT NULL,
                    status TEXT DEFAULT 'Pending',
                    tanggal_daftar DATE,
                    catatan TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (user_id) REFERENCES akun(id),
                    FOREIGN KEY (beasiswa_id) REFERENCES beasiswa(id),
                    UNIQUE(user_id, beasiswa_id)
                )
            """)

            # Tabel 5: FAVORIT (Favorite Scholarships per User)
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS favorit (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER NOT NULL,
                    beasiswa_id INTEGER NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (user_id) REFERENCES akun(id),
                    FOREIGN KEY (beasiswa_id) REFERENCES beasiswa(id),
                    UNIQUE(user_id, beasiswa_id)
                )
            """)

            # Tabel 6: CATATAN (Personal Notes per Beasiswa)
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS catatan (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER NOT NULL,
                    beasiswa_id INTEGER NOT NULL,
                    content TEXT NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (user_id) REFERENCES akun(id),
                    FOREIGN KEY (beasiswa_id) REFERENCES beasiswa(id),
                    UNIQUE(user_id, beasiswa_id)
                )
            """)

            conn.commit()
            logger.info("✅ Database schema initialized successfully")

        except sqlite3.Error as e:
            conn.rollback()
            logger.error(f"Error initializing schema: {e}")
            raise

    def __del__(self):
        """Cleanup on deletion."""
        self.close_connection()


# Support legacy get_connection usage
def get_connection() -> sqlite3.Connection:
    """
    DEPRECATED: Use DatabaseManager().get_connection() instead.
    Kept for backward compatibility while refactoring.
    """
    db = DatabaseManager()
    return db.get_connection()


def init_db():
    """
    DEPRECATED: Use DatabaseManager().init_schema() instead.
    Kept for backward compatibility while refactoring.
    """
    db = DatabaseManager()
    db.init_schema()
