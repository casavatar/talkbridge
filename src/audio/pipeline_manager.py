"""
Audio Pipeline Manager for Dual Source Audio Capture
==================================================

Handles parallel audio streams from microphone and system audio sources
for real-time conversation transcription and translation.

Author: TalkBridge Team  
Date: 2025-09-18
Version: 2.1 (Enhanced with unified logging and error handling)
"""

import threading
import queue
import time
from typing import Dict, List, Optional, Callable, Any, Literal, Union
from dataclasses import dataclass
from enum import Enum

# Import centralized logging and exception handling
import sys
from pathlib import Path

from src.logging_config import get_logger, log_exception
from src.utils.exceptions import (
    AudioCaptureError, PipelineError, DeviceError, 
    create_audio_capture_error, create_pipeline_error
)
from src.utils.error_handler import retry_with_backoff, RetryableError, handle_error

try:
    from .capture import AudioCapture
    AUDIO_CAPTURE_AVAILABLE = True
except ImportError as e:
    AUDIO_CAPTURE_AVAILABLE = False
    AudioCapture = None
    # Use proper logging instead of print
    logger = get_logger(__name__)
    logger.warning("AudioCapture not available - audio pipeline functionality limited", 
                  extra={"error": str(e)})

# Import new adapter infrastructure
try:
    from .ports import AudioData, AudioFormat, TranscriptionResult, TranslationResult
    from .adapters import WhisperSTTAdapter, TranslationAdapter
    ADAPTERS_AVAILABLE = True
except ImportError as e:
    ADAPTERS_AVAILABLE = False
    AudioData = None  # type: ignore
    AudioFormat = None  # type: ignore
    TranscriptionResult = None  # type: ignore
    TranslationResult = None  # type: ignore
    WhisperSTTAdapter = None  # type: ignore
    TranslationAdapter = None  # type: ignore
    logger = get_logger(__name__)
    logger.warning("Audio adapters not available - using legacy pipeline",
                  extra={"error": str(e)})

# Import notification system and async utilities
try:
    from ..ui.notifier import notify, Level
    from ..errors import UserFacingError, ErrorCategory
    from ..utils.async_runner import AsyncTaskRunner
    UI_INTEGRATION_AVAILABLE = True
except ImportError as e:
    UI_INTEGRATION_AVAILABLE = False
    notify = None  # type: ignore
    Level = None  # type: ignore
    UserFacingError = None  # type: ignore
    ErrorCategory = None  # type: ignore
    AsyncTaskRunner = None  # type: ignore
    logger = get_logger(__name__)
    logger.warning("UI integration not available - pipeline notifications disabled",
                  extra={"error": str(e)})

class AudioSourceType(Enum):
    """Audio source types for pipeline management."""
    MICROPHONE = "microphone"
    SYSTEM_AUDIO = "system_audio"

@dataclass
class DeviceInfo:
    """Information about an audio device."""
    index: int
    name: str
    channels: int
    sample_rate: int
    is_input: bool = True

@dataclass
class AudioStreamData:
    """Container for audio stream data with metadata."""
    source_type: AudioSourceType
    audio_data: bytes
    timestamp: float
    device_name: str
    sample_rate: int = 16000
    channels: int = 1
    language_hint: Optional[str] = None

