"""
main.py - Main Application Entry Point & UI Framework
BeasiswaKu - Personal Scholarship Manager

Komponen:
1. LoginWindow - Autentikasi user (login/register)
2. MainWindow - Window utama dengan tab system
3. Integrasi dengan backend (crud.py, gui_beasiswa.py, visualisasi.py)
"""

import sys
import logging
from pathlib import Path
from typing import Optional, Tuple

from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QLabel, QLineEdit, QPushButton, QTabWidget, QStatusBar,
    QMessageBox, QComboBox, QTableWidget, QHeaderView, QDialog,
    QFormLayout, QTextEdit, QScrollArea
)
from PyQt6.QtCore import Qt, QSize, QTimer
from PyQt6.QtGui import QFont, QIcon, QColor, QPixmap
from PyQt6.QtCore import pyqtSignal

from src.database.crud import (
    init_db, login_user, register_user, get_connection
)
from src.visualization.visualisasi import (
    build_statistik_canvases,
    build_tracker_canvases,
)

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# ==================== LOGIN WINDOW ====================

class LoginWindow(QDialog):
    """
    Window untuk login dan register user.
    
    Signals:
        login_success(user_id, username): Emitted ketika login berhasil
    """
    
    login_success = pyqtSignal(int, str)  # user_id, username
    
    def __init__(self):
        super().__init__()
        self.current_user_id = None
        self.init_ui()
        
    def init_ui(self):
        """Initialize login window UI"""
        self.setWindowTitle("BeasiswaKu - Login")
        self.setGeometry(100, 100, 400, 300)
        self.setModal(True)
        
        # Main layout
        layout = QVBoxLayout()
        
        # Logo/Title
        title = QLabel("🎓 BeasiswaKu")
        title.setFont(QFont("Arial", 20, QFont.Weight.Bold))
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(title)
        
        subtitle = QLabel("Personal Scholarship Manager")
        subtitle.setFont(QFont("Arial", 10))
        subtitle.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(subtitle)
        
        layout.addSpacing(20)
        
        # Username field
        username_label = QLabel("📛 Username:")
        self.username_input = QLineEdit()
        self.username_input.setPlaceholderText("Masukkan username")
        layout.addWidget(username_label)
        layout.addWidget(self.username_input)
        
        # Password field
        password_label = QLabel("🔐 Password:")
        self.password_input = QLineEdit()
        self.password_input.setPlaceholderText("Masukkan password")
        self.password_input.setEchoMode(QLineEdit.EchoMode.Password)
        layout.addWidget(password_label)
        layout.addWidget(self.password_input)
        
        # Error message label
        self.error_label = QLabel("")
        self.error_label.setStyleSheet("color: red; font-weight: bold;")
        layout.addWidget(self.error_label)
        
        layout.addSpacing(10)
        
        # Login button
        self.login_btn = QPushButton("🚀 Login")
        self.login_btn.setFont(QFont("Arial", 11, QFont.Weight.Bold))
        self.login_btn.setStyleSheet("background-color: #4CAF50; color: white; padding: 8px;")
        self.login_btn.clicked.connect(self.handle_login)
        layout.addWidget(self.login_btn)
        
        # Register button
        self.register_btn = QPushButton("📝 Daftar Akun Baru")
        self.register_btn.setFont(QFont("Arial", 10))
        self.register_btn.setStyleSheet("background-color: #2196F3; color: white; padding: 8px;")
        self.register_btn.clicked.connect(self.open_register)
        layout.addWidget(self.register_btn)
        
        self.setLayout(layout)
        
        # Fokus ke username saat buka
        self.username_input.setFocus()
        
    def handle_login(self):
        """Handle login button click"""
        username = self.username_input.text().strip()
        password = self.password_input.text().strip()
        
        if not username or not password:
            self.error_label.setText("⚠️ Username dan password harus diisi!")
            return
        
        # Login via backend
        success, message, user_data = login_user(username, password)
        
        if success:
            user_id = user_data['id']
            self.current_user_id = user_id
            logger.info(f"✅ User '{username}' berhasil login")
            self.login_success.emit(user_id, username)
            self.accept()  # Close dialog
        else:
            self.error_label.setText(f"❌ {message}")
            self.password_input.clear()
            self.password_input.setFocus()
    
    def open_register(self):
        """Open register dialog"""
        register_dialog = RegisterWindow()
        if register_dialog.exec() == QDialog.DialogCode.Accepted:
            # Auto-fill username dan close
            self.username_input.setText(register_dialog.new_username)
            self.password_input.setText(register_dialog.new_password)
            self.error_label.setText("✅ Akun berhasil dibuat! Silakan login.")
            self.error_label.setStyleSheet("color: green; font-weight: bold;")


