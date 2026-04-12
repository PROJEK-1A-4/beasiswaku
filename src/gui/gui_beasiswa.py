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
        # Connect double-click to show detail dialog
        if self.tbl_beasiswa:
            self.tbl_beasiswa.itemDoubleClicked.connect(self.on_table_double_click)
            logger.debug("✅ Table double-click signal connected to on_table_double_click()")
        
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
        if self.btn_tambah:
            self.btn_tambah.clicked.connect(self.on_tambah_clicked)
            logger.debug("✅ Tambah button clicked signal connected to on_tambah_clicked()")
        
        # ===== TASK 21: CONNECT EDIT BUTTON SIGNAL =====
        if self.btn_edit:
            self.btn_edit.clicked.connect(self.on_edit_clicked)
            logger.debug("✅ Edit button clicked signal connected to on_edit_clicked()")
        
        # ===== TASK 23: CONNECT HAPUS BUTTON SIGNAL =====
        if self.btn_hapus:
            self.btn_hapus.clicked.connect(self.on_hapus_clicked)
            logger.debug("✅ Hapus button clicked signal connected to on_hapus_clicked()")
        
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
        
        # Apply deadline highlighting to all rows (Task 25)
        self.apply_row_formatting()
        
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
            
            # Apply deadline highlighting to all rows (Task 25)
            self.apply_row_formatting()
            
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
        Opens dialog to add new beasiswa and saves if confirmed.
        """
        logger.info("Tambah button clicked - opening AddBeasiswaDialog")
        
        try:
            # Create and show AddBeasiswaDialog
            dialog = AddBeasiswaDialog(parent=self)
            
            if dialog.exec() == QDialog.DialogCode.Accepted:
                # User clicked OK button
                logger.info("AddBeasiswaDialog accepted - saving new beasiswa")
                
                try:
                    # Get form data from dialog
                    form_data = dialog.get_form_data()
                    
                    # Call add_beasiswa() from CRUD
                    result = add_beasiswa(
                        judul=form_data['judul'],
                        jenjang=form_data['jenjang'],
                        deadline=form_data['deadline'],
                        penyelenggara_id=form_data['penyelenggara_id'],
                        deskripsi=form_data['deskripsi'],
                        benefit=form_data['benefit'],
                        persyaratan=form_data['persyaratan'],
                        minimal_ipk=form_data['minimal_ipk'],
                        coverage=form_data['coverage'],
                        status=form_data['status'],
                        link_aplikasi=form_data['link_aplikasi']
                    )
                    
                    logger.info(f"✅ Beasiswa berhasil ditambahkan: {form_data['judul']}")
                    
                    # Show success message
                    QMessageBox.information(
                        self, 
                        "Sukses", 
                        f"✅ Beasiswa '{form_data['judul']}' berhasil ditambahkan!"
                    )
                    
                    # Refresh table with new data
                    self.refresh_after_crud()
                    
                except ValueError as ve:
                    # Validation error from get_form_data()
                    logger.error(f"❌ Form validation error: {ve}")
                    QMessageBox.warning(self, "⚠️ Error", f"Input tidak valid:\n{str(ve)}")
                    
                except Exception as e:
                    # Database or other error
                    logger.error(f"❌ Error adding beasiswa: {e}")
                    QMessageBox.critical(self, "❌ Error", f"Gagal menambahkan beasiswa:\n{str(e)}")
            else:
                # User clicked Cancel
                logger.info("AddBeasiswaDialog cancelled")
                
        except Exception as e:
            logger.error(f"❌ Error opening AddBeasiswaDialog: {e}")
            QMessageBox.critical(self, "❌ Error", f"Gagal membuka dialog tambah:\n{str(e)}")
    
    def on_edit_clicked(self):
        """
        Handle Edit button click (Task 21) -> get selected row and open EditBeasiswaDialog.
        
        Called when user clicks Edit button.
        Validates row selection, retrieves data, opens edit dialog.
        """
        logger.info("Edit button clicked - validating row selection")
        
        # Check if a row is selected
        selected_rows = self.tbl_beasiswa.selectedIndexes()
        if not selected_rows:
            logger.warning("No row selected for edit")
            QMessageBox.warning(self, "⚠️ Peringatan", "Silakan pilih beasiswa yang ingin diedit!")
            return
        
        try:
            # Get selected row index
            row_index = selected_rows[0].row()
            
            # Get beasiswa data from filtered list
            if row_index >= len(self.filtered_list):
                logger.error(f"Row index {row_index} out of range")
                QMessageBox.critical(self, "❌ Error", "Data beasiswa tidak ditemukan!")
                return
            
            beasiswa_data = self.filtered_list[row_index]
            logger.info(f"Selected beasiswa for edit: {beasiswa_data.get('judul')}")
            
            # Open EditBeasiswaDialog with selected data (Task 22)
            self.on_edit(beasiswa_data)
            
        except Exception as e:
            logger.error(f"❌ Error getting selected row: {e}")
            QMessageBox.critical(self, "❌ Error", f"Gagal memilih baris untuk diedit:\n{str(e)}")
    
    def on_edit(self, beasiswa_data: Dict):
        """
        Open EditBeasiswaDialog and handle edit confirmation (Task 22).
        
        Args:
            beasiswa_data: Dictionary with beasiswa details to edit
        """
        logger.info(f"Opening EditBeasiswaDialog for: {beasiswa_data.get('judul')}")
        
        try:
            # Create and show EditBeasiswaDialog with current data
            dialog = EditBeasiswaDialog(beasiswa_data=beasiswa_data, parent=self)
            
            if dialog.exec() == QDialog.DialogCode.Accepted:
                # User clicked OK button
                logger.info("EditBeasiswaDialog accepted - updating beasiswa")
                
                try:
                    # Get updated form data from dialog
                    updated_data = dialog.get_form_data()
                    
                    # Get beasiswa ID from original data
                    beasiswa_id = beasiswa_data.get('id')
                    if not beasiswa_id:
                        raise ValueError("Beasiswa ID tidak ditemukan")
                    
                    # Call edit_beasiswa() from CRUD
                    result = edit_beasiswa(
                        beasiswa_id=beasiswa_id,
                        judul=updated_data['judul'],
                        jenjang=updated_data['jenjang'],
                        deadline=updated_data['deadline'],
                        penyelenggara_id=updated_data['penyelenggara_id'],
                        deskripsi=updated_data['deskripsi'],
                        benefit=updated_data['benefit'],
                        persyaratan=updated_data['persyaratan'],
                        minimal_ipk=updated_data['minimal_ipk'],
                        coverage=updated_data['coverage'],
                        status=updated_data['status'],
                        link_aplikasi=updated_data['link_aplikasi']
                    )
                    
                    logger.info(f"✅ Beasiswa berhasil diperbarui: {updated_data['judul']}")
                    
                    # Show success message
                    QMessageBox.information(
                        self, 
                        "Sukses", 
                        f"✅ Beasiswa '{updated_data['judul']}' berhasil diperbarui!"
                    )
                    
                    # Refresh table with updated data
                    self.refresh_after_crud()
                    
                except ValueError as ve:
                    # Validation error from get_form_data()
                    logger.error(f"❌ Form validation error: {ve}")
                    QMessageBox.warning(self, "⚠️ Error", f"Input tidak valid:\n{str(ve)}")
                    
                except Exception as e:
                    # Database or other error
                    logger.error(f"❌ Error updating beasiswa: {e}")
                    QMessageBox.critical(self, "❌ Error", f"Gagal memperbarui beasiswa:\n{str(e)}")
            else:
                # User clicked Cancel
                logger.info("EditBeasiswaDialog cancelled")
                
        except Exception as e:
            logger.error(f"❌ Error opening EditBeasiswaDialog: {e}")
            QMessageBox.critical(self, "❌ Error", f"Gagal membuka dialog edit:\n{str(e)}")
    
    def on_hapus_clicked(self):
        """
        Handle Hapus button click (Task 23) -> get selected row and open DeleteConfirmationDialog.
        
        Called when user clicks Hapus button.
        Validates row selection, shows confirmation dialog, deletes if confirmed.
        """
        logger.info("Hapus button clicked - validating row selection")
        
        # Check if a row is selected
        selected_rows = self.tbl_beasiswa.selectedIndexes()
        if not selected_rows:
            logger.warning("No row selected for delete")
            QMessageBox.warning(self, "⚠️ Peringatan", "Silakan pilih beasiswa yang ingin dihapus!")
            return
        
        try:
            # Get selected row index
            row_index = selected_rows[0].row()
            
            # Get beasiswa data from filtered list
            if row_index >= len(self.filtered_list):
                logger.error(f"Row index {row_index} out of range")
                QMessageBox.critical(self, "❌ Error", "Data beasiswa tidak ditemukan!")
                return
            
            beasiswa_data = self.filtered_list[row_index]
            judul = beasiswa_data.get('judul', 'N/A')
            logger.info(f"Selected beasiswa for delete: {judul}")
            
            # Open DeleteConfirmationDialog
            dialog = DeleteConfirmationDialog(beasiswa_judul=judul, parent=self)
            
            if dialog.exec() == QDialog.DialogCode.Accepted:
                # User confirmed deletion
                logger.info("DeleteConfirmationDialog accepted - deleting beasiswa")
                beasiswa_id = beasiswa_data.get('id')
                if beasiswa_id:
                    self.on_delete(beasiswa_id)
                else:
                    logger.error("Beasiswa ID not found in data")
                    QMessageBox.critical(self, "❌ Error", "ID beasiswa tidak ditemukan!")
            else:
                # User cancelled deletion
                logger.info("DeleteConfirmationDialog cancelled")
                
        except Exception as e:
            logger.error(f"❌ Error on delete dialog: {e}")
            QMessageBox.critical(self, "❌ Error", f"Gagal membuka dialog hapus:\n{str(e)}")
    
    def on_delete(self, beasiswa_id: int):
        """
        Delete beasiswa from database (Task 24).
        
        Args:
            beasiswa_id: ID beasiswa yang akan didelete
        """
        logger.info(f"Deleting beasiswa with ID: {beasiswa_id}")
        
        try:
            # Call delete_beasiswa() from CRUD
            result = delete_beasiswa(beasiswa_id=beasiswa_id)
            
            logger.info(f"✅ Beasiswa berhasil dihapus (ID: {beasiswa_id})")
            
            # Show success message
            QMessageBox.information(
                self, 
                "Sukses", 
                "✅ Beasiswa berhasil dihapus!"
            )
            
            # Refresh table with updated data
            self.refresh_after_crud()
            
        except Exception as e:
            logger.error(f"❌ Error deleting beasiswa: {e}")
            QMessageBox.critical(self, "❌ Error", f"Gagal menghapus beasiswa:\n{str(e)}")
    
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
        Called setelah table di-populate dengan data.
        Apply colors: Red (≤3 hari), Yellow (≤7 hari), Green (>7 hari)
        """
        if not self.tbl_beasiswa:
            logger.warning("Table widget not initialized for formatting")
            return
        
        try:
            # Iterate through all rows
            for row in range(self.tbl_beasiswa.rowCount()):
                # Get deadline from column 4
                deadline_item = self.tbl_beasiswa.item(row, 4)
                if not deadline_item:
                    continue
                
                deadline_str = deadline_item.text()
                
                # Get color and status text based on deadline
                color, status_text = self.highlight_deadline(deadline_str)
                
                # Apply color to deadline cell (column 4)
                deadline_item.setForeground(QBrush(color))
                deadline_item.setFont(QFont("Arial", 10, QFont.Weight.Bold))
                
                # Also apply color to entire row for visibility
                for col in range(self.tbl_beasiswa.columnCount()):
                    cell_item = self.tbl_beasiswa.item(row, col)
                    if cell_item:
                        if color == QColor("#FF6B6B"):  # Red - urgent/overdue
                            cell_item.setBackground(QBrush(QColor("#FFEBEE")))  # Light red background
                        elif color == QColor("#FFA500"):  # Yellow - soon
                            cell_item.setBackground(QBrush(QColor("#FFFDE7")))  # Light yellow background
                        # Green doesn't need special background, keep default
            
            logger.info(f"✅ Row formatting applied to {self.tbl_beasiswa.rowCount()} rows")
            
        except Exception as e:
            logger.error(f"❌ Error applying row formatting: {e}")
    
    def on_table_double_click(self, row: int, column: int):
        """
        Handle table double-click to show detail popup (Task 28).
        
        Args:
            row: Row index clicked
            column: Column index clicked
        """
        logger.info(f"Table double-clicked at row {row}, column {column}")
        
        try:
            # Get beasiswa data from filtered list
            if row >= len(self.filtered_list):
                logger.error(f"Row index {row} out of range")
                return
            
            beasiswa_data = self.filtered_list[row]
            logger.info(f"Opening detail dialog for: {beasiswa_data.get('judul')}")
            
            # Show detail dialog (Task 27)
            self.show_detail_dialog(beasiswa_data)
            
        except Exception as e:
            logger.error(f"❌ Error handling table double-click: {e}")
    
    def show_detail_dialog(self, beasiswa_data: Dict):
        """
        Show detail popup dialog with all beasiswa information (Task 27).
        
        Args:
            beasiswa_data: Dictionary with beasiswa details
        """
        logger.info(f"Opening detail dialog for: {beasiswa_data.get('judul')}")
        
        try:
            dialog = BeasiswaDetailDialog(beasiswa_data=beasiswa_data, parent=self)
            dialog.exec()
            
        except Exception as e:
            logger.error(f"❌ Error showing detail dialog: {e}")
            QMessageBox.critical(self, "❌ Error", f"Gagal membuka detail beasiswa:\n{str(e)}")
    
    # =====================================================================
    # SECTION 6: EXPORT (Tasks 29-30)
    # =====================================================================
    
    def on_export_csv_clicked(self):
        """
        Handle Export CSV button click (Task 30).
        Open file dialog and export filtered data to CSV file.
        
        Steps:
        1. Open file save dialog
        2. Get filename from user
        3. Export current table data to CSV
        4. Show success/error message
        """
        logger.info("Export CSV button clicked - opening file save dialog")
        
        try:
            # Open file save dialog
            file_path, _ = QFileDialog.getSaveFileName(
                self,
                "Simpan Data Beasiswa sebagai CSV",
                "",
                "CSV Files (*.csv);;All Files (*.*)"
            )
            
            if not file_path:
                logger.info("Export CSV cancelled by user")
                return
            
            # Ensure file has .csv extension
            if not file_path.endswith('.csv'):
                file_path += '.csv'
            
            logger.info(f"Exporting to: {file_path}")
            
            # Get CSV data from export_to_csv()
            csv_data = self.export_to_csv()
            
            if not csv_data:
                logger.error("Failed to prepare CSV data")
                QMessageBox.critical(self, "❌ Error", "Gagal menyiapkan data CSV!")
                return
            
            # Write to file
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(csv_data)
            
            logger.info(f"✅ CSV file exported successfully: {file_path}")
            QMessageBox.information(
                self,
                "Sukses",
                f"✅ Data beasiswa berhasil diekspor ke:\n{file_path}"
            )
            
        except Exception as e:
            logger.error(f"❌ Error exporting CSV: {e}")
            QMessageBox.critical(self, "❌ Error", f"Gagal mengekspor CSV:\n{str(e)}")
    
    def export_to_csv(self):
        """
        Export filtered beasiswa data to CSV file (Task 29).
        
        Exports current filtered table data to CSV format with columns:
        No, Nama, Penyelenggara, Jenjang, Deadline, Status
        
        Returns:
            bool: True if successful, False otherwise
        """
        logger.info("Exporting filtered beasiswa data to CSV")
        
        try:
            if not self.filtered_list:
                logger.warning("No data to export")
                QMessageBox.warning(self, "⚠️ Peringatan", "Tidak ada data untuk diekspor!")
                return False
            
            # Prepare CSV content
            csv_content = []
            
            # Header row
            header = ["No", "Nama", "Penyelenggara", "Jenjang", "Deadline", "Status"]
            csv_content.append(",".join(header))
            
            # Data rows
            for row_num, beasiswa in enumerate(self.filtered_list, 1):
                nama = beasiswa.get('judul', '')
                penyelenggara = beasiswa.get('penyelenggara_name', str(beasiswa.get('penyelenggara_id', '')))
                jenjang = beasiswa.get('jenjang', '')
                deadline = beasiswa.get('deadline', '')
                status = beasiswa.get('status', '')
                
                # Format row: escape quotes and handle commas
                row = [
                    str(row_num),
                    f'"{nama}"',  # Quote name in case it has commas
                    f'"{penyelenggara}"',
                    jenjang,
                    deadline,
                    status
                ]
                csv_content.append(",".join(row))
            
            # Join all rows
            csv_data = "\n".join(csv_content)
            
            logger.info(f"✅ CSV data prepared: {len(self.filtered_list)} rows")
            return csv_data
            
        except Exception as e:
            logger.error(f"❌ Error preparing CSV data: {e}")
            return False


