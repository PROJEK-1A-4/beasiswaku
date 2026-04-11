# BeasiswaKu

Desktop Scholarship Management System - PyQt6 Application  
**Version 2.0.0 | Status: Production Ready ✓**

## Quick Links

- 📖 **[README](docs/README.md)** - Project overview and quick start
- 🏗️ **[ARCHITECTURE](docs/ARCHITECTURE.md)** - System design and team structure
- 📚 **[API Reference](docs/API.md)** - Function documentation and usage
- 🗄️ **[Database Schema](docs/DATABASE_SCHEMA.md)** - Table structure and relationships
- ⚙️ **[Setup Guide](docs/SETUP.md)** - Installation and configuration

## Quick Start

```bash
# Setup
make setup

# Run application
make run

# Run tests
make test
```

## Features

✅ User authentication with bcrypt  
✅ Scholarship browsing and search  
✅ Application tracking  
✅ Favorites management  
✅ Personal notes  
✅ Data visualization  

## Team

| Member | Role | Module |
|--------|------|--------|
| KEMAL | Web Scraping | `src/scraper/` |
| DARVA | Database & CRUD | `src/database/` + `src/core/` |
| KYLA | GUI Tabs | `src/gui/tab_*.py` |
| AULIA | Main Window & Auth | `src/gui/main_window.py` |
| RICHARD | Visualization | `src/visualization/` |

## Project Status

- ✅ **20/20 Phases Complete**
- ✅ **100% Test Pass Rate** (10/10 suites, 83 scenarios)
- ✅ **Production Ready**
- ✅ **Team-Based Modular Architecture**

## Tech Stack

- **GUI**: PyQt6
- **Database**: SQLite3
- **Security**: bcrypt
- **Testing**: pytest
- **Python**: 3.8+

---

**For detailed information, see documentation files in `docs/` directory.**
