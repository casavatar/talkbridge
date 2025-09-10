#!/usr/bin/env python3
"""
TalkBridge Desktop - UI Utilities
=================================

Utility functions for UI components including icon loading and text cleaning.

Author: TalkBridge Team
Date: 2025-09-09
Version: 1.0
"""

import customtkinter as ctk
from pathlib import Path
from typing import Optional, Tuple

try:
    from PIL import Image
    PIL_AVAILABLE = True
except ImportError:
    PIL_AVAILABLE = False


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
    # Appearance / Theme - avoid 'system' mode on Linux
    ctk.set_appearance_mode("dark")
    ctk.set_default_color_theme("dark-blue")
    
    # Pixelation fix: avoid fractional scaling
    ctk.set_widget_scaling(1.0)
    ctk.set_window_scaling(1.0)


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
