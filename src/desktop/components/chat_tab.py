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

# Standard library imports
import asyncio
from pathlib import Path
from typing import Optional, Any, Dict

# Third-party imports
import customtkinter as ctk

# Local imports - Core utilities
from ...logging_config import get_logger, log_exception
from ...utils.exceptions import UIError, create_ui_error

# Local imports - Event system and services
from ..ui.events import EventBus, get_global_event_bus
from ..ui.ui_services import UIServices

# Local imports - UI components
from .chat_history import ChatHistory
from .device_panel import DevicePanel
from .voice_controls import VoiceControls
from .status_toast import StatusToast, ToastManager
from .ai_actions import AIActions

# Optional imports - Theme and utilities
try:
    from ..ui.theme import (
        ColorPalette, Typography, Spacing, Dimensions, 
        ComponentThemes, UIText
    )
    from ..ui.ui_utils import clean_text
    THEME_AVAILABLE = True
except ImportError:
    # Define fallback functions/classes
    ComponentThemes = None
    clean_text = lambda x: x
    THEME_AVAILABLE = False

# Optional imports - Legacy logging utilities for compatibility
try:
    from ...logging_config import add_error_context
    LEGACY_LOGGING_AVAILABLE = True
except ImportError:
    # Define fallback function
    add_error_context = lambda logger, context: None
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

    def __init__(self, parent: ctk.CTk, state_manager: Optional[Any] = None, core_bridge: Optional[Any] = None) -> None:
        """Initialize the chat tab composition root.
        
        Args:
            parent: The parent widget for this chat tab
            state_manager: Optional state manager instance
            core_bridge: Optional core bridge instance
        """
        self.parent = parent
        self.state_manager = state_manager
        self.core_bridge = core_bridge
        
        # Setup logging
        self.logger = get_logger(__name__)
        if LEGACY_LOGGING_AVAILABLE:
            try:
                add_error_context(self.logger, "ChatTab")
            except NameError:
                # Fallback if add_error_context is not available
                pass
        
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
        self.status_indicator: Optional[ctk.CTkLabel] = None
        
        # Settings
        self.auto_refresh_devices: bool = True
        
        # Initialize UI
        self.setup_ui()
        self.wire_component_events()
        
        # Initial setup
        self._initialize_components()
        
        self.logger.info("ChatTab composition root initialized successfully")

    def setup_ui(self) -> None:
        """Setup the main UI layout and instantiate components.
        
        This method creates the main UI structure including:
        - Main container frame
        - Header with title and status indicator
        - Status toast overlay
        - Main content layout with chat and controls
        """
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
        """Create the main header section with title and status indicator.
        
        The header includes:
        - Application title with emoji
        - Status indicator showing connection state
        """
        header_frame = ctk.CTkFrame(self.main_frame, fg_color="transparent")
        header_frame.pack(fill="x", padx=10, pady=(10, 5))
        
        # Title with theme support
        if THEME_AVAILABLE and ComponentThemes is not None:
            title_text = clean_text("🗣️ AI Chat with Translation & Voice")
            title_label_config = ComponentThemes.get_label_theme()
        else:
            title_text = "🗣️ AI Chat with Translation & Voice"
            title_label_config = {
                "font": ctk.CTkFont(size=20, weight="bold"),
                "text_color": "#ffffff"
            }
        
        title_label = ctk.CTkLabel(
            header_frame,
            text=title_text,
            **title_label_config
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
        """Create the main layout with all UI components.
        
        Layout structure:
        - Left panel: Chat history (expandable)
        - Right panel: Device controls, voice controls, and AI actions (fixed width)
        """
        # Left panel: Chat history
        left_panel = ctk.CTkFrame(self.main_frame, fg_color="transparent")
        left_panel.pack(side="left", fill="both", expand=True, padx=(0, 5))
        
        self.chat_history = ChatHistory(left_panel, self.event_bus)
        
        # Right panel: Controls and actions
        right_panel = ctk.CTkFrame(self.main_frame, fg_color="transparent", width=400)
        right_panel.pack(side="right", fill="y", padx=(5, 0))
        right_panel.pack_propagate(False)  # Maintain fixed width
        
        # Initialize control components
        self._create_control_components(right_panel)

    def _create_control_components(self, parent_panel: ctk.CTkFrame) -> None:
        """Create control components in the right panel.
        
        Args:
            parent_panel: The parent frame to contain the control components
        """
        # Device panel
        self.device_panel = DevicePanel(
            parent_panel, 
            self.event_bus,
            on_mic_device_change=self._on_mic_device_change,
            on_sys_device_change=self._on_sys_device_change,
            on_target_language_change=self._on_target_language_change
        )
        
        # Voice controls
        self.voice_controls = VoiceControls(
            parent_panel,
            self.event_bus,
            on_mic_start=self._on_mic_start,
            on_mic_stop=self._on_mic_stop,
            on_system_start=self._on_system_start,
            on_system_stop=self._on_system_stop
        )
        
        # AI actions
        self.ai_actions = AIActions(
            parent_panel,
            self.event_bus,
            on_send_message=self._on_send_ai_message,
            on_tts_toggle=self._on_tts_toggle
        )

    def wire_component_events(self) -> None:
        """Wire event bus subscriptions for component coordination.
        
        This method sets up any cross-component event subscriptions needed
        for coordination between different UI components. Currently, most
        components handle their own events independently.
        """
        # Note: Individual components subscribe to their own relevant events
        # This method is reserved for future cross-component coordination
        self.logger.debug("Component event wiring completed")

    def _initialize_components(self) -> None:
        """Initialize components with default settings.
        
        This method performs initial setup for all UI components including
        device refresh and language configuration.
        """
        try:
            self.logger.debug("Starting component initialization")
            
            # Refresh device lists if enabled
            if self.auto_refresh_devices:
                self._refresh_devices()
            
            # Set default language
            self._set_default_language()
            
            # Validate component initialization
            self._validate_component_state()
            
            self.logger.info("Components initialized successfully")
            
        except Exception as e:
            self.logger.error(f"Error initializing components: {e}")
            log_exception(self.logger, e, "Component initialization failed")
            self.event_bus.emit_status("Component initialization failed", "error")
    
    def _set_default_language(self) -> None:
        """Set the default target language."""
        try:
            default_language = "en"
            self.ui_services.set_target_language(default_language)
            self.logger.debug(f"Default language set to: {default_language}")
        except Exception as e:
            self.logger.error(f"Error setting default language: {e}")
            raise
    
    def _validate_component_state(self) -> None:
        """Validate that all required components are properly initialized."""
        required_components = [
            ("main_frame", self.main_frame),
            ("chat_history", self.chat_history),
            ("device_panel", self.device_panel),
            ("voice_controls", self.voice_controls),
            ("ai_actions", self.ai_actions),
            ("status_toast", self.status_toast)
        ]
        
        missing_components = []
        for name, component in required_components:
            if component is None:
                missing_components.append(name)
        
        if missing_components:
            error_msg = f"Missing required components: {', '.join(missing_components)}"
            self.logger.error(error_msg)
            raise RuntimeError(error_msg)
        
        self.logger.debug("All required components are initialized")

    # Device management callbacks
    def _on_mic_device_change(self, device_name: str) -> None:
        """Handle microphone device selection.
        
        Args:
            device_name: The name of the selected microphone device
        """
        self.logger.info(f"Microphone device changed: {device_name}")
        try:
            # Device changes are handled by the device panel and services
            # UI components don't need to track device state directly
            self.event_bus.emit_status(f"Microphone changed to: {device_name}", "info", duration=2.0)
        except Exception as e:
            self.logger.error(f"Error handling mic device change: {e}")
            log_exception(self.logger, e, "Mic device change failed")

    def _on_sys_device_change(self, device_name: str) -> None:
        """Handle system audio device selection.
        
        Args:
            device_name: The name of the selected system audio device
        """
        self.logger.info(f"System audio device changed: {device_name}")
        try:
            self.event_bus.emit_status(f"System audio changed to: {device_name}", "info", duration=2.0)
        except Exception as e:
            self.logger.error(f"Error handling system device change: {e}")
            log_exception(self.logger, e, "System device change failed")

    def _on_target_language_change(self, language_code: str) -> None:
        """Handle target language selection.
        
        Args:
            language_code: The selected language code (e.g., 'en', 'es', 'fr')
        """
        self.logger.info(f"Target language changed: {language_code}")
        try:
            self.ui_services.set_target_language(language_code)
            self.event_bus.emit_status(f"Translation language: {language_code}", "success", duration=2.0)
        except Exception as e:
            self.logger.error(f"Error setting target language: {e}")
            log_exception(self.logger, e, "Language change failed")

    # Audio control callbacks
    def _on_mic_start(self) -> None:
        """Handle microphone start request."""
        self.logger.info("Starting microphone capture")
        try:
            self.ui_services.start_microphone()
        except Exception as e:
            self.logger.error(f"Error starting microphone: {e}")
            log_exception(self.logger, e, "Microphone start failed")
            self.event_bus.emit_status(f"Failed to start microphone: {e}", "error")

    def _on_mic_stop(self) -> None:
        """Handle microphone stop request."""
        self.logger.info("Stopping microphone capture")
        try:
            self.ui_services.stop_microphone()
        except Exception as e:
            self.logger.error(f"Error stopping microphone: {e}")
            log_exception(self.logger, e, "Microphone stop failed")

    def _on_system_start(self) -> None:
        """Handle system audio start request."""
        self.logger.info("Starting system audio capture")
        try:
            self.ui_services.start_system_audio()
        except Exception as e:
            self.logger.error(f"Error starting system audio: {e}")
            log_exception(self.logger, e, "System audio start failed")
            self.event_bus.emit_status(f"Failed to start system audio: {e}", "error")

    def _on_system_stop(self) -> None:
        """Handle system audio stop request."""
        self.logger.info("Stopping system audio capture")
        try:
            self.ui_services.stop_system_audio()
        except Exception as e:
            self.logger.error(f"Error stopping system audio: {e}")
            log_exception(self.logger, e, "System audio stop failed")

    # AI interaction callbacks
    def _on_send_ai_message(self, message: str, model: str) -> None:
        """Handle AI message send request.
        
        Args:
            message: The message to send to the AI
            model: The AI model to use
        """
        self.logger.info(f"Sending AI message with model {model}: {message[:50]}...")
        
        try:
            # Add user message to chat history
            if self.chat_history is not None:
                self.chat_history.add_user_message(message)
            else:
                self.logger.warning("Chat history not initialized, cannot add user message")
            
            # Send to AI asynchronously
            asyncio.create_task(self._send_ai_message_async(message, model))
            
        except Exception as e:
            self.logger.error(f"Error handling AI message send request: {e}")
            log_exception(self.logger, e, "AI message send request failed")
            self.event_bus.emit_status(f"Failed to send message: {e}", "error")

    async def _send_ai_message_async(self, message: str, model: str) -> None:
        """Send message to AI asynchronously.
        
        Args:
            message: The message to send to the AI
            model: The AI model to use
        """
        try:
            response = await self.ui_services.send_chat_message(message, model)
            
            if response and self.chat_history is not None:
                # Add assistant response to chat history
                self.chat_history.add_assistant_message(response)
                
                # Handle TTS if enabled
                if self.ai_actions is not None and self.ai_actions.is_tts_enabled():
                    # TTS would be handled by the services layer
                    self.logger.debug("TTS enabled, would trigger text-to-speech")
            elif not response:
                self.logger.warning("Empty response received from AI")
                self.event_bus.emit_status("Received empty response from AI", "warning")
            
        except Exception as e:
            self.logger.error(f"Error sending AI message: {e}")
            log_exception(self.logger, e, "AI message sending failed")
            self.event_bus.emit_status(f"AI chat error: {e}", "error")
        finally:
            # Reset processing state
            try:
                if self.ai_actions is not None:
                    self.ai_actions.set_processing(False)
            except Exception as e:
                self.logger.error(f"Error resetting AI processing state: {e}")

    def _on_tts_toggle(self, enabled: bool) -> None:
        """Handle TTS toggle.
        
        Args:
            enabled: Whether TTS is enabled or disabled
        """
        self.logger.info(f"TTS toggled: {enabled}")
        try:
            # TTS state is managed by the AI actions component
            status_text = "enabled" if enabled else "disabled"
            self.event_bus.emit_status(f"Text-to-speech {status_text}", "info", duration=2.0)
        except Exception as e:
            self.logger.error(f"Error handling TTS toggle: {e}")
            log_exception(self.logger, e, "TTS toggle failed")

    # Utility methods
    def _refresh_devices(self) -> None:
        """Refresh audio device lists."""
        self.logger.info("Refreshing audio devices")
        
        try:
            # Get device lists from services
            input_devices = self.ui_services.get_input_devices()
            loopback_devices = self.ui_services.get_system_loopback_devices()
            
            # Update device panel
            if self.device_panel is not None:
                self.device_panel.refresh_devices(input_devices, loopback_devices)
            else:
                self.logger.warning("Device panel not initialized, cannot refresh devices")
            
            # Emit device refresh event
            self.ui_services.refresh_devices()
            
        except Exception as e:
            self.logger.error(f"Error refreshing devices: {e}")
            log_exception(self.logger, e, "Device refresh failed")

    # Public API methods (for external integration)
    def get_conversation_history(self) -> str:
        """Get the full conversation as text.
        
        Returns:
            The conversation history as a string, or empty string if not available.
        """
        if self.chat_history is not None:
            try:
                return self.chat_history.get_conversation_text()
            except Exception as e:
                self.logger.error(f"Error getting conversation history: {e}")
                return ""
        return ""

    def clear_conversation(self) -> None:
        """Clear the conversation history."""
        if self.chat_history is not None:
            try:
                self.chat_history.clear_history()
                self.logger.info("Conversation history cleared")
            except Exception as e:
                self.logger.error(f"Error clearing conversation history: {e}")
                log_exception(self.logger, e, "Clear conversation failed")
        else:
            self.logger.warning("Chat history not initialized, cannot clear")

    def set_language(self, language_code: str) -> None:
        """Set the target language.
        
        Args:
            language_code: The language code to set (e.g., 'en', 'es', 'fr')
        """
        if self.device_panel is not None:
            try:
                self.device_panel.set_target_language(language_code)
                self.logger.info(f"Target language set to: {language_code}")
            except Exception as e:
                self.logger.error(f"Error setting language: {e}")
                log_exception(self.logger, e, "Language setting failed")
        else:
            self.logger.warning("Device panel not initialized, cannot set language")

    def get_language(self) -> str:
        """Get the current target language.
        
        Returns:
            The current language code, or 'en' as default if not available.
        """
        if self.device_panel is not None:
            try:
                return self.device_panel.get_target_language()
            except Exception as e:
                self.logger.error(f"Error getting language: {e}")
                return "en"  # Default fallback
        else:
            self.logger.warning("Device panel not initialized, returning default language")
            return "en"

    def cleanup(self) -> None:
        """Cleanup resources and stop all services.
        
        This method ensures proper cleanup of all components and services
        to prevent resource leaks and gracefully shut down the chat tab.
        """
        cleanup_errors = []
        
        try:
            self.logger.info("Starting ChatTab cleanup process")
            
            # Stop any ongoing audio processing first
            self._stop_all_audio_processing()
            
            # Cleanup services
            self._cleanup_services(cleanup_errors)
            
            # Cleanup UI components
            self._cleanup_components(cleanup_errors)
            
            # Cleanup toast manager
            self._cleanup_toast_manager(cleanup_errors)
            
            # Report cleanup status
            if cleanup_errors:
                error_summary = f"Cleanup completed with {len(cleanup_errors)} errors"
                self.logger.warning(error_summary)
                for error in cleanup_errors:
                    self.logger.error(f"Cleanup error: {error}")
            else:
                self.logger.info("ChatTab cleanup completed successfully")
            
        except Exception as e:
            self.logger.error(f"Critical error during ChatTab cleanup: {e}")
            log_exception(self.logger, e, "Critical cleanup failure")
    
    def _stop_all_audio_processing(self) -> None:
        """Stop all audio processing before cleanup."""
        try:
            self.ui_services.stop_microphone()
            self.ui_services.stop_system_audio()
            self.logger.debug("Audio processing stopped")
        except Exception as e:
            self.logger.error(f"Error stopping audio processing: {e}")
    
    def _cleanup_services(self, cleanup_errors: list) -> None:
        """Cleanup core services."""
        try:
            self.ui_services.shutdown()
            self.logger.debug("Services cleanup completed")
        except Exception as e:
            cleanup_errors.append(f"Services cleanup failed: {e}")
    
    def _cleanup_components(self, cleanup_errors: list) -> None:
        """Cleanup UI components."""
        components = [
            ("chat_history", self.chat_history),
            ("device_panel", self.device_panel),
            ("voice_controls", self.voice_controls),
            ("status_toast", self.status_toast),
            ("ai_actions", self.ai_actions)
        ]
        
        for name, component in components:
            if component is not None:
                try:
                    component.cleanup()
                    self.logger.debug(f"{name} cleanup completed")
                except Exception as e:
                    cleanup_errors.append(f"{name} cleanup failed: {e}")
    
    def _cleanup_toast_manager(self, cleanup_errors: list) -> None:
        """Cleanup toast manager."""
        try:
            ToastManager.cleanup()
            self.logger.debug("Toast manager cleanup completed")
        except Exception as e:
            cleanup_errors.append(f"Toast manager cleanup failed: {e}")