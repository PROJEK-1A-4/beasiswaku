"""
Beasiswa (Scholarship List) Tab for BeasiswaKu
Professional scholarship listing with search, filters, and actions
"""

import logging
from typing import Optional, Dict, List, Any
from datetime import datetime, date
import csv
import os

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QFrame, QLineEdit,
    QPushButton, QComboBox, QTableWidget, QTableWidgetItem, QHeaderView,
    QAbstractItemView, QFileDialog, QSpacerItem, QSizePolicy, QMessageBox
)
from PyQt6.QtCore import Qt, QSize
from PyQt6.QtGui import QFont, QIcon, QColor

from src.gui.design_tokens import *
from src.database.crud import (
    add_favorit,
    add_lamaran,
    check_user_applied,
    delete_favorit,
)
from src.gui.tab_beranda import BerandaTab
from src.gui.tab_beasiswa import BeasiswaTab
from src.gui.tab_tracker import TrackerTab          # ← FavoritTab BELUM ditambah di sini
from src.gui.tab_statistik import StatistikTab
from src.gui.tab_profil import ProfileTab
# Setup logging
logger = logging.getLogger(__name__)


# ==================== DEADLINE HELPER FUNCTIONS ====================

def _get_days_until_deadline(deadline_str: str) -> Optional[int]:
    # Menggunakan date.today() untuk menghitung selisih hari REAL-TIME
    # Bukan hardcoded berdasarkan tanggal tertentu
    deadline_date = datetime.strptime(deadline_str, "%Y-%m-%d").date()
    today = date.today()
    days_remaining = (deadline_date - today).days
    return days_remaining


