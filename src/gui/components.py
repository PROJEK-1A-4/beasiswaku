"""
Alert Banner Component for BeasiswaKu
Reusable widget untuk menampilkan info, warning, success, dan error messages
"""

import logging
from PyQt6.QtWidgets import QWidget, QHBoxLayout, QLabel, QPushButton
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QFont, QIcon

from src.gui.design_tokens import *

# Setup logging
logger = logging.getLogger(__name__)


class AlertBanner(QWidget):
    """
    Reusable alert banner widget untuk menampilkan pesan dengan berbagai tipe.
    
    Tipe alert yang didukung:
    - 'info': Pesan informasi (biru)
    - 'success': Pesan sukses (hijau)
    - 'warning': Pesan warning (kuning/orange)
    - 'error': Pesan error (merah)
    
    Properties:
    - Dapat ditutup dengan tombol X
    - Menyesuaikan warna background, border, dan text sesuai alert type
    - Animated appearance (fade in)
    
    Example:
        alert = AlertBanner(
            alert_type='success',
            message='Beasiswa telah ditambahkan!',
            closable=True
        )
        layout.addWidget(alert)
        alert.closed.connect(lambda: layout.removeWidget(alert))
    """
    
    # Signal ketika banner ditutup
    closed = pyqtSignal()
    
    def __init__(self, alert_type: str = "info", message: str = "", closable: bool = True, parent=None):
        """
        Inisialisasi AlertBanner
        
        Args:
            alert_type (str): 'info', 'success', 'warning', 'error'
            message (str): Pesan yang akan ditampilkan
            closable (bool): Apakah ada tombol X untuk menutup
            parent: Parent widget
        """
        super().__init__(parent)
        self.alert_type = alert_type
        self.message = message
        self.closable = closable
        
        # Setup UI
        self.init_ui()
    
    def init_ui(self):
        """Inisialisasi UI components"""
        
        # Main layout
        main_layout = QHBoxLayout()
        main_layout.setContentsMargins(12, 10, 12, 10)  # padding: 12px horizontal, 10px vertical
        main_layout.setSpacing(12)
        
        # Define colors based on alert type
        color_map = {
            'info': (COLOR_INFO, '#dbeafe'),
            'success': (COLOR_SUCCESS, COLOR_SUCCESS_LIGHT),
            'warning': (COLOR_WARNING, COLOR_WARNING_LIGHT),
            'error': (COLOR_ERROR, COLOR_ERROR_LIGHT),
        }
        
        border_color, bg_color = color_map.get(self.alert_type, (COLOR_INFO, '#dbeafe'))
        
        # Icon emoji based on alert type
        icon_map = {
            'info': 'ℹ️',
            'success': '✅',
            'warning': '⚠️',
            'error': '❌',
        }
        icon = icon_map.get(self.alert_type, 'ℹ️')
        
        # ===== ICON LABEL =====
        icon_label = QLabel(icon)
        icon_label.setFont(QFont("Arial", 14))
        icon_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        icon_label.setFixedWidth(24)
        main_layout.addWidget(icon_label)
        
        # ===== MESSAGE LABEL =====
        msg_label = QLabel(self.message)
        msg_label.setFont(QFont("Arial", 12))
        msg_label.setWordWrap(True)
        msg_label.setAlignment(Qt.AlignmentFlag.AlignVCenter)
        main_layout.addWidget(msg_label)
        
        # ===== SPACER =====
        main_layout.addStretch()
        
        # ===== CLOSE BUTTON =====
        if self.closable:
            btn_close = QPushButton("✕")
            btn_close.setFont(QFont("Arial", 12))
            btn_close.setFixedSize(28, 28)
            btn_close.setStyleSheet(f"""
                QPushButton {{
                    background-color: transparent;
                    color: {border_color};
                    border: none;
                    border-radius: 4px;
                    padding: 0px;
                    font-weight: bold;
                }}
                QPushButton:hover {{
                    background-color: rgba(0, 0, 0, 0.1);
                }}
            """)
            btn_close.clicked.connect(self._on_close_clicked)
            main_layout.addWidget(btn_close)
        
        # Set widget properties
        self.setLayout(main_layout)
        self.setStyleSheet(f"""
            AlertBanner {{
                background-color: {bg_color};
                border-left: 4px solid {border_color};
                border-radius: {BORDER_RADIUS_MD};
                padding: 0px;
            }}
        """)
    
    def _on_close_clicked(self):
        """Handle close button click"""
        self.closed.emit()
        self.hide()
    
    def set_message(self, message: str):
        """
        Update pesan banner
        
        Args:
            message (str): Pesan baru
        """
        self.message = message
        # Find message label and update
        for i in range(self.layout().count()):
            widget = self.layout().itemAt(i).widget()
            if isinstance(widget, QLabel) and widget != self.layout().itemAt(0).widget():
                widget.setText(message)
                break
    
    def show_alert(self):
        """Tampilkan alert banner (fade in)"""
        self.show()
    
    def close_alert(self):
        """Tutup alert banner"""
        self._on_close_clicked()


# Factory function untuk membuat alert banner dengan mudah
def create_alert(alert_type: str, message: str, closable: bool = True) -> AlertBanner:
    """
    Factory function untuk membuat AlertBanner dengan cepat
    
    Args:
        alert_type (str): 'info', 'success', 'warning', 'error'
        message (str): Pesan yang akan ditampilkan
        closable (bool): Apakah ada tombol X untuk menutup
    
    Returns:
        AlertBanner: Instance dari alert banner
    """
    return AlertBanner(alert_type=alert_type, message=message, closable=closable)


