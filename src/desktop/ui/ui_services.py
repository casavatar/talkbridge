#!/usr/bin/env python3
"""
TalkBridge Desktop - UI Services Facade  
======================================

Thin facade between UI components and core services.
Provides clean interface and handles service-to-event translation.
Enhanced with unified error handling and user-friendly notifications.

Author: TalkBridge Team
Date: 2025-09-18
Version: 2.0 (Enhanced error handling)
"""

from typing import Optional, List, Dict, Any, Literal, Callable
from pathlib import Path
import sys

# Import centralized logging and exception handling
from ...logging_config import get_logger, log_exception
from ...utils.exceptions import (
    TalkBridgeError, AudioCaptureError, DeviceError, PipelineError,
    STTError, TTSError, TranslationError, ServiceError,
    create_audio_capture_error, create_pipeline_error
)

from .events import EventBus, AudioSource, DeviceType
from ...audio.pipeline_manager import PipelineManager
from ...ollama.ollama_client import OllamaClient

class UIServices:
    """
    Thin facade between UI and core services.
    
    Responsibilities:
    - Provide clean UI-facing API for core services
    - Convert service callbacks to UI events via EventBus
    - Handle service initialization and cleanup
    - Manage service state and health
    - Convert service errors to user-friendly notifications
    """
    
    def __init__(self, event_bus: EventBus):
        """Initialize UI services with event bus."""
        self.event_bus = event_bus
        self.logger = get_logger(__name__)
        
        # Core services (initialized lazily)
        self._pipeline_manager: Optional[PipelineManager] = None
        self._ollama_client: Optional[OllamaClient] = None
        
        # Service state
        self._services_initialized = False
        self._current_target_language = "en"
        self._mic_active = False
        self._system_active = False
        
    @property
    def pipeline_manager(self) -> Optional[PipelineManager]:
        """Get pipeline manager, initializing if needed."""
        if self._pipeline_manager is None:
            try:
                self._initialize_pipeline_manager()
            except Exception as e:
                self.logger.error(f"Failed to initialize pipeline manager: {e}")
                self.event_bus.emit_status(f"Audio pipeline initialization failed: {e}", "error")
        return self._pipeline_manager
    
    @property
    def ollama_client(self) -> Optional[OllamaClient]:
        """Get Ollama client, initializing if needed."""
        if self._ollama_client is None:
            try:
                self._initialize_ollama_client()
            except Exception as e:
                self.logger.error(f"Failed to initialize Ollama client: {e}")
                self.event_bus.emit_status(f"AI service initialization failed: {e}", "error")
        return self._ollama_client
    
    def _initialize_pipeline_manager(self) -> None:
        """Initialize the audio pipeline manager with callbacks."""
        try:
            # Pass transcript and translation callbacks to constructor
            self._pipeline_manager = PipelineManager(
                on_transcript=self._on_transcript,
                on_translation=self._on_translation,
                on_status=self._on_pipeline_status
            )
            
            # Set additional callbacks via set_callbacks method
            self._pipeline_manager.set_callbacks(
                error_callback=self._on_pipeline_error,
                data_callback=None  # No raw data to UI
            )
            
            self.logger.info("Pipeline manager initialized successfully")
            self.event_bus.emit_status("Audio pipeline ready", "success")
            
        except Exception as e:
            self.logger.error(f"Pipeline manager initialization failed: {e}")
            raise
    
    def _initialize_ollama_client(self) -> None:
        """Initialize the Ollama client."""
        try:
            self._ollama_client = OllamaClient()
            self.logger.info("Ollama client initialized successfully")
            self.event_bus.emit_status("AI service ready", "success")
            
        except Exception as e:
            self.logger.error(f"Ollama client initialization failed: {e}")
            raise
    
    # Pipeline callback handlers (convert to events)
    def _on_pipeline_status(self, source: str, status: str, device: str) -> None:
        """Handle pipeline status updates."""
        self.logger.debug(f"Pipeline status: {source}:{status} ({device})")
        
        # Convert to UI events
        audio_source: AudioSource = "mic" if "mic" in source.lower() else "system"
        is_active = "active" in status.lower() or "recording" in status.lower()
        
        self.event_bus.emit_audio_state_change(
            source=audio_source,
            is_active=is_active,
            device_name=device
        )
        
        # Also emit as status notification
        self.event_bus.emit_status(f"{source}: {status} ({device})", "info", duration=3.0)
    
    def _on_pipeline_error(self, error_message: str) -> None:
        """Handle pipeline errors."""
        self.logger.error(f"Pipeline error: {error_message}")
        self.event_bus.emit_status(error_message, "error")
    
    def _on_transcript(self, source: str, text: str, language: str, confidence: Optional[float] = None) -> None:
        """Handle transcript from pipeline."""
        self.logger.debug(f"Transcript from {source}: {text[:50]}... (lang: {language})")
        
        audio_source: AudioSource = "mic" if "mic" in source.lower() else "system"
        self.event_bus.emit_transcript(
            source=audio_source,
            text=text,
            language=language,
            confidence=confidence
        )
    
    def _on_translation(self, source: str, original_text: str, source_language: str, 
                       target_language: str, translated_text: str) -> None:
        """Handle translation from pipeline."""
        self.logger.debug(f"Translation from {source}: {original_text[:30]}... -> {translated_text[:30]}...")
        
        audio_source: AudioSource = "mic" if "mic" in source.lower() else "system"
        self.event_bus.emit_translation(
            source=audio_source,
            original_text=original_text,
            source_language=source_language,
            target_language=target_language,
            translated_text=translated_text
        )
    
    # Error handling methods
    def _handle_service_error(self, error: Exception, operation: str, 
                             user_context: str = "") -> None:
        """
        Handle service errors with proper logging and user notification.
        
        Args:
            error: The exception that occurred
            operation: Description of the operation that failed
            user_context: Additional context for user message
        """
        if isinstance(error, TalkBridgeError):
            # Use the structured error information
            self.logger.error(f"{operation} failed: {error.message}", 
                            extra={"error_code": error.error_code, 
                                   "context": error.context})
            
            # Emit user-friendly message to UI
            self.event_bus.emit_status(error.user_message, "error")
            
        else:
            # Handle unexpected errors
            error_msg = f"{operation} failed: {str(error)}"
            log_exception(self.logger, error, operation)
            
            # Provide generic user message
            user_msg = f"{user_context} Please try again or restart the application."
            self.event_bus.emit_status(user_msg, "error")
    
    # Audio control methods
    def start_microphone(self, device_index: Optional[int] = None, 
                        device_hint: str = "auto") -> bool:
        """Start microphone capture with enhanced error handling."""
        try:
            if not self.pipeline_manager:
                error = create_pipeline_error(
                    "Audio pipeline not initialized",
                    stage="initialization"
                )
                self._handle_service_error(error, "start microphone", 
                                         "Audio system not ready.")
                return False
            
            # Handle None device_index - convert to appropriate value for pipeline
            resolved_device_index = device_index if device_index is not None else -1
            
            result = self.pipeline_manager.start_mic_stream(resolved_device_index, device_hint)
            if result:
                self._mic_active = True
                self.logger.info(f"Microphone started (device: {device_hint})")
                self.event_bus.emit_status("Microphone started", "info")
            else:
                # Create specific error for failed start
                error = create_audio_capture_error(
                    f"Failed to start microphone with device hint: {device_hint}",
                    device_name=device_hint if device_hint != "auto" else None
                )
                self._handle_service_error(error, "start microphone")
            
            return result
            
        except (AudioCaptureError, DeviceError, PipelineError) as e:
            # Handle known audio-related errors
            self._handle_service_error(e, "start microphone")
            return False
            
        except Exception as e:
            # Handle unexpected errors
            self._handle_service_error(e, "start microphone", "Microphone failed to start.")
            return False
    
    def stop_microphone(self) -> bool:
        """Stop microphone capture with enhanced error handling."""
        try:
            if not self.pipeline_manager:
                return False
            
            result = self.pipeline_manager.stop_mic_stream()
            if result:
                self._mic_active = False
                self.logger.info("Microphone stopped")
                self.event_bus.emit_status("Microphone stopped", "info")
            else:
                self.logger.warning("Failed to stop microphone cleanly")
                self.event_bus.emit_status("Microphone stop may be incomplete", "warning")
            
            return result
            
        except Exception as e:
            self.logger.error(f"Error stopping microphone: {e}")
            self.event_bus.emit_status(f"Microphone stop error: {e}", "error")
            return False
    
    def start_system_audio(self, device_index: Optional[int] = None, 
                          device_hint: str = "auto") -> bool:
        """Start system audio capture."""
        try:
            if not self.pipeline_manager:
                self.event_bus.emit_status("Audio pipeline not available", "error")
                return False
            
            # Handle None device_index - convert to appropriate value for pipeline
            resolved_device_index = device_index if device_index is not None else -1
            
            result = self.pipeline_manager.start_system_stream(resolved_device_index, device_hint)
            if result:
                self._system_active = True
                self.logger.info(f"System audio started (device: {device_hint})")
            else:
                self.event_bus.emit_status("Failed to start system audio", "error")
            
            return result
            
        except Exception as e:
            self.logger.error(f"Error starting system audio: {e}")
            self.event_bus.emit_status(f"System audio error: {e}", "error")
            return False
    
    def stop_system_audio(self) -> bool:
        """Stop system audio capture."""
        try:
            if not self.pipeline_manager:
                return False
            
            result = self.pipeline_manager.stop_system_stream()
            if result:
                self._system_active = False
                self.logger.info("System audio stopped")
            
            return result
            
        except Exception as e:
            self.logger.error(f"Error stopping system audio: {e}")
            self.event_bus.emit_status(f"System audio stop error: {e}", "error")
            return False
    
    def set_target_language(self, language_code: str) -> bool:
        """Set translation target language."""
        try:
            if not self.pipeline_manager:
                return False
            
            self.pipeline_manager.set_target_language(language_code)
            self._current_target_language = language_code
            self.logger.info(f"Target language set to: {language_code}")
            self.event_bus.emit_status(f"Translation target: {language_code}", "info", duration=2.0)
            return True
            
        except Exception as e:
            self.logger.error(f"Error setting target language: {e}")
            self.event_bus.emit_status(f"Language setting error: {e}", "error")
            return False
    
    # Device enumeration methods
    def get_input_devices(self) -> List[Dict[str, Any]]:
        """Get available input devices."""
        try:
            if not self.pipeline_manager:
                return []
            
            device_infos = self.pipeline_manager.list_input_devices()
            devices = []
            for device_info in device_infos:
                devices.append({
                    'index': device_info.index,
                    'name': device_info.name,
                    'channels': device_info.channels,
                    'sample_rate': device_info.sample_rate,
                    'is_input': device_info.is_input
                })
            
            self.logger.debug(f"Found {len(devices)} input devices")
            return devices
            
        except Exception as e:
            self.logger.error(f"Error listing input devices: {e}")
            self.event_bus.emit_status("Failed to list input devices", "error")
            return []
    
    def get_system_loopback_devices(self) -> List[Dict[str, Any]]:
        """Get available system loopback devices."""
        try:
            if not self.pipeline_manager:
                return []
            
            device_infos = self.pipeline_manager.list_system_loopbacks()
            devices = []
            for device_info in device_infos:
                devices.append({
                    'index': device_info.index,
                    'name': device_info.name,
                    'channels': device_info.channels,
                    'sample_rate': device_info.sample_rate,
                    'is_input': device_info.is_input
                })
            
            self.logger.debug(f"Found {len(devices)} loopback devices")
            return devices
            
        except Exception as e:
            self.logger.error(f"Error listing loopback devices: {e}")
            self.event_bus.emit_status("Failed to list system audio devices", "error")
            return []
    
    def refresh_devices(self) -> None:
        """Refresh device lists and emit update events."""
        try:
            input_devices = self.get_input_devices()
            loopback_devices = self.get_system_loopback_devices()
            
            # Emit device availability events
            for device in input_devices:
                self.event_bus.emit_device_change(
                    device_type="input",
                    device_id=str(device.get("index", "")),
                    device_name=device.get("name", "Unknown"),
                    is_available=True
                )
            
            for device in loopback_devices:
                self.event_bus.emit_device_change(
                    device_type="loopback",
                    device_id=str(device.get("index", "")),
                    device_name=device.get("name", "Unknown"),
                    is_available=True
                )
            
            self.logger.info(f"Refreshed devices: {len(input_devices)} inputs, {len(loopback_devices)} loopbacks")
            
        except Exception as e:
            self.logger.error(f"Error refreshing devices: {e}")
            self.event_bus.emit_status("Device refresh failed", "error")
    
    # AI/Chat methods
    async def send_chat_message(self, message: str, model: str = "llama3.2:3b") -> Optional[str]:
        """Send message to AI and return response."""
        try:
            if not self.ollama_client:
                self.event_bus.emit_status("AI service not available", "error")
                return None
            
            self.logger.debug(f"Sending chat message: {message[:50]}...")
            self.event_bus.emit_status("Processing AI response...", "info")
            
            # Format message for Ollama client - it expects a messages list format
            messages = [{"role": "user", "content": message}]
            # Ensure we get a non-streaming response (string or None)
            response = self.ollama_client.chat(model=model, messages=messages, stream=False)
            
            # Handle the response - it should be a string or None when stream=False
            if response and isinstance(response, str):
                self.logger.debug(f"Received AI response: {response[:50]}...")
                self.event_bus.emit_status("AI response received", "success", duration=2.0)
                return response
            else:
                self.event_bus.emit_status("No AI response received", "warning")
                return None
            
        except Exception as e:
            self.logger.error(f"Error in chat: {e}")
            self.event_bus.emit_status(f"AI chat error: {e}", "error")
            return None
    
    # State queries
    def is_microphone_active(self) -> bool:
        """Check if microphone is currently active."""
        return self._mic_active
    
    def is_system_audio_active(self) -> bool:
        """Check if system audio is currently active."""
        return self._system_active
    
    def get_target_language(self) -> str:
        """Get current target language."""
        return self._current_target_language
    
    # Cleanup
    def shutdown(self) -> None:
        """Shutdown all services and clean up resources."""
        try:
            self.logger.info("Shutting down UI services")
            
            # Stop any active streams
            if self._mic_active:
                self.stop_microphone()
            
            if self._system_active:
                self.stop_system_audio()
            
            # Shutdown pipeline manager
            if self._pipeline_manager:
                self._pipeline_manager.shutdown()
                self._pipeline_manager = None
            
            # Clean up other services
            self._ollama_client = None
            self._services_initialized = False
            
            self.event_bus.emit_status("Services shut down", "info")
            self.logger.info("UI services shutdown complete")
            
        except Exception as e:
            self.logger.error(f"Error during services shutdown: {e}")
            self.event_bus.emit_status(f"Shutdown error: {e}", "error")