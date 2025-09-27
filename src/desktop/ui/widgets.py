#!/usr/bin/env python3
"""
TalkBridge Desktop - Custom Widgets
===================================

Custom composite widgets that combine multiple UI elements into reusable components.
These widgets maintain consistent styling and behavior across the application.

Author: TalkBridge Team  
Date: 2025-01-26
Version: 1.0
"""

import logging
from typing import Any, Callable, Dict, List, Optional, Union

# Try to import customtkinter for UI components
try:
    import customtkinter as ctk
    import tkinter as tk
    CUSTOMTKINTER_AVAILABLE = True
except ImportError:
    CUSTOMTKINTER_AVAILABLE = False
    ctk = None
    tk = None

from .theme import ColorPalette, Typography, Spacing, Dimensions
from .controls import create_frame, create_label, create_button, create_entry

logger = logging.getLogger(__name__)

class StatusIndicator:
    """
    A status indicator widget with colored dot and text.
    Shows status states like active, inactive, error, warning.
    """
    
    def __init__(self, parent: Any, text: str = "", status: str = "inactive"):
        """
        Initialize status indicator.
        
        Args:
            parent: Parent widget
            text: Status text to display
            status: Status type ("active", "inactive", "error", "warning")
        """
        self.parent = parent
        self.status = status
        self.text = text
        
        # Status color mapping
        self.status_colors = {
            "active": ColorPalette.SUCCESS,
            "inactive": ColorPalette.TEXT_TERTIARY,
            "error": ColorPalette.ERROR,
            "warning": ColorPalette.WARNING,
            "info": ColorPalette.INFO
        }
        
        # UI components
        self.container = None
        self.status_dot = None
        self.status_label = None
        
        self._create_widget()
    
    def _create_widget(self):
        """Create the status indicator widget."""
        if not CUSTOMTKINTER_AVAILABLE:
            logger.warning("CustomTkinter not available")
            return
        
        # Main container
        self.container = create_frame(self.parent, variant="transparent")
        if self.container is None:
            return
        
        # Status dot
        dot_color = self.status_colors.get(self.status, ColorPalette.TEXT_TERTIARY)
        self.status_dot = create_label(
            self.container, 
            text="●", 
            variant="body"
        )
        if self.status_dot is not None:
            self.status_dot.configure(text_color=dot_color)
            self.status_dot.pack(side="left", padx=(0, Spacing.XS))
        
        # Status text
        self.status_label = create_label(
            self.container,
            text=self.text,
            variant="body"
        )
        if self.status_label is not None:
            self.status_label.pack(side="left")
    
    def update_status(self, status: str, text: Optional[str] = None):
        """
        Update the status indicator.
        
        Args:
            status: New status type
            text: Optional new text
        """
        self.status = status
        if text is not None:
            self.text = text
        
        # Update dot color
        if self.status_dot is not None:
            dot_color = self.status_colors.get(status, ColorPalette.TEXT_TERTIARY)
            self.status_dot.configure(text_color=dot_color)
        
        # Update text
        if self.status_label is not None and text is not None:
            self.status_label.configure(text=text)
    
    def pack(self, **kwargs):
        """Pack the container widget."""
        if self.container is not None:
            self.container.pack(**kwargs)
    
    def pack_forget(self):
        """Hide the container widget."""
        if self.container is not None:
            self.container.pack_forget()

