#!/usr/bin/env python3
"""
TalkBridge - Custom Exception Hierarchy
=======================================

Structured exception hierarchy for the TalkBridge project.
Provides specific exception types for different error categories with
user-friendly messages and detailed error context.

Author: TalkBridge Team
Date: 2025-09-18
Version: 1.0

Exception Hierarchy:
    TalkBridgeError (base)
    ├── AudioCaptureError
    ├── STTError  
    ├── TTSError
    ├── TranslationError
    ├── UIError
    ├── PipelineError
    ├── ConfigurationError
    └── ServiceError
"""

from typing import Optional, Dict, Any
from enum import Enum

class ErrorSeverity(Enum):
    """Error severity levels for better categorization."""
    LOW = "low"           # Minor issues, continues operation
    MEDIUM = "medium"     # Affects functionality but recoverable
    HIGH = "high"         # Major functionality loss
    CRITICAL = "critical" # Application-breaking errors

class ErrorCategory(Enum):
    """Error categories for better organization."""
    HARDWARE = "hardware"         # Device/hardware related
    NETWORK = "network"           # Network connectivity issues
    SERVICE = "service"           # External service failures  
    CONFIGURATION = "config"      # Configuration problems
    USER_INPUT = "user_input"     # Invalid user input
    SYSTEM = "system"             # System/OS level issues
    PERMISSION = "permission"     # Permission/access issues

class TalkBridgeError(Exception):
    """
    Base exception class for all TalkBridge errors.
    
    Provides structured error information including severity, category,
    user-friendly messages, and technical details for logging.
    """
    
    def __init__(
        self, 
        message: str,
        user_message: Optional[str] = None,
        severity: ErrorSeverity = ErrorSeverity.MEDIUM,
        category: ErrorCategory = ErrorCategory.SYSTEM,
        error_code: Optional[str] = None,
        context: Optional[Dict[str, Any]] = None,
        recoverable: bool = True
    ):
        """
        Initialize TalkBridge error.
        
        Args:
            message: Technical error message for logging
            user_message: User-friendly message for UI display
            severity: Error severity level
            category: Error category
            error_code: Unique error code for tracking
            context: Additional error context data
            recoverable: Whether the error is recoverable
        """
        super().__init__(message)
        self.message = message
        self.user_message = user_message or self._generate_user_message()
        self.severity = severity
        self.category = category
        self.error_code = error_code or self._generate_error_code()
        self.context = context or {}
        self.recoverable = recoverable
        
    def _generate_user_message(self) -> str:
        """Generate a user-friendly message if not provided."""
        return "An error occurred. Please check the logs for details."
        
    def _generate_error_code(self) -> str:
        """Generate an error code based on the exception class."""
        class_name = self.__class__.__name__
        return f"TB_{class_name.upper()}"
        
    def to_dict(self) -> Dict[str, Any]:
        """Convert error to dictionary for serialization."""
        return {
            "error_type": self.__class__.__name__,
            "message": self.message,
            "user_message": self.user_message,
            "severity": self.severity.value,
            "category": self.category.value,
            "error_code": self.error_code,
            "context": self.context,
            "recoverable": self.recoverable
        }

class AudioCaptureError(TalkBridgeError):
    """Errors related to audio capture and recording."""
    
    def __init__(
        self,
        message: str,
        device_name: Optional[str] = None,
        **kwargs
    ):
        user_message = kwargs.pop('user_message', None)
        # Remove category from kwargs if present since we set it explicitly
        kwargs.pop('category', None)
        # Remove category from kwargs if present since we set it explicitly
        kwargs.pop('category', None)
        
        if not user_message:
            if device_name:
                user_message = f"Unable to access microphone '{device_name}'. Please check device permissions and availability."
            else:
                user_message = "Microphone access failed. Please check device permissions."
                
        super().__init__(
            message=message,
            user_message=user_message,
            category=ErrorCategory.HARDWARE,
            **kwargs
        )
        self.device_name = device_name
        if device_name:
            self.context["device_name"] = device_name
            
    def _generate_error_code(self) -> str:
        return "TB_AUDIO_CAPTURE_ERROR"

class AudioPlaybackError(AudioCaptureError):
    """Errors related to audio playback and output."""
    
    def __init__(self, message: str, **kwargs):
        user_message = kwargs.pop('user_message', "Audio playback failed. Please check speaker settings.")
        super().__init__(message, user_message=user_message, **kwargs)
        
    def _generate_error_code(self) -> str:
        return "TB_AUDIO_PLAYBACK_ERROR"

class STTError(TalkBridgeError):
    """Errors related to Speech-to-Text processing."""
    
    def __init__(
        self,
        message: str,
        model_name: Optional[str] = None,
        language: Optional[str] = None,
        **kwargs
    ):
        user_message = kwargs.pop('user_message', None)
        # Remove category from kwargs if present since we set it explicitly
        kwargs.pop('category', None)
        # Remove category from kwargs if present since we set it explicitly
        kwargs.pop('category', None)
        
        if not user_message:
            if model_name:
                user_message = f"Speech recognition failed with model '{model_name}'. Please try again."
            else:
                user_message = "Speech recognition failed. Please check your microphone and try again."
                
        super().__init__(
            message=message,
            user_message=user_message,
            category=ErrorCategory.SERVICE,
            **kwargs
        )
        self.model_name = model_name
        self.language = language
        if model_name:
            self.context["model_name"] = model_name
        if language:
            self.context["language"] = language
            
    def _generate_error_code(self) -> str:
        return "TB_STT_ERROR"

