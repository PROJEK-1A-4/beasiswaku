# 🎯 PANDUAN LENGKAP - Konsep Programming & Fitur BeasiswaKu

**Project:** BeasiswaKu - Personal Scholarship Management Application  
**Purpose:** Dokumentasi komprehensif untuk pembelajaran konsep programming  
**Status:** ✅ Complete & Ready to Learn  

---

## 📋 STRUKTUR DOKUMENTASI

Dokumentasi ini terdiri dari 3 file utama:

1. **CONCEPT_DOCUMENTATION.md** 📚
   - Penjelasan mendalam untuk setiap konsep
   - Architecture & design patterns
   - Real-world examples dari kode BeasiswaKu
   - Visual diagrams (Mermaid)

2. **CODE_EXAMPLES.md** 💻
   - Contoh kode praktis yang langsung bisa digunakan
   - Copy-paste ready code snippets
   - Use cases & best practices
   - Quick reference

3. **PANDUAN_INI.md** (File ini) 🗺️
   - Navigasi & overview
   - Quick learning path
   - FAQ & troubleshooting
   - Tips & tricks

---

## 🚀 QUICK START (5 MENIT)

### Untuk pemula (mulai dari sini):
1. Baca **CONCEPT_DOCUMENTATION.md** → Bagian 1-3
2. Lihat CODE_EXAMPLES.md → Bagian 1-3
3. Jalankan aplikasi dan amati code flow

### Untuk intermediate:
1. Fokus pada **CONCEPT_DOCUMENTATION.md** → Bagian 4-5
2. Study FILE HANDLING & VISUALIZATION
3. Coba buat feature baru menggunakan pattern yang sama

### Untuk advanced:
1. Pelajari **CONCEPT_DOCUMENTATION.md** → Bagian 6 (Keterkaitan)
2. Refactor code untuk OOP yang lebih baik
3. Buat test cases & optimization

---

## 📚 KONSEP YANG DIPELAJARI

### 1. Fungsi (def) untuk Modularisasi
**Tujuan:** Membagi program menjadi bagian-bagian kecil yang reusable

**Key Points:**
- Satu fungsi = satu tanggung jawab (Single Responsibility Principle)
- Function signature yang jelas dengan type hints
- Docstring untuk dokumentasi otomatis
- Reuse di berbagai tempat tanpa duplikasi kode

**Di BeasiswaKu:**
```
Contoh: get_beasiswa_list(user_id) 
  → Query DB → Return List[Dict]
  → Digunakan di BeasiswaTab.load_beasiswa_data()
  → Digunakan di StatistikTab.refresh_statistics()
  → Code reuse!
```

**Belajar dari file:**
- CONCEPT_DOCUMENTATION.md → Bagian 1
- CODE_EXAMPLES.md → Bagian 1 (1A, 1B, 1C, 1D)

---

### 2. Class/Objek untuk Pengelompokan Data & Logika
**Tujuan:** Mengelompokkan data (attributes) & fungsi (methods) terkait dalam satu entity

**Key Points:**
- Encapsulation: Private data, public methods
- Inheritance: Kelas berganda, sharing behavior
- Polymorphism: Banyak form, satu interface
- Singleton pattern: Hanya 1 instance (DatabaseManager)

**Di BeasiswaKu:**
```
Contoh: BeasiswaTab Class
  Attributes: user_id, beasiswa_data, search_input
  Methods: load_beasiswa_data(), search_beasiswa(), refresh_table()
  
  → Semua logic untuk beasiswa tab ada di 1 class
  → Mudah maintain & test
```

**Belajar dari file:**
- CONCEPT_DOCUMENTATION.md → Bagian 2
- CODE_EXAMPLES.md → Bagian 2 (2A, 2B, 2C)

---

### 3. Struktur Data (List, Dict, Tuple)
**Tujuan:** Menyimpan & mengorganisir data dengan efisien

**Key Points:**
- **List:** Ordered collection, mutability, iteration
- **Dict:** Key-value pairs, lookup efficiency, mapping
- **Tuple:** Immutable, multiple returns, dict keys

**Di BeasiswaKu:**
```
Contoh: Data flow
  Dict  → beasiswa{'id': 1, 'nama': '...', 'status': '...'}
  List  → [beasiswa1, beasiswa2, ...] untuk display
  Tuple → (success, message, user_id) dari login_user()
```

**Belajar dari file:**
- CONCEPT_DOCUMENTATION.md → Bagian 3
- CODE_EXAMPLES.md → Bagian 3 (3A, 3B, 3C)

---

### 4. File Handling (File I/O)
**Tujuan:** Persistensi data & komunikasi dengan file system

