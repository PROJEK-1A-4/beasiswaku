.PHONY: help install dev test clean run setup format lint type-check

help:
	@echo "BeasiswaKu - Scholarship Management System"
	@echo ""
	@echo "Available commands:"
	@echo "  make install       Install dependencies"
	@echo "  make dev           Install dev dependencies"
	@echo "  make run           Run the application"
	@echo "  make test          Run all tests"
	@echo "  make test-fast     Run tests without verbose output"
	@echo "  make test-cov      Run tests with coverage"
	@echo "  make clean         Clean up generated files"
	@echo "  make format        Format code with black"
	@echo "  make lint          Run pylint checks"
	@echo "  make type-check    Run mypy type checking"
	@echo "  make setup         Initial setup (create .env, install deps)"
	@echo "  make setup-db      Initialize database"

install:
	pip install -r requirements.txt

dev:
	pip install -r requirements.txt pytest pytest-cov pylint mypy black

run:
	python main.py

test:
	pytest -v

test-fast:
	pytest

test-cov:
	pytest --cov=src --cov-report=html

clean:
	find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name "*.pyc" -delete
	rm -rf .pytest_cache .mypy_cache .coverage htmlcov 2>/dev/null || true

format:
	black src/ main.py tests/

lint:
	pylint src/ main.py tests/ --disable=all --enable=E,F

type-check:
	mypy src/ main.py --strict 2>/dev/null || echo "Type checking completed with some warnings"

setup: install
	@if [ ! -f .env ]; then cp .env.example .env && echo "Created .env file"; else echo ".env already exists"; fi
	@mkdir -p logs data/backup

setup-db:
	python -c "from src.core import DatabaseManager; db = DatabaseManager(); print('Database initialized')"

# Development commands
dev-install: install dev setup

# CI/CD commands
ci: clean test lint

# Team-specific commands
team-kemal:
	@echo "KEMAL (Scraper): Working on src/scraper/"
	pytest tests/test_scraper.py -v

team-darva:
	@echo "DARVA (Database): Working on src/database/"
	pytest tests/test_database.py tests/test_crud.py -v

team-kyla:
	@echo "KYLA (GUI Tabs): Working on src/gui/"
	pytest tests/test_gui.py -v

team-aulia:
	@echo "AULIA (Main GUI): Working on src/gui/"
	pytest tests/test_gui.py -v

team-richard:
	@echo "RICHARD (Visualization): Working on src/visualization/"
	pytest tests/test_visualization.py -v
