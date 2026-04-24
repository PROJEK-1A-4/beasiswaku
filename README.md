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

## Login Guide

BeasiswaKu has two database modes:

### 1) Normal Mode

Use this if you want to run the app with the main database.

```powershell
Remove-Item Env:DATABASE_PATH -ErrorAction SilentlyContinue
python main.py
```

What to do in this mode:
- Open the app normally.
- If the database is still empty, register a new account from the login screen.
- Use that account to log in.

### 2) Demo Mode

Use this for presentations, because it already contains dummy data for charts and tracker views.

```powershell
$env:DATABASE_PATH = "database/beasiswaku_demo.db"
python main.py
```

Demo login account:
- Username: `dummy_user`
- Password: `Dummy123!`

Notes for demo mode:
- The demo database is separate from the main database.
- It is safe to use for presentation because it contains sample data only.
- If you reopen PowerShell, set `DATABASE_PATH` again before running the app.

## Features

✅ User authentication with bcrypt  
✅ Scholarship browsing and search  
✅ Application tracking  
✅ Favorites management  
✅ Personal notes  
✅ Data visualization  

## Simple Presentation Flow

If the lecturer asks how to run the project, you can explain it like this:

1. Run the app in normal mode when you want to use the main database.
2. Run the app in demo mode when you want to show charts and sample data.
3. In demo mode, log in with the dummy account so the Tracker and Statistik tabs already have content.
4. The dummy database is separate, so it does not affect the main database.

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
