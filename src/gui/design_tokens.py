"""
Design Tokens for BeasiswaKu Application
Defines color palette, typography, spacing, and other design constants
"""

# ============================================================================
# COLOR PALETTE
# ============================================================================

# Primary Colors
COLOR_NAVY = "#1e3a8a"  # Primary brand color - deep blue
COLOR_NAVY_DARK = "#0f2144"  # Darker shade of navy for hover/active states
COLOR_NAVY_LIGHT = "#3b5998"  # Lighter shade of navy

COLOR_ORANGE = "#f59e0b"  # Accent color - warm orange
COLOR_ORANGE_DARK = "#d97706"  # Darker shade for hover/active states
COLOR_ORANGE_LIGHT = "#fbbf24"  # Lighter shade of orange

# Neutral Colors
COLOR_WHITE = "#ffffff"
COLOR_GRAY_50 = "#f9fafb"  # Very light gray - backgrounds
COLOR_GRAY_100 = "#f3f4f6"  # Light gray
COLOR_GRAY_200 = "#e5e7eb"  # Light gray - borders
COLOR_GRAY_300 = "#d1d5db"
COLOR_GRAY_400 = "#9ca3af"
COLOR_GRAY_500 = "#6b7280"  # Medium gray
COLOR_GRAY_600 = "#4b5563"
COLOR_GRAY_700 = "#374151"
COLOR_GRAY_800 = "#1f2937"
COLOR_GRAY_900 = "#111827"  # Very dark gray - text

COLOR_BLACK = "#000000"

# Semantic Colors
COLOR_SUCCESS = "#10b981"  # Green - for success/completed states
COLOR_SUCCESS_LIGHT = "#d1fae5"  # Light green background
COLOR_SUCCESS_DARK = "#059669"  # Dark green

COLOR_WARNING = "#f59e0b"  # Orange/Yellow - for warnings (same as accent)
COLOR_WARNING_LIGHT = "#fef3c7"  # Light yellow background
COLOR_WARNING_DARK = "#d97706"

COLOR_ERROR = "#ef4444"  # Red - for errors/danger
COLOR_ERROR_LIGHT = "#fee2e2"  # Light red background
COLOR_ERROR_DARK = "#dc2626"

COLOR_INFO = "#3b82f6"  # Blue - for info messages
COLOR_INFO_LIGHT = "#dbeafe"  # Light blue background
COLOR_INFO_DARK = "#1d4ed8"

# Status Colors for Beasiswa
COLOR_STATUS_PENDING = "#60a5fa"  # Light blue
COLOR_STATUS_APPROVED = "#10b981"  # Green
COLOR_STATUS_REJECTED = "#ef4444"  # Red
COLOR_STATUS_DRAFT = "#9ca3af"  # Gray

# Deadline Colors
COLOR_DEADLINE_CRITICAL = "#ef4444"  # Red - ≤ 3 days
COLOR_DEADLINE_WARNING = "#f59e0b"  # Orange - ≤ 7 days
COLOR_DEADLINE_SAFE = "#10b981"  # Green - > 7 days

# ============================================================================
# TYPOGRAPHY
# ============================================================================

# Font Families
FONT_FAMILY_PRIMARY = "Segoe UI, -apple-system, BlinkMacSystemFont, sans-serif"
FONT_FAMILY_MONOSPACE = "Courier New, monospace"

# Font Sizes (in pixels)
FONT_SIZE_XS = 11
FONT_SIZE_SM = 12
FONT_SIZE_BASE = 13
FONT_SIZE_MD = 14
FONT_SIZE_LG = 16
FONT_SIZE_XL = 18
FONT_SIZE_2XL = 20
FONT_SIZE_3XL = 24
FONT_SIZE_4XL = 28

# Font Weights
FONT_WEIGHT_LIGHT = 300
FONT_WEIGHT_NORMAL = 400
FONT_WEIGHT_MEDIUM = 500
FONT_WEIGHT_SEMIBOLD = 600
FONT_WEIGHT_BOLD = 700

