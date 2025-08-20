#! /src/desktop/windows/dashboard.py
"""
TalkBridge Desktop - Application
================================

Módulo application para TalkBridge

Author: TalkBridge Team
Date: 2025-08-19
Version: 1.0

Requirements:
- PyQt6
======================================================================
Functions:
- __init__: Initializes the application.
- run: Runs the full application.
- _show_splash_screen: Shows the splash screen during loading.
- _initialize_core_components: Initializes the application's core components.
- _show_login_dialog: Shows the login dialog and handles authentication.
- _initialize_services_async: Initializes services asynchronously.
- _do_initialize_services: Performs actual service initialization.
- _on_authentication_completed: Handles authentication result.
- _on_services_initialized: Handles service initialization result.
- _show_main_window: Shows the application's main window.
======================================================================
"""

import sys
import logging
from typing import Optional
from pathlib import Path

from PyQt6.QtWidgets import QApplication, QMessageBox, QSplashScreen
from PyQt6.QtCore import QObject, pyqtSignal, QTimer, QThread
from PyQt6.QtGui import QPixmap, QPainter, QFont

from src.desktop.app.state_manager import StateManager
from src.desktop.dialogs.login_dialog import LoginDialog
from src.desktop.app.main_window import MainWindow
from src.desktop.services.core_bridge import CoreBridge


