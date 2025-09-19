#!/usr/bin/env python3
"""
TalkBridge Desktop - Application (CustomTkinter)
================================================

Application module for TalkBridge with CustomTkinter

Author: TalkBridge Team
Date: 2025-09-08
Version: 2.1

Requirements:
- customtkinter
- tkinter
======================================================================
Functions:
- __init__: Initializes the application.
- run: Runs the full application.
- _show_splash_screen: Shows the splash screen during loading.
- _initialize_core_components: Initializes the application's core components.
- _show_login_dialog: Shows the login dialog and handles authentication.
- _initialize_services_async: Initializes services asynchronously.
- _show_main_window: Shows the application's main window.
======================================================================
"""

import sys
import logging
import threading
import time
from typing import Optional
from pathlib import Path
import tkinter as tk
import customtkinter as ctk
from PIL import Image, ImageDraw, ImageFont

from talkbridge.desktop.app.state_manager import StateManager
from talkbridge.desktop.dialogs.login_dialog import LoginDialog
from talkbridge.desktop.app.main_window import MainWindow
from talkbridge.desktop.services.core_bridge import CoreBridge
from talkbridge.utils.error_handler import (
    RetryableError, CriticalError, UserNotificationError,
    handle_error, retry_with_backoff, notify_error
)
from talkbridge.logging_config import get_logger

# Import new notification and async systems
from talkbridge.ui.notifier import subscribe, notify_info, notify_error
from talkbridge.desktop.notifier_adapter import DesktopNotifier
from talkbridge.utils.async_runner import get_task_runner, run_async, ProgressReporter
from talkbridge.errors import ErrorCategory, handle_user_facing_error

# Import unified theme
try:
    from talkbridge.desktop.ui.theme import (
        ColorPalette, Typography, Spacing, Dimensions, 
        ComponentThemes, UIText, Icons, UXGuidelines
    )
    THEME_AVAILABLE = True
except ImportError:
    THEME_AVAILABLE = False

class ApplicationTheme:
    """Theme configuration for the application."""
    
    # Use unified theme if available, otherwise fallback to original colors
    if THEME_AVAILABLE:
        BACKGROUND_MAIN = ColorPalette.BACKGROUND_PRIMARY
        BACKGROUND_SECONDARY = ColorPalette.BACKGROUND_SECONDARY
        BACKGROUND_SPLASH = ColorPalette.BACKGROUND_PRIMARY
        
        TEXT_PRIMARY = ColorPalette.TEXT_PRIMARY
        TEXT_SECONDARY = ColorPalette.TEXT_SECONDARY
        TEXT_ACCENT = ColorPalette.ACCENT_PRIMARY
        
        ACCENT_BLUE = ColorPalette.ACCENT_PRIMARY
        ACCENT_GREEN = ColorPalette.SUCCESS
        ERROR_COLOR = ColorPalette.ERROR
        WARNING_COLOR = ColorPalette.WARNING
    else:
        # Fallback colors
        BACKGROUND_MAIN = "#1e1e1e"
        BACKGROUND_SECONDARY = "#2d2d2d"
        BACKGROUND_SPLASH = "#0f0f0f"
        
        TEXT_PRIMARY = "#ffffff"
        TEXT_SECONDARY = "#cccccc"
        TEXT_ACCENT = "#0078d4"
        
        ACCENT_BLUE = "#0078d4"
        ACCENT_GREEN = "#4CAF50"
        ERROR_COLOR = "#f44336"
        WARNING_COLOR = "#ff9800"

class SplashConstants:
    """Constants for splash screen configuration."""
    
    WIDTH = 500
    HEIGHT = 350
    LOGO_SIZE = 80
    TITLE_FONT_SIZE = 24
    SUBTITLE_FONT_SIZE = 14
    STATUS_FONT_SIZE = 12
    FADE_DURATION = 2000  # milliseconds
    DISPLAY_DURATION = 3000  # milliseconds

