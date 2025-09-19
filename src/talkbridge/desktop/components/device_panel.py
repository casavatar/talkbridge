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

import logging
from typing import List, Dict, Any, Optional, Callable
from pathlib import Path
import sys
import customtkinter as ctk

from talkbridge.desktop.ui.events import EventBus, EventHandler, DeviceEvent, AudioStateEvent
from talkbridge.desktop.ui.theme import (
    ColorPalette, Typography, Spacing, Dimensions, 
    ComponentThemes
)

class DeviceStatusIndicator:
    """Visual indicator for device status (active/inactive)."""
    
    def __init__(self, parent: ctk.CTkFrame, label: str):
        self.parent = parent
        self.label = label
        
        # Create indicator
        self.container = ctk.CTkFrame(parent, fg_color="transparent")
        self.container.pack(side="left", padx=5)
        
        # Status dot
        self.status_dot = ctk.CTkLabel(
            self.container,
            text="●",
            font=ctk.CTkFont(size=14),
            text_color="#666666"  # Default inactive
        )
        self.status_dot.pack(side="left")
        
        # Label
        self.label_widget = ctk.CTkLabel(
            self.container,
            text=label,
            font=(Typography.FONT_FAMILY_PRIMARY, Typography.FONT_SIZE_CAPTION),
            text_color="#cccccc"
        )
        self.label_widget.pack(side="left", padx=(5, 0))
    
    def set_active(self, active: bool, device_name: Optional[str] = None) -> None:
        """Set the active status and optionally update device name."""
        if active:
            self.status_dot.configure(text_color="#00ff88")  # Green for active
            if device_name:
                self.label_widget.configure(text=f"{self.label}: {device_name}")
        else:
            self.status_dot.configure(text_color="#666666")  # Gray for inactive
            self.label_widget.configure(text=f"{self.label}: Off")

