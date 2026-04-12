"""
visualisasi.py - Analytics and Charts Generation
Owner: RICHARD
Project: BeasiswaKu - Personal Scholarship Manager

Tanggung jawab:
- Generate Matplotlib pie charts & bar charts untuk Tab Tracker & Tab Statistik
- Handle data aggregation functions dari crud.py
- Return FigureCanvas (QWidget) agar bisa diembed langsung ke PyQt6 layout
"""

import logging
from datetime import datetime
from collections import defaultdict

import matplotlib
# Konfigurasi matplotlib untuk menggunakan backend PyQt6
matplotlib.use('qtagg')
from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure

from src.database.crud import (
    get_lamaran_list,
    get_beasiswa_per_jenjang,
    get_top_penyelenggara,
    get_status_availability
)

logger = logging.getLogger(__name__)

# Standard color palette sesuai desain aplikasi
COLOR_PALETTE = {
    'Pending': '#FFC107',       # Amber
    'Submitted': '#2196F3',     # Blue
    'Accepted': '#4CAF50',      # Green
    'Rejected': '#F44336',      # Red
    'Withdrawn': '#9E9E9E',     # Grey
    'Buka': '#4CAF50',          # Green
    'Segera Tutup': '#FFC107',  # Yellow
    'Tutup': '#F44336'          # Red
}