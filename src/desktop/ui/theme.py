#!/usr/bin/env python3
"""
TalkBridge Desktop - Unified Theme System
=========================================

Centralized theme configuration for consistent styling across all desktop components.

Author: TalkBridge Team
Date: 2025-09-08
Version: 2.1

Features:
- Unified color palette
- Component-specific styling
- UX best practices compliance
- Accessibility support
======================================================================
"""

from typing import Dict, Any
from dataclasses import dataclass


@dataclass
class ColorPalette:
    """Unified color palette for the application."""
    
    # Primary background colors
    BACKGROUND_PRIMARY = "#1a1a1a"      # Main background
    BACKGROUND_SECONDARY = "#2d2d2d"    # Secondary surfaces
    BACKGROUND_ELEVATED = "#3a3a3a"     # Elevated surfaces (cards, dialogs)
    BACKGROUND_SURFACE = "#404040"      # Interactive surfaces
    
    # Text colors (WCAG AA compliant)
    TEXT_PRIMARY = "#ffffff"            # Primary text (contrast ratio: 21:1)
    TEXT_SECONDARY = "#cccccc"          # Secondary text (contrast ratio: 15.8:1)
    TEXT_TERTIARY = "#999999"           # Tertiary text (contrast ratio: 10.7:1)
    TEXT_DISABLED = "#666666"           # Disabled text
    TEXT_HINT = "#808080"               # Placeholder/hint text
    
    # Brand and accent colors
    ACCENT_PRIMARY = "#0078d4"          # Primary brand color
    ACCENT_PRIMARY_HOVER = "#106ebe"    # Primary hover state
    ACCENT_PRIMARY_PRESSED = "#005a9e"  # Primary pressed state
    ACCENT_PRIMARY_DISABLED = "#003d6b" # Primary disabled state
    
    # Semantic colors
    SUCCESS = "#16c60c"                 # Success states
    SUCCESS_HOVER = "#13a10e"           # Success hover
    WARNING = "#ff8c00"                 # Warning states
    WARNING_HOVER = "#e67e00"           # Warning hover
    ERROR = "#d13438"                   # Error states
    ERROR_HOVER = "#b02a2f"             # Error hover
    INFO = "#0078d4"                    # Info states (same as primary)
    
    # Interactive element colors
    BORDER_DEFAULT = "#555555"          # Default borders
    BORDER_FOCUS = "#0078d4"            # Focused elements
    BORDER_ERROR = "#d13438"            # Error states
    BORDER_SUCCESS = "#16c60c"          # Success states
    
    # Input field colors
    INPUT_BACKGROUND = "#3a3a3a"        # Input background
    INPUT_BACKGROUND_FOCUS = "#404040"  # Focused input background
    INPUT_BACKGROUND_DISABLED = "#2d2d2d" # Disabled input background
    
    # Overlay colors
    OVERLAY_LIGHT = "rgba(255, 255, 255, 0.1)"  # Light overlay
    OVERLAY_DARK = "rgba(0, 0, 0, 0.3)"         # Dark overlay
    SHADOW = "rgba(0, 0, 0, 0.5)"               # Drop shadow


@dataclass
class Typography:
    """Typography configuration for consistent text styling."""
    
    # Font families
    FONT_FAMILY_PRIMARY = "Segoe UI"
    FONT_FAMILY_MONOSPACE = "Consolas"
    
    # Font sizes (scalable)
    FONT_SIZE_H1 = 24          # Main titles
    FONT_SIZE_H2 = 20          # Section headers
    FONT_SIZE_H3 = 16          # Subsection headers
    FONT_SIZE_BODY = 12        # Body text
    FONT_SIZE_CAPTION = 10     # Small text/captions
    FONT_SIZE_BUTTON = 11      # Button text
    
    # Font weights
    FONT_WEIGHT_LIGHT = "normal"
    FONT_WEIGHT_REGULAR = "normal"
    FONT_WEIGHT_BOLD = "bold"


@dataclass
class Spacing:
    """Spacing configuration for consistent layout."""
    
    # Base spacing unit (all spacing should be multiples of this)
    BASE_UNIT = 4
    
    # Common spacing values
    XS = 4      # Extra small spacing
    SM = 8      # Small spacing
    MD = 12     # Medium spacing
    LG = 16     # Large spacing
    XL = 20     # Extra large spacing
    XXL = 24    # Double extra large spacing
    
    # Component-specific spacing
    MARGIN_MAIN = 20           # Main container margins
    MARGIN_SECTION = 16        # Section margins
    MARGIN_ITEM = 12           # Item margins
    
    PADDING_BUTTON = 8         # Button padding
    PADDING_INPUT = 10         # Input field padding
    PADDING_CARD = 16          # Card padding


