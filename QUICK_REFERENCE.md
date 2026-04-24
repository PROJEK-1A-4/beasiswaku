# ⚡ QUICK REFERENCE - Konsep Programming BeasiswaKu

**Cheat sheet untuk quick lookup** - Cari konsep yang Anda butuhkan dan langsung ke contoh kode.

---

## 🎯 KONSEP QUICK LOOKUP

### Konsep 1️⃣: FUNGSI (def)

| Aspek | Penjelasan | Contoh |
|-------|-----------|--------|
| **Definisi** | Blok kode reusable dengan input & output | `def get_beasiswa(user_id) -> List[Dict]` |
| **Manfaat** | Code reuse, modularisasi, testing | Tidak perlu copy-paste kode |
| **Signature** | `def nama(param: Type) -> ReturnType:` | `def login(username: str, pwd: str) -> Tuple[bool, str, int]` |
| **Return** | Bisa return 1 atau multiple values | `return True, "Success", 42` |
| **Scope** | Variables hanya existed dalam function | Local variables tidak keluar function |
| **Location** | `src/database/crud.py` → CRUD functions | `get_beasiswa_list`, `login_user`, `add_to_favorit` |

**Quick Code Template:**
```python
def function_name(param1: Type1, param2: Type2) -> ReturnType:
    """Docstring explaining what this does."""
    # Implementation
    return result
```

**Find Examples In:**
- 📖 CONCEPT_DOCUMENTATION.md → Bagian 1 (1A, 1B, 1C, 1D)
- 💻 CODE_EXAMPLES.md → Bagian 1

---

### Konsep 2️⃣: CLASS/OBJEK

| Aspek | Penjelasan | Contoh |
|-------|-----------|--------|
| **Definisi** | Blueprint untuk object dengan attributes & methods | `class BeasiswaTab(QWidget)` |
| **Attributes** | Data/property dalam class | `self.user_id, self.beasiswa_data` |
| **Methods** | Function dalam class | `def load_data()`, `def search()` |
| **Singleton** | Hanya 1 instance untuk seluruh app | `DatabaseManager` |
| **Inheritance** | Class child inherit dari parent | `BeasiswaTab(QWidget)` |
| **Encapsulation** | Private data, public methods | `self._private_var` untuk internal |
| **Location** | `src/gui/gui_beasiswa.py` → BeasiswaTab | `src/core/database.py` → DatabaseManager |

**Quick Code Template:**
```python
class ClassName(ParentClass):
    """Docstring."""
    
    def __init__(self, param):
        """Constructor."""
        self.attribute = param
    
    def method(self):
        """Method docstring."""
        pass
```

**Find Examples In:**
- 📖 CONCEPT_DOCUMENTATION.md → Bagian 2 (2A, 2B, 2C)
- 💻 CODE_EXAMPLES.md → Bagian 2

---

### Konsep 3️⃣: STRUKTUR DATA

| Type | Use Case | Example | Methods |
|------|----------|---------|---------|
| **List** | Ordered collection | `[item1, item2, ...]` | `.append()`, `.sort()`, `[filter]` |
| **Dict** | Key-value pairs | `{'key': 'value'}` | `.keys()`, `.values()`, `.items()` |
| **Tuple** | Immutable fixed size | `(value1, value2)` | Unpacking, cannot modify |
| **Set** | Unique items | `{item1, item2}` | `.add()`, `.union()` |

**Quick Operations:**
```python
# List
beasiswa_list = get_beasiswa_list()  # [Dict1, Dict2, ...]
filtered = [b for b in beasiswa_list if b['status'] == 'Buka']
sorted_list = sorted(beasiswa_list, key=lambda b: b['deadline'])

# Dict
beasiswa = {'id': 1, 'nama': '...', 'status': '...'}
value = beasiswa['key']
beasiswa['new_key'] = 'new_value'

# Tuple
success, message, user_id = (True, "OK", 42)
x, y = (100, 50)
```

**Find Examples In:**
- 📖 CONCEPT_DOCUMENTATION.md → Bagian 3 (3A, 3B, 3C)
- 💻 CODE_EXAMPLES.md → Bagian 3

---

### Konsep 4️⃣: FILE HANDLING

