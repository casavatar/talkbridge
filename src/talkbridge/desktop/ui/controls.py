"""
UI control factory functions for TalkBridge Desktop.

This module provides reusable factory functions for creating styled CustomTkinter
components with consistent theming and proper fallback handling.
"""

import logging
from typing import Any, Callable, Dict, Optional

# Try to import customtkinter for UI components
try:
    import customtkinter as ctk
    CUSTOMTKINTER_AVAILABLE = True
except ImportError:
    CUSTOMTKINTER_AVAILABLE = False
    ctk = None

# Import theme system
from .theme import ComponentThemes, CUSTOMTKINTER_AVAILABLE as THEME_CTK_AVAILABLE

logger = logging.getLogger(__name__)

def create_frame(master, variant: str = "default", **kwargs) -> Any:
    """Create a standardized CTkFrame with theme-based styling.
    
    Args:
        master: Parent widget
        variant: Theme variant ("default", "card", "section", or "transparent")
        **kwargs: Additional CustomTkinter CTkFrame parameters that override defaults
        
    Returns:
        CTkFrame instance or None if CustomTkinter is not available
        
    Example:
        # Basic frame
        frame = create_frame(parent)
        
        # Card-style frame with custom padding
        card = create_frame(parent, variant="card", corner_radius=12)
        
        # Transparent frame
        transparent = create_frame(parent, variant="transparent")
    """
    if not CUSTOMTKINTER_AVAILABLE:
        logger.warning("CustomTkinter not available, cannot create frame")
        return None
    
    # Handle special transparent variant
    if variant == "transparent":
        defaults = {"fg_color": "transparent", "corner_radius": 0, "border_width": 0}
    else:
        # Get theme-based defaults
        defaults = ComponentThemes.get_frame_theme(variant)
    
    # Allow kwargs to override defaults
    defaults.update(kwargs)
    
    try:
        frame = ctk.CTkFrame(master, **defaults)
        logger.debug(f"Created frame with variant '{variant}' and defaults: {defaults}")
        return frame
    except Exception as e:
        logger.error(f"Failed to create frame: {e}")
        return None

def create_button(
    master, 
    text: str, 
    command: Optional[Callable] = None, 
    variant: str = "primary", 
    **kwargs
) -> Any:
    """Create a standardized CTkButton with theme-based styling.
    
    Args:
        master: Parent widget
        text: Button text
        command: Button click callback function
        variant: Theme variant ("primary", "secondary", "danger")
        **kwargs: Additional CustomTkinter CTkButton parameters that override defaults
        
    Returns:
        CTkButton instance or None if CustomTkinter is not available
        
    Example:
        # Primary action button
        submit_btn = create_button(parent, "Submit", command=handle_submit)
        
        # Secondary button with custom width
        cancel_btn = create_button(parent, "Cancel", variant="secondary", width=100)
        
        # Danger button
        delete_btn = create_button(parent, "Delete", variant="danger", command=handle_delete)
    """
    if not CUSTOMTKINTER_AVAILABLE:
        logger.warning("CustomTkinter not available, cannot create button")
        return None
    
    # Get theme-based defaults
    defaults = ComponentThemes.get_button_theme(variant)
    
    # Allow kwargs to override defaults
    defaults.update(kwargs)
    
    try:
        button = ctk.CTkButton(master, text=text, command=command, **defaults)
        logger.debug(f"Created button '{text}' with variant '{variant}' and defaults: {defaults}")
        return button
    except Exception as e:
        logger.error(f"Failed to create button '{text}': {e}")
        return None

def create_label(
    master, 
    text: str = "", 
    variant: str = "default", 
    **kwargs
) -> Any:
    """Create a standardized CTkLabel with theme-based styling.
    
    Args:
        master: Parent widget
        text: Label text
        variant: Theme variant ("default", "heading", "caption", "error")
        **kwargs: Additional CustomTkinter CTkLabel parameters that override defaults
        
    Returns:
        CTkLabel instance or None if CustomTkinter is not available
    """
    if not CUSTOMTKINTER_AVAILABLE:
        logger.warning("CustomTkinter not available, cannot create label")
        return None
    
    # Get theme-based defaults
    defaults = ComponentThemes.get_label_theme(variant)
    
    # Allow kwargs to override defaults
    defaults.update(kwargs)
    
    try:
        label = ctk.CTkLabel(master, text=text, **defaults)
        logger.debug(f"Created label '{text}' with variant '{variant}'")
        return label
    except Exception as e:
        logger.error(f"Failed to create label '{text}': {e}")
        return None

