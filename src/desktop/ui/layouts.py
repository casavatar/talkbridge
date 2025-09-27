#!/usr/bin/env python3
"""
TalkBridge Desktop - Layout Utilities
====================================

Common layout patterns and utilities for consistent UI structure.
This module provides reusable layout functions to maintain consistency
across different components and reduce code duplication.

Author: TalkBridge Team
Date: 2025-01-26
Version: 1.0
"""

import logging
from typing import Any, Dict, List, Optional, Tuple, Union, Literal, Callable

# Try to import customtkinter for UI components
try:
    import customtkinter as ctk
    CUSTOMTKINTER_AVAILABLE = True
except ImportError:
    CUSTOMTKINTER_AVAILABLE = False
    ctk = None

from .theme import ColorPalette, Typography, Spacing, Dimensions
from .controls import create_frame, create_label

logger = logging.getLogger(__name__)

# Type aliases
SideType = Literal["left", "right", "top", "bottom"]
AlignType = Literal["start", "center", "end", "stretch"]

def create_header_layout(
    parent: Any,
    title: str,
    subtitle: Optional[str] = None,
    icon: Optional[str] = None,
    actions: Optional[List[Any]] = None
) -> Optional[Any]:
    """
    Create a standardized header layout with title, optional subtitle, and actions.
    
    Args:
        parent: Parent widget
        title: Main title text
        subtitle: Optional subtitle text
        icon: Optional icon/emoji to display
        actions: Optional list of action widgets (buttons, etc.)
        
    Returns:
        Header frame container or None if creation fails
    """
    if not CUSTOMTKINTER_AVAILABLE:
        logger.warning("CustomTkinter not available, cannot create header layout")
        return None
    
    try:
        # Main header container
        header_frame = create_frame(parent, variant="transparent")
        if header_frame is None:
            return None
            
        header_frame.pack(fill="x", padx=Spacing.LG, pady=(Spacing.LG, Spacing.MD))
        
        # Left side - icon and text
        left_frame = create_frame(header_frame, variant="transparent")
        if left_frame is not None:
            left_frame.pack(side="left", fill="both", expand=True)
            
            # Icon if provided
            if icon:
                icon_label = create_label(left_frame, text=icon, variant="title")
                if icon_label is not None:
                    icon_label.pack(side="left", padx=(0, Spacing.SM))
            
            # Title and subtitle container
            text_frame = create_frame(left_frame, variant="transparent")
            if text_frame is not None:
                text_frame.pack(side="left", fill="both", expand=True)
                
                # Main title
                title_label = create_label(text_frame, text=title, variant="title")
                if title_label is not None:
                    title_label.pack(anchor="w")
                
                # Subtitle if provided
                if subtitle:
                    subtitle_label = create_label(text_frame, text=subtitle, variant="caption")
                    if subtitle_label is not None:
                        subtitle_label.pack(anchor="w")
        
        # Right side - actions
        if actions:
            actions_frame = create_frame(header_frame, variant="transparent")
            if actions_frame is not None:
                actions_frame.pack(side="right")
                
                for action in actions:
                    if action is not None:
                        action.pack(side="left", padx=(Spacing.SM, 0))
        
        return header_frame
        
    except Exception as e:
        logger.error(f"Failed to create header layout: {e}")
        return None

