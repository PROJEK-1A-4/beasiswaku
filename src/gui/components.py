"""
Alert Banner Component for BeasiswaKu
Reusable widget untuk menampilkan info, warning, success, dan error messages
"""

from PyQt6.QtWidgets import QWidget, QHBoxLayout, QLabel, QPushButton
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QFont, QIcon

from src.gui.design_tokens import *


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
