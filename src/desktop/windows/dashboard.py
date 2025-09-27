#!/src/desktop/windows/dashboard.py
"""
TalkBridge Desktop - Dashboard
==============================

Dashboard module for TalkBridge

Author: TalkBridge Team
Date: 2025-08-19
Version: 1.0

Requirements:
- PyQt6
======================================================================
Functions:
- __init__: Initialization function
- setup_ui: Configures the card interface.
- apply_styles: Applies CSS styles to the card.
- update_status: Updates the card status.
- _update_status_indicator: Updates the color of the status indicator.
- _get_status_text: Converts the status to readable text.
- _update_action_button: Updates the text and state of the action button.
- _update_details: Updates the details information.
- __init__: Initialization function
- __init__: Initialization function
======================================================================
"""

import logging
from typing import Dict, Optional, Any
from datetime import datetime

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QGridLayout,
    QLabel, QPushButton, QFrame, QScrollArea,
    QProgressBar, QGroupBox, QSizePolicy
)
from PySide6.QtCore import (
    Signal, QTimer, Qt, QSize
)
from PySide6.QtGui import QFont, QIcon, QPalette

class ServiceCard(QWidget):
    """
    Card that shows the status and controls of an individual service.

    Features:
    - Visual status indicator (color)
    - Service title and description
    - Main action button
    - Detailed status information
    """

    action_triggered = Signal(str)  # service_name

    def __init__(self, service_name: str, title: str, description: str,
                 icon_name: Optional[str] = None, parent=None):
        super().__init__(parent)

        self.service_name = service_name
        self.title = title
        self.description = description
        self.icon_name = icon_name

        # Internal state
        self.current_status = "disconnected"
        self.error_message = ""
        self.last_update = None

        # UI components
        self.status_indicator: Optional[QLabel] = None
        self.title_label: Optional[QLabel] = None
        self.description_label: Optional[QLabel] = None
        self.status_label: Optional[QLabel] = None
        self.action_button: Optional[QPushButton] = None
        self.details_label: Optional[QLabel] = None

        self.setup_ui()
        self.update_status("disconnected")

    def setup_ui(self) -> None:
        """Configures the card interface."""
        self.setFixedSize(280, 200)
        self.setObjectName("serviceCard")

        # Main layout
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(15, 15, 15, 15)
        main_layout.setSpacing(10)

        # Header with status indicator and title
        header_layout = QHBoxLayout()
        header_layout.setSpacing(10)

        # Status indicator (colored circle)
        self.status_indicator = QLabel("●")
        self.status_indicator.setObjectName("statusIndicator")
        self.status_indicator.setFont(QFont("Arial", 16))
        self.status_indicator.setFixedSize(20, 20)
        header_layout.addWidget(self.status_indicator)

        # Service title
        self.title_label = QLabel(self.title)
        self.title_label.setObjectName("cardTitle")
        title_font = QFont()
        title_font.setPointSize(14)
        title_font.setBold(True)
        self.title_label.setFont(title_font)
        header_layout.addWidget(self.title_label)

        header_layout.addStretch()
        main_layout.addLayout(header_layout)

        # Description
        self.description_label = QLabel(self.description)
        self.description_label.setObjectName("cardDescription")
        self.description_label.setWordWrap(True)
        self.description_label.setFont(QFont("Arial", 9))
        main_layout.addWidget(self.description_label)

        # Current status
        self.status_label = QLabel("Disconnected")
        self.status_label.setObjectName("cardStatus")
        self.status_label.setFont(QFont("Arial", 8))
        main_layout.addWidget(self.status_label)

        # Additional details (error, last update, etc.)
        self.details_label = QLabel("")
        self.details_label.setObjectName("cardDetails")
        self.details_label.setWordWrap(True)
        self.details_label.setFont(QFont("Arial", 7))
        self.details_label.setMaximumHeight(30)
        main_layout.addWidget(self.details_label)

        main_layout.addStretch()

        # Action button
        self.action_button = QPushButton("Connect")
        self.action_button.setObjectName("cardActionButton")
        self.action_button.setMinimumHeight(35)
        self.action_button.clicked.connect(
            lambda: self.action_triggered.emit(self.service_name)
        )
        main_layout.addWidget(self.action_button)

        # Apply styles
        self.apply_styles()

    def apply_styles(self) -> None:
        """Applies CSS styles to the card."""
        style = """
        QWidget#serviceCard {
            background-color: #3c3c3c;
            border-radius: 10px;
            border: 1px solid #555555;
        }

        QWidget#serviceCard:hover {
            border-color: #0078d4;
            background-color: #404040;
        }

        QLabel#cardTitle {
            color: #ffffff;
        }

        QLabel#cardDescription {
            color: #cccccc;
        }

        QLabel#cardStatus {
            color: #cccccc;
            font-weight: bold;
        }

        QLabel#cardDetails {
            color: #888888;
        }

        QPushButton#cardActionButton {
            background-color: #0078d4;
            color: #ffffff;
            border: none;
            border-radius: 5px;
            padding: 8px;
            font-weight: bold;
        }

        QPushButton#cardActionButton:hover {
            background-color: #106ebe;
        }

        QPushButton#cardActionButton:disabled {
            background-color: #555555;
            color: #888888;
        }
        """
        self.setStyleSheet(style)

    def update_status(self, status: str, error_message: str = "",
                     metadata: Optional[Dict[str, Any]] = None) -> None:
        """
        Updates the card status.

        Args:
            status: New service status
            error_message: Error message if applicable
            metadata: Additional metadata
        """
        self.current_status = status
        self.error_message = error_message
        self.last_update = datetime.now()

        # Update visual indicator
        self._update_status_indicator(status)

        # Update status text
        status_text = self._get_status_text(status)
        if self.status_label:
            self.status_label.setText(status_text)

        # Update action button
        self._update_action_button(status)

        # Update details
        self._update_details(error_message, metadata)

    def _update_status_indicator(self, status: str) -> None:
        """Updates the color of the status indicator."""
        color_map = {
            "connected": "#16c60c",      # Green
            "initializing": "#ff8c00",   # Orange
            "processing": "#0078d4",     # Blue
            "error": "#d13438",          # Red
            "disconnected": "#888888"    # Gray
        }

        color = color_map.get(status, "#888888")
        if self.status_indicator:
            self.status_indicator.setStyleSheet(f"color: {color};")

    def _get_status_text(self, status: str) -> str:
        """Converts the status to readable text."""
        status_map = {
            "connected": "Connected",
            "initializing": "Initializing...",
            "processing": "Processing...",
            "error": "Error",
            "disconnected": "Disconnected",
            "idle": "Idle"
        }
        return status_map.get(status, "Unknown status")

    def _update_action_button(self, status: str) -> None:
        """Updates the text and state of the action button."""
        if not self.action_button:
            return
            
        if status == "connected":
            self.action_button.setText("Configure")
            self.action_button.setEnabled(True)
        elif status == "error":
            self.action_button.setText("Retry")
            self.action_button.setEnabled(True)
        elif status in ["initializing", "processing"]:
            self.action_button.setText("Processing...")
            self.action_button.setEnabled(False)
        else:  # disconnected
            self.action_button.setText("Connect")
            self.action_button.setEnabled(True)

    def _update_details(self, error_message: str, metadata: Optional[Dict[str, Any]] = None) -> None:
        """Updates the details information."""
        if not self.details_label:
            return
            
        details_parts = []
        metadata = metadata or {}

        if error_message:
            details_parts.append(f"Error: {error_message[:50]}...")

        if self.last_update:
            time_str = self.last_update.strftime("%H:%M:%S")
            details_parts.append(f"Updated: {time_str}")

        if metadata:
            # Add relevant metadata
            if "version" in metadata:
                details_parts.append(f"v{metadata['version']}")

        self.details_label.setText(" | ".join(details_parts))