class TalkBridgeApplication:
    """
    Enhanced main TalkBridge Desktop application with CustomTkinter.

    Handles comprehensive system initialization, including:
    - Advanced splash screen with animations
    - User authentication with retry logic
    - Asynchronous service initialization
    - Enhanced error handling and user feedback
    - Modern visual design with theming
    """

    def __init__(self):
        """Initialize the enhanced application."""
        self.logger = get_logger(__name__)
        
        # Core components
        self.state_manager: Optional[StateManager] = None
        self.core_bridge: Optional[CoreBridge] = None
        self.main_window: Optional[MainWindow] = None
        
        # Visual components
        self.splash_window: Optional[ctk.CTkToplevel] = None
        self.splash_progress_bar: Optional[ctk.CTkProgressBar] = None
        self.splash_status_label: Optional[ctk.CTkLabel] = None
        self.splash_animation_running = False
        
        # Application state
        self.authenticated = False
        self.services_initialized = False
        self.initialization_progress = 0.0
        self.exit_code = 0
        self.max_login_attempts = 3
        self.current_login_attempt = 0
        
        # Tkinter root with enhanced configuration
        self.root = ctk.CTk()
        self.root.withdraw()  # Hide initially
        self._configure_root_window()
        
        # Initialize notification system
        self._setup_notification_system()
        
        self.logger.info("Enhanced TalkBridge Application initialized")
    
    def _setup_notification_system(self):
        """Set up the notification system for the desktop application."""
        try:
            # Create desktop notifier and subscribe to global notifications
            self.desktop_notifier = DesktopNotifier(self.root)
            subscribe(self.desktop_notifier)
            
            # Register UI root with task runner for thread-safe callbacks
            get_task_runner().register_ui_root(self.root)
            
            # Start the notification pump
            self.desktop_notifier.start_pump()
            
            self.logger.info("Notification system initialized")
            
        except Exception as e:
            self.logger.error(f"Failed to initialize notification system: {e}")
            # Continue without notifications rather than failing completely

    def _configure_root_window(self):
        """Configure the root window with enhanced settings."""
        # Set appearance mode and theme
        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("dark-blue")
        
        # Configure root window
        self.root.title("TalkBridge Desktop")
        self.root.configure(fg_color=ApplicationTheme.BACKGROUND_MAIN)
        
        # Set window icon if available
        try:
            # You can add an icon file here if available
            # self.root.iconbitmap("path/to/icon.ico")
            pass
        except Exception as e:
            self.logger.debug(f"Window icon not available or failed to set: {e}")

    def run(self) -> int:
        """
        Runs the enhanced full application with comprehensive error handling.
        
        Returns:
            Exit code (0 for success, 1 for error)
        """
        try:
            self.logger.info("Starting enhanced application run sequence")
            
            # Initialize core components first (without splash screen)
            if not self._initialize_core_components():
                self.logger.error("Core components initialization failed")
                self._show_critical_error("Initialization Error", 
                                        "Failed to initialize core components.")
                return 1
            
            # Authentication first - show login dialog immediately
            if not self._handle_authentication_with_retry():
                self.logger.info("Authentication cancelled or failed")
                return 0
            
            # After successful authentication, show splash screen during service initialization
            self._show_enhanced_splash_screen()
            
            # Initialize services synchronously to ensure proper flow
            if not self._initialize_services():
                self.logger.error("Services initialization failed")
                self._close_splash_screen()
                self._show_critical_error("Services Error", 
                                        "Failed to initialize application services.")
                return 1
            
            # Show main window after all initialization is complete
            self._show_main_window()
            
            # Close splash screen after main window is shown
            self._close_splash_screen()
            
            # Start main loop
            self.logger.info("Starting main application loop")
            self.root.mainloop()
            
            return self.exit_code
            
        except Exception as e:
            self.logger.error(f"Critical application error: {e}", exc_info=True)
            self._close_splash_screen()
            self._show_critical_error("Critical Error", 
                                    f"An unexpected error occurred:\n{str(e)}")
            return 1
        finally:
            self._cleanup_application()

    def _show_enhanced_splash_screen(self):
        """Show enhanced splash screen with modern design and animations."""
        try:
            self.logger.info("Showing enhanced splash screen")
            
            # Create splash window
            self.splash_window = ctk.CTkToplevel(self.root)
            self.splash_window.title("TalkBridge Desktop")
            self.splash_window.geometry(f"{SplashConstants.WIDTH}x{SplashConstants.HEIGHT}")
            self.splash_window.resizable(False, False)
            
            # Configure splash window
            self.splash_window.configure(fg_color=ApplicationTheme.BACKGROUND_SPLASH)
            self.splash_window.attributes('-topmost', True)
            
            # Center on screen
            self._center_splash_screen()
            
            # Create splash content
            self._create_splash_content()
            
            # Start loading animation
            self._start_splash_animation()
            
            # Process events to show splash
            self.root.update_idletasks()
            self.root.update()
            
        except Exception as e:
            self.logger.warning(f"Could not show enhanced splash screen: {e}")

    def _center_splash_screen(self):
        """Center splash screen on the display."""
        # Get screen dimensions
        screen_width = self.splash_window.winfo_screenwidth()
        screen_height = self.splash_window.winfo_screenheight()
        
        # Calculate position
        x = (screen_width - SplashConstants.WIDTH) // 2
        y = (screen_height - SplashConstants.HEIGHT) // 2
        
        # Set position
        self.splash_window.geometry(f"{SplashConstants.WIDTH}x{SplashConstants.HEIGHT}+{x}+{y}")

    def _create_splash_content(self):
        """Create the enhanced splash screen content."""
        # Main container
        main_frame = ctk.CTkFrame(
            self.splash_window,
            fg_color="transparent",
            corner_radius=0
        )
        main_frame.pack(fill="both", expand=True, padx=30, pady=40)
        
        # Logo section
        logo_frame = ctk.CTkFrame(main_frame, fg_color="transparent")
        logo_frame.pack(fill="x", pady=(0, 20))
        
        # App logo using clean text instead of emoji
        logo_label = ctk.CTkLabel(
            logo_frame,
            text=Icons.ROBOT if THEME_AVAILABLE else "AI",
            font=ctk.CTkFont(size=SplashConstants.LOGO_SIZE, weight="bold"),
            text_color=ApplicationTheme.ACCENT_BLUE
        )
        logo_label.pack(pady=(0, 10))
        
        # App title
        title_label = ctk.CTkLabel(
            logo_frame,
            text=UIText.APP_NAME if THEME_AVAILABLE else "TalkBridge Desktop",
            font=ctk.CTkFont(size=SplashConstants.TITLE_FONT_SIZE, weight="bold"),
            text_color=ApplicationTheme.TEXT_PRIMARY
        )
        title_label.pack()
        
        # Subtitle
        subtitle_label = ctk.CTkLabel(
            logo_frame,
            text=UIText.APP_SUBTITLE if THEME_AVAILABLE else "AI-Powered Communication Platform",
            font=ctk.CTkFont(size=SplashConstants.SUBTITLE_FONT_SIZE),
            text_color=ApplicationTheme.TEXT_SECONDARY
        )
        subtitle_label.pack(pady=(5, 0))
        
        # Version info
        version_label = ctk.CTkLabel(
            logo_frame,
            text="Version 2.0",
            font=ctk.CTkFont(size=10),
            text_color=ApplicationTheme.TEXT_SECONDARY
        )
        version_label.pack(pady=(10, 0))
        
        # Progress section
        progress_frame = ctk.CTkFrame(main_frame, fg_color="transparent")
        progress_frame.pack(fill="x", side="bottom", pady=(20, 0))
        
        # Progress bar
        self.splash_progress_bar = ctk.CTkProgressBar(
            progress_frame,
            height=8,
            progress_color=ApplicationTheme.ACCENT_BLUE,
            fg_color=ApplicationTheme.BACKGROUND_SECONDARY
        )
        self.splash_progress_bar.pack(fill="x", pady=(0, 10))
        self.splash_progress_bar.set(0)
        
        # Status label
        self.splash_status_label = ctk.CTkLabel(
            progress_frame,
            text="Initializing TalkBridge...",
            font=ctk.CTkFont(size=SplashConstants.STATUS_FONT_SIZE),
            text_color=ApplicationTheme.TEXT_SECONDARY
        )
        self.splash_status_label.pack()

    def _start_splash_animation(self):
        """Start the splash screen loading animation."""
        self.splash_animation_running = True
        self._animate_splash_progress()

    def _animate_splash_progress(self):
        """Animate the splash screen progress bar."""
        if not self.splash_animation_running or not self.splash_progress_bar:
            return
            
        # Animate progress bar
        current_progress = self.splash_progress_bar.get()
        if current_progress < 0.9:
            new_progress = min(current_progress + 0.05, 0.9)
            self.splash_progress_bar.set(new_progress)
        
        # Continue animation
        if self.splash_animation_running:
            self.root.after(100, self._animate_splash_progress)

    def _update_splash_status(self, message: str, progress: float = None):
        """Update splash screen status message and progress."""
        if self.splash_status_label:
            self.splash_status_label.configure(text=message)
        
        if progress is not None and self.splash_progress_bar:
            self.splash_progress_bar.set(progress)
        
        # Process events to update display
        if self.splash_window:
            self.root.update_idletasks()
            self.root.update()

    def _close_splash_screen(self):
        """Close the splash screen with fade animation."""
        try:
            self.splash_animation_running = False
            
            if self.splash_window:
                # Complete progress bar
                if self.splash_progress_bar:
                    self.splash_progress_bar.set(1.0)
                
                # Update final status
                if self.splash_status_label:
                    self.splash_status_label.configure(text="Ready!")
                
                # Brief pause before closing
                self.root.after(500, lambda: self.splash_window.destroy() if self.splash_window else None)
                
        except Exception as e:
            handle_error(e, "Desktop", "Failed to close splash screen", self.logger)
            # Ensure splash window is closed even if animation fails
            try:
                if self.splash_window:
                    self.splash_window.destroy()
            except Exception:
                pass  # Final fallback - window may already be destroyed

    def _handle_authentication_with_retry(self) -> bool:
        """Handle authentication with retry logic and enhanced feedback."""
        self.current_login_attempt = 0
        
        while self.current_login_attempt < self.max_login_attempts:
            self.current_login_attempt += 1
            
            self.logger.info(f"Authentication attempt {self.current_login_attempt}/{self.max_login_attempts}")
            
            # Show login dialog
            login_success = self._show_login_dialog()
            
            if login_success:
                self.authenticated = True
                return True
            
            # Handle failed attempt
            if self.current_login_attempt < self.max_login_attempts:
                # Show retry dialog
                retry = self._show_login_retry_dialog()
                if not retry:
                    self.logger.info("User chose to exit after failed login")
                    return False
            else:
                self.logger.warning("Maximum login attempts reached")
                self._show_error_dialog("Authentication Failed", 
                                      "Maximum login attempts exceeded.\nPlease try again later.")
                return False
        
        return False

    def _show_login_retry_dialog(self) -> bool:
        """Show dialog asking user if they want to retry login."""
        try:
            # Create retry dialog
            retry_dialog = ctk.CTkToplevel(self.root)
            retry_dialog.title("Login Failed")
            retry_dialog.geometry("350x200")
            retry_dialog.resizable(False, False)
            retry_dialog.configure(fg_color=ApplicationTheme.BACKGROUND_MAIN)
            retry_dialog.transient(self.root)
            retry_dialog.grab_set()
            
            # Center dialog
            self._center_dialog(retry_dialog, 350, 200)
            
            result = [False]  # Use list to modify from inner function
            
            # Dialog content
            main_frame = ctk.CTkFrame(retry_dialog, fg_color="transparent")
            main_frame.pack(fill="both", expand=True, padx=20, pady=20)
            
            # Icon and message
            icon_label = ctk.CTkLabel(
                main_frame,
                text="⚠️",
                font=ctk.CTkFont(size=32),
                text_color=ApplicationTheme.WARNING_COLOR
            )
            icon_label.pack(pady=(0, 10))
            
            message_label = ctk.CTkLabel(
                main_frame,
                text="Login failed. Would you like to try again?",
                font=ctk.CTkFont(size=12),
                text_color=ApplicationTheme.TEXT_PRIMARY,
                wraplength=300
            )
            message_label.pack(pady=(0, 20))
            
            # Buttons
            button_frame = ctk.CTkFrame(main_frame, fg_color="transparent")
            button_frame.pack(fill="x")
            
            def on_retry():
                result[0] = True
                retry_dialog.destroy()
            
            def on_exit():
                result[0] = False
                retry_dialog.destroy()
            
            # Exit button
            exit_button = ctk.CTkButton(
                button_frame,
                text="Exit",
                width=100,
                height=35,
                fg_color="transparent",
                text_color=ApplicationTheme.TEXT_SECONDARY,
                border_width=2,
                border_color=ApplicationTheme.BACKGROUND_SECONDARY,
                hover_color=ApplicationTheme.BACKGROUND_SECONDARY,
                command=on_exit
            )
            exit_button.pack(side="left")
            
            # Retry button
            retry_button = ctk.CTkButton(
                button_frame,
                text="Try Again",
                width=100,
                height=35,
                fg_color=ApplicationTheme.ACCENT_BLUE,
                hover_color="#106ebe",
                command=on_retry
            )
            retry_button.pack(side="right")
            
            # Wait for dialog
            retry_dialog.wait_window()
            
            return result[0]
            
        except Exception as e:
            handle_error(e, "Desktop", "Error showing retry dialog", self.logger)
            return False

    def _center_dialog(self, dialog, width, height):
        """Center a dialog on the screen."""
        screen_width = dialog.winfo_screenwidth()
        screen_height = dialog.winfo_screenheight()
        x = (screen_width - width) // 2
        y = (screen_height - height) // 2
        dialog.geometry(f"{width}x{height}+{x}+{y}")

    def _show_error_dialog(self, title: str, message: str):
        """Show an enhanced error dialog."""
        try:
            error_dialog = ctk.CTkToplevel(self.root)
            error_dialog.title(title)
            error_dialog.geometry("400x250")
            error_dialog.resizable(False, False)
            error_dialog.configure(fg_color=ApplicationTheme.BACKGROUND_MAIN)
            error_dialog.transient(self.root)
            error_dialog.grab_set()
            
            # Center dialog
            self._center_dialog(error_dialog, 400, 250)
            
            # Dialog content
            main_frame = ctk.CTkFrame(error_dialog, fg_color="transparent")
            main_frame.pack(fill="both", expand=True, padx=20, pady=20)
            
            # Error icon
            icon_label = ctk.CTkLabel(
                main_frame,
                text="X",
                font=ctk.CTkFont(size=40),
                text_color=ApplicationTheme.ERROR_COLOR
            )
            icon_label.pack(pady=(0, 15))
            
            # Title
            title_label = ctk.CTkLabel(
                main_frame,
                text=title,
                font=ctk.CTkFont(size=16, weight="bold"),
                text_color=ApplicationTheme.TEXT_PRIMARY
            )
            title_label.pack(pady=(0, 10))
            
            # Message
            message_label = ctk.CTkLabel(
                main_frame,
                text=message,
                font=ctk.CTkFont(size=12),
                text_color=ApplicationTheme.TEXT_SECONDARY,
                wraplength=350,
                justify="center"
            )
            message_label.pack(pady=(0, 20))
            
            # OK button
            ok_button = ctk.CTkButton(
                main_frame,
                text="OK",
                width=100,
                height=35,
                fg_color=ApplicationTheme.ERROR_COLOR,
                hover_color="#d32f2f",
                command=error_dialog.destroy
            )
            ok_button.pack()
            
            # Wait for dialog
            error_dialog.wait_window()
            
        except Exception as e:
            handle_error(e, "Desktop", "Error showing error dialog", self.logger)
            # Fallback to basic error display
            try:
                import tkinter.messagebox as messagebox
                messagebox.showerror(title, message)
            except Exception:
                print(f"CRITICAL ERROR - {title}: {message}")  # Last resort

    def _show_critical_error(self, title: str, message: str):
        """Show a critical error dialog and log the error."""
        self.logger.critical(f"{title}: {message}")
        self._show_error_dialog(title, message)

    def _initialize_core_components(self) -> bool:
        """Initialize the application's core components with progress updates."""
        try:
            self.logger.info("Initializing core components...")
            self._update_splash_status("Initializing core components...", 0.1)
            
            # Initialize StateManager
            self.state_manager = StateManager()
            self._update_splash_status("Setting up state management...", 0.3)
            
            if not self.state_manager.initialize():
                raise Exception("StateManager initialization failed")
            
            # Initialize CoreBridge
            self._update_splash_status("Initializing core bridge...", 0.5)
            self.core_bridge = CoreBridge(self.state_manager)
            
            self._update_splash_status("Core components ready", 0.6)
            self.logger.info("Core components initialized successfully")
            return True
            
        except Exception as e:
            handle_error(e, "Desktop", "Error initializing core components", self.logger)
            return False
    def _show_login_dialog(self) -> bool:
        """
        Shows the login dialog and handles authentication.
        
        Returns:
            True if authentication successful, False otherwise
        """
        self.logger.info("Showing login dialog")
        
        try:
            login_dialog = LoginDialog(self.root)
            success, username, password = login_dialog.show()
            
            if success:
                self.authenticated = True
                self.logger.info(f"Authentication successful for user: {username}")
                return True
            else:
                self.logger.info("Authentication cancelled")
                return False
                
        except Exception as e:
            handle_error(e, "Desktop", "Error in login dialog", self.logger)
            return False

    def _initialize_services(self) -> bool:
        """Initializes services asynchronously with progress updates."""
        try:
            self.logger.info("Starting non-blocking service initialization")
            self._update_splash_status("Initializing services...", 0.7)
            
            # Start services asynchronously
            def init_services_task(progress: ProgressReporter):
                progress.update(0, "Loading modules...")
                # Simulate module loading without blocking
                import threading
                
                # Progress updates
                progress.update(33, "Setting up core services...")
                
                # More progress
                progress.update(66, "Finalizing setup...")
                
                # Complete
                progress.update(100, "Services ready!")
                return True
            
            # Run initialization asynchronously
            run_async(
                init_services_task,
                on_success=self._on_services_ready,
                on_error=self._on_services_error,
                on_progress=self._on_service_init_progress,
                task_name="service_initialization"
            )
            
            return True  # Return immediately, actual completion handled by callbacks
            
        except Exception as e:
            self.logger.exception(f"Error starting service initialization: {e}")
            handle_user_facing_error(
                ErrorCategory.SERVICE_INITIALIZATION_FAILED,
                details=str(e),
                context="Application Startup"
            )
            return False
    
    def _on_services_ready(self, result):
        """Callback when services are ready."""
        self.services_initialized = True
        self._update_splash_status("Ready!", 1.0)
        self.logger.info("Services initialization completed successfully")
        notify_info("Services initialized successfully", context="Application")
    
    def _on_services_error(self, error):
        """Callback when service initialization fails."""
        self.logger.error(f"Service initialization failed: {error}")
        handle_user_facing_error(
            ErrorCategory.SERVICE_INITIALIZATION_FAILED,
            details=str(error),
            context="Application Startup"
        )
    
    def _on_service_init_progress(self, progress):
        """Callback for service initialization progress."""
        # Update splash screen with progress
        self._update_splash_status(progress.message, 0.7 + (progress.percentage / 100) * 0.2)

    def _show_main_window(self) -> None:
        """Shows the application's main window."""
        self.logger.info("Showing main window")
        
        try:
            # Create main window with correct parameter mapping
            self.main_window = MainWindow(
                state_manager=self.state_manager,
                core_bridge=self.core_bridge,
                parent=self.root
            )
            
            # Show root window
            self.root.deiconify()
            
            # Connect signals
            def on_window_closing():
                self.logger.info("Main window closing")
                self.root.quit()
            
            self.root.protocol("WM_DELETE_WINDOW", on_window_closing)
            
            self.logger.info("Main window displayed successfully")
            
        except Exception as e:
            self.logger.exception(f"Error showing main window: {e}")
            raise

    def _initialize_core_components(self) -> bool:
        """Initialize the application's core components with progress updates."""
        try:
            self.logger.info("Initializing core components...")
            self._update_splash_status("Initializing core components...", 0.1)
            
            # Initialize StateManager
            self.state_manager = StateManager()
            self._update_splash_status("Setting up state management...", 0.3)
            
            if not self.state_manager.initialize():
                raise Exception("StateManager initialization failed")
            
            # Initialize CoreBridge
            self._update_splash_status("Initializing core bridge...", 0.5)
            self.core_bridge = CoreBridge(self.state_manager)
            
            self._update_splash_status("Core components ready", 0.6)
            self.logger.info("Core components initialized successfully")
            return True
            
        except Exception as e:
            self.logger.error(f"Error initializing core components: {e}")
            return False

    def _initialize_services_async(self):
        """Initialize services asynchronously in background thread."""
        def initialize_services():
            try:
                self.logger.info("Starting async service initialization...")
                self._update_splash_status("Initializing AI services...", 0.9)
                
                # Use async runner instead of time.sleep
                notify_info("Initializing AI services...", context="Startup")
                
                # Simulate service initialization without blocking
                # This would be replaced with actual service initialization
                import threading
                threading.Event().wait(1.0)  # Non-blocking wait
                
                # Mark services as ready
                self.services_initialized = True
                self._update_splash_status("Services ready!", 1.0)
                
                notify_info("All services ready", context="Startup")
                self.logger.info("Service initialization completed")
                
            except Exception as e:
                self.logger.exception(f"Error in async service initialization: {e}")
                handle_user_facing_error(
                    ErrorCategory.SERVICE_INITIALIZATION_FAILED,
                    details=str(e),
                    context="Service Initialization"
                )
        
        # Run in background thread
        run_async(
            initialize_services,
            on_success=lambda result: self.logger.info("Async services ready"),
            on_error=lambda error: self.logger.error(f"Async service error: {error}"),
            task_name="async_service_init"
        )
                self.services_initialized = True
                self._update_splash_status("All services ready!", 1.0)
                
                self.logger.info("Services initialized successfully")
                
            except Exception as e:
                self.logger.error(f"Error initializing services: {e}")
                self.services_initialized = False
        
        # Start initialization in background thread
        init_thread = threading.Thread(target=initialize_services, daemon=True)
        init_thread.start()

    def _handle_logout(self):
        """Handle user logout."""
        try:
            self.logger.info("Handling user logout")
            
            # Clean up resources
            if self.main_window:
                self.main_window.hide()
            
            # Reset authentication state
            self.authenticated = False
            self.services_initialized = False
            
            # Exit application
            self.exit_code = 0
            self.root.quit()
            
        except Exception as e:
            self.logger.error(f"Error during logout: {e}")

    def _cleanup_application(self):
        """Clean up application resources."""
        try:
            self.logger.info("Cleaning up application resources")
            
            # Stop animations
            self.splash_animation_running = False
            
            # Clean up components
            if self.main_window and hasattr(self.main_window, 'cleanup'):
                self.main_window.cleanup()
            
            if self.core_bridge and hasattr(self.core_bridge, 'cleanup'):
                self.core_bridge.cleanup()
            
            if self.state_manager and hasattr(self.state_manager, 'cleanup'):
                self.state_manager.cleanup()
            
            # Close splash screen
            if self.splash_window:
                try:
                    self.splash_window.destroy()
                except Exception:
                    # Ignore splash screen destruction errors during shutdown
                    pass
            
            self.logger.info("Application cleanup completed")
            
        except Exception as e:
            self.logger.error(f"Error during cleanup: {e}")

    def set_exit_code(self, code: int):
        """Set the application exit code."""
        self.exit_code = code

    def exit_application(self):
        """Exit the application gracefully."""
        self.logger.info("Exiting application")
        self.root.quit()

    def get_state_manager(self):
        """Get the state manager instance."""
        return self.state_manager

    def get_core_bridge(self):
        """Get the core bridge instance."""
        return self.core_bridge

    def is_services_ready(self) -> bool:
        """Check if all services are initialized and ready."""
        return self.services_initialized

    def is_user_authenticated(self) -> bool:
        """Check if user is authenticated."""
        return self.authenticated