class RegisterWindow(QDialog):
    """
    Dialog untuk registrasi user baru.
    """
    
    def __init__(self):
        super().__init__()
        self.new_username = ""
        self.new_password = ""
        self.init_ui()
        
    def init_ui(self):
        """Initialize register window UI"""
        self.setWindowTitle("BeasiswaKu - Daftar Akun Baru")
        self.setGeometry(150, 150, 400, 350)
        self.setModal(True)
        
        layout = QVBoxLayout()
        
        # Title
        title = QLabel("Buat Akun Baru")
        title.setFont(QFont("Arial", 16, QFont.Weight.Bold))
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(title)
        
        layout.addSpacing(15)
        
        # Form layout
        form = QFormLayout()
        
        # Nama lengkap
        self.nama_input = QLineEdit()
        self.nama_input.setPlaceholderText("Contoh: Budi Santoso")
        form.addRow("📝 Nama Lengkap:", self.nama_input)
        
        # Email
        self.email_input = QLineEdit()
        self.email_input.setPlaceholderText("Contoh: budi@example.com")
        form.addRow("📧 Email:", self.email_input)
        
        # Username
        self.username_input = QLineEdit()
        self.username_input.setPlaceholderText("Minimal 3 karakter")
        form.addRow("👤 Username:", self.username_input)
        
        # Password
        self.password_input = QLineEdit()
        self.password_input.setPlaceholderText("Minimal 6 karakter")
        self.password_input.setEchoMode(QLineEdit.EchoMode.Password)
        form.addRow("🔐 Password:", self.password_input)
        
        # Confirm password
        self.confirm_password_input = QLineEdit()
        self.confirm_password_input.setPlaceholderText("Ulangi password")
        self.confirm_password_input.setEchoMode(QLineEdit.EchoMode.Password)
        form.addRow("🔐 Konfirmasi Password:", self.confirm_password_input)
        
        layout.addLayout(form)
        
        # Error message
        self.error_label = QLabel("")
        self.error_label.setStyleSheet("color: red; font-weight: bold;")
        layout.addWidget(self.error_label)
        
        layout.addSpacing(10)
        
        # Buttons
        button_layout = QHBoxLayout()
        
        register_btn = QPushButton("✅ Daftar")
        register_btn.setStyleSheet("background-color: #4CAF50; color: white; padding: 8px;")
        register_btn.clicked.connect(self.handle_register)
        button_layout.addWidget(register_btn)
        
        cancel_btn = QPushButton("❌ Batal")
        cancel_btn.setStyleSheet("background-color: #f44336; color: white; padding: 8px;")
        cancel_btn.clicked.connect(self.reject)
        button_layout.addWidget(cancel_btn)
        
        layout.addLayout(button_layout)
        
        self.setLayout(layout)
    
    def handle_register(self):
        """Handle register button click"""
        nama = self.nama_input.text().strip()
        email = self.email_input.text().strip()
        username = self.username_input.text().strip()
        password = self.password_input.text().strip()
        confirm = self.confirm_password_input.text().strip()
        
        # Validasi
        if not all([nama, email, username, password, confirm]):
            self.error_label.setText("⚠️ Semua field harus diisi!")
            return
        
        if len(username) < 3:
            self.error_label.setText("⚠️ Username minimal 3 karakter")
            return
        
        if len(password) < 6:
            self.error_label.setText("⚠️ Password minimal 6 karakter")
            return
        
        if password != confirm:
            self.error_label.setText("⚠️ Password tidak cocok!")
            self.confirm_password_input.clear()
            return
        
        if "@" not in email or "." not in email:
            self.error_label.setText("⚠️ Format email tidak valid!")
            return
        
        # Register via backend
        success, message = register_user(username, email, password)
        
        if success:
            self.new_username = username
            self.new_password = password
            logger.info(f"✅ Akun '{username}' berhasil dibuat")
            QMessageBox.information(self, "Sukses", "✅ Akun berhasil dibuat!\n\nSilakan login dengan akun baru Anda.")
            self.accept()
        else:
            self.error_label.setText(f"❌ {message}")


# ==================== MAIN WINDOW ====================