# ============================================================================
# STATUS BADGE COMPONENT (Task 6)
# ============================================================================

class StatusBadge(QLabel):
    """
    Reusable status badge widget dengan pill-shaped design.
    Menampilkan status dengan warna yang sesuai dan rounded corners.
    
    Status yang didukung:
    - 'pending': Light blue (#dbeafe) untuk status menunggu
    - 'approved': Light green (#d1fae5) untuk status approved
    - 'rejected': Light red (#fee2e2) untuk status rejected
    - 'draft': Light gray (#f3f4f6) untuk status draft
    - 'open': Green untuk beasiswa masih buka
    - 'closing-soon': Orange untuk beasiswa segera tutup
    - 'closed': Red untuk beasiswa sudah tutup
    
    Features:
    - Pill-shaped design (fully rounded corners)
    - Automatic color adjustment berdasarkan status
    - Responsive font size
    - Emoji support untuk visual clarity
    - Centered text alignment
    
    Example:
        badge = StatusBadge(status='approved', text='✅ Approved')
        layout.addWidget(badge)
    """
    
    # Mapping status ke color scheme
    STATUS_COLORS = {
        'pending': {
            'text_color': COLOR_STATUS_PENDING,
            'bg_color': '#dbeafe',
            'emoji': '⏳'
        },
        'approved': {
            'text_color': COLOR_STATUS_APPROVED,
            'bg_color': COLOR_SUCCESS_LIGHT,
            'emoji': '✅'
        },
        'rejected': {
            'text_color': COLOR_STATUS_REJECTED,
            'bg_color': COLOR_ERROR_LIGHT,
            'emoji': '❌'
        },
        'draft': {
            'text_color': COLOR_STATUS_DRAFT,
            'bg_color': COLOR_GRAY_100,
            'emoji': '📝'
        },
        'open': {
            'text_color': COLOR_SUCCESS,
            'bg_color': COLOR_SUCCESS_LIGHT,
            'emoji': '🟢'
        },
        'closing-soon': {
            'text_color': COLOR_WARNING,
            'bg_color': COLOR_WARNING_LIGHT,
            'emoji': '🟡'
        },
        'closed': {
            'text_color': COLOR_ERROR,
            'bg_color': COLOR_ERROR_LIGHT,
            'emoji': '🔴'
        },
    }
    
    def __init__(self, status: str = "pending", text: str = "", show_emoji: bool = True, parent=None):
        """
        Inisialisasi StatusBadge
        
        Args:
            status (str): Status key ('pending', 'approved', 'rejected', 'draft', 'open', 'closing-soon', 'closed')
            text (str): Text yang ditampilkan (auto-generated jika kosong)
            show_emoji (bool): Apakah menampilkan emoji
            parent: Parent widget
        """
        super().__init__(parent)
        self.status = status
        self.show_emoji = show_emoji
        
        # Get color scheme dari status
        colors = self.STATUS_COLORS.get(status, self.STATUS_COLORS['draft'])
        text_color = colors['text_color']
        bg_color = colors['bg_color']
        emoji = colors['emoji']
        
        # Set text (gunakan default jika kosong)
        if not text:
            text = status.replace('-', ' ').title()
        
        if show_emoji:
            display_text = f"{emoji} {text}"
        else:
            display_text = text
        
        # Setup label
        self.setText(display_text)
        self.setFont(QFont("Arial", 11, QFont.Weight.Medium))
        self.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        # Apply pill-shaped styling dengan nama color
        self.setStyleSheet(f"""
            QLabel {{
                background-color: {bg_color};
                color: {text_color};
                border: none;
                border-radius: {BORDER_RADIUS_FULL};
                padding: 4px 12px;
                font-weight: 500;
                font-size: 11px;
            }}
        """)
        
        # Set fixed size untuk badge (width auto-adjust, height fixed)
        self.setFixedHeight(28)
        self.setMinimumWidth(80)
        
        logger.debug(f"✅ StatusBadge created: {status} ({display_text})")
    
    def set_status(self, status: str, text: str = ""):
        """
        Update status dan text badge
        
        Args:
            status (str): Status key baru
            text (str): Text baru (optional)
        """
        self.status = status
        
        # Get color scheme
        colors = self.STATUS_COLORS.get(status, self.STATUS_COLORS['draft'])
        text_color = colors['text_color']
        bg_color = colors['bg_color']
        emoji = colors['emoji']
        
        # Set text
        if not text:
            text = status.replace('-', ' ').title()
        
        if self.show_emoji:
            display_text = f"{emoji} {text}"
        else:
            display_text = text
        
        # Update label
        self.setText(display_text)
        self.setStyleSheet(f"""
            QLabel {{
                background-color: {bg_color};
                color: {text_color};
                border: none;
                border-radius: {BORDER_RADIUS_FULL};
                padding: 4px 12px;
                font-weight: 500;
                font-size: 11px;
            }}
        """)


# Factory function untuk membuat status badge dengan mudah
def create_status_badge(status: str, text: str = "", show_emoji: bool = True) -> StatusBadge:
    """
    Factory function untuk membuat StatusBadge dengan cepat
    
    Args:
        status (str): Status key ('pending', 'approved', 'rejected', 'draft', 'open', 'closing-soon', 'closed')
        text (str): Custom text (akan auto-generate jika kosong)
        show_emoji (bool): Tampilkan emoji
    
    Returns:
        StatusBadge: Instance dari status badge
    """
    return StatusBadge(status=status, text=text, show_emoji=show_emoji)