| Operation | Code | Example |
|-----------|------|---------|
| **Read DB** | `cursor.execute(sql)` | `SELECT * FROM beasiswa` |
| **Write DB** | `execute_commit(sql, values)` | `INSERT INTO beasiswa ...` |
| **Export CSV** | `csv.DictWriter` | Export beasiswa ke file |
| **Logging** | `logger.info()` | `logger.info("User logged in")` |
| **Config JSON** | `json.load()`, `json.dump()` | Load/save preferences |
| **Create Dir** | `Path.mkdir(parents=True)` | Create database folder |

**Quick Snippets:**
```python
# Database
from src.database.crud import get_beasiswa_list
data = get_beasiswa_list(user_id)

# CSV Export
with open('export.csv', 'w') as f:
    writer = csv.DictWriter(f, fieldnames=['nama', 'status'])
    writer.writeheader()
    writer.writerows(data)

# Logging
import logging
logger = logging.getLogger(__name__)
logger.info(f"Loaded {len(data)} items")

# JSON Config
import json
with open('config.json', 'r') as f:
    config = json.load(f)
```

**Find Examples In:**
- 📖 CONCEPT_DOCUMENTATION.md → Bagian 4 (4A, 4B, 4C, 4D)
- 💻 CODE_EXAMPLES.md → Bagian 4

---

### Konsep 5️⃣: CHART & VISUALISASI

| Chart Type | Use Case | Location | Data Format |
|-----------|----------|----------|-------------|
| **Bar Chart** | Comparison by category | `create_bar_chart_beasiswa_per_jenjang` | `Dict[str, int]` |
| **Donut Chart** | Proportion/percentage | `create_donut_chart_status` | `Dict[str, int]` |
| **Horizontal Bar** | Comparison dengan many labels | `create_horizontal_bar_chart` | `Dict[str, int]` |
| **Line Chart** | Trend over time | (Optional) | `List[Tuple]` |

**Quick Template:**
```python
from src.visualization.visualisasi import create_bar_chart_beasiswa_per_jenjang
from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg as FigureCanvas

# Get data
data = get_beasiswa_per_jenjang()  # {'S1': 45, 'S2': 25, ...}

# Create chart
fig, ax = create_bar_chart_beasiswa_per_jenjang(data)

# Embed in PyQt6
canvas = FigureCanvas(fig)
layout.addWidget(canvas)
```

**Find Examples In:**
- 📖 CONCEPT_DOCUMENTATION.md → Bagian 5 (5A, 5B, 5C)
- 💻 CODE_EXAMPLES.md → Bagian 5

---

## 📂 FILE ORGANIZATION CHEATSHEET

```
Mau membuat feature baru?
        ↓
1. Define CRUD function → src/database/crud.py
   def get_my_feature(user_id: int) -> List[Dict]:
       ...
        ↓
2. Create Tab class → src/gui/tab_myfeature.py
   class MyFeatureTab(QWidget):
       def load_data():
           self.data = get_my_feature(self.user_id)
        ↓
3. Register di MainWindow → main.py
   my_tab = MyFeatureTab(user_id)
   tabs.addTab(my_tab, "My Feature")
        ↓
4. Optional: Add chart → src/visualization/visualisasi.py
   def create_my_feature_chart(data):
       fig, ax = plt.subplots()
       ...
```

---

## 🔍 SYNTAX QUICK REFERENCE

### Type Hints
```python
from typing import List, Dict, Optional, Tuple, Any

# Single type
user_id: int
name: str

# Collection types
users: List[Dict]
config: Dict[str, Any]
result: Tuple[bool, str, int]
optional_value: Optional[str]  # Can be str or None
```

### List Comprehension
```python
# Filter
buka = [b for b in beasiswa_list if b['status'] == 'Buka']

# Map/Transform
names = [b['nama'] for b in beasiswa_list]

# Filter + Map
filtered_names = [b['nama'] for b in beasiswa_list if b['jenjang'] == 'S1']
```

### Lambda Functions
```python
# Sort by deadline
sorted_data = sorted(beasiswa_list, key=lambda b: b['deadline'])

# Filter
filtered = list(filter(lambda b: b['status'] == 'Buka', beasiswa_list))
```

### Dictionary Operations
```python
# Create
data = {'key': 'value'}

# Access
value = data['key']
safe_value = data.get('key', 'default')

# Update
data['new_key'] = 'new_value'
data.update({'key1': 'val1', 'key2': 'val2'})

# Iterate
for key, value in data.items():
    print(f"{key}: {value}")

# Merge
merged = {**dict1, **dict2}
```

