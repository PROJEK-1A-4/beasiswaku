"""
gui_notes.py - Catatan Pribadi (Personal Notes) untuk BeasiswaKu
Menyediakan UI components dan helper functions untuk notes per beasiswa

Komponen:
1. Notes editor dialog
2. Notes display widget
3. Notes list view
4. Quick notes toggle
"""

import logging
from typing import Optional, Tuple

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QTextEdit, QDialog,
    QLabel, QMessageBox, QTableWidget, QTableWidgetItem, QHeaderView,
    QDialogButtonBox
)
from PyQt6.QtCore import Qt, pyqtSignal, Qt as QtCore
from PyQt6.QtGui import QFont, QColor, QIcon

from src.database.crud import add_catatan, get_catatan, edit_catatan, delete_catatan, get_catatan_list

logger = logging.getLogger(__name__)


# ==================== NOTES UTILITY FUNCTIONS ====================

def has_note(user_id: int, beasiswa_id: int) -> bool:
    """
    Check apakah beasiswa memiliki catatan dari user.
    
    Args:
        user_id (int): ID user
        beasiswa_id (int): ID beasiswa
    
    Returns:
        bool: True jika ada catatan, False jika tidak
    """
    try:
        note, _ = get_catatan(user_id=user_id, beasiswa_id=beasiswa_id)
        return note is not None
    except:
        return False


def get_note_preview(user_id: int, beasiswa_id: int, max_length: int = 50) -> str:
    """
    Get preview dari catatan (dipotong untuk display).
    
    Args:
        user_id (int): ID user
        beasiswa_id (int): ID beasiswa
        max_length (int): Maksimal karakter yang ditampilkan
    
    Returns:
        str: Preview text atau empty string jika tidak ada catatan
    
    Example:
        >>> preview = get_note_preview(user_id=1, beasiswa_id=5)
        >>> print(f"📝 {preview}...")
    """
    try:
        note_dict, _ = get_catatan(user_id=user_id, beasiswa_id=beasiswa_id)
        if note_dict:
            content = note_dict.get('content', '')
            if len(content) > max_length:
                return content[:max_length] + "..."
            return content
        return ""
    except:
        return ""


def note_status_icon(user_id: int, beasiswa_id: int) -> str:
    """
    Get icon untuk note status.
    
    Args:
        user_id (int): ID user
        beasiswa_id (int): ID beasiswa
    
    Returns:
        str: "📝" jika ada catatan, "📄" jika tidak
    """
    return "📝" if has_note(user_id, beasiswa_id) else "📄"


# ==================== NOTES EDITOR DIALOG ====================

