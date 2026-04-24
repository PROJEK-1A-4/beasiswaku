#!/usr/bin/env python3
"""Unit tests for scraper module (network mocked)."""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.parent))

import json
import tempfile
import unittest
from datetime import datetime, timedelta
from unittest import mock

from bs4 import BeautifulSoup

from src.scraper import scraper


class TestScraperHelpers(unittest.TestCase):
    def test_clean_text(self):
        self.assertEqual(scraper.clean_text("  Halo   Dunia  "), "Halo Dunia")
        self.assertEqual(scraper.clean_text(""), "")

    def test_normalize_url(self):
        self.assertEqual(scraper.normalize_url(""), "")
        self.assertEqual(scraper.normalize_url("https://example.com/a"), "https://example.com/a")
        self.assertEqual(
            scraper.normalize_url("/beasiswa/a"),
            f"{scraper.BASE_URL}/beasiswa/a",
        )
        self.assertEqual(
            scraper.normalize_url("beasiswa/a"),
            f"{scraper.BASE_URL}/beasiswa/a",
        )

    def test_detect_penyelenggara_type(self):
        self.assertEqual(scraper.detect_penyelenggara_type("LPDP RI"), "Pemerintah")
        self.assertEqual(scraper.detect_penyelenggara_type("British Council"), "Internasional")
        self.assertEqual(scraper.detect_penyelenggara_type("Yayasan Pendidikan"), "Swasta")

    def test_get_max_pages_for_category(self):
        self.assertEqual(scraper.get_max_pages_for_category("s1"), scraper.MAX_PAGES_CONFIG["s1"])
        self.assertEqual(scraper.get_max_pages_for_category("unknown"), 1)


class TestDeadlineAndStatus(unittest.TestCase):
    def test_parse_deadline_formats(self):
        cases = {
            "10 Juni 2026": "2026-06-10",
            "5 jan 25": "2025-01-05",
            "31 DEC 2027": "2027-12-31",
            "Tidak Diketahui": "0000-00-00",
            "deadline segera": "0000-00-00",
        }
        for raw, expected in cases.items():
            with self.subTest(raw=raw):
                self.assertEqual(scraper.parse_deadline(raw), expected)

    def test_determine_status_buka(self):
        target = (datetime.now() + timedelta(days=9)).strftime("%Y-%m-%d")
        with mock.patch.object(scraper, "parse_deadline", return_value=target):
            self.assertEqual(scraper.determine_status("apa saja"), "Buka")

    def test_determine_status_segera_tutup(self):
        target = (datetime.now() + timedelta(days=2)).strftime("%Y-%m-%d")
        with mock.patch.object(scraper, "parse_deadline", return_value=target):
            self.assertEqual(scraper.determine_status("apa saja"), "Segera Tutup")

    def test_determine_status_tutup(self):
        target = (datetime.now() - timedelta(days=1)).strftime("%Y-%m-%d")
        with mock.patch.object(scraper, "parse_deadline", return_value=target):
            self.assertEqual(scraper.determine_status("apa saja"), "Tutup")


class TestExtraction(unittest.TestCase):
    def test_extract_penyelenggara(self):
        result = scraper.extract_penyelenggara(
            "Beasiswa LPDP Tahun 2027",
            "Program pendidikan",
        )
        self.assertEqual(result, "LPDP")

    def test_extract_beasiswa_info_from_html(self):
        html = """
        <article class="type-post">
            <h2 class="entry-title">Beasiswa LPDP 2027</h2>
            <a href="/lpdp" title="DEADLINE: 10 Juni 2027">Lihat</a>
            <div class="entry-content">Program untuk mahasiswa berprestasi.</div>
        </article>
        """
        item = BeautifulSoup(html, "html.parser").select_one(".type-post")
        data = scraper.extract_beasiswa_info(item, "s1")

        self.assertIsNotNone(data)
        self.assertEqual(data["nama"], "Beasiswa LPDP 2027")
        self.assertEqual(data["jenjang"], "S1")
        self.assertEqual(data["deadline"], "2027-06-10")
        self.assertTrue(data["link"].startswith(scraper.BASE_URL))


