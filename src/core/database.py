"""
Database Manager Singleton
Owner: DARVA
Centralized database connection management using Singleton pattern.
All database operations should go through this module.
"""

import sqlite3
import logging
import threading
from pathlib import Path
from typing import Optional, Dict

logger = logging.getLogger(__name__)


class DatabaseManager:
    """
    Singleton class for managing database connections.
    Provides one connection per thread while keeping a single manager instance.
    
    Usage:
        db = DatabaseManager()
        conn = db.get_connection()
        # or
        db.execute("SELECT * FROM beasiswa")
    """

    _instance: Optional['DatabaseManager'] = None
    _connections: Dict[int, sqlite3.Connection]
    _connections_lock: threading.Lock

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
        self._connections = {}
        self._connections_lock = threading.Lock()
        self._initialized = True
        logger.info(f"DatabaseManager initialized at {self.db_path}")

    def get_connection(self) -> sqlite3.Connection:
        """
        Get or create database connection for the current thread.
        
        Returns:
            sqlite3.Connection: Active database connection
        """
        thread_id = threading.get_ident()

        with self._connections_lock:
            connection = self._connections.get(thread_id)
            if connection is None:
                connection = self._create_connection()
                self._connections[thread_id] = connection
                logger.debug("Created DB connection for thread %s", thread_id)
                return connection

            try:
                connection.execute("SELECT 1")
                return connection
            except sqlite3.Error:
                logger.warning("Thread %s DB connection invalid. Reconnecting...", thread_id)
                try:
                    connection.close()
                except sqlite3.Error:
                    pass
                new_connection = self._create_connection()
                self._connections[thread_id] = new_connection
                return new_connection

    def _create_connection(self) -> sqlite3.Connection:
        """Create a fresh sqlite connection with configured defaults."""
        from .config import Config

        connection = sqlite3.connect(
            str(self.db_path),
            timeout=Config.DATABASE_TIMEOUT,
            check_same_thread=Config.DATABASE_CHECK_SAME_THREAD
        )
        connection.row_factory = sqlite3.Row
        connection.execute("PRAGMA foreign_keys = ON")
        connection.execute("PRAGMA journal_mode = WAL")
        connection.execute(f"PRAGMA busy_timeout = {Config.DATABASE_BUSY_TIMEOUT_MS}")
        logger.debug("New database connection created with FK+WAL+busy_timeout settings")
        return connection

    def close_connection(self) -> None:
        """Close database connection for the current thread."""
        thread_id = threading.get_ident()
        with self._connections_lock:
            connection = self._connections.pop(thread_id, None)

        if connection is not None:
            connection.close()
            logger.info("Database connection closed for thread %s", thread_id)

    def close_all_connections(self) -> None:
        """Close all tracked database connections across threads."""
        with self._connections_lock:
            connections = list(self._connections.items())
            self._connections.clear()

        for thread_id, connection in connections:
            try:
                connection.close()
            except sqlite3.Error:
                logger.warning("Failed to close DB connection for thread %s", thread_id)
        if connections:
            logger.info("Closed %s database connection(s)", len(connections))

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
        self.close_all_connections()


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
