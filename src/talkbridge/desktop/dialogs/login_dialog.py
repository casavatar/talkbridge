#!/usr/bin/env python3
"""
TalkBridge Desktop - Login Dialog (CustomTkinter)
=================================================

Enhanced login dialog with CustomTkinter and comprehensive styling

Author: TalkBridge Team
Date: 2025-09-08
Version: 2.1

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
from dataclasses import dataclass
import tkinter as tk
import customtkinter as ctk
from ...auth.auth_manager import AuthManager

# Import UI utilities for consistent styling
try:
    from talkbridge.desktop.ui.ui_utils import icon, clean_text, strip_variation_selectors
    UI_UTILS_AVAILABLE = True
except ImportError:
    UI_UTILS_AVAILABLE = False

try:
    from talkbridge.desktop.ui.theme import (
        ColorPalette, Typography, Spacing, Dimensions, 
        ComponentThemes, UIText, Icons, UXGuidelines
    )
    THEME_AVAILABLE = True
except ImportError:
    THEME_AVAILABLE = False

# Dialog dimensions - optimized for content without scrolling
MIN_WIDTH = 480
MIN_HEIGHT = 600  # Fixed height for content to fit without scrolling
EXPANDED_HEIGHT = 620  # Slightly larger if needed

# Spacing and margins (using theme if available)
MAIN_MARGIN = Spacing.MARGIN_MAIN if THEME_AVAILABLE else 25
MAIN_SPACING = Spacing.LG if THEME_AVAILABLE else 15
FORM_SPACING = Spacing.MD if THEME_AVAILABLE else 12
BUTTON_SPACING = Spacing.SM if THEME_AVAILABLE else 10

# Component heights (using theme if available)
INPUT_HEIGHT = Dimensions.HEIGHT_INPUT if THEME_AVAILABLE else 40
BUTTON_HEIGHT = Dimensions.HEIGHT_BUTTON if THEME_AVAILABLE else 45
STATUS_LABEL_HEIGHT = 30

# Timeouts (in milliseconds)
AUTH_TIMEOUT = 3000  # 3 seconds
SUCCESS_DISPLAY_TIME = 1500  # 1.5 seconds
ERROR_DISPLAY_TIME = 8000  # 8 seconds

# Font sizes (using theme if available)
TITLE_FONT_SIZE = Typography.FONT_SIZE_H1 if THEME_AVAILABLE else 22
SUBTITLE_FONT_SIZE = Typography.FONT_SIZE_CAPTION if THEME_AVAILABLE else 11
LABEL_FONT_SIZE = Typography.FONT_SIZE_CAPTION if THEME_AVAILABLE else 11
INPUT_FONT_SIZE = Typography.FONT_SIZE_BODY if THEME_AVAILABLE else 12

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
    
    # Use unified theme if available, otherwise fallback to original colors
    if THEME_AVAILABLE:
        # Background colors
        BACKGROUND_MAIN = ColorPalette.BACKGROUND_PRIMARY
        BACKGROUND_SECONDARY = ColorPalette.BACKGROUND_SECONDARY
        BACKGROUND_ELEVATED = ColorPalette.BACKGROUND_ELEVATED
        
        # Text colors
        TEXT_PRIMARY = ColorPalette.TEXT_PRIMARY
        TEXT_SECONDARY = ColorPalette.TEXT_SECONDARY
        TEXT_MUTED = ColorPalette.TEXT_TERTIARY
        TEXT_ERROR = ColorPalette.ERROR
        TEXT_SUCCESS = ColorPalette.SUCCESS
        
        # Accent colors
        ACCENT_BLUE = ColorPalette.ACCENT_PRIMARY
        ACCENT_BLUE_HOVER = ColorPalette.ACCENT_PRIMARY_HOVER
        ACCENT_GREEN = ColorPalette.SUCCESS
        ACCENT_RED = ColorPalette.ERROR
        
        # Input colors
        INPUT_BACKGROUND = ColorPalette.INPUT_BACKGROUND
        INPUT_BORDER = ColorPalette.BORDER_DEFAULT
        INPUT_BORDER_FOCUS = ColorPalette.BORDER_FOCUS
        INPUT_BORDER_ERROR = ColorPalette.BORDER_ERROR
    else:
        # Fallback colors
        BACKGROUND_MAIN = "#1e1e1e"
        BACKGROUND_SECONDARY = "#2d2d2d"
        BACKGROUND_ELEVATED = "#3c3c3c"
        
        TEXT_PRIMARY = "#ffffff"
        TEXT_SECONDARY = "#cccccc"
        TEXT_MUTED = "#999999"
        TEXT_ERROR = "#ff6b6b"
        TEXT_SUCCESS = "#4CAF50"
        
        ACCENT_BLUE = "#0078d4"
        ACCENT_BLUE_HOVER = "#106ebe"
        ACCENT_GREEN = "#4CAF50"
        ACCENT_RED = "#f44336"
        
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
        
        # Initialize authentication manager
        self.auth_manager = AuthManager()
        
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
        self.status_label: Optional[ctk.CTkLabel] = None
        self.logo_label: Optional[ctk.CTkLabel] = None
        
        # Authentication thread
        self.auth_thread: Optional[threading.Thread] = None

    def show(self) -> Tuple[bool, str, str]:
        """
        Show the login dialog and return authentication result.
        
        Returns:
            Tuple[bool, str, str]: (success, username, password)
        """
        self.logger.info("Showing enhanced login dialog")
        
        try:
            # Create dialog window
            self.dialog = ctk.CTkToplevel(self.parent)
            self.dialog.title("TalkBridge - Login")
            self.dialog.geometry(f"{MIN_WIDTH}x{MIN_HEIGHT}")
            self.dialog.resizable(False, False)
            
            # Configure dialog
            self.dialog.configure(fg_color=LoginTheme.BACKGROUND_MAIN)
            
            # Center on parent or screen
            self.center_dialog()
            
            # Configure window properties
            if self.parent and self.parent.winfo_exists():
                self.dialog.transient(self.parent)
            
            # Setup UI before making visible
            self.setup_ui()
            
            # Make dialog visible and focused
            self.dialog.deiconify()  # Ensure dialog is visible
            self.dialog.lift()       # Bring to front
            self.dialog.attributes('-topmost', True)  # Stay on top
            self.dialog.focus_force()  # Force focus
            self.dialog.grab_set()     # Modal behavior
            
            # Load saved credentials if available
            self.load_saved_credentials()
            
            # Focus on username entry after a short delay
            self.dialog.after(100, self._focus_username_entry)
            
            # Wait for dialog to close
            self.dialog.wait_window()
            
            return self.result, self.username, self.password
            
        except Exception as e:
            self.logger.error(f"Error creating login dialog: {e}")
            # Return failure if dialog creation fails
            return False, "", ""

    def _focus_username_entry(self):
        """Set focus to username entry with error handling."""
        try:
            if self.username_entry and self.username_entry.winfo_exists():
                self.username_entry.focus()
        except Exception as e:
            self.logger.warning(f"Error setting focus to username entry: {e}")

    def setup_ui(self) -> None:
        """Set up the enhanced login dialog UI with proper layout."""
        try:
            # Main container with regular frame (no scrolling needed)
            main_frame = ctk.CTkFrame(
                self.dialog, 
                fg_color="transparent"
            )
            main_frame.pack(fill="both", expand=True, padx=MAIN_MARGIN, pady=MAIN_MARGIN)
            
            # Header section
            self._create_header_section(main_frame)
            
            # Form section
            self._create_form_section(main_frame)
            
            # Status section (without progress bar)
            self._create_status_section(main_frame)
            
            # Initial validation
            self.validate_inputs()
            
            # Configure window close protocol
            self.dialog.protocol("WM_DELETE_WINDOW", self.cancel)
            
            self.logger.info("Enhanced login dialog UI setup completed")
            
        except Exception as e:
            self.logger.error(f"Error setting up login dialog UI: {e}")
            raise

    def _create_header_section(self, parent):
        """Create the header section with logo and title."""
        header_frame = ctk.CTkFrame(parent, fg_color="transparent")
        header_frame.pack(fill="x", pady=(0, MAIN_SPACING))
        
        # Logo using clean text instead of emoji
        self.logo_label = ctk.CTkLabel(
            header_frame,
            text=Icons.ROBOT if THEME_AVAILABLE else "AI",
            font=ctk.CTkFont(size=40, weight="bold"),
            text_color=LoginTheme.ACCENT_BLUE
        )
        self.logo_label.pack(pady=(0, 8))
        
        # Title
        self.title_label = ctk.CTkLabel(
            header_frame,
            text=UIText.APP_NAME if THEME_AVAILABLE else "TalkBridge Desktop",
            font=ctk.CTkFont(size=TITLE_FONT_SIZE, weight="bold"),
            text_color=LoginTheme.TEXT_PRIMARY
        )
        self.title_label.pack()
        
        # Subtitle
        self.subtitle_label = ctk.CTkLabel(
            header_frame,
            text=UIText.APP_SUBTITLE if THEME_AVAILABLE else "AI-Powered Communication Platform",
            font=ctk.CTkFont(size=SUBTITLE_FONT_SIZE),
            text_color=LoginTheme.TEXT_SECONDARY
        )
        self.subtitle_label.pack(pady=(3, 0))

    def _create_form_section(self, parent):
        """Create the form section with inputs and buttons."""
        # Form container
        form_frame = ctk.CTkFrame(
            parent, 
            fg_color=LoginTheme.BACKGROUND_SECONDARY, 
            corner_radius=12
        )
        form_frame.pack(fill="x", pady=MAIN_SPACING)
        
        # Form content with padding
        form_content = ctk.CTkFrame(form_frame, fg_color="transparent")
        form_content.pack(fill="both", expand=True, padx=25, pady=20)
        
        # Form title using clean text
        form_title = ctk.CTkLabel(
            form_content,
            text=UIText.LOGIN_TITLE if THEME_AVAILABLE else "Sign In",
            font=ctk.CTkFont(size=16, weight="bold"),
            text_color=LoginTheme.TEXT_PRIMARY
        )
        form_title.pack(pady=(0, 15))
        
        # Username field
        self._create_username_field(form_content)
        
        # Password field
        self._create_password_field(form_content)
        
        # Options
        self._create_options_section(form_content)
        
        # Buttons
        self._create_buttons_section(form_content)

    def _create_username_field(self, parent):
        """Create username input field."""
        username_frame = ctk.CTkFrame(parent, fg_color="transparent")
        username_frame.pack(fill="x", pady=(0, FORM_SPACING))
        
        username_label = ctk.CTkLabel(
            username_frame,
            text=UIText.USERNAME_LABEL if THEME_AVAILABLE else "Username:",
            font=ctk.CTkFont(size=LABEL_FONT_SIZE),
            text_color=LoginTheme.TEXT_PRIMARY
        )
        username_label.pack(anchor="w", pady=(0, 4))
        
        entry_style = ComponentThemes.get_input_theme() if THEME_AVAILABLE else {
            "height": Dimensions.HEIGHT_INPUT,
            "fg_color": LoginTheme.INPUT_BACKGROUND,
            "border_color": LoginTheme.INPUT_BORDER,
            "corner_radius": Dimensions.RADIUS_MD,
            "font": ctk.CTkFont(size=Typography.FONT_SIZE_BODY)
        }
        
        self.username_entry = ctk.CTkEntry(
            username_frame,
            placeholder_text=clean_text("Enter your username") if UI_UTILS_AVAILABLE else "Enter your username",
            **entry_style
        )
        self.username_entry.pack(fill="x")
        self.username_entry.bind("<KeyRelease>", self.on_input_changed)
        self.username_entry.bind("<FocusIn>", lambda e: self.on_field_focus(self.username_entry))
        self.username_entry.bind("<FocusOut>", lambda e: self.on_field_unfocus(self.username_entry))

    def _create_password_field(self, parent):
        """Create password input field with show/hide toggle."""
        password_frame = ctk.CTkFrame(parent, fg_color="transparent")
        password_frame.pack(fill="x", pady=(0, FORM_SPACING))
        
        password_label = ctk.CTkLabel(
            password_frame,
            text=UIText.PASSWORD_LABEL if THEME_AVAILABLE else "Password:",
            font=ctk.CTkFont(size=LABEL_FONT_SIZE),
            text_color=LoginTheme.TEXT_PRIMARY
        )
        password_label.pack(anchor="w", pady=(0, 4))
        
        # Password input container
        password_input_frame = ctk.CTkFrame(password_frame, fg_color="transparent")
        password_input_frame.pack(fill="x")
        
        entry_style = ComponentThemes.get_input_theme() if THEME_AVAILABLE else {
            "height": Dimensions.HEIGHT_INPUT,
            "fg_color": LoginTheme.INPUT_BACKGROUND,
            "border_color": LoginTheme.INPUT_BORDER,
            "corner_radius": Dimensions.RADIUS_MD,
            "font": ctk.CTkFont(size=Typography.FONT_SIZE_BODY)
        }
        
        self.password_entry = ctk.CTkEntry(
            password_input_frame,
            placeholder_text=clean_text("Enter your password") if UI_UTILS_AVAILABLE else "Enter your password",
            show="*",
            **entry_style
        )
        self.password_entry.pack(side="left", fill="x", expand=True, padx=(0, 8))
        self.password_entry.bind("<KeyRelease>", self.on_input_changed)
        self.password_entry.bind("<Return>", lambda e: self.login())
        self.password_entry.bind("<FocusIn>", lambda e: self.on_field_focus(self.password_entry))
        self.password_entry.bind("<FocusOut>", lambda e: self.on_field_unfocus(self.password_entry))
        
        # Show/hide password toggle with accessible text
        self.show_password_var = tk.BooleanVar()
        self.show_password_checkbox = ctk.CTkCheckBox(
            password_input_frame,
            text=UIText.SHOW_PASSWORD if THEME_AVAILABLE else "Show",
            width=60,
            height=28,
            checkbox_width=18,
            checkbox_height=18,
            variable=self.show_password_var,
            command=self.toggle_password_visibility,
            fg_color=LoginTheme.ACCENT_BLUE,
            font=ctk.CTkFont(size=9)
        )
        self.show_password_checkbox.pack(side="right")

    def _create_options_section(self, parent):
        """Create options section with remember me checkbox."""
        options_frame = ctk.CTkFrame(parent, fg_color="transparent")
        options_frame.pack(fill="x", pady=(0, FORM_SPACING))
        
        # Remember me checkbox
        self.remember_var = tk.BooleanVar()
        self.remember_checkbox = ctk.CTkCheckBox(
            options_frame,
            text=UIText.REMEMBER_ME if THEME_AVAILABLE else "Remember me",
            variable=self.remember_var,
            font=ctk.CTkFont(size=10),
            text_color=LoginTheme.TEXT_SECONDARY,
            fg_color=LoginTheme.ACCENT_BLUE,
            height=20
        )
        self.remember_checkbox.pack(anchor="w")

    def _create_buttons_section(self, parent):
        """Create buttons section with login and cancel buttons."""
        button_frame = ctk.CTkFrame(parent, fg_color="transparent")
        button_frame.pack(fill="x", pady=(FORM_SPACING, 0))
        
        # Login button with theme-aware styling
        button_theme = ComponentThemes.get_button_theme("primary") if THEME_AVAILABLE else {}
        # Remove all conflicting parameters from theme to avoid conflicts
        excluded_params = ['height', 'command', 'text', 'corner_radius', 'font', 'fg_color', 'hover_color']
        button_theme_clean = {k: v for k, v in button_theme.items() if k not in excluded_params} if THEME_AVAILABLE else {}
        
        # Login button with consistent styling
        button_style = ComponentThemes.get_button_theme() if THEME_AVAILABLE else {
            "height": Dimensions.HEIGHT_BUTTON,
            "fg_color": LoginTheme.ACCENT_BLUE,
            "hover_color": LoginTheme.ACCENT_BLUE_HOVER,
            "corner_radius": Dimensions.RADIUS_MD,
            "font": ctk.CTkFont(size=Typography.FONT_SIZE_BUTTON)
        }
        
        self.login_button = ctk.CTkButton(
            button_frame,
            text=clean_text("Sign In") if UI_UTILS_AVAILABLE else "Sign In",
            command=self.login,
            image=icon("login") if UI_UTILS_AVAILABLE else None,
            compound="left",
            **button_style
        )
        self.login_button.pack(fill="x", pady=(0, Spacing.SM))
        
        # Cancel button with secondary styling
        cancel_theme = ComponentThemes.get_button_theme("secondary") if THEME_AVAILABLE else {
            "height": Dimensions.HEIGHT_BUTTON,
            "fg_color": "transparent",
            "text_color": LoginTheme.TEXT_SECONDARY,
            "border_width": Dimensions.BORDER_THIN,
            "border_color": LoginTheme.INPUT_BORDER,
            "hover_color": LoginTheme.BACKGROUND_ELEVATED,
            "corner_radius": Dimensions.RADIUS_MD,
            "font": ctk.CTkFont(size=Typography.FONT_SIZE_BUTTON)
        }
        
        self.cancel_button = ctk.CTkButton(
            button_frame,
            text=clean_text("Cancel") if UI_UTILS_AVAILABLE else "Cancel",
            command=self.cancel,
            image=icon("close") if UI_UTILS_AVAILABLE else None,
            compound="left",
            **cancel_theme
        )
        self.cancel_button.pack(fill="x")

    def _create_status_section(self, parent):
        """Create status section (progress bar removed)."""
        status_frame = ctk.CTkFrame(parent, fg_color="transparent")
        status_frame.pack(fill="x", pady=MAIN_SPACING)
        
        # Status label with improved styling
        self.status_label = ctk.CTkLabel(
            status_frame,
            text="Ready to sign in",
            height=STATUS_LABEL_HEIGHT,
            font=ctk.CTkFont(size=Typography.FONT_SIZE_CAPTION),
            text_color=LoginTheme.TEXT_SECONDARY,
            wraplength=400
        )
        self.status_label.pack()

    def center_dialog(self) -> None:
        """Center the dialog on its parent window or screen."""
        try:
            if self.parent and self.parent.winfo_viewable():
                # Parent is visible, center on parent
                parent_x = self.parent.winfo_x()
                parent_y = self.parent.winfo_y()
                parent_width = self.parent.winfo_width()
                parent_height = self.parent.winfo_height()
                
                dialog_x = parent_x + (parent_width - MIN_WIDTH) // 2
                dialog_y = parent_y + (parent_height - MIN_HEIGHT) // 2
                
                self.dialog.geometry(f"{MIN_WIDTH}x{MIN_HEIGHT}+{dialog_x}+{dialog_y}")
            else:
                # Parent is hidden or not available, center on screen
                screen_width = self.dialog.winfo_screenwidth()
                screen_height = self.dialog.winfo_screenheight()
                
                dialog_x = (screen_width - MIN_WIDTH) // 2
                dialog_y = (screen_height - MIN_HEIGHT) // 2
                
                self.dialog.geometry(f"{MIN_WIDTH}x{MIN_HEIGHT}+{dialog_x}+{dialog_y}")
        except Exception as e:
            # Fallback to default geometry if positioning fails
            self.logger.warning(f"Error centering dialog: {e}, using default position")
            self.dialog.geometry(f"{MIN_WIDTH}x{MIN_HEIGHT}")

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
            self.update_status(UIText.READY if THEME_AVAILABLE else "Ready to sign in", LoginTheme.TEXT_SECONDARY)
        else:
            self.login_button.configure(state="disabled")
            if not username:
                self.update_status("Please enter your username", LoginTheme.TEXT_ERROR)
            elif len(username) < 3:
                self.update_status("Username must be at least 3 characters", LoginTheme.TEXT_ERROR)
            elif not password:
                self.update_status("Please enter your password", LoginTheme.TEXT_ERROR)

    def update_status(self, message: str, color: str = None) -> None:
        """Update status message."""
        try:
            if not self.dialog or not self.dialog.winfo_exists():
                return
                
            if color is None:
                color = LoginTheme.TEXT_SECONDARY
            
            if self.status_label and self.status_label.winfo_exists():
                self.status_label.configure(text=message, text_color=color)
                self.dialog.update_idletasks()
        except (tk.TclError, RuntimeError) as e:
            self.logger.warning(f"Cannot update status: {e}")

    def set_auth_state(self, state: AuthenticationState) -> None:
        """Set authentication state and update UI."""
        try:
            if not self.dialog or not self.dialog.winfo_exists():
                return
                
            self.auth_state = state
            
            if state == AuthenticationState.IDLE:
                if self.login_button and self.login_button.winfo_exists():
                    self.login_button.configure(
                        text=UIText.SIGN_IN_BUTTON if THEME_AVAILABLE else "Sign In", 
                        state="normal"
                    )
                if self.username_entry and self.username_entry.winfo_exists():
                    self.username_entry.configure(state="normal")
                if self.password_entry and self.password_entry.winfo_exists():
                    self.password_entry.configure(state="normal")
                self.update_status(UIText.READY if THEME_AVAILABLE else "Ready to sign in")
                
            elif state == AuthenticationState.AUTHENTICATING:
                if self.login_button and self.login_button.winfo_exists():
                    self.login_button.configure(
                        text=UIText.SIGNING_IN if THEME_AVAILABLE else "Signing in...", 
                        state="disabled"
                    )
                if self.username_entry and self.username_entry.winfo_exists():
                    self.username_entry.configure(state="disabled")
                if self.password_entry and self.password_entry.winfo_exists():
                    self.password_entry.configure(state="disabled")
                self.update_status(UIText.SIGNING_IN if THEME_AVAILABLE else "Authenticating...", LoginTheme.ACCENT_BLUE)
                
            elif state == AuthenticationState.SUCCESS:
                if self.login_button and self.login_button.winfo_exists():
                    self.login_button.configure(
                        text=UIText.AUTH_SUCCESS if THEME_AVAILABLE else "Success!", 
                        state="disabled"
                    )
                self.update_status(
                    "Authentication successful!" if THEME_AVAILABLE else "Authentication successful!", 
                    LoginTheme.TEXT_SUCCESS
                )
                
            elif state == AuthenticationState.FAILED:
                if self.login_button and self.login_button.winfo_exists():
                    self.login_button.configure(
                        text=UIText.AUTH_FAILED if THEME_AVAILABLE else "Authentication failed", 
                        state="normal"
                    )
                if self.username_entry and self.username_entry.winfo_exists():
                    self.username_entry.configure(state="normal")
                if self.password_entry and self.password_entry.winfo_exists():
                    self.password_entry.configure(state="normal")
                self.update_status("Authentication failed. Please try again.", LoginTheme.TEXT_ERROR)
                
            elif state == AuthenticationState.TIMEOUT:
                if self.login_button and self.login_button.winfo_exists():
                    self.login_button.configure(
                        text="Request timed out", 
                        state="normal"
                    )
                if self.username_entry and self.username_entry.winfo_exists():
                    self.username_entry.configure(state="normal")
                if self.password_entry and self.password_entry.winfo_exists():
                    self.password_entry.configure(state="normal")
                self.update_status("Authentication timed out. Please try again.", LoginTheme.TEXT_ERROR)
                
        except (tk.TclError, RuntimeError) as e:
            self.logger.warning(f"Cannot update auth state: {e}")

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
                    return
                    
        except Exception as e:
            self.logger.warning(f"Could not load saved credentials: {e}")
        
        # Set default values for testing if no saved credentials
        self.username_entry.insert(0, "admin")
        self.password_entry.insert(0, "password")

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
            self.logger.info("Login attempt ignored - authentication already in progress")
            return
            
        self.username = self.username_entry.get().strip()
        self.password = self.password_entry.get().strip()
        
        if not self.username or not self.password:
            self.logger.warning("Login attempt with empty credentials")
            self.update_status("Please fill in all fields", LoginTheme.TEXT_ERROR)
            return
            
        self.logger.info(f"Starting authentication for user: {self.username}")
        
        # Perform authentication asynchronously to avoid UI blocking
        self.set_auth_state(AuthenticationState.AUTHENTICATING)
        
        # Start authentication in background thread
        auth_thread = threading.Thread(target=self._authenticate_async, daemon=True)
        auth_thread.start()
        
        # Set up timeout monitoring
        self._setup_auth_timeout()

    def _authenticate_async(self) -> None:
        """Perform authentication in background thread."""
        import time
        auth_start_time = time.time()
        
        try:
            self.logger.info(f"Starting background authentication for user: {self.username}")
            
            # Update status to show progress
            if self.dialog and self.dialog.winfo_exists():
                self.dialog.after(0, lambda: self.update_status("Verifying credentials...", LoginTheme.ACCENT_BLUE))
            
            # Perform authentication (returns tuple: success, user_data, message)
            success, user_data, message = self.auth_manager.authenticate(self.username, self.password)
            
            auth_duration = time.time() - auth_start_time
            self.logger.info(f"Authentication completed in {auth_duration:.2f} seconds for user: {self.username}")
            
            # Store user data for successful logins
            if success and user_data:
                self.auth_result = AuthenticationResult(
                    success=True,
                    message=message,
                    username=self.username,
                    state=AuthenticationState.SUCCESS
                )
            
            # Schedule UI update on main thread
            if self.dialog and self.dialog.winfo_exists():
                self.dialog.after(0, lambda: self._on_auth_complete_thread_safe(success, message))
            
        except Exception as e:
            auth_duration = time.time() - auth_start_time
            self.logger.error(f"Background authentication error after {auth_duration:.2f} seconds: {e}")
            # Schedule error handling on main thread
            if self.dialog and self.dialog.winfo_exists():
                self.dialog.after(0, lambda: self._on_auth_complete_thread_safe(False, f"Authentication system error: {str(e)}"))
    
    def _setup_auth_timeout(self) -> None:
        """Set up authentication timeout monitoring."""
        # Set a longer timeout for authentication (30 seconds for slower systems)
        auth_timeout = 30000  # 30 seconds in milliseconds
        
        def auth_timeout_handler():
            """Handle authentication timeout."""
            if self.auth_state == AuthenticationState.AUTHENTICATING:
                self.logger.warning(f"Authentication timeout for user: {self.username}")
                self.set_auth_state(AuthenticationState.TIMEOUT)
                timeout_message = (
                    "Authentication is taking longer than expected. "
                    "This may be due to system load or network issues. "
                    "Please try again."
                )
                self._on_auth_complete_thread_safe(False, timeout_message)
        
        # Schedule timeout
        self.dialog.after(auth_timeout, auth_timeout_handler)
    
    def _on_auth_complete_thread_safe(self, success: bool, message: str = "") -> None:
        """Thread-safe wrapper for authentication completion."""
        try:
            # Only process if still in authenticating state (not timed out)
            if self.auth_state == AuthenticationState.AUTHENTICATING:
                self._on_auth_complete(success, message)
        except Exception as e:
            self.logger.error(f"Error in thread-safe auth completion: {e}")
    def _perform_authentication(self) -> None:
        """Legacy synchronous authentication method - kept for compatibility."""
        self.logger.warning("Using legacy synchronous authentication - consider using async method")
        self._authenticate_async()

    def _authenticate(self) -> None:
        """Perform authentication in separate thread - DEPRECATED."""
        # This method is now deprecated in favor of synchronous authentication
        pass

    def _on_auth_complete(self, success: bool, message: str = "") -> None:
        """Handle authentication completion on main thread."""
        try:
            if not self.dialog or not self.dialog.winfo_exists():
                self.logger.warning("Dialog no longer exists in auth completion")
                return
                
            # Re-enable UI elements first
            self._re_enable_ui()
                
            if success:
                self.logger.info(f"Authentication successful for user: {self.username}")
                self.set_auth_state(AuthenticationState.SUCCESS)
                self.update_status(message or "Authentication successful!", LoginTheme.TEXT_SUCCESS)
                self.save_credentials()
                self.result = True
                
                # Close dialog after brief delay
                try:
                    self.dialog.after(1000, self._safe_destroy_dialog)
                except (tk.TclError, RuntimeError) as e:
                    self.logger.warning(f"Cannot schedule dialog destruction: {e}")
                    self._safe_destroy_dialog()  # Try to destroy immediately
            else:
                self.logger.warning(f"Authentication failed for user: {self.username} - {message}")
                self.set_auth_state(AuthenticationState.FAILED)
                self.update_status(message or "Authentication failed. Please try again.", LoginTheme.TEXT_ERROR)
                if self.password_entry and self.password_entry.winfo_exists():
                    self.password_entry.delete(0, 'end')
                    self.password_entry.focus()
                    
        except Exception as e:
            self.logger.error(f"Error in auth completion handler: {e}")
    
    def _re_enable_ui(self) -> None:
        """Re-enable UI elements after authentication."""
        try:
            if self.login_button and self.login_button.winfo_exists():
                self.login_button.configure(
                    text=UIText.SIGN_IN_BUTTON if THEME_AVAILABLE else "Sign In",
                    state="normal"
                )
            if self.cancel_button and self.cancel_button.winfo_exists():
                self.cancel_button.configure(state="normal")
            if self.username_entry and self.username_entry.winfo_exists():
                self.username_entry.configure(state="normal")
            if self.password_entry and self.password_entry.winfo_exists():
                self.password_entry.configure(state="normal")
        except (tk.TclError, RuntimeError) as e:
            self.logger.warning(f"Error re-enabling UI: {e}")

    def _safe_destroy_dialog(self) -> None:
        """Safely destroy the dialog with error handling."""
        try:
            if self.dialog and self.dialog.winfo_exists():
                self.dialog.destroy()
        except (tk.TclError, RuntimeError) as e:
            self.logger.warning(f"Error destroying dialog: {e}")

    def _on_auth_error(self, error_message: str) -> None:
        """Handle authentication error on main thread."""
        try:
            if not self.dialog or not self.dialog.winfo_exists():
                self.logger.warning("Dialog no longer exists in auth error handler")
                return
                
            self.set_auth_state(AuthenticationState.FAILED)
            self.update_status(f"Error: {error_message}", LoginTheme.TEXT_ERROR)
            
        except Exception as e:
            self.logger.error(f"Error in auth error handler: {e}")

    def cancel(self) -> None:
        """Handle cancel button click."""
        self.result = False
        self._safe_destroy_dialog()

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
