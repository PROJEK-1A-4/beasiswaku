"""Shared status normalization utilities for UI and analytics."""

from typing import Iterable, Mapping, Dict

SCHOLARSHIP_STATUS_ORDER = ("Buka", "Segera Tutup", "Tutup")
APPLICATION_STATUS_ORDER = ("Pending", "Diterima", "Ditolak")


def normalize_scholarship_status(status: str) -> str:
    """Map arbitrary scholarship status text into canonical UI labels."""
    normalized = (status or "").strip().lower()

    if normalized in {"buka", "open", "aktif"}:
        return "Buka"
    if normalized in {"segera tutup", "closing", "closing soon", "deadline dekat"}:
        return "Segera Tutup"
    if normalized in {"tutup", "closed"}:
        return "Tutup"
    return "Buka"


def normalize_application_status(status: str) -> str:
    """Map backend lamaran status variants into canonical UI labels."""
    normalized = (status or "").strip().lower()

    if normalized in {"accepted", "diterima"}:
        return "Diterima"
    if normalized in {"rejected", "ditolak", "withdrawn"}:
        return "Ditolak"
    return "Pending"


def ordered_counts(raw_counts: Mapping[str, int], labels: Iterable[str]) -> Dict[str, int]:
    """Build a deterministic count map in the requested label order."""
    result = {label: 0 for label in labels}
    for key, value in raw_counts.items():
        if key in result:
            result[key] += int(value or 0)
    return result
