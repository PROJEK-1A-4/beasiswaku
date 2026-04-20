#!/usr/bin/env python3
"""Initialization tests using assertion-based pytest style."""

import importlib
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.parent))


def test_required_core_imports():
    """Core modules should be importable without errors."""
    required_modules = [
        "src.core.config",
        "src.database.crud",
        "sqlite3",
    ]

    for module_name in required_modules:
        module = importlib.import_module(module_name)
        assert module is not None
