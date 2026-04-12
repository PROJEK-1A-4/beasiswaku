"""
gui_beasiswa.py - Beasiswa Tab UI Implementation
BeasiswaKu - Personal Scholarship Manager

Komponen:
1. BeasiswaTab - Main beasiswa tab widget
2. AddBeasiswaDialog - Dialog untuk tambah beasiswa baru
3. EditBeasiswaDialog - Dialog untuk edit beasiswa existing
4. DeleteConfirmationDialog - Dialog untuk konfirmasi hapus
5. BeasiswaDetailDialog - Dialog untuk tampil detail beasiswa

PIC: Kyla (UI/UX Specialist - Beasiswa Tab)
"""

import logging
import csv
from pathlib import Path
from datetime import datetime, timedelta
from typing import Optional, List, Dict, Tuple

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QGridLayout, QFormLayout,
    QTableWidget, QTableWidgetItem, QComboBox, QLineEdit, QPushButton,
    QLabel, QMessageBox, QDialog, QHeaderView, QFileDialog,
    QSpinBox, QDoubleSpinBox, QTextEdit, QDateEdit
)
from PyQt6.QtCore import Qt, QDate, pyqtSignal, QTimer
from PyQt6.QtGui import QFont, QColor, QBrush

from src.database.crud import (
    get_beasiswa_list, add_beasiswa, edit_beasiswa,
    delete_beasiswa, get_connection
)

# Setup logging
logger = logging.getLogger(__name__)


# ==================== MAIN BEASISWA TAB ====================

class BeasiswaTab(QWidget):
    """
    Tab untuk menampilkan daftar beasiswa dengan fitur:
    - Tabel display dengan 6 kolom
    - Filter by jenjang (D3, D4, S1, S2)
    - Filter by status (Buka, Segera Tutup, Tutup)
    - Real-time search
    - CRUD operations (Tambah, Edit, Hapus)
    - Highlight deadline (merah ≤3 hari, kuning ≤7 hari)
    - Detail popup (double-click)
    - Export to CSV
    """
    
    # Signal untuk refresh data
    data_changed = pyqtSignal()
    
    def __init__(self, user_id: int):
        super().__init__()
        self.user_id = user_id
        self.beasiswa_list = []
        self.filtered_list = []
        
        # Initialize UI
        self.init_ui()
        
        # Load initial data
        self.load_beasiswa_data()
    
    def init_ui(self):
        """Initialize Beasiswa Tab UI"""
        logger.info("Initializing BeasiswaTab UI...")
        main_layout = QVBoxLayout()
        
        # Placeholder - akan diganti di task-task berikutnya
        
        self.setLayout(main_layout)
        logger.info("✅ BeasiswaTab UI initialized")
    
    def load_beasiswa_data(self):
        """
        Load beasiswa data dari database.
        Called saat tab dibuka atau refresh button diklik.
        """
        try:
            self.beasiswa_list, total_count = get_beasiswa_list()
            logger.info(f"✅ Loaded {len(self.beasiswa_list)} beasiswa from database")
        except Exception as e:
            logger.error(f"❌ Error loading beasiswa data: {e}")
            self.beasiswa_list = []
    
    def apply_filters(self):
        """
        Apply filters (jenjang, status, search) to beasiswa list.
        """
        # Will be implemented in Task 14
        pass
    
    def highlight_deadline(self, deadline_str: str) -> Tuple[QColor, str]:
        """
        Determine deadline color based on days remaining.
        
        Args:
            deadline_str: Date string (YYYY-MM-DD format)
            
        Returns:
            Tuple[QColor, str]: (color, status_text)
                - Red: ≤ 3 hari
                - Yellow: ≤ 7 hari
                - Green: > 7 hari
        """
        try:
            deadline = datetime.strptime(deadline_str, '%Y-%m-%d').date()
            today = datetime.now().date()
            days_remaining = (deadline - today).days
            
            if days_remaining < 0:
                return QColor("#FF6B6B"), "LEWAT"  # Red - overdue
            elif days_remaining <= 3:
                return QColor("#FF6B6B"), f"{days_remaining}h"  # Red - urgent
            elif days_remaining <= 7:
                return QColor("#FFA500"), f"{days_remaining}h"  # Yellow - soon
            else:
                return QColor("#4CAF50"), f"{days_remaining}h"  # Green - plenty of time
        except ValueError:
            return QColor("#FFFFFF"), "?"
    
    def export_to_csv(self):
        """
        Export filtered beasiswa data to CSV file.
        """
        # Will be implemented in Task 29
        pass


# ==================== DIALOG CLASSES ====================

class AddBeasiswaDialog(QDialog):
    """
    Dialog untuk menambah beasiswa baru.
    Form fields untuk semua beasiswa properties.
    """
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.init_ui()
    
    def init_ui(self):
        """Initialize Add Beasiswa Dialog UI"""
        self.setWindowTitle("Tambah Beasiswa Baru")
        self.setGeometry(200, 200, 600, 700)
        self.setModal(True)
        
        # Placeholder - akan diisi di Task 17
        layout = QVBoxLayout()
        self.setLayout(layout)
    
    def get_form_data(self) -> Dict:
        """Get form data and validate"""
        # Will be implemented in Task 17
        pass


class EditBeasiswaDialog(QDialog):
    """
    Dialog untuk edit beasiswa existing.
    Form fields pre-filled dengan data existing.
    """
    
    def __init__(self, beasiswa_data: Dict, parent=None):
        super().__init__(parent)
        self.beasiswa_data = beasiswa_data
        self.init_ui()
    
    def init_ui(self):
        """Initialize Edit Beasiswa Dialog UI"""
        self.setWindowTitle(f"Edit Beasiswa - {self.beasiswa_data.get('judul', '')}")
        self.setGeometry(200, 200, 600, 700)
        self.setModal(True)
        
        # Placeholder - akan diisi di Task 18
        layout = QVBoxLayout()
        self.setLayout(layout)
    
    def get_form_data(self) -> Dict:
        """Get form data and validate"""
        # Will be implemented in Task 18
        pass


class DeleteConfirmationDialog(QDialog):
    """
    Dialog untuk konfirmasi penghapusan beasiswa.
    Menampilkan warning dan tombol Yes/No.
    """
    
    def __init__(self, beasiswa_judul: str, parent=None):
        super().__init__(parent)
        self.beasiswa_judul = beasiswa_judul
        self.init_ui()
    
    def init_ui(self):
        """Initialize Delete Confirmation Dialog UI"""
        self.setWindowTitle("Konfirmasi Hapus")
        self.setGeometry(300, 300, 400, 200)
        self.setModal(True)
        
        # Placeholder - akan diisi di Task 19
        layout = QVBoxLayout()
        self.setLayout(layout)


class BeasiswaDetailDialog(QDialog):
    """
    Dialog untuk menampilkan detail lengkap beasiswa.
    Dipanggil saat user double-click row di table.
    """
    
    def __init__(self, beasiswa_data: Dict, parent=None):
        super().__init__(parent)
        self.beasiswa_data = beasiswa_data
        self.init_ui()
    
    def init_ui(self):
        """Initialize Beasiswa Detail Dialog UI"""
        self.setWindowTitle(f"Detail Beasiswa - {self.beasiswa_data.get('judul', '')}")
        self.setGeometry(150, 150, 700, 600)
        self.setModal(True)
        
        # Placeholder - akan diisi di Task 28
        layout = QVBoxLayout()
        self.setLayout(layout)