class NotesEditorDialog(QDialog):
    """
    Dialog untuk edit/create catatan untuk beasiswa tertentu.
    
    Features:
    - Text editor dengan validasi
    - Character counter
    - Save/Cancel buttons
    """
    
    notes_saved = pyqtSignal(bool)  # True means baru di-save/update
    
    def __init__(self, user_id: int, beasiswa_id: int, beasiswa_judul: str, parent=None):
        super().__init__(parent)
        self.user_id = user_id
        self.beasiswa_id = beasiswa_id
        self.beasiswa_judul = beasiswa_judul
        self.is_new = True  # Whether this is a new note
        
        self.setWindowTitle(f"📝 Catatan - {beasiswa_judul}")
        self.setGeometry(100, 100, 600, 400)
        
        self.init_ui()
        self.load_existing_note()
        
    def init_ui(self):
        """Initialize dialog UI"""
        layout = QVBoxLayout()
        
        # Title
        title = QLabel(f"Catatan Pribadi: {self.beasiswa_judul}")
        title.setFont(QFont("Arial", 11, QFont.Weight.Bold))
        layout.addWidget(title)
        
        # Text editor
        self.editor = QTextEdit()
        self.editor.setPlaceholderText(
            "Tulis catatan pribadi Anda untuk beasiswa ini...\n"
            "Contoh: Strategi lamaran, persiapan dokumen, deadlines, dll"
        )
        self.editor.setMinimumHeight(250)
        self.editor.textChanged.connect(self.on_text_changed)
        layout.addWidget(self.editor)
        
        # Character counter
        counter_layout = QHBoxLayout()
        counter_layout.addStretch()
        self.counter_label = QLabel("0/2000")
        self.counter_label.setStyleSheet("color: #666; font-size: 10px;")
        counter_layout.addWidget(self.counter_label)
        layout.addLayout(counter_layout)
        
        # Buttons
        button_layout = QHBoxLayout()
        
        # Delete button (only if note exists)
        self.delete_btn = QPushButton("🗑️ Hapus")
        self.delete_btn.setMaximumWidth(100)
        self.delete_btn.setStyleSheet("""
            QPushButton {
                background-color: #ff6b6b;
                color: white;
                border: none;
                border-radius: 3px;
                padding: 5px;
            }
            QPushButton:hover {
                background-color: #ff5252;
            }
            QPushButton:disabled {
                background-color: #cccccc;
                color: #666;
            }
        """)
        self.delete_btn.clicked.connect(self.on_delete)
        button_layout.addWidget(self.delete_btn)
        
        button_layout.addStretch()
        
        # Cancel button
        cancel_btn = QPushButton("❌ Batal")
        cancel_btn.setMaximumWidth(100)
        cancel_btn.clicked.connect(self.reject)
        button_layout.addWidget(cancel_btn)
        
        # Save button
        self.save_btn = QPushButton("💾 Simpan")
        self.save_btn.setMaximumWidth(100)
        self.save_btn.setStyleSheet("""
            QPushButton {
                background-color: #51cf66;
                color: white;
                border: none;
                border-radius: 3px;
                padding: 5px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #40c057;
            }
            QPushButton:disabled {
                background-color: #cccccc;
                color: #666;
            }
        """)
        self.save_btn.clicked.connect(self.on_save)
        button_layout.addWidget(self.save_btn)
        
        layout.addLayout(button_layout)
        
        self.setLayout(layout)
    
    def load_existing_note(self):
        """Load existing note jika ada"""
        note_dict, _ = get_catatan(self.user_id, self.beasiswa_id)
        
        if note_dict:
            self.editor.setText(note_dict['content'])
            self.is_new = False
            self.delete_btn.setEnabled(True)
        else:
            self.is_new = True
            self.delete_btn.setEnabled(False)
    
    def on_text_changed(self):
        """Handle text changed"""
        text = self.editor.toPlainText()
        length = len(text)
        
        # Update counter
        self.counter_label.setText(f"{length}/2000")
        
        # Color warning jika terlalu panjang
        if length >= 1900:
            self.counter_label.setStyleSheet("color: #ff6b6b; font-size: 10px; font-weight: bold;")
        elif length >= 1800:
            self.counter_label.setStyleSheet("color: #ffb74d; font-size: 10px;")
        else:
            self.counter_label.setStyleSheet("color: #666; font-size: 10px;")
        
        # Disable save jika kosong
        self.save_btn.setEnabled(length > 0)
    
    def on_save(self):
        """Handle save button"""
        content = self.editor.toPlainText().strip()
        
        if not content:
            QMessageBox.warning(self, "Validation", "Catatan tidak boleh kosong")
            return
        
        if len(content) > 2000:
            QMessageBox.warning(self, "Validation", "Catatan maksimal 2000 karakter")
            return
        
        try:
            if self.is_new:
                # Add new note
                success, msg, _ = add_catatan(
                    user_id=self.user_id,
                    beasiswa_id=self.beasiswa_id,
                    content=content
                )
            else:
                # Edit existing note
                success, msg = edit_catatan(
                    user_id=self.user_id,
                    beasiswa_id=self.beasiswa_id,
                    content=content
                )
            
            if success:
                logger.info(f"✅ Notes saved: {msg}")
                self.notes_saved.emit(True)
                QMessageBox.information(self, "Success", "✅ Catatan berhasil disimpan")
                self.accept()
            else:
                logger.error(f"❌ Save failed: {msg}")
                QMessageBox.warning(self, "Error", f"❌ {msg}")
        
        except Exception as e:
            logger.error(f"❌ Error saving notes: {e}")
            QMessageBox.critical(self, "Error", f"Error: {str(e)}")
    
    def on_delete(self):
        """Handle delete button"""
        reply = QMessageBox.question(
            self,
            "Konfirmasi",
            "Hapus catatan ini? Tindakan tidak bisa dibatalkan.",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        
        if reply == QMessageBox.StandardButton.Yes:
            try:
                success, msg = delete_catatan(
                    user_id=self.user_id,
                    beasiswa_id=self.beasiswa_id
                )
                
                if success:
                    logger.info(f"✅ Notes deleted: {msg}")
                    self.notes_saved.emit(True)
                    QMessageBox.information(self, "Success", "✅ Catatan berhasil dihapus")
                    self.accept()
                else:
                    logger.error(f"❌ Delete failed: {msg}")
                    QMessageBox.warning(self, "Error", f"❌ {msg}")
            
            except Exception as e:
                logger.error(f"❌ Error deleting notes: {e}")
                QMessageBox.critical(self, "Error", f"Error: {str(e)}")


# ==================== QUICK NOTES BUTTON ====================

class QuickNotesButton(QPushButton):
    """
    Custom button untuk quick access edit notes per beasiswa.
    
    Signals:
        notes_clicked(): Emitted saat button diklik
    """
    
    notes_clicked = pyqtSignal()
    
    def __init__(self, user_id: int, beasiswa_id: int, beasiswa_judul: str):
        super().__init__()
        self.user_id = user_id
        self.beasiswa_id = beasiswa_id
        self.beasiswa_judul = beasiswa_judul
        
        self.init_ui()
        self.update_appearance()
        
    def init_ui(self):
        """Initialize button UI"""
        self.setMaximumWidth(60)
        self.setMaximumHeight(40)
        self.setFont(QFont("Arial", 10))
        self.clicked.connect(self.on_click)
        
    def update_appearance(self):
        """Update button appearance based on note status"""
        has_note = has_note(self.user_id, self.beasiswa_id)
        
        if has_note:
            self.setText("📝")
            self.setStyleSheet("""
                QPushButton {
                    background-color: #e3f2fd;
                    border: 2px solid #2196F3;
                    border-radius: 5px;
                    font-size: 14px;
                }
                QPushButton:hover {
                    background-color: #bbdefb;
                }
            """)
            self.setToolTip("Ada catatan - Klik untuk edit")
        else:
            self.setText("📄")
            self.setStyleSheet("""
                QPushButton {
                    background-color: #f5f5f5;
                    border: 2px solid #cccccc;
                    border-radius: 5px;
                    font-size: 14px;
                }
                QPushButton:hover {
                    background-color: #e8e8e8;
                    border: 2px solid #888;
                }
            """)
            self.setToolTip("Tidak ada catatan - Klik untuk tambah")
    
    def on_click(self):
        """Handle button click"""
        dialog = NotesEditorDialog(
            user_id=self.user_id,
            beasiswa_id=self.beasiswa_id,
            beasiswa_judul=self.beasiswa_judul
        )
        
        if dialog.exec() == QDialog.DialogCode.Accepted:
            self.update_appearance()
            self.notes_clicked.emit()


# ==================== NOTES LIST VIEW ====================

class NotesListView(QWidget):
    """
    Widget untuk menampilkan dan manage daftar semua catatan user.
    
    Features:
    - Table view dengan all notes
    - Search/filter functionality
    - Quick edit buttons
    """
    
    notes_updated = pyqtSignal()  # Emit when notes are modified
    
    def __init__(self, user_id: int):
        super().__init__()
        self.user_id = user_id
        self.notes_list = []
        
        self.init_ui()
        self.load_notes()
        
    def init_ui(self):
        """Initialize UI"""
        layout = QVBoxLayout()
        
        # Title
        title = QLabel("📝 Catatan Pribadi Saya")
        title.setFont(QFont("Arial", 12, QFont.Weight.Bold))
        layout.addWidget(title)
        
        # Table
        self.table = QTableWidget()
        self.table.setColumnCount(5)
        self.table.setHorizontalHeaderLabels([
            "No.", "Beasiswa", "Jenjang", "Catatan Preview", "Aksi"
        ])
        
        # Configure table
        header = self.table.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(1, QHeaderView.ResizeMode.Stretch)
        header.setSectionResizeMode(2, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(3, QHeaderView.ResizeMode.Stretch)
        header.setSectionResizeMode(4, QHeaderView.ResizeMode.ResizeToContents)
        
        self.table.setStyleSheet("""
            QTableWidget {
                gridline-color: #e0e0e0;
                background-color: #ffffff;
            }
            QTableWidget::item {
                padding: 5px;
            }
            QHeaderView::section {
                background-color: #f5f5f5;
                padding: 5px;
                border: 1px solid #d0d0d0;
            }
        """)
        
        layout.addWidget(self.table)
        
        # Info label
        self.info_label = QLabel("")
        self.info_label.setStyleSheet("color: #666; font-size: 10px;")
        layout.addWidget(self.info_label)
        
        self.setLayout(layout)
    
    def load_notes(self):
        """Load notes from database"""
        try:
            self.notes_list, total = get_catatan_list(user_id=self.user_id)
            self.update_table()
            self.info_label.setText(f"Total {total} catatan")
            logger.info(f"✅ Loaded {total} catatan for user {self.user_id}")
        except Exception as e:
            logger.error(f"❌ Error loading notes: {e}")
            QMessageBox.critical(self, "Error", f"Gagal memuat catatan: {e}")
    
    def update_table(self):
        """Update table dengan current notes"""
        self.table.setRowCount(0)
        
        for idx, note in enumerate(self.notes_list, 1):
            row = self.table.rowCount()
            self.table.insertRow(row)
            
            # No.
            no_item = QTableWidgetItem(str(idx))
            no_item.setFlags(no_item.flags() & ~Qt.ItemFlag.ItemIsEditable)
            self.table.setItem(row, 0, no_item)
            
            # Beasiswa title
            judul_item = QTableWidgetItem(note.get('beasiswa_judul', ''))
            judul_item.setFlags(judul_item.flags() & ~Qt.ItemFlag.ItemIsEditable)
            self.table.setItem(row, 1, judul_item)
            
            # Jenjang
            jenjang_item = QTableWidgetItem(note.get('beasiswa_jenjang', ''))
            jenjang_item.setFlags(jenjang_item.flags() & ~Qt.ItemFlag.ItemIsEditable)
            self.table.setItem(row, 2, jenjang_item)
            
            # Notes preview
            content = note.get('content', '')
            preview = content[:50] + "..." if len(content) > 50 else content
            preview_item = QTableWidgetItem(preview)
            preview_item.setFlags(preview_item.flags() & ~Qt.ItemFlag.ItemIsEditable)
            self.table.setItem(row, 3, preview_item)
            
            # Edit button
            edit_btn = QPushButton("✏️ Edit")
            edit_btn.setMaximumWidth(80)
            edit_btn.setStyleSheet("""
                QPushButton {
                    background-color: #2196F3;
                    color: white;
                    border: none;
                    border-radius: 3px;
                    padding: 3px;
                    font-size: 10px;
                }
                QPushButton:hover {
                    background-color: #1976D2;
                }
            """)
            
            beasiswa_id = note.get('beasiswa_id')
            judul = note.get('beasiswa_judul')
            edit_btn.clicked.connect(
                lambda checked, bid=beasiswa_id, btitle=judul: self.on_edit_note(bid, btitle)
            )
            
            self.table.setCellWidget(row, 4, edit_btn)
    
    def on_edit_note(self, beasiswa_id: int, beasiswa_judul: str):
        """Handle edit button click"""
        dialog = NotesEditorDialog(
            user_id=self.user_id,
            beasiswa_id=beasiswa_id,
            beasiswa_judul=beasiswa_judul,
            parent=self
        )
        
        if dialog.exec() == QDialog.DialogCode.Accepted:
            self.load_notes()
            self.notes_updated.emit()
    
    def refresh(self):
        """Refresh notes list"""
        self.load_notes()


if __name__ == "__main__":
    # Test notes utilities
    print("Notes GUI module loaded successfully")
