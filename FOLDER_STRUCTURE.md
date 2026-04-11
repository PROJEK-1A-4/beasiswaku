# 📁 BeasiswaKu - Struktur Folder Lengkap

## 🏢 ROOT LEVEL (Bersih & Minimal)

```
beasiswaku/
│
├── main.py                          # ✅ Entry point aplikasi (PyQt6)
├── setup.sh                         # ✅ Setup script Linux
├── setup_and_run.sh                 # ✅ Setup + run script
│
├── README.md                        # ✅ Quick reference
├── blueprint_beasiswaku.md          # ✅ Project blueprint (referensi)
├── copilot-instructions.md          # ✅ VS Code Copilot config
├── REFACTORING_COMPLETION_REPORT.md # ✅ Refactoring summary
│
├── requirements.txt                 # ✅ Python dependencies
├── .env.example                     # ✅ Environment template
├── Makefile                         # ✅ Development commands
│
└── .gitignore                       # ✅ Git ignore rules
```

---

## 📦 SRC/ - Kode Aplikasi (6 Modul)

```
src/
│
├── __init__.py                              # Package initialization
│
├── core/                                    # 🔧 Shared Infrastructure (DARVA)
│   ├── __init__.py
│   ├── config.py          ✅ Config class - Centralized configuration
│   └── database.py        ✅ DatabaseManager singleton pattern
│
├── database/                                # 🗄️ CRUD Operations (DARVA)
│   ├── __init__.py
│   └── crud.py            ✅ All database operations (23 functions)
│
├── gui/                                     # 🖥️ PyQt6 Interface (KYLA + AULIA)
│   ├── __init__.py
│   ├── main_window.py     ✅ Main window & tab system (AULIA)
│   ├── login_window.py    ✅ Authentication UI (AULIA)
│   ├── tab_beasiswa.py    ✅ Scholarship browsing tab (KYLA)
│   ├── tab_favorit.py     ✅ Favorites management (KYLA)
│   ├── tab_notes.py       ✅ Personal notes (KYLA)
│   ├── dialogs.py         📋 Modal dialogs (KYLA) - ready
│   └── styles.py          📋 Theme & styling (AULIA) - ready
│
├── scraper/                                 # 🌐 Web Scraping (KEMAL)
│   ├── __init__.py
│   ├── scraper.py         📋 Template ready for KEMAL
│   ├── parsers.py         📋 Optional: data parsers
│   └── data_cleaner.py    📋 Optional: data cleaning
│
├── visualization/                           # 📊 Analytics & Charts (RICHARD)
│   ├── __init__.py
│   ├── visualisasi.py     📋 Template ready for RICHARD
│   ├── charts.py          📋 Optional: chart generation
│   └── aggregator.py      📋 Optional: data aggregation
│
└── utils/                                   # 🛠️ Shared Utilities (DARVA-led)
    ├── __init__.py
    ├── helpers.py         📋 Helper functions
    ├── validators.py      📋 Input validation
    └── constants.py       📋 Shared constants
```

---

## 📚 DOCS/ - Essential Documentation (5 Files)

```
docs/
│
├── README.md                  # 📖 Quick reference & overview
├── ARCHITECTURE.md            # 🏗️ System design (11KB)
│                              #    - Module diagram
│                              #    - Team structure
│                              #    - Design patterns
│                              #    - Data flow
│
├── API.md                     # 📚 Complete API reference (9.1KB)
│                              #    - All CRUD functions
│                              #    - Parameter descriptions
│                              #    - Usage examples
│
├── DATABASE_SCHEMA.md         # 🗄️ Database documentation (15KB)
│                              #    - 6 table definitions
│                              #    - Fields & constraints
│                              #    - Relationships (ERD)
│                              #    - Sample queries
│
└── SETUP.md                   # ⚙️ Installation & config (9.9KB)
                               #    - Setup instructions
                               #    - Team workflow
                               #    - Troubleshooting
```

---

## 🧪 TESTS/ - Test Suite (Organized by Module)

```
tests/
│
├── __init__.py
├── conftest.py                              # ✅ Pytest configuration & fixtures
│
├── unit/                                    # 🧪 Unit Tests
│   ├── __init__.py
│   ├── test_phase_1_1.py      ✅ Database schema & initialization
│   ├── test_phase_1_3.py      ✅ Authentication
│   ├── test_phase_2_2.py      ✅ Beasiswa CRUD
│   ├── test_phase_3_1.py      ✅ Lamaran CRUD
│   ├── test_phase_3_2.py      ✅ Favorit CRUD
│   ├── test_phase_4_1.py      ✅ Aggregation queries
│   ├── test_phase_5_2.py      ✅ Application tracking
│   ├── test_phase_5_3.py      ✅ Favorites UI
│   ├── test_phase_5_4.py      ✅ Notes functionality
│   └── test_auth_demo.py      ✅ Auth demo
│
└── integration/                             # 📌 Integration Tests (Ready)
    ├── __init__.py
    └── (reserved for full integration tests)
```

---

## 💾 DATA/ - Database & Backups

