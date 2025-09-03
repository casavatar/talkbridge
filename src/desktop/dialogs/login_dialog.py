#!/usr/bin/env python3
"""
TalkBridge Desktop - Login Dialog
=================================

Modern, responsive login dialog with asynchronous authentication support.

Author: TalkBridge Team
Date: 2025-08-28
Version: 2.0

Features:
- Asynchronous authentication with visual feedback
- Credential management and persistence
- Thread-safe operations
- Modern UI with responsive design
- Comprehensive error handling and logging
"""

import logging
from typing import Optional, Tuple, Any, Callable
from dataclasses import dataclass
from enum import Enum
from pathlib import Path

from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QFormLayout,
    QLineEdit, QPushButton, QLabel, QCheckBox,
    QFrame, QMessageBox, QProgressBar, QWidget
)
from PySide6.QtCore import (
    Signal, QThread, QObject, QTimer, Qt
)
from PySide6.QtGui import QFont, QPixmap, QPainter, QPalette

# Import existing authentication module
try:
    from src.auth.auth_manager import AuthManager
except ImportError:
    AuthManager = None


# Constants
class UIConstants:
    """UI-related constants for the login dialog."""
    
    # Dialog dimensions
    MIN_WIDTH = 400
    MIN_HEIGHT = 400
    EXPANDED_HEIGHT = 450
    
    # Spacing and margins
    MAIN_MARGIN = 30
    MAIN_SPACING = 20
    FORM_SPACING = 15
    BUTTON_SPACING = 15
    
    # Component heights
    INPUT_HEIGHT = 35
    BUTTON_HEIGHT = 40
    PROGRESS_BAR_HEIGHT = 25
    STATUS_LABEL_HEIGHT = 45
    
    # Timeouts (in milliseconds)
    AUTH_TIMEOUT = 3000  # 3 seconds
    SUCCESS_DISPLAY_TIME = 1500  # 1.5 seconds
    ERROR_DISPLAY_TIME = 8000  # 8 seconds
    
    # Font sizes
    TITLE_FONT_SIZE = 24
    SUBTITLE_FONT_SIZE = 10


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
    state: AuthenticationState = AuthenticationState.IDLE


class StyleManager:
    """Manages CSS styles for the login dialog."""
    
    @staticmethod
    def get_main_style() -> str:
        """Returns the main stylesheet for the dialog."""
        return """
        QDialog {
            background-color: #2b2b2b;
            color: #ffffff;
        }

        QLabel {
            color: #ffffff;
        }

        QLineEdit {
            background-color: #3c3c3c;
            border: 2px solid #555555;
            border-radius: 5px;
            padding: 5px;
            color: #ffffff;
        }

        QLineEdit:focus {
            border-color: #0078d4;
        }

        QPushButton {
            background-color: #0078d4;
            color: #ffffff;
            border: none;
            border-radius: 5px;
            padding: 8px;
            font-weight: bold;
        }

        QPushButton:hover {
            background-color: #106ebe;
        }

        QPushButton:pressed {
            background-color: #005a9e;
        }

        QPushButton:disabled {
            background-color: #555555;
            color: #888888;
        }

        QCheckBox {
            color: #ffffff;
        }

        QCheckBox::indicator {
            width: 15px;
            height: 15px;
        }

        QCheckBox::indicator:unchecked {
            background-color: #3c3c3c;
            border: 2px solid #555555;
            border-radius: 3px;
        }

        QCheckBox::indicator:checked {
            background-color: #0078d4;
            border: 2px solid #0078d4;
            border-radius: 3px;
        }

        QProgressBar {
            border: 2px solid #555555;
            border-radius: 5px;
            background-color: #3c3c3c;
        }

        QProgressBar::chunk {
            background-color: #0078d4;
            border-radius: 3px;
        }
        """
    
    @staticmethod
    def get_status_style(status_type: str) -> str:
        """Returns stylesheet for status messages."""
        styles = {
            "loading": """
                color: #3498db;
                background-color: #1b2435;
                border: 1px solid #3498db;
                border-radius: 5px;
                padding: 8px;
                font-weight: bold;
                margin: 5px 0px;
            """,
            "success": """
                color: #2ed573;
                background-color: #1b2f1b;
                border: 1px solid #2ed573;
                border-radius: 5px;
                padding: 8px;
                font-weight: bold;
                margin: 5px 0px;
            """,
            "error": """
                color: #ff4757;
                background-color: #2f1b1b;
                border: 1px solid #ff4757;
                border-radius: 5px;
                padding: 8px;
                font-weight: bold;
                margin: 5px 0px;
            """
        }
        return styles.get(status_type, styles["error"])


