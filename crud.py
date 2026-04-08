"""
crud.py - Database CRUD operations dan Authentication
Untuk BeasiswaKu - Personal Scholarship Manager

Tanggung jawab:
- Database initialization dan schema management
- Authentication: hashing password, register, login
- CRUD operations untuk beasiswa dan lamaran
- Session management
"""

import sqlite3
import bcrypt
import logging
from pathlib import Path
from datetime import datetime
from typing import Optional, List, Dict, Tuple

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Database path
DB_PATH = Path("database/beasiswaku.db")
DB_PATH.parent.mkdir(parents=True, exist_ok=True)


def get_connection():
    """
    Membuka koneksi ke database SQLite.
    
    Returns:
        sqlite3.Connection: Koneksi ke database
    """
    conn = sqlite3.connect(str(DB_PATH))
    conn.row_factory = sqlite3.Row  # Enable column access by name
    return conn


def init_db():
    """
    Menginisialisasi database dan membuat semua tabel jika belum ada.
    
    Tabel yang dibuat:
    1. akun - menyimpan data user dengan password ter-hash
    2. beasiswa - data beasiswa hasil scraping
    3. penyelenggara - informasi organisasi pemberi beasiswa
    4. riwayat_lamaran - tracking status lamaran per user
    5. favorit - daftar beasiswa favorit per user
    
    Raises:
        sqlite3.Error: Jika ada error saat membuat tabel
    """
    conn = get_connection()
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
        
        conn.commit()
        logger.info(f"✅ Database schema initialized successfully at {DB_PATH}")
        
    except sqlite3.Error as e:
        logger.error(f"❌ Error initializing database: {e}")
        raise
    finally:
        cursor.close()
        conn.close()


def hash_password(password: str) -> str:
    """
    Hash password menggunakan bcrypt.
    
    Args:
        password (str): Plain text password
        
    Returns:
        str: Hashed password (bytes, dikodekan ke string)
        
    Example:
        >>> hashed = hash_password("mypassword123")
        >>> print(hashed)  # $2b$12$nOUIs5kJ7naTuTFkBy1H.e...
    """
    salt = bcrypt.gensalt(rounds=12)
    hashed = bcrypt.hashpw(password.encode('utf-8'), salt)
    return hashed.decode('utf-8')


def verify_password(password: str, hashed_password: str) -> bool:
    """
    Verifikasi password terhadap hash yang tersimpan.
    
    Args:
        password (str): Plain text password yang akan diverifikasi
        hashed_password (str): Hash yang tersimpan di database
        
    Returns:
        bool: True jika password cocok, False jika tidak cocok
        
    Example:
        >>> hashed = hash_password("mypassword123")
        >>> verify_password("mypassword123", hashed)
        True
        >>> verify_password("wrongpassword", hashed)
        False
    """
    return bcrypt.checkpw(password.encode('utf-8'), hashed_password.encode('utf-8'))


def register_user(username: str, email: str, password: str, 
                 nama_lengkap: str = "", jenjang: str = "") -> Tuple[bool, str]:
    """
    Mendaftarkan user baru dengan validasi.
    
    Args:
        username (str): Nama user (harus unik)
        email (str): Email (harus unik)
        password (str): Password plain text (akan di-hash)
        nama_lengkap (str, optional): Nama lengkap user
        jenjang (str, optional): Jenjang pendidikan (D3, D4, S1, S2)
        
    Returns:
        Tuple[bool, str]: 
            - (True, "Success message") jika registrasi berhasil
            - (False, "Error message") jika ada error
            
    Error cases:
        - Username diperlukan
        - Email diperlukan
        - Password diperlukan (minimal 6 karakter)
        - Username atau email sudah terdaftar
        - Database error
        
    Example:
        >>> success, msg = register_user("john_doe", "john@example.com", "pass123")
        >>> if success:
        ...     print(f"User registered! {msg}")
        ... else:
        ...     print(f"Error: {msg}")
    """
    # Validasi input
    if not username or not username.strip():
        return False, "Username tidak boleh kosong"
    
    if not email or not email.strip():
        return False, "Email tidak boleh kosong"
    
    if not password or len(password) < 6:
        return False, "Password harus minimal 6 karakter"
    
    username = username.strip()
    email = email.strip()
    
    try:
        conn = get_connection()
        cursor = conn.cursor()
        
        # Hash password
        password_hash = hash_password(password)
        
        # Insert user
        cursor.execute("""
            INSERT INTO akun (username, email, password_hash, nama_lengkap, jenjang)
            VALUES (?, ?, ?, ?, ?)
        """, (username, email, password_hash, nama_lengkap, jenjang))
        
        conn.commit()
        logger.info(f"✅ User '{username}' registered successfully")
        return True, f"User '{username}' berhasil terdaftar!"
        
    except sqlite3.IntegrityError as e:
        conn.rollback()
        if "username" in str(e).lower():
            error_msg = f"Username '{username}' sudah terdaftar"
        elif "email" in str(e).lower():
            error_msg = f"Email '{email}' sudah terdaftar"
        else:
            error_msg = f"User dengan data tersebut sudah ada"
        logger.warning(f"⚠️ Registration failed: {error_msg}")
        return False, error_msg
        
    except sqlite3.Error as e:
        conn.rollback()
        logger.error(f"❌ Database error during registration: {e}")
        return False, f"Terjadi error saat registrasi: {str(e)}"
        
    finally:
        cursor.close()
        conn.close()