# ==================== DIALOG CLASSES ====================

class AddBeasiswaDialog(QDialog):
    """
    Dialog untuk menambah beasiswa baru (Task 16).
    Form fields untuk semua beasiswa properties.
    """
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.init_ui()
    
    def init_ui(self):
        """Initialize Add Beasiswa Dialog UI with form fields"""
        self.setWindowTitle("➕ Tambah Beasiswa Baru")
        self.setGeometry(200, 200, 700, 850)
        self.setModal(True)
        
        layout = QVBoxLayout()
        
        # ===== REQUIRED FIELDS SECTION =====
        form_layout = QFormLayout()
        
        # Field 1: Judul Beasiswa (required)
        self.entry_judul = QLineEdit()
        self.entry_judul.setPlaceholderText("e.g., Beasiswa LPDP 2026")
        form_layout.addRow("Judul Beasiswa *:", self.entry_judul)
        
        # Field 2: Jenjang (required) - Dropdown
        self.combo_jenjang = QComboBox()
        self.combo_jenjang.addItems(["D3", "D4", "S1", "S2"])
        form_layout.addRow("Jenjang *:", self.combo_jenjang)
        
        # Field 3: Deadline (required) - Date picker
        self.entry_deadline = QLineEdit()
        self.entry_deadline.setPlaceholderText("YYYY-MM-DD (e.g., 2026-12-31)")
        form_layout.addRow("Deadline *:", self.entry_deadline)
        
        # ===== OPTIONAL FIELDS SECTION =====
        
        # Field 4: Penyelenggara ID (optional)
        self.entry_penyelenggara = QLineEdit()
        self.entry_penyelenggara.setPlaceholderText("e.g., 1 (jika ada)")
        form_layout.addRow("Penyelenggara ID:", self.entry_penyelenggara)
        
        # Field 5: Status (optional) - Dropdown
        self.combo_status = QComboBox()
        self.combo_status.addItems(["Buka", "Segera Tutup", "Tutup"])
        self.combo_status.setCurrentText("Buka")
        form_layout.addRow("Status:", self.combo_status)
        
        # Field 6: Minimal IPK (optional)
        self.entry_ipk = QLineEdit()
        self.entry_ipk.setPlaceholderText("e.g., 3.0 (0.0 - 4.0)")
        form_layout.addRow("Minimal IPK:", self.entry_ipk)
        
        # Field 7: Deskripsi (optional) - Multi-line
        self.text_deskripsi = QTextEdit()
        self.text_deskripsi.setPlaceholderText("Deskripsi beasiswa...")
        self.text_deskripsi.setMaximumHeight(80)
        form_layout.addRow("Deskripsi:", self.text_deskripsi)
        
        # Field 8: Benefit (optional) - Multi-line
        self.text_benefit = QTextEdit()
        self.text_benefit.setPlaceholderText("Benefit/keuntungan beasiswa...")
        self.text_benefit.setMaximumHeight(80)
        form_layout.addRow("Benefit:", self.text_benefit)
        
        # Field 9: Persyaratan (optional) - Multi-line
        self.text_persyaratan = QTextEdit()
        self.text_persyaratan.setPlaceholderText("Persyaratan dan ketentuan...")
        self.text_persyaratan.setMaximumHeight(80)
        form_layout.addRow("Persyaratan:", self.text_persyaratan)
        
        # Field 10: Coverage (optional)
        self.entry_coverage = QLineEdit()
        self.entry_coverage.setPlaceholderText("e.g., Fully, Partially, Partial Tuition")
        form_layout.addRow("Coverage:", self.entry_coverage)
        
        # Field 11: Link Aplikasi (optional)
        self.entry_link = QLineEdit()
        self.entry_link.setPlaceholderText("https://...")
        form_layout.addRow("Link Aplikasi:", self.entry_link)
        
        layout.addLayout(form_layout)
        
        # ===== BUTTON SECTION =====
        button_layout = QHBoxLayout()
        button_layout.addStretch()
        
        btn_ok = QPushButton("✅ Tambah")
        btn_ok.setStyleSheet("""
            QPushButton {
                background-color: #4CAF50;
                color: white;
                border: none;
                border-radius: 5px;
                padding: 8px 20px;
                font-weight: bold;
            }
            QPushButton:hover { background-color: #45a049; }
            QPushButton:pressed { background-color: #3d8b40; }
        """)
        btn_ok.clicked.connect(self.accept)
        button_layout.addWidget(btn_ok)
        
        btn_cancel = QPushButton("❌ Batal")
        btn_cancel.setStyleSheet("""
            QPushButton {
                background-color: #f44336;
                color: white;
                border: none;
                border-radius: 5px;
                padding: 8px 20px;
                font-weight: bold;
            }
            QPushButton:hover { background-color: #da190b; }
            QPushButton:pressed { background-color: #ba0a0a; }
        """)
        btn_cancel.clicked.connect(self.reject)
        button_layout.addWidget(btn_cancel)
        
        layout.addLayout(button_layout)
        
        self.setLayout(layout)
        logger.debug("✅ AddBeasiswaDialog UI initialized")
    
    def get_form_data(self) -> Dict:
        """
        Get form data and validate (Task 16).
        
        Returns:
            Dict: Form data with keys: judul, jenjang, deadline, 
                  penyelenggara_id, deskripsi, benefit, persyaratan,
                  minimal_ipk, coverage, status, link_aplikasi
        """
        # Get required fields
        judul = self.entry_judul.text().strip()
        if not judul:
            raise ValueError("Judul beasiswa tidak boleh kosong")
        
        jenjang = self.combo_jenjang.currentText()
        
        deadline = self.entry_deadline.text().strip()
        if not deadline:
            raise ValueError("Deadline tidak boleh kosong")
        
        # Validate deadline format (YYYY-MM-DD)
        try:
            from datetime import datetime
            datetime.strptime(deadline, '%Y-%m-%d')
        except ValueError:
            raise ValueError("Format deadline harus YYYY-MM-DD (e.g., 2026-12-31)")
        
        # Get optional fields
        penyelenggara_id = None
        penyelenggara_str = self.entry_penyelenggara.text().strip()
        if penyelenggara_str:
            try:
                penyelenggara_id = int(penyelenggara_str)
            except ValueError:
                raise ValueError("Penyelenggara ID harus berupa angka")
        
        deskripsi = self.text_deskripsi.toPlainText().strip()
        benefit = self.text_benefit.toPlainText().strip()
        persyaratan = self.text_persyaratan.toPlainText().strip()
        coverage = self.entry_coverage.text().strip()
        status = self.combo_status.currentText()
        link_aplikasi = self.entry_link.text().strip()
        
        # Validate IPK if provided
        minimal_ipk = None
        ipk_str = self.entry_ipk.text().strip()
        if ipk_str:
            try:
                minimal_ipk = float(ipk_str)
                if not (0.0 <= minimal_ipk <= 4.0):
                    raise ValueError("IPK harus antara 0.0 dan 4.0")
            except ValueError:
                raise ValueError("Minimal IPK harus berupa angka desimal (0.0 - 4.0)")
        
        return {
            'judul': judul,
            'jenjang': jenjang,
            'deadline': deadline,
            'penyelenggara_id': penyelenggara_id,
            'deskripsi': deskripsi,
            'benefit': benefit,
            'persyaratan': persyaratan,
            'minimal_ipk': minimal_ipk,
            'coverage': coverage,
            'status': status,
            'link_aplikasi': link_aplikasi
        }


