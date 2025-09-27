#!/usr/bin/env python3
"""
TalkBridge Desktop - Device Panel Component
===========================================

Component for device selection, status display, and audio configuration.
Handles microphone/system audio device lists, status indicators, and settings.

Author: TalkBridge Team
Date: 2025-09-18
Version: 1.0
"""

# Standard library imports
import logging
import sys
from pathlib import Path
from typing import List, Dict, Any, Optional, Callable, Union

# Third-party imports
import customtkinter as ctk

# Local imports - Core utilities
from ...logging_config import get_logger, log_exception

# Local imports - Event system
from ..ui.events import EventBus, EventHandler, DeviceEvent, AudioStateEvent

# Local imports - Theme system
from ..ui.theme import (
    ColorPalette, 
    Typography, 
    Dimensions, 
    Spacing, 
    ComponentThemes
)

class DeviceStatusIndicator:
    """Visual indicator for device status (active/inactive).
    
    A composite widget that shows a status dot and label indicating
    whether an audio device is currently active or inactive.
    """
    
    def __init__(self, parent: ctk.CTkFrame, label: str) -> None:
        """Initialize the device status indicator.
        
        Args:
            parent: The parent frame to contain this indicator
            label: The base label text for this device type
        """
        self.parent = parent
        self.label = label
        self.logger = get_logger(__name__)
        
        # UI components
        self.container: Optional[ctk.CTkFrame] = None
        self.status_dot: Optional[ctk.CTkLabel] = None
        self.label_widget: Optional[ctk.CTkLabel] = None
        
        try:
            self._create_ui()
        except Exception as e:
            self.logger.error(f"Error creating device status indicator: {e}")
            log_exception(self.logger, e, "DeviceStatusIndicator creation failed")
    
    def _create_ui(self) -> None:
        """Create the UI components for the status indicator."""
        # Create indicator container
        self.container = ctk.CTkFrame(self.parent, fg_color="transparent")
        self.container.pack(side="left", padx=5)
        
        # Status dot
        self.status_dot = ctk.CTkLabel(
            self.container,
            text="●",
            font=ctk.CTkFont(size=14),
            text_color="#666666"  # Default inactive
        )
        self.status_dot.pack(side="left")
        
        # Label with theme support
        label_font = (
            (Typography.FONT_FAMILY_PRIMARY, Typography.FONT_SIZE_CAPTION)
            if hasattr(Typography, 'FONT_FAMILY_PRIMARY')
            else ctk.CTkFont(size=12)
        )
        
        self.label_widget = ctk.CTkLabel(
            self.container,
            text=self.label,
            font=label_font,
            text_color="#cccccc"
        )
        self.label_widget.pack(side="left", padx=(5, 0))
    
    def set_active(self, active: bool, device_name: Optional[str] = None) -> None:
        """Set the active status and optionally update device name.
        
        Args:
            active: Whether the device is currently active
            device_name: Optional name of the active device
        """
        try:
            if self.status_dot is None or self.label_widget is None:
                self.logger.warning("Status indicator components not initialized")
                return
            
            if active:
                self.status_dot.configure(text_color="#00ff88")  # Green for active
                display_text = (
                    f"{self.label}: {device_name}" if device_name 
                    else f"{self.label}: Active"
                )
            else:
                self.status_dot.configure(text_color="#666666")  # Gray for inactive
                display_text = f"{self.label}: Off"
            
            self.label_widget.configure(text=display_text)
            
        except Exception as e:
            self.logger.error(f"Error setting device status: {e}")
            log_exception(self.logger, e, "Device status update failed")
    
    def cleanup(self) -> None:
        """Clean up resources."""
        try:
            if self.container is not None:
                self.container.destroy()
        except Exception as e:
            self.logger.error(f"Error cleaning up status indicator: {e}")