class TestCategoryScraping(unittest.TestCase):
    def _fake_response(self, html: str):
        response = mock.Mock()
        response.content = html.encode("utf-8")
        response.raise_for_status.return_value = None
        return response

    def test_scrape_category_with_pagination(self):
        page1 = """
        <article class="type-post">
            <h2 class="entry-title">A</h2>
            <a href="/a" title="DEADLINE: 10 Juni 2028">Link</a>
            <div class="entry-content">Desc A</div>
        </article>
        """
        page2 = """
        <article class="type-post">
            <h2 class="entry-title">B</h2>
            <a href="/b" title="DEADLINE: 11 Juni 2028">Link</a>
            <div class="entry-content">Desc B</div>
        </article>
        """

        def _side_effect(url, headers=None, timeout=None):
            if "/page/2/" in url:
                return self._fake_response(page2)
            return self._fake_response(page1)

        with mock.patch.dict(scraper.MAX_PAGES_CONFIG, {"s1": 2}, clear=False):
            with mock.patch("src.scraper.scraper.requests.get", side_effect=_side_effect) as mocked_get:
                with mock.patch("src.scraper.scraper.time.sleep", return_value=None):
                    result = scraper.scrape_category("beasiswa-s1", "s1")

        self.assertEqual(len(result), 2)
        self.assertEqual(mocked_get.call_count, 2)


class TestOrchestration(unittest.TestCase):
    def test_scrape_beasiswa_data_aggregate(self):
        fake_s1 = [{"nama": "A", "penyelenggara": "LPDP"}]
        fake_s2 = [
            {"nama": "B", "penyelenggara": "LPDP"},
            {"nama": "C", "penyelenggara": "British Council"},
        ]

        def _fake_scrape(slug, category_name):
            if category_name == "s1":
                return fake_s1
            return fake_s2

        with mock.patch.dict(
            scraper.CATEGORIES,
            {"s1": "beasiswa-s1", "s2": "beasiswa-s2"},
            clear=True,
        ):
            with mock.patch("src.scraper.scraper.scrape_category", side_effect=_fake_scrape):
                with mock.patch("src.scraper.scraper.save_backup", return_value={}) as mocked_backup:
                    result = scraper.scrape_beasiswa_data()

        self.assertEqual(len(result["beasiswa"]), 3)
        self.assertEqual(len(result["penyelenggara"]), 2)
        mocked_backup.assert_called_once()

    def test_save_backup_creates_files(self):
        data = {
            "beasiswa": [{"nama": "A"}],
            "penyelenggara": [{"nama": "LPDP"}],
            "timestamp": datetime.now().isoformat(),
            "total_beasiswa": 1,
            "total_penyelenggara": 1,
        }

        with tempfile.TemporaryDirectory() as temp_dir:
            with mock.patch.object(scraper, "BACKUP_DIR", temp_dir):
                status = scraper.save_backup(data)

            self.assertEqual(status.get("beasiswa.json"), "✅")
            self.assertEqual(status.get("penyelenggara.json"), "✅")
            self.assertEqual(status.get("riwayat_lamaran.json"), "✅")

            beasiswa_path = Path(temp_dir) / "beasiswa.json"
            metadata_path = Path(temp_dir) / "_metadata.json"

            self.assertTrue(beasiswa_path.exists())
            self.assertTrue(metadata_path.exists())

            with beasiswa_path.open("r", encoding="utf-8") as handle:
                parsed = json.load(handle)
            self.assertEqual(len(parsed), 1)

    def test_get_scraper_thread_factory(self):
        thread = scraper.get_scraper_thread()
        if scraper.PYQT_AVAILABLE:
            self.assertIsNotNone(thread)
        else:
            self.assertIsNone(thread)


if __name__ == "__main__":
    unittest.main(verbosity=2)
