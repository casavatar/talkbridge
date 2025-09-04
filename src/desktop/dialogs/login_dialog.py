#!/usr/bin/env python3
"""
TalkBridge Desktop - Login Dialog (CustomTkinter)
=================================================

Enhanced login dialog with CustomTkinter and comprehensive styling

Author: TalkBridge Team
Date: 2025-09-03
Version: 2.0

Requirements:
- customtkinter
- tkinter
======================================================================
"""

import logging
import threading
import time
import json
from pathlib import Path
from enum import Enum
from typing import Optional, Tuple
import customtkinter as ctk
import tkinter as tk
from ...auth.auth_manager import AuthManager
from typing import Optional, Tuple
from enum import Enum
from dataclasses import dataclass
import tkinter as tk
import customtkinter as ctk


class UIConstants:
    """UI-related constants for the login dialog."""
    
    # Dialog dimensions
    MIN_WIDTH = 400
    MIN_HEIGHT = 450
    EXPANDED_HEIGHT = 500
    
    # Spacing and margins
    MAIN_MARGIN = 30
    MAIN_SPACING = 20
    FORM_SPACING = 15
    BUTTON_SPACING = 15
    
    # Component heights
    INPUT_HEIGHT = 35
    BUTTON_HEIGHT = 40
    PROGRESS_BAR_HEIGHT = 8
    STATUS_LABEL_HEIGHT = 45
    
    # Timeouts (in milliseconds)
    AUTH_TIMEOUT = 3000  # 3 seconds
    SUCCESS_DISPLAY_TIME = 1500  # 1.5 seconds
    ERROR_DISPLAY_TIME = 8000  # 8 seconds
    
    # Font sizes
    TITLE_FONT_SIZE = 24
    SUBTITLE_FONT_SIZE = 12
    LABEL_FONT_SIZE = 12
    INPUT_FONT_SIZE = 12


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
    message: str
    username: str = ""
    state: AuthenticationState = AuthenticationState.IDLE


class LoginTheme:
    """Theme colors and styling for the login dialog."""
    
    # Background colors
    BACKGROUND_MAIN = "#1e1e1e"
    BACKGROUND_SECONDARY = "#2d2d2d"
    BACKGROUND_ELEVATED = "#3c3c3c"
    
    # Text colors
    TEXT_PRIMARY = "#ffffff"
    TEXT_SECONDARY = "#cccccc"
    TEXT_MUTED = "#999999"
    TEXT_ERROR = "#ff6b6b"
    TEXT_SUCCESS = "#4CAF50"
    
    # Accent colors
    ACCENT_BLUE = "#0078d4"
    ACCENT_BLUE_HOVER = "#106ebe"
    ACCENT_GREEN = "#4CAF50"
    ACCENT_RED = "#f44336"
    
    # Input colors
    INPUT_BACKGROUND = "#3c3c3c"
    INPUT_BORDER = "#555555"
    INPUT_BORDER_FOCUS = "#0078d4"
    INPUT_BORDER_ERROR = "#f44336"