class EditBeasiswaDialog(QDialog):
    """
    Dialog untuk edit beasiswa existing (Task 17).
    Form fields pre-filled dengan data existing.
    """
    
    def __init__(self, beasiswa_data: Dict, parent=None):
        super().__init__(parent)
        self.beasiswa_data = beasiswa_data
        self.init_ui()
    
    def init_ui(self):
        """Initialize Edit Beasiswa Dialog UI with pre-filled data"""
        judul = self.beasiswa_data.get('judul', 'Beasiswa')
        self.setWindowTitle(f"✏️ Edit - {judul}")
        self.setGeometry(200, 200, 700, 850)
        self.setModal(True)
        
        layout = QVBoxLayout()
        
        # ===== REQUIRED FIELDS SECTION =====
        form_layout = QFormLayout()
        
        # Field 1: Judul Beasiswa (required) - Pre-filled
        self.entry_judul = QLineEdit()
        self.entry_judul.setText(self.beasiswa_data.get('judul', ''))
        form_layout.addRow("Judul Beasiswa *:", self.entry_judul)
        
        # Field 2: Jenjang (required) - Dropdown pre-filled
        self.combo_jenjang = QComboBox()
        self.combo_jenjang.addItems(["D3", "D4", "S1", "S2"])
        current_jenjang = self.beasiswa_data.get('jenjang', 'S1')
        if current_jenjang in ["D3", "D4", "S1", "S2"]:
            self.combo_jenjang.setCurrentText(current_jenjang)
        form_layout.addRow("Jenjang *:", self.combo_jenjang)
        
        # Field 3: Deadline (required) - Pre-filled
        self.entry_deadline = QLineEdit()
        self.entry_deadline.setText(self.beasiswa_data.get('deadline', ''))
        self.entry_deadline.setPlaceholderText("YYYY-MM-DD (e.g., 2026-12-31)")
        form_layout.addRow("Deadline *:", self.entry_deadline)
        
        # ===== OPTIONAL FIELDS SECTION =====
        
        # Field 4: Penyelenggara ID (optional) - Pre-filled
        self.entry_penyelenggara = QLineEdit()
        penyelenggara_id = self.beasiswa_data.get('penyelenggara_id')
        if penyelenggara_id:
            self.entry_penyelenggara.setText(str(penyelenggara_id))
        form_layout.addRow("Penyelenggara ID:", self.entry_penyelenggara)
        
        # Field 5: Status (optional) - Dropdown pre-filled
        self.combo_status = QComboBox()
        self.combo_status.addItems(["Buka", "Segera Tutup", "Tutup"])
        current_status = self.beasiswa_data.get('status', 'Buka')
        if current_status in ["Buka", "Segera Tutup", "Tutup"]:
            self.combo_status.setCurrentText(current_status)
        form_layout.addRow("Status:", self.combo_status)
        
        # Field 6: Minimal IPK (optional) - Pre-filled
        self.entry_ipk = QLineEdit()
        minimal_ipk = self.beasiswa_data.get('minimal_ipk')
        if minimal_ipk:
            self.entry_ipk.setText(str(minimal_ipk))
        form_layout.addRow("Minimal IPK:", self.entry_ipk)
        
        # Field 7: Deskripsi (optional) - Multi-line pre-filled
        self.text_deskripsi = QTextEdit()
        self.text_deskripsi.setPlainText(self.beasiswa_data.get('deskripsi', ''))
        self.text_deskripsi.setMaximumHeight(80)
        form_layout.addRow("Deskripsi:", self.text_deskripsi)
        
        # Field 8: Benefit (optional) - Multi-line pre-filled
        self.text_benefit = QTextEdit()
        self.text_benefit.setPlainText(self.beasiswa_data.get('benefit', ''))
        self.text_benefit.setMaximumHeight(80)
        form_layout.addRow("Benefit:", self.text_benefit)
        
        # Field 9: Persyaratan (optional) - Multi-line pre-filled
        self.text_persyaratan = QTextEdit()
        self.text_persyaratan.setPlainText(self.beasiswa_data.get('persyaratan', ''))
        self.text_persyaratan.setMaximumHeight(80)
        form_layout.addRow("Persyaratan:", self.text_persyaratan)
        
        # Field 10: Coverage (optional) - Pre-filled
        self.entry_coverage = QLineEdit()
        self.entry_coverage.setText(self.beasiswa_data.get('coverage', ''))
        form_layout.addRow("Coverage:", self.entry_coverage)
        
        # Field 11: Link Aplikasi (optional) - Pre-filled
        self.entry_link = QLineEdit()
        self.entry_link.setText(self.beasiswa_data.get('link_aplikasi', ''))
        form_layout.addRow("Link Aplikasi:", self.entry_link)
        
        layout.addLayout(form_layout)
        
        # ===== BUTTON SECTION =====
        button_layout = QHBoxLayout()
        button_layout.addStretch()
        
        btn_ok = QPushButton("✅ Simpan")
        btn_ok.setStyleSheet("""
            QPushButton {
                background-color: #2196F3;
                color: white;
                border: none;
                border-radius: 5px;
                padding: 8px 20px;
                font-weight: bold;
            }
            QPushButton:hover { background-color: #0b7dda; }
            QPushButton:pressed { background-color: #0966cc; }
        """)
        btn_ok.clicked.connect(self.accept)
        button_layout.addWidget(btn_ok)
        
        btn_cancel = QPushButton("❌ Batal")
        btn_cancel.setStyleSheet("""
            QPushButton {
                background-color: #f44336;
                color: white;
                border: none;
                border-radius: 5px;
                padding: 8px 20px;
                font-weight: bold;
            }
            QPushButton:hover { background-color: #da190b; }
            QPushButton:pressed { background-color: #ba0a0a; }
        """)
        btn_cancel.clicked.connect(self.reject)
        button_layout.addWidget(btn_cancel)
        
        layout.addLayout(button_layout)
        
        self.setLayout(layout)
        logger.debug(f"✅ EditBeasiswaDialog UI initialized for: {judul}")
    
    def get_form_data(self) -> Dict:
        """
        Get form data and validate (Task 17).
        
        Returns:
            Dict: Form data with all beasiswa fields (same as AddBeasiswaDialog)
        """
        # Get required fields
        judul = self.entry_judul.text().strip()
        if not judul:
            raise ValueError("Judul beasiswa tidak boleh kosong")
        
        jenjang = self.combo_jenjang.currentText()
        
        deadline = self.entry_deadline.text().strip()
        if not deadline:
            raise ValueError("Deadline tidak boleh kosong")
        
        # Validate deadline format (YYYY-MM-DD)
        try:
            from datetime import datetime
            datetime.strptime(deadline, '%Y-%m-%d')
        except ValueError:
            raise ValueError("Format deadline harus YYYY-MM-DD (e.g., 2026-12-31)")
        
        # Get optional fields
        penyelenggara_id = None
        penyelenggara_str = self.entry_penyelenggara.text().strip()
        if penyelenggara_str:
            try:
                penyelenggara_id = int(penyelenggara_str)
            except ValueError:
                raise ValueError("Penyelenggara ID harus berupa angka")
        
        deskripsi = self.text_deskripsi.toPlainText().strip()
        benefit = self.text_benefit.toPlainText().strip()
        persyaratan = self.text_persyaratan.toPlainText().strip()
        coverage = self.entry_coverage.text().strip()
        status = self.combo_status.currentText()
        link_aplikasi = self.entry_link.text().strip()
        
        # Validate IPK if provided
        minimal_ipk = None
        ipk_str = self.entry_ipk.text().strip()
        if ipk_str:
            try:
                minimal_ipk = float(ipk_str)
                if not (0.0 <= minimal_ipk <= 4.0):
                    raise ValueError("IPK harus antara 0.0 dan 4.0")
            except ValueError:
                raise ValueError("Minimal IPK harus berupa angka desimal (0.0 - 4.0)")
        
        return {
            'id': self.beasiswa_data.get('id'),  # Preserve original ID
            'judul': judul,
            'jenjang': jenjang,
            'deadline': deadline,
            'penyelenggara_id': penyelenggara_id,
            'deskripsi': deskripsi,
            'benefit': benefit,
            'persyaratan': persyaratan,
            'minimal_ipk': minimal_ipk,
            'coverage': coverage,
            'status': status,
            'link_aplikasi': link_aplikasi
        }


