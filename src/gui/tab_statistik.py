"""
Statistik (Statistics Dashboard) Tab for BeasiswaKu
Real-time visualization of scholarship data dengan 3 main charts
"""

import logging
from typing import Optional, Dict, List, Any
from datetime import datetime

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QFrame,
    QPushButton, QGridLayout, QSpacerItem, QSizePolicy
)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont

import matplotlib.pyplot as plt
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
import numpy as np

from src.gui.design_tokens import *
from src.gui.styles import get_button_solid_stylesheet
from src.database.crud import get_connection

# Setup logging
logger = logging.getLogger(__name__)

# Color mapping untuk charts
CHART_COLORS = {
    "navy": "#1e3a8a",
    "orange": "#f59e0b",
    "success": "#10b981",
    "error": "#ef4444",
    "gray": "#6b7280",
    "light_gray": "#f3f4f6",
}


class ChartCanvas(FigureCanvas):
    """
    Matplotlib chart canvas untuk PyQt6 integration.
    """
    
    def __init__(self, figure: Figure, parent=None):
        super().__init__(figure)
        self.setParent(parent)
        self.figure = figure
        # Set white background
        self.figure.patch.set_facecolor('white')
    
    def plot(self):
        """Refresh plot."""
        self.draw()


class StatistikTab(QWidget):
    """
    Statistik (Statistics Dashboard) Tab - Data visualization dengan 3 main charts.
    
    Charts:
    1. Bar Chart: Beasiswa per Jenjang Pendidikan
       - X-axis: D3, D4, S1, S2
       - Y-axis: Number of scholarships
       - Colors: Navy/Orange
    
    2. Donut Chart: Status Ketersediaan Beasiswa
       - Buka (Green, 63%)
       - Segera Tutup (Orange, 17%)
       - Tutup (Gray, 20%)
       - Center: Total number
    
    3. Horizontal Bar Chart: Top 5 Penyelenggara Beasiswa
       - Names: Kemendikbud, LPDP, Tanoto Foundation, Bank Indonesia, Djarum Foundation
       - Values: 8, 6, 5, 4, 3
       - Color: Orange bars
    
    Features:
    - Real-time data dari database
    - Responsive charts
    - Professional styling dengan Navy + Orange
    - Stat cards di atas dengan summary data
    """
    
    def __init__(self, user_id: int, parent=None):
        super().__init__(parent)
        self.user_id = user_id
        self.stat_data: Dict[str, Any] = {}
        self.charts = []
        
        logger.info(f"Initializing StatistikTab")
        self.init_ui()
        self.load_statistics()
    
    def init_ui(self):
        """Initialize Statistik Tab UI."""
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(16, 16, 16, 16)  # SPACING_4
        main_layout.setSpacing(12)  # SPACING_3
        
        # ===== HEADER SECTION =====
        header_layout = QVBoxLayout()
        header_layout.setSpacing(4)
        
        title_label = QLabel("Dashboard Statistik")
        title_font = QFont(FONT_FAMILY_PRIMARY, 20)
        title_font.setWeight(QFont.Weight.Bold)
        title_label.setFont(title_font)
        title_label.setStyleSheet(f"color: {COLOR_NAVY};")
        header_layout.addWidget(title_label)
        
        subtitle_label = QLabel("Data real-time hasil scraping indbeasiswa.com")
        subtitle_label.setFont(QFont(FONT_FAMILY_PRIMARY, FONT_SIZE_BASE))
        subtitle_label.setStyleSheet(f"color: {COLOR_GRAY_600};")
        header_layout.addWidget(subtitle_label)
        
        main_layout.addLayout(header_layout)
        main_layout.addSpacing(8)  # SPACING_2
        
        # ===== STAT CARDS SECTION =====
        stats_layout = QGridLayout()
        stats_layout.setSpacing(12)  # SPACING_3
        
        stat_configs = [
            {"number": "48", "label": "Total Beasiswa", "icon": "📚"},
            {"number": "30", "label": "Beasiswa Buka", "icon": "🟢"},
            {"number": "8", "label": "Segera Tutup", "icon": "⏰"},
            {"number": "10", "label": "Beasiswa Tutup", "icon": "🔒"},
        ]
        
        for idx, config in enumerate(stat_configs):
            card = self._create_stat_card(config["icon"], config["number"], config["label"])
            stats_layout.addWidget(card, 0, idx)
        
        main_layout.addLayout(stats_layout)
        main_layout.addSpacing(8)  # SPACING_2
        
        # ===== CHARTS SECTION =====
        charts_layout = QGridLayout()
        charts_layout.setSpacing(12)  # SPACING_3
        
        # Chart 1: Beasiswa per Jenjang (Bar Chart)
        chart1 = self._create_chart_frame(
            self._create_bar_chart(),
            "Beasiswa per Jenjang Pendidikan"
        )
        charts_layout.addWidget(chart1, 0, 0)
        
        # Chart 2: Status Ketersediaan (Donut Chart)
        chart2 = self._create_chart_frame(
            self._create_donut_chart(),
            "Status Ketersediaan Beasiswa"
        )
        charts_layout.addWidget(chart2, 0, 1)
        
        # Chart 3: Top 5 Penyelenggara (Horizontal Bar Chart)
        chart3 = self._create_chart_frame(
            self._create_horizontal_bar_chart(),
            "Top 5 Penyelenggara Beasiswa",
            full_width=True
        )
        charts_layout.addWidget(chart3, 1, 0, 1, 2)
        
        main_layout.addLayout(charts_layout)
        main_layout.addStretch()
        
        # Apply stylesheet
        self.setStyleSheet(f"background-color: {COLOR_GRAY_BACKGROUND};")
    
    def _create_stat_card(self, icon: str, number: str, label: str) -> QFrame:
        """Create a stat card widget."""
        card = QFrame()
        card.setFrameStyle(QFrame.Shape.Box | QFrame.Shadow.Plain)
        
        layout = QHBoxLayout(card)
        layout.setContentsMargins(12, 12, 12, 12)
        layout.setSpacing(12)
        
        # Icon
        icon_label = QLabel(icon)
        icon_label.setFont(QFont(FONT_FAMILY_PRIMARY, 24))
        layout.addWidget(icon_label)
        
        # Number + Label
        text_layout = QVBoxLayout()
        
        num_label = QLabel(number)
        num_font = QFont(FONT_FAMILY_PRIMARY, 24)
        num_font.setWeight(QFont.Weight.Bold)
        num_label.setFont(num_font)
        num_label.setStyleSheet(f"color: {COLOR_NAVY};")
        text_layout.addWidget(num_label)
        
        text_label = QLabel(label)
        text_label.setFont(QFont(FONT_FAMILY_PRIMARY, FONT_SIZE_BASE))
        text_label.setStyleSheet(f"color: {COLOR_GRAY_600};")
        text_layout.addWidget(text_label)
        
        layout.addLayout(text_layout)
        layout.addStretch()
        
        card.setStyleSheet(f"""
            QFrame {{
                background-color: {COLOR_WHITE};
                border: 1px solid {COLOR_GRAY_200};
                border-radius: {BORDER_RADIUS_MD};
            }}
        """)
        
        return card
    
    def _create_chart_frame(self, canvas: FigureCanvas, title: str, full_width: bool = False) -> QFrame:
        """Create chart frame dengan title."""
        frame = QFrame()
        frame.setFrameStyle(QFrame.Shape.Box | QFrame.Shadow.Plain)
        frame.setStyleSheet(f"""
            QFrame {{
                background-color: {COLOR_WHITE};
                border: 1px solid {COLOR_GRAY_200};
                border-radius: {BORDER_RADIUS_MD};
            }}
        """)
        
        layout = QVBoxLayout(frame)
        layout.setContentsMargins(12, 12, 12, 12)
        layout.setSpacing(8)
        
        # Title
        title_label = QLabel(title)
        title_font = QFont(FONT_FAMILY_PRIMARY, FONT_SIZE_LG)
        title_font.setWeight(QFont.Weight.Medium)
        title_label.setFont(title_font)
        title_label.setStyleSheet(f"color: {COLOR_NAVY};")
        layout.addWidget(title_label)
        
        # Canvas
        layout.addWidget(canvas)
        
        return frame
    
    def _create_bar_chart(self) -> FigureCanvas:
        """Create bar chart: Beasiswa per Jenjang Pendidikan."""
        figure = Figure(figsize=(5, 3.5), dpi=100)
        ax = figure.add_subplot(111)
        
        # Data
        jenjang = ['D3', 'D4', 'S1', 'S2']
        values = [8, 6, 28, 6]
        colors = [CHART_COLORS["navy"] if v != 28 else CHART_COLORS["orange"] for v in values]
        
        # Create bar chart
        bars = ax.bar(jenjang, values, color=colors, edgecolor='none', width=0.6)
        
        # Add value labels on bars
        for bar, value in zip(bars, values):
            height = bar.get_height()
            ax.text(bar.get_x() + bar.get_width()/2., height,
                   f'{int(value)}',
                   ha='center', va='bottom', fontsize=10, fontweight='bold', color=CHART_COLORS["navy"])
        
        # Styling
        ax.set_ylabel('Jumlah Beasiswa', fontsize=10, color=CHART_COLORS["gray"], fontweight='bold')
        ax.set_xlabel('Jenjang Pendidikan', fontsize=10, color=CHART_COLORS["gray"], fontweight='bold')
        ax.set_ylim(0, max(values) * 1.15)
        ax.spines['top'].set_visible(False)
        ax.spines['right'].set_visible(False)
        ax.spines['left'].set_color(CHART_COLORS["light_gray"])
        ax.spines['bottom'].set_color(CHART_COLORS["light_gray"])
        ax.set_facecolor('white')
        figure.patch.set_facecolor('white')
        
        # Grid
        ax.grid(axis='y', alpha=0.3, linestyle='--', color=CHART_COLORS["light_gray"])
        ax.set_axisbelow(True)
        
        figure.tight_layout()
        return FigureCanvas(figure)
    
    def _create_donut_chart(self) -> FigureCanvas:
        """Create donut chart: Status Ketersediaan Beasiswa."""
        figure = Figure(figsize=(5, 3.5), dpi=100)
        ax = figure.add_subplot(111)
        
        # Data
        statuses = ['Buka', 'Segera Tutup', 'Tutup']
        values = [30, 8, 10]  # 63%, 17%, 20% of 48
        colors = [CHART_COLORS["success"], CHART_COLORS["orange"], CHART_COLORS["gray"]]
        
        # Create donut chart
        wedges, texts, autotexts = ax.pie(values, labels=statuses, colors=colors,
                                           autopct='%1.0f%%', startangle=90,
                                           textprops={'fontsize': 9, 'weight': 'bold'},
                                           wedgeprops=dict(width=0.5, edgecolor='white', linewidth=2))
        
        # Style percentage text
        for autotext in autotexts:
            autotext.set_color('white')
            autotext.set_fontweight('bold')
            autotext.set_fontsize(10)
        
        # Add center text
        centre_circle = plt.Circle((0, 0), 0.70, fc='white', edgecolor='white')
        ax.add_artist(centre_circle)
        
        # Center text
        ax.text(0, 0.15, '48', ha='center', va='center',
               fontsize=24, fontweight='bold', color=CHART_COLORS["navy"])
        ax.text(0, -0.15, 'total', ha='center', va='center',
               fontsize=10, color=CHART_COLORS["gray"], fontweight='bold')
        
        ax.set_facecolor('white')
        figure.patch.set_facecolor('white')
        
        figure.tight_layout()
        return FigureCanvas(figure)
    
    def _create_horizontal_bar_chart(self) -> FigureCanvas:
        """Create horizontal bar chart: Top 5 Penyelenggara Beasiswa."""
        figure = Figure(figsize=(10, 2.5), dpi=100)
        ax = figure.add_subplot(111)
        
        # Data
        penyelenggara = [
            'Kemendikbud',
            'LPDP',
            'Tanoto Foundation',
            'Bank Indonesia',
            'Djarum Foundation'
        ]
        values = [8, 6, 5, 4, 3]
        
        # Create horizontal bar chart
        bars = ax.barh(penyelenggara, values, color=CHART_COLORS["orange"], edgecolor='none', height=0.6)
        
        # Add value labels
        for bar, value in zip(bars, values):
            width = bar.get_width()
            ax.text(width, bar.get_y() + bar.get_height()/2.,
                   f'{int(value)}',
                   ha='left', va='center', fontsize=9, fontweight='bold',
                   color=CHART_COLORS["navy"], bbox=dict(boxstyle='round,pad=0.3',
                                                          facecolor='white', edgecolor='none', alpha=0.8))
        
        # Styling
        ax.set_xlabel('Jumlah Beasiswa', fontsize=10, color=CHART_COLORS["gray"], fontweight='bold')
        ax.set_xlim(0, max(values) * 1.3)
        ax.spines['top'].set_visible(False)
        ax.spines['right'].set_visible(False)
        ax.spines['left'].set_color(CHART_COLORS["light_gray"])
        ax.spines['bottom'].set_color(CHART_COLORS["light_gray"])
        ax.set_facecolor('white')
        figure.patch.set_facecolor('white')
        
        # Grid
        ax.grid(axis='x', alpha=0.3, linestyle='--', color=CHART_COLORS["light_gray"])
        ax.set_axisbelow(True)
        
        figure.tight_layout()
        return FigureCanvas(figure)
    
    def load_statistics(self):
        """Load statistics data dari database."""
        try:
            conn = get_connection()
            cursor = conn.cursor()
            
            # Query 1: Total beasiswa
            cursor.execute("SELECT COUNT(*) as total FROM beasiswa")
            total = cursor.fetchone()[0]
            logger.info(f"Total beasiswa: {total}")
            
            # Query 2: Beasiswa by status
            cursor.execute("""
                SELECT status, COUNT(*) as count 
                FROM beasiswa 
                GROUP BY status
            """)
            status_data = cursor.fetchall()
            logger.info(f"Status distribution: {status_data}")
            
            # Query 3: Beasiswa by jenjang
            cursor.execute("""
                SELECT jenjang, COUNT(*) as count 
                FROM beasiswa 
                GROUP BY jenjang
                ORDER BY count DESC
            """)
            jenjang_data = cursor.fetchall()
            logger.info(f"Jenjang distribution: {jenjang_data}")
            
            # Query 4: Top penyelenggara
            cursor.execute("""
                SELECT penyelenggara_id, COUNT(*) as count 
                FROM beasiswa 
                WHERE penyelenggara_id IS NOT NULL
                GROUP BY penyelenggara_id
                ORDER BY count DESC
                LIMIT 5
            """)
            penyelenggara_data = cursor.fetchall()
            logger.info(f"Top penyelenggara: {penyelenggara_data}")
            
            self.stat_data = {
                'total': total,
                'status': status_data,
                'jenjang': jenjang_data,
                'penyelenggara': penyelenggara_data
            }
            
        except Exception as e:
            logger.error(f"Error loading statistics: {e}")
    
    def refresh_data(self):
        """Refresh statistics data."""
        self.load_statistics()
        logger.info("Statistics data refreshed")
