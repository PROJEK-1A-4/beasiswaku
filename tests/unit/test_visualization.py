#!/usr/bin/env python3
"""Unit tests for visualization module."""

import os
import sys
from pathlib import Path

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

import unittest
from unittest import mock

import matplotlib.pyplot as plt

from src.visualization import visualisasi as viz


class VisualizationTestCase(unittest.TestCase):
    def tearDown(self):
        plt.close("all")


class TestChartBuilders(VisualizationTestCase):
    def test_bar_chart_beasiswa_per_jenjang(self):
        fig, ax = viz.create_bar_chart_beasiswa_per_jenjang({"D3": 2, "S1": 4})
        self.assertEqual(len(ax.patches), 2)
        self.assertIsNotNone(fig)

    def test_bar_chart_beasiswa_per_jenjang_empty(self):
        _, ax = viz.create_bar_chart_beasiswa_per_jenjang({})
        texts = [txt.get_text() for txt in ax.texts]
        self.assertTrue(any("Data tidak tersedia" in text for text in texts))

    def test_bar_chart_top_penyelenggara_limit(self):
        data = [
            {"nama_penyelenggara": "Org A", "total_beasiswa": 8},
            {"nama_penyelenggara": "Org B", "total_beasiswa": 6},
            {"nama_penyelenggara": "Org C", "total_beasiswa": 4},
        ]
        _, ax = viz.create_bar_chart_top_penyelenggara(data, limit=2)
        self.assertEqual(len(ax.patches), 2)

    def test_pie_chart_status_ketersediaan(self):
        _, ax = viz.create_pie_chart_status_ketersediaan({"Buka": 10, "Tutup": 2})
        self.assertEqual(len(ax.patches), 2)

    def test_pie_chart_status_lamaran_empty(self):
        _, ax = viz.create_pie_chart_status_lamaran({})
        texts = [txt.get_text() for txt in ax.texts]
        self.assertTrue(any("Data tidak tersedia" in text for text in texts))

    def test_bar_chart_lamaran_per_bulan(self):
        _, ax = viz.create_bar_chart_lamaran_per_bulan({"2026-01": 1, "2026-02": 3})
        self.assertEqual(len(ax.patches), 2)


class TestDataLoaders(VisualizationTestCase):
    def test_load_statistik_data(self):
        with mock.patch("src.visualization.visualisasi.get_beasiswa_per_jenjang", return_value={"S1": 5}):
            with mock.patch("src.visualization.visualisasi.get_top_penyelenggara", return_value=[{"nama_penyelenggara": "LPDP", "total_beasiswa": 5}]):
                with mock.patch("src.visualization.visualisasi.get_status_availability", return_value={"Buka": 3}):
                    jenjang, top_org, status = viz.load_statistik_data()

        self.assertEqual(jenjang, {"S1": 5})
        self.assertEqual(len(top_org), 1)
        self.assertEqual(status, {"Buka": 3})

    def test_load_tracker_data_aggregate(self):
        fake_rows = [
            {"status": "Pending", "tanggal_daftar": "2026-01-10"},
            {"status": "Accepted", "tanggal_daftar": "2026-01-25"},
            {"status": "Rejected", "tanggal_daftar": "x"},
        ]
        with mock.patch("src.visualization.visualisasi.get_lamaran_list", return_value=(fake_rows, 3)):
            status_counts, month_counts = viz.load_tracker_data(user_id=10)

        self.assertEqual(status_counts["Pending"], 1)
        self.assertEqual(status_counts["Accepted"], 1)
        self.assertEqual(month_counts["2026-01"], 2)
        self.assertEqual(month_counts["Unknown"], 1)

    def test_load_tracker_data_empty(self):
        with mock.patch("src.visualization.visualisasi.get_lamaran_list", return_value=([], 0)):
            status_counts, month_counts = viz.load_tracker_data(user_id=99)
        self.assertEqual(status_counts, {})
        self.assertEqual(month_counts, {})


class TestCanvasBuilders(VisualizationTestCase):
    def test_figure_to_canvas(self):
        fig, _ = plt.subplots()
        canvas = viz.figure_to_canvas(fig)
        self.assertIsInstance(canvas, viz.FigureCanvas)

    def test_build_statistik_canvases(self):
        with mock.patch(
            "src.visualization.visualisasi.load_statistik_data",
            return_value=(
                {"S1": 4},
                [{"nama_penyelenggara": "LPDP", "total_beasiswa": 4}],
                {"Buka": 4},
            ),
        ):
            canvases = viz.build_statistik_canvases()

        self.assertEqual(
            set(canvases.keys()),
            {"canvas_jenjang", "canvas_penyelenggara", "canvas_status"},
        )

    def test_build_tracker_canvases(self):
        with mock.patch(
            "src.visualization.visualisasi.load_tracker_data",
            return_value=({"Pending": 2}, {"2026-01": 2}),
        ):
            canvases = viz.build_tracker_canvases(user_id=1)

        self.assertEqual(
            set(canvases.keys()),
            {"canvas_lamaran_status", "canvas_lamaran_bulanan"},
        )


if __name__ == "__main__":
    unittest.main(verbosity=2)
