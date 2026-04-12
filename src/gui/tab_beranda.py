"""
Beranda (Dashboard) Tab for BeasiswaKu
Main dashboard showing welcome, stats, recent activity, and deadline alerts
"""

import logging
from datetime import datetime, timedelta
from typing import Optional, List, Dict, Any
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QScrollArea,
    QFrame, QPushButton, QGridLayout, QSpacerItem, QSizePolicy
)
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QFont, QColor, QIcon

from src.gui.design_tokens import *
from src.gui.styles import get_button_solid_stylesheet
from src.gui.components import AlertBanner
from src.database.crud import get_connection

# Setup logging
logger = logging.getLogger(__name__)


class StatCard(QFrame):
    """
    Reusable stat card untuk menampilkan statistik dengan icon, number, dan label.
    
    Features:
    - Icon (emoji atau icon)
    - Large number (prominent)
    - Label text
    - Colored left border accent
    - Deskripsi opsional
    
    Example:
        card = StatCard(
            icon="📚",
            number="48",
            label="Total Beasiswa",
            accent_color="#1e3a8a",  # Navy
            description="Tersedia di database"
        )
    """
    
    def __init__(self, icon: str = "", number: str = "0", label: str = "", 
                 accent_color: str = COLOR_NAVY, description: str = "", parent=None):
        super().__init__(parent)
        self.icon = icon
        self.number = number
        self.label = label
        self.accent_color = accent_color
        self.description = description
        
        self.setFrameStyle(QFrame.Shape.Box | QFrame.Shadow.Plain)
        self.init_ui()
    
    def init_ui(self):
        """Initialize UI components."""
        layout = QHBoxLayout(self)
        layout.setContentsMargins(16, 16, 16, 16)  # SPACING_4
        layout.setSpacing(12)  # SPACING_3
        
        # Left border accent
        left_border = QFrame()
        left_border.setFrameStyle(QFrame.Shape.Box | QFrame.Shadow.Plain)
        left_border.setMaximumWidth(4)
        left_border.setStyleSheet(f"background-color: {self.accent_color}; border: none;")
        layout.addWidget(left_border)
        
        # Content layout
        content_layout = QVBoxLayout()
        content_layout.setSpacing(4)
        
        # Icon + Number row
        icon_number_layout = QHBoxLayout()
        icon_number_layout.setSpacing(8)
        
        icon_label = QLabel(self.icon)
        icon_label.setFont(QFont(FONT_FAMILY_PRIMARY, 28))  # Large emoji
        icon_number_layout.addWidget(icon_label)
        
        number_label = QLabel(self.number)
        number_font = QFont(FONT_FAMILY_PRIMARY, 28)  # FONT_SIZE_2XL equivalent
        number_font.setWeight(QFont.Weight.Bold)
        number_label.setFont(number_font)
        number_label.setStyleSheet(f"color: {COLOR_NAVY}; font-weight: bold;")
        icon_number_layout.addWidget(number_label)
        
        content_layout.addLayout(icon_number_layout)
        
        # Label text
        label_widget = QLabel(self.label)
        label_font = QFont(FONT_FAMILY_PRIMARY, FONT_SIZE_BASE)
        label_font.setWeight(QFont.Weight.Medium)
        label_widget.setFont(label_font)
        label_widget.setStyleSheet(f"color: {COLOR_NAVY};")
        content_layout.addWidget(label_widget)
        
        # Description (optional)
        if self.description:
            desc_widget = QLabel(self.description)
            desc_widget.setFont(QFont(FONT_FAMILY_PRIMARY, FONT_SIZE_SM))
            desc_widget.setStyleSheet(f"color: {COLOR_GRAY_500};")
            content_layout.addWidget(desc_widget)
        
        layout.addLayout(content_layout)
        layout.addStretch()
        
        # Apply card styling
        self.setStyleSheet(f"""
            QFrame {{
                background-color: {COLOR_WHITE};
                border: 1px solid {COLOR_GRAY_200};
                border-radius: {BORDER_RADIUS_MD};
                padding: 0px;
            }}
        """)


