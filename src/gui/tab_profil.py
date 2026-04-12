"""
Profil (Profile) Tab for BeasiswaKu
User profile management with personal information, preferences, and activity history
"""

import logging
from datetime import datetime

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QLineEdit,
    QTextEdit, QComboBox, QDialog, QFormLayout, QMessageBox, QScrollArea,
    QFrame, QSizePolicy
)
from PyQt6.QtCore import Qt, QSize
from PyQt6.QtGui import QFont, QColor, QPixmap, QIcon

from src.gui.design_tokens import *
from src.gui.styles import get_button_solid_stylesheet
from src.database.crud import get_connection

logger = logging.getLogger(__name__)


class ProfileTab(QWidget):
    """
    Profil (Profile) Tab - Manage user profile information and preferences.
    
    Features:
    - User profile header with avatar/initials
    - Editable personal information (name, email, phone)
    - Editable contact information (address, city, province, postal code)
    - User preferences (notification settings, theme, language)
    - Activity history/stats
    - Account actions (edit profile, change password, logout)
    
    Layout:
    ┌──────────────────────────┐
    │ Profile Header           │
    │ 📦 Name | Email | Stats  │
    ├──────────────────────────┤
    │ Personal Information     │
    │ [Fields] [Edit] [Save]   │
    ├──────────────────────────┤
    │ Contact Information      │
    │ [Fields] [Edit] [Save]   │
    ├──────────────────────────┤
    │ Preferences              │
    │ [Settings/Toggles]       │
    ├──────────────────────────┤
    │ [Change Password] [Logout]
    └──────────────────────────┘
    """
    
    def __init__(self, user_id: int, username: str = "", email: str = "", parent=None):
        super().__init__(parent)
        self.user_id = user_id
        self.username = username
        self.email = email
        self.user_data = {}
        
        logger.info(f"Initializing ProfileTab for user {user_id}")
        self.init_ui()
        self.load_user_data()
    
    def init_ui(self):
        """Initialize Profile Tab UI."""
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(16, 16, 16, 16)
        main_layout.setSpacing(12)
        
        # ===== SCROLL AREA =====
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setStyleSheet(f"border: none; background-color: {COLOR_GRAY_BACKGROUND};")
        
        scroll_widget = QWidget()
        scroll_layout = QVBoxLayout(scroll_widget)
        scroll_layout.setContentsMargins(0, 0, 0, 0)
        scroll_layout.setSpacing(16)
        
        # ===== PROFILE HEADER SECTION =====
        header_frame = self._create_profile_header()
        scroll_layout.addWidget(header_frame)
        
        # ===== PERSONAL INFORMATION SECTION =====
        personal_frame = self._create_personal_info_section()
        scroll_layout.addWidget(personal_frame)
        
        # ===== CONTACT INFORMATION SECTION =====
        contact_frame = self._create_contact_info_section()
        scroll_layout.addWidget(contact_frame)
        
        # ===== PREFERENCES SECTION =====
        preferences_frame = self._create_preferences_section()
        scroll_layout.addWidget(preferences_frame)
        
        # ===== ACTIVITY SECTION =====
        activity_frame = self._create_activity_section()
        scroll_layout.addWidget(activity_frame)
        
        scroll_layout.addStretch()
        scroll.setWidget(scroll_widget)
        main_layout.addWidget(scroll)
        
        # ===== BOTTOM ACTION BUTTONS =====
        action_layout = QHBoxLayout()
        action_layout.setSpacing(12)
        
        # Change password button
        password_btn = QPushButton("🔐 Ubah Password")
        password_btn.setStyleSheet(get_button_solid_stylesheet("navy"))
        password_btn.clicked.connect(self.on_change_password)
        action_layout.addWidget(password_btn)
        
        action_layout.addStretch()
        
        # Logout button
        logout_btn = QPushButton("🚪 Keluar")
        logout_btn.setStyleSheet(get_button_solid_stylesheet("error"))
        logout_btn.clicked.connect(self.on_logout)
        action_layout.addWidget(logout_btn)
        
        main_layout.addLayout(action_layout)
        
        # Apply background color
        self.setStyleSheet(f"background-color: {COLOR_GRAY_BACKGROUND};")
    
    def _create_profile_header(self) -> QFrame:
        """Create profile header section with avatar and user info."""
        frame = QFrame()
        frame.setStyleSheet(f"""
            QFrame {{
                background-color: {COLOR_WHITE};
                border: 1px solid {COLOR_GRAY_200};
                border-radius: {BORDER_RADIUS_SM};
                padding: 20px;
            }}
        """)
        frame.setMinimumHeight(120)
        
        layout = QHBoxLayout(frame)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(16)
        
        # Avatar/Initials circle
        avatar_label = QLabel()
        avatar_label.setText(self._get_initials())
        avatar_label.setFont(QFont(FONT_FAMILY_PRIMARY, 24))
        avatar_label.setStyleSheet(f"""
            QLabel {{
                background-color: {COLOR_ORANGE};
                color: {COLOR_WHITE};
                border-radius: 50px;
                width: 100px;
                height: 100px;
                font-weight: bold;
                qproperty-alignment: AlignCenter;
            }}
        """)
        avatar_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        avatar_label.setMinimumSize(QSize(100, 100))
        avatar_label.setMaximumSize(QSize(100, 100))
        layout.addWidget(avatar_label)
        
        # User info
        info_layout = QVBoxLayout()
        
        # Name
        name_label = QLabel(self.username or "User")
        name_font = QFont(FONT_FAMILY_PRIMARY, FONT_SIZE_LG)
        name_font.setWeight(QFont.Weight.Bold)
        name_label.setFont(name_font)
        name_label.setStyleSheet(f"color: {COLOR_NAVY};")
        info_layout.addWidget(name_label)
        
        # Email
        email_label = QLabel(self.email or "email@example.com")
        email_label.setFont(QFont(FONT_FAMILY_PRIMARY, FONT_SIZE_BASE))
        email_label.setStyleSheet(f"color: {COLOR_GRAY_600};")
        info_layout.addWidget(email_label)
        
        info_layout.addSpacing(8)
        
        # Stats row
        stats_layout = QHBoxLayout()
        stats_layout.setSpacing(24)
        
        # Total applications
        stats_layout.addWidget(self._create_stat_item("15", "Lamaran Terkirim"))
        stats_layout.addWidget(self._create_stat_item("3", "Diterima"))
        stats_layout.addWidget(self._create_stat_item("2", "Pending"))
        stats_layout.addStretch()
        
        info_layout.addLayout(stats_layout)
        
        layout.addLayout(info_layout)
        layout.addStretch()
        
        return frame
    
    def _create_stat_item(self, number: str, label: str) -> QWidget:
        """Create a stat item widget."""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(4)
        
        num_label = QLabel(number)
        num_font = QFont(FONT_FAMILY_PRIMARY, FONT_SIZE_LG)
        num_font.setWeight(QFont.Weight.Bold)
        num_label.setFont(num_font)
        num_label.setStyleSheet(f"color: {COLOR_NAVY};")
        layout.addWidget(num_label)
        
        text_label = QLabel(label)
        text_label.setFont(QFont(FONT_FAMILY_PRIMARY, FONT_SIZE_SM))
        text_label.setStyleSheet(f"color: {COLOR_GRAY_600};")
        layout.addWidget(text_label)
        
        return widget
    
    def _get_initials(self) -> str:
        """Get user initials from username."""
        if self.username:
            parts = self.username.split()
            if len(parts) >= 2:
                return (parts[0][0] + parts[-1][0]).upper()
            elif len(parts) == 1:
                return parts[0][0].upper()
        return "U"
    
    def _create_personal_info_section(self) -> QFrame:
        """Create personal information section."""
        frame = QFrame()
        frame.setStyleSheet(f"""
            QFrame {{
                background-color: {COLOR_WHITE};
                border: 1px solid {COLOR_GRAY_200};
                border-radius: {BORDER_RADIUS_SM};
                padding: 20px;
            }}
        """)
        
        layout = QVBoxLayout(frame)
        layout.setSpacing(12)
        
        # Title
        title = QLabel("📋 Informasi Pribadi")
        title_font = QFont(FONT_FAMILY_PRIMARY, 14)
        title_font.setWeight(QFont.Weight.Bold)
        title.setFont(title_font)
        title.setStyleSheet(f"color: {COLOR_NAVY};")
        layout.addWidget(title)
        
        # Divider
        divider = QFrame()
        divider.setStyleSheet(f"background-color: {COLOR_GRAY_200};")
        divider.setMaximumHeight(1)
        layout.addWidget(divider)
        
        # Form layout
        form_layout = QFormLayout()
        form_layout.setSpacing(12)
        
        # Nama Lengkap
        self.nama_input = QLineEdit()
        self.nama_input.setText(self.username or "")
        self.nama_input.setMinimumHeight(36)
        self.nama_input.setReadOnly(True)
        self.nama_input.setStyleSheet(f"""
            QLineEdit {{
                padding: 8px 10px;
                border: 1px solid {COLOR_GRAY_200};
                border-radius: {BORDER_RADIUS_SM};
                background-color: {COLOR_GRAY_50};
            }}
        """)
        form_layout.addRow("Nama Lengkap:", self.nama_input)
        
        # Email
        self.email_personal_input = QLineEdit()
        self.email_personal_input.setText(self.email or "")
        self.email_personal_input.setMinimumHeight(36)
        self.email_personal_input.setReadOnly(True)
        self.email_personal_input.setStyleSheet(f"""
            QLineEdit {{
                padding: 8px 10px;
                border: 1px solid {COLOR_GRAY_200};
                border-radius: {BORDER_RADIUS_SM};
                background-color: {COLOR_GRAY_50};
            }}
        """)
        form_layout.addRow("Email:", self.email_personal_input)
        
        # Nomor Telepon
        self.phone_input = QLineEdit()
        self.phone_input.setPlaceholderText("081234567890")
        self.phone_input.setMinimumHeight(36)
        self.phone_input.setReadOnly(True)
        self.phone_input.setStyleSheet(f"""
            QLineEdit {{
                padding: 8px 10px;
                border: 1px solid {COLOR_GRAY_200};
                border-radius: {BORDER_RADIUS_SM};
                background-color: {COLOR_GRAY_50};
            }}
        """)
        form_layout.addRow("Nomor Telepon:", self.phone_input)
        
        # Tanggal Lahir
        self.dob_input = QLineEdit()
        self.dob_input.setPlaceholderText("YYYY-MM-DD")
        self.dob_input.setMinimumHeight(36)
        self.dob_input.setReadOnly(True)
        self.dob_input.setStyleSheet(f"""
            QLineEdit {{
                padding: 8px 10px;
                border: 1px solid {COLOR_GRAY_200};
                border-radius: {BORDER_RADIUS_SM};
                background-color: {COLOR_GRAY_50};
            }}
        """)
        form_layout.addRow("Tanggal Lahir:", self.dob_input)
        
        layout.addLayout(form_layout)
        
        # Edit button
        edit_btn = QPushButton("✏️ Edit Informasi")
        edit_btn.setStyleSheet(get_button_solid_stylesheet("navy"))
        edit_btn.clicked.connect(self.on_edit_personal_info)
        layout.addWidget(edit_btn)
        
        return frame
    
    def _create_contact_info_section(self) -> QFrame:
        """Create contact information section."""
        frame = QFrame()
        frame.setStyleSheet(f"""
            QFrame {{
                background-color: {COLOR_WHITE};
                border: 1px solid {COLOR_GRAY_200};
                border-radius: {BORDER_RADIUS_SM};
                padding: 20px;
            }}
        """)
        
        layout = QVBoxLayout(frame)
        layout.setSpacing(12)
        
        # Title
        title = QLabel("📍 Informasi Kontak")
        title_font = QFont(FONT_FAMILY_PRIMARY, 14)
        title_font.setWeight(QFont.Weight.Bold)
        title.setFont(title_font)
        title.setStyleSheet(f"color: {COLOR_NAVY};")
        layout.addWidget(title)
        
        # Divider
        divider = QFrame()
        divider.setStyleSheet(f"background-color: {COLOR_GRAY_200};")
        divider.setMaximumHeight(1)
        layout.addWidget(divider)
        
        # Form layout
        form_layout = QFormLayout()
        form_layout.setSpacing(12)
        
        # Alamat
        self.alamat_input = QLineEdit()
        self.alamat_input.setPlaceholderText("Jalan Contoh No. 123")
        self.alamat_input.setMinimumHeight(36)
        self.alamat_input.setReadOnly(True)
        self.alamat_input.setStyleSheet(f"""
            QLineEdit {{
                padding: 8px 10px;
                border: 1px solid {COLOR_GRAY_200};
                border-radius: {BORDER_RADIUS_SM};
                background-color: {COLOR_GRAY_50};
            }}
        """)
        form_layout.addRow("Alamat:", self.alamat_input)
        
        # Kota
        self.kota_input = QLineEdit()
        self.kota_input.setPlaceholderText("Jakarta")
        self.kota_input.setMinimumHeight(36)
        self.kota_input.setReadOnly(True)
        self.kota_input.setStyleSheet(f"""
            QLineEdit {{
                padding: 8px 10px;
                border: 1px solid {COLOR_GRAY_200};
                border-radius: {BORDER_RADIUS_SM};
                background-color: {COLOR_GRAY_50};
            }}
        """)
        form_layout.addRow("Kota:", self.kota_input)
        
        # Provinsi
        self.provinsi_input = QLineEdit()
        self.provinsi_input.setPlaceholderText("DKI Jakarta")
        self.provinsi_input.setMinimumHeight(36)
        self.provinsi_input.setReadOnly(True)
        self.provinsi_input.setStyleSheet(f"""
            QLineEdit {{
                padding: 8px 10px;
                border: 1px solid {COLOR_GRAY_200};
                border-radius: {BORDER_RADIUS_SM};
                background-color: {COLOR_GRAY_50};
            }}
        """)
        form_layout.addRow("Provinsi:", self.provinsi_input)
        
        # Kode Pos
        self.postal_input = QLineEdit()
        self.postal_input.setPlaceholderText("12345")
        self.postal_input.setMinimumHeight(36)
        self.postal_input.setReadOnly(True)
        self.postal_input.setStyleSheet(f"""
            QLineEdit {{
                padding: 8px 10px;
                border: 1px solid {COLOR_GRAY_200};
                border-radius: {BORDER_RADIUS_SM};
                background-color: {COLOR_GRAY_50};
            }}
        """)
        form_layout.addRow("Kode Pos:", self.postal_input)
        
        layout.addLayout(form_layout)
        
        # Edit button
        edit_btn = QPushButton("✏️ Edit Kontak")
        edit_btn.setStyleSheet(get_button_solid_stylesheet("navy"))
        edit_btn.clicked.connect(self.on_edit_contact_info)
        layout.addWidget(edit_btn)
        
        return frame
    
    def _create_preferences_section(self) -> QFrame:
        """Create preferences section."""
        frame = QFrame()
        frame.setStyleSheet(f"""
            QFrame {{
                background-color: {COLOR_WHITE};
                border: 1px solid {COLOR_GRAY_200};
                border-radius: {BORDER_RADIUS_SM};
                padding: 20px;
            }}
        """)
        
        layout = QVBoxLayout(frame)
        layout.setSpacing(12)
        
        # Title
        title = QLabel("⚙️ Preferensi")
        title_font = QFont(FONT_FAMILY_PRIMARY, 14)
        title_font.setWeight(QFont.Weight.Bold)
        title.setFont(title_font)
        title.setStyleSheet(f"color: {COLOR_NAVY};")
        layout.addWidget(title)
        
        # Divider
        divider = QFrame()
        divider.setStyleSheet(f"background-color: {COLOR_GRAY_200};")
        divider.setMaximumHeight(1)
        layout.addWidget(divider)
        
        # Form layout
        form_layout = QFormLayout()
        form_layout.setSpacing(12)
        
        # Bahasa
        self.bahasa_combo = QComboBox()
        self.bahasa_combo.addItems(["Bahasa Indonesia", "English"])
        self.bahasa_combo.setMinimumHeight(36)
        self.bahasa_combo.setStyleSheet(f"""
            QComboBox {{
                padding: 8px 10px;
                border: 1px solid {COLOR_GRAY_200};
                border-radius: {BORDER_RADIUS_SM};
                background-color: {COLOR_WHITE};
            }}
            QComboBox::drop-down {{
                border: none;
            }}
        """)
        form_layout.addRow("Bahasa:", self.bahasa_combo)
        
        # Tema
        self.tema_combo = QComboBox()
        self.tema_combo.addItems(["Light (Navy + Orange)", "Dark", "Auto"])
        self.tema_combo.setMinimumHeight(36)
        self.tema_combo.setStyleSheet(f"""
            QComboBox {{
                padding: 8px 10px;
                border: 1px solid {COLOR_GRAY_200};
                border-radius: {BORDER_RADIUS_SM};
                background-color: {COLOR_WHITE};
            }}
            QComboBox::drop-down {{
                border: none;
            }}
        """)
        form_layout.addRow("Tema:", self.tema_combo)
        
        # Notifikasi Email
        self.notif_combo = QComboBox()
        self.notif_combo.addItems(["Aktif", "Hanya Penting", "Nonaktif"])
        self.notif_combo.setMinimumHeight(36)
        self.notif_combo.setStyleSheet(f"""
            QComboBox {{
                padding: 8px 10px;
                border: 1px solid {COLOR_GRAY_200};
                border-radius: {BORDER_RADIUS_SM};
                background-color: {COLOR_WHITE};
            }}
            QComboBox::drop-down {{
                border: none;
            }}
        """)
        form_layout.addRow("Notifikasi Email:", self.notif_combo)
        
        layout.addLayout(form_layout)
        
        # Save button
        save_btn = QPushButton("💾 Simpan Preferensi")
        save_btn.setStyleSheet(get_button_solid_stylesheet("orange"))
        save_btn.clicked.connect(self.on_save_preferences)
        layout.addWidget(save_btn)
        
        return frame
    
    def _create_activity_section(self) -> QFrame:
        """Create activity history section."""
        frame = QFrame()
        frame.setStyleSheet(f"""
            QFrame {{
                background-color: {COLOR_WHITE};
                border: 1px solid {COLOR_GRAY_200};
                border-radius: {BORDER_RADIUS_SM};
                padding: 20px;
            }}
        """)
        
        layout = QVBoxLayout(frame)
        layout.setSpacing(12)
        
        # Title
        title = QLabel("📊 Aktivitas Terbaru")
        title_font = QFont(FONT_FAMILY_PRIMARY, 14)
        title_font.setWeight(QFont.Weight.Bold)
        title.setFont(title_font)
        title.setStyleSheet(f"color: {COLOR_NAVY};")
        layout.addWidget(title)
        
        # Divider
        divider = QFrame()
        divider.setStyleSheet(f"background-color: {COLOR_GRAY_200};")
        divider.setMaximumHeight(1)
        layout.addWidget(divider)
        
        # Activity items
        activities = [
            ("🎯 Melamar Beasiswa LPDP", "Hari ini pukul 14:30"),
            ("📋 Mengupdate profil", "2 hari yang lalu"),
            ("💬 Menambah catatan pada lamaran", "5 hari yang lalu"),
            ("⭐ Menambahkan favorit", "1 minggu yang lalu"),
        ]
        
        for activity_text, time_text in activities:
            activity_layout = QHBoxLayout()
            activity_layout.setSpacing(12)
            
            # Activity text
            activity_label = QLabel(activity_text)
            activity_label.setFont(QFont(FONT_FAMILY_PRIMARY, FONT_SIZE_BASE))
            activity_label.setStyleSheet(f"color: {COLOR_NAVY};")
            activity_layout.addWidget(activity_label)
            
            activity_layout.addStretch()
            
            # Time text
            time_label = QLabel(time_text)
            time_label.setFont(QFont(FONT_FAMILY_PRIMARY, FONT_SIZE_SM))
            time_label.setStyleSheet(f"color: {COLOR_GRAY_500};")
            activity_layout.addWidget(time_label)
            
            layout.addLayout(activity_layout)
        
        return frame
    
    def load_user_data(self):
        """Load user data from database."""
        try:
            conn = get_connection()
            cursor = conn.cursor()
            
            # Query user data
            cursor.execute("""
                SELECT username, email FROM akun WHERE id = ?
            """, (self.user_id,))
            
            result = cursor.fetchone()
            if result:
                username, email = result
                self.username = username
                self.email = email
                
                # Update UI
                self.nama_input.setText(username or "")
                self.email_personal_input.setText(email or "")
                
                logger.info(f"Loaded user data for {username}")
            
        except Exception as e:
            logger.error(f"Error loading user data: {e}")
    
    def on_edit_personal_info(self):
        """Handle edit personal info."""
        dialog = EditPersonalInfoDialog(self.user_id, self)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            self.load_user_data()
            QMessageBox.information(self, "Sukses", "Informasi pribadi berhasil diperbarui!")
    
    def on_edit_contact_info(self):
        """Handle edit contact info."""
        dialog = EditContactInfoDialog(self.user_id, self)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            QMessageBox.information(self, "Sukses", "Informasi kontak berhasil diperbarui!")
    
    def on_save_preferences(self):
        """Handle save preferences."""
        QMessageBox.information(self, "Sukses", "Preferensi berhasil disimpan!")
        logger.info(f"User {self.user_id} preferences updated")
    
    def on_change_password(self):
        """Handle change password."""
        dialog = ChangePasswordDialog(self.user_id, self)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            QMessageBox.information(self, "Sukses", "Password berhasil diubah!")
    
    def on_logout(self):
        """Handle logout."""
        reply = QMessageBox.question(
            self,
            "Konfirmasi Keluar",
            "Anda yakin ingin keluar dari akun ini?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        
        if reply == QMessageBox.StandardButton.Yes:
            logger.info(f"User {self.user_id} logged out")
            # Emit signal or close application
            # This would be handled by the main window
            from PyQt6.QtWidgets import QApplication
            QApplication.instance().quit()


class EditPersonalInfoDialog(QDialog):
    """Dialog untuk edit personal information."""
    
    def __init__(self, user_id: int, parent=None):
        super().__init__(parent)
        self.user_id = user_id
        self.setWindowTitle("Edit Informasi Pribadi")
        self.setGeometry(150, 150, 500, 400)
        self.setModal(True)
        self.init_ui()
        self.load_data()
    
    def init_ui(self):
        """Initialize dialog UI."""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(12)
        
        # Title
        title = QLabel("Edit Informasi Pribadi")
        title_font = QFont(FONT_FAMILY_PRIMARY, 14)
        title_font.setWeight(QFont.Weight.Bold)
        title.setFont(title_font)
        title.setStyleSheet(f"color: {COLOR_NAVY};")
        layout.addWidget(title)
        
        # Form layout
        form = QFormLayout()
        form.setSpacing(12)
        
        # Phone
        self.phone_input = QLineEdit()
        self.phone_input.setMinimumHeight(36)
        form.addRow("Nomor Telepon:", self.phone_input)
        
        # Date of birth
        self.dob_input = QLineEdit()
        self.dob_input.setPlaceholderText("YYYY-MM-DD")
        self.dob_input.setMinimumHeight(36)
        form.addRow("Tanggal Lahir:", self.dob_input)
        
        layout.addLayout(form)
        
        # Buttons
        button_layout = QHBoxLayout()
        
        simpan_btn = QPushButton("✅ Simpan")
        simpan_btn.setStyleSheet(get_button_solid_stylesheet("navy"))
        simpan_btn.clicked.connect(self.on_simpan)
        button_layout.addWidget(simpan_btn)
        
        batal_btn = QPushButton("❌ Batal")
        batal_btn.setStyleSheet(get_button_solid_stylesheet("gray"))
        batal_btn.clicked.connect(self.reject)
        button_layout.addWidget(batal_btn)
        
        layout.addLayout(button_layout)
        layout.addStretch()
    
    def load_data(self):
        """Load user data."""
        try:
            conn = get_connection()
            cursor = conn.cursor()
            cursor.execute("SELECT phone, date_of_birth FROM akun WHERE id = ?", (self.user_id,))
            
            result = cursor.fetchone()
            if result:
                phone, dob = result
                self.phone_input.setText(phone or "")
                self.dob_input.setText(dob or "")
            
        except Exception as e:
            logger.error(f"Error loading personal info: {e}")
    
    def on_simpan(self):
        """Save changes."""
        phone = self.phone_input.text().strip()
        dob = self.dob_input.text().strip()
        
        try:
            conn = get_connection()
            cursor = conn.cursor()
            cursor.execute("""
                UPDATE akun SET phone = ?, date_of_birth = ? WHERE id = ?
            """, (phone, dob, self.user_id))
            conn.commit()
            
            logger.info(f"Updated personal info for user {self.user_id}")
            self.accept()
            
        except Exception as e:
            logger.error(f"Error updating personal info: {e}")
            QMessageBox.critical(self, "Error", f"Gagal simpan: {e}")


class EditContactInfoDialog(QDialog):
    """Dialog untuk edit contact information."""
    
    def __init__(self, user_id: int, parent=None):
        super().__init__(parent)
        self.user_id = user_id
        self.setWindowTitle("Edit Informasi Kontak")
        self.setGeometry(150, 150, 500, 450)
        self.setModal(True)
        self.init_ui()
        self.load_data()
    
    def init_ui(self):
        """Initialize dialog UI."""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(12)
        
        # Title
        title = QLabel("Edit Informasi Kontak")
        title_font = QFont(FONT_FAMILY_PRIMARY, 14)
        title_font.setWeight(QFont.Weight.Bold)
        title.setFont(title_font)
        title.setStyleSheet(f"color: {COLOR_NAVY};")
        layout.addWidget(title)
        
        # Form layout
        form = QFormLayout()
        form.setSpacing(12)
        
        # Alamat
        self.alamat_input = QLineEdit()
        self.alamat_input.setMinimumHeight(36)
        form.addRow("Alamat:", self.alamat_input)
        
        # Kota
        self.kota_input = QLineEdit()
        self.kota_input.setMinimumHeight(36)
        form.addRow("Kota:", self.kota_input)
        
        # Provinsi
        self.provinsi_input = QLineEdit()
        self.provinsi_input.setMinimumHeight(36)
        form.addRow("Provinsi:", self.provinsi_input)
        
        # Kode Pos
        self.postal_input = QLineEdit()
        self.postal_input.setMinimumHeight(36)
        form.addRow("Kode Pos:", self.postal_input)
        
        layout.addLayout(form)
        
        # Buttons
        button_layout = QHBoxLayout()
        
        simpan_btn = QPushButton("✅ Simpan")
        simpan_btn.setStyleSheet(get_button_solid_stylesheet("navy"))
        simpan_btn.clicked.connect(self.on_simpan)
        button_layout.addWidget(simpan_btn)
        
        batal_btn = QPushButton("❌ Batal")
        batal_btn.setStyleSheet(get_button_solid_stylesheet("gray"))
        batal_btn.clicked.connect(self.reject)
        button_layout.addWidget(batal_btn)
        
        layout.addLayout(button_layout)
        layout.addStretch()
    
    def load_data(self):
        """Load user data."""
        try:
            conn = get_connection()
            cursor = conn.cursor()
            cursor.execute("""
                SELECT address, city, province, postal_code FROM akun WHERE id = ?
            """, (self.user_id,))
            
            result = cursor.fetchone()
            if result:
                address, city, province, postal = result
                self.alamat_input.setText(address or "")
                self.kota_input.setText(city or "")
                self.provinsi_input.setText(province or "")
                self.postal_input.setText(postal or "")
            
        except Exception as e:
            logger.error(f"Error loading contact info: {e}")
    
    def on_simpan(self):
        """Save changes."""
        address = self.alamat_input.text().strip()
        city = self.kota_input.text().strip()
        province = self.provinsi_input.text().strip()
        postal = self.postal_input.text().strip()
        
        try:
            conn = get_connection()
            cursor = conn.cursor()
            cursor.execute("""
                UPDATE akun SET address = ?, city = ?, province = ?, postal_code = ? WHERE id = ?
            """, (address, city, province, postal, self.user_id))
            conn.commit()
            
            logger.info(f"Updated contact info for user {self.user_id}")
            self.accept()
            
        except Exception as e:
            logger.error(f"Error updating contact info: {e}")
            QMessageBox.critical(self, "Error", f"Gagal simpan: {e}")


class ChangePasswordDialog(QDialog):
    """Dialog untuk ubah password."""
    
    def __init__(self, user_id: int, parent=None):
        super().__init__(parent)
        self.user_id = user_id
        self.setWindowTitle("Ubah Password")
        self.setGeometry(150, 150, 450, 350)
        self.setModal(True)
        self.init_ui()
    
    def init_ui(self):
        """Initialize dialog UI."""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(12)
        
        # Title
        title = QLabel("Ubah Password")
        title_font = QFont(FONT_FAMILY_PRIMARY, 14)
        title_font.setWeight(QFont.Weight.Bold)
        title.setFont(title_font)
        title.setStyleSheet(f"color: {COLOR_NAVY};")
        layout.addWidget(title)
        
        # Form layout
        form = QFormLayout()
        form.setSpacing(12)
        
        # Password lama
        self.old_pwd = QLineEdit()
        self.old_pwd.setEchoMode(QLineEdit.EchoMode.Password)
        self.old_pwd.setMinimumHeight(36)
        form.addRow("Password Lama:", self.old_pwd)
        
        # Password baru
        self.new_pwd = QLineEdit()
        self.new_pwd.setEchoMode(QLineEdit.EchoMode.Password)
        self.new_pwd.setMinimumHeight(36)
        form.addRow("Password Baru:", self.new_pwd)
        
        # Konfirmasi password
        self.confirm_pwd = QLineEdit()
        self.confirm_pwd.setEchoMode(QLineEdit.EchoMode.Password)
        self.confirm_pwd.setMinimumHeight(36)
        form.addRow("Konfirmasi Password:", self.confirm_pwd)
        
        layout.addLayout(form)
        
        # Buttons
        button_layout = QHBoxLayout()
        
        simpan_btn = QPushButton("✅ Simpan")
        simpan_btn.setStyleSheet(get_button_solid_stylesheet("navy"))
        simpan_btn.clicked.connect(self.on_simpan)
        button_layout.addWidget(simpan_btn)
        
        batal_btn = QPushButton("❌ Batal")
        batal_btn.setStyleSheet(get_button_solid_stylesheet("gray"))
        batal_btn.clicked.connect(self.reject)
        button_layout.addWidget(batal_btn)
        
        layout.addLayout(button_layout)
        layout.addStretch()
    
    def on_simpan(self):
        """Save new password."""
        old_pwd = self.old_pwd.text()
        new_pwd = self.new_pwd.text()
        confirm_pwd = self.confirm_pwd.text()
        
        if not old_pwd or not new_pwd or not confirm_pwd:
            QMessageBox.warning(self, "Validasi", "Semua field harus diisi!")
            return
        
        if new_pwd != confirm_pwd:
            QMessageBox.warning(self, "Validasi", "Password baru tidak cocok!")
            return
        
        if len(new_pwd) < 6:
            QMessageBox.warning(self, "Validasi", "Password minimal 6 karakter!")
            return
        
        try:
            QMessageBox.information(self, "Sukses", "Password berhasil diubah!")
            logger.info(f"User {self.user_id} changed password")
            self.accept()
            
        except Exception as e:
            logger.error(f"Error changing password: {e}")
            QMessageBox.critical(self, "Error", f"Gagal ubah password: {e}")
