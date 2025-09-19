#!/usr/bin/env python3
"""
TalkBridge Desktop - Chat Tab (Refactored)
==========================================

Clean composition root for the chat interface. Orchestrates UI components
and services using event-driven architecture with proper separation of concerns.

Author: TalkBridge Team
Date: 2025-09-18
Version: 3.1 (Enhanced with unified logging and error handling)

Key Changes:
- Reduced from 2400+ LOC to <300 LOC composition root
- Eliminated direct service dependencies from UI
- Implemented event-driven architecture with EventBus
- Split into focused, maintainable components
- Added proper error handling and logging
- Integrated centralized logging and custom exceptions
"""

import asyncio
from typing import Optional
from pathlib import Path
import customtkinter as ctk

.parent.parent.parent))

# Import centralized logging and exception handling
from talkbridge.logging_config import get_logger, log_exception
from talkbridge.utils.exceptions import UIError, create_ui_error

# Import event system and services
from talkbridge.desktop.ui.events import EventBus, get_global_event_bus
from talkbridge.desktop.ui.ui_services import UIServices

# Import UI components
from talkbridge.desktop.components.chat_history import ChatHistory
from talkbridge.desktop.components.device_panel import DevicePanel
from talkbridge.desktop.components.voice_controls import VoiceControls
from talkbridge.desktop.components.status_toast import StatusToast, ToastManager
from talkbridge.desktop.components.ai_actions import AIActions

# Import theme and utilities
try:
    from talkbridge.desktop.ui.theme import (
        ColorPalette, Typography, Spacing, Dimensions, 
        ComponentThemes, UIText
    )
    from talkbridge.desktop.ui.ui_utils import clean_text
    THEME_AVAILABLE = True
except ImportError:
    THEME_AVAILABLE = False

# Import legacy logging utilities for compatibility
try:
    from talkbridge.logging_config import add_error_context
    LEGACY_LOGGING_AVAILABLE = True
except ImportError:
    LEGACY_LOGGING_AVAILABLE = False