```
data/
│
├── beasiswaku.db              # 📦 Main SQLite database
│                              #    - 6 tables
│                              #    - User data
│                              #    - Scholarship data
│
└── backup/                    # 💾 Backup Directory
    └── beasiswaku_backup.db   # 📋 (placeholder for backups)
```

**Purpose:**
- `beasiswaku.db` - Live production database
- `backup/` - Automated backup location (for disaster recovery)
- **Configured in:**
  - `src/core/config.py`: `DATABASE_PATH`, `BACKUP_DIR`
  - `.env`: `DATABASE_PATH`, `DATABASE_BACKUP_PATH`

---

## 📝 LOGS/ - Application Logs

```
logs/
│
└── beasiswa.log               # 📋 Application logs
                               #    - Info level by default
                               #    - Configured in src/core/config.py
```

**Configured in:**
- `src/core/config.py`: `LOG_FILE`, `LOG_LEVEL`
- `.env`: `LOG_LEVEL`, `LOG_FILE`

---

## 🎨 ASSETS/ - Images & Resources (Legacy)

```
assets/
│
└── (reserved for UI assets if needed)
```

---

## 📂 DATABASE/ - Old Database Folder (Legacy)

```
database/
│
├── beasiswa.db                # 🔄 Migrated to data/beasiswaku.db
└── (legacy location, can be removed)
```

**Note:** Old database location. All database operations now use `data/beasiswaku.db`

---

## 🔑 KEY FILES UNTUK TEAM

| File | Owner | Purpose |
|------|-------|---------|
| `src/core/config.py` | DARVA | 🔧 Central configuration management |
| `src/core/database.py` | DARVA | 🗄️ Database connection singleton |
| `src/database/crud.py` | DARVA | 📝 All CRUD operations |
| `src/gui/main_window.py` | AULIA | 🖥️ Main application window |
| `src/gui/login_window.py` | AULIA | 🔐 Authentication UI |
| `src/gui/tab_*.py` | KYLA | 📑 Tab components |
| `src/scraper/scraper.py` | KEMAL | 🌐 Web scraping (template) |
| `src/visualization/visualisasi.py` | RICHARD | 📊 Analytics (template) |

---

## 🎯 FOLDER SUMMARY

| Folder | Files | Purpose | Owner |
|--------|-------|---------|-------|
| `src/core/` | 2 | Shared infrastructure | DARVA |
| `src/database/` | 1 | CRUD operations | DARVA |
| `src/gui/` | 5+ | User interface | KYLA, AULIA |
| `src/scraper/` | 1+ | Web scraping | KEMAL |
| `src/visualization/` | 1+ | Analytics | RICHARD |
| `src/utils/` | 1+ | Shared utilities | DARVA-led |
| `docs/` | 5 | Documentation | All |
| `tests/unit/` | 10 | Unit tests | All |
| `tests/integration/` | - | Integration tests (ready) | All |
| `data/` | 2 | Database & backups | - |
| `logs/` | 1 | Application logs | - |

---

## ✅ TOTAL FILES

- **Python files in src/**: 15 files
- **Test files**: 14 files
- **Documentation files**: 5 files
- **Config files**: 3 files (.env.example, Makefile, requirements.txt)
- **Root files**: 4 files (main.py, 2 setup scripts, .gitignore)

**Total**: ~41 files (clean & organized)

---

## 🗺️ TREE VIEW

```
beasiswaku/
├── src/                      # 6 modules (15 files)
│   ├── core/                 # Infrastructure (DARVA)
│   ├── database/             # CRUD (DARVA)
│   ├── gui/                  # Interface (KYLA, AULIA)
│   ├── scraper/              # Scraping (KEMAL)
│   ├── visualization/        # Analytics (RICHARD)
│   └── utils/                # Shared (DARVA-led)
│
├── tests/                    # 14 test files + conftest
│   ├── unit/                 # 10 unit test suites ✅
│   └── integration/          # Framework ready
│
├── docs/                     # 5 essential files ✅
│   ├── ARCHITECTURE.md       # System design
│   ├── API.md                # Function reference
│   ├── DATABASE_SCHEMA.md    # Database structure
│   ├── SETUP.md              # Installation
│   └── README.md             # Quick start
│
├── data/                     # Database & backups
│   ├── beasiswaku.db         # Main SQLite DB
│   └── backup/               # Backup location
│
├── logs/                     # Application logs
│   └── beasiswa.log
│
├── database/                 # Legacy folder (old location)
│    └── beasiswa.db
│
├── assets/                   # UI resources (reserved)
│
├── main.py                   # Entry point ✅
├── Makefile                  # Dev commands ✅
├── .env.example              # Config template ✅
├── requirements.txt          # Dependencies ✅
│
├── README.md                 # Quick reference ✅
├── blueprint_beasiswaku.md   # Project blueprint
├── copilot-instructions.md   # VS Code config
└── REFACTORING_COMPLETION_REPORT.md # Summary
```

---

## 🗂️ FOLDER PURPOSE LEGEND

| Symbol | Meaning |
|--------|---------|
| ✅ | Essential, production ready |
| 📋 | Template, ready for team to implement |
| 🔄 | Legacy, can be archived |
| 📌 | Reserved for future use |