class QuickActionButton(QPushButton):
    """Styled quick action button."""

    def __init__(self, title: str, icon_name: Optional[str] = None, parent=None):
        super().__init__(title, parent)

        self.setMinimumSize(120, 60)
        self.setMaximumSize(160, 80)

        # Apply styles
        style = """
        QPushButton {
            background-color: #0078d4;
            color: #ffffff;
            border: none;
            border-radius: 8px;
            font-size: 12px;
            font-weight: bold;
            padding: 10px;
        }

        QPushButton:hover {
            background-color: #106ebe;
        }

        QPushButton:pressed {
            background-color: #005a9e;
        }
        """
        self.setStyleSheet(style)

class Dashboard(QWidget):
    """
    Main dashboard of TalkBridge Desktop.

    Shows:
    - Status of all services in cards
    - Main quick actions
    - User session information
    - Basic statistics
    """

    # Signals
    service_action_requested = Signal(str)  # service_name
    quick_action_requested = Signal(str)  # action_name

    def __init__(self, state_manager=None, core_bridge=None, parent=None):
        super().__init__(parent)

        self.state_manager = state_manager
        self.core_bridge = core_bridge
        self.logger = logging.getLogger("talkbridge.desktop.dashboard")

        # UI components
        self.service_cards: Dict[str, ServiceCard] = {}
        self.user_info_label: Optional[QLabel] = None
        self.stats_label: Optional[QLabel] = None

        # Timer for periodic updates
        self.update_timer = QTimer()
        self.update_timer.timeout.connect(self.update_dashboard)

        self.setup_ui()
        self.connect_signals()

        # Start periodic updates (every 5 seconds)
        self.update_timer.start(5000)

        self.logger.info("Dashboard initialized")

    def setup_ui(self) -> None:
        """Configures the dashboard interface."""
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(20, 20, 20, 20)
        main_layout.setSpacing(20)

        # Header with user information
        self.create_header(main_layout)

        # Quick actions area
        self.create_quick_actions(main_layout)

        # Services cards grid
        self.create_services_grid(main_layout)

        # Footer with statistics
        self.create_footer(main_layout)

        # Apply global styles
        self.apply_global_styles()

    def create_header(self, parent_layout: QVBoxLayout) -> None:
        """Creates the header section with user information."""
        header_frame = QFrame()
        header_frame.setObjectName("headerFrame")
        header_layout = QHBoxLayout(header_frame)
        header_layout.setContentsMargins(15, 15, 15, 15)

        # User information
        user_info_layout = QVBoxLayout()

        welcome_label = QLabel("Welcome to TalkBridge")
        welcome_label.setObjectName("welcomeLabel")
        welcome_font = QFont()
        welcome_font.setPointSize(18)
        welcome_font.setBold(True)
        welcome_label.setFont(welcome_font)
        user_info_layout.addWidget(welcome_label)

        self.user_info_label = QLabel("Loading user information...")
        self.user_info_label.setObjectName("userInfoLabel")
        user_info_layout.addWidget(self.user_info_label)

        header_layout.addLayout(user_info_layout)
        header_layout.addStretch()

        parent_layout.addWidget(header_frame)

    def create_quick_actions(self, parent_layout: QVBoxLayout) -> None:
        """Creates the quick actions section."""
        actions_group = QGroupBox("Quick Actions")
        actions_group.setObjectName("quickActionsGroup")
        actions_layout = QHBoxLayout(actions_group)
        actions_layout.setSpacing(15)

        # Quick action buttons
        quick_actions = [
            ("New Chat", "chat"),
            ("Settings", "settings"),
            ("Avatar", "avatar"),
            ("Statistics", "stats")
        ]

        for title, action in quick_actions:
            button = QuickActionButton(title)
            button.clicked.connect(
                lambda checked, a=action: self.quick_action_requested.emit(a)
            )
            actions_layout.addWidget(button)

        actions_layout.addStretch()
        parent_layout.addWidget(actions_group)

    def create_services_grid(self, parent_layout: QVBoxLayout) -> None:
        """Creates the services cards grid."""
        services_group = QGroupBox("Service Status")
        services_group.setObjectName("servicesGroup")
        services_layout = QVBoxLayout(services_group)

        # Scroll area for cards
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)

        # Container widget for the grid
        grid_widget = QWidget()
        grid_layout = QGridLayout(grid_widget)
        grid_layout.setSpacing(15)

        # Define services and their cards
        services_info = [
            ("tts", "Text-to-Speech", "AI voice synthesis", "🎤"),
            ("audio", "Audio", "Audio capture and processing", "🎵"),
            ("translation", "Translation", "Multi-language translation engine", "🌐"),
            ("camera", "Camera", "Video capture and face detection", "📹"),
            ("avatar", "Avatar", "Synchronized facial animation", "👤"),
            ("ollama", "Ollama LLM", "Natural language processing", "🤖")
        ]

        # Create cards in a 3-column grid
        for i, (service_name, title, description, icon) in enumerate(services_info):
            row = i // 3
            col = i % 3

            card = ServiceCard(service_name, title, description, icon)
            card.action_triggered.connect(self.service_action_requested)

            self.service_cards[service_name] = card
            grid_layout.addWidget(card, row, col)

        # Ensure columns are evenly distributed
        for col in range(3):
            grid_layout.setColumnStretch(col, 1)

        scroll_area.setWidget(grid_widget)
        services_layout.addWidget(scroll_area)

        parent_layout.addWidget(services_group)

    def create_footer(self, parent_layout: QVBoxLayout) -> None:
        """Creates the footer with statistics."""
        footer_frame = QFrame()
        footer_frame.setObjectName("footerFrame")
        footer_layout = QHBoxLayout(footer_frame)
        footer_layout.setContentsMargins(15, 10, 15, 10)

        self.stats_label = QLabel("Statistics: Loading...")
        self.stats_label.setObjectName("statsLabel")
        footer_layout.addWidget(self.stats_label)

        footer_layout.addStretch()

        # Last update timestamp
        self.last_update_label = QLabel("")
        self.last_update_label.setObjectName("lastUpdateLabel")
        footer_layout.addWidget(self.last_update_label)

        parent_layout.addWidget(footer_frame)

    def apply_global_styles(self) -> None:
        """Applies global styles to the dashboard."""
        style = """
        QWidget {
            background-color: #2b2b2b;
            color: #ffffff;
        }

        QFrame#headerFrame {
            background-color: #3c3c3c;
            border-radius: 10px;
            border: 1px solid #555555;
        }

        QFrame#footerFrame {
            background-color: #3c3c3c;
            border-radius: 5px;
        }

        QLabel#welcomeLabel {
            color: #ffffff;
        }

        QLabel#userInfoLabel {
            color: #cccccc;
        }

        QLabel#statsLabel {
            color: #cccccc;
        }

        QLabel#lastUpdateLabel {
            color: #888888;
            font-size: 10px;
        }

        QGroupBox {
            font-size: 14px;
            font-weight: bold;
            color: #ffffff;
            border: 2px solid #555555;
            border-radius: 8px;
            margin: 10px 0px;
            padding-top: 20px;
        }

        QGroupBox::title {
            subcontrol-origin: margin;
            left: 10px;
            padding: 0 5px 0 5px;
            color: #ffffff;
        }

        QScrollArea {
            border: none;
            background-color: transparent;
        }
        """
        self.setStyleSheet(style)

    def connect_signals(self) -> None:
        """Connects signals from StateManager and CoreBridge."""
        if self.state_manager:
            # Connect to service status changes
            self.state_manager.service_status_changed.connect(
                self.on_service_status_changed
            )

            # Connect to user session changes
            self.state_manager.user_session_changed.connect(
                self.on_user_session_changed
            )

    def on_service_status_changed(self, service_name: str, status: str) -> None:
        """
        Handles changes in service status.

        Args:
            service_name: Service name
            status: New status
        """
        if service_name in self.service_cards and self.state_manager:
            # Get additional status information
            service_status = self.state_manager.get_service_status(service_name)

            error_message = ""
            metadata = {}

            if service_status:
                error_message = service_status.error_message or ""
                metadata = service_status.metadata or {}

            # Update card
            self.service_cards[service_name].update_status(
                status, error_message, metadata
            )

    def on_user_session_changed(self, user_session) -> None:
        """
        Handles changes in user session.

        Args:
            user_session: New user session or None
        """
        if user_session and user_session.is_authenticated:
            user_text = f"User: {user_session.username}"
            if hasattr(user_session, 'login_time'):
                login_time = datetime.fromisoformat(user_session.login_time)
                time_str = login_time.strftime("%H:%M")
                user_text += f" | Session started: {time_str}"
        else:
            user_text = "No active session"

        if self.user_info_label:
            self.user_info_label.setText(user_text)

    def update_dashboard(self) -> None:
        """Periodically updates dashboard information."""
        try:
            # Update statistics
            self.update_statistics()

            # Update timestamp
            current_time = datetime.now().strftime("%H:%M:%S")
            self.last_update_label.setText(f"Last update: {current_time}")

            # Update user activity
            if self.state_manager:
                self.state_manager.update_last_activity()

        except Exception as e:
            self.logger.warning(f"Error updating dashboard: {e}")

    def update_statistics(self) -> None:
        """Updates the displayed statistics."""
        try:
            if not self.state_manager:
                return

            # Count services by status
            all_statuses = self.state_manager.get_all_service_statuses()

            connected = sum(1 for s in all_statuses.values() if s.status == "connected")
            total = len(all_statuses)
            errors = sum(1 for s in all_statuses.values() if s.status == "error")

            stats_text = f"Services: {connected}/{total} connected"
            if errors > 0:
                stats_text += f" | {errors} with errors"

            if self.stats_label:
                self.stats_label.setText(stats_text)

        except Exception as e:
            self.logger.warning(f"Error updating statistics: {e}")
            if self.stats_label:
                self.stats_label.setText("Error loading statistics")

    def refresh_all_services(self) -> None:
        """Updates the status of all services."""
        if not self.state_manager:
            return

        all_statuses = self.state_manager.get_all_service_statuses()

        for service_name, service_status in all_statuses.items():
            if service_name in self.service_cards:
                self.service_cards[service_name].update_status(
                    service_status.status,
                    service_status.error_message or "",
                    service_status.metadata or {}
                )

    def showEvent(self, event) -> None:
        """Handles the widget show event."""
        super().showEvent(event)

        # Refresh information when dashboard is shown
        self.refresh_all_services()
        self.update_dashboard()

    def closeEvent(self, event) -> None:
        """Handles the widget close event."""
        # Stop update timer
        if self.update_timer.isActive():
            self.update_timer.stop()

        super().closeEvent(event)
