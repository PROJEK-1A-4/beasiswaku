"""
Tracker Lamaran (Application Tracker) Tab for BeasiswaKu
Track scholarship applications with status visualization and analytics
"""

import logging
from typing import List, Dict, Any
from datetime import datetime
import matplotlib.pyplot as plt
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
import numpy as np

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QTableWidget, QTableWidgetItem,
    QPushButton, QHeaderView, QFrame, QAbstractItemView, QGridLayout, QScrollArea
)
from PyQt6.QtCore import Qt, QSize
from PyQt6.QtGui import QFont, QColor

from src.gui.design_tokens import *
from src.gui.styles import get_button_solid_stylesheet
from src.database.crud import get_connection

logger = logging.getLogger(__name__)

# Color mapping
CHART_COLORS = {
    "navy": "#1e3a8a",
    "orange": "#f59e0b",
    "success": "#10b981",
    "error": "#ef4444",
    "gray": "#6b7280",
    "light_gray": "#f3f4f6",
    "blue": "#3b82f6",
}


class ChartCanvas(FigureCanvas):
    """Matplotlib chart canvas untuk PyQt6 integration."""
    
    def __init__(self, figure: Figure, parent=None):
        super().__init__(figure)
        self.setParent(parent)
        self.figure = figure
        self.figure.patch.set_facecolor('white')
    
    def plot(self):
        """Refresh plot."""
        self.draw()


