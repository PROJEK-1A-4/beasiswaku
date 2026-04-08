# 🗄️ DATABASE & CONNECTION GUIDE

## 1️⃣ **DATABASE APA YANG DIGUNAKAN?**

### **SQLite 3** ✅

```
Database Type:  SQLite 3 (lightweight, file-based)
Location:       database/beasiswaku.db
Size:           ~45 KB (file berdiri sendiri)
Koneksi:        Lokal (tidak perlu server)
```

### Mengapa SQLite?

| Aspek | SQLite |
|-------|--------|
| Install | ✅ Built-in (tidak perlu install) |
| Setup | ✅ Instant (no config needed) |
| Standalone | ✅ 1 file database |
| Speed | ✅ Fast untuk CRUD |
| Python | ✅ Module `sqlite3` built-in |
| Cocok untuk | ✅ Desktop app, single-user, offline-first |

**Tidak perlu**:
- ❌ MySQL server
- ❌ PostgreSQL server  
- ❌ MongoDB instance
- ❌ Docker container
- ❌ Network setup

Semua dalam 1 file: `database/beasiswaku.db` ✨

---

## 2️⃣ **BAGAIMANA CARA KONEKSI?**

### **A. Connection Method (Di Python)**

```python
import sqlite3
from pathlib import Path

# Definisikan path database
DB_PATH = Path("database/beasiswaku.db")

# Buka koneksi
def get_connection():
    conn = sqlite3.connect(str(DB_PATH))
    conn.row_factory = sqlite3.Row  # Enable column access by name
    return conn

# Gunakan koneksi
conn = get_connection()
cursor = conn.cursor()

# Query database
cursor.execute("SELECT * FROM beasiswa")
results = cursor.fetchall()

# Close
cursor.close()
conn.close()
```

### **B. Cara Koneksi di BeasiswaKu:**

**File:** [crud.py](crud.py) → Function `get_connection()`

```python
def get_connection():
    """
    Membuka koneksi ke database SQLite.
    
    Returns:
        sqlite3.Connection: Koneksi ke database
    """
    conn = sqlite3.connect(str(DB_PATH))
    conn.row_factory = sqlite3.Row  # Enable column access by name
    return conn
```

**Digunakan di semua CRUD functions:**
- ✅ `register_user()` - write to akun table
- ✅ `login_user()` - read from akun table
- ✅ Eventually: `add_beasiswa()`, `edit_beasiswa()`, dll

### **C. Lifecycle Koneksi:**

```
1. get_connection()          → Buka koneksi ke beasiswaku.db
2. cursor = conn.cursor()    → Siap execute queries
3. cursor.execute(SQL)       → Jalankan query
4. conn.commit()             → Simpan perubahan (INSERT/UPDATE/DELETE)
5. cursor.close()            → Tutup cursor
6. conn.close()              → Tutup koneksi
```

### **D. Error Handling:**

Koneksi sudah include error handling:

```python
try:
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("INSERT INTO akun ...")
    conn.commit()
    return True, "Success"
except sqlite3.IntegrityError as e:
    conn.rollback()  # Batalkan perubahan
    return False, f"Error: {e}"
finally:
    cursor.close()
    conn.close()
```

---

## 3️⃣ **APAKAH PROGRAM SUDAH BISA DIRUN?**

### **Status Sekarang:** 🔶 **PARTIAL** (50% siap)

| Komponan | Status | Keterangan |
|----------|--------|-----------|
| **Database Schema** | ✅ DONE | 5 tabel siap |
| **Authentication** | ✅ DONE | register, login, password hashing |
| **Test Suite** | ✅ DONE | test_phase_1_1.py |
| **GUI (main.py)** | ❌ EMPTY | Belum ada implementasi |
| **CRUD Beasiswa** | ❌ MISSING | add/get/edit/delete beasiswa |
| **CRUD Lamaran** | ❌ MISSING | add/get/edit/delete lamaran |
| **Dependencies** | ⚠️ PARTIAL | PyQt6 & lxml belum install |

---

## 4️⃣ **SEBELUM BISA RUN, INSTALL DEPENDENCIES DULU!**

### **Step 1: Install packages dari requirements.txt**

```bash
pip install -r requirements.txt
```

Ini akan install:
```
PyQt6              → GUI framework
matplotlib         → Charts/visualisasi
requests           → HTTP requests (untuk scraper)
beautifulsoup4     → Web scraping
lxml               → XML parsing
bcrypt             → Password hashing
plyer              → Notifications
```

### **Step 2: Verify install**

```bash
python3 << 'EOF'
import sqlite3
import bcrypt
import PyQt6.QtWidgets
print("✅ Semua import berhasil!")
EOF
```

**Output jika berhasil:**
```
✅ Semua import berhasil!
```

### **Step 3: Check database**

```bash
python3 -c "from crud import init_db; init_db()"
ls -lah database/beasiswaku.db
```

