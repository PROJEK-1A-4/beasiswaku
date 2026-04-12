"""Data service for beasiswa tab table rendering."""

import logging
from typing import Any, Dict, List

from src.database.crud import get_connection
from src.services.status_utils import normalize_scholarship_status

logger = logging.getLogger(__name__)


def get_beasiswa_table_data() -> List[Dict[str, Any]]:
    """Fetch scholarship rows with organizer names for tabular UI."""
    try:
        conn = get_connection()
        cursor = conn.cursor()

        cursor.execute(
            """
            SELECT b.id, b.judul, p.nama, b.jenjang, b.deadline, b.status
            FROM beasiswa b
            LEFT JOIN penyelenggara p ON b.penyelenggara_id = p.id
            ORDER BY b.deadline ASC
            """
        )

        rows = cursor.fetchall()
        cursor.close()

        data: List[Dict[str, Any]] = []
        for row in rows:
            data.append(
                {
                    "id": row[0],
                    "nama": row[1] or "(Tanpa Judul)",
                    "penyelenggara": row[2] or "Tidak Ada",
                    "jenjang": row[3] or "-",
                    "deadline": row[4] or "-",
                    "status": normalize_scholarship_status(row[5]),
                }
            )

        return data
    except Exception as exc:
        logger.error("Error loading beasiswa table data: %s", exc)
        return []
