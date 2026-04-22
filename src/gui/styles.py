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


def get_input_field_stylesheet(disabled=False):
    """
    Backward-compatible input field stylesheet helper.

    Some GUI modules previously imported this symbol directly. Keeping this
    helper avoids runtime ImportError while returning the same token-based
    styling used across the app.
    """

    if disabled:
        return f"""
        QLineEdit, QTextEdit, QComboBox {{
            background-color: {COLOR_GRAY_100};
            border: {BORDER_WIDTH_SM} solid {COLOR_GRAY_200};
            border-radius: {BORDER_RADIUS_MD};
            padding: 8px 12px;
            font-size: {FONT_SIZE_BASE}px;
            color: {COLOR_GRAY_500};
        }}
        """

    return f"""
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
    """


# ==================== TASK 8: BUTTON VARIANTS (Solid/Outlined) ====================

def get_button_solid_stylesheet(color="navy", disabled=False):
    """
    Returns stylesheet for solid/filled buttons (primary style).
    
    Args:
        color: 'navy' (default), 'orange', 'success', 'error', 'gray'
        disabled: If True, applies disabled styling
    
    Example:
        btn.setStyleSheet(get_button_solid_stylesheet('orange'))
    """
    
    color_map = {
        "navy": {
            "bg": COLOR_NAVY,
            "bg_hover": COLOR_NAVY_DARK,
            "bg_pressed": COLOR_NAVY_DARK,
            "text": COLOR_WHITE,
        },
        "orange": {
            "bg": COLOR_ORANGE,
            "bg_hover": COLOR_ORANGE_DARK,
            "bg_pressed": COLOR_ORANGE_DARK,
            "text": COLOR_WHITE,
        },
        "success": {
            "bg": COLOR_SUCCESS,
            "bg_hover": "#059669",  # Darker green
            "bg_pressed": "#059669",
            "text": COLOR_WHITE,
        },
        "error": {
            "bg": COLOR_ERROR,
            "bg_hover": COLOR_ERROR_DARK,
            "bg_pressed": COLOR_ERROR_DARK,
            "text": COLOR_WHITE,
        },
        "gray": {
            "bg": COLOR_GRAY_500,
            "bg_hover": COLOR_GRAY_600,
            "bg_pressed": COLOR_GRAY_600,
            "text": COLOR_WHITE,
        },
    }
    
    colors = color_map.get(color, color_map["navy"])
    
    if disabled:
        return f"""
        QPushButton {{
            background-color: {COLOR_GRAY_300};
            color: {COLOR_GRAY_500};
            border: none;
            border-radius: {BORDER_RADIUS_MD};
            padding: 8px 16px;
            font-weight: {FONT_WEIGHT_MEDIUM};
            font-size: {FONT_SIZE_MD}px;
        }}
        """
    
    return f"""
    QPushButton {{
        background-color: {colors['bg']};
        color: {colors['text']};
        border: none;
        border-radius: {BORDER_RADIUS_MD};
        padding: 8px 16px;
        font-weight: {FONT_WEIGHT_MEDIUM};
        font-size: {FONT_SIZE_MD}px;
    }}
    QPushButton:hover {{
        background-color: {colors['bg_hover']};
    }}
    QPushButton:pressed {{
        background-color: {colors['bg_pressed']};
    }}
    QPushButton:disabled {{
        background-color: {COLOR_GRAY_300};
        color: {COLOR_GRAY_500};
    }}
    """


