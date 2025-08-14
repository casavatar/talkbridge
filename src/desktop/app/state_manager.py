"""
TalkBridge Desktop - State Manager
=================================

Centralized state manager for the desktop application.
Handles configuration, user preferences, service status,
and data persistence.

Author: TalkBridge Team
Date: 2025
"""

import os
import json
import yaml
import logging
from pathlib import Path
from typing import Any, Dict, Optional, List
from dataclasses import dataclass, asdict
from datetime import datetime

from PyQt6.QtCore import QObject, pyqtSignal, QSettings


@dataclass
class ServiceStatus:
    """Status of an individual service."""
    name: str
    status: str  # "connected", "disconnected", "error", "initializing"
    last_update: str
    error_message: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None


@dataclass
class UserSession:
    """User session information."""
    username: str
    login_time: str
    is_authenticated: bool
    remember_credentials: bool
    last_activity: str


@dataclass
class ApplicationState:
    """Global application state."""
    user_session: Optional[UserSession] = None
    services: Dict[str, ServiceStatus] = None
    ui_preferences: Dict[str, Any] = None
    last_save_time: Optional[str] = None

    def __post_init__(self):
        if self.services is None:
            self.services = {}
        if self.ui_preferences is None:
            self.ui_preferences = {}


class StateManager(QObject):
    """
    Centralized state manager for TalkBridge Desktop.

    Main functions:
    - Configuration management from config.yaml
    - Service status and monitoring
    - User and UI preferences
    - User session and authentication
    - Automatic data persistence
    """

    # Signals to notify state changes
    state_changed = pyqtSignal(str, object)  # key, value
    service_status_changed = pyqtSignal(str, str)  # service_name, status
    user_session_changed = pyqtSignal(object)  # UserSession
    configuration_loaded = pyqtSignal()
    error_occurred = pyqtSignal(str, str)  # error_type, message

    def __init__(self, parent=None):
        super().__init__(parent)

        self.logger = logging.getLogger("talkbridge.desktop.state")

        # Important paths
        self.project_root = Path(__file__).parent.parent.parent.parent
        self.config_dir = self.project_root / "config"
        self.data_dir = self.project_root / "data"
        self.state_file = self.data_dir / "app_state.json"

        # Configurations
        self.config: Dict[str, Any] = {}
        self.app_state = ApplicationState()
        self.qt_settings = QSettings()

        # Internal state
        self.is_initialized = False
        self.auto_save_enabled = True

        self.logger.info("StateManager created")

    def initialize(self) -> bool:
        """
        Initializes the StateManager by loading configuration and state.

        Returns:
            bool: True if initialization was successful
        """
        try:
            self.logger.info("Initializing StateManager...")

            # Create necessary directories
            self.data_dir.mkdir(parents=True, exist_ok=True)

            # Load main configuration
            if not self._load_main_config():
                self.logger.error("Failed to load main configuration")
                return False

            # Load application state
            self._load_app_state()

            # Initialize default services
            self._initialize_default_services()

            self.is_initialized = True
            self.configuration_loaded.emit()

            self.logger.info("StateManager initialized successfully")
            return True

        except Exception as e:
            self.logger.error(f"Error initializing StateManager: {e}", exc_info=True)
            return False

    def _load_main_config(self) -> bool:
        """
        Loads the main configuration from config.yaml.

        Returns:
            bool: True if loading was successful
        """
        try:
            config_file = self.config_dir / "config.yaml"

            if config_file.exists():
                with open(config_file, 'r', encoding='utf-8') as f:
                    self.config = yaml.safe_load(f) or {}
                self.logger.info(f"Configuration loaded from {config_file}")
            else:
                self.logger.warning(f"Configuration file not found: {config_file}")
                self.config = self._get_default_config()

            return True

        except Exception as e:
            self.logger.error(f"Error loading configuration: {e}")
            self.config = self._get_default_config()
            return False

    def _get_default_config(self) -> Dict[str, Any]:
        """Returns default configuration."""
        return {
            "app": {
                "name": "TalkBridge Desktop",
                "version": "1.0.0",
                "debug": False
            },
            "ui": {
                "theme": "dark",
                "window_size": {"width": 1200, "height": 800},
                "auto_save_state": True
            },
            "services": {
                "tts": {"enabled": True},
                "audio": {"enabled": True},
                "translation": {"enabled": True},
                "ollama": {"enabled": True},
                "animation": {"enabled": True}
            }
        }

    def _load_app_state(self) -> None:
        """Loads the application state from file."""
        try:
            if self.state_file.exists():
                with open(self.state_file, 'r', encoding='utf-8') as f:
                    state_data = json.load(f)

                # Rebuild state from JSON
                self.app_state = self._deserialize_state(state_data)
                self.logger.info("Application state loaded")
            else:
                self.logger.info("No previous state file exists")

        except Exception as e:
            self.logger.warning(f"Error loading application state: {e}")
            # Continue with default state

    def _initialize_default_services(self) -> None:
        """Initializes default service states."""
        service_names = ["tts", "audio", "translation", "ollama", "animation", "camera"]

        for service_name in service_names:
            if service_name not in self.app_state.services:
                self.app_state.services[service_name] = ServiceStatus(
                    name=service_name,
                    status="disconnected",
                    last_update=datetime.now().isoformat(),
                    error_message=None,
                    metadata={}
                )

    def get_config(self, key: str, default: Any = None) -> Any:
        """
        Gets a configuration value using dot notation.

        Args:
            key: Key in "section.subsection.key" format
            default: Default value if not found

        Returns:
            Any: Configuration value or default
        """
        try:
            keys = key.split('.')
            value = self.config

            for k in keys:
                if isinstance(value, dict) and k in value:
                    value = value[k]
                else:
                    return default

            return value

        except Exception as e:
            self.logger.warning(f"Error getting config '{key}': {e}")
            return default

    def set_config(self, key: str, value: Any) -> None:
        """
        Sets a configuration value using dot notation.

        Args:
            key: Key in "section.subsection.key" format
            value: Value to set
        """
        try:
            keys = key.split('.')
            config = self.config

            # Navigate to the second-to-last level
            for k in keys[:-1]:
                if k not in config:
                    config[k] = {}
                config = config[k]

            # Set the value
            config[keys[-1]] = value

            self.state_changed.emit(key, value)

            if self.auto_save_enabled:
                self._save_config()

        except Exception as e:
            self.logger.error(f"Error setting config '{key}': {e}")

    def get_setting(self, key: str, default: Any = None) -> Any:
        """
        Gets a user preference from QSettings.

        Args:
            key: Preference key
            default: Default value

        Returns:
            Any: Preference value
        """
        return self.qt_settings.value(key, default)

    def set_setting(self, key: str, value: Any) -> None:
        """
        Sets a user preference in QSettings.

        Args:
            key: Preference key
            value: Value to set
        """
        self.qt_settings.setValue(key, value)
        self.qt_settings.sync()

    def get_service_status(self, service_name: str) -> Optional[ServiceStatus]:
        """
        Gets the status of a specific service.

        Args:
            service_name: Service name

        Returns:
            ServiceStatus: Service status or None if not found
        """
        return self.app_state.services.get(service_name)

    def set_service_status(self, service_name: str, status: str,
                          error_message: Optional[str] = None,
                          metadata: Optional[Dict[str, Any]] = None) -> None:
        """
        Updates the status of a service.

        Args:
            service_name: Service name
            status: New status ("connected", "disconnected", "error", "initializing")
            error_message: Error message if applicable
            metadata: Additional metadata
        """
        try:
            service_status = ServiceStatus(
                name=service_name,
                status=status,
                last_update=datetime.now().isoformat(),
                error_message=error_message,
                metadata=metadata or {}
            )

            self.app_state.services[service_name] = service_status

            # Emit signals
            self.service_status_changed.emit(service_name, status)
            self.state_changed.emit(f"service.{service_name}.status", status)

            if self.auto_save_enabled:
                self.save_state()

            self.logger.debug(f"Service '{service_name}' status updated to '{status}'")

        except Exception as e:
            self.logger.error(f"Error updating service status '{service_name}': {e}")

    def get_all_service_statuses(self) -> Dict[str, ServiceStatus]:
        """Returns the status of all services."""
        return self.app_state.services.copy()

    def set_user_session(self, username: str, is_authenticated: bool = True,
                        remember_credentials: bool = False) -> None:
        """
        Sets the current user session.

        Args:
            username: Username
            is_authenticated: If authenticated
            remember_credentials: If credentials should be remembered
        """
        try:
            self.app_state.user_session = UserSession(
                username=username,
                login_time=datetime.now().isoformat(),
                is_authenticated=is_authenticated,
                remember_credentials=remember_credentials,
                last_activity=datetime.now().isoformat()
            )

            self.user_session_changed.emit(self.app_state.user_session)

            if self.auto_save_enabled:
                self.save_state()

            self.logger.info(f"User session set: {username}")

        except Exception as e:
            self.logger.error(f"Error setting user session: {e}")

    def get_user_session(self) -> Optional[UserSession]:
        """Returns the current user session."""
        return self.app_state.user_session

    def clear_user_session(self) -> None:
        """Clears the current user session."""
        self.app_state.user_session = None
        self.user_session_changed.emit(None)

        if self.auto_save_enabled:
            self.save_state()

        self.logger.info("User session cleared")

    def update_last_activity(self) -> None:
        """Updates the user's last activity timestamp."""
        if self.app_state.user_session:
            self.app_state.user_session.last_activity = datetime.now().isoformat()

    def save_state(self) -> bool:
        """
        Saves the current application state.

        Returns:
            bool: True if saved successfully
        """
        try:
            self.app_state.last_save_time = datetime.now().isoformat()

            # Serialize state
            state_data = self._serialize_state(self.app_state)

            # Save to file
            with open(self.state_file, 'w', encoding='utf-8') as f:
                json.dump(state_data, f, indent=2, ensure_ascii=False)

            self.logger.debug("Application state saved")
            return True

        except Exception as e:
            self.logger.error(f"Error saving state: {e}")
            return False

    def _save_config(self) -> bool:
        """Saves the main configuration."""
        try:
            config_file = self.config_dir / "config.yaml"
            with open(config_file, 'w', encoding='utf-8') as f:
                yaml.dump(self.config, f, default_flow_style=False,
                         allow_unicode=True)

            return True

        except Exception as e:
            self.logger.error(f"Error saving configuration: {e}")
            return False

    def _serialize_state(self, state: ApplicationState) -> Dict[str, Any]:
        """Serializes the application state to a dictionary."""
        return {
            "user_session": asdict(state.user_session) if state.user_session else None,
            "services": {name: asdict(status) for name, status in state.services.items()},
            "ui_preferences": state.ui_preferences,
            "last_save_time": state.last_save_time
        }

    def _deserialize_state(self, data: Dict[str, Any]) -> ApplicationState:
        """Deserializes a dictionary to ApplicationState."""
        state = ApplicationState()

        # User session
        if data.get("user_session"):
            state.user_session = UserSession(**data["user_session"])

        # Services
        services_data = data.get("services", {})
        state.services = {}
        for name, status_data in services_data.items():
            state.services[name] = ServiceStatus(**status_data)

        # UI preferences
        state.ui_preferences = data.get("ui_preferences", {})
        state.last_save_time = data.get("last_save_time")

        return state

    def reset_to_defaults(self) -> None:
        """Resets the state to default values."""
        self.logger.info("Resetting state to default values")

        self.config = self._get_default_config()
        self.app_state = ApplicationState()
        self._initialize_default_services()

        if self.auto_save_enabled:
            self.save_state()
            self._save_config()

    def cleanup(self) -> None:
        """Cleans up resources before closing."""
        try:
            self.logger.info("Cleaning up StateManager...")

            if self.auto_save_enabled and self.is_initialized:
                self.save_state()

            self.qt_settings.sync()

        except Exception as e:
            self.logger.error(f"Error during cleanup: {e}")

    def __del__(self):
        """StateManager destructor."""
        self.cleanup()