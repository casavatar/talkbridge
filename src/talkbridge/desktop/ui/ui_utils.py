#!/usr/bin/env python3
"""
TalkBridge Desktop - UI Utilities
=================================

Utility functions for UI components including icon loading, text cleaning,
and platform-specific fixes for optimal CustomTkinter performance.

Features:
- Cross-platform UI configuration
- Wayland display server detection and fixes
- Enhanced scaling fixes for Wayland (addresses LoginDialog sizing issues)
- Tk and CustomTkinter scaling coordination
- Icon loading with fallbacks
- Text cleaning for safe UI display
- Environment-specific optimizations

Wayland Scaling Fixes:
- Detects Linux + Wayland environment automatically
- Applies empirically tested scaling factor (1.35) via tk.call("tk", "scaling", factor)
- Coordinates CustomTkinter widget and window scaling
- Addresses specific issues like LoginDialog appearing too small
- Provides verification and diagnostic tools

Author: TalkBridge Team
Date: 2025-09-17
Version: 1.2
"""

import customtkinter as ctk
import os
import platform
import subprocess
import tkinter as tk
from pathlib import Path
from typing import Optional, Tuple
from ...logging_config import get_logger

logger = get_logger(__name__)

try:
    from PIL import Image
    PIL_AVAILABLE = True
except ImportError:
    PIL_AVAILABLE = False

def detect_operating_system() -> str:
    """
    Detect the current operating system.
    
    Returns:
        String identifying the OS: 'Linux', 'Windows', 'Darwin' (macOS), or 'Unknown'
    """
    return platform.system()

def is_wayland_session() -> bool:
    """
    Detect if the current Linux session is running on Wayland.
    
    Returns:
        True if running on Wayland, False otherwise (including non-Linux systems)
    """
    # Improved OS detection - must be Linux
    if platform.system() != 'Linux':
        return False
    
    # Primary check: XDG_SESSION_TYPE (most reliable for modern systems)
    if os.environ.get('XDG_SESSION_TYPE') == 'wayland':
        return True
    
    # Secondary check: WAYLAND_DISPLAY environment variable
    if 'WAYLAND_DISPLAY' in os.environ and os.environ.get('WAYLAND_DISPLAY'):
        return True
    
    # Additional checks for various desktop environments
    if os.environ.get('GDK_BACKEND') == 'wayland':
        return True
    
    if os.environ.get('QT_QPA_PLATFORM') == 'wayland':
        return True
    
    # Try to detect via loginctl (systemd systems)
    try:
        result = subprocess.run(['loginctl', 'show-session', 'self', '-p', 'Type'], 
                              capture_output=True, text=True, timeout=2)
        if result.returncode == 0 and 'Type=wayland' in result.stdout:
            return True
    except (subprocess.TimeoutExpired, subprocess.SubprocessError, FileNotFoundError):
        pass
    
    return False

def detect_screen_dpi() -> float:
    """
    Detect screen DPI to determine appropriate scaling factor.
    
    Returns:
        Screen DPI as float, or 96.0 as fallback
    """
    try:
        # Create a temporary root to get DPI info
        import tkinter as tk
        temp_root = tk.Tk()
        temp_root.withdraw()  # Hide the window
        
        # Get DPI using Tk's method
        screen_dpi = temp_root.winfo_fpixels('1i')
        temp_root.destroy()
        
        return screen_dpi
    except Exception:
        # Fallback to standard DPI
        return 96.0

def calculate_adaptive_scaling() -> float:
    """
    Calculate adaptive scaling factor based on DPI and environment.
    
    Returns:
        Appropriate scaling factor for current environment
    """
    # Get screen DPI
    screen_dpi = detect_screen_dpi()
    logger.info(f"Detected screen DPI: {screen_dpi}")
    
    # Calculate scaling factor based on DPI thresholds
    if screen_dpi > 200:
        # Very high DPI (4K+ displays)
        scaling_factor = 2.6
        dpi_category = "Very High DPI"
    elif screen_dpi > 150:
        # High DPI displays 
        scaling_factor = 2.3
        dpi_category = "High DPI"
    elif screen_dpi > 130:
        # Medium-high DPI
        scaling_factor = 2.0
        dpi_category = "Medium-High DPI"
    else:
        # Standard DPI or lower
        scaling_factor = 1.8  # Stronger scaling for Wayland
        dpi_category = "Standard DPI"
    
    logger.info(f"DPI Category: {dpi_category}, Selected scaling factor: {scaling_factor}")
    
    return scaling_factor

