"""
Status utilities for TalkBridge

Provides centralized status update functionality for UI components.
"""

import logging
from typing import Optional, Union
from enum import Enum

try:
    import customtkinter as ctk
    CUSTOMTKINTER_AVAILABLE = True
except ImportError:
    ctk = None  # type: ignore
    CUSTOMTKINTER_AVAILABLE = False

try:
    import tkinter as tk
    TKINTER_AVAILABLE = True
except ImportError:
    tk = None  # type: ignore
    TKINTER_AVAILABLE = False


class StatusLevel(Enum):
    """Status level enumeration for consistent status indication."""
    INFO = "info"
    SUCCESS = "success"
    WARNING = "warning"
    ERROR = "error"


class StatusColors:
    """Color constants for different status levels."""
    INFO = "#2196F3"      # Blue
    SUCCESS = "#4CAF50"   # Green
    WARNING = "#FF9800"   # Orange
    ERROR = "#f44336"     # Red
    SECONDARY = "#757575" # Gray


def update_status(label: Union[str, object], 
                 text: str, 
                 level: StatusLevel = StatusLevel.INFO,
                 color: Optional[str] = None) -> None:
    """
    Update status for various UI label types with consistent styling.
    
    Args:
        label: The label widget to update (supports tkinter.Label, customtkinter widgets, or logger name)
        text: Status text to display
        level: Status level (info, success, warning, error)
        color: Custom color override (optional)
    """
    # Determine color based on level if not explicitly provided
    if color is None:
        color_map = {
            StatusLevel.INFO: StatusColors.INFO,
            StatusLevel.SUCCESS: StatusColors.SUCCESS,
            StatusLevel.WARNING: StatusColors.WARNING,
            StatusLevel.ERROR: StatusColors.ERROR
        }
        color = color_map.get(level, StatusColors.INFO)
    
    # Handle string input as logger name
    if isinstance(label, str):
        logger = logging.getLogger(label)
        log_method_map = {
            StatusLevel.INFO: logger.info,
            StatusLevel.SUCCESS: logger.info,
            StatusLevel.WARNING: logger.warning,
            StatusLevel.ERROR: logger.error
        }
        log_method_map.get(level, logger.info)(text)
        return
    
    # Handle different widget types
    try:
        # Try customtkinter first
        if hasattr(label, 'configure') and hasattr(label, 'cget'):
            if CUSTOMTKINTER_AVAILABLE and ctk is not None and isinstance(label, (ctk.CTkLabel, ctk.CTkButton)):
                _update_customtkinter_widget(label, text, color)
            elif TKINTER_AVAILABLE and hasattr(label, 'config'):
                _update_tkinter_widget(label, text, color)
            else:
                # Generic widget with configure method - add type checking
                if hasattr(label, 'configure'):
                    label.configure(text=text)  # type: ignore
        else:
            # Fallback to string representation
            logging.getLogger("talkbridge.status").info(f"Status update: {text}")
            
    except Exception as e:
        # Fallback logging if widget update fails
        logger = logging.getLogger("talkbridge.status")
        logger.warning(f"Failed to update status widget: {e}")
        logger.info(f"Status: {text}")


def _update_customtkinter_widget(widget, text: str, color: str) -> None:
    """Update customtkinter widget with status."""
    try:
        # For customtkinter widgets, use text_color parameter
        if hasattr(widget, 'configure'):
            widget.configure(text=text, text_color=color)
        else:
            widget.configure(text=text)
    except Exception as e:
        logging.getLogger("talkbridge.status").debug(f"CustomTkinter widget update failed: {e}")
        widget.configure(text=text)


def _update_tkinter_widget(widget, text: str, color: str) -> None:
    """Update standard tkinter widget with status."""
    try:
        # For standard tkinter widgets, use fg parameter
        if hasattr(widget, 'config'):
            widget.config(text=text, fg=color)
        else:
            widget.configure(text=text)
    except Exception as e:
        logging.getLogger("talkbridge.status").debug(f"Tkinter widget update failed: {e}")
        widget.configure(text=text)


def update_connection_status(widget, connected: bool) -> None:
    """
    Update connection status indicator with standard styling.
    
    Args:
        widget: The widget to update
        connected: Connection state
    """
    if connected:
        update_status(widget, "🟢 Connected", StatusLevel.SUCCESS)
    else:
        update_status(widget, "🔴 Disconnected", StatusLevel.ERROR)


def set_status(label, text: str, level: str = "info") -> None:
    """
    Legacy wrapper for update_status to maintain backward compatibility.
    
    Args:
        label: The label widget to update
        text: Status text to display
        level: Status level string ("info", "success", "warning", "error")
    """
    try:
        status_level = StatusLevel(level.lower())
    except ValueError:
        status_level = StatusLevel.INFO
    
    update_status(label, text, status_level)


def create_status_label(parent, initial_text: str = "Ready", **kwargs):
    """
    Create a standardized status label widget.
    
    Args:
        parent: Parent widget
        initial_text: Initial status text
        **kwargs: Additional widget creation arguments
        
    Returns:
        Status label widget
    """
    default_kwargs = {
        'text': initial_text,
        'anchor': 'w',
        'width': 300
    }
    default_kwargs.update(kwargs)
    
    if CUSTOMTKINTER_AVAILABLE and ctk is not None:
        return ctk.CTkLabel(parent, **default_kwargs)
    elif TKINTER_AVAILABLE and tk is not None:
        # Convert customtkinter args to tkinter args
        tk_kwargs = {
            'text': default_kwargs.get('text', initial_text),
            'anchor': default_kwargs.get('anchor', 'w'),
            'width': default_kwargs.get('width', 300)
        }
        return tk.Label(parent, **tk_kwargs)
    else:
        raise ImportError("Neither tkinter nor customtkinter is available")


# Convenience functions for common status levels
def status_info(label, text: str) -> None:
    """Set info status."""
    update_status(label, text, StatusLevel.INFO)


def status_success(label, text: str) -> None:
    """Set success status."""
    update_status(label, text, StatusLevel.SUCCESS)


def status_warning(label, text: str) -> None:
    """Set warning status."""
    update_status(label, text, StatusLevel.WARNING)


def status_error(label, text: str) -> None:
    """Set error status."""
    update_status(label, text, StatusLevel.ERROR)