class TTSError(TalkBridgeError):
    """Errors related to Text-to-Speech processing."""
    
    def __init__(
        self,
        message: str,
        voice_name: Optional[str] = None,
        language: Optional[str] = None,
        **kwargs
    ):
        user_message = kwargs.pop('user_message', None)
        # Remove category from kwargs if present since we set it explicitly
        kwargs.pop('category', None)
        # Remove category from kwargs if present since we set it explicitly
        kwargs.pop('category', None)
        
        if not user_message:
            if voice_name:
                user_message = f"Text-to-speech failed with voice '{voice_name}'. Please try a different voice."
            else:
                user_message = "Text-to-speech generation failed. Please try again."
                
        super().__init__(
            message=message,
            user_message=user_message,
            category=ErrorCategory.SERVICE,
            **kwargs
        )
        self.voice_name = voice_name
        self.language = language
        if voice_name:
            self.context["voice_name"] = voice_name
        if language:
            self.context["language"] = language
            
    def _generate_error_code(self) -> str:
        return "TB_TTS_ERROR"

class TranslationError(TalkBridgeError):
    """Errors related to text translation."""
    
    def __init__(
        self,
        message: str,
        source_language: Optional[str] = None,
        target_language: Optional[str] = None,
        service_name: Optional[str] = None,
        **kwargs
    ):
        user_message = kwargs.pop('user_message', None)
        # Remove category from kwargs if present since we set it explicitly
        kwargs.pop('category', None)
        if not user_message:
            if source_language and target_language:
                user_message = f"Translation from {source_language} to {target_language} failed. Please try again."
            else:
                user_message = "Translation service is currently unavailable. Please try again later."
                
        super().__init__(
            message=message,
            user_message=user_message,
            category=ErrorCategory.SERVICE,
            **kwargs
        )
        self.source_language = source_language
        self.target_language = target_language
        self.service_name = service_name
        
        if source_language:
            self.context["source_language"] = source_language
        if target_language:
            self.context["target_language"] = target_language
        if service_name:
            self.context["service_name"] = service_name
            
    def _generate_error_code(self) -> str:
        return "TB_TRANSLATION_ERROR"

class UIError(TalkBridgeError):
    """Errors related to user interface components."""
    
    def __init__(
        self,
        message: str,
        component_name: Optional[str] = None,
        **kwargs
    ):
        user_message = kwargs.pop('user_message', None)
        # Remove category from kwargs if present since we set it explicitly
        kwargs.pop('category', None)
        if not user_message:
            if component_name:
                user_message = f"Interface component '{component_name}' encountered an error. Please refresh the application."
            else:
                user_message = "Interface error occurred. Please refresh the application."
                
        super().__init__(
            message=message,
            user_message=user_message,
            category=ErrorCategory.USER_INPUT,
            **kwargs
        )
        self.component_name = component_name
        if component_name:
            self.context["component_name"] = component_name
            
    def _generate_error_code(self) -> str:
        return "TB_UI_ERROR"

class PipelineError(TalkBridgeError):
    """Errors related to audio processing pipeline."""
    
    def __init__(
        self,
        message: str,
        pipeline_stage: Optional[str] = None,
        **kwargs
    ):
        user_message = kwargs.pop('user_message', None)
        # Remove category from kwargs if present since we set it explicitly
        kwargs.pop('category', None)
        if not user_message:
            if pipeline_stage:
                user_message = f"Audio processing failed at stage '{pipeline_stage}'. Please try again."
            else:
                user_message = "Audio processing pipeline failed. Please restart the application."
                
        super().__init__(
            message=message,
            user_message=user_message,
            category=ErrorCategory.SYSTEM,
            severity=ErrorSeverity.HIGH,
            **kwargs
        )
        self.pipeline_stage = pipeline_stage
        if pipeline_stage:
            self.context["pipeline_stage"] = pipeline_stage
            
    def _generate_error_code(self) -> str:
        return "TB_PIPELINE_ERROR"

class ConfigurationError(TalkBridgeError):
    """Errors related to application configuration."""
    
    def __init__(
        self,
        message: str,
        config_key: Optional[str] = None,
        config_file: Optional[str] = None,
        **kwargs
    ):
        user_message = kwargs.pop('user_message', None)
        # Remove category from kwargs if present since we set it explicitly
        kwargs.pop('category', None)
        if not user_message:
            if config_key:
                user_message = f"Configuration error: Invalid setting '{config_key}'. Please check your configuration."
            else:
                user_message = "Configuration error. Please check your settings and restart the application."
                
        super().__init__(
            message=message,
            user_message=user_message,
            category=ErrorCategory.CONFIGURATION,
            severity=ErrorSeverity.HIGH,
            recoverable=False,
            **kwargs
        )
        self.config_key = config_key
        self.config_file = config_file
        
        if config_key:
            self.context["config_key"] = config_key
        if config_file:
            self.context["config_file"] = config_file
            
    def _generate_error_code(self) -> str:
        return "TB_CONFIG_ERROR"