def apply_wayland_fixes() -> None:
    """
    Apply CustomTkinter fixes specific to Wayland environments.
    
    These fixes address common issues like:
    - Blurry text rendering
    - Scaling problems 
    - Window positioning issues
    - Color depth problems
    
    The fixes work by:
    1. Forcing X11 backend through XWayland for better Tkinter compatibility
    2. Setting explicit scaling factors to prevent fractional scaling
    3. Configuring font rendering for better text clarity
    4. Disabling auto-scaling features that cause issues
    
    Note: These environment variables must be set before any GUI toolkit
    initialization, which is why this is called early in configure_ui().
    """
    if not is_wayland_session():
        return
    
    # Set environment variables to improve rendering on Wayland
    wayland_env_fixes = {
        # Force X11 backend for better CustomTkinter compatibility
        'GDK_BACKEND': 'x11',
        'QT_QPA_PLATFORM': 'xcb',
        
        # Improve font rendering
        'FREETYPE_PROPERTIES': 'truetype:interpreter-version=40',
        
        # Fix scaling issues
        'GDK_SCALE': '1',
        'GDK_DPI_SCALE': '1',
        
        # Disable fractional scaling for Tkinter
        'XWAYLAND_SCALE': '1',
        
        # Force integer scaling
        'QT_AUTO_SCREEN_SCALE_FACTOR': '0',
        'QT_SCALE_FACTOR': '1',
        
        # Improve Tkinter window behavior
        'TK_SILENCE_DEPRECATION': '1',
    }
    
    # Apply environment variables only if not already set
    for env_var, value in wayland_env_fixes.items():
        if env_var not in os.environ:
            os.environ[env_var] = value

def get_display_info() -> dict:
    """
    Get information about the current display setup.
    
    Returns:
        Dictionary with display information including OS, display server, and scaling
    """
    info = {
        'os': detect_operating_system(),
        'is_wayland': is_wayland_session(),
        'display_server': 'wayland' if is_wayland_session() else 'x11',
        'wayland_display': os.environ.get('WAYLAND_DISPLAY', 'not_set'),
        'xdg_session_type': os.environ.get('XDG_SESSION_TYPE', 'not_set'),
    }
    
    # Add scaling information if available
    if 'GDK_SCALE' in os.environ:
        info['gdk_scale'] = os.environ['GDK_SCALE']
    if 'QT_SCALE_FACTOR' in os.environ:
        info['qt_scale'] = os.environ['QT_SCALE_FACTOR']
    
    return info

def icon(name: str, size: Tuple[int, int] = (18, 18)) -> Optional[ctk.CTkImage]:
    """
    Load icon images for UI elements.
    
    Args:
        name: Icon name (without extension)
        size: Tuple of (width, height)
        
    Returns:
        CTkImage or None if not available
    """
    if not PIL_AVAILABLE:
        return None
        
    try:
        # Get project root
        current_file = Path(__file__)
        project_root = current_file.parent.parent.parent
        
        # Look for icons in resources directory
        icon_path = project_root / "src" / "desktop" / "resources" / f"{name}.png"
        
        if icon_path.exists():
            return ctk.CTkImage(Image.open(icon_path), size=size)
        else:
            # Create a simple colored square as placeholder
            placeholder = Image.new('RGBA', size, (100, 100, 100, 255))
            return ctk.CTkImage(placeholder, size=size)
            
    except Exception:
        return None  # Silent fallback

def strip_variation_selectors(s: str) -> str:
    """
    Remove Unicode variation selectors that cause rendering issues.
    
    Args:
        s: Input string
        
    Returns:
        String with variation selectors removed
    """
    if not isinstance(s, str):
        return str(s)
    
    # Remove common variation selectors
    cleaned = s.replace("\ufe0e", "").replace("\ufe0f", "")
    
    # Remove other problematic Unicode characters
    cleaned = cleaned.replace("\u200d", "")  # Zero-width joiner
    cleaned = cleaned.replace("\u200c", "")  # Zero-width non-joiner
    
    return cleaned

