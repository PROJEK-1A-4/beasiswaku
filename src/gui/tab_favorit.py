"""
gui_favorit.py - Fitur Favorit (Bookmark) untuk BeasiswaKu
Menyediakan UI components dan helper functions untuk favorit functionality

Komponen:
1. Favorit toggle button (⭐)
2. Favorit list view
3. Utility functions untuk favorit management
"""

import logging
from typing import List, Dict, Tuple, Optional

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QTableWidget,
    QTableWidgetItem, QHeaderView, QMessageBox, QLabel, QLineEdit,
    QComboBox, QFrame, QDialog
)
from PyQt6.QtCore import Qt, pyqtSignal, QSize
from PyQt6.QtGui import QFont, QColor, QIcon

from src.database.crud import (
    add_favorit, delete_favorit, get_favorit_list,
    add_lamaran, check_user_applied
)

logger = logging.getLogger(__name__)


# ==================== FAVORIT UTILITY FUNCTIONS ====================

def toggle_favorit(user_id: int, beasiswa_id: int) -> Tuple[bool, str, bool]:
    """
    Toggle favorit status untuk beasiswa tertentu.
    
    Jika beasiswa sudah di-favorit, hapus. Jika belum, tambahkan.
    
    Args:
        user_id (int): ID user
        beasiswa_id (int): ID beasiswa
    
    Returns:
        Tuple[bool, str, bool]:
            - (True/False, "message", is_favorited)
            - is_favorited: True jika sekarang di-favorit, False jika belum
    
    Example:
        >>> success, msg, is_fav = toggle_favorit(user_id=1, beasiswa_id=5)
        >>> if success:
        ...     status = "⭐" if is_fav else "☆"
        ...     print(f"Favorit status: {status}")
    """
    if not user_id or not isinstance(user_id, int):
        return False, "User ID tidak valid", False
    
    if not beasiswa_id or not isinstance(beasiswa_id, int):
        return False, "Beasiswa ID tidak valid", False
    
    try:
        # Get current favorit list to check if exists
        favorit_list, _ = get_favorit_list(user_id=user_id)
        
        is_currently_favorited = any(f['beasiswa_id'] == beasiswa_id for f in favorit_list)
        
        if is_currently_favorited:
            # Remove from favorit
            success, msg = delete_favorit(user_id=user_id, beasiswa_id=beasiswa_id)
            if success:
                logger.info(f"✅ Beasiswa {beasiswa_id} dihapus dari favorit user {user_id}")
                return True, msg, False  # Now not favorited
            else:
                logger.error(f"❌ Gagal hapus favorit: {msg}")
                return False, msg, True  # Still favorited
        else:
            # Add to favorit
            success, msg, _ = add_favorit(user_id=user_id, beasiswa_id=beasiswa_id)
            if success:
                logger.info(f"✅ Beasiswa {beasiswa_id} ditambahkan ke favorit user {user_id}")
                return True, msg, True  # Now favorited
            else:
                logger.error(f"❌ Gagal tambah favorit: {msg}")
                return False, msg, False  # Still not favorited
        
    except Exception as e:
        logger.error(f"❌ Error saat toggle favorit: {e}")
        return False, f"Error: {str(e)}", False


def is_beasiswa_favorited(user_id: int, beasiswa_id: int) -> bool:
    """
    Check apakah beasiswa sudah di-favorit user.
    
    Args:
        user_id (int): ID user
        beasiswa_id (int): ID beasiswa
    
    Returns:
        bool: True jika favorited, False jika belum
    """
    if not user_id or not isinstance(user_id, int):
        return False
    
    try:
        favorit_list, _ = get_favorit_list(user_id=user_id)
        return any(f['beasiswa_id'] == beasiswa_id for f in favorit_list)
    except Exception as e:
        logger.warning(f"Failed to check favorite status - user_id: {user_id}, beasiswa_id: {beasiswa_id}. Error: {str(e)}")
        return False


def get_favorit_icon(is_favorited: bool) -> str:
    """
    Get icon string untuk favorit status.
    
    Args:
        is_favorited (bool): Apakah beasiswa di-favorit
    
    Returns:
        str: "⭐" jika favorited, "☆" jika belum
    """
    return "⭐" if is_favorited else "☆"


# ==================== FAVORIT BUTTON ====================

