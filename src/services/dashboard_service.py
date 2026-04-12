"""Data service for tracker and statistik tabs."""

from collections import Counter
from datetime import datetime
from typing import Any, Dict, List, Optional, Tuple

from src.database.crud import (
    get_beasiswa_list,
    get_beasiswa_per_jenjang,
    get_lamaran_list,
    get_status_availability,
    get_top_penyelenggara,
)
from src.services.status_utils import (
    APPLICATION_STATUS_ORDER,
    SCHOLARSHIP_STATUS_ORDER,
    normalize_application_status,
    normalize_scholarship_status,
    ordered_counts,
)


def _format_date(raw_date: Any) -> Tuple[str, Optional[str]]:
    """Return human-friendly date and YYYY-MM bucket for chart aggregation."""
    if not raw_date:
        return "-", None

    raw_text = str(raw_date).strip()
    if not raw_text:
        return "-", None

    for fmt in ("%Y-%m-%d", "%Y-%m-%d %H:%M:%S"):
        try:
            parsed = datetime.strptime(raw_text, fmt)
            return parsed.strftime("%d %b %Y"), parsed.strftime("%Y-%m")
        except ValueError:
            continue

    # Fallback for values that still contain YYYY-MM prefix.
    month_key = raw_text[:7] if len(raw_text) >= 7 else None
    return raw_text, month_key


def get_tracker_snapshot(user_id: int) -> Dict[str, Any]:
    """Return normalized tracker table rows and aggregate charts data."""
    lamaran_rows, _ = get_lamaran_list(
        filter_user_id=user_id,
        sort_by="tanggal_daftar",
        sort_order="DESC",
    )

    applications: List[Dict[str, Any]] = []
    status_counter: Counter = Counter()
    month_counter: Counter = Counter()

    for row in lamaran_rows:
        display_date, month_key = _format_date(row.get("tanggal_daftar"))
        status = normalize_application_status(row.get("status"))

        applications.append(
            {
                "id": row.get("id"),
                "nama": row.get("beasiswa_judul") or "(Tanpa Judul)",
                "tanggal": display_date,
                "status": status,
                "catatan": row.get("catatan") or "-",
                "month_key": month_key,
            }
        )

        status_counter[status] += 1
        if month_key:
            month_counter[month_key] += 1

    return {
        "applications": applications,
        "status_counts": ordered_counts(status_counter, APPLICATION_STATUS_ORDER),
        "month_counts": dict(sorted(month_counter.items())),
    }


def get_statistik_snapshot(top_limit: int = 5) -> Dict[str, Any]:
    """Return normalized statistik datasets for cards and charts."""
    _, total_beasiswa = get_beasiswa_list()

    raw_status_counts = get_status_availability()
    normalized_status_counter: Counter = Counter()
    for key, value in raw_status_counts.items():
        normalized_status_counter[normalize_scholarship_status(key)] += int(value or 0)

    jenjang_counts = {
        str(key): int(value)
        for key, value in get_beasiswa_per_jenjang().items()
        if key
    }

    penyelenggara_counts = [
        {
            "nama_penyelenggara": item.get("nama_penyelenggara") or "(Tidak Ada)",
            "count": int(item.get("total_beasiswa") or 0),
        }
        for item in get_top_penyelenggara(limit=top_limit)
    ]

    return {
        "total": int(total_beasiswa or 0),
        "status_counts": ordered_counts(normalized_status_counter, SCHOLARSHIP_STATUS_ORDER),
        "jenjang_counts": jenjang_counts,
        "penyelenggara_counts": penyelenggara_counts,
    }