def login_user(username: str, password: str) -> Tuple[bool, str, Optional[Dict]]:
    """
    Melakukan login user dengan verifikasi password.
    
    Args:
        username (str): Username atau email
        password (str): Password plain text
        
    Returns:
        Tuple[bool, str, Optional[Dict]]:
            - (True, "Success message", user_data) jika login berhasil
            - (False, "Error message", None) jika login gagal
        
        user_data dict contains:
            - id: User ID
            - username: Username
            - email: Email
            - nama_lengkap: Nama lengkap
            - jenjang: Jenjang pendidikan
            
    Error cases:
        - Username/email tidak ditemukan
        - Password salah
        - Database error
        
    Example:
        >>> success, msg, user = login_user("john_doe", "pass123")
        >>> if success:
        ...     print(f"Welcome {user['nama_lengkap']}!")
        ... else:
        ...     print(f"Login failed: {msg}")
    """
    if not username or not password:
        return False, "Username dan password diperlukan", None
    
    try:
        conn = get_connection()
        cursor = conn.cursor()
        
        # Cari user berdasarkan username atau email
        cursor.execute("""
            SELECT id, username, email, password_hash, nama_lengkap, jenjang
            FROM akun
            WHERE username = ? OR email = ?
        """, (username, username))
        
        user = cursor.fetchone()
        cursor.close()
        
        if not user:
            logger.warning(f"⚠️ Login attempt with unknown user: {username}")
            return False, "Username atau email tidak ditemukan", None
        
        # Verifikasi password
        if not verify_password(password, user['password_hash']):
            logger.warning(f"⚠️ Login attempt with wrong password for user: {username}")
            return False, "Password salah", None
        
        # Prepare user data (exclude password hash)
        user_data = {
            'id': user['id'],
            'username': user['username'],
            'email': user['email'],
            'nama_lengkap': user['nama_lengkap'],
            'jenjang': user['jenjang']
        }
        
        logger.info(f"✅ User '{username}' logged in successfully")
        return True, f"Selamat datang, {user['nama_lengkap'] or user['username']}!", user_data
        
    except sqlite3.Error as e:
        logger.error(f"❌ Database error during login: {e}")
        return False, f"Terjadi error saat login: {str(e)}", None
        
    finally:
        conn.close()


# =====================================================================
# PHASE 2.2: CRUD BEASISWA FUNCTIONS
# =====================================================================

