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
    QFormLayout, QTextEdit, QFrame
)
from PyQt6.QtCore import Qt, QSize, QTimer
from PyQt6.QtGui import QFont, QIcon, QColor, QPixmap
from PyQt6.QtCore import pyqtSignal

from src.database.crud import (
    init_db, login_user, register_user, get_connection
)
from src.gui.tab_beranda import BerandaTab
from src.gui.gui_beasiswa import BeasiswaTab
from src.gui.tab_tracker import TrackerTab
from src.gui.tab_statistik import StatistikTab
from src.gui.tab_profil import ProfileTab
from src.gui.sidebar import Sidebar
from src.gui.sidebar import Sidebar

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
            logger.info(f"[SUCCESS] User '{username}' berhasil login")
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
            logger.info(f"[SUCCESS] Akun '{username}' berhasil dibuat")
            QMessageBox.information(self, "Sukses", "Akun berhasil dibuat!\n\nSilakan login dengan akun baru Anda.")
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
        
        # Central widget
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # Main layout
        main_container_layout = QHBoxLayout()
        main_container_layout.setContentsMargins(0, 0, 0, 0)
        main_container_layout.setSpacing(0)
        
        # ===== SIDEBAR =====
        self.sidebar = Sidebar()
        self.sidebar.setMinimumWidth(220)
        self.sidebar.setMaximumWidth(220)
        self.sidebar.nav_clicked.connect(self.on_sidebar_nav_clicked)
        self.sidebar.settings_clicked.connect(self.open_settings)
        self.sidebar.logout_clicked.connect(self.handle_logout)
        main_container_layout.addWidget(self.sidebar)
        
        # ===== RIGHT PANEL (Top bar + Tabs) =====
        right_panel_layout = QVBoxLayout()
        right_panel_layout.setContentsMargins(0, 0, 0, 0)
        right_panel_layout.setSpacing(0)
        
        # Top bar
        top_bar_layout = QHBoxLayout()
        
        # App logo/title
        app_title = QLabel("🎓 BeasiswaKu - Personal Scholarship Manager")
        app_title.setFont(QFont("Arial", 12, QFont.Weight.Bold))
        top_bar_layout.addWidget(app_title)
        
        # Spacer
        top_bar_layout.addStretch()
        
        # User info
        user_label = QLabel(f"👤 {self.username}")
        user_label.setFont(QFont("Arial", 10))
        top_bar_layout.addWidget(user_label)
        
        top_bar_layout.setContentsMargins(16, 12, 16, 12)
        top_bar_frame = QFrame()
        top_bar_frame.setStyleSheet("border-bottom: 1px solid #e0e0e0;")
        top_bar_frame.setLayout(top_bar_layout)
        top_bar_frame.setMaximumHeight(50)
        right_panel_layout.addWidget(top_bar_frame)
        
        # ===== TAB WIDGET =====
        self.tabs = QTabWidget()
        
        # Tab 0: Beranda (Home/Dashboard)
        self.beranda_tab = BerandaTab(self.user_id, self.username)
        self.tabs.addTab(self.beranda_tab, "🏠 Beranda")
        
        # Tab 1: Beasiswa
        self.beasiswa_tab = BeasiswaTab(self.user_id)
        self.tabs.addTab(self.beasiswa_tab, "📚 Beasiswa")
        
        # Tab 2: Tracker
        self.tracker_tab = TrackerTab(self.user_id)
        self.tabs.addTab(self.tracker_tab, "📋 Tracker Lamaran")
        
        # Tab 3: Statistik
        self.statistik_tab = StatistikTab(self.user_id)
        self.tabs.addTab(self.statistik_tab, "📊 Statistik")
        
        # Tab 4: Profil
        self.profil_tab = ProfileTab(self.user_id, self.username)
        self.tabs.addTab(self.profil_tab, "👤 Profil")
        
        # Hide tab bar (navigation is in sidebar)
        self.tabs.tabBar().hide()
        
        right_panel_layout.addWidget(self.tabs)
        
        # Create right panel widget
        right_panel_widget = QWidget()
        right_panel_widget.setLayout(right_panel_layout)
        main_container_layout.addWidget(right_panel_widget)
        
        # Set main container as central widget
        main_container = QWidget()
        main_container.setLayout(main_container_layout)
        central_widget = main_container
        
        # Create wrapper for layout
        wrapper_layout = QVBoxLayout()
        wrapper_layout.setContentsMargins(0, 0, 0, 0)
        wrapper_layout.setSpacing(0)
        wrapper_layout.addWidget(central_widget)
        
        real_central = QWidget()
        real_central.setLayout(wrapper_layout)
        self.setCentralWidget(real_central)
        
        # ===== STATUS BAR =====
        self.statusBar().showMessage("✅ Aplikasi siap digunakan | Database: beasiswaku.db")
        
    def center_window(self):
        """Center window di layar"""
        screen = self.screen()
        screen_geometry = screen.availableGeometry()
        window_geometry = self.frameGeometry()
        
        center_point = screen_geometry.center()
        window_geometry.moveCenter(center_point)
        self.move(window_geometry.topLeft())
    
    def on_sidebar_nav_clicked(self, tab_index: int):
        """Handle sidebar navigation click."""
        self.tabs.setCurrentIndex(tab_index)
        logger.info(f"Switched to tab {tab_index}")
    
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
            logger.info(f"[SUCCESS] User '{self.username}' logout")
            self.close()


