# 📚 DOKUMENTASI KONSEP PROGRAMMING - BeasiswaKu

**Project:** BeasiswaKu - Personal Scholarship Management Application  
**Date:** April 13, 2026  
**Status:** Complete with Code Examples  

---

## 📖 DAFTAR ISI
1. [Penggunaan Fungsi (def) untuk Modularisasi](#1-penggunaan-fungsi-def-untuk-modularisasi)
2. [Penggunaan Class/Objek untuk Pengelompokan Data & Logika](#2-penggunaan-classobjek-untuk-pengelompokan-data--logika)
3. [Penggunaan Struktur Data (List, Dictionary, Tuple)](#3-penggunaan-struktur-data-list-dictionary-tuple)
4. [File Handling (Membaca & Menulis File)](#4-file-handling-membaca--menulis-file)
5. [Visualisasi & Chart](#5-visualisasi--chart)
6. [Keterkaitan Konsep dengan Fitur](#6-keterkaitan-konsep-dengan-fitur)

---

## 1. Penggunaan Fungsi (def) untuk Modularisasi

### Konsep: Modularisasi dengan Fungsi

Fungsi digunakan untuk membagi program menjadi bagian-bagian kecil yang reusable, mudah dipahami, dan mudah di-maintain.

### Contoh di BeasiswaKu:

#### A. **Database CRUD Functions** (src/database/crud.py)
```python
def init_db():
    """Inisialisasi database dengan schema awal."""
    # Setup koneksi database
    # Create tables
    # Setup default data

def login_user(username: str, password: str) -> Tuple[bool, str, int]:
    """
    Login user ke sistem.
    
    Args:
        username: Username pengguna
        password: Password pengguna
    
    Returns:
        (success: bool, message: str, user_id: int)
    """
    # Validasi username
    # Check password
    # Return hasil

def register_user(username: str, email: str, password: str) -> Tuple[bool, str]:
    """
    Register user baru.
    
    Args:
        username: Username baru
        email: Email user
        password: Password (di-hash)
    
    Returns:
        (success: bool, message: str)
    """
    # Validasi input
    # Hash password (keamanan)
    # Insert ke DB
    # Return hasil

def get_beasiswa_list(user_id: int) -> List[Dict]:
    """Load semua beasiswa dari database."""
    # Query DB
    # Format data
    # Return list of beasiswa

def add_beasiswa_to_favorit(user_id: int, beasiswa_id: int) -> bool:
    """Tambahkan beasiswa ke favorit user."""
    # Insert ke tabel favorit
    # Return success status

def get_lamaran_by_user(user_id: int) -> List[Dict]:
    """Ambil semua lamaran yang dibuat user."""
    # Query database
    # Filter by user_id
    # Return list of lamaran
```

#### B. **Styling Helper Functions** (src/gui/styles.py)
```python
def get_button_solid_stylesheet(bg_color: str, text_color: str = "white") -> str:
    """
    Generate stylesheet untuk solid button.
    
    Manfaat modularisasi:
    - Reusable di semua button
    - Konsisten styling
    - Mudah diubah (DRY - Don't Repeat Yourself)
    """
    return f"""
        QPushButton {{
            background-color: {bg_color};
            color: {text_color};
            border: none;
            border-radius: 8px;
            padding: 10px 16px;
            font-weight: bold;
        }}
        QPushButton:hover {{
            background-color: darker({bg_color}, 110%);
        }}
    """

def get_table_stylesheet() -> str:
    """Generate stylesheet untuk table."""
    return """
        QTableWidget {
            gridline-color: #d7dee8;
            background-color: white;
        }
        QTableWidget::item {
            padding: 8px;
            border: none;
        }
    """

def get_input_field_stylesheet() -> str:
    """Generate stylesheet untuk input field."""
    return """
        QLineEdit {
            border: 1px solid #d7dee8;
            border-radius: 8px;
            padding: 10px;
            font-size: 13px;
        }
    """
```

#### C. **Visualization Functions** (src/visualization/visualisasi.py)
```python
def _apply_axis_style(ax) -> None:
    """Helper internal untuk styling sumbu chart secara konsisten."""
    ax.grid(axis="y", linestyle="--", alpha=0.35)
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)

def create_bar_chart_beasiswa_per_jenjang(
    data: Dict[str, int],
    title: str = "Jumlah Beasiswa per Jenjang"
) -> Tuple[plt.Figure, plt.Axes]:
    """
    Buat chart bar untuk beasiswa per jenjang.
    
    Modularisasi:
    - Fungsi khusus untuk 1 jenis chart
    - Dapat dipanggil dari berbagai tempat
    - Data dari database, display di UI
    """
    fig, ax = plt.subplots(figsize=(10, 6))
    
    if not data:
        _render_empty_state(ax, title)
        return fig, ax
    
    # Process data
    jenjang = list(data.keys())
    counts = list(data.values())
    
    # Create bar chart
    bars = ax.bar(jenjang, counts, color="#1E88E5", edgecolor="white", linewidth=1.5)
    
    # Apply styling
    _apply_axis_style(ax)
    ax.set_ylabel("Jumlah Beasiswa", fontsize=11, fontweight="bold")
    ax.yaxis.set_major_locator(MaxNLocator(integer=True))
    
    return fig, ax

def create_donut_chart_status(
    data: Dict[str, int],
    title: str = "Status Beasiswa"
) -> Tuple[plt.Figure, plt.Axes]:
    """Buat donut chart untuk status beasiswa."""
    fig, ax = plt.subplots(figsize=(8, 6))
    
    if not data:
        _render_empty_state(ax, title)
        return fig, ax
    
    # Create donut
    labels = list(data.keys())
    sizes = list(data.values())
    colors = [COLOR_PALETTE.get(label, "#cccccc") for label in labels]
    
    wedges, texts, autotexts = ax.pie(
        sizes, labels=labels, colors=colors,
        autopct='%1.1f%%', startangle=90
    )
    
    # Add center circle untuk donut effect
    centre_circle = plt.Circle((0, 0), 0.70, fc='white')
    ax.add_artist(centre_circle)
    
    return fig, ax
```

### Keuntungan Modularisasi dengan Fungsi:

| Aspek | Manfaat |
|-------|---------|
| **Reusability** | Fungsi dapat dipanggil berkali-kali dari berbagai tempat |
| **Readability** | Kode lebih mudah dibaca dan dipahami |
| **Maintainability** | Perubahan cukup dilakukan di 1 tempat (DRY principle) |
| **Testing** | Lebih mudah untuk unit testing setiap fungsi |
| **Organization** | Program terstruktur dengan baik, logis |

---

## 2. Penggunaan Class/Objek untuk Pengelompokan Data & Logika

### Konsep: OOP (Object-Oriented Programming)

Class digunakan untuk mengelompokkan data (attributes) dan fungsi (methods) yang saling terkait dalam satu entitas logis.

### Contoh di BeasiswaKu:

#### A. **DatabaseManager Class** (src/core/database.py)
```python
class DatabaseManager:
    """
    Singleton class untuk mengelola koneksi database.
    
    Attributes:
        _instance: Singleton instance
        _connection: SQLite connection
        db_path: Path ke database file
    
    Methods:
        get_connection(): Dapatkan koneksi DB
        execute(): Execute query
        execute_commit(): Execute dan commit
        init_schema(): Buat schema tables
        close_connection(): Tutup koneksi
    """
    
    _instance: Optional['DatabaseManager'] = None
    _connection: Optional[sqlite3.Connection] = None
    
    def __new__(cls):
        """Singleton pattern: hanya 1 instance untuk seluruh app."""
        if cls._instance is None:
            cls._instance = super(DatabaseManager, cls).__new__(cls)
            cls._instance._initialized = False
        return cls._instance
    
    def __init__(self):
        """Initialize database manager."""
        if self._initialized:
            return
        self.db_path = Path(Config.DATABASE_PATH)
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
    
    def get_connection(self) -> sqlite3.Connection:
        """
        Get atau create database connection.
        
        Keuntungan:
        - Lazy initialization
        - Reuse existing connection
        - Efficient resource usage
        """
        if self._connection is None:
            self._connection = sqlite3.connect(str(self.db_path))
            self._connection.row_factory = sqlite3.Row
        return self._connection
    
    def execute(self, query: str, params: tuple = None):
        """Execute read query."""
        conn = self.get_connection()
        cursor = conn.cursor()
        if params:
            cursor.execute(query, params)
        else:
            cursor.execute(query)
        return cursor
    
    def execute_commit(self, query: str, params: tuple = None) -> int:
        """Execute write query with commit."""
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
```

**Keuntungan:**
- **Encapsulation:** Database logic terisolasi dalam class
- **Singleton Pattern:** Hanya 1 connection untuk seluruh app (efficient)
- **Error Handling:** Rollback otomatis jika ada error
- **Reusability:** Dapat digunakan dari berbagai modul

#### B. **LoginWindow Class** (main.py)
```python
class LoginWindow(QDialog):
    """
    Window untuk login dan register user.
    
    Attributes:
        current_user_id: ID user yang login
        username_input: QLineEdit field username
        password_input: QLineEdit field password
    
    Signals:
        login_success: Signal saat login berhasil
    
    Methods:
        init_ui(): Setup UI components
        handle_login(): Process login
        handle_register(): Process register
        emit_login_success(): Emit signal ke main window
    """
    
    login_success = pyqtSignal(int, str)  # user_id, username
    
    def __init__(self):
        super().__init__()
        self.current_user_id = None
        self.init_ui()
    
    def init_ui(self):
        """Initialize login window UI."""
        self.setWindowTitle("BeasiswaKu - Login")
        self.setGeometry(100, 100, 400, 300)
        self.setModal(True)
        
        layout = QVBoxLayout()
        
        # Title
        title = QLabel("🎓 BeasiswaKu")
        title.setFont(QFont("Arial", 20, QFont.Weight.Bold))
        layout.addWidget(title)
        
        # Input fields
        self.username_input = QLineEdit()
        self.username_input.setPlaceholderText("Username")
        layout.addWidget(self.username_input)
        
        self.password_input = QLineEdit()
        self.password_input.setPlaceholderText("Password")
        self.password_input.setEchoMode(QLineEdit.EchoMode.Password)
        layout.addWidget(self.password_input)
        
        # Buttons
        login_btn = QPushButton("Login")
        login_btn.clicked.connect(self.handle_login)
        layout.addWidget(login_btn)
        
        self.setLayout(layout)
    
    def handle_login(self):
        """Process login dengan validasi."""
        username = self.username_input.text()
        password = self.password_input.text()
        
        # Validasi
        if not username or not password:
            QMessageBox.warning(self, "Error", "Username dan password tidak boleh kosong")
            return
        
        # Call CRUD function
        success, message, user_id = login_user(username, password)
        
        if success:
            self.current_user_id = user_id
            self.login_success.emit(user_id, username)
            self.accept()
        else:
            QMessageBox.critical(self, "Login Failed", message)
    
    def handle_register(self):
        """Process register user baru."""
        # Similar to handle_login
        pass
```

#### C. **BeasiswaTab Class** (src/gui/gui_beasiswa.py)
```python
class BeasiswaTab(QWidget):
    """
    Tab Beasiswa (Scholarship List) dengan data table dan actions.
    
    Attributes:
        user_id: ID user yang login
        beasiswa_data: List of beasiswa dict
        search_input: QLineEdit untuk search
        filter_status: QComboBox untuk filter status
        filter_jenjang: QComboBox untuk filter jenjang
        table: QTableWidget untuk display data
    
    Methods:
        init_ui(): Setup UI
        load_beasiswa_data(): Load data dari DB
        search_beasiswa(): Filter data berdasarkan search
        filter_by_status(): Filter by status
        refresh_table(): Update table display
        open_detail_dialog(): Show detail beasiswa
        add_to_favorit(): Add beasiswa ke favorit
    """
    
    def __init__(self, user_id: int, parent=None):
        super().__init__(parent)
        self.user_id = user_id
        self.beasiswa_data: List[Dict[str, Any]] = []
        self.init_ui()
        self.load_beasiswa_data()
    
    def load_beasiswa_data(self):
        """Load beasiswa dari database."""
        try:
            # Call CRUD function
            self.beasiswa_data = get_beasiswa_list(self.user_id)
            self.refresh_table()
        except Exception as e:
            logger.error(f"Error loading beasiswa: {e}")
            QMessageBox.critical(self, "Error", f"Failed to load data: {e}")
    
    def search_beasiswa(self, search_text: str):
        """Filter beasiswa by nama, dengan case-insensitive search."""
        filtered = [
            b for b in self.beasiswa_data
            if search_text.lower() in b['nama'].lower()
        ]
        self.display_in_table(filtered)
    
    def refresh_table(self):
        """Refresh table display dengan latest data."""
        self.display_in_table(self.beasiswa_data)
    
    def display_in_table(self, data: List[Dict]):
        """Populate table dengan beasiswa data."""
        self.table.setRowCount(len(data))
        
        for row, beasiswa in enumerate(data):
            # Create table items
            self.table.setItem(row, 0, QTableWidgetItem(beasiswa['nama']))
            self.table.setItem(row, 1, QTableWidgetItem(beasiswa['penyelenggara']))
            # ... more columns
```

**Keuntungan Class-based approach:**
- **State Management:** Data (beasiswa_data) tersimpan dalam class
- **Encapsulation:** UI logic terpisah dari business logic
- **Reusability:** Class dapat di-inherit untuk custom functionality
- **Organization:** Data dan method terkait dalam satu tempat

---

## 3. Penggunaan Struktur Data (List, Dictionary, Tuple)

### Konsep: Struktur Data untuk Penyimpanan Data

BeasiswaKu menggunakan berbagai struktur data untuk menyimpan dan mengelola data dengan efisien.

### A. **List** - Penyimpanan Data Terurut
```python
# Load semua beasiswa sebagai list
beasiswa_data: List[Dict[str, Any]] = get_beasiswa_list(user_id)
# Result: [
#   {'id': 1, 'nama': 'Beasiswa A', 'status': 'Buka', ...},
#   {'id': 2, 'nama': 'Beasiswa B', 'status': 'Tutup', ...},
#   ...
# ]

# Filter beasiswa dengan list comprehension
filtered = [
    b for b in beasiswa_data
    if b['status'] == 'Buka'  # Hanya beasiswa yang masih buka
]

# Count beasiswa by status
from collections import Counter
status_counts = Counter([b['status'] for b in beasiswa_data])
# Result: {'Buka': 45, 'Segera Tutup': 20, 'Tutup': 35}

# Sorting data
sorted_beasiswa = sorted(beasiswa_data, key=lambda b: b['deadline'])
# Sort by deadline terdekat
```

**Use Cases:**
- Menyimpan list beasiswa dari database
- Menyimpan list lamaran user
- Menyimpan search results
- Iterating data untuk display di table

### B. **Dictionary** - Penyimpanan Key-Value Pairs
```python
# Single beasiswa record
beasiswa = {
    'id': 1,
    'nama': 'Beasiswa Unggulan',
    'penyelenggara': 'Kemendikbud',
    'jenjang': 'S1',
    'status': 'Buka',
    'deadline': '2024-06-30',
    'deskripsi': '...',
    'persyaratan': ['IPK >= 3.0', 'Surat rekomendasi', ...],
    'benefit': 'Uang tunai + asuransi',
    'contact_email': 'info@kemendikbud.go.id'
}

# User profile
user_profile = {
    'id': 1,
    'username': 'kyla',
    'email': 'kyla@example.com',
    'nama_lengkap': 'Kyla Aurellio',
    'jenjang': 'S1',
    'ipk': 3.85,
    'universitas': 'ITB',
    'telepon': '081234567890'
}

# Statistics dict
stats = {
    'total_beasiswa': 100,
    'beasiswa_buka': 45,
    'beasiswa_segera_tutup': 20,
    'beasiswa_tutup': 35,
    'lamaran_submitted': 15,
    'lamaran_accepted': 5,
    'lamaran_rejected': 3
}

# Color palette untuk chart
COLOR_PALETTE = {
    "Buka": "#2E7D32",
    "Segera Tutup": "#F9A825",
    "Tutup": "#C62828",
    "Pending": "#546E7A",
    "Submitted": "#1E88E5"
}

# Access values
status = beasiswa['status']  # Output: 'Buka'
if stats['beasiswa_buka'] > 40:
    print("Banyak beasiswa yang masih buka")

# Iterate over dict
for status, count in stats.items():
    print(f"{status}: {count}")

# Merging dicts (Python 3.9+)
merged_stats = {**stats, 'new_field': 'value'}
```

**Database as Dictionary:**
```python
# SQL query results dikonversi ke dict via sqlite3.Row
conn.row_factory = sqlite3.Row  # Return dict-like objects

cursor.execute("SELECT * FROM beasiswa WHERE id = ?", (1,))
beasiswa = cursor.fetchone()  # Returns sqlite3.Row (like dict)

# Convert to regular dict
beasiswa_dict = dict(beasiswa)
```

**Use Cases:**
- Menyimpan record dari database
- Mapping value ke color (STATUS → COLOR)
- Configuration dictionary
- JSON serialization untuk API

### C. **Tuple** - Data Immutable (Fixed)
```python
# Return multiple values dari function
def login_user(username: str, password: str) -> Tuple[bool, str, int]:
    """
    Return tuple: (success, message, user_id)
    """
    # ...
    return (True, "Login successful", 42)

# Usage
success, message, user_id = login_user("kyla", "password123")

# Function dari visualization
def create_bar_chart(...) -> Tuple[plt.Figure, plt.Axes]:
    """Return (figure, axes) untuk chart display."""
    fig, ax = plt.subplots()
    # ... create chart
    return fig, ax

# Color tuple
def determine_status_color(status: str) -> Tuple[str, str]:
    """Return (text_color, background_color)."""
    if status == 'Buka':
        return ("#2E7D32", "#E8F5E9")
    # ...

# Coordinate tuple
point = (100, 50)  # (x, y) untuk GUI positioning
size = (400, 300)  # (width, height)

# Unpacking tuple
x, y = point
width, height = size

# Tuple sebagai key dalam dict (immutable)
button_styles = {
    ('navy', 'solid'): "...",
    ('orange', 'outline'): "..."
}
```

**Use Cases:**
- Return multiple values dari function
- Fixed collections (x, y coordinates)
- Dictionary keys (karena immutable)
- Function signatures


### D. **Kombinasi Struktur Data**
```python
# Complex nested structure dari database
lamaran_data = [
    {
        'id': 1,
        'beasiswa_id': 5,
        'beasiswa_nama': 'Beasiswa A',
        'status': 'Submitted',
        'tanggal_apply': '2024-05-15',
        'dokumen': ('CV.pdf', 'Surat.pdf', 'IPK.pdf'),  # Tuple of docs
        'notes': {
            'reviewer': 'Admin',
            'feedback': 'Menunggu verifikasi',
            'rating': 4
        }
    },
    # ... more lamaran
]

# Process nested data
for lamaran in lamaran_data:
    beasiswa_name = lamaran['beasiswa_nama']  # Access dict
    status = lamaran['status']
    docs = lamaran['dokumen']  # Tuple
    reviewer_notes = lamaran['notes']  # Dict
    feedback = reviewer_notes['feedback']
```

---

## 4. File Handling (Membaca & Menulis File)

### Konsep: File I/O untuk Persistensi Data & Export

BeasiswaKu menggunakan file handling untuk database, configuration, dan export data.

### A. **Database File Handling** (src/core/config.py & database.py)
```python
# Configuration file path
class Config:
    BASE_DIR = Path(__file__).resolve().parent.parent.parent
    DATABASE_PATH = BASE_DIR / "database" / "beasiswaku.db"
    LOG_DIR = BASE_DIR / "logs"

# Create directory jika tidak ada
db_path = Path(Config.DATABASE_PATH)
db_path.parent.mkdir(parents=True, exist_ok=True)

# Connect ke database file
conn = sqlite3.connect(str(db_path), timeout=10)

# Create tables dan write schema ke database
def init_schema():
    cursor = conn.cursor()
    
    # DROP & CREATE untuk reset
    cursor.execute("DROP TABLE IF EXISTS beasiswa")
    
    # CREATE dengan schema
    cursor.execute("""
        CREATE TABLE beasiswa (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nama TEXT NOT NULL,
            penyelenggara_id INTEGER,
            jenjang TEXT,
            status TEXT,
            deadline DATE,
            ...
        )
    """)
    
    conn.commit()

# Insert data (write ke database)
def insert_beasiswa(data: Dict) -> int:
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO beasiswa (nama, penyelenggara_id, jenjang, status)
        VALUES (?, ?, ?, ?)
    """, (data['nama'], data['penyelenggara_id'], data['jenjang'], data['status']))
    conn.commit()
    return cursor.lastrowid

# Read dari database
def read_beasiswa(beasiswa_id: int) -> Dict:
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM beasiswa WHERE id = ?", (beasiswa_id,))
    row = cursor.fetchone()
    return dict(row) if row else None
```

### B. **CSV Export** (src/gui/gui_beasiswa.py)
```python
def export_to_csv(self):
    """Export beasiswa table ke CSV file."""
    # Open file dialog untuk pilih lokasi save
    file_path, _ = QFileDialog.getSaveFileName(
        self,
        "Export Beasiswa",
        "",
        "CSV Files (*.csv);;All Files (*)"
    )
    
    if not file_path:
        return  # User cancel
    
    try:
        # Buka file untuk writing
        with open(file_path, 'w', newline='', encoding='utf-8') as csvfile:
            # Create CSV writer
            fieldnames = ['ID', 'Nama', 'Penyelenggara', 'Jenjang', 'Status', 'Deadline']
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            
            # Write header
            writer.writeheader()
            
            # Write data rows
            for beasiswa in self.beasiswa_data:
                writer.writerow({
                    'ID': beasiswa['id'],
                    'Nama': beasiswa['nama'],
                    'Penyelenggara': beasiswa['penyelenggara'],
                    'Jenjang': beasiswa['jenjang'],
                    'Status': beasiswa['status'],
                    'Deadline': beasiswa['deadline']
                })
        
        # Success message
        QMessageBox.information(self, "Success", f"Data exported to {file_path}")
        
    except Exception as e:
        logger.error(f"Export error: {e}")
        QMessageBox.critical(self, "Error", f"Failed to export: {e}")
```

### C. **Logging File** (main.py)
```python
# Setup logging ke file
import logging
from pathlib import Path

LOG_DIR = Path("logs")
LOG_DIR.mkdir(exist_ok=True)

# Configure file handler
file_handler = logging.FileHandler(LOG_DIR / "beasiswaku.log")
file_handler.setLevel(logging.DEBUG)

# Configure console handler
console_handler = logging.StreamHandler()
console_handler.setLevel(logging.INFO)

# Create logger
logger = logging.getLogger(__name__)
logger.addHandler(file_handler)
logger.addHandler(console_handler)

# Write log messages
logger.info(f"Application started at {datetime.now()}")
logger.error(f"Database connection failed: {error_msg}")
logger.debug(f"User {user_id} logged in")
```

### D. **Configuration File Handling**
```python
# Config sebagai Python file (src/core/config.py)
from pathlib import Path

class Config:
    """Application configuration."""
    
    # Paths
    BASE_DIR = Path(__file__).resolve().parent.parent.parent
    DATABASE_PATH = BASE_DIR / "database" / "beasiswaku.db"
    LOG_DIR = BASE_DIR / "logs"
    
    # Database
    DATABASE_TIMEOUT = 10
    DATABASE_CHECK_SAME_THREAD = False
    
    # GUI
    WINDOW_WIDTH = 1280
    WINDOW_HEIGHT = 800
    WINDOW_TITLE = "BeasiswaKu - Personal Scholarship Manager"
    
    # Colors
    PRIMARY_COLOR = "#1e3a8a"  # Navy
    ACCENT_COLOR = "#f59e0b"   # Orange

# Usage
from src.core.config import Config
db_path = Config.DATABASE_PATH
window_title = Config.WINDOW_TITLE
```

### E. **JSON untuk Preference Storage** (Alternative)
```python
import json

def save_user_preferences(user_id: int, preferences: Dict):
    """Save user preferences ke JSON file."""
    pref_file = Path(f"data/user_{user_id}_prefs.json")
    pref_file.parent.mkdir(parents=True, exist_ok=True)
    
    # Write dict ke JSON
    with open(pref_file, 'w') as f:
        json.dump(preferences, f, indent=4)

def load_user_preferences(user_id: int) -> Dict:
    """Load user preferences dari JSON file."""
    pref_file = Path(f"data/user_{user_id}_prefs.json")
    
    if not pref_file.exists():
        return {}  # Default preferences
    
    # Read JSON
    with open(pref_file, 'r') as f:
        preferences = json.load(f)
    
    return preferences

# Usage
prefs = {
    'theme': 'dark',
    'language': 'id',
    'notifications': True,
    'items_per_page': 20
}
save_user_preferences(42, prefs)

loaded_prefs = load_user_preferences(42)
```

**File Handling Use Cases:**
- Database persistence (SQLite file)
- Export data (CSV)
- Logging (log files)
- Configuration (config files)
- User preferences (JSON)

---

## 5. Visualisasi & Chart

### A. **Matplotlib Chart Functions** (src/visualization/visualisasi.py)

#### 1. Bar Chart - Beasiswa per Jenjang
```python
def create_bar_chart_beasiswa_per_jenjang(
    data: Dict[str, int],
    title: str = "Jumlah Beasiswa per Jenjang"
) -> Tuple[plt.Figure, plt.Axes]:
    """
    Buat bar chart untuk jumlah beasiswa per jenjang (S1, S2, S3, dll).
    
    Data input:
        {'S1': 45, 'S2': 25, 'S3': 30}
    
    Output:
        Bar chart dengan navy color
    """
    fig, ax = plt.subplots(figsize=(10, 6))
    
    if not data:
        _render_empty_state(ax, title)
        return fig, ax
    
    # Extract jenjang & counts
    jenjang = list(data.keys())    # ['S1', 'S2', 'S3']
    counts = list(data.values())   # [45, 25, 30]
    
    # Create bars
    bars = ax.bar(
        jenjang, 
        counts, 
        color="#1E88E5",           # Navy blue
        edgecolor="white",         # White border
        linewidth=1.5
    )
    
    # Add value labels on bars
    for bar in bars:
        height = bar.get_height()
        ax.text(
            bar.get_x() + bar.get_width()/2.,
            height,
            f'{int(height)}',
            ha='center', va='bottom',
            fontweight='bold', fontsize=10
        )
    
    # Styling
    _apply_axis_style(ax)  # Apply common styling
    ax.set_ylabel("Jumlah Beasiswa", fontsize=11, fontweight="bold")
    ax.yaxis.set_major_locator(MaxNLocator(integer=True))
    
    plt.tight_layout()
    return fig, ax
```

#### 2. Donut Chart - Status Beasiswa
```python
def create_donut_chart_status(
    data: Dict[str, int],
    title: str = "Status Beasiswa"
) -> Tuple[plt.Figure, plt.Axes]:
    """
    Buat donut chart untuk distribusi status beasiswa.
    
    Data input:
        {'Buka': 45, 'Segera Tutup': 20, 'Tutup': 35}
    
    Output:
        Donut chart dengan color legend
    """
    fig, ax = plt.subplots(figsize=(8, 6))
    
    if not data:
        _render_empty_state(ax, title)
        return fig, ax
    
    # Extract labels & sizes
    labels = list(data.keys())      # ['Buka', 'Segera Tutup', 'Tutup']
    sizes = list(data.values())     # [45, 20, 35]
    
    # Map status ke warna
    colors = [
        COLOR_PALETTE.get(label, "#cccccc")
        for label in labels
    ]
    # Result: ['#2E7D32' (green), '#F9A825' (orange), '#C62828' (red)]
    
    # Create pie chart
    wedges, texts, autotexts = ax.pie(
        sizes,
        labels=labels,
        colors=colors,
        autopct='%1.1f%%',      # Show percentage
        startangle=90,
        textprops={'fontsize': 10, 'weight': 'bold'}
    )
    
    # Create white center circle untuk donut effect
    centre_circle = plt.Circle((0, 0), 0.70, fc='white')
    ax.add_artist(centre_circle)
    
    # Make percentage text white for visibility
    for autotext in autotexts:
        autotext.set_color('white')
        autotext.set_fontweight('bold')
    
    return fig, ax
```

#### 3. Horizontal Bar Chart - Top Penyelenggara
```python
def create_horizontal_bar_chart_top_penyelenggara(
    data: Dict[str, int],
    title: str = "Top 10 Penyelenggara"
) -> Tuple[plt.Figure, plt.Axes]:
    """
    Buat horizontal bar chart untuk top penyelenggara.
    
    Data input:
        {'Kemendikbud': 50, 'Mandiri': 30, 'BCA': 25, ...}
    
    Output:
        Horizontal bar chart (lebih readable untuk banyak label)
    """
    fig, ax = plt.subplots(figsize=(10, 8))
    
    if not data:
        _render_empty_state(ax, title)
        return fig, ax
    
    # Extract & sort data
    penyelenggara = list(data.keys())
    counts = list(data.values())
    
    # Create horizontal bars
    bars = ax.barh(
        penyelenggara,
        counts,
        color="#26A69A",        # Teal color
        edgecolor="white",
        linewidth=1.5
    )
    
    # Add value labels
    for i, (bar, count) in enumerate(zip(bars, counts)):
        ax.text(
            count,
            bar.get_y() + bar.get_height()/2.,
            f' {int(count)}',
            ha='left', va='center',
            fontweight='bold', fontsize=9
        )
    
    # Styling
    ax.set_xlabel("Jumlah Beasiswa", fontsize=11, fontweight="bold")
    ax.grid(axis='x', linestyle='--', alpha=0.35)
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    
    plt.tight_layout()
    return fig, ax
```

### B. **Integration ke PyQt6 GUI**

#### Displaying Chart di Tab (src/gui/tab_statistik.py)
```python
from src.visualization.visualisasi import (
    create_bar_chart_beasiswa_per_jenjang,
    create_donut_chart_status,
    create_horizontal_bar_chart_top_penyelenggara
)
from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg as FigureCanvas

class StatistikTab(QWidget):
    """Tab untuk menampilkan statistik & chart."""
    
    def __init__(self, user_id: int, parent=None):
        super().__init__(parent)
        self.user_id = user_id
        self.init_ui()
    
    def init_ui(self):
        """Setup UI dengan chart."""
        main_layout = QVBoxLayout(self)
        
        # Chart 1: Beasiswa per Jenjang
        data_jenjang = get_beasiswa_per_jenjang()
        fig_bar, ax_bar = create_bar_chart_beasiswa_per_jenjang(data_jenjang)
        canvas_bar = FigureCanvas(fig_bar)
        canvas_bar.setMinimumHeight(300)
        main_layout.addWidget(canvas_bar)
        
        # Chart 2: Status Distribution
        data_status = get_status_availability()
        fig_donut, ax_donut = create_donut_chart_status(data_status)
        canvas_donut = FigureCanvas(fig_donut)
        canvas_donut.setMinimumHeight(300)
        main_layout.addWidget(canvas_donut)
        
        # Chart 3: Top Penyelenggara
        data_penyelenggara = get_top_penyelenggara()
        fig_horiz, ax_horiz = create_horizontal_bar_chart_top_penyelenggara(data_penyelenggara)
        canvas_horiz = FigureCanvas(fig_horiz)
        canvas_horiz.setMinimumHeight(350)
        main_layout.addWidget(canvas_horiz)
    
    def refresh_charts(self):
        """Refresh semua chart dengan latest data."""
        # Clear layout
        while self.main_layout.count():
            self.main_layout.takeAt(0).widget().deleteLater()
        
        # Rebuild dengan data baru
        self.init_ui()
```

### C. **Data Flow untuk Chart**
```
Database (SQLite)
    ↓
    └─→ CRUD Functions (get_beasiswa_per_jenjang, dll)
        ↓
        └─→ Data: Dict[str, int]
            ↓
            └─→ Visualization Functions (create_*_chart)
                ↓
                └─→ Figure, Axes (matplotlib objects)
                    ↓
                    └─→ FigureCanvas (PyQt6)
                        ↓
                        └─→ Displayed in Tab UI
```

**Chart Types dalam BeasiswaKu:**
1. **Bar Chart** - Beasiswa by Jenjang (S1, S2, S3)
2. **Donut/Pie Chart** - Status distribution (Buka, Tutup, Segera Tutup)
3. **Horizontal Bar** - Top Penyelenggara
4. **Line Chart** (Optional) - Lamaran trends over time

---

## 6. Keterkaitan Konsep dengan Fitur

### Fitur: "Daftar Beasiswa" (BeasiswaTab)

```
┌─────────────────────────────────────────────────────────────┐
│ FITUR: DAFTAR & CARI BEASISWA                               │
│ (Menampilkan semua beasiswa dengan search & filter)          │
└─────────────────────────────────────────────────────────────┘

1. STRUKTUR DATA (List, Dict)
   └─→ beasiswa_data: List[Dict] = get_beasiswa_list()
       [{
           'id': 1,
           'nama': 'Beasiswa Unggulan',
           'penyelenggara': 'Kemendikbud',
           'jenjang': 'S1',
           'status': 'Buka',
           'deadline': '2024-06-30'
       }, ...]

2. FUNGSI MODULAR (get_beasiswa_list, search, filter)
   └─→ def get_beasiswa_list(user_id: int) -> List[Dict]
   └─→ def search_beasiswa(search_text: str)
   └─→ def filter_by_status(status: str)
   └─→ def refresh_table()

3. CLASS (BeasiswaTab)
   └─→ class BeasiswaTab(QWidget):
       ├─ Attributes: user_id, beasiswa_data, search_input, table
       ├─ Methods: init_ui(), load_data(), search(), filter(), refresh()
       └─ Signals: data_updated, search_completed

4. DATABASE FILE HANDLING
   └─→ CRUD operations from database/beasiswaku.db
       ├─ Read: SELECT * FROM beasiswa
       ├─ Create: INSERT INTO beasiswa (via dialog)
       ├─ Update: UPDATE beasiswa SET ... (via dialog)
       └─ Delete: DELETE FROM beasiswa (via confirmation)

5. VISUALIZATION (Optional: Chart)
   └─→ Statistics di tab statistik
       ├─ Beasiswa per jenjang (Bar chart)
       ├─ Status distribution (Donut chart)
       └─ Top penyelenggara (Horizontal bar chart)
```

### Fitur: "Login & Register"

```
┌─────────────────────────────────────────────────────────────┐
│ FITUR: AUTENTIKASI (Login & Register)                       │
│ (User login/register untuk akses aplikasi)                  │
└─────────────────────────────────────────────────────────────┘

1. STRUKTUR DATA (Dict, Tuple)
   └─→ User dict: {'id': 1, 'username': 'kyla', 'email': '...'}
   └─→ Return tuple: (success: bool, message: str, user_id: int)

2. FUNGSI MODULAR (login_user, register_user, hash_password)
   └─→ def login_user(username, password) -> Tuple[bool, str, int]
   └─→ def register_user(username, email, password) -> Tuple[bool, str]
   └─→ def hash_password(password) -> str (security)
   └─→ def verify_password(password, hash) -> bool

3. CLASS (LoginWindow)
   └─→ class LoginWindow(QDialog):
       ├─ Attributes: username_input, password_input, current_user_id
       ├─ Methods: init_ui(), handle_login(), handle_register()
       ├─ Signals: login_success(user_id, username)
       └─ Validation: Check empty fields, user exists, password match

4. DATABASE FILE HANDLING
   └─→ Read from database/beasiswaku.db
       ├─ Check user exists: SELECT * FROM akun WHERE username = ?
       ├─ Write new user: INSERT INTO akun (username, email, password_hash)
       └─ Retrieve user data after login

5. LOGGING (File handling)
   └─→ Log successful/failed login attempts
       └─→ logger.info(f"User {username} logged in successfully")
       └─→ logger.warning(f"Failed login attempt for {username}")
```

### Fitur: "Dashboard Statistik"

```
┌─────────────────────────────────────────────────────────────┐
│ FITUR: STATISTIK & CHART                                    │
│ (Visualisasi data beasiswa & lamaran)                       │
└─────────────────────────────────────────────────────────────┘

1. STRUKTUR DATA (Dict - untuk mapping)
   └─→ Beasiswa per jenjang: {'S1': 45, 'S2': 25, 'S3': 30}
   └─→ Status distribution: {'Buka': 45, 'Tutup': 35, 'Segera Tutup': 20}
   └─→ Color mapping: {'Buka': '#2E7D32', 'Tutup': '#C62828', ...}

2. FUNGSI MODULAR (Chart functions)
   └─→ def create_bar_chart_beasiswa_per_jenjang(data) -> Tuple[Figure, Axes]
   └─→ def create_donut_chart_status(data) -> Tuple[Figure, Axes]
   └─→ def create_horizontal_bar_chart_top_penyelenggara(data) -> Tuple[Figure, Axes]
   └─→ def _apply_axis_style(ax) -> None (Helper function)

3. CLASS (StatistikTab)
   └─→ class StatistikTab(QWidget):
       ├─ Attributes: user_id, canvas_bar, canvas_donut, canvas_horiz
       ├─ Methods: init_ui(), refresh_charts(), load_statistics()
       └─ Integration: FigureCanvas dari matplotlib

4. DATABASE FILE HANDLING
   └─→ Read from database/beasiswaku.db
       ├─ Get beasiswa by jenjang: SELECT jenjang, COUNT(*) FROM beasiswa
       ├─ Get status distribution: SELECT status, COUNT(*) FROM beasiswa
       ├─ Get top penyelenggara: SELECT penyelenggara, COUNT(*) ORDER BY COUNT

5. VISUALIZATION (Core feature)
   └─→ 3 chart types
       ├─ Bar chart (numerical comparison)
       ├─ Donut chart (proportion visualization)
       └─ Horizontal bar chart (labeled data sorting)
   └─→ Matplotlib + PyQt6 Integration
       └─→ FigureCanvas untuk embed chart di GUI
```

---

## Summary: Konsep → Fitur → Code

| Konsep | Implementasi | Manfaat |
|--------|--------------|---------|
| **Fungsi (def)** | Modular CRUD, chart, styling helpers | Reusable, maintainable, testable |
| **Class** | LoginWindow, BeasiswaTab, DatabaseManager | Organization, encapsulation, OOP |
| **List** | beasiswa_data[], search results, filtering | Ordered collection, iteration |
| **Dictionary** | User profiles, config, color mapping, stats | Key-value storage, lookup efficiency |
| **Tuple** | Function returns, coordinates, immutable data | Multiple return values, unpacking |
| **File Handling** | Database, CSV export, logging, config | Persistence, data export, debugging |
| **Visualization** | Charts untuk statistik dashboard | Data analysis, user insight, analytics |

---

## Kesimpulan

BeasiswaKu adalah aplikasi yang comprehensive yang mengintegrasikan semua konsep programming penting:

1. ✅ **Fungsi** untuk code reusability & modularity
2. ✅ **Class/OOP** untuk organization & encapsulation
3. ✅ **Struktur Data** untuk efficient data management
4. ✅ **File Handling** untuk persistence & export
5. ✅ **Visualisasi** untuk data insights & analytics

Semua konsep ini bekerja bersama menciptakan aplikasi yang robust, maintainable, dan user-friendly.

---

**Created:** April 13, 2026  
**Last Updated:** April 13, 2026  
**Status:** ✅ Complete Documentation