def create_section_layout(
    parent: Any,
    title: str,
    content_widget: Optional[Any] = None,
    collapsible: bool = False
) -> Optional[Tuple[Any, Any]]:
    """
    Create a standardized section layout with title and content area.
    
    Args:
        parent: Parent widget
        title: Section title
        content_widget: Optional widget to place in content area
        collapsible: Whether section can be collapsed
        
    Returns:
        Tuple of (section_frame, content_frame) or None if creation fails
    """
    if not CUSTOMTKINTER_AVAILABLE:
        logger.warning("CustomTkinter not available, cannot create section layout")
        return None
    
    try:
        # Main section container
        section_frame = create_frame(parent, variant="section")
        if section_frame is None:
            return None
            
        section_frame.pack(fill="x", padx=Spacing.LG, pady=Spacing.MD)
        
        # Section header
        header_frame = create_frame(section_frame, variant="transparent")
        if header_frame is not None:
            header_frame.pack(fill="x", padx=Spacing.LG, pady=(Spacing.LG, Spacing.SM))
            
            # Section title
            title_label = create_label(header_frame, text=title, variant="heading")
            if title_label is not None:
                title_label.pack(side="left")
            
            # Collapse button if collapsible
            if collapsible and ctk is not None:
                collapse_btn = ctk.CTkButton(
                    header_frame,
                    text="−",
                    width=30,
                    height=30,
                    fg_color="transparent",
                    text_color=ColorPalette.TEXT_SECONDARY,
                    hover_color=ColorPalette.BACKGROUND_SURFACE
                )
                collapse_btn.pack(side="right")
        
        # Content area
        content_frame = create_frame(section_frame, variant="transparent")
        if content_frame is not None:
            content_frame.pack(fill="both", expand=True, padx=Spacing.LG, pady=(0, Spacing.LG))
            
            # Add provided content widget
            if content_widget is not None:
                content_widget.pack(fill="both", expand=True)
        
        return section_frame, content_frame
        
    except Exception as e:
        logger.error(f"Failed to create section layout: {e}")
        return None

def create_card_layout(
    parent: Any,
    content_widgets: Optional[List[Any]] = None,
    padding: Optional[int] = None
) -> Optional[Any]:
    """
    Create a card-style container layout.
    
    Args:
        parent: Parent widget
        content_widgets: Optional list of widgets to add to card
        padding: Optional custom padding (uses theme default if None)
        
    Returns:
        Card frame container or None if creation fails
    """
    if not CUSTOMTKINTER_AVAILABLE:
        logger.warning("CustomTkinter not available, cannot create card layout")
        return None
    
    try:
        # Main card container
        card_frame = create_frame(parent, variant="card")
        if card_frame is None:
            return None
            
        card_padding = padding if padding is not None else Spacing.LG
        card_frame.pack(fill="x", padx=Spacing.LG, pady=Spacing.MD)
        
        # Content area with padding
        content_frame = create_frame(card_frame, variant="transparent")
        if content_frame is not None:
            content_frame.pack(fill="both", expand=True, padx=card_padding, pady=card_padding)
            
            # Add provided content widgets
            if content_widgets:
                for widget in content_widgets:
                    if widget is not None:
                        widget.pack(fill="x", pady=Spacing.SM)
        
        return card_frame
        
    except Exception as e:
        logger.error(f"Failed to create card layout: {e}")
        return None

def create_button_row(
    parent: Any,
    buttons: List[Dict[str, Any]],
    alignment: AlignType = "end",
    spacing: Optional[int] = None
) -> Optional[Any]:
    """
    Create a row of buttons with consistent spacing and alignment.
    
    Args:
        parent: Parent widget
        buttons: List of button configurations (text, command, variant, etc.)
        alignment: Button alignment ("start", "center", "end", "stretch")
        spacing: Custom spacing between buttons
        
    Returns:
        Button row frame or None if creation fails
    """
    if not CUSTOMTKINTER_AVAILABLE:
        logger.warning("CustomTkinter not available, cannot create button row")
        return None
    
    try:
        from .controls import create_button
        
        # Button row container
        button_frame = create_frame(parent, variant="transparent")
        if button_frame is None:
            return None
            
        button_spacing = spacing if spacing is not None else Spacing.MD
        button_frame.pack(fill="x", padx=Spacing.LG, pady=Spacing.MD)
        
        # Alignment frame
        if alignment == "center":
            align_frame = create_frame(button_frame, variant="transparent")
            if align_frame is not None:
                align_frame.pack(expand=True)
        elif alignment == "end":
            align_frame = create_frame(button_frame, variant="transparent")
            if align_frame is not None:
                align_frame.pack(side="right")
        else:  # start or stretch
            align_frame = button_frame
        
        # Create buttons
        for i, btn_config in enumerate(buttons):
            if align_frame is not None:
                button = create_button(
                    align_frame,
                    text=btn_config.get("text", "Button"),
                    command=btn_config.get("command"),
                    variant=btn_config.get("variant", "primary"),
                    **{k: v for k, v in btn_config.items() if k not in ["text", "command", "variant"]}
                )
                
                if button is not None:
                    if alignment == "stretch":
                        button.pack(side="left", fill="x", expand=True, padx=(0 if i == 0 else button_spacing, 0))
                    else:
                        button.pack(side="left", padx=(0 if i == 0 else button_spacing, 0))
        
        return button_frame
        
    except Exception as e:
        logger.error(f"Failed to create button row: {e}")
        return None