---

## 🎨 DESIGN TOKENS (Colors, Fonts)

```python
# Import dari design_tokens.py
from src.gui.design_tokens import *

# Colors
COLOR_NAVY = "#1e3a8a"
COLOR_ORANGE = "#f59e0b"
COLOR_WHITE = "#ffffff"
COLOR_GRAY_200 = "#e5e7eb"

# Fonts
FONT_FAMILY_PRIMARY = "Arial"
FONT_SIZE_BASE = 13
FONT_SIZE_LARGE = 28

# Spacing
PADDING_BASE = 16
MARGIN_BASE = 12

# Border
BORDER_RADIUS_MD = "8px"

# Usage
button.setStyleSheet(get_button_solid_stylesheet(COLOR_NAVY))
label.setFont(QFont(FONT_FAMILY_PRIMARY, FONT_SIZE_LARGE, QFont.Weight.Bold))
```

---

## 🛠️ COMMON PATTERNS

### 1. Load Data & Display (CRUD → UI)
```python
def load_beasiswa_data(self):
    try:
        self.beasiswa_data = get_beasiswa_list(self.user_id)
        self.refresh_table()
    except Exception as e:
        logger.error(f"Error loading: {e}")
        QMessageBox.critical(self, "Error", str(e))
```

### 2. Search/Filter
```python
def search_beasiswa(self, search_text: str):
    filtered = [b for b in self.beasiswa_data 
                if search_text.lower() in b['nama'].lower()]
    self.display_in_table(filtered)
```

### 3. Dialog Form
```python
dialog = MyDialog(parent=self)
if dialog.exec() == QDialog.DialogCode.Accepted:
    # User clicked OK
    result = dialog.get_data()
else:
    # User clicked Cancel
    pass
```

### 4. Error Handling
```python
try:
    operation()
except ValueError as e:
    logger.error(f"Value error: {e}")
    QMessageBox.warning(self, "Warning", str(e))
except Exception as e:
    logger.error(f"Unexpected error: {e}")
    QMessageBox.critical(self, "Error", str(e))
```

### 5. Database Query
```python
db = DatabaseManager()
cursor = db.execute("SELECT * FROM beasiswa WHERE id = ?", (beasiswa_id,))
row = cursor.fetchone()
data = dict(row) if row else None
```

---

## 📊 DATA FLOW CHEATSHEET

### User Login
```
User Input
  ↓
LoginWindow.handle_login()
  ↓
login_user(username, password) [CRUD Function]
  ↓
Query: SELECT * FROM akun WHERE username = ?
  ↓
Check password_hash match
  ↓
Return: (success: bool, message: str, user_id: int) [Tuple]
  ↓
If success → Emit signal → MainWindow opens
```

### User Search Beasiswa
```
User types in search_input
  ↓
textChanged signal triggered
  ↓
BeasiswaTab.search_beasiswa(search_text)
  ↓
List comprehension filter
  ↓
Filter list of beasiswa by nama
  ↓
display_in_table(filtered_data)
  ↓
Table widget updated
  ↓
User sees filtered results
```

### View Statistics
```
StatistikTab.__init__()
  ↓
self.init_ui()
  ↓
Loop: For each chart type
  → Query DB: get_beasiswa_per_jenjang()
  → Returns Dict: {'S1': 45, 'S2': 25, 'S3': 30}
  → create_bar_chart(data)
  → Returns (Figure, Axes)
  → FigureCanvas(fig)
  → Add to layout
  ↓
User sees 3 charts
```

---

## ⚡ PERFORMANCE TIPS

```python
# ❌ Inefficient: Query dalam loop
for i in range(100):
    data = cursor.execute("SELECT * FROM beasiswa WHERE id = ?", (i,))

# ✅ Efficient: Single query
data = cursor.execute("SELECT * FROM beasiswa").fetchall()

# ❌ Inefficient: Redundant list operations
filtered1 = [b for b in data if b['status'] == 'Buka']
filtered2 = [b for filtered1 if b['jenjang'] == 'S1']

# ✅ Efficient: Combined filter
filtered = [b for b in data if b['status'] == 'Buka' and b['jenjang'] == 'S1']

# ❌ Inefficient: String concatenation
result = ""
for item in items:
    result += item + ", "

# ✅ Efficient: Join
result = ", ".join(items)
```

---