def clean_text(text: str) -> str:
    """
    Clean text for safe display in UI components.
    
    Args:
        text: Input text
        
    Returns:
        Cleaned text safe for UI display
    """
    if not text:
        return ""
    
    # Strip variation selectors
    cleaned = strip_variation_selectors(text)
    
    # Remove or replace common problematic emoji/Unicode
    emoji_replacements = {
        "🧹": "Clean",
        "📁": "Folder",
        "🔊": "Audio",
        "🎤": "Mic",
        "📹": "Camera",
        "⚙️": "Settings",
        "🚀": "Start",
        "⏹️": "Stop",
        "📋": "Clipboard",
        "💾": "Save",
        "🔄": "Refresh",
        "❌": "Close",
        "✅": "OK",
        "⚠️": "Warning",
        "🎯": "Target",
        "🔍": "Search",
        "📊": "Stats",
        "🌐": "Web",
        "🎨": "Theme",
        "🌍": "",
        "🧠": "",
        "💾": "Export",
        "🗑️": "Clear",
        "📤": "Send"
    }
    
    for emoji, replacement in emoji_replacements.items():
        cleaned = cleaned.replace(emoji, replacement)
    
    return cleaned.strip()

def configure_ui():
    """Configure global UI settings for consistent appearance."""
    # Apply Wayland fixes if needed (must be done before CTk initialization)
    apply_wayland_fixes()
    
    # Apply font scaling for Wayland/HiDPI displays (must be done early)
    apply_font_scaling_for_wayland()
    
    # Appearance / Theme - avoid 'system' mode on Linux
    ctk.set_appearance_mode("dark")
    ctk.set_default_color_theme("dark-blue")
    
    # Apply platform-specific scaling fixes
    apply_platform_scaling_fixes()

def apply_font_scaling_for_wayland():
    """
    Apply font scaling specifically for Wayland environments to fix text readability.
    This addresses the issue where text remains too small even after window scaling.
    """
    try:
        # Import theme module to apply font scaling
        from .theme import apply_font_scaling, get_font_scaling_info
        
        # Apply font scaling based on environment detection
        apply_font_scaling()
        
        # Log scaling information for debugging
        scaling_info = get_font_scaling_info()
        logger.info(f"Font scaling applied - Wayland: {scaling_info['wayland_detected']}, Scale: {scaling_info['font_scale_factor']}")
        logger.info(f"Scaled font sizes - Body: {scaling_info['scaled_sizes']['body']}, Button: {scaling_info['scaled_sizes']['button']}")
        
    except Exception as e:
        logger.error(f"Failed to apply font scaling for Wayland: {e}")
        # Continue without font scaling rather than failing completely
        logger.warning("Continuing with default font sizes")

def apply_platform_scaling_fixes():
    """
    Apply platform-specific scaling fixes, particularly for Wayland on Linux.
    
    This addresses specific issues like:
    - LoginDialog and other dialogs appearing too small on Wayland
    - DPI/scaling misbehavior in CustomTkinter under Wayland
    - Inconsistent window sizing across different display servers
    """
    is_linux = detect_operating_system() == 'Linux'
    is_wayland = is_wayland_session()
    
    # Log environment detection for debugging
    logger.info(f"Platform detection - OS: {detect_operating_system()}, Wayland: {is_wayland}")
    
    if is_linux and is_wayland:
        # Apply Wayland-specific scaling fixes
        apply_wayland_scaling_fixes()
    else:
        # Apply conservative scaling for other platforms
        apply_standard_scaling()

def apply_wayland_scaling_fixes():
    """
    Apply stronger and adaptive scaling fixes specifically for Wayland environments.
    This includes DPI-aware scaling for HiDPI displays to properly handle LoginDialog 
    and other modal dialogs that render too small.
    """
    
    try:
        # Calculate adaptive scaling factor based on DPI
        scaling_factor = calculate_adaptive_scaling()
        
        logger.info(f"Applying Wayland-specific adaptive scaling with factor: {scaling_factor}")
        
        # Create a temporary root to apply Tk scaling
        try:
            # Try to get existing root or create a temporary one
            import tkinter as tk
            try:
                root = tk._default_root
                if root is None:
                    # Create temporary root for scaling configuration
                    temp_root = tk.Tk()
                    temp_root.withdraw()  # Hide the window
                    temp_root.tk.call("tk", "scaling", scaling_factor)
                    temp_root.destroy()
                else:
                    root.tk.call("tk", "scaling", scaling_factor)
                    
                logger.info(f"Applied Tk scaling factor: {scaling_factor} for Wayland")
            except Exception as tk_error:
                logger.warning(f"Could not apply Tk scaling: {tk_error}")
        
        except ImportError:
            logger.warning("tkinter not available for scaling fix")
        
        # Apply CustomTkinter scaling to maintain consistency
        ctk.set_widget_scaling(scaling_factor)
        ctk.set_window_scaling(scaling_factor)
        logger.info(f"Applied CustomTkinter scaling factor: {scaling_factor} for Wayland")
        
        # Set environment variable for debugging/verification
        os.environ['TALKBRIDGE_WAYLAND_SCALING'] = str(scaling_factor)
        
        logger.info(f"Wayland adaptive scaling fixes applied successfully with factor {scaling_factor}")
        
    except Exception as e:
        logger.error(f"Failed to apply Wayland adaptive scaling fixes: {e}")
        # Fallback to basic strong scaling
        try:
            import tkinter as tk
            fallback_factor = 1.6
            
            # Apply fallback scaling
            try:
                root = tk._default_root
                if root is None:
                    temp_root = tk.Tk()
                    temp_root.withdraw()
                    temp_root.tk.call("tk", "scaling", fallback_factor)
                    temp_root.destroy()
                else:
                    root.tk.call("tk", "scaling", fallback_factor)
            except Exception:
                pass
            
            ctk.set_widget_scaling(fallback_factor)
            ctk.set_window_scaling(fallback_factor)
            os.environ['TALKBRIDGE_WAYLAND_SCALING'] = str(fallback_factor)
            logger.info(f"Applied fallback Wayland scaling: {fallback_factor}")
        except Exception as fallback_error:
            logger.error(f"Even fallback scaling failed: {fallback_error}")
            # Final fallback to standard scaling
            apply_standard_scaling()

