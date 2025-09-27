#!/usr/bin/env python3
"""
TalkBridge Desktop - Logout Dialog (Centralized UI)
===================================================

Logout confirmation dialog using centralized UI components for consistent
styling and maintainability.

Author: TalkBridge Team  
Date: 2025-01-26
Version: 3.0 (Centralized)

Features:
- Uses centralized ConfirmationDialog widget
- Consistent theme-based styling
- Proper error handling and logging
- Maintainable through centralized components
======================================================================
"""

import logging
from typing import Optional, Any

# Import centralized UI components
try:
    from ..ui.widgets import ConfirmationDialog
    from ..ui.theme import ColorPalette
    CENTRALIZED_UI_AVAILABLE = True
except ImportError as e:
    logging.warning(f"Could not import centralized UI components: {e}")
    # Create dummy classes for type hints
    ConfirmationDialog = None
    ColorPalette = None
    CENTRALIZED_UI_AVAILABLE = False

class LogoutDialog:
    """
    Logout confirmation dialog using centralized UI components.
    
    This dialog provides a consistent confirmation interface that follows
    the established design system. It uses the ConfirmationDialog widget
    for standardized appearance and behavior.
    
    Features:
    - Centralized theme-based styling  
    - Consistent confirmation workflow
    - Proper error handling and logging
    - Warning icon with appropriate colors
    - Maintains backward compatibility
    
    Usage:
        dialog = LogoutDialog(parent_window)
        if dialog.show():
            # User confirmed logout
            perform_logout_actions()
        else:
            # User cancelled or closed dialog
            logger.info("Logout cancelled")
    """

    def __init__(self, parent: Any):
        """Initialize the logout dialog.
        
        Args:
            parent: Parent window widget (CTk instance or compatible)
        """
        self.parent = parent
        self.logger = logging.getLogger("talkbridge.desktop.logout")
        
        # Dialog configuration
        self.title = "Logout Confirmation"
        self.message = "Are you sure you want to logout?\nAll unsaved changes will be lost."
        self.icon = "⚠️"
        self.confirm_text = "Logout"
        self.cancel_text = "Cancel"
        
        # State tracking
        self.result = False
        
        self.logger.debug("Initialized LogoutDialog with centralized components")

    def show(self) -> bool:
        """
        Show the logout confirmation dialog and return user choice.
        
        Returns:
            bool: True if user confirmed logout, False if cancelled or error occurred
        """
        self.logger.info("Showing logout confirmation dialog")
        
        if not CENTRALIZED_UI_AVAILABLE:
            self.logger.error("Centralized UI components not available - falling back to basic dialog")
            return self._show_fallback_dialog()
        
        try:
            # Create centralized confirmation dialog
            if ConfirmationDialog is not None and ColorPalette is not None:
                dialog = ConfirmationDialog(
                    parent=self.parent,
                    title=self.title,
                    message=self.message,
                    confirm_text=self.confirm_text,
                    cancel_text=self.cancel_text,
                    icon=self.icon,
                    icon_color=ColorPalette.WARNING,  # Use theme warning color
                    dialog_width=400,
                    dialog_height=200
                )
            else:
                raise ImportError("ConfirmationDialog or ColorPalette not available")
            
            # Show dialog and get result
            result = dialog.show()
            
            # Handle result (True/False/None)
            if result is True:
                self.logger.info("User confirmed logout")
                self.result = True
                return True
            elif result is False:
                self.logger.info("User cancelled logout")
                self.result = False
                return False
            else:
                # None indicates dialog was closed without decision
                self.logger.info("Logout dialog closed without decision")
                self.result = False
                return False
                
        except Exception as e:
            self.logger.error(f"Failed to show centralized logout dialog: {e}")
            return self._show_fallback_dialog()

    def _show_fallback_dialog(self) -> bool:
        """
        Fallback dialog implementation for when centralized components fail.
        
        This maintains backward compatibility by providing a basic dialog
        when the centralized UI system is unavailable.
        
        Returns:
            bool: True if user confirmed, False otherwise
        """
        self.logger.warning("Using fallback dialog implementation")
        
        try:
            import tkinter as tk
            from tkinter import messagebox
            
            # Simple messagebox fallback
            result = messagebox.askyesno(
                title=self.title,
                message=self.message,
                icon="warning"
            )
            
            self.result = bool(result)
            self.logger.info(f"Fallback dialog result: {self.result}")
            return self.result
            
        except Exception as e:
            self.logger.error(f"Fallback dialog failed: {e}")
            # Ultimate fallback - assume user wants to cancel
            self.result = False
            return False