class FavoritButton(QPushButton):
    """
    Custom button untuk toggle favorit dengan visual feedback.
    
    Signals:
        favorit_toggled(bool): Emitted saat favorit status berubah
    """
    
    favorit_toggled = pyqtSignal(bool)  # True = now favorited, False = now unfavorited
    
    def __init__(self, user_id: int, beasiswa_id: int, initial_state: bool = False):
        super().__init__()
        self.user_id = user_id
        self.beasiswa_id = beasiswa_id
        self.is_favorited = initial_state
        
        self.init_ui()
        self.update_appearance()
        
    def init_ui(self):
        """Initialize button UI"""
        self.setMaximumWidth(50)
        self.setMaximumHeight(40)
        self.setFont(QFont("Arial", 12))
        self.clicked.connect(self.on_click)
        
    def update_appearance(self):
        """Update button appearance based on favorit status"""
        if self.is_favorited:
            self.setText("⭐")
            self.setStyleSheet("""
                QPushButton {
                    background-color: #FFD700;
                    border: 2px solid #FFA500;
                    border-radius: 5px;
                    font-size: 16px;
                }
                QPushButton:hover {
                    background-color: #FFC700;
                }
                QPushButton:pressed {
                    background-color: #FFB700;
                }
            """)
            self.setToolTip("Hapus dari favorit")
        else:
            self.setText("☆")
            self.setStyleSheet("""
                QPushButton {
                    background-color: #f0f0f0;
                    border: 2px solid #cccccc;
                    border-radius: 5px;
                    font-size: 16px;
                }
                QPushButton:hover {
                    background-color: #e8e8e8;
                    border: 2px solid #888;
                }
                QPushButton:pressed {
                    background-color: #d8d8d8;
                }
            """)
            self.setToolTip("Tambah ke favorit")
    
    def on_click(self):
        """Handle button click"""
        success, message, new_state = toggle_favorit(
            user_id=self.user_id,
            beasiswa_id=self.beasiswa_id
        )
        
        if success:
            self.is_favorited = new_state
            self.update_appearance()
            self.favorit_toggled.emit(new_state)
            logger.info(f"✅ Favorit toggled: {message}")
        else:
            QMessageBox.warning(
                self,
                "Error",
                f"❌ Gagal mengubah favorit: {message}"
            )
    
    def update_state(self, is_favorited: bool):
        """Update button state without triggering toggle"""
        self.is_favorited = is_favorited
        self.update_appearance()


# ==================== FAVORIT LIST VIEW ====================