class DevicePanel(EventHandler):
    """
    Device panel component for audio device management and configuration.
    
    This component provides a comprehensive interface for managing audio devices
    and related settings in the TalkBridge application. It handles device selection,
    status monitoring, and language configuration with proper error handling and
    user feedback.
    
    Features:
    - Input device selection (microphone) with dropdown list
    - System audio device selection (loopback) with dropdown list  
    - Real-time device status indicators with visual feedback
    - Target language selection for translation services
    - Device refresh functionality with user feedback
    - Event-driven architecture for loose coupling
    - Comprehensive error handling and logging
    
    Attributes:
        input_devices: List of available input (microphone) devices
        loopback_devices: List of available system audio (loopback) devices
        selected_mic_device: Currently selected microphone device name
        selected_sys_device: Currently selected system audio device name
        current_target_language: Currently selected translation target language
        available_languages: Dictionary of supported languages (code -> name)
    
    Events Emitted:
        - Device selection changes via callbacks
        - Status updates via event bus
        
    Events Consumed:
        - device_change: Updates when devices are added/removed
        - audio_state_change: Updates device status indicators
    """
    
    def __init__(self, parent: ctk.CTkFrame, event_bus: EventBus,
                 on_mic_device_change: Optional[Callable[[str], None]] = None,
                 on_sys_device_change: Optional[Callable[[str], None]] = None,
                 on_target_language_change: Optional[Callable[[str], None]] = None) -> None:
        """Initialize device panel component.
        
        Args:
            parent: The parent frame to contain this panel
            event_bus: The event bus for inter-component communication
            on_mic_device_change: Callback for microphone device changes
            on_sys_device_change: Callback for system audio device changes
            on_target_language_change: Callback for language setting changes
        """
        super().__init__(event_bus)
        self.parent = parent
        self.logger = get_logger(__name__)
        
        # Callbacks
        self.on_mic_device_change = on_mic_device_change
        self.on_sys_device_change = on_sys_device_change
        self.on_target_language_change = on_target_language_change
        
        # Device data
        self.input_devices: List[Dict[str, Any]] = []
        self.loopback_devices: List[Dict[str, Any]] = []
        self.selected_mic_device: Optional[str] = None
        self.selected_sys_device: Optional[str] = None
        
        # Language settings
        self.current_target_language: str = "en"
        self.available_languages: Dict[str, str] = {
            "en": "English",
            "es": "Spanish", 
            "fr": "French",
            "de": "German",
            "it": "Italian",
            "pt": "Portuguese",
            "ru": "Russian",
            "ja": "Japanese",
            "ko": "Korean",
            "zh": "Chinese"
        }
        
        # UI components (initialized in setup_ui)
        self.main_frame: Optional[ctk.CTkFrame] = None
        self.mic_device_combo: Optional[ctk.CTkComboBox] = None
        self.sys_device_combo: Optional[ctk.CTkComboBox] = None
        self.target_language_combo: Optional[ctk.CTkComboBox] = None
        self.mic_status_indicator: Optional[DeviceStatusIndicator] = None
        self.sys_status_indicator: Optional[DeviceStatusIndicator] = None
        self.refresh_button: Optional[ctk.CTkButton] = None
        
        # Initialize component
        try:
            self._initialize_component()
            self.logger.info("Device panel initialized successfully")
        except Exception as e:
            self.logger.error(f"Error initializing device panel: {e}")
            log_exception(self.logger, e, "Device panel initialization failed")
    
    def _initialize_component(self) -> None:
        """Initialize the component with UI and events."""
        # Setup UI
        self.setup_ui()
        
        # Subscribe to events
        self.subscribe_to_events()
        
        # Validate initialization
        self._validate_initialization()
    
    def _validate_initialization(self) -> None:
        """Validate that component was properly initialized."""
        required_components = [
            ("main_frame", self.main_frame),
            ("mic_device_combo", self.mic_device_combo),
            ("sys_device_combo", self.sys_device_combo),
            ("target_language_combo", self.target_language_combo),
            ("refresh_button", self.refresh_button)
        ]
        
        missing_components = []
        for name, component in required_components:
            if component is None:
                missing_components.append(name)
        
        if missing_components:
            error_msg = f"Missing UI components: {', '.join(missing_components)}"
            self.logger.error(error_msg)
            raise RuntimeError(error_msg)
    
    def setup_ui(self) -> None:
        """Setup the device panel UI components and layout.
        
        Creates the complete user interface including:
        - Main container frame with proper styling
        - Title section with refresh button
        - Device selection dropdowns for microphone and system audio
        - Status indicators for real-time device monitoring
        - Language selection controls for translation settings
        
        The UI is organized in a vertical layout with clear sections
        for different types of controls and information.
        """
        try:
            # Main container with theme support
            corner_radius = getattr(Dimensions, 'RADIUS_MD', 8) if hasattr(Dimensions, 'RADIUS_MD') else 8
            
            self.main_frame = ctk.CTkFrame(
                self.parent, 
                fg_color="#2d2d2d",
                corner_radius=corner_radius
            )
            self.main_frame.pack(fill="x", padx=10, pady=5)
            
            # Create UI sections
            self._create_title_section()
            self._create_device_selection()
            self._create_status_indicators()
            self._create_language_settings()
            
            self.logger.debug("Device panel UI setup completed")
            
        except Exception as e:
            self.logger.error(f"Error setting up device panel UI: {e}")
            log_exception(self.logger, e, "Device panel UI setup failed")
            raise
    
    def _create_title_section(self) -> None:
        """Create the title section with refresh button."""
        title_frame = ctk.CTkFrame(self.main_frame, fg_color="transparent")
        title_frame.pack(fill="x", padx=15, pady=(15, 5))
        
        # Title with theme support
        title_font = (
            (Typography.FONT_FAMILY_PRIMARY, Typography.FONT_SIZE_BODY, Typography.FONT_WEIGHT_BOLD)
            if hasattr(Typography, 'FONT_FAMILY_PRIMARY')
            else ctk.CTkFont(size=14, weight="bold")
        )
        
        title_label = ctk.CTkLabel(
            title_frame,
            text="Audio Devices & Settings",
            font=title_font,
            text_color="#ffffff"
        )
        title_label.pack(side="left")
        
        # Refresh button with theme support
        refresh_font = (
            (Typography.FONT_FAMILY_PRIMARY, Typography.FONT_SIZE_CAPTION)
            if hasattr(Typography, 'FONT_FAMILY_PRIMARY')
            else ctk.CTkFont(size=12)
        )
        
        self.refresh_button = ctk.CTkButton(
            title_frame,
            text="🔄 Refresh",
            width=80,
            height=25,
            font=refresh_font,
            command=self._on_refresh_devices
        )
        self.refresh_button.pack(side="right")
    
    def _create_device_selection(self) -> None:
        """Create device selection controls.
        
        Creates dropdown menus for selecting audio input and output devices:
        - Microphone selection for voice input
        - System audio selection for capturing system sounds
        
        Both dropdowns are initially populated with placeholder text and
        will be updated when actual device lists are provided.
        """
        device_frame = ctk.CTkFrame(self.main_frame, fg_color="transparent")
        device_frame.pack(fill="x", padx=15, pady=5)
        
        # Create microphone selection controls
        self._create_mic_selection(device_frame)
        
        # Create system audio selection controls  
        self._create_sys_selection(device_frame)
    
    def _create_mic_selection(self, parent: ctk.CTkFrame) -> None:
        """Create microphone device selection controls."""
        mic_frame = ctk.CTkFrame(parent, fg_color="transparent")
        mic_frame.pack(fill="x", pady=2)
        
        # Label with theme support
        label_font = (
            (Typography.FONT_FAMILY_PRIMARY, Typography.FONT_SIZE_CAPTION)
            if hasattr(Typography, 'FONT_FAMILY_PRIMARY')
            else ctk.CTkFont(size=12)
        )
        
        mic_label = ctk.CTkLabel(
            mic_frame,
            text="Microphone:",
            font=label_font,
            text_color="#cccccc",
            width=100
        )
        mic_label.pack(side="left", padx=(0, 10))
        
        # Combo box with theme support
        combo_font = (
            (Typography.FONT_FAMILY_PRIMARY, Typography.FONT_SIZE_CAPTION)
            if hasattr(Typography, 'FONT_FAMILY_PRIMARY')
            else ctk.CTkFont(size=12)
        )
        
        self.mic_device_combo = ctk.CTkComboBox(
            mic_frame,
            values=["No devices available"],
            width=250,
            height=28,
            font=combo_font,
            command=self._on_mic_device_selected
        )
        self.mic_device_combo.pack(side="left", fill="x", expand=True)
    
    def _create_sys_selection(self, parent: ctk.CTkFrame) -> None:
        """Create system audio device selection controls."""
        sys_frame = ctk.CTkFrame(parent, fg_color="transparent")
        sys_frame.pack(fill="x", pady=2)
        
        # Label with theme support
        label_font = (
            (Typography.FONT_FAMILY_PRIMARY, Typography.FONT_SIZE_CAPTION)
            if hasattr(Typography, 'FONT_FAMILY_PRIMARY')
            else ctk.CTkFont(size=12)
        )
        
        sys_label = ctk.CTkLabel(
            sys_frame,
            text="System Audio:",
            font=label_font,
            text_color="#cccccc",
            width=100
        )
        sys_label.pack(side="left", padx=(0, 10))
        
        # Combo box with theme support
        combo_font = (
            (Typography.FONT_FAMILY_PRIMARY, Typography.FONT_SIZE_CAPTION)
            if hasattr(Typography, 'FONT_FAMILY_PRIMARY')
            else ctk.CTkFont(size=12)
        )
        
        self.sys_device_combo = ctk.CTkComboBox(
            sys_frame,
            values=["No devices available"],
            width=250,
            height=28,
            font=combo_font,
            command=self._on_sys_device_selected
        )
        self.sys_device_combo.pack(side="left", fill="x", expand=True)
    
    def _create_status_indicators(self) -> None:
        """Create device status indicators."""
        status_frame = ctk.CTkFrame(
            self.main_frame, 
            fg_color="#3c3c3c",
            corner_radius=6
        )
        status_frame.pack(fill="x", padx=15, pady=5)
        
        # Header
        status_header = ctk.CTkLabel(
            status_frame,
            text="Device Status",
            font=(Typography.FONT_FAMILY_PRIMARY, Typography.FONT_SIZE_CAPTION, Typography.FONT_WEIGHT_BOLD),
            text_color="#ffffff"
        )
        status_header.pack(pady=(10, 5))
        
        # Status indicators container
        indicators_frame = ctk.CTkFrame(status_frame, fg_color="transparent")
        indicators_frame.pack(fill="x", padx=10, pady=(0, 10))
        
        # Microphone status
        self.mic_status_indicator = DeviceStatusIndicator(indicators_frame, "Mic")
        
        # System audio status
        self.sys_status_indicator = DeviceStatusIndicator(indicators_frame, "System")
    
    def _create_language_settings(self) -> None:
        """Create language selection controls."""
        lang_frame = ctk.CTkFrame(self.main_frame, fg_color="transparent")
        lang_frame.pack(fill="x", padx=15, pady=(5, 15))
        
        # Target language selection
        target_frame = ctk.CTkFrame(lang_frame, fg_color="transparent")
        target_frame.pack(fill="x", pady=2)
        
        target_label = ctk.CTkLabel(
            target_frame,
            text="Translate to:",
            font=(Typography.FONT_FAMILY_PRIMARY, Typography.FONT_SIZE_CAPTION),
            text_color="#cccccc",
            width=100
        )
        target_label.pack(side="left", padx=(0, 10))
        
        language_values = [f"{code} - {name}" for code, name in self.available_languages.items()]
        
        self.target_language_combo = ctk.CTkComboBox(
            target_frame,
            values=language_values,
            width=200,
            height=28,
            font=(Typography.FONT_FAMILY_PRIMARY, Typography.FONT_SIZE_CAPTION),
            command=self._on_target_language_selected
        )
        self.target_language_combo.pack(side="left")
        self.target_language_combo.set("en - English")  # Default
    
    def subscribe_to_events(self) -> None:
        """Subscribe to relevant events."""
        self.event_bus.subscribe("device_change", self._on_device_change_event)
        self.event_bus.subscribe("audio_state_change", self._on_audio_state_change_event)
    
    def unsubscribe_from_events(self) -> None:
        """Unsubscribe from events."""
        self.event_bus.unsubscribe("device_change", self._on_device_change_event)
        self.event_bus.unsubscribe("audio_state_change", self._on_audio_state_change_event)
    
    def _on_device_change_event(self, event: DeviceEvent) -> None:
        """Handle device change events."""
        self.logger.debug(f"Device change: {event.device_type} - {event.device_name}")
        # Note: Device refresh will be triggered by explicit refresh requests
        # This event is mainly for logging and potential UI state updates
    
    def _on_audio_state_change_event(self, event: AudioStateEvent) -> None:
        """Handle audio state change events.
        
        Args:
            event: The audio state change event containing source and status info
        """
        try:
            self.logger.debug(f"Audio state change: {event.source} - {event.is_active}")
            
            if event.source == "mic" and self.mic_status_indicator is not None:
                self.mic_status_indicator.set_active(event.is_active, event.device_name)
            elif event.source == "system" and self.sys_status_indicator is not None:
                self.sys_status_indicator.set_active(event.is_active, event.device_name)
            else:
                if event.source == "mic" and self.mic_status_indicator is None:
                    self.logger.warning("Microphone status indicator not initialized")
                elif event.source == "system" and self.sys_status_indicator is None:
                    self.logger.warning("System status indicator not initialized")
        
        except Exception as e:
            self.logger.error(f"Error handling audio state change event: {e}")
            log_exception(self.logger, e, "Audio state change event handling failed")
    
    def _on_mic_device_selected(self, device_name: str) -> None:
        """Handle microphone device selection.
        
        Args:
            device_name: The name of the selected microphone device
        """
        try:
            if not device_name or device_name in ["No devices available", "No microphones available"]:
                self.logger.debug("Invalid or placeholder microphone device selected")
                return
            
            self.selected_mic_device = device_name
            self.logger.info(f"Selected microphone device: {device_name}")
            
            # Notify callback if available
            if self.on_mic_device_change is not None:
                self.on_mic_device_change(device_name)
            else:
                self.logger.debug("No microphone device change callback registered")
                
        except Exception as e:
            self.logger.error(f"Error handling microphone device selection: {e}")
            log_exception(self.logger, e, "Microphone device selection failed")
    
    def _on_sys_device_selected(self, device_name: str) -> None:
        """Handle system audio device selection.
        
        Args:
            device_name: The name of the selected system audio device
        """
        try:
            if not device_name or device_name in ["No devices available", "No system audio available"]:
                self.logger.debug("Invalid or placeholder system audio device selected")
                return
            
            self.selected_sys_device = device_name
            self.logger.info(f"Selected system audio device: {device_name}")
            
            # Notify callback if available
            if self.on_sys_device_change is not None:
                self.on_sys_device_change(device_name)
            else:
                self.logger.debug("No system device change callback registered")
                
        except Exception as e:
            self.logger.error(f"Error handling system audio device selection: {e}")
            log_exception(self.logger, e, "System audio device selection failed")
    
    def _on_target_language_selected(self, language_selection: str) -> None:
        """Handle target language selection.
        
        Args:
            language_selection: The selected language in "code - name" format
        """
        try:
            # Extract language code from "code - name" format
            if not language_selection or " - " not in language_selection:
                self.logger.warning(f"Invalid language selection format: {language_selection}")
                return
            
            language_code = language_selection.split(" - ")[0].strip()
            
            if language_code not in self.available_languages:
                self.logger.warning(f"Unknown language code selected: {language_code}")
                return
            
            self.current_target_language = language_code
            self.logger.info(f"Selected target language: {language_code}")
            
            # Notify callback if available
            if self.on_target_language_change is not None:
                self.on_target_language_change(language_code)
            else:
                self.logger.debug("No target language change callback registered")
                
        except Exception as e:
            self.logger.error(f"Error handling target language selection: {e}")
            log_exception(self.logger, e, "Target language selection failed")
    
    def _on_refresh_devices(self) -> None:
        """Handle device refresh request."""
        try:
            self.logger.info("Refreshing device lists")
            
            # Disable refresh button temporarily
            if self.refresh_button is not None:
                self.refresh_button.configure(state="disabled", text="Refreshing...")
                
                # Re-enable after a delay (will be updated by device refresh callback)
                self.refresh_button.after(2000, lambda: self._reset_refresh_button())
            else:
                self.logger.warning("Refresh button not initialized, cannot update state")
            
            # Note: Device refresh would be handled by external services
            # that provide new device lists via refresh_devices() method
            
        except Exception as e:
            self.logger.error(f"Error handling device refresh request: {e}")
            log_exception(self.logger, e, "Device refresh request failed")
            self._reset_refresh_button()
    
    def _reset_refresh_button(self) -> None:
        """Reset the refresh button to normal state."""
        try:
            if self.refresh_button is not None:
                self.refresh_button.configure(state="normal", text="🔄 Refresh")
        except Exception as e:
            self.logger.error(f"Error resetting refresh button: {e}")
    
    def refresh_devices(self, input_devices: List[Dict[str, Any]], 
                       loopback_devices: List[Dict[str, Any]]) -> None:
        """Refresh device lists with new data.
        
        Args:
            input_devices: List of available input (microphone) devices
            loopback_devices: List of available loopback (system audio) devices
        """
        try:
            self.logger.info(f"Updating device lists: {len(input_devices)} inputs, {len(loopback_devices)} loopbacks")
            
            # Store device data
            self.input_devices = input_devices or []
            self.loopback_devices = loopback_devices or []
            
            # Update microphone devices
            self._update_mic_device_list(input_devices)
            
            # Update system audio devices
            self._update_sys_device_list(loopback_devices)
            
            # Reset refresh button state
            self._reset_refresh_button()
            
        except Exception as e:
            self.logger.error(f"Error refreshing device lists: {e}")
            log_exception(self.logger, e, "Device list refresh failed")
    
    def _update_mic_device_list(self, input_devices: List[Dict[str, Any]]) -> None:
        """Update the microphone device dropdown list.
        
        Args:
            input_devices: List of available input devices
        """
        try:
            if self.mic_device_combo is None:
                self.logger.warning("Microphone device combo not initialized")
                return
            
            mic_names = []
            for device in input_devices:
                name = device.get("name", "Unknown Device")
                index = device.get("index", "")
                mic_names.append(f"{name} ({index})")
            
            if mic_names:
                self.mic_device_combo.configure(values=mic_names)
                if not self.selected_mic_device:
                    self.mic_device_combo.set(mic_names[0])
                    self.selected_mic_device = mic_names[0]
            else:
                self.mic_device_combo.configure(values=["No microphones available"])
                self.mic_device_combo.set("No microphones available")
                self.selected_mic_device = None
                
        except Exception as e:
            self.logger.error(f"Error updating microphone device list: {e}")
    
    def _update_sys_device_list(self, loopback_devices: List[Dict[str, Any]]) -> None:
        """Update the system audio device dropdown list.
        
        Args:
            loopback_devices: List of available loopback devices
        """
        try:
            if self.sys_device_combo is None:
                self.logger.warning("System device combo not initialized")
                return
            
            sys_names = []
            for device in loopback_devices:
                name = device.get("name", "Unknown Device")
                index = device.get("index", "")
                sys_names.append(f"{name} ({index})")
            
            if sys_names:
                self.sys_device_combo.configure(values=sys_names)
                if not self.selected_sys_device:
                    self.sys_device_combo.set(sys_names[0])
                    self.selected_sys_device = sys_names[0]
            else:
                self.sys_device_combo.configure(values=["No system audio available"])
                self.sys_device_combo.set("No system audio available")
                self.selected_sys_device = None
                
        except Exception as e:
            self.logger.error(f"Error updating system device list: {e}")
    
    def set_status(self, mic_active: bool, sys_active: bool, 
                   mic_device: Optional[str] = None, sys_device: Optional[str] = None) -> None:
        """Set device status indicators.
        
        Args:
            mic_active: Whether the microphone is currently active
            sys_active: Whether system audio capture is currently active
            mic_device: Optional name of the active microphone device
            sys_device: Optional name of the active system audio device
        """
        try:
            if self.mic_status_indicator is not None:
                self.mic_status_indicator.set_active(mic_active, mic_device)
            else:
                self.logger.warning("Microphone status indicator not available for status update")
            
            if self.sys_status_indicator is not None:
                self.sys_status_indicator.set_active(sys_active, sys_device)
            else:
                self.logger.warning("System status indicator not available for status update")
                
        except Exception as e:
            self.logger.error(f"Error setting device status: {e}")
            log_exception(self.logger, e, "Device status update failed")
    
    def get_selected_mic_device(self) -> Optional[str]:
        """Get the currently selected microphone device.
        
        Returns:
            The name of the currently selected microphone device,
            or None if no valid device is selected.
        """
        return self.selected_mic_device
    
    def get_selected_sys_device(self) -> Optional[str]:
        """Get the currently selected system audio device.
        
        Returns:
            The name of the currently selected system audio device,
            or None if no valid device is selected.
        """
        return self.selected_sys_device
    
    def get_target_language(self) -> str:
        """Get the currently selected target language for translation.
        
        Returns:
            The language code (e.g., 'en', 'es', 'fr') of the currently
            selected target language. Defaults to 'en' if not set.
        """
        return self.current_target_language
    
    def set_target_language(self, language_code: str) -> None:
        """Set the target language programmatically.
        
        Args:
            language_code: The language code to set (e.g., 'en', 'es', 'fr')
        """
        try:
            if language_code not in self.available_languages:
                self.logger.warning(f"Unknown language code: {language_code}")
                return
            
            self.current_target_language = language_code
            language_name = self.available_languages[language_code]
            
            if self.target_language_combo is not None:
                self.target_language_combo.set(f"{language_code} - {language_name}")
                self.logger.info(f"Target language set to: {language_code}")
            else:
                self.logger.warning("Target language combo not initialized, language stored but UI not updated")
                
        except Exception as e:
            self.logger.error(f"Error setting target language: {e}")
            log_exception(self.logger, e, "Language setting failed")
    
    def cleanup(self) -> None:
        """Clean up resources and prepare for component destruction.
        
        This method ensures proper cleanup of all resources used by the
        device panel component, including:
        - Event bus subscriptions
        - UI component references
        - Status indicator cleanup
        - Device list cleanup
        
        Should be called before the component is destroyed to prevent
        memory leaks and ensure graceful shutdown.
        """
        cleanup_errors = []
        
        try:
            self.logger.info("Starting device panel cleanup")
            
            # Unsubscribe from events
            try:
                self.unsubscribe_from_events()
            except Exception as e:
                cleanup_errors.append(f"Event unsubscription failed: {e}")
            
            # Cleanup status indicators
            try:
                if self.mic_status_indicator is not None:
                    self.mic_status_indicator.cleanup()
                if self.sys_status_indicator is not None:
                    self.sys_status_indicator.cleanup()
            except Exception as e:
                cleanup_errors.append(f"Status indicator cleanup failed: {e}")
            
            # Clear device lists and selections
            try:
                self.input_devices.clear()
                self.loopback_devices.clear()
                self.selected_mic_device = None
                self.selected_sys_device = None
            except Exception as e:
                cleanup_errors.append(f"Device data cleanup failed: {e}")
            
            # Clear UI component references
            self._clear_ui_references()
            
            # Report cleanup status
            if cleanup_errors:
                error_summary = f"Device panel cleanup completed with {len(cleanup_errors)} errors"
                self.logger.warning(error_summary)
                for error in cleanup_errors:
                    self.logger.error(f"Cleanup error: {error}")
            else:
                self.logger.info("Device panel cleanup completed successfully")
                
        except Exception as e:
            self.logger.error(f"Critical error during device panel cleanup: {e}")
            log_exception(self.logger, e, "Critical cleanup failure")
    
    def _clear_ui_references(self) -> None:
        """Clear all UI component references."""
        try:
            self.main_frame = None
            self.mic_device_combo = None
            self.sys_device_combo = None
            self.target_language_combo = None
            self.mic_status_indicator = None
            self.sys_status_indicator = None
            self.refresh_button = None
        except Exception as e:
            self.logger.error(f"Error clearing UI references: {e}")