**Key Points:**
- Database files (SQLite)
- CSV export untuk user
- Log files untuk debugging
- Configuration JSON

**Di BeasiswaKu:**
```
Contoh: File operations
  SQLite DB  → database/beasiswaku.db (persistensi data)
  CSV Export → Export beasiswa ke file (user feature)
  Log Files  → logs/*.log (debugging)
  Config JSON → Preferensi user (future)
```

**Belajar dari file:**
- CONCEPT_DOCUMENTATION.md → Bagian 4
- CODE_EXAMPLES.md → Bagian 4 (4A, 4B, 4C, 4D)

---

### 5. Visualisasi & Chart
**Tujuan:** Menampilkan data dalam bentuk visual (charts, graphs)

**Key Points:**
- Matplotlib untuk chart generation
- PyQt6 FigureCanvas untuk embedding
- Multiple chart types (bar, donut, line)
- Empty state handling

**Di BeasiswaKu:**
```
Contoh: Charts
  Bar Chart  → Beasiswa per jenjang (S1, S2, S3)
  Donut Chart → Status distribution (Buka, Tutup, Segera Tutup)
  Horizontal → Top penyelenggara

  Pipeline: DB → Dict → Chart Function → matplotlib → PyQt6
```

**Belajar dari file:**
- CONCEPT_DOCUMENTATION.md → Bagian 5
- CODE_EXAMPLES.md → Bagian 5 (5A, 5B, 5C)

---

### 6. Keterkaitan Konsep dengan Fitur
**Tujuan:** Memahami bagaimana konsep bekerja bersama dalam satu fitur

**Contoh Fitur: "Daftar Beasiswa"**
```
Database File ──[File Handling]──→ CRUD Functions
                                        ↓
Data (List, Dict) ──[Struktur Data]──→ BeasiswaTab Class
                                        ↓
UI Logic ──[Class & Methods]──→ Display in Table
                                        ↓
User sees beasiswa list & can search
```

**Belajar dari file:**
- CONCEPT_DOCUMENTATION.md → Bagian 6 (Fitur examples)

---

## 🎓 CARA BELAJAR YANG EFEKTIF

### Step 1: Pahami Konsep (Theory)
```
Read CONCEPT_DOCUMENTATION.md
↓
Pahami penjelasan, diagram, & analisis
↓
Catat poin-poin penting
```

### Step 2: Lihat Contoh Kode (Practice)
```
Read CODE_EXAMPLES.md
↓
Copy code examples
↓
Modify & eksperimen
```

### Step 3: Analisis Kode Asli (Implementation)
```
Buka file sumber di repository
  src/gui/gui_beasiswa.py
  src/database/crud.py
  src/visualization/visualisasi.py
↓
Identifikasi konsep yang digunakan
↓
Bandingkan dengan examples
```

### Step 4: Implementasi Fitur Baru (Application)
```
Gunakan pattern yang sudah dipelajari
↓
Buat fitur baru atau fix bugs
↓
Test & validate
```

### Step 5: Refactor & Optimize (Mastery)
```
Review code untuk improvement
↓
Apply best practices
↓
Documentation & testing
```

---

## 📊 PETA KODE DAN RELASI

### File Organization & Konsep yang Digunakan

```
src/
├── core/
│   ├── config.py
│   │   └─ [Struktur Data: Dict untuk CONFIG]
│   │   └─ [File Handling: Path management]
│   │
│   └── database.py
│       └─ [Class: DatabaseManager (Singleton)]
│       └─ [File Handling: SQLite file operations]
│       └─ [Struktur Data: Dict conversion dari SQL]
│
├── database/
│   └── crud.py
│       └─ [Fungsi: get_*, insert_*, update_*, delete_*]
│       └─ [Struktur Data: List[Dict] returns]
│       └─ [Tuple: (bool, str, int) return values]
│
├── gui/
│   ├── design_tokens.py
│   │   └─ [Struktur Data: Dict untuk COLOR_PALETTE]
│   │
│   ├── styles.py
│   │   └─ [Fungsi: get_*_stylesheet() helpers]
│   │
│   ├── components.py
│   │   └─ [Class: AlertBanner, StatusBadge]
│   │
│   ├── gui_beasiswa.py
│   │   └─ [Class: BeasiswaTab - Main feature]
│   │   └─ [Struktur Data: beasiswa_data List[Dict]]
│   │   └─ [File Handling: CSV export]
│   │
│   ├── tab_beranda.py, tab_statistik.py, dll
│   │   └─ [Class: BerandaTab, StatistikTab, etc]
│   │
│   └── sidebar.py
│       └─ [Class: Sidebar - Navigation]
│
├── visualization/
│   └── visualisasi.py
│       └─ [Fungsi: create_*_chart() functions]
│       └─ [Struktur Data: Dict untuk chart data]
│       └─ [Chart: Matplotlib integration]
│
└── main.py
    └─ [Class: LoginWindow, MainWindow]
    └─ [File Handling: Database initialization]
```

