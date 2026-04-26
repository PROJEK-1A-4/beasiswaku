"""
Test P2-05: Integrasi Alur Statistik dan Tracker dengan Standardisasi Status.
Memastikan implementasi P2-02 di status_utils.py berfungsi end-to-end saat data ditarik.
"""

import sys
import pytest
import logging
from pathlib import Path

project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from src.database.crud import (
    init_db, register_user, add_beasiswa, add_lamaran, get_connection
)
from src.services.dashboard_service import get_statistik_snapshot, get_tracker_snapshot
from src.services.status_utils import SCHOLARSHIP_STATUS_ORDER, APPLICATION_STATUS_ORDER

logger = logging.getLogger(__name__)

class TestStatusStandardizationFlow:

    @pytest.fixture(autouse=True)
    def setup_database(self, isolated_database):
        """Fixture menggunakan test DB yang terisolasi dari conftest.py"""
        self.user_id = register_user("test_status", "test@status.com", "Pass123", "User Status", "S1")

        # Insert ragam data mentah dengan variasi status text (menguji normalizer)
        add_beasiswa(judul="Beasiswa A", jenjang="S1", deadline="2026-12-31", status="buka", penyelenggara_id=None)
        add_beasiswa(judul="Beasiswa B", jenjang="S1", deadline="2026-12-31", status="closing soon", penyelenggara_id=None)
        add_beasiswa(judul="Beasiswa C", jenjang="S1", deadline="2025-01-01", status="closed", penyelenggara_id=None)

        # Insert lamaran dengan variasi status mentah
        add_lamaran(user_id=self.user_id, beasiswa_id=1, status="Pending", catatan="")
        add_lamaran(user_id=self.user_id, beasiswa_id=2, status="accepted", catatan="")
        add_lamaran(user_id=self.user_id, beasiswa_id=3, status="withdrawn", catatan="")

    def test_statistik_status_normalization(self):
        """Memastikan get_statistik_snapshot mengembalikan status beasiswa yang baku"""
        snapshot = get_statistik_snapshot()
        status_counts = snapshot.get("status_counts", {})

        # Memastikan tidak ada key aneh seperti "closing soon" atau "closed" di dictionary
        for key in status_counts.keys():
            assert key in SCHOLARSHIP_STATUS_ORDER, f"Status mentah {key} bocor ke UI Statistik!"

        assert status_counts["Buka"] == 1
        assert status_counts["Segera Tutup"] == 1
        assert status_counts["Tutup"] == 1

    def test_tracker_status_normalization(self):
        """Memastikan get_tracker_snapshot mengembalikan status lamaran yang baku"""
        snapshot = get_tracker_snapshot(self.user_id)
        status_counts = snapshot.get("status_counts", {})

        # Memastikan status mentah seperti "accepted" atau "withdrawn" berubah jadi standar UI
        for key in status_counts.keys():
            assert key in APPLICATION_STATUS_ORDER, f"Status lamaran mentah {key} bocor ke UI Tracker!"

        assert status_counts["Pending"] == 1
        assert status_counts["Diterima"] == 1
        assert status_counts["Ditolak"] == 1

        logger.info("✅ Alur integrasi Statistik & Tracker dengan Normalisasi Status sukses!")