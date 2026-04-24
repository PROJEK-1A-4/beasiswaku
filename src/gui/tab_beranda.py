"""
Beranda (Dashboard) Tab for BeasiswaKu
Main dashboard showing welcome, stats, recent activity, and deadline alerts
"""

import logging
from datetime import datetime
from typing import Optional, List, Dict, Any

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QScrollArea,
    QFrame, QPushButton, QGridLayout
)
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QFont

from src.gui.design_tokens import *
from src.gui.styles import get_button_solid_stylesheet
from src.gui.components import AlertBanner
from src.scraper.scraper import get_scraper_thread
from src.services.dashboard_service import get_beranda_snapshot, sync_beasiswa_from_scraper

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
        self.number_label: Optional[QLabel] = None
        self.label_widget: Optional[QLabel] = None
        self.desc_widget: Optional[QLabel] = None
        
        self.setFrameStyle(QFrame.Shape.Box | QFrame.Shadow.Plain)
        self.init_ui()
    
    def init_ui(self):
        """Initialize UI components."""
        self.setObjectName("statCard")
        layout = QHBoxLayout(self)
        layout.setContentsMargins(16, 16, 16, 16)  # SPACING_4
        layout.setSpacing(12)  # SPACING_3
        
        # Left border accent
        left_border = QFrame()
        left_border.setObjectName("statAccent")
        left_border.setFixedWidth(4)
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
        
        self.number_label = QLabel(self.number)
        number_font = QFont(FONT_FAMILY_PRIMARY, 28)  # FONT_SIZE_2XL equivalent
        number_font.setWeight(QFont.Weight.Bold)
        self.number_label.setFont(number_font)
        self.number_label.setStyleSheet(f"color: {COLOR_NAVY}; font-weight: bold;")
        icon_number_layout.addWidget(self.number_label)
        
        content_layout.addLayout(icon_number_layout)
        
        # Label text
        self.label_widget = QLabel(self.label)
        label_font = QFont(FONT_FAMILY_PRIMARY, FONT_SIZE_BASE)
        label_font.setWeight(QFont.Weight.Medium)
        self.label_widget.setFont(label_font)
        self.label_widget.setStyleSheet(f"color: {COLOR_NAVY};")
        content_layout.addWidget(self.label_widget)
        
        # Description (optional)
        self.desc_widget = QLabel(self.description)
        self.desc_widget.setFont(QFont(FONT_FAMILY_PRIMARY, FONT_SIZE_SM))
        self.desc_widget.setStyleSheet(f"color: {COLOR_GRAY_500};")
        self.desc_widget.setVisible(bool(self.description))
        content_layout.addWidget(self.desc_widget)
        
        layout.addLayout(content_layout)
        layout.addStretch()
        
        # Apply card styling
        self.setStyleSheet(f"""
            QFrame#statCard {{
                background-color: {COLOR_WHITE};
                border: 1px solid {COLOR_GRAY_200};
                border-radius: {BORDER_RADIUS_MD};
                padding: 0px;
            }}
            QFrame#statAccent {{
                background-color: {self.accent_color};
                border: none;
                border-radius: 2px;
            }}
            QLabel {{
                border: none;
                background: transparent;
            }}
        """)

    def set_data(self, number: str, label: Optional[str] = None, description: Optional[str] = None):
        """Update card values after async/data refresh."""
        self.number = str(number)
        if self.number_label:
            self.number_label.setText(self.number)

        if label is not None:
            self.label = label
            if self.label_widget:
                self.label_widget.setText(label)

        if description is not None:
            self.description = description
            if self.desc_widget:
                self.desc_widget.setText(description)
                self.desc_widget.setVisible(bool(description))


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
        self.setObjectName("deadlineCard")
        layout = QVBoxLayout(self)
        layout.setContentsMargins(12, 12, 12, 12)  # SPACING_3
        layout.setSpacing(8)  # SPACING_2
        
        # Title
        title_label = QLabel(self.judul)
        title_label.setWordWrap(True)
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
        level_label.setObjectName("deadlineLevelPill")
        level_font = QFont(FONT_FAMILY_PRIMARY, FONT_SIZE_XS)
        level_label.setFont(level_font)
        level_label.setStyleSheet(f"""
            color: {COLOR_GRAY_500};
            padding: 4px 8px;
            background-color: {COLOR_GRAY_100};
            border-radius: 4px;
            border: none;
        """)
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
            QFrame#deadlineCard {{
                background-color: {self.bg_color};
                border: 1px solid {COLOR_GRAY_200};
                border-left: 4px solid {self.accent_color};
                border-radius: {BORDER_RADIUS_SM};
            }}
            QLabel {{
                border: none;
                background: transparent;
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
        self.setObjectName("activityItem")
        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 6, 0, 6)  # SPACING_2
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
        title_label.setWordWrap(True)
        title_font = QFont(FONT_FAMILY_PRIMARY, FONT_SIZE_BASE)
        title_font.setWeight(QFont.Weight.Medium)
        title_label.setFont(title_font)
        title_label.setStyleSheet(f"color: {COLOR_NAVY};")
        text_layout.addWidget(title_label)
        
        desc_label = QLabel(self.description)
        desc_label.setWordWrap(True)
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
        time_label.setVisible(bool(self.time_ago))
        layout.addWidget(time_label, alignment=Qt.AlignmentFlag.AlignRight)

        self.setStyleSheet("""
            QFrame#activityItem {
                border: none;
                background: transparent;
            }
            QLabel {
                border: none;
                background: transparent;
            }
        """)


class FavoriteScholarshipItem(QFrame):
    """Compact favorite scholarship row with status pill."""

    STATUS_STYLE = {
        "Buka": ("#dcfce7", "#16a34a"),
        "Segera Tutup": ("#fef3c7", "#d97706"),
        "Tutup": ("#fee2e2", "#dc2626"),
    }

    def __init__(self, title: str, subtitle: str, status: str = "Buka", parent=None):
        super().__init__(parent)
        self.title = title
        self.subtitle = subtitle
        self.status = status
        self.setObjectName("favoriteRow")
        self.init_ui()

    def init_ui(self):
        layout = QHBoxLayout(self)
        layout.setContentsMargins(12, 10, 12, 10)
        layout.setSpacing(10)

        star_label = QLabel("⭐")
        star_label.setObjectName("favoriteStar")
        star_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        star_label.setFixedSize(28, 28)
        layout.addWidget(star_label)

        text_layout = QVBoxLayout()
        text_layout.setSpacing(2)

        title_label = QLabel(self.title)
        title_label.setObjectName("favoriteTitle")
        title_label.setWordWrap(False)
        text_layout.addWidget(title_label)

        subtitle_label = QLabel(self.subtitle)
        subtitle_label.setObjectName("favoriteSubtitle")
        subtitle_label.setWordWrap(False)
        text_layout.addWidget(subtitle_label)

        layout.addLayout(text_layout, 1)

        bg_color, fg_color = self.STATUS_STYLE.get(self.status, ("#e5e7eb", "#4b5563"))
        status_label = QLabel(self.status)
        status_label.setObjectName("favoriteStatus")
        status_label.setStyleSheet(
            f"""
            background-color: {bg_color};
            color: {fg_color};
            border: none;
            border-radius: 11px;
            padding: 4px 10px;
            font-weight: 600;
            """
        )
        layout.addWidget(status_label, alignment=Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)


class ActivityTimelineItem(QFrame):
    """Timeline-like activity row with colored marker and status chip."""

    STATUS_STYLE = {
        "Pending": ("#3b82f6", "#dbeafe", "#1d4ed8"),
        "Diterima": ("#10b981", "#d1fae5", "#047857"),
        "Ditolak": ("#ef4444", "#fee2e2", "#b91c1c"),
    }

    def __init__(self, title: str, time_ago: str, status: str = "Pending", parent=None):
        super().__init__(parent)
        self.title = title
        self.time_ago = time_ago
        self.status = status
        self.setObjectName("activityTimelineRow")
        self.init_ui()

    def init_ui(self):
        dot_color, chip_bg, chip_fg = self.STATUS_STYLE.get(
            self.status,
            (COLOR_GRAY_400, COLOR_GRAY_100, COLOR_GRAY_600),
        )

        layout = QHBoxLayout(self)
        layout.setContentsMargins(8, 8, 8, 8)
        layout.setSpacing(12)

        dot = QLabel("●")
        dot.setObjectName("activityDot")
        dot.setStyleSheet(f"color: {dot_color}; font-size: 15px; border: none; background: transparent;")
        dot.setFixedWidth(16)
        layout.addWidget(dot, alignment=Qt.AlignmentFlag.AlignTop)

        text_layout = QVBoxLayout()
        text_layout.setSpacing(2)

        title_label = QLabel(self.title)
        title_label.setObjectName("activityTitle")
        title_label.setWordWrap(True)
        text_layout.addWidget(title_label)

        time_label = QLabel(self.time_ago)
        time_label.setObjectName("activityTime")
        text_layout.addWidget(time_label)

        layout.addLayout(text_layout, 1)

        status_chip = QLabel(self.status)
        status_chip.setObjectName("activityStatusChip")
        status_chip.setStyleSheet(
            f"""
            background-color: {chip_bg};
            color: {chip_fg};
            border: none;
            border-radius: 11px;
            padding: 4px 10px;
            font-weight: 600;
            """
        )
        layout.addWidget(status_chip, alignment=Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)


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
    
    navigate_to_tab = pyqtSignal(int)

    def __init__(self, user_id: int, username: str = "", parent=None):
        super().__init__(parent)
        self.user_id = user_id
        self.username = username
        self.alert_banner: Optional[AlertBanner] = None
        self.date_label: Optional[QLabel] = None
        self.stat_cards: List[StatCard] = []
        self.deadline_cards_layout: Optional[QHBoxLayout] = None
        self.favorite_items_layout: Optional[QVBoxLayout] = None
        self.activity_items_layout: Optional[QVBoxLayout] = None
        self.refresh_btn: Optional[QPushButton] = None
        self.sync_btn: Optional[QPushButton] = None
        self._sync_thread = None
        self._sync_in_progress = False
        
        logger.info(f"Initializing BerandaTab for user {user_id}")
        self.init_ui()
        self.load_dashboard_data()
    
    def init_ui(self):
        """Initialize Beranda Tab UI."""
        # Create scroll area untuk enable scrolling
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setStyleSheet(f"""
            QScrollArea {{
                background-color: {COLOR_GRAY_BACKGROUND};
                border: none;
            }}
            QScrollBar:vertical {{
                width: 8px;
                background-color: {COLOR_GRAY_200};
            }}
            QScrollBar::handle:vertical {{
                background-color: {COLOR_GRAY_400};
                border-radius: 4px;
            }}
            QScrollBar::handle:vertical:hover {{
                background-color: {COLOR_GRAY_500};
            }}
        """)
        
        # Content widget dengan main layout
        content_widget = QWidget()
        main_layout = QVBoxLayout(content_widget)
        main_layout.setContentsMargins(16, 16, 16, 16)  # SPACING_4
        main_layout.setSpacing(12)  # SPACING_3
        
        # Set scroll area
        self.setStyleSheet(f"""
            QWidget {{
                background-color: {COLOR_GRAY_BACKGROUND};
            }}
        """)
        scroll_area.setWidget(content_widget)
        
        # Tambah scroll area ke main widget
        main_parent_layout = QVBoxLayout(self)
        main_parent_layout.setContentsMargins(0, 0, 0, 0)
        main_parent_layout.addWidget(scroll_area)
        
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
        
        self.date_label = QLabel(datetime.now().strftime("%A, %d %B %Y"))
        self.date_label.setFont(QFont(FONT_FAMILY_PRIMARY, FONT_SIZE_BASE))
        self.date_label.setStyleSheet(f"color: {COLOR_GRAY_600};")
        greeting_layout.addWidget(self.date_label)
        
        header_layout.addLayout(greeting_layout)
        header_layout.addStretch()
        
        # Action buttons
        self.refresh_btn = QPushButton("🔄 Refresh Data")
        self.refresh_btn.setStyleSheet(get_button_solid_stylesheet("navy"))
        self.refresh_btn.setMaximumWidth(130)
        self.refresh_btn.clicked.connect(self.refresh_data)
        header_layout.addWidget(self.refresh_btn)

        self.sync_btn = QPushButton("🌐 Sync dari Web")
        self.sync_btn.setStyleSheet(get_button_solid_stylesheet("orange"))
        self.sync_btn.setMaximumWidth(160)
        self.sync_btn.clicked.connect(self.sync_from_web)
        header_layout.addWidget(self.sync_btn)
        
        lihat_semua_btn = QPushButton("📋 Lihat Semua Beasiswa")
        lihat_semua_btn.setStyleSheet(get_button_solid_stylesheet("gray"))
        lihat_semua_btn.setMaximumWidth(180)
        lihat_semua_btn.clicked.connect(lambda: self.navigate_to_tab.emit(1))
        header_layout.addWidget(lihat_semua_btn)
        
        main_layout.addLayout(header_layout)
        main_layout.addSpacing(8)  # SPACING_2
        
        # ===== ALERT BANNER =====
        self.alert_banner = AlertBanner(
            alert_type="warning",
            message="Memuat data dashboard...",
            closable=True
        )
        main_layout.addWidget(self.alert_banner)
        main_layout.addSpacing(8)  # SPACING_2
        
        # ===== STAT CARDS SECTION =====
        stats_layout = QGridLayout()
        stats_layout.setSpacing(12)  # SPACING_3
        
        stat_configs = [
            {"icon": "📚", "label": "Total Beasiswa", "number": "0", "desc": "Tersedia di database", "color": COLOR_NAVY},
            {"icon": "⏰", "label": "Deadline Minggu Ini", "number": "0", "desc": "Segera daftar!", "color": COLOR_ERROR},
            {"icon": "📄", "label": "Total Lamaranku", "number": "0", "desc": "Tercatat di Tracker", "color": COLOR_NAVY},
            {"icon": "✅", "label": "Diterima", "number": "0", "desc": "Selamat, terus semangat!", "color": COLOR_SUCCESS},
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
        
        self.deadline_cards_layout = QHBoxLayout()
        self.deadline_cards_layout.setSpacing(12)  # SPACING_3
        main_layout.addLayout(self.deadline_cards_layout)
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
        lihat_fav_btn.clicked.connect(lambda: self.navigate_to_tab.emit(1))
        fav_section.addWidget(lihat_fav_btn)
        
        main_layout.addLayout(fav_section)

        fav_items_widget = QFrame()
        fav_items_widget.setObjectName("dashboardListCard")
        self.favorite_items_layout = QVBoxLayout(fav_items_widget)
        self.favorite_items_layout.setContentsMargins(8, 8, 8, 8)
        self.favorite_items_layout.setSpacing(8)
        main_layout.addWidget(fav_items_widget)
        
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
        lihat_activity_btn.clicked.connect(lambda: self.navigate_to_tab.emit(2))
        activity_section.addWidget(lihat_activity_btn)
        
        main_layout.addLayout(activity_section)

        activity_items_widget = QFrame()
        activity_items_widget.setObjectName("dashboardListCard")
        self.activity_items_layout = QVBoxLayout(activity_items_widget)
        self.activity_items_layout.setContentsMargins(8, 8, 8, 8)
        self.activity_items_layout.setSpacing(0)
        main_layout.addWidget(activity_items_widget)
        
        main_layout.addStretch()
        
        # Apply stylesheet to main widget
        self.setStyleSheet(f"""
            QWidget {{
                background-color: {COLOR_GRAY_BACKGROUND};
            }}
            QFrame#dashboardListCard {{
                background-color: {COLOR_WHITE};
                border: 1px solid {COLOR_GRAY_200};
                border-radius: {BORDER_RADIUS_MD};
            }}
            QFrame#favoriteRow {{
                background-color: {COLOR_WHITE};
                border: 1px solid {COLOR_GRAY_200};
                border-radius: {BORDER_RADIUS_MD};
            }}
            QLabel#favoriteStar {{
                background-color: #fff7ed;
                border: none;
                border-radius: 14px;
            }}
            QLabel#favoriteTitle {{
                color: {COLOR_NAVY};
                font-size: {FONT_SIZE_MD}px;
                font-weight: 700;
                border: none;
                background: transparent;
            }}
            QLabel#favoriteSubtitle {{
                color: {COLOR_GRAY_500};
                font-size: {FONT_SIZE_SM}px;
                border: none;
                background: transparent;
            }}
            QLabel#activityTitle {{
                color: {COLOR_NAVY};
                font-size: {FONT_SIZE_MD}px;
                font-weight: 600;
                border: none;
                background: transparent;
            }}
            QLabel#activityTime {{
                color: {COLOR_GRAY_500};
                font-size: {FONT_SIZE_SM}px;
                border: none;
                background: transparent;
            }}
        """)

    def _clear_layout(self, layout: Optional[QVBoxLayout]):
        """Remove all widgets/items from a layout."""
        if layout is None:
            return

        while layout.count():
            item = layout.takeAt(0)
            widget = item.widget()
            if widget is not None:
                widget.deleteLater()

    def _render_deadline_cards(self, cards: List[Dict[str, Any]]):
        """Render nearest deadline cards from snapshot data."""
        self._clear_layout(self.deadline_cards_layout)

        if not cards:
            empty_label = QLabel("Belum ada deadline dekat untuk ditampilkan.")
            empty_label.setStyleSheet(f"color: {COLOR_GRAY_500}; padding: 8px 0;")
            self.deadline_cards_layout.addWidget(empty_label)
            self.deadline_cards_layout.addStretch()
            return

        for card_data in cards:
            card = BeasiswaDeadlineCard(
                judul=card_data.get("judul", "(Tanpa Judul)"),
                penyelenggara=card_data.get("penyelenggara", "Tidak Ada"),
                jenjang=card_data.get("jenjang", "-"),
                deadline=card_data.get("deadline", "-"),
                urgency=card_data.get("urgency", "warning"),
            )
            card.setMaximumWidth(320)
            self.deadline_cards_layout.addWidget(card)

        self.deadline_cards_layout.addStretch()

    def _render_favorites(self, favorites: List[Dict[str, Any]]):
        """Render favorite scholarships section from DB data."""
        self._clear_layout(self.favorite_items_layout)

        if not favorites:
            empty_label = QLabel("Belum ada beasiswa favorit. Tambahkan dari tab Beasiswa.")
            empty_label.setStyleSheet(f"color: {COLOR_GRAY_500}; padding: 8px 0;")
            self.favorite_items_layout.addWidget(empty_label)
            return

        for item in favorites:
            subtitle = (
                f"{item.get('provider', 'Penyelenggara tidak diketahui')}"
                f" • {item.get('jenjang', '-')}"
            )
            fav_widget = FavoriteScholarshipItem(
                title=item.get("title", "(Tanpa Judul)"),
                subtitle=subtitle,
                status=item.get("status", "Buka"),
            )
            self.favorite_items_layout.addWidget(fav_widget)

    def _render_activities(self, activities: List[Dict[str, Any]]):
        """Render recent activities from tracker records."""
        self._clear_layout(self.activity_items_layout)

        if not activities:
            empty_label = QLabel("Belum ada aktivitas lamaran terbaru.")
            empty_label.setStyleSheet(f"color: {COLOR_GRAY_500}; padding: 8px 0;")
            self.activity_items_layout.addWidget(empty_label)
            return

        total_items = len(activities)
        for idx, activity in enumerate(activities):
            activity_widget = ActivityTimelineItem(
                title=activity.get("title", "Aktivitas"),
                time_ago=activity.get("time", ""),
                status=activity.get("status", "Pending"),
            )
            self.activity_items_layout.addWidget(activity_widget)

            if idx < total_items - 1:
                separator = QFrame()
                separator.setObjectName("activitySeparator")
                separator.setFixedHeight(1)
                separator.setStyleSheet(f"background-color: {COLOR_GRAY_200}; border: none;")
                self.activity_items_layout.addWidget(separator)

    def _set_sync_state(self, syncing: bool):
        """Toggle UI state while sync job is running."""
        self._sync_in_progress = syncing

        if self.sync_btn:
            self.sync_btn.setEnabled(not syncing)
            self.sync_btn.setText("⏳ Sinkronisasi..." if syncing else "🌐 Sync dari Web")

        if self.refresh_btn:
            self.refresh_btn.setEnabled(not syncing)
    
    def load_dashboard_data(self):
        """Load dashboard data snapshot dari service layer (real DB)."""
        try:
            snapshot = get_beranda_snapshot(self.user_id)
            stats = snapshot.get("stats", {})

            if self.alert_banner:
                self.alert_banner.set_message(snapshot.get("alert_message", "Dashboard siap digunakan."))

            if len(self.stat_cards) >= 4:
                self.stat_cards[0].set_data(str(stats.get("total_beasiswa", 0)))
                self.stat_cards[1].set_data(str(stats.get("deadline_minggu_ini", 0)))
                self.stat_cards[2].set_data(str(stats.get("total_lamaran", 0)))
                self.stat_cards[3].set_data(str(stats.get("diterima", 0)))

            self._render_deadline_cards(snapshot.get("deadline_cards", []))
            self._render_favorites(snapshot.get("favorites", []))
            self._render_activities(snapshot.get("activities", []))

            if self.date_label:
                self.date_label.setText(datetime.now().strftime("%A, %d %B %Y"))

            logger.info("Beranda snapshot loaded successfully")
            
        except Exception as e:
            logger.error(f"Error loading dashboard data: {e}")

    def _finish_sync(self, summary: Dict[str, int]):
        """Finalize sync job and refresh dashboard UI."""
        self.load_dashboard_data()

        if self.alert_banner:
            self.alert_banner.set_message(
                "Sync selesai. "
                f"Scraped: {summary.get('scraped', 0)} | "
                f"Baru: {summary.get('inserted', 0)} | "
                f"Update: {summary.get('updated', 0)} | "
                f"Lewati: {summary.get('skipped', 0)} | "
                f"Error: {summary.get('errors', 0)}"
            )

        self._set_sync_state(False)

    def _on_scrape_finished(self, scrape_payload: object):
        """Handle scraper thread completion and persist result into DB."""
        summary = sync_beasiswa_from_scraper(scrape_payload if isinstance(scrape_payload, dict) else None)
        self._finish_sync(summary)

    def _on_scrape_error(self, message: str):
        """Handle scraper thread error."""
        logger.error("Sync error: %s", message)
        if self.alert_banner:
            self.alert_banner.set_message(f"Gagal sinkronisasi: {message}")
        self._set_sync_state(False)

    def sync_from_web(self):
        """Run scraping sync job and refresh all beranda sections."""
        if self._sync_in_progress:
            return

        self._set_sync_state(True)
        if self.alert_banner:
            self.alert_banner.set_message("Sedang sinkronisasi data terbaru dari web...")

        thread = get_scraper_thread()
        if thread is None:
            summary = sync_beasiswa_from_scraper()
            self._finish_sync(summary)
            return

        self._sync_thread = thread
        self._sync_thread.finished.connect(self._on_scrape_finished)
        self._sync_thread.error.connect(self._on_scrape_error)
        self._sync_thread.start()
    
    def refresh_data(self):
        """Refresh dashboard data."""
        self.load_dashboard_data()