class ActionButton:
    """
    An enhanced button with icon, text, and optional badge/indicator.
    Supports different visual states and loading indicators.
    """
    
    def __init__(
        self, 
        parent: Any, 
        text: str,
        command: Optional[Callable] = None,
        icon: Optional[str] = None,
        variant: str = "primary",
        badge_text: Optional[str] = None,
        loading: bool = False
    ):
        """
        Initialize action button.
        
        Args:
            parent: Parent widget
            text: Button text
            command: Click handler
            icon: Optional icon/emoji
            variant: Button style variant
            badge_text: Optional badge text
            loading: Whether to show loading state
        """
        self.parent = parent
        self.text = text
        self.command = command
        self.icon = icon
        self.variant = variant
        self.badge_text = badge_text
        self.loading = loading
        self.enabled = True
        
        # UI components
        self.container = None
        self.button = None
        self.badge_label = None
        
        self._create_widget()
    
    def _create_widget(self):
        """Create the action button widget."""
        if not CUSTOMTKINTER_AVAILABLE:
            logger.warning("CustomTkinter not available")
            return
        
        # Main container
        self.container = create_frame(self.parent, variant="transparent")
        if self.container is None:
            return
        
        # Button text with icon
        button_text = f"{self.icon} {self.text}" if self.icon else self.text
        if self.loading:
            button_text = f"⟳ {self.text}"
        
        # Main button
        self.button = create_button(
            self.container,
            text=button_text,
            command=self._on_click,
            variant=self.variant
        )
        if self.button is not None:
            self.button.pack(side="left")
        
        # Badge
        if self.badge_text:
            self.badge_label = create_label(
                self.container,
                text=self.badge_text,
                variant="caption"
            )
            if self.badge_label is not None:
                self.badge_label.configure(
                    fg_color=ColorPalette.ERROR,
                    text_color=ColorPalette.TEXT_PRIMARY,
                    corner_radius=8,
                    width=20,
                    height=20
                )
                self.badge_label.pack(side="left", padx=(Spacing.XS, 0))
    
    def _on_click(self):
        """Handle button click."""
        if self.enabled and not self.loading and self.command:
            self.command()
    
    def set_loading(self, loading: bool):
        """Set loading state."""
        self.loading = loading
        if self.button is not None:
            button_text = f"⟳ {self.text}" if loading else f"{self.icon} {self.text}" if self.icon else self.text
            self.button.configure(text=button_text)
    
    def set_enabled(self, enabled: bool):
        """Set enabled state."""
        self.enabled = enabled
        if self.button is not None:
            self.button.configure(state="normal" if enabled else "disabled")
    
    def update_badge(self, badge_text: Optional[str]):
        """Update badge text."""
        self.badge_text = badge_text
        if self.badge_label is not None:
            if badge_text:
                self.badge_label.configure(text=badge_text)
                self.badge_label.pack(side="left", padx=(Spacing.XS, 0))
            else:
                self.badge_label.pack_forget()
    
    def pack(self, **kwargs):
        """Pack the container widget."""
        if self.container is not None:
            self.container.pack(**kwargs)

class InfoCard:
    """
    An information card with title, content, and optional actions.
    Used for displaying structured information with consistent styling.
    """
    
    def __init__(
        self,
        parent: Any,
        title: str,
        content: str = "",
        icon: Optional[str] = None,
        actions: Optional[List[Dict[str, Any]]] = None,
        variant: str = "default"
    ):
        """
        Initialize info card.
        
        Args:
            parent: Parent widget
            title: Card title
            content: Card content text
            icon: Optional icon/emoji
            actions: Optional list of action button configs
            variant: Card style variant
        """
        self.parent = parent
        self.title = title
        self.content = content
        self.icon = icon
        self.actions = actions or []
        self.variant = variant
        
        # UI components
        self.container = None
        self.title_label = None
        self.content_label = None
        self.action_buttons = []
        
        self._create_widget()
    
    def _create_widget(self):
        """Create the info card widget."""
        if not CUSTOMTKINTER_AVAILABLE:
            logger.warning("CustomTkinter not available")
            return
        
        # Main card container
        self.container = create_frame(self.parent, variant="card")
        if self.container is None:
            return
        
        # Content area
        content_frame = create_frame(self.container, variant="transparent")
        if content_frame is not None:
            content_frame.pack(fill="both", expand=True, padx=Spacing.LG, pady=Spacing.LG)
            
            # Header with icon and title
            header_frame = create_frame(content_frame, variant="transparent")
            if header_frame is not None:
                header_frame.pack(fill="x", pady=(0, Spacing.MD))
                
                # Icon
                if self.icon:
                    icon_label = create_label(header_frame, text=self.icon, variant="heading")
                    if icon_label is not None:
                        icon_label.pack(side="left", padx=(0, Spacing.SM))
                
                # Title
                self.title_label = create_label(header_frame, text=self.title, variant="heading")
                if self.title_label is not None:
                    self.title_label.pack(side="left")
            
            # Content
            if self.content:
                self.content_label = create_label(content_frame, text=self.content, variant="body")
                if self.content_label is not None:
                    self.content_label.pack(fill="x", pady=(0, Spacing.MD))
            
            # Actions
            if self.actions:
                actions_frame = create_frame(content_frame, variant="transparent")
                if actions_frame is not None:
                    actions_frame.pack(fill="x")
                    
                    for action_config in self.actions:
                        action_btn = create_button(
                            actions_frame,
                            text=action_config.get("text", "Action"),
                            command=action_config.get("command"),
                            variant=action_config.get("variant", "secondary")
                        )
                        if action_btn is not None:
                            action_btn.pack(side="left", padx=(0, Spacing.SM))
                            self.action_buttons.append(action_btn)
    
    def update_content(self, title: Optional[str] = None, content: Optional[str] = None):
        """Update card content."""
        if title is not None:
            self.title = title
            if self.title_label is not None:
                self.title_label.configure(text=title)
        
        if content is not None:
            self.content = content
            if self.content_label is not None:
                self.content_label.configure(text=content)
    
    def pack(self, **kwargs):
        """Pack the container widget."""
        if self.container is not None:
            self.container.pack(**kwargs)

