# Setup and Installation Guide - BeasiswaKu

## Prerequisites

- Python 3.8 or higher
- pip (Python package manager)
- Git (for version control)
- At least 100MB free disk space

## Installation

### Option 1: Automatic Setup (Recommended)

```bash
# Clone or download the project
cd beasiswaku

# Run automated setup
make setup
```

This will:
- Install all dependencies from `requirements.txt`
- Create `.env` configuration file (from `.env.example`)
- Initialize necessary directories
- Set up the database

### Option 2: Manual Setup

```bash
# 1. Install dependencies
pip install -r requirements.txt

# 2. Create .env file
cp .env.example .env

# 3. Initialize database
python3 -c "from src.core.database import DatabaseManager; db = DatabaseManager(); db.init_schema()"

# 4. Create data directories
mkdir -p data logs data/backup
```

## Environment Configuration

### .env File

Copy `.env.example` to `.env` and customize:

```bash
# Database Configuration
DATABASE_PATH=database/beasiswaku.db
DATABASE_BACKUP_PATH=database/backup/beasiswa_backup.db

# Application Configuration
APP_NAME=BeasiswaKu
APP_VERSION=2.0.0
DEBUG_MODE=False

# GUI Configuration
WINDOW_WIDTH=1200
WINDOW_HEIGHT=800
THEME=light

# Scraper Configuration (for KEMAL)
SCRAPER_TIMEOUT=30
SCRAPER_RETRIES=3
SCRAPER_USER_AGENT=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36

# Logging Configuration
LOG_LEVEL=INFO
LOG_FILE=logs/beasiswa.log
```

### Running with Custom Configuration

```bash
# Override via environment variables
export DATABASE_PATH=/custom/path/beasiswa.db
export DEBUG_MODE=True
export WINDOW_WIDTH=1400

python3 main.py
```

## Running the Application

### Start GUI Application

```bash
# Using Makefile
make run

# Or directly
python3main.py
```

### Run Tests

```bash
# All tests
make test

# Specific test file
python3 tests/unit/test_phase_1_1.py

# With coverage report
make test-cov
```

## Development Setup

### Install Development Dependencies

```bash
# Install dev dependencies
make dev-install

# Or manually
pip install -r requirements.txt
pip install pytest pytest-cov pylint mypy black
```

### Code Quality Commands

```bash
# Format code
make format

# Lint code
make lint

# Type checking
make type-check

# All quality checks
make ci
```

## Project Structure

```
beasiswaku/
├── src/
│   ├── core/              # Shared database & config
│   │   ├── __init__.py
│   │   ├── config.py      # Configuration management
│   │   └── database.py    # DatabaseManager singleton
│   ├── database/          # CRUD operations (DARVA)
│   │   ├── __init__.py
│   │   └── crud.py
│   ├── gui/               # PyQt6 interface (KYLA, AULIA)
│   │   ├── __init__.py
│   │   ├── main_window.py
│   │   ├── login_window.py
│   │   ├── tab_beasiswa.py
│   │   ├── tab_favorit.py
│   │   ├── tab_notes.py
│   │   ├── dialogs.py
│   │   └── styles.py
│   ├── scraper/           # Web scraping (KEMAL)
│   │   ├── __init__.py
│   │   └── scraper.py
│   ├── visualization/     # Charts & analytics (RICHARD)
│   │   ├── __init__.py
│   │   └── visualisasi.py
│   └── utils/             # Shared utilities
│       ├── __init__.py
│       └── helpers.py
├── data/                  # Database and backups
│   ├── beasiswaku.db      # Main database
│   └── backup/            # Backups directory
├── tests/                 # Unit and integration tests
│   ├── __init__.py
│   ├── conftest.py        # Pytest configuration
│   ├── unit/              # Unit tests
│   └── integration/       # Integration tests
├── docs/                  # Essential documentation
│   ├── README.md          # This file
│   ├── ARCHITECTURE.md    # System design
│   ├── API.md             # CRUD API reference
│   └── DATABASE_SCHEMA.md # Database structure
├── logs/                  # Application logs
├── main.py                # Application entry point
├── requirements.txt       # Python dependencies
├── .env.example          # Environment template
├── Makefile              # Development commands
└── README.md             # Project overview
```

## Database

### Location
- Default: `database/beasiswaku.db`
- Configurable: Set `DATABASE_PATH` in `.env`

### Initialization

Database is automatically initialized on first run.

Manual initialization:
```python
from src.core.database import DatabaseManager

db = DatabaseManager()
db.init_schema()
```

### Backup

```bash
# Automatic backup (setup creates)
cp database/beasiswaku.db database/backup/beasiswaku_backup.db

# Using Makefile (when available)
make backup
```

### Restore

```bash
cp database/backup/beasiswaku_backup.db database/beasiswaku.db
```

## Directory Permissions

Ensure write access to:
```bash
chmod -R 755 data/          # Database directory
chmod -R 755 logs/          # Logs directory
chmod 644 database/*.db     # Database files
```

## Troubleshooting

### Module Import Errors

```
ModuleNotFoundError: No module named 'PyQt6'
```