def create_form_row(
    parent: Any,
    label_text: str,
    input_widget: Any,
    help_text: Optional[str] = None,
    required: bool = False
) -> Optional[Any]:
    """
    Create a standardized form row with label, input, and optional help text.
    
    Args:
        parent: Parent widget
        label_text: Label text for the input
        input_widget: Input widget (entry, combobox, etc.)
        help_text: Optional help/description text
        required: Whether field is required (shows indicator)
        
    Returns:
        Form row frame or None if creation fails
    """
    if not CUSTOMTKINTER_AVAILABLE:
        logger.warning("CustomTkinter not available, cannot create form row")
        return None
    
    try:
        # Main row container
        row_frame = create_frame(parent, variant="transparent")
        if row_frame is None:
            return None
            
        row_frame.pack(fill="x", pady=Spacing.SM)
        
        # Label
        label_text_full = f"{label_text} *" if required else label_text
        label = create_label(row_frame, text=label_text_full, variant="body")
        if label is not None:
            label.pack(anchor="w", pady=(0, Spacing.XS))
        
        # Input widget
        if input_widget is not None:
            input_widget.pack(fill="x", pady=(0, Spacing.XS))
        
        # Help text
        if help_text:
            help_label = create_label(row_frame, text=help_text, variant="hint")
            if help_label is not None:
                help_label.pack(anchor="w")
        
        return row_frame
        
    except Exception as e:
        logger.error(f"Failed to create form row: {e}")
        return None

def setup_auth_dialog_layout(dialog_window: Any, content_dict: Dict[str, Any]) -> Optional[Dict[str, Any]]:
    """
    Set up a complete authentication dialog layout with all sections.
    
    Args:
        dialog_window: The dialog window widget
        content_dict: Dictionary containing dialog content configuration:
            - app_name: Application name for header
            - app_subtitle: Application subtitle  
            - logo_text: Logo text/icon
            - form_title: Form section title
            - username_label: Username field label
            - password_label: Password field label
            - remember_text: Remember me checkbox text
            - login_text: Login button text
            - cancel_text: Cancel button text
            - status_text: Initial status text
            
    Returns:
        Dictionary containing references to created UI elements, or None if failed
    """
    if not CUSTOMTKINTER_AVAILABLE or not dialog_window:
        return None
        
    try:
        # Main container with margins
        main_frame = create_frame(dialog_window, variant="transparent")
        if not main_frame:
            return None
        main_frame.pack(fill="both", expand=True, padx=Spacing.MARGIN_MAIN, pady=Spacing.MARGIN_MAIN)
        
        # Create sections
        ui_elements = {}
        
        # Header section
        header_elements = create_auth_header_section(main_frame, content_dict)
        if header_elements:
            ui_elements.update(header_elements)
        
        # Form section  
        form_elements = create_auth_form_section(main_frame, content_dict)
        if form_elements:
            ui_elements.update(form_elements)
            
        # Status section
        status_elements = create_auth_status_section(main_frame, content_dict)
        if status_elements:
            ui_elements.update(status_elements)
        
        ui_elements['main_frame'] = main_frame
        logger.debug("Successfully set up authentication dialog layout")
        return ui_elements
        
    except Exception as e:
        logger.error(f"Failed to setup auth dialog layout: {e}")
        return None