class DevicePanel(EventHandler):
    """
    Device panel component for audio device management.
    
    Features:
    - Input device selection (microphone)
    - System audio device selection (loopback)
    - Device status indicators
    - Language setting controls
    - Refresh devices functionality
    """
    
    def __init__(self, parent: ctk.CTkFrame, event_bus: EventBus,
                 on_mic_device_change: Optional[Callable[[str], None]] = None,
                 on_sys_device_change: Optional[Callable[[str], None]] = None,
                 on_target_language_change: Optional[Callable[[str], None]] = None):
        """Initialize device panel component."""
        super().__init__(event_bus)
        self.parent = parent
        
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
        self.current_target_language = "en"
        self.available_languages = {
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
        
        # UI components
        self.main_frame = None
        self.mic_device_combo = None
        self.sys_device_combo = None
        self.target_language_combo = None
        self.mic_status_indicator = None
        self.sys_status_indicator = None
        self.refresh_button = None
        
        # Setup UI
        self.setup_ui()
        
        # Subscribe to events
        self.subscribe_to_events()
    
    def setup_ui(self) -> None:
        """Setup the device panel UI."""
        # Main container
        self.main_frame = ctk.CTkFrame(
            self.parent, 
            fg_color="#2d2d2d",
            corner_radius=Dimensions.RADIUS_MD
        )
        self.main_frame.pack(fill="x", padx=10, pady=5)
        
        # Title
        title_frame = ctk.CTkFrame(self.main_frame, fg_color="transparent")
        title_frame.pack(fill="x", padx=15, pady=(15, 5))
        
        title_label = ctk.CTkLabel(
            title_frame,
            text="Audio Devices & Settings",
            font=(Typography.FONT_FAMILY_PRIMARY, Typography.FONT_SIZE_BODY, Typography.FONT_WEIGHT_BOLD),
            text_color="#ffffff"
        )
        title_label.pack(side="left")
        
        # Refresh button
        self.refresh_button = ctk.CTkButton(
            title_frame,
            text="🔄 Refresh",
            width=80,
            height=25,
            font=(Typography.FONT_FAMILY_PRIMARY, Typography.FONT_SIZE_CAPTION),
            command=self._on_refresh_devices
        )
        self.refresh_button.pack(side="right")
        
        # Device selection section
        self._create_device_selection()
        
        # Status indicators section
        self._create_status_indicators()
        
        # Language settings section
        self._create_language_settings()
    
    def _create_device_selection(self) -> None:
        """Create device selection controls."""
        device_frame = ctk.CTkFrame(self.main_frame, fg_color="transparent")
        device_frame.pack(fill="x", padx=15, pady=5)
        
        # Microphone device selection
        mic_frame = ctk.CTkFrame(device_frame, fg_color="transparent")
        mic_frame.pack(fill="x", pady=2)
        
        mic_label = ctk.CTkLabel(
            mic_frame,
            text="Microphone:",
            font=(Typography.FONT_FAMILY_PRIMARY, Typography.FONT_SIZE_CAPTION),
            text_color="#cccccc",
            width=100
        )
        mic_label.pack(side="left", padx=(0, 10))
        
        self.mic_device_combo = ctk.CTkComboBox(
            mic_frame,
            values=["No devices available"],
            width=250,
            height=28,
            font=(Typography.FONT_FAMILY_PRIMARY, Typography.FONT_SIZE_CAPTION),
            command=self._on_mic_device_selected
        )
        self.mic_device_combo.pack(side="left", fill="x", expand=True)
        
        # System audio device selection
        sys_frame = ctk.CTkFrame(device_frame, fg_color="transparent")
        sys_frame.pack(fill="x", pady=2)
        
        sys_label = ctk.CTkLabel(
            sys_frame,
            text="System Audio:",
            font=(Typography.FONT_FAMILY_PRIMARY, Typography.FONT_SIZE_CAPTION),
            text_color="#cccccc",
            width=100
        )
        sys_label.pack(side="left", padx=(0, 10))
        
        self.sys_device_combo = ctk.CTkComboBox(
            sys_frame,
            values=["No devices available"],
            width=250,
            height=28,
            font=(Typography.FONT_FAMILY_PRIMARY, Typography.FONT_SIZE_CAPTION),
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
        """Handle audio state change events."""
        self.logger.debug(f"Audio state change: {event.source} - {event.is_active}")
        
        if event.source == "mic":
            self.mic_status_indicator.set_active(event.is_active, event.device_name)
        elif event.source == "system":
            self.sys_status_indicator.set_active(event.is_active, event.device_name)
    
    def _on_mic_device_selected(self, device_name: str) -> None:
        """Handle microphone device selection."""
        if device_name and device_name != "No devices available":
            self.selected_mic_device = device_name
            self.logger.info(f"Selected microphone device: {device_name}")
            
            if self.on_mic_device_change:
                self.on_mic_device_change(device_name)
    
    def _on_sys_device_selected(self, device_name: str) -> None:
        """Handle system audio device selection."""
        if device_name and device_name != "No devices available":
            self.selected_sys_device = device_name
            self.logger.info(f"Selected system audio device: {device_name}")
            
            if self.on_sys_device_change:
                self.on_sys_device_change(device_name)
    
    def _on_target_language_selected(self, language_selection: str) -> None:
        """Handle target language selection."""
        # Extract language code from "code - name" format
        if " - " in language_selection:
            language_code = language_selection.split(" - ")[0]
            self.current_target_language = language_code
            self.logger.info(f"Selected target language: {language_code}")
            
            if self.on_target_language_change:
                self.on_target_language_change(language_code)
    
    def _on_refresh_devices(self) -> None:
        """Handle device refresh request."""
        self.logger.info("Refreshing device lists")
        
        # Disable refresh button temporarily
        self.refresh_button.configure(state="disabled", text="Refreshing...")
        
        # Re-enable after a delay (will be updated by device refresh callback)
        self.refresh_button.after(2000, lambda: self.refresh_button.configure(
            state="normal", text="🔄 Refresh"
        ))
    
    def refresh_devices(self, input_devices: List[Dict[str, Any]], 
                       loopback_devices: List[Dict[str, Any]]) -> None:
        """Refresh device lists with new data."""
        self.logger.info(f"Updating device lists: {len(input_devices)} inputs, {len(loopback_devices)} loopbacks")
        
        # Store device data
        self.input_devices = input_devices
        self.loopback_devices = loopback_devices
        
        # Update microphone device combo
        mic_names = []
        for device in input_devices:
            name = device.get("name", "Unknown Device")
            index = device.get("index", "")
            mic_names.append(f"{name} ({index})")
        
        if mic_names:
            self.mic_device_combo.configure(values=mic_names)
            if not self.selected_mic_device and mic_names:
                self.mic_device_combo.set(mic_names[0])
                self.selected_mic_device = mic_names[0]
        else:
            self.mic_device_combo.configure(values=["No microphones available"])
            self.mic_device_combo.set("No microphones available")
        
        # Update system audio device combo
        sys_names = []
        for device in loopback_devices:
            name = device.get("name", "Unknown Device")
            index = device.get("index", "")
            sys_names.append(f"{name} ({index})")
        
        if sys_names:
            self.sys_device_combo.configure(values=sys_names)
            if not self.selected_sys_device and sys_names:
                self.sys_device_combo.set(sys_names[0])
                self.selected_sys_device = sys_names[0]
        else:
            self.sys_device_combo.configure(values=["No system audio available"])
            self.sys_device_combo.set("No system audio available")
    
    def set_status(self, mic_active: bool, sys_active: bool, 
                   mic_device: Optional[str] = None, sys_device: Optional[str] = None) -> None:
        """Set device status indicators."""
        self.mic_status_indicator.set_active(mic_active, mic_device)
        self.sys_status_indicator.set_active(sys_active, sys_device)
    
    def get_selected_mic_device(self) -> Optional[str]:
        """Get the currently selected microphone device."""
        return self.selected_mic_device
    
    def get_selected_sys_device(self) -> Optional[str]:
        """Get the currently selected system audio device."""
        return self.selected_sys_device
    
    def get_target_language(self) -> str:
        """Get the currently selected target language."""
        return self.current_target_language
    
    def set_target_language(self, language_code: str) -> None:
        """Set the target language programmatically."""
        if language_code in self.available_languages:
            self.current_target_language = language_code
            language_name = self.available_languages[language_code]
            self.target_language_combo.set(f"{language_code} - {language_name}")
            self.logger.info(f"Target language set to: {language_code}")
    
    def cleanup(self) -> None:
        """Clean up resources."""
        self.logger.info("Cleaning up device panel")
        self.unsubscribe_from_events()