class FavoritListView(QWidget):
    """
    Widget untuk menampilkan dan manage daftar favorit beasiswa.
    
    Features:
    - Tabel daftar favorit dengan sorting
    - Quick action untuk hapus favorit
    - Search/filter by judul
    """
    
    favorit_removed = pyqtSignal(int)  # Emit beasiswa_id saat dihapus
    
    def __init__(self, user_id: int):
        super().__init__()
        self.user_id = user_id
        self.favorit_list = []
        
        self.init_ui()
        self.load_favorit_list()
        
    def init_ui(self):
        """Initialize UI"""
        layout = QVBoxLayout()
        
        # Title
        title = QLabel("⭐ Daftar Favorit Saya")
        title.setFont(QFont("Arial", 12, QFont.Weight.Bold))
        layout.addWidget(title)
        
        # Search bar
        search_layout = QHBoxLayout()
        search_label = QLabel("🔍 Cari:")
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Cari berdasarkan judul beasiswa...")
        self.search_input.textChanged.connect(self.on_search_changed)
        search_layout.addWidget(search_label)
        search_layout.addWidget(self.search_input)
        layout.addLayout(search_layout)
        
        # Table
        self.table = QTableWidget()
        self.table.setColumnCount(6)
        self.table.setHorizontalHeaderLabels([
            "No.", "Judul Beasiswa", "Jenjang", "Deadline",
            "Status", "Aksi"
        ])
        
        # Configure table
        header = self.table.horizontalHeader()
        header.setSectionResizeMode(1, QHeaderView.ResizeMode.Stretch)
        header.setSectionResizeMode(2, QHeaderView.ResizeMode.ResizeToContents)
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
    
    def load_favorit_list(self):
        """Load favorit list from database"""
        try:
            self.favorit_list, total = get_favorit_list(user_id=self.user_id)
            self.update_table()
            self.info_label.setText(f"Total {total} beasiswa di-favorit")
            logger.info(f"✅ Loaded {total} favorit beasiswa for user {self.user_id}")
        except Exception as e:
            logger.error(f"❌ Error loading favorit list: {e}")
            QMessageBox.critical(self, "Error", f"Gagal memuat daftar favorit: {e}")
    
    def update_table(self):
        """Update table dengan current favorit list"""
        self.table.setRowCount(0)
        
        for idx, beasiswa in enumerate(self.favorit_list, 1):
            row = self.table.rowCount()
            self.table.insertRow(row)
            
            # No.
            no_item = QTableWidgetItem(str(idx))
            no_item.setFlags(no_item.flags() & ~Qt.ItemFlag.ItemIsEditable)
            self.table.setItem(row, 0, no_item)
            
            # Judul
            judul_item = QTableWidgetItem(beasiswa.get('judul', ''))
            judul_item.setFlags(judul_item.flags() & ~Qt.ItemFlag.ItemIsEditable)
            self.table.setItem(row, 1, judul_item)
            
            # Jenjang
            jenjang_item = QTableWidgetItem(beasiswa.get('jenjang', ''))
            jenjang_item.setFlags(jenjang_item.flags() & ~Qt.ItemFlag.ItemIsEditable)
            self.table.setItem(row, 2, jenjang_item)
            
            # Deadline
            deadline = beasiswa.get('deadline', '')
            deadline_item = QTableWidgetItem(deadline)
            deadline_item.setFlags(deadline_item.flags() & ~Qt.ItemFlag.ItemIsEditable)
            
            # Color deadline
            if deadline <= "2026-07-31":
                deadline_item.setBackground(QColor("#ffcccc"))  # Red
            elif deadline <= "2026-09-30":
                deadline_item.setBackground(QColor("#ffffcc"))  # Yellow
            
            self.table.setItem(row, 3, deadline_item)
            
            # Status
            status_item = QTableWidgetItem(beasiswa.get('status', ''))
            status_item.setFlags(status_item.flags() & ~Qt.ItemFlag.ItemIsEditable)
            self.table.setItem(row, 4, status_item)
            
            # Remove button
            remove_btn = QPushButton("❌ Hapus")
            remove_btn.setMaximumWidth(80)
            remove_btn.setStyleSheet("""
                QPushButton {
                    background-color: #ff6b6b;
                    color: white;
                    border: none;
                    border-radius: 3px;
                    padding: 3px;
                    font-size: 10px;
                }
                QPushButton:hover {
                    background-color: #ff5252;
                }
            """)
            
            beasiswa_id = beasiswa.get('beasiswa_id')
            remove_btn.clicked.connect(
                lambda checked, bid=beasiswa_id: self.on_remove_favorit(bid)
            )
            
            self.table.setCellWidget(row, 5, remove_btn)
    
    def on_search_changed(self):
        """Handle search input changed"""
        search_term = self.search_input.text().lower()
        
        for row in range(self.table.rowCount()):
            judul_item = self.table.item(row, 1)
            judul_text = judul_item.text().lower() if judul_item else ""
            
            should_show = search_term in judul_text
            self.table.setRowHidden(row, not should_show)
    
    def on_remove_favorit(self, beasiswa_id: int):
        """Handle remove favorit button click"""
        reply = QMessageBox.question(
            self,
            "Konfirmasi",
            "Hapus beasiswa dari favorit?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        
        if reply == QMessageBox.StandardButton.Yes:
            success, message = delete_favorit(
                user_id=self.user_id,
                beasiswa_id=beasiswa_id
            )
            
            if success:
                logger.info(f"✅ Favorit dihapus: {message}")
                self.favorit_removed.emit(beasiswa_id)
                self.load_favorit_list()  # Reload list
            else:
                QMessageBox.warning(self, "Error", f"❌ {message}")
    
    def refresh(self):
        """Refresh favorit list"""
        self.load_favorit_list()


# ==================== FAVORIT STATISTICS ====================

def get_favorit_stats(user_id: int) -> Dict[str, int]:
    """
    Get statistik favorit user.
    
    Args:
        user_id (int): ID user
    
    Returns:
        Dict[str, int]: Stats dengan keys:
            - total: Total beasiswa di-favorit
            - open: Beasiswa status "Buka"
            - closing: Beasiswa status "Segera Tutup"
            - closed: Beasiswa status "Tutup"
    
    Example:
        >>> stats = get_favorit_stats(user_id=1)
        >>> print(f"Total favorit: {stats['total']}")
    """
    try:
        favorit_list, total = get_favorit_list(user_id=user_id)
        
        stats = {
            'total': total,
            'open': sum(1 for f in favorit_list if f['status'] == 'Buka'),
            'closing': sum(1 for f in favorit_list if f['status'] == 'Segera Tutup'),
            'closed': sum(1 for f in favorit_list if f['status'] == 'Tutup'),
        }
        
        return stats
        
    except Exception as e:
        logger.error(f"❌ Error getting favorit stats: {e}")
        return {'total': 0, 'open': 0, 'closing': 0, 'closed': 0}


if __name__ == "__main__":
    # Test favorit functions
    print("Favorit UI module loaded successfully")