@dataclass
class Dimensions:
    """Dimension configuration for consistent sizing."""
    
    # Minimum interactive target size (accessibility)
    MIN_TOUCH_TARGET = 44      # Minimum touch target size
    
    # Component heights
    HEIGHT_BUTTON = 40         # Standard button height
    HEIGHT_INPUT = 36          # Input field height
    HEIGHT_SLIDER = 24         # Slider height
    HEIGHT_TAB = 40            # Tab height
    HEIGHT_TOOLBAR = 48        # Toolbar height
    HEIGHT_STATUS_BAR = 32     # Status bar height
    
    # Border radius
    RADIUS_SM = 4              # Small radius
    RADIUS_MD = 6              # Medium radius
    RADIUS_LG = 8              # Large radius
    RADIUS_XL = 12             # Extra large radius
    
    # Border widths
    BORDER_THIN = 1            # Thin border
    BORDER_THICK = 2           # Thick border


class ComponentThemes:
    """Component-specific theme configurations."""
    
    @staticmethod
    def get_button_theme(variant: str = "primary") -> Dict[str, Any]:
        """Get button theme configuration."""
        base_theme = {
            "height": Dimensions.HEIGHT_BUTTON,
            "corner_radius": Dimensions.RADIUS_MD,
            "border_width": 0,
            "font": (Typography.FONT_FAMILY_PRIMARY, Typography.FONT_SIZE_BUTTON, Typography.FONT_WEIGHT_REGULAR),
        }
        
        if variant == "primary":
            return {
                **base_theme,
                "fg_color": ColorPalette.ACCENT_PRIMARY,
                "hover_color": ColorPalette.ACCENT_PRIMARY_HOVER,
                "text_color": ColorPalette.TEXT_PRIMARY,
            }
        elif variant == "secondary":
            return {
                **base_theme,
                "fg_color": "transparent",
                "hover_color": ColorPalette.BACKGROUND_SURFACE,
                "text_color": ColorPalette.TEXT_SECONDARY,
                "border_width": Dimensions.BORDER_THIN,
                "border_color": ColorPalette.BORDER_DEFAULT,
            }
        elif variant == "danger":
            return {
                **base_theme,
                "fg_color": ColorPalette.ERROR,
                "hover_color": ColorPalette.ERROR_HOVER,
                "text_color": ColorPalette.TEXT_PRIMARY,
            }
        elif variant == "success":
            return {
                **base_theme,
                "fg_color": ColorPalette.SUCCESS,
                "hover_color": ColorPalette.SUCCESS_HOVER,
                "text_color": ColorPalette.TEXT_PRIMARY,
            }
        else:
            return base_theme
    
    @staticmethod
    def get_input_theme() -> Dict[str, Any]:
        """Get input field theme configuration."""
        return {
            "height": Dimensions.HEIGHT_INPUT,
            "corner_radius": Dimensions.RADIUS_MD,
            "border_width": Dimensions.BORDER_THIN,
            "fg_color": ColorPalette.INPUT_BACKGROUND,
            "border_color": ColorPalette.BORDER_DEFAULT,
            "text_color": ColorPalette.TEXT_PRIMARY,
            "placeholder_text_color": ColorPalette.TEXT_HINT,
            "font": (Typography.FONT_FAMILY_PRIMARY, Typography.FONT_SIZE_BODY),
        }
    
    @staticmethod
    def get_frame_theme(variant: str = "default") -> Dict[str, Any]:
        """Get frame theme configuration."""
        base_theme = {
            "corner_radius": Dimensions.RADIUS_MD,
            "border_width": 0,
        }
        
        if variant == "card":
            return {
                **base_theme,
                "fg_color": ColorPalette.BACKGROUND_ELEVATED,
                "corner_radius": Dimensions.RADIUS_LG,
            }
        elif variant == "section":
            return {
                **base_theme,
                "fg_color": ColorPalette.BACKGROUND_SECONDARY,
            }
        else:
            return {
                **base_theme,
                "fg_color": ColorPalette.BACKGROUND_PRIMARY,
            }
    
    @staticmethod
    def get_label_theme(variant: str = "default") -> Dict[str, Any]:
        """Get label theme configuration."""
        base_theme = {
            "font": (Typography.FONT_FAMILY_PRIMARY, Typography.FONT_SIZE_BODY),
        }
        
        if variant == "title":
            return {
                **base_theme,
                "text_color": ColorPalette.TEXT_PRIMARY,
                "font": (Typography.FONT_FAMILY_PRIMARY, Typography.FONT_SIZE_H2, Typography.FONT_WEIGHT_BOLD),
            }
        elif variant == "subtitle":
            return {
                **base_theme,
                "text_color": ColorPalette.TEXT_SECONDARY,
                "font": (Typography.FONT_FAMILY_PRIMARY, Typography.FONT_SIZE_H3),
            }
        elif variant == "caption":
            return {
                **base_theme,
                "text_color": ColorPalette.TEXT_TERTIARY,
                "font": (Typography.FONT_FAMILY_PRIMARY, Typography.FONT_SIZE_CAPTION),
            }
        elif variant == "error":
            return {
                **base_theme,
                "text_color": ColorPalette.ERROR,
            }
        elif variant == "success":
            return {
                **base_theme,
                "text_color": ColorPalette.SUCCESS,
            }
        elif variant == "warning":
            return {
                **base_theme,
                "text_color": ColorPalette.WARNING,
            }
        else:
            return {
                **base_theme,
                "text_color": ColorPalette.TEXT_PRIMARY,
            }
    
    @staticmethod
    def get_combobox_theme() -> Dict[str, Any]:
        """Get combobox theme configuration."""
        return {
            "height": Dimensions.HEIGHT_INPUT,
            "corner_radius": Dimensions.RADIUS_MD,
            "border_width": Dimensions.BORDER_THIN,
            "fg_color": ColorPalette.INPUT_BACKGROUND,
            "border_color": ColorPalette.BORDER_DEFAULT,
            "text_color": ColorPalette.TEXT_PRIMARY,
            "font": (Typography.FONT_FAMILY_PRIMARY, Typography.FONT_SIZE_BODY),
            "state": "readonly"
        }
    
    @staticmethod
    def get_checkbox_theme() -> Dict[str, Any]:
        """Get checkbox theme configuration."""
        return {
            "fg_color": ColorPalette.ACCENT_PRIMARY,
            "hover_color": ColorPalette.ACCENT_PRIMARY_HOVER,
            "text_color": ColorPalette.TEXT_PRIMARY,
            "font": (Typography.FONT_FAMILY_PRIMARY, Typography.FONT_SIZE_BODY),
        }
    
    @staticmethod
    def get_switch_theme() -> Dict[str, Any]:
        """Get switch theme configuration."""
        return {
            "fg_color": ColorPalette.ACCENT_PRIMARY,
            "progress_color": ColorPalette.ACCENT_PRIMARY_HOVER,
            "text_color": ColorPalette.TEXT_PRIMARY,
            "font": (Typography.FONT_FAMILY_PRIMARY, Typography.FONT_SIZE_BODY),
        }
    
    @staticmethod
    def get_progressbar_theme() -> Dict[str, Any]:
        """Get progress bar theme configuration."""
        return {
            "progress_color": ColorPalette.ACCENT_PRIMARY,
            "fg_color": ColorPalette.BACKGROUND_SURFACE,
            "height": 8,
        }


