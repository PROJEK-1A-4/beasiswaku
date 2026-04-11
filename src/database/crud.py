"""
crud.py - Database CRUD operations dan Authentication
Untuk BeasiswaKu - Personal Scholarship Manager

Tanggung jawab:
- Database initialization dan schema management  (delegated to src.core.database)
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

from ..core.database import DatabaseManager
from ..core.config import Config

# Setup logging
logger = logging.getLogger(__name__)


def get_connection():
    """
    Membuka koneksi ke database SQLite.
    Uses DatabaseManager singleton for connection pooling.
    
    Returns:
        sqlite3.Connection: Koneksi ke database
    """
    db = DatabaseManager()
    return db.get_connection()


def init_db():
    """
    Menginisialisasi database dan membuat semua tabel jika belum ada.
    Delegates to DatabaseManager.init_schema()
    """
    db = DatabaseManager()
    db.init_schema()


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


# =====================================================================
# PHASE 3.1: CRUD LAMARAN FUNCTIONS
# =====================================================================

def add_lamaran(user_id: int, beasiswa_id: int, tanggal_daftar: Optional[str] = None,
               status: str = "Pending", catatan: str = "") -> Tuple[bool, str, Optional[int]]:
    """
    Menambahkan lamaran beasiswa baru (application record).
    
    Args:
        user_id (int): ID user yang melakukan lamaran (required)
        beasiswa_id (int): ID beasiswa yang didaftar (required)
        tanggal_daftar (str, optional): Tanggal pendaftaran (format YYYY-MM-DD)
            - Jika None, akan menggunakan tanggal hari ini
        status (str, optional): Status lamaran - default 'Pending'
            - Valid values: Pending, Submitted, Accepted, Rejected, Withdrawn
        catatan (str, optional): Catatan/notes tentang lamaran
    
    Returns:
        Tuple[bool, str, Optional[int]]:
            - (True, "Success message", lamaran_id) jika berhasil
            - (False, "Error message", None) jika gagal
    
    Error cases:
        - User ID tidak valid
        - Beasiswa ID tidak valid (foreign key)
        - User sudah pernah mendaftar beasiswa ini (UNIQUE constraint)
        - Database error
    
    Example:
        >>> success, msg, id = add_lamaran(
        ...     user_id=1,
        ...     beasiswa_id=5,
        ...     tanggal_daftar="2026-04-08",
        ...     status="Submitted"
        ... )
        >>> if success:
        ...     print(f"Lamaran added with ID: {id}")
    """
    # Validasi input
    if not user_id or not isinstance(user_id, int):
        return False, "User ID harus berupa angka integer", None
    
    if not beasiswa_id or not isinstance(beasiswa_id, int):
        return False, "Beasiswa ID harus berupa angka integer", None
    
    # Set default tanggal_daftar jika tidak diberikan
    if tanggal_daftar is None or tanggal_daftar.strip() == "":
        tanggal_daftar = datetime.now().strftime('%Y-%m-%d')
    else:
        # Validasi format tanggal_daftar (YYYY-MM-DD)
        try:
            datetime.strptime(tanggal_daftar.strip(), '%Y-%m-%d')
            tanggal_daftar = tanggal_daftar.strip()
        except ValueError:
            return False, "Format tanggal_daftar harus YYYY-MM-DD (contoh: 2026-04-08)", None
    
    # Validasi status
    valid_status = ['Pending', 'Submitted', 'Accepted', 'Rejected', 'Withdrawn']
    if status not in valid_status:
        return False, f"Status harus salah satu dari: {', '.join(valid_status)}", None
    
    try:
        conn = get_connection()
        cursor = conn.cursor()
        
        # Enable foreign key checking
        cursor.execute("PRAGMA foreign_keys = ON")
        
        # Check if user exists
        cursor.execute("SELECT id, username FROM akun WHERE id = ?", (user_id,))
        user = cursor.fetchone()
        if not user:
            return False, f"User dengan ID {user_id} tidak ditemukan", None
        
        # Check if beasiswa exists
        cursor.execute("SELECT id, judul FROM beasiswa WHERE id = ?", (beasiswa_id,))
        beasiswa = cursor.fetchone()
        if not beasiswa:
            return False, f"Beasiswa dengan ID {beasiswa_id} tidak ditemukan", None
        
        # Insert lamaran
        cursor.execute("""
            INSERT INTO riwayat_lamaran (
                user_id, beasiswa_id, tanggal_daftar, status, catatan
            ) VALUES (?, ?, ?, ?, ?)
        """, (user_id, beasiswa_id, tanggal_daftar, status, catatan.strip()))
        
        conn.commit()
        lamaran_id = cursor.lastrowid
        
        logger.info(f"✅ Lamaran '{beasiswa['judul']}' for user {user['username']} "
                   f"added successfully (ID: {lamaran_id}, Status: {status})")
        return True, f"Lamaran untuk '{beasiswa['judul']}' berhasil ditambahkan!", lamaran_id
        
    except sqlite3.IntegrityError as e:
        conn.rollback()
        if "UNIQUE" in str(e):
            error_msg = "Anda sudah pernah mendaftar beasiswa ini sebelumnya"
        elif "FOREIGN KEY" in str(e):
            error_msg = f"User atau Beasiswa tidak ditemukan"
        else:
            error_msg = f"Data constraint violation: {str(e)}"
        logger.warning(f"⚠️ Lamaran add failed: {error_msg}")
        return False, error_msg, None
        
    except sqlite3.Error as e:
        conn.rollback()
        logger.error(f"❌ Database error saat menambah lamaran: {e}")
        return False, f"Terjadi error database: {str(e)}", None
        
    finally:
        cursor.close()
        conn.close()


def get_lamaran_list(filter_user_id: Optional[int] = None,
                    filter_beasiswa_id: Optional[int] = None,
                    filter_status: Optional[str] = None,
                    sort_by: str = 'tanggal_daftar',
                    sort_order: str = 'DESC') -> Tuple[List[Dict], int]:
    """
    Mengambil list lamaran dari database dengan support filter dan sorting.
    
    Args:
        filter_user_id (int, optional): Filter by user ID
        filter_beasiswa_id (int, optional): Filter by beasiswa ID
        filter_status (str, optional): Filter by status (Pending, Submitted, Accepted, Rejected, Withdrawn)
        sort_by (str, optional): Column to sort by (tanggal_daftar, status, created_at, user_id, beasiswa_id)
            - default: 'tanggal_daftar'
        sort_order (str, optional): Sort order (ASC, DESC) - default: 'DESC'
    
    Returns:
        Tuple[List[Dict], int]:
            - (lamaran_list, total_count) - list of lamaran records and total count
            - Each record contains: id, user_id, beasiswa_id, status, tanggal_daftar, 
              catatan, created_at, updated_at, plus joined fields: username, beasiswa_judul, jenjang
    
    Example:
        >>> lamarans, total = get_lamaran_list(
        ...     filter_user_id=1,
        ...     filter_status='Accepted',
        ...     sort_by='tanggal_daftar',
        ...     sort_order='DESC'
        ... )
        >>> print(f"Found {total} accepted applications")
        >>> for l in lamarans:
        ...     print(f"{l['username']} - {l['beasiswa_judul']}: {l['status']}")
    """
    try:
        conn = get_connection()
        cursor = conn.cursor()
        
        # Build WHERE clause dynamically
        where_clauses = []
        params = []
        
        # Filter by user_id
        if filter_user_id:
            if isinstance(filter_user_id, int):
                where_clauses.append("rl.user_id = ?")
                params.append(filter_user_id)
        
        # Filter by beasiswa_id
        if filter_beasiswa_id:
            if isinstance(filter_beasiswa_id, int):
                where_clauses.append("rl.beasiswa_id = ?")
                params.append(filter_beasiswa_id)
        
        # Filter by status
        if filter_status:
            filter_status = filter_status.strip()
            valid_status = ['Pending', 'Submitted', 'Accepted', 'Rejected', 'Withdrawn']
            if filter_status in valid_status:
                where_clauses.append("rl.status = ?")
                params.append(filter_status)
        
        # Build WHERE clause string
        where_sql = ""
        if where_clauses:
            where_sql = "WHERE " + " AND ".join(where_clauses)
        
        # Validate sort_by
        valid_sort_columns = ['tanggal_daftar', 'status', 'created_at', 'user_id', 'beasiswa_id']
        sort_by = sort_by.strip().lower() if sort_by else 'tanggal_daftar'
        if sort_by not in valid_sort_columns:
            sort_by = 'tanggal_daftar'
        
        # Add table alias for sort
        sort_column = f"rl.{sort_by}"
        
        # Validate sort_order
        sort_order = sort_order.strip().upper() if sort_order else 'DESC'
        if sort_order not in ['ASC', 'DESC']:
            sort_order = 'DESC'
        
        # Get total count
        count_query = f"""
            SELECT COUNT(*) as count 
            FROM riwayat_lamaran rl
            {where_sql}
        """
        cursor.execute(count_query, params)
        total_count = cursor.fetchone()['count']
        
        # Get data with sorting and joined fields
        query = f"""
            SELECT 
                rl.id, rl.user_id, rl.beasiswa_id, rl.status, rl.tanggal_daftar, 
                rl.catatan, rl.created_at, rl.updated_at,
                a.username, b.judul as beasiswa_judul, b.jenjang
            FROM riwayat_lamaran rl
            JOIN akun a ON rl.user_id = a.id
            JOIN beasiswa b ON rl.beasiswa_id = b.id
            {where_sql}
            ORDER BY {sort_column} {sort_order}
        """
        
        cursor.execute(query, params)
        results = cursor.fetchall()
        
        # Convert to list of dictionaries
        lamaran_list = [dict(row) for row in results]
        
        logger.info(f"✅ Retrieved {len(lamaran_list)} lamarans "
                   f"(Total: {total_count}, Filter: user_id={filter_user_id}, "
                   f"beasiswa_id={filter_beasiswa_id}, status={filter_status})")
        
        cursor.close()
        conn.close()
        
        return lamaran_list, total_count
        
    except sqlite3.Error as e:
        logger.error(f"❌ Database error saat retrieve lamarans: {e}")
        return [], 0


def edit_lamaran(lamaran_id: int, **kwargs) -> Tuple[bool, str]:
    """
    Mengupdate data lamaran yang sudah ada.
    
    Args:
        lamaran_id (int): ID lamaran yang akan diupdate
        **kwargs: Field-field yang ingin diupdate (status, tanggal_daftar, catatan)
    
    Returns:
        Tuple[bool, str]:
            - (True, "Success message") jika berhasil
            - (False, "Error message") jika gagal
    
    Validation rules:
        - status: harus salah satu dari Pending, Submitted, Accepted, Rejected, Withdrawn
        - tanggal_daftar: format YYYY-MM-DD
        - catatan: text field, optional
    
    Example:
        >>> success, msg = edit_lamaran(
        ...     1,
        ...     status="Accepted",
        ...     catatan="Diterima dengan nilai tertinggi"
        ... )
        >>> if success:
        ...     print("Update successful!")
    """
    if not lamaran_id or not isinstance(lamaran_id, int):
        return False, "ID lamaran harus berupa angka integer"
    
    if not kwargs:
        return False, "Tidak ada field yang diupdate"
    
    # Validasi setiap field yang akan diupdate
    allowed_fields = {
        'status': str,
        'tanggal_daftar': str,
        'catatan': str,
    }
    
    # Build update clauses dan prepare params
    update_clauses = []
    params = []
    
    for field, value in kwargs.items():
        if field not in allowed_fields:
            return False, f"Field '{field}' tidak diizinkan untuk diupdate"
        
        # Validasi field-specific rules
        if field == 'status':
            status_val = str(value).strip()
            valid_status = ['Pending', 'Submitted', 'Accepted', 'Rejected', 'Withdrawn']
            if status_val not in valid_status:
                return False, f"Status harus salah satu dari: {', '.join(valid_status)}"
            update_clauses.append("status = ?")
            params.append(status_val)
        
        elif field == 'tanggal_daftar':
            if not value or not str(value).strip():
                return False, "Tanggal daftar tidak boleh kosong"
            try:
                datetime.strptime(str(value).strip(), '%Y-%m-%d')
            except ValueError:
                return False, "Format tanggal_daftar harus YYYY-MM-DD (contoh: 2026-04-08)"
            update_clauses.append("tanggal_daftar = ?")
            params.append(str(value).strip())
        
        elif field == 'catatan':
            update_clauses.append("catatan = ?")
            params.append(str(value).strip() if value else "")
    
    if not update_clauses:
        return False, "Tidak ada field yang valid untuk diupdate"
    
    # Add updated_at timestamp
    update_clauses.append("updated_at = CURRENT_TIMESTAMP")
    
    # Add lamaran_id untuk WHERE clause
    params.append(lamaran_id)
    
    try:
        conn = get_connection()
        cursor = conn.cursor()
        
        # Check if lamaran exists
        cursor.execute("""
            SELECT rl.id, a.username, b.judul 
            FROM riwayat_lamaran rl
            JOIN akun a ON rl.user_id = a.id
            JOIN beasiswa b ON rl.beasiswa_id = b.id
            WHERE rl.id = ?
        """, (lamaran_id,))
        existing = cursor.fetchone()
        
        if not existing:
            return False, f"Lamaran dengan ID {lamaran_id} tidak ditemukan"
        
        existing_desc = f"{existing['username']} → {existing['judul']}"
        
        # Update lamaran
        update_sql = f"""
            UPDATE riwayat_lamaran
            SET {', '.join(update_clauses)}
            WHERE id = ?
        """
        
        cursor.execute(update_sql, params)
        conn.commit()
        
        logger.info(f"✅ Lamaran '{existing_desc}' (ID: {lamaran_id}) updated successfully")
        return True, f"Lamaran '{existing_desc}' berhasil diupdate!"
        
    except sqlite3.Error as e:
        conn.rollback()
        logger.error(f"❌ Database error saat update lamaran: {e}")
        return False, f"Terjadi error database: {str(e)}"
        
    finally:
        cursor.close()
        conn.close()


def delete_lamaran(lamaran_id: int) -> Tuple[bool, str]:
    """
    Menghapus lamaran dari database.
    
    Args:
        lamaran_id (int): ID lamaran yang akan dihapus
    
    Returns:
        Tuple[bool, str]:
            - (True, "Success message") jika berhasil
            - (False, "Error message") jika gagal
    
    Example:
        >>> success, msg = delete_lamaran(1)
        >>> if success:
        ...     print("Lamaran deleted successfully")
        ... else:
        ...     print(f"Error: {msg}")
    """
    if not lamaran_id or not isinstance(lamaran_id, int):
        return False, "ID lamaran harus berupa angka integer"
    
    try:
        conn = get_connection()
        cursor = conn.cursor()
        
        # Check if lamaran exists
        cursor.execute("""
            SELECT rl.id, a.username, b.judul 
            FROM riwayat_lamaran rl
            JOIN akun a ON rl.user_id = a.id
            JOIN beasiswa b ON rl.beasiswa_id = b.id
            WHERE rl.id = ?
        """, (lamaran_id,))
        existing = cursor.fetchone()
        
        if not existing:
            return False, f"Lamaran dengan ID {lamaran_id} tidak ditemukan"
        
        existing_desc = f"{existing['username']} → {existing['judul']}"
        
        # Delete lamaran
        cursor.execute("DELETE FROM riwayat_lamaran WHERE id = ?", (lamaran_id,))
        conn.commit()
        
        logger.info(f"✅ Lamaran '{existing_desc}' (ID: {lamaran_id}) deleted successfully")
        return True, f"Lamaran '{existing_desc}' berhasil dihapus!"
        
    except sqlite3.Error as e:
        conn.rollback()
        logger.error(f"❌ Database error saat delete lamaran: {e}")
        return False, f"Terjadi error database: {str(e)}"
        
    finally:
        cursor.close()
        conn.close()


# =====================================================================
# PHASE 3.2: CRUD FAVORIT FUNCTIONS
# =====================================================================

def add_favorit(user_id: int, beasiswa_id: int) -> Tuple[bool, str, Optional[int]]:
    """
    Menambahkan beasiswa ke daftar favorit user.
    
    Args:
        user_id (int): ID user yang menambah favorit
        beasiswa_id (int): ID beasiswa yang akan difavoritkan
    
    Returns:
        Tuple[bool, str, Optional[int]]:
            - (True, "Success message", favorit_id) jika berhasil
            - (False, "Error message", None) jika gagal
    
    Error cases:
        - User ID tidak valid
        - Beasiswa ID tidak valid
        - Sudah di-favorite sebelumnya (UNIQUE constraint)
        - Database error
    
    Example:
        >>> success, msg, id = add_favorit(user_id=1, beasiswa_id=5)
        >>> if success:
        ...     print(f"Beasiswa added to favorites! ID: {id}")
    """
    if not user_id or not isinstance(user_id, int):
        return False, "User ID harus berupa angka integer", None
    
    if not beasiswa_id or not isinstance(beasiswa_id, int):
        return False, "Beasiswa ID harus berupa angka integer", None
    
    try:
        conn = get_connection()
        cursor = conn.cursor()
        
        # Enable foreign key checking
        cursor.execute("PRAGMA foreign_keys = ON")
        
        # Check if user exists
        cursor.execute("SELECT id, username FROM akun WHERE id = ?", (user_id,))
        user = cursor.fetchone()
        if not user:
            return False, f"User dengan ID {user_id} tidak ditemukan", None
        
        # Check if beasiswa exists
        cursor.execute("SELECT id, judul FROM beasiswa WHERE id = ?", (beasiswa_id,))
        beasiswa = cursor.fetchone()
        if not beasiswa:
            return False, f"Beasiswa dengan ID {beasiswa_id} tidak ditemukan", None
        
        # Insert favorit
        cursor.execute("""
            INSERT INTO favorit (user_id, beasiswa_id)
            VALUES (?, ?)
        """, (user_id, beasiswa_id))
        
        conn.commit()
        favorit_id = cursor.lastrowid
        
        logger.info(f"✅ Beasiswa '{beasiswa['judul']}' added to favorites for user {user['username']} (ID: {favorit_id})")
        return True, f"Beasiswa '{beasiswa['judul']}' ditambahkan ke favorit!", favorit_id
        
    except sqlite3.IntegrityError as e:
        conn.rollback()
        if "UNIQUE" in str(e):
            error_msg = "Beasiswa ini sudah ada di daftar favorit Anda"
        elif "FOREIGN KEY" in str(e):
            error_msg = "User atau Beasiswa tidak ditemukan"
        else:
            error_msg = f"Data constraint violation: {str(e)}"
        logger.warning(f"⚠️ Favorit add failed: {error_msg}")
        return False, error_msg, None
        
    except sqlite3.Error as e:
        conn.rollback()
        logger.error(f"❌ Database error saat menambah favorit: {e}")
        return False, f"Terjadi error database: {str(e)}", None
        
    finally:
        cursor.close()
        conn.close()


def get_favorit_list(user_id: int, sort_by: str = 'created_at',
                     sort_order: str = 'DESC') -> Tuple[List[Dict], int]:
    """
    Mengambil list favorit dari database untuk user tertentu.
    
    Args:
        user_id (int): ID user
        sort_by (str, optional): Column to sort by (created_at, judul, jenjang, deadline)
            - default: 'created_at'
        sort_order (str, optional): Sort order (ASC, DESC) - default: 'DESC'
    
    Returns:
        Tuple[List[Dict], int]:
            - (favorit_list, total_count) - list of favorite beasiswa records and total count
            - Each record contains: id, user_id, beasiswa_id, created_at, plus joined fields:
              judul, jenjang, deadline, benefit, status, penyelenggara_id
    
    Example:
        >>> favorit_list, total = get_favorit_list(user_id=1)
        >>> print(f"Found {total} favorite scholarships")
        >>> for fav in favorit_list:
        ...     print(f"{fav['judul']} - {fav['jenjang']}")
    """
    if not user_id or not isinstance(user_id, int):
        return [], 0
    
    try:
        conn = get_connection()
        cursor = conn.cursor()
        
        # Validate sort_by
        valid_sort_columns = ['created_at', 'judul', 'jenjang', 'deadline', 'status']
        sort_by = sort_by.strip().lower() if sort_by else 'created_at'
        if sort_by not in valid_sort_columns:
            sort_by = 'created_at'
        
        # For joined sort columns
        if sort_by in ['judul', 'jenjang', 'deadline', 'status']:
            sort_column = f"b.{sort_by}"
        else:
            sort_column = f"f.{sort_by}"
        
        # Validate sort_order
        sort_order = sort_order.strip().upper() if sort_order else 'DESC'
        if sort_order not in ['ASC', 'DESC']:
            sort_order = 'DESC'
        
        # Get total count
        count_query = """
            SELECT COUNT(*) as count 
            FROM favorit f
            WHERE f.user_id = ?
        """
        cursor.execute(count_query, (user_id,))
        total_count = cursor.fetchone()['count']
        
        # Get data with sorting and joined fields
        query = f"""
            SELECT 
                f.id, f.user_id, f.beasiswa_id, f.created_at,
                b.judul, b.jenjang, b.deadline, b.benefit, b.status,
                b.penyelenggara_id, b.minimal_ipk, b.coverage
            FROM favorit f
            JOIN beasiswa b ON f.beasiswa_id = b.id
            WHERE f.user_id = ?
            ORDER BY {sort_column} {sort_order}
        """
        
        cursor.execute(query, (user_id,))
        results = cursor.fetchall()
        
        # Convert to list of dictionaries
        favorit_list = [dict(row) for row in results]
        
        logger.info(f"✅ Retrieved {len(favorit_list)} favorites for user {user_id} (Total: {total_count})")
        
        cursor.close()
        conn.close()
        
        return favorit_list, total_count
        
    except sqlite3.Error as e:
        logger.error(f"❌ Database error saat retrieve favorit: {e}")
        return [], 0


def delete_favorit(user_id: int, beasiswa_id: int) -> Tuple[bool, str]:
    """
    Menghapus beasiswa dari daftar favorit user.
    
    Args:
        user_id (int): ID user
        beasiswa_id (int): ID beasiswa yang akan dihapus dari favorit
    
    Returns:
        Tuple[bool, str]:
            - (True, "Success message") jika berhasil
            - (False, "Error message") jika gagal
    
    Example:
        >>> success, msg = delete_favorit(user_id=1, beasiswa_id=5)
        >>> if success:
        ...     print("Beasiswa removed from favorites")
    """
    if not user_id or not isinstance(user_id, int):
        return False, "User ID harus berupa angka integer"
    
    if not beasiswa_id or not isinstance(beasiswa_id, int):
        return False, "Beasiswa ID harus berupa angka integer"
    
    try:
        conn = get_connection()
        cursor = conn.cursor()
        
        # Check if favorit exists
        cursor.execute("""
            SELECT f.id, b.judul 
            FROM favorit f
            JOIN beasiswa b ON f.beasiswa_id = b.id
            WHERE f.user_id = ? AND f.beasiswa_id = ?
        """, (user_id, beasiswa_id))
        existing = cursor.fetchone()
        
        if not existing:
            return False, f"Beasiswa tidak ada di daftar favorit Anda"
        
        existing_judul = existing['judul']
        
        # Delete favorit
        cursor.execute("""
            DELETE FROM favorit 
            WHERE user_id = ? AND beasiswa_id = ?
        """, (user_id, beasiswa_id))
        
        conn.commit()
        
        logger.info(f"✅ Beasiswa '{existing_judul}' removed from favorites for user {user_id}")
        return True, f"Beasiswa '{existing_judul}' dihapus dari favorit!"
        
    except sqlite3.Error as e:
        conn.rollback()
        logger.error(f"❌ Database error saat delete favorit: {e}")
        return False, f"Terjadi error database: {str(e)}"
        
    finally:
        cursor.close()
        conn.close()


# ========================== PHASE 4.1 AGGREGATION QUERIES ==========================

def get_beasiswa_per_jenjang() -> Dict[str, int]:
    """
    Mengambil jumlah beasiswa per jenjang pendidikan.
    
    Mengagregasi data beasiswa berdasarkan jenjang (D3, D4, S1, S2)
    dan mengembalikan count untuk masing-masing level.
    
    Returns:
        Dict[str, int]: Dictionary dengan format {jenjang: count}
            Contoh: {'D3': 5, 'D4': 8, 'S1': 15, 'S2': 3}
            Jenjang yang tidak memiliki beasiswa tidak akan muncul dalam dict.
    
    Example:
        >>> stats = get_beasiswa_per_jenjang()
        >>> print(f"Total S1: {stats.get('S1', 0)}")
        Total S1: 15
    """
    try:
        conn = get_connection()
        cursor = conn.cursor()
        
        # Query untuk count beasiswa per jenjang
        query = """
            SELECT jenjang, COUNT(*) as total
            FROM beasiswa
            WHERE jenjang IS NOT NULL
            GROUP BY jenjang
            ORDER BY jenjang ASC
        """
        
        cursor.execute(query)
        results = cursor.fetchall()
        
        # Convert ke dictionary
        jenjang_dict = {row['jenjang']: row['total'] for row in results}
        
        total_beasiswa = sum(jenjang_dict.values())
        logger.info(f"✅ Retrieved beasiswa per jenjang: {jenjang_dict} (Total: {total_beasiswa})")
        
        cursor.close()
        conn.close()
        
        return jenjang_dict
        
    except sqlite3.Error as e:
        logger.error(f"❌ Database error saat get beasiswa per jenjang: {e}")
        return {}


def get_top_penyelenggara(limit: int = 10) -> List[Dict[str, any]]:
    """
    Mengambil daftar penyelenggara dengan jumlah beasiswa terbanyak.
    
    Mengagregasi jumlah beasiswa per penyelenggara dan mengembalikan
    top N penyelenggara berdasarkan jumlah beasiswa yang disediakan.
    
    Args:
        limit (int, optional): Jumlah top penyelenggara yang dicari (default: 10)
    
    Returns:
        List[Dict[str, any]]: List of dictionaries dengan struktur:
            [{
                'penyelenggara_id': int,
                'nama_penyelenggara': str,
                'total_beasiswa': int,
                'website': str,
                'contact_email': str
            }, ...]
            List akan terurut dari jumlah beasiswa terbanyak ke paling sedikit.
            Jika tidak ada data, return list kosong.
    
    Example:
        >>> top_orgs = get_top_penyelenggara(limit=5)
        >>> for org in top_orgs:
        ...     print(f"{org['nama_penyelenggara']}: {org['total_beasiswa']} beasiswa")
    """
    if limit <= 0:
        return []
    
    try:
        conn = get_connection()
        cursor = conn.cursor()
        
        # Query untuk count beasiswa per penyelenggara
        # Menggunakan LEFT JOIN karena ada beasiswa yang belum memiliki penyelenggara
        query = """
            SELECT 
                p.id as penyelenggara_id,
                COALESCE(p.nama, '(Tidak Ada)') as nama_penyelenggara,
                COUNT(b.id) as total_beasiswa,
                COALESCE(p.website, '-') as website,
                COALESCE(p.contact_email, '-') as contact_email
            FROM beasiswa b
            LEFT JOIN penyelenggara p ON b.penyelenggara_id = p.id
            GROUP BY b.penyelenggara_id
            ORDER BY total_beasiswa DESC, nama_penyelenggara ASC
            LIMIT ?
        """
        
        cursor.execute(query, (limit,))
        results = cursor.fetchall()
        
        # Convert ke list of dictionaries
        penyelenggara_list = [dict(row) for row in results]
        
        total_count = len(penyelenggara_list)
        logger.info(f"✅ Retrieved top {total_count} penyelenggara")
        
        cursor.close()
        conn.close()
        
        return penyelenggara_list
        
    except sqlite3.Error as e:
        logger.error(f"❌ Database error saat get top penyelenggara: {e}")
        return []


def get_status_availability() -> Dict[str, int]:
    """
    Mengambil status ketersediaan beasiswa.
    
    Mengagregasi jumlah beasiswa berdasarkan status:
    - 'Buka': Beasiswa masih membuka pendaftaran
    - 'Segera Tutup': Deadline pendaftaran sudah dekat
    - 'Tutup': Beasiswa sudah ditutup
    
    Returns:
        Dict[str, int]: Dictionary dengan status sebagai key dan count sebagai value
            Contoh: {'Buka': 15, 'Segera Tutup': 5, 'Tutup': 3}
            Status yang tidak memiliki beasiswa tidak akan muncul dalam dict.
    
    Example:
        >>> availability = get_status_availability()
        >>> print(f"Total Buka: {availability.get('Buka', 0)}")
        Total Buka: 15
        >>> if availability.get('Tutup', 0) > 0:
        ...     print(f"Hati-hati! {availability['Tutup']} beasiswa sudah tutup")
    """
    try:
        conn = get_connection()
        cursor = conn.cursor()
        
        # Query untuk count beasiswa per status
        query = """
            SELECT 
                status,
                COUNT(*) as total
            FROM beasiswa
            WHERE status IS NOT NULL
            GROUP BY status
            ORDER BY 
                CASE status
                    WHEN 'Buka' THEN 1
                    WHEN 'Segera Tutup' THEN 2
                    WHEN 'Tutup' THEN 3
                    ELSE 4
                END
        """
        
        cursor.execute(query)
        results = cursor.fetchall()
        
        # Convert ke dictionary
        status_dict = {row['status']: row['total'] for row in results}
        
        total_beasiswa = sum(status_dict.values())
        logger.info(f"✅ Retrieved status availability: {status_dict} (Total: {total_beasiswa})")
        
        cursor.close()
        conn.close()
        
        return status_dict
        
    except sqlite3.Error as e:
        logger.error(f"❌ Database error saat get status availability: {e}")
        return {}


# ========================== PHASE 5 ENHANCEMENT ==========================

def check_user_applied(user_id: int, beasiswa_id: int) -> bool:
    """
    Cek apakah user sudah mendaftar beasiswa tertentu.
    
    Melihat di tabel riwayat_lamaran apakah ada record (user_id, beasiswa_id).
    
    Args:
        user_id (int): ID user yang dicek
        beasiswa_id (int): ID beasiswa yang dicek
    
    Returns:
        bool: True jika user sudah mendaftar, False jika belum
    
    Example:
        >>> if check_user_applied(user_id=1, beasiswa_id=5):
        ...     print("User sudah mendaftar beasiswa ini")
    """
    if not user_id or not isinstance(user_id, int):
        return False
    
    if not beasiswa_id or not isinstance(beasiswa_id, int):
        return False
    
    try:
        conn = get_connection()
        cursor = conn.cursor()
        
        # Check if record exists
        cursor.execute("""
            SELECT id FROM riwayat_lamaran
            WHERE user_id = ? AND beasiswa_id = ?
            LIMIT 1
        """, (user_id, beasiswa_id))
        
        result = cursor.fetchone()
        
        cursor.close()
        conn.close()
        
        return result is not None
        
    except sqlite3.Error as e:
        logger.error(f"❌ Database error saat check user applied: {e}")
        return False


def get_beasiswa_list_for_user(user_id: int,
                              filter_jenjang: Optional[str] = None,
                              filter_status: Optional[str] = None,
                              search_judul: Optional[str] = None,
                              sort_by: str = 'deadline',
                              sort_order: str = 'ASC') -> Tuple[List[Dict], int]:
    """
    Mengambil list beasiswa dengan informasi sudah daftar user.
    
    Sama seperti get_beasiswa_list() tapi menambahkan kolom 'sudah_daftar' 
    yang menunjukkan apakah user sudah mendaftar beasiswa tersebut.
    
    Args:
        user_id (int): ID user yang ingin lihat data beasiswa
        filter_jenjang (str, optional): Filter by jenjang (D3, D4, S1, S2)
        filter_status (str, optional): Filter by status (Buka, Segera Tutup, Tutup)
        search_judul (str, optional): Search by judul (case-insensitive LIKE)
        sort_by (str, optional): Column to sort by (deadline, judul, created_at, status)
        sort_order (str, optional): Sort order (ASC, DESC)
    
    Returns:
        Tuple[List[Dict], int]:
            - List of beasiswa with added 'sudah_daftar' field (True/False)
            - Total count of beasiswa
    
    Example:
        >>> beasiswa_list, total = get_beasiswa_list_for_user(
        ...     user_id=1,
        ...     filter_jenjang='S1',
        ...     filter_status='Buka'
        ... )
        >>> for b in beasiswa_list:
        ...     status = "✅ Sudah daftar" if b['sudah_daftar'] else "❌ Belum daftar"
        ...     print(f"{b['judul']} - {status}")
    """
    if not user_id or not isinstance(user_id, int):
        return [], 0
    
    try:
        # First get the beasiswa list (existing function)
        beasiswa_list, total_count = get_beasiswa_list(
            filter_jenjang=filter_jenjang,
            filter_status=filter_status,
            search_judul=search_judul,
            sort_by=sort_by,
            sort_order=sort_order
        )
        
        # Add sudah_daftar field for each beasiswa
        for beasiswa in beasiswa_list:
            beasiswa['sudah_daftar'] = check_user_applied(user_id, beasiswa['id'])
        
        logger.info(f"✅ Retrieved {len(beasiswa_list)} beasiswa for user {user_id} "
                   f"with 'sudah_daftar' status")
        
        return beasiswa_list, total_count
        
    except Exception as e:
        logger.error(f"❌ Error saat get beasiswa list for user: {e}")
        return [], 0


# ==================== PHASE 5.4: CATATAN PRIBADI (NOTES) ====================

def add_catatan(user_id: int, beasiswa_id: int, content: str) -> Tuple[bool, str, Optional[int]]:
    """
    Menambahkan catatan pribadi untuk beasiswa tertentu.
    
    Setiap user hanya bisa memiliki 1 catatan per beasiswa.
    Jika sudah ada, akan mengembalikan error (gunakan edit_catatan untuk update).
    
    Args:
        user_id (int): ID user
        beasiswa_id (int): ID beasiswa
        content (str): Isi catatan (minimal 1 karakter, maksimal 2000)
    
    Returns:
        Tuple[bool, str, Optional[int]]:
            - (True, "Success message", catatan_id) jika berhasil
            - (False, "Error message", None) jika ada error
    
    Raises:
        ValueError: Jika content kosong
        sqlite3.IntegrityError: Jika sudah ada catatan untuk user-beasiswa ini
    """
    if not user_id or not isinstance(user_id, int):
        return False, "User ID tidak valid", None
    
    if not beasiswa_id or not isinstance(beasiswa_id, int):
        return False, "Beasiswa ID tidak valid", None
    
    if not content or not isinstance(content, str) or len(content.strip()) == 0:
        return False, "Catatan tidak boleh kosong", None
    
    if len(content) > 2000:
        return False, "Catatan maksimal 2000 karakter", None
    
    conn = get_connection()
    cursor = conn.cursor()
    
    try:
        # Check if user exists
        cursor.execute("SELECT id FROM akun WHERE id = ?", (user_id,))
        if not cursor.fetchone():
            logger.error(f"❌ User dengan ID {user_id} tidak ditemukan")
            return False, f"User dengan ID {user_id} tidak ditemukan", None
        
        # Check if beasiswa exists
        cursor.execute("SELECT id FROM beasiswa WHERE id = ?", (beasiswa_id,))
        if not cursor.fetchone():
            logger.error(f"❌ Beasiswa dengan ID {beasiswa_id} tidak ditemukan")
            return False, f"Beasiswa dengan ID {beasiswa_id} tidak ditemukan", None
        
        # Insert catatan
        cursor.execute(
            "INSERT INTO catatan (user_id, beasiswa_id, content) VALUES (?, ?, ?)",
            (user_id, beasiswa_id, content.strip())
        )
        conn.commit()
        catatan_id = cursor.lastrowid
        
        logger.info(f"✅ Catatan untuk beasiswa {beasiswa_id} ditambahkan user {user_id} "
                   f"(ID: {catatan_id})")
        return True, f"Catatan berhasil ditambahkan", catatan_id
        
    except sqlite3.IntegrityError as e:
        logger.error(f"❌ Catatan untuk beasiswa ini sudah ada: {e}")
        return False, "Catatan untuk beasiswa ini sudah ada. Gunakan edit untuk mengupdate.", None
    except Exception as e:
        logger.error(f"❌ Error saat tambah catatan: {e}")
        return False, f"Error: {str(e)}", None
    finally:
        cursor.close()
        conn.close()


def get_catatan(user_id: int, beasiswa_id: int) -> Tuple[Optional[Dict], str]:
    """
    Mengambil catatan pribadi untuk beasiswa tertentu dari user.
    
    Args:
        user_id (int): ID user
        beasiswa_id (int): ID beasiswa
    
    Returns:
        Tuple[Optional[Dict], str]:
            - (Dict dengan fields: id, user_id, beasiswa_id, content, created_at, updated_at, atau None)
            - Message string
    
    Dict fields jika catatan ditemukan:
        - id: int - ID catatan
        - user_id: int - ID user
        - beasiswa_id: int - ID beasiswa
        - content: str - Isi catatan
        - created_at: str - Waktu buat
        - updated_at: str - Waktu update terakhir
    """
    if not user_id or not isinstance(user_id, int):
        return None, "User ID tidak valid"
    
    if not beasiswa_id or not isinstance(beasiswa_id, int):
        return None, "Beasiswa ID tidak valid"
    
    conn = get_connection()
    cursor = conn.cursor()
    
    try:
        cursor.execute(
            """SELECT id, user_id, beasiswa_id, content, created_at, updated_at 
               FROM catatan WHERE user_id = ? AND beasiswa_id = ?""",
            (user_id, beasiswa_id)
        )
        
        result = cursor.fetchone()
        
        if result:
            catatan = dict(result)
            logger.info(f"✅ Catatan ditemukan untuk user {user_id}, beasiswa {beasiswa_id}")
            return catatan, "Catatan ditemukan"
        else:
            logger.info(f"⚠️  Tidak ada catatan untuk user {user_id}, beasiswa {beasiswa_id}")
            return None, "Belum ada catatan untuk beasiswa ini"
        
    except Exception as e:
        logger.error(f"❌ Error saat ambil catatan: {e}")
        return None, f"Error: {str(e)}"
    finally:
        cursor.close()
        conn.close()


def edit_catatan(user_id: int, beasiswa_id: int, content: str) -> Tuple[bool, str]:
    """
    Mengupdate catatan pribadi untuk beasiswa tertentu.
    
    Args:
        user_id (int): ID user
        beasiswa_id (int): ID beasiswa
        content (str): Isi catatan baru (minimal 1 karakter, maksimal 2000)
    
    Returns:
        Tuple[bool, str]:
            - (True, "Success message") jika berhasil
            - (False, "Error message") jika ada error
    """
    if not user_id or not isinstance(user_id, int):
        return False, "User ID tidak valid"
    
    if not beasiswa_id or not isinstance(beasiswa_id, int):
        return False, "Beasiswa ID tidak valid"
    
    if not content or not isinstance(content, str) or len(content.strip()) == 0:
        return False, "Catatan tidak boleh kosong"
    
    if len(content) > 2000:
        return False, "Catatan maksimal 2000 karakter"
    
    conn = get_connection()
    cursor = conn.cursor()
    
    try:
        # Check if catatan exists
        cursor.execute(
            "SELECT id FROM catatan WHERE user_id = ? AND beasiswa_id = ?",
            (user_id, beasiswa_id)
        )
        
        if not cursor.fetchone():
            logger.error(f"❌ Catatan untuk user {user_id}, beasiswa {beasiswa_id} tidak ditemukan")
            return False, "Catatan tidak ditemukan"
        
        # Update catatan
        cursor.execute(
            """UPDATE catatan SET content = ?, updated_at = CURRENT_TIMESTAMP 
               WHERE user_id = ? AND beasiswa_id = ?""",
            (content.strip(), user_id, beasiswa_id)
        )
        conn.commit()
        
        logger.info(f"✅ Catatan untuk user {user_id}, beasiswa {beasiswa_id} diupdate")
        return True, "Catatan berhasil diupdate"
        
    except Exception as e:
        logger.error(f"❌ Error saat edit catatan: {e}")
        return False, f"Error: {str(e)}"
    finally:
        cursor.close()
        conn.close()


def delete_catatan(user_id: int, beasiswa_id: int) -> Tuple[bool, str]:
    """
    Menghapus catatan pribadi untuk beasiswa tertentu.
    
    Args:
        user_id (int): ID user
        beasiswa_id (int): ID beasiswa
    
    Returns:
        Tuple[bool, str]:
            - (True, "Success message") jika berhasil
            - (False, "Error message") jika ada error atau catatan tidak ditemukan
    """
    if not user_id or not isinstance(user_id, int):
        return False, "User ID tidak valid"
    
    if not beasiswa_id or not isinstance(beasiswa_id, int):
        return False, "Beasiswa ID tidak valid"
    
    conn = get_connection()
    cursor = conn.cursor()
    
    try:
        # Check if catatan exists
        cursor.execute(
            "SELECT id FROM catatan WHERE user_id = ? AND beasiswa_id = ?",
            (user_id, beasiswa_id)
        )
        
        if not cursor.fetchone():
            logger.error(f"❌ Catatan untuk user {user_id}, beasiswa {beasiswa_id} tidak ditemukan")
            return False, "Catatan tidak ditemukan"
        
        # Delete catatan
        cursor.execute(
            "DELETE FROM catatan WHERE user_id = ? AND beasiswa_id = ?",
            (user_id, beasiswa_id)
        )
        conn.commit()
        
        logger.info(f"✅ Catatan untuk user {user_id}, beasiswa {beasiswa_id} dihapus")
        return True, "Catatan berhasil dihapus"
        
    except Exception as e:
        logger.error(f"❌ Error saat delete catatan: {e}")
        return False, f"Error: {str(e)}"
    finally:
        cursor.close()
        conn.close()


def get_catatan_list(user_id: int, filter_jenjang: Optional[str] = None,
                     search_judul: Optional[str] = None) -> Tuple[List[Dict], int]:
    """
    Mengambil daftar semua catatan user dengan informasi beasiswa.
    
    Berguna untuk melihat semua catatan dalam satu list dengan detail beasiswa.
    
    Args:
        user_id (int): ID user
        filter_jenjang (str, optional): Filter by jenjang (D3, D4, S1, S2)
        search_judul (str, optional): Search beasiswa by judul (case-insensitive)
    
    Returns:
        Tuple[List[Dict], int]:
            - List of catatan dengan fields:
              * catatan_id: int
              * user_id: int
              * beasiswa_id: int
              * content: str - Isi catatan
              * created_at: str
              * updated_at: str
              * beasiswa_judul: str
              * beasiswa_jenjang: str
              * beasiswa_deadline: str
              * beasiswa_status: str
            - Total count
    """
    if not user_id or not isinstance(user_id, int):
        return [], 0
    
    conn = get_connection()
    cursor = conn.cursor()
    
    try:
        # Base query dengan join ke beasiswa table
        query = """
            SELECT 
                c.id as catatan_id,
                c.user_id,
                c.beasiswa_id,
                c.content,
                c.created_at,
                c.updated_at,
                b.judul as beasiswa_judul,
                b.jenjang as beasiswa_jenjang,
                b.deadline as beasiswa_deadline,
                b.status as beasiswa_status
            FROM catatan c
            JOIN beasiswa b ON c.beasiswa_id = b.id
            WHERE c.user_id = ?
        """
        params = [user_id]
        
        # Add filters
        if filter_jenjang:
            query += " AND b.jenjang = ?"
            params.append(filter_jenjang)
        
        if search_judul:
            query += " AND b.judul LIKE ?"
            params.append(f"%{search_judul}%")
        
        # Order by created_at descending (newest first)
        query += " ORDER BY c.created_at DESC"
        
        cursor.execute(query, params)
        results = cursor.fetchall()
        
        catatan_list = [dict(row) for row in results]
        total = len(catatan_list)
        
        logger.info(f"✅ Retrieved {total} catatan for user {user_id}")
        return catatan_list, total
        
    except Exception as e:
        logger.error(f"❌ Error saat ambil catatan list: {e}")
        return [], 0
    finally:
        cursor.close()
        conn.close()


if __name__ == "__main__":
    # Script untuk testing
    init_db()
    print("✅ Database schema created successfully!")