def _get_deadline_color(days_remaining: Optional[int]) -> str:
    """
    Get color for deadline display based on days remaining.
    
    Color scheme:
    - Red (COLOR_ERROR): 7 days or less remaining
    - Yellow (COLOR_WARNING): 8-30 days remaining
    - Green (COLOR_SUCCESS): More than 30 days remaining
    - Gray (COLOR_GRAY_500): If days_remaining is None (unparseable)
    
    Args:
        days_remaining (int or None): Days until deadline
    
    Returns:
        str: Hex color code
    
    def _get_deadline_color(days_remaining: Optional[int]) -> str:
    if days_remaining <= 7:
        return COLOR_ERROR      # Red
    elif days_remaining <= 30:
        return COLOR_WARNING    # Yellow
    else:
        return COLOR_SUCCESS    # Green
    - Action buttons: Deadline Dekat, Refresh, Export CSV
    - Professional table dengan 7 columns
    - Status badges (Buka, Segera Tutup, Tutup)
    - Action icons: View, Bookmark, Apply
    """
    
    def __init__(self, user_id: int, event_bus=None, parent=None):
        super().__init__(parent)
        self.user_id = user_id
        self.event_bus = event_bus
        self.beasiswa_data: List[Dict[str, Any]] = []
        self.displayed_data: List[Dict[str, Any]] = []
        self.refresh_btn: Optional[QPushButton] = None
        self.sync_btn: Optional[QPushButton] = None
        self._sync_thread = None
        self._sync_in_progress = False
        
        # ===== PAGINATION VARIABLES =====
        self.current_page: int = 1
        self.items_per_page: int = 20
        self.total_pages: int = 0
        self.filtered_data: List[Dict[str, Any]] = []
        
        logger.info(f"Initializing BeasiswaTab")
        self.init_ui()
        self._bind_event_bus()
        loaded_count = self.load_beasiswa_data()
        if loaded_count == 0:
            self.sync_from_web(auto_trigger=True)
    
    def init_ui(self):
        """Initialize Beasiswa Tab UI dengan search, filters, dan table."""
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(24, 20, 24, 20)
        main_layout.setSpacing(0)
        
        self.setStyleSheet(f"background-color: {COLOR_GRAY_BACKGROUND};")
        
        # ===== HEADER SECTION =====
        header_layout = QVBoxLayout()
        header_layout.setSpacing(4)
        header_layout.setContentsMargins(0, 0, 0, 0)
        
        title_label = QLabel("Daftar Beasiswa")
        title_font = QFont(FONT_FAMILY_PRIMARY, 28)
        title_font.setWeight(QFont.Weight.Bold)
        title_label.setFont(title_font)
        title_label.setStyleSheet(f"color: {COLOR_NAVY}; padding: 0px;")
        header_layout.addWidget(title_label)
        
        # Subtitle dengan last updated time
        self.subtitle_label = QLabel(f"Terakhir diperbaharui: {datetime.now().strftime('%d %b %Y %H:%M')}")
        self.subtitle_label.setFont(QFont(FONT_FAMILY_PRIMARY, FONT_SIZE_BASE))
        # Pagination state variables:
        self.current_page: int = 1
        self.items_per_page: int = 20
        self.total_pages: int = 0

    # populate_table() dengan page slicing:
    def populate_table(self, data: List[Dict[str, Any]], page: int = 1):
        start_idx = (self.current_page - 1) * self.items_per_page
        end_idx = start_idx + self.items_per_page
        page_data = data[start_idx:end_idx]  # Hanya render 20 item per page
        main_layout.addLayout(header_layout)
        main_layout.addSpacing(20)
            
        # ===== TOOLBAR SECTION =====
        toolbar_layout = QHBoxLayout()
        toolbar_layout.setSpacing(12)
        toolbar_layout.setContentsMargins(0, 0, 0, 0)
        
        # Search box
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Cari nama beasiswa...")
        self.search_input.setMinimumHeight(44)
        self.search_input.setMinimumWidth(350)
        self.search_input.setFont(QFont(FONT_FAMILY_PRIMARY, FONT_SIZE_BASE))
        self.search_input.setStyleSheet(f"""
            QLineEdit {{
                background-color: {COLOR_WHITE};
                border: 1px solid {COLOR_GRAY_200};
                border-radius: {BORDER_RADIUS_MD};
                padding: 10px 14px;
                color: {COLOR_NAVY};
                font-size: {FONT_SIZE_BASE}px;
            }}
            QLineEdit::placeholder {{
                color: {COLOR_GRAY_400};
            }}
            QLineEdit:focus {{
                border: 2px solid {COLOR_ORANGE};
                padding: 9px 13px;
            }}
        """)
        self.search_input.textChanged.connect(self.filter_table)
        toolbar_layout.addWidget(self.search_input)
        
        # Filter dropdown 1 - Status
        status_label = QLabel("Status")
        status_label.setFont(QFont(FONT_FAMILY_PRIMARY, FONT_SIZE_SM))
        status_label.setStyleSheet(f"color: {COLOR_GRAY_600};")
        
        self.status_filter = QComboBox()
        self.status_filter.addItems(["Semua", *SCHOLARSHIP_STATUS_ORDER])
        self.status_filter.setMinimumHeight(40)
        self.status_filter.setMaximumWidth(150)
        self.status_filter.setFont(QFont(FONT_FAMILY_PRIMARY, FONT_SIZE_BASE))
        self.status_filter.setStyleSheet(f"""
            QComboBox {{
                background-color: {COLOR_WHITE};
                border: 1px solid {COLOR_GRAY_200};
                border-radius: {BORDER_RADIUS_MD};
                padding: 8px 12px;
                color: {COLOR_NAVY};
            }}
            QComboBox::drop-down {{
                border: none;
            }}
            QComboBox::down-arrow {{
                image: none;
            }}
        """)
        self.status_filter.currentTextChanged.connect(self.filter_table)
        toolbar_layout.addWidget(self.status_filter)
        
        # Filter dropdown 2 - Jenjang
        jenjang_label = QLabel("Jenjang")
        jenjang_label.setFont(QFont(FONT_FAMILY_PRIMARY, FONT_SIZE_SM))
        jenjang_label.setStyleSheet(f"color: {COLOR_GRAY_600};")
        
        self.jenjang_filter = QComboBox()
        self.jenjang_filter.addItems(["Semua", "D3", "D4", "S1", "S2"])
        self.jenjang_filter.setMinimumHeight(40)
        self.jenjang_filter.setMaximumWidth(150)
        self.jenjang_filter.setFont(QFont(FONT_FAMILY_PRIMARY, FONT_SIZE_BASE))
        self.jenjang_filter.setStyleSheet(f"""
            QComboBox {{
                background-color: {COLOR_WHITE};
                border: 1px solid {COLOR_GRAY_200};
                border-radius: {BORDER_RADIUS_MD};
                padding: 8px 12px;
                color: {COLOR_NAVY};
            }}
            QComboBox::drop-down {{
                border: none;
            }}
            QComboBox::down-arrow {{
                image: none;
            }}
        """)
        self.jenjang_filter.currentTextChanged.connect(self.filter_table)
        toolbar_layout.addWidget(self.jenjang_filter)
        
        toolbar_layout.addStretch()
        
        # Deadline Dekat button
        deadline_btn = QPushButton("⚠ Deadline Dekat")
        deadline_btn.setMinimumHeight(40)
        deadline_btn.setFont(QFont(FONT_FAMILY_PRIMARY, FONT_SIZE_BASE))
        deadline_btn.setStyleSheet(f"""
            QPushButton {{
                background-color: transparent;
                border: 2px solid {COLOR_ERROR};
                border-radius: {BORDER_RADIUS_MD};
                color: {COLOR_ERROR};
                padding: 8px 16px;
                font-weight: bold;
            }}
            QPushButton:hover {{
                background-color: {COLOR_ERROR_LIGHT};
            }}
            QPushButton:pressed {{
                background-color: {COLOR_ERROR_LIGHT};
                border: 2px solid {COLOR_ERROR_DARK};
            }}
        """)
        deadline_btn.clicked.connect(self.filter_by_deadline)
        toolbar_layout.addWidget(deadline_btn)
        
        # Refresh button
        self.refresh_btn = QPushButton("↻ Refresh")
        self.refresh_btn.setMinimumHeight(40)
        self.refresh_btn.setFont(QFont(FONT_FAMILY_PRIMARY, FONT_SIZE_BASE))
        self.refresh_btn.setStyleSheet(f"""
            QPushButton {{
                background-color: {COLOR_WHITE};
                border: 1px solid {COLOR_GRAY_200};
                border-radius: {BORDER_RADIUS_MD};
                color: {COLOR_NAVY};
                padding: 8px 16px;
                font-weight: bold;
            }}
            QPushButton:hover {{
                background-color: {COLOR_GRAY_100};
                border: 1px solid {COLOR_GRAY_300};
            }}
            QPushButton:pressed {{
                background-color: {COLOR_GRAY_200};
            }}
        """)
        self.refresh_btn.clicked.connect(self.refresh_data)
        toolbar_layout.addWidget(self.refresh_btn)

        # Sync web button
        self.sync_btn = QPushButton("🌐 Sync Web")
        self.sync_btn.setMinimumHeight(40)
        self.sync_btn.setFont(QFont(FONT_FAMILY_PRIMARY, FONT_SIZE_BASE))
        self.sync_btn.setStyleSheet(f"""
            QPushButton {{
                background-color: {COLOR_WHITE};
                border: 1px solid {COLOR_ORANGE};
                border-radius: {BORDER_RADIUS_MD};
                color: {COLOR_ORANGE};
                padding: 8px 16px;
                font-weight: bold;
            }}
            QPushButton:hover {{
                background-color: {COLOR_WARNING_LIGHT};
            }}
            QPushButton:pressed {{
                background-color: {COLOR_WARNING_LIGHT};
                border: 1px solid {COLOR_ORANGE_DARK};
            }}
        """)
        self.sync_btn.clicked.connect(self.sync_from_web)
        toolbar_layout.addWidget(self.sync_btn)
        
        # Export CSV button
        export_btn = QPushButton("⬇ Export CSV")
        export_btn.setMinimumHeight(40)
        export_btn.setFont(QFont(FONT_FAMILY_PRIMARY, FONT_SIZE_BASE))
        export_btn.setStyleSheet(f"""
            QPushButton {{
                background-color: {COLOR_ORANGE};
                border: none;
                border-radius: {BORDER_RADIUS_MD};
                color: white;
                padding: 8px 16px;
                font-weight: bold;
            }}
            QPushButton:hover {{
                background-color: {COLOR_ORANGE_DARK};
            }}
            QPushButton:pressed {{
                background-color: {COLOR_ORANGE_LIGHT};
                color: {COLOR_NAVY};
            }}
        """)
        export_btn.clicked.connect(self.export_to_csv)
        toolbar_layout.addWidget(export_btn)
        
        main_layout.addLayout(toolbar_layout)
        main_layout.addSpacing(16)
        
        # ===== TABLE SECTION =====
        self.table = QTableWidget()
        self.table.setColumnCount(7)
        self.table.setHorizontalHeaderLabels([
            "NO", "NAMA BEASISWA", "PENYELENGGARA", 
            "JENJANG", "DEADLINE", "STATUS", "AKSI"
        ])
        
        # Table styling
        self.table.setFont(QFont(FONT_FAMILY_PRIMARY, FONT_SIZE_BASE))
        self.table.setStyleSheet(f"""
            QTableWidget {{
                background-color: {COLOR_WHITE};
                gridline-color: {COLOR_GRAY_200};
                border: 1px solid {COLOR_GRAY_200};
                border-radius: {BORDER_RADIUS_MD};
            }}
            QTableWidget::item {{
                padding: 12px;
                border-bottom: 1px solid {COLOR_GRAY_100};
            }}
            QTableWidget::item:selected {{
                background-color: {COLOR_GRAY_100};
            }}
            QHeaderView::section {{
                background-color: {COLOR_GRAY_50};
                padding: 12px;
                border: none;
                border-bottom: 1px solid {COLOR_GRAY_200};
                font-weight: bold;
                color: {COLOR_GRAY_700};
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
        header.setSectionResizeMode(0, QHeaderView.ResizeMode.ResizeToContents)  # NO
        header.setSectionResizeMode(1, QHeaderView.ResizeMode.Stretch)  # NAMA
        header.setSectionResizeMode(2, QHeaderView.ResizeMode.ResizeToContents)  # PENYELENGGARA
        header.setSectionResizeMode(3, QHeaderView.ResizeMode.ResizeToContents)  # JENJANG
        header.setSectionResizeMode(4, QHeaderView.ResizeMode.ResizeToContents)  # DEADLINE
        header.setSectionResizeMode(5, QHeaderView.ResizeMode.Interactive)  # STATUS
        header.setSectionResizeMode(6, QHeaderView.ResizeMode.Interactive)  # AKSI

        self.table.setColumnWidth(5, 130)
        self.table.setColumnWidth(6, 170)
        self.table.verticalHeader().setDefaultSectionSize(44)
        
        self.table.setMinimumHeight(400)
        main_layout.addWidget(self.table)
        main_layout.addSpacing(16)
        
        # ===== PAGINATION SECTION =====
        pagination_layout = QHBoxLayout()
        pagination_layout.setContentsMargins(0, 0, 0, 0)
        pagination_layout.setSpacing(12)
        
        # Previous button
        self.prev_btn = QPushButton("← Sebelumnya")
        self.prev_btn.setMinimumHeight(36)
        self.prev_btn.setMaximumWidth(120)
        self.prev_btn.setFont(QFont(FONT_FAMILY_PRIMARY, FONT_SIZE_SM))
        self.prev_btn.setStyleSheet(f"""
            QPushButton {{
                background-color: {COLOR_WHITE};
                border: 1px solid {COLOR_GRAY_200};
                border-radius: {BORDER_RADIUS_MD};
                color: {COLOR_NAVY};
                padding: 6px 12px;
                font-weight: bold;
            }}
            QPushButton:hover {{
                background-color: {COLOR_GRAY_100};
                border: 1px solid {COLOR_GRAY_300};
            }}
            QPushButton:pressed {{
                background-color: {COLOR_GRAY_200};
            }}
            QPushButton:disabled {{
                background-color: {COLOR_GRAY_100};
                color: {COLOR_GRAY_400};
                border: 1px solid {COLOR_GRAY_200};
            }}
        """)
        self.prev_btn.clicked.connect(self._on_previous_page)
        pagination_layout.addWidget(self.prev_btn)
        
        # Page info label
        pagination_layout.addStretch()
        self.page_info_label = QLabel("Halaman 1 dari 1")
        self.page_info_label.setFont(QFont(FONT_FAMILY_PRIMARY, FONT_SIZE_SM))
        self.page_info_label.setStyleSheet(f"color: {COLOR_GRAY_600};")
        self.page_info_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        pagination_layout.addWidget(self.page_info_label)
        pagination_layout.addStretch()
        
        # Next button
        self.next_btn = QPushButton("Selanjutnya →")
        self.next_btn.setMinimumHeight(36)
        self.next_btn.setMaximumWidth(120)
        self.next_btn.setFont(QFont(FONT_FAMILY_PRIMARY, FONT_SIZE_SM))
        self.next_btn.setStyleSheet(f"""
            QPushButton {{
                background-color: {COLOR_WHITE};
                border: 1px solid {COLOR_GRAY_200};
                border-radius: {BORDER_RADIUS_MD};
                color: {COLOR_NAVY};
                padding: 6px 12px;
                font-weight: bold;
            }}
            QPushButton:hover {{
                background-color: {COLOR_GRAY_100};
                border: 1px solid {COLOR_GRAY_300};
            }}
            QPushButton:pressed {{
                background-color: {COLOR_GRAY_200};
            }}
            QPushButton:disabled {{
                background-color: {COLOR_GRAY_100};
                color: {COLOR_GRAY_400};
                border: 1px solid {COLOR_GRAY_200};
            }}
        """)
        self.next_btn.clicked.connect(self._on_next_page)
        pagination_layout.addWidget(self.next_btn)
        
        main_layout.addLayout(pagination_layout)
        main_layout.addStretch()
    
    def _create_status_badge(self, status: str) -> QWidget:
        """Create a styled status badge."""
        badge_frame = QFrame()
        badge_frame.setObjectName("statusBadgeFrame")
        badge_layout = QHBoxLayout(badge_frame)
        badge_layout.setContentsMargins(0, 0, 0, 0)
        badge_layout.setSpacing(0)
        badge_frame.setMinimumHeight(28)
        
        # Determine colors based on status
        if status == "Buka":
            bg_color = "#d1fae5"  # Light green
            text_color = COLOR_SUCCESS
            border_color = COLOR_SUCCESS
        elif status == "Segera Tutup":
            bg_color = COLOR_WARNING_LIGHT
            text_color = COLOR_ORANGE
            border_color = COLOR_ORANGE
        else:  # Tutup
            bg_color = "#e5e7eb"
            text_color = COLOR_GRAY_500
            border_color = COLOR_GRAY_400
        
        badge_label = QLabel(status)
        badge_label.setObjectName("statusBadgeLabel")
        badge_label.setFont(QFont(FONT_FAMILY_PRIMARY, 9))
        badge_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        badge_label.setStyleSheet(f"""
            background-color: {bg_color};
            color: {text_color};
            font-weight: bold;
            padding: 4px 12px;
            border: 1px solid {border_color};
            border-radius: 5px;
        """)

        badge_frame.setStyleSheet(f"""
            QFrame#statusBadgeFrame {{
                background: transparent;
                border: none;
            }}
        """)

        badge_layout.addWidget(badge_label)
        return badge_frame
    
    def _create_action_buttons(self, row_id: int) -> QWidget:
        """Create action buttons (View, Bookmark, Apply)."""
        action_frame = QFrame()
        action_layout = QHBoxLayout(action_frame)
        action_layout.setContentsMargins(6, 4, 6, 4)
        action_layout.setSpacing(6)
        action_frame.setMinimumSize(150, 34)
        
        # View button
        view_btn = QPushButton("Detail")
        view_btn.setMinimumSize(46, 28)
        view_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        view_btn.setStyleSheet(f"""
            QPushButton {{
                background-color: {COLOR_WHITE};
                border: 1px solid {COLOR_GRAY_300};
                border-radius: 6px;
                font-size: 10px;
                color: {COLOR_GRAY_700};
                font-weight: 600;
                padding: 0 6px;
            }}
            QPushButton:hover {{
                background-color: {COLOR_GRAY_100};
                border: 1px solid {COLOR_GRAY_400};
            }}
        """)
        view_btn.clicked.connect(lambda: self.view_beasiswa(row_id))
        action_layout.addWidget(view_btn)
        
        # Bookmark button
        bookmark_btn = QPushButton("Fav")
        bookmark_btn.setMinimumSize(40, 28)
        bookmark_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        bookmark_btn.setStyleSheet(f"""
            QPushButton {{
                background-color: {COLOR_WHITE};
                border: 1px solid {COLOR_ORANGE};
                border-radius: 6px;
                font-size: 10px;
                color: {COLOR_ORANGE};
                font-weight: 600;
                padding: 0 6px;
            }}
            QPushButton:hover {{
                background-color: {COLOR_WARNING_LIGHT};
            }}
        """)
        bookmark_btn.clicked.connect(lambda: self.toggle_bookmark(row_id))
        action_layout.addWidget(bookmark_btn)
        
        # Apply button
        apply_btn = QPushButton("Lamar")
        apply_btn.setMinimumSize(48, 28)
        apply_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        apply_btn.setStyleSheet(f"""
            QPushButton {{
                background-color: {COLOR_SUCCESS_LIGHT};
                border: 1px solid {COLOR_SUCCESS};
                border-radius: 6px;
                font-size: 10px;
                color: {COLOR_SUCCESS};
                font-weight: 700;
                padding: 0 6px;
            }}
            QPushButton:hover {{
                background-color: #c5f2df;
            }}
        """)
        apply_btn.clicked.connect(lambda: self.apply_beasiswa(row_id))
        action_layout.addWidget(apply_btn)

        return action_frame
    
    def load_beasiswa_data(self) -> int:
        """Load beasiswa data dari database."""
        try:
            self.beasiswa_data = get_beasiswa_table_data()
            
            logger.info(f"Loaded {len(self.beasiswa_data)} beasiswa")
            self.populate_table(self.beasiswa_data, page=1)
            self.subtitle_label.setText(
                "Terakhir diperbaharui: "
                f"{datetime.now().strftime('%d %b %Y %H:%M')} | "
                f"Total {len(self.beasiswa_data)} | "
                f"DB {self._current_db_name()}"
            )
            return len(self.beasiswa_data)
        except Exception as e:
            logger.error(f"Error loading beasiswa data: {e}")
            self.beasiswa_data = []
            self.populate_table([], page=1)
            self.subtitle_label.setText(
                "Gagal memuat data | "
                f"DB {self._current_db_name()}"
            )
            return 0

    def _current_db_name(self) -> str:
        """Get current sqlite filename for quick diagnostics in UI."""
        try:
            return DatabaseManager().db_path.name
        except Exception:
            return "unknown"

    def _bind_event_bus(self):
        """Subscribe to shared refresh events when available."""
        if self.event_bus is None:
            return

        self.event_bus.data_changed.connect(self._on_data_changed)

    def _on_data_changed(self, topic: str):
        """Reload scholarship data after a shared mutation event."""
        if topic in {"beasiswa.updated", "favorit.updated", "lamaran.updated", "profile.updated"}:
            self.refresh_data()

    def _emit_data_changed(self, topic: str):
        """Notify other tabs that shared data changed."""
        if self.event_bus is not None:
            self.event_bus.data_changed.emit(topic)

    def _set_sync_state(self, syncing: bool):
        """Toggle button states while sync is running."""
        self._sync_in_progress = syncing

        if self.refresh_btn:
            self.refresh_btn.setEnabled(not syncing)

        if self.sync_btn:
            self.sync_btn.setEnabled(not syncing)
            self.sync_btn.setText("⏳ Syncing..." if syncing else "🌐 Sync Web")

    def _finish_sync(self, summary: Dict[str, int]):
        """Finalize sync flow and reload table."""
        loaded = self.load_beasiswa_data()
        self.subtitle_label.setText(
            "Terakhir diperbaharui: "
            f"{datetime.now().strftime('%d %b %Y %H:%M')} | "
            f"Scraped {summary.get('scraped', 0)} | "
            f"Baru {summary.get('inserted', 0)} | "
            f"Update {summary.get('updated', 0)} | "
            f"Total tampil {loaded} | "
            f"DB {self._current_db_name()}"
        )
        self._emit_data_changed("beasiswa.updated")
        self._set_sync_state(False)

    def _on_sync_finished(self, scrape_payload: object):
        """Handle async scrape completion."""
        summary = sync_beasiswa_from_scraper(scrape_payload if isinstance(scrape_payload, dict) else None)
        self._finish_sync(summary)

    def _on_sync_error(self, message: str):
        """Handle async scrape error."""
        logger.error("Beasiswa sync error: %s", message)
        self.subtitle_label.setText(f"Sync gagal: {message} | DB {self._current_db_name()}")
        self._set_sync_state(False)

    def sync_from_web(self, auto_trigger: bool = False):
        """Sync latest scholarship data from web scraper into database."""
        if self._sync_in_progress:
            return

        self._set_sync_state(True)
        if auto_trigger:
            self.subtitle_label.setText("Database kosong, sinkronisasi web dimulai...")
        else:
            self.subtitle_label.setText("Sinkronisasi web sedang berjalan...")

        thread = get_scraper_thread()
        if thread is None:
            summary = sync_beasiswa_from_scraper()
            self._finish_sync(summary)
            return

        self._sync_thread = thread
        self._sync_thread.finished.connect(self._on_sync_finished)
        self._sync_thread.error.connect(self._on_sync_error)
        self._sync_thread.start()
    
    def populate_table(self, data: List[Dict[str, Any]], page: int = 1):
        """
        Populate table dengan data untuk halaman tertentu.
        
        Args:
            data: List of all scholarship data (sudah difilter)
            page: Halaman yang ingin ditampilkan (default 1)
        """
        # Store filtered data dan hitung total pages
        self.filtered_data = data
        self.current_page = page
        self.total_pages = max(1, (len(data) + self.items_per_page - 1) // self.items_per_page)
        
        # Validate page number
        if self.current_page > self.total_pages:
            self.current_page = self.total_pages
        if self.current_page < 1:
            self.current_page = 1
        
        # Calculate slice untuk current page
        start_idx = (self.current_page - 1) * self.items_per_page
        end_idx = start_idx + self.items_per_page
        page_data = data[start_idx:end_idx]
        
        # Populate table dengan hanya page_data (bukan semua data)
        self.displayed_data = list(page_data)
        self.table.setRowCount(len(page_data))
        
        for row_idx, item in enumerate(page_data):
            # Hitung actual row number dari full dataset
            actual_row_number = start_idx + row_idx + 1
            
            # NO
            no_item = QTableWidgetItem(str(actual_row_number))
            no_item.setFont(QFont(FONT_FAMILY_PRIMARY, FONT_SIZE_BASE))
            no_item.setForeground(QColor(COLOR_GRAY_700))
            self.table.setItem(row_idx, 0, no_item)
            
            # NAMA BEASISWA
            nama_item = QTableWidgetItem(item["nama"])
            nama_item.setFont(QFont(FONT_FAMILY_PRIMARY, FONT_SIZE_BASE))
            nama_item.setForeground(QColor(COLOR_NAVY))
            nama_item.setFont(_make_bold_font(nama_item.font()))
            self.table.setItem(row_idx, 1, nama_item)
            
            # PENYELENGGARA
            penyelenggara_item = QTableWidgetItem(item["penyelenggara"])
            penyelenggara_item.setFont(QFont(FONT_FAMILY_PRIMARY, FONT_SIZE_BASE))
            penyelenggara_item.setForeground(QColor(COLOR_GRAY_700))
            self.table.setItem(row_idx, 2, penyelenggara_item)
            
            # JENJANG
            jenjang_item = QTableWidgetItem(item["jenjang"])
            jenjang_item.setFont(QFont(FONT_FAMILY_PRIMARY, FONT_SIZE_BASE))
            jenjang_item.setForeground(QColor(COLOR_NAVY))
            self.table.setItem(row_idx, 3, jenjang_item)
            
            # DEADLINE - dengan warna dinamis berdasarkan hari tersisa
            days_left = _get_days_until_deadline(item["deadline"])
            deadline_color = _get_deadline_color(days_left)
            
            # Format display: "2026-05-15 (22 hari)" atau "2026-05-15" jika error
            if days_left is not None:
                deadline_display = f"{item['deadline']} ({days_left} hari)"
            else:
                deadline_display = item["deadline"]
            
            deadline_item = QTableWidgetItem(deadline_display)
            deadline_item.setFont(QFont(FONT_FAMILY_PRIMARY, FONT_SIZE_BASE))
            deadline_item.setForeground(QColor(deadline_color))
            self.table.setItem(row_idx, 4, deadline_item)
            
            # STATUS (Badge)
            badge = self._create_status_badge(item["status"])
            self.table.setCellWidget(row_idx, 5, badge)

            # AKSI (Buttons)
            actions = self._create_action_buttons(item["id"])
            self.table.setCellWidget(row_idx, 6, actions)
        
        # Update pagination UI (buttons dan label)
        self._update_pagination_ui()
    
    def filter_table(self):
        """Filter table berdasarkan search dan filters, reset ke halaman 1."""
        filtered_data = self._get_filtered_data()
        self.populate_table(filtered_data, page=1)

    def _get_filtered_data(self) -> List[Dict[str, Any]]:
        """Return beasiswa rows that match current search and filter controls."""
        search_text = self.search_input.text().lower()
        status_filter = self.status_filter.currentText()
        jenjang_filter = self.jenjang_filter.currentText()

        return [
            item for item in self.beasiswa_data
            if (search_text in item["nama"].lower() or 
                search_text in item["penyelenggara"].lower()) and
               (status_filter == "Semua" or item["status"] == status_filter) and
               (jenjang_filter == "Semua" or item["jenjang"] == jenjang_filter)
        ]
    
    def filter_by_deadline(self):
        """Filter beasiswa yang deadline-nya dekat (7 hari atau kurang)."""
        deadline_soon = []
        for item in self.beasiswa_data:
            days = _get_days_until_deadline(item["deadline"])
            if days is not None and days <= 7:
                deadline_soon.append(item)
        
        if not deadline_soon:
            QMessageBox.information(
                self,
                "Tidak Ada Deadline Dekat",
                "Tidak ada beasiswa dengan deadline dalam 7 hari ke depan.",
            )
        
        self.populate_table(deadline_soon, page=1)
    
    def refresh_data(self):
        """Refresh data dari database."""
        logger.info("Refreshing beasiswa data...")
        loaded = self.load_beasiswa_data()
        if loaded == 0 and not self._sync_in_progress:
            self.sync_from_web(auto_trigger=True)
            return
        self.subtitle_label.setText(f"Terakhir diperbaharui: {datetime.now().strftime('%d %b %Y %H:%M')}")
    
    def export_to_csv(self):
        """Export beasiswa data ke CSV file."""
        file_path, _ = QFileDialog.getSaveFileName(
            self, "Export Beasiswa", "", "CSV Files (*.csv)"
        )

        if file_path:
            if not file_path.lower().endswith(".csv"):
                file_path = f"{file_path}.csv"

            rows_to_export = self.displayed_data if self.displayed_data else self._get_filtered_data()
            if not rows_to_export:
                QMessageBox.information(
                    self,
                    "Export CSV",
                    "Tidak ada data yang bisa diexport. Ubah filter atau kata kunci pencarian.",
                )
                return

            try:
                with open(file_path, 'w', newline='', encoding='utf-8') as csvfile:
                    fieldnames = ['NO', 'NAMA BEASISWA', 'PENYELENGGARA', 'JENJANG', 'DEADLINE', 'STATUS']
                    writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
                    
                    writer.writeheader()
                    for idx, item in enumerate(rows_to_export, 1):
                        writer.writerow({
                            'NO': idx,
                            'NAMA BEASISWA': item['nama'],
                            'PENYELENGGARA': item['penyelenggara'],
                            'JENJANG': item['jenjang'],
                            'DEADLINE': item['deadline'],
                            'STATUS': item['status']
                        })

                logger.info(f"Data exported to {file_path}")
                QMessageBox.information(
                    self,
                    "Export CSV",
                    f"Berhasil export {len(rows_to_export)} baris ke:\n{file_path}",
                )
            except Exception as e:
                logger.error(f"Error exporting data: {e}")
                QMessageBox.warning(
                    self,
                    "Export Gagal",
                    f"Terjadi kesalahan saat export CSV:\n{e}",
                )
    
    def view_beasiswa(self, beasiswa_id: int):
        """View beasiswa details."""
        logger.info(f"Viewing beasiswa {beasiswa_id}")

        detail = self._get_beasiswa_detail(beasiswa_id)
        if detail is None:
            QMessageBox.warning(self, "Detail Tidak Tersedia", "Data detail beasiswa tidak ditemukan.")
            return

        summary_lines = [
            f"Nama: {detail.get('judul', '(Tanpa Judul)')}",
            f"Penyelenggara: {detail.get('penyelenggara', 'Tidak Ada')}",
            f"Jenjang: {detail.get('jenjang', '-')}",
            f"Deadline: {detail.get('deadline', '-')}",
            f"Status: {detail.get('status', '-')}",
        ]

        extra_lines = [
            f"Benefit: {detail.get('benefit') or '-'}",
            f"Persyaratan: {detail.get('persyaratan') or '-'}",
            f"Minimal IPK: {detail.get('minimal_ipk') if detail.get('minimal_ipk') is not None else '-'}",
            f"Coverage: {detail.get('coverage') or '-'}",
            f"Link Aplikasi: {detail.get('link_aplikasi') or '-'}",
            "",
            "Deskripsi:",
            detail.get('deskripsi') or '-',
        ]

        msg = QMessageBox(self)
        msg.setIcon(QMessageBox.Icon.Information)
        msg.setWindowTitle("Detail Beasiswa")
        msg.setText("\n".join(summary_lines))
        msg.setDetailedText("\n".join(extra_lines))
        msg.exec()

    def _get_beasiswa_detail(self, beasiswa_id: int) -> Optional[Dict[str, Any]]:
        """Fetch full scholarship detail row from DB for detail dialog."""
        conn = get_connection()
        cursor = conn.cursor()

        try:
            cursor.execute(
                """
                SELECT b.id, b.judul, COALESCE(p.nama, 'Tidak Ada') AS penyelenggara,
                       b.jenjang, b.deadline, b.status, b.deskripsi, b.benefit,
                       b.persyaratan, b.minimal_ipk, b.coverage, b.link_aplikasi
                FROM beasiswa b
                LEFT JOIN penyelenggara p ON b.penyelenggara_id = p.id
                WHERE b.id = ?
                LIMIT 1
                """,
                (beasiswa_id,),
            )
            row = cursor.fetchone()
            if not row:
                return None

            return {
                "id": row[0],
                "judul": row[1],
                "penyelenggara": row[2],
                "jenjang": row[3],
                "deadline": row[4],
                "status": row[5],
                "deskripsi": row[6],
                "benefit": row[7],
                "persyaratan": row[8],
                "minimal_ipk": row[9],
                "coverage": row[10],
                "link_aplikasi": row[11],
            }
        finally:
            cursor.close()

    def _is_favorited(self, beasiswa_id: int) -> bool:
        """Check if current user already bookmarked a scholarship."""
        conn = get_connection()
        cursor = conn.cursor()

        try:
            cursor.execute(
                """
                SELECT id FROM favorit
                WHERE user_id = ? AND beasiswa_id = ?
                LIMIT 1
                """,
                (self.user_id, beasiswa_id),
            )
            return cursor.fetchone() is not None
        finally:
            cursor.close()
    
    def toggle_bookmark(self, beasiswa_id: int):
        """Toggle bookmark untuk beasiswa."""
        logger.info(f"Toggling bookmark for beasiswa {beasiswa_id}")

        if self._is_favorited(beasiswa_id):
            success, message = delete_favorit(self.user_id, beasiswa_id)
            if success:
                QMessageBox.information(self, "Favorit", message)
                self._emit_data_changed("favorit.updated")
                return
            QMessageBox.warning(self, "Favorit Gagal", message)
            return

        success, message, _ = add_favorit(self.user_id, beasiswa_id)
        if success:
            QMessageBox.information(self, "Favorit", message)
            self._emit_data_changed("favorit.updated")
            return

        QMessageBox.warning(self, "Favorit Gagal", message)
    
    def apply_beasiswa(self, beasiswa_id: int):
        """Apply untuk beasiswa."""
        logger.info(f"Applying for beasiswa {beasiswa_id}")

        if check_user_applied(self.user_id, beasiswa_id):
            QMessageBox.information(
                self,
                "Lamaran Sudah Ada",
                "Anda sudah pernah menambahkan lamaran untuk beasiswa ini.",
            )
            return

        success, message, _ = add_lamaran(
            user_id=self.user_id,
            beasiswa_id=beasiswa_id,
            status="Pending",
        )

        if success:
            QMessageBox.information(self, "Lamaran Berhasil", message)
            self.subtitle_label.setText(
                "Lamaran berhasil ditambahkan ke Tracker | "
                f"DB {self._current_db_name()}"
            )
            self._emit_data_changed("lamaran.updated")
            return

        QMessageBox.warning(self, "Lamaran Gagal", message)

    def _refresh_tracker_tab(self):
        """Refresh tracker tab data if main window exposes tracker instance."""
        try:
            main_window = self.window()
            tracker_tab = getattr(main_window, "tracker_tab", None)
            if tracker_tab and hasattr(tracker_tab, "load_applications"):
                tracker_tab.load_applications()
        except Exception as exc:
            logger.warning("Tracker refresh skipped: %s", exc)

    def _refresh_beranda_tab(self):
        """Refresh beranda snapshot so favorites/stats stay in sync."""
        try:
            main_window = self.window()
            beranda_tab = getattr(main_window, "beranda_tab", None)
            if beranda_tab and hasattr(beranda_tab, "load_dashboard_data"):
                beranda_tab.load_dashboard_data()
        except Exception as exc:
            logger.warning("Beranda refresh skipped: %s", exc)

    def _on_previous_page(self):
        """Handler untuk tombol Previous."""
        if self.current_page > 1:
            self.populate_table(self.filtered_data, page=self.current_page - 1)

    def _on_next_page(self):
        """Handler untuk tombol Next."""
        if self.current_page < self.total_pages:
            self.populate_table(self.filtered_data, page=self.current_page + 1)

    def _update_pagination_ui(self):
        """Update pagination buttons dan label berdasarkan current_page dan total_pages."""
        self.page_info_label.setText(f"Halaman {self.current_page} dari {self.total_pages}")
        self.prev_btn.setEnabled(self.current_page > 1)
        self.next_btn.setEnabled(self.current_page < self.total_pages)


def _make_bold_font(font: QFont) -> QFont:
    """Helper function to make font bold."""
    font.setWeight(QFont.Weight.Bold)
    return font