### Data Flow Example: "User Search Beasiswa"

```
User Input (Search keyword)
        ↓
BeasiswaTab.search_beasiswa() [Method - Class]
        ↓
List comprehension [Struktur Data - Filter]
        ↓
Filtered List[Dict] [Struktur Data - Result]
        ↓
BeasiswaTab.display_in_table() [Method - Class]
        ↓
QTableWidget updated [GUI Display]
        ↓
User sees filtered results
```

---

## ❓ FAQ & TROUBLESHOOTING

### Q1: Bagaimana cara membuat fitur baru?

**A:** Ikuti pattern yang sudah ada:

1. **CRUD Function** (src/database/crud.py)
   ```python
   def get_my_feature(user_id: int) -> List[Dict]:
       # Query database
       # Return data
   ```

2. **Tab Class** (src/gui/tab_myfeature.py)
   ```python
   class MyFeatureTab(QWidget):
       def __init__(self, user_id):
           self.user_id = user_id
           self.init_ui()
       
       def init_ui(self):
           # Setup UI
       
       def load_data(self):
           # Load dari CRUD function
   ```

3. **Add to MainWindow** (main.py)
   ```python
   my_tab = MyFeatureTab(user_id)
   tabs.addTab(my_tab, "My Feature")
   ```

---

### Q2: Bagaimana cara menambah chart baru?

**A:** Gunakan pattern dari src/visualization/visualisasi.py:

```python
def create_my_chart(data: Dict) -> Tuple[plt.Figure, plt.Axes]:
    fig, ax = plt.subplots()
    # Create chart
    _apply_axis_style(ax)  # Use helper
    return fig, ax

# Di Tab:
fig, ax = create_my_chart(data)
canvas = FigureCanvas(fig)
layout.addWidget(canvas)
```

---

### Q3: Database error saat query?

**A:** Check:
1. SQL syntax correctness
2. Parameter tuple length matches ?
3. Table exists dan column names benar
4. User_id validation
5. Connection open & tidak closed

```python
# ❌ Wrong
cursor.execute("SELECT * FROM beasiswa WHERE id = ?", id)

# ✅ Correct
cursor.execute("SELECT * FROM beasiswa WHERE id = ?", (id,))
```

---

### Q4: Chart tidak muncul di UI?

**A:** Check:
1. Data tidak kosong (handle empty state)
2. FigureCanvas properly attached ke layout
3. Matplotlib backend compatible dengan PyQt6
4. Error handling di try-except

---

## 💡 BEST PRACTICES

### 1. Type Hints Selalu
```python
# ❌ Bad
def get_data():
    return data

# ✅ Good
def get_data(user_id: int) -> List[Dict[str, Any]]:
    return data
```

### 2. Function Documentation
```python
# ❌ Bad
def search(text):
    ...

# ✅ Good
def search_beasiswa(search_text: str) -> List[Dict]:
    """
    Search beasiswa by name.
    
    Args:
        search_text: Search keyword (case-insensitive)
    
    Returns:
        List of matching beasiswa dictionaries
    """
    ...
```

### 3. Error Handling
```python
# ❌ Bad
def load_data():
    data = get_beasiswa_list()
    return data

# ✅ Good
def load_data(self):
    try:
        self.data = get_beasiswa_list(self.user_id)
        self.refresh_table()
    except Exception as e:
        logger.error(f"Error loading data: {e}")
        QMessageBox.critical(self, "Error", f"Failed to load: {e}")
```

### 4. Code Organization
```
# ❌ One file dengan 2000+ lines

# ✅ Separate files
gui_beasiswa.py      (500+ lines)
tab_beranda.py       (300+ lines)
tab_statistik.py     (300+ lines)
design_tokens.py     (150+ lines)
styles.py            (200+ lines)
```

### 5. DRY Principle (Don't Repeat Yourself)
```python
# ❌ Repetitive styling
button1.setStyleSheet("background: #1e3a8a; color: white; ...")
button2.setStyleSheet("background: #1e3a8a; color: white; ...")

# ✅ Reusable function
stylesheet = get_button_solid_stylesheet("#1e3a8a")
button1.setStyleSheet(stylesheet)
button2.setStyleSheet(stylesheet)
```

---

## 🔧 Tools & Debugging

