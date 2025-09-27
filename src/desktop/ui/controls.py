"""
UI control factory functions for TalkBridge Desktop.

This module provides reusable factory functions for creating styled CustomTkinter
components with consistent theming and proper fallback handling. All UI components
should be created through these factories to ensure consistent styling.
"""

import logging
from typing import Any, Callable, Dict, Optional, Union, Literal

# Try to import customtkinter for UI components
try:
    import customtkinter as ctk
    CUSTOMTKINTER_AVAILABLE = True
except ImportError:
    CUSTOMTKINTER_AVAILABLE = False
    ctk = None

# Import theme system
from .theme import ComponentThemes, ColorPalette, Typography, Dimensions, Spacing

logger = logging.getLogger(__name__)

# Type aliases for better readability
FrameVariant = Literal["default", "card", "section", "transparent", "elevated", "surface"]
ButtonVariant = Literal["primary", "secondary", "success", "danger", "warning", "ghost"]
LabelVariant = Literal["title", "heading", "body", "caption", "hint"]

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
        if ctk is not None:
            frame = ctk.CTkFrame(master, **defaults)
            logger.debug(f"Created frame with variant '{variant}' and defaults: {defaults}")
            return frame
        else:
            logger.error("CustomTkinter not available")
            return None
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
        if ctk is not None:
            button = ctk.CTkButton(master, text=text, command=command, **defaults)
            logger.debug(f"Created button '{text}' with variant '{variant}' and defaults: {defaults}")
            return button
        else:
            logger.error("CustomTkinter not available")
            return None
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
        if ctk is not None:
            label = ctk.CTkLabel(master, text=text, **defaults)
            logger.debug(f"Created label '{text}' with variant '{variant}'")
            return label
        else:
            logger.error("CustomTkinter not available")
            return None
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
        if ctk is not None:
            entry = ctk.CTkEntry(master, placeholder_text=placeholder_text, **defaults)
            logger.debug(f"Created entry with placeholder '{placeholder_text}'")
            return entry
        else:
            logger.error("CustomTkinter not available")
            return None
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
    defaults: Dict[str, Any] = {
        "corner_radius": 8,
        "border_width": 1
    }
    
    if ctk is not None:
        defaults["font"] = ctk.CTkFont(size=14)
    
    # Allow kwargs to override defaults
    defaults.update(kwargs)
    
    try:
        if ctk is not None:
            textbox = ctk.CTkTextbox(master, **defaults)
            logger.debug("Created textbox with styling")
            return textbox
        else:
            logger.error("CustomTkinter not available")
            return None
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
        if ctk is not None:
            checkbox = ctk.CTkCheckBox(master, text=text, **defaults)
            logger.debug(f"Created checkbox '{text}'")
            return checkbox
        else:
            logger.error("CustomTkinter not available")
            return None
    except Exception as e:
        logger.error(f"Failed to create checkbox '{text}': {e}")
        return None

