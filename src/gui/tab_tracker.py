"""
Tracker Lamaran (Application Tracker) Tab for BeasiswaKu - PLACEHOLDER
Task 15: Full implementation akan dilakukan kemudian
"""

import logging
from typing import Optional

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QLabel, QPushButton, QTableWidget,
    QTableWidgetItem, QHeaderView, QHBoxLayout, QLineEdit
)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont

from src.gui.design_tokens import *
from src.gui.styles import get_button_solid_stylesheet
from src.database.crud import get_connection

logger = logging.getLogger(__name__)


class TrackerTab(QWidget):
    """
    Tracker Lamaran (Application Tracker) Tab - Placeholder untuk Task 15.
    
    Features yang akan diimplementasikan:
    - Tabel tracking lamaran untuk setiap beasiswa
    - Status tracking: Pending, Diterima, Ditolak
    - Timeline progress per aplikasi
    - Notes/catatan per aplikasi
    
    Akan di-implement di Task 15.
    """
    
    def __init__(self, user_id: int, parent=None):
        super().__init__(parent)
        self.user_id = user_id
        logger.info(f"Initializing TrackerTab (Placeholder) for user {user_id}")
        self.init_ui()
    
    def init_ui(self):
        """Initialize Tracker Tab UI (Placeholder)."""
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(16, 16, 16, 16)
        main_layout.setSpacing(12)
        
        # Title
        title = QLabel("Tracker Lamaran")
        title_font = QFont(FONT_FAMILY_PRIMARY, 20)
        title_font.setWeight(QFont.Weight.Bold)
        title.setFont(title_font)
        title.setStyleSheet(f"color: {COLOR_NAVY};")
        main_layout.addWidget(title)
        
        # Placeholder message
        placeholder = QLabel("🚀 Fitur Tracker Lamaran akan segera hadir!\n\nTask 15: Full implementation dengan tabel tracking, status updates, dan progres timeline.")
        placeholder.setFont(QFont(FONT_FAMILY_PRIMARY, FONT_SIZE_BASE))
        placeholder.setStyleSheet(f"color: {COLOR_GRAY_600}; padding: 20px; background-color: {COLOR_GRAY_100}; border-radius: 6px;")
        placeholder.setAlignment(Qt.AlignmentFlag.AlignCenter)
        main_layout.addWidget(placeholder)
        
        main_layout.addStretch()
        self.setStyleSheet(f"background-color: {COLOR_GRAY_BACKGROUND};")
