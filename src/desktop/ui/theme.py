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
- Dynamic font scaling for Wayland/HiDPI displays
======================================================================
"""

import os
import logging
from typing import Dict, Any
from dataclasses import dataclass

# Try to import customtkinter for theme management
try:
    import customtkinter as ctk
    CUSTOMTKINTER_AVAILABLE = True
except ImportError:
    CUSTOMTKINTER_AVAILABLE = False
    ctk = None

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
    
    # Base font sizes (before scaling)
    _BASE_FONT_SIZE_H1 = 24          # Main titles
    _BASE_FONT_SIZE_H2 = 20          # Section headers
    _BASE_FONT_SIZE_H3 = 16          # Subsection headers
    _BASE_FONT_SIZE_BODY = 12        # Body text
    _BASE_FONT_SIZE_CAPTION = 10     # Small text/captions
    _BASE_FONT_SIZE_BUTTON = 11      # Button text
    
    # Current font scale factor (set by configure_ui)
    _font_scale_factor = 1.0
    
    # Font weights
    FONT_WEIGHT_LIGHT = "normal"
    FONT_WEIGHT_REGULAR = "normal"
    FONT_WEIGHT_BOLD = "bold"
    
    @classmethod
    def set_font_scale(cls, scale_factor: float) -> None:
        """Set the global font scale factor and update all font sizes."""
        cls._font_scale_factor = scale_factor
        
        # Update the actual font size attributes
        cls.FONT_SIZE_H1 = int(cls._BASE_FONT_SIZE_H1 * scale_factor)
        cls.FONT_SIZE_H2 = int(cls._BASE_FONT_SIZE_H2 * scale_factor)
        cls.FONT_SIZE_H3 = int(cls._BASE_FONT_SIZE_H3 * scale_factor)
        cls.FONT_SIZE_BODY = int(cls._BASE_FONT_SIZE_BODY * scale_factor)
        cls.FONT_SIZE_CAPTION = int(cls._BASE_FONT_SIZE_CAPTION * scale_factor)
        cls.FONT_SIZE_BUTTON = int(cls._BASE_FONT_SIZE_BUTTON * scale_factor)
        
        import logging
        logger = logging.getLogger(__name__)
        logger.info(f"Font scale factor set to: {scale_factor}")
        logger.info(f"Scaled font sizes - H1: {cls.FONT_SIZE_H1}, H2: {cls.FONT_SIZE_H2}, Body: {cls.FONT_SIZE_BODY}, Button: {cls.FONT_SIZE_BUTTON}")
    
    @classmethod
    def get_font_scale(cls) -> float:
        """Get the current font scale factor."""
        return cls._font_scale_factor
    
    # Default font sizes (will be updated by set_font_scale)
    FONT_SIZE_H1 = _BASE_FONT_SIZE_H1          # Main titles
    FONT_SIZE_H2 = _BASE_FONT_SIZE_H2          # Section headers
    FONT_SIZE_H3 = _BASE_FONT_SIZE_H3          # Subsection headers
    FONT_SIZE_BODY = _BASE_FONT_SIZE_BODY      # Body text
    FONT_SIZE_CAPTION = _BASE_FONT_SIZE_CAPTION # Small text/captions
    FONT_SIZE_BUTTON = _BASE_FONT_SIZE_BUTTON   # Button text

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

class ThemeManager:
    """Centralized theme manager for TalkBridge Desktop UI."""
    
    _current_theme = "dark"  # Default to dark theme
    _current_color_theme = "blue"  # Default color theme
    _theme_initialized = False
    
    @classmethod
    def initialize(cls) -> None:
        """Initialize the theme system. Call this once at application startup."""
        if cls._theme_initialized:
            return
            
        import logging
        logger = logging.getLogger(__name__)
        
        try:
            # Apply font scaling based on environment
            apply_font_scaling()
            
            # Set default CustomTkinter theme if available
            if CUSTOMTKINTER_AVAILABLE:
                cls._apply_customtkinter_theme()
                logger.info("Theme system initialized with CustomTkinter integration")
            else:
                logger.warning("CustomTkinter not available, theme system initialized without UI integration")
            
            cls._theme_initialized = True
            
        except Exception as e:
            logger.error(f"Failed to initialize theme system: {e}")
            cls._theme_initialized = False
    
    @classmethod
    def set_theme(cls, theme: str) -> None:
        """Apply light/dark theme globally.
        
        Args:
            theme: Theme name - "light", "dark", or "system"
        """
        if theme not in ("light", "dark", "system"):
            raise ValueError(f"Unsupported theme: {theme}. Supported themes: light, dark, system")
        
        import logging
        logger = logging.getLogger(__name__)
        
        try:
            cls._current_theme = theme
            
            if CUSTOMTKINTER_AVAILABLE and ctk is not None:
                ctk.set_appearance_mode(theme)
                logger.info(f"Applied theme: {theme}")
            else:
                logger.warning(f"CustomTkinter not available, theme '{theme}' set but not applied to UI")
                
        except Exception as e:
            logger.error(f"Failed to apply theme '{theme}': {e}")
    
    @classmethod
    def get_theme(cls) -> str:
        """Get the current theme.
        
        Returns:
            Current theme name
        """
        return cls._current_theme
    
    @classmethod
    def set_color_theme(cls, color: str) -> None:
        """Apply a global accent color theme.
        
        Args:
            color: Color theme name - "blue", "green", "dark-blue", etc.
                  See CustomTkinter documentation for available themes.
        """
        import logging
        logger = logging.getLogger(__name__)
        
        try:
            cls._current_color_theme = color
            
            if CUSTOMTKINTER_AVAILABLE and ctk is not None:
                ctk.set_default_color_theme(color)
                logger.info(f"Applied color theme: {color}")
            else:
                logger.warning(f"CustomTkinter not available, color theme '{color}' set but not applied to UI")
                
        except Exception as e:
            logger.error(f"Failed to apply color theme '{color}': {e}")
    
    @classmethod
    def apply_accent_color(cls, color: str) -> None:
        """Apply a global accent color. Alias for set_color_theme for backward compatibility.
        
        Args:
            color: Color theme name
        """
        cls.set_color_theme(color)
    
    @classmethod
    def get_color_theme(cls) -> str:
        """Get the current color theme.
        
        Returns:
            Current color theme name
        """
        return cls._current_color_theme
    
    @classmethod
    def _apply_customtkinter_theme(cls) -> None:
        """Apply the current theme configuration to CustomTkinter."""
        if not CUSTOMTKINTER_AVAILABLE or ctk is None:
            return
            
        # Apply current appearance mode
        ctk.set_appearance_mode(cls._current_theme)
        
        # Apply current color theme  
        ctk.set_default_color_theme(cls._current_color_theme)
    
    @classmethod
    def get_theme_config(cls) -> Dict[str, Any]:
        """Get comprehensive theme configuration for manual application.
        
        Returns:
            Dictionary with all theme settings
        """
        return {
            "appearance_mode": cls._current_theme,
            "color_theme": cls._current_color_theme,
            "customtkinter_theme": get_customtkinter_theme(),
            "color_palette": ColorPalette,
            "typography": Typography,
            "spacing": Spacing,
            "dimensions": Dimensions,
            "font_scaling": get_font_scaling_info(),
            "customtkinter_available": CUSTOMTKINTER_AVAILABLE,
            "theme_initialized": cls._theme_initialized
        }
    
    @classmethod
    def apply_widget_theme(cls, widget, theme_type: str = "default", variant: str = "default") -> None:
        """Apply theme to a specific widget.
        
        Args:
            widget: Widget to apply theme to
            theme_type: Type of theme (button, input, frame, label, etc.)
            variant: Theme variant (primary, secondary, danger, etc.)
        """
        try:
            if theme_type == "button":
                theme_config = ComponentThemes.get_button_theme(variant)
            elif theme_type == "input":
                theme_config = ComponentThemes.get_input_theme()
            elif theme_type == "frame":
                theme_config = ComponentThemes.get_frame_theme(variant)
            elif theme_type == "label":
                theme_config = ComponentThemes.get_label_theme(variant)
            elif theme_type == "combobox":
                theme_config = ComponentThemes.get_combobox_theme()
            elif theme_type == "checkbox":
                theme_config = ComponentThemes.get_checkbox_theme()
            elif theme_type == "switch":
                theme_config = ComponentThemes.get_switch_theme()
            elif theme_type == "progressbar":
                theme_config = ComponentThemes.get_progressbar_theme()
            else:
                # Fallback to default configuration
                theme_config = {}
            
            apply_theme_to_widget(widget, theme_config)
            
        except Exception as e:
            import logging
            logger = logging.getLogger(__name__)
            logger.warning(f"Failed to apply {theme_type} theme to widget: {e}")
    
    @classmethod
    def reset_theme(cls) -> None:
        """Reset theme to default settings."""
        cls._current_theme = "dark"
        cls._current_color_theme = "blue"
        cls._theme_initialized = False
        
        # Reset font scaling
        reset_font_scaling()
        
        # Re-initialize with defaults
        cls.initialize()

def apply_theme_to_widget(widget, theme_config: Dict[str, Any]) -> None:
    """Apply theme configuration to a widget."""
    try:
        for key, value in theme_config.items():
            if hasattr(widget, 'configure'):
                widget.configure(**{key: value})
    except Exception as e:
        import logging
        logger = logging.getLogger("src.theme")
        logger.warning(f"Could not apply theme configuration: {e}")

def detect_wayland_environment() -> bool:
    """
    Detect if running on Linux with Wayland session.
    
    Returns:
        True if running on Wayland, False otherwise
    """
    import platform
    
    # Must be Linux
    if platform.system() != 'Linux':
        return False
    
    # Check various Wayland indicators
    wayland_indicators = [
        os.environ.get('XDG_SESSION_TYPE') == 'wayland',
        'WAYLAND_DISPLAY' in os.environ and os.environ.get('WAYLAND_DISPLAY'),
        os.environ.get('GDK_BACKEND') == 'wayland',
        os.environ.get('QT_QPA_PLATFORM') == 'wayland'
    ]
    
    return any(wayland_indicators)

def calculate_font_scale_factor() -> float:
    """
    Calculate appropriate font scale factor for the current environment.
    
    Returns:
        Font scale factor (1.0 for standard, 1.4+ for Wayland)
    """
    import logging
    logger = logging.getLogger(__name__)
    
    # Check for manual override first
    override = os.environ.get('FORCE_DESKTOP_FONT_SCALE')
    if override:
        try:
            manual_scale = float(override)
            logger.info(f"Using manual font scale override: {manual_scale}")
            return manual_scale
        except ValueError:
            logger.warning(f"Invalid FORCE_DESKTOP_FONT_SCALE value: {override}")
    
    # Check if Wayland environment
    if detect_wayland_environment():
        # Use stronger font scaling for Wayland/HiDPI
        font_scale = 1.4
        logger.info(f"Wayland environment detected, using font scale: {font_scale}")
        return font_scale
    else:
        # Standard scaling for other environments
        font_scale = 1.0
        logger.info(f"Non-Wayland environment, using standard font scale: {font_scale}")
        return font_scale

def apply_font_scaling() -> None:
    """
    Apply font scaling based on the current environment.
    This should be called early in the UI initialization process.
    """
    import logging
    logger = logging.getLogger(__name__)
    
    try:
        # Calculate and apply font scale factor
        scale_factor = calculate_font_scale_factor()
        Typography.set_font_scale(scale_factor)
        
        # Set environment variable to track scaling applied
        os.environ['TALKBRIDGE_FONT_SCALE'] = str(scale_factor)
        
        logger.info(f"Font scaling applied successfully with factor: {scale_factor}")
        
    except Exception as e:
        logger.error(f"Failed to apply font scaling: {e}")
        # Fallback to default scaling
        Typography.set_font_scale(1.0)
        os.environ['TALKBRIDGE_FONT_SCALE'] = "1.0"

def get_font_scaling_info() -> Dict[str, Any]:
    """
    Get information about current font scaling configuration.
    
    Returns:
        Dictionary with font scaling details
    """
    return {
        'wayland_detected': detect_wayland_environment(),
        'font_scale_factor': Typography.get_font_scale(),
        'environment_override': os.environ.get('FORCE_DESKTOP_FONT_SCALE'),
        'applied_scale': os.environ.get('TALKBRIDGE_FONT_SCALE'),
        'scaled_sizes': {
            'h1': Typography.FONT_SIZE_H1,
            'h2': Typography.FONT_SIZE_H2,
            'h3': Typography.FONT_SIZE_H3,
            'body': Typography.FONT_SIZE_BODY,
            'button': Typography.FONT_SIZE_BUTTON,
            'caption': Typography.FONT_SIZE_CAPTION,
        }
    }

def set_manual_font_scale(scale_factor: float) -> None:
    """
    Manually set font scale factor for testing purposes.
    
    Args:
        scale_factor: Font scale factor (e.g., 1.0, 1.4, 2.0)
    """
    import logging
    logger = logging.getLogger(__name__)
    
    Typography.set_font_scale(scale_factor)
    os.environ['TALKBRIDGE_FONT_SCALE'] = str(scale_factor)
    os.environ['FORCE_DESKTOP_FONT_SCALE'] = str(scale_factor)
    
    logger.info(f"Manual font scale override applied: {scale_factor}")

def reset_font_scaling() -> None:
    """Reset font scaling to default (1.0)."""
    Typography.set_font_scale(1.0)
    if 'TALKBRIDGE_FONT_SCALE' in os.environ:
        del os.environ['TALKBRIDGE_FONT_SCALE']
    if 'FORCE_DESKTOP_FONT_SCALE' in os.environ:
        del os.environ['FORCE_DESKTOP_FONT_SCALE']

# Export main functions for external use
__all__ = [
    'ColorPalette',
    'Typography', 
    'Spacing',
    'Dimensions',
    'ComponentThemes',
    'UXGuidelines',
    'ThemeManager',
    'get_customtkinter_theme',
    'apply_theme_to_widget',
    'detect_wayland_environment',
    'calculate_font_scale_factor',
    'apply_font_scaling',
    'get_font_scaling_info',
    'set_manual_font_scale',
    'reset_font_scaling'
]

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
