#!/usr/bin/env python3
"""
TalkBridge Desktop - Login Dialog (Refactored)
==============================================

Modernized login dialog using centralized UI system for consistent styling and maintainable code.

Author: TalkBridge Team
Date: 2025-01-26
Version: 3.0

Features:
- Uses centralized UI factory functions and widgets
- Consistent with application-wide theming
- Simplified codebase with proper separation of concerns
- Maintains all original functionality while eliminating hardcoded styling
======================================================================
"""

import logging
from typing import Optional, Tuple
from enum import Enum
from dataclasses import dataclass

# Import centralized UI system
try:
    from ..ui.widgets import AuthenticationDialog
    UI_SYSTEM_AVAILABLE = True
except ImportError:
    UI_SYSTEM_AVAILABLE = False
    AuthenticationDialog = None

# Import legacy CustomTkinter for fallback compatibility
try:
    import customtkinter as ctk
    import tkinter as tk
    CUSTOMTKINTER_AVAILABLE = True
except ImportError:
    CUSTOMTKINTER_AVAILABLE = False
    ctk = None
    tk = None

# Maintain backward compatibility with existing types
class AuthenticationState(Enum):
    """Authentication process states."""
    IDLE = "idle"
    AUTHENTICATING = "authenticating"
    SUCCESS = "success"
    FAILED = "failed"
    TIMEOUT = "timeout"
    CANCELLED = "cancelled"

@dataclass
class AuthenticationResult:
    """Container for authentication results."""
    success: bool
    user_data: Optional[dict] = None
    message: str = ""
    state: AuthenticationState = AuthenticationState.IDLE