class AuthWorker(QObject):
    """Worker thread for asynchronous authentication operations."""

    authentication_completed = Signal(bool, str)  # success, message
    authentication_progress = Signal(str)  # progress message

    def __init__(self, username: str, password: str, parent=None):
        super().__init__(parent)
        self.username = username
        self.password = password
        self.logger = logging.getLogger("talkbridge.desktop.auth")

    def authenticate(self) -> None:
        """Runs the authentication process asynchronously."""
        self.logger.info(f"🔄 AuthWorker.authenticate() STARTED for user: {self.username}")
        try:
            self.logger.info(f"🔄 Starting authentication for user: {self.username}")
            self.authentication_progress.emit("🔐 Initializing authentication...")

            if AuthManager:
                self.logger.info("📋 AuthManager available, attempting authentication...")
                self.authentication_progress.emit("📂 Loading user database...")
                
                # Add explicit timing for debugging
                import time
                start_time = time.time()
                
                auth_manager = AuthManager()
                load_time = time.time() - start_time
                self.logger.info(f"⏱️ AuthManager loaded in {load_time:.3f}s")
                
                self.authentication_progress.emit("🔍 Verifying credentials...")
                
                auth_start = time.time()
                success = auth_manager.authenticate(self.username, self.password)
                auth_time = time.time() - auth_start
                self.logger.info(f"⏱️ Authentication completed in {auth_time:.3f}s")

                if success:
                    message = "✅ Welcome! Authentication successful"
                    self.logger.info(f"✅ User {self.username} authenticated successfully")
                    self.authentication_progress.emit("✅ Authentication successful!")
                else:
                    message = "❌ Authentication failed. Please check your credentials"
                    self.logger.warning(f"❌ Authentication failed for user: {self.username}")
                    self.authentication_progress.emit("❌ Authentication failed")
            else:
                self.logger.error("❌ AuthManager not available - authentication not possible")
                success = False
                message = "❌ Authentication service unavailable. Please contact administrator."
                self.authentication_progress.emit("❌ Service unavailable")

            self.logger.info(f"🔄 Emitting authentication result: {success}")
            self.authentication_completed.emit(success, message)
            self.logger.info("✅ Authentication signal emitted successfully")

        except Exception as e:
            error_msg = f"❌ Authentication error: {str(e)}"
            self.logger.error(error_msg, exc_info=True)
            self.authentication_progress.emit(f"❌ Error: {str(e)}")
            self.authentication_completed.emit(False, error_msg)
        finally:
            self.logger.info(f"🔄 AuthWorker.authenticate() FINISHED for user: {self.username}")


