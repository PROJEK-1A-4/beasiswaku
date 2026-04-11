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
        
        # ===== SECTION 2: FILTER SECTION (Tasks 5-7, 15) =====
        # Filter by jenjang and status
        filter_layout = self._create_filter_layout()
        if filter_layout:
            main_layout.addLayout(filter_layout)
            main_layout.addSpacing(5)
        
        # ===== TASK 15: CONNECT FILTER DROPDOWN SIGNALS =====
        # Connect jenjang dropdown currentTextChanged to apply_filters
        if self.combo_jenjang:
            self.combo_jenjang.currentTextChanged.connect(self.apply_filters)
            logger.debug("✅ Jenjang dropdown signal connected to apply_filters()")
        
        # Connect status dropdown currentTextChanged to apply_filters
        if self.combo_status:
            self.combo_status.currentTextChanged.connect(self.apply_filters)
            logger.debug("✅ Status dropdown signal connected to apply_filters()")
        
        # ===== TASK 7: CONNECT SEARCH KEYRELEASE SIGNAL =====
        # Connect search entry KeyRelease event to apply filters
        if self.entry_search:
            self.entry_search.keyReleaseEvent = self._on_search_key_release
            logger.debug("✅ Search entry KeyRelease signal connected to apply_filters()")        
        # ===== SECTION 3: TABLE WIDGET (Task 8) =====
        # Display beasiswa data in table format
        self.tbl_beasiswa = self._create_table_widget()
        if self.tbl_beasiswa:
            main_layout.addWidget(self.tbl_beasiswa)
            main_layout.addSpacing(5)
        
        # ===== TASK 28: CONNECT TABLE DOUBLE-CLICK EVENT =====
        # Will be implemented in Task 28 (connect itemDoubleClicked signal)
        
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
        
        # ===== TASK 20: CONNECT TAMBAH BUTTON SIGNAL =====
        # Will be implemented in Task 20 (connect to on_tambah_clicked)
        
        # ===== TASK 21: CONNECT EDIT BUTTON SIGNAL =====
        # Will be implemented in Task 21 (connect to on_edit_clicked)
        
        # ===== TASK 23: CONNECT HAPUS BUTTON SIGNAL =====
        # Will be implemented in Task 23 (connect to on_hapus_clicked)
        
        # ===== TASK 16: CONNECT REFRESH BUTTON SIGNAL (Task 10) =====
        if self.btn_refresh:
            self.btn_refresh.clicked.connect(self.on_refresh_clicked)
            logger.debug("✅ Refresh button clicked signal connected to on_refresh_clicked()")
        
        # ===== TASK 30: CONNECT EXPORT CSV BUTTON SIGNAL (Task 10) =====
        if self.btn_export_csv:
            self.btn_export_csv.clicked.connect(self.on_export_csv_clicked)
            logger.debug("✅ Export CSV button clicked signal connected to on_export_csv_clicked()")
        
        # ===== FINALIZE LAYOUT =====
        self.setLayout(main_layout)
        logger.info("✅ BeasiswaTab UI initialized with all sections")
    
    def _create_top_bar_layout(self) -> QHBoxLayout:
        """
        Create top bar with title and timestamp (Task 4).
        
        Display:
        - Left: Title label with emoji (📚 Beasiswa Tab)
        - Right: Last scraping timestamp
        
        Returns:
            QHBoxLayout: Layout containing title label and timestamp label
        """
        layout = QHBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(10)
        
        # ===== TITLE LABEL (Left side) =====
        self.lbl_title = QLabel("📚 Daftar Beasiswa")
        self.lbl_title.setFont(QFont("Arial", 14, QFont.Weight.Bold))
        self.lbl_title.setStyleSheet("color: #1976D2; padding: 5px 0px;")
        layout.addWidget(self.lbl_title)
        
        # ===== SPACER (Center) =====
        layout.addStretch()
        
        # ===== TIMESTAMP LABEL (Right side) =====
        # Display "Scraping terakhir: [timestamp]" or "Belum ada data"
        timestamp_text = "Scraping terakhir: -"
        if self.last_scrape_time:
            timestamp_text = f"Scraping terakhir: {self.last_scrape_time}"
        
        self.lbl_timestamp = QLabel(timestamp_text)
        self.lbl_timestamp.setFont(QFont("Arial", 9))
        self.lbl_timestamp.setStyleSheet("color: #666; font-style: italic;")
        self.lbl_timestamp.setAlignment(Qt.AlignmentFlag.AlignRight)
        layout.addWidget(self.lbl_timestamp)
        
        logger.debug("✅ Top bar layout created (title + timestamp)")
        
        return layout
    
    def update_timestamp_label(self):
        """
        Update timestamp label dengan last scrape time (Helper untuk Task 4).
        Called setelah load_beasiswa_data() untuk refresh timestamp display.
        """
        if not self.lbl_timestamp:
            return
        
        if self.last_scrape_time:
            timestamp_text = f"Scraping terakhir: {self.last_scrape_time}"
        else:
            timestamp_text = "Scraping terakhir: -"
        
        self.lbl_timestamp.setText(timestamp_text)
        logger.debug(f"Timestamp label updated: {timestamp_text}")
    
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
        
        # ===== TASK 5: JENJANG DROPDOWN =====
        # Filter dropdown untuk education level
        lbl_jenjang = QLabel("Jenjang:")
        lbl_jenjang.setFont(QFont("Arial", 10))
        layout.addWidget(lbl_jenjang)
        
        self.combo_jenjang = QComboBox()
        self.combo_jenjang.setFont(QFont("Arial", 10))
        self.combo_jenjang.setMinimumWidth(100)
        self.combo_jenjang.addItems([
            "Semua",      # Default: show all
            "D3",
            "D4",
            "S1",
            "S2"
        ])
        self.combo_jenjang.setCurrentIndex(0)  # Default to "Semua"
        layout.addWidget(self.combo_jenjang)
        
        logger.debug("✅ Jenjang dropdown created with options: Semua, D3, D4, S1, S2")
        
        # ===== TASK 6: STATUS DROPDOWN =====
        # Filter dropdown untuk status ketersediaan beasiswa
        lbl_status = QLabel("Status:")
        lbl_status.setFont(QFont("Arial", 10))
        layout.addWidget(lbl_status)
        
        self.combo_status = QComboBox()
        self.combo_status.setFont(QFont("Arial", 10))
        self.combo_status.setMinimumWidth(120)
        self.combo_status.addItems([
            "Semua",           # Default: show all
            "Buka",
            "Segera Tutup",
            "Tutup"
        ])
        self.combo_status.setCurrentIndex(0)  # Default to "Semua"
        layout.addWidget(self.combo_status)
        
        logger.debug("✅ Status dropdown created with options: Semua, Buka, Segera Tutup, Tutup")
        
        # ===== TASK 7: SEARCH ENTRY =====
        # Real-time search entry untuk filter by judul
        lbl_search = QLabel("Cari:")
        lbl_search.setFont(QFont("Arial", 10))
        layout.addWidget(lbl_search)
        
        self.entry_search = QLineEdit()
        self.entry_search.setFont(QFont("Arial", 10))
        self.entry_search.setPlaceholderText("Cari beasiswa...")
        self.entry_search.setMinimumWidth(200)
        layout.addWidget(self.entry_search)
        
        logger.debug("✅ Search entry created with placeholder 'Cari beasiswa...'")
        
        # Add stretch to push remaining space to the right
        layout.addStretch()
        
        return layout
    
    def _create_table_widget(self) -> QTableWidget:
        """
        Create and configure QTableWidget (Task 8).
        
        Columns:
        1. No (index) - width: 50px
        2. Nama (judul) - width: 250px
        3. Penyelenggara - width: 150px
        4. Jenjang - width: 80px
        5. Deadline - width: 120px
        6. Status - width: 100px
        
        Features:
        - Single row selection
        - Alternating row colors
        - Read-only cells (editing via dialog)
        - Double-click event (Task 28)
        
        Returns:
            QTableWidget: Configured table widget
        """
        table = QTableWidget()
        
        # ===== SETUP COLUMNS =====
        table.setColumnCount(6)
        table.setHorizontalHeaderLabels([
            "No", "Nama", "Penyelenggara", 
            "Jenjang", "Deadline", "Status"
        ])
        
        # ===== COLUMN WIDTH SETTINGS =====
        table.setColumnWidth(0, 50)      # No
        table.setColumnWidth(1, 250)     # Nama (widest)
        table.setColumnWidth(2, 150)     # Penyelenggara
        table.setColumnWidth(3, 80)      # Jenjang
        table.setColumnWidth(4, 120)     # Deadline
        table.setColumnWidth(5, 100)     # Status
        
        # ===== HEADER CONFIGURATION =====
        header = table.horizontalHeader()
        header.setFont(QFont("Arial", 10, QFont.Weight.Bold))
        header.setStyleSheet("background-color: #E8EAF6; color: #1976D2;")
        header.setStretchLastSection(False)
        
        # ===== SELECTION BEHAVIOR =====
        table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        table.setSelectionMode(QTableWidget.SelectionMode.SingleSelection)
        
        # ===== ROW APPEARANCE =====
        table.setAlternatingRowColors(True)
        table.setStyleSheet("""
            QTableWidget {
                background-color: white;
                alternate-background-color: #F5F5F5;
                gridline-color: #E0E0E0;
            }
            QTableWidget::item {
                padding: 5px;
                border: none;
            }
        """)
        
        # ===== RESIZE BEHAVIOR =====
        table.setSortingEnabled(False)  # Will be enabled in Task 8 extension
        table.setColumnCount(6)
        
        # ===== READ-ONLY CELLS =====
        # Cells will be set as read-only in Task 12 during population
        
        logger.debug("✅ QTableWidget created with 6 columns: No, Nama, Penyelenggara, Jenjang, Deadline, Status")
        
        return table
    
    def _clear_table(self):
        """
        Clear all rows from table (Helper for Task 12).
        Used before populating with new data.
        """
        if not self.tbl_beasiswa:
            return
        
        self.tbl_beasiswa.setRowCount(0)
        logger.debug("Table cleared (all rows removed)")
    
    def _create_crud_buttons_layout(self) -> QHBoxLayout:
        """
        Create CRUD buttons section (Task 9-10).
        
        Buttons (Task 9):
        - Tambah (green) - Add new beasiswa
        - Edit (blue) - Edit selected beasiswa
        - Hapus (red) - Delete selected beasiswa
        
        Additional (Task 10):
        - Refresh (gray) - Reload data from database
        - Export CSV (orange) - Export filtered data
        
        Returns:
            QHBoxLayout: Layout containing all CRUD buttons
        """
        layout = QHBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(10)
        
        # ===== TASK 9: TAMBAH BUTTON (Green) =====
        self.btn_tambah = QPushButton("➕ Tambah")
        self.btn_tambah.setFont(QFont("Arial", 10, QFont.Weight.Bold))
        self.btn_tambah.setMinimumHeight(35)
        self.btn_tambah.setMinimumWidth(100)
        self.btn_tambah.setStyleSheet("""
            QPushButton {
                background-color: #4CAF50;
                color: white;
                border: none;
                border-radius: 5px;
                padding: 8px 15px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #45a049;
            }
            QPushButton:pressed {
                background-color: #3d8b40;
            }
        """)
        layout.addWidget(self.btn_tambah)
        logger.debug("✅ Tambah button created (green, #4CAF50)")
        
        # ===== TASK 9: EDIT BUTTON (Blue) =====
        self.btn_edit = QPushButton("✏️ Edit")
        self.btn_edit.setFont(QFont("Arial", 10, QFont.Weight.Bold))
        self.btn_edit.setMinimumHeight(35)
        self.btn_edit.setMinimumWidth(100)
        self.btn_edit.setStyleSheet("""
            QPushButton {
                background-color: #2196F3;
                color: white;
                border: none;
                border-radius: 5px;
                padding: 8px 15px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #0b7dda;
            }
            QPushButton:pressed {
                background-color: #0a66c2;
            }
        """)
        layout.addWidget(self.btn_edit)
        logger.debug("✅ Edit button created (blue, #2196F3)")
        
        # ===== TASK 9: HAPUS BUTTON (Red) =====
        self.btn_hapus = QPushButton("🗑️ Hapus")
        self.btn_hapus.setFont(QFont("Arial", 10, QFont.Weight.Bold))
        self.btn_hapus.setMinimumHeight(35)
        self.btn_hapus.setMinimumWidth(100)
        self.btn_hapus.setStyleSheet("""
            QPushButton {
                background-color: #f44336;
                color: white;
                border: none;
                border-radius: 5px;
                padding: 8px 15px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #da190b;
            }
            QPushButton:pressed {
                background-color: #ba0000;
            }
        """)
        layout.addWidget(self.btn_hapus)
        logger.debug("✅ Hapus button created (red, #f44336)")
        
        # ===== TASK 10: REFRESH BUTTON (Gray) =====
        self.btn_refresh = QPushButton("🔄 Refresh")
        self.btn_refresh.setFont(QFont("Arial", 10, QFont.Weight.Bold))
        self.btn_refresh.setMinimumHeight(35)
        self.btn_refresh.setMinimumWidth(100)
        self.btn_refresh.setStyleSheet("""
            QPushButton {
                background-color: #757575;
                color: white;
                border: none;
                border-radius: 5px;
                padding: 8px 15px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #616161;
            }
            QPushButton:pressed {
                background-color: #424242;
            }
        """)
        layout.addWidget(self.btn_refresh)
        logger.debug("✅ Refresh button created (gray, #757575)")
        
        # ===== TASK 10: EXPORT CSV BUTTON (Orange) =====
        self.btn_export_csv = QPushButton("📊 Export CSV")
        self.btn_export_csv.setFont(QFont("Arial", 10, QFont.Weight.Bold))
        self.btn_export_csv.setMinimumHeight(35)
        self.btn_export_csv.setMinimumWidth(120)
        self.btn_export_csv.setStyleSheet("""
            QPushButton {
                background-color: #FF9800;
                color: white;
                border: none;
                border-radius: 5px;
                padding: 8px 15px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #F57C00;
            }
            QPushButton:pressed {
                background-color: #E65100;
            }
        """)
        layout.addWidget(self.btn_export_csv)
        logger.debug("✅ Export CSV button created (orange, #FF9800)")
        
        # ===== SPACER =====
        layout.addStretch()
        
        return layout
    
    def _get_selected_row_index(self) -> Optional[int]:
        """
        Get index of selected row in table (Helper for Task 9).
        
        Returns:
            Optional[int]: Row index if selected, None otherwise
        """
        if not self.tbl_beasiswa:
            return None
        
        selected_rows = self.tbl_beasiswa.selectedIndexes()
        if not selected_rows:
            return None
        
        # Get the row from first selected index
        return selected_rows[0].row()
    
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
        Fills rows dengan beasiswa data dan apply formatting.
        """
        if not self.tbl_beasiswa:
            logger.warning("❌ Table widget not initialized")
            return
        
        self._clear_table()
        
        if not self.beasiswa_list:
            self.update_row_count(0)
            logger.info("No beasiswa data to populate")
            return
        
        for row_num, beasiswa in enumerate(self.beasiswa_list, 1):
            # Insert new row at end of table
            row_position = self.tbl_beasiswa.rowCount()
            self.tbl_beasiswa.insertRow(row_position)
            
            # Column 0: No (Row number)
            no_item = QTableWidgetItem(str(row_num))
            no_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            self.tbl_beasiswa.setItem(row_position, 0, no_item)
            
            # Column 1: Nama (judul beasiswa)
            nama_item = QTableWidgetItem(beasiswa.get('judul', ''))
            self.tbl_beasiswa.setItem(row_position, 1, nama_item)
            
            # Column 2: Penyelenggara (dari penyelenggara_name atau penyelenggara_id)
            penyelenggara = beasiswa.get('penyelenggara_name', str(beasiswa.get('penyelenggara_id', '')))
            penyelenggara_item = QTableWidgetItem(penyelenggara)
            self.tbl_beasiswa.setItem(row_position, 2, penyelenggara_item)
            
            # Column 3: Jenjang
            jenjang_item = QTableWidgetItem(beasiswa.get('jenjang', ''))
            jenjang_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            self.tbl_beasiswa.setItem(row_position, 3, jenjang_item)
            
            # Column 4: Deadline
            deadline_str = beasiswa.get('deadline', '')
            deadline_item = QTableWidgetItem(deadline_str)
            deadline_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            self.tbl_beasiswa.setItem(row_position, 4, deadline_item)
            
            # Column 5: Status
            status = beasiswa.get('status', '')
            status_item = QTableWidgetItem(status)
            status_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            self.tbl_beasiswa.setItem(row_position, 5, status_item)
        
        # Update row count label
        self.update_row_count(len(self.beasiswa_list))
        logger.info(f"✅ Table populated with {len(self.beasiswa_list)} rows")
    
    def update_row_count(self, count: int):
        """
        Update row count label (Task 13).
        
        Args:
            count: Number of rows displayed
        """
        if not self.lbl_row_count:
            logger.warning("❌ Row count label not initialized")
            return
        
        # Format: "Total: X Beasiswa" (pluralize)
        beasiswa_text = "Beasiswa" if count == 1 else "Beasiswa"
        total_text = f"Total: {count} {beasiswa_text}"
        
        self.lbl_row_count.setText(total_text)
        logger.debug(f"Row count updated: {total_text}")
    
    # =====================================================================
    # SECTION 3: FILTERING & SEARCH (Tasks 14-16)
    # =====================================================================
    
    def apply_filters(self):
        """
        Apply filters (jenjang, status, search) to beasiswa list (Task 14).
        Combines all active filters and updates table display.
        
        Process:
        1. Get filter values from dropdowns and search entry
        2. Call get_beasiswa_list() with filter parameters for server-side filtering
        3. Update filtered_list with results
        4. Refresh table display with filtered data
        5. Update row count label
        """
        try:
            # Get filter values
            filter_jenjang = self._get_filter_jenjang()
            filter_status = self._get_filter_status()
            search_text = self._get_search_text()
            
            logger.debug(f"Applying filters - Jenjang: {filter_jenjang}, Status: {filter_status}, Search: {search_text}")
            
            # Call get_beasiswa_list with filter parameters for server-side filtering
            self.filtered_list, total_filtered = get_beasiswa_list(
                filter_jenjang=filter_jenjang,
                filter_status=filter_status,
                search_judul=search_text if search_text else None
            )
            
            logger.info(f"✅ Filters applied: {len(self.filtered_list)} beasiswa matched")
            
            # Clear and repopulate table with filtered data
            self._clear_table()
            
            if not self.filtered_list:
                self.update_row_count(0)
                logger.info("No beasiswa matches applied filters")
                return
            
            # Populate table with filtered data
            for row_num, beasiswa in enumerate(self.filtered_list, 1):
                row_position = self.tbl_beasiswa.rowCount()
                self.tbl_beasiswa.insertRow(row_position)
                
                # Column 0: No
                no_item = QTableWidgetItem(str(row_num))
                no_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
                self.tbl_beasiswa.setItem(row_position, 0, no_item)
                
                # Column 1: Nama (judul)
                nama_item = QTableWidgetItem(beasiswa.get('judul', ''))
                self.tbl_beasiswa.setItem(row_position, 1, nama_item)
                
                # Column 2: Penyelenggara
                penyelenggara = beasiswa.get('penyelenggara_name', str(beasiswa.get('penyelenggara_id', '')))
                penyelenggara_item = QTableWidgetItem(penyelenggara)
                self.tbl_beasiswa.setItem(row_position, 2, penyelenggara_item)
                
                # Column 3: Jenjang
                jenjang_item = QTableWidgetItem(beasiswa.get('jenjang', ''))
                jenjang_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
                self.tbl_beasiswa.setItem(row_position, 3, jenjang_item)
                
                # Column 4: Deadline
                deadline_str = beasiswa.get('deadline', '')
                deadline_item = QTableWidgetItem(deadline_str)
                deadline_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
                self.tbl_beasiswa.setItem(row_position, 4, deadline_item)
                
                # Column 5: Status
                status = beasiswa.get('status', '')
                status_item = QTableWidgetItem(status)
                status_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
                self.tbl_beasiswa.setItem(row_position, 5, status_item)
            
            # Update row count with filtered result count
            self.update_row_count(len(self.filtered_list))
            
        except Exception as e:
            logger.error(f"❌ Error applying filters: {e}")
            self._clear_table()
            self.update_row_count(0)
    
    def _on_search_key_release(self, event):
        """
        Handle search entry KeyRelease event (Helper for Task 7).
        Triggered when user types in search box.
        
        Args:
            event: QKeyEvent object
        """
        # Call parent's keyReleaseEvent first
        super(QLineEdit, self.entry_search).keyReleaseEvent(event)
        
        # Trigger apply_filters() on key release
        self.apply_filters()
        logger.debug(f"Search key released: '{self._get_search_text()}'")
    
    def _get_filter_jenjang(self) -> Optional[str]:
        """
        Get selected jenjang filter value (Helper method for Task 5).
        
        Returns:
            Optional[str]: Selected value ("D3", "D4", "S1", "S2") or None if "Semua" is selected
        """
        if not self.combo_jenjang:
            return None
        
        selected = self.combo_jenjang.currentText()
        
        # Return None if "Semua" is selected (means no filter)
        if selected == "Semua":
            return None
        
        return selected
    
    def _get_filter_status(self) -> Optional[str]:
        """
        Get selected status filter value (Helper method for Task 6).
        
        Returns:
            Optional[str]: Selected value ("Buka", "Segera Tutup", "Tutup") or None if "Semua" is selected
        """
        if not self.combo_status:
            return None
        
        selected = self.combo_status.currentText()
        
        # Return None if "Semua" is selected (means no filter)
        if selected == "Semua":
            return None
        
        return selected
    
    def _get_search_text(self) -> str:
        """
        Get search entry text (Helper method for Task 7).
        
        Returns:
            str: Text from search entry (empty string if no text)
        """
        if not self.entry_search:
            return ""
        
        search_text = self.entry_search.text().strip()
        return search_text
    
    def on_refresh_clicked(self):
        """
        Handle Refresh button click (Task 16).
        Reload data from database and refresh table.
        
        Steps:
        1. Load fresh data from database
        2. Update timestamp label
        3. Apply current filters
        4. Show success message
        """
        logger.info("Refresh button clicked - reloading data from database")
        self.refresh_after_crud()
        QMessageBox.information(self, "Sukses", "✅ Data beasiswa berhasil di-refresh!")
        logger.info("✅ Data refresh completed successfully")
    
    # =====================================================================
    # SECTION 4: CRUD OPERATIONS (Tasks 17-24)
    # =====================================================================
    
    def on_tambah_clicked(self):
        """
        Handle Tambah button click (Task 20) -> open AddBeasiswaDialog.
        
        Called when user clicks Tambah button.
        Will open dialog to add new beasiswa (implemented in Task 20).
        """
        logger.info("Tambah button clicked - will open AddBeasiswaDialog in Task 20")
        # Will be implemented in Task 20
        pass
    
    def on_edit_clicked(self):
        """
        Handle Edit button click (Task 21) -> get selected row and open EditBeasiswaDialog.
        
        Called when user clicks Edit button.
        Validates row selection, retrieves data, opens edit dialog (Task 21).
        """
        logger.info("Edit button clicked - will open EditBeasiswaDialog in Task 21")
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
        """
        Handle Hapus button click (Task 23) -> get selected row and open DeleteConfirmationDialog.
        
        Called when user clicks Hapus button.
        Validates row selection, shows confirmation dialog, deletes if confirmed (Task 23).
        """
        logger.info("Hapus button clicked - will open DeleteConfirmationDialog in Task 23")
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
        
        Steps:
        1. Reload data from database
        2. Update timestamp label
        3. Apply current filters
        """
        self.load_beasiswa_data()
        self.update_timestamp_label()
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
        """
        Handle Export CSV button click (Task 30).
        Open file dialog and export filtered data.
        
        Steps:
        1. Open file save dialog
        2. Get filename from user
        3. Export current table data to CSV
        4. Show success/error message
        """
        logger.info("Export CSV button clicked - opening file save dialog")
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
