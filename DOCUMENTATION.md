% BeasiswaKu - Dokumentasi Lengkap
% Sistem Manajemen Beasiswa Desktop
% April 2026

# BeasiswaKu - Dokumentasi Lengkap

## 📋 Daftar Isi
1. [Overview Proyek](#overview)
2. [Arsitektur Sistem](#arsitektur)
3. [Panduan Instalasi](#instalasi)
4. [Panduan Penggunaan](#penggunaan)
5. [Spesifikasi Teknis](#spesifikasi)
6. [API Reference](#api)
7. [Testing & QA](#testing)

---

## Overview Proyek {#overview}

### Apa itu BeasiswaKu?

**BeasiswaKu** adalah aplikasi desktop untuk manajemen beasiswa secara personal. Aplikasi ini membantu pengguna untuk:
- 📚 Melihat daftar beasiswa yang tersedia
- 📋 Melacak status lamaran beasiswa
- ⭐ Menyimpan beasiswa favorit
- 📝 Membuat catatan pribadi untuk setiap beasiswa
- 📊 Melihat statistik beasiswa per jenjang pendidikan

### Target Pengguna

- Mahasiswa yang mencari informasi beasiswa
- Pendaftar beasiswa yang ingin mengorganisir lamaran mereka
- Siapapun yang ingin memantau peluang beasiswa

### Fitur Utama

| Fitur | Deskripsi | Status |
|-------|-----------|--------|
| 🔐 Autentikasi | Login/Register dengan bcrypt | ✅ Complete |
| 💾 Database | SQLite dengan 6 tabel | ✅ Complete |
| 📚 Manajemen Beasiswa | CRUD lengkap + filter/sort | ✅ Complete |
| 📋 Tracking Lamaran | Catat status aplikasi | ✅ Complete |
| ⭐ Favorit | Bookmark beasiswa pilihan | ✅ Complete |
| 📝 Catatan Pribadi | Notes per beasiswa | ✅ Complete |
| 📊 Statistik | Analytics per jenjang | ✅ Complete |
| 🖥️ GUI | PyQt6 Interface | ✅ Complete |

---

## Arsitektur Sistem {#arsitektur}

### Struktur Folder

```
beasiswaku/
├── crud.py                 # Backend CRUD operations (2,117 lines)
├── main.py                 # GUI entry point (562 lines)
├── gui_favorit.py          # Favorit UI components (446 lines)
├── gui_notes.py            # Notes UI components (539 lines)
├── scraper.py              # Web scraper (untuk future use)
├── visualisasi.py          # Data visualization (untuk future use)
├── requirements.txt        # Python dependencies
├── database/
│   └── beasiswaku.db       # SQLite database (auto-created)
├── test_*.py               # Test suites (10 files)
└── assets/                 # Resources folder
```

### Arsitektur Aplikasi

```
┌─────────────────────────────────────────────┐
│         PyQt6 GUI Layer                     │
│  ┌───────────────────────────────────────┐  │
│  │  main.py (LoginWindow, MainWindow)    │  │
│  │  gui_favorit.py (Favorit components)  │  │
│  │  gui_notes.py (Notes components)      │  │
│  └───────────────────────────────────────┘  │
└─────────────────────────────────────────────┘
           ↓ PyQt Signals/Slots ↓
┌─────────────────────────────────────────────┐
│    Business Logic Layer (crud.py)           │
│  ┌───────────────────────────────────────┐  │
│  │  Authentication (register/login)      │  │
│  │  CRUD Operations (4 x 4 functions)    │  │
│  │  Aggregations & Helpers               │  │
│  │  Validation & Error Handling          │  │
│  └───────────────────────────────────────┘  │
└─────────────────────────────────────────────┘
           ↓ SQL Queries ↓
┌─────────────────────────────────────────────┐
│    Database Layer (SQLite)                  │
│  ┌───────────────────────────────────────┐  │
│  │  6 Tables: akun, penyelenggara,       │  │
│  │  beasiswa, riwayat_lamaran,           │  │
│  │  favorit, catatan                     │  │
│  └───────────────────────────────────────┘  │
└─────────────────────────────────────────────┘
```

### Technology Stack

- **Language**: Python 3.x
- **GUI Framework**: PyQt6
- **Database**: SQLite 3
- **Authentication**: bcrypt for password hashing
- **Logging**: Python logging module
- **Testing**: Custom test suites

---

## Panduan Instalasi {#instalasi}

### Requirement

- Python 3.8+
- pip (Python package manager)
- ~50 MB disk space

### Langkah Instalasi

#### 1. Setup Python Environment

```bash
# Create virtual environment
python3 -m venv ~/.local/share/beasiswa/env

# Activate virtual environment
source ~/.local/share/beasiswa/env/bin/activate

# Upgrade pip
pip install --upgrade pip
```

#### 2. Install Dependencies

```bash
# Clone/download project
cd beasiswaku

# Install requirements
pip install -r requirements.txt
```

**requirements.txt:**
```
PyQt6==6.4.0
matplotlib==3.7.0
requests==2.31.0
beautifulsoup4==4.12.0
lxml==4.9.0
bcrypt==4.0.1
plyer==2.1.0
```

#### 3. Verify Installation

```bash
# Run comprehensive analysis
python3 comprehensive_analysis.py

# Run all tests
python3 test_phase_1_1.py
python3 test_auth_demo.py
python3 test_phase_2_2.py
# ... etc
```

#### 4. First Run

```bash
# Run the application
python3 main.py

# Database akan auto-created on first run
```

---

## Panduan Penggunaan {#penggunaan}

### 1. Login / Register

**First Time User (Register):**
1. Click "📝 Register" button pada login screen
2. Isi form dengan:
   - Username (unique)
   - Email (valid format)
   - Password (minimum 6 chars, dengan uppercase, number, special char)
3. Click "Register"
4. Redirect ke login screen
5. Login dengan username dan password

**Existing User (Login):**
1. Input username dan password
2. Click "Login"
3. Success → Main Window

### 2. Main Window - 3 Tabs

#### Tab 1: Beasiswa 📚
- **Lihat Daftar Beasiswa**: Semua beasiswa dengan filter & sort
- **Filter Options**:
  - Filter by Jenjang (D3, D4, S1, S2)
  - Filter by Status (Buka, Segera Tutup, Tutup)
  - Search by Judul
- **Action per Beasiswa**:
  - ⭐ Toggle Favorit
  - 📝 Edit/Add Catatan
  - 📋 Daftar Lamaran
  - ℹ️ View Details

#### Tab 2: Tracker 📋
- **Lihat Riwayat Lamaran**: Status semua lamaran Anda
- **Update Status**: Pending → Approved/Rejected
- **Filter**: By Status, by Jenjang

#### Tab 3: Statistik 📊
- **Statistik Beasiswa**: Count per jenjang
- **Top Penyelenggara**: Provider dengan most beasiswa
- **Status Distribution**: Buka/Tutup breakdown

### 3. Favorit Management

**Add Favorit:**
1. Di Beasiswa tab, click ⭐ button
2. Icon berubah jadi filled star (⭐)
3. Beasiswa disimpan ke favorit list

**View Favorit:**
1. View Favorit widget (shows all favorited)
2. Click "Edit" untuk manage
3. Click "❌ Remove" untuk hapus

**Quick Access:**
1. Favorit terbaru di dashboard
2. Quick access ke favorited beasiswa

### 4. Catatan Management

**Add Note:**
1. Click 📄 button di Beasiswa
2. Dialog terbuka → Edit notes
3. Type content (max 2000 chars)
4. Click "💾 Save"

**Edit Note:**
1. Click 📝 button (jika ada notes)
2. Dialog terbuka dengan existing content
3. Update text
4. Click "💾 Save"

**Delete Note:**
1. Di note editor dialog
2. Click "🗑️ Hapus"
3. Confirm deletion

---

## Spesifikasi Teknis {#spesifikasi}

### Database Schema

#### 1. Table: akun (Users)
```sql
CREATE TABLE akun (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT UNIQUE NOT NULL,
    email TEXT UNIQUE NOT NULL,
    password_hash TEXT NOT NULL,
    nama_lengkap TEXT,
    jenjang TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
)
```

**Fields:**
- `id`: User identifier
- `username`: Login username (unique)
- `email`: User email (unique, validated)
- `password_hash`: bcrypt hashed password
- `nama_lengkap`: Full name (optional)
- `jenjang`: Education level (D3/D4/S1/S2)
- `created_at`: Account creation timestamp
- `updated_at`: Last update timestamp

#### 2. Table: beasiswa (Scholarships)
```sql
CREATE TABLE beasiswa (
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
```

**Key Fields:**
- `judul`: Scholarship name
- `jenjang`: Target education level (D3, D4, S1, S2)
- `deadline`: Application deadline (YYYY-MM-DD format)
- `status`: Buka/Segera Tutup/Tutup
- `minimal_ipk`: Minimum GPA requirement
- `coverage`: Fully/Partially/Other coverage type

#### 3. Table: riwayat_lamaran (Applications)
```sql
CREATE TABLE riwayat_lamaran (
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
```

**Unique Constraint**: One application per user per scholarship

#### 4. Table: favorit (Bookmarks)
```sql
CREATE TABLE favorit (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    beasiswa_id INTEGER NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES akun(id),
    FOREIGN KEY (beasiswa_id) REFERENCES beasiswa(id),
    UNIQUE(user_id, beasiswa_id)
)
```

#### 5. Table: catatan (Notes)
```sql
CREATE TABLE catatan (
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
```

#### 6. Table: penyelenggara (Providers)
```sql
CREATE TABLE penyelenggara (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    nama TEXT NOT NULL,
    description TEXT,
    website TEXT,
    contact_email TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
)
```

---

## API Reference {#api}

### Authentication Functions

#### `register_user(username, email, password, nama_lengkap="", jenjang="")`

Register new user account.

**Parameters:**
- `username` (str): Unique username
- `email` (str): User email (must be valid)
- `password` (str): Min 6 chars, must include uppercase, number, special char
- `nama_lengkap` (str, optional): Full name
- `jenjang` (str, optional): D3/D4/S1/S2

**Returns:** `(bool, str)` - (success, message)

**Example:**
```python
from crud import register_user

success, msg = register_user(
    username="john_doe",
    email="john@example.com",
    password="SecurePass123!",
    nama_lengkap="John Doe",
    jenjang="S1"
)

if success:
    print("Registration successful!")
else:
    print(f"Error: {msg}")
```

#### `login_user(username, password)`

Login to existing account.

**Parameters:**
- `username` (str): Username
- `password` (str): Password

**Returns:** `(bool, str, Dict)` - (success, message, user_dict)

**User Dict Fields:**
- `id`: User ID
- `username`: Username
- `email`: Email
- `nama_lengkap`: Full name
- `jenjang`: Education level

---

### Beasiswa CRUD

#### `add_beasiswa(judul, jenjang, deadline, **kwargs)`

Add new scholarship.

**Required Parameters:**
- `judul` (str): Scholarship name
- `jenjang` (str): D3/D4/S1/S2
- `deadline` (str): YYYY-MM-DD format

**Optional Parameters:**
- `penyelenggara_id` (int): Provider ID
- `deskripsi` (str): Description
- `benefit` (str): Benefits
- `persyaratan` (str): Requirements
- `minimal_ipk` (float): Min GPA (0.0-4.0)
- `coverage` (str): Coverage type
- `status` (str): Buka/Segera Tutup/Tutup
- `link_aplikasi` (str): Application link

**Returns:** `(bool, str, Optional[int])` - (success, message, scholarship_id)

#### `get_beasiswa_list(filter_jenjang=None, filter_status=None, search_judul=None, sort_by='deadline', sort_order='ASC', start=0, limit=100)`

Get list of scholarships with filtering.

**Parameters:**
- `filter_jenjang` (str): Filter by education level
- `filter_status` (str): Filter by status
- `search_judul` (str): Search by name (case-insensitive)
- `sort_by` (str): Sort column (deadline/judul/created_at/status)
- `sort_order` (str): ASC or DESC
- `start` (int): Pagination offset
- `limit` (int): Max results

**Returns:** `(List[Dict], int)` - (scholarship_list, total_count)

#### `edit_beasiswa(beasiswa_id, **kwargs)`

Update scholarship.

**Parameters:**
- `beasiswa_id` (int): Scholarship ID
- Any fields to update as kwargs

**Returns:** `(bool, str)`

#### `delete_beasiswa(beasiswa_id)`

Delete scholarship.

**Parameters:**
- `beasiswa_id` (int): Scholarship ID

**Returns:** `(bool, str)`

---

### Favorit Management

#### `add_favorit(user_id, beasiswa_id)`

Add scholarship to favorites.

**Returns:** `(bool, str, Optional[int])` - (success, message, favorit_id)

#### `get_favorit_list(user_id, sort_by='created_at', sort_order='DESC')`

Get user's favorite scholarships.

**Returns:** `(List[Dict], int)` - (favorit_list, total_count)

#### `delete_favorit(user_id, beasiswa_id)`

Remove from favorites.

**Returns:** `(bool, str)`

---

### Catatan (Notes) Management

#### `add_catatan(user_id, beasiswa_id, content)`

Add note for scholarship.

**Parameters:**
- `user_id` (int): User ID
- `beasiswa_id` (int): Scholarship ID
- `content` (str): Note content (max 2000 chars)

**Returns:** `(bool, str, Optional[int])` - (success, message, note_id)

#### `get_catatan(user_id, beasiswa_id)`

Get note for specific scholarship.

**Returns:** `(Optional[Dict], str)` - (note_dict, message)

#### `edit_catatan(user_id, beasiswa_id, content)`

Update note.

**Returns:** `(bool, str)`

#### `delete_catatan(user_id, beasiswa_id)`

Delete note.

**Returns:** `(bool, str)`

#### `get_catatan_list(user_id, filter_jenjang=None, search_judul=None)`

Get user's all notes with filters.

**Returns:** `(List[Dict], int)` - (notes_list, total_count)

---

## Testing & QA {#testing}

### Test Coverage

| Test Suite | Coverage | Status |
|-----------|----------|--------|
| test_phase_1_1.py | Database Schema | ✅ PASSED |
| test_auth_demo.py | Authentication | ✅ PASSED |
| test_phase_2_2.py | Beasiswa CRUD | ✅ PASSED |
| test_phase_3_1.py | Lamaran CRUD | ✅ PASSED |
| test_phase_3_2.py | Favorit CRUD | ✅ PASSED |
| test_phase_4_1.py | Aggregations | ✅ PASSED |
| test_phase_1_3.py | GUI Framework | ✅ PASSED |
| test_phase_5_2.py | Sudah Daftar Logic | ✅ PASSED |
| test_phase_5_3.py | Favorit UI | ✅ PASSED |
| test_phase_5_4.py | Notes Features | ✅ PASSED |

**Total: 10/10 (100%) Test Suites Passing**

### Running Tests

```bash
# Run all tests
python3 test_phase_1_1.py
python3 test_auth_demo.py
python3 test_phase_2_2.py
python3 test_phase_3_1.py
python3 test_phase_3_2.py
python3 test_phase_4_1.py
python3 test_phase_1_3.py
python3 test_phase_5_2.py
python3 test_phase_5_3.py
python3 test_phase_5_4.py

# Run comprehensive analysis
python3 comprehensive_analysis.py
```

### Test Scenarios Covered

**Database & Schema:**
- ✅ All 6 tables created correctly
- ✅ All constraints enforced (UNIQUE, FK)
- ✅ Timestamp tracking working

**Authentication:**
- ✅ Registration with validation
- ✅ Password hashing with bcrypt
- ✅ Login verification
- ✅ Email format validation

**CRUD Operations:**
- ✅ Create with validation
- ✅ Read with filtering & sorting
- ✅ Update with timestamp tracking
- ✅ Delete with integrity checks

**Favorit System:**
- ✅ Add/remove favorit
- ✅ Check favorit status
- ✅ Multi-user independence
- ✅ Visual indicators

**Notes System:**
- ✅ Add/edit/delete notes
- ✅ 2000 character limit
- ✅ Duplicate prevention
- ✅ Filter & search

**Aggregations:**
- ✅ Count per jenjang
- ✅ Top providers
- ✅ Status distribution

---

## Troubleshooting

### Database Errors

**Q: "database is locked"**
- A: Close other instances of the application
- Delete `database/beasiswaku.db` and restart

**Q: "table already exists"**
- A: Database auto-initialization works correctly
- Safe to ignore if app starts properly

### GUI Issues

**Q: PyQt6 not found**
- A: Run `pip install PyQt6`

**Q: Window doesn't display**
- A: Check display settings, try running with:
  ```bash
  QT_QPA_PLATFORM=offscreen python3 main.py
  ```

---

## Support & Contact

For issues or questions:
- Check test files for examples
- Review comprehensive_analysis.py for system info
- Check logs in terminal output

---

**Status: Version 1.0 - Production Ready ✅**
**Last Updated: 2026-04-11**