def create_auth_header_section(parent: Any, content_dict: Dict[str, Any]) -> Optional[Dict[str, Any]]:
    """
    Create the header section for authentication dialogs.
    
    Args:
        parent: Parent widget
        content_dict: Content configuration dictionary
        
    Returns:
        Dictionary with header UI element references
    """
    if not CUSTOMTKINTER_AVAILABLE:
        return None
        
    try:
        # Header container
        header_frame = create_frame(parent, variant="transparent")
        if not header_frame:
            return None
        header_frame.pack(fill="x", pady=(0, Spacing.LG))
        
        # Logo/icon
        logo_text = content_dict.get('logo_text', 'AI')
        logo_label = create_label(
            header_frame,
            text=logo_text,
            variant="default"
        )
        if logo_label and ctk:
            logo_label.configure(
                font=ctk.CTkFont(size=40, weight="bold"),
                text_color=ColorPalette.ACCENT_PRIMARY
            )
            logo_label.pack(pady=(0, Spacing.SM))
        
        # Main title
        app_name = content_dict.get('app_name', 'TalkBridge Desktop')
        title_label = create_label(
            header_frame,
            text=app_name,
            variant="heading"
        )
        if title_label and ctk:
            title_label.configure(
                font=ctk.CTkFont(size=Typography.FONT_SIZE_H1, weight="bold"),
                text_color=ColorPalette.TEXT_PRIMARY
            )
            title_label.pack()
        
        # Subtitle
        app_subtitle = content_dict.get('app_subtitle', 'AI-Powered Communication Platform')
        subtitle_label = create_label(
            header_frame,
            text=app_subtitle,
            variant="caption"
        )
        if subtitle_label and ctk:
            subtitle_label.configure(
                font=ctk.CTkFont(size=Typography.FONT_SIZE_CAPTION),
                text_color=ColorPalette.TEXT_SECONDARY
            )
            subtitle_label.pack(pady=(3, 0))
        
        return {
            'header_frame': header_frame,
            'logo_label': logo_label,
            'title_label': title_label,
            'subtitle_label': subtitle_label
        }
        
    except Exception as e:
        logger.error(f"Failed to create auth header section: {e}")
        return None

