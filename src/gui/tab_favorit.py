"""
tab_favorit.py - Dedicated Tab untuk Favorit (Bookmark) Beasiswa
Menampilkan daftar beasiswa yang sudah di-bookmark user dengan management features

Komponen:
1. NotesDialog - Modal dialog untuk view/edit notes untuk beasiswa
2. FavoritTab - Tab utama untuk menampilkan daftar favorit dengan aksi
"""

import logging
from typing import List, Dict, Optional, Any
from datetime import date

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QTableWidget,
    QTableWidgetItem, QHeaderView, QMessageBox, QLabel, QLineEdit,
    QDialog, QTextEdit, QPlainTextEdit
)
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QFont, QColor

from src.database.crud import (
    get_favorit_list, delete_favorit, add_lamaran, 
    check_user_applied, get_catatan, add_catatan, 
    edit_catatan, delete_catatan
)
from src.gui.design_tokens import (
    COLOR_NAVY, COLOR_ORANGE, COLOR_SUCCESS, COLOR_ERROR,
    COLOR_WARNING, COLOR_GRAY_700, FONT_FAMILY_PRIMARY,
    BORDER_RADIUS_MD
)

logger = logging.getLogger(__name__)


# ==================== NOTES DIALOG ====================

class NotesDialog(QDialog):
    """
    Modal dialog untuk view/edit catatan untuk beasiswa tertentu.
    
    Features:
    - View existing notes atau tambah notes baru
    - Save dan delete notes functionality
    - Auto-close setelah save
    """
    
    notes_changed = pyqtSignal(int)  # Emit beasiswa_id saat notes berubah
    
    def __init__(self, user_id: int, beasiswa_id: int, beasiswa_title: str, parent=None):
        super().__init__(parent)
        self.user_id = user_id
        self.beasiswa_id = beasiswa_id
        self.beasiswa_title = beasiswa_title
        self.current_catatan_id = None
        
        self.setWindowTitle(f"📝 Catatan: {beasiswa_title}")
        self.setGeometry(100, 100, 500, 400)
        
        self.init_ui()
        self.load_notes()
    
    def init_ui(self):
        """Initialize dialog UI"""
        layout = QVBoxLayout()
        
        # Title
        title = QLabel(f"Catatan untuk: {self.beasiswa_title}")
        title.setFont(QFont(FONT_FAMILY_PRIMARY, 11, QFont.Weight.Bold))
        layout.addWidget(title)
        
        # Notes text editor
        self.notes_input = QPlainTextEdit()
        self.notes_input.setPlaceholderText("Tulis catatan Anda di sini...\n\nContoh:\n- Status lamaran\n- Persyaratan yang sudah dipenuhi\n- Follow-up plan")
        self.notes_input.setFont(QFont(FONT_FAMILY_PRIMARY, 10))
        layout.addWidget(self.notes_input)
        
        # Button layout
        button_layout = QHBoxLayout()
        
        self.save_btn = QPushButton("💾 Simpan")
        self.save_btn.setStyleSheet(f"""
            QPushButton {{
                background-color: {COLOR_SUCCESS};
                color: white;
                border: none;
                border-radius: {BORDER_RADIUS_MD};
                padding: 8px 16px;
                font-weight: bold;
            }}
            QPushButton:hover {{
                background-color: #0a9d6f;
            }}
        """)
        self.save_btn.clicked.connect(self.on_save)
        button_layout.addWidget(self.save_btn)
        
        self.delete_btn = QPushButton("🗑️ Hapus")
        self.delete_btn.setStyleSheet(f"""
            QPushButton {{
                background-color: {COLOR_ERROR};
                color: white;
                border: none;
                border-radius: {BORDER_RADIUS_MD};
                padding: 8px 16px;
                font-weight: bold;
            }}
            QPushButton:hover {{
                background-color: #dc2626;
            }}
        """)
        self.delete_btn.clicked.connect(self.on_delete)
        button_layout.addWidget(self.delete_btn)
        
        self.close_btn = QPushButton("✕ Tutup")
        self.close_btn.setStyleSheet(f"""
            QPushButton {{
                background-color: {COLOR_GRAY_700};
                color: white;
                border: none;
                border-radius: {BORDER_RADIUS_MD};
                padding: 8px 16px;
            }}
            QPushButton:hover {{
                background-color: #374151;
            }}
        """)
        self.close_btn.clicked.connect(self.close)
        button_layout.addWidget(self.close_btn)
        
        layout.addLayout(button_layout)
        self.setLayout(layout)
    
    def load_notes(self):
        """Load existing notes from database"""
        try:
            catatan_list, _ = get_catatan(user_id=self.user_id, beasiswa_id=self.beasiswa_id)
            
            if catatan_list:
                catatan = catatan_list[0]  # Get first (most recent) note
                self.current_catatan_id = catatan.get('catatan_id')
                self.notes_input.setPlainText(catatan.get('isi_catatan', ''))
                logger.info(f"✅ Loaded notes for beasiswa {self.beasiswa_id}")
            else:
                self.notes_input.setPlainText("")
                self.current_catatan_id = None
                
        except Exception as e:
            logger.error(f"❌ Error loading notes: {e}")
            QMessageBox.warning(self, "Error", f"Gagal memuat catatan: {e}")
    
    def on_save(self):
        """Save notes to database"""
        notes_text = self.notes_input.toPlainText().strip()
        
        if not notes_text:
            QMessageBox.warning(self, "Peringatan", "Catatan tidak boleh kosong!")
            return
        
        try:
            if self.current_catatan_id:
                # Update existing notes
                success, message = edit_catatan(
                    catatan_id=self.current_catatan_id,
                    isi_catatan=notes_text
                )
            else:
                # Add new notes
                success, message, catatan_id = add_catatan(
                    user_id=self.user_id,
                    beasiswa_id=self.beasiswa_id,
                    isi_catatan=notes_text
                )
                if success:
                    self.current_catatan_id = catatan_id
            
            if success:
                logger.info(f"✅ Notes saved for beasiswa {self.beasiswa_id}")
                self.notes_changed.emit(self.beasiswa_id)
                QMessageBox.information(self, "Sukses", "Catatan berhasil disimpan!")
                self.close()
            else:
                logger.error(f"❌ Failed to save notes: {message}")
                QMessageBox.warning(self, "Error", f"Gagal menyimpan catatan: {message}")
                
        except Exception as e:
            logger.error(f"❌ Error saving notes: {e}")
            QMessageBox.critical(self, "Error", f"Error: {str(e)}")
    
    def on_delete(self):
        """Delete notes from database"""
        if not self.current_catatan_id:
            QMessageBox.information(self, "Info", "Tidak ada catatan untuk dihapus")
            return
        
        reply = QMessageBox.question(
            self,
            "Konfirmasi",
            "Hapus catatan ini?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        
        if reply == QMessageBox.StandardButton.Yes:
            try:
                success, message = delete_catatan(catatan_id=self.current_catatan_id)
                
                if success:
                    logger.info(f"✅ Notes deleted for beasiswa {self.beasiswa_id}")
                    self.current_catatan_id = None
                    self.notes_input.setPlainText("")
                    self.notes_changed.emit(self.beasiswa_id)
                    QMessageBox.information(self, "Sukses", "Catatan berhasil dihapus!")
                    self.close()
                else:
                    logger.error(f"❌ Failed to delete notes: {message}")
                    QMessageBox.warning(self, "Error", f"Gagal menghapus catatan: {message}")
                    
            except Exception as e:
                logger.error(f"❌ Error deleting notes: {e}")
                QMessageBox.critical(self, "Error", f"Error: {str(e)}")


# ==================== FAVORIT TAB ====================

class FavoritTab(QWidget):
    """
    Tab utama untuk menampilkan daftar beasiswa yang di-bookmark user.
    
    Features:
    - Tabel daftar favorit dengan 6 kolom
    - Search/filter by nama beasiswa
    - Action buttons: Notes (📝), Remove (✕), Apply (Lamar)
    - Dynamic deadline coloring
    """
    
    favorit_updated = pyqtSignal()  # Emitted saat ada perubahan pada favorit
    
    def __init__(self, user_id: int):
        super().__init__()
        self.user_id = user_id
        self.favorit_data: List[Dict[str, Any]] = []
        
        self.init_ui()
        self.load_favorit_data()
    
    def init_ui(self):
        """Initialize tab UI"""
        layout = QVBoxLayout()
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(15)
        
        # Header
        header_layout = QHBoxLayout()
        title = QLabel("⭐ Beasiswa Favorit Saya")
        title.setFont(QFont(FONT_FAMILY_PRIMARY, 14, QFont.Weight.Bold))
        header_layout.addWidget(title)
        header_layout.addStretch()
        layout.addLayout(header_layout)
        
        # Search bar
        search_layout = QHBoxLayout()
        search_label = QLabel("🔍 Cari:")
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Cari berdasarkan nama beasiswa atau penyelenggara...")
        self.search_input.setMaximumWidth(300)
        self.search_input.textChanged.connect(self.filter_table)
        search_layout.addWidget(search_label)
        search_layout.addWidget(self.search_input)
        search_layout.addStretch()
        layout.addLayout(search_layout)
        
        # Table
        self.table = QTableWidget()
        self.table.setColumnCount(6)
        self.table.setHorizontalHeaderLabels([
            "NO", "NAMA BEASISWA", "PENYELENGGARA", "JENJANG", "DEADLINE", "AKSI"
        ])
        
        # Configure table header
        header = self.table.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(1, QHeaderView.ResizeMode.Stretch)
        header.setSectionResizeMode(2, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(3, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(4, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(5, QHeaderView.ResizeMode.ResizeToContents)
        
        header.setStyleSheet(f"""
            QHeaderView::section {{
                background-color: {COLOR_NAVY};
                color: white;
                padding: 8px;
                border: 1px solid #ccc;
                font-weight: bold;
            }}
        """)
        
        self.table.setStyleSheet(f"""
            QTableWidget {{
                gridline-color: #e0e0e0;
                background-color: white;
                border: 1px solid #ddd;
                border-radius: {BORDER_RADIUS_MD};
            }}
            QTableWidget::item {{
                padding: 8px;
                border-bottom: 1px solid #f0f0f0;
            }}
        """)
        
        self.table.setRowCount(0)
        layout.addWidget(self.table)
        
        # Info label
        self.info_label = QLabel("Memuat data...")
        self.info_label.setStyleSheet(f"color: {COLOR_GRAY_700}; font-size: 11px;")
        layout.addWidget(self.info_label)
        
        self.setLayout(layout)
    
    def load_favorit_data(self):
        """Load favorit data dari database"""
        try:
            self.favorit_data, total = get_favorit_list(user_id=self.user_id)
            self.populate_table(self.favorit_data)
            self.info_label.setText(f"Total {total} beasiswa di-favorit | Menampilkan semua")
            logger.info(f"✅ Loaded {total} favorit beasiswa for user {self.user_id}")
            
        except Exception as e:
            logger.error(f"❌ Error loading favorit data: {e}")
            self.info_label.setText(f"Error: {str(e)}")
            QMessageBox.critical(self, "Error", f"Gagal memuat daftar favorit: {e}")
    
    def populate_table(self, data: List[Dict[str, Any]]):
        """Populate table dengan favorit data"""
        self.table.setRowCount(0)
        
        for idx, beasiswa in enumerate(data, 1):
            row = self.table.rowCount()
            self.table.insertRow(row)
            
            # NO
            no_item = QTableWidgetItem(str(idx))
            no_item.setFlags(no_item.flags() & ~Qt.ItemFlag.ItemIsEditable)
            self.table.setItem(row, 0, no_item)
            
            # NAMA BEASISWA
            nama_item = QTableWidgetItem(beasiswa.get('judul', ''))
            nama_item.setFlags(nama_item.flags() & ~Qt.ItemFlag.ItemIsEditable)
            self.table.setItem(row, 1, nama_item)
            
            # PENYELENGGARA
            penyelenggara_item = QTableWidgetItem(beasiswa.get('penyelenggara', ''))
            penyelenggara_item.setFlags(penyelenggara_item.flags() & ~Qt.ItemFlag.ItemIsEditable)
            self.table.setItem(row, 2, penyelenggara_item)
            
            # JENJANG
            jenjang_item = QTableWidgetItem(beasiswa.get('jenjang', ''))
            jenjang_item.setFlags(jenjang_item.flags() & ~Qt.ItemFlag.ItemIsEditable)
            self.table.setItem(row, 3, jenjang_item)
            
            # DEADLINE dengan dynamic coloring
            deadline_str = beasiswa.get('deadline', '')
            days_remaining = self._get_days_until_deadline(deadline_str)
            deadline_color = self._get_deadline_color(days_remaining)
            
            if days_remaining is not None:
                deadline_display = f"{deadline_str} ({days_remaining} hari)"
            else:
                deadline_display = deadline_str
            
            deadline_item = QTableWidgetItem(deadline_display)
            deadline_item.setFlags(deadline_item.flags() & ~Qt.ItemFlag.ItemIsEditable)
            deadline_item.setForeground(QColor(deadline_color))
            deadline_item.setFont(QFont(FONT_FAMILY_PRIMARY, 9, QFont.Weight.Bold))
            self.table.setItem(row, 4, deadline_item)
            
            # AKSI buttons
            action_widget = QWidget()
            action_layout = QHBoxLayout()
            action_layout.setContentsMargins(2, 2, 2, 2)
            action_layout.setSpacing(5)
            
            beasiswa_id = beasiswa.get('beasiswa_id')
            beasiswa_title = beasiswa.get('judul', '')
            
            # Notes button
            notes_btn = QPushButton("📝")
            notes_btn.setMaximumWidth(35)
            notes_btn.setToolTip("Lihat/Edit catatan")
            notes_btn.setStyleSheet(f"""
                QPushButton {{
                    background-color: {COLOR_ORANGE};
                    color: white;
                    border: none;
                    border-radius: {BORDER_RADIUS_MD};
                    font-size: 12px;
                    padding: 4px;
                }}
                QPushButton:hover {{
                    background-color: #d97706;
                }}
            """)
            notes_btn.clicked.connect(
                lambda checked, bid=beasiswa_id, title=beasiswa_title: 
                self.open_notes(bid, title)
            )
            action_layout.addWidget(notes_btn)
            
            # Remove button
            remove_btn = QPushButton("✕")
            remove_btn.setMaximumWidth(35)
            remove_btn.setToolTip("Hapus dari favorit")
            remove_btn.setStyleSheet(f"""
                QPushButton {{
                    background-color: {COLOR_ERROR};
                    color: white;
                    border: none;
                    border-radius: {BORDER_RADIUS_MD};
                    font-size: 14px;
                    padding: 4px;
                }}
                QPushButton:hover {{
                    background-color: #dc2626;
                }}
            """)
            remove_btn.clicked.connect(
                lambda checked, bid=beasiswa_id: self.remove_favorit(bid)
            )
            action_layout.addWidget(remove_btn)
            
            # Apply button
            apply_btn = QPushButton("Lamar")
            apply_btn.setMaximumWidth(60)
            apply_btn.setToolTip("Lamar beasiswa ini")
            
            # Check if already applied
            already_applied = check_user_applied(
                user_id=self.user_id,
                beasiswa_id=beasiswa_id
            )
            
            if already_applied:
                apply_btn.setStyleSheet(f"""
                    QPushButton {{
                        background-color: {COLOR_SUCCESS};
                        color: white;
                        border: none;
                        border-radius: {BORDER_RADIUS_MD};
                        font-size: 10px;
                        padding: 4px;
                    }}
                """)
                apply_btn.setText("✓ Sudah")
                apply_btn.setEnabled(False)
            else:
                apply_btn.setStyleSheet(f"""
                    QPushButton {{
                        background-color: {COLOR_SUCCESS};
                        color: white;
                        border: none;
                        border-radius: {BORDER_RADIUS_MD};
                        font-size: 10px;
                        padding: 4px;
                    }}
                    QPushButton:hover {{
                        background-color: #059669;
                    }}
                """)
                apply_btn.clicked.connect(
                    lambda checked, bid=beasiswa_id: self.apply_scholarship(bid)
                )
            
            action_layout.addWidget(apply_btn)
            action_layout.addStretch()
            action_widget.setLayout(action_layout)
            
            self.table.setCellWidget(row, 5, action_widget)
    
    def _get_days_until_deadline(self, deadline_str: str) -> Optional[int]:
        """Calculate days remaining until deadline"""
        try:
            if not deadline_str:
                return None
            
            deadline_date = date.fromisoformat(deadline_str)
            today = date.today()
            days_remaining = (deadline_date - today).days
            return days_remaining if days_remaining >= 0 else 0
            
        except (ValueError, TypeError):
            return None
    
    def _get_deadline_color(self, days_remaining: Optional[int]) -> str:
        """Get color code based on days remaining"""
        if days_remaining is None:
            return COLOR_GRAY_700
        elif days_remaining <= 7:
            return COLOR_ERROR  # Red
        elif days_remaining <= 30:
            return COLOR_WARNING  # Yellow/Orange
        else:
            return COLOR_SUCCESS  # Green
    
    def filter_table(self):
        """Filter table berdasarkan search input"""
        search_term = self.search_input.text().lower()
        
        for row in range(self.table.rowCount()):
            nama_item = self.table.item(row, 1)
            penyelenggara_item = self.table.item(row, 2)
            
            nama_text = nama_item.text().lower() if nama_item else ""
            penyelenggara_text = penyelenggara_item.text().lower() if penyelenggara_item else ""
            
            should_show = search_term in nama_text or search_term in penyelenggara_text
            self.table.setRowHidden(row, not should_show)
    
    def open_notes(self, beasiswa_id: int, beasiswa_title: str):
        """Open notes dialog untuk beasiswa tertentu"""
        dialog = NotesDialog(self.user_id, beasiswa_id, beasiswa_title, parent=self)
        dialog.notes_changed.connect(lambda: self.load_favorit_data())
        dialog.exec()
    
    def remove_favorit(self, beasiswa_id: int):
        """Remove beasiswa dari favorit"""
        reply = QMessageBox.question(
            self,
            "Konfirmasi",
            "Hapus beasiswa dari favorit?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        
        if reply == QMessageBox.StandardButton.Yes:
            try:
                success, message = delete_favorit(
                    user_id=self.user_id,
                    beasiswa_id=beasiswa_id
                )
                
                if success:
                    logger.info(f"✅ Beasiswa {beasiswa_id} dihapus dari favorit")
                    self.favorit_updated.emit()
                    self.load_favorit_data()
                else:
                    logger.error(f"❌ Failed to remove favorit: {message}")
                    QMessageBox.warning(self, "Error", f"Gagal menghapus: {message}")
                    
            except Exception as e:
                logger.error(f"❌ Error removing favorit: {e}")
                QMessageBox.critical(self, "Error", f"Error: {str(e)}")
    
    def apply_scholarship(self, beasiswa_id: int):
        """Apply untuk beasiswa (create lamaran record)"""
        try:
            success, message, lamaran_id = add_lamaran(
                user_id=self.user_id,
                beasiswa_id=beasiswa_id
            )
            
            if success:
                logger.info(f"✅ Lamaran berhasil dibuat untuk beasiswa {beasiswa_id}")
                QMessageBox.information(self, "Sukses", "Lamaran berhasil dibuat!")
                self.load_favorit_data()  # Refresh table
            else:
                logger.error(f"❌ Failed to apply: {message}")
                QMessageBox.warning(self, "Error", f"Gagal membuat lamaran: {message}")
                
        except Exception as e:
            logger.error(f"❌ Error applying for scholarship: {e}")
            QMessageBox.critical(self, "Error", f"Error: {str(e)}")
    
    def refresh(self):
        """Refresh favorit data"""
        self.load_favorit_data()


if __name__ == "__main__":
    print("FavoritTab module loaded successfully")
