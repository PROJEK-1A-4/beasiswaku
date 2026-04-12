"""
PyQt6 Stylesheets for BeasiswaKu Application
Uses design tokens to provide consistent styling across the application
"""

from src.gui.design_tokens import *

def get_stylesheet():
    """
    Returns the complete QSS (Qt Stylesheet) for BeasiswaKu application
    using design tokens for colors, fonts, spacing, and styling
    """
    
    stylesheet = f"""
    /* ========================================================================
       GLOBAL STYLES
       ======================================================================== */
    
    * {{
        font-family: {FONT_FAMILY_PRIMARY};
        font-size: {FONT_SIZE_BASE}px;
        color: {COLOR_GRAY_900};
    }}
    
    QMainWindow {{
        background-color: {COLOR_WHITE};
    }}
    
    QWidget {{
        background-color: {COLOR_WHITE};
    }}
    
    /* ========================================================================
       BUTTONS
       ======================================================================== */
    
    QPushButton {{
        background-color: {COLOR_NAVY};
        color: {COLOR_WHITE};
        border: none;
        border-radius: {BORDER_RADIUS_MD};
        padding: 8px 16px;
        font-weight: {FONT_WEIGHT_MEDIUM};
        font-size: {FONT_SIZE_MD}px;
        cursor: pointer;
    }}
    
    QPushButton:hover {{
        background-color: {COLOR_NAVY_DARK};
    }}
    
    QPushButton:pressed {{
        background-color: {COLOR_NAVY_DARK};
    }}
    
    QPushButton:disabled {{
        background-color: {COLOR_GRAY_300};
        color: {COLOR_GRAY_500};
    }}
    
    /* Primary Orange Button */
    QPushButton.button-primary-orange {{
        background-color: {COLOR_ORANGE};
        color: {COLOR_WHITE};
    }}
    
    QPushButton.button-primary-orange:hover {{
        background-color: {COLOR_ORANGE_DARK};
    }}
    
    /* Outlined Button */
    QPushButton.button-outlined {{
        background-color: {COLOR_WHITE};
        color: {COLOR_NAVY};
        border: {BORDER_WIDTH_SM} solid {COLOR_NAVY};
    }}
    
    QPushButton.button-outlined:hover {{
        background-color: {COLOR_GRAY_50};
        border: {BORDER_WIDTH_SM} solid {COLOR_NAVY_DARK};
        color: {COLOR_NAVY_DARK};
    }}
    
    /* Outlined Orange Button */
    QPushButton.button-outlined-orange {{
        background-color: {COLOR_WHITE};
        color: {COLOR_ORANGE};
        border: {BORDER_WIDTH_SM} solid {COLOR_ORANGE};
    }}
    
    QPushButton.button-outlined-orange:hover {{
        background-color: {COLOR_WARNING_LIGHT};
        border: {BORDER_WIDTH_SM} solid {COLOR_ORANGE_DARK};
        color: {COLOR_ORANGE_DARK};
    }}
    
    /* Danger/Delete Button */
    QPushButton.button-danger {{
        background-color: {COLOR_ERROR};
        color: {COLOR_WHITE};
    }}
    
    QPushButton.button-danger:hover {{
        background-color: {COLOR_ERROR_DARK};
    }}
    
    /* Small Button */
    QPushButton.button-sm {{
        padding: 6px 12px;
        font-size: {FONT_SIZE_SM}px;
        height: {BUTTON_HEIGHT_SM};
    }}
    
    /* Large Button */
    QPushButton.button-lg {{
        padding: 12px 24px;
        font-size: {FONT_SIZE_LG}px;
        height: {BUTTON_HEIGHT_LG};
    }}
    
    /* ========================================================================
       LABELS & TEXT
       ======================================================================== */
    
    QLabel {{
        color: {COLOR_GRAY_900};
    }}
    
    QLabel.label-title {{
        font-size: {FONT_SIZE_2XL}px;
        font-weight: {FONT_WEIGHT_BOLD};
        color: {COLOR_NAVY};
    }}
    
    QLabel.label-subtitle {{
        font-size: {FONT_SIZE_LG}px;
        font-weight: {FONT_WEIGHT_SEMIBOLD};
        color: {COLOR_NAVY};
    }}
    
    QLabel.label-secondary {{
        color: {COLOR_GRAY_600};
        font-size: {FONT_SIZE_SM}px;
    }}
    
    QLabel.label-success {{
        color: {COLOR_SUCCESS};
        font-weight: {FONT_WEIGHT_MEDIUM};
    }}
    
    QLabel.label-warning {{
        color: {COLOR_WARNING};
        font-weight: {FONT_WEIGHT_MEDIUM};
    }}
    
    QLabel.label-error {{
        color: {COLOR_ERROR};
        font-weight: {FONT_WEIGHT_MEDIUM};
    }}
    
    /* ========================================================================
       INPUT FIELDS (QLineEdit, QTextEdit, QComboBox)
       ======================================================================== */
    
    QLineEdit, QTextEdit, QComboBox {{
        background-color: {COLOR_WHITE};
        border: {BORDER_WIDTH_SM} solid {COLOR_GRAY_200};
        border-radius: {BORDER_RADIUS_MD};
        padding: 8px 12px;
        font-size: {FONT_SIZE_BASE}px;
        color: {COLOR_GRAY_900};
    }}
    
    QLineEdit:focus, QTextEdit:focus, QComboBox:focus {{
        border: {BORDER_WIDTH_SM} solid {COLOR_NAVY};
        outline: none;
    }}
    
    QLineEdit:hover, QTextEdit:hover, QComboBox:hover {{
        border: {BORDER_WIDTH_SM} solid {COLOR_GRAY_300};
    }}
    
    QLineEdit:disabled, QTextEdit:disabled, QComboBox:disabled {{
        background-color: {COLOR_GRAY_100};
        color: {COLOR_GRAY_500};
        border: {BORDER_WIDTH_SM} solid {COLOR_GRAY_200};
    }}
    
    /* ========================================================================
       TABLE
       ======================================================================== */
    
    QTableWidget {{
        background-color: {COLOR_WHITE};
        alternate-background-color: {COLOR_GRAY_50};
        gridline-color: {COLOR_GRAY_200};
        border: {BORDER_WIDTH_SM} solid {COLOR_GRAY_200};
        border-radius: {BORDER_RADIUS_MD};
    }}
    
    QTableWidget::item {{
        padding: 8px 12px;
        border-bottom: {BORDER_WIDTH_SM} solid {COLOR_GRAY_200};
    }}
    
    QTableWidget::item:selected {{
        background-color: {COLOR_NAVY};
        color: {COLOR_WHITE};
    }}
    
    QHeaderView::section {{
        background-color: {COLOR_NAVY};
        color: {COLOR_WHITE};
        padding: 8px 12px;
        border: none;
        font-weight: {FONT_WEIGHT_SEMIBOLD};
        font-size: {FONT_SIZE_MD}px;
        text-align: left;
    }}
    
    /* ========================================================================
       DIALOG & MESSAGE BOXES
       ======================================================================== */
    
    QDialog {{
        background-color: {COLOR_WHITE};
    }}
    
    QMessageBox {{
        background-color: {COLOR_WHITE};
    }}
    
    QMessageBox QLabel {{
        color: {COLOR_GRAY_900};
    }}
    
    /* ========================================================================
       TAB WIDGET
       ======================================================================== */
    
    QTabWidget::pane {{
        border: {BORDER_WIDTH_SM} solid {COLOR_GRAY_200};
    }}
    
    QTabBar::tab {{
        background-color: {COLOR_GRAY_100};
        color: {COLOR_GRAY_700};
        padding: 8px 16px;
        border: {BORDER_WIDTH_SM} solid {COLOR_GRAY_200};
        border-bottom: none;
        font-weight: {FONT_WEIGHT_MEDIUM};
    }}
    
    QTabBar::tab:selected {{
        background-color: {COLOR_NAVY};
        color: {COLOR_WHITE};
        border: {BORDER_WIDTH_SM} solid {COLOR_NAVY};
    }}
    
    QTabBar::tab:hover {{
        background-color: {COLOR_GRAY_200};
    }}
    
    /* ========================================================================
       SCROLL BARS
       ======================================================================== */
    
    QScrollBar:vertical {{
        background-color: {COLOR_GRAY_50};
        width: 12px;
        margin: 0px;
    }}
    
    QScrollBar::handle:vertical {{
        background-color: {COLOR_GRAY_400};
        border-radius: 6px;
        min-height: 20px;
    }}
    
    QScrollBar::handle:vertical:hover {{
        background-color: {COLOR_GRAY_600};
    }}
    
    QScrollBar:horizontal {{
        background-color: {COLOR_GRAY_50};
        height: 12px;
        margin: 0px;
    }}
    
    QScrollBar::handle:horizontal {{
        background-color: {COLOR_GRAY_400};
        border-radius: 6px;
        min-width: 20px;
    }}
    
    QScrollBar::handle:horizontal:hover {{
        background-color: {COLOR_GRAY_600};
    }}
    
    QScrollBar::sub-line, QScrollBar::add-line {{
        background: none;
        border: none;
    }}
    
    /* ========================================================================
       GROUP BOXES
       ======================================================================== */
    
    QGroupBox {{
        border: {BORDER_WIDTH_SM} solid {COLOR_GRAY_200};
        border-radius: {BORDER_RADIUS_MD};
        margin-top: 10px;
        padding-top: 10px;
        font-weight: {FONT_WEIGHT_MEDIUM};
        color: {COLOR_NAVY};
    }}
    
    QGroupBox::title {{
        subcontrol-origin: margin;
        left: 15px;
        padding: 0 3px 0 3px;
    }}
    
    /* ========================================================================
       COMBO BOX
       ======================================================================== */
    
    QComboBox::drop-down {{
        border: none;
        background-color: transparent;
    }}
    
    QComboBox::down-arrow {{
        image: none;
        width: 0px;
    }}
    
    QComboBox QAbstractItemView {{
        background-color: {COLOR_WHITE};
        selection-background-color: {COLOR_NAVY};
        border: {BORDER_WIDTH_SM} solid {COLOR_GRAY_200};
    }}
    """
    
    return stylesheet