class WindowTheme:
    """Window-specific theme configuration."""
    
    # Main window
    MAIN_WINDOW = {
        "fg_color": ColorPalette.BACKGROUND_PRIMARY,
        "title_color": ColorPalette.TEXT_PRIMARY,
    }
    
    # Dialog windows
    DIALOG_WINDOW = {
        "fg_color": ColorPalette.BACKGROUND_PRIMARY,
        "title_color": ColorPalette.TEXT_PRIMARY,
    }
    
    # Modal overlays
    MODAL_OVERLAY = {
        "fg_color": ColorPalette.OVERLAY_DARK,
    }


class UIText:
    """Clean, user-friendly text content without special characters."""
    
    # Application branding
    APP_NAME = "TalkBridge Desktop"
    APP_SUBTITLE = "AI-Powered Communication Platform"
    
    # Authentication
    LOGIN_TITLE = "Sign In"
    LOGIN_SUBTITLE = "Access your TalkBridge account"
    USERNAME_LABEL = "Username"
    PASSWORD_LABEL = "Password"
    REMEMBER_ME = "Remember me"
    SHOW_PASSWORD = "Show"
    SIGN_IN_BUTTON = "Sign In"
    CANCEL_BUTTON = "Cancel"
    
    # Authentication states
    SIGNING_IN = "Signing in..."
    AUTH_SUCCESS = "Success!"
    AUTH_FAILED = "Authentication failed"
    AUTH_TIMEOUT = "Request timed out"
    
    # Main window
    MAIN_TITLE = "TalkBridge Desktop - AI Communication Platform"
    
    # Tabs
    CHAT_TAB = "AI Chat"
    AVATAR_TAB = "Avatar"
    SETTINGS_TAB = "Settings"
    
    # Status messages
    READY = "Ready"
    CONNECTING = "Connecting..."
    CONNECTED = "Connected"
    DISCONNECTED = "Disconnected"
    ERROR_OCCURRED = "An error occurred"
    
    # Form validation
    FIELD_REQUIRED = "This field is required"
    INVALID_INPUT = "Invalid input"
    
    # Accessibility
    CLOSE_DIALOG = "Close dialog"
    TOGGLE_VISIBILITY = "Toggle password visibility"
    MINIMIZE_WINDOW = "Minimize window"
    MAXIMIZE_WINDOW = "Maximize window"
    CLOSE_WINDOW = "Close window"


