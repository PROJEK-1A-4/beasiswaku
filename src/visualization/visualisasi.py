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

def create_empty_canvas(message: str = "Tidak ada data") -> FigureCanvas:
    """Helper untuk membuat canvas kosong dengan pesan (jika data belum ada)."""
    fig = Figure(figsize=(5, 4), dpi=100)
    ax = fig.add_subplot(111)
    ax.text(0.5, 0.5, message, ha='center', va='center', fontsize=12, color='gray')
    ax.axis('off')
    return FigureCanvas(fig)


# ============================================================================
# CHARTS UNTUK TAB TRACKER LAMARAN
# ============================================================================

def create_pie_chart_lamaran(user_id: int) -> FigureCanvas:
    """
    Pie chart: Proporsi status lamaran user (Pending / Accepted / Rejected / etc).
    """
    try:
        lamarans, total = get_lamaran_list(filter_user_id=user_id)
        
        if total == 0:
            return create_empty_canvas("Belum ada data lamaran")

        # Agregasi data
        status_counts = defaultdict(int)
        for lamaran in lamarans:
            status = lamaran.get('status', 'Pending')
            status_counts[status] += 1

        labels = list(status_counts.keys())
        sizes = list(status_counts.values())
        colors = [COLOR_PALETTE.get(status, '#CCCCCC') for status in labels]

        # Generate grafik
        fig = Figure(figsize=(5, 4), dpi=100)
        ax = fig.add_subplot(111)
        
        wedges, texts, autotexts = ax.pie(
            sizes, labels=labels, colors=colors, 
            autopct='%1.1f%%', startangle=90,
            wedgeprops={'edgecolor': 'white', 'linewidth': 1}
        )
        
        ax.set_title('Proporsi Status Lamaran', fontsize=12, pad=15, fontweight='bold')
        fig.tight_layout()
        
        logger.info(f"✅ Pie chart lamaran berhasil di-generate untuk user {user_id}")
        return FigureCanvas(fig)
        
    except Exception as e:
        logger.error(f"❌ Error generating pie chart lamaran: {e}")
        return create_empty_canvas("Gagal memuat grafik")


def create_bar_chart_lamaran_per_bulan(user_id: int) -> FigureCanvas:
    """
    Bar chart: Tren jumlah lamaran per bulan.
    """
    try:
        lamarans, total = get_lamaran_list(filter_user_id=user_id)
        
        if total == 0:
            return create_empty_canvas("Belum ada data lamaran")

        # Agregasi data by YYYY-MM
        monthly_counts = defaultdict(int)
        for lamaran in lamarans:
            tgl_daftar = lamaran.get('tanggal_daftar')
            if tgl_daftar:
                # Ambil YYYY-MM
                bulan = tgl_daftar[:7]
                monthly_counts[bulan] += 1

        if not monthly_counts:
            return create_empty_canvas("Data tanggal tidak valid")

        # Sortir secara kronologis
        sorted_months = sorted(monthly_counts.keys())
        counts = [monthly_counts[m] for m in sorted_months]

        # Ubah format YYYY-MM ke format yang lebih mudah dibaca (e.g. "Jan 2026")
        formatted_months = []
        for m in sorted_months:
            dt = datetime.strptime(m, "%Y-%m")
            formatted_months.append(dt.strftime("%b %Y"))

        # Generate grafik
        fig = Figure(figsize=(6, 4), dpi=100)
        ax = fig.add_subplot(111)
        
        bars = ax.bar(formatted_months, counts, color='#2196F3', width=0.6)
        
        # Tambahkan label angka di atas tiap bar
        for bar in bars:
            height = bar.get_height()
            ax.text(bar.get_x() + bar.get_width()/2., height,
                    f'{int(height)}',
                    ha='center', va='bottom')

        ax.set_title('Tren Lamaran per Bulan', fontsize=12, pad=15, fontweight='bold')
        ax.set_ylabel('Jumlah Beasiswa')
        
        # Rotate x labels if there are too many
        if len(formatted_months) > 4:
            ax.tick_params(axis='x', rotation=45)
            
        fig.tight_layout()
        
        logger.info(f"✅ Bar chart tren lamaran berhasil di-generate untuk user {user_id}")
        return FigureCanvas(fig)

    except Exception as e:
        logger.error(f"❌ Error generating bar chart lamaran: {e}")
        return create_empty_canvas("Gagal memuat grafik")