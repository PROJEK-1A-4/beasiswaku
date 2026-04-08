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


def get_beasiswa_list(filter_jenjang: Optional[str] = None,
                     filter_status: Optional[str] = None,
                     search_judul: Optional[str] = None,
                     sort_by: str = 'deadline',
                     sort_order: str = 'ASC') -> Tuple[List[Dict], int]:
    """
    Mengambil list beasiswa dari database dengan support filter dan sorting.
    
    Args:
        filter_jenjang (str, optional): Filter by jenjang (D3, D4, S1, S2)
        filter_status (str, optional): Filter by status (Buka, Segera Tutup, Tutup)
        search_judul (str, optional): Search by judul (case-insensitive LIKE)
        sort_by (str, optional): Column to sort by (deadline, judul, created_at, status)
            - default: 'deadline'
        sort_order (str, optional): Sort order (ASC, DESC) - default: 'ASC'
    
    Returns:
        Tuple[List[Dict], int]:
            - (beasiswa_list, total_count) - list of beasiswa records and total count
            - Each record contains: id, judul, jenjang, deadline, status, 
              benefit, minimal_ipk, coverage, penyelenggara_id, created_at, updated_at
    
    Example:
        >>> beasiswa_list, total = get_beasiswa_list(
        ...     filter_jenjang='S1',
        ...     filter_status='Buka',
        ...     search_judul='LPDP',
        ...     sort_by='deadline',
        ...     sort_order='ASC'
        ... )
        >>> print(f"Found {total} beasiswa")
        >>> for b in beasiswa_list:
        ...     print(f"{b['judul']} - {b['deadline']}")
    """
    try:
        conn = get_connection()
        cursor = conn.cursor()
        
        # Build WHERE clause dynamically
        where_clauses = []
        params = []
        
        # Filter by jenjang
        if filter_jenjang:
            filter_jenjang = filter_jenjang.strip().upper()
            if filter_jenjang in ['D3', 'D4', 'S1', 'S2']:
                where_clauses.append("jenjang = ?")
                params.append(filter_jenjang)
        
        # Filter by status
        if filter_status:
            filter_status = filter_status.strip()
            valid_status = ['Buka', 'Segera Tutup', 'Tutup']
            if filter_status in valid_status:
                where_clauses.append("status = ?")
                params.append(filter_status)
        
        # Search by judul (case-insensitive LIKE)
        if search_judul:
            search_judul = search_judul.strip()
            where_clauses.append("judul LIKE ?")
            params.append(f"%{search_judul}%")
        
        # Build WHERE clause string
        where_sql = ""
        if where_clauses:
            where_sql = "WHERE " + " AND ".join(where_clauses)
        
        # Validate sort_by
        valid_sort_columns = ['deadline', 'judul', 'created_at', 'jenjang', 'status', 'id']
        sort_by = sort_by.strip().lower() if sort_by else 'deadline'
        if sort_by not in valid_sort_columns:
            sort_by = 'deadline'
        
        # Validate sort_order
        sort_order = sort_order.strip().upper() if sort_order else 'ASC'
        if sort_order not in ['ASC', 'DESC']:
            sort_order = 'ASC'
        
        # Get total count
        count_query = f"SELECT COUNT(*) as count FROM beasiswa {where_sql}"
        cursor.execute(count_query, params)
        total_count = cursor.fetchone()[0]
        
        # Get data with sorting
        query = f"""
            SELECT 
                id, judul, penyelenggara_id, jenjang, deadline, deskripsi,
                benefit, persyaratan, minimal_ipk, coverage, status,
                link_aplikasi, scrape_date, created_at, updated_at
            FROM beasiswa
            {where_sql}
            ORDER BY {sort_by} {sort_order}
        """
        
        cursor.execute(query, params)
        results = cursor.fetchall()
        
        # Convert to list of dictionaries
        beasiswa_list = [dict(row) for row in results]
        
        logger.info(f"✅ Retrieved {len(beasiswa_list)} beasiswa "
                   f"(Total: {total_count}, Filter: jenjang={filter_jenjang}, "
                   f"status={filter_status}, search={search_judul})")
        
        cursor.close()
        conn.close()
        
        return beasiswa_list, total_count
        
    except sqlite3.Error as e:
        logger.error(f"❌ Database error saat retrieve beasiswa: {e}")
        return [], 0