def get_button_outlined_stylesheet(color="navy", disabled=False):
    """
    Returns stylesheet for outlined/hollow buttons (secondary style).
    
    Args:
        color: 'navy' (default), 'orange', 'error', 'gray'
        disabled: If True, applies disabled styling
    
    Example:
        btn.setStyleSheet(get_button_outlined_stylesheet('orange'))
    """
    
    color_map = {
        "navy": {
            "border": COLOR_NAVY,
            "border_hover": COLOR_NAVY_DARK,
            "text": COLOR_NAVY,
            "text_hover": COLOR_NAVY_DARK,
            "bg_hover": COLOR_GRAY_50,
        },
        "orange": {
            "border": COLOR_ORANGE,
            "border_hover": COLOR_ORANGE_DARK,
            "text": COLOR_ORANGE,
            "text_hover": COLOR_ORANGE_DARK,
            "bg_hover": COLOR_WARNING_LIGHT,
        },
        "error": {
            "border": COLOR_ERROR,
            "border_hover": COLOR_ERROR_DARK,
            "text": COLOR_ERROR,
            "text_hover": COLOR_ERROR_DARK,
            "bg_hover": COLOR_ERROR_LIGHT,
        },
        "gray": {
            "border": COLOR_GRAY_300,
            "border_hover": COLOR_GRAY_400,
            "text": COLOR_GRAY_700,
            "text_hover": COLOR_GRAY_900,
            "bg_hover": COLOR_GRAY_100,
        },
    }
    
    colors = color_map.get(color, color_map["navy"])
    
    if disabled:
        return f"""
        QPushButton {{
            background-color: {COLOR_WHITE};
            color: {COLOR_GRAY_400};
            border: {BORDER_WIDTH_SM} solid {COLOR_GRAY_300};
            border-radius: {BORDER_RADIUS_MD};
            padding: 8px 16px;
            font-weight: {FONT_WEIGHT_MEDIUM};
            font-size: {FONT_SIZE_MD}px;
        }}
        """
    
    return f"""
    QPushButton {{
        background-color: {COLOR_WHITE};
        color: {colors['text']};
        border: {BORDER_WIDTH_SM} solid {colors['border']};
        border-radius: {BORDER_RADIUS_MD};
        padding: 8px 16px;
        font-weight: {FONT_WEIGHT_MEDIUM};
        font-size: {FONT_SIZE_MD}px;
    }}
    QPushButton:hover {{
        background-color: {colors['bg_hover']};
        color: {colors['text_hover']};
        border: {BORDER_WIDTH_SM} solid {colors['border_hover']};
    }}
    QPushButton:pressed {{
        background-color: {colors['bg_hover']};
        color: {colors['text_hover']};
        border: {BORDER_WIDTH_SM} solid {colors['border_hover']};
    }}
    QPushButton:disabled {{
        background-color: {COLOR_WHITE};
        color: {COLOR_GRAY_400};
        border: {BORDER_WIDTH_SM} solid {COLOR_GRAY_300};
    }}
    """


def get_button_icon_stylesheet(color="navy", has_border=True):
    """
    Returns stylesheet for icon-only buttons (Task 7).
    
    Args:
        color: 'navy' (default), 'error', 'gray', 'orange'
        has_border: If True, shows subtle border; if False, transparent
    
    Example:
        btn_edit.setStyleSheet(get_button_icon_stylesheet('navy'))
        btn_delete.setStyleSheet(get_button_icon_stylesheet('error'))
    """
    
    color_map = {
        "navy": {
            "icon_color": COLOR_NAVY,
            "border_color": COLOR_GRAY_300,
            "border_hover": COLOR_NAVY,
            "bg_hover": COLOR_GRAY_100,
        },
        "error": {
            "icon_color": COLOR_ERROR,
            "border_color": COLOR_GRAY_300,
            "border_hover": COLOR_ERROR,
            "bg_hover": COLOR_ERROR_LIGHT,
        },
        "gray": {
            "icon_color": COLOR_GRAY_600,
            "border_color": COLOR_GRAY_300,
            "border_hover": COLOR_GRAY_600,
            "bg_hover": COLOR_GRAY_100,
        },
        "orange": {
            "icon_color": COLOR_ORANGE,
            "border_color": COLOR_GRAY_300,
            "border_hover": COLOR_ORANGE,
            "bg_hover": COLOR_WARNING_LIGHT,
        },
    }
    
    colors = color_map.get(color, color_map["navy"])
    border_style = f"{BORDER_WIDTH_SM} solid {colors['border_color']}" if has_border else "none"
    
    return f"""
    QPushButton {{
        background-color: transparent;
        color: {colors['icon_color']};
        border: {border_style};
        border-radius: {BORDER_RADIUS_MD};
        padding: 4px;
        font-size: 16px;
    }}
    QPushButton:hover {{
        background-color: {colors['bg_hover']};
        border: {BORDER_WIDTH_SM} solid {colors['border_hover']};
    }}
    QPushButton:pressed {{
        background-color: {colors['bg_hover']};
        border: {BORDER_WIDTH_SM} solid {colors['border_hover']};
    }}
    QPushButton:disabled {{
        color: {COLOR_GRAY_400};
        border: {BORDER_WIDTH_SM} solid {COLOR_GRAY_300};
    }}
    """


