"""
Sidebar Navigation Component for BeasiswaKu
Collapsible sidebar with navigation to all main tabs
"""

import logging
from typing import Callable, Dict, List

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QScrollArea, QFrame
)
from PyQt6.QtCore import Qt, pyqtSignal, QSize, QPropertyAnimation, QRect, QEasingCurve
from PyQt6.QtGui import QFont, QColor, QIcon

from src.gui.design_tokens import *

logger = logging.getLogger(__name__)


class SidebarNavItem(QPushButton):
    """Navigation item button with icon and label."""
    
    def __init__(self, icon: str, label: str, parent=None):
        super().__init__(parent)
        self.icon = icon
        self.label = label
        self.is_active = False
        
        self.setText(f"{icon}  {label}")
        self.setFont(QFont(FONT_FAMILY_PRIMARY, FONT_SIZE_BASE))
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        self.setMinimumHeight(48)
        self.update_style()
    
    def set_active(self, active: bool):
        """Set whether this item is active."""
        self.is_active = active
        self.update_style()
    
    def update_style(self):
        """Update button style based on active state."""
        if self.is_active:
            self.setStyleSheet(f"""
                QPushButton {{
                    background-color: qlineargradient(
                        x1:0, y1:0, x2:1, y2:0,
                        stop:0 {COLOR_COBALT}, stop:1 {COLOR_COBALT_LIGHT}
                    );
                    color: {COLOR_WHITE};
                    border: 1px solid {COLOR_COBALT_DARK};
                    border-radius: 10px;
                    padding: 12px 14px;
                    margin: 2px 8px;
                    text-align: left;
                    font-weight: 600;
                }}
                QPushButton:hover {{
                    background-color: qlineargradient(
                        x1:0, y1:0, x2:1, y2:0,
                        stop:0 {COLOR_COBALT}, stop:1 {COLOR_COBALT}
                    );
                }}
            """)
        else:
            self.setStyleSheet(f"""
                QPushButton {{
                    background-color: transparent;
                    color: {COLOR_GRAY_600};
                    border: 1px solid transparent;
                    border-radius: 10px;
                    padding: 12px 14px;
                    margin: 2px 8px;
                    text-align: left;
                }}
                QPushButton:hover {{
                    background-color: {COLOR_WHITE};
                    color: {COLOR_COBALT};
                    border: 1px solid #d7e2f2;
                }}
            """)


