#!/usr/bin/env python3
"""
TalkBridge Desktop - Main Window (CustomTkinter)
================================================

Main window with integrated tabs for chat, avatar and settings.

Author: TalkBridge Team
Date: 2025-09-03
Version: 2.0

Requirements:
- customtkinter
- tkinter
======================================================================
Functions:
- __init__: Initialize the main window with tabs
- setup_ui: Sets up the main interface with tab widget
- create_menu_bar: Creates the menu bar
- create_status_bar: Creates the status bar
- configure_window: Configures window properties
- center_window: Centers the window on the screen
- connect_signals: Connects component signals
- show_logout_dialog: Shows logout confirmation dialog
- logout: Handles user logout
======================================================================
"""

import logging
from typing import Optional
from pathlib import Path
import tkinter as tk
import customtkinter as ctk

# Import the tab components
from src.desktop.components.chat_tab import ChatTab
from src.desktop.components.avatar_tab import AvatarTab  
from src.desktop.components.settings_tab import SettingsTab


class MainWindowTheme:
    """Theme configuration for the main window."""
    
    # Base colors
    BACKGROUND_MAIN = "#1e1e1e"
    BACKGROUND_SECONDARY = "#2d2d2d"
    BACKGROUND_ELEVATED = "#3c3c3c"
    
    # Text colors
    TEXT_PRIMARY = "#ffffff"
    TEXT_SECONDARY = "#cccccc"
    TEXT_HINT = "#888888"
    
    # Accent colors
    ACCENT_BLUE = "#0078d4"
    ACCENT_BLUE_HOVER = "#106ebe"
    ACCENT_RED = "#f44336"
    ACCENT_RED_HOVER = "#d32f2f"
    
    # Tab colors
    TAB_SELECTED = "#3c3c3c"
    TAB_UNSELECTED = "#2d2d2d"
    TAB_HOVER = "#4a4a4a"


class UIConstants:
    """UI layout constants for the main window."""
    
    # Window dimensions
    MIN_WIDTH = 1200
    MIN_HEIGHT = 800
    DEFAULT_WIDTH = 1400
    DEFAULT_HEIGHT = 900
    
    # Spacing
    MARGIN = 10
    TITLE_MARGIN = 15
    BUTTON_SPACING = 10
    
    # Component heights
    TITLE_HEIGHT = 50
    STATUS_HEIGHT = 30
    BUTTON_HEIGHT = 35
    
    # Fonts
    TITLE_FONT_SIZE = 18
    BUTTON_FONT_SIZE = 12