# ==================== TASK 10: DIALOG STYLING ====================

def get_dialog_stylesheet():
    """
    Returns stylesheet for dialog windows and forms (Task 10).
    
    Applies consistent Navy + Orange styling to:
    - Dialog backgrounds
    - Form labels (Navy text, bold)
    - Input fields (QLineEdit, QTextEdit, QComboBox)
    - Dialog borders and spacing
    
    Usage:
        dialog = MyDialog()
        dialog.setStyleSheet(get_dialog_stylesheet())
    """
    
    stylesheet = f"""
    /* Dialog container */
    QDialog {{
        background-color: {COLOR_WHITE};
        border: {BORDER_WIDTH_SM} solid {COLOR_GRAY_200};
    }}
    
    /* Dialog field labels (form layout) */
    QLabel {{
        color: {COLOR_NAVY};
        font-weight: {FONT_WEIGHT_MEDIUM};
        font-size: {FONT_SIZE_BASE}px;
    }}
    
    /* Input fields in dialogs */
    QDialog QLineEdit, QDialog QTextEdit {{
        background-color: {COLOR_WHITE};
        border: {BORDER_WIDTH_SM} solid {COLOR_GRAY_300};
        border-radius: {BORDER_RADIUS_MD};
        padding: 8px 12px;
        font-size: {FONT_SIZE_BASE}px;
        color: {COLOR_GRAY_900};
    }}
    
    QDialog QLineEdit:focus, QDialog QTextEdit:focus {{
        border: 2px solid {COLOR_NAVY};
        outline: none;
    }}
    
    QDialog QLineEdit:hover, QDialog QTextEdit:hover {{
        border: {BORDER_WIDTH_SM} solid {COLOR_NAVY};
        background-color: {COLOR_GRAY_50};
    }}
    
    /* Combo boxes in dialogs */
    QDialog QComboBox {{
        background-color: {COLOR_WHITE};
        border: {BORDER_WIDTH_SM} solid {COLOR_GRAY_300};
        border-radius: {BORDER_RADIUS_MD};
        padding: 8px 12px;
        font-size: {FONT_SIZE_BASE}px;
        color: {COLOR_GRAY_900};
    }}
    
    QDialog QComboBox:focus {{
        border: 2px solid {COLOR_NAVY};
        outline: none;
    }}
    
    QDialog QComboBox:hover {{
        border: {BORDER_WIDTH_SM} solid {COLOR_NAVY};
        background-color: {COLOR_GRAY_50};
    }}
    
    QDialog QComboBox::drop-down {{
        border: none;
        background-color: transparent;
    }}
    
    QDialog QComboBox QAbstractItemView {{
        background-color: {COLOR_WHITE};
        selection-background-color: {COLOR_NAVY};
        color: {COLOR_GRAY_900};
        border: {BORDER_WIDTH_SM} solid {COLOR_GRAY_200};
    }}
    """
    
    return stylesheet