class Sidebar(QWidget):
    """
    Sidebar Navigation Component for BeasiswaKu.
    
    Features:
    - Collapsible sidebar with navigation items
    - 5 main menu items: Beranda, Beasiswa, Tracker, Statistik, Profil
    - Active indicator with Orange highlight
    - Smooth hover effects
    - Navy + Orange theming
    - Professional spacing and typography
    
    Layout:
    ┌──────────────────┐
    │ 🎓 BeasiswaKu    │  <- Header
    ├──────────────────┤
    │ 🏠 Beranda   <-- │  <- Active item (Orange)
    │ 📚 Beasiswa      │
    │ 📋 Tracker       │
    │ 📊 Statistik     │
    │ 👤 Profil        │
    ├──────────────────┤
    │                  │  <- Spacer
    │ ⚙️  Pengaturan   │  <- Settings
    │ 🚪 Keluar        │  <- Logout
    └──────────────────┘
    """
    
    # Signals
    nav_clicked = pyqtSignal(int)  # Tab index
    settings_clicked = pyqtSignal()
    logout_clicked = pyqtSignal()
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.nav_items: Dict[int, SidebarNavItem] = {}
        self.current_active = 0
        self.is_expanded = True
        
        logger.info("Initializing Sidebar Navigation")
        self.init_ui()
    
    def init_ui(self):
        """Initialize sidebar UI."""
        self.setObjectName("sidebarRoot")
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)
        
        # ===== HEADER SECTION =====
        header_frame = QFrame()
        header_frame.setObjectName("sidebarHeader")
        header_frame.setStyleSheet(f"""
            QFrame#sidebarHeader {{
                background-color: qlineargradient(
                    x1:0, y1:0, x2:1, y2:0,
                    stop:0 {COLOR_COBALT_DARK}, stop:1 {COLOR_COBALT}
                );
                border-bottom: 1px solid #0b2a53;
            }}
        """)
        header_frame.setMinimumHeight(94)
        header_frame.setMaximumHeight(94)
        
        header_layout = QVBoxLayout(header_frame)
        header_layout.setContentsMargins(14, 10, 14, 10)
        header_layout.setSpacing(2)
        
        # Logo
        logo_label = QLabel("🎓 BeasiswaKu")
        logo_label.setObjectName("sidebarLogo")
        logo_font = QFont(FONT_FAMILY_PRIMARY, FONT_SIZE_XL)
        logo_font.setWeight(QFont.Weight.Bold)
        logo_label.setFont(logo_font)
        logo_label.setStyleSheet(f"color: {COLOR_WHITE}; letter-spacing: 0.2px;")
        header_layout.addWidget(logo_label)
        
        # Tagline
        tagline_label = QLabel("Discover • Track • Apply")
        tagline_label.setObjectName("sidebarTagline")
        tagline_label.setFont(QFont(FONT_FAMILY_PRIMARY, FONT_SIZE_XS))
        tagline_label.setStyleSheet(f"color: #c9d8f0;")
        header_layout.addWidget(tagline_label)

        badge_row = QHBoxLayout()
        badge_row.setContentsMargins(0, 4, 0, 0)
        badge_row.setSpacing(0)
        edition_badge = QLabel("Desktop Edition")
        edition_badge.setObjectName("editionBadge")
        edition_badge.setFont(QFont(FONT_FAMILY_PRIMARY, FONT_SIZE_XS))
        edition_badge.setStyleSheet(
            f"background-color: {COLOR_AMBER}; color: #3a2a00; "
            "padding: 2px 10px; border-radius: 9px; font-weight: 700;"
        )
        edition_badge.setAlignment(Qt.AlignmentFlag.AlignLeft)
        edition_badge.setFixedHeight(18)
        edition_badge.setMaximumWidth(108)
        badge_row.addWidget(edition_badge, alignment=Qt.AlignmentFlag.AlignLeft)
        badge_row.addStretch()
        header_layout.addLayout(badge_row)
        
        main_layout.addWidget(header_frame)
        
        # ===== NAVIGATION SECTION (Scroll Area) =====
        nav_scroll = QScrollArea()
        nav_scroll.setWidgetResizable(True)
        nav_scroll.setStyleSheet(f"""
            QScrollArea {{
                border: none;
                background-color: {COLOR_SURFACE_SOFT};
            }}
            QScrollBar:vertical {{
                border: none;
                background-color: {COLOR_SURFACE_SOFT};
                width: 6px;
            }}
            QScrollBar::handle:vertical {{
                background-color: #c7d6eb;
                border-radius: 3px;
            }}
            QScrollBar::handle:vertical:hover {{
                background-color: #9eb6d7;
            }}
        """)
        
        nav_widget = QWidget()
        nav_layout = QVBoxLayout(nav_widget)
        nav_layout.setContentsMargins(0, 10, 0, 10)
        nav_layout.setSpacing(4)
        
        # Navigation menu items
        menu_items = [
            (0, "🏠", "Beranda"),
            (1, "📚", "Beasiswa"),
            (2, "📋", "Tracker Lamaran"),
            (3, "📊", "Statistik"),
            (4, "👤", "Profil"),
        ]
        
        for tab_index, icon, label in menu_items:
            item = SidebarNavItem(icon, label)
            item.clicked.connect(lambda checked, idx=tab_index: self.on_nav_item_clicked(idx))
            nav_layout.addWidget(item)
            self.nav_items[tab_index] = item
        
        nav_layout.addStretch()
        nav_scroll.setWidget(nav_widget)
        main_layout.addWidget(nav_scroll, 1)
        
        # ===== BOTTOM ACTION SECTION =====
        bottom_frame = QFrame()
        bottom_frame.setStyleSheet(f"""
            QFrame {{
                background-color: {COLOR_SURFACE_SOFT};
                border-top: 1px solid #d7e1f1;
            }}
        """)
        bottom_frame.setMinimumHeight(120)
        
        bottom_layout = QVBoxLayout(bottom_frame)
        bottom_layout.setContentsMargins(8, 8, 8, 8)
        bottom_layout.setSpacing(4)
        
        # Settings button
        settings_btn = QPushButton("⚙️  Pengaturan")
        settings_btn.setFont(QFont(FONT_FAMILY_PRIMARY, FONT_SIZE_BASE))
        settings_btn.setMinimumHeight(40)
        settings_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        settings_btn.setStyleSheet(f"""
            QPushButton {{
                background-color: transparent;
                color: {COLOR_GRAY_600};
                border: 1px solid transparent;
                border-radius: 10px;
                padding: 10px 12px;
                margin: 0 4px;
                text-align: left;
            }}
            QPushButton:hover {{
                background-color: {COLOR_WHITE};
                color: {COLOR_COBALT};
                border: 1px solid #d7e2f2;
            }}
        """)
        settings_btn.clicked.connect(self.settings_clicked.emit)
        bottom_layout.addWidget(settings_btn)
        
        # Logout button
        logout_btn = QPushButton("🚪  Keluar")
        logout_btn.setFont(QFont(FONT_FAMILY_PRIMARY, FONT_SIZE_BASE))
        logout_btn.setMinimumHeight(40)
        logout_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        logout_btn.setStyleSheet(f"""
            QPushButton {{
                background-color: transparent;
                color: {COLOR_ERROR};
                border: 1px solid transparent;
                border-radius: 10px;
                padding: 10px 12px;
                margin: 0 4px;
                text-align: left;
                font-weight: 600;
            }}
            QPushButton:hover {{
                background-color: {COLOR_ERROR_LIGHT};
                color: {COLOR_ERROR};
                border: 1px solid #f5c7c7;
            }}
        """)
        logout_btn.clicked.connect(self.logout_clicked.emit)
        bottom_layout.addWidget(logout_btn)
        
        main_layout.addWidget(bottom_frame)
        
        # Apply main stylesheet
        self.setStyleSheet(f"""
            QWidget#sidebarRoot {{
                background-color: {COLOR_SURFACE_SOFT};
                border-right: 1px solid #d9e2f0;
            }}
        """)
        
        # Set initial active item
        self.set_active_item(0)
    
    def on_nav_item_clicked(self, tab_index: int):
        """Handle navigation item click."""
        self.set_active_item(tab_index)
        self.nav_clicked.emit(tab_index)
        logger.info(f"Navigation clicked: tab {tab_index}")
    
    def set_active_item(self, tab_index: int):
        """Set active navigation item."""
        # Deactivate previous
        if self.current_active in self.nav_items:
            self.nav_items[self.current_active].set_active(False)
        
        # Activate new
        if tab_index in self.nav_items:
            self.nav_items[tab_index].set_active(True)
            self.current_active = tab_index
    
    def toggle_expand(self):
        """Toggle sidebar expansion (for future collapsible feature)."""
        self.is_expanded = not self.is_expanded
        logger.info(f"Sidebar toggled: {'expanded' if self.is_expanded else 'collapsed'}")