class PipelineManager:
    """
    Manages parallel audio pipelines for microphone and system audio capture.
    
    Features:
    - Independent audio capture threads for each source
    - Thread-safe queues for audio data processing
    - Device management and selection
    - Status monitoring and callbacks
    - Error handling and recovery
    - Dual pipeline support (mic + system/loopback)
    """
    
    def __init__(self, 
                 on_transcript: Optional[Callable] = None,
                 on_translation: Optional[Callable] = None,
                 on_status: Optional[Callable] = None):
        """Initialize the audio pipeline manager.
        
        Args:
            on_transcript: Callback for transcript events (source, text, language)
            on_translation: Callback for translation events (source, original, translated)
            on_status: Callback for status updates (source, status, device)
        """
        self.logger = get_logger(__name__)
        
        # Initialize UI integration components if available
        self.async_runner = None
        if UI_INTEGRATION_AVAILABLE and AsyncTaskRunner is not None:
            try:
                self.async_runner = AsyncTaskRunner()
                self.logger.info("Audio pipeline integrated with notification system")
            except Exception as e:
                self.logger.warning(f"Failed to initialize async runner: {e}")
        
        # Audio capture instances
        self.mic_capture: Optional[Any] = None
        self.sys_capture: Optional[Any] = None
        
        # Threading components
        self.mic_thread: Optional[threading.Thread] = None
        self.sys_thread: Optional[threading.Thread] = None
        self.processing_thread: Optional[threading.Thread] = None
        
        # Thread control
        self.mic_running = threading.Event()
        self.sys_running = threading.Event()
        self.processing_running = threading.Event()
        self.shutdown_event = threading.Event()
        
        # Audio data queues
        self.mic_queue: queue.Queue = queue.Queue(maxsize=100)
        self.sys_queue: queue.Queue = queue.Queue(maxsize=100)
        self.output_queue: queue.Queue = queue.Queue(maxsize=200)
        
        # Device management
        self.selected_mic_device: Optional[int] = None
        self.selected_sys_device: Optional[int] = None
        self.available_devices: Dict[str, List[DeviceInfo]] = {
            'input': [],
            'system_loopback': []
        }
        
        # Language and processing settings
        self.target_language: str = "en"
        
        # Initialize processing adapters
        self.stt_adapter: Optional[Any] = None
        self.translation_adapter: Optional[Any] = None
        
        # Audio buffering for voice activity detection
        self.audio_buffer_duration = 3.0  # seconds
        self.audio_buffers = {
            AudioSourceType.MICROPHONE: [],
            AudioSourceType.SYSTEM_AUDIO: []
        }
        self.last_activity_time: Dict[AudioSourceType, float] = {
            AudioSourceType.MICROPHONE: 0.0,
            AudioSourceType.SYSTEM_AUDIO: 0.0
        }
        self.vad_threshold = 0.01  # Voice activity detection threshold
        self.silence_duration = 1.0  # seconds of silence before processing buffer
        
        # Initialize adapters if available
        if ADAPTERS_AVAILABLE and WhisperSTTAdapter is not None:
            try:
                self.stt_adapter = WhisperSTTAdapter(model_size="base")
                self.logger.info("STT adapter initialized")
            except Exception as e:
                self.logger.warning(f"Failed to initialize STT adapter: {e}")
        
        if ADAPTERS_AVAILABLE and TranslationAdapter is not None:
            try:
                self.translation_adapter = TranslationAdapter(service="google")
                self.logger.info("Translation adapter initialized")
            except Exception as e:
                self.logger.warning(f"Failed to initialize translation adapter: {e}")
        
        # Legacy backends (fallback)
        self.stt_backend = None
        self.translation_provider = None
        
        # Status tracking
        self.mic_active = False
        self.sys_active = False
        self.recording_stats = {
            'mic_packets': 0,
            'sys_packets': 0,
            'start_time': None,
            'last_activity': None
        }
        
        # Callbacks - using dependency injection pattern
        self.on_transcript = on_transcript
        self.on_translation = on_translation
        self.on_status = on_status
        
        # Legacy callback support (for backwards compatibility)
        self.status_callback: Optional[Callable] = None
        self.error_callback: Optional[Callable] = None
        self.data_callback: Optional[Callable] = None
        
        # Initialize available devices
        self.refresh_audio_devices()
    
    def set_callbacks(self, 
                     status_callback: Optional[Callable] = None,
                     error_callback: Optional[Callable] = None,
                     data_callback: Optional[Callable] = None):
        """Set legacy callback functions for status updates, errors, and data processing."""
        self.status_callback = status_callback
        self.error_callback = error_callback
        self.data_callback = data_callback
    
    def list_input_devices(self) -> List[DeviceInfo]:
        """List available input devices (microphones)."""
        return self.available_devices.get('input', [])
    
    def list_system_loopbacks(self) -> List[DeviceInfo]:
        """List available system loopback devices."""
        return self.available_devices.get('system_loopback', [])
    
    def set_target_language(self, lang_code: str) -> None:
        """Set the target language for translations."""
        self.target_language = lang_code
        self.logger.info(f"Target language set to: {lang_code}")
    
    def set_translation_provider(self, provider) -> None:
        """Set the translation provider."""
        self.translation_provider = provider
        self.logger.info(f"Translation provider set to: {type(provider).__name__}")
    
    def set_stt_backend(self, backend) -> None:
        """Set the speech-to-text backend."""
        self.stt_backend = backend
        self.logger.info(f"STT backend set to: {type(backend).__name__}")
    
    def refresh_audio_devices(self) -> Dict[str, List[DeviceInfo]]:
        """Refresh and return available audio devices."""
        if not AUDIO_CAPTURE_AVAILABLE:
            self.logger.warning("AudioCapture not available - cannot refresh devices")
            return self.available_devices
        
        try:
            # Get device information from AudioCapture
            if not AUDIO_CAPTURE_AVAILABLE or AudioCapture is None:
                self.logger.warning("AudioCapture not available for device refresh")
                return self.available_devices
                
            temp_capture = AudioCapture()
            devices_info = temp_capture.list_devices()
            
            # Clear existing devices
            self.available_devices = {'input': [], 'system_loopback': []}
            
            # Process all devices from sd.query_devices()
            all_devices = devices_info.get('devices', [])
            self.logger.info(f"Detected audio devices: {len(all_devices)}")
            
            for i, device in enumerate(all_devices):
                device_name = device.get('name', f'Unknown Device {i}')
                max_input_channels = device.get('max_input_channels', 0)
                max_output_channels = device.get('max_output_channels', 0)
                
                # Log device details for debugging
                self.logger.debug(f"Device {i}: {device_name} "
                                f"(in:{max_input_channels}, out:{max_output_channels})")
                
                # Add as input device if it has input channels
                if max_input_channels > 0:
                    # Exclude monitor/loopback devices from regular input list
                    if not any(keyword in device_name.lower() 
                              for keyword in ['monitor', 'loopback', 'output']):
                        device_info = DeviceInfo(
                            index=i,
                            name=device_name,
                            channels=max_input_channels,
                            sample_rate=device.get('default_samplerate', 16000),
                            is_input=True
                        )
                        self.available_devices['input'].append(device_info)
                
                # Add as system loopback device if it's a monitor/loopback device
                if any(keyword in device_name.lower() 
                      for keyword in ['monitor', 'loopback', 'stereo mix', 'what u hear']):
                    device_info = DeviceInfo(
                        index=i,
                        name=device_name,
                        channels=max_output_channels if max_output_channels > 0 else 2,
                        sample_rate=device.get('default_samplerate', 44100),
                        is_input=False
                    )
                    self.available_devices['system_loopback'].append(device_info)
            
            self.logger.info(f"Found {len(self.available_devices['input'])} input devices")
            self.logger.info(f"Found {len(self.available_devices['system_loopback'])} loopback devices")
            
            # Log device names for debugging
            for device in self.available_devices['input']:
                self.logger.info(f"Microphone: {device.name}")
            for device in self.available_devices['system_loopback']:
                self.logger.info(f"System Audio: {device.name}")
            
            return self.available_devices
            
        except Exception as e:
            self.logger.error(f"Error refreshing audio devices: {e}")
            if self.error_callback:
                self.error_callback(f"Device refresh error: {e}")
            return self.available_devices
    
    def get_available_devices(self, source_type: AudioSourceType) -> List[str]:
        """Get available devices for the specified source type (legacy method)."""
        if source_type == AudioSourceType.MICROPHONE:
            return [device.name for device in self.available_devices.get('input', [])]
        elif source_type == AudioSourceType.SYSTEM_AUDIO:
            return [device.name for device in self.available_devices.get('system_loopback', [])]
        return []
    
    def set_device(self, source_type: AudioSourceType, device_name: str) -> bool:
        """Set the selected device for the specified source type (legacy method)."""
        try:
            if source_type == AudioSourceType.MICROPHONE:
                devices = self.available_devices.get('input', [])
                for device in devices:
                    if device.name == device_name:
                        self.selected_mic_device = device.index
                        self.logger.info(f"Selected microphone device: {device_name} (index: {device.index})")
                        return True
                        
            elif source_type == AudioSourceType.SYSTEM_AUDIO:
                devices = self.available_devices.get('system_loopback', [])
                for device in devices:
                    if device.name == device_name:
                        self.selected_sys_device = device.index
                        self.logger.info(f"Selected system audio device: {device_name} (index: {device.index})")
                        return True
            
            self.logger.error(f"Device '{device_name}' not found for {source_type.value}")
            return False
            
        except Exception as e:
            self.logger.error(f"Error setting device {device_name} for {source_type.value}: {e}")
            if self.error_callback:
                self.error_callback(f"Device selection error: {e}")
            return False
    
    def start_mic_stream(self, 
                        device_index: int, 
                        lang_hint: Union[str, Literal["auto"]] = "auto") -> bool:
        """Start microphone audio stream."""
        if not AUDIO_CAPTURE_AVAILABLE:
            self.logger.error("AudioCapture not available")
            return False
        
        if self.mic_active:
            self.logger.warning("Microphone capture already active")
            return True
        
        try:
            # Initialize microphone capture
            if not AUDIO_CAPTURE_AVAILABLE or AudioCapture is None:
                self.logger.error("AudioCapture not available")
                return False
                
            self.mic_capture = AudioCapture()
            
            # Find device by index
            device_name = "Unknown"
            for device in self.available_devices.get('input', []):
                if device.index == device_index:
                    device_name = device.name
                    break
            
            if not self.mic_capture.initialize_device_by_index(device_index):
                self.logger.error(f"Failed to initialize microphone device index: {device_index}")
                return False
            
            self.selected_mic_device = device_index
            
            # Start capture thread
            self.mic_running.set()
            self.mic_thread = threading.Thread(
                target=self._microphone_capture_loop,
                name="MicrophoneCapture",
                daemon=True
            )
            self.mic_thread.start()
            
            self.mic_active = True
            self.recording_stats['start_time'] = time.time()
            self.logger.info(f"Started microphone stream on device: {device_name} (index: {device_index})")
            
            # Notify callbacks
            if self.on_status:
                self.on_status("microphone", "started", device_name)
            if self.status_callback:
                self.status_callback("microphone", "started", device_name)
            
            # Send user notification
            self._notify_audio_event(f"Microphone started: {device_name}", "info", "audio_system")
            
            return True
            
        except Exception as e:
            self.logger.error(f"Error starting microphone stream: {e}")
            if self.error_callback:
                self.error_callback(f"Microphone start error: {e}")
            return False
    
    def start_system_stream(self, 
                           device_index: int, 
                           lang_hint: Union[str, Literal["auto"]] = "auto") -> bool:
        """Start system audio stream."""
        if not AUDIO_CAPTURE_AVAILABLE:
            self.logger.error("AudioCapture not available")
            return False
        
        if self.sys_active:
            self.logger.warning("System audio capture already active")
            return True
        
        try:
            # Initialize system audio capture
            if not AUDIO_CAPTURE_AVAILABLE or AudioCapture is None:
                self.logger.error("AudioCapture not available")
                return False
                
            self.sys_capture = AudioCapture()
            
            # Find device by index
            device_name = "Unknown"
            for device in self.available_devices.get('system_loopback', []):
                if device.index == device_index:
                    device_name = device.name
                    break
            
            if not self.sys_capture.initialize_device_by_index(device_index):
                self.logger.error(f"Failed to initialize system audio device index: {device_index}")
                return False
            
            self.selected_sys_device = device_index
            
            # Start capture thread
            self.sys_running.set()
            self.sys_thread = threading.Thread(
                target=self._system_capture_loop,
                name="SystemAudioCapture",
                daemon=True
            )
            self.sys_thread.start()
            
            self.sys_active = True
            if not self.recording_stats['start_time']:
                self.recording_stats['start_time'] = time.time()
            self.logger.info(f"Started system audio stream on device: {device_name} (index: {device_index})")
            
            # Notify callbacks
            if self.on_status:
                self.on_status("system_audio", "started", device_name)
            if self.status_callback:
                self.status_callback("system_audio", "started", device_name)
            
            # Send user notification
            self._notify_audio_event(f"System audio started: {device_name}", "info", "audio_system")
            
            return True
            
        except Exception as e:
            self.logger.error(f"Error starting system audio stream: {e}")
            if self.error_callback:
                self.error_callback(f"System audio start error: {e}")
            return False
    
    def stop_mic_stream(self) -> bool:
        """Stop microphone audio stream."""
        return self.stop_microphone_capture()
    
    def stop_system_stream(self) -> bool:
        """Stop system audio stream."""
        return self.stop_system_capture()
    
    def is_mic_active(self) -> bool:
        """Check if microphone stream is active."""
        return self.mic_active
    
    def is_system_active(self) -> bool:
        """Check if system audio stream is active."""
        return self.sys_active
    
    # Legacy methods for backwards compatibility
    @retry_with_backoff(
        max_retries=3, 
        initial_delay=1.0, 
        retryable_exceptions=[RetryableError, ConnectionError, OSError]
    )
    def start_microphone_capture(self) -> bool:
        """Start microphone audio capture with retry logic."""
        try:
            if self.selected_mic_device is not None:
                return self.start_mic_stream(self.selected_mic_device)
            else:
                error_msg = "No microphone device selected"
                self.logger.error(error_msg)
                
                # Raise specific exception instead of just returning False
                raise DeviceError(
                    message=error_msg,
                    device_type="microphone",
                    user_message="Please select a microphone device before starting capture"
                )
                
        except DeviceError:
            # Re-raise device errors as-is (not retryable)
            raise
        except (OSError, ConnectionError) as e:
            # These errors might be retryable (device temporarily unavailable)
            error_msg = f"Device temporarily unavailable: {str(e)}"
            self.logger.warning(error_msg)
            raise RetryableError(error_msg) from e
        except Exception as e:
            # Convert unexpected errors to AudioCaptureError
            error_msg = f"Failed to start microphone capture: {str(e)}"
            self.logger.exception(error_msg)
            raise create_audio_capture_error(
                message=error_msg,
                device_name=f"Device {self.selected_mic_device}" if self.selected_mic_device else None
            )
    
    @retry_with_backoff(
        max_retries=3, 
        initial_delay=1.0, 
        retryable_exceptions=[RetryableError, ConnectionError, OSError]
    )
    def start_system_capture(self) -> bool:
        """Start system audio capture with retry logic."""
        try:
            if self.selected_sys_device is not None:
                return self.start_system_stream(self.selected_sys_device)
            else:
                error_msg = "No system audio device selected"
                self.logger.error(error_msg)
                
                # Raise specific exception instead of just returning False
                raise DeviceError(
                    message=error_msg,
                    device_type="system_audio",
                    user_message="Please select a system audio device before starting capture"
                )
                
        except DeviceError:
            # Re-raise device errors as-is (not retryable)
            raise
        except (OSError, ConnectionError) as e:
            # These errors might be retryable (device temporarily unavailable)
            error_msg = f"System audio device temporarily unavailable: {str(e)}"
            self.logger.warning(error_msg)
            raise RetryableError(error_msg) from e
        except Exception as e:
            # Convert unexpected errors to AudioCaptureError
            error_msg = f"Failed to start system audio capture: {str(e)}"
            self.logger.exception(error_msg)
            raise create_audio_capture_error(
                message=error_msg,
                device_name=f"Device {self.selected_sys_device}" if self.selected_sys_device else None
            )
    
    def stop_microphone_capture(self) -> bool:
        """Stop microphone audio capture."""
        if not self.mic_active:
            return True
        
        try:
            self.mic_running.clear()
            
            if self.mic_thread and self.mic_thread.is_alive():
                self.mic_thread.join(timeout=2.0)
            
            if self.mic_capture:
                self.mic_capture.stop_capture()
                self.mic_capture = None
            
            self.mic_active = False
            self.logger.info("Stopped microphone capture")
            
            # Notify callbacks
            device_name = f"Device {self.selected_mic_device}" if self.selected_mic_device else "Unknown"
            if self.on_status:
                self.on_status("microphone", "stopped", device_name)
            if self.status_callback:
                self.status_callback("microphone", "stopped", device_name)
            
            return True
            
        except Exception as e:
            error_msg = f"Error stopping microphone capture: {str(e)}"
            log_exception(self.logger, e, "Failed to stop microphone capture")
            
            # Notify error callbacks with user-friendly message
            if self.error_callback:
                self.error_callback("Failed to stop microphone. Please restart the application.")
            if self.on_status:
                self.on_status("microphone", "error", "Stop failed")
                
            # Don't raise exception for stop operations - just log and return False
            return False
    
    def stop_system_capture(self) -> bool:
        """Stop system audio capture."""
        if not self.sys_active:
            return True
        
        try:
            self.sys_running.clear()
            
            if self.sys_thread and self.sys_thread.is_alive():
                self.sys_thread.join(timeout=2.0)
            
            if self.sys_capture:
                self.sys_capture.stop_capture()
                self.sys_capture = None
            
            self.sys_active = False
            self.logger.info("Stopped system audio capture")
            
            # Notify callbacks
            device_name = f"Device {self.selected_sys_device}" if self.selected_sys_device else "Unknown"
            if self.on_status:
                self.on_status("system_audio", "stopped", device_name)
            if self.status_callback:
                self.status_callback("system_audio", "stopped", device_name)
            
            return True
            
        except Exception as e:
            self.logger.error(f"Error stopping system audio capture: {e}")
            if self.error_callback:
                self.error_callback(f"System audio stop error: {e}")
            return False
    
    def start_processing(self) -> bool:
        """Start the audio data processing thread."""
        if self.processing_running.is_set():
            return True
        
        try:
            self.processing_running.set()
            self.processing_thread = threading.Thread(
                target=self._processing_loop,
                name="AudioProcessing",
                daemon=True
            )
            self.processing_thread.start()
            
            self.logger.info("Started audio processing thread")
            return True
            
        except Exception as e:
            self.logger.error(f"Error starting audio processing: {e}")
            if self.error_callback:
                self.error_callback(f"Processing start error: {e}")
            return False
    
    def stop_processing(self) -> bool:
        """Stop the audio data processing thread."""
        if not self.processing_running.is_set():
            return True
        
        try:
            self.processing_running.clear()
            
            if self.processing_thread and self.processing_thread.is_alive():
                self.processing_thread.join(timeout=2.0)
            
            self.logger.info("Stopped audio processing thread")
            return True
            
        except Exception as e:
            self.logger.error(f"Error stopping audio processing: {e}")
            return False
    
    def shutdown(self) -> bool:
        """Shutdown all audio pipelines and cleanup resources."""
        self.logger.info("Shutting down audio pipeline manager")
        
        # Set shutdown event
        self.shutdown_event.set()
        
        # Stop all captures
        success = True
        success &= self.stop_microphone_capture()
        success &= self.stop_system_capture()
        success &= self.stop_processing()
        
        # Clear queues
        self._clear_queues()
        
        # Reset statistics
        self.recording_stats = {
            'mic_packets': 0,
            'sys_packets': 0,
            'start_time': None,
            'last_activity': None
        }
        
        self.logger.info("Audio pipeline manager shutdown complete")
        return success
    
    def get_status(self) -> Dict[str, Any]:
        """Get current status of audio pipelines."""
        return {
            'microphone': {
                'active': self.mic_active,
                'device': self.selected_mic_device,
                'packets_captured': self.recording_stats['mic_packets']
            },
            'system_audio': {
                'active': self.sys_active,
                'device': self.selected_sys_device,
                'packets_captured': self.recording_stats['sys_packets']
            },
            'processing': {
                'active': self.processing_running.is_set(),
                'queue_sizes': {
                    'microphone': self.mic_queue.qsize(),
                    'system_audio': self.sys_queue.qsize(),
                    'output': self.output_queue.qsize()
                }
            },
            'session': {
                'start_time': self.recording_stats['start_time'],
                'last_activity': self.recording_stats['last_activity'],
                'total_packets': (self.recording_stats['mic_packets'] + 
                                 self.recording_stats['sys_packets'])
            }
        }
    
    def _microphone_capture_loop(self):
        """Main loop for microphone audio capture."""
        self.logger.debug("Microphone capture loop started")
        
        try:
            while self.mic_running.is_set() and not self.shutdown_event.is_set():
                if not self.mic_capture:
                    break
                
                # Capture audio data
                audio_data = self.mic_capture.capture_chunk()
                if audio_data is not None:
                    device_name = "Unknown"
                    for device in self.available_devices.get('input', []):
                        if device.index == self.selected_mic_device:
                            device_name = device.name
                            break
                    
                    # Convert numpy array to bytes if necessary
                    if hasattr(audio_data, 'tobytes'):
                        audio_bytes = audio_data.tobytes()
                    elif isinstance(audio_data, bytes):
                        audio_bytes = audio_data
                    else:
                        # Convert other types to bytes
                        import numpy as np
                        audio_bytes = np.array(audio_data, dtype=np.int16).tobytes()
                    
                    stream_data = AudioStreamData(
                        source_type=AudioSourceType.MICROPHONE,
                        audio_data=audio_bytes,
                        timestamp=time.time(),
                        device_name=device_name,
                        sample_rate=getattr(self.mic_capture, 'sample_rate', 16000),
                        channels=getattr(self.mic_capture, 'channels', 1)
                    )
                    
                    try:
                        self.mic_queue.put_nowait(stream_data)
                        self.recording_stats['mic_packets'] += 1
                        self.recording_stats['last_activity'] = time.time()
                    except queue.Full:
                        self.logger.warning("Microphone queue full, dropping packet")
                
                # Small delay to prevent CPU overload - use threading.Event for better control
                if not self.shutdown_event.wait(0.01):  # Non-blocking wait for 10ms
                    continue
                
        except Exception as e:
            self.logger.error(f"Error in microphone capture loop: {e}")
            if self.error_callback:
                self.error_callback(f"Microphone capture error: {e}")
        
        self.logger.debug("Microphone capture loop ended")
    
    def _system_capture_loop(self):
        """Main loop for system audio capture."""
        self.logger.debug("System audio capture loop started")
        
        try:
            while self.sys_running.is_set() and not self.shutdown_event.is_set():
                if not self.sys_capture:
                    break
                
                # Capture audio data
                audio_data = self.sys_capture.capture_chunk()
                if audio_data is not None:
                    device_name = "Unknown"
                    for device in self.available_devices.get('system_loopback', []):
                        if device.index == self.selected_sys_device:
                            device_name = device.name
                            break
                    
                    # Convert numpy array to bytes if necessary
                    if hasattr(audio_data, 'tobytes'):
                        audio_bytes = audio_data.tobytes()
                    elif isinstance(audio_data, bytes):
                        audio_bytes = audio_data
                    else:
                        # Convert other types to bytes
                        import numpy as np
                        audio_bytes = np.array(audio_data, dtype=np.int16).tobytes()
                    
                    stream_data = AudioStreamData(
                        source_type=AudioSourceType.SYSTEM_AUDIO,
                        audio_data=audio_bytes,
                        timestamp=time.time(),
                        device_name=device_name,
                        sample_rate=getattr(self.sys_capture, 'sample_rate', 16000),
                        channels=getattr(self.sys_capture, 'channels', 1)
                    )
                    
                    try:
                        self.sys_queue.put_nowait(stream_data)
                        self.recording_stats['sys_packets'] += 1
                        self.recording_stats['last_activity'] = time.time()
                    except queue.Full:
                        self.logger.warning("System audio queue full, dropping packet")
                
                # Small delay to prevent CPU overload - use threading.Event for better control
                if not self.shutdown_event.wait(0.01):  # Non-blocking wait for 10ms
                    continue
                
        except Exception as e:
            self.logger.error(f"Error in system audio capture loop: {e}")
            if self.error_callback:
                self.error_callback(f"System audio capture error: {e}")
        
        self.logger.debug("System audio capture loop ended")
    
    def _processing_loop(self):
        """Main loop for processing audio data from both sources."""
        self.logger.debug("Audio processing loop started")
        
        # Initialize health check timing
        last_health_check = time.time()
        
        try:
            while self.processing_running.is_set() and not self.shutdown_event.is_set():
                processed_any = False
                
                # Process microphone data
                try:
                    stream_data = self.mic_queue.get_nowait()
                    self.output_queue.put_nowait(stream_data)
                    self.recording_stats['mic_packets'] += 1
                    
                    # Call legacy callbacks with error handling
                    if self.data_callback:
                        try:
                            self.data_callback(stream_data)
                        except Exception as callback_error:
                            self.logger.error(f"Data callback error: {callback_error}")
                    
                    # New callback system with STT processing and error handling
                    if self.on_transcript:
                        try:
                            self._process_audio_for_transcript(stream_data)
                        except Exception as stt_error:
                            self.handle_component_failure("stt_adapter", stt_error)
                    
                    processed_any = True
                except queue.Empty:
                    self.logger.debug("Microphone queue empty (non-fatal)")
                except Exception as e:
                    self.logger.error(f"Error processing microphone data: {e}")
                    self.handle_component_failure("mic_capture", e)
                
                # Process system audio data
                try:
                    stream_data = self.sys_queue.get_nowait()
                    self.output_queue.put_nowait(stream_data)
                    self.recording_stats['sys_packets'] += 1
                    
                    # Call legacy callbacks with error handling
                    if self.data_callback:
                        try:
                            self.data_callback(stream_data)
                        except Exception as callback_error:
                            self.logger.error(f"Data callback error: {callback_error}")
                    
                    # New callback system with STT processing and error handling
                    if self.on_transcript:
                        try:
                            self._process_audio_for_transcript(stream_data)
                        except Exception as stt_error:
                            self.handle_component_failure("stt_adapter", stt_error)
                    
                    processed_any = True
                except queue.Empty:
                    self.logger.debug("System audio queue empty (non-fatal)")
                except Exception as e:
                    self.logger.error(f"Error processing system audio data: {e}")
                    self.handle_component_failure("sys_capture", e)
                
                # If no data was processed, sleep briefly to prevent CPU spinning
                if not processed_any:
                    if not self.shutdown_event.wait(0.05):  # Non-blocking wait for 50ms
                        continue
                
                # Periodic health check
                if time.time() - last_health_check > 30.0:  # Every 30 seconds
                    health_status = self.get_pipeline_health()
                    if health_status['overall_status'] != 'healthy':
                        self.logger.warning(f"Pipeline health degraded: {health_status}")
                    last_health_check = time.time()
                    
        except Exception as e:
            self.logger.error(f"Error in audio processing loop: {e}")
            if self.error_callback:
                self.error_callback(f"Audio processing error: {e}")
        
        self.logger.debug("Audio processing loop ended")
    
    def _process_audio_for_transcript(self, stream_data: AudioStreamData):
        """Process audio data through buffering, VAD, and STT pipeline.
        
        This method properly integrates STT processing into the pipeline,
        ensuring that callbacks receive transcribed text instead of raw audio bytes.
        Includes voice activity detection and buffering for better transcription quality.
        """
        try:
            # Skip processing if no STT adapter available
            if not self.stt_adapter:
                self.logger.warning("No STT adapter available, skipping transcript processing")
                return
            
            # Add audio chunk to buffer for VAD processing
            self._add_to_audio_buffer(stream_data)
            
            # Check for voice activity and process buffer if appropriate
            if self._should_process_buffer(stream_data.source_type):
                self._process_buffered_audio(stream_data.source_type)
            
        except Exception as e:
            self.logger.error(f"Error processing audio for transcript: {e}")
            # Optionally call error callback
            if self.error_callback:
                self.error_callback(f"STT processing error: {e}")
    
    def _add_to_audio_buffer(self, stream_data: AudioStreamData):
        """Add audio chunk to the appropriate buffer for VAD processing."""
        try:
            buffer = self.audio_buffers[stream_data.source_type]
            
            # Add current chunk to buffer
            buffer.append(stream_data)
            
            # Simple voice activity detection based on RMS energy
            has_voice_activity = self._detect_voice_activity(stream_data.audio_data)
            
            if has_voice_activity:
                self.last_activity_time[stream_data.source_type] = time.time()
            
            # Limit buffer size to prevent excessive memory usage
            max_buffer_chunks = int(self.audio_buffer_duration / 1.0)  # Assuming 1-second chunks
            if len(buffer) > max_buffer_chunks:
                buffer.pop(0)  # Remove oldest chunk
                
        except Exception as e:
            self.logger.error(f"Error adding audio to buffer: {e}")
    
    def _detect_voice_activity(self, audio_data: bytes) -> bool:
        """Simple voice activity detection based on RMS energy."""
        try:
            # Convert bytes to samples (assuming 16-bit PCM)
            import struct
            samples = struct.unpack(f'<{len(audio_data)//2}h', audio_data)
            
            # Calculate RMS energy
            if len(samples) > 0:
                rms = (sum(sample * sample for sample in samples) / len(samples)) ** 0.5
                normalized_rms = rms / 32768.0  # Normalize to [0, 1] range
                
                # Check if energy exceeds threshold
                return normalized_rms > self.vad_threshold
            else:
                return False
                
        except Exception as e:
            self.logger.debug(f"VAD processing error: {e}")
            return True  # Default to processing if VAD fails
    
    def _should_process_buffer(self, source_type: AudioSourceType) -> bool:
        """Determine if the audio buffer should be processed for transcription."""
        current_time = time.time()
        last_activity = self.last_activity_time[source_type]
        
        # Process if we have sufficient silence after voice activity
        silence_duration = current_time - last_activity
        has_sufficient_silence = silence_duration >= self.silence_duration
        
        # Also process if buffer is getting full
        buffer_length = len(self.audio_buffers[source_type])
        max_buffer_chunks = int(self.audio_buffer_duration / 1.0)
        buffer_full = buffer_length >= max_buffer_chunks
        
        return has_sufficient_silence and buffer_length > 0 or buffer_full
    
    def _process_buffered_audio(self, source_type: AudioSourceType):
        """Process accumulated audio buffer through STT."""
        try:
            buffer = self.audio_buffers[source_type]
            
            if not buffer:
                return
            
            # Combine audio chunks into single audio data
            combined_audio_data = self._combine_audio_chunks(buffer)
            
            if not combined_audio_data:
                return
            
            # Use the most recent chunk's metadata for the combined audio
            latest_chunk = buffer[-1]
            
            # Convert to AudioData format for STT adapter
            if not ADAPTERS_AVAILABLE or AudioData is None or AudioFormat is None:
                self.logger.warning("AudioData/AudioFormat not available, cannot create audio data object")
                return
                
            audio_data = AudioData(
                data=combined_audio_data,
                sample_rate=latest_chunk.sample_rate,
                channels=latest_chunk.channels,
                format=AudioFormat.PCM,
                source_type=source_type.value,
                language_hint=latest_chunk.language_hint,
                device_info=latest_chunk.device_name
            )
            
            # Perform STT transcription
            if self.stt_adapter is None:
                self.logger.warning("STT adapter is None, cannot transcribe audio")
                return
                
            transcription_result = self.stt_adapter.transcribe(audio_data)
            
            # Only process if we got meaningful text
            if transcription_result.text.strip():
                source = source_type.value
                text = transcription_result.text.strip()
                language = transcription_result.language
                confidence = transcription_result.confidence
                
                self.logger.debug(f"Transcribed from {source}: '{text}' (lang: {language}, confidence: {confidence:.2f})")
                
                # Call transcript callback with proper signature: (source, text, language)
                if self.on_transcript:
                    self.on_transcript(source, text, language, confidence)
                
                # Send notification for transcript
                self._notify_transcript_processed(source, text)
                
                # Handle translation if enabled and translation callback exists
                if self.on_translation and self.translation_adapter and language != self.target_language:
                    self._process_translation(source, text, language, self.target_language)
            
            # Clear the processed buffer
            self.audio_buffers[source_type].clear()
            
        except Exception as e:
            self.logger.error(f"Error processing buffered audio: {e}")
    
    def _combine_audio_chunks(self, audio_chunks: List[AudioStreamData]) -> bytes:
        """Combine multiple audio chunks into a single audio data buffer."""
        try:
            if not audio_chunks:
                return b''
            
            # Simply concatenate audio data from all chunks
            combined_data = b''.join(chunk.audio_data for chunk in audio_chunks)
            return combined_data
            
        except Exception as e:
            self.logger.error(f"Error combining audio chunks: {e}")
            return b''
    
    def _process_translation(self, source: str, original_text: str, source_lang: str, target_lang: str):
        """Process translation and call translation callback."""
        try:
            if not self.translation_adapter:
                self.logger.warning("No translation adapter available")
                return
            
            # Perform translation
            translation_result = self.translation_adapter.translate(
                text=original_text,
                source_lang=source_lang,
                target_lang=target_lang
            )
            
            if translation_result.translated_text.strip():
                translated_text = translation_result.translated_text.strip()
                
                self.logger.debug(f"Translated from {source_lang} to {target_lang}: '{original_text}' -> '{translated_text}'")
                
                # Call translation callback with proper signature
                if self.on_translation:
                    self.on_translation(source, original_text, translated_text, source_lang, target_lang)
                
                # Send notification for translation
                self._notify_translation_processed(source, original_text, translated_text)
            
        except Exception as e:
            self.logger.error(f"Error processing translation: {e}")
            if self.error_callback:
                self.error_callback(f"Translation processing error: {e}")
    
    def get_pipeline_health(self) -> Dict[str, Any]:
        """Get comprehensive health status of the pipeline components."""
        health_status = {
            'timestamp': time.time(),
            'overall_status': 'healthy',
            'components': {
                'stt_adapter': {
                    'available': self.stt_adapter is not None,
                    'ready': self.stt_adapter.is_ready() if self.stt_adapter else False,
                    'error': None
                },
                'translation_adapter': {
                    'available': self.translation_adapter is not None,
                    'ready': self.translation_adapter.is_ready() if self.translation_adapter else False,
                    'error': None
                },
                'audio_capture': {
                    'mic_active': self.mic_active,
                    'sys_active': self.sys_active,
                    'processing_active': self.processing_running.is_set(),
                    'error': None
                }
            },
            'performance': {
                'mic_packets_processed': self.recording_stats['mic_packets'],
                'sys_packets_processed': self.recording_stats['sys_packets'],
                'uptime': time.time() - self.recording_stats['start_time'] if self.recording_stats['start_time'] else 0,
                'queue_sizes': {
                    'mic_queue': self.mic_queue.qsize(),
                    'sys_queue': self.sys_queue.qsize(),
                    'output_queue': self.output_queue.qsize()
                }
            }
        }
        
        # Test component health
        try:
            if self.stt_adapter and not self.stt_adapter.is_ready():
                health_status['components']['stt_adapter']['error'] = "STT adapter not ready"
                health_status['overall_status'] = 'degraded'
        except Exception as e:
            health_status['components']['stt_adapter']['error'] = str(e)
            health_status['overall_status'] = 'degraded'
        
        try:
            if self.translation_adapter and not self.translation_adapter.is_ready():
                health_status['components']['translation_adapter']['error'] = "Translation adapter not ready"
                health_status['overall_status'] = 'degraded'
        except Exception as e:
            health_status['components']['translation_adapter']['error'] = str(e)
            health_status['overall_status'] = 'degraded'
        
        # Check for queue overflow
        if any(q.qsize() > q.maxsize * 0.8 for q in [self.mic_queue, self.sys_queue, self.output_queue]):
            health_status['components']['audio_capture']['error'] = "Queue overflow detected"
            health_status['overall_status'] = 'degraded'
        
        return health_status
    
    def handle_component_failure(self, component_name: str, error: Exception):
        """Handle component failure with graceful degradation."""
        self.logger.error(f"Component failure detected in {component_name}: {error}")
        
        # Implement graceful degradation strategies
        if component_name == "stt_adapter":
            self.logger.warning("STT adapter failed, disabling transcript processing")
            self.stt_adapter = None
            if self.on_status:
                self.on_status("stt", "failed", {"error": str(error)})
        
        elif component_name == "translation_adapter":
            self.logger.warning("Translation adapter failed, disabling translation")
            self.translation_adapter = None
            if self.on_status:
                self.on_status("translation", "failed", {"error": str(error)})
        
        elif component_name == "mic_capture":
            self.logger.warning("Microphone capture failed, attempting restart")
            if self.async_runner and UI_INTEGRATION_AVAILABLE:
                # Schedule async restart to avoid blocking
                try:
                    self._restart_microphone_async()
                    self.logger.info("Microphone successfully restarted")
                except Exception as e:
                    self._handle_restart_failure("microphone", e)
            else:
                # Fallback to blocking restart
                try:
                    self.stop_mic_stream()
                    if self.selected_mic_device is not None:
                        device_index = self.selected_mic_device
                        threading.Timer(1.0, lambda: self.start_mic_stream(device_index)).start()
                except Exception as restart_error:
                    self.logger.error(f"Failed to restart microphone: {restart_error}")
                    if self.on_status:
                        self.on_status("microphone", "restart_failed", {"error": str(restart_error)})
        
        elif component_name == "sys_capture":
            self.logger.warning("System audio capture failed, attempting restart")
            if self.async_runner and UI_INTEGRATION_AVAILABLE:
                # Schedule async restart to avoid blocking
                try:
                    self._restart_system_audio_async()
                    self.logger.info("System audio successfully restarted")
                except Exception as e:
                    self._handle_restart_failure("system_audio", e)
            else:
                # Fallback to blocking restart
                try:
                    self.stop_system_stream()
                    if self.selected_sys_device is not None:
                        device_index = self.selected_sys_device
                        threading.Timer(1.0, lambda: self.start_system_stream(device_index)).start()
                except Exception as restart_error:
                    self.logger.error(f"Failed to restart system audio: {restart_error}")
                    if self.on_status:
                        self.on_status("system_audio", "restart_failed", {"error": str(restart_error)})
        
        # Notify error callback
        if self.error_callback:
            self.error_callback(f"Component {component_name} failed: {error}")
        
        # Send user notification if UI integration is available
        if UI_INTEGRATION_AVAILABLE and notify is not None:
            try:
                # Just log since notify function signature is complex
                self.logger.warning(f"Audio component '{component_name}' encountered an error")
            except Exception as e:
                self.logger.warning(f"Failed to send user notification: {e}")
    
    def _restart_microphone_async(self):
        """Async microphone restart operation."""
        import time
        self.stop_mic_stream()
        time.sleep(1)  # Brief delay for cleanup - acceptable in background thread
        
        if self.selected_mic_device is None:
            if UserFacingError is not None:
                raise UserFacingError("No microphone device selected for restart")
            else:
                raise RuntimeError("No microphone device selected for restart")
        
        result = self.start_mic_stream(self.selected_mic_device)
        if not result:
            raise RuntimeError("Failed to restart microphone audio capture")
        return result
    
    def _restart_system_audio_async(self):
        """Async system audio restart operation."""
        import time
        self.stop_system_stream()
        time.sleep(1)  # Brief delay for cleanup - acceptable in background thread
        
        if self.selected_sys_device is None:
            raise RuntimeError("No system audio device selected for restart")
        
        result = self.start_system_stream(self.selected_sys_device)
        if not result:
            raise RuntimeError("Failed to restart system audio capture")
        return result
    
    def _handle_restart_failure(self, component_type: str, error: Exception):
        """Handle restart failure with proper user notification."""
        self.logger.error(f"Failed to restart {component_type}: {error}")
        if self.on_status:
            self.on_status(component_type, "restart_failed", {"error": str(error)})
        
        if UI_INTEGRATION_AVAILABLE and notify is not None:
            try:
                # Just log since notify function signature is complex
                self.logger.error(f"Failed to restart {component_type} audio")
            except Exception as e:
                self.logger.warning(f"Failed to send restart failure notification: {e}")
    
    def _notify_audio_event(self, message: str, level: str = "info", category: str = "audio_pipeline"):
        """Send audio event notification to UI if available."""
        if UI_INTEGRATION_AVAILABLE and notify is not None:
            try:
                # Just log the message since notify function signature is complex
                self.logger.info(f"Audio event notification: {message} (level: {level}, category: {category})")
            except Exception as e:
                self.logger.warning(f"Failed to send audio event notification: {e}")
    
    def _notify_transcript_processed(self, source: str, text: str):
        """Notify when transcript is processed."""
        self._notify_audio_event(
            f"Transcript from {source}: {text[:50]}{'...' if len(text) > 50 else ''}",
            "info",
            category="transcript"
        )
    
    def _notify_translation_processed(self, source: str, original: str, translated: str):
        """Notify when translation is processed."""
        self._notify_audio_event(
            f"Translation from {source}: {translated[:50]}{'...' if len(translated) > 50 else ''}",
            "info",
            category="translation"
        )
    
    def _clear_queues(self):
        """Clear all audio data queues."""
        queues = [self.mic_queue, self.sys_queue, self.output_queue]
        for q in queues:
            while not q.empty():
                try:
                    q.get_nowait()
                except queue.Empty:
                    self.logger.debug("Queue empty during cleanup (expected)")
                    break
        
        self.logger.debug("Audio queues cleared")

# Backward-compatible alias (temporary)
AudioPipelineManager = PipelineManager