class Icons:
    """Unicode icons that are widely supported and accessible."""
    
    # Basic shapes and symbols
    USER = "●"          # User indicator
    ROBOT = "◐"         # Bot/AI indicator
    LOCK = "●"          # Security indicator
    KEY = "♦"           # Key/password indicator
    EYE = "○"           # Visibility toggle
    CHECK = "✓"         # Success indicator
    CROSS = "✗"         # Error/cancel indicator
    ARROW = "→"         # Direction indicator
    REFRESH = "↻"       # Refresh/reload indicator
    SETTINGS = "⚙"      # Settings indicator
    
    # Status indicators
    ONLINE = "●"        # Online status (green)
    OFFLINE = "○"       # Offline status
    LOADING = "◐"       # Loading state
    WARNING = "⚠"       # Warning state
    ERROR = "!"         # Error state
    INFO = "i"          # Information


class UXGuidelines:
    """UX best practices and guidelines."""
    
    # Interaction feedback
    HOVER_TRANSITION_MS = 150      # Hover state transition time
    CLICK_FEEDBACK_MS = 100        # Click feedback duration
    LOADING_MIN_DURATION_MS = 500  # Minimum loading state duration
    
    # Animation timing
    FAST_ANIMATION_MS = 150        # Fast animations (hover, focus)
    NORMAL_ANIMATION_MS = 300      # Normal animations (transitions)
    SLOW_ANIMATION_MS = 500        # Slow animations (page changes)
    
    # Form validation
    VALIDATION_DELAY_MS = 300      # Delay before showing validation
    ERROR_DISPLAY_MS = 5000        # How long to show error messages
    SUCCESS_DISPLAY_MS = 3000      # How long to show success messages
    
    # Accessibility
    MIN_CONTRAST_RATIO = 4.5       # WCAG AA minimum contrast ratio
    MIN_TOUCH_TARGET_PX = 44       # Minimum touch target size
    
    # Focus management
    FOCUS_RING_WIDTH = 2           # Focus indicator width
    FOCUS_RING_OFFSET = 2          # Focus indicator offset


def apply_theme_to_widget(widget, theme_config: Dict[str, Any]) -> None:
    """Apply theme configuration to a widget."""
    try:
        for key, value in theme_config.items():
            if hasattr(widget, 'configure'):
                widget.configure(**{key: value})
    except Exception as e:
        import logging
        logger = logging.getLogger("talkbridge.theme")
        logger.warning(f"Could not apply theme configuration: {e}")


def get_customtkinter_theme() -> Dict[str, Any]:
    """Get CustomTkinter global theme configuration."""
    return {
        "CTk": {
            "fg_color": ColorPalette.BACKGROUND_PRIMARY,
        },
        "CTkToplevel": {
            "fg_color": ColorPalette.BACKGROUND_PRIMARY,
        },
        "CTkFrame": {
            "fg_color": ColorPalette.BACKGROUND_SECONDARY,
            "corner_radius": Dimensions.RADIUS_MD,
        },
        "CTkButton": ComponentThemes.get_button_theme("primary"),
        "CTkEntry": ComponentThemes.get_input_theme(),
        "CTkLabel": ComponentThemes.get_label_theme(),
        "CTkCheckBox": {
            "fg_color": ColorPalette.ACCENT_PRIMARY,
            "hover_color": ColorPalette.ACCENT_PRIMARY_HOVER,
            "text_color": ColorPalette.TEXT_PRIMARY,
        },
        "CTkProgressBar": {
            "progress_color": ColorPalette.ACCENT_PRIMARY,
            "fg_color": ColorPalette.BACKGROUND_SURFACE,
        },
        "CTkSlider": {
            "progress_color": ColorPalette.ACCENT_PRIMARY,
            "button_color": ColorPalette.ACCENT_PRIMARY,
            "button_hover_color": ColorPalette.ACCENT_PRIMARY_HOVER,
        },
        "CTkTabview": {
            "fg_color": ColorPalette.BACKGROUND_SECONDARY,
            "segmented_button_fg_color": ColorPalette.BACKGROUND_SURFACE,
            "segmented_button_selected_color": ColorPalette.ACCENT_PRIMARY,
            "segmented_button_selected_hover_color": ColorPalette.ACCENT_PRIMARY_HOVER,
            "text_color": ColorPalette.TEXT_PRIMARY,
        },
    }
