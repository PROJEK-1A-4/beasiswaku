# Modul visualisasi Beasiswaku 
# Peran:
# 1. Mengambil data statistik/tracker dari CRUD.
# 2. Mengubah data menjadi chart.
# 3. Menampilkan chart di dashbord pengguna.
# 4. Mengembalikan Figure untuk dipasang ke PyQt6.

from __future__ import annotations

from collections import Counter
from datetime import datetime
from typing import Dict, List, Tuple

import matplotlib.pyplot as plt

# FigureCanvas untuk integrasi Matplotlib ke PyQt6
try:
    from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg as FigureCanvas
except Exception:
    from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas

# Import data layer (CRUD) sebagai sumber data yang resmi
from src.database.crud import (
    get_beasiswa_per_jenjang,
    get_top_penyelenggara,
    get_status_availability,
    get_lamaran_list,
)
# Menyusun variasi warna untuk chart agar tampilan seragam dan menarik.
COLOR_PALETTE = {
    # Status beasiswa
    "Buka": "#2E7D32",
    "Segera Tutup": "#F9A825",
    "Tutup": "#C62828",
    # Status lamaran
    "Pending": "#546E7A",
    "Submitted": "#1E88E5",
    "Accepted": "#2E7D32",
    "Rejected": "#C62828",
    "Withdrawn": "#8E24AA",
    # Utility
    "bar_default": "#1E88E5",
    "bar_secondary": "#26A69A",
    "grid": "#D9D9D9",
    "empty_text": "#777777",
}

def _apply_axis_style(ax) -> None:
    """
    Fungsi helper internal untuk merapikan style sumbu chart.

    Alasan ada fungsi ini:
    - Agar semua chart memiliki style yang konsisten.
    - Menghindari duplikasi kode styling di setiap fungsi chart.
    """
    ax.grid(axis="y", linestyle="--", alpha=0.35, color=COLOR_PALETTE["grid"])
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)

    