# ==================== SETTINGS WINDOW ====================

class SettingsWindow(QDialog):
    """Dialog untuk pengaturan user dengan Password change & Profile edit"""
    
    def __init__(self, user_id: int, username: str):
        super().__init__()
        self.user_id = user_id
        self.username = username
        self.init_ui()
    
    def init_ui(self):
        """Initialize settings window UI"""
        self.setWindowTitle("⚙️ Pengaturan Akun")
        self.setGeometry(200, 200, 500, 400)
        self.setModal(True)
        
        layout = QVBoxLayout()
        layout.setContentsMargins(16, 16, 16, 16)
        layout.setSpacing(12)
        
        # Title
        title = QLabel("⚙️ Pengaturan Akun")
        title.setFont(QFont("Arial", 14, QFont.Weight.Bold))
        title.setStyleSheet("color: #1e3a8a;")
        layout.addWidget(title)
        
        layout.addSpacing(10)
        
        # Info user
        info_label = QLabel(f"👤 Username: {self.username}\n📌 User ID: {self.user_id}")
        info_label.setFont(QFont("Arial", 10))
        info_label.setStyleSheet("padding: 10px; background-color: #f0f7ff; border-left: 4px solid #f59e0b; border-radius: 5px; color: #1e3a8a;")
        layout.addWidget(info_label)
        
        layout.addSpacing(15)
        
        # Ganti Password Section
        pwd_label = QLabel("🔐 Ganti Password")
        pwd_label.setFont(QFont("Arial", 11, QFont.Weight.Bold))
        pwd_label.setStyleSheet("color: #1e3a8a;")
        layout.addWidget(pwd_label)
        
        pwd_layout = QFormLayout()
        self.old_pwd = QLineEdit()
        self.old_pwd.setPlaceholderText("Password lama")
        self.old_pwd.setEchoMode(QLineEdit.EchoMode.Password)
        pwd_layout.addRow("Password Lama:", self.old_pwd)
        
        self.new_pwd = QLineEdit()
        self.new_pwd.setPlaceholderText("Password baru (min 6 karakter)")
        self.new_pwd.setEchoMode(QLineEdit.EchoMode.Password)
        pwd_layout.addRow("Password Baru:", self.new_pwd)
        
        layout.addLayout(pwd_layout)
        
        # Button layout
        btn_layout = QHBoxLayout()
        btn_layout.addStretch()
        
        save_pwd_btn = QPushButton("💾 Simpan Password")
        save_pwd_btn.setStyleSheet("background-color: #1e3a8a; color: white; padding: 8px 16px; border-radius: 4px; font-weight: bold;")
        save_pwd_btn.clicked.connect(self.save_password)
        btn_layout.addWidget(save_pwd_btn)
        
        layout.addLayout(btn_layout)
        layout.addSpacing(15)
        
        # Message label
        self.message_label = QLabel("")
        self.message_label.setStyleSheet("font-weight: bold;")
        layout.addWidget(self.message_label)
        
        layout.addStretch()
        
        # Close button
        close_btn = QPushButton("✖️ Tutup")
        close_btn.setStyleSheet("background-color: #9ca3af; color: white; padding: 8px 16px; border-radius: 4px;")
        close_btn.clicked.connect(self.accept)
        layout.addWidget(close_btn)
        
        self.setLayout(layout)
    
    def save_password(self):
        """Save new password"""
        old_pwd = self.old_pwd.text()
        new_pwd = self.new_pwd.text()
        
        if not old_pwd or not new_pwd:
            self.message_label.setText("❌ Password tidak boleh kosong!")
            self.message_label.setStyleSheet("color: red; font-weight: bold;")
            return
        
        if len(new_pwd) < 6:
            self.message_label.setText("❌ Password minimal 6 karakter!")
            self.message_label.setStyleSheet("color: red; font-weight: bold;")
            return
        
        try:
            conn = get_connection()
            cursor = conn.cursor()
            
            # Check old password
            cursor.execute("SELECT password FROM akun WHERE id_akun = ?", (self.user_id,))
            result = cursor.fetchone()
            
            if result is None or result[0] != old_pwd:
                self.message_label.setText("❌ Password lama salah!")
                self.message_label.setStyleSheet("color: red; font-weight: bold;")
                return
            
            # Update password
            cursor.execute("UPDATE akun SET password = ? WHERE id_akun = ?", (new_pwd, self.user_id))
            conn.commit()
            
            self.message_label.setText("✅ Password berhasil diubah!")
            self.message_label.setStyleSheet("color: green; font-weight: bold;")
            
            # Clear inputs
            self.old_pwd.clear()
            self.new_pwd.clear()
            
            logger.info(f"[SUCCESS] Password for user {self.username} changed")
        
        except Exception as e:
            self.message_label.setText(f"❌ Error: {str(e)}")
            self.message_label.setStyleSheet("color: red; font-weight: bold;")
            logger.error(f"Error changing password: {e}")


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
