# BeasiswaKu - Desktop Scholarship Management System

A PyQt6-based desktop application for managing scholarship information with features for searching, tracking applications, and managing personal notes.

## Quick Start

```bash
# Setup and install
make setup

# Run the application
make run

# Run tests
make test
```

## Features

- **Authentication**: User registration and login with bcrypt password hashing
- **Scholarship Management**: Browse, search, and manage scholarship data
- **Application Tracking**: Track scholarship applications with status updates
- **Favorites**: Create personalized list of favorite scholarships
- **Personal Notes**: Add notes to scholarship entries for personal tracking
- **Data Visualization**: Analytics and charts for scholarship metrics

## Project Structure

```
beasiswaku/
├── src/
│   ├── core/          - Shared database & config (DatabaseManager, Config class)
│   ├── database/      - CRUD operations (DARVA)
│   ├── gui/           - PyQt6 interface (KYLA, AULIA)
│   ├── scraper/       - Web scraping (KEMAL)
│   ├── visualization/ - Analytics & charts (RICHARD)
│   └── utils/         - Shared utilities
├── data/              - Database files and backups
├── tests/             - Unit and integration tests
├── docs/              - Documentation
└── main.py            - Application entry point
```

## Team Responsibilities

- **KEMAL**: Web scraping and data collection (`src/scraper/`)
- **DARVA**: Database and CRUD operations (`src/database/`)
- **KYLA**: GUI tabs and dialogs (`src/gui/tab_*.py`)
- **AULIA**: Main window and authentication UI (`src/gui/main_window.py`, `login_window.py`)
- **RICHARD**: Visualization and analytics (`src/visualization/`)

## Requirements

- Python 3.8+
- PyQt6
- SQLite3
- bcrypt

See `requirements.txt` for complete dependency list.

## Documentation

- [ARCHITECTURE.md](docs/ARCHITECTURE.md) - System design and module organization
- [API.md](docs/API.md) - CRUD operations and function reference
- [DATABASE_SCHEMA.md](docs/DATABASE_SCHEMA.md) - Database tables and relationships
- [SETUP.md](docs/SETUP.md) - Installation, configuration, and deployment

## Testing

```bash
# Run all tests
make test

# Run with coverage
make test-cov

# Run specific test suite
python3 tests/unit/test_phase_1_1.py
```

## Development

```bash
# Format code
make format

# Lint code
make lint

# Type check
make type-check

# Development setup (install dev dependencies)
make dev-install
```

## License

Internal project - University assignment

## Status

✅ Complete and tested (20/20 phases)  
✅ 100% test pass rate (10/10 suites, 83 scenarios)  
✅ Production-ready application