class LoginDialog:
    """
    Enhanced login dialog for TalkBridge Desktop application.
    
    This refactored version uses the centralized UI system while maintaining
    full backward compatibility with the original interface.
    """

    def __init__(self, parent):
        """Initialize the login dialog with centralized UI system."""
        self.parent = parent
        self.logger = logging.getLogger("src.desktop.login")
        
        # Dialog state (maintaining original interface)
        self.result = False
        self.username = ""
        self.password = ""
        
        # Use centralized authentication dialog if available
        if UI_SYSTEM_AVAILABLE and AuthenticationDialog:
            self.auth_dialog = AuthenticationDialog(parent, "TalkBridge - Login")
            self.logger.info("Using centralized authentication dialog")
        else:
            self.auth_dialog = None
            self.logger.warning("Centralized UI system not available, falling back to legacy implementation")

    def show(self) -> Tuple[bool, str, str]:
        """
        Show the login dialog and return authentication result.
        
        Returns:
            Tuple[bool, str, str]: (success, username, password)
        """
        self.logger.info("Showing login dialog")
        
        try:
            if self.auth_dialog:
                # Use centralized authentication dialog
                success, username, password = self.auth_dialog.show()
                
                # Update instance state for backward compatibility
                self.result = success
                self.username = username
                self.password = password
                
                return success, username, password
            else:
                # Fallback to simple implementation if centralized system unavailable
                return self._show_fallback_dialog()
                
        except Exception as e:
            self.logger.error(f"Error showing login dialog: {e}")
            return False, "", ""

    def _show_fallback_dialog(self) -> Tuple[bool, str, str]:
        """
        Fallback implementation when centralized UI system is not available.
        
        Returns:
            Tuple[bool, str, str]: (success, username, password)
        """
        if not CUSTOMTKINTER_AVAILABLE:
            self.logger.error("Neither centralized UI system nor CustomTkinter available")
            return False, "", ""
        
        self.logger.info("Using fallback login dialog implementation")
        
        try:
            # Create simple dialog window
            if not ctk:
                self.logger.error("CustomTkinter not available")
                return False, "", ""
            
            dialog = ctk.CTkToplevel(self.parent)
            dialog.title("TalkBridge - Login")
            dialog.geometry("400x300")
            dialog.resizable(False, False)
            
            # Center dialog
            if self.parent and hasattr(self.parent, 'winfo_exists') and self.parent.winfo_exists():
                dialog.transient(self.parent)
                parent_x = self.parent.winfo_x()
                parent_y = self.parent.winfo_y()
                parent_width = self.parent.winfo_width()
                parent_height = self.parent.winfo_height()
                
                dialog_x = parent_x + (parent_width - 400) // 2
                dialog_y = parent_y + (parent_height - 300) // 2
                dialog.geometry(f"400x300+{dialog_x}+{dialog_y}")
            
            # Create simple form
            main_frame = ctk.CTkFrame(dialog)
            main_frame.pack(fill="both", expand=True, padx=20, pady=20)
            
            # Title
            title_label = ctk.CTkLabel(
                main_frame, 
                text="TalkBridge Login", 
                font=ctk.CTkFont(size=18, weight="bold")
            )
            title_label.pack(pady=(0, 20))
            
            # Username field
            username_label = ctk.CTkLabel(main_frame, text="Username:")
            username_label.pack(anchor="w", pady=(0, 5))
            
            username_entry = ctk.CTkEntry(main_frame, placeholder_text="Enter username")
            username_entry.pack(fill="x", pady=(0, 15))
            
            # Password field
            password_label = ctk.CTkLabel(main_frame, text="Password:")
            password_label.pack(anchor="w", pady=(0, 5))
            
            password_entry = ctk.CTkEntry(main_frame, placeholder_text="Enter password", show="*")
            password_entry.pack(fill="x", pady=(0, 20))
            
            # Status label
            status_label = ctk.CTkLabel(main_frame, text="", text_color="#ff6b6b")
            status_label.pack(pady=(0, 15))
            
            # Button frame
            button_frame = ctk.CTkFrame(main_frame, fg_color="transparent")
            button_frame.pack(fill="x")
            
            # Result storage
            dialog_result = {"success": False, "username": "", "password": ""}
            
            def validate_and_login():
                username = username_entry.get().strip()
                password = password_entry.get().strip()
                
                if len(username) < 3:
                    status_label.configure(text="Username must be at least 3 characters")
                    return
                
                if len(password) < 1:
                    status_label.configure(text="Password is required")
                    return
                
                # Simple validation (in real implementation, use auth manager)
                dialog_result["success"] = True
                dialog_result["username"] = username
                dialog_result["password"] = password
                
                dialog.destroy()
            
            def cancel_login():
                dialog_result["success"] = False
                dialog.destroy()
            
            # Login button
            login_button = ctk.CTkButton(
                button_frame, 
                text="Login", 
                command=validate_and_login
            )
            login_button.pack(side="left", fill="x", expand=True, padx=(0, 10))
            
            # Cancel button
            cancel_button = ctk.CTkButton(
                button_frame, 
                text="Cancel", 
                command=cancel_login,
                fg_color="transparent",
                border_width=1
            )
            cancel_button.pack(side="right", fill="x", expand=True, padx=(10, 0))
            
            # Bind Enter key to login
            username_entry.bind("<Return>", lambda e: validate_and_login())
            password_entry.bind("<Return>", lambda e: validate_and_login())
            
            # Set focus and show dialog
            username_entry.focus()
            dialog.deiconify()
            dialog.grab_set()
            dialog.wait_window()
            
            # Update instance state
            self.result = dialog_result["success"]
            self.username = dialog_result["username"]
            self.password = dialog_result["password"]
            
            return dialog_result["success"], dialog_result["username"], dialog_result["password"]
            
        except Exception as e:
            self.logger.error(f"Error in fallback dialog: {e}")
            return False, "", ""

    # Maintain backward compatibility methods
    def get_credentials(self) -> Tuple[str, str]:
        """
        Gets the entered credentials.
        
        Returns:
            Tuple of (username, password)
        """
        return self.username, self.password

    def should_remember(self) -> bool:
        """
        Checks if credentials should be remembered.
        
        Returns:
            True if remember checkbox is checked (always False in refactored version)
        """
        # In the centralized system, this would be handled by the AuthenticationDialog
        if self.auth_dialog and hasattr(self.auth_dialog, 'remember_credentials'):
            return self.auth_dialog.remember_credentials
        return False

# Maintain full backward compatibility
__all__ = ["LoginDialog", "AuthenticationState", "AuthenticationResult"]