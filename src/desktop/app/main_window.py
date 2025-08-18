
#! /src/desktop/app/main_window.py
#----------------------------------------------------------------------------------------------------------------------------
# description: Main application window for TalkBridge Desktop
#----------------------------------------------------------------------------------------------------------------------------
# author: ingekastel
# date: 2025-06-02
# version: 1.0
#----------------------------------------------------------------------------------------------------------------------------
# requirements:
# - PyQt6
#----------------------------------------------------------------------------------------------------------------------------
# functions:
# - setup_ui: Set up the user interface for the main window
# - load_user_data: Load user-specific data for the main window
# - refresh_data: Refresh the displayed data
# - show_error: Display an error message
#----------------------------------------------------------------------------------------------------------------------------

import logging
from typing import Optional

from PyQt6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QMenuBar, QStatusBar, QStackedWidget, QToolBar,
    QLabel, QMessageBox
)
from PyQt6.QtCore import pyqtSignal, QTimer, Qt
from PyQt6.QtGui import QAction, QFont, QIcon

from src.desktop.windows.dashboard import Dashboard



class MainWindow(QMainWindow):
    """
    Main window of TalkBridge Desktop.

    Features:
    - MenuBar with main options
    - StatusBar with status information
    - StackedWidget for different views
    - Centralized window management
    """

    # Signals
    window_closing = pyqtSignal()
    view_changed = pyqtSignal(str)  # view_name

    def __init__(self, state_manager=None, core_bridge=None, parent=None):
        super().__init__(parent)

        self.state_manager = state_manager
        self.core_bridge = core_bridge
        self.logger = logging.getLogger("talkbridge.desktop.mainwindow")

        # Main widgets
        self.central_widget: Optional[QWidget] = None
        self.stacked_widget: Optional[QStackedWidget] = None
        self.dashboard: Optional[Dashboard] = None

        # State
        self.current_view = "dashboard"

        self.setup_ui()
        self.create_menu_bar()
        self.create_status_bar()
        self.connect_signals()

        # Configure window
        self.configure_window()

        self.logger.info("MainWindow initialized")
    
    def setup_ui(self) -> None:
        """Sets up the main interface."""
        # Central widget with stacked layout
        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)

        layout = QVBoxLayout(self.central_widget)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        # Stacked widget for different views
        self.stacked_widget = QStackedWidget()
        layout.addWidget(self.stacked_widget)

        # Create and add dashboard
        self.dashboard = Dashboard(self.state_manager, self.core_bridge)
        self.stacked_widget.addWidget(self.dashboard)

        # Show dashboard by default
        self.stacked_widget.setCurrentWidget(self.dashboard)
    
    def create_menu_bar(self) -> None:
        """Creates the menu bar."""
        menubar = self.menuBar()

        # File menu
        file_menu = menubar.addMenu("&File")

        # New Chat action
        new_chat_action = QAction("&New Chat", self)
        new_chat_action.setShortcut("Ctrl+N")
        new_chat_action.setStatusTip("Start new conversation")
        new_chat_action.triggered.connect(lambda: self.show_view("chat"))
        file_menu.addAction(new_chat_action)

        file_menu.addSeparator()

        # Exit action
        exit_action = QAction("&Exit", self)
        exit_action.setShortcut("Ctrl+Q")
        exit_action.setStatusTip("Exit the application")
        exit_action.triggered.connect(self.close)
        file_menu.addAction(exit_action)

        # View menu
        view_menu = menubar.addMenu("&View")

        dashboard_action = QAction("&Dashboard", self)
        dashboard_action.setShortcut("Ctrl+D")
        dashboard_action.triggered.connect(lambda: self.show_view("dashboard"))
        view_menu.addAction(dashboard_action)

        # Tools menu
        tools_menu = menubar.addMenu("&Tools")

        settings_action = QAction("&Settings", self)
        settings_action.setShortcut("Ctrl+,")
        settings_action.triggered.connect(lambda: self.show_view("settings"))
        tools_menu.addAction(settings_action)

        # Help menu
        help_menu = menubar.addMenu("&Help")

        about_action = QAction("&About", self)
        about_action.triggered.connect(self.show_about)
        help_menu.addAction(about_action)
    
    def create_status_bar(self) -> None:
        """Creates the status bar."""
        self.statusBar().showMessage("TalkBridge Desktop - Ready")

        # Label to show user info
        self.user_status_label = QLabel("User: Loading...")
        self.statusBar().addPermanentWidget(self.user_status_label)

        # Label to show connection status
        self.connection_status_label = QLabel("●")
        self.connection_status_label.setStyleSheet("color: #16c60c; font-size: 16px;")
        self.statusBar().addPermanentWidget(self.connection_status_label)
    
    def configure_window(self) -> None:
        """Configures window properties."""
        self.setWindowTitle("TalkBridge Desktop - Real-Time Voice Translation")

        # Size and position
        if self.state_manager:
            width = self.state_manager.get_config("ui.window_size.width", 1200)
            height = self.state_manager.get_config("ui.window_size.height", 800)
        else:
            width, height = 1200, 800

        self.resize(width, height)

        # Center window
        self.center_window()

        # Minimum size
        self.setMinimumSize(800, 600)
    
    def center_window(self) -> None:
        """Centers the window on the screen."""
        screen = self.screen().availableGeometry()
        window = self.frameGeometry()
        window.moveCenter(screen.center())
        self.move(window.topLeft())
    
    def connect_signals(self) -> None:
        """Connects component signals."""
        if self.dashboard:
            self.dashboard.service_action_requested.connect(
                self.handle_service_action
            )
            self.dashboard.quick_action_requested.connect(
                self.handle_quick_action
            )

        if self.state_manager:
            self.state_manager.user_session_changed.connect(
                self.update_user_status
            )
            self.state_manager.service_status_changed.connect(
                self.update_connection_status
            )
    
    def show_view(self, view_name: str) -> None:
        """
        Shows a specific view.

        Args:
            view_name: Name of the view to show
        """
        if view_name == "dashboard" and self.dashboard:
            self.stacked_widget.setCurrentWidget(self.dashboard)
            self.current_view = "dashboard"
            self.statusBar().showMessage("View: Dashboard")
        elif view_name == "chat":
            # TODO: Implement chat window
            self.statusBar().showMessage("Chat - Coming soon")
        elif view_name == "settings":
            # TODO: Implement settings window
            self.statusBar().showMessage("Settings - Coming soon")

        self.view_changed.emit(view_name)
    
    def handle_service_action(self, service_name: str) -> None:
        """
        Handles service actions from the dashboard.

        Args:
            service_name: Name of the service
        """
        self.logger.info(f"Service action requested: {service_name}")

        if self.core_bridge:
            current_status = self.core_bridge.get_service_status(service_name)

            if current_status == "disconnected" or current_status == "error":
                # Try to reconnect/initialize service
                self.statusBar().showMessage(f"Connecting service {service_name}...")
                # TODO: Implement specific reconnection logic
            elif current_status == "connected":
                # Show service configuration
                self.statusBar().showMessage(f"Opening configuration for {service_name}...")
                # TODO: Open service configuration window
    
    def handle_quick_action(self, action_name: str) -> None:
        """
        Handles quick actions from the dashboard.

        Args:
            action_name: Name of the action
        """
        self.logger.info(f"Quick action requested: {action_name}")

        if action_name == "chat":
            self.show_view("chat")
        elif action_name == "settings":
            self.show_view("settings")
        elif action_name == "avatar":
            self.statusBar().showMessage("Avatar - Coming soon")
        elif action_name == "stats":
            self.statusBar().showMessage("Statistics - Coming soon")
    
    def update_user_status(self, user_session) -> None:
        """
        Updates user info in the status bar.

        Args:
            user_session: Current user session
        """
        if user_session and user_session.is_authenticated:
            self.user_status_label.setText(f"User: {user_session.username}")
        else:
            self.user_status_label.setText("User: Not authenticated")
    
    def update_connection_status(self, service_name: str, status: str) -> None:
        """
        Updates the connection status indicator.

        Args:
            service_name: Name of the service
            status: Service status
        """
        # Determine color based on critical service states
        critical_services = ["tts", "audio", "translation"]

        if service_name in critical_services:
            if status == "connected":
                color = "#16c60c"  # Green
            elif status == "error":
                color = "#d13438"  # Red
            else:
                color = "#ff8c00"  # Orange

            self.connection_status_label.setStyleSheet(f"color: {color}; font-size: 16px;")
    
    def show_about(self) -> None:
        """Shows the 'About' dialog."""
        about_text = """
        <h2>TalkBridge Desktop</h2>
        <p><b>Version:</b> 1.0.0</p>
        <p><b>Description:</b> Real-time voice translation platform with AI</p>
        <p><b>Features:</b></p>
        <ul>
            <li>Voice synthesis with Coqui TTS</li>
            <li>Multi-language translation</li>
            <li>Synchronized facial animation</li>
            <li>LLM integration (Ollama)</li>
            <li>Real-time audio processing</li>
        </ul>
        <p><b>Developed by:</b> TalkBridge Team</p>
        """

        QMessageBox.about(self, "About TalkBridge", about_text)
    
    def closeEvent(self, event) -> None:
        """Handles the window close event."""
        self.logger.info("Closing main window...")

        # Save window size
        if self.state_manager:
            self.state_manager.set_config("ui.window_size.width", self.width())
            self.state_manager.set_config("ui.window_size.height", self.height())

        # Emit close signal
        self.window_closing.emit()

        # Accept close event
        event.accept()

        self.logger.info("Main window closed")
