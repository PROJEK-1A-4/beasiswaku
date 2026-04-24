"""
Profil (Profile) Tab for BeasiswaKu
User profile management dengan layout yang rapi dan terstruktur
"""

import logging
import re
from datetime import datetime

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QLineEdit,
    QFrame, QScrollArea, QGridLayout, QCheckBox, QMessageBox
)
from PyQt6.QtCore import Qt, QSize
from PyQt6.QtGui import QFont, QColor

from src.gui.design_tokens import *
from src.gui.styles import get_button_solid_stylesheet
from src.database.crud import get_connection, update_user_password, update_user_profile

logger = logging.getLogger(__name__)


class ProfileTab(QWidget):
    """
    Profil Tab dengan 2-column layout:
    - Left: Profile card dengan avatar, stats, info dasar
    - Right: Detailed sections (Informasi Pribadi, Keamanan, Preferensi, Aktivitas)
    """
    
    def __init__(self, user_id: int, username: str = "", email: str = "", event_bus=None, parent=None):
        super().__init__(parent)
        self.user_id = user_id
        self.username = username
        self.email = email
        self.event_bus = event_bus
        self.user_data = {}
        self.profile_fields = {}
        self.editable_profile_field_keys = {"nama_lengkap", "email", "username", "jenjang"}
        self.profile_edit_mode = False
        self.current_password_input = None
        self.new_password_input = None
        self.confirm_password_input = None
        
        logger.info(f"Initializing ProfileTab for user {user_id}")
        self.load_user_data()
        self.init_ui()
    
    def init_ui(self):
        """Initialize Profile Tab dengan 2-column layout."""
        self.setObjectName("profileTabRoot")
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
        scroll_widget.setObjectName("profileScrollContent")
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

        self.setStyleSheet(f"""
            QWidget#profileTabRoot {{
                background-color: {COLOR_GRAY_BACKGROUND};
            }}
            QWidget#profileScrollContent {{
                background-color: transparent;
            }}
            QLabel {{
                background: transparent;
                border: none;
            }}
        """)
    
    def _create_profile_card(self) -> QFrame:
        """Create left column profile card."""
        frame = QFrame()
        frame.setObjectName("profileCard")
        frame.setStyleSheet(f"""
            QFrame#profileCard {{
                background-color: {COLOR_WHITE};
                border: 1px solid {COLOR_GRAY_200};
                border-radius: {BORDER_RADIUS_MD};
            }}
            QFrame#profileCard QFrame#profileDivider {{
                background-color: {COLOR_GRAY_200};
                border: none;
                min-height: 1px;
                max-height: 1px;
            }}
            QFrame#profileCard QFrame#profileInfoRow {{
                background: transparent;
                border: none;
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
        university_label = QLabel("Institusi belum disinkronkan")
        university_label.setFont(QFont(FONT_FAMILY_PRIMARY, FONT_SIZE_SM))
        university_label.setStyleSheet(f"color: {COLOR_GRAY_500}; text-align: center;")
        university_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(university_label)
        
        # Divider
        divider = QFrame()
        divider.setObjectName("profileDivider")
        divider.setMaximumHeight(1)
        layout.addWidget(divider)
        
        # ===== STATS =====
        stats_layout = QGridLayout()
        stats_layout.setSpacing(16)
        stats_layout.setContentsMargins(0, 0, 0, 0)
        
        # Lamaran
        lamaran_num = QLabel("-")
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
        diterima_num = QLabel("-")
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
        favorit_num = QLabel("-")
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
        divider2.setObjectName("profileDivider")
        divider2.setMaximumHeight(1)
        layout.addWidget(divider2)
        
        # ===== DETAILS =====
        details_layout = QVBoxLayout()
        details_layout.setSpacing(8)
        details_layout.setContentsMargins(0, 0, 0, 0)

        join_display = "Januari 2026"
        created_at = self.user_data.get("created_at")
        if created_at:
            try:
                parsed = datetime.strptime(str(created_at).split(" ")[0], "%Y-%m-%d")
                join_display = parsed.strftime("%B %Y")
            except ValueError:
                pass

        details_layout.addWidget(
            self._create_profile_info_row("👤", "Username", self.username or "-")
        )
        details_layout.addWidget(
            self._create_profile_info_row("✉", "Email", self.email or "-")
        )
        details_layout.addWidget(
            self._create_profile_info_row("📅", "Bergabung", join_display)
        )
        details_layout.addWidget(
            self._create_profile_info_row("🔐", "Status Akun", "Aktif", badge=True)
        )
        
        layout.addLayout(details_layout)
        layout.addStretch()
        
        return frame
    
    def _create_informasi_pribadi(self) -> QFrame:
        """Create Informasi Pribadi section."""
        frame = QFrame()
        frame.setObjectName("informasiPribadiCard")
        frame.setStyleSheet(f"""
            QFrame#informasiPribadiCard {{
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
        edit_btn.clicked.connect(self._on_edit_profile_clicked)
        header_layout.addWidget(edit_btn)
        layout.addLayout(header_layout)
        
        # Form Grid (2 columns, aligned rows)
        form_layout = QGridLayout()
        form_layout.setSpacing(16)
        form_layout.setContentsMargins(0, 0, 0, 0)

        nama_lengkap = self.user_data.get("nama_lengkap") or self.username or "-"
        username = self.user_data.get("username") or self.username or "-"
        email = self.user_data.get("email") or self.email or "-"
        jenjang = self.user_data.get("jenjang") or "-"

        left_fields = [
            ("NAMA LENGKAP", nama_lengkap),
            ("EMAIL", email),
            ("INSTITUSI", "POLBAN"),
            ("SEMESTER", "Semester 2"),
        ]
        right_fields = [
            ("USERNAME", username),
            ("JENJANG", jenjang),
            ("NIM", "21524003"),
        ]

        for idx, (label, value) in enumerate(left_fields):
            row = idx * 2
            form_layout.addWidget(self._create_form_label(label), row, 0)
            field = QLineEdit()
            field.setText(str(value))
            field.setReadOnly(True)
            field.setMinimumHeight(40)
            field.setStyleSheet(self._get_input_stylesheet())
            form_layout.addWidget(field, row + 1, 0)
            # Store field reference in profile_fields dict
            field_key = label.lower().replace(" ", "_")
            self.profile_fields[field_key] = field

        for idx, (label, value) in enumerate(right_fields):
            row = idx * 2
            form_layout.addWidget(self._create_form_label(label), row, 1)
            field = QLineEdit()
            field.setText(str(value))
            field.setReadOnly(True)
            field.setMinimumHeight(40)
            field.setStyleSheet(self._get_input_stylesheet())
            form_layout.addWidget(field, row + 1, 1)
            # Store field reference in profile_fields dict
            field_key = label.lower().replace(" ", "_")
            self.profile_fields[field_key] = field
        self._set_profile_edit_mode(False)
        
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
        save_btn.clicked.connect(self._on_save_profile_clicked)
        layout.addWidget(save_btn)
        
        return frame
    
    def _create_keamanan_akun(self) -> QFrame:
        """Create Keamanan Akun section."""
        frame = QFrame()
        frame.setObjectName("keamananCard")
        frame.setStyleSheet(f"""
            QFrame#keamananCard {{
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
        form_layout.addWidget(self._create_form_label("PASSWORD SAAT INI"))
        current_pass = QLineEdit()
        current_pass.setEchoMode(QLineEdit.EchoMode.Password)
        current_pass.setPlaceholderText("Masukkan password saat ini")
        current_pass.setMinimumHeight(40)
        current_pass.setStyleSheet(self._get_input_stylesheet())
        form_layout.addWidget(current_pass)
        self.current_password_input = current_pass
        
        # New password
        form_layout.addWidget(self._create_form_label("PASSWORD BARU"))
        new_pass = QLineEdit()
        new_pass.setPlaceholderText("Min. 8 karakter")
        new_pass.setMinimumHeight(40)
        new_pass.setStyleSheet(self._get_input_stylesheet())
        form_layout.addWidget(new_pass)
        self.new_password_input = new_pass
        
        # Confirm password
        form_layout.addWidget(self._create_form_label("KONFIRMASI"))
        confirm_pass = QLineEdit()
        confirm_pass.setPlaceholderText("Ulangi password")
        confirm_pass.setMinimumHeight(40)
        confirm_pass.setStyleSheet(self._get_input_stylesheet())
        form_layout.addWidget(confirm_pass)
        self.confirm_password_input = confirm_pass
        
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
        change_btn.clicked.connect(self._on_change_password_clicked)
        layout.addWidget(change_btn)
        
        return frame
    
    def _create_preferensi_aplikasi(self) -> QFrame:
        """Create Preferensi Aplikasi section."""
        frame = QFrame()
        frame.setObjectName("preferensiCard")
        frame.setStyleSheet(f"""
            QFrame#preferensiCard {{
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
        
        layout.addSpacing(8)
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
        
        layout.addSpacing(8)
        layout.addLayout(scrape_row)
        
        scrape_desc = QLabel("Perbarui data beasiswa otomatis saat buka app")
        scrape_desc.setFont(QFont(FONT_FAMILY_PRIMARY, FONT_SIZE_SM))
        scrape_desc.setStyleSheet(f"color: {COLOR_GRAY_500}; margin-left: 28px;")
        layout.addWidget(scrape_desc)
        
        return frame
    
    def _create_aktivitas_terakhir(self) -> QFrame:
        """Create Aktivitas Terakhir section."""
        frame = QFrame()
        frame.setObjectName("aktivitasCard")
        frame.setStyleSheet(f"""
            QFrame#aktivitasCard {{
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

    def _create_form_label(self, text: str) -> QLabel:
        """Create consistent form label style for profile sections."""
        label = QLabel(text)
        label.setFont(QFont(FONT_FAMILY_PRIMARY, FONT_SIZE_SM))
        label.setStyleSheet(f"color: {COLOR_GRAY_700}; font-weight: bold;")
        return label

    def _create_profile_info_row(self, icon: str, label_text: str, value_text: str, badge: bool = False) -> QFrame:
        """Create compact info row for profile card details."""
        row = QFrame()
        row.setObjectName("profileInfoRow")

        row_layout = QHBoxLayout(row)
        row_layout.setContentsMargins(0, 2, 0, 2)
        row_layout.setSpacing(8)

        icon_label = QLabel(icon)
        icon_label.setFont(QFont(FONT_FAMILY_PRIMARY, 13))
        row_layout.addWidget(icon_label)

        label = QLabel(label_text)
        label.setFont(QFont(FONT_FAMILY_PRIMARY, FONT_SIZE_SM))
        label.setStyleSheet(f"color: {COLOR_GRAY_600};")
        row_layout.addWidget(label)
        row_layout.addStretch()

        value = QLabel(value_text)
        value.setFont(QFont(FONT_FAMILY_PRIMARY, FONT_SIZE_BASE))
        if badge:
            value.setStyleSheet(
                f"color: {COLOR_SUCCESS}; font-weight: 700; "
                f"background-color: {COLOR_SUCCESS_LIGHT}; border-radius: 6px; "
                "padding: 4px 10px;"
            )
        else:
            value.setStyleSheet(f"color: {COLOR_NAVY}; font-weight: 700;")
        row_layout.addWidget(value)

        return row
    
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
                self._sync_profile_fields_from_user_data()
                logger.info(f"Loaded user data for {self.username}")
            else:
                logger.warning(f"User data not found for user_id={self.user_id}")
        except Exception as e:
            logger.error(f"Error loading user data: {e}")
        finally:
            if cursor is not None:
                cursor.close()

    def _sync_profile_fields_from_user_data(self):
        """Push loaded user data into visible form fields."""
        if not self.profile_fields:
            return

        field_value_map = {
            "nama_lengkap": self.user_data.get("nama_lengkap") or self.user_data.get("username") or self.username or "-",
            "email": self.user_data.get("email") or self.email or "-",
            "username": self.user_data.get("username") or self.username or "-",
            "jenjang": self.user_data.get("jenjang") or "-",
        }

        for field_key, field_value in field_value_map.items():
            field = self.profile_fields.get(field_key)
            if field is not None:
                field.setText(str(field_value))

    def _set_profile_edit_mode(self, enabled: bool):
        """Toggle editable state for profile form fields."""
        self.profile_edit_mode = enabled
        for field_key, field in self.profile_fields.items():
            if field_key in self.editable_profile_field_keys:
                field.setReadOnly(not enabled)

        logger.info("Profile edit mode %s", "enabled" if enabled else "disabled")

    def _emit_data_changed(self, topic: str):
        """Notify other tabs that user-related data changed."""
        if self.event_bus is not None:
            self.event_bus.data_changed.emit(topic)

    def _on_edit_profile_clicked(self):
        """Enable all profile fields for editing."""
        self._set_profile_edit_mode(True)

    def _on_save_profile_clicked(self):
        """Validate and save profile data."""
        # Validate profile fields
        is_valid, error_msg = self._validate_profile_fields()
        if not is_valid:
            QMessageBox.warning(self, "Validasi Gagal", error_msg)
            return

        nama_field = self.profile_fields.get("nama_lengkap")
        email_field = self.profile_fields.get("email")
        username_field = self.profile_fields.get("username")
        jenjang_field = self.profile_fields.get("jenjang")

        if not all([nama_field, email_field, username_field, jenjang_field]):
            QMessageBox.warning(self, "Validasi Gagal", "Form profil belum siap.")
            return

        success, message = update_user_profile(
            self.user_id,
            username_field.text().strip(),
            email_field.text().strip(),
            nama_field.text().strip(),
            jenjang_field.text().strip(),
        )
        if not success:
            QMessageBox.warning(self, "Gagal Menyimpan", message)
            return

        self.load_user_data()
        self._set_profile_edit_mode(False)
        QMessageBox.information(self, "Berhasil", message)
        self._emit_data_changed("profile.updated")
        logger.info("Profile update completed for user_id=%s", self.user_id)

    def _on_change_password_clicked(self):
        """Validate and change password."""
        # Validate password fields
        is_valid, error_msg = self._validate_password_fields()
        if not is_valid:
            QMessageBox.warning(self, "Validasi Gagal", error_msg)
            return

        success, message = update_user_password(
            self.user_id,
            self.current_password_input.text().strip(),
            self.new_password_input.text().strip(),
        )
        if not success:
            QMessageBox.warning(self, "Gagal Mengubah Password", message)
            return

        # Clear password fields
        self.current_password_input.setText("")
        self.new_password_input.setText("")
        self.confirm_password_input.setText("")
        QMessageBox.information(self, "Berhasil", message)
        self._emit_data_changed("profile.updated")
        logger.info("Password update completed for user_id=%s", self.user_id)
    
    def _validate_profile_fields(self) -> tuple[bool, str]:
        """Validate profile fields. Returns (is_valid, error_message)."""
        # Get field values
        nama_field = self.profile_fields.get("nama_lengkap")
        email_field = self.profile_fields.get("email")
        username_field = self.profile_fields.get("username")
        jenjang_field = self.profile_fields.get("jenjang")
        if not all([nama_field, email_field, username_field, jenjang_field]):
            return False, "Form profil belum siap."

        nama = nama_field.text().strip()
        email = email_field.text().strip()
        username = username_field.text().strip()
        jenjang = jenjang_field.text().strip()
        
        # Validate nama is not empty
        if not nama:
            return False, "Nama lengkap tidak boleh kosong."

        if not username:
            return False, "Username tidak boleh kosong."

        if not jenjang:
            return False, "Jenjang tidak boleh kosong."
        
        # Validate email format
        email_pattern = r'^[^@]+@[^@]+\.[^@]+$'
        if not re.match(email_pattern, email):
            return False, "Format email tidak valid."
        
        return True, ""
    
    def _validate_password_fields(self) -> tuple[bool, str]:
        """Validate password fields. Returns (is_valid, error_message)."""
        current_pwd = self.current_password_input.text().strip()
        new_pwd = self.new_password_input.text().strip()
        confirm_pwd = self.confirm_password_input.text().strip()
        
        # Validate current password is not empty
        if not current_pwd or current_pwd == "••••••••":
            return False, "Password saat ini harus diisi."
        
        # Validate new password is not empty
        if not new_pwd:
            return False, "Password baru tidak boleh kosong."
        
        # Validate new password min 8 chars
        if len(new_pwd) < 8:
            return False, "Password baru minimal 8 karakter."
        
        # Validate passwords match
        if new_pwd != confirm_pwd:
            return False, "Password baru tidak cocok dengan konfirmasi."
        
        return True, ""