def create_combobox(
    master,
    values: Optional[list] = None,
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
        if ctk is not None:
            combobox = ctk.CTkComboBox(master, values=values, **defaults)
            logger.debug(f"Created combobox with {len(values)} values")
            return combobox
        else:
            logger.error("CustomTkinter not available")
            return None
    except Exception as e:
        logger.error(f"Failed to create combobox: {e}")
        return None

# Specialized dialog control functions
def create_dialog_window(parent, title: str = "Dialog", width: int = 480, height: int = 600, **kwargs) -> Any:
    """Create a standardized dialog window with proper theming and modal behavior.
    
    Args:
        parent: Parent window
        title: Dialog window title
        width: Dialog width in pixels
        height: Dialog height in pixels
        **kwargs: Additional CustomTkinter CTkToplevel parameters
        
    Returns:
        CTkToplevel instance or None if CustomTkinter is not available
    """
    if not CUSTOMTKINTER_AVAILABLE:
        logger.warning("CustomTkinter not available, cannot create dialog window")
        return None
    
    # Default dialog configuration
    defaults = {
        "fg_color": ColorPalette.BACKGROUND_PRIMARY,
        "corner_radius": 0
    }
    defaults.update(kwargs)
    
    try:
        if ctk is not None:
            dialog = ctk.CTkToplevel(parent, **defaults)
            dialog.title(title)
            dialog.geometry(f"{width}x{height}")
            dialog.resizable(False, False)
            
            # Configure dialog properties
            if parent and hasattr(parent, 'winfo_exists') and parent.winfo_exists():
                dialog.transient(parent)
            
            logger.debug(f"Created dialog window '{title}' ({width}x{height})")
            return dialog
        else:
            logger.error("CustomTkinter not available")
            return None
    except Exception as e:
        logger.error(f"Failed to create dialog window '{title}': {e}")
        return None

def create_auth_form_frame(master, **kwargs) -> Any:
    """Create a form frame specifically styled for authentication dialogs.
    
    Args:
        master: Parent widget
        **kwargs: Additional CustomTkinter CTkFrame parameters
        
    Returns:
        CTkFrame instance or None if CustomTkinter is not available
    """
    if not CUSTOMTKINTER_AVAILABLE:
        return None
    
    defaults = {
        "fg_color": ColorPalette.BACKGROUND_SECONDARY,
        "corner_radius": Dimensions.RADIUS_LG,
        "border_width": 0
    }
    defaults.update(kwargs)
    
    try:
        if ctk is not None:
            frame = ctk.CTkFrame(master, **defaults)
            logger.debug("Created authentication form frame")
            return frame
        else:
            return None
    except Exception as e:
        logger.error(f"Failed to create auth form frame: {e}")
        return None

def create_password_field_with_toggle(master, placeholder: str = "Enter your password", **kwargs) -> tuple:
    """Create a password entry field with show/hide toggle functionality.
    
    Args:
        master: Parent widget
        placeholder: Placeholder text for the entry
        **kwargs: Additional parameters for the entry field
        
    Returns:
        Tuple of (entry_widget, toggle_checkbox, container_frame) or (None, None, None)
    """
    if not CUSTOMTKINTER_AVAILABLE:
        return None, None, None
    
    try:
        import tkinter as tk
        
        # Container frame for the password field and toggle
        container = create_frame(master, variant="transparent")
        if not container:
            return None, None, None
        
        # Password entry field
        entry_defaults = ComponentThemes.get_input_theme()
        entry_defaults.update({
            "placeholder_text": placeholder,
            "show": "*"
        })
        entry_defaults.update(kwargs)
        
        if ctk is not None:
            password_entry = ctk.CTkEntry(container, **entry_defaults)
            password_entry.pack(side="left", fill="x", expand=True, padx=(0, Spacing.SM))
            
            # Show/hide toggle checkbox
            show_var = tk.BooleanVar()
            
            def toggle_password():
                if show_var.get():
                    password_entry.configure(show="")
                else:
                    password_entry.configure(show="*")
            
            toggle_checkbox = ctk.CTkCheckBox(
                container,
                text="Show",
                width=60,
                height=28,
                checkbox_width=18,
                checkbox_height=18,
                variable=show_var,
                command=toggle_password,
                fg_color=ColorPalette.ACCENT_PRIMARY,
                font=ctk.CTkFont(size=Typography.FONT_SIZE_CAPTION) if ctk else None
            )
            toggle_checkbox.pack(side="right")
            
            logger.debug("Created password field with toggle")
            return password_entry, toggle_checkbox, container
        else:
            return None, None, None
    except Exception as e:
        logger.error(f"Failed to create password field with toggle: {e}")
        return None, None, None

def create_dialog_button_set(master, primary_text: str = "OK", secondary_text: str = "Cancel", 
                           primary_command: Optional[Callable] = None, 
                           secondary_command: Optional[Callable] = None, **kwargs) -> tuple:
    """Create a standardized set of dialog buttons (primary and secondary).
    
    Args:
        master: Parent widget
        primary_text: Text for primary button
        secondary_text: Text for secondary button
        primary_command: Command for primary button
        secondary_command: Command for secondary button
        **kwargs: Additional parameters
        
    Returns:
        Tuple of (primary_button, secondary_button, container_frame)
    """
    if not CUSTOMTKINTER_AVAILABLE:
        return None, None, None
    
    try:
        # Container for buttons
        container = create_frame(master, variant="transparent")
        if not container:
            return None, None, None
        
        # Primary button (action button)
        primary_button = create_button(
            container, 
            text=primary_text, 
            command=primary_command, 
            variant="primary"
        )
        if primary_button:
            primary_button.pack(fill="x", pady=(0, Spacing.SM))
        
        # Secondary button (cancel/close)
        secondary_button = create_button(
            container, 
            text=secondary_text, 
            command=secondary_command, 
            variant="secondary"
        )
        if secondary_button:
            secondary_button.pack(fill="x")
        
        logger.debug(f"Created dialog button set: '{primary_text}' and '{secondary_text}'")
        return primary_button, secondary_button, container
    except Exception as e:
        logger.error(f"Failed to create dialog button set: {e}")
        return None, None, None

def create_status_indicator(master, initial_text: str = "Ready", **kwargs) -> Any:
    """Create a status indicator label for dialogs and forms.
    
    Args:
        master: Parent widget
        initial_text: Initial status text
        **kwargs: Additional CustomTkinter CTkLabel parameters
        
    Returns:
        CTkLabel instance configured as a status indicator
    """
    if not CUSTOMTKINTER_AVAILABLE:
        return None
    
    defaults = {
        "text": initial_text,
        "height": 30,
        "font": ctk.CTkFont(size=Typography.FONT_SIZE_CAPTION) if ctk else None,
        "text_color": ColorPalette.TEXT_SECONDARY,
        "wraplength": 400,
        "anchor": "center"
    }
    defaults.update(kwargs)
    
    try:
        if ctk is not None:
            status_label = ctk.CTkLabel(master, **defaults)
            
            # Add method to update status with color
            def update_status(text: str, color: Optional[str] = None):
                try:
                    if hasattr(status_label, 'winfo_exists') and status_label.winfo_exists():
                        status_label.configure(
                            text=text,
                            text_color=color or ColorPalette.TEXT_SECONDARY
                        )
                except Exception as e:
                    logger.warning(f"Failed to update status: {e}")
            
            # Store the update method in a way that doesn't trigger linting errors
            setattr(status_label, 'update_status', update_status)
            
            logger.debug(f"Created status indicator with text: '{initial_text}'")
            return status_label
        else:
            return None
    except Exception as e:
        logger.error(f"Failed to create status indicator: {e}")
        return None

# Specialized confirmation dialog controls
def create_confirmation_dialog(parent, title: str = "Confirmation", width: int = 400, height: int = 200, **kwargs) -> Any:
    """Create a standardized confirmation dialog window.
    
    Args:
        parent: Parent window
        title: Dialog window title
        width: Dialog width in pixels  
        height: Dialog height in pixels
        **kwargs: Additional CustomTkinter CTkToplevel parameters
        
    Returns:
        CTkToplevel instance or None if CustomTkinter is not available
    """
    if not CUSTOMTKINTER_AVAILABLE:
        logger.warning("CustomTkinter not available, cannot create confirmation dialog")
        return None
    
    # Default confirmation dialog configuration
    defaults = {
        "fg_color": ColorPalette.BACKGROUND_PRIMARY,
        "corner_radius": 0
    }
    defaults.update(kwargs)
    
    try:
        if ctk is not None:
            dialog = ctk.CTkToplevel(parent, **defaults)
            dialog.title(title)
            dialog.geometry(f"{width}x{height}")
            dialog.resizable(False, False)
            
            # Configure dialog properties
            if parent and hasattr(parent, 'winfo_exists') and parent.winfo_exists():
                dialog.transient(parent)
            
            logger.debug(f"Created confirmation dialog '{title}' ({width}x{height})")
            return dialog
        else:
            logger.error("CustomTkinter not available")
            return None
    except Exception as e:
        logger.error(f"Failed to create confirmation dialog '{title}': {e}")
        return None

def create_warning_dialog(parent, title: str = "Warning", **kwargs) -> Any:
    """Create a warning-styled confirmation dialog.
    
    Args:
        parent: Parent window
        title: Dialog window title
        **kwargs: Additional parameters
        
    Returns:
        CTkToplevel instance configured for warning display
    """
    return create_confirmation_dialog(
        parent, 
        title=title, 
        width=400, 
        height=200, 
        **kwargs
    )

def create_icon_label(parent, icon_text: str = "ℹ️", icon_size: int = 32, 
                     color: Optional[str] = None, **kwargs) -> Any:
    """Create an icon label for dialogs and notifications.
    
    Args:
        parent: Parent widget
        icon_text: Icon text (emoji or character)
        icon_size: Font size for the icon
        color: Text color (uses theme default if None)
        **kwargs: Additional CustomTkinter CTkLabel parameters
        
    Returns:
        CTkLabel instance configured as an icon
    """
    if not CUSTOMTKINTER_AVAILABLE:
        return None
    
    # Default icon styling
    defaults = {
        "text": icon_text,
        "font": ctk.CTkFont(size=icon_size) if ctk else None,
        "text_color": color or ColorPalette.TEXT_PRIMARY
    }
    defaults.update(kwargs)
    
    try:
        if ctk is not None:
            icon_label = ctk.CTkLabel(parent, **defaults)
            logger.debug(f"Created icon label with text: '{icon_text}'")
            return icon_label
        else:
            return None
    except Exception as e:
        logger.error(f"Failed to create icon label: {e}")
        return None

def create_confirmation_button_set(master, confirm_text: str = "Yes", cancel_text: str = "No",
                                 confirm_variant: str = "danger", cancel_variant: str = "secondary",
                                 confirm_command: Optional[Callable] = None,
                                 cancel_command: Optional[Callable] = None, **kwargs) -> tuple:
    """Create a standardized set of confirmation buttons.
    
    Args:
        master: Parent widget
        confirm_text: Text for confirmation button
        cancel_text: Text for cancel button
        confirm_variant: Button variant for confirmation ("danger", "primary", "warning")
        cancel_variant: Button variant for cancel ("secondary", "ghost")
        confirm_command: Command for confirmation button
        cancel_command: Command for cancel button
        **kwargs: Additional parameters
        
    Returns:
        Tuple of (confirm_button, cancel_button, container_frame)
    """
    if not CUSTOMTKINTER_AVAILABLE:
        return None, None, None
    
    try:
        # Container for buttons
        container = create_frame(master, variant="transparent")
        if not container:
            return None, None, None
        
        # Cancel button (left side)
        cancel_button = create_button(
            container,
            text=cancel_text,
            command=cancel_command,
            variant=cancel_variant,
            width=120,
            height=35
        )
        if cancel_button:
            cancel_button.pack(side="left", padx=(0, Spacing.SM))
        
        # Confirm button (right side) 
        confirm_button = create_button(
            container,
            text=confirm_text,
            command=confirm_command,
            variant=confirm_variant,
            width=120,
            height=35
        )
        if confirm_button:
            confirm_button.pack(side="right")
        
        logger.debug(f"Created confirmation button set: '{confirm_text}' and '{cancel_text}'")
        return confirm_button, cancel_button, container
    except Exception as e:
        logger.error(f"Failed to create confirmation button set: {e}")
        return None, None, None

# Export the main control creation functions
__all__ = [
    "create_frame",
    "create_button", 
    "create_label",
    "create_entry",
    "create_textbox",
    "create_checkbox",
    "create_combobox",
    "create_dialog_window",
    "create_auth_form_frame",
    "create_password_field_with_toggle",
    "create_dialog_button_set",
    "create_status_indicator",
    "create_confirmation_dialog",
    "create_warning_dialog",
    "create_icon_label",
    "create_confirmation_button_set",
    "CUSTOMTKINTER_AVAILABLE"
]