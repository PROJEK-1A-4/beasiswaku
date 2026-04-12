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