class TalkBridgeApplication(QApplication):
    """
    Main TalkBridge Desktop application.

    Handles full system initialization, including:
    - User authentication
    - Service initialization
    - Global state management
    - Coordination between windows and components
    """

    # Signals for communication between components
    authentication_completed = pyqtSignal(bool, str)  # success, message
    services_initialized = pyqtSignal(bool)  # success
    application_ready = pyqtSignal()

    def __init__(self, argv: list) -> None:
        """
        Initializes the application.

        Args:
            argv: Command line arguments
        """
        super().__init__(argv)

        # Configure logger
        self.logger = logging.getLogger("talkbridge.desktop.app")

        # Main components
        self.state_manager: Optional[StateManager] = None
        self.core_bridge: Optional[CoreBridge] = None
        self.main_window: Optional[MainWindow] = None
        self.splash_screen: Optional[QSplashScreen] = None

        # Initialization states
        self.is_authenticated = False
        self.services_ready = False

        # Connect signals
        self.authentication_completed.connect(self._on_authentication_completed)
        self.services_initialized.connect(self._on_services_initialized)

        self.logger.info("TalkBridgeApplication initialized")

    def run(self) -> int:
        """
        Runs the full application.

        Returns:
            int: Application exit code
        """
        try:
            # Show splash screen
            self._show_splash_screen()

            # Initialize core components
            if not self._initialize_core_components():
                self.logger.error("Core components initialization failed")
                return 1

            # Show login dialog
            if not self._show_login_dialog():
                self.logger.info("User cancelled login")
                return 0

            # Initialize services
            self._initialize_services_async()

            # Run main loop
            return self.exec()

        except Exception as e:
            self.logger.error(f"Application execution error: {e}", exc_info=True)
            self._show_critical_error("Critical Error", str(e))
            return 1
        finally:
            self._cleanup()

    def _show_splash_screen(self) -> None:
        """Shows the splash screen during loading."""
        try:
            # Create basic splash screen
            splash_pixmap = QPixmap(400, 300)
            splash_pixmap.fill(self.palette().color(self.palette().ColorRole.Window))

            painter = QPainter(splash_pixmap)
            painter.setFont(QFont("Arial", 16))
            painter.drawText(
                splash_pixmap.rect(),
                0x84,  # Qt.AlignCenter
                "TalkBridge\nLoading..."
            )
            painter.end()

            self.splash_screen = QSplashScreen(splash_pixmap)
            self.splash_screen.show()
            self.processEvents()

        except Exception as e:
            self.logger.warning(f"Could not show splash screen: {e}")

    def _initialize_core_components(self) -> bool:
        """
        Initializes the application's core components.

        Returns:
            bool: True if initialization was successful
        """
        try:
            self.logger.info("Initializing core components...")

            # Initialize StateManager
            self.state_manager = StateManager()
            if not self.state_manager.initialize():
                raise Exception("StateManager initialization failed")

            # Initialize CoreBridge
            self.core_bridge = CoreBridge(self.state_manager)

            self.logger.info("Core components initialized successfully")
            return True

        except Exception as e:
            self.logger.error(f"Error initializing core components: {e}")
            return False

    def _show_login_dialog(self) -> bool:
        """
        Shows the login dialog and handles authentication.

        Returns:
            bool: True if login was successful
        """
        try:
            if self.splash_screen:
                self.splash_screen.showMessage("Signing in...", 0x82)  # Qt.AlignBottom

            login_dialog = LoginDialog(self.state_manager)
            login_dialog.authentication_result.connect(self.authentication_completed)

            # Show modal dialog
            result = login_dialog.exec()

            # Process result
            if result == login_dialog.DialogCode.Accepted and self.is_authenticated:
                self.logger.info("Authentication successful")
                return True
            else:
                self.logger.info("Authentication failed or cancelled")
                return False

        except Exception as e:
            self.logger.error(f"Login process error: {e}")
            self._show_critical_error("Login Error", str(e))
            return False

    def _initialize_services_async(self) -> None:
        """Initializes services asynchronously."""
        if self.splash_screen:
            self.splash_screen.showMessage("Initializing services...", 0x82)

        # Use QTimer for non-blocking initialization
        QTimer.singleShot(100, self._do_initialize_services)

    def _do_initialize_services(self) -> None:
        """Performs actual service initialization."""
        try:
            self.logger.info("Initializing services...")

            # Initialize services via CoreBridge
            success = self.core_bridge.initialize_all_services()

            self.services_initialized.emit(success)

        except Exception as e:
            self.logger.error(f"Error initializing services: {e}")
            self.services_initialized.emit(False)

    def _on_authentication_completed(self, success: bool, message: str) -> None:
        """
        Handles authentication result.

        Args:
            success: True if authentication was successful
            message: Descriptive result message
        """
        self.is_authenticated = success
        if success:
            self.logger.info("User authenticated successfully")
        else:
            self.logger.warning(f"Authentication failed: {message}")

    def _on_services_initialized(self, success: bool) -> None:
        """
        Handles service initialization result.

        Args:
            success: True if services were initialized successfully
        """
        self.services_ready = success

        if success:
            self.logger.info("Services initialized successfully")
            self._show_main_window()
        else:
            self.logger.error("Service initialization failed")
            self._show_critical_error(
                "Service Error",
                "Could not initialize all required services."
            )

    def _show_main_window(self) -> None:
        """Shows the application's main window."""
        try:
            # Hide splash screen
            if self.splash_screen:
                self.splash_screen.close()
                self.splash_screen = None

            # Create and show main window
            self.main_window = MainWindow(self.state_manager, self.core_bridge)
            self.main_window.show()

            # Emit application ready signal
            self.application_ready.emit()

            self.logger.info("Application fully initialized")

        except Exception as e:
            self.logger.error(f"Error showing main window: {e}")
            self._show_critical_error("Interface Error", str(e))

    def _show_critical_error(self, title: str, message: str) -> None:
        """
        Shows a critical error to the user.

        Args:
            title: Error title
            message: Descriptive message
        """
        msg_box = QMessageBox()
        msg_box.setIcon(QMessageBox.Icon.Critical)
        msg_box.setWindowTitle(title)
        msg_box.setText(message)
        msg_box.setDetailedText(f"See logs in data/logs/desktop.log for more details.")
        msg_box.setStandardButtons(QMessageBox.StandardButton.Ok)
        msg_box.exec()

    def _cleanup(self) -> None:
        """Cleans up resources when closing the application."""
        try:
            self.logger.info("Cleaning up application resources...")

            # Close splash screen if it still exists
            if self.splash_screen:
                self.splash_screen.close()

            # Clean up services
            if self.core_bridge:
                self.core_bridge.cleanup()

            # Save state
            if self.state_manager:
                self.state_manager.save_state()

            self.logger.info("Cleanup completed")

        except Exception as e:
            self.logger.error(f"Error during cleanup: {e}")

    def closeEvent(self, event) -> None:
        """Handles the application's close event."""
        self.logger.info("Closing application...")
        self._cleanup()
        super().closeEvent(event)