class BeasiswaDeadlineCard(QFrame):
    """
    Card untuk menampilkan scholarship dengan deadline dekat.
    """
    
    def __init__(self, judul: str = "", penyelenggara: str = "", jenjang: str = "",
                 deadline: str = "", urgency: str = "normal", parent=None):
        super().__init__(parent)
        self.judul = judul
        self.penyelenggara = penyelenggara
        self.jenjang = jenjang
        self.deadline = deadline
        self.urgency = urgency  # 'urgent', 'warning', 'normal'
        
        # Determine color based on urgency
        if urgency == "urgent":
            self.accent_color = COLOR_ERROR  # Red
            self.bg_color = "#fef2f2"  # Light red
        elif urgency == "warning":
            self.accent_color = COLOR_WARNING  # Orange
            self.bg_color = "#fffbeb"  # Light yellow
        else:
            self.accent_color = COLOR_GRAY_400
            self.bg_color = "#f9fafb"  # Light gray
        
        self.setFrameStyle(QFrame.Shape.Box | QFrame.Shadow.Plain)
        self.init_ui()
    
    def init_ui(self):
        """Initialize UI components."""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(12, 12, 12, 12)  # SPACING_3
        layout.setSpacing(8)  # SPACING_2
        
        # Title
        title_label = QLabel(self.judul)
        title_font = QFont(FONT_FAMILY_PRIMARY, FONT_SIZE_BASE)
        title_font.setWeight(QFont.Weight.Medium)
        title_label.setFont(title_font)
        title_label.setStyleSheet(f"color: {COLOR_NAVY};")
        layout.addWidget(title_label)
        
        # Penyelenggara
        org_label = QLabel(self.penyelenggara)
        org_label.setFont(QFont(FONT_FAMILY_PRIMARY, FONT_SIZE_SM))
        org_label.setStyleSheet(f"color: {COLOR_GRAY_600};")
        layout.addWidget(org_label)
        
        # Jenjang
        level_label = QLabel(self.jenjang)
        level_font = QFont(FONT_FAMILY_PRIMARY, FONT_SIZE_XS)
        level_label.setFont(level_font)
        level_label.setStyleSheet(f"color: {COLOR_GRAY_500}; padding: 4px 8px; background-color: {COLOR_GRAY_100}; border-radius: 4px; width: fit-content;")
        layout.addWidget(level_label)
        
        # Deadline with urgency indicator
        deadline_layout = QHBoxLayout()
        deadline_layout.setSpacing(8)
        
        urgency_icon = "🔴" if self.urgency == "urgent" else ("⏰" if self.urgency == "warning" else "🟢")
        urgency_label = QLabel(urgency_icon)
        urgency_label.setFont(QFont(FONT_FAMILY_PRIMARY, FONT_SIZE_BASE))
        deadline_layout.addWidget(urgency_label)
        
        deadline_text = QLabel(self.deadline)
        deadline_text.setFont(QFont(FONT_FAMILY_PRIMARY, FONT_SIZE_SM))
        deadline_text.setStyleSheet(f"color: {self.accent_color}; font-weight: bold;")
        deadline_layout.addWidget(deadline_text)
        deadline_layout.addStretch()
        
        layout.addLayout(deadline_layout)
        
        # Apply card styling
        self.setStyleSheet(f"""
            QFrame {{
                background-color: {self.bg_color};
                border: 1px solid {COLOR_GRAY_200};
                border-left: 4px solid {self.accent_color};
                border-radius: {BORDER_RADIUS_SM};
            }}
        """)