class LoginDialog:
    """
    Enhanced login dialog for TalkBridge Desktop application.
    Provides modern authentication UI with theming and validation.
    
    Features:
    - Modern CustomTkinter styling with animations
    - Asynchronous authentication with progress indicators
    - Comprehensive error handling and user feedback
    - Remember credentials functionality
    - Responsive design with proper theming
    - Password visibility toggle
    - Real-time validation feedback
    """

    def __init__(self, parent: ctk.CTk):
        """Initialize the enhanced login dialog."""
        self.parent = parent
        self.logger = logging.getLogger("talkbridge.desktop.login")
        
        # Authentication state
        self.auth_state = AuthenticationState.IDLE
        self.auth_result: Optional[AuthenticationResult] = None
        
        # Dialog result
        self.result = False
        self.username = ""
        self.password = ""
        
        # Dialog window
        self.dialog: Optional[ctk.CTkToplevel] = None
        
        # UI elements
        self.title_label: Optional[ctk.CTkLabel] = None
        self.subtitle_label: Optional[ctk.CTkLabel] = None
        self.username_entry: Optional[ctk.CTkEntry] = None
        self.password_entry: Optional[ctk.CTkEntry] = None
        self.remember_var: Optional[tk.BooleanVar] = None
        self.remember_checkbox: Optional[ctk.CTkCheckBox] = None
        self.show_password_var: Optional[tk.BooleanVar] = None
        self.show_password_checkbox: Optional[ctk.CTkCheckBox] = None
        self.login_button: Optional[ctk.CTkButton] = None
        self.cancel_button: Optional[ctk.CTkButton] = None
        self.progress_bar: Optional[ctk.CTkProgressBar] = None
        self.status_label: Optional[ctk.CTkLabel] = None
        self.logo_label: Optional[ctk.CTkLabel] = None
        
        # Animation and timing
        self.animation_running = False
        self.auth_thread: Optional[threading.Thread] = None

    def show(self) -> Tuple[bool, str, str]:
        """
        Show the login dialog and return authentication result.
        
        Returns:
            Tuple[bool, str, str]: (success, username, password)
        """
        self.logger.info("Showing enhanced login dialog")
        
        # Create dialog window
        self.dialog = ctk.CTkToplevel(self.parent)
        self.dialog.title("TalkBridge - Login")
        self.dialog.geometry(f"{UIConstants.MIN_WIDTH}x{UIConstants.MIN_HEIGHT}")
        self.dialog.resizable(False, False)
        
        # Center on parent
        self.center_dialog()
        
        # Configure dialog
        self.dialog.configure(fg_color=LoginTheme.BACKGROUND_MAIN)
        self.dialog.transient(self.parent)
        self.dialog.grab_set()
        
        # Setup UI
        self.setup_ui()
        
        # Load saved credentials if available
        self.load_saved_credentials()
        
        # Focus on username entry
        self.username_entry.focus()
        
        # Wait for dialog to close
        self.dialog.wait_window()
        
        return self.result, self.username, self.password

    def setup_ui(self) -> None:
        """Set up the enhanced login dialog UI."""
        # Main container
        main_frame = ctk.CTkFrame(self.dialog, fg_color="transparent")
        main_frame.pack(fill="both", expand=True, padx=UIConstants.MAIN_MARGIN, pady=UIConstants.MAIN_MARGIN)
        
        # Logo and title section
        header_frame = ctk.CTkFrame(main_frame, fg_color="transparent")
        header_frame.pack(fill="x", pady=(0, UIConstants.MAIN_SPACING))
        
        # Logo placeholder
        self.logo_label = ctk.CTkLabel(
            header_frame,
            text="🤖",
            font=ctk.CTkFont(size=48),
            text_color=LoginTheme.ACCENT_BLUE
        )
        self.logo_label.pack(pady=(0, 10))
        
        # Title
        self.title_label = ctk.CTkLabel(
            header_frame,
            text="TalkBridge Desktop",
            font=ctk.CTkFont(size=UIConstants.TITLE_FONT_SIZE, weight="bold"),
            text_color=LoginTheme.TEXT_PRIMARY
        )
        self.title_label.pack()
        
        # Subtitle
        self.subtitle_label = ctk.CTkLabel(
            header_frame,
            text="AI-Powered Communication Platform",
            font=ctk.CTkFont(size=UIConstants.SUBTITLE_FONT_SIZE),
            text_color=LoginTheme.TEXT_SECONDARY
        )
        self.subtitle_label.pack(pady=(5, 0))
        
        # Form section
        form_frame = ctk.CTkFrame(main_frame, fg_color=LoginTheme.BACKGROUND_SECONDARY, corner_radius=15)
        form_frame.pack(fill="x", pady=UIConstants.MAIN_SPACING)
        
        # Form title
        form_title = ctk.CTkLabel(
            form_frame,
            text="🔐 Sign In",
            font=ctk.CTkFont(size=16, weight="bold"),
            text_color=LoginTheme.TEXT_PRIMARY
        )
        form_title.pack(pady=(20, 15))
        
        # Username field
        username_frame = ctk.CTkFrame(form_frame, fg_color="transparent")
        username_frame.pack(fill="x", padx=20, pady=UIConstants.FORM_SPACING)
        
        username_label = ctk.CTkLabel(
            username_frame,
            text="👤 Username:",
            font=ctk.CTkFont(size=UIConstants.LABEL_FONT_SIZE),
            text_color=LoginTheme.TEXT_PRIMARY
        )
        username_label.pack(anchor="w", pady=(0, 5))
        
        self.username_entry = ctk.CTkEntry(
            username_frame,
            height=UIConstants.INPUT_HEIGHT,
            placeholder_text="Enter your username",
            font=ctk.CTkFont(size=UIConstants.INPUT_FONT_SIZE),
            fg_color=LoginTheme.INPUT_BACKGROUND,
            border_color=LoginTheme.INPUT_BORDER
        )
        self.username_entry.pack(fill="x")
        self.username_entry.bind("<KeyRelease>", self.on_input_changed)
        self.username_entry.bind("<FocusIn>", lambda e: self.on_field_focus(self.username_entry))
        self.username_entry.bind("<FocusOut>", lambda e: self.on_field_unfocus(self.username_entry))
        
        # Password field
        password_frame = ctk.CTkFrame(form_frame, fg_color="transparent")
        password_frame.pack(fill="x", padx=20, pady=UIConstants.FORM_SPACING)
        
        password_label = ctk.CTkLabel(
            password_frame,
            text="🔒 Password:",
            font=ctk.CTkFont(size=UIConstants.LABEL_FONT_SIZE),
            text_color=LoginTheme.TEXT_PRIMARY
        )
        password_label.pack(anchor="w", pady=(0, 5))
        
        password_input_frame = ctk.CTkFrame(password_frame, fg_color="transparent")
        password_input_frame.pack(fill="x")
        
        self.password_entry = ctk.CTkEntry(
            password_input_frame,
            height=UIConstants.INPUT_HEIGHT,
            placeholder_text="Enter your password",
            show="*",
            font=ctk.CTkFont(size=UIConstants.INPUT_FONT_SIZE),
            fg_color=LoginTheme.INPUT_BACKGROUND,
            border_color=LoginTheme.INPUT_BORDER
        )
        self.password_entry.pack(side="left", fill="x", expand=True)
        self.password_entry.bind("<KeyRelease>", self.on_input_changed)
        self.password_entry.bind("<Return>", lambda e: self.login())
        self.password_entry.bind("<FocusIn>", lambda e: self.on_field_focus(self.password_entry))
        self.password_entry.bind("<FocusOut>", lambda e: self.on_field_unfocus(self.password_entry))
        
        # Show/hide password toggle
        self.show_password_var = tk.BooleanVar()
        self.show_password_checkbox = ctk.CTkCheckBox(
            password_input_frame,
            text="👁️",
            width=30,
            checkbox_width=20,
            checkbox_height=20,
            variable=self.show_password_var,
            command=self.toggle_password_visibility
        )
        self.show_password_checkbox.pack(side="right", padx=(10, 0))
        
        # Options section
        options_frame = ctk.CTkFrame(form_frame, fg_color="transparent")
        options_frame.pack(fill="x", padx=20, pady=UIConstants.FORM_SPACING)
        
        # Remember me checkbox
        self.remember_var = tk.BooleanVar()
        self.remember_checkbox = ctk.CTkCheckBox(
            options_frame,
            text="🔄 Remember me",
            variable=self.remember_var,
            font=ctk.CTkFont(size=11),
            text_color=LoginTheme.TEXT_SECONDARY
        )
        self.remember_checkbox.pack(anchor="w")
        
        # Buttons section
        button_frame = ctk.CTkFrame(form_frame, fg_color="transparent")
        button_frame.pack(fill="x", padx=20, pady=(UIConstants.FORM_SPACING, 20))
        
        # Login button
        self.login_button = ctk.CTkButton(
            button_frame,
            text="🚀 Sign In",
            height=UIConstants.BUTTON_HEIGHT,
            command=self.login,
            fg_color=LoginTheme.ACCENT_BLUE,
            hover_color=LoginTheme.ACCENT_BLUE_HOVER,
            font=ctk.CTkFont(size=14, weight="bold")
        )
        self.login_button.pack(fill="x", pady=(0, UIConstants.BUTTON_SPACING))
        
        # Cancel button
        self.cancel_button = ctk.CTkButton(
            button_frame,
            text="❌ Cancel",
            height=UIConstants.BUTTON_HEIGHT,
            command=self.cancel,
            fg_color="transparent",
            text_color=LoginTheme.TEXT_SECONDARY,
            border_width=2,
            border_color=LoginTheme.INPUT_BORDER,
            hover_color=LoginTheme.BACKGROUND_ELEVATED,
            font=ctk.CTkFont(size=12)
        )
        self.cancel_button.pack(fill="x")
        
        # Progress and status section
        progress_frame = ctk.CTkFrame(main_frame, fg_color="transparent")
        progress_frame.pack(fill="x", pady=UIConstants.MAIN_SPACING)
        
        # Progress bar
        self.progress_bar = ctk.CTkProgressBar(
            progress_frame,
            height=UIConstants.PROGRESS_BAR_HEIGHT,
            progress_color=LoginTheme.ACCENT_BLUE
        )
        self.progress_bar.pack(fill="x", pady=(0, 10))
        self.progress_bar.set(0)
        
        # Status label
        self.status_label = ctk.CTkLabel(
            progress_frame,
            text="Ready to sign in",
            height=UIConstants.STATUS_LABEL_HEIGHT,
            font=ctk.CTkFont(size=11),
            text_color=LoginTheme.TEXT_SECONDARY,
            wraplength=300
        )
        self.status_label.pack()
        
        # Initial validation
        self.validate_inputs()
        
        self.logger.info("Enhanced login dialog UI setup completed")

    def center_dialog(self) -> None:
        """Center the dialog on its parent window."""
        if self.parent:
            parent_x = self.parent.winfo_x()
            parent_y = self.parent.winfo_y()
            parent_width = self.parent.winfo_width()
            parent_height = self.parent.winfo_height()
            
            dialog_x = parent_x + (parent_width - UIConstants.MIN_WIDTH) // 2
            dialog_y = parent_y + (parent_height - UIConstants.MIN_HEIGHT) // 2
            
            self.dialog.geometry(f"{UIConstants.MIN_WIDTH}x{UIConstants.MIN_HEIGHT}+{dialog_x}+{dialog_y}")

    def on_field_focus(self, field: ctk.CTkEntry) -> None:
        """Handle field focus event."""
        field.configure(border_color=LoginTheme.ACCENT_BLUE)

    def on_field_unfocus(self, field: ctk.CTkEntry) -> None:
        """Handle field unfocus event."""
        field.configure(border_color=LoginTheme.INPUT_BORDER)

    def toggle_password_visibility(self) -> None:
        """Toggle password visibility."""
        if self.show_password_var.get():
            self.password_entry.configure(show="")
        else:
            self.password_entry.configure(show="*")

    def on_input_changed(self, event=None) -> None:
        """Handle input field changes."""
        self.validate_inputs()

    def validate_inputs(self) -> None:
        """Validate input fields and update UI accordingly."""
        username = self.username_entry.get().strip()
        password = self.password_entry.get().strip()
        
        is_valid = len(username) >= 3 and len(password) >= 1
        
        # Update login button state
        if is_valid:
            self.login_button.configure(state="normal")
            self.update_status("Ready to sign in", LoginTheme.TEXT_SECONDARY)
        else:
            self.login_button.configure(state="disabled")
            if not username:
                self.update_status("Please enter your username", LoginTheme.ERROR_COLOR)
            elif len(username) < 3:
                self.update_status("Username must be at least 3 characters", LoginTheme.ERROR_COLOR)
            elif not password:
                self.update_status("Please enter your password", LoginTheme.ERROR_COLOR)

    def update_status(self, message: str, color: str = None) -> None:
        """Update status message."""
        if color is None:
            color = LoginTheme.TEXT_SECONDARY
        
        self.status_label.configure(text=message, text_color=color)
        self.dialog.update_idletasks()

    def set_auth_state(self, state: AuthenticationState) -> None:
        """Set authentication state and update UI."""
        self.auth_state = state
        
        if state == AuthenticationState.IDLE:
            self.login_button.configure(text="🚀 Sign In", state="normal")
            self.username_entry.configure(state="normal")
            self.password_entry.configure(state="normal")
            self.progress_bar.set(0)
            self.update_status("Ready to sign in")
            
        elif state == AuthenticationState.AUTHENTICATING:
            self.login_button.configure(text="🔄 Signing In...", state="disabled")
            self.username_entry.configure(state="disabled")
            self.password_entry.configure(state="disabled")
            self.update_status("Authenticating...")
            self.start_progress_animation()
            
        elif state == AuthenticationState.SUCCESS:
            self.login_button.configure(text="✅ Success!", state="disabled")
            self.progress_bar.set(1)
            self.update_status("Authentication successful!", LoginTheme.SUCCESS_COLOR)
            
        elif state == AuthenticationState.FAILED:
            self.login_button.configure(text="❌ Failed", state="normal")
            self.username_entry.configure(state="normal")
            self.password_entry.configure(state="normal")
            self.progress_bar.set(0)
            self.update_status("Authentication failed. Please try again.", LoginTheme.ERROR_COLOR)
            
        elif state == AuthenticationState.ERROR:
            self.login_button.configure(text="⚠️ Error", state="normal")
            self.username_entry.configure(state="normal")
            self.password_entry.configure(state="normal")
            self.progress_bar.set(0)
            self.update_status("An error occurred. Please try again.", LoginTheme.ERROR_COLOR)

    def start_progress_animation(self) -> None:
        """Start progress bar animation."""
        if not self.animation_running:
            self.animation_running = True
            self.animate_progress()

    def animate_progress(self) -> None:
        """Animate progress bar during authentication."""
        if self.animation_running and self.auth_state == AuthenticationState.AUTHENTICATING:
            current = self.progress_bar.get()
            if current < 0.9:
                self.progress_bar.set(current + 0.1)
            else:
                self.progress_bar.set(0.1)
            
            # Continue animation
            self.dialog.after(200, self.animate_progress)
        else:
            self.animation_running = False

    def load_saved_credentials(self) -> None:
        """Load saved credentials if remember me was checked."""
        try:
            saved_file = Path.home() / ".talkbridge" / "credentials"
            if saved_file.exists():
                with open(saved_file, 'r') as f:
                    data = json.load(f)
                    
                username = data.get('username', '')
                remember = data.get('remember', False)
                
                if username and remember:
                    self.username_entry.insert(0, username)
                    self.remember_var.set(True)
                    self.password_entry.focus()  # Focus on password if username is loaded
                    
        except Exception as e:
            self.logger.warning(f"Could not load saved credentials: {e}")

    def save_credentials(self) -> None:
        """Save credentials if remember me is checked."""
        try:
            if self.remember_var.get():
                credentials_dir = Path.home() / ".talkbridge"
                credentials_dir.mkdir(exist_ok=True)
                
                saved_file = credentials_dir / "credentials"
                with open(saved_file, 'w') as f:
                    json.dump({
                        'username': self.username,
                        'remember': True
                    }, f)
                    
                # Set appropriate permissions
                saved_file.chmod(0o600)
            else:
                # Remove saved credentials if remember me is unchecked
                saved_file = Path.home() / ".talkbridge" / "credentials"
                if saved_file.exists():
                    saved_file.unlink()
                    
        except Exception as e:
            self.logger.warning(f"Could not save credentials: {e}")

    def login(self) -> None:
        """Handle login button click."""
        if self.auth_state == AuthenticationState.AUTHENTICATING:
            return
            
        self.username = self.username_entry.get().strip()
        self.password = self.password_entry.get().strip()
        
        if not self.username or not self.password:
            self.update_status("Please fill in all fields", LoginTheme.ERROR_COLOR)
            return
            
        # Start authentication in separate thread
        self.set_auth_state(AuthenticationState.AUTHENTICATING)
        self.auth_thread = threading.Thread(target=self._authenticate, daemon=True)
        self.auth_thread.start()

    def _authenticate(self) -> None:
        """Perform authentication in separate thread."""
        try:
            success = self.auth_manager.authenticate(self.username, self.password)
            
            # Simulate some processing time
            time.sleep(1)
            
            # Update UI on main thread
            self.dialog.after(0, self._on_auth_complete, success)
            
        except Exception as e:
            self.logger.error(f"Authentication error: {e}")
            self.dialog.after(0, self._on_auth_error, str(e))

    def _on_auth_complete(self, success: bool) -> None:
        """Handle authentication completion on main thread."""
        if success:
            self.set_auth_state(AuthenticationState.SUCCESS)
            self.save_credentials()
            self.result = True
            
            # Close dialog after brief delay
            self.dialog.after(1000, self.dialog.destroy)
        else:
            self.set_auth_state(AuthenticationState.FAILED)
            self.password_entry.delete(0, 'end')
            self.password_entry.focus()

    def _on_auth_error(self, error_message: str) -> None:
        """Handle authentication error on main thread."""
        self.set_auth_state(AuthenticationState.ERROR)
        self.update_status(f"Error: {error_message}", LoginTheme.ERROR_COLOR)

    def cancel(self) -> None:
        """Handle cancel button click."""
        self.result = False
        self.dialog.destroy()

    def show(self) -> bool:
        """
        Shows the login dialog.
        
        Returns:
            True if login successful, False if cancelled
        """
        self.logger.info("Showing login dialog")
        
        # Create dialog window
        self.dialog = ctk.CTkToplevel(self.parent)
        self.dialog.title("TalkBridge Login")
        self.dialog.geometry("400x350")
        self.dialog.resizable(False, False)
        
        # Center dialog
        self.dialog.update_idletasks()
        x = (self.dialog.winfo_screenwidth() // 2) - (400 // 2)
        y = (self.dialog.winfo_screenheight() // 2) - (350 // 2)
        self.dialog.geometry(f"400x350+{x}+{y}")
        
        # Make dialog modal
        self.dialog.transient(self.parent)
        self.dialog.grab_set()
        
        # Setup UI
        self._setup_ui()
        
        # Handle window close
        self.dialog.protocol("WM_DELETE_WINDOW", self._on_cancel)
        
        # Wait for dialog to close
        self.dialog.wait_window()
        
        return self.result

    def _setup_ui(self) -> None:
        """Sets up the login dialog UI."""
        # Main frame
        main_frame = ctk.CTkFrame(self.dialog)
        main_frame.pack(fill="both", expand=True, padx=20, pady=20)
        
        # Title
        title_label = ctk.CTkLabel(
            main_frame,
            text="TalkBridge Login",
            font=ctk.CTkFont(size=24, weight="bold")
        )
        title_label.pack(pady=20)
        
        # Subtitle
        subtitle_label = ctk.CTkLabel(
            main_frame,
            text="Please enter your credentials",
            font=ctk.CTkFont(size=12)
        )
        subtitle_label.pack(pady=(0, 20))
        
        # Username field
        username_label = ctk.CTkLabel(
            main_frame,
            text="Username:",
            font=ctk.CTkFont(size=12)
        )
        username_label.pack(anchor="w", padx=20)
        
        self.username_entry = ctk.CTkEntry(
            main_frame,
            placeholder_text="Enter username",
            width=300,
            height=32
        )
        self.username_entry.pack(pady=(5, 15), padx=20)
        
        # Password field
        password_label = ctk.CTkLabel(
            main_frame,
            text="Password:",
            font=ctk.CTkFont(size=12)
        )
        password_label.pack(anchor="w", padx=20)
        
        self.password_entry = ctk.CTkEntry(
            main_frame,
            placeholder_text="Enter password",
            show="*",
            width=300,
            height=32
        )
        self.password_entry.pack(pady=(5, 15), padx=20)
        
        # Remember credentials checkbox
        self.remember_var = tk.BooleanVar()
        remember_checkbox = ctk.CTkCheckBox(
            main_frame,
            text="Remember credentials",
            variable=self.remember_var,
            font=ctk.CTkFont(size=11)
        )
        remember_checkbox.pack(pady=(10, 20))
        
        # Buttons frame
        button_frame = ctk.CTkFrame(main_frame, fg_color="transparent")
        button_frame.pack(pady=10)
        
        # Login button
        login_button = ctk.CTkButton(
            button_frame,
            text="Login",
            width=120,
            height=32,
            command=self._on_login
        )
        login_button.pack(side="left", padx=10)
        
        # Cancel button
        cancel_button = ctk.CTkButton(
            button_frame,
            text="Cancel",
            width=120,
            height=32,
            fg_color="gray",
            hover_color="darkgray",
            command=self._on_cancel
        )
        cancel_button.pack(side="left", padx=10)
        
        # Set default values for testing
        self.username_entry.insert(0, "admin")
        self.password_entry.insert(0, "password")
        
        # Focus on username entry
        self.username_entry.focus()
        
        # Bind Enter key to login
        self.dialog.bind('<Return>', lambda e: self._on_login())

    def _on_login(self) -> None:
        """Handles login button click."""
        self.username = self.username_entry.get().strip()
        self.password = self.password_entry.get()
        
        if not self.username:
            self._show_error("Please enter a username")
            return
        
        if not self.password:
            self._show_error("Please enter a password")
            return
        
        # Simple authentication (in real app, use proper auth)
        if self.username == "admin" and self.password == "password":
            self.result = True
            self.logger.info(f"Login successful for user: {self.username}")
            self.dialog.destroy()
        else:
            self._show_error("Invalid username or password")
            self.password_entry.delete(0, tk.END)
            self.password_entry.focus()

    def _on_cancel(self) -> None:
        """Handles cancel button click."""
        self.result = False
        self.logger.info("Login cancelled")
        self.dialog.destroy()

    def _show_error(self, message: str) -> None:
        """Shows an error message."""
        self.logger.error(f"Login error: {message}")
        
        # Create error dialog
        error_dialog = ctk.CTkToplevel(self.dialog)
        error_dialog.title("Login Error")
        error_dialog.geometry("300x150")
        error_dialog.resizable(False, False)
        
        # Center error dialog
        error_dialog.update_idletasks()
        x = (error_dialog.winfo_screenwidth() // 2) - (300 // 2)
        y = (error_dialog.winfo_screenheight() // 2) - (150 // 2)
        error_dialog.geometry(f"300x150+{x}+{y}")
        
        # Add content
        frame = ctk.CTkFrame(error_dialog)
        frame.pack(fill="both", expand=True, padx=20, pady=20)
        
        # Error message
        label = ctk.CTkLabel(
            frame,
            text=message,
            font=ctk.CTkFont(size=12),
            wraplength=260
        )
        label.pack(pady=20)
        
        # OK button
        ok_button = ctk.CTkButton(
            frame,
            text="OK",
            command=error_dialog.destroy
        )
        ok_button.pack(pady=10)
        
        # Make error dialog modal
        error_dialog.transient(self.dialog)
        error_dialog.grab_set()
        error_dialog.wait_window()

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
            True if remember checkbox is checked
        """
        return self.remember_var.get() if self.remember_var else False