class AuthenticationManager:
    """Manages authentication operations and thread lifecycle."""
    
    def __init__(self, logger: logging.Logger):
        self.logger = logger
        self.thread: Optional[QThread] = None
        self.worker: Optional[AuthWorker] = None
        self.timeout_timer: Optional[QTimer] = None
        self.cleanup_function: Optional[Callable] = None
        self.progress_callback: Optional[Callable[[str], None]] = None
        self._is_running = False
    
    def authenticate(self, username: str, password: str, 
                     completion_callback: Callable[[bool, str], None],
                     progress_callback: Optional[Callable[[str], None]] = None,
                     cleanup_function: Optional[Callable] = None) -> bool:
        """
        Initiates asynchronous authentication.
        
        Args:
            username: User's username
            password: User's password
            completion_callback: Callback for authentication result
            progress_callback: Optional callback for progress updates
            
        Returns:
            True if authentication started successfully
        """
        self.logger.info(f"🚀 AuthenticationManager.authenticate() called for user: {username}")
        
        if self._is_running:
            self.logger.warning("Authentication already in progress - returning False")
            return False
        
        try:
            self.progress_callback = progress_callback
            self.logger.info("📝 Creating authentication thread...")
            self._create_auth_thread(username, password, completion_callback)
            self.logger.info("⏰ Starting timeout timer...")
            self._start_timeout_timer(completion_callback)
            self.logger.info("🏃‍♂️ Starting thread...")
            self.thread.start()
            self._is_running = True
            self.logger.info("✅ Authentication process initiated successfully")
            return True
        except Exception as e:
            self.logger.error(f"❌ Failed to start authentication: {e}", exc_info=True)
            return False
    
    def _create_auth_thread(self, username: str, password: str,
                          completion_callback: Callable[[bool, str], None]) -> None:
        """Creates and configures the authentication thread."""
        # Use standard thread creation for AuthWorker
        self.thread = QThread()
        self.worker = AuthWorker(username, password)
        self.worker.moveToThread(self.thread)
        
        self.thread.started.connect(self.worker.authenticate)
        self.worker.authentication_completed.connect(self._on_auth_completed)
        self.worker.authentication_completed.connect(completion_callback)
        self.worker.authentication_completed.connect(self.thread.quit)
        self.thread.finished.connect(self.thread.deleteLater)
        # Connect progress signal if available
        if hasattr(self.worker, 'authentication_progress'):
            self.worker.authentication_progress.connect(self._on_auth_progress)
    
    def _on_auth_completed(self, success: bool, message: str) -> None:
        """Handle authentication completion - stop timeout timer."""
        self.logger.debug(f"Authentication completed: {success}")
        # Stop timeout timer on main thread
        if self.timeout_timer:
            self.timeout_timer.stop()
            self.timeout_timer.deleteLater()
            self.timeout_timer = None
    
    def _on_auth_progress(self, message: str) -> None:
        """Handle authentication progress updates."""
        self.logger.debug(f"Auth progress: {message}")
        if hasattr(self, 'progress_callback') and self.progress_callback:
            self.progress_callback(message)
    
    def _start_timeout_timer(self, completion_callback: Callable[[bool, str], None]) -> None:
        """Starts the authentication timeout timer."""
        self.timeout_timer = QTimer()
        self.timeout_timer.setSingleShot(True)
        self.timeout_timer.timeout.connect(
            lambda: self._handle_timeout(completion_callback)
        )
        self.timeout_timer.start(UIConstants.AUTH_TIMEOUT)
    
    def _handle_timeout(self, completion_callback: Callable[[bool, str], None]) -> None:
        """Handles authentication timeout."""
        self.logger.error("Authentication timeout")
        self.cleanup()
        timeout_msg = (
            "❌ Authentication timeout. The system may be slow.\n\n"
            "Try these test credentials:\n"
            "• admin / admin123\n"
            "• user / user123\n"
            "• test / test123\n"
            "• demo / demo123"
        )
        completion_callback(False, timeout_msg)
    
    def cleanup(self) -> None:
        """Safely cleans up authentication resources."""
        if self.timeout_timer:
            self.timeout_timer.stop()
            self.timeout_timer = None
        
        if self._is_running and self.thread:
            self.logger.info("Cleaning up authentication thread...")
            
            try:
                self._is_running = False
                
                if self.cleanup_function:
                    self.cleanup_function()
                else:
                    self._standard_thread_cleanup()
                
                self.thread = None
                self.worker = None
                
            except Exception as e:
                self.logger.error(f"Error during cleanup: {e}")
                self._force_cleanup()
    
    def _standard_thread_cleanup(self) -> None:
        """Standard thread cleanup procedure."""
        try:
            if self.thread and hasattr(self.thread, 'isRunning'):
                # Check if thread is still running (avoid accessing deleted objects)
                try:
                    is_running = self.thread.isRunning()
                except RuntimeError:
                    # Object already deleted by Qt
                    self.logger.debug("Thread object already deleted by Qt")
                    return
                
                if is_running:
                    self.thread.requestInterruption()
                    self.thread.quit()
                    
                    if not self.thread.wait(3000):
                        self.logger.warning("Thread did not stop gracefully, terminating")
                        try:
                            self.thread.terminate()
                            if not self.thread.wait(2000):
                                self.logger.error("Thread termination failed")
                        except RuntimeError:
                            self.logger.debug("Thread already terminated")
                
                # Schedule deletion safely
                try:
                    if hasattr(self.thread, 'deleteLater'):
                        self.thread.deleteLater()
                except RuntimeError:
                    self.logger.debug("Thread already scheduled for deletion")
        except Exception as e:
            self.logger.debug(f"Thread cleanup exception (expected): {e}")
        finally:
            # Always clear references
            self.thread = None
            self.worker = None
    
    def _force_cleanup(self) -> None:
        """Forces cleanup of resources."""
        self.thread = None
        self.worker = None
        self._is_running = False
    
    @property
    def is_running(self) -> bool:
        """Returns True if authentication is in progress."""
        return self._is_running