class TrackerTab(QWidget):
    """
    Tracker Lamaran Tab dengan 2 sections:
    1. Top: Table applications dengan status badges dan aksi
    2. Bottom: Analytics dengan donut chart dan bar chart
    """
    
    def __init__(self, user_id: int, parent=None):
        super().__init__(parent)
        self.user_id = user_id
        self.applications = []
        
        logger.info(f"Initializing TrackerTab for user {user_id}")
        self.init_ui()
        self.load_applications()
    
    def init_ui(self):
        """Initialize Tracker Tab UI."""
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(24, 20, 24, 20)
        main_layout.setSpacing(0)
        
        # ===== HEADER =====
        header_layout = QVBoxLayout()
        header_layout.setSpacing(4)
        header_layout.setContentsMargins(0, 0, 0, 0)
        
        title_label = QLabel("Tracker Lamaran")
        title_font = QFont(FONT_FAMILY_PRIMARY, 28)
        title_font.setWeight(QFont.Weight.Bold)
        title_label.setFont(title_font)
        title_label.setStyleSheet(f"color: {COLOR_NAVY}; padding: 0px;")
        header_layout.addWidget(title_label)
        
        main_layout.addLayout(header_layout)
        main_layout.addSpacing(20)
        
        # ===== SCROLL AREA =====
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setStyleSheet(f"border: none; background-color: {COLOR_GRAY_BACKGROUND};")
        
        scroll_widget = QWidget()
        scroll_layout = QVBoxLayout(scroll_widget)
        scroll_layout.setContentsMargins(0, 0, 0, 0)
        scroll_layout.setSpacing(0)
        
        # ===== SECTION 1: RIWAYAT LAMARAN (TABLE) =====
        section1_frame = self._create_riwayat_lamaran_section()
        scroll_layout.addWidget(section1_frame)
        scroll_layout.addSpacing(24)
        
        # ===== SECTION 2: ANALYTICS (2 COLUMNS) =====
        analytics_layout = QHBoxLayout()
        analytics_layout.setSpacing(24)
        analytics_layout.setContentsMargins(0, 0, 0, 0)
        
        # Left: Proporsi Status
        proporsi_frame = self._create_proporsi_status()
        analytics_layout.addWidget(proporsi_frame, 1)
        
        # Right: Lamaran per Bulan
        bulanan_frame = self._create_lamaran_per_bulan()
        analytics_layout.addWidget(bulanan_frame, 1)
        
        scroll_layout.addLayout(analytics_layout)
        scroll_layout.addStretch()
        
        scroll.setWidget(scroll_widget)
        main_layout.addWidget(scroll)
        
        self.setStyleSheet(f"background-color: {COLOR_GRAY_BACKGROUND};")
    
    def _create_riwayat_lamaran_section(self) -> QFrame:
        """Create riwayat lamaran table section."""
        frame = QFrame()
        frame.setStyleSheet(f"""
            QFrame {{
                background-color: {COLOR_WHITE};
                border: 1px solid {COLOR_GRAY_200};
                border-radius: {BORDER_RADIUS_MD};
            }}
        """)
        
        layout = QVBoxLayout(frame)
        layout.setContentsMargins(24, 24, 24, 24)
        layout.setSpacing(12)
        
        # Header with button
        header_layout = QHBoxLayout()
        header_layout.setContentsMargins(0, 0, 0, 0)
        header_layout.setSpacing(8)
        
        header_label = QLabel("Riwayat Lamaranku")
        header_font = QFont(FONT_FAMILY_PRIMARY, 16)
        header_font.setWeight(QFont.Weight.Bold)
        header_label.setFont(header_font)
        header_label.setStyleSheet(f"color: {COLOR_NAVY};")
        header_layout.addWidget(header_label)
        header_layout.addStretch()
        
        tambah_btn = QPushButton("➕ Tambah Lamaran")
        tambah_btn.setMinimumHeight(36)
        tambah_btn.setMaximumWidth(180)
        tambah_btn.setStyleSheet(f"""
            QPushButton {{
                background-color: {COLOR_ORANGE};
                border: none;
                border-radius: {BORDER_RADIUS_SM};
                color: white;
                font-weight: bold;
                font-size: 11px;
                padding: 8px 16px;
            }}
            QPushButton:hover {{
                background-color: {COLOR_ORANGE_DARK};
            }}
        """)
        tambah_btn.clicked.connect(self.on_tambah_lamaran)
        header_layout.addWidget(tambah_btn)
        
        layout.addLayout(header_layout)
        
        # Table
        self.table = QTableWidget()
        self.table.setColumnCount(5)
        self.table.setHorizontalHeaderLabels([
            "Nama Beasiswa", "Tanggal Daftar", "Status", "Catatan", "Aksi"
        ])
        
        # Table styling
        self.table.setFont(QFont(FONT_FAMILY_PRIMARY, FONT_SIZE_BASE))
        self.table.setStyleSheet(f"""
            QTableWidget {{
                background-color: {COLOR_WHITE};
                gridline-color: {COLOR_GRAY_200};
                border: none;
            }}
            QTableWidget::item {{
                padding: 12px;
                border-bottom: 1px solid {COLOR_GRAY_100};
            }}
            QTableWidget::item:selected {{
                background-color: {COLOR_GRAY_100};
            }}
            QHeaderView::section {{
                background-color: {COLOR_WHITE};
                padding: 12px;
                border: none;
                border-bottom: 1px solid {COLOR_GRAY_200};
                font-weight: bold;
                color: {COLOR_NAVY};
                font-size: 10px;
            }}
        """)
        
        # Table configuration
        self.table.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        self.table.setSelectionMode(QAbstractItemView.SelectionMode.SingleSelection)
        self.table.setAlternatingRowColors(False)
        self.table.setShowGrid(True)
        
        # Column widths
        header = self.table.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.ResizeMode.Stretch)  # Nama
        header.setSectionResizeMode(1, QHeaderView.ResizeMode.ResizeToContents)  # Tanggal
        header.setSectionResizeMode(2, QHeaderView.ResizeMode.ResizeToContents)  # Status
        header.setSectionResizeMode(3, QHeaderView.ResizeMode.Stretch)  # Catatan
        header.setSectionResizeMode(4, QHeaderView.ResizeMode.ResizeToContents)  # Aksi
        
        self.table.setMinimumHeight(300)
        layout.addWidget(self.table)
        
        return frame
    
    def _create_proporsi_status(self) -> QFrame:
        """Create proporsi status donut chart."""
        frame = QFrame()
        frame.setStyleSheet(f"""
            QFrame {{
                background-color: {COLOR_WHITE};
                border: 1px solid {COLOR_GRAY_200};
                border-radius: {BORDER_RADIUS_MD};
            }}
        """)
        
        layout = QVBoxLayout(frame)
        layout.setContentsMargins(24, 24, 24, 24)
        layout.setSpacing(16)
        
        # Title
        title_label = QLabel("Proporsi Status Lamaran")
        title_font = QFont(FONT_FAMILY_PRIMARY, 14)
        title_font.setWeight(QFont.Weight.Bold)
        title_label.setFont(title_font)
        title_label.setStyleSheet(f"color: {COLOR_NAVY};")
        layout.addWidget(title_label)
        
        subtitle_label = QLabel("Berdasarkan total 9 lamaran tercatat")
        subtitle_label.setFont(QFont(FONT_FAMILY_PRIMARY, FONT_SIZE_SM))
        subtitle_label.setStyleSheet(f"color: {COLOR_GRAY_600};")
        layout.addWidget(subtitle_label)
        
        # Chart
        canvas = self._create_donut_chart()
        layout.addWidget(canvas)
        
        # Legend
        legend_layout = QHBoxLayout()
        legend_layout.setSpacing(16)
        
        # Pending
        pending_box = QFrame()
        pending_box.setStyleSheet(f"""
            QFrame {{
                background-color: {CHART_COLORS['blue']};
                border-radius: 2px;
                min-width: 20px;
                min-height: 20px;
            }}
        """)
        legend_layout.addWidget(pending_box)
        
        pending_label = QLabel("Pending\n5 lamaran")
        pending_label.setFont(QFont(FONT_FAMILY_PRIMARY, FONT_SIZE_SM))
        pending_label.setStyleSheet(f"color: {CHART_COLORS['blue']}; font-weight: bold;")
        legend_layout.addWidget(pending_label)
        
        legend_layout.addSpacing(12)
        
        # Diterima
        diterima_box = QFrame()
        diterima_box.setStyleSheet(f"""
            QFrame {{
                background-color: {CHART_COLORS['success']};
                border-radius: 2px;
                min-width: 20px;
                min-height: 20px;
            }}
        """)
        legend_layout.addWidget(diterima_box)
        
        diterima_label = QLabel("Diterima\n2 lamaran")
        diterima_label.setFont(QFont(FONT_FAMILY_PRIMARY, FONT_SIZE_SM))
        diterima_label.setStyleSheet(f"color: {CHART_COLORS['success']}; font-weight: bold;")
        legend_layout.addWidget(diterima_label)
        
        legend_layout.addSpacing(12)
        
        # Ditolak
        ditolak_box = QFrame()
        ditolak_box.setStyleSheet(f"""
            QFrame {{
                background-color: {CHART_COLORS['error']};
                border-radius: 2px;
                min-width: 20px;
                min-height: 20px;
            }}
        """)
        legend_layout.addWidget(ditolak_box)
        
        ditolak_label = QLabel("Ditolak\n2 lamaran")
        ditolak_label.setFont(QFont(FONT_FAMILY_PRIMARY, FONT_SIZE_SM))
        ditolak_label.setStyleSheet(f"color: {CHART_COLORS['error']}; font-weight: bold;")
        legend_layout.addWidget(ditolak_label)
        
        legend_layout.addStretch()
        layout.addLayout(legend_layout)
        
        return frame
    
    def _create_lamaran_per_bulan(self) -> QFrame:
        """Create lamaran per bulan bar chart."""
        frame = QFrame()
        frame.setStyleSheet(f"""
            QFrame {{
                background-color: {COLOR_WHITE};
                border: 1px solid {COLOR_GRAY_200};
                border-radius: {BORDER_RADIUS_MD};
            }}
        """)
        
        layout = QVBoxLayout(frame)
        layout.setContentsMargins(24, 24, 24, 24)
        layout.setSpacing(16)
        
        # Title
        title_label = QLabel("Lamaran per Bulan")
        title_font = QFont(FONT_FAMILY_PRIMARY, 14)
        title_font.setWeight(QFont.Weight.Bold)
        title_label.setFont(title_font)
        title_label.setStyleSheet(f"color: {COLOR_NAVY};")
        layout.addWidget(title_label)
        
        subtitle_label = QLabel("6 bulan terakhir")
        subtitle_label.setFont(QFont(FONT_FAMILY_PRIMARY, FONT_SIZE_SM))
        subtitle_label.setStyleSheet(f"color: {COLOR_GRAY_600};")
        layout.addWidget(subtitle_label)
        
        # Chart
        canvas = self._create_bar_chart()
        layout.addWidget(canvas)
        
        # Info box
        info_box = QFrame()
        info_box.setStyleSheet(f"""
            QFrame {{
                background-color: {COLOR_WARNING_LIGHT};
                border: 1px solid {COLOR_ORANGE};
                border-radius: {BORDER_RADIUS_SM};
                padding: 12px;
            }}
        """)
        info_layout = QHBoxLayout(info_box)
        info_layout.setContentsMargins(8, 8, 8, 8)
        
        info_icon = QLabel("📈")
        info_icon.setFont(QFont(FONT_FAMILY_PRIMARY, 14))
        info_layout.addWidget(info_icon)
        
        info_text = QLabel("Terbanyak di bulan Maret 2026 dengan 3 lamaran")
        info_text.setFont(QFont(FONT_FAMILY_PRIMARY, FONT_SIZE_SM))
        info_text.setStyleSheet(f"color: {COLOR_ORANGE}; font-weight: bold;")
        info_layout.addWidget(info_text)
        
        layout.addWidget(info_box)
        
        return frame
    
    def _create_donut_chart(self) -> FigureCanvas:
        """Create donut chart for status distribution."""
        figure = Figure(figsize=(6, 4), dpi=100)
        ax = figure.add_subplot(111)
        
        sizes = [5, 2, 2]  # Pending, Diterima, Ditolak
        labels = ['Pending', 'Diterima', 'Ditolak']
        colors = [CHART_COLORS['blue'], CHART_COLORS['success'], CHART_COLORS['error']]
        
        wedges, texts, autotexts = ax.pie(
            sizes, labels=labels, colors=colors,
            autopct='%1.0f%%', startangle=90,
            textprops={'fontsize': 9, 'weight': 'bold'},
            wedgeprops=dict(width=0.4, edgecolor='white', linewidth=2)
        )
        
        for autotext in autotexts:
            autotext.set_color('white')
            autotext.set_fontweight('bold')
            autotext.set_fontsize(10)
        
        # Center circle text
        centre_circle = plt.Circle((0, 0), 0.70, fc='white', edgecolor='white', linewidth=0)
        ax.add_artist(centre_circle)
        
        ax.text(0, 0, '9\nTotal', ha='center', va='center',
               fontsize=18, fontweight='bold', color=CHART_COLORS['navy'])
        
        ax.set_facecolor('white')
        figure.patch.set_facecolor('white')
        figure.tight_layout(pad=0.5)
        
        return FigureCanvas(figure)
    
    def _create_bar_chart(self) -> FigureCanvas:
        """Create bar chart for monthly applications."""
        figure = Figure(figsize=(6, 4), dpi=100)
        ax = figure.add_subplot(111)
        
        months = ['Nov 25', 'Des 25', 'Jan 26', 'Feb 26', 'Mar 26', 'Apr 26']
        values = [1, 2, 2, 3, 1]
        
        # Colors: navy, navy, navy, orange (for Mar which is highest), navy
        colors_list = [CHART_COLORS['navy'], CHART_COLORS['navy'], 
                       CHART_COLORS['navy'], CHART_COLORS['orange'],
                       CHART_COLORS['navy']]
        
        bars = ax.bar(months[:5], values, color=colors_list, edgecolor='none', 
                     width=0.6, alpha=0.85)
        
        # Value labels on top
        for bar, value in zip(bars, values):
            height = bar.get_height()
            ax.text(bar.get_x() + bar.get_width()/2., height + 0.1,
                   f'{int(value)}', ha='center', va='bottom', fontsize=10, 
                   fontweight='bold', color=CHART_COLORS['navy'])
        
        # Styling
        ax.set_ylim(0, 4.5)
        ax.set_ylabel('Jumlah Lamaran', fontsize=9, color=CHART_COLORS['gray'], 
                     fontweight='bold')
        ax.spines['top'].set_visible(False)
        ax.spines['right'].set_visible(False)
        ax.spines['left'].set_color(CHART_COLORS['light_gray'])
        ax.spines['bottom'].set_color(CHART_COLORS['light_gray'])
        ax.set_facecolor('white')
        figure.patch.set_facecolor('white')
        ax.grid(axis='y', alpha=0.25, linestyle='-', color=CHART_COLORS['light_gray'])
        
        ax.tick_params(axis='x', labelsize=8, colors=CHART_COLORS['navy'])
        ax.tick_params(axis='y', labelsize=8, colors=CHART_COLORS['gray'])
        
        figure.tight_layout(pad=0.8)
        return FigureCanvas(figure)
    
    def load_applications(self):
        """Load applications data."""
        try:
            conn = get_connection()
            cursor = conn.cursor()
            
            # Sample data untuk sekarang
            sample_apps = [
                ("Beasiswa LPDP 2026", "10 Mar 2026", "Pending", "Menunggu hasil seleksi administrasi"),
                ("Beasiswa Unggulan Kemendikbud", "15 Feb 2026", "Diterima", "Lulus seleksi, sudah menerima LOA"),
                ("Beasiswa BCA", "20 Jan 2026", "Ditolak", "Tidak lolos seleksi wawancara"),
                ("Beasiswa Djarum Plus", "5 Mar 2026", "Pending", "Proses verifikasi dokumen"),
                ("Beasiswa Tanoto Foundation", "28 Feb 2026", "Diterima", "Sudah menandatangani kontrak beasiswa"),
                ("Beasiswa Bank Indonesia", "12 Jan 2026", "Ditolak", "IPK tidak memenuhi syarat"),
                ("Beasiswa Sampoerna University", "8 Mar 2026", "Pending", "Menunggu jadwal wawancara"),
            ]
            
            self.applications = sample_apps
            self.populate_table(sample_apps)
            
            logger.info(f"Loaded {len(self.applications)} applications")
            conn.close()
        except Exception as e:
            logger.error(f"Error loading applications: {e}")
    
    def populate_table(self, apps):
        """Populate table dengan data."""
        self.table.setRowCount(len(apps))
        
        for row_idx, app in enumerate(apps):
            nama, tanggal, status, catatan = app[0], app[1], app[2], app[3]
            
            # Nama Beasiswa
            nama_item = QTableWidgetItem(nama)
            nama_item.setFont(QFont(FONT_FAMILY_PRIMARY, FONT_SIZE_BASE))
            nama_item.setForeground(QColor(COLOR_NAVY))
            nama_font = nama_item.font()
            nama_font.setWeight(QFont.Weight.Bold)
            nama_item.setFont(nama_font)
            self.table.setItem(row_idx, 0, nama_item)
            
            # Tanggal
            tanggal_item = QTableWidgetItem(tanggal)
            tanggal_item.setFont(QFont(FONT_FAMILY_PRIMARY, FONT_SIZE_BASE))
            tanggal_item.setForeground(QColor(COLOR_GRAY_700))
            self.table.setItem(row_idx, 1, tanggal_item)
            
            # Status (badge)
            status_widget = self._create_status_badge(status)
            self.table.setCellWidget(row_idx, 2, status_widget)
            
            # Catatan
            catatan_item = QTableWidgetItem(catatan)
            catatan_item.setFont(QFont(FONT_FAMILY_PRIMARY, FONT_SIZE_BASE))
            catatan_item.setForeground(QColor(COLOR_GRAY_700))
            self.table.setItem(row_idx, 3, catatan_item)
            
            # Aksi
            action_widget = self._create_action_buttons(row_idx)
            self.table.setCellWidget(row_idx, 4, action_widget)
    
    def _create_status_badge(self, status: str) -> QFrame:
        """Create status badge."""
        badge_frame = QFrame()
        badge_layout = QHBoxLayout(badge_frame)
        badge_layout.setContentsMargins(0, 0, 0, 0)
        badge_layout.setSpacing(0)
        
        if status == "Pending":
            bg_color = "#dbeafe"  # Light blue
            text_color = CHART_COLORS['blue']
        elif status == "Diterima":
            bg_color = "#d1fae5"  # Light green
            text_color = CHART_COLORS['success']
        else:  # Ditolak
            bg_color = "#fee2e2"  # Light red
            text_color = CHART_COLORS['error']
        
        badge_label = QLabel(status)
        badge_label.setFont(QFont(FONT_FAMILY_PRIMARY, FONT_SIZE_SM))
        badge_label.setStyleSheet(f"""
            color: {text_color};
            font-weight: bold;
            padding: 4px 8px;
        """)
        
        badge_frame.setStyleSheet(f"""
            QFrame {{
                background-color: {bg_color};
                border: 1px solid {text_color};
                border-radius: 4px;
            }}
        """)
        
        badge_layout.addWidget(badge_label)
        return badge_frame
    
    def _create_action_buttons(self, row_idx: int) -> QFrame:
        """Create action buttons (edit, delete)."""
        action_frame = QFrame()
        action_layout = QHBoxLayout(action_frame)
        action_layout.setContentsMargins(0, 0, 0, 0)
        action_layout.setSpacing(8)
        
        # Edit button
        edit_btn = QPushButton("✏")
        edit_btn.setMaximumSize(28, 28)
        edit_btn.setStyleSheet(f"""
            QPushButton {{
                background-color: transparent;
                border: none;
                font-size: 14px;
                color: {COLOR_GRAY_600};
            }}
            QPushButton:hover {{
                background-color: {COLOR_GRAY_100};
                border-radius: 4px;
            }}
        """)
        action_layout.addWidget(edit_btn)
        
        # Delete button
        delete_btn = QPushButton("🗑")
        delete_btn.setMaximumSize(28, 28)
        delete_btn.setStyleSheet(f"""
            QPushButton {{
                background-color: transparent;
                border: none;
                font-size: 14px;
                color: {COLOR_ERROR};
            }}
            QPushButton:hover {{
                background-color: {COLOR_ERROR_LIGHT};
                border-radius: 4px;
            }}
        """)
        delete_btn.clicked.connect(lambda: self.on_delete_lamaran(row_idx))
        action_layout.addWidget(delete_btn)
        
        action_layout.addStretch()
        return action_frame
    
    def on_tambah_lamaran(self):
        """Handle add application."""
        logger.info("Add lamaran clicked")
    
    def on_delete_lamaran(self, row_idx: int):
        """Handle delete application."""
        logger.info(f"Delete lamaran at row {row_idx}")