**Output jika berhasil:**
```
-rw-r--r-- 1 user user 45056 Apr  8 22:05 database/beasiswaku.db
```

---

## 5️⃣ **COMMAND YANG BISA DIJALANKAN SEKARANG:**

### ✅ **Sudah bisa:**

```bash
# 1. Initialize database
python3 -c "from crud import init_db; init_db()"

# 2. Test database schema
python3 test_phase_1_1.py

# 3. Test authentication (register & login)
python3 << 'EOF'
from crud import register_user, login_user

# Register user baru
success, msg = register_user("john_doe", "john@example.com", "password123")
print(f"Register: {msg}")

# Login
success, msg, user = login_user("john_doe", "password123")
if success:
    print(f"Login: {msg}")
    print(f"User: {user}")
EOF

# 4. Direct SQL queries via sqlite3
sqlite3 database/beasiswaku.db "SELECT * FROM akun;"
```

### ❌ **Belum bisa:**

```bash
# GUI (empty main.py)
python3 main.py → Error: No GUI implemented yet

# Scraping (empty scraper.py)
python3 scraper.py → Error: No scraper implemented yet

# CRUD Beasiswa (functions missing)
python3 -c "from crud import add_beasiswa" → Error: Function not found
```

---

## 6️⃣ **ROADMAP: ISI YANG HARUS DIKERJAKAN UNTUK FULL RUN**

### **Next Steps (Urutan):**

```
✅ Phase 1.1: Database Schema (DONE)
✅ Phase 1.2: Authentication (DONE)
⏳ Phase 1.3: Main Window GUI  ← Darva/Kyla
   - Login screen
   - Main window with tabs (Beasiswa | Tracker | Statistik)
   - Logout functionality

⏳ Phase 2.2: CRUD Beasiswa Functions  ← Darva
   - add_beasiswa()
   - get_beasiswa_list()
   - edit_beasiswa()
   - delete_beasiswa()

⏳ Phase 2.1: Auto Scraper  ← Kemal
   - scrape_beasiswa_data()
   - Parse website
   - Insert to beasiswa table

⏳ Phase 2.3: Tab Beasiswa UI  ← Kyla
   - Display tabel beasiswa
   - Filter & search
   - CRUD UI panels

⏳ Phase 3: Tab Tracker & Lamaran  ← Darva + Kyla

⏳ Phase 4: Tab Statistik & Charts  ← Aulia + Kyla

⏳ Phase 5: Features tambahan
```

---

## 7️⃣ **TROUBLESHOOTING**

### **Error: "No module named 'sqlite3'"**
```bash
# sqlite3 sudah built-in, cek Python version
python3 --version

# Jika masalah persistence, reinstall Python
# Tidak perlu install sqlite3 terpisah
```

### **Error: "Database is locked"**
```python
# Terjadi saat concurrent access
# Solution: Pastikan close() connection setelah use
conn.close()  # Selalu tutup!
```

### **Error: "Foreign key constraint failed"**
```sql
-- Enable foreign keys di SQLite
PRAGMA foreign_keys = ON;
```

### **Error: "No such table"**
```bash
# Pastikan sudah init database
python3 -c "from crud import init_db; init_db()"
```

---

## 📋 **CHECKLIST: SIAP UNTUK RUN?**

- [ ] Dependencies installed? → Run `pip install -r requirements.txt`
- [ ] Database file ada? → Check `database/beasiswaku.db`
- [ ] Test suite passed? → Run `python3 test_phase_1_1.py`
- [ ] Can authenticate? → Run register & login test
- [ ] **NO**, main.py masih kosong

---

## 🎯 **KESIMPULAN JAWABAN**

| Pertanyaan | Jawaban |
|-----------|---------|
| **Database apa?** | **SQLite 3** (file-based, built-in) |
| **Dimana lokasinya?** | `database/beasiswaku.db` |
| **Cara koneksi?** | Via `sqlite3.connect()` di Python |
| **Koneksi siap?** | ✅ YA - Function `get_connection()` sudah ada |
| **Bisa di-run sekarang?** | 🔶 PARTIAL - Backend OK, GUI belum |
| **Yang perlu dilakukan?** | 1. Install dependencies: `pip install -r requirements.txt` |
|  | 2. Implement main.py GUI |
|  | 3. Implement CRUD functions |
| **Berapa lama setup?** | 5 menit (install + verify) |

---

## 🚀 **NEXT COMMAND UNTUK DICOBA:**

```bash
# 1. Install dependencies (5 menit)
pip install -r requirements.txt

# 2. Verify setup (30 detik)
python3 -c "from crud import init_db, register_user; init_db(); print('✅ Setup OK')"

# 3. Test authentication (1 menit)
python3 test_auth.py  # (saya buatkan di langkah berikut)

# 4. Lanjut ke Phase 2.2: CRUD Beasiswa
```

---

**Mau saya buatkan test file untuk authentication agar bisa lihat database connection berfungsi?**

Atau langsung ke Phase 2.2 (CRUD Beasiswa)?