class CredentialManager:
    """Manages credential persistence and loading."""
    
    def __init__(self, state_manager: Any, logger: logging.Logger):
        self.state_manager = state_manager
        self.logger = logger
    
    def load_credentials(self) -> Tuple[str, bool]:
        """
        Loads saved credentials.
        
        Returns:
            Tuple of (username, remember_flag)
        """
        try:
            if not self._has_state_manager():
                return "", False
            
            remember = self.state_manager.get_setting('auth.remember_credentials', False)
            username = self.state_manager.get_setting('auth.username', '') if remember else ""
            
            return username, remember
            
        except Exception as e:
            self.logger.warning(f"Could not load saved credentials: {e}")
            return "", False
    
    def save_credentials(self, username: str, remember: bool) -> None:
        """
        Saves credentials if requested.
        
        Args:
            username: Username to save
            remember: Whether to remember credentials
        """
        try:
            if not self._has_state_manager():
                return
            
            self.state_manager.set_setting('auth.remember_credentials', remember)
            
            if remember:
                self.state_manager.set_setting('auth.username', username)
            else:
                self.state_manager.set_setting('auth.username', '')
                
        except Exception as e:
            self.logger.warning(f"Could not save credentials: {e}")
    
    def _has_state_manager(self) -> bool:
        """Checks if state manager is available and has required methods."""
        return (self.state_manager and 
                hasattr(self.state_manager, 'get_setting') and
                hasattr(self.state_manager, 'set_setting'))


class UIComponentFactory:
    """Factory for creating UI components with consistent styling."""
    
    @staticmethod
    def create_header_section() -> QFrame:
        """Creates the dialog header section."""
        header_frame = QFrame()
        header_layout = QVBoxLayout(header_frame)
        header_layout.setContentsMargins(0, 0, 0, 0)
        header_layout.setSpacing(10)

        # Main title
        title_label = QLabel("TalkBridge")
        title_font = QFont()
        title_font.setPointSize(UIConstants.TITLE_FONT_SIZE)
        title_font.setBold(True)
        title_label.setFont(title_font)
        title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        header_layout.addWidget(title_label)

        # Subtitle
        subtitle_label = QLabel("Real-Time Voice Translation")
        subtitle_font = QFont()
        subtitle_font.setPointSize(UIConstants.SUBTITLE_FONT_SIZE)
        subtitle_label.setFont(subtitle_font)
        subtitle_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        header_layout.addWidget(subtitle_label)

        return header_frame
    
    @staticmethod
    def create_login_form() -> Tuple[QFrame, QLineEdit, QLineEdit, QCheckBox]:
        """Creates the login form components."""
        form_frame = QFrame()
        form_layout = QFormLayout(form_frame)
        form_layout.setContentsMargins(0, 0, 0, 0)
        form_layout.setSpacing(UIConstants.FORM_SPACING)

        # Username field
        username_edit = QLineEdit()
        username_edit.setPlaceholderText("Enter your username")
        username_edit.setMinimumHeight(UIConstants.INPUT_HEIGHT)
        form_layout.addRow("Username:", username_edit)

        # Password field
        password_edit = QLineEdit()
        password_edit.setPlaceholderText("Enter your password")
        password_edit.setEchoMode(QLineEdit.EchoMode.Password)
        password_edit.setMinimumHeight(UIConstants.INPUT_HEIGHT)
        form_layout.addRow("Password:", password_edit)

        # Remember credentials checkbox
        remember_checkbox = QCheckBox("Remember credentials")
        form_layout.addRow("", remember_checkbox)

        return form_frame, username_edit, password_edit, remember_checkbox
    
    @staticmethod
    def create_button_section() -> Tuple[QFrame, QPushButton, QPushButton]:
        """Creates the action buttons."""
        button_frame = QFrame()
        button_layout = QHBoxLayout(button_frame)
        button_layout.setContentsMargins(0, 0, 0, 0)
        button_layout.setSpacing(UIConstants.BUTTON_SPACING)

        # Cancel button
        cancel_button = QPushButton("Cancel")
        cancel_button.setMinimumHeight(UIConstants.BUTTON_HEIGHT)
        button_layout.addWidget(cancel_button)

        # Login button
        login_button = QPushButton("Sign In")
        login_button.setMinimumHeight(UIConstants.BUTTON_HEIGHT)
        login_button.setDefault(True)
        button_layout.addWidget(login_button)

        return button_frame, cancel_button, login_button
    
    @staticmethod
    def create_progress_bar() -> QProgressBar:
        """Creates a progress bar for authentication feedback."""
        progress_bar = QProgressBar()
        progress_bar.setVisible(False)
        progress_bar.setMinimumHeight(UIConstants.PROGRESS_BAR_HEIGHT)
        return progress_bar
    
    @staticmethod
    def create_status_label() -> QLabel:
        """Creates a status label for messages."""
        status_label = QLabel()
        status_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        status_label.setVisible(False)
        status_label.setWordWrap(True)
        status_label.setMinimumHeight(UIConstants.STATUS_LABEL_HEIGHT)
        return status_label
    """Worker thread for asynchronous authentication operations."""

    authentication_completed = Signal(bool, str)  # success, message

    def __init__(self, username: str, password: str, parent=None):
        super().__init__(parent)
        self.username = username
        self.password = password
        self.logger = logging.getLogger("talkbridge.desktop.auth")

    def authenticate(self) -> None:
        """Runs the authentication process asynchronously."""
        try:
            self.logger.info(f"Starting authentication for user: {self.username}")

            # Use AuthManager for authentication
            if AuthManager:
                self.logger.info("AuthManager available, attempting authentication...")
                auth_manager = AuthManager()
                success = auth_manager.authenticate(self.username, self.password)

                if success:
                    message = "Welcome! Authentication successful"
                    self.logger.info(f"User {self.username} authenticated successfully")
                else:
                    message = "❌ Authentication failed. Please check your credentials"
                    self.logger.warning(f"Authentication failed for user: {self.username}")
            else:
                self.logger.error("AuthManager not available - authentication not possible")
                success = False
                message = "❌ Authentication service unavailable. Please contact administrator."

            self.logger.info(f"Authentication result: {success}, emitting signal...")
            self.authentication_completed.emit(success, message)
            self.logger.info("Signal emitted successfully")

        except Exception as e:
            error_msg = f"Error during authentication: {str(e)}"
            self.logger.error(error_msg, exc_info=True)
            self.authentication_completed.emit(False, f"❌ Authentication error: {str(e)}")
            self.authentication_completed.emit(False, error_msg)


