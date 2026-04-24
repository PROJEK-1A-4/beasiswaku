"""Data service for tracker, statistik, and beranda tabs."""

from collections import Counter
from datetime import date, datetime, timedelta
import re
import logging
from typing import Any, Dict, List, Optional, Tuple

# Centralized logging
logger = logging.getLogger(__name__)

from src.database.crud import (
    get_connection,
    get_beasiswa_list,
    get_beasiswa_per_jenjang,
    get_favorit_list,
    get_lamaran_list,
    get_status_availability,
    get_top_penyelenggara,
)
from src.scraper.scraper import scrape_beasiswa_data
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


def _parse_iso_date(raw_date: Any) -> Optional[date]:
    """Parse YYYY-MM-DD (or datetime-like string) into date."""
    if not raw_date:
        return None

    raw_text = str(raw_date).strip()
    if not raw_text:
        return None

    raw_head = raw_text.split(" ")[0]
    try:
        return datetime.strptime(raw_head, "%Y-%m-%d").date()
    except ValueError:
        return None


def _format_days_left(days_left: int) -> str:
    """Convert day delta into human-friendly Indonesian text."""
    if days_left < 0:
        return "Sudah tutup"
    if days_left == 0:
        return "Tutup hari ini"
    if days_left == 1:
        return "Tutup dalam 1 hari"
    return f"Tutup dalam {days_left} hari"


