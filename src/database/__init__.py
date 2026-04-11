"""
Database module - CRUD operations for all entities
Owner: DARVA
"""

from .crud import *

__all__ = [
    "create_beasiswa",
    "get_beasiswa",
    "update_beasiswa",
    "delete_beasiswa",
    "create_lamaran",
    "get_lamaran",
    "update_lamaran",
    "delete_lamaran",
    "create_favorit",
    "get_favorit",
    "delete_favorit",
    "create_notes",
    "update_notes",
]