class LoginDialog(QDialog):
    """
    Modern login dialog for TalkBridge Desktop.

    Features:
    - Asynchronous authentication with visual feedback
    - Credential management and persistence
    - Thread-safe operations with proper cleanup
    - Responsive UI design with consistent styling
    - Comprehensive error handling and user feedback
    """

    authentication_result = Signal(bool, str)  # success, message

    def __init__(self, state_manager=None, parent=None):
        super().__init__(parent)

        # Core components
        self.state_manager = state_manager
        self.logger = logging.getLogger("talkbridge.desktop.login")
        
        # Managers
        self.auth_manager = AuthenticationManager(self.logger)
        self.credential_manager = CredentialManager(state_manager, self.logger)
        
        # UI components
        self.username_edit: Optional[QLineEdit] = None
        self.password_edit: Optional[QLineEdit] = None
        self.remember_checkbox: Optional[QCheckBox] = None
        self.login_button: Optional[QPushButton] = None
        self.cancel_button: Optional[QPushButton] = None
        self.progress_bar: Optional[QProgressBar] = None
        self.status_label: Optional[QLabel] = None

        # State management
        self.current_state = AuthenticationState.IDLE
        self._result_emitted = False

        # Initialize UI
        self._setup_dialog()
        self._setup_ui_components()
        self._connect_signals()
        self._load_initial_state()

        self.logger.info("LoginDialog initialized successfully")

    def _setup_dialog(self) -> None:
        """Configures basic dialog properties."""
        self.setWindowTitle("TalkBridge - Sign In")
        self.setMinimumSize(UIConstants.MIN_WIDTH, UIConstants.MIN_HEIGHT)
        self.resize(UIConstants.MIN_WIDTH, UIConstants.MIN_HEIGHT)
        self.setModal(True)

        # Configure window flags
        self.setWindowFlags(
            Qt.WindowType.Dialog |
            Qt.WindowType.WindowTitleHint |
            Qt.WindowType.WindowCloseButtonHint
        )

    def _setup_ui_components(self) -> None:
        """Creates and arranges all UI components."""
        # Main layout
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(
            UIConstants.MAIN_MARGIN, UIConstants.MAIN_MARGIN,
            UIConstants.MAIN_MARGIN, UIConstants.MAIN_MARGIN
        )
        main_layout.setSpacing(UIConstants.MAIN_SPACING)

        # Create components using factory
        header_frame = UIComponentFactory.create_header_section()
        main_layout.addWidget(header_frame)

        form_frame, self.username_edit, self.password_edit, self.remember_checkbox = \
            UIComponentFactory.create_login_form()
        main_layout.addWidget(form_frame)

        self.progress_bar = UIComponentFactory.create_progress_bar()
        main_layout.addWidget(self.progress_bar)

        self.status_label = UIComponentFactory.create_status_label()
        main_layout.addWidget(self.status_label)

        button_frame, self.cancel_button, self.login_button = \
            UIComponentFactory.create_button_section()
        main_layout.addWidget(button_frame)

        # Add stretch to keep layout compact
        main_layout.addStretch()

        # Apply styling
        self.setStyleSheet(StyleManager.get_main_style())

    def _connect_signals(self) -> None:
        """Connects all signal-slot relationships."""
        self.login_button.clicked.connect(self._handle_login_attempt)
        self.cancel_button.clicked.connect(self._handle_cancel)
        
        # Enable login with Enter key
        self.username_edit.returnPressed.connect(self._handle_login_attempt)
        self.password_edit.returnPressed.connect(self._handle_login_attempt)

    def _load_initial_state(self) -> None:
        """Loads initial state including saved credentials."""
        username, remember = self.credential_manager.load_credentials()
        
        if username:
            self.username_edit.setText(username)
            self.remember_checkbox.setChecked(remember)
            self.password_edit.setFocus()
        else:
            self.username_edit.setFocus()

    def _handle_login_attempt(self) -> None:
        """Handles user login attempt."""
        if self.current_state == AuthenticationState.AUTHENTICATING:
            return

        # Validate input
        username = self.username_edit.text().strip()
        password = self.password_edit.text()

        if not username:
            self._show_status_message("⚠️ Please enter a username", "error")
            return

        # Start authentication
        self._set_authentication_state(AuthenticationState.AUTHENTICATING)
        
        success = self.auth_manager.authenticate(
            username, password, self._on_authentication_completed, self._on_auth_progress_update
        )
        
        if not success:
            self._set_authentication_state(AuthenticationState.FAILED)
            self._show_status_message("❌ Failed to start authentication", "error")

    def _handle_cancel(self) -> None:
        """Handles cancel button click."""
        self.logger.info("User cancelled login")
        self._set_authentication_state(AuthenticationState.CANCELLED)
        self._cleanup_and_emit_result(False, "Login cancelled by user")
        self.reject()

    def _on_authentication_completed(self, success: bool, message: str) -> None:
        """
        Handles authentication completion.
        
        Args:
            success: Whether authentication was successful
            message: Result message
        """
        if success:
            self._handle_successful_authentication(message)
        else:
            self._handle_failed_authentication(message)

    def _handle_successful_authentication(self, message: str) -> None:
        """Handles successful authentication."""
        self.logger.info("Authentication successful")
        self._set_authentication_state(AuthenticationState.SUCCESS)
        self._show_status_message(message, "success")
        
        # Save credentials if requested
        username = self.username_edit.text().strip()
        remember = self.remember_checkbox.isChecked()
        self.credential_manager.save_credentials(username, remember)
        
        # Delay before closing to show success message
        QTimer.singleShot(UIConstants.SUCCESS_DISPLAY_TIME, self._complete_successful_login)

    def _handle_failed_authentication(self, message: str) -> None:
        """Handles failed authentication."""
        self.logger.warning(f"Authentication failed: {message}")
        self._set_authentication_state(AuthenticationState.FAILED)
        self._show_status_message(message, "error")
        
        # Clear password and focus for retry
        self.password_edit.clear()
        self.password_edit.setFocus()
        
        self._cleanup_and_emit_result(False, message)

    def _on_auth_progress_update(self, message: str) -> None:
        """Handle authentication progress updates from the worker."""
        self.logger.debug(f"Authentication progress: {message}")
        self._show_status_message(message, "loading")

    def _complete_successful_login(self) -> None:
        """Completes successful login process."""
        self._cleanup_and_emit_result(True, "Authentication successful")
        self.accept()

    def _set_authentication_state(self, state: AuthenticationState) -> None:
        """
        Sets the current authentication state and updates UI.
        
        Args:
            state: New authentication state
        """
        self.current_state = state
        
        # Update UI based on state
        is_authenticating = (state == AuthenticationState.AUTHENTICATING)
        
        # Enable/disable controls
        self.username_edit.setEnabled(not is_authenticating)
        self.password_edit.setEnabled(not is_authenticating)
        self.remember_checkbox.setEnabled(not is_authenticating)
        self.login_button.setEnabled(not is_authenticating)

        # Show/hide progress bar
        self.progress_bar.setVisible(is_authenticating)
        if is_authenticating:
            self.progress_bar.setRange(0, 0)  # Indeterminate progress
            self._show_status_message("🔐 Verifying credentials...", "loading")
        
        # Adjust dialog size if needed
        self._adjust_dialog_size()

    def _show_status_message(self, message: str, message_type: str) -> None:
        """
        Shows a status message to the user.
        
        Args:
            message: Message to display
            message_type: Type of message (loading, success, error)
        """
        self.status_label.setText(message)
        self.status_label.setStyleSheet(StyleManager.get_status_style(message_type))
        self.status_label.setVisible(True)
        
        # Auto-hide error messages after delay
        if message_type == "error":
            QTimer.singleShot(
                UIConstants.ERROR_DISPLAY_TIME,
                lambda: self.status_label.setVisible(False)
            )
        
        self._adjust_dialog_size()

    def _adjust_dialog_size(self) -> None:
        """Adjusts dialog size to accommodate visible elements."""
        current_size = self.size()
        min_height = (UIConstants.EXPANDED_HEIGHT 
                     if (self.progress_bar.isVisible() or self.status_label.isVisible())
                     else UIConstants.MIN_HEIGHT)
        
        if current_size.height() < min_height:
            self.resize(current_size.width(), min_height)

    def _cleanup_and_emit_result(self, success: bool, message: str) -> None:
        """
        Cleans up resources and emits result if not already done.
        
        Args:
            success: Authentication success status
            message: Result message
        """
        if not self._result_emitted:
            self._result_emitted = True
            self.authentication_result.emit(success, message)
        
        self.auth_manager.cleanup()

    def closeEvent(self, event) -> None:
        """Handles dialog close event."""
        self.logger.info("Login dialog close event")
        self._cleanup_and_emit_result(False, "Login window closed")
        super().closeEvent(event)

    def reject(self) -> None:
        """Handles dialog rejection (ESC, X button)."""
        self.logger.info("Login dialog rejected")
        self._cleanup_and_emit_result(False, "Login cancelled")
        super().reject()


