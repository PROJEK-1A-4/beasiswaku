"""
Profil (Profile) Tab for BeasiswaKu
User profile management dengan layout yang rapi dan terstruktur
"""

import logging
from datetime import datetime

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QLineEdit,
    QFrame, QScrollArea, QGridLayout, QCheckBox
)
from PyQt6.QtCore import Qt, QSize
from PyQt6.QtGui import QFont, QColor

from src.gui.design_tokens import *
from src.gui.styles import get_button_solid_stylesheet
from src.database.crud import get_connection

logger = logging.getLogger(__name__)


class ProfileTab(QWidget):
    """
    Profil Tab dengan 2-column layout:
    - Left: Profile card dengan avatar, stats, info dasar
    - Right: Detailed sections (Informasi Pribadi, Keamanan, Preferensi, Aktivitas)
    """
    
    def __init__(self, user_id: int, username: str = "", email: str = "", parent=None):
        super().__init__(parent)
        self.user_id = user_id
        self.username = username
        self.email = email
        self.user_data = {}
        
        logger.info(f"Initializing ProfileTab for user {user_id}")
        self.load_user_data()
        self.init_ui()
    
    def init_ui(self):
        """Initialize Profile Tab dengan 2-column layout."""
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(24, 20, 24, 20)
        main_layout.setSpacing(0)
        
        # ===== HEADER =====
        header_layout = QVBoxLayout()
        header_layout.setSpacing(4)
        header_layout.setContentsMargins(0, 0, 0, 0)
        
        title_label = QLabel("Profil Saya")
        title_font = QFont(FONT_FAMILY_PRIMARY, 28)
        title_font.setWeight(QFont.Weight.Bold)
        title_label.setFont(title_font)
        title_label.setStyleSheet(f"color: {COLOR_NAVY}; padding: 0px;")
        header_layout.addWidget(title_label)
        
        subtitle_label = QLabel("Kelola informasi akun dan preferensi kamu")
        subtitle_label.setFont(QFont(FONT_FAMILY_PRIMARY, FONT_SIZE_BASE))
        subtitle_label.setStyleSheet(f"color: {COLOR_GRAY_400}; padding: 0px;")
        header_layout.addWidget(subtitle_label)
        
        main_layout.addLayout(header_layout)
        main_layout.addSpacing(20)
        
        # ===== SCROLL AREA =====
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setStyleSheet(f"border: none; background-color: {COLOR_GRAY_BACKGROUND};")
        
        scroll_widget = QWidget()
        scroll_layout = QVBoxLayout(scroll_widget)
        scroll_layout.setContentsMargins(0, 0, 0, 0)
        scroll_layout.setSpacing(0)
        
        # ===== 2-COLUMN LAYOUT =====
        content_layout = QHBoxLayout()
        content_layout.setSpacing(24)
        content_layout.setContentsMargins(0, 0, 0, 0)
        
        # LEFT COLUMN - Profile Card
        left_frame = self._create_profile_card()
        content_layout.addWidget(left_frame, 1)
        
        # RIGHT COLUMN - Detailed Sections
        right_layout = QVBoxLayout()
        right_layout.setSpacing(24)
        right_layout.setContentsMargins(0, 0, 0, 0)
        
        # Informasi Pribadi Section
        right_layout.addWidget(self._create_informasi_pribadi())
        
        # Keamanan Akun Section
        right_layout.addWidget(self._create_keamanan_akun())
        
        # Preferensi Aplikasi Section
        right_layout.addWidget(self._create_preferensi_aplikasi())
        
        # Aktivitas Terakhir Section
        right_layout.addWidget(self._create_aktivitas_terakhir())
        
        right_layout.addStretch()
        
        content_layout.addLayout(right_layout, 2)
        
        scroll_layout.addLayout(content_layout)
        scroll_layout.addStretch()
        
        scroll.setWidget(scroll_widget)
        main_layout.addWidget(scroll)
        
        self.setStyleSheet(f"background-color: {COLOR_GRAY_BACKGROUND};")
    
    def _create_profile_card(self) -> QFrame:
        """Create left column profile card."""
        frame = QFrame()
        frame.setStyleSheet(f"""
            QFrame {{
                background-color: {COLOR_WHITE};
                border: 1px solid {COLOR_GRAY_200};
                border-radius: {BORDER_RADIUS_MD};
            }}
        """)
        
        layout = QVBoxLayout(frame)
        layout.setContentsMargins(24, 24, 24, 24)
        layout.setSpacing(16)
        
        # ===== AVATAR & NAME =====
        avatar_label = QLabel()
        avatar_label.setText(self._get_initials())
        avatar_label.setFont(QFont(FONT_FAMILY_PRIMARY, 32))
        avatar_label.setStyleSheet(f"""
            QLabel {{
                background-color: {COLOR_ORANGE};
                color: {COLOR_WHITE};
                border-radius: 64px;
                font-weight: bold;
            }}
        """)
        avatar_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        avatar_label.setMinimumSize(QSize(128, 128))
        avatar_label.setMaximumSize(QSize(128, 128))
        layout.addWidget(avatar_label, alignment=Qt.AlignmentFlag.AlignHCenter)
        
        # Name
        name_label = QLabel(self.username or "Aulia Rahmi")
        name_font = QFont(FONT_FAMILY_PRIMARY, 18)
        name_font.setWeight(QFont.Weight.Bold)
        name_label.setFont(name_font)
        name_label.setStyleSheet(f"color: {COLOR_NAVY}; text-align: center;")
        name_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(name_label)
        
        # Level/status
        level_label = QLabel("Mahasiswa D4")
        level_label.setFont(QFont(FONT_FAMILY_PRIMARY, FONT_SIZE_BASE))
        level_label.setStyleSheet(f"color: {COLOR_GRAY_600}; text-align: center;")
        level_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(level_label)
        
        # University
        university_label = QLabel("Teknik Informatika - POLBAN")
        university_label.setFont(QFont(FONT_FAMILY_PRIMARY, FONT_SIZE_SM))
        university_label.setStyleSheet(f"color: {COLOR_GRAY_500}; text-align: center;")
        university_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(university_label)
        
        # Divider
        divider = QFrame()
        divider.setStyleSheet(f"background-color: {COLOR_GRAY_200};")
        divider.setMaximumHeight(1)
        layout.addWidget(divider)
        
        # ===== STATS =====
        stats_layout = QGridLayout()
        stats_layout.setSpacing(16)
        stats_layout.setContentsMargins(0, 0, 0, 0)
        
        # Lamaran
        lamaran_num = QLabel("9")
        lamaran_num.setFont(QFont(FONT_FAMILY_PRIMARY, FONT_SIZE_2XL))
        lamaran_num.setStyleSheet(f"color: {COLOR_NAVY}; font-weight: bold;")
        lamaran_num.setAlignment(Qt.AlignmentFlag.AlignCenter)
        stats_layout.addWidget(lamaran_num, 0, 0)
        
        lamaran_label = QLabel("Lamaran")
        lamaran_label.setFont(QFont(FONT_FAMILY_PRIMARY, FONT_SIZE_SM))
        lamaran_label.setStyleSheet(f"color: {COLOR_GRAY_600};")
        lamaran_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        stats_layout.addWidget(lamaran_label, 1, 0)
        
        # Diterima
        diterima_num = QLabel("2")
        diterima_num.setFont(QFont(FONT_FAMILY_PRIMARY, FONT_SIZE_2XL))
        diterima_num.setStyleSheet(f"color: {COLOR_SUCCESS}; font-weight: bold;")
        diterima_num.setAlignment(Qt.AlignmentFlag.AlignCenter)
        stats_layout.addWidget(diterima_num, 0, 1)
        
        diterima_label = QLabel("Diterima")
        diterima_label.setFont(QFont(FONT_FAMILY_PRIMARY, FONT_SIZE_SM))
        diterima_label.setStyleSheet(f"color: {COLOR_GRAY_600};")
        diterima_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        stats_layout.addWidget(diterima_label, 1, 1)
        
        # Favorit
        favorit_num = QLabel("12")
        favorit_num.setFont(QFont(FONT_FAMILY_PRIMARY, FONT_SIZE_2XL))
        favorit_num.setStyleSheet(f"color: {COLOR_ORANGE}; font-weight: bold;")
        favorit_num.setAlignment(Qt.AlignmentFlag.AlignCenter)
        stats_layout.addWidget(favorit_num, 0, 2)
        
        favorit_label = QLabel("Favorit")
        favorit_label.setFont(QFont(FONT_FAMILY_PRIMARY, FONT_SIZE_SM))
        favorit_label.setStyleSheet(f"color: {COLOR_GRAY_600};")
        favorit_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        stats_layout.addWidget(favorit_label, 1, 2)
        
        layout.addLayout(stats_layout)
        
        # Divider
        divider2 = QFrame()
        divider2.setStyleSheet(f"background-color: {COLOR_GRAY_200};")
        divider2.setMaximumHeight(1)
        layout.addWidget(divider2)
        
        # ===== DETAILS =====
        details_layout = QVBoxLayout()
        details_layout.setSpacing(12)
        details_layout.setContentsMargins(0, 0, 0, 0)
        
        # Username
        username_row = QHBoxLayout()
        username_icon = QLabel("👤")
        username_icon.setFont(QFont(FONT_FAMILY_PRIMARY, 14))
        username_row.addWidget(username_icon)
        username_label = QLabel("Username")
        username_label.setFont(QFont(FONT_FAMILY_PRIMARY, FONT_SIZE_SM))
        username_label.setStyleSheet(f"color: {COLOR_GRAY_600};")
        username_row.addWidget(username_label)
        details_layout.addLayout(username_row)
        
        username_value = QLabel(self.username or "aulia_rahmi")
        username_value.setFont(QFont(FONT_FAMILY_PRIMARY, FONT_SIZE_BASE))
        username_value.setStyleSheet(f"color: {COLOR_NAVY}; font-weight: bold; margin-left: 28px;")
        details_layout.addWidget(username_value)
        
        # Email
        email_row = QHBoxLayout()
        email_icon = QLabel("✉")
        email_icon.setFont(QFont(FONT_FAMILY_PRIMARY, 14))
        email_row.addWidget(email_icon)
        email_label = QLabel("Email")
        email_label.setFont(QFont(FONT_FAMILY_PRIMARY, FONT_SIZE_SM))
        email_label.setStyleSheet(f"color: {COLOR_GRAY_600};")
        email_row.addWidget(email_label)
        details_layout.addLayout(email_row)
        
        email_value = QLabel(self.email or "aulia@email.com")
        email_value.setFont(QFont(FONT_FAMILY_PRIMARY, FONT_SIZE_BASE))
        email_value.setStyleSheet(f"color: {COLOR_NAVY}; font-weight: bold; margin-left: 28px;")
        details_layout.addWidget(email_value)
        
        # Bergabung
        join_row = QHBoxLayout()
        join_icon = QLabel("📅")
        join_icon.setFont(QFont(FONT_FAMILY_PRIMARY, 14))
        join_row.addWidget(join_icon)
        join_label = QLabel("Bergabung")
        join_label.setFont(QFont(FONT_FAMILY_PRIMARY, FONT_SIZE_SM))
        join_label.setStyleSheet(f"color: {COLOR_GRAY_600};")
        join_row.addWidget(join_label)
        details_layout.addLayout(join_row)
        
        join_value = QLabel("Januari 2026")
        join_value.setFont(QFont(FONT_FAMILY_PRIMARY, FONT_SIZE_BASE))
        join_value.setStyleSheet(f"color: {COLOR_NAVY}; font-weight: bold; margin-left: 28px;")
        details_layout.addWidget(join_value)
        
        # Status
        status_row = QHBoxLayout()
        status_icon = QLabel("🔐")
        status_icon.setFont(QFont(FONT_FAMILY_PRIMARY, 14))
        status_row.addWidget(status_icon)
        status_label = QLabel("Status Akun")
        status_label.setFont(QFont(FONT_FAMILY_PRIMARY, FONT_SIZE_SM))
        status_label.setStyleSheet(f"color: {COLOR_GRAY_600};")
        status_row.addWidget(status_label)
        details_layout.addLayout(status_row)
        
        status_badge = QLabel("Aktif")
        status_badge.setFont(QFont(FONT_FAMILY_PRIMARY, FONT_SIZE_SM))
        status_badge.setStyleSheet(f"""
            color: {COLOR_SUCCESS}; 
            font-weight: bold; 
            margin-left: 28px;
            background-color: {COLOR_SUCCESS_LIGHT};
            padding: 4px 8px;
            border-radius: 4px;
            width: fit-content;
        """)
        details_layout.addWidget(status_badge)
        
        layout.addLayout(details_layout)
        layout.addStretch()
        
        return frame
    
    def _create_informasi_pribadi(self) -> QFrame:
        """Create Informasi Pribadi section."""
        frame = QFrame()
        frame.setStyleSheet(f"""
            QFrame {{
                background-color: {COLOR_WHITE};
                border: 1px solid {COLOR_GRAY_200};
                border-radius: {BORDER_RADIUS_MD};
            }}
        """)
        
        layout = QVBoxLayout(frame)
        layout.setContentsMargins(24, 24, 24, 24)
        layout.setSpacing(16)
        
        # Header
        header_layout = QHBoxLayout()
        header_label = QLabel("Informasi Pribadi")
        header_font = QFont(FONT_FAMILY_PRIMARY, 16)
        header_font.setWeight(QFont.Weight.Bold)
        header_label.setFont(header_font)
        header_label.setStyleSheet(f"color: {COLOR_NAVY};")
        header_layout.addWidget(header_label)
        header_layout.addStretch()
        
        edit_btn = QPushButton("✏ Edit")
        edit_btn.setMinimumHeight(32)
        edit_btn.setMaximumWidth(100)
        edit_btn.setStyleSheet(f"""
            QPushButton {{
                background-color: transparent;
                border: 1px solid {COLOR_GRAY_300};
                border-radius: {BORDER_RADIUS_SM};
                color: {COLOR_NAVY};
                font-weight: bold;
                padding: 6px 12px;
            }}
            QPushButton:hover {{
                background-color: {COLOR_GRAY_100};
            }}
        """)
        header_layout.addWidget(edit_btn)
        layout.addLayout(header_layout)
        
        # Form Grid (2 columns)
        form_layout = QGridLayout()
        form_layout.setSpacing(16)
        form_layout.setContentsMargins(0, 0, 0, 0)
        
        # Nama Lengkap
        form_layout.addWidget(QLabel("NAMA LENGKAP"), 0, 0)
        nama_input = QLineEdit()
        nama_input.setText("Aulia Rahmi Taufik")
        nama_input.setReadOnly(True)
        nama_input.setMinimumHeight(40)
        nama_input.setStyleSheet(self._get_input_stylesheet())
        form_layout.addWidget(nama_input, 1, 0)
        
        # Username
        form_layout.addWidget(QLabel("USERNAME"), 1, 1)
        username_input = QLineEdit()
        username_input.setText("aulia_rahmi")
        username_input.setReadOnly(True)
        username_input.setMinimumHeight(40)
        username_input.setStyleSheet(self._get_input_stylesheet())
        form_layout.addWidget(username_input, 2, 1)
        
        # Email
        form_layout.addWidget(QLabel("EMAIL"), 2, 0)
        email_input = QLineEdit()
        email_input.setText("aulia.rahmi@gmail.com")
        email_input.setReadOnly(True)
        email_input.setMinimumHeight(40)
        email_input.setStyleSheet(self._get_input_stylesheet())
        form_layout.addWidget(email_input, 3, 0)
        
        # Jenjang
        form_layout.addWidget(QLabel("JENJANG"), 3, 1)
        jenjang_input = QLineEdit()
        jenjang_input.setText("D4 Sarjana Terapan")
        jenjang_input.setReadOnly(True)
        jenjang_input.setMinimumHeight(40)
        jenjang_input.setStyleSheet(self._get_input_stylesheet())
        form_layout.addWidget(jenjang_input, 4, 1)
        
        # Institusi
        form_layout.addWidget(QLabel("INSTITUSI"), 4, 0)
        institusi_input = QLineEdit()
        institusi_input.setText("POLBAN")
        institusi_input.setReadOnly(True)
        institusi_input.setMinimumHeight(40)
        institusi_input.setStyleSheet(self._get_input_stylesheet())
        form_layout.addWidget(institusi_input, 5, 0)
        
        # NIM
        form_layout.addWidget(QLabel("NIM"), 5, 1)
        nim_input = QLineEdit()
        nim_input.setText("21524003")
        nim_input.setReadOnly(True)
        nim_input.setMinimumHeight(40)
        nim_input.setStyleSheet(self._get_input_stylesheet())
        form_layout.addWidget(nim_input, 6, 1)
        
        # Semester
        form_layout.addWidget(QLabel("SEMESTER"), 6, 0)
        semester_input = QLineEdit()
        semester_input.setText("Semester 2")
        semester_input.setReadOnly(True)
        semester_input.setMinimumHeight(40)
        semester_input.setStyleSheet(self._get_input_stylesheet())
        form_layout.addWidget(semester_input, 7, 0)
        
        form_layout.setColumnStretch(0, 1)
        form_layout.setColumnStretch(1, 1)
        
        layout.addLayout(form_layout)
        
        # Save button
        save_btn = QPushButton("Simpan Perubahan")
        save_btn.setMinimumHeight(40)
        save_btn.setStyleSheet(f"""
            QPushButton {{
                background-color: {COLOR_NAVY};
                border: none;
                border-radius: {BORDER_RADIUS_SM};
                color: {COLOR_WHITE};
                font-weight: bold;
                font-size: 11px;
            }}
            QPushButton:hover {{
                background-color: {COLOR_NAVY_DARK};
            }}
        """)
        layout.addWidget(save_btn)
        
        return frame
    
    def _create_keamanan_akun(self) -> QFrame:
        """Create Keamanan Akun section."""
        frame = QFrame()
        frame.setStyleSheet(f"""
            QFrame {{
                background-color: {COLOR_WHITE};
                border: 1px solid {COLOR_GRAY_200};
                border-radius: {BORDER_RADIUS_MD};
            }}
        """)
        
        layout = QVBoxLayout(frame)
        layout.setContentsMargins(24, 24, 24, 24)
        layout.setSpacing(16)
        
        # Header
        title_label = QLabel("Keamanan Akun")
        title_font = QFont(FONT_FAMILY_PRIMARY, 16)
        title_font.setWeight(QFont.Weight.Bold)
        title_label.setFont(title_font)
        title_label.setStyleSheet(f"color: {COLOR_NAVY};")
        layout.addWidget(title_label)
        
        # Form
        form_layout = QGridLayout()
        form_layout.setSpacing(16)
        form_layout.setContentsMargins(0, 0, 0, 0)
        
        # Current password
        form_layout.addWidget(QLabel("PASSWORD SAAT INI"))
        current_pass = QLineEdit()
        current_pass.setEchoMode(QLineEdit.EchoMode.Password)
        current_pass.setText("••••••••")
        current_pass.setMinimumHeight(40)
        current_pass.setStyleSheet(self._get_input_stylesheet())
        form_layout.addWidget(current_pass)
        
        # New password
        form_layout.addWidget(QLabel("PASSWORD BARU"))
        new_pass = QLineEdit()
        new_pass.setPlaceholderText("Min. 8 karakter")
        new_pass.setMinimumHeight(40)
        new_pass.setStyleSheet(self._get_input_stylesheet())
        form_layout.addWidget(new_pass)
        
        # Confirm password
        form_layout.addWidget(QLabel("KONFIRMASI"))
        confirm_pass = QLineEdit()
        confirm_pass.setPlaceholderText("Ulangi password")
        confirm_pass.setMinimumHeight(40)
        confirm_pass.setStyleSheet(self._get_input_stylesheet())
        form_layout.addWidget(confirm_pass)
        
        layout.addLayout(form_layout)
        
        # Change password button
        change_btn = QPushButton("Ubah Password")
        change_btn.setMinimumHeight(40)
        change_btn.setStyleSheet(f"""
            QPushButton {{
                background-color: {COLOR_NAVY};
                border: none;
                border-radius: {BORDER_RADIUS_SM};
                color: {COLOR_WHITE};
                font-weight: bold;
                font-size: 11px;
            }}
            QPushButton:hover {{
                background-color: {COLOR_NAVY_DARK};
            }}
        """)
        layout.addWidget(change_btn)
        
        return frame
    
    def _create_preferensi_aplikasi(self) -> QFrame:
        """Create Preferensi Aplikasi section."""
        frame = QFrame()
        frame.setStyleSheet(f"""
            QFrame {{
                background-color: {COLOR_WHITE};
                border: 1px solid {COLOR_GRAY_200};
                border-radius: {BORDER_RADIUS_MD};
            }}
        """)
        
        layout = QVBoxLayout(frame)
        layout.setContentsMargins(24, 24, 24, 24)
        layout.setSpacing(16)
        
        # Header
        title_label = QLabel("Preferensi Aplikasi")
        title_font = QFont(FONT_FAMILY_PRIMARY, 16)
        title_font.setWeight(QFont.Weight.Bold)
        title_label.setFont(title_font)
        title_label.setStyleSheet(f"color: {COLOR_NAVY};")
        layout.addWidget(title_label)
        
        # Notifikasi Deadline
        notif_row = QHBoxLayout()
        notif_icon = QLabel("🔔")
        notif_icon.setFont(QFont(FONT_FAMILY_PRIMARY, 14))
        notif_row.addWidget(notif_icon)
        notif_label = QLabel("Notifikasi Deadline")
        notif_label.setFont(QFont(FONT_FAMILY_PRIMARY, FONT_SIZE_BASE))
        notif_row.addWidget(notif_label)
        notif_row.addStretch()
        
        toggle1 = QCheckBox()
        toggle1.setChecked(True)
        toggle1.setMinimumSize(40, 24)
        notif_row.addWidget(toggle1)
        
        layout.addLayout(notif_row)
        
        notif_desc = QLabel("Peringatan beasiswa yang akan tutup")
        notif_desc.setFont(QFont(FONT_FAMILY_PRIMARY, FONT_SIZE_SM))
        notif_desc.setStyleSheet(f"color: {COLOR_GRAY_500}; margin-left: 28px;")
        layout.addWidget(notif_desc)
        
        # Mode Gelap
        dark_row = QHBoxLayout()
        dark_icon = QLabel("🌙")
        dark_icon.setFont(QFont(FONT_FAMILY_PRIMARY, 14))
        dark_row.addWidget(dark_icon)
        dark_label = QLabel("Mode Gelap")
        dark_label.setFont(QFont(FONT_FAMILY_PRIMARY, FONT_SIZE_BASE))
        dark_row.addWidget(dark_label)
        dark_row.addStretch()
        
        toggle2 = QCheckBox()
        toggle2.setChecked(False)
        toggle2.setMinimumSize(40, 24)
        dark_row.addWidget(toggle2)
        
        layout.addWidget(QFrame())  # Spacer
        layout.addLayout(dark_row)
        
        dark_desc = QLabel("Tampilan gelap untuk kenyamanan mata")
        dark_desc.setFont(QFont(FONT_FAMILY_PRIMARY, FONT_SIZE_SM))
        dark_desc.setStyleSheet(f"color: {COLOR_GRAY_500}; margin-left: 28px;")
        layout.addWidget(dark_desc)
        
        # Auto-Scraping
        scrape_row = QHBoxLayout()
        scrape_icon = QLabel("📡")
        scrape_icon.setFont(QFont(FONT_FAMILY_PRIMARY, 14))
        scrape_row.addWidget(scrape_icon)
        scrape_label = QLabel("Auto-Scraping")
        scrape_label.setFont(QFont(FONT_FAMILY_PRIMARY, FONT_SIZE_BASE))
        scrape_row.addWidget(scrape_label)
        scrape_row.addStretch()
        
        toggle3 = QCheckBox()
        toggle3.setChecked(True)
        toggle3.setMinimumSize(40, 24)
        scrape_row.addWidget(toggle3)
        
        layout.addWidget(QFrame())  # Spacer
        layout.addLayout(scrape_row)
        
        scrape_desc = QLabel("Perbarui data beasiswa otomatis saat buka app")
        scrape_desc.setFont(QFont(FONT_FAMILY_PRIMARY, FONT_SIZE_SM))
        scrape_desc.setStyleSheet(f"color: {COLOR_GRAY_500}; margin-left: 28px;")
        layout.addWidget(scrape_desc)
        
        return frame
    
    def _create_aktivitas_terakhir(self) -> QFrame:
        """Create Aktivitas Terakhir section."""
        frame = QFrame()
        frame.setStyleSheet(f"""
            QFrame {{
                background-color: {COLOR_WHITE};
                border: 1px solid {COLOR_GRAY_200};
                border-radius: {BORDER_RADIUS_MD};
            }}
        """)
        
        layout = QVBoxLayout(frame)
        layout.setContentsMargins(24, 24, 24, 24)
        layout.setSpacing(12)
        
        # Header
        title_label = QLabel("Aktivitas Terakhir")
        title_font = QFont(FONT_FAMILY_PRIMARY, 16)
        title_font.setWeight(QFont.Weight.Bold)
        title_label.setFont(title_font)
        title_label.setStyleSheet(f"color: {COLOR_NAVY};")
        layout.addWidget(title_label)
        
        # Activities
        activities = [
            ("Lamaran Diterima", "Beasiswa Tanoto Foundation", "3 hari lalu", COLOR_SUCCESS),
            ("Favorit Ditambahkan", "Beasiswa Unggulan Kemendikbud", "5 hari lalu", COLOR_ORANGE),
            ("Lamaran Dikirim", "Beasiswa Bank Indonesia", "1 minggu lalu", COLOR_NAVY),
        ]
        
        for title, desc, time, color in activities:
            activity_layout = QHBoxLayout()
            activity_layout.setSpacing(12)
            
            # Dot indicator
            dot = QLabel("●")
            dot.setFont(QFont(FONT_FAMILY_PRIMARY, 12))
            dot.setStyleSheet(f"color: {color};")
            activity_layout.addWidget(dot)
            
            # Info
            info_layout = QVBoxLayout()
            info_layout.setSpacing(2)
            
            title_lbl = QLabel(title)
            title_lbl.setFont(QFont(FONT_FAMILY_PRIMARY, FONT_SIZE_BASE))
            title_lbl.setStyleSheet(f"color: {COLOR_NAVY}; font-weight: bold;")
            info_layout.addWidget(title_lbl)
            
            desc_lbl = QLabel(desc)
            desc_lbl.setFont(QFont(FONT_FAMILY_PRIMARY, FONT_SIZE_SM))
            desc_lbl.setStyleSheet(f"color: {COLOR_GRAY_600};")
            info_layout.addWidget(desc_lbl)
            
            activity_layout.addLayout(info_layout)
            activity_layout.addStretch()
            
            # Time
            time_lbl = QLabel(time)
            time_lbl.setFont(QFont(FONT_FAMILY_PRIMARY, FONT_SIZE_SM))
            time_lbl.setStyleSheet(f"color: {COLOR_GRAY_500};")
            activity_layout.addWidget(time_lbl)
            
            layout.addLayout(activity_layout)
        
        return frame
    
    def _get_input_stylesheet(self) -> str:
        """Get stylesheet for input fields."""
        return f"""
            QLineEdit {{
                padding: 10px 12px;
                border: 1px solid {COLOR_GRAY_200};
                border-radius: {BORDER_RADIUS_SM};
                background-color: {COLOR_WHITE};
                color: {COLOR_NAVY};
                font-size: 11px;
            }}
            QLineEdit:focus {{
                border: 2px solid {COLOR_ORANGE};
                padding: 9px 11px;
            }}
        """
    
    def _get_initials(self) -> str:
        """Get user initials."""
        if self.username:
            parts = self.username.split()
            if len(parts) >= 2:
                return (parts[0][0] + parts[-1][0]).upper()
            return self.username[0].upper()
        return "AR"
    
    def load_user_data(self):
        """Load user data from database."""
        try:
            conn = get_connection()
            cursor = conn.cursor()
            cursor.execute(
                """
                SELECT id, username, email, nama_lengkap, jenjang, created_at
                FROM akun
                WHERE id = ?
                """,
                (self.user_id,)
            )
            result = cursor.fetchone()
            if result:
                self.user_data = dict(result)
                self.username = result["username"] or self.username
                self.email = result["email"] or self.email
                logger.info(f"Loaded user data for {self.username}")
            else:
                logger.warning(f"User data not found for user_id={self.user_id}")
            cursor.close()
        except Exception as e:
            logger.error(f"Error loading user data: {e}")
