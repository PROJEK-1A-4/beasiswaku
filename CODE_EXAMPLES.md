# 💻 CODE EXAMPLES - Konsep Programming dalam BeasiswaKu

Dokumentasi ini memuat contoh kode praktis untuk setiap konsep programming yang digunakan.

---

## 📚 DAFTAR CONTOH

1. [Fungsi (def) untuk Modularisasi](#1-fungsi-def-untuk-modularisasi)
2. [Class/Objek untuk Pengelompokan](#2-classobjek-untuk-pengelompokan)
3. [Struktur Data: List, Dict, Tuple](#3-struktur-data-list-dict-tuple)
4. [File Handling & I/O](#4-file-handling--io)
5. [Chart & Visualisasi](#5-chart--visualisasi)

---

## 1. Fungsi (def) untuk Modularisasi

### Contoh 1A: CRUD Function (Baca Data)

**File:** `src/database/crud.py`

```python
def get_beasiswa_list(user_id: int) -> List[Dict[str, Any]]:
    """
    Ambil daftar semua beasiswa dari database.
    
    Modularisasi benefits:
    - Dipisah dari UI logic
    - Reusable di berbagai tempat
    - Mudah di-test
    
    Args:
        user_id: ID user (untuk future filtering)
    
    Returns:
        List of beasiswa dictionaries
    """
    try:
        db = DatabaseManager()
        conn = db.get_connection()
        cursor = conn.cursor()
        
        # Query dengan JOIN untuk full data
        query = """
            SELECT 
                b.id,
                b.nama,
                p.nama as penyelenggara,
                b.jenjang,
                b.status,
                b.deadline,
                b.benefit,
                b.deskripsi
            FROM beasiswa b
            LEFT JOIN penyelenggara p ON b.penyelenggara_id = p.id
            WHERE b.status != 'Expired'
            ORDER BY b.deadline ASC
        """
        
        cursor.execute(query)
        rows = cursor.fetchall()
        
        # Convert sqlite3.Row to dict
        beasiswa_list = [dict(row) for row in rows]
        
        logger.info(f"Loaded {len(beasiswa_list)} beasiswa for user {user_id}")
        return beasiswa_list
        
    except Exception as e:
        logger.error(f"Error loading beasiswa: {e}")
        raise

# Usage di BeasiswaTab:
beasiswa_data = get_beasiswa_list(user_id=42)
# Output: [{'id': 1, 'nama': 'Beasiswa A', 'status': 'Buka', ...}, ...]
```

### Contoh 1B: CRUD Function (Tulis Data)

```python
def add_beasiswa_to_favorit(user_id: int, beasiswa_id: int) -> bool:
    """
    Tambahkan beasiswa ke favorit user.
    
    Args:
        user_id: ID user
        beasiswa_id: ID beasiswa
    
    Returns:
        True jika berhasil, False jika gagal
    """
    try:
        db = DatabaseManager()
        query = """
            INSERT INTO favorit (user_id, beasiswa_id, created_at)
            VALUES (?, ?, CURRENT_TIMESTAMP)
        """
        
        db.execute_commit(query, (user_id, beasiswa_id))
        logger.info(f"Added beasiswa {beasiswa_id} to favorit for user {user_id}")
        return True
        
    except sqlite3.IntegrityError:
        # Beasiswa sudah di favorit
        logger.warning(f"Beasiswa {beasiswa_id} already in favorit")
        return False
    except Exception as e:
        logger.error(f"Error adding to favorit: {e}")
        return False

# Usage:
success = add_beasiswa_to_favorit(user_id=42, beasiswa_id=5)
if success:
    print("Added to favorit!")
```

### Contoh 1C: Helper Function (Styling)

```python
def get_button_solid_stylesheet(
    bg_color: str,
    text_color: str = "white",
    border_radius: int = 8
) -> str:
    """
    Generate stylesheet untuk solid button.
    
    DRY principle:
    - Reusable di semua solid button
    - Konsisten styling
    - Mudah dimodifikasi di 1 tempat
    
    Args:
        bg_color: Background color (hex)
        text_color: Text color (default: white)
        border_radius: Border radius in pixels
    
    Returns:
        Stylesheet string untuk QPushButton
    """
    return f"""
        QPushButton {{
            background-color: {bg_color};
            color: {text_color};
            border: none;
            border-radius: {border_radius}px;
            padding: 10px 16px;
            font-weight: bold;
            font-size: 13px;
        }}
        
        QPushButton:hover {{
            background-color: {_darken_color(bg_color, 10)};
        }}
        
        QPushButton:pressed {{
            background-color: {_darken_color(bg_color, 20)};
        }}
        
        QPushButton:disabled {{
            background-color: #cccccc;
            color: #999999;
        }}
    """

def _darken_color(hex_color: str, percent: int) -> str:
    """Helper: Darken color untuk hover/pressed state."""
    # Implementation...
    pass

# Usage:
btn_login = QPushButton("Login")
btn_login.setStyleSheet(get_button_solid_stylesheet("#1e3a8a"))  # Navy button

btn_action = QPushButton("Action")
btn_action.setStyleSheet(get_button_solid_stylesheet("#f59e0b"))  # Orange button
```

### Contoh 1D: Function dengan Default Parameter & Type Hints

```python
def create_bar_chart_beasiswa_per_jenjang(
    data: Dict[str, int],
    title: str = "Jumlah Beasiswa per Jenjang",
    figsize: Tuple[int, int] = (10, 6),
    color: str = "#1E88E5"
) -> Tuple[plt.Figure, plt.Axes]:
    """
    Buat bar chart untuk beasiswa per jenjang.
    
    Type hints benefits:
    - IDE autocomplete lebih baik
    - Early error detection
    - Documentation otomatis
    
    Args:
        data: Dict dengan jenjang sebagai key
        title: Judul chart (default: standar)
        figsize: Size chart (width, height)
        color: Warna bar chart
    
    Returns:
        (Figure, Axes) dari matplotlib
    """
    fig, ax = plt.subplots(figsize=figsize)
    
    if not data:
        _render_empty_state(ax, title)
        return fig, ax
    
    jenjang = list(data.keys())
    counts = list(data.values())
    
    bars = ax.bar(jenjang, counts, color=color, edgecolor="white", linewidth=1.5)
    
    # Add value labels
    for bar in bars:
        height = bar.get_height()
        ax.text(bar.get_x() + bar.get_width()/2., height,
                f'{int(height)}', ha='center', va='bottom', fontweight='bold')
    
    _apply_axis_style(ax)
    return fig, ax

# Usage dengan default params:
fig, ax = create_bar_chart_beasiswa_per_jenjang(
    data={'S1': 45, 'S2': 25, 'S3': 30}
)

# Usage dengan custom params:
fig, ax = create_bar_chart_beasiswa_per_jenjang(
    data={'S1': 45, 'S2': 25, 'S3': 30},
    title="Distribusi Beasiswa 2024",
    color="#f59e0b"  # Orange
)
```

---

## 2. Class/Objek untuk Pengelompokan

### Contoh 2A: Singleton Class (DatabaseManager)

```python
class DatabaseManager:
    """
    Singleton pattern untuk database connection.
    
    Ensure hanya 1 koneksi untuk seluruh aplikasi.
    Benefits:
    - Single point of truth untuk DB
    - Efficient resource usage
    - Easy connection management
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
        """Initialize (called only once)."""
        if self._initialized:
            return
        
        from src.core.config import Config
        self.db_path = Path(Config.DATABASE_PATH)
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self._initialized = True
        logger.info(f"DatabaseManager initialized at {self.db_path}")
    
    def get_connection(self) -> sqlite3.Connection:
        """Get atau create connection (lazy initialization)."""
        if self._connection is None:
            self._connection = sqlite3.connect(str(self.db_path), timeout=10)
            self._connection.row_factory = sqlite3.Row
            logger.debug("New database connection created")
        return self._connection
    
    def execute(self, query: str, params: tuple = None):
        """Execute SELECT query."""
        conn = self.get_connection()
        cursor = conn.cursor()
        if params:
            cursor.execute(query, params)
        else:
            cursor.execute(query)
        return cursor
    
    def execute_commit(self, query: str, params: tuple = None) -> int:
        """Execute INSERT/UPDATE/DELETE dengan commit."""
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
    
    def close_connection(self) -> None:
        """Close connection."""
        if self._connection is not None:
            self._connection.close()
            self._connection = None
            logger.info("Database connection closed")

# Usage:
# Anywhere dalam aplikasi
db = DatabaseManager()  # Returns same instance
conn = db.get_connection()

# Atau langsung
DatabaseManager().execute("SELECT * FROM beasiswa")

# Same instance everywhere
db1 = DatabaseManager()
db2 = DatabaseManager()
assert db1 is db2  # True - sama instance!
```

### Contoh 2B: PyQt6 Widget Class

```python
class BeasiswaTab(QWidget):
    """
    Tab untuk menampilkan daftar beasiswa.
    
    Attributes:
        user_id: ID user yang login
        beasiswa_data: List of beasiswa dari DB
        search_input: QLineEdit untuk search
        filter_status: QComboBox untuk filter
        table: QTableWidget untuk display
    
    Methods:
        init_ui(): Setup UI components
        load_beasiswa_data(): Load dari database
        search_beasiswa(): Filter berdasarkan search text
        filter_by_status(): Filter berdasarkan status
    """
    
    # Signals untuk komunikasi dengan parent
    data_updated = pyqtSignal(int)  # Emitted saat data updated
    search_completed = pyqtSignal(int)  # Emitted saat search selesai
    
    def __init__(self, user_id: int, parent=None):
        super().__init__(parent)
        self.user_id = user_id
        self.beasiswa_data: List[Dict[str, Any]] = []
        
        logger.info(f"Initializing BeasiswaTab for user {user_id}")
        self.init_ui()
        self.load_beasiswa_data()
    
    def init_ui(self):
        """Initialize UI dengan layout."""
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(24, 20, 24, 20)
        
        # Title
        title = QLabel("Daftar Beasiswa")
        title.setFont(QFont("Arial", 28, QFont.Weight.Bold))
        main_layout.addWidget(title)
        
        # Search & Filter
        search_layout = QHBoxLayout()
        
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Cari nama beasiswa...")
        self.search_input.textChanged.connect(self.search_beasiswa)
        search_layout.addWidget(self.search_input)
        
        self.filter_status = QComboBox()
        self.filter_status.addItems(["Semua", "Buka", "Segera Tutup", "Tutup"])
        self.filter_status.currentTextChanged.connect(self.filter_by_status)
        search_layout.addWidget(self.filter_status)
        
        main_layout.addLayout(search_layout)
        
        # Table
        self.table = QTableWidget()
        self.table.setColumnCount(6)
        self.table.setHorizontalHeaderLabels(
            ["ID", "Nama", "Penyelenggara", "Jenjang", "Status", "Deadline"]
        )
        self.table.horizontalHeader().setStretchLastSection(True)
        main_layout.addWidget(self.table)
    
    def load_beasiswa_data(self):
        """Load beasiswa dari database."""
        try:
            self.beasiswa_data = get_beasiswa_list(self.user_id)
            self.refresh_table()
            logger.info(f"Loaded {len(self.beasiswa_data)} beasiswa")
        except Exception as e:
            logger.error(f"Error loading beasiswa: {e}")
            QMessageBox.critical(self, "Error", f"Failed to load: {e}")
    
    def search_beasiswa(self, search_text: str):
        """Filter beasiswa by nama (real-time search)."""
        # List comprehension untuk filter
        filtered = [
            b for b in self.beasiswa_data
            if search_text.lower() in b['nama'].lower()
        ]
        self.display_in_table(filtered)
        self.search_completed.emit(len(filtered))
    
    def filter_by_status(self, status: str):
        """Filter beasiswa by status."""
        if status == "Semua":
            filtered = self.beasiswa_data
        else:
            filtered = [b for b in self.beasiswa_data if b['status'] == status]
        
        self.display_in_table(filtered)
    
    def display_in_table(self, data: List[Dict]):
        """Populate table dengan beasiswa data."""
        self.table.setRowCount(len(data))
        
        for row, beasiswa in enumerate(data):
            self.table.setItem(row, 0, QTableWidgetItem(str(beasiswa['id'])))
            self.table.setItem(row, 1, QTableWidgetItem(beasiswa['nama']))
            self.table.setItem(row, 2, QTableWidgetItem(beasiswa['penyelenggara']))
            self.table.setItem(row, 3, QTableWidgetItem(beasiswa['jenjang']))
            self.table.setItem(row, 4, QTableWidgetItem(beasiswa['status']))
            self.table.setItem(row, 5, QTableWidgetItem(beasiswa['deadline']))

# Usage dalam MainWindow:
beasiswa_tab = BeasiswaTab(user_id=42)
tabs.addTab(beasiswa_tab, "Beasiswa")
```

### Contoh 2C: Custom Dialog Class

```python
class BeasiswaDetailDialog(QDialog):
    """Dialog untuk menampilkan/edit detail beasiswa."""
    
    beasiswa_updated = pyqtSignal(dict)  # Emit saat data updated
    
    def __init__(self, beasiswa: Dict, parent=None):
        super().__init__(parent)
        self.beasiswa = beasiswa
        self.init_ui()
    
    def init_ui(self):
        """Setup dialog UI."""
        self.setWindowTitle(f"Detail - {self.beasiswa['nama']}")
        self.setGeometry(100, 100, 500, 600)
        
        layout = QFormLayout()
        
        # Input fields
        self.nama_input = QLineEdit()
        self.nama_input.setText(self.beasiswa['nama'])
        layout.addRow("Nama:", self.nama_input)
        
        self.jenjang_combo = QComboBox()
        self.jenjang_combo.addItems(["S1", "S2", "S3"])
        self.jenjang_combo.setCurrentText(self.beasiswa['jenjang'])
        layout.addRow("Jenjang:", self.jenjang_combo)
        
        self.status_combo = QComboBox()
        self.status_combo.addItems(["Buka", "Segera Tutup", "Tutup"])
        self.status_combo.setCurrentText(self.beasiswa['status'])
        layout.addRow("Status:", self.status_combo)
        
        # Buttons
        btn_layout = QHBoxLayout()
        
        save_btn = QPushButton("Simpan")
        save_btn.clicked.connect(self.save_changes)
        btn_layout.addWidget(save_btn)
        
        cancel_btn = QPushButton("Batal")
        cancel_btn.clicked.connect(self.reject)
        btn_layout.addWidget(cancel_btn)
        
        layout.addRow(btn_layout)
        self.setLayout(layout)
    
    def save_changes(self):
        """Save perubahan ke database."""
        updated = {
            **self.beasiswa,
            'nama': self.nama_input.text(),
            'jenjang': self.jenjang_combo.currentText(),
            'status': self.status_combo.currentText()
        }
        
        try:
            # Update DB
            update_beasiswa(updated)
            self.beasiswa_updated.emit(updated)
            self.accept()
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to save: {e}")

# Usage:
dialog = BeasiswaDetailDialog(beasiswa_data)
if dialog.exec() == QDialog.DialogCode.Accepted:
    print("Beasiswa updated")
```

---

## 3. Struktur Data: List, Dict, Tuple

### Contoh 3A: List - Penyimpanan Data Terurut

```python
# Load beasiswa sebagai list
beasiswa_data: List[Dict[str, Any]] = get_beasiswa_list(user_id)

# Result structure:
beasiswa_data = [
    {
        'id': 1,
        'nama': 'Beasiswa Unggulan',
        'penyelenggara': 'Kemendikbud',
        'jenjang': 'S1',
        'status': 'Buka',
        'deadline': '2024-06-30'
    },
    {
        'id': 2,
        'nama': 'Beasiswa Mandiri',
        'penyelenggara': 'Bank Mandiri',
        'jenjang': 'S1',
        'status': 'Segera Tutup',
        'deadline': '2024-06-15'
    },
    # ... more items
]

# ===== LIST OPERATIONS =====

# 1. ITERATE
for beasiswa in beasiswa_data:
    print(f"{beasiswa['nama']} - {beasiswa['status']}")

# 2. FILTERING (List Comprehension)
# Hanya beasiswa yang masih buka
buka = [b for b in beasiswa_data if b['status'] == 'Buka']
print(f"Found {len(buka)} open scholarships")

# Hanya S1 beasiswa
s1_only = [b for b in beasiswa_data if b['jenjang'] == 'S1']

# Beasiswa dari Kemendikbud
kemendikbud = [b for b in beasiswa_data if b['penyelenggara'] == 'Kemendikbud']

# 3. SORTING
# Sort by deadline terdekat
sorted_by_deadline = sorted(beasiswa_data, key=lambda b: b['deadline'])

# Sort by nama (A-Z)
sorted_by_name = sorted(beasiswa_data, key=lambda b: b['nama'])

# 4. MAPPING
nama_list = [b['nama'] for b in beasiswa_data]
# Result: ['Beasiswa Unggulan', 'Beasiswa Mandiri', ...]

# 5. COUNTING
from collections import Counter

status_counts = Counter([b['status'] for b in beasiswa_data])
# Result: Counter({'Buka': 45, 'Segera Tutup': 20, 'Tutup': 35})

jenjang_counts = Counter([b['jenjang'] for b in beasiswa_data])
# Result: Counter({'S1': 45, 'S2': 25, 'S3': 30})

# 6. FINDING
first_buka = next((b for b in beasiswa_data if b['status'] == 'Buka'), None)
if first_buka:
    print(f"First open: {first_buka['nama']}")

# 7. ANY/ALL
has_s1 = any(b['jenjang'] == 'S1' for b in beasiswa_data)
all_buka = all(b['status'] == 'Buka' for b in beasiswa_data)

# 8. SLICING
top_5 = beasiswa_data[:5]  # First 5
last_3 = beasiswa_data[-3:]  # Last 3
every_other = beasiswa_data[::2]  # Every other item

print(f"Total: {len(beasiswa_data)}")
```

### Contoh 3B: Dictionary - Penyimpanan Key-Value

```python
# Single beasiswa record
beasiswa = {
    'id': 1,
    'nama': 'Beasiswa Unggulan',
    'penyelenggara_id': 5,
    'penyelenggara': 'Kemendikbud',
    'jenjang': 'S1',
    'status': 'Buka',
    'deadline': '2024-06-30',
    'benefit': 'Rp 5.000.000/bulan + Asuransi',
    'persyaratan': ['IPK >= 3.0', 'Surat rekomendasi', 'Esai'],
    'contact': 'info@kemendikbud.go.id'
}

# ===== DICT OPERATIONS =====

# 1. ACCESS VALUES
nama = beasiswa['nama']  # 'Beasiswa Unggulan'
status = beasiswa.get('status', 'Unknown')  # Safe access

# 2. MODIFY VALUES
beasiswa['status'] = 'Tutup'
beasiswa['updated_at'] = datetime.now()

# 3. ADD NEW KEY-VALUE
beasiswa['views'] = 150
beasiswa['last_viewed'] = '2024-05-20'

# 4. DELETE KEY
del beasiswa['views']

# 5. ITERATE KEYS
for key in beasiswa.keys():
    print(f"Key: {key}")

# 6. ITERATE VALUES
for value in beasiswa.values():
    print(f"Value: {value}")

# 7. ITERATE KEY-VALUE PAIRS
for key, value in beasiswa.items():
    print(f"{key}: {value}")

# 8. CHECK KEY EXISTS
if 'nama' in beasiswa:
    print("Nama field exists")

# 9. UPDATE MULTIPLE VALUES
beasiswa.update({
    'status': 'Buka',
    'views': 200,
    'last_updated': datetime.now()
})

# 10. MERGE DICTS (Python 3.9+)
new_data = {'views': 250, 'trending': True}
merged = {**beasiswa, **new_data}

# ===== ADVANCED: MAPPING STRUCTURES =====

# Color mapping
COLOR_MAP = {
    'Buka': '#2E7D32',      # Green
    'Segera Tutup': '#F9A825',  # Orange
    'Tutup': '#C62828'      # Red
}

status = beasiswa['status']
color = COLOR_MAP.get(status, '#cccccc')

# Configuration dict
CONFIG = {
    'app_name': 'BeasiswaKu',
    'version': '2.0.0',
    'db_path': 'database/beasiswaku.db',
    'window_size': (1280, 800),
    'theme': 'navy-orange'
}

# Type mapping
type_mapping = {
    str: 'String',
    int: 'Integer',
    float: 'Number',
    list: 'Array',
    dict: 'Object'
}

# User profile
user_profile = {
    'id': 42,
    'username': 'kyla',
    'email': 'kyla@example.com',
    'nama_lengkap': 'Kyla Aurellio',
    'universitas': 'ITB',
    'ipk': 3.85,
    'jenjang': 'S1',
    'preferences': {  # Nested dict
        'theme': 'dark',
        'notifications': True,
        'language': 'id'
    }
}

# Access nested dict
theme = user_profile['preferences']['theme']
```

### Contoh 3C: Tuple - Immutable Data & Multiple Returns

```python
# 1. FUNCTION RETURN MULTIPLE VALUES
def login_user(username: str, password: str) -> Tuple[bool, str, int]:
    """Return (success, message, user_id)."""
    # ... validation logic
    if valid:
        return (True, "Login successful", 42)
    else:
        return (False, "Invalid credentials", -1)

# Usage: Unpacking tuple
success, message, user_id = login_user("kyla", "password123")
if success:
    print(f"Welcome {user_id}!")

# 2. CHART FUNCTION RETURNS
def create_chart() -> Tuple[plt.Figure, plt.Axes]:
    """Return matplotlib figure and axes."""
    fig, ax = plt.subplots()
    # ... create chart
    return fig, ax

fig, ax = create_chart()
canvas = FigureCanvas(fig)

# 3. COORDINATE TUPLES
point = (100, 50)  # (x, y)
x, y = point

button_position = (x + 10, y + 10)  # New position

# 4. FIXED SIZE DATA
rgb_color = (30, 58, 138)  # (R, G, B) for Navy
r, g, b = rgb_color

# 5. TUPLE AS DICTIONARY KEY (Immutable!)
button_styles = {
    ('navy', 'solid'): "background-color: #1e3a8a;",
    ('navy', 'outline'): "background: transparent; border: 2px solid #1e3a8a;",
    ('orange', 'solid'): "background-color: #f59e0b;",
    ('orange', 'outline'): "background: transparent; border: 2px solid #f59e0b;"
}

# Access
style = button_styles[('navy', 'solid')]

# 6. MULTIPLE ASSIGNMENT
user_data = (42, "kyla", "kyla@example.com")
user_id, username, email = user_data

# 7. RETURNING MULTIPLE WITH TUPLE
def get_user_stats(user_id: int) -> Tuple[int, int, float]:
    """Return (total_lamaran, accepted, avg_score)."""
    lamaran_count = 15
    accepted_count = 5
    avg_score = 3.85
    return (lamaran_count, accepted_count, avg_score)

total, accepted, score = get_user_stats(42)
print(f"Applied: {total}, Accepted: {accepted}, Score: {score}")

# 8. TUPLE UNPACKING WITH *
data = ("Beasiswa A", "Kemendikbud", "S1", "Buka")
nama, penyelenggara, *rest = data
# nama = "Beasiswa A"
# penyelenggara = "Kemendikbud"
# rest = ["S1", "Buka"]

# 9. TUPLE IMMUTABILITY
config = (1280, 800)  # Window size - should not change
# config[0] = 1920  # Error! Tuples are immutable

# If need mutability, use list instead
mutable_list = [1280, 800]
mutable_list[0] = 1920  # OK
```

---

## 4. File Handling & I/O

### Contoh 4A: Database File Handling

```python
# Configuration file paths
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent.parent
DATABASE_PATH = BASE_DIR / "database" / "beasiswaku.db"
LOG_DIR = BASE_DIR / "logs"

# Ensure directories exist
DATABASE_PATH.parent.mkdir(parents=True, exist_ok=True)
LOG_DIR.mkdir(parents=True, exist_ok=True)

# Create/Connect to database
import sqlite3

conn = sqlite3.connect(str(DATABASE_PATH), timeout=10)
conn.row_factory = sqlite3.Row  # Return dict-like objects

# Create schema
def init_database():
    """Initialize database dengan default schema."""
    cursor = conn.cursor()
    
    # Create tables
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS beasiswa (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nama TEXT NOT NULL,
            penyelenggara_id INTEGER,
            jenjang TEXT,
            status TEXT,
            deadline DATE,
            benefit TEXT,
            deskripsi TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS akun (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            email TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL,
            nama_lengkap TEXT,
            jenjang TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    
    conn.commit()
    logger.info("Database schema initialized")

# Read from database
def read_beasiswa(beasiswa_id: int) -> Optional[Dict]:
    """Read single beasiswa from database."""
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM beasiswa WHERE id = ?", (beasiswa_id,))
    row = cursor.fetchone()
    return dict(row) if row else None

# Write to database
def insert_beasiswa(nama: str, penyelenggara_id: int, jenjang: str) -> int:
    """Insert beasiswa, return lastrowid."""
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO beasiswa (nama, penyelenggara_id, jenjang)
        VALUES (?, ?, ?)
    """, (nama, penyelenggara_id, jenjang))
    conn.commit()
    logger.info(f"Inserted beasiswa with id {cursor.lastrowid}")
    return cursor.lastrowid

# Update database
def update_beasiswa(beasiswa_id: int, status: str) -> bool:
    """Update beasiswa status."""
    try:
        cursor = conn.cursor()
        cursor.execute("""
            UPDATE beasiswa
            SET status = ?, updated_at = CURRENT_TIMESTAMP
            WHERE id = ?
        """, (status, beasiswa_id))
        conn.commit()
        logger.info(f"Updated beasiswa {beasiswa_id} status to {status}")
        return True
    except sqlite3.Error as e:
        conn.rollback()
        logger.error(f"Update error: {e}")
        return False

# Close connection
def close_database():
    """Close database connection."""
    conn.close()
    logger.info("Database connection closed")
```

### Contoh 4B: CSV Export

```python
import csv
from datetime import datetime

def export_beasiswa_to_csv(beasiswa_data: List[Dict], filename: str = None) -> str:
    """
    Export beasiswa data ke CSV file.
    
    Args:
        beasiswa_data: List of beasiswa dictionaries
        filename: Output filename (default: beasiswa_export_YYYYMMDD.csv)
    
    Returns:
        Path ke file yang di-export
    """
    if filename is None:
        filename = f"beasiswa_export_{datetime.now().strftime('%Y%m%d')}.csv"
    
    filepath = Path("data") / filename
    filepath.parent.mkdir(parents=True, exist_ok=True)
    
    try:
        # Define columns
        fieldnames = ['ID', 'Nama', 'Penyelenggara', 'Jenjang', 'Status', 'Deadline', 'Benefit']
        
        # Write CSV
        with open(filepath, 'w', newline='', encoding='utf-8') as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            
            # Write header
            writer.writeheader()
            
            # Write data rows
            for beasiswa in beasiswa_data:
                writer.writerow({
                    'ID': beasiswa.get('id', ''),
                    'Nama': beasiswa.get('nama', ''),
                    'Penyelenggara': beasiswa.get('penyelenggara', ''),
                    'Jenjang': beasiswa.get('jenjang', ''),
                    'Status': beasiswa.get('status', ''),
                    'Deadline': beasiswa.get('deadline', ''),
                    'Benefit': beasiswa.get('benefit', '')
                })
        
        logger.info(f"Exported {len(beasiswa_data)} beasiswa to {filepath}")
        return str(filepath)
        
    except Exception as e:
        logger.error(f"CSV export error: {e}")
        raise

# Usage dalam PyQt6:
def on_export_clicked(self):
    """Handle export button click."""
    file_path, _ = QFileDialog.getSaveFileName(
        self,
        "Export Beasiswa",
        "",
        "CSV Files (*.csv);;All Files (*)"
    )
    
    if file_path:
        try:
            export_beasiswa_to_csv(self.beasiswa_data, file_path)
            QMessageBox.information(self, "Success", f"Exported to {file_path}")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Export failed: {e}")
```

### Contoh 4C: Logging File

```python
import logging
from pathlib import Path
from datetime import datetime

# Setup logging configuration
LOG_DIR = Path("logs")
LOG_DIR.mkdir(exist_ok=True)

log_filename = f"beasiswaku_{datetime.now().strftime('%Y%m%d')}.log"
log_path = LOG_DIR / log_filename

# Create logger
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

# File handler
file_handler = logging.FileHandler(log_path)
file_handler.setLevel(logging.DEBUG)

# Console handler
console_handler = logging.StreamHandler()
console_handler.setLevel(logging.INFO)

# Formatter
formatter = logging.Formatter(
    '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)
file_handler.setFormatter(formatter)
console_handler.setFormatter(formatter)

# Add handlers
logger.addHandler(file_handler)
logger.addHandler(console_handler)

# Usage
logger.info("Application started")
logger.debug("Loaded configuration file")
logger.warning("Database connection slow")
logger.error("Failed to load beasiswa")
logger.critical("Database file corrupted")

# Example log output:
# 2024-05-20 10:30:45 - __main__ - INFO - Application started
# 2024-05-20 10:30:45 - __main__ - DEBUG - Loaded configuration file
```

### Contoh 4D: JSON Configuration

```python
import json
from pathlib import Path
from typing import Dict, Any

CONFIG_FILE = Path("config.json")

def load_config() -> Dict[str, Any]:
    """Load configuration from JSON file."""
    if not CONFIG_FILE.exists():
        return get_default_config()
    
    try:
        with open(CONFIG_FILE, 'r', encoding='utf-8') as f:
            config = json.load(f)
        logger.info("Configuration loaded")
        return config
    except Exception as e:
        logger.error(f"Config load error: {e}")
        return get_default_config()

def save_config(config: Dict[str, Any]):
    """Save configuration to JSON file."""
    try:
        with open(CONFIG_FILE, 'w', encoding='utf-8') as f:
            json.dump(config, f, indent=4)
        logger.info("Configuration saved")
    except Exception as e:
        logger.error(f"Config save error: {e}")

def get_default_config() -> Dict[str, Any]:
    """Return default configuration."""
    return {
        'app_name': 'BeasiswaKu',
        'version': '2.0.0',
        'window_width': 1280,
        'window_height': 800,
        'theme': 'navy-orange',
        'language': 'id',
        'notifications_enabled': True,
        'items_per_page': 20
    }

# Usage:
config = load_config()
print(config['window_width'])  # 1280

# Modify
config['theme'] = 'dark'
save_config(config)
```

---

## 5. Chart & Visualisasi

### Contoh 5A: Bar Chart Function

```python
from matplotlib import pyplot as plt
from matplotlib.ticker import MaxNLocator
from typing import Dict, Tuple

def create_bar_chart_beasiswa_per_jenjang(
    data: Dict[str, int],
    title: str = "Jumlah Beasiswa per Jenjang"
) -> Tuple[plt.Figure, plt.Axes]:
    """
    Buat bar chart untuk beasiswa per jenjang.
    
    Data input: {'S1': 45, 'S2': 25, 'S3': 30}
    
    Features:
    - Responsive sizing
    - Value labels on bars
    - Professional styling
    - Empty state handling
    """
    fig, ax = plt.subplots(figsize=(10, 6))
    
    # Handle empty data
    if not data:
        ax.text(0.5, 0.5, "Data tidak tersedia",
                ha='center', va='center',
                fontsize=12, color='#5f6b7a',
                transform=ax.transAxes)
        ax.set_xticks([])
        ax.set_yticks([])
        return fig, ax
    
    # Extract data
    jenjang = list(data.keys())      # ['S1', 'S2', 'S3']
    counts = list(data.values())     # [45, 25, 30]
    
    # Create bar chart
    bars = ax.bar(
        jenjang,
        counts,
        color="#1E88E5",          # Navy blue
        edgecolor="white",
        linewidth=1.5,
        alpha=0.8
    )
    
    # Add value labels on top of bars
    for bar in bars:
        height = bar.get_height()
        ax.text(
            bar.get_x() + bar.get_width()/2.,
            height,
            f'{int(height)}',
            ha='center',
            va='bottom',
            fontweight='bold',
            fontsize=11
        )
    
    # Styling
    ax.grid(axis='y', linestyle='--', alpha=0.35, color='#D9D9D9')
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    ax.set_ylabel("Jumlah Beasiswa", fontsize=11, fontweight="bold")
    ax.yaxis.set_major_locator(MaxNLocator(integer=True))
    
    plt.tight_layout()
    return fig, ax

# Usage dalam PyQt6:
from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg as FigureCanvas

data = get_beasiswa_per_jenjang()  # {'S1': 45, 'S2': 25, 'S3': 30}
fig, ax = create_bar_chart_beasiswa_per_jenjang(data)
canvas = FigureCanvas(fig)
layout.addWidget(canvas)
```

### Contoh 5B: Donut Chart Function

```python
def create_donut_chart_status(
    data: Dict[str, int],
    title: str = "Status Beasiswa"
) -> Tuple[plt.Figure, plt.Axes]:
    """
    Buat donut chart untuk status distribution.
    
    Data input: {'Buka': 45, 'Segera Tutup': 20, 'Tutup': 35}
    
    Features:
    - Color coding by status
    - Percentage labels
    - Professional appearance
    """
    COLOR_MAP = {
        'Buka': '#2E7D32',          # Green
        'Segera Tutup': '#F9A825',  # Orange
        'Tutup': '#C62828'          # Red
    }
    
    fig, ax = plt.subplots(figsize=(8, 6))
    
    # Handle empty data
    if not data:
        ax.text(0.5, 0.5, "Data tidak tersedia",
                ha='center', va='center', fontsize=12,
                transform=ax.transAxes)
        return fig, ax
    
    # Extract data
    labels = list(data.keys())      # ['Buka', 'Segera Tutup', 'Tutup']
    sizes = list(data.values())     # [45, 20, 35]
    colors = [COLOR_MAP.get(l, '#cccccc') for l in labels]
    
    # Create pie chart
    wedges, texts, autotexts = ax.pie(
        sizes,
        labels=labels,
        colors=colors,
        autopct='%1.1f%%',
        startangle=90,
        textprops={'fontsize': 10, 'weight': 'bold'}
    )
    
    # Make percentage text white
    for autotext in autotexts:
        autotext.set_color('white')
        autotext.set_fontweight('bold')
    
    # Create white center circle (donut effect)
    centre_circle = plt.Circle((0, 0), 0.70, fc='white')
    ax.add_artist(centre_circle)
    
    plt.tight_layout()
    return fig, ax
```

### Contoh 5C: Integration ke PyQt6

```python
class StatistikTab(QWidget):
    """Tab untuk statistik dengan chart."""
    
    def __init__(self, user_id: int, parent=None):
        super().__init__(parent)
        self.user_id = user_id
        self.init_ui()
    
    def init_ui(self):
        """Setup UI dengan multiple charts."""
        main_layout = QVBoxLayout(self)
        main_layout.setSpacing(20)
        
        # Chart 1: Beasiswa per Jenjang
        self._add_chart(
            main_layout,
            "Beasiswa per Jenjang",
            lambda: get_beasiswa_per_jenjang(),
            create_bar_chart_beasiswa_per_jenjang
        )
        
        # Chart 2: Status Distribution
        self._add_chart(
            main_layout,
            "Status Beasiswa",
            lambda: get_status_availability(),
            create_donut_chart_status
        )
        
        # Chart 3: Top Penyelenggara
        self._add_chart(
            main_layout,
            "Top 10 Penyelenggara",
            lambda: get_top_penyelenggara(),
            create_horizontal_bar_chart
        )
    
    def _add_chart(self, layout, title, data_func, chart_func):
        """Helper: Tambahkan chart ke layout."""
        try:
            data = data_func()
            fig, ax = chart_func(data)
            
            canvas = FigureCanvas(fig)
            canvas.setMinimumHeight(300)
            
            # Wrap dalam frame/card
            card = QWidget()
            card.setStyleSheet("""
                QWidget {
                    background: white;
                    border: 1px solid #d7dee8;
                    border-radius: 12px;
                }
            """)
            card_layout = QVBoxLayout(card)
            card_layout.setContentsMargins(16, 14, 16, 16)
            
            # Title
            title_label = QLabel(title)
            title_label.setFont(QFont("Arial", 13, QFont.Weight.Bold))
            card_layout.addWidget(title_label)
            
            # Canvas
            card_layout.addWidget(canvas)
            
            layout.addWidget(card)
            
        except Exception as e:
            logger.error(f"Chart error: {e}")
            error_label = QLabel(f"Failed to load chart: {e}")
            layout.addWidget(error_label)
```

---

## 📌 Quick Reference

### Function Pattern
```python
def function_name(param1: Type1, param2: Type2) -> ReturnType:
    """Docstring."""
    # Implementation
    return result
```

### Class Pattern
```python
class ClassName:
    """Docstring."""
    
    def __init__(self, param):
        self.attribute = param
    
    def method(self):
        """Method docstring."""
        pass
```

### Dictionary Pattern
```python
data = {
    'key1': 'value1',
    'key2': 'value2',
    'nested': {'inner_key': 'inner_value'}
}
```

### List Pattern
```python
items = [item1, item2, item3]
filtered = [item for item in items if condition]
```

---

**Last Updated:** April 13, 2026  
**Status:** ✅ Complete with Examples