**Solution:**
```bash
pip install PyQt6
pip install -r requirements.txt
```

### Database Connection Error

```
Cannot operate on a closed database
```

**Solution:**
- Ensure `database/` directory exists and is writable
- Check `DATABASE_PATH` in `.env`
- Re-initialize database: `python3 -c "from src.core.database import DatabaseManager; db = DatabaseManager(); db.init_schema()"`

### Port Already in Use (if using network features)

**Solution:**
- Change port in `.env`
- Kill existing process: `pkill -f "python3 main.py"`

### Slow Performance

**Solution:**
- Close other applications using resources
- Clear logs: `rm -f logs/beasiswa.log*`
- Optimize database: `sqlite3 database/beasiswaku.db "VACUUM; ANALYZE;"`

## Team Development Workflow

### Branching Strategy

```
main (production)
  ↑
  └─ darva (DARVA's integration branch)
      ├ feature/scraper-kemal (KEMAL)
      ├ feature/gui-kyla (KYLA)
      ├ feature/gui-aulia (AULIA)
      └ feature/visualization-richard (RICHARD)
```

### Individual Setup

**For KEMAL (Scraper):**
```bash
git checkout -b feature/scraper-kemal
cd src/scraper
# Develop in src/scraper/scraper.py
```

**For DARVA (Database):**
```bash
git checkout -b feature/database-darva
cd src/database
# Develop in src/database/ and src/core/
```

**For KYLA (GUI Tabs):**
```bash
git checkout -b feature/gui-kyla
cd src/gui
# Develop in src/gui/tab_*.py, src/gui/dialogs.py
```

**For AULIA (Main GUI):**
```bash
git checkout -b feature/gui-aulia
cd src/gui
# Develop in src/gui/main_window.py, src/gui/login_window.py
```

**For RICHARD (Visualization):**
```bash
git checkout -b feature/visualization-richard
cd src/visualization
# Develop in src/visualization/
```

### Making Changes

```bash
# 1. Create feature branch
git checkout -b feature/your-feature-name

# 2. Make changes in your module
# 3. Test your changes
make test

# 4. Commit with clear messages
git commit -m "Feature: Add new functionality"

# 5. Push to repository
git push origin feature/your-feature-name

# 6. Create Pull Request to darva branch
```

### Testing Before Commit

```bash
# Run tests for your module
make team-kemal      # For KEMAL
make team-darva      # For DARVA
make team-kyla       # For KYLA
make team-aulia      # For AULIA
make team-richard    # For RICHARD

# Or run all tests
make test
```

## Deployment

### Creating Installer (Windows)

```bash
# Using setuptools
python3 setup.py bdist_msi

# Using PyInstaller
pip install pyinstaller
pyinstaller --onefile --windowed main.py
```

### Docker Deployment (Optional)

```dockerfile
FROM python:3.9-slim
WORKDIR /app
COPY . .
RUN pip install -r requirements.txt
CMD ["python3", "main.py"]
```

Build and run:
```bash
docker build -t beasiswaku .
docker run -it beasiswaku
```

## Performance Optimization

### Database Optimization

```python
from src.core.database import DatabaseManager

db = DatabaseManager()
conn = db.get_connection()

# Optimize database
conn.execute("VACUUM")
conn.execute("ANALYZE")
conn.commit()
```

### GUI Performance

- Use threading for long operations
- Implement lazy loading for large datasets
- Cache frequently accessed data

## Logging

Logs are written to `logs/beasiswa.log`

Configure logging level in `.env`:
```
LOG_LEVEL=DEBUG    # Verbose logging
LOG_LEVEL=INFO     # Normal logging
LOG_LEVEL=WARNING  # Only warnings and errors
```

View logs:
```bash
tail -f logs/beasiswa.log        # Real-time
cat logs/beasiswa.log | grep ERROR  # Errors only
```

## Updates and Maintenance

### Updating Dependencies

```bash
# Check for updates
pip list --outdated

# Update all packages
pip install --upgrade -r requirements.txt
```

### Database Migrations

For schema changes:
1. Update `src/core/database.py`
2. Create migration script in `data/migrations/`
3. Document in ARCHITECTURE.md
4. Test thoroughly before deployment

## Getting Help

### Documentation Files

- `README.md` - Project overview
- `ARCHITECTURE.md` - System design and modules
- `API.md` - Function reference and usage examples
- `DATABASE_SCHEMA.md` - Database structure

### Common Tasks

```bash
make help           # Show available commands
make install        # Install dependencies
make dev            # Install dev dependencies
make run            # Run application
make test           # Run tests
make clean          # Clean generated files
make format         # Format code
make lint           # Check code quality
```

## Support and Contribution

For issues or contributions:
1. Check existing documentation
2. Review ARCHITECTURE.md for design patterns
3. Add tests for new features
4. Follow code style (use `make format`)
5. Update documentation for changes

## Version Information

**Current Version:** 2.0.0  
**Python:** 3.8+  
**PyQt6:** Latest stable  
**SQLite:** 3.x  
**Status:** Production Ready