class MainWindow(QMainWindow):
    """
    Main application window dengan tab system.
    
    Tabs:
    1. Tab Beasiswa - Daftar beasiswa
    2. Tab Tracker - Riwayat lamaran
    3. Tab Statistik - Grafik dan statistik
    """
    
    def __init__(self, user_id: int, username: str):
        super().__init__()
        self.user_id = user_id
        self.username = username
        
        self.init_ui()
        
    def init_ui(self):
        """Initialize main window UI"""
        self.setWindowTitle(f"BeasiswaKu - {self.username}")
        self.setGeometry(0, 0, 1200, 700)
        self.center_window()
        self.setStyleSheet("""
            QMainWindow {
                background: #f5f7fb;
            }
            QWidget {
                font-family: Arial;
            }
            QTabWidget::pane {
                border: 1px solid #d7dee8;
                background: white;
                top: -1px;
            }
            QTabBar::tab {
                background: #e9eef5;
                color: #2b2b2b;
                padding: 8px 14px;
                margin-right: 4px;
                border-top-left-radius: 6px;
                border-top-right-radius: 6px;
            }
            QTabBar::tab:selected {
                background: white;
                border: 1px solid #d7dee8;
                border-bottom-color: white;
            }
            QPushButton {
                padding: 7px 12px;
                border-radius: 6px;
                border: 1px solid #c7d0db;
                background: #ffffff;
            }
            QPushButton:hover {
                background: #f0f4f8;
            }
        """)
        
        # Central widget
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # Main layout
        layout = QVBoxLayout()
        layout.setContentsMargins(12, 12, 12, 12)
        layout.setSpacing(10)
        
        # ===== TOP BAR =====
        header_bar = QWidget()
        header_bar.setStyleSheet("""
            QWidget {
                background: white;
                border: 1px solid #d7dee8;
                border-radius: 12px;
            }
        """)
        top_bar_layout = QHBoxLayout(header_bar)
        top_bar_layout.setContentsMargins(16, 12, 16, 12)
        top_bar_layout.setSpacing(10)
        
        # App logo/title
        app_title = QLabel("🎓 BeasiswaKu - Personal Scholarship Manager")
        app_title.setFont(QFont("Arial", 13, QFont.Weight.Bold))
        app_title.setStyleSheet("color: #203040;")
        top_bar_layout.addWidget(app_title)
        
        # Spacer
        top_bar_layout.addStretch()
        
        # User info
        user_label = QLabel(f"👤 {self.username}")
        user_label.setFont(QFont("Arial", 10))
        user_label.setStyleSheet("color: #4c5a6b;")
        top_bar_layout.addWidget(user_label)
        
        # Settings button (placeholder)
        settings_btn = QPushButton("⚙️ Pengaturan")
        settings_btn.setMaximumWidth(120)
        settings_btn.setStyleSheet("background: #ffffff; color: #203040;")
        settings_btn.clicked.connect(self.open_settings)
        top_bar_layout.addWidget(settings_btn)
        
        # Logout button
        logout_btn = QPushButton("🚪 Logout")
        logout_btn.setMaximumWidth(100)
        logout_btn.setStyleSheet("background-color: #f44336; color: white; border: 1px solid #d32f2f;")
        logout_btn.clicked.connect(self.handle_logout)
        top_bar_layout.addWidget(logout_btn)
        
        layout.addWidget(header_bar)
        
        # ===== TAB WIDGET =====
        self.tabs = QTabWidget()
        self.tabs.setDocumentMode(True)
        self.tabs.setStyleSheet(self.tabs.styleSheet() + "QTabBar::tab { min-width: 110px; }")
        
        # Tab 1: Beasiswa
        self.beasiswa_tab = BeasiswaTab(self.user_id)
        self.tabs.addTab(self.beasiswa_tab, "📚 Beasiswa")
        
        # Tab 2: Tracker
        self.tracker_tab = TrackerTab(self.user_id)
        self.tabs.addTab(self.tracker_tab, "📋 Tracker Lamaran")
        
        # Tab 3: Statistik
        self.statistik_tab = StatistikTab(self.user_id)
        self.tabs.addTab(self.statistik_tab, "📊 Statistik")
        self.tabs.setDocumentMode(True)
        self.tabs.setStyleSheet("QTabBar::tab { min-width: 110px; }")
        
        layout.addWidget(self.tabs)
        
        # ===== STATUS BAR =====
        self.statusBar().showMessage("✅ Aplikasi siap digunakan | Database: beasiswaku.db")
        
        central_widget.setLayout(layout)
        
    def center_window(self):
        """Center window di layar"""
        screen = self.screen()
        screen_geometry = screen.availableGeometry()
        window_geometry = self.frameGeometry()
        
        center_point = screen_geometry.center()
        window_geometry.moveCenter(center_point)
        self.move(window_geometry.topLeft())
    
    def open_settings(self):
        """Open settings dialog"""
        settings_dialog = SettingsWindow(self.user_id, self.username)
        settings_dialog.exec()
    
    def handle_logout(self):
        """Handle logout"""
        reply = QMessageBox.question(
            self,
            "Konfirmasi Logout",
            f"Anda yakin ingin keluar, {self.username}?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        
        if reply == QMessageBox.StandardButton.Yes:
            logger.info(f"✅ User '{self.username}' logout")
            self.close()


# ==================== PLACEHOLDER TABS ====================

class BeasiswaTab(QWidget):
    """Tab untuk daftar beasiswa - akan diimplement di gui_beasiswa.py"""
    
    def __init__(self, user_id: int):
        super().__init__()
        self.user_id = user_id
        self.init_ui()
    
    def init_ui(self):
        """Initialize beasiswa tab UI"""
        layout = QVBoxLayout()
        layout.setContentsMargins(18, 18, 18, 18)
        layout.setSpacing(0)

        card = QWidget()
        card.setStyleSheet("""
            QWidget {
                background: #ffffff;
                border: 1px solid #d7dee8;
                border-radius: 12px;
            }
        """)
        card_layout = QVBoxLayout(card)
        card_layout.setContentsMargins(24, 24, 24, 24)
        card_layout.setSpacing(12)

        title = QLabel("📚 Daftar Beasiswa")
        title.setFont(QFont("Arial", 14, QFont.Weight.Bold))
        title.setStyleSheet("color: #203040;")
        card_layout.addWidget(title)

        subtitle = QLabel("Area ini akan berisi daftar beasiswa, filter, dan aksi CRUD.")
        subtitle.setFont(QFont("Arial", 10))
        subtitle.setStyleSheet("color: #607080;")
        card_layout.addWidget(subtitle)
        
        # Placeholder content
        label = QLabel("" + 
                      "Fitur ini akan menampilkan:\n" +
                      "• Tabel beasiswa dengan filter & search\n" +
                      "• Highlight deadline (merah/kuning)\n" +
                      "• CRUD beasiswa (tambah, edit, hapus)\n" +
                      "• Export CSV\n" +
                      "• Refresh data")
        label.setAlignment(Qt.AlignmentFlag.AlignLeft)
        label.setFont(QFont("Arial", 11))
        label.setStyleSheet("""
            QLabel {
                padding: 18px;
                background: #f7f9fc;
                color: #243447;
                border: 1px dashed #c7d0db;
                border-radius: 10px;
                line-height: 1.5;
            }
        """)
        
        card_layout.addWidget(label)
        card_layout.addStretch()
        layout.addWidget(card)
        self.setLayout(layout)


class TrackerTab(QWidget):
    """Tab untuk tracking lamaran - akan diimplement di crud.py"""
    
    def __init__(self, user_id: int):
        super().__init__()
        self.user_id = user_id
        self.init_ui()
    
    def init_ui(self):
        """Initialize tracker tab UI"""
        layout = QVBoxLayout()
        layout.setContentsMargins(12, 12, 12, 12)
        layout.setSpacing(12)

        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)

        content = QWidget()
        content_layout = QVBoxLayout(content)
        content_layout.setContentsMargins(0, 0, 0, 0)
        content_layout.setSpacing(16)

        title = QLabel("📋 Tracker Lamaran")
        title.setFont(QFont("Arial", 12, QFont.Weight.Bold))
        content_layout.addWidget(title)

        try:
            tracker_canvases = build_tracker_canvases(self.user_id)
            tracker_status_canvas = tracker_canvases["canvas_lamaran_status"]
            tracker_month_canvas = tracker_canvases["canvas_lamaran_bulanan"]
            tracker_status_canvas.setMinimumHeight(320)
            tracker_month_canvas.setMinimumHeight(320)
            content_layout.addWidget(tracker_status_canvas)
            content_layout.addWidget(tracker_month_canvas)
        except Exception as e:
            logger.error(f"❌ Gagal memuat chart tracker: {e}")
            error_label = QLabel(
                "Gagal memuat chart tracker.\n"
                "Silakan cek data lamaran atau koneksi database."
            )
            error_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            error_label.setFont(QFont("Arial", 11))
            error_label.setStyleSheet("padding: 40px; background-color: #f8d7da; border-radius: 5px;")
            content_layout.addWidget(error_label)

        scroll_area.setWidget(content)
        layout.addWidget(scroll_area)

        self.setLayout(layout)