class ActivityItem(QFrame):
    """Activity timeline item untuk latest activities."""
    
    def __init__(self, emoji: str = "", title: str = "", description: str = "",
                 time_ago: str = "", parent=None):
        super().__init__(parent)
        self.emoji = emoji
        self.title = title
        self.description = description
        self.time_ago = time_ago
        
        self.setFrameStyle(QFrame.Shape.NoFrame)
        self.init_ui()
    
    def init_ui(self):
        """Initialize UI components."""
        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 8, 0, 8)  # SPACING_2
        layout.setSpacing(12)  # SPACING_3
        
        # Emoji/Icon
        emoji_label = QLabel(self.emoji)
        emoji_label.setFont(QFont(FONT_FAMILY_PRIMARY, FONT_SIZE_LG))
        emoji_label.setMaximumWidth(24)
        layout.addWidget(emoji_label)
        
        # Text content
        text_layout = QVBoxLayout()
        text_layout.setSpacing(4)
        
        title_label = QLabel(self.title)
        title_font = QFont(FONT_FAMILY_PRIMARY, FONT_SIZE_BASE)
        title_font.setWeight(QFont.Weight.Medium)
        title_label.setFont(title_font)
        title_label.setStyleSheet(f"color: {COLOR_NAVY};")
        text_layout.addWidget(title_label)
        
        desc_label = QLabel(self.description)
        desc_label.setFont(QFont(FONT_FAMILY_PRIMARY, FONT_SIZE_SM))
        desc_label.setStyleSheet(f"color: {COLOR_GRAY_600};")
        text_layout.addWidget(desc_label)
        
        layout.addLayout(text_layout)
        layout.addStretch()
        
        # Time ago
        time_label = QLabel(self.time_ago)
        time_label.setFont(QFont(FONT_FAMILY_PRIMARY, FONT_SIZE_XS))
        time_label.setStyleSheet(f"color: {COLOR_GRAY_500};")
        time_label.setMaximumWidth(80)
        layout.addWidget(time_label, alignment=Qt.AlignmentFlag.AlignRight)