def create_auth_form_section(parent: Any, content_dict: Dict[str, Any]) -> Optional[Dict[str, Any]]:
    """
    Create the form section for authentication dialogs.
    
    Args:
        parent: Parent widget
        content_dict: Content configuration dictionary
        
    Returns:
        Dictionary with form UI element references
    """
    if not CUSTOMTKINTER_AVAILABLE:
        return None
        
    try:
        from .controls import create_auth_form_frame, create_entry, create_password_field_with_toggle, create_checkbox, create_dialog_button_set
        import tkinter as tk
        
        # Form container
        form_frame = create_auth_form_frame(parent)
        if not form_frame:
            return None
        form_frame.pack(fill="x", pady=Spacing.LG)
        
        # Form content with padding
        form_content = create_frame(form_frame, variant="transparent")
        if not form_content:
            return None
        form_content.pack(fill="both", expand=True, padx=25, pady=20)
        
        # Form title
        form_title = content_dict.get('form_title', 'Sign In')
        form_title_label = create_label(
            form_content,
            text=form_title,
            variant="heading"
        )
        if form_title_label and ctk:
            form_title_label.configure(
                font=ctk.CTkFont(size=16, weight="bold"),
                text_color=ColorPalette.TEXT_PRIMARY
            )
            form_title_label.pack(pady=(0, 15))
        
        # Initialize variables
        username_frame = None
        username_label = None
        username_entry = None
        password_frame = None
        password_label = None
        password_entry = None
        password_toggle = None
        password_container = None
        options_frame = None
        remember_var = None
        remember_checkbox = None
        
        # Username field
        username_label_text = content_dict.get('username_label', 'Username:')
        username_frame = create_frame(form_content, variant="transparent")
        if username_frame:
            username_frame.pack(fill="x", pady=(0, Spacing.MD))
            
            username_label = create_label(username_frame, text=username_label_text, variant="caption")
            if username_label:
                username_label.pack(anchor="w", pady=(0, 4))
            
            username_entry = create_entry(
                username_frame, 
                placeholder_text="Enter your username"
            )
            if username_entry:
                username_entry.pack(fill="x")
        
        # Password field with toggle
        password_label_text = content_dict.get('password_label', 'Password:')
        password_frame = create_frame(form_content, variant="transparent")
        if password_frame:
            password_frame.pack(fill="x", pady=(0, Spacing.MD))
            
            password_label = create_label(password_frame, text=password_label_text, variant="caption")
            if password_label:
                password_label.pack(anchor="w", pady=(0, 4))
            
            password_entry, password_toggle, password_container = create_password_field_with_toggle(
                password_frame,
                placeholder="Enter your password"
            )
            if password_container:
                password_container.pack(fill="x")
        
        # Options section (Remember me)
        options_frame = create_frame(form_content, variant="transparent")
        if options_frame:
            options_frame.pack(fill="x", pady=(0, Spacing.MD))
            
            remember_var = tk.BooleanVar()
            remember_text = content_dict.get('remember_text', 'Remember me')
            remember_checkbox = create_checkbox(
                options_frame,
                text=remember_text,
                variable=remember_var
            )
            if remember_checkbox:
                remember_checkbox.pack(anchor="w")
        
        # Buttons section
        login_text = content_dict.get('login_text', 'Sign In')
        cancel_text = content_dict.get('cancel_text', 'Cancel')
        login_button, cancel_button, button_container = create_dialog_button_set(
            form_content,
            primary_text=login_text,
            secondary_text=cancel_text
        )
        if button_container:
            button_container.pack(fill="x", pady=(Spacing.MD, 0))
        
        return {
            'form_frame': form_frame,
            'form_content': form_content,
            'form_title_label': form_title_label,
            'username_frame': username_frame,
            'username_label': username_label,
            'username_entry': username_entry,
            'password_frame': password_frame,
            'password_label': password_label,
            'password_entry': password_entry,
            'password_toggle': password_toggle,
            'password_container': password_container,
            'options_frame': options_frame,
            'remember_checkbox': remember_checkbox,
            'remember_var': remember_var,
            'login_button': login_button,
            'cancel_button': cancel_button,
            'button_container': button_container
        }
        
    except Exception as e:
        logger.error(f"Failed to create auth form section: {e}")
        return None

def create_auth_status_section(parent: Any, content_dict: Dict[str, Any]) -> Optional[Dict[str, Any]]:
    """
    Create the status section for authentication dialogs.
    
    Args:
        parent: Parent widget
        content_dict: Content configuration dictionary
        
    Returns:
        Dictionary with status UI element references
    """
    if not CUSTOMTKINTER_AVAILABLE:
        return None
        
    try:
        from .controls import create_status_indicator
        
        # Status container
        status_frame = create_frame(parent, variant="transparent")
        if not status_frame:
            return None
        status_frame.pack(fill="x", pady=Spacing.LG)
        
        # Status indicator
        initial_status = content_dict.get('status_text', 'Ready to sign in')
        status_label = create_status_indicator(status_frame, initial_text=initial_status)
        if status_label:
            status_label.pack()
        
        return {
            'status_frame': status_frame,
            'status_label': status_label
        }
        
    except Exception as e:
        logger.error(f"Failed to create auth status section: {e}")
        return None

def setup_confirmation_dialog_layout(dialog: Any, content_frame: Any) -> None:
    """Set up the standardized layout for confirmation dialogs.
    
    Args:
        dialog: The dialog window
        content_frame: The main content frame
    """
    if not dialog or not content_frame:
        logger.warning("Cannot setup confirmation dialog layout - invalid parameters")
        return
    
    try:
        # Configure content frame to fill dialog
        content_frame.pack(fill="both", expand=True, padx=Spacing.LG, pady=Spacing.LG)
        
        # Apply responsive behavior if dialog window supports it
        if hasattr(dialog, 'grid_rowconfigure'):
            dialog.grid_rowconfigure(0, weight=1)
            dialog.grid_columnconfigure(0, weight=1)
        
        logger.debug("Applied confirmation dialog layout")
    except Exception as e:
        logger.error(f"Failed to setup confirmation dialog layout: {e}")