class DeleteConfirmationDialog(QDialog):
    """
    Dialog untuk konfirmasi penghapusan beasiswa (Task 18).
    Menampilkan warning dan tombol Yes/No.
    """
    
    def __init__(self, beasiswa_judul: str, parent=None):
        super().__init__(parent)
        self.beasiswa_judul = beasiswa_judul
        self.init_ui()
    
    def init_ui(self):
        """Initialize Delete Confirmation Dialog UI"""
        self.setWindowTitle("⚠️ Konfirmasi Hapus")
        self.setGeometry(300, 300, 500, 250)
        self.setModal(True)
        
        layout = QVBoxLayout()
        layout.setSpacing(15)
        
        # ===== WARNING ICON & MESSAGE =====
        message_layout = QHBoxLayout()
        
        # Warning icon/emoji
        icon_label = QLabel("⚠️")
        icon_label.setFont(QFont("Arial", 32))
        icon_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        message_layout.addWidget(icon_label)
        
        # Warning message
        message_text = f"""Apakah Anda yakin ingin menghapus beasiswa:

"{self.beasiswa_judul}"

Tindakan ini TIDAK DAPAT DIBATALKAN dan akan menghapus semua data terkait."""
        
        msg_label = QLabel(message_text)
        msg_label.setFont(QFont("Arial", 10))
        msg_label.setWordWrap(True)
        msg_label.setStyleSheet("color: #d32f2f; font-weight: bold;")
        msg_label.setAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignTop)
        message_layout.addWidget(msg_label, 1)
        
        layout.addLayout(message_layout)
        layout.addSpacing(10)
        
        # ===== BUTTON SECTION =====
        button_layout = QHBoxLayout()
        button_layout.addStretch()
        
        # Yes button (Delete) - Red
        btn_yes = QPushButton("🗑️ Ya, Hapus")
        btn_yes.setStyleSheet("""
            QPushButton {
                background-color: #f44336;
                color: white;
                border: none;
                border-radius: 5px;
                padding: 10px 25px;
                font-weight: bold;
                font-size: 11px;
            }
            QPushButton:hover { background-color: #da190b; }
            QPushButton:pressed { background-color: #ba0a0a; }
        """)
        btn_yes.clicked.connect(self.accept)
        button_layout.addWidget(btn_yes)
        
        # No button (Cancel) - Gray
        btn_no = QPushButton("❌ Batal")
        btn_no.setStyleSheet("""
            QPushButton {
                background-color: #757575;
                color: white;
                border: none;
                border-radius: 5px;
                padding: 10px 25px;
                font-weight: bold;
                font-size: 11px;
            }
            QPushButton:hover { background-color: #616161; }
            QPushButton:pressed { background-color: #424242; }
        """)
        btn_no.clicked.connect(self.reject)
        button_layout.addWidget(btn_no)
        
        layout.addLayout(button_layout)
        layout.addSpacing(10)
        
        self.setLayout(layout)
        logger.debug(f"✅ DeleteConfirmationDialog UI initialized for: {self.beasiswa_judul}")