# Line Heights
LINE_HEIGHT_TIGHT = 1.2
LINE_HEIGHT_NORMAL = 1.5
LINE_HEIGHT_RELAXED = 1.75

# ============================================================================
# SPACING SCALE
# ============================================================================
# Based on 4px base unit

SPACING_1 = "4px"    # xs
SPACING_2 = "8px"    # small
SPACING_3 = "12px"   # sm
SPACING_4 = "16px"   # base
SPACING_5 = "20px"   # md
SPACING_6 = "24px"   # lg
SPACING_8 = "32px"   # xl
SPACING_10 = "40px"  # 2xl
SPACING_12 = "48px"  # 3xl
SPACING_16 = "64px"  # 4xl

# Common spacing combinations
PADDING_XS = SPACING_1
PADDING_SM = SPACING_2
PADDING_MD = SPACING_3
PADDING_LG = SPACING_4
PADDING_XL = SPACING_5

MARGIN_XS = SPACING_1
MARGIN_SM = SPACING_2
MARGIN_MD = SPACING_3
MARGIN_LG = SPACING_4
MARGIN_XL = SPACING_5

# ============================================================================
# BORDER RADIUS
# ============================================================================

BORDER_RADIUS_NONE = "0px"
BORDER_RADIUS_SM = "4px"
BORDER_RADIUS_MD = "6px"
BORDER_RADIUS_LG = "8px"
BORDER_RADIUS_FULL = "9999px"  # Pill-shaped (fully rounded)

# ============================================================================
# SHADOW & ELEVATION
# ============================================================================

SHADOW_NONE = "none"
SHADOW_SM = "0 1px 2px 0 rgba(0, 0, 0, 0.05)"
SHADOW_MD = "0 4px 6px -1px rgba(0, 0, 0, 0.1), 0 2px 4px -1px rgba(0, 0, 0, 0.06)"
SHADOW_LG = "0 10px 15px -3px rgba(0, 0, 0, 0.1), 0 4px 6px -2px rgba(0, 0, 0, 0.05)"
SHADOW_XL = "0 20px 25px -5px rgba(0, 0, 0, 0.1), 0 10px 10px -5px rgba(0, 0, 0, 0.04)"

# ============================================================================
# BORDER WIDTH
# ============================================================================

BORDER_WIDTH_NONE = "0px"
BORDER_WIDTH_SM = "1px"
BORDER_WIDTH_MD = "2px"
BORDER_WIDTH_LG = "3px"
BORDER_WIDTH_XL = "4px"

# ============================================================================
# ANIMATION & TRANSITIONS
# ============================================================================

TRANSITION_FAST = "150ms ease-in-out"
TRANSITION_NORMAL = "200ms ease-in-out"
TRANSITION_SLOW = "300ms ease-in-out"

# ============================================================================
# COMPONENT SIZES
# ============================================================================

# Button Sizes
BUTTON_HEIGHT_SM = "32px"
BUTTON_HEIGHT_MD = "40px"
BUTTON_HEIGHT_LG = "48px"

BUTTON_PADDING_H_SM = "12px"
BUTTON_PADDING_H_MD = "16px"
BUTTON_PADDING_H_LG = "24px"

# Icon Sizes
ICON_SIZE_XS = "16px"
ICON_SIZE_SM = "18px"
ICON_SIZE_MD = "24px"
ICON_SIZE_LG = "32px"
ICON_SIZE_XL = "48px"

# ============================================================================
# Z-INDEX SCALE
# ============================================================================

Z_INDEX_DROPDOWN = 10
Z_INDEX_STICKY = 20
Z_INDEX_FIXED = 30
Z_INDEX_MODAL_BACKDROP = 40
Z_INDEX_MODAL = 50
Z_INDEX_POPOVER = 60
Z_INDEX_TOOLTIP = 70