def apply_standard_scaling():
    """
    Apply standard scaling for non-Wayland environments.
    
    Uses conservative 1.0 scaling to prevent issues on other platforms.
    """
    
    try:
        # Conservative scaling for X11, Windows, and macOS
        ctk.set_widget_scaling(1.0)
        ctk.set_window_scaling(1.0)
        logger.info("Applied standard scaling (1.0) for non-Wayland environment")
        
    except Exception as e:
        logger.warning(f"Failed to apply standard scaling: {e}")

def get_ui_environment_info() -> dict:
    """
    Get comprehensive information about the UI environment and applied fixes.
    
    Returns:
        Dictionary containing environment info and fix status
    """
    display_info = get_display_info()
    
    info = {
        'environment': display_info,
        'wayland_fixes_applied': is_wayland_session(),
        'customtkinter_version': getattr(ctk, '__version__', 'unknown'),
        'python_version': platform.python_version(),
    }
    
    # Add scaling information
    is_linux = detect_operating_system() == 'Linux'
    is_wayland = is_wayland_session()
    
    # Get DPI information
    try:
        screen_dpi = detect_screen_dpi()
        adaptive_scaling = calculate_adaptive_scaling()
    except Exception:
        screen_dpi = "unknown"
        adaptive_scaling = "unknown"
    
    info['scaling_info'] = {
        'platform': detect_operating_system(),
        'wayland_detected': is_wayland,
        'screen_dpi': screen_dpi,
        'adaptive_scaling_factor': adaptive_scaling,
        'scaling_applied': 'wayland' if (is_linux and is_wayland) else 'standard',
        'wayland_scaling_factor': os.environ.get('TALKBRIDGE_WAYLAND_SCALING'),
    }
    
    # Add font scaling information
    try:
        from .theme import get_font_scaling_info
        font_info = get_font_scaling_info()
        info['font_scaling_info'] = font_info
    except Exception as e:
        info['font_scaling_info'] = {'error': str(e)}
    
    # Add information about applied environment variables
    if is_wayland_session():
        info['applied_env_vars'] = {
            'GDK_BACKEND': os.environ.get('GDK_BACKEND'),
            'QT_QPA_PLATFORM': os.environ.get('QT_QPA_PLATFORM'),
            'GDK_SCALE': os.environ.get('GDK_SCALE'),
            'QT_SCALE_FACTOR': os.environ.get('QT_SCALE_FACTOR'),
        }
    
    return info