def create_warning_header(parent: Any, title: str = "Warning", icon: str = "⚠️", 
                         icon_color: Optional[str] = None) -> Any:
    """Create a warning header section for confirmation dialogs.
    
    Args:
        parent: Parent widget
        title: Header title text
        icon: Warning icon (emoji or character)
        icon_color: Icon color (uses warning theme if None)
        
    Returns:
        Header frame containing icon and title
    """
    if not CUSTOMTKINTER_AVAILABLE:
        return None
    
    try:
        from .controls import create_frame, create_label, create_icon_label
        
        # Header container
        header_frame = create_frame(parent, variant="transparent")
        if not header_frame:
            return None
        
        # Icon
        icon_label = create_icon_label(
            header_frame,
            icon_text=icon,
            icon_size=32,
            color=icon_color or ColorPalette.WARNING
        )
        if icon_label:
            icon_label.pack(side="top", pady=(0, Spacing.SM))
        
        # Title  
        title_label = create_label(
            header_frame,
            text=title,
            variant="heading",
            font_size=18
        )
        if title_label:
            title_label.pack(side="top")
        
        logger.debug(f"Created warning header: '{title}'")
        return header_frame
    except Exception as e:
        logger.error(f"Failed to create warning header: {e}")
        return None

def create_message_body(parent: Any, message: str, font_size: int = 12,
                       text_color: Optional[str] = None, alignment: str = "center") -> Any:
    """Create a message body section for confirmation dialogs.
    
    Args:
        parent: Parent widget
        message: Message text to display
        font_size: Font size for message text
        text_color: Text color (uses theme default if None)
        alignment: Text alignment ("center", "left", "right")
        
    Returns:
        Label widget containing the message
    """
    if not CUSTOMTKINTER_AVAILABLE:
        return None
    
    try:
        from .controls import create_label
        
        message_label = create_label(
            parent,
            text=message,
            font_size=font_size,
            text_color=text_color or ColorPalette.TEXT_PRIMARY,
            justify=alignment,
            wraplength=300  # Wrap long messages
        )
        
        if message_label:
            logger.debug(f"Created message body with {len(message)} characters")
        
        return message_label
    except Exception as e:
        logger.error(f"Failed to create message body: {e}")
        return None

def create_confirmation_buttons_layout(parent: Any, confirm_text: str = "Yes", 
                                     cancel_text: str = "No", 
                                     confirm_command: Optional[Callable] = None,
                                     cancel_command: Optional[Callable] = None) -> tuple:
    """Create and layout confirmation buttons section.
    
    Args:
        parent: Parent widget
        confirm_text: Text for confirmation button
        cancel_text: Text for cancel button
        confirm_command: Command for confirmation button
        cancel_command: Command for cancel button
        
    Returns:
        Tuple of (confirm_button, cancel_button, button_container)
    """
    if not CUSTOMTKINTER_AVAILABLE:
        return None, None, None
    
    try:
        from .controls import create_frame, create_confirmation_button_set
        
        # Button container with proper spacing
        button_frame = create_frame(parent, variant="transparent")
        if not button_frame:
            return None, None, None
        
        # Create button set
        confirm_btn, cancel_btn, btn_container = create_confirmation_button_set(
            button_frame,
            confirm_text=confirm_text,
            cancel_text=cancel_text,
            confirm_command=confirm_command,
            cancel_command=cancel_command
        )
        
        if btn_container:
            btn_container.pack(pady=(Spacing.LG, 0))
        
        logger.debug(f"Created confirmation buttons layout")
        return confirm_btn, cancel_btn, button_frame
    except Exception as e:
        logger.error(f"Failed to create confirmation buttons layout: {e}")
        return None, None, None

# Export layout functions
__all__ = [
    "create_header_layout",
    "create_section_layout", 
    "create_card_layout",
    "create_button_row",
    "create_form_row",
    "setup_auth_dialog_layout",
    "create_auth_header_section",
    "create_auth_form_section", 
    "create_auth_status_section",
    "setup_confirmation_dialog_layout",
    "create_warning_header",
    "create_message_body",
    "create_confirmation_buttons_layout"
]