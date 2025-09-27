#!/usr/bin/env python3
"""
TalkBridge Desktop - Main Window (CustomTkinter)
================================================

Main window with integrated tabs for chat, avatar and settings.

Author: TalkBridge Team
Date: 2025-09-08
Version: 2.1

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
from src.utils.status_utils import update_status, update_connection_status

# Import unified theme
try:
    from src.desktop.ui.theme import (
        ColorPalette, Typography, Spacing, Dimensions, 
        ComponentThemes, UIText, Icons, UXGuidelines
    )
    THEME_AVAILABLE = True
except ImportError:
    THEME_AVAILABLE = False

class MainWindowTheme:
    """Theme configuration for the main window."""
    
    # Use unified theme if available, otherwise fallback to original colors
    if THEME_AVAILABLE:
        BACKGROUND_MAIN = getattr(globals().get('ColorPalette'), 'BACKGROUND_PRIMARY', "#1e1e1e")
        BACKGROUND_SECONDARY = getattr(globals().get('ColorPalette'), 'BACKGROUND_SECONDARY', "#2d2d2d")
        BACKGROUND_ELEVATED = getattr(globals().get('ColorPalette'), 'BACKGROUND_ELEVATED', "#3c3c3c")
        
        TEXT_PRIMARY = getattr(globals().get('ColorPalette'), 'TEXT_PRIMARY', "#ffffff")
        TEXT_SECONDARY = getattr(globals().get('ColorPalette'), 'TEXT_SECONDARY', "#cccccc")
        TEXT_HINT = getattr(globals().get('ColorPalette'), 'TEXT_HINT', "#888888")
        
        ACCENT_BLUE = getattr(globals().get('ColorPalette'), 'ACCENT_PRIMARY', "#0078d4")
        ACCENT_BLUE_HOVER = getattr(globals().get('ColorPalette'), 'ACCENT_PRIMARY_HOVER', "#106ebe")
        ACCENT_RED = getattr(globals().get('ColorPalette'), 'ERROR', "#f44336")
        ACCENT_RED_HOVER = getattr(globals().get('ColorPalette'), 'ERROR_HOVER', "#d32f2f")
        
        TAB_SELECTED = getattr(globals().get('ColorPalette'), 'BACKGROUND_ELEVATED', "#3c3c3c")
        TAB_UNSELECTED = getattr(globals().get('ColorPalette'), 'BACKGROUND_SECONDARY', "#2d2d2d")
        TAB_HOVER = getattr(globals().get('ColorPalette'), 'BACKGROUND_SURFACE', "#4a4a4a")
    else:
        # Fallback colors
        BACKGROUND_MAIN = "#1e1e1e"
        BACKGROUND_SECONDARY = "#2d2d2d"
        BACKGROUND_ELEVATED = "#3c3c3c"
        
        TEXT_PRIMARY = "#ffffff"
        TEXT_SECONDARY = "#cccccc"
        TEXT_HINT = "#888888"
        
        ACCENT_BLUE = "#0078d4"
        ACCENT_BLUE_HOVER = "#106ebe"
        ACCENT_RED = "#f44336"
        ACCENT_RED_HOVER = "#d32f2f"
        
        TAB_SELECTED = "#3c3c3c"
        TAB_UNSELECTED = "#2d2d2d"
        TAB_HOVER = "#4a4a4a"

# Window dimensions
MIN_WIDTH = 1200
MIN_HEIGHT = 800
DEFAULT_WIDTH = 1400
DEFAULT_HEIGHT = 900

# Spacing (using theme if available)
MARGIN = getattr(globals().get('Spacing'), 'SM', 10) if THEME_AVAILABLE else 10
TITLE_MARGIN = getattr(globals().get('Spacing'), 'LG', 15) if THEME_AVAILABLE else 15
BUTTON_SPACING = getattr(globals().get('Spacing'), 'SM', 10) if THEME_AVAILABLE else 10

# Component heights (using theme if available)
TITLE_HEIGHT = 50
STATUS_HEIGHT = getattr(globals().get('Dimensions'), 'HEIGHT_STATUS_BAR', 30) if THEME_AVAILABLE else 30
BUTTON_HEIGHT = getattr(globals().get('Dimensions'), 'HEIGHT_BUTTON', 35) if THEME_AVAILABLE else 35

# Fonts (using theme if available)
TITLE_FONT_SIZE = getattr(globals().get('Typography'), 'FONT_SIZE_H3', 18) if THEME_AVAILABLE else 18
BUTTON_FONT_SIZE = getattr(globals().get('Typography'), 'FONT_SIZE_BODY', 12) if THEME_AVAILABLE else 12

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

    def __init__(self, state_manager=None, core_bridge=None, parent=None, logout_callback=None):
        """Initialize the enhanced main window."""
        self.state_manager = state_manager
        self.core_bridge = core_bridge
        self.parent = parent
        self.logout_callback = logout_callback
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
            # Use the parent window directly instead of creating a new toplevel
            self.window = self.parent
            # Update the parent window's title to be more descriptive
            title_method = getattr(self.window, 'title', None)
            if title_method and callable(title_method):
                title_method("TalkBridge Desktop - AI Communication Platform")
        else:
            self.window = ctk.CTk()
            # Configure window
            title_method = getattr(self.window, 'title', None)
            if title_method and callable(title_method):
                title_method("TalkBridge Desktop - AI Communication Platform")
        
        if self.window is None:
            raise RuntimeError("Failed to create window")
            
        # Configure window geometry and constraints
        if hasattr(self.window, 'geometry'):
            self.window.geometry(f"{DEFAULT_WIDTH}x{DEFAULT_HEIGHT}")
        if hasattr(self.window, 'minsize'):
            self.window.minsize(MIN_WIDTH, MIN_HEIGHT)
        
        # Apply main theme
        if hasattr(self.window, 'configure'):
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
            height=TITLE_HEIGHT,
            corner_radius=0
        )
        self.title_frame.pack(fill="x", padx=0, pady=0)
        self.title_frame.pack_propagate(False)
        
        # Title and branding
        title_container = ctk.CTkFrame(self.title_frame, fg_color="transparent")
        title_container.pack(side="left", fill="both", expand=True, padx=TITLE_MARGIN)
        
        # App icon and title using clean text
        self.title_label = ctk.CTkLabel(
            title_container,
            text=getattr(globals().get('UIText'), 'MAIN_TITLE', "TalkBridge Desktop - AI Communication Platform") if THEME_AVAILABLE else "TalkBridge Desktop - AI Communication Platform",
            font=ctk.CTkFont(size=TITLE_FONT_SIZE, weight="bold"),
            text_color=MainWindowTheme.ACCENT_BLUE
        )
        self.title_label.pack(side="left", pady=MARGIN)
        
        # Right side controls
        controls_frame = ctk.CTkFrame(self.title_frame, fg_color="transparent")
        controls_frame.pack(side="right", padx=TITLE_MARGIN)
        
        # Window controls
        self.minimize_button = ctk.CTkButton(
            controls_frame,
            text="-",
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
        
        # Logout button with clean text
        self.logout_button = ctk.CTkButton(
            controls_frame,
            text="Logout",
            width=80,
            height=BUTTON_HEIGHT,
            fg_color=MainWindowTheme.ACCENT_RED,
            hover_color=MainWindowTheme.ACCENT_RED_HOVER,
            font=ctk.CTkFont(size=BUTTON_FONT_SIZE, weight="bold"),
            command=self.show_logout_dialog
        )
        self.logout_button.pack(side="left", padx=(BUTTON_SPACING, 0))

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
        self.tabview.pack(fill="both", expand=True, padx=MARGIN, pady=(0, MARGIN))
        
        # Create tabs with clean text labels
        chat_tab_frame = self.tabview.add(getattr(globals().get('UIText'), 'CHAT_TAB', "Chat") if THEME_AVAILABLE else "Chat")
        avatar_tab_frame = self.tabview.add(getattr(globals().get('UIText'), 'AVATAR_TAB', "Avatar") if THEME_AVAILABLE else "Avatar")
        settings_tab_frame = self.tabview.add(getattr(globals().get('UIText'), 'SETTINGS_TAB', "Settings") if THEME_AVAILABLE else "Settings")
        
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
        self.tabview.set(getattr(globals().get('UIText'), 'CHAT_TAB', "Chat") if THEME_AVAILABLE else "Chat")

    def create_status_bar(self):
        """Create the enhanced status bar."""
        self.status_frame = ctk.CTkFrame(
            self.main_frame,
            fg_color=MainWindowTheme.BACKGROUND_SECONDARY,
            height=STATUS_HEIGHT,
            corner_radius=0
        )
        self.status_frame.pack(fill="x", side="bottom")
        self.status_frame.pack_propagate(False)
        
        # Status content
        status_container = ctk.CTkFrame(self.status_frame, fg_color="transparent")
        status_container.pack(fill="both", expand=True, padx=MARGIN)
        
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
        if self.window and hasattr(self.window, 'protocol'):
            self.window.protocol("WM_DELETE_WINDOW", self.on_window_close)
        
        # Keyboard shortcuts
        if self.window and hasattr(self.window, 'bind'):
            self.window.bind("<Control-q>", lambda e: self.on_window_close())
            self.window.bind("<F11>", lambda e: self.toggle_fullscreen())
            self.window.bind("<Escape>", lambda e: self.exit_fullscreen())

    def center_window(self):
        """Center the window on the screen."""
        if not self.window:
            return
        if hasattr(self.window, 'update_idletasks'):
            self.window.update_idletasks()
        
        # Get screen dimensions
        if hasattr(self.window, 'winfo_screenwidth') and hasattr(self.window, 'winfo_screenheight'):
            screen_width = self.window.winfo_screenwidth()
            screen_height = self.window.winfo_screenheight()
            
            # Calculate position
            x = (screen_width - DEFAULT_WIDTH) // 2
            y = (screen_height - DEFAULT_HEIGHT) // 2
            
            # Set position
            if hasattr(self.window, 'geometry'):
                self.window.geometry(f"{DEFAULT_WIDTH}x{DEFAULT_HEIGHT}+{x}+{y}")

    def minimize_window(self):
        """Minimize the window."""
        if self.window and hasattr(self.window, 'iconify'):
            self.window.iconify()

    def toggle_fullscreen(self):
        """Toggle fullscreen mode."""
        if self.is_fullscreen:
            self.exit_fullscreen()
        else:
            self.enter_fullscreen()

    def enter_fullscreen(self):
        """Enter fullscreen mode."""
        if not self.is_fullscreen and self.window:
            if hasattr(self.window, 'geometry'):
                self.normal_geometry = self.window.geometry()
            if hasattr(self.window, 'attributes'):
                self.window.attributes('-fullscreen', True)
            self.is_fullscreen = True
            if hasattr(self, 'maximize_button') and self.maximize_button:
                self.maximize_button.configure(text="🗗")

    def exit_fullscreen(self):
        """Exit fullscreen mode."""
        if self.is_fullscreen and self.window:
            if hasattr(self.window, 'attributes'):
                self.window.attributes('-fullscreen', False)
            if self.normal_geometry and hasattr(self.window, 'geometry'):
                self.window.geometry(self.normal_geometry)
            self.is_fullscreen = False
            if hasattr(self, 'maximize_button') and self.maximize_button:
                self.maximize_button.configure(text="□")

    def update_status(self, message: str, color: Optional[str] = None):
        """Update status bar message."""
        if self.status_label:
            # Use centralized status utility for consistency
            from src.utils.status_utils import StatusLevel
            level = StatusLevel.INFO if color is None else StatusLevel.INFO
            update_status(self.status_label, message, level=level)
            # Apply custom color if provided
            if color is not None:
                self.status_label.configure(text_color=color)

    def update_connection_status(self, connected: bool):
        """Update connection status indicator."""
        if self.connection_status:
            # Use centralized connection status utility
            update_connection_status(self.connection_status, connected)

    def show_logout_dialog(self):
        """Show logout confirmation dialog."""
        try:
            # Simple logout without dialog for now
            # TODO: Implement proper logout dialog
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
            if self.window and hasattr(self.window, 'destroy'):
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
            if self.window and hasattr(self.window, 'geometry'):
                geometry = self.window.geometry()
                self.logger.debug(f"Saving window geometry: {geometry}")
            
            # Clean up resources
            if self.chat_tab and hasattr(self.chat_tab, 'cleanup'):
                self.chat_tab.cleanup()
            if self.avatar_tab and hasattr(self.avatar_tab, 'cleanup'):
                self.avatar_tab.cleanup()
            if self.settings_tab and hasattr(self.settings_tab, 'cleanup'):
                cleanup_method = getattr(self.settings_tab, 'cleanup', None)
                if cleanup_method and callable(cleanup_method):
                    cleanup_method()
            
            # Destroy window
            if self.window and hasattr(self.window, 'destroy'):
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
        # Only run mainloop if this window is standalone (no parent)
        if self.window and not self.parent:
            self.window.mainloop()
        elif self.parent:
            # When using a parent window, the parent manages the mainloop
            self.logger.info("MainWindow using parent's mainloop - not starting own event loop")