### Logging untuk debugging
```python
import logging

logger = logging.getLogger(__name__)

# Di code
logger.debug("Variable value: " + str(value))
logger.info("Operation completed")
logger.warning("Potential issue detected")
logger.error("Operation failed: " + str(error))

# Check logs di: logs/*.log
```

### Database inspection
```python
# Di Python REPL
from src.database.crud import get_connection

conn = get_connection()
cursor = conn.cursor()

# Check data
cursor.execute("SELECT COUNT(*) FROM beasiswa")
count = cursor.fetchone()[0]
print(f"Total beasiswa: {count}")

# Check schema
cursor.execute("PRAGMA table_info(beasiswa)")
columns = cursor.fetchall()
for col in columns:
    print(col)
```

### GUI debugging
```python
# Add debug labels
debug_label = QLabel(f"Loaded: {len(data)} items")
layout.addWidget(debug_label)

# Or use print
print(f"Data: {self.data}")

# Or use PyQt debugger
import pdb; pdb.set_trace()
```

---

## 📈 PROGRESS CHECKLIST

Gunakan checklist ini untuk track progress pembelajaran:

### Basic Understanding
- [ ] Pahami 5 konsep utama 
- [ ] Bisa identifikasi konsep di kode
- [ ] Bisa explain kepada orang lain

### Practical Skills
- [ ] Bisa write function dengan type hints
- [ ] Bisa define class dengan proper structure
- [ ] Bisa manipulate List, Dict, Tuple
- [ ] Bisa query database dengan CRUD

### Advanced Skills
- [ ] Bisa create fitur baru lengkap
- [ ] Bisa refactor code untuk improvement
- [ ] Bisa debug complex issues
- [ ] Bisa optimize performance

### Mastery
- [ ] Bisa review code & provide feedback
- [ ] Bisa mentor orang lain
- [ ] Bisa design architecture untuk project baru
- [ ] Bisa apply design patterns

---

## 📚 NEXT STEPS

Setelah menyelesaikan dokumentasi ini:

1. **Design Patterns** (Advanced)
   - Singleton, Factory, Observer pattern
   - MVC, MVVM architecture
   - Repository pattern

2. **Testing** (Important)
   - Unit tests dengan pytest
   - Integration tests
   - UI testing

3. **Performance** (Optimization)
   - Database indexing
   - Query optimization
   - Caching strategies

4. **Deployment** (Real-world)
   - Docker containerization
   - CI/CD pipeline
   - Production deployment

---

## 📞 RESOURCES

### Internal Documentation
- 📖 CONCEPT_DOCUMENTATION.md - Penjelasan mendalam
- 💻 CODE_EXAMPLES.md - Contoh kode praktis
- 📊 Architecture diagrams - Visual reference

### External Resources
- 📘 Python official docs: https://docs.python.org
- 📗 PyQt6 documentation: https://www.riverbankcomputing.com/static/Docs/PyQt6
- 📙 SQLite docs: https://www.sqlite.org/docs.html
- 📕 Matplotlib guide: https://matplotlib.org

---

## ✅ CHECKLIST SELESAI DOKUMENTASI

- [x] CONCEPT_DOCUMENTATION.md (6 sections, 150+ KB)
- [x] CODE_EXAMPLES.md (5 sections, 120+ KB)
- [x] PANDUAN_INI.md (10+ KB)
- [x] 5 Mermaid diagrams untuk visualization
- [x] Quick start guide
- [x] FAQ & troubleshooting
- [x] Best practices
- [x] Progress checklist
- [x] Resources & next steps

---

## 🎉 SELAMAT!

Anda sekarang memiliki dokumentasi lengkap untuk memahami:

1. ✅ **Fungsi (def)** untuk code modularization
2. ✅ **Class/Objek** untuk OOP design
3. ✅ **Struktur Data** untuk data management
4. ✅ **File Handling** untuk persistence
5. ✅ **Visualisasi** untuk analytics & charts
6. ✅ **Keterkaitan** konsep dalam real features

**Total Content:**
- 3 markdown files dengan 270+ KB dokumentasi
- 50+ code examples yang ready to use
- 5 architecture diagrams
- Lengkap dengan FAQ, tips, & troubleshooting

---

**Created:** April 13, 2026  
**Last Updated:** April 13, 2026  
**Status:** ✅ COMPLETE & READY TO LEARN

---

### Pertanyaan? Lihat file dokumentasi yang sesuai:
- Konsep theory → **CONCEPT_DOCUMENTATION.md**
- Code examples → **CODE_EXAMPLES.md**
- Bingung? → **FAQ section di file ini**

Selamat belajar! 🚀
