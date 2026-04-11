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
        
        # ===== DATA VARIABLES =====
        self.beasiswa_list: List[Dict] = []
        self.filtered_list: List[Dict] = []
        self.last_scrape_time: Optional[str] = None
        
        # ===== UI WIDGETS (akan diinisialisasi di init_ui) =====
        # Top bar widgets
        self.lbl_title: Optional[QLabel] = None
        self.lbl_timestamp: Optional[QLabel] = None
        
        # Filter widgets
        self.combo_jenjang: Optional[QComboBox] = None
        self.combo_status: Optional[QComboBox] = None
        self.entry_search: Optional[QLineEdit] = None
        
        # Table widget
        self.tbl_beasiswa: Optional[QTableWidget] = None
        self.lbl_row_count: Optional[QLabel] = None
        
        # CRUD buttons
        self.btn_tambah: Optional[QPushButton] = None
        self.btn_edit: Optional[QPushButton] = None
        self.btn_hapus: Optional[QPushButton] = None
        self.btn_refresh: Optional[QPushButton] = None
        self.btn_export_csv: Optional[QPushButton] = None
        
        # Initialize UI
        self.init_ui()
        
        # Load initial data
        self.load_beasiswa_data()
        self.populate_table()
    
    # =====================================================================
    # SECTION 1: UI INITIALIZATION (Tasks 3-10)
    # =====================================================================
    
    def init_ui(self):
        """
        Initialize Beasiswa Tab UI with complete layout hierarchy.
        
        Layout Structure:
        ├── Top Bar (Title + Timestamp)
        ├── Filter Section (Jenjang + Status Dropdowns)
        ├── Search Section (Real-time search entry)
        ├── Table Widget (Beasiswa data display)
        ├── Row Count Label
        └── CRUD Buttons (Tambah, Edit, Hapus, Refresh, Export)
        
        Each section will be implemented in Tasks 4-10.
        """
        logger.info("Initializing BeasiswaTab UI...")
        
        # ===== MAIN LAYOUT =====
        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(10, 10, 10, 10)  # Padding around edges
        main_layout.setSpacing(10)  # Space between sections
        
        # ===== SECTION 1: TOP BAR (Task 4) =====
        # Display title and last scraping timestamp
        top_bar_layout = self._create_top_bar_layout()
        if top_bar_layout:
            main_layout.addLayout(top_bar_layout)
            main_layout.addSpacing(5)
        
        # ===== SECTION 2: FILTER SECTION (Tasks 5-6) =====
        # Filter by jenjang and status
        filter_layout = self._create_filter_layout()
        if filter_layout:
            main_layout.addLayout(filter_layout)
            main_layout.addSpacing(5)
        
        # ===== SECTION 3: TABLE WIDGET (Task 8) =====
        # Display beasiswa data in table format
        self.tbl_beasiswa = self._create_table_widget()
        if self.tbl_beasiswa:
            main_layout.addWidget(self.tbl_beasiswa)
            main_layout.addSpacing(5)
        
        # ===== SECTION 4: ROW COUNT LABEL (Task 13) =====
        # Display total number of rows displayed
        self.lbl_row_count = QLabel("Total: 0 Beasiswa")
        self.lbl_row_count.setFont(QFont("Arial", 9))
        self.lbl_row_count.setStyleSheet("color: #666; font-style: italic;")
        main_layout.addWidget(self.lbl_row_count)
        main_layout.addSpacing(5)
        
        # ===== SECTION 5: CRUD BUTTONS (Tasks 9-10) =====
        # Action buttons for CRUD operations
        crud_layout = self._create_crud_buttons_layout()
        if crud_layout:
            main_layout.addLayout(crud_layout)
        
        # ===== FINALIZE LAYOUT =====
        self.setLayout(main_layout)
        logger.info("✅ BeasiswaTab UI initialized with all sections")
    
    def _create_top_bar_layout(self) -> QHBoxLayout:
        """
        Create top bar with title and timestamp (Task 4).
        
        Returns:
            QHBoxLayout: Layout containing title label and timestamp label
        """
        layout = QHBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(10)
        
        # Will be populated with widgets in Task 4
        
        return layout
    
    def _create_filter_layout(self) -> QHBoxLayout:
        """
        Create filter section (Task 5-7).
        
        Contains:
        - Dropdown for jenjang filter (Task 5)
        - Dropdown for status filter (Task 6)
        - Search entry (Task 7)
        
        Returns:
            QHBoxLayout: Layout containing all filter widgets
        """
        layout = QHBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(10)
        
        # Will be populated with widgets in Tasks 5-7
        
        return layout
    
    def _create_table_widget(self) -> QTableWidget:
        """
        Create and configure QTableWidget (Task 8).
        
        Columns:
        1. No (index)
        2. Nama (judul)
        3. Penyelenggara
        4. Jenjang
        5. Deadline
        6. Status
        
        Returns:
            QTableWidget: Configured table widget
        """
        table = QTableWidget()
        table.setColumnCount(6)
        table.setHorizontalHeaderLabels([
            "No", "Nama", "Penyelenggara", 
            "Jenjang", "Deadline", "Status"
        ])
        
        # Will be populated with configuration in Task 8
        
        return table
    
    def _create_crud_buttons_layout(self) -> QHBoxLayout:
        """
        Create CRUD buttons section (Task 9-10).
        
        Buttons:
        - Tambah (Task 9)
        - Edit (Task 9)
        - Hapus (Task 9)
        - Refresh (Task 10)
        - Export CSV (Task 10)
        
        Returns:
            QHBoxLayout: Layout containing all CRUD buttons
        """
        layout = QHBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(10)
        
        # Will be populated with buttons in Tasks 9-10
        
        return layout
    
    # =====================================================================
    # SECTION 2: DATA LOADING (Tasks 11-13)
    # =====================================================================
    
    def load_beasiswa_data(self):
        """
        Load beasiswa data dari database (Task 11).
        Called saat tab dibuka atau refresh button diklik.
        
        Retrieves:
        - List of beasiswa from database using get_beasiswa_list()
        - Total count of records
        - Last scraping timestamp from first record
        
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            self.beasiswa_list, total_count = get_beasiswa_list()
            logger.info(f"✅ Loaded {len(self.beasiswa_list)} beasiswa from database (Total: {total_count})")
            
            # Update last scrape time from first record
            if self.beasiswa_list and 'scrape_date' in self.beasiswa_list[0]:
                self.last_scrape_time = self.beasiswa_list[0]['scrape_date']
                logger.debug(f"Last scrape time: {self.last_scrape_time}")
            else:
                self.last_scrape_time = None
            
            return True
        except Exception as e:
            logger.error(f"❌ Error loading beasiswa data: {e}")
            self.beasiswa_list = []
            self.last_scrape_time = None
            return False
    
    def populate_table(self):
        """
        Populate QTableWidget dengan data dari beasiswa_list (Task 12).
        Will fill rows dengan beasiswa data and apply formatting.
        """
        # Will be implemented in Task 12
        pass
    
    def update_row_count(self, count: int):
        """
        Update row count label (Task 13).
        
        Args:
            count: Number of rows displayed
        """
        # Will be implemented in Task 13
        pass
    
    # =====================================================================
    # SECTION 3: FILTERING & SEARCH (Tasks 14-16)
    # =====================================================================
    
    def apply_filters(self):
        """
        Apply filters (jenjang, status, search) to beasiswa list (Task 14).
        Combines all active filters and updates table display.
        """
        # Will be implemented in Task 14
        pass
    
    def _get_filter_jenjang(self) -> Optional[str]:
        """Get selected jenjang filter value"""
        # Helper method for Task 14
        pass
    
    def _get_filter_status(self) -> Optional[str]:
        """Get selected status filter value"""
        # Helper method for Task 14
        pass
    
    def _get_search_text(self) -> str:
        """Get search entry text"""
        # Helper method for Task 14
        pass
    
    def on_refresh_clicked(self):
        """
        Handle Refresh button click (Task 16).
        Reload data from database and refresh table.
        """
        # Will be implemented in Task 16
        pass
    
    # =====================================================================
    # SECTION 4: CRUD OPERATIONS (Tasks 17-24)
    # =====================================================================
    
    def on_tambah_clicked(self):
        """Handle Tambah button click (Task 20) -> open AddBeasiswaDialog"""
        # Will be implemented in Task 20
        pass
    
    def on_edit_clicked(self):
        """Handle Edit button click (Task 21) -> get selected row and open EditBeasiswaDialog"""
        # Will be implemented in Task 21
        pass
    
    def on_edit(self, beasiswa_data: Dict):
        """
        Get selected row data for editing (Task 22).
        
        Args:
            beasiswa_data: Dictionary with beasiswa details
        """
        # Will be implemented in Task 22
        pass
    
    def on_hapus_clicked(self):
        """Handle Hapus button click (Task 23) -> get selected row and open DeleteConfirmationDialog"""
        # Will be implemented in Task 23
        pass
    
    def on_delete(self, beasiswa_id: int):
        """
        Delete beasiswa dengan confirmation (Task 24).
        
        Args:
            beasiswa_id: ID beasiswa yang akan didelete
        """
        # Will be implemented in Task 24
        pass
    
    def refresh_after_crud(self):
        """
        Refresh table after add/edit/delete operation.
        Helper method untuk Tasks 20-24.
        """
        self.load_beasiswa_data()
        self.apply_filters()
    
    # =====================================================================
    # SECTION 5: FORMATTING & DISPLAY (Tasks 25-28)
    # =====================================================================
    
    def highlight_deadline(self, deadline_str: str) -> Tuple[QColor, str]:
        """
        Determine deadline color based on days remaining (Task 25).
        
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
    
    def apply_row_formatting(self):
        """
        Apply deadline highlight to all table rows (Task 26).
        Called setelah table di-populate.
        """
        # Will be implemented in Task 26
        pass
    
    def on_table_double_click(self, row: int, column: int):
        """
        Handle table double-click to show detail popup (Task 28).
        
        Args:
            row: Row index clicked
            column: Column index clicked
        """
        # Will be implemented in Task 28
        pass
    
    def show_detail_dialog(self, beasiswa_data: Dict):
        """
        Show detail popup dialog (Task 27).
        
        Args:
            beasiswa_data: Dictionary with beasiswa details
        """
        # Will be implemented in Task 27
        pass
    
    # =====================================================================
    # SECTION 6: EXPORT (Tasks 29-30)
    # =====================================================================
    
    def on_export_csv_clicked(self):
        """Handle Export CSV button click (Task 30)"""
        # Will be implemented in Task 30
        pass
    
    def export_to_csv(self):
        """
        Export filtered beasiswa data to CSV file (Task 29).
        
        Returns:
            bool: True if successful, False otherwise
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
