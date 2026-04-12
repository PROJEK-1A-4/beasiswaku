"""
Tracker Lamaran (Application Tracker) Tab for BeasiswaKu
Track scholarship applications with status updates and timeline
"""

import logging
from typing import Optional, List, Dict, Any
from datetime import datetime

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QTableWidget,
    QTableWidgetItem, QHeaderView, QPushButton, QLineEdit, QComboBox,
    QDialog, QFormLayout, QTextEdit, QMessageBox, QFrame
)
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QFont, QColor

from src.gui.design_tokens import *
from src.gui.styles import get_button_solid_stylesheet
from src.gui.components import create_status_badge
from src.database.crud import get_connection

logger = logging.getLogger(__name__)


class TrackerTab(QWidget):
    """
    Tracker Lamaran (Application Tracker) Tab - Track scholarship applications.
    
    Features:
    - Table dengan columns: Nama Beasiswa, Tanggal Daftar, Status, Catatan, Aksi
    - Status tracking: Pending (blue), Diterima (green), Ditolak (red)
    - Action buttons: Edit, Delete icons
    - "Tambah Lamaran" button untuk add new applications
    - Search/filter functionality
    - Real-time status updates
    - Database integration dengan riwayat_lamaran table
    
    Layout:
    ┌─────────────────────────────────────────┐
    │ Tracker Lamaran                          │
    │ Riwayat Lamaranku          [+ Tambah]   │
    ├─────────────────────────────────────────┤
    │ NO │ NAMA BEASISWA│ TGL DAFTAR│STATUS│AKSI
    ├─────────────────────────────────────────┤
    │ 1  │ Beasiswa LPDP│ 10 Mar   │Pending│✏️🗑️
    │ 2  │ Beasiswa BCA │ 15 Feb   │Diterima│✏️🗑️
    │ 3  │ Beasiswa OSC │ 25 Mei   │Ditolak │✏️🗑️
    └─────────────────────────────────────────┘
    """
    
    def __init__(self, user_id: int, parent=None):
        super().__init__(parent)
        self.user_id = user_id
        self.applications = []
        
        logger.info(f"Initializing TrackerTab for user {user_id}")
        self.init_ui()
        self.load_applications()
    
    def init_ui(self):
        """Initialize Tracker Tab UI."""
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(16, 16, 16, 16)  # SPACING_4
        main_layout.setSpacing(12)  # SPACING_3
        
        # ===== HEADER SECTION =====
        header_layout = QHBoxLayout()
        header_layout.setSpacing(12)
        
        # Title
        title_layout = QVBoxLayout()
        
        title_label = QLabel("Tracker Lamaran")
        title_font = QFont(FONT_FAMILY_PRIMARY, 20)
        title_font.setWeight(QFont.Weight.Bold)
        title_label.setFont(title_font)
        title_label.setStyleSheet(f"color: {COLOR_NAVY};")
        title_layout.addWidget(title_label)
        
        subtitle_label = QLabel("Riwayat Lamaranku")
        subtitle_label.setFont(QFont(FONT_FAMILY_PRIMARY, FONT_SIZE_BASE))
        subtitle_label.setStyleSheet(f"color: {COLOR_GRAY_600};")
        title_layout.addWidget(subtitle_label)
        
        header_layout.addLayout(title_layout)
        header_layout.addStretch()
        
        # "Tambah Lamaran" button
        tambah_btn = QPushButton("➕ Tambah Lamaran")
        tambah_btn.setStyleSheet(get_button_solid_stylesheet("orange"))
        tambah_btn.setMaximumWidth(140)
        tambah_btn.clicked.connect(self.on_tambah_lamaran)
        header_layout.addWidget(tambah_btn)
        
        main_layout.addLayout(header_layout)
        main_layout.addSpacing(8)  # SPACING_2
        
        # ===== TABLE SECTION =====
        self.table = QTableWidget()
        self.table.setColumnCount(5)
        self.table.setHorizontalHeaderLabels(["NO", "NAMA BEASISWA", "TANGGAL DAFTAR", "STATUS", "AKSI"])
        
        # Table styling
        header = self.table.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(1, QHeaderView.ResizeMode.Stretch)
        header.setSectionResizeMode(2, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(3, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(4, QHeaderView.ResizeMode.ResizeToContents)
        
        # Set row height
        self.table.verticalHeader().setDefaultSectionSize(36)  # 36px row height
        
        # Header styling
        header.setMinimumHeight(40)
        header.setDefaultAlignment(Qt.AlignmentFlag.AlignVCenter)
        
        # Apply stylesheet
        self.table.setStyleSheet(f"""
            QTableWidget {{
                background-color: {COLOR_WHITE};
                alternate-background-color: {COLOR_GRAY_50};
                gridline-color: {COLOR_GRAY_200};
                border: 1px solid {COLOR_GRAY_200};
                border-radius: {BORDER_RADIUS_SM};
            }}
            QTableWidget::item {{
                padding: 8px 10px;
            }}
            QHeaderView::section {{
                background-color: {COLOR_NAVY};
                color: {COLOR_WHITE};
                padding: 8px;
                border: none;
                font-weight: bold;
                font-size: 11px;
            }}
        """)
        
        self.table.setAlternatingRowColors(True)
        self.table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.table.setSelectionMode(QTableWidget.SelectionMode.SingleSelection)
        
        main_layout.addWidget(self.table)
        
        # Apply background color
        self.setStyleSheet(f"background-color: {COLOR_GRAY_BACKGROUND};")
    
    def load_applications(self):
        """Load tracking data dari database."""
        try:
            conn = get_connection()
            cursor = conn.cursor()
            
            # Query applications untuk user ini
            cursor.execute("""
                SELECT 
                    rl.id,
                    b.judul,
                    rl.tanggal_daftar,
                    rl.status,
                    rl.catatan
                FROM riwayat_lamaran rl
                JOIN beasiswa b ON rl.beasiswa_id = b.id
                WHERE rl.user_id = ?
                ORDER BY rl.tanggal_daftar DESC
            """, (self.user_id,))
            
            results = cursor.fetchall()
            self.applications = results
            
            # Populate table
            self.table.setRowCount(len(results))
            
            for row, result in enumerate(results):
                lamaran_id, beasiswa_judul, tanggal_daftar, status, catatan = result
                
                # Column 0: NO
                no_item = QTableWidgetItem(str(row + 1))
                no_item.setFont(QFont(FONT_FAMILY_PRIMARY, FONT_SIZE_BASE))
                no_item.setForeground(QColor(COLOR_GRAY_700))
                self.table.setItem(row, 0, no_item)
                
                # Column 1: NAMA BEASISWA
                nama_item = QTableWidgetItem(beasiswa_judul)
                nama_font = QFont(FONT_FAMILY_PRIMARY, FONT_SIZE_BASE)
                nama_font.setWeight(QFont.Weight.Medium)
                nama_item.setFont(nama_font)
                nama_item.setForeground(QColor(COLOR_NAVY))
                self.table.setItem(row, 1, nama_item)
                
                # Column 2: TANGGAL DAFTAR
                if tanggal_daftar:
                    # Format tanggal
                    tanggal_obj = datetime.strptime(tanggal_daftar, "%Y-%m-%d")
                    tanggal_text = tanggal_obj.strftime("%d %b %Y")
                else:
                    tanggal_text = "-"
                
                tanggal_item = QTableWidgetItem(tanggal_text)
                tanggal_item.setFont(QFont(FONT_FAMILY_PRIMARY, FONT_SIZE_BASE))
                tanggal_item.setForeground(QColor(COLOR_GRAY_600))
                self.table.setItem(row, 2, tanggal_item)
                
                # Column 3: STATUS (dengan badge)
                status_widget = create_status_badge(
                    status=self._map_status_to_badge_type(status),
                    text=status or "Pending"
                )
                self.table.setCellWidget(row, 3, status_widget)
                
                # Column 4: AKSI (Edit + Delete buttons)
                aksi_layout = QHBoxLayout()
                aksi_layout.setContentsMargins(0, 0, 0, 0)
                aksi_layout.setSpacing(4)
                
                # Edit button
                edit_btn = QPushButton("✏️")
                edit_btn.setMaximumWidth(36)
                edit_btn.setMaximumHeight(36)
                edit_btn.setToolTip("Edit lamaran")
                edit_btn.setStyleSheet(f"""
                    QPushButton {{
                        background-color: transparent;
                        border: 1px solid {COLOR_NAVY};
                        color: {COLOR_NAVY};
                        border-radius: 4px;
                        font-size: 14px;
                        padding: 0px;
                    }}
                    QPushButton:hover {{
                        background-color: {COLOR_GRAY_50};
                    }}
                """)
                edit_btn.clicked.connect(lambda checked, lid=lamaran_id: self.on_edit_lamaran(lid))
                aksi_layout.addWidget(edit_btn)
                
                # Delete button
                delete_btn = QPushButton("🗑️")
                delete_btn.setMaximumWidth(36)
                delete_btn.setMaximumHeight(36)
                delete_btn.setToolTip("Hapus lamaran")
                delete_btn.setStyleSheet(f"""
                    QPushButton {{
                        background-color: transparent;
                        border: 1px solid {COLOR_ERROR};
                        color: {COLOR_ERROR};
                        border-radius: 4px;
                        font-size: 14px;
                        padding: 0px;
                    }}
                    QPushButton:hover {{
                        background-color: {COLOR_ERROR_LIGHT};
                    }}
                """)
                delete_btn.clicked.connect(lambda checked, lid=lamaran_id: self.on_delete_lamaran(lid))
                aksi_layout.addWidget(delete_btn)
                
                aksi_layout.addStretch()
                
                aksi_widget = QWidget()
                aksi_widget.setLayout(aksi_layout)
                self.table.setCellWidget(row, 4, aksi_widget)
            
            logger.info(f"Loaded {len(results)} applications untuk user {self.user_id}")
            
        except Exception as e:
            logger.error(f"Error loading applications: {e}")
            QMessageBox.critical(self, "Error", f"Gagal load data: {e}")
    
    def _map_status_to_badge_type(self, status: str) -> str:
        """Map status dari database ke badge type."""
        status_lower = (status or "").lower()
        
        if "diterima" in status_lower or "approved" in status_lower:
            return "approved"
        elif "tolak" in status_lower or "rejected" in status_lower:
            return "rejected"
        elif "proses" in status_lower or "pending" in status_lower:
            return "pending"
        else:
            return "pending"
    
    def on_tambah_lamaran(self):
        """Handle tambah lamaran button."""
        dialog = TambahLamaranDialog(self.user_id, self)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            self.load_applications()
            QMessageBox.information(self, "Sukses", "Lamaran berhasil ditambahkan!")
    
    def on_edit_lamaran(self, lamaran_id: int):
        """Handle edit lamaran."""
        dialog = EditLamaranDialog(lamaran_id, self.user_id, self)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            self.load_applications()
            QMessageBox.information(self, "Sukses", "Lamaran berhasil diperbarui!")
    
    def on_delete_lamaran(self, lamaran_id: int):
        """Handle delete lamaran."""
        reply = QMessageBox.question(
            self,
            "Konfirmasi Hapus",
            "Anda yakin ingin menghapus lamaran ini?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        
        if reply == QMessageBox.StandardButton.Yes:
            try:
                conn = get_connection()
                cursor = conn.cursor()
                cursor.execute("DELETE FROM riwayat_lamaran WHERE id = ? AND user_id = ?", 
                             (lamaran_id, self.user_id))
                conn.commit()
                
                self.load_applications()
                QMessageBox.information(self, "Sukses", "Lamaran berhasil dihapus!")
                logger.info(f"Deleted lamaran {lamaran_id}")
                
            except Exception as e:
                logger.error(f"Error deleting lamaran: {e}")
                QMessageBox.critical(self, "Error", f"Gagal hapus: {e}")


class TambahLamaranDialog(QDialog):
    """Dialog untuk tambah lamaran baru."""
    
    def __init__(self, user_id: int, parent=None):
        super().__init__(parent)
        self.user_id = user_id
        self.setWindowTitle("Tambah Lamaran")
        self.setGeometry(150, 150, 500, 400)
        self.setModal(True)
        self.init_ui()
    
    def init_ui(self):
        """Initialize dialog UI."""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(12)
        
        # Title
        title = QLabel("Tambah Lamaran Baru")
        title_font = QFont(FONT_FAMILY_PRIMARY, 14)
        title_font.setWeight(QFont.Weight.Bold)
        title.setFont(title_font)
        title.setStyleSheet(f"color: {COLOR_NAVY};")
        layout.addWidget(title)
        
        # Form layout
        form = QFormLayout()
        form.setSpacing(12)
        
        # Beasiswa selection
        self.beasiswa_combo = QComboBox()
        self.beasiswa_combo.setMinimumHeight(36)
        self._load_beasiswa_options()
        form.addRow("Beasiswa:", self.beasiswa_combo)
        
        # Tanggal daftar
        self.tanggal_input = QLineEdit()
        self.tanggal_input.setPlaceholderText("YYYY-MM-DD")
        self.tanggal_input.setMinimumHeight(36)
        form.addRow("Tanggal Daftar:", self.tanggal_input)
        
        # Status
        self.status_combo = QComboBox()
        self.status_combo.addItems(["Pending", "Proses", "Diterima", "Ditolak"])
        self.status_combo.setMinimumHeight(36)
        form.addRow("Status:", self.status_combo)
        
        # Catatan
        self.catatan_input = QTextEdit()
        self.catatan_input.setPlaceholderText("Catatan tambahan (opsional)...")
        self.catatan_input.setMinimumHeight(80)
        form.addRow("Catatan:", self.catatan_input)
        
        layout.addLayout(form)
        
        # Buttons
        button_layout = QHBoxLayout()
        
        simpan_btn = QPushButton("✅ Simpan")
        simpan_btn.setStyleSheet(get_button_solid_stylesheet("navy"))
        simpan_btn.clicked.connect(self.on_simpan)
        button_layout.addWidget(simpan_btn)
        
        batal_btn = QPushButton("❌ Batal")
        batal_btn.setStyleSheet(get_button_solid_stylesheet("gray"))
        batal_btn.clicked.connect(self.reject)
        button_layout.addWidget(batal_btn)
        
        layout.addLayout(button_layout)
        layout.addStretch()
    
    def _load_beasiswa_options(self):
        """Load beasiswa options into combo."""
        try:
            conn = get_connection()
            cursor = conn.cursor()
            cursor.execute("SELECT id, judul FROM beasiswa ORDER BY judul")
            
            results = cursor.fetchall()
            for beasiswa_id, judul in results:
                self.beasiswa_combo.addItem(judul, beasiswa_id)
            
        except Exception as e:
            logger.error(f"Error loading beasiswa: {e}")
    
    def on_simpan(self):
        """Save lamaran baru."""
        beasiswa_id = self.beasiswa_combo.currentData()
        tanggal = self.tanggal_input.text().strip()
        status = self.status_combo.currentText()
        catatan = self.catatan_input.toPlainText().strip()
        
        if not beasiswa_id or not tanggal:
            QMessageBox.warning(self, "Validasi", "Beasiswa dan Tanggal harus diisi!")
            return
        
        try:
            conn = get_connection()
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO riwayat_lamaran (user_id, beasiswa_id, tanggal_daftar, status, catatan)
                VALUES (?, ?, ?, ?, ?)
            """, (self.user_id, beasiswa_id, tanggal, status, catatan))
            conn.commit()
            
            logger.info(f"Created lamaran untuk beasiswa {beasiswa_id}")
            self.accept()
            
        except Exception as e:
            logger.error(f"Error creating lamaran: {e}")
            QMessageBox.critical(self, "Error", f"Gagal simpan: {e}")


class EditLamaranDialog(QDialog):
    """Dialog untuk edit lamaran."""
    
    def __init__(self, lamaran_id: int, user_id: int, parent=None):
        super().__init__(parent)
        self.lamaran_id = lamaran_id
        self.user_id = user_id
        self.setWindowTitle("Edit Lamaran")
        self.setGeometry(150, 150, 500, 400)
        self.setModal(True)
        self.init_ui()
        self.load_data()
    
    def init_ui(self):
        """Initialize dialog UI."""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(12)
        
        # Title
        title = QLabel("Edit Lamaran")
        title_font = QFont(FONT_FAMILY_PRIMARY, 14)
        title_font.setWeight(QFont.Weight.Bold)
        title.setFont(title_font)
        title.setStyleSheet(f"color: {COLOR_NAVY};")
        layout.addWidget(title)
        
        # Form layout
        form = QFormLayout()
        form.setSpacing(12)
        
        # Beasiswa (read-only)
        self.beasiswa_label = QLabel()
        form.addRow("Beasiswa:", self.beasiswa_label)
        
        # Tanggal daftar
        self.tanggal_input = QLineEdit()
        self.tanggal_input.setMinimumHeight(36)
        form.addRow("Tanggal Daftar:", self.tanggal_input)
        
        # Status
        self.status_combo = QComboBox()
        self.status_combo.addItems(["Pending", "Proses", "Diterima", "Ditolak"])
        self.status_combo.setMinimumHeight(36)
        form.addRow("Status:", self.status_combo)
        
        # Catatan
        self.catatan_input = QTextEdit()
        self.catatan_input.setMinimumHeight(80)
        form.addRow("Catatan:", self.catatan_input)
        
        layout.addLayout(form)
        
        # Buttons
        button_layout = QHBoxLayout()
        
        simpan_btn = QPushButton("✅ Simpan")
        simpan_btn.setStyleSheet(get_button_solid_stylesheet("navy"))
        simpan_btn.clicked.connect(self.on_simpan)
        button_layout.addWidget(simpan_btn)
        
        batal_btn = QPushButton("❌ Batal")
        batal_btn.setStyleSheet(get_button_solid_stylesheet("gray"))
        batal_btn.clicked.connect(self.reject)
        button_layout.addWidget(batal_btn)
        
        layout.addLayout(button_layout)
        layout.addStretch()
    
    def load_data(self):
        """Load lamaran data."""
        try:
            conn = get_connection()
            cursor = conn.cursor()
            cursor.execute("""
                SELECT b.judul, rl.tanggal_daftar, rl.status, rl.catatan
                FROM riwayat_lamaran rl
                JOIN beasiswa b ON rl.beasiswa_id = b.id
                WHERE rl.id = ? AND rl.user_id = ?
            """, (self.lamaran_id, self.user_id))
            
            result = cursor.fetchone()
            if result:
                beasiswa_judul, tanggal, status, catatan = result
                self.beasiswa_label.setText(beasiswa_judul)
                self.tanggal_input.setText(tanggal or "")
                self.status_combo.setCurrentText(status or "Pending")
                self.catatan_input.setText(catatan or "")
            
        except Exception as e:
            logger.error(f"Error loading lamaran data: {e}")
    
    def on_simpan(self):
        """Save changes."""
        tanggal = self.tanggal_input.text().strip()
        status = self.status_combo.currentText()
        catatan = self.catatan_input.toPlainText().strip()
        
        try:
            conn = get_connection()
            cursor = conn.cursor()
            cursor.execute("""
                UPDATE riwayat_lamaran 
                SET tanggal_daftar = ?, status = ?, catatan = ?
                WHERE id = ? AND user_id = ?
            """, (tanggal, status, catatan, self.lamaran_id, self.user_id))
            conn.commit()
            
            logger.info(f"Updated lamaran {self.lamaran_id}")
            self.accept()
            
        except Exception as e:
            logger.error(f"Error updating lamaran: {e}")
            QMessageBox.critical(self, "Error", f"Gagal simpan: {e}")
