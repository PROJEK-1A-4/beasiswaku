# BeasiswaKu Architecture

## System Overview

BeasiswaKu is a modular PyQt6-based desktop application organized into 6 functional modules with clear team ownership.

```
┌─────────────────────────────────────────────────────────┐
│                   main.py (Entry Point)                 │
│                   (AULIA: UI Orchestration)             │
└────────────┬────────────────────────────────────────────┘
             │
    ┌────────┴──────────────────────────────┐
    │                                        │
    ▼                                        ▼
┌─────────────┐                  ┌──────────────────┐
│  GUI Layer  │                  │  Data Layer      │
│  (src/gui/) │                  │  (src/database/) │
│ KYLA, AULIA │                  │    (DARVA)       │
└──────┬──────┘                  └────────┬─────────┘
       │                                   │
       │        ┌──────────────────────────┼──────────────────┐
       │        │                          │                  │
       ▼        ▼                          ▼                  ▼
   ┌─────────────────────┐  ┌──────────────────────┐  ┌──────────────────┐
   │   Login & Register  │  │   Authentication     │  │   Database       │
   │   (AULIA)           │  │   (password hashing) │  │   Connection     │
   │                     │  │   (DARVA)            │  │   Management     │
   └─────────────────────┘  └──────────────────────┘  │   (DARVA)        │
                                                       └──────────────────┘
                                                              │
                ┌──────────────────────────────────────────┬─┘
                │                                          │
                ▼                                          ▼
    ┌──────────────────────────┐          ┌──────────────────────────┐
    │   CRUD Operations        │          │   SQLite Database        │
    │   - beasiswa             │          │   (6 tables)             │
    │   - lamaran              │          │   - akun                 │
    │   - favorit              │          │   - beasiswa             │
    │   - catatan              │          │   - penyelenggara        │
    │   (DARVA: src/database/) │          │   - riwayat_lamaran      │
    └──────────────────────────┘          │   - favorit              │
                                          │   - catatan              │
                                          └──────────────────────────┘


┌─────────────────────────────────────────────────────┐
│              External Module Integration            │
├─────────────┬──────────────────┬───────────────────┤
│   Scraper   │  Visualization   │   Utilities       │
│  (KEMAL)    │   (RICHARD)      │   (DARVA-led)     │
│ src/scraper │ src/visualization│   src/utils       │
└─────────────┴──────────────────┴───────────────────┘
```

## Module Organization

### 1. **src/core/** - Shared Infrastructure
- `config.py` - Centralized configuration management (Config class)
- `database.py` - DatabaseManager singleton for connections
- `__init__.py` - Package exports

**Responsibility**: Core infrastructure shared by all modules

### 2. **src/database/** (DARVA)
- `crud.py` - All CRUD operations and authentication
  - User management (register, login, hash verification)
  - Beasiswa CRUD
  - Lamaran (applications) CRUD
  - Favorit (favorites) CRUD
  - Catatan (notes) CRUD
  - Aggregation queries

**Responsibility**: Database operations and business logic

### 3. **src/gui/** (KYLA + AULIA)
- `main_window.py` - Main application window (AULIA)
- `login_window.py` - Authentication UI (AULIA)
- `tab_beasiswa.py` - Scholarship browsing tab (KYLA)
- `tab_favorit.py` - Favorites management tab (KYLA)
- `tab_notes.py` - Notes management tab (KYLA)
- `styles.py` - UI theming and styling (AULIA)
- `dialogs.py` - Modal dialogs and popups (KYLA)

**Responsibility**: User interface and user interactions

### 4. **src/scraper/** (KEMAL) 
- `scraper.py` - Web scraping and data collection
- Optional: data cleaner, parsers, JSON backup

**Responsibility**: External data collection and ingestion

### 5. **src/visualization/** (RICHARD)
- `visualisasi.py` - Analytics and chart generation
- Optional: aggregation helpers, color themes

**Responsibility**: Data visualization and analytics

### 6. **src/utils/** (DARVA-led, shared)
- Common utility functions needed by multiple modules
- Validation helpers
- Formatting utilities
- Shared constants

**Responsibility**: Cross-module utilities and helpers

## Design Patterns Used

### 1. Singleton Pattern
```python
# DatabaseManager - ensures single connection throughout app
db = DatabaseManager()
conn = db.get_connection()
```

### 2. Configuration Management
```python
# Config class - centralized configuration from environment
from src.core.config import Config
db_path = Config.DATABASE_PATH
app_name = Config.APP_NAME
```

### 3. Layered Architecture
- **Presentation Layer**: `src/gui/`
- **Business Logic Layer**: `src/database/` + `src/core/`
- **Data Access Layer**: `src/core/database.py`
- **External Integration**: `src/scraper/`, `src/visualization/`

## Dependencies