def verify_scaling_fixes() -> dict:
    """
    Verify that scaling fixes have been applied correctly.
    
    Returns:
        Dictionary with verification status and current settings
    """
    # Get DPI and scaling information
    try:
        screen_dpi = detect_screen_dpi()
        adaptive_scaling = calculate_adaptive_scaling()
    except Exception:
        screen_dpi = "detection_failed"
        adaptive_scaling = "calculation_failed"
    
    verification = {
        'wayland_detected': is_wayland_session(),
        'screen_dpi': screen_dpi,
        'adaptive_scaling_factor': adaptive_scaling,
        'scaling_factor_set': os.environ.get('TALKBRIDGE_WAYLAND_SCALING'),
        'environment_fixes': {
            'gdk_backend': os.environ.get('GDK_BACKEND'),
            'qt_platform': os.environ.get('QT_QPA_PLATFORM'),
        },
        'recommendations': []
    }
    
    # Add recommendations based on current state
    if verification['wayland_detected']:
        if not verification['scaling_factor_set']:
            verification['recommendations'].append(
                "Call configure_ui() to apply Wayland adaptive scaling fixes"
            )
        else:
            current_factor = verification['scaling_factor_set']
            recommended_factor = verification['adaptive_scaling_factor']
            if current_factor != str(recommended_factor):
                verification['recommendations'].append(
                    f"Current scaling {current_factor} differs from recommended {recommended_factor} for DPI {screen_dpi}"
                )
            else:
                verification['recommendations'].append(
                    f"Wayland adaptive scaling factor {current_factor} applied successfully for DPI {screen_dpi}"
                )
    else:
        verification['recommendations'].append(
            "No Wayland-specific fixes needed for current environment"
        )
    
    return verification

def set_manual_scaling_override(scaling_factor: float) -> None:
    """
    Manually override the scaling factor for testing or special cases.
    
    Args:
        scaling_factor: Desired scaling factor (e.g., 1.6, 1.7, 1.8)
    """
    
    try:
        import tkinter as tk
        import customtkinter as ctk
        
        # Apply Tk scaling
        try:
            root = tk._default_root
            if root is None:
                temp_root = tk.Tk()
                temp_root.withdraw()
                temp_root.tk.call("tk", "scaling", scaling_factor)
                temp_root.destroy()
            else:
                root.tk.call("tk", "scaling", scaling_factor)
        except Exception as tk_error:
            logger.warning(f"Could not apply Tk scaling override: {tk_error}")
        
        # Apply CustomTkinter scaling
        ctk.set_widget_scaling(scaling_factor)
        ctk.set_window_scaling(scaling_factor)
        
        # Set environment variable
        os.environ['TALKBRIDGE_MANUAL_SCALING'] = str(scaling_factor)
        os.environ['TALKBRIDGE_WAYLAND_SCALING'] = str(scaling_factor)
        
        logger.info(f"Manual scaling override applied: {scaling_factor}")
        
    except Exception as e:
        logger.error(f"Failed to apply manual scaling override: {e}")

if __name__ == "__main__":
    # Test script for DPI detection and scaling calculation
    # logging.basicConfig(level=logging.INFO, format='%(levelname)s - %(message)s')
    
    logger.info("=== TalkBridge UI Utils - Wayland/DPI Testing ===")
    
    # Test OS detection
    logger.info(f"Operating System: {detect_operating_system()}")
    logger.info(f"Wayland Session: {is_wayland_session()}")
    
    # Test DPI detection
    try:
        dpi = detect_screen_dpi()
        logger.info(f"Detected Screen DPI: {dpi}")
    except Exception as e:
        logger.error(f"DPI Detection Failed: {e}")
        dpi = 96.0
    
    # Test adaptive scaling calculation
    try:
        scaling = calculate_adaptive_scaling()
        logger.info(f"Recommended Scaling Factor: {scaling}")
    except Exception as e:
        logger.error(f"Scaling Calculation Failed: {e}")
    
    # Test environment info
    try:
        env_info = get_ui_environment_info()
        logger.info("Environment Info:")
        for key, value in env_info.items():
            if isinstance(value, dict):
                logger.info(f"  {key}:")
                for subkey, subvalue in value.items():
                    logger.info(f"    {subkey}: {subvalue}")
            else:
                logger.info(f"  {key}: {value}")
    except Exception as e:
        logger.error(f"Environment Info Failed: {e}")
    
    logger.info("=== End Testing ===")

# Export main functions for external use
__all__ = [
    'detect_operating_system',
    'is_wayland_session', 
    'detect_screen_dpi',
    'calculate_adaptive_scaling',
    'apply_wayland_fixes',
    'apply_wayland_scaling_fixes',
    'configure_ui',
    'get_ui_environment_info',
    'verify_scaling_fixes',
    'set_manual_scaling_override',
    'clean_text_for_display'
]

# Icon name mappings for common UI elements
ICON_MAPPINGS = {
    "clear": "broom",
    "folder": "folder",
    "audio": "speaker",
    "microphone": "microphone", 
    "camera": "camera",
    "settings": "gear",
    "start": "play",
    "stop": "stop",
    "clipboard": "clipboard",
    "save": "save",
    "refresh": "refresh",
    "close": "x",
    "ok": "check",
    "warning": "warning",
    "target": "target",
    "search": "search",
    "stats": "chart",
    "web": "globe",
    "theme": "palette"
}