class BeasiswaDetailDialog(QDialog):
    """
    Dialog untuk menampilkan detail lengkap beasiswa (Task 27 & 28).
    Dipanggil saat user double-click row di table.
    Menampilkan semua field beasiswa dengan format readable.
    """
    
    def __init__(self, beasiswa_data: Dict, parent=None):
        super().__init__(parent)
        self.beasiswa_data = beasiswa_data
        self.init_ui()
    
    def init_ui(self):
        """Initialize Beasiswa Detail Dialog UI dengan semua informasi beasiswa"""
        judul = self.beasiswa_data.get('judul', 'Beasiswa')
        self.setWindowTitle(f"📚 Detail Beasiswa - {judul}")
        self.setGeometry(150, 150, 850, 750)
        self.setModal(True)
        
        # Main layout
        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(15, 15, 15, 15)
        main_layout.setSpacing(10)
        
        # ===== TITLE SECTION =====
        title_label = QLabel(f"📚 {judul}")
        title_label.setFont(QFont("Arial", 14, QFont.Weight.Bold))
        title_label.setStyleSheet("color: #1976D2; padding: 10px 0px;")
        main_layout.addWidget(title_label)
        
        # ===== SEPARATOR LINE =====
        separator = QLabel("─" * 80)
        separator.setStyleSheet("color: #E0E0E0;")
        main_layout.addWidget(separator)
        
        # ===== TEXT AREA FOR CONTENT =====
        text_edit = QTextEdit()
        text_edit.setReadOnly(True)
        text_edit.setStyleSheet("""
            QTextEdit {
                background-color: #FAFAFA;
                border: 1px solid #E0E0E0;
                border-radius: 5px;
                padding: 15px;
                font-family: 'Courier New', monospace;
                font-size: 10px;
                line-height: 1.6;
            }
        """)
        
        # Build detail content as HTML
        html_content = self._build_detail_html()
        text_edit.setHtml(html_content)
        
        main_layout.addWidget(text_edit)
        
        # ===== BUTTON SECTION =====
        button_layout = QHBoxLayout()
        button_layout.addStretch()
        
        # Close button
        btn_close = QPushButton("✅ Tutup")
        btn_close.setStyleSheet("""
            QPushButton {
                background-color: #2196F3;
                color: white;
                border: none;
                border-radius: 5px;
                padding: 10px 30px;
                font-weight: bold;
                font-size: 11px;
            }
            QPushButton:hover { background-color: #0b7dda; }
            QPushButton:pressed { background-color: #0966cc; }
        """)
        btn_close.clicked.connect(self.accept)
        button_layout.addWidget(btn_close)
        
        main_layout.addLayout(button_layout)
        
        self.setLayout(main_layout)
        logger.debug(f"✅ BeasiswaDetailDialog UI initialized for: {judul}")
    
    def _build_detail_html(self) -> str:
        """
        Build HTML content for detail display (Task 27).
        Format: Bold label: value with proper line breaks
        
        Returns:
            str: HTML formatted content with all beasiswa fields
        """
        try:
            html_parts = [
                "<div style='font-family: Arial, sans-serif; line-height: 1.8;'>"
            ]
            
            # Required fields
            judul = self.beasiswa_data.get('judul', 'N/A')
            html_parts.append(f"<p><b>Judul Beasiswa:</b><br/>{judul}</p>")
            
            jenjang = self.beasiswa_data.get('jenjang', 'N/A')
            html_parts.append(f"<p><b>Jenjang Pendidikan:</b><br/>{jenjang}</p>")
            
            deadline = self.beasiswa_data.get('deadline', 'N/A')
            html_parts.append(f"<p><b>Deadline Pendaftaran:</b><br/>{deadline}</p>")
            
            status = self.beasiswa_data.get('status', 'N/A')
            html_parts.append(f"<p><b>Status Beasiswa:</b><br/>{status}</p>")
            
            # Optional fields - only show if not empty
            penyelenggara = self.beasiswa_data.get('penyelenggara_name')
            if not penyelenggara:
                penyelenggara_id = self.beasiswa_data.get('penyelenggara_id')
                if penyelenggara_id:
                    penyelenggara = f"ID: {penyelenggara_id}"
            if penyelenggara:
                html_parts.append(f"<p><b>Penyelenggara:</b><br/>{penyelenggara}</p>")
            
            minimal_ipk = self.beasiswa_data.get('minimal_ipk')
            if minimal_ipk:
                html_parts.append(f"<p><b>Minimal IPK:</b><br/>{minimal_ipk}</p>")
            
            coverage = self.beasiswa_data.get('coverage')
            if coverage:
                html_parts.append(f"<p><b>Coverage Beasiswa:</b><br/>{coverage}</p>")
            
            deskripsi = self.beasiswa_data.get('deskripsi')
            if deskripsi and deskripsi.strip():
                html_parts.append(f"<p><b>Deskripsi:</b><br/>{deskripsi}</p>")
            
            benefit = self.beasiswa_data.get('benefit')
            if benefit and benefit.strip():
                html_parts.append(f"<p><b>Benefit/Keuntungan:</b><br/>{benefit}</p>")
            
            persyaratan = self.beasiswa_data.get('persyaratan')
            if persyaratan and persyaratan.strip():
                html_parts.append(f"<p><b>Persyaratan & Ketentuan:</b><br/>{persyaratan}</p>")
            
            link_aplikasi = self.beasiswa_data.get('link_aplikasi')
            if link_aplikasi and link_aplikasi.strip():
                html_parts.append(f"<p><b>Link Aplikasi:</b><br/><a href='{link_aplikasi}' style='color: #1976D2;'>{link_aplikasi}</a></p>")
            
            html_parts.append("</div>")
            
            return "".join(html_parts)
            
        except Exception as e:
            logger.error(f"❌ Error building detail HTML: {e}")
            return f"<p style='color: red;'>Error loading detail: {str(e)}</p>"
