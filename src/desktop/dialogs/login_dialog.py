#! /src/desktop/dialogs/login_dialog.py
#----------------------------------------------------------------------------------------------------------------------------
# description: Login dialog for TalkBridge Desktop application
#----------------------------------------------------------------------------------------------------------------------------
# author: ingekastel
# date: 2025-06-02
# version: 1.0
#----------------------------------------------------------------------------------------------------------------------------
# requirements:
# - PyQt6
#----------------------------------------------------------------------------------------------------------------------------
# functions:
# - create_login_dialog: Create and display the login dialog
# - handle_login: Process the login credentials
# - show_login_error: Display an error message for failed login attempts
#----------------------------------------------------------------------------------------------------------------------------

import logging
from typing import Optional
from pathlib import Path

from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QFormLayout,
    QLineEdit, QPushButton, QLabel, QCheckBox,
    QFrame, QMessageBox, QProgressBar, QWidget
)
from PyQt6.QtCore import (
    pyqtSignal, QThread, QObject, QTimer, Qt
)
from PyQt6.QtGui import QFont, QPixmap, QPainter, QPalette

# Import existing authentication module
try:
    from src.ui.auth.auth_manager import AuthManager
except ImportError:
    # Fallback if not available
    AuthManager = None


class AuthWorker(QObject):
    """Worker thread for asynchronous authentication operations."""

    authentication_completed = pyqtSignal(bool, str)  # success, message

    def __init__(self, username: str, password: str, parent=None):
        super().__init__(parent)
        self.username = username
        self.password = password
        self.logger = logging.getLogger("talkbridge.desktop.auth")

    def authenticate(self) -> None:
        """Runs the authentication process asynchronously."""
        try:
            self.logger.info(f"Starting authentication for user: {self.username}")

            # Use AuthManager if available
            if AuthManager:
                auth_manager = AuthManager()
                success = auth_manager.authenticate(self.username, self.password)

                if success:
                    message = "Authentication successful"
                    self.logger.info(f"User {self.username} authenticated successfully")
                else:
                    message = "Invalid credentials"
                    self.logger.warning(f"Authentication failed for user: {self.username}")
            else:
                # Demo/development mode - always accepts admin/admin
                success = (self.username == "admin" and self.password == "admin")
                message = "Authentication successful (demo mode)" if success else "Invalid credentials"
                self.logger.warning("AuthManager not available, using demo mode")

            self.authentication_completed.emit(success, message)

        except Exception as e:
            error_msg = f"Error during authentication: {str(e)}"
            self.logger.error(error_msg, exc_info=True)
            self.authentication_completed.emit(False, error_msg)