```
PyQt6 (GUI)
    ↓
src/gui/ ←────┐
              │
src/database/ ┼─→ src/core/database (DatabaseManager)
              │         ↓
src/scraper/  ┼─→ SQLite Database
              │    (database/beasiswaku.db)
              │
src/visualization/ ←─┘
```

## Data Flow

1. **User launches app** → `main.py`
2. **Login/Register** → `gui/login_window.py` → `database/crud.py` → Database
3. **Browse scholarships** → `gui/tab_beasiswa.py` → `database/crud.py` → Database
4. **Add to favorites** → `gui/tab_favorit.py` → `database/crud.py` → Database
5. **Add notes** → `gui/tab_notes.py` → `database/crud.py` → Database
6. **View analytics** → `visualization/visualisasi.py` → aggregation from Database
7. **Update from web** → `scraper/scraper.py` → `database/crud.py` → Database

## Team Workflow

Each team member works in their designated module:

```
darva branch (DARVA)
├── src/database/
├── src/core/
└── src/utils/

feature/scraper-kemal (KEMAL)
├── src/scraper/
└── tests/unit/test_scraper.py

feature/gui-kyla (KYLA)
├── src/gui/tab_*.py
└── src/gui/dialogs.py

feature/gui-aulia (AULIA)
├── src/gui/main_window.py
├── src/gui/login_window.py
├── src/gui/styles.py
└── tests/unit/test_gui.py

feature/visualization-richard (RICHARD)
├── src/visualization/
└── tests/unit/test_visualization.py
```

**Git Workflow:**
1. Each developer creates a feature branch: `feature/module-name`
2. Work locally in designated modules
3. Regular commits with clear messages
4. Test locally before merging
5. Create PR for code review
6. Merge to `darva` branch
7. DARVA merges `darva` → `main` when all features ready

## Key Interfaces

### Config Class
```python
from src.core.config import Config

Config.DATABASE_PATH          # Path to SQLite database
Config.APP_NAME              # Application name
Config.WINDOW_WIDTH          # GUI window width
Config.DEBUG_MODE            # Debug logging level
Config.TEAM_STRUCTURE        # Team member assignments
```

### DatabaseManager
```python
from src.core.database import DatabaseManager

db = DatabaseManager()
conn = db.get_connection()   # Get connection (singleton)
db.execute(query, params)    # Execute query
db.execute_commit(query)     # Execute and commit
db.init_schema()             # Initialize database schema
```

### CRUD Functions
```python
from src.database.crud import (
    register_user, login_user,
    create_beasiswa, get_beasiswa, update_beasiswa, delete_beasiswa,
    add_favorit, delete_favorit, get_favorit_list,
    add_catatan, get_catatan, edit_catatan, delete_catatan
)
```

## Testing

Each module has corresponding tests:
- `tests/unit/test_phase_1_1.py` - Database schema
- `tests/unit/test_phase_2_2.py` - Authentication
- `tests/unit/test_phase_3_1.py` - Beasiswa CRUD
- `tests/unit/test_phase_3_2.py` - Lamaran CRUD
- `tests/unit/test_phase_4_1.py` - Aggregation queries
- `tests/unit/test_phase_5_*.py` - GUI and features

## Configuration

Application configuration via `Config` class:
- Database path and timeout
- Window dimensions and theme
- Scraper settings
- Logging configuration
- Team assignments

Override with environment variables:
```bash
export DATABASE_PATH=database/custom.db
export DEBUG_MODE=True
export WINDOW_WIDTH=1400
python main.py
```

## Performance Considerations

- Singleton database connection: Reduces connection overhead
- Connection pooling ready: Can be added to `DatabaseManager`
- Row factory caching: Enables column access by name
- Lazy imports: Module imports only when needed

## Security

- **Password hashing**: bcrypt with 12 rounds
- **SQL injection prevention**: Parameterized queries
- **Input validation**: Type hints and validators in CRUD functions
- **Session management**: User context in application state

## Future Enhancements

- Add logging to all modules
- Implement caching for frequent queries
- Add data export (CSV, JSON, PDF)
- Async operations for long-running tasks
- Unit test coverage for all modules
- API server for remote access

## Kebijakan Import & Compatibility Wrapper
Untuk menjaga stabilitas saat proses refaktor besar, proyek menerapkan kebijakan Compatibility Wrapper:
- **Canonical Path:** Import modul GUI yang baru wajib langsung mengarah ke file implementasi asli (contoh: from src.gui.tab_beasiswa import BeasiswaTab).
- **Wrapper File:** File seperti src/gui/gui_beasiswa.py dipertahankan hanya sebagai jembatan (wrapper) bagi modul atau test lama yang masih memanggil path lama.
- **Aturan Tim:** Dilarang menambahkan logika bisnis baru ke dalam file wrapper. Semua ekstensi fitur harus dilakukan di file canonical (tab_*.py).