class BerandaTab(QWidget):
    """
    Beranda (Dashboard) Tab - Main home page untuk BeasiswaKu.
    
    Features:
    - Greeting dengan user name dan waktu
    - Alert banner untuk deadline warning
    - 4 stat cards (Total Beasiswa, Deadline Minggu Ini, Lamaran, Diterima)
    - Beasiswa dengan deadline dekat (3-4 cards)
    - Beasiswa favorit list
    - Recent activity timeline
    - CTA buttons untuk action
    
    Layout:
    ┌─────────────────────────────────────────┐
    │ Halo, [Name]! 👋                        │
    │ [Date]         [Refresh] [Lihat Semua]  │
    ├─────────────────────────────────────────┤
    │ ⚠️ Ada N beasiswa dengan deadline...    │
    ├─────────────────────────────────────────┤
    │ [Stat 1] [Stat 2] [Stat 3] [Stat 4]     │
    ├─────────────────────────────────────────┤
    │ 📌 Beasiswa Deadline Dekat               │
    │ [Card 1] [Card 2] [Card 3]              │
    ├─────────────────────────────────────────┤
    │ ⭐ Beasiswa Favoritku                   │
    │ [List item 1]                           │
    │ [List item 2]                           │
    │ [Lihat Semua →]                         │
    ├─────────────────────────────────────────┤
    │ 🕐 Aktivitas Terbaru                    │
    │ [Activity 1]                            │
    │ [Activity 2]                            │
    │ [Lihat Semua →]                         │
    └─────────────────────────────────────────┘
    """
    
    def __init__(self, user_id: int, username: str = "", parent=None):
        super().__init__(parent)
        self.user_id = user_id
        self.username = username
        self.alert_banner: Optional[AlertBanner] = None
        
        logger.info(f"Initializing BerandaTab for user {user_id}")
        self.init_ui()
        self.load_dashboard_data()
    
    def init_ui(self):
        """Initialize Beranda Tab UI."""
        # Main layout
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(16, 16, 16, 16)  # SPACING_4
        main_layout.setSpacing(12)  # SPACING_3
        
        # ===== HEADER SECTION =====
        header_layout = QHBoxLayout()
        header_layout.setSpacing(12)
        
        # Greeting
        greeting_layout = QVBoxLayout()
        greeting_layout.setSpacing(4)
        
        greeting_text = QLabel(f"Halo, {self.username}! 👋")
        greeting_font = QFont(FONT_FAMILY_PRIMARY, 20)
        greeting_font.setWeight(QFont.Weight.Bold)
        greeting_text.setFont(greeting_font)
        greeting_text.setStyleSheet(f"color: {COLOR_NAVY};")
        greeting_layout.addWidget(greeting_text)
        
        date_text = QLabel(datetime.now().strftime("%A, %d %B %Y"))
        date_text.setFont(QFont(FONT_FAMILY_PRIMARY, FONT_SIZE_BASE))
        date_text.setStyleSheet(f"color: {COLOR_GRAY_600};")
        greeting_layout.addWidget(date_text)
        
        header_layout.addLayout(greeting_layout)
        header_layout.addStretch()
        
        # Action buttons
        refresh_btn = QPushButton("🔄 Refresh Data")
        refresh_btn.setStyleSheet(get_button_solid_stylesheet("navy"))
        refresh_btn.setMaximumWidth(120)
        header_layout.addWidget(refresh_btn)
        
        lihat_semua_btn = QPushButton("📋 Lihat Semua Beasiswa")
        lihat_semua_btn.setStyleSheet(get_button_solid_stylesheet("orange"))
        lihat_semua_btn.setMaximumWidth(180)
        header_layout.addWidget(lihat_semua_btn)
        
        main_layout.addLayout(header_layout)
        main_layout.addSpacing(8)  # SPACING_2
        
        # ===== ALERT BANNER =====
        self.alert_banner = AlertBanner(
            alert_type="warning",
            message="Ada 3 beasiswa yang deadline-nya minggu ini. Jangan sampai terlawat!",
            closable=True
        )
        main_layout.addWidget(self.alert_banner)
        main_layout.addSpacing(8)  # SPACING_2
        
        # ===== STAT CARDS SECTION =====
        stats_layout = QGridLayout()
        stats_layout.setSpacing(12)  # SPACING_3
        
        self.stat_cards = []
        stat_configs = [
            {"icon": "📚", "label": "Total Beasiswa", "number": "48", "desc": "Tersedia di database", "color": COLOR_NAVY},
            {"icon": "⏰", "label": "Deadline Minggu Ini", "number": "3", "desc": "Segera daftar!", "color": COLOR_ERROR},
            {"icon": "📄", "label": "Total Lamaranku", "number": "12", "desc": "Tercatat di Tracker", "color": COLOR_NAVY},
            {"icon": "✅", "label": "Diterima", "number": "2", "desc": "Selamat, terus semangat!", "color": COLOR_SUCCESS},
        ]
        
        for idx, config in enumerate(stat_configs):
            card = StatCard(
                icon=config["icon"],
                number=config["number"],
                label=config["label"],
                description=config["desc"],
                accent_color=config["color"]
            )
            self.stat_cards.append(card)
            stats_layout.addWidget(card, 0, idx)
        
        main_layout.addLayout(stats_layout)
        main_layout.addSpacing(8)  # SPACING_2
        
        # ===== BEASISWA DEADLINE DEKAT SECTION =====
        section_label = QLabel("📌 Beasiswa Deadline Dekat")
        section_font = QFont(FONT_FAMILY_PRIMARY, FONT_SIZE_LG)
        section_font.setWeight(QFont.Weight.Bold)
        section_label.setFont(section_font)
        section_label.setStyleSheet(f"color: {COLOR_NAVY};")
        main_layout.addWidget(section_label)
        
        deadline_cards_layout = QHBoxLayout()
        deadline_cards_layout.setSpacing(12)  # SPACING_3
        
        self.deadline_cards = []
        deadline_configs = [
            {
                "judul": "Beasiswa Unggulan Kementerkbud 2026",
                "penyelenggara": "Kementerkbud RI",
                "jenjang": "D4 / S1",
                "deadline": "Tutup dalam 3 hari",
                "urgency": "urgent"
            },
            {
                "judul": "Beasiswa LPDP 2026",
                "penyelenggara": "Kemenkeu RI",
                "jenjang": "S2",
                "deadline": "Tutup dalam 6 hari",
                "urgency": "warning"
            },
            {
                "judul": "Beasiswa Sampoerna University",
                "penyelenggara": "Sampoerna Foundation",
                "jenjang": "S1",
                "deadline": "Tutup dalam 6 hari",
                "urgency": "warning"
            },
        ]
        
        for config in deadline_configs:
            card = BeasiswaDeadlineCard(
                judul=config["judul"],
                penyelenggara=config["penyelenggara"],
                jenjang=config["jenjang"],
                deadline=config["deadline"],
                urgency=config["urgency"]
            )
            card.setMaximumWidth(300)
            self.deadline_cards.append(card)
            deadline_cards_layout.addWidget(card)
        
        deadline_cards_layout.addStretch()
        main_layout.addLayout(deadline_cards_layout)
        main_layout.addSpacing(8)  # SPACING_2
        
        # ===== BEASISWA FAVORIT SECTION =====
        fav_section = QHBoxLayout()
        fav_label = QLabel("⭐ Beasiswa Favoritku")
        fav_font = QFont(FONT_FAMILY_PRIMARY, FONT_SIZE_LG)
        fav_font.setWeight(QFont.Weight.Bold)
        fav_label.setFont(fav_font)
        fav_label.setStyleSheet(f"color: {COLOR_NAVY};")
        fav_section.addWidget(fav_label)
        fav_section.addStretch()
        
        lihat_fav_btn = QPushButton("Lihat Semua →")
        lihat_fav_btn.setStyleSheet(f"color: {COLOR_ORANGE}; border: none; font-weight: bold;")
        fav_section.addWidget(lihat_fav_btn)
        
        main_layout.addLayout(fav_section)
        
        # Sample favorite items
        fav_items = [
            {"icon": "⭐", "title": "Beasiswa BCA", "desc": "Bank BCA"},
            {"icon": "⭐", "title": "Beasiswa Djarum Plus", "desc": "Djarum Foundation"},
        ]
        
        for item in fav_items:
            fav_widget = ActivityItem(
                emoji=item["icon"],
                title=item["title"],
                description=item["desc"]
            )
            main_layout.addWidget(fav_widget)
        
        main_layout.addSpacing(8)  # SPACING_2
        
        # ===== AKTIVITAS TERBARU SECTION =====
        activity_section = QHBoxLayout()
        activity_label = QLabel("🕐 Aktivitas Terbaru")
        activity_font = QFont(FONT_FAMILY_PRIMARY, FONT_SIZE_LG)
        activity_font.setWeight(QFont.Weight.Bold)
        activity_label.setFont(activity_font)
        activity_label.setStyleSheet(f"color: {COLOR_NAVY};")
        activity_section.addWidget(activity_label)
        activity_section.addStretch()
        
        lihat_activity_btn = QPushButton("Lihat Semua →")
        lihat_activity_btn.setStyleSheet(f"color: {COLOR_ORANGE}; border: none; font-weight: bold;")
        activity_section.addWidget(lihat_activity_btn)
        
        main_layout.addLayout(activity_section)
        
        # Sample activities
        activities = [
            {"emoji": "🟠", "title": "Menambahkan lamaran Beasiswa Bank Indonesia", "desc": "2 hari yang lalu", "time": ""},
            {"emoji": "🟢", "title": "Mendai favorit: Beasiswa Unggulan Kementerkbud", "desc": "4 hari yang lalu", "time": ""},
            {"emoji": "🔵", "title": "Memperbaharui status lamaran Beasiswa LPDP — Diterima", "desc": "1 minggu yang lalu", "time": ""},
        ]
        
        for activity in activities:
            activity_widget = ActivityItem(
                emoji=activity["emoji"],
                title=activity["title"],
                description=activity["desc"],
                time_ago=activity["time"]
            )
            main_layout.addWidget(activity_widget)
        
        main_layout.addStretch()
        
        # Apply stylesheet to main widget
        self.setStyleSheet(f"""
            QWidget {{
                background-color: {COLOR_GRAY_BACKGROUND};
            }}
        """)
    
    def load_dashboard_data(self):
        """Load dashboard data dari database."""
        try:
            conn = get_connection()
            cursor = conn.cursor()
            
            # Get total beasiswa count
            cursor.execute("SELECT COUNT(*) as total FROM beasiswa")
            total_beasiswa = cursor.fetchone()[0]
            logger.info(f"Total beasiswa: {total_beasiswa}")
            
            # Update stat card
            if self.stat_cards:
                self.stat_cards[0].number = str(total_beasiswa)
                self.stat_cards[0].update()
            
        except Exception as e:
            logger.error(f"Error loading dashboard data: {e}")
    
    def refresh_data(self):
        """Refresh dashboard data."""
        self.load_dashboard_data()
        if self.alert_banner:
            self.alert_banner.show_alert("success", "Data berhasil diperbarui!")