## 🐛 DEBUGGING QUICK TIPS

```python
# 1. Print debugging
print(f"Variable value: {variable}")
print(f"Data type: {type(data)}")
print(f"Data length: {len(data)}")

# 2. Logging
logger.debug(f"Debug info: {data}")
logger.info(f"Operation: {step}")
logger.warning(f"Warning: {issue}")
logger.error(f"Error: {error}")

# 3. Check database
SELECT COUNT(*) FROM beasiswa;
SELECT * FROM beasiswa LIMIT 5;
PRAGMA table_info(beasiswa);

# 4. PyQt breakpoint
import pdb; pdb.set_trace()  # Set breakpoint

# 5. Exception details
except Exception as e:
    logger.error(f"Error: {e}")
    import traceback
    traceback.print_exc()
```

---

## 📚 KONSEP DIPETAKAN KE FILE

| Konsep | File | Class/Function | Line |
|--------|------|-----------------|------|
| **Function** | `src/database/crud.py` | `get_beasiswa_list()` | See file |
| **Class** | `src/gui/gui_beasiswa.py` | `BeasiswaTab` | See file |
| **List/Dict** | Everywhere | Used throughout | See code |
| **File I/O** | `src/core/database.py` | `DatabaseManager` | See file |
| **Chart** | `src/visualization/visualisasi.py` | `create_bar_chart_*()` | See file |
| **Integration** | `src/gui/tab_statistik.py` | `StatistikTab` | See file |

---

## ✅ COMMON MISTAKES & FIXES

| Mistake | Problem | Fix |
|---------|---------|-----|
| `cursor.execute(sql, param)` | Missing tuple | `cursor.execute(sql, (param,))` |
| `beasiswa_data[0]` | Error jika list kosong | `if beasiswa_data: beasiswa_data[0]` |
| `dict['key']` | KeyError jika key tidak ada | `dict.get('key', 'default')` |
| `fig, ax = create_chart()` tanpa return | None error | Ensure function returns `(fig, ax)` |
| `QWidget.setStylesheet()` typo | Stylesheet tidak apply | Check: `setStyleSheet()` (bukan stylesheet) |
| `self.data` used sebelum `load_data()` | Data None/empty | Call `load_data()` di `__init__()` |

---

## 🎯 GOAL: DARI PEMULA KE EXPERT

### Level 1: PEMULA (Understanding)
- [ ] Pahami 5 konsep utama
- [ ] Bisa identify konsep di kode
- [ ] Bisa run aplikasi

### Level 2: INTERMEDIATE (Applying)
- [ ] Bisa write function dengan proper signature
- [ ] Bisa create simple class
- [ ] Bisa query database
- [ ] Bisa fix simple bugs

### Level 3: ADVANCED (Doing)
- [ ] Bisa create fitur baru lengkap
- [ ] Bisa refactor code
- [ ] Bisa optimize performance
- [ ] Bisa debug complex issues

### Level 4: EXPERT (Teaching)
- [ ] Bisa design architecture
- [ ] Bisa mentor orang lain
- [ ] Bisa create best practices guide
- [ ] Bisa review & approve code

---

## 🚀 NEXT STEPS

1. **Read LEARNING_GUIDE.md** → Learning path
2. **Read CONCEPT_DOCUMENTATION.md** → Theory
3. **Read CODE_EXAMPLES.md** → Practice
4. **Read source code** → Implementation
5. **Create feature** → Application
6. **Test & deploy** → Mastery

---

**Created:** April 13, 2026  
**Quick Links:**
- 📖 Full concepts → `CONCEPT_DOCUMENTATION.md`
- 💻 Code examples → `CODE_EXAMPLES.md`
- 🗺️ Learning guide → `LEARNING_GUIDE.md`
- ⚡ This file → `QUICK_REFERENCE.md`

---

## Pertanyaan Cepat?

| Pertanyaan | Halaman |
|-----------|--------|
| Apa itu function? | Bagian 1 |
| Bagaimana membuat class? | Bagian 2 |
| Gimana use List & Dict? | Bagian 3 |
| Cara query database? | Bagian 4 |
| Bikin chart gimana? | Bagian 5 |
| Mau buat feature baru? | FILE ORGANIZATION |
| Error/bug di mana? | DEBUGGING TIPS |
| Syntax apa aja? | SYNTAX QUICK REFERENCE |

**Happy Learning! 🎓**
