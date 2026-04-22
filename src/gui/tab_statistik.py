"""
Statistik (Statistics Dashboard) Tab for BeasiswaKu
Real-time visualization of scholarship data dengan 3 main charts
"""

import logging
from textwrap import shorten
from typing import Optional, Dict, List, Any

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QFrame,
    QGridLayout, QScrollArea
)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont

import matplotlib.pyplot as plt
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure

from src.gui.design_tokens import *
from src.services.dashboard_service import get_statistik_snapshot
from src.services.status_utils import SCHOLARSHIP_STATUS_ORDER

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
        self.load_statistics()
        self.init_ui()

    def _get_status_count_map(self) -> Dict[str, int]:
        """Convert status rows into a normalized dictionary."""
        status_map = {label: 0 for label in SCHOLARSHIP_STATUS_ORDER}
        for key, count in self.stat_data.get("status_counts", {}).items():
            if key in status_map:
                status_map[key] = int(count or 0)
        return status_map

    def _get_jenjang_count_map(self) -> Dict[str, int]:
        """Convert jenjang rows into dictionary."""
        return {
            str(key): int(value)
            for key, value in self.stat_data.get("jenjang_counts", {}).items()
            if key
        }
    
    def init_ui(self):
        """Initialize Statistik Tab UI dengan scroll area."""
        self.setObjectName("statistikTabRoot")

        if not hasattr(self, "_content_main_layout"):
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
            self._content_widget = QWidget()
            self._content_widget.setObjectName("statistikContentWidget")
            self._content_main_layout = QVBoxLayout(self._content_widget)
            self._content_main_layout.setContentsMargins(24, 20, 24, 20)
            self._content_main_layout.setSpacing(0)

            scroll_area.setWidget(self._content_widget)

            main_parent_layout = QVBoxLayout(self)
            main_parent_layout.setContentsMargins(0, 0, 0, 0)
            main_parent_layout.addWidget(scroll_area)

        self._populate_content()
        
        # Apply scoped stylesheet to avoid nested border artifacts.
        self.setStyleSheet(f"""
            QWidget#statistikTabRoot {{
                background-color: {COLOR_GRAY_BACKGROUND};
            }}
            QWidget#statistikContentWidget {{
                background: transparent;
            }}
            QFrame#statCard {{
                background-color: {COLOR_WHITE};
                border: 1px solid {COLOR_GRAY_200};
                border-radius: {BORDER_RADIUS_MD};
            }}
            QFrame#statAccent {{
                border: none;
                border-radius: 2px;
            }}
            QFrame#chartCard {{
                background-color: {COLOR_WHITE};
                border: 1px solid {COLOR_GRAY_200};
                border-radius: {BORDER_RADIUS_MD};
            }}
            QLabel#chartTitle {{
                color: {COLOR_NAVY};
                font-weight: 700;
                border: none;
            }}
            QLabel {{
                border: none;
                background: transparent;
            }}
        """)

    def _clear_layout(self, layout: QVBoxLayout) -> None:
        """Delete all widgets/layout items in a layout."""
        while layout.count():
            item = layout.takeAt(0)
            child_layout = item.layout()
            if child_layout is not None:
                self._clear_layout(child_layout)
            widget = item.widget()
            if widget is not None:
                widget.deleteLater()

    def _populate_content(self) -> None:
        """Populate or refresh the visible statistics content."""
        main_layout = self._content_main_layout
        self._clear_layout(main_layout)

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
        main_layout.addSpacing(16)

        # ===== STAT CARDS SECTION =====
        stats_layout = QGridLayout()
        stats_layout.setSpacing(16)
        stats_layout.setContentsMargins(0, 0, 0, 0)

        status_map = self._get_status_count_map()
        total_beasiswa = int(self.stat_data.get("total", 0) or 0)

        stat_configs = [
            {"number": str(total_beasiswa), "label": "Total Beasiswa", "icon": "📚"},
            {"number": str(status_map.get("Buka", 0)), "label": "Beasiswa Buka", "icon": "🟢"},
            {"number": str(status_map.get("Segera Tutup", 0)), "label": "Segera Tutup", "icon": "⏰"},
            {"number": str(status_map.get("Tutup", 0)), "label": "Beasiswa Tutup", "icon": "🔒"},
        ]

        for idx, config in enumerate(stat_configs):
            card = self._create_stat_card(config["icon"], config["number"], config["label"])
            card.setMinimumHeight(100)
            stats_layout.addWidget(card, 0, idx)

        main_layout.addLayout(stats_layout)
        main_layout.addSpacing(16)

        chart1_frame = self._create_chart_card(
            title="Beasiswa per Jenjang Pendidikan",
            canvas=self._create_bar_chart(),
            object_name="chartJenjangCard",
        )
        main_layout.addWidget(chart1_frame)
        main_layout.addSpacing(24)

        chart2_frame = self._create_chart_card(
            title="Status Ketersediaan Beasiswa",
            canvas=self._create_donut_chart(),
            object_name="chartStatusCard",
        )
        main_layout.addWidget(chart2_frame)
        main_layout.addSpacing(24)

        chart3_frame = self._create_chart_card(
            title="Top 5 Penyelenggara Beasiswa",
            canvas=self._create_horizontal_bar_chart(),
            object_name="chartPenyelenggaraCard",
        )
        main_layout.addWidget(chart3_frame)
        main_layout.addSpacing(16)
        main_layout.addStretch()

    def _create_chart_card(self, title: str, canvas: FigureCanvas, object_name: str) -> QFrame:
        """Create a clean chart card with scoped style and consistent spacing."""
        frame = QFrame()
        frame.setObjectName("chartCard")
        frame.setProperty("chartKind", object_name)

        layout = QVBoxLayout(frame)
        layout.setContentsMargins(20, 18, 20, 18)
        layout.setSpacing(10)

        title_label = QLabel(title)
        title_label.setObjectName("chartTitle")
        title_label.setFont(QFont(FONT_FAMILY_PRIMARY, 16, QFont.Weight.Bold))
        layout.addWidget(title_label)

        canvas.setMinimumHeight(220)
        layout.addWidget(canvas)
        return frame
    
    def _create_stat_card(self, icon: str, number: str, label: str) -> QFrame:
        """Create a stat card widget dengan left border colored dan consistem height."""
        card = QFrame()
        card.setObjectName("statCard")
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
        left_border.setObjectName("statAccent")
        left_border.setMaximumWidth(5)
        left_border.setStyleSheet(f"background-color: {border_color}; border: none;")
        layout.addWidget(left_border)
        
        # Content area
        content_layout = QHBoxLayout()
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
        
        layout.addLayout(content_layout, 1)
        
        return card
    
    def _create_bar_chart(self) -> FigureCanvas:
        """Create bar chart: Beasiswa per Jenjang Pendidikan dengan sizing yang lebih besar."""
        figure = Figure(figsize=(10, 4), dpi=100)
        ax = figure.add_subplot(111)

        # Data dari database
        jenjang_map = self._get_jenjang_count_map()
        ordered_keys = ["D3", "D4", "S1", "S2"]
        extra_keys = [k for k in jenjang_map.keys() if k not in ordered_keys]
        jenjang = [k for k in ordered_keys if k in jenjang_map] + sorted(extra_keys)

        if not jenjang:
            jenjang = ["-"]
            values = [0]
        else:
            values = [jenjang_map.get(k, 0) for k in jenjang]

        max_val = max(values) if values else 0
        colors = [CHART_COLORS["navy"] if v != 28 else CHART_COLORS["orange"] for v in values]

        # Highlight nilai tertinggi bila ada data
        if max_val > 0:
            colors = [CHART_COLORS["orange"] if v == max_val else CHART_COLORS["navy"] for v in values]
        
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
        ax.set_ylim(0, max(1, int(max_val * 1.2) + 1))
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
        figure = Figure(figsize=(8.8, 3.6), dpi=100)
        ax = figure.add_subplot(111)

        # Data dari database
        status_map = self._get_status_count_map()
        statuses = ['Buka', 'Segera Tutup', 'Tutup']
        values = [status_map.get(s, 0) for s in statuses]
        colors = [CHART_COLORS["success"], CHART_COLORS["orange"], CHART_COLORS["gray"]]
        total = sum(values)
        
        # Create donut chart dengan styling lebih baik
        if total > 0:
            wedges, texts, autotexts = ax.pie(
                values,
                labels=None,
                colors=colors,
                autopct=lambda pct: f"{pct:.0f}%" if pct > 0 else "",
                pctdistance=0.76,
                startangle=90,
                textprops={'fontsize': 9, 'weight': 'bold', 'color': CHART_COLORS["navy"]},
                wedgeprops=dict(width=0.36, edgecolor='white', linewidth=2.0),
            )
        
            # Style percentage text dengan lebih baik
            for autotext in autotexts:
                autotext.set_color('white')
                autotext.set_fontweight('bold')
                autotext.set_fontsize(9)

            # legend outside chart area to avoid overlap
            ax.legend(
                handles=wedges,
                labels=statuses,
                loc='center left',
                bbox_to_anchor=(1.02, 0.5),
                frameon=False,
                fontsize=9,
            )

        else:
            ax.pie(
                [1],
                labels=["Belum Ada Data"],
                colors=[CHART_COLORS["light_gray"]],
                startangle=90,
                textprops={'fontsize': 9, 'weight': 'bold', 'color': CHART_COLORS["gray"]},
                wedgeprops=dict(width=0.36, edgecolor='white', linewidth=2.0),
            )
        
        # Add center circle dan text yang lebih rapi
        centre_circle = plt.Circle((0, 0), 0.64, fc='white', edgecolor='white', linewidth=0)
        ax.add_artist(centre_circle)
        
        # Center text dengan styling lebih baik
        ax.text(0, 0.09, str(total), ha='center', va='center',
                fontsize=22, fontweight='bold', color=CHART_COLORS["navy"])
        ax.text(0, -0.13, 'Total', ha='center', va='center',
                fontsize=10, color=CHART_COLORS["gray"], fontweight='bold')
        
        ax.set_facecolor('white')
        figure.patch.set_facecolor('white')
        
        figure.tight_layout(pad=0.8)
        return FigureCanvas(figure)
    
    def _create_horizontal_bar_chart(self) -> FigureCanvas:
        """Create horizontal bar chart: Top 5 Penyelenggara Beasiswa dengan full width."""
        figure = Figure(figsize=(10, 4), dpi=100)
        ax = figure.add_subplot(111)

        # Data dari database
        penyelenggara_rows = self.stat_data.get("penyelenggara_counts", [])
        penyelenggara = []
        values = []

        for row in penyelenggara_rows:
            nama = row.get("nama_penyelenggara")
            count = row.get("count")
            display_nama = str(nama) if nama else "(Tidak Ada)"
            penyelenggara.append(shorten(display_nama, width=22, placeholder="..."))
            values.append(int(count or 0))

        if not penyelenggara:
            penyelenggara = ["Belum Ada Data"]
            values = [0]
        
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
        ax.tick_params(axis='y', labelsize=9, colors=CHART_COLORS["navy"])
        ax.tick_params(axis='x', labelsize=8, colors=CHART_COLORS["gray"])
        
        # Styling
        ax.set_xlabel('Jumlah Beasiswa', fontsize=9, color=CHART_COLORS["gray"], fontweight='bold', labelpad=8)
        ax.set_xlim(0, max(1, int(max(values) * 1.35) + 1))
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
            self.stat_data = get_statistik_snapshot(top_limit=5)
            logger.info("Loaded statistik snapshot from service layer")
            
        except Exception as e:
            logger.error(f"Error loading statistics: {e}")
    
    def refresh_data(self):
        """Refresh statistics data."""
        self.load_statistics()
        self._populate_content()
        logger.info("Statistics data refreshed")