def get_alert_banner_stylesheet(alert_type="info"):
    """
    Returns stylesheet for alert/warning banners
    alert_type: 'success', 'warning', 'error', 'info'
    """
    
    color_map = {
        "success": (COLOR_SUCCESS, COLOR_SUCCESS_LIGHT),
        "warning": (COLOR_WARNING, COLOR_WARNING_LIGHT),
        "error": (COLOR_ERROR, COLOR_ERROR_LIGHT),
        "info": (COLOR_INFO, COLOR_INFO_LIGHT),
    }
    
    text_color, bg_color = color_map.get(alert_type, (COLOR_INFO, COLOR_INFO_LIGHT))
    
    stylesheet = f"""
    QFrame {{
        background-color: {bg_color};
        border-left: 4px solid {text_color};
        border-radius: {BORDER_RADIUS_MD};
        padding: 12px 16px;
    }}
    
    QLabel {{
        color: {text_color};
        font-weight: {FONT_WEIGHT_MEDIUM};
    }}
    """
    
    return stylesheet


def get_status_badge_stylesheet(status="pending"):
    """
    Returns stylesheet for status badges (pill-shaped)
    status: 'pending', 'approved', 'rejected', 'draft'
    """
    
    color_map = {
        "pending": (COLOR_STATUS_PENDING, "#dbeafe"),
        "approved": (COLOR_STATUS_APPROVED, COLOR_SUCCESS_LIGHT),
        "rejected": (COLOR_STATUS_REJECTED, COLOR_ERROR_LIGHT),
        "draft": (COLOR_STATUS_DRAFT, COLOR_GRAY_100),
    }
    
    text_color, bg_color = color_map.get(status, (COLOR_STATUS_PENDING, "#dbeafe"))
    
    stylesheet = f"""
    QLabel {{
        background-color: {bg_color};
        color: {text_color};
        border-radius: {BORDER_RADIUS_FULL};
        padding: 4px 12px;
        font-weight: {FONT_WEIGHT_MEDIUM};
        font-size: {FONT_SIZE_SM}px;
    }}
    """
    
    return stylesheet