def edit_beasiswa(beasiswa_id: int, **kwargs) -> Tuple[bool, str]:
    """
    Mengupdate data beasiswa yang sudah ada.
    
    Args:
        beasiswa_id (int): ID beasiswa yang akan diupdate
        **kwargs: Field-field yang ingin diupdate (judul, jenjang, deadline, status, 
                  deskripsi, benefit, persyaratan, minimal_ipk, coverage, link_aplikasi)
    
    Returns:
        Tuple[bool, str]:
            - (True, "Success message") jika berhasil
            - (False, "Error message") jika gagal
    
    Validation rules:
        - judul: tidak boleh kosong
        - jenjang: harus salah satu dari D3, D4, S1, S2
        - deadline: format YYYY-MM-DD
        - status: harus salah satu dari Buka, Segera Tutup, Tutup
        - minimal_ipk: harus antara 0.0 - 4.0 (jika ada)
    
    Example:
        >>> success, msg = edit_beasiswa(
        ...     1,
        ...     judul="Beasiswa A2 Updated",
        ...     status="Segera Tutup"
        ... )
        >>> if success:
        ...     print("Update successful!")
    """
    if not beasiswa_id or not isinstance(beasiswa_id, int):
        return False, "ID beasiswa harus berupa angka integer"
    
    if not kwargs:
        return False, "Tidak ada field yang diupdate"
    
    # Validasi setiap field yang akan diupdate
    allowed_fields = {
        'judul': str,
        'jenjang': str,
        'deadline': str,
        'penyelenggara_id': int,
        'deskripsi': str,
        'benefit': str,
        'persyaratan': str,
        'minimal_ipk': (int, float, type(None)),
        'coverage': str,
        'status': str,
        'link_aplikasi': str
    }
    
    # Build update clauses dan prepare params
    update_clauses = []
    params = []
    
    for field, value in kwargs.items():
        if field not in allowed_fields:
            return False, f"Field '{field}' tidak diizinkan untuk diupdate"
        
        # Validasi field-specific rules
        if field == 'judul':
            if not value or not str(value).strip():
                return False, "Judul beasiswa tidak boleh kosong"
            update_clauses.append("judul = ?")
            params.append(str(value).strip())
        
        elif field == 'jenjang':
            jenjang_upper = str(value).strip().upper()
            if jenjang_upper not in ['D3', 'D4', 'S1', 'S2']:
                return False, "Jenjang harus salah satu dari: D3, D4, S1, S2"
            update_clauses.append("jenjang = ?")
            params.append(jenjang_upper)
        
        elif field == 'deadline':
            if not value or not str(value).strip():
                return False, "Deadline tidak boleh kosong"
            try:
                datetime.strptime(str(value).strip(), '%Y-%m-%d')
            except ValueError:
                return False, "Format deadline harus YYYY-MM-DD (contoh: 2026-12-31)"
            update_clauses.append("deadline = ?")
            params.append(str(value).strip())
        
        elif field == 'status':
            status_val = str(value).strip()
            valid_status = ['Buka', 'Segera Tutup', 'Tutup']
            if status_val not in valid_status:
                return False, f"Status harus salah satu dari: {', '.join(valid_status)}"
            update_clauses.append("status = ?")
            params.append(status_val)
        
        elif field == 'minimal_ipk':
            if value is not None:
                try:
                    ipk_float = float(value)
                    if ipk_float < 0.0 or ipk_float > 4.0:
                        return False, "IPK minimal harus antara 0.0 - 4.0"
                except (ValueError, TypeError):
                    return False, "IPK minimal harus berupa angka desimal"
            update_clauses.append("minimal_ipk = ?")
            params.append(value)
        
        elif field == 'penyelenggara_id':
            if value is not None:
                try:
                    int_val = int(value)
                    update_clauses.append("penyelenggara_id = ?")
                    params.append(int_val)
                except (ValueError, TypeError):
                    return False, "Penyelenggara ID harus berupa angka"
            else:
                update_clauses.append("penyelenggara_id = ?")
                params.append(None)
        
        else:
            # untuk field lainnya (deskripsi, benefit, persyaratan, coverage, link_aplikasi)
            update_clauses.append(f"{field} = ?")
            params.append(str(value).strip() if value else "")
    
    if not update_clauses:
        return False, "Tidak ada field yang valid untuk diupdate"
    
    # Add updated_at timestamp
    update_clauses.append("updated_at = CURRENT_TIMESTAMP")
    
    # Add beasiswa_id untuk WHERE clause
    params.append(beasiswa_id)
    
    try:
        conn = get_connection()
        cursor = conn.cursor()
        
        # Enable foreign key checking untuk SQLite
        cursor.execute("PRAGMA foreign_keys = ON")
        
        # Check if beasiswa exists
        cursor.execute("SELECT id, judul FROM beasiswa WHERE id = ?", (beasiswa_id,))
        existing = cursor.fetchone()
        
        if not existing:
            return False, f"Beasiswa dengan ID {beasiswa_id} tidak ditemukan"
        
        existing_judul = existing['judul']
        
        # Update beasiswa
        update_sql = f"""
            UPDATE beasiswa
            SET {', '.join(update_clauses)}
            WHERE id = ?
        """
        
        cursor.execute(update_sql, params)
        conn.commit()
        
        logger.info(f"✅ Beasiswa '{existing_judul}' (ID: {beasiswa_id}) updated successfully")
        return True, f"Beasiswa '{existing_judul}' berhasil diupdate!"
        
    except sqlite3.IntegrityError as e:
        conn.rollback()
        if "FOREIGN KEY" in str(e):
            error_msg = f"Penyelenggara dengan ID tidak ditemukan"
        else:
            error_msg = f"Data constraint violation: {str(e)}"
        logger.warning(f"⚠️ Beasiswa update failed: {error_msg}")
        return False, error_msg
        
    except sqlite3.Error as e:
        conn.rollback()
        logger.error(f"❌ Database error saat update beasiswa: {e}")
        return False, f"Terjadi error database: {str(e)}"
        
    finally:
        cursor.close()
        conn.close()