class ProgressIndicator:
    """
    A progress indicator with bar and optional percentage text.
    Shows progress states for operations.
    """
    
    def __init__(
        self,
        parent: Any,
        label: str = "",
        show_percentage: bool = True,
        indeterminate: bool = False
    ):
        """
        Initialize progress indicator.
        
        Args:
            parent: Parent widget
            label: Progress label text
            show_percentage: Whether to show percentage text
            indeterminate: Whether to show indeterminate progress
        """
        self.parent = parent
        self.label = label
        self.show_percentage = show_percentage
        self.indeterminate = indeterminate
        self.progress_value = 0.0
        
        # UI components
        self.container = None
        self.label_widget = None
        self.progress_bar = None
        self.percentage_label = None
        
        self._create_widget()
    
    def _create_widget(self):
        """Create the progress indicator widget."""
        if not CUSTOMTKINTER_AVAILABLE:
            logger.warning("CustomTkinter not available")
            return
        
        # Main container
        self.container = create_frame(self.parent, variant="transparent")
        if self.container is None:
            return
        
        # Label
        if self.label:
            self.label_widget = create_label(self.container, text=self.label, variant="body")
            if self.label_widget is not None:
                self.label_widget.pack(anchor="w", pady=(0, Spacing.XS))
        
        # Progress bar container
        progress_container = create_frame(self.container, variant="transparent")
        if progress_container is not None:
            progress_container.pack(fill="x")
            
            # Progress bar
            if ctk is not None:
                if self.indeterminate:
                    self.progress_bar = ctk.CTkProgressBar(
                        progress_container,
                        mode="indeterminate",
                        progress_color=ColorPalette.ACCENT_PRIMARY
                    )
                    self.progress_bar.start()
                else:
                    self.progress_bar = ctk.CTkProgressBar(
                        progress_container,
                        progress_color=ColorPalette.ACCENT_PRIMARY
                    )
                    self.progress_bar.set(0)
                
                self.progress_bar.pack(side="left", fill="x", expand=True)
            
            # Percentage label
            if self.show_percentage and not self.indeterminate:
                self.percentage_label = create_label(progress_container, text="0%", variant="caption")
                if self.percentage_label is not None:
                    self.percentage_label.pack(side="right", padx=(Spacing.SM, 0))
    
    def set_progress(self, value: float):
        """
        Set progress value (0.0 to 1.0).
        
        Args:
            value: Progress value between 0.0 and 1.0
        """
        if self.indeterminate:
            return
        
        self.progress_value = max(0.0, min(1.0, value))
        
        if self.progress_bar is not None:
            self.progress_bar.set(self.progress_value)
        
        if self.percentage_label is not None:
            percentage = int(self.progress_value * 100)
            self.percentage_label.configure(text=f"{percentage}%")
    
    def pack(self, **kwargs):
        """Pack the container widget."""
        if self.container is not None:
            self.container.pack(**kwargs)