def create_entry(
    master, 
    placeholder_text: str = "", 
    **kwargs
) -> Any:
    """Create a standardized CTkEntry with theme-based styling.
    
    Args:
        master: Parent widget
        placeholder_text: Placeholder text shown when empty
        **kwargs: Additional CustomTkinter CTkEntry parameters that override defaults
        
    Returns:
        CTkEntry instance or None if CustomTkinter is not available
    """
    if not CUSTOMTKINTER_AVAILABLE:
        logger.warning("CustomTkinter not available, cannot create entry")
        return None
    
    # Get theme-based defaults
    defaults = ComponentThemes.get_input_theme()
    
    # Allow kwargs to override defaults
    defaults.update(kwargs)
    
    try:
        entry = ctk.CTkEntry(master, placeholder_text=placeholder_text, **defaults)
        logger.debug(f"Created entry with placeholder '{placeholder_text}'")
        return entry
    except Exception as e:
        logger.error(f"Failed to create entry: {e}")
        return None

def create_textbox(
    master, 
    **kwargs
) -> Any:
    """Create a standardized CTkTextbox with theme-based styling.
    
    Args:
        master: Parent widget
        **kwargs: Additional CustomTkinter CTkTextbox parameters that override defaults
        
    Returns:
        CTkTextbox instance or None if CustomTkinter is not available
    """
    if not CUSTOMTKINTER_AVAILABLE:
        logger.warning("CustomTkinter not available, cannot create textbox")
        return None
    
    # Basic defaults for textbox (no specific theme method exists)
    defaults = {
        "corner_radius": 8,
        "border_width": 1,
        "font": ctk.CTkFont(size=14)
    }
    
    # Allow kwargs to override defaults
    defaults.update(kwargs)
    
    try:
        textbox = ctk.CTkTextbox(master, **defaults)
        logger.debug("Created textbox with styling")
        return textbox
    except Exception as e:
        logger.error(f"Failed to create textbox: {e}")
        return None

def create_checkbox(
    master,
    text: str = "",
    **kwargs
) -> Any:
    """Create a standardized CTkCheckBox with theme-based styling.
    
    Args:
        master: Parent widget
        text: Checkbox label text
        **kwargs: Additional CustomTkinter CTkCheckBox parameters that override defaults
        
    Returns:
        CTkCheckBox instance or None if CustomTkinter is not available
    """
    if not CUSTOMTKINTER_AVAILABLE:
        logger.warning("CustomTkinter not available, cannot create checkbox")
        return None
    
    # Get theme-based defaults
    defaults = ComponentThemes.get_checkbox_theme()
    
    # Allow kwargs to override defaults
    defaults.update(kwargs)
    
    try:
        checkbox = ctk.CTkCheckBox(master, text=text, **defaults)
        logger.debug(f"Created checkbox '{text}'")
        return checkbox
    except Exception as e:
        logger.error(f"Failed to create checkbox '{text}': {e}")
        return None

def create_combobox(
    master,
    values: list = None,
    **kwargs
) -> Any:
    """Create a standardized CTkComboBox with theme-based styling.
    
    Args:
        master: Parent widget
        values: List of dropdown options
        **kwargs: Additional CustomTkinter CTkComboBox parameters that override defaults
        
    Returns:
        CTkComboBox instance or None if CustomTkinter is not available
    """
    if not CUSTOMTKINTER_AVAILABLE:
        logger.warning("CustomTkinter not available, cannot create combobox")
        return None
    
    if values is None:
        values = []
    
    # Get theme-based defaults
    defaults = ComponentThemes.get_combobox_theme()
    
    # Allow kwargs to override defaults
    defaults.update(kwargs)
    
    try:
        combobox = ctk.CTkComboBox(master, values=values, **defaults)
        logger.debug(f"Created combobox with {len(values)} values")
        return combobox
    except Exception as e:
        logger.error(f"Failed to create combobox: {e}")
        return None

# Export the main control creation functions
__all__ = [
    "create_frame",
    "create_button", 
    "create_label",
    "create_entry",
    "create_textbox",
    "create_checkbox",
    "create_combobox",
    "CUSTOMTKINTER_AVAILABLE"
]