"""
main.py - Main Application Entry Point & UI Framework
BeasiswaKu - Personal Scholarship Manager

Komponen:
1. LoginWindow - Autentikasi user (login/register)
2. MainWindow - Window utama dengan tab system
3. Integrasi dengan backend (crud.py, tab_beasiswa.py, visualisasi.py)
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
from PyQt6.QtCore import Qt, QSize, QTimer, QObject, pyqtSignal
from PyQt6.QtGui import QFont, QIcon, QColor, QPixmap

from src.database.crud import (
    init_db, login_user, register_user, get_connection,
    hash_password, verify_password
)
from src.core import setup_logging
from src.gui.tab_beranda import BerandaTab
from src.gui.tab_beasiswa import BeasiswaTab
from src.gui.tab_tracker import TrackerTab
from src.gui.tab_statistik import StatistikTab
from src.gui.tab_profil import ProfileTab
from src.gui.sidebar import Sidebar
from src.gui.design_tokens import (
    COLOR_AMBER,
    COLOR_COBALT,
    COLOR_COBALT_DARK,
    COLOR_COBALT_LIGHT,
    COLOR_ERROR,
    COLOR_GRAY_100,
    COLOR_GRAY_200,
    COLOR_GRAY_300,
    COLOR_GRAY_500,
    COLOR_GRAY_600,
    COLOR_GRAY_700,
    COLOR_GRAY_900,
    COLOR_SUCCESS,
    COLOR_SURFACE_APP,
    COLOR_SURFACE_SOFT,
    COLOR_WHITE,
    FONT_FAMILY_PRIMARY,
    FONT_SIZE_LG,
    FONT_SIZE_MD,
    FONT_SIZE_SM,
    FONT_SIZE_XS,
)

logger = logging.getLogger(__name__)


class AppSignalBus(QObject):
    """Shared event bus for cross-tab refresh notifications."""

    data_changed = pyqtSignal(str)


def _create_chart_section(section_title: str, canvas, min_height: int) -> QWidget:
    """Bungkus canvas chart dalam kartu dengan judul yang jelas."""
    section = QWidget()
    section.setStyleSheet("""
        QWidget {
            background: white;
            border: 1px solid #d7dee8;
            border-radius: 12px;
        }
    """)

    section_layout = QVBoxLayout(section)
    section_layout.setContentsMargins(16, 14, 16, 16)
    section_layout.setSpacing(8)

    heading = QLabel(section_title)
    heading.setFont(QFont("Arial", 13, QFont.Weight.Bold))
    heading.setStyleSheet("color: #203040;")
    section_layout.addWidget(heading)

    canvas.setMinimumHeight(min_height)
    canvas.setStyleSheet("background: transparent;")
    section_layout.addWidget(canvas)

    return section

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
        self.resize(980, 700)
        self.setMinimumSize(760, 540)
        self.setModal(True)
        self.setStyleSheet(f"""
            QDialog {{
                background-color: {COLOR_SURFACE_SOFT};
                font-family: {FONT_FAMILY_PRIMARY};
            }}
            QFrame#authCard {{
                background-color: {COLOR_WHITE};
                border: 1px solid #d6e2f2;
                border-radius: 18px;
            }}
            QLabel {{
                color: {COLOR_GRAY_700};
            }}
            QLabel#authTitle {{
                color: {COLOR_COBALT_DARK};
                font-weight: 700;
            }}
            QLabel#authSubtitle {{
                color: {COLOR_GRAY_600};
            }}
            QLabel#authCaption {{
                color: {COLOR_GRAY_600};
            }}
            QLabel#authMessage {{
                min-height: 20px;
                font-weight: 600;
            }}
            QLineEdit {{
                background-color: {COLOR_WHITE};
                border: 1px solid {COLOR_GRAY_200};
                border-radius: 8px;
                padding: 8px 10px;
                color: {COLOR_GRAY_900};
            }}
            QLineEdit:focus {{
                border: 1px solid {COLOR_COBALT};
            }}
            QPushButton {{
                border-radius: 8px;
                padding: 9px 10px;
                font-weight: 600;
            }}
            QPushButton#primaryAction {{
                background-color: {COLOR_COBALT};
                color: {COLOR_WHITE};
                border: 1px solid {COLOR_COBALT_DARK};
            }}
            QPushButton#primaryAction:hover {{
                background-color: {COLOR_COBALT_LIGHT};
            }}
            QPushButton#secondaryAction {{
                background-color: {COLOR_WHITE};
                color: {COLOR_COBALT};
                border: 1px solid #d3dff0;
            }}
            QPushButton#secondaryAction:hover {{
                background-color: #f7fbff;
                border: 1px solid {COLOR_COBALT};
            }}
        """)

        # Root layout keeps form centered on large windows
        root_layout = QVBoxLayout(self)
        root_layout.setContentsMargins(28, 24, 28, 24)
        root_layout.setSpacing(0)
        root_layout.addStretch()

        card = QFrame()
        card.setObjectName("authCard")
        card.setMaximumWidth(520)
        card_layout = QVBoxLayout(card)
        card_layout.setContentsMargins(28, 28, 28, 24)
        card_layout.setSpacing(12)

        # Logo/Title
        title = QLabel("🎓 BeasiswaKu")
        title.setObjectName("authTitle")
        title.setFont(QFont("Trebuchet MS", 26, QFont.Weight.Bold))
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        card_layout.addWidget(title)
        
        subtitle = QLabel("Personal Scholarship Manager")
        subtitle.setObjectName("authSubtitle")
        subtitle.setObjectName("authCaption")
        subtitle.setFont(QFont("Trebuchet MS", FONT_SIZE_MD))
        subtitle.setAlignment(Qt.AlignmentFlag.AlignCenter)
        card_layout.addWidget(subtitle)

        card_layout.addSpacing(8)

        # Username field
        username_label = QLabel("Username")
        username_label.setFont(QFont("Trebuchet MS", FONT_SIZE_SM, QFont.Weight.DemiBold))
        self.username_input = QLineEdit()
        self.username_input.setPlaceholderText("Masukkan username")
        self.username_input.setMinimumHeight(42)
        card_layout.addWidget(username_label)
        card_layout.addWidget(self.username_input)

        # Password field
        password_label = QLabel("Password")
        password_label.setFont(QFont("Trebuchet MS", FONT_SIZE_SM, QFont.Weight.DemiBold))
        self.password_input = QLineEdit()
        self.password_input.setPlaceholderText("Masukkan password")
        self.password_input.setEchoMode(QLineEdit.EchoMode.Password)
        self.password_input.setMinimumHeight(42)
        card_layout.addWidget(password_label)
        card_layout.addWidget(self.password_input)

        # Error message label
        self.error_label = QLabel("")
        self.error_label.setObjectName("authMessage")
        card_layout.addWidget(self.error_label)

        card_layout.addSpacing(8)

        # Login button
        self.login_btn = QPushButton("🚀 Login")
        self.login_btn.setObjectName("primaryAction")
        self.login_btn.setFont(QFont("Trebuchet MS", FONT_SIZE_MD, QFont.Weight.Bold))
        self.login_btn.setMinimumHeight(42)
        self.login_btn.clicked.connect(self.handle_login)
        card_layout.addWidget(self.login_btn)

        # Register button
        self.register_btn = QPushButton("📝 Daftar Akun Baru")
        self.register_btn.setObjectName("secondaryAction")
        self.register_btn.setFont(QFont("Trebuchet MS", FONT_SIZE_SM))
        self.register_btn.setMinimumHeight(42)
        self.register_btn.clicked.connect(self.open_register)
        card_layout.addWidget(self.register_btn)

        root_layout.addWidget(card, alignment=Qt.AlignmentFlag.AlignHCenter)
        root_layout.addStretch()

        # Fokus ke username saat buka
        self.username_input.setFocus()
        
    def handle_login(self):
        """Handle login button click"""
        username = self.username_input.text().strip()
        password = self.password_input.text().strip()
        
        if not username or not password:
            self.error_label.setText("⚠️ Username dan password harus diisi!")
            self.error_label.setStyleSheet(f"color: {COLOR_ERROR}; font-weight: 600;")
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
            self.error_label.setStyleSheet(f"color: {COLOR_ERROR}; font-weight: 600;")
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
            self.error_label.setStyleSheet(f"color: {COLOR_SUCCESS}; font-weight: 600;")


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
        self.resize(1020, 740)
        self.setMinimumSize(820, 620)
        self.setModal(True)
        self.setStyleSheet(f"""
            QDialog {{
                background-color: {COLOR_SURFACE_SOFT};
                font-family: {FONT_FAMILY_PRIMARY};
            }}
            QFrame#registerCard {{
                background-color: {COLOR_WHITE};
                border: 1px solid #d6e2f2;
                border-radius: 18px;
            }}
            QLabel {{
                color: {COLOR_GRAY_700};
            }}
            QLabel#registerTitle {{
                color: {COLOR_COBALT_DARK};
                font-weight: 700;
            }}
            QLabel#registerMessage {{
                min-height: 20px;
                font-weight: 600;
            }}
            QLineEdit {{
                background-color: {COLOR_WHITE};
                border: 1px solid {COLOR_GRAY_200};
                border-radius: 8px;
                padding: 8px 10px;
                color: {COLOR_GRAY_900};
            }}
            QLineEdit:focus {{
                border: 1px solid {COLOR_COBALT};
            }}
            QPushButton {{
                border-radius: 8px;
                padding: 9px 10px;
                font-weight: 600;
            }}
            QPushButton#primaryAction {{
                background-color: {COLOR_COBALT};
                color: {COLOR_WHITE};
                border: 1px solid {COLOR_COBALT_DARK};
            }}
            QPushButton#primaryAction:hover {{
                background-color: {COLOR_COBALT_LIGHT};
            }}
            QPushButton#dangerAction {{
                background-color: {COLOR_WHITE};
                color: {COLOR_ERROR};
                border: 1px solid #f2c4c4;
            }}
            QPushButton#dangerAction:hover {{
                background-color: #fff5f5;
                border: 1px solid {COLOR_ERROR};
            }}
        """)

        root_layout = QVBoxLayout(self)
        root_layout.setContentsMargins(28, 24, 28, 24)
        root_layout.setSpacing(0)
        root_layout.addStretch()

        card = QFrame()
        card.setObjectName("registerCard")
        card.setMaximumWidth(620)
        layout = QVBoxLayout(card)
        layout.setContentsMargins(28, 28, 28, 24)
        layout.setSpacing(12)

        # Title
        title = QLabel("Buat Akun Baru")
        title.setObjectName("registerTitle")
        title.setFont(QFont("Trebuchet MS", 24, QFont.Weight.Bold))
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(title)

        subtitle = QLabel("Lengkapi data berikut untuk membuat akun baru")
        subtitle.setAlignment(Qt.AlignmentFlag.AlignCenter)
        subtitle.setStyleSheet(f"color: {COLOR_GRAY_600};")
        subtitle.setFont(QFont("Trebuchet MS", FONT_SIZE_SM))
        layout.addWidget(subtitle)

        layout.addSpacing(10)
        
        # Form layout
        form = QFormLayout()
        form.setHorizontalSpacing(14)
        form.setVerticalSpacing(10)
        form.setLabelAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter)
        form.setFormAlignment(Qt.AlignmentFlag.AlignHCenter)
        
        # Nama lengkap
        self.nama_input = QLineEdit()
        self.nama_input.setPlaceholderText("Contoh: Budi Santoso")
        self.nama_input.setMinimumHeight(40)
        form.addRow("📝 Nama Lengkap:", self.nama_input)
        
        # Email
        self.email_input = QLineEdit()
        self.email_input.setPlaceholderText("Contoh: budi@example.com")
        self.email_input.setMinimumHeight(40)
        form.addRow("📧 Email:", self.email_input)
        
        # Username
        self.username_input = QLineEdit()
        self.username_input.setPlaceholderText("Minimal 3 karakter")
        self.username_input.setMinimumHeight(40)
        form.addRow("👤 Username:", self.username_input)
        
        # Password
        self.password_input = QLineEdit()
        self.password_input.setPlaceholderText("Minimal 6 karakter")
        self.password_input.setEchoMode(QLineEdit.EchoMode.Password)
        self.password_input.setMinimumHeight(40)
        form.addRow("🔐 Password:", self.password_input)
        
        # Confirm password
        self.confirm_password_input = QLineEdit()
        self.confirm_password_input.setPlaceholderText("Ulangi password")
        self.confirm_password_input.setEchoMode(QLineEdit.EchoMode.Password)
        self.confirm_password_input.setMinimumHeight(40)
        form.addRow("🔐 Konfirmasi Password:", self.confirm_password_input)
        
        layout.addLayout(form)
        
        # Error message
        self.error_label = QLabel("")
        self.error_label.setObjectName("registerMessage")
        layout.addWidget(self.error_label)
        
        layout.addSpacing(10)
        
        # Buttons
        button_layout = QHBoxLayout()
        button_layout.setSpacing(10)
        
        register_btn = QPushButton("✅ Daftar")
        register_btn.setObjectName("primaryAction")
        register_btn.setMinimumHeight(42)
        register_btn.clicked.connect(self.handle_register)
        button_layout.addWidget(register_btn)
        
        cancel_btn = QPushButton("❌ Batal")
        cancel_btn.setObjectName("dangerAction")
        cancel_btn.setMinimumHeight(42)
        cancel_btn.clicked.connect(self.reject)
        button_layout.addWidget(cancel_btn)
        
        layout.addLayout(button_layout)

        root_layout.addWidget(card, alignment=Qt.AlignmentFlag.AlignHCenter)
        root_layout.addStretch()
    
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
            self.error_label.setStyleSheet(f"color: {COLOR_ERROR}; font-weight: 600;")
            return
        
        if len(username) < 3:
            self.error_label.setText("⚠️ Username minimal 3 karakter")
            self.error_label.setStyleSheet(f"color: {COLOR_ERROR}; font-weight: 600;")
            return
        
        if len(password) < 6:
            self.error_label.setText("⚠️ Password minimal 6 karakter")
            self.error_label.setStyleSheet(f"color: {COLOR_ERROR}; font-weight: 600;")
            return
        
        if password != confirm:
            self.error_label.setText("⚠️ Password tidak cocok!")
            self.error_label.setStyleSheet(f"color: {COLOR_ERROR}; font-weight: 600;")
            self.confirm_password_input.clear()
            return
        
        if "@" not in email or "." not in email:
            self.error_label.setText("⚠️ Format email tidak valid!")
            self.error_label.setStyleSheet(f"color: {COLOR_ERROR}; font-weight: 600;")
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
            self.error_label.setStyleSheet(f"color: {COLOR_ERROR}; font-weight: 600;")


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
        self.signals = AppSignalBus()
        self.signals.data_changed.connect(self._handle_data_changed)
        
        self.init_ui()
        
    def init_ui(self):
        """Initialize main window UI"""
        self.setWindowTitle(f"BeasiswaKu - {self.username}")
        self.setGeometry(0, 0, 1200, 700)
        self.center_window()
        self.setStyleSheet(f"""
            QMainWindow {{
                background: {COLOR_SURFACE_APP};
            }}
            QWidget {{
                font-family: {FONT_FAMILY_PRIMARY};
                color: {COLOR_GRAY_900};
            }}
            QTabWidget::pane {{
                border: 1px solid #d7e1f1;
                background: {COLOR_WHITE};
                top: -1px;
            }}
            QTabBar::tab {{
                background: {COLOR_GRAY_100};
                color: {COLOR_GRAY_700};
                padding: 9px 14px;
                margin-right: 4px;
                border-top-left-radius: 8px;
                border-top-right-radius: 8px;
            }}
            QTabBar::tab:selected {{
                background: {COLOR_WHITE};
                border: 1px solid #d7e1f1;
                border-bottom-color: {COLOR_WHITE};
            }}
            QPushButton {{
                padding: 8px 12px;
                border-radius: 8px;
                border: 1px solid #cfdced;
                background: {COLOR_WHITE};
            }}
            QPushButton:hover {{
                background: #f6faff;
            }}
        """)
        
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
        top_bar_layout.setContentsMargins(18, 14, 18, 14)
        top_bar_layout.setSpacing(12)
        
        title_box = QWidget()
        title_layout = QVBoxLayout(title_box)
        title_layout.setContentsMargins(0, 0, 0, 0)
        title_layout.setSpacing(2)

        app_title = QLabel("BeasiswaKu Workspace")
        app_title.setFont(QFont("Trebuchet MS", FONT_SIZE_LG, QFont.Weight.Bold))
        app_title.setStyleSheet(f"color: {COLOR_COBALT_DARK};")
        title_layout.addWidget(app_title)

        app_subtitle = QLabel("Scholarship planning dashboard")
        app_subtitle.setFont(QFont("Trebuchet MS", FONT_SIZE_XS))
        app_subtitle.setStyleSheet(f"color: {COLOR_GRAY_600};")
        title_layout.addWidget(app_subtitle)

        top_bar_layout.addWidget(title_box)
        
        # Spacer
        top_bar_layout.addStretch()
        
        workspace_badge = QLabel("Live Sync")
        workspace_badge.setFont(QFont("Trebuchet MS", FONT_SIZE_XS, QFont.Weight.DemiBold))
        workspace_badge.setStyleSheet(
            f"background-color: {COLOR_AMBER}; color: #3a2a00; "
            "padding: 4px 10px; border-radius: 10px;"
        )
        top_bar_layout.addWidget(workspace_badge)

        # User info
        self.user_label = QLabel(f"👤 {self.username}")
        self.user_label.setFont(QFont("Trebuchet MS", FONT_SIZE_SM, QFont.Weight.Medium))
        self.user_label.setStyleSheet(
            f"background-color: {COLOR_WHITE}; color: {COLOR_COBALT}; "
            "padding: 5px 12px; border-radius: 14px; border: 1px solid #d7e2f2;"
        )
        top_bar_layout.addWidget(self.user_label)
        
        top_bar_frame = QFrame()
        top_bar_frame.setStyleSheet(f"""
            QFrame {{
                background-color: qlineargradient(
                    x1:0, y1:0, x2:0, y2:1,
                    stop:0 {COLOR_WHITE}, stop:1 {COLOR_SURFACE_SOFT}
                );
                border-bottom: 1px solid #d7e2f2;
            }}
        """)
        top_bar_frame.setLayout(top_bar_layout)
        top_bar_frame.setMinimumHeight(74)
        top_bar_frame.setMaximumHeight(74)
        right_panel_layout.addWidget(top_bar_frame)
        
        # ===== TAB WIDGET =====
        self.tabs = QTabWidget()
        self.tabs.setDocumentMode(True)
        
        # Tab 0: Beranda (Home/Dashboard)
        self.beranda_tab = BerandaTab(self.user_id, self.username)
        self.beranda_tab.navigate_to_tab.connect(self.on_sidebar_nav_clicked)
        self.tabs.addTab(self.beranda_tab, "🏠 Beranda")
        
        # Tab 1: Beasiswa
        self.beasiswa_tab = BeasiswaTab(self.user_id, self.signals)
        self.tabs.addTab(self.beasiswa_tab, "📚 Beasiswa")
        
        # Tab 2: Tracker
        self.tracker_tab = TrackerTab(self.user_id, self.signals)
        self.tabs.addTab(self.tracker_tab, "📋 Tracker Lamaran")
        
        # Tab 3: Statistik
        self.statistik_tab = StatistikTab(self.user_id)
        self.tabs.addTab(self.statistik_tab, "📊 Statistik")
        self.tabs.setDocumentMode(True)
        self.tabs.setStyleSheet("QTabBar::tab { min-width: 120px; }")
        
        # Tab 4: Profil
        self.profil_tab = ProfileTab(self.user_id, self.username, event_bus=self.signals)
        self.tabs.addTab(self.profil_tab, "👤 Profil")
        
        # Hide tab bar (navigation is in sidebar)
        self.tabs.tabBar().hide()
        
        right_panel_layout.addWidget(self.tabs)
        
        # Create right panel widget
        right_panel_widget = QWidget()
        right_panel_widget.setStyleSheet(f"background-color: {COLOR_SURFACE_APP};")
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

    def _handle_data_changed(self, topic: str):
        """Refresh tabs and shell widgets after data mutations."""
        if topic in {"beasiswa.updated", "favorit.updated", "lamaran.updated", "profile.updated"}:
            if hasattr(self.beranda_tab, "load_dashboard_data"):
                self.beranda_tab.load_dashboard_data()

        if topic in {"beasiswa.updated", "favorit.updated"} and hasattr(self.beasiswa_tab, "refresh_data"):
            self.beasiswa_tab.refresh_data()

        if topic in {"lamaran.updated", "profile.updated"} and hasattr(self.tracker_tab, "load_applications"):
            self.tracker_tab.load_applications()

        if topic == "profile.updated":
            self.username = getattr(self.profil_tab, "username", self.username) or self.username
            self.user_label.setText(f"👤 {self.username}")
            self.setWindowTitle(f"BeasiswaKu - {self.username}")
        
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
        self.setStyleSheet(f"""
            QDialog {{
                background-color: {COLOR_SURFACE_SOFT};
                font-family: {FONT_FAMILY_PRIMARY};
            }}
            QLabel {{
                color: {COLOR_GRAY_700};
            }}
            QLabel#titleLabel {{
                color: {COLOR_COBALT_DARK};
                font-weight: 700;
            }}
            QLabel#infoPanel {{
                padding: 12px;
                background-color: {COLOR_WHITE};
                border-left: 4px solid {COLOR_AMBER};
                border-radius: 8px;
                border: 1px solid #d7e2f2;
                color: {COLOR_COBALT_DARK};
            }}
            QLabel#sectionLabel {{
                color: {COLOR_COBALT};
                font-weight: 700;
            }}
            QLabel#messageLabel {{
                min-height: 20px;
                font-weight: 600;
            }}
            QLineEdit {{
                background-color: {COLOR_WHITE};
                border: 1px solid {COLOR_GRAY_200};
                border-radius: 8px;
                padding: 8px 10px;
                color: {COLOR_GRAY_900};
            }}
            QLineEdit:focus {{
                border: 1px solid {COLOR_COBALT};
            }}
            QPushButton {{
                border-radius: 8px;
                padding: 8px 14px;
                font-weight: 600;
            }}
            QPushButton#primaryAction {{
                background-color: {COLOR_COBALT};
                color: {COLOR_WHITE};
                border: 1px solid {COLOR_COBALT_DARK};
            }}
            QPushButton#primaryAction:hover {{
                background-color: {COLOR_COBALT_LIGHT};
            }}
            QPushButton#neutralAction {{
                background-color: {COLOR_WHITE};
                color: {COLOR_GRAY_700};
                border: 1px solid #d7e1f1;
            }}
            QPushButton#neutralAction:hover {{
                background-color: #f7fbff;
                border: 1px solid #c5d6ed;
            }}
        """)
        
        layout = QVBoxLayout()
        layout.setContentsMargins(16, 16, 16, 16)
        layout.setSpacing(12)
        
        # Title
        title = QLabel("⚙️ Pengaturan Akun")
        title.setObjectName("titleLabel")
        title.setFont(QFont("Trebuchet MS", FONT_SIZE_LG, QFont.Weight.Bold))
        layout.addWidget(title)
        
        layout.addSpacing(10)
        
        # Info user
        info_label = QLabel(f"👤 Username: {self.username}\n📌 User ID: {self.user_id}")
        info_label.setObjectName("infoPanel")
        info_label.setFont(QFont("Trebuchet MS", FONT_SIZE_SM))
        layout.addWidget(info_label)
        
        layout.addSpacing(15)
        
        # Ganti Password Section
        pwd_label = QLabel("🔐 Ganti Password")
        pwd_label.setObjectName("sectionLabel")
        pwd_label.setFont(QFont("Trebuchet MS", FONT_SIZE_MD, QFont.Weight.Bold))
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
        save_pwd_btn.setObjectName("primaryAction")
        save_pwd_btn.clicked.connect(self.save_password)
        btn_layout.addWidget(save_pwd_btn)
        
        layout.addLayout(btn_layout)
        layout.addSpacing(15)
        
        # Message label
        self.message_label = QLabel("")
        self.message_label.setObjectName("messageLabel")
        layout.addWidget(self.message_label)
        
        layout.addStretch()
        
        # Close button
        close_btn = QPushButton("✖️ Tutup")
        close_btn.setObjectName("neutralAction")
        close_btn.clicked.connect(self.accept)
        layout.addWidget(close_btn)
        
        self.setLayout(layout)
    
    def save_password(self):
        """Save new password"""
        old_pwd = self.old_pwd.text()
        new_pwd = self.new_pwd.text()
        
        if not old_pwd or not new_pwd:
            self.message_label.setText("❌ Password tidak boleh kosong!")
            self.message_label.setStyleSheet(f"color: {COLOR_ERROR}; font-weight: 600;")
            return
        
        if len(new_pwd) < 6:
            self.message_label.setText("❌ Password minimal 6 karakter!")
            self.message_label.setStyleSheet(f"color: {COLOR_ERROR}; font-weight: 600;")
            return
        
        try:
            conn = get_connection()
            cursor = conn.cursor()
            
            # Check old password
            cursor.execute("SELECT password_hash FROM akun WHERE id = ?", (self.user_id,))
            result = cursor.fetchone()
            
            if result is None or not verify_password(old_pwd, result[0]):
                self.message_label.setText("❌ Password lama salah!")
                self.message_label.setStyleSheet(f"color: {COLOR_ERROR}; font-weight: 600;")
                return
            
            # Update password
            new_password_hash = hash_password(new_pwd)
            cursor.execute(
                "UPDATE akun SET password_hash = ?, updated_at = CURRENT_TIMESTAMP WHERE id = ?",
                (new_password_hash, self.user_id)
            )
            conn.commit()
            
            self.message_label.setText("✅ Password berhasil diubah!")
            self.message_label.setStyleSheet(f"color: {COLOR_SUCCESS}; font-weight: 600;")
            
            # Clear inputs
            self.old_pwd.clear()
            self.new_pwd.clear()
            
            logger.info(f"[SUCCESS] Password for user {self.username} changed")
        
        except Exception as e:
            self.message_label.setText(f"❌ Error: {str(e)}")
            self.message_label.setStyleSheet(f"color: {COLOR_ERROR}; font-weight: 600;")
            logger.error(f"Error changing password: {e}")


# ==================== APPLICATION ENTRY POINT ====================

def main():
    """Main entry point aplikasi"""
    # Setup centralized logging (MUST be first)
    setup_logging()
    logger = logging.getLogger(__name__)
    
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