class StatistikTab(QWidget):
    """Tab untuk statistik - akan diimplement di visualisasi.py"""
    
    def __init__(self, user_id: int):
        super().__init__()
        self.user_id = user_id
        self.init_ui()
    
    def init_ui(self):
        """Initialize statistik tab UI"""
        layout = QVBoxLayout()
        layout.setContentsMargins(12, 12, 12, 12)
        layout.setSpacing(12)

        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)

        content = QWidget()
        content_layout = QVBoxLayout(content)
        content_layout.setContentsMargins(0, 0, 0, 0)
        content_layout.setSpacing(16)

        title = QLabel("📊 Statistik & Grafik")
        title.setFont(QFont("Arial", 12, QFont.Weight.Bold))
        content_layout.addWidget(title)

        try:
            statistik_canvases = build_statistik_canvases()
            canvas_jenjang = statistik_canvases["canvas_jenjang"]
            canvas_penyelenggara = statistik_canvases["canvas_penyelenggara"]
            canvas_status = statistik_canvases["canvas_status"]
            canvas_jenjang.setMinimumHeight(300)
            canvas_penyelenggara.setMinimumHeight(300)
            canvas_status.setMinimumHeight(300)
            content_layout.addWidget(canvas_jenjang)
            content_layout.addWidget(canvas_penyelenggara)
            content_layout.addWidget(canvas_status)
        except Exception as e:
            logger.error(f"❌ Gagal memuat chart statistik: {e}")
            error_label = QLabel(
                "Gagal memuat chart statistik.\n"
                "Silakan cek data beasiswa atau koneksi database."
            )
            error_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            error_label.setFont(QFont("Arial", 11))
            error_label.setStyleSheet("padding: 40px; background-color: #f8d7da; border-radius: 5px;")
            content_layout.addWidget(error_label)

        scroll_area.setWidget(content)
        layout.addWidget(scroll_area)

        self.setLayout(layout)


