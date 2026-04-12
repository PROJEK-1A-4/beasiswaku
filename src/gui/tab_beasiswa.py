"""
Beasiswa (Scholarship List) Tab for BeasiswaKu
Professional scholarship listing with search, filters, and actions
"""

import logging
from typing import Optional, Dict, List, Any
from datetime import datetime
import csv
import os

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QFrame, QLineEdit,
    QPushButton, QComboBox, QTableWidget, QTableWidgetItem, QHeaderView,
    QAbstractItemView, QFileDialog, QSpacerItem, QSizePolicy
)
from PyQt6.QtCore import Qt, QSize
from PyQt6.QtGui import QFont, QIcon, QColor

from src.gui.design_tokens import *
from src.gui.styles import get_button_solid_stylesheet, get_input_field_stylesheet
from src.services.beasiswa_service import get_beasiswa_table_data
from src.services.status_utils import SCHOLARSHIP_STATUS_ORDER

# Setup logging
logger = logging.getLogger(__name__)


class BeasiswaTab(QWidget):
    """
    Beasiswa (Scholarship List) Tab dengan professional data table.
    
    Features:
    - Search bar untuk cari beasiswa
    - Filters: Status, Jenjang
    - Action buttons: Deadline Dekat, Refresh, Export CSV
    - Professional table dengan 7 columns
    - Status badges (Buka, Segera Tutup, Tutup)
    - Action icons: View, Bookmark, Apply
    """
    
    def __init__(self, user_id: int, parent=None):
        super().__init__(parent)
        self.user_id = user_id
        self.beasiswa_data: List[Dict[str, Any]] = []
        
        logger.info(f"Initializing BeasiswaTab")
        self.init_ui()
        self.load_beasiswa_data()
    
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
        self.subtitle_label.setStyleSheet(f"color: {COLOR_GRAY_400}; padding: 0px;")
        header_layout.addWidget(self.subtitle_label)
        
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
        refresh_btn = QPushButton("↻ Refresh")
        refresh_btn.setMinimumHeight(40)
        refresh_btn.setFont(QFont(FONT_FAMILY_PRIMARY, FONT_SIZE_BASE))
        refresh_btn.setStyleSheet(f"""
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
        refresh_btn.clicked.connect(self.refresh_data)
        toolbar_layout.addWidget(refresh_btn)
        
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
        header.setSectionResizeMode(5, QHeaderView.ResizeMode.ResizeToContents)  # STATUS
        header.setSectionResizeMode(6, QHeaderView.ResizeMode.ResizeToContents)  # AKSI
        
        self.table.setMinimumHeight(400)
        main_layout.addWidget(self.table)
        main_layout.addStretch()
    
    def _create_status_badge(self, status: str) -> QWidget:
        """Create a styled status badge."""
        badge_frame = QFrame()
        badge_layout = QHBoxLayout(badge_frame)
        badge_layout.setContentsMargins(8, 4, 8, 4)
        badge_layout.setSpacing(0)
        
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
        badge_label.setFont(QFont(FONT_FAMILY_PRIMARY, 9))
        badge_label.setStyleSheet(f"""
            color: {text_color};
            font-weight: bold;
            padding: 4px 8px;
        """)
        
        badge_frame.setStyleSheet(f"""
            QFrame {{
                background-color: {bg_color};
                border: 1px solid {border_color};
                border-radius: 4px;
            }}
        """)
        
        badge_layout.addWidget(badge_label)
        return badge_frame
    
    def _create_action_buttons(self, row_id: int) -> QWidget:
        """Create action buttons (View, Bookmark, Apply)."""
        action_frame = QFrame()
        action_layout = QHBoxLayout(action_frame)
        action_layout.setContentsMargins(0, 0, 0, 0)
        action_layout.setSpacing(8)
        
        # View button
        view_btn = QPushButton("👁")
        view_btn.setMaximumSize(32, 32)
        view_btn.setStyleSheet(f"""
            QPushButton {{
                background-color: transparent;
                border: none;
                font-size: 16px;
            }}
            QPushButton:hover {{
                background-color: {COLOR_GRAY_100};
                border-radius: 4px;
            }}
        """)
        view_btn.clicked.connect(lambda: self.view_beasiswa(row_id))
        action_layout.addWidget(view_btn)
        
        # Bookmark button
        bookmark_btn = QPushButton("🔖")
        bookmark_btn.setMaximumSize(32, 32)
        bookmark_btn.setStyleSheet(f"""
            QPushButton {{
                background-color: transparent;
                border: none;
                font-size: 16px;
            }}
            QPushButton:hover {{
                background-color: {COLOR_GRAY_100};
                border-radius: 4px;
            }}
        """)
        bookmark_btn.clicked.connect(lambda: self.toggle_bookmark(row_id))
        action_layout.addWidget(bookmark_btn)
        
        # Apply button
        apply_btn = QPushButton("✓")
        apply_btn.setMaximumSize(32, 32)
        apply_btn.setStyleSheet(f"""
            QPushButton {{
                background-color: transparent;
                border: none;
                font-size: 18px;
                color: {COLOR_SUCCESS};
                font-weight: bold;
            }}
            QPushButton:hover {{
                background-color: {COLOR_SUCCESS_LIGHT};
                border-radius: 4px;
            }}
        """)
        apply_btn.clicked.connect(lambda: self.apply_beasiswa(row_id))
        action_layout.addWidget(apply_btn)
        
        action_layout.addStretch()
        return action_frame
    
    def load_beasiswa_data(self):
        """Load beasiswa data dari database."""
        try:
            self.beasiswa_data = get_beasiswa_table_data()
            
            logger.info(f"Loaded {len(self.beasiswa_data)} beasiswa")
            self.populate_table(self.beasiswa_data)
        except Exception as e:
            logger.error(f"Error loading beasiswa data: {e}")
    
    def populate_table(self, data: List[Dict[str, Any]]):
        """Populate table dengan data."""
        self.table.setRowCount(len(data))
        
        for row_idx, item in enumerate(data):
            # NO
            no_item = QTableWidgetItem(str(row_idx + 1))
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
            
            # DEADLINE
            deadline_item = QTableWidgetItem(item["deadline"])
            deadline_item.setFont(QFont(FONT_FAMILY_PRIMARY, FONT_SIZE_BASE))
            deadline_item.setForeground(QColor(COLOR_GRAY_700))
            self.table.setItem(row_idx, 4, deadline_item)
            
            # STATUS (Badge)
            status_item = QTableWidgetItem()
            badge = self._create_status_badge(item["status"])
            self.table.setCellWidget(row_idx, 5, badge)
            self.table.setItem(row_idx, 5, status_item)
            
            # AKSI (Buttons)
            action_item = QTableWidgetItem()
            actions = self._create_action_buttons(item["id"])
            self.table.setCellWidget(row_idx, 6, actions)
            self.table.setItem(row_idx, 6, action_item)
    
    def filter_table(self):
        """Filter table berdasarkan search dan filters."""
        search_text = self.search_input.text().lower()
        status_filter = self.status_filter.currentText()
        jenjang_filter = self.jenjang_filter.currentText()
        
        filtered_data = [
            item for item in self.beasiswa_data
            if (search_text in item["nama"].lower() or 
                search_text in item["penyelenggara"].lower()) and
               (status_filter == "Semua" or item["status"] == status_filter) and
               (jenjang_filter == "Semua" or item["jenjang"] == jenjang_filter)
        ]
        
        self.populate_table(filtered_data)
    
    def filter_by_deadline(self):
        """Filter beasiswa yang deadline-nya dekat (dalam 7 hari)."""
        deadline_soon = [
            item for item in self.beasiswa_data
            if item["status"] != "Tutup"  # Only open/closing soon
        ]
        
        self.populate_table(deadline_soon)
    
    def refresh_data(self):
        """Refresh data dari database."""
        logger.info("Refreshing beasiswa data...")
        self.load_beasiswa_data()
        self.subtitle_label.setText(f"Terakhir diperbaharui: {datetime.now().strftime('%d %b %Y %H:%M')}")
    
    def export_to_csv(self):
        """Export beasiswa data ke CSV file."""
        file_path, _ = QFileDialog.getSaveFileName(
            self, "Export Beasiswa", "", "CSV Files (*.csv)"
        )
        
        if file_path:
            try:
                with open(file_path, 'w', newline='', encoding='utf-8') as csvfile:
                    fieldnames = ['NO', 'NAMA BEASISWA', 'PENYELENGGARA', 'JENJANG', 'DEADLINE', 'STATUS']
                    writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
                    
                    writer.writeheader()
                    for idx, item in enumerate(self.beasiswa_data, 1):
                        writer.writerow({
                            'NO': idx,
                            'NAMA BEASISWA': item['nama'],
                            'PENYELENGGARA': item['penyelenggara'],
                            'JENJANG': item['jenjang'],
                            'DEADLINE': item['deadline'],
                            'STATUS': item['status']
                        })
                
                logger.info(f"Data exported to {file_path}")
            except Exception as e:
                logger.error(f"Error exporting data: {e}")
    
    def view_beasiswa(self, beasiswa_id: int):
        """View beasiswa details."""
        logger.info(f"Viewing beasiswa {beasiswa_id}")
        # TODO: Implement detail view
    
    def toggle_bookmark(self, beasiswa_id: int):
        """Toggle bookmark untuk beasiswa."""
        logger.info(f"Toggling bookmark for beasiswa {beasiswa_id}")
        # TODO: Implement bookmark toggle
    
    def apply_beasiswa(self, beasiswa_id: int):
        """Apply untuk beasiswa."""
        logger.info(f"Applying for beasiswa {beasiswa_id}")
        # TODO: Implement apply functionality


def _make_bold_font(font: QFont) -> QFont:
    """Helper function to make font bold."""
    font.setWeight(QFont.Weight.Bold)
    return font