class LoginDialog(QDialog):
    """
    Login dialog for TalkBridge Desktop.

    Features:
    - Asynchronous authentication with visual feedback
    - Option to remember credentials
    - Integration with existing AuthManager
    - Modern and responsive design
    """

    authentication_result = pyqtSignal(bool, str)  # success, message

    def __init__(self, state_manager=None, parent=None):
        super().__init__(parent)

        self.state_manager = state_manager
        self.logger = logging.getLogger("talkbridge.desktop.login")

        # UI components
        self.username_edit: Optional[QLineEdit] = None
        self.password_edit: Optional[QLineEdit] = None
        self.remember_checkbox: Optional[QCheckBox] = None
        self.login_button: Optional[QPushButton] = None
        self.cancel_button: Optional[QPushButton] = None
        self.progress_bar: Optional[QProgressBar] = None
        self.status_label: Optional[QLabel] = None

        # Worker thread for authentication
        self.auth_thread: Optional[QThread] = None
        self.auth_worker: Optional[AuthWorker] = None

        # Dialog state
        self.is_authenticating = False

        # Setup UI
        self.setup_ui()
        self.setup_connections()
        self.load_saved_credentials()

        self.logger.info("LoginDialog initialized")

    def setup_ui(self) -> None:
        """Sets up the dialog's user interface."""
        self.setWindowTitle("TalkBridge - Sign In")
        self.setFixedSize(400, 350)
        self.setModal(True)

        # Configure window flags
        self.setWindowFlags(
            Qt.WindowType.Dialog |
            Qt.WindowType.WindowTitleHint |
            Qt.WindowType.WindowCloseButtonHint
        )

        # Main layout
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(30, 30, 30, 30)
        main_layout.setSpacing(20)

        # Header with logo/title
        self._create_header(main_layout)

        # Login form
        self._create_login_form(main_layout)

        # Progress bar
        self.progress_bar = QProgressBar()
        self.progress_bar.setVisible(False)
        main_layout.addWidget(self.progress_bar)

        # Status label
        self.status_label = QLabel()
        self.status_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.status_label.setVisible(False)
        main_layout.addWidget(self.status_label)

        # Buttons
        self._create_buttons(main_layout)

        # Apply styles
        self._apply_styles()

    def _create_header(self, parent_layout: QVBoxLayout) -> None:
        """Creates the dialog header section."""
        header_frame = QFrame()
        header_layout = QVBoxLayout(header_frame)
        header_layout.setContentsMargins(0, 0, 0, 0)
        header_layout.setSpacing(10)

        # Main title
        title_label = QLabel("TalkBridge")
        title_font = QFont()
        title_font.setPointSize(24)
        title_font.setBold(True)
        title_label.setFont(title_font)
        title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        header_layout.addWidget(title_label)

        # Subtitle
        subtitle_label = QLabel("Real-Time Voice Translation")
        subtitle_font = QFont()
        subtitle_font.setPointSize(10)
        subtitle_label.setFont(subtitle_font)
        subtitle_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        header_layout.addWidget(subtitle_label)

        parent_layout.addWidget(header_frame)

    def _create_login_form(self, parent_layout: QVBoxLayout) -> None:
        """Creates the login form."""
        form_frame = QFrame()
        form_layout = QFormLayout(form_frame)
        form_layout.setContentsMargins(0, 0, 0, 0)
        form_layout.setSpacing(15)

        # Username field
        self.username_edit = QLineEdit()
        self.username_edit.setPlaceholderText("Enter your username")
        self.username_edit.setMinimumHeight(35)
        form_layout.addRow("Username:", self.username_edit)

        # Password field
        self.password_edit = QLineEdit()
        self.password_edit.setPlaceholderText("Enter your password")
        self.password_edit.setEchoMode(QLineEdit.EchoMode.Password)
        self.password_edit.setMinimumHeight(35)
        form_layout.addRow("Password:", self.password_edit)

        # Remember credentials checkbox
        self.remember_checkbox = QCheckBox("Remember credentials")
        form_layout.addRow("", self.remember_checkbox)

        parent_layout.addWidget(form_frame)

    def _create_buttons(self, parent_layout: QVBoxLayout) -> None:
        """Creates the action buttons."""
        button_frame = QFrame()
        button_layout = QHBoxLayout(button_frame)
        button_layout.setContentsMargins(0, 0, 0, 0)
        button_layout.setSpacing(15)

        # Cancel button
        self.cancel_button = QPushButton("Cancel")
        self.cancel_button.setMinimumHeight(40)
        button_layout.addWidget(self.cancel_button)

        # Login button
        self.login_button = QPushButton("Sign In")
        self.login_button.setMinimumHeight(40)
        self.login_button.setDefault(True)
        button_layout.addWidget(self.login_button)

        parent_layout.addWidget(button_frame)

    def _apply_styles(self) -> None:
        """Applies CSS styles to the dialog."""
        style = """
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
        self.setStyleSheet(style)

    def setup_connections(self) -> None:
        """Configures signal and slot connections."""
        self.login_button.clicked.connect(self.start_authentication)
        self.cancel_button.clicked.connect(self.reject)

        # Allow login with Enter
        self.username_edit.returnPressed.connect(self.start_authentication)
        self.password_edit.returnPressed.connect(self.start_authentication)

    def load_saved_credentials(self) -> None:
        """Loads saved credentials if available."""
        try:
            if self.state_manager and hasattr(self.state_manager, 'get_setting'):
                remember = self.state_manager.get_setting('auth.remember_credentials', False)

                if remember:
                    username = self.state_manager.get_setting('auth.username', '')
                    self.username_edit.setText(username)
                    self.remember_checkbox.setChecked(True)

                    # Focus password if username is already loaded
                    if username:
                        self.password_edit.setFocus()
                    else:
                        self.username_edit.setFocus()
                else:
                    self.username_edit.setFocus()
            else:
                self.username_edit.setFocus()

        except Exception as e:
            self.logger.warning(f"Could not load saved credentials: {e}")
            self.username_edit.setFocus()

    def save_credentials(self) -> None:
        """Saves credentials if the user requests it."""
        try:
            if self.state_manager and hasattr(self.state_manager, 'set_setting'):
                remember = self.remember_checkbox.isChecked()
                self.state_manager.set_setting('auth.remember_credentials', remember)

                if remember:
                    username = self.username_edit.text().strip()
                    self.state_manager.set_setting('auth.username', username)
                else:
                    # Clear saved credentials
                    self.state_manager.set_setting('auth.username', '')

        except Exception as e:
            self.logger.warning(f"Could not save credentials: {e}")

    def start_authentication(self) -> None:
        """Starts the asynchronous authentication process."""
        if self.is_authenticating:
            return

        # Validate fields
        username = self.username_edit.text().strip()
        password = self.password_edit.text()

        if not username or not password:
            self.show_error_message("Please enter username and password")
            return

        # Set UI to loading state
        self.set_ui_loading_state(True)

        # Create worker thread
        self.auth_thread = QThread()
        self.auth_worker = AuthWorker(username, password)
        self.auth_worker.moveToThread(self.auth_thread)

        # Connect signals
        self.auth_thread.started.connect(self.auth_worker.authenticate)
        self.auth_worker.authentication_completed.connect(self.on_authentication_completed)
        self.auth_worker.authentication_completed.connect(self.auth_thread.quit)
        self.auth_thread.finished.connect(self.auth_thread.deleteLater)

        # Start thread
        self.auth_thread.start()

    def set_ui_loading_state(self, loading: bool) -> None:
        """
        Sets the UI to loading state.

        Args:
            loading: True if in loading state
        """
        self.is_authenticating = loading

        # Disable/enable controls
        self.username_edit.setEnabled(not loading)
        self.password_edit.setEnabled(not loading)
        self.remember_checkbox.setEnabled(not loading)
        self.login_button.setEnabled(not loading)

        # Show/hide progress bar
        self.progress_bar.setVisible(loading)
        if loading:
            self.progress_bar.setRange(0, 0)  # Indeterminate progress
            self.status_label.setText("Authenticating...")
            self.status_label.setVisible(True)
        else:
            self.progress_bar.setVisible(False)
            self.status_label.setVisible(False)

    def on_authentication_completed(self, success: bool, message: str) -> None:
        """
        Handles the result of authentication.

        Args:
            success: True if authentication was successful
            message: Descriptive result message
        """
        self.set_ui_loading_state(False)

        if success:
            self.logger.info("Authentication successful")
            self.save_credentials()
            self.authentication_result.emit(True, message)
            self.accept()
        else:
            self.logger.warning(f"Authentication failed: {message}")
            self.show_error_message(message)
            self.authentication_result.emit(False, message)

    def show_error_message(self, message: str) -> None:
        """
        Shows an error message to the user.

        Args:
            message: Error message
        """
        self.status_label.setText(f"Error: {message}")
        self.status_label.setStyleSheet("color: #d13438;")
        self.status_label.setVisible(True)

        # Hide message after 5 seconds
        QTimer.singleShot(5000, lambda: self.status_label.setVisible(False))

    def closeEvent(self, event) -> None:
        """Handles the dialog close event."""
        if self.is_authenticating and self.auth_thread:
            # Cancel authentication in progress
            self.auth_thread.terminate()
            self.auth_thread.wait()

        super().closeEvent(event)