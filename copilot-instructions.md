---
name: beasiswaku-project-instructions
description: >-
  BeasiswaKu project-specific conventions. Use when: implementing features, modifying database schema, creating GUI components, writing scraper logic, generating visualizations, or changing project architecture. Enforces adherence to the project blueprint (blueprint_beasiswaku.md) as the source of truth. All improvisation or architectural changes require explicit user confirmation before implementation.
applyTo: >-
  **/*.py
---

# BeasiswaKu Development Instructions

This document defines project conventions, architectural constraints, and code standards for the BeasiswaKu scholarship manager application.

## 🎯 Core Principle

**The blueprint (`blueprint_beasiswaku.md`) is the source of truth.** Any suggested improvisation, architectural change, or feature deviation **requires explicit user confirmation** before implementation.

---

## 0. Tim, Pembagian Tugas & Dependencies

### ⚠️ Penting: Urutan Implementasi MVP

**Implementasi HARUS mengikuti urutan ini** agar tidak ada blocker:

```
FASE 1 — FOUNDATION (Prerequisite semua fitur lain)
├─ 1.1 Database Schema (Darva)
│   └─ Tabel: akun, beasiswa, penyelenggara, riwayat_lamaran
│
├─ 1.2 Authentication (Darva)
│   ├─ register_user(), login_user(), verify_password() di crud.py
│   └─ Login Screen di main.py
│
└─ 1.3 Main Window Layout (Kyla + Darva)
    └─ Header (nama app, username, logout), Tab bar (Beasiswa|Tracker|Statistik)

     ✅ BLOCKER: Fase 1 HARUS selesai sebelum fase 2-5

FASE 2 — TAB BEASISWA (Independent dari tracker)
├─ 2.1 Auto-Scraping (Kemal) [Start bisa parallel tapi dijalankan saat Fase 1 selesai]
│   ├─ scrape_beasiswa_data() di scraper.py
│   ├─ Simpan ke tabel beasiswa
│   └─ Backup to JSON
│
├─ 2.2 CRUD Beasiswa (Darva)
│   └─ add_beasiswa(), edit_beasiswa(), delete_beasiswa(), get_beasiswa_list() di crud.py
│
└─ 2.3 Tab Beasiswa UI (Kyla) [BLOCKED oleh 2.1 & 2.2]
    ├─ Tabel display
    ├─ Filter jenjang & status
    ├─ Search real-time
    ├─ CRUD panel (tambah, edit, hapus)
    ├─ Highlight deadline (merah/kuning)
    ├─ Export CSV
    └─ Detail popup (dobel klik)

FASE 3 — TAB TRACKER (Independent dari beasiswa tapi butuh data beasiswa)
├─ 3.1 CRUD Lamaran (Darva) [BLOCKED oleh Fase 1]
│   ├─ add_lamaran(), edit_lamaran(), delete_lamaran(), get_lamaran_list() di crud.py
│   └─ Validasi input
│
├─ 3.2 Tracker Tab UI (Kyla) [BLOCKED oleh 3.1 & Fase 1]
│   ├─ Tabel lamaran
│   ├─ Form tambah/edit/hapus
│   └─ Dialog konfirmasi
│
└─ 3.3 Charts Tracker (Aulia) [BLOCKED oleh 3.1]
    ├─ Pie chart status lamaran
    └─ Bar chart lamaran per bulan

FASE 4 — TAB STATISTIK (BLOCKED oleh Fase 2 & 3)
├─ 4.1 Data Aggregation Queries (Darva)
│   ├─ Query beasiswa per jenjang
│   ├─ Query top penyelenggara
│   └─ Query status availability
│
└─ 4.2 Statistik Charts (Aulia + Richard)
    ├─ Bar chart beasiswa per jenjang
    ├─ Bar chart top 5 penyelenggara
    └─ Pie chart status ketersediaan

FASE 5 — FITUR TAMBAHAN (BLOCKED oleh Fase 1-4)
├─ 5.1 Highlight deadline + warning popup (Kyla)
├─ 5.2 Kolom "Sudah Daftar?" (Kyla + Darva)
├─ 5.3 Fitur Favorit/Bookmark (Kyla + Darva)
├─ 5.4 Catatan pribadi per beasiswa (Darva + Kyla)
├─ 5.5 Halaman profil pengguna (Darva)
├─ 5.6 Dark/Light Mode (Aulia + Kyla)
└─ 5.7 Counter jumlah data di tab (Aulia)
```

### Checklist Prerequisite Sebelum Implement Fitur

**SEBELUM implement fitur Tab Beasiswa:**
- [ ] Database schema sudah buat (tabel `beasiswa`, `penyelenggara`)
- [ ] CRUD function sudah ada di crud.py
- [ ] Auto-scraper sudah siap (minimal test scrape 1 beasiswa)

**SEBELUM implement fitur Tab Tracker:**
- [ ] Tab Beasiswa SUDAH SELESAI atau minimal database sudah bisa query beasiswa
- [ ] CRUD lamaran sudah buat di crud.py
- [ ] Form validation function sudah ada

**SEBELUM implement fitur statistik:**
- [ ] Tab Beasiswa sudah buat & punya data
- [ ] Tab Tracker sudah buat & punya data function
- [ ] Matplotlib/Plotly sudah install

**SEBELUM implement fitur tambahan:**
- [ ] Semua 4 fitur utama (Auth, Beasiswa, Tracker, Statistik) SUDAH SELESAI dan TESTED
- [ ] Database stabil, CRUD functions tested
- [ ] UI layout stable, tidak ada major refactor pending

---

### Protokol: "Saya Mau Implement Fitur X, Apa Prerequisite?"

**Format:**
```
"Saya mau implementasikan [fitur]. Apa prerequisitenya? 
Sudah selesai atau belum?"
```

**Contoh:**
```
"Saya (Kyla) mau implementasikan Tab Beasiswa. 
Cek prerequisite mana yang sudah selesai:"
```

**Copilot akan respond:**
```
Checklist prerequisite Tab Beasiswa:
- [ ] Database schema tabel beasiswa
- [ ] get_beasiswa_list() CRUD
- [ ] add_beasiswa(), edit_beasiswa(), delete_beasiswa() CRUD
- [ ] scrape_beasiswa_data() simpan ke database
- [ ] Main window layout sudah buat (header + tab bar)

Status: 
  ✅ Database schema — sudah
  ❌ CRUD function — belum (Darva masih implement)
  ⏳ Scraper — in-progress (Kemal)
  ✅ Main window — sudah

Action: TUNGGU Darva selesai CRUD, baru Kyla mulai implement UI
```

---

### Struktur Tim

| Nama | Peran Utama | Modul | 
|------|---|---|
| **Darva** | Database & Auth Specialist | `crud.py`, `main.py` (session) |
| **Kyla** | UI/UX Specialist (Beasiswa Tab) | `gui_beasiswa.py`, `main.py` (layout) |
| **Aulia** | Analytics & Visualization Specialist | `visualisasi.py`, UI themes |
| **Kemal** | Data & Search Specialist | `scraper.py`, search features |
| **Richard** | Advanced Analytics | `visualisasi.py` (tren charts) |

### Pembagian Fitur MVP (Target UTS)

#### 🔐 Autentikasi (Darva)
- Register form → `main.py` (UI bersama Kyla)
- Login screen → `main.py` (UI bersama Kyla)
- Password bcrypt hashing → `crud.py` (Darva)
- Session management → `main.py` (Darva)

#### 📋 Tab Beasiswa (Kyla + supporting)
- **Kyla (PIC):** Tabel, filter, search, sort, highlight deadline, detail popup, favorit
- **Darva:** Database schema + CRUD operations
- **Kemal:** Refresh scraper trigger

#### 📝 Tab Tracker Lamaran (Darva + Kyla)
- **Darva (PIC):** Database schema, CRUD operations, form logic
- **Kyla (supporting):** Form UI & table display
- **Aulia:** Pie chart & bar chart

#### 📊 Tab Statistik (Aulia + Richard)
- **Aulia (PIC):** Bar chart (jenjang), pie chart (status), styling
- **Richard (supporting):** Advanced tren charts (jika diperlukan)
- **Darva:** Data aggregation queries

#### 🔄 Web Scraping (Kemal)
- **Kemal (PIC):** Scraper logic, auto-scrape on startup, data validation
- **Darva:** Backup to JSON, database integration
- **Kyla:** UI untuk trigger refresh manual

#### 🎨 UI & Styling (Kyla + Aulia)
- **Kyla (PIC):** Tab Beasiswa layout, form design, table styling
- **Aulia (PIC):** Dark/Light mode, theme consistency, counter badges

### Protokol Komunikasi Antar Tim

**Jika mengerjakan fitur yang melibatkan modul orang lain:**

| Situasi | Action | Contoh |
|---------|--------|--------|
| Perlu database schema baru | **Ping Darva dulu** | Kyla mau tambah kolom "sudah_daftar" |
| Perlu CRUD function baru | **Ping Darva dulu** | Kemal perlu query favorit beasiswa |
| Perlu chart/visualisasi | **Ping Aulia/Richard** | Darva perlu pie chart status |
| Perlu scraper update | **Ping Kemal dulu** | Aulia perlu field baru dari scraper |
| Perlu UI integration | **Ping Kyla dulu** | Darva perlu form Tambah Lamaran di Tracker |

### Request Format untuk Copilot

**Jika Anda ingin Copilot fokus ke PIC tertentu:**

```
"Darva: Buatkan CRUD function untuk tambah beasiswa baru di crud.py"
```

**Atau jika instruksi harus involve multiple orang:**

```
"Koordinasi Kyla + Aulia: 
- Kyla: UI untuk dark/light mode toggle di header
- Aulia: CSS/styling logic di main.py"
```

---

## 1. Project Architecture & File Organization

### Mandatory Structure
Maintain this folder structure exactly as defined in the blueprint:

```
beasiswaku/
├── main.py                    # Entry point, main window, login screen, notifications
├── scraper.py                 # Web scraping + auto-scraping + JSON backup
├── crud.py                    # CRUD operations, authentication, Tracker UI
├── gui_beasiswa.py            # Beasiswa Tab UI
├── visualisasi.py             # All graphs (Tracker & Statistics tabs)
├── database/
│   └── beasiswaku.db          # SQLite database (auto-created on first run)
├── backup/
│   ├── beasiswa.json
│   ├── penyelenggara.json
│   └── riwayat_lamaran.json
├── assets/
│   └── icon.png
├── requirements.txt
├── blueprint_beasiswaku.md
└── README.md
```

### Module Responsibilities (Do NOT Mix)

| Module | Owner | Responsibility |
|--------|-------|---|
| `main.py` | Darva + Kyla | Application entry point, main window layout, login screen, session management |
| `crud.py` | **Darva (PIC)** | All database CRUD operations, user authentication (bcrypt), Tracker tab logic |
| `gui_beasiswa.py` | **Kyla (PIC)** | Beasiswa table display, filtering, sorting, search, CRUD panel, export CSV, detail popup |
| `scraper.py` | **Kemal (PIC)** | Web scraping logic, auto-scraping thread, data validation, JSON backups |
| `visualisasi.py` | **Aulia (PIC)** + Richard | All chart generation (Matplotlib/Plotly), Tracker tab graphs & Statistics tab |

**Catatan:** Jika ada fitur yang memerlukan kolaborasi, ikuti "Protokol Komunikasi Antar Tim" di atas.

---

## 2. Database Schema Implementation

### Mandatory Constraints

1. **Database must match schema in blueprint exactly** — Section 6.2
2. Use **SQLite only**; file must be `database/beasiswaku.db`
3. Schema setup must be in `crud.py` within table creation functions
4. **Password hashing MUST use `bcrypt`** — never plaintext
5. All datetime values use SQLite's `CURRENT_TIMESTAMP` with `'localtime'` timezone
6. Foreign keys are not mandatory for MVP but recommended for data integrity

### Table Creation Pattern

```python
# In crud.py - init_db() function
def init_db():
    """Initialize database with all required tables."""
    conn = sqlite3.connect(DATABASE_PATH)
    cursor = conn.cursor()
    
    # Table creation with proper types and constraints
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS akun (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nama_lengkap TEXT NOT NULL,
            username TEXT NOT NULL UNIQUE,
            email TEXT NOT NULL UNIQUE,
            password_hash TEXT NOT NULL,
            created_at TEXT DEFAULT (datetime('now', 'localtime'))
        )
    ''')
    # ... other tables ...
    
    conn.commit()
    conn.close()
```

### Adding New Tables

**Before adding any new table:**
1. Confirm with user that it aligns with blueprint features
2. Document the exact schema with data types, constraints, and purpose
3. Add table creation to `init_db()`
4. Add corresponding CRUD functions to `crud.py`

---

## 3. Python Code Style & Standards

### Language & Environment
- **Python version:** 3.8+ (check with user if unclear)
- **Text encoding:** Always UTF-8 (especially for Indonesian strings)
- **Imports:** Standard library → Third-party → Local modules (organized alphabetically within groups)

### Naming Conventions

| Element | Style | Example |
|---------|-------|---------|
| Functions | `snake_case` | `get_beasiswa_aktif()`, `validate_email()` |
| Classes | `PascalCase` | `LoginWindow`, `BeasiswaTracker` |
| Constants | `UPPER_SNAKE_CASE` | `DATABASE_PATH`, `SCRAPE_TIMEOUT` |
| Variables | `snake_case` | `user_id`, `deadline_list` |
| Private methods | `_leading_underscore` | `_load_config()` |
| Boolean flags | `is_`, `has_`, `should_` prefix | `is_logged_in`, `has_error` |

### Code Organization

```python
# Header comments
"""
Module: gui_beasiswa.py
Purpose: Beasiswa tab UI and data display logic
Author: [Name]
Last updated: [Date]
"""

# Imports (organized)
import sqlite3
from datetime import datetime
from typing import List, Dict, Optional

import tkinter as tk
from tkinter import ttk, messagebox

from crud import get_beasiswa_list
from utils import validate_date

# Constants
COLUMN_WIDTHS = {'nama': 250, 'deadline': 100}
HIGHLIGHT_COLOR_URGENT = '#FFE6E6'  # Red tint for ≤3 days
HIGHLIGHT_COLOR_WARNING = '#FFFACD'  # Yellow for ≤7 days

# Classes
class BeasiswaTab:
    """UI tab for displaying and managing scholarship data."""
    
    def __init__(self, parent):
        self.parent = parent
        # ... initialization ...
    
    def refresh_table(self):
        """Reload table data from database."""
        pass

# Execution guard
if __name__ == '__main__':
    pass
```

### Docstrings & Comments

- **Module level:** Docstring at top with purpose and key functions
- **Functions:** Docstring with brief description, args, return type, and exceptions
- **Complex logic:** Inline comments explaining "why", not "what"
- **Inline comments:** Only for non-obvious logic; remove self-explanatory comments

```python
def check_deadline_urgency(deadline_str: str) -> str:
    """
    Determine deadline urgency level for UI highlighting.
    
    Args:
        deadline_str: ISO format date string (YYYY-MM-DD)
    
    Returns:
        'urgent' (≤3 days), 'warning' (≤7 days), or 'normal' (>7 days)
    
    Raises:
        ValueError: If deadline_str is not valid ISO format
    """
    from datetime import datetime, timedelta
    deadline = datetime.fromisoformat(deadline_str).date()
    days_left = (deadline - datetime.now().date()).days
    
    # Edge case: handle past deadlines
    if days_left < 0:
        return 'expired'
    
    return 'urgent' if days_left <= 3 else ('warning' if days_left <= 7 else 'normal')
```

---

## 4. Tkinter GUI Standards

### Window & Layout Conventions

```python
# Use grid layout for consistency
self.frame = tk.Frame(parent, bg='#f0f0f0')
self.frame.grid(row=0, column=0, sticky='nsew', padx=10, pady=10)

# Consistent padding
PAD_OUTER = {'padx': 10, 'pady': 10}
PAD_INNER = {'padx': 5, 'pady': 5}

# Frame organization: header → controls → data → footer
self.header_frame = tk.Frame(self.frame, bg='#ffffff')
self.control_frame = tk.Frame(self.frame, bg='#f0f0f0')
self.data_frame = tk.Frame(self.frame, bg='#ffffff')
self.footer_frame = tk.Frame(self.frame, bg='#f0f0f0')
```

### Widget Naming Pattern

```python
# Prefix indicates widget type
self.btn_refresh = tk.Button(...)           # Button
self.lbl_status = tk.Label(...)             # Label
self.entry_search = tk.Entry(...)           # Entry
self.combo_filter = ttk.Combobox(...)       # Combobox
self.tbl_beasiswa = ttk.Treeview(...)       # Table/Treeview
self.chart_frame = tk.Frame(...)            # Chart container (matplotlib)
```

### Common UI Pattern: Search & Filter

```python
# Control frame with search + filter dropdowns
search_var = tk.StringVar()
search_entry = tk.Entry(control_frame, textvariable=search_var, width=30)
search_entry.grid(row=0, column=0, padx=5)

jenjang_var = tk.StringVar(value='Semua')
jenjang_combo = ttk.Combobox(control_frame, textvariable=jenjang_var, 
                              values=['Semua', 'D3', 'D4', 'S1', 'S2'], state='readonly')
jenjang_combo.grid(row=0, column=1, padx=5)

# Bind to refresh table
search_entry.bind('<KeyRelease>', lambda e: refresh_table_with_filters())
jenjang_combo.bind('<<ComboboxSelected>>', lambda e: refresh_table_with_filters())
```

### Dialog & Message Boxes

```python
# Error dialog
messagebox.showerror("Error", "Invalid date format. Please use YYYY-MM-DD")

# Confirmation dialog
if messagebox.askyesno("Confirm", "Delete this scholarship record?"):
    # Perform deletion
    pass

# Info dialog
messagebox.showinfo("Success", "Data saved successfully!")
```

---

## 5. Database Operation Patterns (CRUD)

### Connection Management

```python
def get_db_connection():
    """Open database connection with error handling."""
    try:
        conn = sqlite3.connect(DATABASE_PATH)
        conn.row_factory = sqlite3.Row  # Return rows as dict-like objects
        return conn
    except sqlite3.OperationalError as e:
        print(f"Database connection error: {e}")
        return None

def execute_query(query: str, params: tuple = ()) -> bool:
    """Execute INSERT/UPDATE/DELETE with error handling."""
    conn = get_db_connection()
    if not conn:
        return False
    
    try:
        cursor = conn.cursor()
        cursor.execute(query, params)
        conn.commit()
        return True
    except sqlite3.IntegrityError as e:
        print(f"Data integrity error: {e}")
        messagebox.showerror("Error", "Data conflict. Please check your input.")
        return False
    finally:
        conn.close()

def fetch_query(query: str, params: tuple = ()) -> List[sqlite3.Row]:
    """Execute SELECT and return results."""
    conn = get_db_connection()
    if not conn:
        return []
    
    try:
        cursor = conn.cursor()
        cursor.execute(query, params)
        return cursor.fetchall()
    finally:
        conn.close()
```

### CRUD Function Template

```python
def add_lamaran(user_id: int, nama_beasiswa: str, tanggal_daftar: str, 
                status: str, catatan: str = "") -> bool:
    """
    Add new scholarship application record.
    
    Args:
        user_id: Foreign key to akun table
        nama_beasiswa: Name of scholarship
        tanggal_daftar: Application date (YYYY-MM-DD)
        status: 'Pending', 'Diterima', or 'Ditolak'
        catatan: Optional notes
    
    Returns:
        True if successful, False otherwise
    """
    if not validate_date(tanggal_daftar):
        messagebox.showerror("Error", "Invalid date format")
        return False
    
    query = """
        INSERT INTO riwayat_lamaran 
        (user_id, nama_beasiswa, tanggal_daftar, status, catatan, created_at)
        VALUES (?, ?, ?, ?, ?, datetime('now', 'localtime'))
    """
    
    return execute_query(query, (user_id, nama_beasiswa, tanggal_daftar, status, catatan))
```

---

## 6. Authentication & Security

### Password Hashing (MANDATORY)

```python
import bcrypt

def hash_password(password: str) -> str:
    """Hash password using bcrypt."""
    salt = bcrypt.gensalt(rounds=12)
    return bcrypt.hashpw(password.encode('utf-8'), salt).decode('utf-8')

def verify_password(password: str, password_hash: str) -> bool:
    """Verify plain password against bcrypt hash."""
    return bcrypt.checkpw(password.encode('utf-8'), password_hash.encode('utf-8'))

# Registration
def register_user(nama_lengkap: str, username: str, email: str, password: str) -> bool:
    """Register new user with hashed password."""
    password_hash = hash_password(password)
    
    query = """
        INSERT INTO akun (nama_lengkap, username, email, password_hash)
        VALUES (?, ?, ?, ?)
    """
    return execute_query(query, (nama_lengkap, username, email, password_hash))

# Login
def login_user(username: str, password: str) -> Optional[int]:
    """
    Authenticate user and return user_id if successful.
    
    Returns:
        user_id (int) if login successful, None otherwise
    """
    result = fetch_query("SELECT id, password_hash FROM akun WHERE username = ?", (username,))
    
    if result and verify_password(password, result[0]['password_hash']):
        return result[0]['id']
    return None
```

### Session Management

```python
# In main.py after successful login
self.current_user_id = login_user(username, password)
self.current_username = username  # Store for UI display

# On logout
self.current_user_id = None
self.current_username = None
# Return to login screen
```

---

## 7. Data Validation Standards

### Input Validation Pattern

```python
def validate_scholarship_form(nama: str, penyelenggara: str, jenjang: str, 
                             deadline: str) -> tuple[bool, str]:
    """
    Validate scholarship form input.
    
    Returns:
        (is_valid: bool, error_message: str)
    """
    if not nama or len(nama) < 3:
        return False, "Scholarship name must be at least 3 characters"
    
    if not penyelenggara or len(penyelenggara) < 2:
        return False, "Provider name is required"
    
    if jenjang not in ['D3', 'D4', 'S1', 'S2']:
        return False, "Invalid education level"
    
    if not validate_date(deadline):
        return False, "Invalid date format (use YYYY-MM-DD)"
    
    return True, ""

# Usage in form submission
is_valid, error_msg = validate_scholarship_form(nama, penyelenggara, jenjang, deadline)
if not is_valid:
    messagebox.showerror("Validation Error", error_msg)
    return
# Proceed with database insert
```

### Email Validation

```python
import re

def validate_email(email: str) -> bool:
    """Validate email format."""
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return re.match(pattern, email) is not None
```

---

## 8. Visualization Standards (Matplotlib/Plotly)

### Chart Integration Pattern

```python
# In visualisasi.py
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

def create_pie_chart_lamaran(user_id: int, parent_frame: tk.Frame) -> None:
    """
    Create pie chart showing application status distribution.
    
    Args:
        user_id: User ID to filter data
        parent_frame: Tkinter frame to embed chart
    """
    # Query data
    data = fetch_lamaran_status_summary(user_id)
    
    # Create figure
    fig, ax = plt.subplots(figsize=(6, 5), dpi=100)
    
    # Plot with Indonesian labels
    labels = ['Pending', 'Diterima', 'Ditolak']
    sizes = [data['pending'], data['accepted'], data['rejected']]
    colors = ['#FFC107', '#4CAF50', '#F44336']
    
    ax.pie(sizes, labels=labels, colors=colors, autopct='%1.1f%%', startangle=90)
    ax.set_title('Status Lamaran Beasiswa', fontsize=14, fontweight='bold')
    
    # Embed in Tkinter
    canvas = FigureCanvasTkAgg(fig, master=parent_frame)
    canvas.draw()
    canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)
```

### Color Standards

```python
# Use consistent color palette
COLOR_PALETTE = {
    'pending': '#FFC107',      # Amber/Yellow
    'accepted': '#4CAF50',     # Green
    'rejected': '#F44336',     # Red
    'urgent': '#FFE6E6',       # Light red (≤3 days)
    'warning': '#FFFACD',      # Light yellow (≤7 days)
    'normal': '#FFFFFF',       # White
}
```

---

## 9. Web Scraping Standards (scraper.py)

### Scraping Function Pattern

```python
import requests
from bs4 import BeautifulSoup

def scrape_beasiswa_data() -> List[Dict]:
    """
    Scrape scholarship data from target websites.
    
    Returns:
        List of scholarship dictionaries with keys:
        ['nama', 'penyelenggara', 'jenjang', 'deadline', 'deskripsi', 'link']
    """
    beasiswa_list = []
    
    try:
        # Set User-Agent to avoid blocking
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
        
        response = requests.get('https://example.com/beasiswa', headers=headers, timeout=10)
        response.raise_for_status()
        
        soup = BeautifulSoup(response.content, 'html.parser')
        
        # Parse and validate data
        for item in soup.select('div.scholarship-item'):
            beasiswa = {
                'nama': item.select_one('.title')?.get_text(strip=True),
                'penyelenggara': item.select_one('.provider')?.get_text(strip=True),
                'jenjang': item.select_one('.level')?.get_text(strip=True),
                'deadline': item.select_one('.deadline')?.get_text(strip=True),
                'deskripsi': item.select_one('.description')?.get_text(strip=True),
                'link': item.select_one('a')?.get('href'),
            }
            
            # Validate before adding
            if validate_beasiswa_data(beasiswa):
                beasiswa_list.append(beasiswa)
        
        # Create JSON backup
        backup_to_json(beasiswa_list, 'backup/beasiswa.json')
        
        return beasiswa_list
    
    except requests.exceptions.RequestException as e:
        print(f"Scraping error: {e}")
        return []
```

### Auto-Scraping Thread

```python
import threading
import time

def auto_scrape_background():
    """Run scraping in background thread on app startup if database is empty."""
    def scrape_task():
        print("Starting auto-scrape...")
        beasiswa_data = scrape_beasiswa_data()
        
        # Insert into database
        for beasiswa in beasiswa_data:
            execute_query(
                """INSERT INTO beasiswa 
                (nama, penyelenggara, jenjang, deadline, deskripsi, status, link)
                VALUES (?, ?, ?, ?, ?, 'Buka', ?)""",
                (beasiswa['nama'], beasiswa['penyelenggara'], beasiswa['jenjang'],
                 beasiswa['deadline'], beasiswa['deskripsi'], beasiswa['link'])
            )
        print(f"Auto-scrape completed: {len(beasiswa_data)} scholarships loaded")
    
    # Run in background
    thread = threading.Thread(target=scrape_task, daemon=True)
    thread.start()

# In main.py on startup
if is_database_empty():
    auto_scrape_background()
```

---

## 10. Backup & Data Export

### JSON Backup Format

```python
import json
from datetime import datetime

def backup_to_json(data: List[Dict], filepath: str) -> bool:
    """Backup data to JSON file with metadata."""
    try:
        backup_data = {
            'timestamp': datetime.now().isoformat(),
            'data': data
        }
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(backup_data, f, indent=2, ensure_ascii=False)
        return True
    except IOError as e:
        print(f"Backup error: {e}")
        return False
```

### CSV Export Pattern

```python
import csv

def export_to_csv(data: List[Dict], filename: str) -> bool:
    """Export data to CSV file."""
    if not data:
        messagebox.showwarning("Export", "No data to export")
        return False
    
    try:
        with open(filename, 'w', newline='', encoding='utf-8') as csvfile:
            fieldnames = list(data[0].keys())
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            
            writer.writeheader()
            writer.writerows(data)
        
        messagebox.showinfo("Success", f"Data exported to {filename}")
        return True
    except IOError as e:
        messagebox.showerror("Error", f"Export failed: {e}")
        return False
```

---

## 11. Error Handling & Logging

### Error Handling Pattern

```python
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('app.log'),
        logging.StreamHandler()
    ]
)

def safe_operation(operation_name: str, operation_func, *args):
    """
    Execute operation with error handling and logging.
    
    Args:
        operation_name: Description of operation for logging
        operation_func: Function to execute
        *args: Arguments to pass to function
    """
    try:
        result = operation_func(*args)
        logging.info(f"{operation_name} completed successfully")
        return result
    except Exception as e:
        logging.error(f"{operation_name} failed: {e}")
        messagebox.showerror("Error", f"Operation failed: {str(e)}")
        return None
```

### Common Exception Types

```python
# Database errors
except sqlite3.IntegrityError:
    # Duplicate key, foreign key, or unique constraint violation
    messagebox.showerror("Error", "Data conflict. Please check your input.")

except sqlite3.OperationalError:
    # Database locked or syntax error
    messagebox.showerror("Error", "Database error. Please try again later.")

# Network errors (scraping)
except requests.exceptions.Timeout:
    messagebox.showwarning("Warning", "Request timed out. Check your internet connection.")

except requests.exceptions.ConnectionError:
    messagebox.showwarning("Warning", "Connection failed. Check your internet connection.")
```

---

## 12. Development Workflow & Checkpoints

### Before Implementing a Feature

1. **Check blueprint** — Section 3 (Feature List) and 4 (User Flow)
2. **Confirm UI layout** — Section 5 (Screen Requirements)
3. **Verify database schema** — Section 6.2
4. **Identify PIC (Person In Charge)** — Lihat Section 0 "Pembagian Tugas"
5. **Check prerequisites & dependencies** — Lihat Section 0 "Urutan Implementasi MVP" & "Checklist Prerequisite"
6. **Ask for approval** if changes deviate from blueprint
7. **Notify PIC** jika feature melibatkan modul orang lain (ikuti protokol komunikasi)

### Example Workflow

**Skenario 1:** Kyla mau implementasikan Tab Beasiswa

```
1. Kyla check Section 0 "Urutan Implementasi MVP" → Tab Beasiswa di FASE 2
2. Kyla lihat prerequisite:
   ✅ Database schema tabel beasiswa — sudah (Darva)
   ✅ get_beasiswa_list() CRUD — sudah
   ⏳ add/edit/delete CRUD — in-progress (Darva)
   ✅ scraper.py dengan database save — sudah
   ✅ Main window layout — sudah
3. Kyla lihat blocker: "Tunggu add/edit/delete CRUD selesai dulu"
4. Kyla ping Darva: "Kapan CRUD function selesai? Saya ready mulai UI"
5. Setelah Darva OK, Kyla mulai Tab Beasiswa di gui_beasiswa.py
6. Keduanya sync test, discussion UI-database sync
```

**Skenario 2:** Aulia mau implementasikan Tab Statistik

```
1. Aulia check Section 0 "Urutan Implementasi MVP" → Tab Statistik di FASE 4
2. FASE 4 = BLOCKED oleh FASE 2 & 3
3. Aulia lihat status:
   ⏳ FASE 2 (Tab Beasiswa) — in-progress (Kyla)
   ⏳ FASE 3 (Tab Tracker) — in-progress (Darva)
4. Aulia tidak bisa start Tab Statistik sampai keduanya selesai
   ALTERNATIF: Aulia bisa prepare file visualisasi.py + data aggregation queries dulu
5. Setelah FASE 2 & 3 OK, Aulia implement chartnya
```

**Skenario 3:** Kyla ingin tambahkan kolom "Sudah Daftar?" (FASE 5)

```
1. Kyla check Section 0 → "Kolom Sudah Daftar?" di FASE 5
2. FASE 5 = BLOCKED oleh FASE 1-4 selesai
3. Kyla cek: semua 4 fase sudah OK? Jika ya, baru bisa mulai
4. Kyla lihat prerequisite untuk fitur ini:
   - Darva: Tambah kolom 'sudah_daftar' ke tabel beasiswa
   - Kyla: UI checkbox di Tab Beasiswa
5. Kyla & Darva koordinasi implementasi
```

### During Implementation

- Follow the module responsibility table (Section 1)
- Use code templates provided in this document
- Write docstrings before implementation
- Test CRUD operations with sample data
- Add debug logging for development
- **Communicate** dengan PIC modul lain jika perlu sharing data/function
- **Check blocking tasks** — jika stuck, cek apakah dependencynya sudah selesai

### Before Committing

- Verify all database queries use parameterized statements (prevent SQL injection)
- Confirm bcrypt is used for all passwords
- Test form validation with edge cases (empty, special chars, long strings)
- Ensure error messages are user-friendly (in Indonesian where appropriate)
- Check that all UI labels match the blueprint naming

### Handling Blocking & Dependencies

**Jika Anda stuck karena blocking task:**

Format ke Copilot:
```
"Saya (Kyla) mau implementasikan [fitur]. 
Ada blocking task dari [siapa]? 
Cek status prerequisitenya dan beri tahu action apa yang harus saya lakukan."
```

Contoh:
```
"Saya (Aulia) mau implementasikan Tab Statistik.
Cek Section 0 — dependency apa yang masih pending?
Apa saya bisa mulai prep file visualisasi.py sambil tunggu?"
```

**Copilot akan respond dengan:**

✅ **Checklist Status:**
```
Prerequisite Tab Statistik (FASE 4):
- [ ] FASE 1 Foundation — ✅ DONE
- [ ] FASE 2 Tab Beasiswa — ⏳ in-progress (Kyla, ETA: X waktu)
- [ ] FASE 3 Tab Tracker — ⏳ in-progress (Darva, ETA: X waktu)

Status: BLOCKING — tidak bisa mulai sampai FASE 2 & 3 selesai

Alternatif: 
  - Prep file visualisasi.py structure
  - Setup matplotlib/plotly
  - Buat dummy data untuk test chart
  - Cek palette warna & styling
```

⚠️ **Alert jika ada blocking:**
```
"Tidak bisa implement [fitur] karena butuh [dependency].
Status [dependency]: [blockingStatus]
Hubungi [PIC] untuk tanya kapan selesai.
Sementara itu, Anda bisa [alternative tasks]."
```

---

## 13. Communication Pattern: Deviations & Improvements

### When Proposing Changes

**Always follow this format:**

1. **State the current blueprint requirement**  
   *"Blueprint Section X.X specifies that [feature description]"*

2. **Explain the proposed change**  
   *"I suggest we [change/add/modify] because [reasoning]"*

3. **Wait for confirmation**  
   *"Proceed? (yes/no)"*

### Example

> **Current:** Blueprint Section 3.1 specifies a simple text input for scholarship notes.
>
> **Proposal:** Add a rich text editor (support bold, italic, links) to allow better formatting of notes.
>
> **Reasoning:** Users often want to save formatted notes with emphasis on important deadlines or requirements.
>
> **Impact:** Requires switching from `tk.Text` to `tk.Text` with styling support or a Tkinter text editor library.
>
> **Proceed with implementation?**

---

## 14. Cara Meminta Bantuan Copilot Berdasarkan Role

### Prompt Format Umum

**Untuk implementasi fitur:**
```
"[Nama Anda]: Implementasikan [fitur] di [modul] sesuai blueprint Section X"
```

**Untuk cek prerequisite sebelum mulai:**
```
"Saya (Nama) mau mulai [fitur]. 
Cek Section 0 — apa prerequisitenya? Sudah selesai atau blocker?"
```

**Untuk koordinasi multi-orang:**
```
"Koordinasi:
- [Nama1]: [Task]
- [Nama2]: [Task]
- [NamaX]: [Task]

Sync point: [kapan merge/test bersama]"
```

---

### Jika Anda adalah **Darva** (CRUD & Database)

```
"Darva: Buatkan CRUD function untuk tambah/edit/hapus lamaran di crud.py
dengan validasi input dan error handling sesuai instructions Section 5"
```

```
"Darva: Buat authentication function login_user() dengan bcrypt verification
dan session management di main.py"
```

### Jika Anda adalah **Kyla** (Beasiswa Tab UI)

```
"Kyla: Buatkan tabel Beasiswa di gui_beasiswa.py dengan:
- Filter jenjang & status
- Search real-time
- Highlight baris deadline (merah ≤3, kuning ≤7)
Sesuai blueprint Section 5 Layar 3"
```

```
"Kyla: Implementasikan detail popup beasiswa (dobel klik baris)
dengan button favorit dan tombol tambah ke tracker"
```

### Jika Anda adalah **Aulia** (Analytics & Visualization)

```
"Aulia: Buatkan pie chart status lamaran (Pending/Diterima/Ditolak)
untuk Tab Tracker Lamaran menggunakan matplotlib"
```

```
"Aulia: Implementasikan dark mode & light mode toggle di main.py header
dengan CSS/styling yang konsisten di semua tab"
```

### Jika Anda adalah **Kemal** (Scraping & Search)

```
"Kemal: Update scraper.py untuk scrape beasiswa terbaru dengan
validasi data dan backup JSON ke backup/beasiswa.json"
```

```
"Kemal: Implementasikan full-text search untuk deskripsi beasiswa
di Tab Beasiswa (kolaborasi dengan Kyla untuk UI)"
```

### Jika Anda adalah **Richard** (Advanced Charts)

```
"Richard: Buatkan grafik tren lamaran per bulan di Tab Statistik
dengan bar chart menunjukkan tren keberhasilan"
```

### Jika Butuh Kolaborasi Multi-Orang

```
"Koordinasi:
- Darva: Tambahkan kolom 'sudah_daftar' ke tabel beasiswa di crud.py
- Kyla: Tambahkan checkbox column di Tab Beasiswa untuk 'sudah_daftar'
- Keduanya: Sync antara database dan UI

Sesuai blueprint Section 3.3 'Kolom Sudah Daftar?'"
```

---

### Jika Ada Blocking Task

**Prompt Contoh 1: Cek Prerequisite Sebelum Mulai**
```
"Saya (Kyla) ingin implementasikan Tab Beasiswa.
Cek prerequisite di Section 0 — apa yang sudah done, apa yang masih pending?"
```

**Response yang diharapkan:**
```
✅ Tab Beasiswa Prerequisites:
  ✅ FASE 1 Foundation (database, auth, main layout) — DONE
  ✅ Database schema beasiswa + penyelenggara — DONE
  ✅ get_beasiswa_list() CRUD — DONE
  ⏳ add_beasiswa(), edit_beasiswa(), delete_beasiswa() — in-progress (Darva, ETA 1 hari)
  ✅ scrape_beasiswa_data() → database — DONE
  ✅ Main window layout — DONE

Status: PARTIAL BLOCKING — Tunggu add/edit/delete CRUD Darva selesai
Action: KYLA BISA MULAI siapkan:
  - gui_beasiswa.py file structure
  - Treeview widget setup (display, filtering, sorting)
Setelah Darva OK, Kyla integrate CRUD operations.

Timing: Darva ETA 1 hari, jadi Kyla bisa mulai prep sekarang.
```

**Prompt Contoh 2: Blocker — Tidak Bisa Mulai**
```
"Saya (Aulia) mau implementasikan Tab Statistik. Apa blockernya?"
```

**Response yang diharapkan:**
```
❌ Tab Statistik BLOCKED!

Prerequisite di Section 0:
  ✅ FASE 1 Foundation — DONE
  ⏳ FASE 2 Tab Beasiswa — in-progress (Kyla, ETA 3 hari)
  ⏳ FASE 3 Tab Tracker — in-progress (Darva, ETA 2 hari)

Status: BLOCKER — Tab Statistik butuh data dari Tab Beasiswa & Tracker
Action: TIDAK BISA MULAI sampai keduanya selesai

Alternatif sementara (sambil tunggu):
  1. Siapkan file visualisasi.py dengan import semua library
  2. Buat data aggregation queries di crud.py (Darva) untuk statistik
  3. Buat dummy data untuk test chart structure
  4. Desain warna palette & styling untuk charts
  5. Test matplotlib setup

ETA keduanya: 3 hari. Jadi Aulia bisa start prep sekarang, 
  implementasi charts mulai 3 hari.
```

**Prompt Contoh 3: Koordinasi Unblock**
```
"Tim status update:
- Darva: Selesai CRUD beasiswa dan lamaran
- Kyla: Ready 80% Tab Beasiswa, tinggal tunggu CRUD final test
- Kemal: Scraper stable
- Aulia: Ready prep Statistik

Kapan bisa sync testing bersama? Siapa yang harus selesai dulu?"
```

---

---

## 15. Progress Tracking & Team Sync

### Real-Time Progress Template

**Setiap hari atau sebelum standup, update status:**

```markdown
## BeasiswaKu Development Progress — [Tanggal]

### FASE 1 — Foundation
- [x] Database schema (Darva) ✅ DONE
- [x] Authentication (Darva) ✅ DONE
- [x] Main window layout (Kyla) ✅ DONE

### FASE 2 — Tab Beasiswa
- [x] Auto-scraping (Kemal) ✅ DONE
- [x] CRUD beasiswa (Darva) ✅ DONE — 2 hari lalu
- [ ] Tab Beasiswa UI (Kyla) 🟡 in-progress (60%) — Siap diintegrasikan besok

### FASE 3 — Tab Tracker
- [ ] CRUD lamaran (Darva) 🟡 in-progress (80%) — Selesai dalam [X] hari
- [ ] Tracker Tab UI (Kyla) ⏳ blocked (waiting Darva CRUD) — Start [tanggal]
- [ ] Charts Tracker (Aulia) ⏳ blocked (waiting CRUD) — Start [tanggal]

### FASE 4 — Tab Statistik
- [ ] Data Aggregation (Darva) ⏳ blocked
- [ ] Statistik Charts (Aulia + Richard) ⏳ blocked

### FASE 5 — Features Tambahan
- [ ] Fitur X (PIC) ⏳ blocked

### Blocker & Risk
- ⚠️ Kyla stuck di Tab Beasiswa detail popup (detail: [masalah]) → Ping Darva [tanggal]
- ⚠️ Aulia siap mulai, tapi perlu final database schema — Darva [kapan confirm?]

### Next 24 Hours
- [ ] Darva: Finalize CRUD lamaran (Kyla will verify)
- [ ] Kyla: Integrate CRUD dengan Tab Beasiswa UI (test dengan Darva)
- [ ] Aulia: Prep visualisasi.py + dummy data
```

### Command untuk Copilot: "Trackan Progress Ini"

```
"Trackan progress ini di Section 0:
- Darva: CRUD beasiswa ✅ DONE 2 hari lalu
- Darva: CRUD lamaran 🟡 80% in-progress
- Kyla: Tab Beasiswa UI 🟡 60% in-progress
- Kyla: Tab Tracker ⏳ blocked (Darva)

Apa next action yang harus dilakukan untuk unblock team?"
```

**Copilot akan respond:**
```
Status Analysis FASE 2 & 3:

UNBLOCK Kyla (Tab Beasiswa):
  - Darva CRUD beasiswa sudah ✅ 
  - Kyla bisa finish CRUD integration today
  
UNBLOCK Darva (CRUD Lamaran):
  - Est. selesai: [X] hari (on track)
  
UNBLOCK Kyla (Tab Tracker):
  - Tunggu Darva CRUD lamaran ✓ (est: X hari)
  - Bisa start prep UI sekarang
  
UNBLOCK Aulia (Tab Statistik):
  - Tunggu FASE 2 & 3 selesai (est: X hari)
  - Bisa prep visualisasi.py sekarang ✓

Recommendation:
  TODAY: Kyla finish + test Tab Beasiswa dengan Darva
  TOMORROW: Kyla start Tab Tracker UI prep
  IN 2 DAYS: Aulia bisa start Chart implementation
```

---

## 16. Troubleshooting & Common Issues

### Jika Saya (Copilot) Lupa Section 0 (Tim)

Ingatkan saya dengan:
```
"Cek Section 0 di copilot-instructions.md — siapa PIC untuk modul ini?"
```

### Jika Ada Konflik Ownership

Contoh: Kyla dan Darva sama-sama ingin implement fitur favorit

**Action:** Ping salah satu PIC untuk koordinasi
```
"Darva & Kyla: Ada konflik implementasi fitur Favorit.
Darva implement database (tabel), Kyla implement UI (button).
Siapa yang mulai duluan?"
```

---

## 17. Appendix: Quick Reference

### Common Requirements
- **Python:** 3.8+
- **GUI:** Tkinter (built-in)
- **Database:** SQLite (included)
- **Scraping:** `requests`, `beautifulsoup4`
- **Charts:** `matplotlib` or `plotly`
- **Encryption:** `bcrypt`

### Environment Setup
```bash
pip install -r requirements.txt
```

### Running the Application
```bash
python main.py
```

### Database Reset (Development Only)
```bash
rm database/beasiswaku.db
python main.py  # Recreates database with auto-scrape
```

---

**Last Updated:** April 2026 (dengan Tim Assignments)  
**Status:** Active (Aligned with Blueprint v1.0)  
**Next Review:** After UTS milestone