class ChatTab:
    """
    Composition root for the chat interface.
    
    Responsibilities:
    - Orchestrate UI components
    - Wire event bus subscriptions
    - Delegate actions to UI services
    - Manage component lifecycle
    
    Does NOT:
    - Directly interact with STT/TTS/Translation engines
    - Handle audio processing logic
    - Manage device enumeration
    - Process transcripts or translations
    """

    def __init__(self, parent, state_manager=None, core_bridge=None):
        """Initialize the chat tab composition root."""
        self.parent = parent
        self.state_manager = state_manager
        self.core_bridge = core_bridge
        
        # Setup logging
        self.logger = get_logger(__name__)
        if LEGACY_LOGGING_AVAILABLE:
            add_error_context(self.logger, "ChatTab")
        
        # Event system
        self.event_bus = get_global_event_bus()
        
        # Services facade
        self.ui_services = UIServices(self.event_bus)
        
        # UI components (initialized in setup_ui)
        self.main_frame: Optional[ctk.CTkFrame] = None
        self.chat_history: Optional[ChatHistory] = None
        self.device_panel: Optional[DevicePanel] = None
        self.voice_controls: Optional[VoiceControls] = None
        self.status_toast: Optional[StatusToast] = None
        self.ai_actions: Optional[AIActions] = None
        
        # Settings
        self.auto_refresh_devices = True
        
        # Initialize UI
        self.setup_ui()
        self.wire_component_events()
        
        # Initial setup
        self._initialize_components()
        
        self.logger.info("ChatTab composition root initialized successfully")

    def setup_ui(self) -> None:
        """Setup the main UI layout and instantiate components."""
        # Main container
        self.main_frame = ctk.CTkFrame(
            self.parent, 
            fg_color="#1e1e1e" if THEME_AVAILABLE else "#2b2b2b"
        )
        self.main_frame.pack(fill="both", expand=True, padx=10, pady=10)
        
        # Title header
        self._create_header()
        
        # Status toast (overlay)
        self.status_toast = StatusToast(self.main_frame, self.event_bus)
        ToastManager.initialize(self.main_frame, self.event_bus)
        
        # Main content layout
        self._create_layout()
        
        self.logger.info("UI components created and layouted")

    def _create_header(self) -> None:
        """Create the main header section."""
        header_frame = ctk.CTkFrame(self.main_frame, fg_color="transparent")
        header_frame.pack(fill="x", padx=10, pady=(10, 5))
        
        # Title
        title_text = clean_text("🗣️ AI Chat with Translation & Voice") if THEME_AVAILABLE else "🗣️ AI Chat with Translation & Voice"
        title_label = ctk.CTkLabel(
            header_frame,
            text=title_text,
            **ComponentThemes.get_label_theme() if THEME_AVAILABLE else {
                "font": ctk.CTkFont(size=20, weight="bold"),
                "text_color": "#ffffff"
            }
        )
        title_label.pack(side="left")
        
        # Status indicator
        self.status_indicator = ctk.CTkLabel(
            header_frame,
            text="●",
            font=ctk.CTkFont(size=16),
            text_color="#4CAF50"
        )
        self.status_indicator.pack(side="right", padx=10)

    def _create_layout(self) -> None:
        """Create the main layout with all components."""
        # Left panel: Chat history
        left_panel = ctk.CTkFrame(self.main_frame, fg_color="transparent")
        left_panel.pack(side="left", fill="both", expand=True, padx=(0, 5))
        
        self.chat_history = ChatHistory(left_panel, self.event_bus)
        
        # Right panel: Controls and actions
        right_panel = ctk.CTkFrame(self.main_frame, fg_color="transparent", width=400)
        right_panel.pack(side="right", fill="y", padx=(5, 0))
        right_panel.pack_propagate(False)  # Maintain fixed width
        
        # Device panel
        self.device_panel = DevicePanel(
            right_panel, 
            self.event_bus,
            on_mic_device_change=self._on_mic_device_change,
            on_sys_device_change=self._on_sys_device_change,
            on_target_language_change=self._on_target_language_change
        )
        
        # Voice controls
        self.voice_controls = VoiceControls(
            right_panel,
            self.event_bus,
            on_mic_start=self._on_mic_start,
            on_mic_stop=self._on_mic_stop,
            on_system_start=self._on_system_start,
            on_system_stop=self._on_system_stop
        )
        
        # AI actions
        self.ai_actions = AIActions(
            right_panel,
            self.event_bus,
            on_send_message=self._on_send_ai_message,
            on_tts_toggle=self._on_tts_toggle
        )

    def wire_component_events(self) -> None:
        """Wire event bus subscriptions for component coordination."""
        # Note: Individual components subscribe to their own relevant events
        # This method is for cross-component coordination if needed
        pass

    def _initialize_components(self) -> None:
        """Initialize components with default settings."""
        try:
            # Refresh device lists
            if self.auto_refresh_devices:
                self._refresh_devices()
            
            # Set default language
            self.ui_services.set_target_language("en")
            
            self.logger.info("Components initialized successfully")
            
        except Exception as e:
            self.logger.error(f"Error initializing components: {e}")
            log_exception(self.logger, e, "Component initialization failed")

    # Device management callbacks
    def _on_mic_device_change(self, device_name: str) -> None:
        """Handle microphone device selection."""
        self.logger.info(f"Microphone device changed: {device_name}")
        # Device changes are handled by the device panel and services
        # UI components don't need to track device state directly

    def _on_sys_device_change(self, device_name: str) -> None:
        """Handle system audio device selection."""
        self.logger.info(f"System audio device changed: {device_name}")

    def _on_target_language_change(self, language_code: str) -> None:
        """Handle target language selection."""
        self.logger.info(f"Target language changed: {language_code}")
        self.ui_services.set_target_language(language_code)

    # Audio control callbacks
    def _on_mic_start(self) -> None:
        """Handle microphone start request."""
        self.logger.info("Starting microphone capture")
        self.ui_services.start_microphone()

    def _on_mic_stop(self) -> None:
        """Handle microphone stop request."""
        self.logger.info("Stopping microphone capture")
        self.ui_services.stop_microphone()

    def _on_system_start(self) -> None:
        """Handle system audio start request."""
        self.logger.info("Starting system audio capture")
        self.ui_services.start_system_audio()

    def _on_system_stop(self) -> None:
        """Handle system audio stop request."""
        self.logger.info("Stopping system audio capture")
        self.ui_services.stop_system_audio()

    # AI interaction callbacks
    def _on_send_ai_message(self, message: str, model: str) -> None:
        """Handle AI message send request."""
        self.logger.info(f"Sending AI message with model {model}: {message[:50]}...")
        
        # Add user message to chat history
        self.chat_history.add_user_message(message)
        
        # Send to AI asynchronously
        asyncio.create_task(self._send_ai_message_async(message, model))

    async def _send_ai_message_async(self, message: str, model: str) -> None:
        """Send message to AI asynchronously."""
        try:
            response = await self.ui_services.send_chat_message(message, model)
            
            if response:
                # Add assistant response to chat history
                self.chat_history.add_assistant_message(response)
                
                # Handle TTS if enabled
                if self.ai_actions.is_tts_enabled():
                    # TTS would be handled by the services layer
                    pass
            
        except Exception as e:
            self.logger.error(f"Error sending AI message: {e}")
            self.event_bus.emit_status(f"AI chat error: {e}", "error")
        finally:
            # Reset processing state
            self.ai_actions.set_processing(False)

    def _on_tts_toggle(self, enabled: bool) -> None:
        """Handle TTS toggle."""
        self.logger.info(f"TTS toggled: {enabled}")
        # TTS state is managed by the AI actions component

    # Utility methods
    def _refresh_devices(self) -> None:
        """Refresh audio device lists."""
        self.logger.info("Refreshing audio devices")
        
        try:
            # Get device lists from services
            input_devices = self.ui_services.get_input_devices()
            loopback_devices = self.ui_services.get_system_loopback_devices()
            
            # Update device panel
            self.device_panel.refresh_devices(input_devices, loopback_devices)
            
            # Emit device refresh event
            self.ui_services.refresh_devices()
            
        except Exception as e:
            self.logger.error(f"Error refreshing devices: {e}")

    # Public API methods (for external integration)
    def get_conversation_history(self) -> str:
        """Get the full conversation as text."""
        if self.chat_history:
            return self.chat_history.get_conversation_text()
        return ""

    def clear_conversation(self) -> None:
        """Clear the conversation history."""
        if self.chat_history:
            self.chat_history.clear_history()
        self.logger.info("Conversation history cleared")

    def set_language(self, language_code: str) -> None:
        """Set the target language."""
        self.device_panel.set_target_language(language_code)

    def get_language(self) -> str:
        """Get the current target language."""
        return self.device_panel.get_target_language()

    def cleanup(self) -> None:
        """Cleanup resources and stop all services."""
        try:
            self.logger.info("Cleaning up ChatTab resources")
            
            # Cleanup services
            self.ui_services.shutdown()
            
            # Cleanup components
            if self.chat_history:
                self.chat_history.cleanup()
            if self.device_panel:
                self.device_panel.cleanup()
            if self.voice_controls:
                self.voice_controls.cleanup()
            if self.status_toast:
                self.status_toast.cleanup()
            if self.ai_actions:
                self.ai_actions.cleanup()
            
            # Cleanup toast manager
            ToastManager.cleanup()
            
            self.logger.info("ChatTab cleanup completed")
            
        except Exception as e:
            self.logger.error(f"Error during ChatTab cleanup: {e}")
            log_exception(self.logger, e, "Cleanup failed")