def delete_beasiswa(beasiswa_id: int) -> Tuple[bool, str]:
    """
    Menghapus beasiswa dari database dengan cascade deletion dari tabel terkait.
    
    Args:
        beasiswa_id (int): ID beasiswa yang akan dihapus
    
    Returns:
        Tuple[bool, str]:
            - (True, "Success message") jika berhasil
            - (False, "Error message") jika gagal
    
    Cascade deletion:
        - Delete dari riwayat_lamaran (applications history)
        - Delete dari favorit (favorite list)
        - Delete dari beasiswa (main table)
    
    Example:
        >>> success, msg = delete_beasiswa(1)
        >>> if success:
        ...     print("Beasiswa deleted successfully")
        ... else:
        ...     print(f"Error: {msg}")
    """
    if not beasiswa_id or not isinstance(beasiswa_id, int):
        return False, "ID beasiswa harus berupa angka integer"
    
    try:
        conn = get_connection()
        cursor = conn.cursor()
        
        # Enable foreign key checking untuk SQLite
        cursor.execute("PRAGMA foreign_keys = ON")
        
        # Check if beasiswa exists
        cursor.execute("SELECT id, judul FROM beasiswa WHERE id = ?", (beasiswa_id,))
        existing = cursor.fetchone()
        
        if not existing:
            return False, f"Beasiswa dengan ID {beasiswa_id} tidak ditemukan"
        
        existing_judul = existing['judul']
        
        # Get count of related records before deletion
        cursor.execute("SELECT COUNT(*) as count FROM riwayat_lamaran WHERE beasiswa_id = ?", (beasiswa_id,))
        lamaran_count = cursor.fetchone()['count']
        
        cursor.execute("SELECT COUNT(*) as count FROM favorit WHERE beasiswa_id = ?", (beasiswa_id,))
        favorit_count = cursor.fetchone()['count']
        
        # Delete from dependent tables (cascade deletion)
        cursor.execute("DELETE FROM riwayat_lamaran WHERE beasiswa_id = ?", (beasiswa_id,))
        cursor.execute("DELETE FROM favorit WHERE beasiswa_id = ?", (beasiswa_id,))
        
        # Delete from beasiswa table
        cursor.execute("DELETE FROM beasiswa WHERE id = ?", (beasiswa_id,))
        
        conn.commit()
        
        logger.info(f"✅ Beasiswa '{existing_judul}' (ID: {beasiswa_id}) deleted successfully")
        logger.info(f"   └─ Cascade deleted: {lamaran_count} lamaran record(s), {favorit_count} favorit record(s)")
        
        return True, f"Beasiswa '{existing_judul}' berhasil dihapus! (Cascade: {lamaran_count} lamaran, {favorit_count} favorit)"
        
    except sqlite3.Error as e:
        conn.rollback()
        logger.error(f"❌ Database error saat delete beasiswa: {e}")
        return False, f"Terjadi error database: {str(e)}"
        
    finally:
        cursor.close()
        conn.close()


if __name__ == "__main__":
    # Script untuk testing
    init_db()
    print("✅ Database schema created successfully!")
