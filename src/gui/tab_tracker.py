"""
Tracker Lamaran (Application Tracker) Tab for BeasiswaKu
Track scholarship applications with status visualization and analytics
"""

import logging
from typing import List, Dict, Any, Optional
from datetime import datetime
import matplotlib.pyplot as plt
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QTableWidget, QTableWidgetItem,
    QPushButton, QHeaderView, QFrame, QAbstractItemView, QScrollArea,
    QMessageBox, QInputDialog
)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont, QColor

from src.gui.design_tokens import *
from src.database.crud import delete_lamaran, edit_lamaran
from src.services.dashboard_service import get_tracker_snapshot
from src.services.status_utils import APPLICATION_STATUS_ORDER

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
    
    def __init__(self, user_id: int, event_bus=None, parent=None):
        super().__init__(parent)
        self.user_id = user_id
        self.event_bus = event_bus
        self._status_counts = {label: 0 for label in APPLICATION_STATUS_ORDER}
        self._month_counts: Dict[str, int] = {}
        self.analytics_layout: Optional[QHBoxLayout] = None
        self.proporsi_frame: Optional[QFrame] = None
        self.bulanan_frame: Optional[QFrame] = None
        self.table_count_label: Optional[QLabel] = None
        self.applications = self._fetch_applications()
        
        logger.info(f"Initializing TrackerTab for user {user_id}")
        self.init_ui()
        self._bind_event_bus()
        self.populate_table(self.applications)

    def _fetch_applications(self) -> List[Dict[str, Any]]:
        """Ambil data tracker dari service layer."""
        snapshot = get_tracker_snapshot(self.user_id)
        self._status_counts = dict(snapshot.get("status_counts", {}))
        self._month_counts = dict(snapshot.get("month_counts", {}))
        applications = list(snapshot.get("applications", []))

        logger.info(f"Loaded {len(applications)} application(s) from service")
        return applications

    def _get_status_counts(self) -> Dict[str, int]:
        """Ringkas jumlah lamaran per status untuk UI analytics."""
        return {
            label: int(self._status_counts.get(label, 0))
            for label in APPLICATION_STATUS_ORDER
        }

    def _get_month_counts(self) -> Dict[str, int]:
        """Ringkas jumlah lamaran per bulan (format YYYY-MM)."""
        return dict(sorted(self._month_counts.items()))

    def _bind_event_bus(self):
        """Subscribe to shared refresh events when available."""
        if self.event_bus is None:
            return

        self.event_bus.data_changed.connect(self._on_data_changed)

    def _on_data_changed(self, topic: str):
        """Reload tracker data after a shared mutation event."""
        if topic in {"lamaran.updated", "beasiswa.updated", "profile.updated"}:
            self.load_applications()

    def _emit_data_changed(self, topic: str):
        """Notify other tabs that shared data changed."""
        if self.event_bus is not None:
            self.event_bus.data_changed.emit(topic)
    
    def init_ui(self):
        """Initialize Tracker Tab UI."""
        self.setObjectName("trackerTabRoot")
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

        subtitle_label = QLabel("Pantau status lamaran dan progres bulananmu secara real-time")
        subtitle_label.setFont(QFont(FONT_FAMILY_PRIMARY, FONT_SIZE_BASE))
        subtitle_label.setStyleSheet(f"color: {COLOR_GRAY_600};")
        header_layout.addWidget(subtitle_label)
        
        main_layout.addLayout(header_layout)
        main_layout.addSpacing(20)
        
        # ===== SCROLL AREA =====
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setStyleSheet(f"border: none; background-color: {COLOR_GRAY_BACKGROUND};")
        
        scroll_widget = QWidget()
        scroll_widget.setObjectName("trackerScrollContent")
        scroll_layout = QVBoxLayout(scroll_widget)
        scroll_layout.setContentsMargins(0, 0, 0, 0)
        scroll_layout.setSpacing(0)
        
        # ===== SECTION 1: RIWAYAT LAMARAN (TABLE) =====
        section1_frame = self._create_riwayat_lamaran_section()
        scroll_layout.addWidget(section1_frame)
        scroll_layout.addSpacing(24)
        
        # ===== SECTION 2: ANALYTICS (2 COLUMNS) =====
        self.analytics_layout = QHBoxLayout()
        self.analytics_layout.setSpacing(24)
        self.analytics_layout.setContentsMargins(0, 0, 0, 0)
        
        # Left: Proporsi Status
        self.proporsi_frame = self._create_proporsi_status()
        self.analytics_layout.addWidget(self.proporsi_frame, 1)
        
        # Right: Lamaran per Bulan
        self.bulanan_frame = self._create_lamaran_per_bulan()
        self.analytics_layout.addWidget(self.bulanan_frame, 1)
        
        scroll_layout.addLayout(self.analytics_layout)
        scroll_layout.addStretch()
        
        scroll.setWidget(scroll_widget)
        main_layout.addWidget(scroll)

        self.setStyleSheet(f"""
            QWidget#trackerTabRoot {{
                background-color: {COLOR_GRAY_BACKGROUND};
            }}
            QWidget#trackerScrollContent {{
                background-color: transparent;
            }}
            QLabel {{
                border: none;
                background: transparent;
            }}
        """)
    
    def _create_riwayat_lamaran_section(self) -> QFrame:
        """Create riwayat lamaran table section."""
        frame = QFrame()
        frame.setObjectName("trackerTableCard")
        frame.setStyleSheet(f"""
            QFrame#trackerTableCard {{
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

        self.table_count_label = QLabel(f"{len(self.applications)} item")
        self.table_count_label.setFont(QFont(FONT_FAMILY_PRIMARY, FONT_SIZE_XS, QFont.Weight.DemiBold))
        self.table_count_label.setStyleSheet(
            f"background-color: {COLOR_GRAY_100}; color: {COLOR_GRAY_600}; "
            "padding: 4px 10px; border-radius: 10px;"
        )
        header_layout.addWidget(self.table_count_label)
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
                color: {COLOR_NAVY};
            }}
            QTableWidget::item:selected {{
                background-color: #e8f0ff;
                color: {COLOR_NAVY};
            }}
            QHeaderView::section {{
                background-color: {COLOR_WHITE};
                padding: 10px 12px;
                border: none;
                border-bottom: 1px solid {COLOR_GRAY_200};
                font-weight: bold;
                color: {COLOR_NAVY};
                font-size: 11px;
            }}
        """)
        
        # Table configuration
        self.table.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        self.table.setSelectionMode(QAbstractItemView.SelectionMode.SingleSelection)
        self.table.setAlternatingRowColors(False)
        self.table.setShowGrid(True)
        self.table.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        self.table.verticalHeader().setVisible(False)
        self.table.verticalHeader().setDefaultSectionSize(46)
        self.table.verticalHeader().setMinimumSectionSize(46)
        
        # Column widths
        header = self.table.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.ResizeMode.Stretch)  # Nama
        header.setSectionResizeMode(1, QHeaderView.ResizeMode.Interactive)  # Tanggal
        header.setSectionResizeMode(2, QHeaderView.ResizeMode.Interactive)  # Status
        header.setSectionResizeMode(3, QHeaderView.ResizeMode.Stretch)  # Catatan
        header.setSectionResizeMode(4, QHeaderView.ResizeMode.Interactive)  # Aksi

        self.table.setColumnWidth(1, 130)
        self.table.setColumnWidth(2, 120)
        self.table.setColumnWidth(4, 150)
        
        self.table.setMinimumHeight(300)
        layout.addWidget(self.table)
        
        return frame
    
    def _create_proporsi_status(self) -> QFrame:
        """Create proporsi status donut chart."""
        frame = QFrame()
        frame.setObjectName("trackerStatusCard")
        frame.setStyleSheet(f"""
            QFrame#trackerStatusCard {{
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
        
        status_counts = self._get_status_counts()
        total_lamaran = sum(status_counts.values())

        subtitle_label = QLabel(f"Berdasarkan total {total_lamaran} lamaran tercatat")
        subtitle_label.setFont(QFont(FONT_FAMILY_PRIMARY, FONT_SIZE_SM))
        subtitle_label.setStyleSheet(f"color: {COLOR_GRAY_600};")
        layout.addWidget(subtitle_label)
        
        # Chart
        canvas = self._create_donut_chart()
        canvas.setMinimumHeight(230)
        layout.addWidget(canvas)
        
        # Legend
        legend_layout = QHBoxLayout()
        legend_layout.setSpacing(16)

        legend_color_map = {
            "Pending": CHART_COLORS["blue"],
            "Diterima": CHART_COLORS["success"],
            "Ditolak": CHART_COLORS["error"],
        }
        legend_items = [
            (label, legend_color_map[label])
            for label in APPLICATION_STATUS_ORDER
        ]

        for idx, (label, color) in enumerate(legend_items):
            color_box = QFrame()
            color_box.setObjectName("legendSwatch")
            color_box.setStyleSheet(
                f"""
                QFrame#legendSwatch {{
                    background-color: {color};
                    border-radius: 2px;
                    min-width: 20px;
                    min-height: 20px;
                }}
                """
            )
            legend_layout.addWidget(color_box)

            item_label = QLabel(f"{label}\n{status_counts[label]} lamaran")
            item_label.setFont(QFont(FONT_FAMILY_PRIMARY, FONT_SIZE_SM))
            item_label.setStyleSheet(f"color: {color}; font-weight: bold;")
            legend_layout.addWidget(item_label)

            if idx < len(legend_items) - 1:
                legend_layout.addSpacing(12)
        
        legend_layout.addStretch()
        layout.addLayout(legend_layout)
        
        return frame
    
    def _create_lamaran_per_bulan(self) -> QFrame:
        """Create lamaran per bulan bar chart."""
        frame = QFrame()
        frame.setObjectName("trackerMonthlyCard")
        frame.setStyleSheet(f"""
            QFrame#trackerMonthlyCard {{
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
        canvas.setMinimumHeight(210)
        layout.addWidget(canvas)
        
        # Info box
        info_box = QFrame()
        info_box.setObjectName("monthlyInfoBox")
        info_box.setStyleSheet(f"""
            QFrame#monthlyInfoBox {{
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
        
        month_counts = self._get_month_counts()
        if month_counts:
            max_key = max(month_counts, key=month_counts.get)
            max_value = month_counts[max_key]
            try:
                max_label = datetime.strptime(max_key, "%Y-%m").strftime("%B %Y")
            except ValueError:
                max_label = max_key
            info_message = f"Terbanyak di bulan {max_label} dengan {max_value} lamaran"
        else:
            info_message = "Belum ada data lamaran bulanan"

        info_text = QLabel(info_message)
        info_text.setFont(QFont(FONT_FAMILY_PRIMARY, FONT_SIZE_SM))
        info_text.setStyleSheet(f"color: {COLOR_ORANGE}; font-weight: bold;")
        info_layout.addWidget(info_text)
        
        layout.addWidget(info_box)
        
        return frame
    
    def _create_donut_chart(self) -> FigureCanvas:
        """Create donut chart for status distribution."""
        figure = Figure(figsize=(5.5, 3.2), dpi=100)
        ax = figure.add_subplot(111)

        status_counts = self._get_status_counts()
        labels = list(APPLICATION_STATUS_ORDER)
        sizes = [status_counts[label] for label in labels]
        color_map = {
            "Pending": CHART_COLORS["blue"],
            "Diterima": CHART_COLORS["success"],
            "Ditolak": CHART_COLORS["error"],
        }
        colors = [color_map[label] for label in labels]
        total = sum(sizes)

        if total > 0:
            wedges, texts, autotexts = ax.pie(
                sizes,
                labels=None,
                colors=colors,
                autopct=lambda pct: f"{pct:.0f}%" if pct > 0 else "",
                pctdistance=0.78,
                startangle=90,
                textprops={"fontsize": 9, "weight": "bold"},
                wedgeprops=dict(width=0.34, edgecolor="white", linewidth=2),
            )

            for autotext in autotexts:
                autotext.set_color("white")
                autotext.set_fontweight("bold")
                autotext.set_fontsize(10)
        else:
            ax.pie(
                [1],
                labels=["Belum Ada Data"],
                colors=[CHART_COLORS["light_gray"]],
                startangle=90,
                textprops={"fontsize": 9, "weight": "bold", "color": CHART_COLORS["gray"]},
                wedgeprops=dict(width=0.4, edgecolor="white", linewidth=2),
            )
        
        # Center circle text
        centre_circle = plt.Circle((0, 0), 0.66, fc='white', edgecolor='white', linewidth=0)
        ax.add_artist(centre_circle)
        
        ax.text(0, 0.10, str(total), ha='center', va='center',
                fontsize=20, fontweight='bold', color=CHART_COLORS['navy'])
        ax.text(0, -0.14, 'Total', ha='center', va='center',
                fontsize=10, fontweight='bold', color=CHART_COLORS['gray'])
        
        ax.set_facecolor('white')
        figure.patch.set_facecolor('white')
        figure.tight_layout(pad=0.5)
        
        return FigureCanvas(figure)
    
    def _create_bar_chart(self) -> FigureCanvas:
        """Create bar chart for monthly applications."""
        figure = Figure(figsize=(5.5, 3.1), dpi=100)
        ax = figure.add_subplot(111)

        month_counts = self._get_month_counts()
        if month_counts:
            month_keys = sorted(month_counts.keys())[-5:]
            months = []
            values = []
            for key in month_keys:
                values.append(month_counts[key])
                try:
                    months.append(datetime.strptime(key, "%Y-%m").strftime("%b %y"))
                except ValueError:
                    months.append(key)
        else:
            months = ["-"]
            values = [0]

        max_value = max(values) if values else 0
        colors_list = [CHART_COLORS["orange"] if value == max_value and max_value > 0 else CHART_COLORS["navy"] for value in values]

        bars = ax.bar(months, values, color=colors_list, edgecolor='none', width=0.6, alpha=0.85)
        
        # Value labels on top
        for bar, value in zip(bars, values):
            height = bar.get_height()
            ax.text(bar.get_x() + bar.get_width()/2., height + 0.1,
                   f'{int(value)}', ha='center', va='bottom', fontsize=10, 
                   fontweight='bold', color=CHART_COLORS['navy'])
        
        # Styling
        ax.set_ylim(0, max(1, max_value + 1))
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
        self.applications = self._fetch_applications()
        self.populate_table(self.applications)
        self._refresh_analytics_widgets()

    def _replace_analytics_widget(self, index: int, new_widget: QWidget):
        """Replace analytics panel widget at index with refreshed content."""
        if self.analytics_layout is None:
            return

        item = self.analytics_layout.itemAt(index)
        old_widget = item.widget() if item is not None else None
        if old_widget is not None:
            self.analytics_layout.replaceWidget(old_widget, new_widget)
            old_widget.deleteLater()
        else:
            self.analytics_layout.insertWidget(index, new_widget, 1)

    def _refresh_analytics_widgets(self):
        """Rebuild donut and monthly charts after data updates."""
        self.proporsi_frame = self._create_proporsi_status()
        self.bulanan_frame = self._create_lamaran_per_bulan()
        self._replace_analytics_widget(0, self.proporsi_frame)
        self._replace_analytics_widget(1, self.bulanan_frame)
    
    def populate_table(self, apps):
        """Populate table dengan data."""
        self.table.clearSpans()

        if self.table_count_label:
            label = "item" if len(apps) == 1 else "item"
            self.table_count_label.setText(f"{len(apps)} {label}")

        if not apps:
            self.table.setRowCount(1)
            self.table.setColumnCount(5)
            self.table.setSpan(0, 0, 1, 5)
            empty_item = QTableWidgetItem("Belum ada lamaran. Klik 'Tambah Lamaran' untuk memulai.")
            empty_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            empty_item.setForeground(QColor(COLOR_GRAY_500))
            self.table.setItem(0, 0, empty_item)
            return

        self.table.setRowCount(len(apps))
        
        for row_idx, app in enumerate(apps):
            self.table.setRowHeight(row_idx, 50)

            nama = app["nama"]
            tanggal = app["tanggal"]
            status = app["status"]
            catatan = app["catatan"]
            
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
        badge_frame.setObjectName("trackerStatusBadge")
        badge_layout = QHBoxLayout(badge_frame)
        badge_layout.setContentsMargins(8, 4, 8, 4)
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
        badge_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        badge_label.setStyleSheet(f"""
            color: {text_color};
            font-weight: bold;
            padding: 3px 8px;
        """)
        
        badge_frame.setStyleSheet(f"""
            QFrame#trackerStatusBadge {{
                background-color: {bg_color};
                border: 1px solid {text_color};
                border-radius: 12px;
            }}
        """)
        
        badge_layout.addWidget(badge_label)
        return badge_frame
    
    def _create_action_buttons(self, row_idx: int) -> QFrame:
        """Create action buttons (edit, delete)."""
        action_frame = QFrame()
        action_frame.setObjectName("trackerActionCell")
        action_frame.setMinimumHeight(30)
        action_frame.setMaximumHeight(30)
        action_frame.setStyleSheet("QFrame#trackerActionCell { background: transparent; border: none; }")

        action_layout = QHBoxLayout(action_frame)
        action_layout.setContentsMargins(0, 0, 0, 0)
        action_layout.setSpacing(6)
        
        # Edit button
        edit_btn = QPushButton("Edit")
        edit_btn.setMinimumSize(54, 28)
        edit_btn.setMaximumHeight(28)
        edit_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        edit_btn.setStyleSheet(f"""
            QPushButton {{
                background-color: {COLOR_WHITE};
                border: 1px solid {COLOR_GRAY_300};
                border-radius: 6px;
                font-size: 10px;
                color: {COLOR_GRAY_700};
                font-weight: 600;
            }}
            QPushButton:hover {{
                background-color: {COLOR_GRAY_100};
                border: 1px solid {COLOR_GRAY_400};
            }}
        """)
        edit_btn.clicked.connect(lambda: self.on_edit_lamaran(row_idx))
        action_layout.addWidget(edit_btn)
        
        # Delete button
        delete_btn = QPushButton("Hapus")
        delete_btn.setMinimumSize(60, 28)
        delete_btn.setMaximumHeight(28)
        delete_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        delete_btn.setStyleSheet(f"""
            QPushButton {{
                background-color: {COLOR_WHITE};
                border: 1px solid #f2c4c4;
                border-radius: 6px;
                font-size: 10px;
                color: {COLOR_ERROR};
                font-weight: 600;
            }}
            QPushButton:hover {{
                background-color: {COLOR_ERROR_LIGHT};
                border: 1px solid {COLOR_ERROR};
            }}
        """)
        delete_btn.clicked.connect(lambda: self.on_delete_lamaran(row_idx))
        action_layout.addWidget(delete_btn)

        return action_frame
    
    def on_tambah_lamaran(self):
        """Handle add application."""
        logger.info("Add lamaran clicked")
        main_window = self.window()
        tabs = getattr(main_window, "tabs", None)
        if tabs is not None:
            tabs.setCurrentIndex(1)
            return

        QMessageBox.warning(
            self,
            "Tambah Lamaran",
            "Navigasi ke tab Beasiswa tidak tersedia pada konteks saat ini.",
        )
    
    def on_delete_lamaran(self, row_idx: int):
        """Handle delete application."""
        logger.info(f"Delete lamaran at row {row_idx}")
        if row_idx < 0 or row_idx >= len(self.applications):
            return

        app = self.applications[row_idx]
        lamaran_id = int(app.get("id") or 0)
        if lamaran_id <= 0:
            QMessageBox.warning(self, "Hapus Lamaran", "ID lamaran tidak valid.")
            return

        answer = QMessageBox.question(
            self,
            "Konfirmasi Hapus",
            f"Hapus lamaran untuk '{app.get('nama', '(Tanpa Judul)')}'?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No,
        )
        if answer != QMessageBox.StandardButton.Yes:
            return

        success, message = delete_lamaran(lamaran_id)
        if success:
            QMessageBox.information(self, "Hapus Lamaran", message)
            self.load_applications()
            self._emit_data_changed("lamaran.updated")
            return

        QMessageBox.warning(self, "Hapus Lamaran", message)

    def on_edit_lamaran(self, row_idx: int):
        """Handle edit application status."""
        logger.info(f"Edit lamaran at row {row_idx}")
        if row_idx < 0 or row_idx >= len(self.applications):
            return

        app = self.applications[row_idx]
        lamaran_id = int(app.get("id") or 0)
        if lamaran_id <= 0:
            QMessageBox.warning(self, "Update Lamaran", "ID lamaran tidak valid.")
            return

        status_options = ["Pending", "Diterima", "Ditolak"]
        current_status = app.get("status", "Pending")
        default_index = status_options.index(current_status) if current_status in status_options else 0

        selected_status, ok = QInputDialog.getItem(
            self,
            "Update Status Lamaran",
            f"Status untuk '{app.get('nama', '(Tanpa Judul)')}':",
            status_options,
            default_index,
            False,
        )
        if not ok:
            return

        current_note = "" if app.get("catatan") in {None, "-"} else str(app.get("catatan"))
        updated_note, note_ok = QInputDialog.getText(
            self,
            "Update Catatan",
            "Catatan (opsional):",
            text=current_note,
        )
        if not note_ok:
            updated_note = current_note

        db_status_map = {
            "Pending": "Pending",
            "Diterima": "Accepted",
            "Ditolak": "Rejected",
        }
        db_status = db_status_map.get(selected_status, "Pending")

        success, message = edit_lamaran(lamaran_id, status=db_status, catatan=updated_note)
        if success:
            QMessageBox.information(self, "Update Lamaran", message)
            self.load_applications()
            self._emit_data_changed("lamaran.updated")
            return

        QMessageBox.warning(self, "Update Lamaran", message)