# ==================== SETTINGS WINDOW ====================

class SettingsWindow(QDialog):
    """Dialog untuk pengaturan user"""
    
    def __init__(self, user_id: int, username: str):
        super().__init__()
        self.user_id = user_id
        self.username = username
        self.init_ui()
    
    def init_ui(self):
        """Initialize settings window UI"""
        self.setWindowTitle("Pengaturan")
        self.setGeometry(200, 200, 500, 400)
        self.setModal(True)
        
        layout = QVBoxLayout()
        
        # Title
        title = QLabel("⚙️ Pengaturan Akun")
        title.setFont(QFont("Arial", 14, QFont.Weight.Bold))
        layout.addWidget(title)
        
        layout.addSpacing(10)
        
        # Info user
        info_label = QLabel(f"Username: {self.username}\nUser ID: {self.user_id}")
        info_label.setFont(QFont("Arial", 10))
        info_label.setStyleSheet("padding: 10px; background-color: #e3f2fd; border-radius: 5px;")
        layout.addWidget(info_label)
        
        layout.addSpacing(15)
        
        # Features coming soon
        features_label = QLabel("Fitur yang akan datang:\n" +
                               "• Ganti password\n" +
                               "• Edit profil\n" +
                               "• Preferensi aplikasi\n" +
                               "• Backup & restore data")
        features_label.setFont(QFont("Arial", 10))
        layout.addWidget(features_label)
        
        layout.addStretch()
        
        # Close button
        close_btn = QPushButton("Tutup")
        close_btn.setStyleSheet("background-color: #2196F3; color: white; padding: 8px;")
        close_btn.clicked.connect(self.accept)
        layout.addWidget(close_btn)
        
        self.setLayout(layout)


# ==================== APPLICATION ENTRY POINT ====================

def main():
    """Main entry point aplikasi"""
    app = QApplication(sys.argv)
    
    # Initialize database
    try:
        init_db()
        logger.info("✅ Database initialized")
    except Exception as e:
        logger.error(f"❌ Database initialization failed: {e}")
        QMessageBox.critical(None, "Error", f"Gagal menginisialisasi database:\n{e}")
        sys.exit(1)
    
    # Show login window
    login_window = LoginWindow()
    
    if login_window.exec() == QDialog.DialogCode.Accepted:
        # Get user info from login
        user_id = login_window.current_user_id
        username = login_window.username_input.text()
        
        # Open main window
        main_window = MainWindow(user_id, username)
        main_window.show()
        
        # Run application
        sys.exit(app.exec())
    else:
        # Login cancelled
        logger.info("Aplikasi ditutup tanpa login")
        sys.exit(0)


if __name__ == "__main__":
    main()