def _relative_time(raw_ts: Any) -> str:
    """Best-effort relative time formatter for activity timeline."""
    if not raw_ts:
        return "baru saja"

    raw_text = str(raw_ts).strip()
    if not raw_text:
        return "baru saja"

    parsed: Optional[datetime] = None
    for fmt in ("%Y-%m-%d %H:%M:%S", "%Y-%m-%d"):
        try:
            parsed = datetime.strptime(raw_text.split(".")[0], fmt)
            break
        except ValueError:
            continue

    if parsed is None:
        return raw_text

    delta = datetime.now() - parsed
    if delta.days >= 7:
        weeks = delta.days // 7
        return f"{weeks} minggu lalu"
    if delta.days >= 1:
        return f"{delta.days} hari lalu"
    hours = max(int(delta.total_seconds() // 3600), 0)
    if hours >= 1:
        return f"{hours} jam lalu"
    minutes = max(int(delta.total_seconds() // 60), 0)
    if minutes >= 1:
        return f"{minutes} menit lalu"
    return "baru saja"


def _format_deadline_label(raw_deadline: Any) -> str:
    """Format deadline date into compact human-readable Indonesian-friendly label."""
    parsed = _parse_iso_date(raw_deadline)
    if parsed is None:
        return "-"
    return parsed.strftime("%d %b %Y")


def _clean_favorite_title(raw_title: Any) -> str:
    """Clean noisy scraped title suffixes so favorite cards stay readable."""
    title = str(raw_title or "").strip()
    if not title:
        return "(Tanpa Judul)"

    title = re.sub(r"\s*\(\s*deadline\s*:[^)]+\)\s*$", "", title, flags=re.IGNORECASE)
    title = re.sub(r"\s+-\s*deadline\s*[:\-].*$", "", title, flags=re.IGNORECASE)
    return title.strip()


def get_beranda_snapshot(
    user_id: int,
    deadline_limit: int = 3,
    favorite_limit: int = 5,
    activity_limit: int = 5,
) -> Dict[str, Any]:
    """Return consolidated beranda data sourced from database records."""
    conn = get_connection()
    cursor = conn.cursor()

    today = datetime.now().date()

    cursor.execute(
        """
        SELECT b.id, b.judul, COALESCE(p.nama, 'Tidak Ada') as penyelenggara,
               b.jenjang, b.deadline, b.status
        FROM beasiswa b
        LEFT JOIN penyelenggara p ON b.penyelenggara_id = p.id
        ORDER BY b.deadline ASC, b.id DESC
        """
    )
    beasiswa_rows = cursor.fetchall()
    cursor.close()

    deadline_cards: List[Dict[str, str]] = []
    deadline_week_count = 0

    for row in beasiswa_rows:
        status = normalize_scholarship_status(row[5])
        deadline_date = _parse_iso_date(row[4])
        if not deadline_date:
            continue

        days_left = (deadline_date - today).days
        if 0 <= days_left <= 7:
            deadline_week_count += 1

        if status == "Tutup" or days_left < 0:
            continue

        if days_left <= 14:
            urgency = "urgent" if days_left <= 3 else "warning"
            deadline_cards.append(
                {
                    "judul": row[1] or "(Tanpa Judul)",
                    "penyelenggara": row[2] or "Tidak Ada",
                    "jenjang": row[3] or "-",
                    "deadline": _format_days_left(days_left),
                    "urgency": urgency,
                }
            )

    deadline_cards = deadline_cards[: max(deadline_limit, 0)]

    lamaran_rows, total_lamaran = get_lamaran_list(
        filter_user_id=user_id,
        sort_by="created_at",
        sort_order="DESC",
    )

    accepted_count = 0
    activities: List[Dict[str, str]] = []
    emoji_by_status = {
        "Pending": "🟠",
        "Diterima": "✅",
        "Ditolak": "❌",
    }

    for row in lamaran_rows:
        normalized_status = normalize_application_status(row.get("status"))
        if normalized_status == "Diterima":
            accepted_count += 1

        if len(activities) < max(activity_limit, 0):
            activities.append(
                {
                    "emoji": emoji_by_status.get(normalized_status, "ℹ️"),
                    "title": f"Lamaran: {row.get('beasiswa_judul') or '(Tanpa Judul)'}",
                    "description": f"Status: {normalized_status}",
                    "status": normalized_status,
                    "time": _relative_time(row.get("created_at") or row.get("tanggal_daftar")),
                }
            )

    favorit_rows, _ = get_favorit_list(user_id=user_id, sort_by="created_at", sort_order="DESC")
    favorites: List[Dict[str, str]] = []
    for row in favorit_rows[: max(favorite_limit, 0)]:
        provider = row.get("penyelenggara") or "Penyelenggara tidak diketahui"
        deadline_label = _format_deadline_label(row.get("deadline"))
        description = f"{row.get('jenjang') or '-'} • {provider}"
        if deadline_label != "-":
            description = f"{description} • Deadline {deadline_label}"

        favorites.append(
            {
                "emoji": "⭐",
                "title": _clean_favorite_title(row.get("judul")),
                "description": description,
                "provider": provider,
                "jenjang": row.get("jenjang") or "-",
                "deadline": deadline_label,
                "status": normalize_scholarship_status(row.get("status")),
            }
        )

    if deadline_week_count > 0:
        alert_message = (
            f"Ada {deadline_week_count} beasiswa yang deadline-nya minggu ini. "
            "Jangan sampai terlewat!"
        )
    else:
        alert_message = "Tidak ada deadline kritis minggu ini. Tetap pantau beasiswa baru!"

    return {
        "last_updated": datetime.now().strftime("%d %b %Y %H:%M"),
        "stats": {
            "total_beasiswa": len(beasiswa_rows),
            "deadline_minggu_ini": deadline_week_count,
            "total_lamaran": int(total_lamaran or 0),
            "diterima": accepted_count,
        },
        "alert_message": alert_message,
        "deadline_cards": deadline_cards,
        "favorites": favorites,
        "activities": activities,
    }


def _normalize_jenjang_for_db(raw_jenjang: Any, judul: str) -> str:
    """Map scraper category labels into jenjang values accepted by CRUD."""
    text = str(raw_jenjang or "").strip().upper()
    if text in {"D3", "D4", "S1", "S2"}:
        return text
    if "DIPLOMA" in text:
        return "D3"

    title_upper = (judul or "").upper()
    for jenjang in ("D4", "D3", "S2", "S1"):
        if jenjang in title_upper:
            return jenjang

    # Fallback keeps the record usable in existing filters.
    return "S1"


def _normalize_deadline_for_db(raw_deadline: Any) -> str:
    """Ensure deadline is a valid YYYY-MM-DD accepted by add_beasiswa."""
    deadline = _parse_iso_date(raw_deadline)
    if deadline is None:
        deadline = datetime.now().date() + timedelta(days=90)
    return deadline.strftime("%Y-%m-%d")


def sync_beasiswa_from_scraper(scrape_result: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    """Scrape latest scholarships and upsert into DB without duplicating by title+jenjang.
    
    Return:
        Dict with structure:
        {
            "scraped": int,
            "inserted": int,
            "updated": int,
            "skipped": int,
            "errors": int,
            "error_details": [{"judul": str, "alasan": str}, ...]
        }
    """
    payload = scrape_result or scrape_beasiswa_data()
    scraped_rows = payload.get("beasiswa", []) if isinstance(payload, dict) else []

    conn = get_connection()
    cursor = conn.cursor()

    inserted = 0
    updated = 0
    skipped = 0
    errors = 0
    error_details = []

    try:
        logger.info(f"🔄 Syncing {len(scraped_rows)} scraped beasiswa to database...")
        
        for idx, item in enumerate(scraped_rows, 1):
            judul = str(item.get("nama") or "").strip()
            if not judul:
                skipped += 1
                continue

            try:
                jenjang = _normalize_jenjang_for_db(item.get("jenjang"), judul)
                deadline = _normalize_deadline_for_db(item.get("deadline"))
                status = normalize_scholarship_status(item.get("status"))
                deskripsi = str(item.get("deskripsi") or "").strip()
                link_aplikasi = str(item.get("link") or "").strip()
                penyelenggara_nama = str(item.get("penyelenggara") or "").strip()

                penyelenggara_id = None
                if penyelenggara_nama and penyelenggara_nama.lower() != "tidak diketahui":
                    cursor.execute(
                        "SELECT id FROM penyelenggara WHERE lower(nama) = lower(?) ORDER BY id ASC LIMIT 1",
                        (penyelenggara_nama,),
                    )
                    provider_row = cursor.fetchone()
                    if provider_row:
                        penyelenggara_id = provider_row[0]
                    else:
                        cursor.execute(
                            "INSERT INTO penyelenggara (nama) VALUES (?)",
                            (penyelenggara_nama,),
                        )
                        penyelenggara_id = cursor.lastrowid

                cursor.execute(
                    """
                    SELECT id FROM beasiswa
                    WHERE lower(judul) = lower(?) AND jenjang = ?
                    ORDER BY id ASC
                    LIMIT 1
                    """,
                    (judul, jenjang),
                )
                existing = cursor.fetchone()

                if existing:
                    cursor.execute(
                        """
                        UPDATE beasiswa
                        SET penyelenggara_id = ?, deadline = ?, deskripsi = ?, status = ?,
                            link_aplikasi = ?, scrape_date = CURRENT_TIMESTAMP,
                            updated_at = CURRENT_TIMESTAMP
                        WHERE id = ?
                        """,
                        (
                            penyelenggara_id,
                            deadline,
                            deskripsi,
                            status,
                            link_aplikasi,
                            existing[0],
                        ),
                    )
                    updated += 1
                    logger.debug(f"  [{idx}/{len(scraped_rows)}] ✅ Updated: {judul}")
                else:
                    cursor.execute(
                        """
                        INSERT INTO beasiswa (
                            judul, penyelenggara_id, jenjang, deadline,
                            deskripsi, status, link_aplikasi, scrape_date
                        ) VALUES (?, ?, ?, ?, ?, ?, ?, CURRENT_TIMESTAMP)
                        """,
                        (
                            judul,
                            penyelenggara_id,
                            jenjang,
                            deadline,
                            deskripsi,
                            status,
                            link_aplikasi,
                        ),
                    )
                    inserted += 1
                    logger.debug(f"  [{idx}/{len(scraped_rows)}] ✅ Inserted: {judul}")

            except ValueError as e:
                errors += 1
                error_reason = f"Validation error: {str(e)}"
                error_details.append({"judul": judul, "alasan": error_reason})
                logger.warning(f"  [{idx}/{len(scraped_rows)}] ❌ {judul} - {error_reason}")
            
            except KeyError as e:
                errors += 1
                error_reason = f"Missing required field: {str(e)}"
                error_details.append({"judul": judul, "alasan": error_reason})
                logger.warning(f"  [{idx}/{len(scraped_rows)}] ❌ {judul} - {error_reason}")
            
            except Exception as e:
                errors += 1
                error_reason = f"{type(e).__name__}: {str(e)}"
                error_details.append({"judul": judul, "alasan": error_reason})
                logger.error(f"  [{idx}/{len(scraped_rows)}] ❌ {judul} - {error_reason}", exc_info=False)

        conn.commit()
        logger.info(f"✅ Sync complete: {inserted} inserted, {updated} updated, {errors} errors, {skipped} skipped")

        return {
            "scraped": len(scraped_rows),
            "inserted": inserted,
            "updated": updated,
            "skipped": skipped,
            "errors": errors,
            "error_details": error_details,
        }
    except Exception as e:
        error_msg = f"Sync transaction failed: {type(e).__name__}: {str(e)}"
        logger.error(f"🔴 {error_msg}", exc_info=False)
        conn.rollback()
        return {
            "scraped": len(scraped_rows),
            "inserted": inserted,
            "updated": updated,
            "skipped": skipped,
            "errors": errors + 1,
            "error_details": error_details,
            "transaction_error": error_msg,
        }
    finally:
        cursor.close()