# Legacy compatibility - remove old implementation after this point
class AuthWorker(QObject):
    """Worker thread for asynchronous authentication operations."""

    authentication_completed = Signal(bool, str)  # success, message

    def __init__(self, username: str, password: str, parent=None):
        super().__init__(parent)
        self.username = username
        self.password = password
        self.logger = logging.getLogger("talkbridge.desktop.auth")

    def authenticate(self) -> None:
        """Runs the authentication process asynchronously."""
        try:
            self.logger.info(f"Starting authentication for user: {self.username}")

            # Use AuthManager for authentication
            if AuthManager:
                self.logger.info("AuthManager available, attempting authentication...")
                auth_manager = AuthManager()
                success = auth_manager.authenticate(self.username, self.password)

                if success:
                    message = "Welcome! Authentication successful"
                    self.logger.info(f"User {self.username} authenticated successfully")
                else:
                    message = "❌ Authentication failed. Please check your credentials"
                    self.logger.warning(f"Authentication failed for user: {self.username}")
            else:
                self.logger.error("AuthManager not available - authentication not possible")
                success = False
                message = "❌ Authentication service unavailable. Please contact administrator."

            self.logger.info(f"Authentication result: {success}, emitting signal...")
            self.authentication_completed.emit(success, message)
            self.logger.info("Signal emitted successfully")

        except Exception as e:
            error_msg = f"Error during authentication: {str(e)}"
            self.logger.error(error_msg, exc_info=True)
            self.authentication_completed.emit(False, f"❌ Authentication error: {str(e)}")
            self.authentication_completed.emit(False, error_msg)