def add_beasiswa(judul: str, jenjang: str, deadline: str,
                penyelenggara_id: Optional[int] = None,
                deskripsi: str = "", benefit: str = "",
                persyaratan: str = "", minimal_ipk: Optional[float] = None,
                coverage: str = "", status: str = "Buka",
                link_aplikasi: str = "") -> Tuple[bool, str, Optional[int]]:
    """
    Menambahkan beasiswa baru ke database.
    
    Args:
        judul (str): Judul/nama beasiswa (required)
        jenjang (str): Jenjang pendidikan (D3, D4, S1, S2)
        deadline (str): Deadline pendaftaran (format YYYY-MM-DD)
        penyelenggara_id (int, optional): ID penyelenggara
        deskripsi (str, optional): Deskripsi beasiswa
        benefit (str, optional): Benefit/keuntungan beasiswa
        persyaratan (str, optional): Persyaratan beasiswa
        minimal_ipk (float, optional): IPK minimal (0.0 - 4.0)
        coverage (str, optional): Jenis coverage (Fully, Partially, etc)
        status (str, optional): Status beasiswa (Buka, Segera Tutup, Tutup) - default 'Buka'
        link_aplikasi (str, optional): Link aplikasi/form
    
    Returns:
        Tuple[bool, str, Optional[int]]:
            - (True, "Success message", beasiswa_id) jika berhasil
            - (False, "Error message", None) jika gagal
    
    Error cases:
        - Judul kosong
        - Jenjang tidak valid
        - Deadline format tidak valid
        - Penyelenggara_id tidak ada (foreign key violation)
        - Database error
    
    Example:
        >>> success, msg, id = add_beasiswa(
        ...     "Beasiswa A1",
        ...     "S1",
        ...     "2026-12-31",
        ...     penyelenggara_id=1,
        ...     benefit="Subsidi penuh"
        ... )
        >>> if success:
        ...     print(f"Beasiswa added with ID: {id}")
    """
    # Validasi input
    if not judul or not judul.strip():
        return False, "Judul beasiswa tidak boleh kosong", None
    
    if not jenjang or jenjang.strip().upper() not in ['D3', 'D4', 'S1', 'S2']:
        return False, "Jenjang harus salah satu dari: D3, D4, S1, S2", None
    
    if not deadline or not deadline.strip():
        return False, "Deadline tidak boleh kosong", None
    
    # Validasi format deadline (YYYY-MM-DD)
    try:
        datetime.strptime(deadline, '%Y-%m-%d')
    except ValueError:
        return False, "Format deadline harus YYYY-MM-DD (contoh: 2026-12-31)", None
    
    # Validasi minimal_ipk jika ada
    if minimal_ipk is not None:
        try:
            ipk_float = float(minimal_ipk)
            if ipk_float < 0.0 or ipk_float > 4.0:
                return False, "IPK minimal harus antara 0.0 - 4.0", None
        except (ValueError, TypeError):
            return False, "IPK minimal harus berupa angka desimal", None
    
    judul = judul.strip()
    jenjang = jenjang.strip().upper()
    
    try:
        conn = get_connection()
        cursor = conn.cursor()
        
        # Enable foreign key checking untuk SQLite
        cursor.execute("PRAGMA foreign_keys = ON")
        
        # Insert beasiswa
        cursor.execute("""
            INSERT INTO beasiswa (
                judul, jenjang, deadline, penyelenggara_id,
                deskripsi, benefit, persyaratan, minimal_ipk,
                coverage, status, link_aplikasi, scrape_date
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, CURRENT_TIMESTAMP)
        """, (
            judul, jenjang, deadline, penyelenggara_id,
            deskripsi.strip(), benefit.strip(), persyaratan.strip(),
            minimal_ipk, coverage.strip(), status, link_aplikasi.strip()
        ))
        
        conn.commit()
        beasiswa_id = cursor.lastrowid
        
        logger.info(f"✅ Beasiswa '{judul}' added successfully (ID: {beasiswa_id}, Jenjang: {jenjang})")
        return True, f"Beasiswa '{judul}' berhasil ditambahkan!", beasiswa_id
        
    except sqlite3.IntegrityError as e:
        conn.rollback()
        if "FOREIGN KEY" in str(e):
            error_msg = f"Penyelenggara dengan ID {penyelenggara_id} tidak ditemukan"
        else:
            error_msg = f"Data constraint violation: {str(e)}"
        logger.warning(f"⚠️ Beasiswa add failed: {error_msg}")
        return False, error_msg, None
        
    except sqlite3.Error as e:
        conn.rollback()
        logger.error(f"❌ Database error saat menambah beasiswa: {e}")
        return False, f"Terjadi error database: {str(e)}", None
        
    finally:
        cursor.close()
        conn.close()


if __name__ == "__main__":
    # Script untuk testing
    init_db()
    print("✅ Database schema created successfully!")
