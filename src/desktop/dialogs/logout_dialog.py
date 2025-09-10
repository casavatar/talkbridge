#!/usr/bin/env python3
"""
TalkBridge Desktop - Logout Dialog (CustomTkinter)
==================================================

Simple logout confirmation dialog with CustomTkinter styling.

Author: TalkBridge Team
Date: 2025-09-03
Version: 2.0

Requirements:
- customtkinter
- tkinter
======================================================================
"""

import logging
import customtkinter as ctk
import tkinter as tk
from typing import Optional


class LogoutDialog:
    """
    Simple logout confirmation dialog.
    
    Features:
    - Modern CustomTkinter styling
    - Clear confirmation message
    - Yes/No options with appropriate styling
    """

    def __init__(self, parent: ctk.CTk):
        """Initialize the logout dialog."""
        self.parent = parent
        self.logger = logging.getLogger("talkbridge.desktop.logout")
        
        # Dialog state
        self.result = False
        self.dialog: Optional[ctk.CTkToplevel] = None

    def show(self) -> bool:
        """
        Show the logout dialog and return user choice.
        
        Returns:
            bool: True if user confirmed logout, False otherwise
        """
        self.logger.info("Showing logout confirmation dialog")
        
        # Create dialog window
        self.dialog = ctk.CTkToplevel(self.parent)
        self.dialog.title("Logout Confirmation")
        self.dialog.geometry("400x200")
        self.dialog.resizable(False, False)
        
        # Center on parent
        self._center_dialog()
        
        # Configure dialog
        self.dialog.configure(fg_color="#1e1e1e")
        self.dialog.transient(self.parent)
        self.dialog.grab_set()
        
        # Setup UI
        self._setup_ui()
        
        # Focus on dialog
        self.dialog.focus()
        
        # Wait for dialog to close
        self.dialog.wait_window()
        
        return self.result

    def _setup_ui(self):
        """Set up the dialog UI."""
        # Main container
        main_frame = ctk.CTkFrame(self.dialog, fg_color="transparent")
        main_frame.pack(fill="both", expand=True, padx=20, pady=20)
        
        # Icon and title
        title_frame = ctk.CTkFrame(main_frame, fg_color="transparent")
        title_frame.pack(fill="x", pady=(0, 20))
        
        # Warning icon
        icon_label = ctk.CTkLabel(
            title_frame,
            text="⚠️",
            font=ctk.CTkFont(size=32),
            text_color="#ff9800"
        )
        icon_label.pack(pady=(0, 10))
        
        # Title
        title_label = ctk.CTkLabel(
            title_frame,
            text="Logout Confirmation",
            font=ctk.CTkFont(size=18, weight="bold"),
            text_color="#ffffff"
        )
        title_label.pack()
        
        # Message
        message_label = ctk.CTkLabel(
            main_frame,
            text="Are you sure you want to logout?\nAll unsaved changes will be lost.",
            font=ctk.CTkFont(size=12),
            text_color="#cccccc",
            justify="center"
        )
        message_label.pack(pady=(0, 30))
        
        # Buttons
        button_frame = ctk.CTkFrame(main_frame, fg_color="transparent")
        button_frame.pack(fill="x")
        
        # Cancel button
        cancel_button = ctk.CTkButton(
            button_frame,
            text="Cancel",
            width=120,
            height=35,
            fg_color="transparent",
            text_color="#ffffff",
            border_width=2,
            border_color="#555555",
            hover_color="#3c3c3c",
            font=ctk.CTkFont(size=12, weight="bold"),
            command=self._cancel
        )
        cancel_button.pack(side="left", padx=(0, 10))
        
        # Logout button
        logout_button = ctk.CTkButton(
            button_frame,
            text="Logout",
            width=120,
            height=35,
            fg_color="#f44336",
            hover_color="#d32f2f",
            font=ctk.CTkFont(size=12, weight="bold"),
            command=self._confirm
        )
        logout_button.pack(side="right")
        
        # Focus on cancel button by default
        cancel_button.focus()

    def _center_dialog(self):
        """Center the dialog on its parent window."""
        if self.parent:
            parent_x = self.parent.winfo_x()
            parent_y = self.parent.winfo_y()
            parent_width = self.parent.winfo_width()
            parent_height = self.parent.winfo_height()
            
            dialog_x = parent_x + (parent_width - 400) // 2
            dialog_y = parent_y + (parent_height - 200) // 2
            
            self.dialog.geometry(f"400x200+{dialog_x}+{dialog_y}")

    def _confirm(self):
        """Handle logout confirmation."""
        self.result = True
        self.dialog.destroy()

    def _cancel(self):
        """Handle logout cancellation."""
        self.result = False
        self.dialog.destroy()