class AuthenticationDialog:
    """
    A complete authentication dialog widget that handles login workflows.
    Provides modern UI with validation, state management, and proper error handling.
    """
    
    def __init__(self, parent: Any, title: str = "TalkBridge - Login"):
        """
        Initialize authentication dialog.
        
        Args:
            parent: Parent window
            title: Dialog window title
        """
        self.parent = parent
        self.title = title
        self.logger = logging.getLogger("AuthenticationDialog")
        
        # Dialog state
        self.result = False
        self.username = ""
        self.password = ""
        self.remember_credentials = False
        
        # UI elements (will be populated by layout)
        self.dialog = None
        self.ui_elements: Dict[str, Any] = {}
        
        # Authentication manager
        try:
            from ...auth.auth_manager import AuthManager
            self.auth_manager = AuthManager()
        except ImportError:
            self.logger.warning("AuthManager not available")
            self.auth_manager = None
    
    def show(self) -> tuple[bool, str, str]:
        """
        Show the authentication dialog and return result.
        
        Returns:
            Tuple of (success, username, password)
        """
        if not CUSTOMTKINTER_AVAILABLE:
            self.logger.error("CustomTkinter not available")
            return False, "", ""
        
        try:
            from .controls import create_dialog_window
            from .layouts import setup_auth_dialog_layout
            
            # Create dialog window
            self.dialog = create_dialog_window(
                self.parent,
                title=self.title,
                width=480,
                height=600
            )
            
            if not self.dialog:
                return False, "", ""
            
            # Set up dialog layout
            content_config = {
                'app_name': 'TalkBridge Desktop',
                'app_subtitle': 'AI-Powered Communication Platform',
                'logo_text': 'AI',
                'form_title': 'Sign In',
                'username_label': 'Username:',
                'password_label': 'Password:',
                'remember_text': 'Remember me',
                'login_text': 'Sign In',
                'cancel_text': 'Cancel',
                'status_text': 'Ready to sign in'
            }
            
            ui_elements = setup_auth_dialog_layout(self.dialog, content_config)
            if not ui_elements:
                self.logger.error("Failed to set up dialog layout")
                return False, "", ""
            self.ui_elements = ui_elements
            
            # Connect event handlers
            self._setup_event_handlers()
            
            # Center and configure dialog
            self._center_dialog()
            self._configure_dialog_properties()
            
            # Load saved credentials if available
            self._load_saved_credentials()
            
            # Show dialog and wait for result
            self.dialog.deiconify()
            self.dialog.lift()
            self.dialog.attributes('-topmost', True)
            self.dialog.focus_force()
            self.dialog.grab_set()
            
            # Focus username entry after a short delay
            if self.ui_elements.get('username_entry'):
                self.dialog.after(100, lambda: self._safe_focus(self.ui_elements['username_entry']))
            
            # Wait for dialog to close
            self.dialog.wait_window()
            
            return self.result, self.username, self.password
            
        except Exception as e:
            self.logger.error(f"Error showing authentication dialog: {e}")
            return False, "", ""
    
    def _setup_event_handlers(self):
        """Set up event handlers for dialog interaction."""
        try:
            # Button event handlers
            if self.ui_elements.get('login_button'):
                self.ui_elements['login_button'].configure(command=self._handle_login)
            
            if self.ui_elements.get('cancel_button'):
                self.ui_elements['cancel_button'].configure(command=self._handle_cancel)
            
            # Entry field event handlers
            if self.ui_elements.get('username_entry'):
                self.ui_elements['username_entry'].bind("<KeyRelease>", self._on_input_changed)
                self.ui_elements['username_entry'].bind("<Return>", lambda e: self._handle_login())
            
            if self.ui_elements.get('password_entry'):
                self.ui_elements['password_entry'].bind("<KeyRelease>", self._on_input_changed)
                self.ui_elements['password_entry'].bind("<Return>", lambda e: self._handle_login())
            
            # Dialog close handler
            if self.dialog:
                self.dialog.protocol("WM_DELETE_WINDOW", self._handle_cancel)
            
            # Initial validation
            self._validate_inputs()
            
        except Exception as e:
            self.logger.error(f"Error setting up event handlers: {e}")
    
    def _center_dialog(self):
        """Center the dialog on parent or screen."""
        try:
            if not self.dialog:
                return
                
            if self.parent and hasattr(self.parent, 'winfo_viewable') and self.parent.winfo_viewable():
                # Center on parent
                parent_x = self.parent.winfo_x()
                parent_y = self.parent.winfo_y()
                parent_width = self.parent.winfo_width()
                parent_height = self.parent.winfo_height()
                
                dialog_x = parent_x + (parent_width - 480) // 2
                dialog_y = parent_y + (parent_height - 600) // 2
                
                self.dialog.geometry(f"480x600+{dialog_x}+{dialog_y}")
            else:
                # Center on screen
                screen_width = self.dialog.winfo_screenwidth()
                screen_height = self.dialog.winfo_screenheight()
                
                dialog_x = (screen_width - 480) // 2
                dialog_y = (screen_height - 600) // 2
                
                self.dialog.geometry(f"480x600+{dialog_x}+{dialog_y}")
                
        except Exception as e:
            self.logger.warning(f"Error centering dialog: {e}")
    
    def _configure_dialog_properties(self):
        """Configure dialog window properties."""
        try:
            if self.dialog and hasattr(self.dialog, 'winfo_exists') and self.dialog.winfo_exists():
                self.dialog.resizable(False, False)
                if self.parent and hasattr(self.parent, 'winfo_exists') and self.parent.winfo_exists():
                    self.dialog.transient(self.parent)
        except Exception as e:
            self.logger.warning(f"Error configuring dialog properties: {e}")
    
    def _on_input_changed(self, event=None):
        """Handle input field changes."""
        self._validate_inputs()
    
    def _validate_inputs(self):
        """Validate input fields and update UI accordingly."""
        try:
            username_entry = self.ui_elements.get('username_entry')
            password_entry = self.ui_elements.get('password_entry')
            login_button = self.ui_elements.get('login_button')
            status_label = self.ui_elements.get('status_label')
            
            if not username_entry or not password_entry:
                return
            
            username = username_entry.get().strip()
            password = password_entry.get().strip()
            
            is_valid = len(username) >= 3 and len(password) >= 1
            
            # Update login button state
            if login_button:
                login_button.configure(state="normal" if is_valid else "disabled")
            
            # Update status
            if status_label and hasattr(status_label, 'update_status'):
                if is_valid:
                    status_label.update_status("Ready to sign in", ColorPalette.TEXT_SECONDARY)
                elif not username:
                    status_label.update_status("Please enter your username", ColorPalette.ERROR)
                elif len(username) < 3:
                    status_label.update_status("Username must be at least 3 characters", ColorPalette.ERROR)
                elif not password:
                    status_label.update_status("Please enter your password", ColorPalette.ERROR)
                    
        except Exception as e:
            self.logger.error(f"Error validating inputs: {e}")
    
    def _handle_login(self):
        """Handle login button click."""
        try:
            username_entry = self.ui_elements.get('username_entry')
            password_entry = self.ui_elements.get('password_entry')
            remember_checkbox = self.ui_elements.get('remember_checkbox')
            
            if not username_entry or not password_entry:
                return
            
            self.username = username_entry.get().strip()
            self.password = password_entry.get().strip()
            
            if remember_checkbox and hasattr(remember_checkbox, 'get'):
                self.remember_credentials = remember_checkbox.get()
            
            # Validate credentials
            if len(self.username) < 3:
                self._update_status("Username must be at least 3 characters", ColorPalette.ERROR)
                return
            
            if len(self.password) < 1:
                self._update_status("Please enter your password", ColorPalette.ERROR)
                return
            
            # Update UI for authentication
            self._set_authenticating_state()
            
            # Perform authentication (simplified for now)
            success = self._authenticate_user(self.username, self.password)
            
            if success:
                self._handle_auth_success()
            else:
                self._handle_auth_failure("Invalid username or password")
                
        except Exception as e:
            self.logger.error(f"Error handling login: {e}")
            self._handle_auth_failure(f"Authentication error: {e}")
    
    def _handle_cancel(self):
        """Handle cancel button click or dialog close."""
        self.logger.info("Authentication cancelled by user")
        self.result = False
        self._safe_destroy_dialog()
    
    def _authenticate_user(self, username: str, password: str) -> bool:
        """
        Authenticate user credentials.
        
        Args:
            username: Username to authenticate
            password: Password to authenticate
            
        Returns:
            True if authentication successful, False otherwise
        """
        try:
            if self.auth_manager:
                # Use actual authentication manager
                try:
                    auth_result = self.auth_manager.authenticate(username, password)
                    # Handle tuple return type (success, user_info, message)
                    if isinstance(auth_result, tuple) and len(auth_result) >= 1:
                        return bool(auth_result[0])
                    else:
                        return bool(auth_result)
                except Exception as e:
                    self.logger.error(f"Auth manager error: {e}")
                    return False
            else:
                # Fallback simple authentication for demo
                return len(username) >= 3 and len(password) >= 1
        except Exception as e:
            self.logger.error(f"Authentication error: {e}")
            return False
    
    def _set_authenticating_state(self):
        """Set UI to authenticating state."""
        try:
            login_button = self.ui_elements.get('login_button')
            username_entry = self.ui_elements.get('username_entry')
            password_entry = self.ui_elements.get('password_entry')
            
            if login_button:
                login_button.configure(text="Signing in...", state="disabled")
            if username_entry:
                username_entry.configure(state="disabled")
            if password_entry:
                password_entry.configure(state="disabled")
                
            self._update_status("Authenticating...", ColorPalette.ACCENT_PRIMARY)
            
        except Exception as e:
            self.logger.error(f"Error setting authenticating state: {e}")
    
    def _handle_auth_success(self):
        """Handle successful authentication."""
        try:
            self._update_status("Authentication successful!", ColorPalette.SUCCESS)
            self.result = True
            
            # Save credentials if requested
            if self.remember_credentials:
                self._save_credentials()
            
            # Close dialog after brief delay
            if self.dialog:
                self.dialog.after(1000, self._safe_destroy_dialog)
                
        except Exception as e:
            self.logger.error(f"Error handling auth success: {e}")
    
    def _handle_auth_failure(self, message: str):
        """Handle authentication failure."""
        try:
            self._update_status(message, ColorPalette.ERROR)
            self._re_enable_ui()
            
            # Clear password and refocus
            password_entry = self.ui_elements.get('password_entry')
            if password_entry:
                password_entry.delete(0, 'end')
                self._safe_focus(password_entry)
                
        except Exception as e:
            self.logger.error(f"Error handling auth failure: {e}")
    
    def _re_enable_ui(self):
        """Re-enable UI elements after authentication."""
        try:
            login_button = self.ui_elements.get('login_button')
            username_entry = self.ui_elements.get('username_entry')
            password_entry = self.ui_elements.get('password_entry')
            
            if login_button:
                login_button.configure(text="Sign In", state="normal")
            if username_entry:
                username_entry.configure(state="normal")
            if password_entry:
                password_entry.configure(state="normal")
                
        except Exception as e:
            self.logger.error(f"Error re-enabling UI: {e}")
    
    def _update_status(self, message: str, color: Optional[str] = None):
        """Update status message."""
        try:
            status_label = self.ui_elements.get('status_label')
            if status_label and hasattr(status_label, 'update_status'):
                status_label.update_status(message, color)
        except Exception as e:
            self.logger.error(f"Error updating status: {e}")
    
    def _safe_focus(self, widget):
        """Safely set focus to a widget."""
        try:
            if widget and hasattr(widget, 'winfo_exists') and widget.winfo_exists():
                widget.focus()
        except Exception as e:
            self.logger.debug(f"Could not focus widget: {e}")
    
    def _safe_destroy_dialog(self):
        """Safely destroy the dialog."""
        try:
            if self.dialog and hasattr(self.dialog, 'winfo_exists') and self.dialog.winfo_exists():
                self.dialog.destroy()
        except Exception as e:
            self.logger.warning(f"Error destroying dialog: {e}")
    
    def _load_saved_credentials(self):
        """Load saved credentials if available."""
        # Implementation would load from secure storage
        pass
    
    def _save_credentials(self):
        """Save credentials securely."""
        # Implementation would save to secure storage
        pass

