"""
Statistik (Statistics Dashboard) Tab for BeasiswaKu
Real-time visualization of scholarship data dengan 3 main charts
"""

import logging
from typing import Optional, Dict, List, Any
from datetime import datetime

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QFrame,
    QPushButton, QGridLayout, QSpacerItem, QSizePolicy, QScrollArea
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
        """Initialize Statistik Tab UI dengan scroll area."""
        # Create scroll area untuk enable scrolling
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setStyleSheet(f"""
            QScrollArea {{
                background-color: {COLOR_GRAY_BACKGROUND};
                border: none;
            }}
            QScrollBar:vertical {{
                width: 8px;
                background-color: {COLOR_GRAY_200};
            }}
            QScrollBar::handle:vertical {{
                background-color: {COLOR_GRAY_400};
                border-radius: 4px;
            }}
            QScrollBar::handle:vertical:hover {{
                background-color: {COLOR_GRAY_500};
            }}
        """)
        
        # Content widget dengan main layout
        content_widget = QWidget()
        main_layout = QVBoxLayout(content_widget)
        main_layout.setContentsMargins(24, 20, 24, 20)  # Better margins
        main_layout.setSpacing(0)  # Control spacing manually
        
        # Set scroll area
        self.setStyleSheet(f"background-color: {COLOR_GRAY_BACKGROUND};")
        scroll_area.setWidget(content_widget)
        
        # Tambah scroll area ke main widget
        main_parent_layout = QVBoxLayout(self)
        main_parent_layout.setContentsMargins(0, 0, 0, 0)
        main_parent_layout.addWidget(scroll_area)
        
        # ===== HEADER SECTION =====
        header_layout = QVBoxLayout()
        header_layout.setSpacing(4)
        header_layout.setContentsMargins(0, 0, 0, 0)
        
        title_label = QLabel("Dashboard Statistik")
        title_font = QFont(FONT_FAMILY_PRIMARY, 28)
        title_font.setWeight(QFont.Weight.Bold)
        title_label.setFont(title_font)
        title_label.setStyleSheet(f"color: {COLOR_NAVY}; line-height: 1.2; padding: 0px;")
        header_layout.addWidget(title_label)
        
        subtitle_label = QLabel("Data real-time hasil scraping indbeasiswa.com")
        subtitle_label.setFont(QFont(FONT_FAMILY_PRIMARY, FONT_SIZE_BASE))
        subtitle_label.setStyleSheet(f"color: {COLOR_GRAY_500}; padding: 0px;")
        header_layout.addWidget(subtitle_label)
        
        main_layout.addLayout(header_layout)
        main_layout.addSpacing(16)  # Better spacing after header
        
        # ===== STAT CARDS SECTION =====
        stats_layout = QGridLayout()
        stats_layout.setSpacing(16)  # SPACING_4
        stats_layout.setContentsMargins(0, 0, 0, 0)
        
        stat_configs = [
            {"number": "48", "label": "Total Beasiswa", "icon": "📚"},
            {"number": "30", "label": "Beasiswa Buka", "icon": "🟢"},
            {"number": "8", "label": "Segera Tutup", "icon": "⏰"},
            {"number": "10", "label": "Beasiswa Tutup", "icon": "🔒"},
        ]
        
        for idx, config in enumerate(stat_configs):
            card = self._create_stat_card(config["icon"], config["number"], config["label"])
            card.setMinimumHeight(100)  # Consistent height
            stats_layout.addWidget(card, 0, idx)
        
        main_layout.addLayout(stats_layout)
        main_layout.addSpacing(16)  # SPACING_4
        
        # ===== CHARTS SECTION (Vertical Stack, Scrollable) =====
        # Chart 1: Beasiswa per Jenjang (Bar Chart)
        chart1_frame = QFrame()
        chart1_frame.setFrameStyle(QFrame.Shape.Box | QFrame.Shadow.Plain)
        chart1_frame.setStyleSheet(f"""
            QFrame {{
                background-color: {COLOR_WHITE};
                border: 1px solid {COLOR_GRAY_200};
                border-radius: {BORDER_RADIUS_MD};
            }}
        """)
        chart1_layout = QVBoxLayout(chart1_frame)
        chart1_layout.setContentsMargins(20, 20, 20, 20)
        chart1_layout.setSpacing(12)
        
        chart1_title = QLabel("Beasiswa per Jenjang Pendidikan")
        chart1_title_font = QFont(FONT_FAMILY_PRIMARY, 16)
        chart1_title_font.setWeight(QFont.Weight.Bold)
        chart1_title.setFont(chart1_title_font)
        chart1_title.setStyleSheet(f"color: {COLOR_NAVY};")
        chart1_layout.addWidget(chart1_title)
        
        chart1_layout.addWidget(self._create_bar_chart())
        
        main_layout.addWidget(chart1_frame)
        main_layout.addSpacing(24)  # More spacing between charts
        
        # Chart 2: Status Ketersediaan (Donut Chart)
        chart2_frame = QFrame()
        chart2_frame.setFrameStyle(QFrame.Shape.Box | QFrame.Shadow.Plain)
        chart2_frame.setStyleSheet(f"""
            QFrame {{
                background-color: {COLOR_WHITE};
                border: 1px solid {COLOR_GRAY_200};
                border-radius: {BORDER_RADIUS_MD};
            }}
        """)
        chart2_layout = QVBoxLayout(chart2_frame)
        chart2_layout.setContentsMargins(20, 20, 20, 20)
        chart2_layout.setSpacing(12)
        
        chart2_title = QLabel("Status Ketersediaan Beasiswa")
        chart2_title_font = QFont(FONT_FAMILY_PRIMARY, 16)
        chart2_title_font.setWeight(QFont.Weight.Bold)
        chart2_title.setFont(chart2_title_font)
        chart2_title.setStyleSheet(f"color: {COLOR_NAVY};")
        chart2_layout.addWidget(chart2_title)
        
        chart2_layout.addWidget(self._create_donut_chart())
        
        main_layout.addWidget(chart2_frame)
        main_layout.addSpacing(24)  # More spacing between charts
        
        # ===== TOP PENYELENGGARA SECTION (Full Width) =====
        chart3_frame = QFrame()
        chart3_frame.setFrameStyle(QFrame.Shape.Box | QFrame.Shadow.Plain)
        chart3_frame.setStyleSheet(f"""
            QFrame {{
                background-color: {COLOR_WHITE};
                border: 1px solid {COLOR_GRAY_200};
                border-radius: {BORDER_RADIUS_MD};
            }}
        """)
        chart3_layout = QVBoxLayout(chart3_frame)
        chart3_layout.setContentsMargins(20, 20, 20, 20)
        chart3_layout.setSpacing(12)
        
        chart3_title = QLabel("Top 5 Penyelenggara Beasiswa")
        chart3_title_font = QFont(FONT_FAMILY_PRIMARY, 16)
        chart3_title_font.setWeight(QFont.Weight.Bold)
        chart3_title.setFont(chart3_title_font)
        chart3_title.setStyleSheet(f"color: {COLOR_NAVY};")
        chart3_layout.addWidget(chart3_title)
        
        chart3_layout.addWidget(self._create_horizontal_bar_chart())
        
        main_layout.addWidget(chart3_frame)
        main_layout.addSpacing(16)  # SPACING_4
        main_layout.addStretch()
        
        # Apply stylesheet to main widget
        self.setStyleSheet(f"background-color: {COLOR_GRAY_BACKGROUND};")
    
    def _create_stat_card(self, icon: str, number: str, label: str) -> QFrame:
        """Create a stat card widget dengan left border colored dan consistem height."""
        card = QFrame()
        card.setFrameStyle(QFrame.Shape.Box | QFrame.Shadow.Plain)
        card.setMinimumHeight(100)
        
        layout = QHBoxLayout(card)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        
        # Tentukan warna border berdasarkan icon/label
        if "Total" in label:
            border_color = COLOR_NAVY
        elif "Buka" in label:
            border_color = "#10b981"  # Green
        elif "Tutup" in label and "Segera" in label:
            border_color = COLOR_ORANGE
        else:
            border_color = COLOR_GRAY_400
        
        # Left border
        left_border = QFrame()
        left_border.setMaximumWidth(5)
        left_border.setStyleSheet(f"background-color: {border_color}; border: none;")
        layout.addWidget(left_border)
        
        # Content area
        content_frame = QFrame()
        content_frame.setStyleSheet(f"background-color: {COLOR_WHITE};")
        content_layout = QHBoxLayout(content_frame)
        content_layout.setContentsMargins(16, 16, 16, 16)
        content_layout.setSpacing(14)
        
        # Icon dengan background circle - improved sizing
        icon_label = QLabel(icon)
        icon_label.setFont(QFont(FONT_FAMILY_PRIMARY, 28))
        icon_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        icon_frame = QFrame()
        icon_frame.setMaximumWidth(56)
        icon_frame.setMaximumHeight(56)
        icon_frame.setMinimumWidth(56)
        icon_frame.setMinimumHeight(56)
        icon_frame.setStyleSheet(f"background-color: #f3f4f6; border-radius: 8px; border: none;")
        icon_layout = QHBoxLayout(icon_frame)
        icon_layout.setContentsMargins(0, 0, 0, 0)
        icon_layout.addWidget(icon_label)
        content_layout.addWidget(icon_frame)
        
        # Text layout
        text_layout = QVBoxLayout()
        text_layout.setSpacing(4)
        text_layout.setContentsMargins(0, 0, 0, 0)
        
        num_label = QLabel(number)
        num_font = QFont(FONT_FAMILY_PRIMARY, 24)
        num_font.setWeight(QFont.Weight.Bold)
        num_label.setFont(num_font)
        num_label.setStyleSheet(f"color: {COLOR_NAVY}; padding: 0px;")
        text_layout.addWidget(num_label)
        
        label_widget = QLabel(label)
        label_widget.setFont(QFont(FONT_FAMILY_PRIMARY, FONT_SIZE_SM))
        label_widget.setStyleSheet(f"color: {COLOR_GRAY_600}; padding: 0px;")
        text_layout.addWidget(label_widget)
        
        content_layout.addLayout(text_layout)
        content_layout.addStretch()
        
        layout.addWidget(content_frame, 1)
        
        card.setStyleSheet(f"""
            QFrame {{
                background-color: {COLOR_WHITE};
                border: 1px solid {COLOR_GRAY_200};
                border-left: none;
                border-radius: {BORDER_RADIUS_MD};
            }}
        """)
        
        return card
    
    def _create_bar_chart(self) -> FigureCanvas:
        """Create bar chart: Beasiswa per Jenjang Pendidikan dengan sizing yang lebih besar."""
        figure = Figure(figsize=(10, 4), dpi=100)
        ax = figure.add_subplot(111)
        
        # Data dengan label yang lebih jelas
        jenjang = ['D3', 'D4', 'S1', 'S2']
        values = [8, 6, 28, 6]
        colors = [CHART_COLORS["navy"] if v != 28 else CHART_COLORS["orange"] for v in values]
        
        # Create bar chart dengan styling yang lebih baik
        bars = ax.bar(jenjang, values, color=colors, edgecolor='none', width=0.65, alpha=0.85)
        
        # Add value labels dengan positioning yang lebih rapi
        for bar, value in zip(bars, values):
            height = bar.get_height()
            ax.text(bar.get_x() + bar.get_width()/2., height + 0.5,
                   f'{int(value)}',
                   ha='center', va='bottom', fontsize=9, fontweight='bold', 
                   color=CHART_COLORS["navy"])
        
        # Improve label styling
        ax.tick_params(axis='x', labelsize=9, colors=CHART_COLORS["navy"])
        ax.tick_params(axis='y', labelsize=8, colors=CHART_COLORS["gray"])
        
        # Styling
        ax.set_ylabel('Jumlah Beasiswa', fontsize=9, color=CHART_COLORS["gray"], fontweight='bold', labelpad=8)
        ax.set_xlabel('Jenjang Pendidikan', fontsize=9, color=CHART_COLORS["gray"], fontweight='bold', labelpad=8)
        ax.set_ylim(0, max(values) * 1.2)
        ax.spines['top'].set_visible(False)
        ax.spines['right'].set_visible(False)
        ax.spines['left'].set_color(CHART_COLORS["light_gray"])
        ax.spines['bottom'].set_color(CHART_COLORS["light_gray"])
        ax.spines['left'].set_linewidth(0.5)
        ax.spines['bottom'].set_linewidth(0.5)
        ax.set_facecolor('white')
        figure.patch.set_facecolor('white')
        
        # Grid styling
        ax.grid(axis='y', alpha=0.25, linestyle='-', color=CHART_COLORS["light_gray"], linewidth=0.5)
        ax.set_axisbelow(True)
        
        # Better layout
        figure.tight_layout(pad=0.8)
        return FigureCanvas(figure)
    
    def _create_donut_chart(self) -> FigureCanvas:
        """Create donut chart: Status Ketersediaan Beasiswa dengan sizing yang lebih besar."""
        figure = Figure(figsize=(10, 4), dpi=100)
        ax = figure.add_subplot(111)
        
        # Data dengan label yang jelas
        statuses = ['Buka', 'Segera Tutup', 'Tutup']
        values = [30, 8, 10]  # 63%, 17%, 20% of 48
        colors = [CHART_COLORS["success"], CHART_COLORS["orange"], CHART_COLORS["gray"]]
        
        # Create donut chart dengan styling lebih baik
        wedges, texts, autotexts = ax.pie(values, labels=statuses, colors=colors,
                                           autopct='%1.0f%%', startangle=90,
                                           textprops={'fontsize': 9, 'weight': 'bold', 'color': CHART_COLORS["navy"]},
                                           wedgeprops=dict(width=0.5, edgecolor='white', linewidth=2.5))
        
        # Style percentage text dengan lebih baik
        for autotext in autotexts:
            autotext.set_color('white')
            autotext.set_fontweight('bold')
            autotext.set_fontsize(9)
        
        # Style labels
        for text in texts:
            text.set_fontsize(8)
            text.set_fontweight('bold')
            text.set_color(CHART_COLORS["navy"])
        
        # Add center circle dan text yang lebih rapi
        centre_circle = plt.Circle((0, 0), 0.70, fc='white', edgecolor='white', linewidth=0)
        ax.add_artist(centre_circle)
        
        # Center text dengan styling lebih baik
        ax.text(0, 0.18, '48', ha='center', va='center',
               fontsize=26, fontweight='bold', color=CHART_COLORS["navy"])
        ax.text(0, -0.18, 'Scholarship', ha='center', va='center',
               fontsize=9, color=CHART_COLORS["gray"], fontweight='bold')
        
        ax.set_facecolor('white')
        figure.patch.set_facecolor('white')
        
        figure.tight_layout(pad=0.8)
        return FigureCanvas(figure)
    
    def _create_horizontal_bar_chart(self) -> FigureCanvas:
        """Create horizontal bar chart: Top 5 Penyelenggara Beasiswa dengan full width."""
        figure = Figure(figsize=(10, 4), dpi=100)
        ax = figure.add_subplot(111)
        
        # Data dengan nama yang lebih rapi
        penyelenggara = [
            'Kemendikbud RI',
            'LPDP (Kemenkeu)',
            'Tanoto Foundation',
            'Bank Indonesia',
            'Djarum Plus'
        ]
        values = [8, 6, 5, 4, 3]
        
        # Create horizontal bar chart dengan styling yang lebih baik
        bars = ax.barh(penyelenggara, values, color=CHART_COLORS["orange"], 
                      edgecolor='none', height=0.65, alpha=0.85)
        
        # Add value labels dengan background yang cleaner
        for bar, value in zip(bars, values):
            width = bar.get_width()
            # Label di dalam/di tepi bar
            ax.text(width + 0.2, bar.get_y() + bar.get_height()/2.,
                   f'{int(value)}',
                   ha='left', va='center', fontsize=8, fontweight='bold',
                   color=CHART_COLORS["navy"])
        
        # Improve label styling
        ax.tick_params(axis='y', labelsize=8, colors=CHART_COLORS["navy"])
        ax.tick_params(axis='x', labelsize=8, colors=CHART_COLORS["gray"])
        
        # Styling
        ax.set_xlabel('Jumlah Beasiswa', fontsize=9, color=CHART_COLORS["gray"], fontweight='bold', labelpad=8)
        ax.set_xlim(0, max(values) * 1.35)
        ax.spines['top'].set_visible(False)
        ax.spines['right'].set_visible(False)
        ax.spines['left'].set_color(CHART_COLORS["light_gray"])
        ax.spines['bottom'].set_color(CHART_COLORS["light_gray"])
        ax.spines['left'].set_linewidth(0.5)
        ax.spines['bottom'].set_linewidth(0.5)
        ax.set_facecolor('white')
        figure.patch.set_facecolor('white')
        
        # Grid styling - improve visibility
        ax.grid(axis='x', alpha=0.25, linestyle='-', color=CHART_COLORS["light_gray"], linewidth=0.5)
        ax.set_axisbelow(True)
        
        # Better layout
        figure.tight_layout(pad=0.8)
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