class ServiceError(TalkBridgeError):
    """Errors related to external services and dependencies."""
    
    def __init__(
        self,
        message: str,
        service_name: Optional[str] = None,
        service_url: Optional[str] = None,
        **kwargs
    ):
        user_message = kwargs.pop('user_message', None)
        # Remove category from kwargs if present since we set it explicitly
        kwargs.pop('category', None)
        if not user_message:
            if service_name:
                user_message = f"Service '{service_name}' is currently unavailable. Please check your connection and try again."
            else:
                user_message = "External service is currently unavailable. Please try again later."
                
        super().__init__(
            message=message,
            user_message=user_message,
            category=ErrorCategory.NETWORK,
            **kwargs
        )
        self.service_name = service_name
        self.service_url = service_url
        
        if service_name:
            self.context["service_name"] = service_name
        if service_url:
            self.context["service_url"] = service_url
            
    def _generate_error_code(self) -> str:
        return "TB_SERVICE_ERROR"

class DeviceError(AudioCaptureError):
    """Errors related to hardware devices (microphones, speakers, cameras)."""
    
    def __init__(
        self,
        message: str,
        device_type: Optional[str] = None,
        device_id: Optional[str] = None,
        **kwargs
    ):
        user_message = kwargs.pop('user_message', None)
        # Remove category from kwargs if present since we set it explicitly
        kwargs.pop('category', None)
        if not user_message:
            if device_type:
                user_message = f"{device_type.title()} device not found or inaccessible. Please check connections and permissions."
            else:
                user_message = "Device not found or inaccessible. Please check connections and permissions."
                
        super().__init__(
            message=message,
            user_message=user_message,
            category=ErrorCategory.HARDWARE,
            **kwargs
        )
        self.device_type = device_type
        self.device_id = device_id
        
        if device_type:
            self.context["device_type"] = device_type
        if device_id:
            self.context["device_id"] = device_id
            
    def _generate_error_code(self) -> str:
        return "TB_DEVICE_ERROR"

class NetworkError(ServiceError):
    """Errors related to network connectivity and communication."""
    
    def __init__(self, message: str, **kwargs):
        user_message = kwargs.pop('user_message', "Network connection failed. Please check your internet connection.")
        super().__init__(
            message,
            user_message=user_message,
            category=ErrorCategory.NETWORK,
            **kwargs
        )
        
    def _generate_error_code(self) -> str:
        return "TB_NETWORK_ERROR"

class PermissionError(TalkBridgeError):
    """Errors related to permissions and access rights."""
    
    def __init__(
        self,
        message: str,
        resource_type: Optional[str] = None,
        **kwargs
    ):
        user_message = kwargs.pop('user_message', None)
        # Remove category from kwargs if present since we set it explicitly
        kwargs.pop('category', None)
        if not user_message:
            if resource_type:
                user_message = f"Permission denied for {resource_type}. Please grant the necessary permissions."
            else:
                user_message = "Permission denied. Please grant the necessary permissions and restart the application."
                
        super().__init__(
            message=message,
            user_message=user_message,
            category=ErrorCategory.PERMISSION,
            severity=ErrorSeverity.HIGH,
            **kwargs
        )
        self.resource_type = resource_type
        if resource_type:
            self.context["resource_type"] = resource_type
            
    def _generate_error_code(self) -> str:
        return "TB_PERMISSION_ERROR"

# Convenience functions for creating common errors

def create_audio_capture_error(
    message: str,
    device_name: Optional[str] = None,
    **kwargs
) -> AudioCaptureError:
    """Create an audio capture error with common defaults."""
    return AudioCaptureError(message, device_name=device_name, **kwargs)

def create_stt_error(
    message: str,
    model_name: Optional[str] = None,
    **kwargs
) -> STTError:
    """Create an STT error with common defaults."""
    return STTError(message, model_name=model_name, **kwargs)

def create_tts_error(
    message: str,
    voice_name: Optional[str] = None,
    **kwargs
) -> TTSError:
    """Create a TTS error with common defaults.""" 
    return TTSError(message, voice_name=voice_name, **kwargs)

def create_translation_error(
    message: str,
    source_lang: Optional[str] = None,
    target_lang: Optional[str] = None,
    **kwargs
) -> TranslationError:
    """Create a translation error with common defaults."""
    return TranslationError(
        message,
        source_language=source_lang,
        target_language=target_lang,
        **kwargs
    )

def create_ui_error(
    message: str,
    component: Optional[str] = None,
    **kwargs
) -> UIError:
    """Create a UI error with common defaults."""
    return UIError(message, component_name=component, **kwargs)

def create_pipeline_error(
    message: str,
    stage: Optional[str] = None,
    **kwargs
) -> PipelineError:
    """Create a pipeline error with common defaults."""
    return PipelineError(message, pipeline_stage=stage, **kwargs)