class ConfirmationDialog:
    """Standardized confirmation dialog widget for Yes/No decision prompts.
    
    This widget provides a consistent confirmation dialog interface that follows
    the centralized theme system. It handles common confirmation workflows
    like logout confirmations, delete confirmations, warning prompts, etc.
    
    Key Features:
    - Centralized styling through theme system
    - Boolean result handling (True/False/None)
    - Customizable messages and button text
    - Icon support for visual feedback
    - Automatic centering and focus management
    - Consistent error handling and logging
    
    Example Usage:
        dialog = ConfirmationDialog(
            parent=main_window,
            title="Logout Confirmation",
            message="Are you sure you want to logout?",
            icon="⚠️",
            icon_color=ColorPalette.WARNING
        )
        result = dialog.show()
        if result is True:
            # User confirmed
            perform_logout()
        elif result is False:
            # User cancelled
            logger.info("Logout cancelled by user")
        # result is None if dialog was closed without decision
    """
    
    def __init__(self, parent: Any, title: str = "Confirmation", message: str = "Are you sure?",
                 confirm_text: str = "Yes", cancel_text: str = "No", 
                 icon: str = "ℹ️", icon_color: Optional[str] = None,
                 dialog_width: int = 400, dialog_height: int = 200):
        """Initialize the confirmation dialog.
        
        Args:
            parent: Parent window widget
            title: Dialog window title
            message: Main confirmation message text
            confirm_text: Text for the confirmation button (default: "Yes")
            cancel_text: Text for the cancel button (default: "No")
            icon: Icon emoji or character to display (default: "ℹ️")
            icon_color: Color for the icon (uses theme default if None)
            dialog_width: Dialog width in pixels (default: 400)
            dialog_height: Dialog height in pixels (default: 200)
        """
        self.parent = parent
        self.title = title
        self.message = message
        self.confirm_text = confirm_text
        self.cancel_text = cancel_text
        self.icon = icon
        self.icon_color = icon_color
        self.dialog_width = dialog_width
        self.dialog_height = dialog_height
        
        # Dialog state
        self.dialog: Optional[Any] = None
        self.result: Optional[bool] = None
        self._dialog_active = False
        
        logger.debug(f"Initialized ConfirmationDialog: '{title}'")
    
    def _create_dialog_window(self) -> Optional[Any]:
        """Create the main dialog window."""
        try:
            from .controls import create_confirmation_dialog
            
            dialog = create_confirmation_dialog(
                self.parent,
                title=self.title,
                width=self.dialog_width,
                height=self.dialog_height
            )
            
            if dialog:
                # Configure dialog properties
                dialog.transient(self.parent)
                dialog.grab_set()  # Make modal
                dialog.protocol("WM_DELETE_WINDOW", self._on_dialog_close)
                
                # Center the dialog
                self._center_dialog(dialog)
                logger.debug(f"Created confirmation dialog window: '{self.title}'")
            
            return dialog
        except Exception as e:
            logger.error(f"Failed to create confirmation dialog window: {e}")
            return None
    
    def _setup_dialog_content(self) -> bool:
        """Set up the dialog content using centralized layouts."""
        if not self.dialog:
            return False
        
        try:
            from .controls import create_frame
            from .layouts import (
                setup_confirmation_dialog_layout,
                create_warning_header,
                create_message_body,
                create_confirmation_buttons_layout
            )
            
            # Main content frame
            content_frame = create_frame(self.dialog, variant="transparent")
            if not content_frame:
                return False
            
            # Setup layout
            setup_confirmation_dialog_layout(self.dialog, content_frame)
            
            # Header with icon and title
            header_frame = create_warning_header(
                content_frame,
                title="",  # Title already in dialog window
                icon=self.icon,
                icon_color=self.icon_color
            )
            if header_frame:
                header_frame.pack(pady=(0, Spacing.MD))
            
            # Message body
            message_label = create_message_body(
                content_frame,
                message=self.message,
                font_size=12
            )
            if message_label:
                message_label.pack(pady=(0, Spacing.LG))
            
            # Button section
            confirm_btn, cancel_btn, button_frame = create_confirmation_buttons_layout(
                content_frame,
                confirm_text=self.confirm_text,
                cancel_text=self.cancel_text,
                confirm_command=self._on_confirm,
                cancel_command=self._on_cancel
            )
            
            if button_frame:
                button_frame.pack(side="bottom", fill="x")
            
            # Store button references for focus management
            self.confirm_button = confirm_btn
            self.cancel_button = cancel_btn
            
            logger.debug("Successfully setup confirmation dialog content")
            return True
        except Exception as e:
            logger.error(f"Failed to setup confirmation dialog content: {e}")
            return False
    
    def _center_dialog(self, dialog: Any) -> None:
        """Center the dialog on the parent window."""
        try:
            dialog.update_idletasks()  # Ensure geometry is calculated
            
            # Get parent window position and size
            if self.parent and hasattr(self.parent, 'winfo_x'):
                parent_x = self.parent.winfo_x()
                parent_y = self.parent.winfo_y()
                parent_width = self.parent.winfo_width()
                parent_height = self.parent.winfo_height()
                
                # Calculate center position
                x = parent_x + (parent_width // 2) - (self.dialog_width // 2)
                y = parent_y + (parent_height // 2) - (self.dialog_height // 2)
                
                dialog.geometry(f"{self.dialog_width}x{self.dialog_height}+{x}+{y}")
                logger.debug(f"Centered dialog at ({x}, {y})")
        except Exception as e:
            logger.warning(f"Could not center dialog: {e}")
    
    def _on_confirm(self) -> None:
        """Handle confirmation button click."""
        logger.debug("User confirmed action")
        self.result = True
        self._close_dialog()
    
    def _on_cancel(self) -> None:
        """Handle cancel button click."""
        logger.debug("User cancelled action")
        self.result = False
        self._close_dialog()
    
    def _on_dialog_close(self) -> None:
        """Handle dialog window close event."""
        logger.debug("Dialog closed without decision")
        self.result = None
        self._close_dialog()
    
    def _close_dialog(self) -> None:
        """Close the dialog and clean up."""
        if self.dialog and self._dialog_active:
            try:
                self.dialog.grab_release()
                self.dialog.destroy()
                self._dialog_active = False
                logger.debug("Confirmation dialog closed")
            except Exception as e:
                logger.error(f"Error closing confirmation dialog: {e}")
    
    def show(self) -> Optional[bool]:
        """Show the confirmation dialog and return the user's decision.
        
        Returns:
            True if user confirmed
            False if user cancelled
            None if dialog was closed without decision or error occurred
        """
        if not CUSTOMTKINTER_AVAILABLE:
            logger.error("Cannot show confirmation dialog - CustomTkinter not available")
            return None
        
        if self._dialog_active:
            logger.warning("Confirmation dialog already active")
            return None
        
        try:
            # Create dialog
            self.dialog = self._create_dialog_window()
            if not self.dialog:
                return None
            
            # Setup content
            if not self._setup_dialog_content():
                self._close_dialog()
                return None
            
            # Show dialog
            self._dialog_active = True
            self.dialog.focus()
            
            # Set default button focus
            if hasattr(self, 'cancel_button') and self.cancel_button:
                self.cancel_button.focus()
            
            # Wait for user interaction
            self.dialog.wait_window()
            
            logger.info(f"Confirmation dialog result: {self.result}")
            return self.result
            
        except Exception as e:
            logger.error(f"Failed to show confirmation dialog: {e}")
            self._close_dialog()
            return None

# Export custom widgets
__all__ = [
    "StatusIndicator",
    "ActionButton", 
    "InfoCard",
    "ProgressIndicator",
    "AuthenticationDialog",
    "ConfirmationDialog"
]