class MainWindow:
    """
    Enhanced main window of TalkBridge Desktop with integrated tabs using CustomTkinter.

    Features:
    - Modern tabbed interface with Chat, Avatar, and Settings tabs
    - Comprehensive theming and visual feedback
    - Enhanced title bar with branding and logout functionality
    - Status bar with real-time information
    - Responsive design with proper window management
    - Keyboard shortcuts and accessibility features
    """

    def __init__(self, state_manager=None, core_bridge=None, parent=None):
        """Initialize the enhanced main window."""
        self.state_manager = state_manager
        self.core_bridge = core_bridge
        self.parent = parent
        self.logger = logging.getLogger("talkbridge.desktop.mainwindow")

        # Window reference
        self.window: Optional[ctk.CTk] = None
        
        # UI Components
        self.main_frame: Optional[ctk.CTkFrame] = None
        self.title_frame: Optional[ctk.CTkFrame] = None
        self.title_label: Optional[ctk.CTkLabel] = None
        self.logout_button: Optional[ctk.CTkButton] = None
        self.tabview: Optional[ctk.CTkTabview] = None
        self.status_frame: Optional[ctk.CTkFrame] = None
        self.status_label: Optional[ctk.CTkLabel] = None
        
        # Tab components
        self.chat_tab: Optional[ChatTab] = None
        self.avatar_tab: Optional[AvatarTab] = None
        self.settings_tab: Optional[SettingsTab] = None
        
        # Window state
        self.is_fullscreen = False
        self.normal_geometry = None
        
        try:
            self.setup_window()
            self.setup_ui()
            self.create_tabs()
            self.create_status_bar()
            self.configure_window()
            self.logger.info("Enhanced main window initialized successfully")
        except Exception as e:
            self.logger.error(f"Error initializing main window: {e}")
            raise

    def setup_window(self):
        """Set up the main window."""
        if self.parent:
            self.window = ctk.CTkToplevel(self.parent)
        else:
            self.window = ctk.CTk()
        
        # Configure window
        self.window.title("TalkBridge Desktop - AI Communication Platform")
        self.window.geometry(f"{UIConstants.DEFAULT_WIDTH}x{UIConstants.DEFAULT_HEIGHT}")
        self.window.minsize(UIConstants.MIN_WIDTH, UIConstants.MIN_HEIGHT)
        
        # Apply main theme
        self.window.configure(fg_color=MainWindowTheme.BACKGROUND_MAIN)
        
        # Set appearance mode
        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("dark-blue")

    def setup_ui(self):
        """Set up the enhanced main user interface."""
        # Main container frame
        self.main_frame = ctk.CTkFrame(
            self.window,
            fg_color=MainWindowTheme.BACKGROUND_MAIN,
            corner_radius=0
        )
        self.main_frame.pack(fill="both", expand=True)
        
        # Title bar section
        self.create_title_bar()
        
        # Main content area will be created in create_tabs()

    def create_title_bar(self):
        """Create the enhanced title bar."""
        self.title_frame = ctk.CTkFrame(
            self.main_frame,
            fg_color=MainWindowTheme.BACKGROUND_SECONDARY,
            height=UIConstants.TITLE_HEIGHT,
            corner_radius=0
        )
        self.title_frame.pack(fill="x", padx=0, pady=0)
        self.title_frame.pack_propagate(False)
        
        # Title and branding
        title_container = ctk.CTkFrame(self.title_frame, fg_color="transparent")
        title_container.pack(side="left", fill="both", expand=True, padx=UIConstants.TITLE_MARGIN)
        
        # App icon and title
        self.title_label = ctk.CTkLabel(
            title_container,
            text="🤖 TalkBridge Desktop - AI Communication Platform",
            font=ctk.CTkFont(size=UIConstants.TITLE_FONT_SIZE, weight="bold"),
            text_color=MainWindowTheme.ACCENT_BLUE
        )
        self.title_label.pack(side="left", pady=UIConstants.MARGIN)
        
        # Right side controls
        controls_frame = ctk.CTkFrame(self.title_frame, fg_color="transparent")
        controls_frame.pack(side="right", padx=UIConstants.TITLE_MARGIN)
        
        # Window controls
        self.minimize_button = ctk.CTkButton(
            controls_frame,
            text="–",
            width=30,
            height=25,
            fg_color="transparent",
            text_color=MainWindowTheme.TEXT_SECONDARY,
            hover_color=MainWindowTheme.BACKGROUND_ELEVATED,
            font=ctk.CTkFont(size=16, weight="bold"),
            command=self.minimize_window
        )
        self.minimize_button.pack(side="left", padx=(0, 5))
        
        self.maximize_button = ctk.CTkButton(
            controls_frame,
            text="□",
            width=30,
            height=25,
            fg_color="transparent",
            text_color=MainWindowTheme.TEXT_SECONDARY,
            hover_color=MainWindowTheme.BACKGROUND_ELEVATED,
            font=ctk.CTkFont(size=12, weight="bold"),
            command=self.toggle_fullscreen
        )
        self.maximize_button.pack(side="left", padx=(0, 5))
        
        # Logout button
        self.logout_button = ctk.CTkButton(
            controls_frame,
            text="🔓 Logout",
            width=80,
            height=UIConstants.BUTTON_HEIGHT,
            fg_color=MainWindowTheme.ACCENT_RED,
            hover_color=MainWindowTheme.ACCENT_RED_HOVER,
            font=ctk.CTkFont(size=UIConstants.BUTTON_FONT_SIZE, weight="bold"),
            command=self.show_logout_dialog
        )
        self.logout_button.pack(side="left", padx=(UIConstants.BUTTON_SPACING, 0))

    def create_tabs(self):
        """Create the main tab interface."""
        # Tab container
        self.tabview = ctk.CTkTabview(
            self.main_frame,
            fg_color=MainWindowTheme.BACKGROUND_MAIN,
            segmented_button_fg_color=MainWindowTheme.BACKGROUND_SECONDARY,
            segmented_button_selected_color=MainWindowTheme.TAB_SELECTED,
            segmented_button_selected_hover_color=MainWindowTheme.TAB_HOVER,
            segmented_button_unselected_color=MainWindowTheme.TAB_UNSELECTED,
            segmented_button_unselected_hover_color=MainWindowTheme.TAB_HOVER,
            text_color=MainWindowTheme.TEXT_PRIMARY,
            anchor="nw"
        )
        self.tabview.pack(fill="both", expand=True, padx=UIConstants.MARGIN, pady=(0, UIConstants.MARGIN))
        
        # Create tabs
        chat_tab_frame = self.tabview.add("💬 Chat")
        avatar_tab_frame = self.tabview.add("🎭 Avatar")
        settings_tab_frame = self.tabview.add("⚙️ Settings")
        
        try:
            # Initialize tab components
            self.chat_tab = ChatTab(
                chat_tab_frame,
                state_manager=self.state_manager,
                core_bridge=self.core_bridge
            )
            self.logger.info("Chat tab initialized")
        except Exception as e:
            self.logger.error(f"Error initializing chat tab: {e}")
            
        try:
            self.avatar_tab = AvatarTab(
                avatar_tab_frame,
                state_manager=self.state_manager,
                core_bridge=self.core_bridge
            )
            self.logger.info("Avatar tab initialized")
        except Exception as e:
            self.logger.error(f"Error initializing avatar tab: {e}")
            
        try:
            self.settings_tab = SettingsTab(
                settings_tab_frame,
                state_manager=self.state_manager,
                core_bridge=self.core_bridge
            )
            self.logger.info("Settings tab initialized")
        except Exception as e:
            self.logger.error(f"Error initializing settings tab: {e}")
        
        # Set default tab
        self.tabview.set("💬 Chat")

    def create_status_bar(self):
        """Create the enhanced status bar."""
        self.status_frame = ctk.CTkFrame(
            self.main_frame,
            fg_color=MainWindowTheme.BACKGROUND_SECONDARY,
            height=UIConstants.STATUS_HEIGHT,
            corner_radius=0
        )
        self.status_frame.pack(fill="x", side="bottom")
        self.status_frame.pack_propagate(False)
        
        # Status content
        status_container = ctk.CTkFrame(self.status_frame, fg_color="transparent")
        status_container.pack(fill="both", expand=True, padx=UIConstants.MARGIN)
        
        # Main status label
        self.status_label = ctk.CTkLabel(
            status_container,
            text="Ready - TalkBridge Desktop v2.0",
            font=ctk.CTkFont(size=10),
            text_color=MainWindowTheme.TEXT_SECONDARY
        )
        self.status_label.pack(side="left", pady=5)
        
        # Right side status indicators
        indicators_frame = ctk.CTkFrame(status_container, fg_color="transparent")
        indicators_frame.pack(side="right")
        
        # Connection status
        self.connection_status = ctk.CTkLabel(
            indicators_frame,
            text="🟢 Connected",
            font=ctk.CTkFont(size=9),
            text_color=MainWindowTheme.TEXT_SECONDARY
        )
        self.connection_status.pack(side="right", padx=(10, 0))

    def configure_window(self):
        """Configure window properties and behavior."""
        # Center window on screen
        self.center_window()
        
        # Bind window events
        self.window.protocol("WM_DELETE_WINDOW", self.on_window_close)
        
        # Keyboard shortcuts
        self.window.bind("<Control-q>", lambda e: self.on_window_close())
        self.window.bind("<F11>", lambda e: self.toggle_fullscreen())
        self.window.bind("<Escape>", lambda e: self.exit_fullscreen())

    def center_window(self):
        """Center the window on the screen."""
        self.window.update_idletasks()
        
        # Get screen dimensions
        screen_width = self.window.winfo_screenwidth()
        screen_height = self.window.winfo_screenheight()
        
        # Calculate position
        x = (screen_width - UIConstants.DEFAULT_WIDTH) // 2
        y = (screen_height - UIConstants.DEFAULT_HEIGHT) // 2
        
        # Set position
        self.window.geometry(f"{UIConstants.DEFAULT_WIDTH}x{UIConstants.DEFAULT_HEIGHT}+{x}+{y}")

    def minimize_window(self):
        """Minimize the window."""
        self.window.iconify()

    def toggle_fullscreen(self):
        """Toggle fullscreen mode."""
        if self.is_fullscreen:
            self.exit_fullscreen()
        else:
            self.enter_fullscreen()

    def enter_fullscreen(self):
        """Enter fullscreen mode."""
        if not self.is_fullscreen:
            self.normal_geometry = self.window.geometry()
            self.window.attributes('-fullscreen', True)
            self.is_fullscreen = True
            self.maximize_button.configure(text="🗗")

    def exit_fullscreen(self):
        """Exit fullscreen mode."""
        if self.is_fullscreen:
            self.window.attributes('-fullscreen', False)
            if self.normal_geometry:
                self.window.geometry(self.normal_geometry)
            self.is_fullscreen = False
            self.maximize_button.configure(text="□")

    def update_status(self, message: str, color: str = None):
        """Update status bar message."""
        if self.status_label:
            if color is None:
                color = MainWindowTheme.TEXT_SECONDARY
            self.status_label.configure(text=message, text_color=color)

    def update_connection_status(self, connected: bool):
        """Update connection status indicator."""
        if self.connection_status:
            if connected:
                self.connection_status.configure(text="🟢 Connected", text_color="#4CAF50")
            else:
                self.connection_status.configure(text="🔴 Disconnected", text_color="#f44336")

    def show_logout_dialog(self):
        """Show logout confirmation dialog."""
        try:
            from src.desktop.dialogs.logout_dialog import LogoutDialog
            
            dialog = LogoutDialog(self.window)
            result = dialog.show()
            
            if result:
                self.logout()
                
        except ImportError:
            # Fallback to simple confirmation
            from tkinter import messagebox
            result = messagebox.askyesno(
                "Logout Confirmation",
                "Are you sure you want to logout?",
                icon="question"
            )
            if result:
                self.logout()

    def logout(self):
        """Handle user logout."""
        try:
            self.logger.info("User logout requested")
            
            # Clean up resources
            if self.chat_tab:
                # Save chat state if needed
                pass
            
            if self.settings_tab:
                # Save settings if needed
                pass
            
            # Close window
            self.window.destroy()
            
            # Signal logout to parent application
            if hasattr(self, 'logout_callback') and self.logout_callback:
                self.logout_callback()
                
        except Exception as e:
            self.logger.error(f"Error during logout: {e}")

    def on_window_close(self):
        """Handle window close event."""
        try:
            self.logger.info("Window close requested")
            
            # Save window state
            geometry = self.window.geometry()
            self.logger.debug(f"Saving window geometry: {geometry}")
            
            # Clean up resources
            if hasattr(self.chat_tab, 'cleanup'):
                self.chat_tab.cleanup()
            if hasattr(self.avatar_tab, 'cleanup'):
                self.avatar_tab.cleanup()
            if hasattr(self.settings_tab, 'cleanup'):
                self.settings_tab.cleanup()
            
            # Destroy window
            self.window.destroy()
            
        except Exception as e:
            self.logger.error(f"Error during window close: {e}")

    def show(self):
        """Show the main window."""
        if self.window:
            self.window.deiconify()
            self.window.focus_force()

    def hide(self):
        """Hide the main window."""
        if self.window:
            self.window.withdraw()

    def get_window(self):
        """Get the main window widget."""
        return self.window

    def run(self):
        """Run the main window event loop."""
        if self.window:
            self.window.mainloop()

    def __init__(self, root: ctk.CTk, state_manager=None, core_bridge=None):
        """Initialize the main window."""
        self.root = root
        self.state_manager = state_manager
        self.core_bridge = core_bridge
        self.logger = logging.getLogger("talkbridge.desktop.mainwindow")

        # Main widgets
        self.main_frame: Optional[ctk.CTkFrame] = None
        self.tab_view: Optional[ctk.CTkTabview] = None
        self.chat_tab: Optional[ChatTab] = None
        self.avatar_tab: Optional[AvatarTab] = None
        self.settings_tab: Optional[SettingsTab] = None
        self.status_frame: Optional[ctk.CTkFrame] = None
        self.status_label: Optional[ctk.CTkLabel] = None

        # Callbacks
        self.window_closing_callback = None
        self.logout_requested_callback = None
        self.view_changed_callback = None

        try:
            self.setup_ui()
            self.logger.info("UI setup completed")
        except Exception as e:
            self.logger.error(f"Error in setup_ui: {e}")
            raise
            
        try:
            self.create_menu_bar()
            self.logger.info("Menu bar created")
        except Exception as e:
            self.logger.error(f"Error in create_menu_bar: {e}")
            raise
            
        try:
            self.create_status_bar()
            self.logger.info("Status bar created")
        except Exception as e:
            self.logger.error(f"Error in create_status_bar: {e}")
            raise
            
        try:
            self.connect_signals()
            self.logger.info("Signals connected")
        except Exception as e:
            self.logger.error(f"Error in connect_signals: {e}")
            raise

        # Configure window
        self.configure_window()
        self.center_window()

    def setup_ui(self) -> None:
        """Sets up the main interface with tab widget."""
        self.logger.info("Setting up main UI")
        
        # Configure root window
        self.root.title("TalkBridge Desktop - CustomTkinter Edition")
        self.root.geometry("1200x800")
        
        # Create main frame
        self.main_frame = ctk.CTkFrame(self.root)
        self.main_frame.pack(fill="both", expand=True, padx=10, pady=10)
        
        # Create tab view
        self.tab_view = ctk.CTkTabview(self.main_frame, width=1150, height=700)
        self.tab_view.pack(fill="both", expand=True, padx=10, pady=10)
        
        # Add tabs
        self.tab_view.add("Chat")
        self.tab_view.add("Avatar")
        self.tab_view.add("Settings")
        
        try:
            # Create tab contents
            self.create_tabs()
            self.logger.info("Tabs created successfully")
        except Exception as e:
            self.logger.error(f"Error creating tabs: {e}")
            # Create fallback content
            fallback_label = ctk.CTkLabel(
                self.tab_view.tab("Chat"),
                text="Error loading components. Running in basic mode.",
                font=ctk.CTkFont(size=16)
            )
            fallback_label.pack(expand=True)

    def create_menu_bar(self) -> None:
        """Creates the menu bar."""
        self.logger.info("Creating menu bar")
        
        # Create menu frame
        menu_frame = ctk.CTkFrame(self.root, height=40)
        menu_frame.pack(fill="x", padx=10, pady=(10, 0))
        menu_frame.pack_propagate(False)
        
        # File menu button
        file_button = ctk.CTkButton(
            menu_frame,
            text="File",
            width=80,
            height=30,
            command=self._show_file_menu
        )
        file_button.pack(side="left", padx=5, pady=5)
        
        # View menu button
        view_button = ctk.CTkButton(
            menu_frame,
            text="View",
            width=80,
            height=30,
            command=self._show_view_menu
        )
        view_button.pack(side="left", padx=5, pady=5)
        
        # Help menu button
        help_button = ctk.CTkButton(
            menu_frame,
            text="Help",
            width=80,
            height=30,
            command=self._show_help_menu
        )
        help_button.pack(side="left", padx=5, pady=5)
        
        # Logout button (right side)
        logout_button = ctk.CTkButton(
            menu_frame,
            text="Logout",
            width=80,
            height=30,
            fg_color="red",
            hover_color="darkred",
            command=self.logout
        )
        logout_button.pack(side="right", padx=5, pady=5)

    def create_status_bar(self) -> None:
        """Creates the status bar."""
        self.logger.info("Creating status bar")
        
        # Create status frame
        self.status_frame = ctk.CTkFrame(self.root, height=30)
        self.status_frame.pack(fill="x", side="bottom", padx=10, pady=(0, 10))
        self.status_frame.pack_propagate(False)
        
        # Status label
        self.status_label = ctk.CTkLabel(
            self.status_frame,
            text="Ready",
            font=ctk.CTkFont(size=12)
        )
        self.status_label.pack(side="left", padx=10, pady=5)

    def create_tabs(self) -> None:
        """Creates the tab contents."""
        self.logger.info("Creating tab contents")
        
        try:
            # Chat tab
            self.chat_tab = ChatTab(
                self.tab_view.tab("Chat"),
                state_manager=self.state_manager,
                core_bridge=self.core_bridge
            )
            self.logger.info("Chat tab created")
            
        except Exception as e:
            self.logger.error(f"Error creating chat tab: {e}")
            # Create fallback chat tab
            fallback_label = ctk.CTkLabel(
                self.tab_view.tab("Chat"),
                text="Chat functionality temporarily unavailable",
                font=ctk.CTkFont(size=14)
            )
            fallback_label.pack(expand=True)

        try:
            # Avatar tab  
            self.avatar_tab = AvatarTab(
                self.tab_view.tab("Avatar"),
                state_manager=self.state_manager,
                core_bridge=self.core_bridge
            )
            self.logger.info("Avatar tab created")
            
        except Exception as e:
            self.logger.error(f"Error creating avatar tab: {e}")
            # Create fallback avatar tab
            fallback_label = ctk.CTkLabel(
                self.tab_view.tab("Avatar"),
                text="Avatar functionality temporarily unavailable",
                font=ctk.CTkFont(size=14)
            )
            fallback_label.pack(expand=True)

        try:
            # Settings tab
            self.settings_tab = SettingsTab(
                self.tab_view.tab("Settings"),
                state_manager=self.state_manager,
                core_bridge=self.core_bridge
            )
            self.logger.info("Settings tab created")
            
        except Exception as e:
            self.logger.error(f"Error creating settings tab: {e}")
            # Create fallback settings tab
            fallback_label = ctk.CTkLabel(
                self.tab_view.tab("Settings"),
                text="Settings functionality temporarily unavailable",
                font=ctk.CTkFont(size=14)
            )
            fallback_label.pack(expand=True)

    def connect_signals(self) -> None:
        """Connects component signals."""
        self.logger.info("Connecting signals")
        
        # Connect tab change event
        def on_tab_change():
            current_tab = self.tab_view.get()
            self.status_label.configure(text=f"View: {current_tab}")
            if self.view_changed_callback:
                self.view_changed_callback(current_tab)
        
        # Monitor tab changes
        self.tab_view.configure(command=on_tab_change)
        
        # Connect tab error signals if available
        if hasattr(self.chat_tab, 'error_occurred_callback'):
            self.chat_tab.error_occurred_callback = self.show_error_message
            
        if hasattr(self.avatar_tab, 'error_occurred_callback'):
            self.avatar_tab.error_occurred_callback = self.show_error_message
            
        if hasattr(self.settings_tab, 'error_occurred_callback'):
            self.settings_tab.error_occurred_callback = self.show_error_message

    def configure_window(self) -> None:
        """Configures window properties."""
        self.logger.info("Configuring window properties")
        
        # Set minimum size
        self.root.minsize(800, 600)
        
        # Configure grid weights
        self.root.grid_rowconfigure(0, weight=1)
        self.root.grid_columnconfigure(0, weight=1)

    def center_window(self) -> None:
        """Centers the window on the screen."""
        self.root.update_idletasks()
        
        # Get screen dimensions
        screen_width = self.root.winfo_screenwidth()
        screen_height = self.root.winfo_screenheight()
        
        # Get window dimensions
        window_width = self.root.winfo_reqwidth()
        window_height = self.root.winfo_reqheight()
        
        # Calculate position
        x = (screen_width // 2) - (window_width // 2)
        y = (screen_height // 2) - (window_height // 2)
        
        self.root.geometry(f"+{x}+{y}")

    def show_error_message(self, message: str) -> None:
        """Shows an error message to the user."""
        self.logger.error(f"Displaying error message: {message}")
        
        # Create error dialog
        dialog = ctk.CTkToplevel(self.root)
        dialog.title("Error")
        dialog.geometry("400x200")
        dialog.resizable(False, False)
        
        # Center dialog
        dialog.update_idletasks()
        x = (dialog.winfo_screenwidth() // 2) - (400 // 2)
        y = (dialog.winfo_screenheight() // 2) - (200 // 2)
        dialog.geometry(f"400x200+{x}+{y}")
        
        # Add content
        frame = ctk.CTkFrame(dialog)
        frame.pack(fill="both", expand=True, padx=20, pady=20)
        
        # Error message
        label = ctk.CTkLabel(
            frame,
            text=message,
            font=ctk.CTkFont(size=12),
            wraplength=350
        )
        label.pack(pady=20)
        
        # OK button
        ok_button = ctk.CTkButton(
            frame,
            text="OK",
            command=dialog.destroy
        )
        ok_button.pack(pady=10)
        
        # Make dialog modal
        dialog.transient(self.root)
        dialog.grab_set()

    def show_logout_dialog(self) -> bool:
        """
        Shows logout confirmation dialog.
        
        Returns:
            True if user confirms logout, False otherwise
        """
        result = [False]  # Use list to modify from inner function
        
        # Create logout dialog
        dialog = ctk.CTkToplevel(self.root)
        dialog.title("Confirm Logout")
        dialog.geometry("300x150")
        dialog.resizable(False, False)
        
        # Center dialog
        dialog.update_idletasks()
        x = (dialog.winfo_screenwidth() // 2) - (300 // 2)
        y = (dialog.winfo_screenheight() // 2) - (150 // 2)
        dialog.geometry(f"300x150+{x}+{y}")
        
        # Add content
        frame = ctk.CTkFrame(dialog)
        frame.pack(fill="both", expand=True, padx=20, pady=20)
        
        # Question
        label = ctk.CTkLabel(
            frame,
            text="Are you sure you want to logout?",
            font=ctk.CTkFont(size=12)
        )
        label.pack(pady=20)
        
        # Buttons frame
        button_frame = ctk.CTkFrame(frame, fg_color="transparent")
        button_frame.pack(pady=10)
        
        def on_yes():
            result[0] = True
            dialog.destroy()
        
        def on_no():
            result[0] = False
            dialog.destroy()
        
        # Yes button
        yes_button = ctk.CTkButton(
            button_frame,
            text="Yes",
            width=80,
            command=on_yes
        )
        yes_button.pack(side="left", padx=10)
        
        # No button
        no_button = ctk.CTkButton(
            button_frame,
            text="No",
            width=80,
            command=on_no
        )
        no_button.pack(side="left", padx=10)
        
        # Make dialog modal
        dialog.transient(self.root)
        dialog.grab_set()
        dialog.wait_window()
        
        return result[0]

    def logout(self) -> None:
        """Handles user logout."""
        self.logger.info("Logout requested")
        
        if self.show_logout_dialog():
            self.logger.info("User confirmed logout")
            if self.logout_requested_callback:
                self.logout_requested_callback()
            self.root.quit()
        else:
            self.logger.info("User cancelled logout")

    def _show_file_menu(self) -> None:
        """Shows file menu options."""
        # Create context menu
        menu = tk.Menu(self.root, tearoff=0)
        menu.add_command(label="New Session", command=lambda: self.status_label.configure(text="New Session"))
        menu.add_command(label="Open...", command=lambda: self.status_label.configure(text="Open"))
        menu.add_command(label="Save", command=lambda: self.status_label.configure(text="Save"))
        menu.add_separator()
        menu.add_command(label="Exit", command=self.root.quit)
        
        # Show menu at cursor position
        try:
            menu.tk_popup(self.root.winfo_pointerx(), self.root.winfo_pointery())
        finally:
            menu.grab_release()

    def _show_view_menu(self) -> None:
        """Shows view menu options."""
        # Create context menu
        menu = tk.Menu(self.root, tearoff=0)
        menu.add_command(label="Chat", command=lambda: self.tab_view.set("Chat"))
        menu.add_command(label="Avatar", command=lambda: self.tab_view.set("Avatar"))
        menu.add_command(label="Settings", command=lambda: self.tab_view.set("Settings"))
        
        # Show menu at cursor position
        try:
            menu.tk_popup(self.root.winfo_pointerx(), self.root.winfo_pointery())
        finally:
            menu.grab_release()

    def _show_help_menu(self) -> None:
        """Shows help menu options."""
        # Create context menu
        menu = tk.Menu(self.root, tearoff=0)
        menu.add_command(label="About", command=self._show_about_dialog)
        menu.add_command(label="User Guide", command=lambda: self.status_label.configure(text="User Guide"))
        
        # Show menu at cursor position
        try:
            menu.tk_popup(self.root.winfo_pointerx(), self.root.winfo_pointery())
        finally:
            menu.grab_release()

    def _show_about_dialog(self) -> None:
        """Shows about dialog."""
        # Create about dialog
        dialog = ctk.CTkToplevel(self.root)
        dialog.title("About TalkBridge")
        dialog.geometry("400x300")
        dialog.resizable(False, False)
        
        # Center dialog
        dialog.update_idletasks()
        x = (dialog.winfo_screenwidth() // 2) - (400 // 2)
        y = (dialog.winfo_screenheight() // 2) - (300 // 2)
        dialog.geometry(f"400x300+{x}+{y}")
        
        # Add content
        frame = ctk.CTkFrame(dialog)
        frame.pack(fill="both", expand=True, padx=20, pady=20)
        
        # Title
        title_label = ctk.CTkLabel(
            frame,
            text="TalkBridge Desktop",
            font=ctk.CTkFont(size=20, weight="bold")
        )
        title_label.pack(pady=20)
        
        # Version
        version_label = ctk.CTkLabel(
            frame,
            text="Version 2.0 - CustomTkinter Edition",
            font=ctk.CTkFont(size=12)
        )
        version_label.pack(pady=5)
        
        # Description
        desc_label = ctk.CTkLabel(
            frame,
            text="AI-powered conversation and avatar system\nwith real-time translation and voice synthesis",
            font=ctk.CTkFont(size=11),
            justify="center"
        )
        desc_label.pack(pady=20)
        
        # OK button
        ok_button = ctk.CTkButton(
            frame,
            text="OK",
            command=dialog.destroy
        )
        ok_button.pack(pady=20)
        
        # Make dialog modal
        dialog.transient(self.root)
        dialog.grab_set()
