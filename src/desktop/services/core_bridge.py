"""
TalkBridge Desktop - Core Bridge Service
=======================================

Bridge between the user interface and TalkBridge core modules.
Provides a unified API with proper threading for asynchronous operations
and service state management.

Author: TalkBridge Team
Date: 2025
"""

import logging
from typing import Dict, Any, Optional, Callable, List
from pathlib import Path
from threading import Lock

from PyQt6.QtCore import (
    QObject, pyqtSignal, QThread, QThreadPool, 
    QRunnable, QTimer, QMutex
)

# Imports from TalkBridge core modules
try:
    from src.tts.synthesizer import synthesize_voice
    TTS_AVAILABLE = True
except ImportError:
    TTS_AVAILABLE = False
    logging.warning("TTS module not available")

try:
    from src.audio.capture import AudioCapture
    AUDIO_AVAILABLE = True
except ImportError:
    AUDIO_AVAILABLE = False
    logging.warning("Audio Capture module not available")

try:
    from src.translation.translator import Translator
    TRANSLATION_AVAILABLE = True
except ImportError:
    TRANSLATION_AVAILABLE = False
    logging.warning("Translation module not available")

try:
    from src.animation.face_sync import FaceSync
    ANIMATION_AVAILABLE = True
except ImportError:
    ANIMATION_AVAILABLE = False
    logging.warning("Animation module not available")

try:
    from src.ollama.ollama_client import OllamaClient
    OLLAMA_AVAILABLE = True
except ImportError:
    OLLAMA_AVAILABLE = False
    logging.warning("Ollama module not available")


class WorkerSignals(QObject):
    """Signals for asynchronous workers."""
    finished = pyqtSignal()
    error = pyqtSignal(str)
    result = pyqtSignal(object)
    progress = pyqtSignal(int)


class BaseWorker(QRunnable):
    """Base worker for asynchronous operations."""
    
    def __init__(self, operation: Callable, *args, **kwargs):
        super().__init__()
        self.operation = operation
        self.args = args
        self.kwargs = kwargs
        self.signals = WorkerSignals()
        self.is_cancelled = False
    
    def run(self) -> None:
        """Executes the operation in the thread pool."""
        try:
            if not self.is_cancelled:
                result = self.operation(*self.args, **self.kwargs)
                if not self.is_cancelled:
                    self.signals.result.emit(result)
        except Exception as e:
            self.signals.error.emit(str(e))
        finally:
            self.signals.finished.emit()
    
    def cancel(self) -> None:
        """Cancels the operation."""
        self.is_cancelled = True


class TTSService(QObject):
    """Text-to-Speech service with asynchronous operations."""
    
    synthesis_completed = pyqtSignal(str, bytes)  # text, audio_data
    synthesis_failed = pyqtSignal(str, str)  # text, error_message
    status_changed = pyqtSignal(str)  # status
    
    def __init__(self, state_manager=None, parent=None):
        super().__init__(parent)
        self.state_manager = state_manager
        self.logger = logging.getLogger("talkbridge.desktop.tts")
        self.thread_pool = QThreadPool()
        self.is_available = TTS_AVAILABLE
        
        # Internal state
        self.current_workers: List[BaseWorker] = []
        self.worker_lock = Lock()
        
        self.logger.info(f"TTSService initialized (available: {self.is_available})")
    
    def synthesize_async(self, text: str, output_path: Optional[str] = None,
                        voice_settings: Optional[Dict[str, Any]] = None) -> bool:
        """
        Asynchronously synthesizes text to speech.

        Args:
            text: Text to synthesize
            output_path: Optional output path
            voice_settings: Voice configuration

        Returns:
            bool: True if the operation started successfully
        """
        if not self.is_available:
            self.synthesis_failed.emit(text, "TTS service not available")
            return False
        
        if not text.strip():
            self.synthesis_failed.emit(text, "Empty text")
            return False
        
        try:
            # Create worker
            worker = BaseWorker(self._do_synthesis, text, output_path, voice_settings)
            worker.signals.result.connect(
                lambda result: self.synthesis_completed.emit(text, result)
            )
            worker.signals.error.connect(
                lambda error: self.synthesis_failed.emit(text, error)
            )
            worker.signals.finished.connect(
                lambda: self._cleanup_worker(worker)
            )
            
            # Add to active workers list
            with self.worker_lock:
                self.current_workers.append(worker)
            
            # Execute
            self.thread_pool.start(worker)
            self.status_changed.emit("processing")
            
            return True
            
        except Exception as e:
            self.logger.error(f"Error starting TTS synthesis: {e}")
            self.synthesis_failed.emit(text, str(e))
            return False
    
    def _do_synthesis(self, text: str, output_path: Optional[str] = None,
                     voice_settings: Optional[Dict[str, Any]] = None) -> bytes:
        """Performs the actual voice synthesis."""
        try:
            self.logger.info(f"Synthesizing text: '{text[:50]}...'")
            
            # Use default config if not provided
            if voice_settings is None:
                voice_settings = self._get_default_voice_settings()

            # Call core module
            if output_path:
                synthesize_voice(text, output_path, **voice_settings)
                # Read generated file
                with open(output_path, 'rb') as f:
                    audio_data = f.read()
            else:
                # Generate in memory (implementation depends on module)
                temp_path = "/tmp/tts_temp.wav"
                synthesize_voice(text, temp_path, **voice_settings)
                with open(temp_path, 'rb') as f:
                    audio_data = f.read()

            self.logger.info("TTS synthesis completed")
            return audio_data

        except Exception as e:
            self.logger.error(f"Error in TTS synthesis: {e}")
            raise
    
    def _get_default_voice_settings(self) -> Dict[str, Any]:
        """Returns default voice configuration."""
        if self.state_manager:
            return {
                "voice": self.state_manager.get_config("tts.voice", "default"),
                "speed": self.state_manager.get_config("tts.speed", 1.0),
                "pitch": self.state_manager.get_config("tts.pitch", 1.0)
            }
        return {"voice": "default", "speed": 1.0, "pitch": 1.0}
    
    def _cleanup_worker(self, worker: BaseWorker) -> None:
        """Cleans up a completed worker."""
        with self.worker_lock:
            if worker in self.current_workers:
                self.current_workers.remove(worker)
        
        # Update status if no active workers
        if not self.current_workers:
            self.status_changed.emit("idle")
    
    def cancel_all_synthesis(self) -> None:
        """Cancels all ongoing synthesis operations."""
        with self.worker_lock:
            for worker in self.current_workers:
                worker.cancel()
        self.status_changed.emit("cancelled")


class AudioService(QObject):
    """Audio service with capture and processing."""
    
    audio_captured = pyqtSignal(bytes)  # audio_data
    recording_started = pyqtSignal()
    recording_stopped = pyqtSignal()
    status_changed = pyqtSignal(str)  # status
    error_occurred = pyqtSignal(str)  # error_message
    
    def __init__(self, state_manager=None, parent=None):
        super().__init__(parent)
        self.state_manager = state_manager
        self.logger = logging.getLogger("talkbridge.desktop.audio")
        self.is_available = AUDIO_AVAILABLE
        
        # Audio components
        self.audio_capture: Optional[AudioCapture] = None
        self.is_recording = False
        
        # Timer for audio polling
        self.audio_timer = QTimer()
        self.audio_timer.timeout.connect(self._process_audio_buffer)
        
        self.logger.info(f"AudioService initialized (available: {self.is_available})")
    
    def initialize_audio_capture(self) -> bool:
        """
        Initializes the audio capture system.

        Returns:
            bool: True if initialized successfully
        """
        if not self.is_available:
            self.error_occurred.emit("Audio module not available")
            return False
        
        try:
            # Get audio config
            audio_config = self._get_audio_config()

            # Initialize AudioCapture
            self.audio_capture = AudioCapture(**audio_config)

            self.status_changed.emit("initialized")
            self.logger.info("Audio capture system initialized")
            return True

        except Exception as e:
            error_msg = f"Error initializing audio capture: {e}"
            self.logger.error(error_msg)
            self.error_occurred.emit(error_msg)
            return False
    
    def start_recording(self) -> bool:
        """
        Starts audio recording.

        Returns:
            bool: True if started successfully
        """
        if not self.audio_capture:
            if not self.initialize_audio_capture():
                return False
        
        try:
            self.audio_capture.start_recording()
            self.is_recording = True
            
            # Start timer for processing
            self.audio_timer.start(100)  # Process every 100ms
            
            self.recording_started.emit()
            self.status_changed.emit("recording")
            
            self.logger.info("Audio recording started")
            return True

        except Exception as e:
            error_msg = f"Error starting recording: {e}"
            self.logger.error(error_msg)
            self.error_occurred.emit(error_msg)
            return False
    
    def stop_recording(self) -> bytes:
        """
        Stops audio recording and returns the data.

        Returns:
            bytes: Recorded audio data
        """
        if not self.is_recording:
            return b""
        
        try:
            # Stop timer
            self.audio_timer.stop()
            
            # Stop capture
            audio_data = self.audio_capture.stop_recording()
            self.is_recording = False
            
            self.recording_stopped.emit()
            self.status_changed.emit("idle")
            
            if audio_data:
                self.audio_captured.emit(audio_data)
            
            self.logger.info("Audio recording stopped")
            return audio_data or b""

        except Exception as e:
            error_msg = f"Error stopping recording: {e}"
            self.logger.error(error_msg)
            self.error_occurred.emit(error_msg)
            return b""
    
    def _process_audio_buffer(self) -> None:
        """Processes the audio buffer in real time."""
        if not self.audio_capture or not self.is_recording:
            return
        
        try:
            # Get buffer data (module-specific implementation)
            buffer_data = getattr(self.audio_capture, 'get_buffer_data', lambda: None)()

            if buffer_data:
                # Emit data for real-time processing
                self.audio_captured.emit(buffer_data)

        except Exception as e:
            self.logger.warning(f"Error processing audio buffer: {e}")
    
    def _get_audio_config(self) -> Dict[str, Any]:
        """Returns audio configuration from StateManager."""
        if self.state_manager:
            return {
                "sample_rate": self.state_manager.get_config("audio.sample_rate", 44100),
                "channels": self.state_manager.get_config("audio.channels", 1),
                "chunk_size": self.state_manager.get_config("audio.chunk_size", 1024)
            }
        return {"sample_rate": 44100, "channels": 1, "chunk_size": 1024}


class CoreBridge(QObject):
    """
    Main bridge between UI and TalkBridge core modules.

    Coordinates all services and provides a unified API
    for the user interface.
    """
    
    # General signals
    service_initialized = pyqtSignal(str, bool)  # service_name, success
    all_services_ready = pyqtSignal(bool)  # success
    service_error = pyqtSignal(str, str)  # service_name, error_message
    
    def __init__(self, state_manager=None, parent=None):
        super().__init__(parent)
        
        self.state_manager = state_manager
        self.logger = logging.getLogger("talkbridge.desktop.bridge")
        
        # Services
        self.tts_service: Optional[TTSService] = None
        self.audio_service: Optional[AudioService] = None
        
        # State
        self.services_initialized = {}
        self.mutex = QMutex()
        
        self.logger.info("CoreBridge initialized")
    
    def initialize_all_services(self) -> bool:
        """
        Initializes all available services.

        Returns:
            bool: True if at least one service was initialized successfully
        """
        try:
            self.logger.info("Initializing all services...")
            
            success_count = 0
            total_services = 0
            
            # Initialize TTS Service
            total_services += 1
            if self._initialize_tts_service():
                success_count += 1
            
            # Initialize Audio Service
            total_services += 1
            if self._initialize_audio_service():
                success_count += 1
            
            # TODO: Initialize other services (Translation, Ollama, Animation)
            
            # Determine overall success
            overall_success = success_count > 0
            
            self.all_services_ready.emit(overall_success)
            
            self.logger.info(
                f"Service initialization completed: "
                f"{success_count}/{total_services} successful"
            )
            
            return overall_success
            
        except Exception as e:
            self.logger.error(f"Error during service initialization: {e}")
            self.all_services_ready.emit(False)
            return False
    
    def _initialize_tts_service(self) -> bool:
        """Initializes the TTS service."""
        try:
            self.tts_service = TTSService(self.state_manager, self)
            
            # Connect signals
            self.tts_service.status_changed.connect(
                lambda status: self._update_service_status("tts", status)
            )
            self.tts_service.synthesis_failed.connect(
                lambda text, error: self.service_error.emit("tts", error)
            )
            
            success = self.tts_service.is_available
            self.services_initialized["tts"] = success
            self.service_initialized.emit("tts", success)
            
            if self.state_manager:
                status = "connected" if success else "error"
                self.state_manager.set_service_status("tts", status)
            
            return success
            
        except Exception as e:
            self.logger.error(f"Error initializing TTS service: {e}")
            self.service_initialized.emit("tts", False)
            return False
    
    def _initialize_audio_service(self) -> bool:
        """Initializes the audio service."""
        try:
            self.audio_service = AudioService(self.state_manager, self)
            
            # Connect signals
            self.audio_service.status_changed.connect(
                lambda status: self._update_service_status("audio", status)
            )
            self.audio_service.error_occurred.connect(
                lambda error: self.service_error.emit("audio", error)
            )
            
            success = self.audio_service.is_available
            self.services_initialized["audio"] = success
            self.service_initialized.emit("audio", success)
            
            if self.state_manager:
                status = "connected" if success else "error"
                self.state_manager.set_service_status("audio", status)
            
            return success
            
        except Exception as e:
            self.logger.error(f"Error initializing audio service: {e}")
            self.service_initialized.emit("audio", False)
            return False
    
    def _update_service_status(self, service_name: str, status: str) -> None:
        """Updates the status of a service in StateManager."""
        if self.state_manager:
            self.state_manager.set_service_status(service_name, status)
    
    # Public API for services

    def synthesize_text(self, text: str, **kwargs) -> bool:
        """Public API for text synthesis."""
        if self.tts_service:
            return self.tts_service.synthesize_async(text, **kwargs)
        return False

    def start_audio_recording(self) -> bool:
        """Public API to start audio recording."""
        if self.audio_service:
            return self.audio_service.start_recording()
        return False

    def stop_audio_recording(self) -> bytes:
        """Public API to stop audio recording."""
        if self.audio_service:
            return self.audio_service.stop_recording()
        return b""

    def get_service_status(self, service_name: str) -> str:
        """
        Gets the current status of a service.

        Args:
            service_name: Service name

        Returns:
            str: Service status
        """
        if self.state_manager:
            status = self.state_manager.get_service_status(service_name)
            return status.status if status else "unknown"
        return "unknown"

    def is_service_available(self, service_name: str) -> bool:
        """
        Checks if a service is available.

        Args:
            service_name: Service name

        Returns:
            bool: True if available
        """
        return self.services_initialized.get(service_name, False)

    def cleanup(self) -> None:
        """Cleans up resources for all services."""
        try:
            self.logger.info("Cleaning up CoreBridge resources...")

            # Clean up TTS Service
            if self.tts_service:
                self.tts_service.cancel_all_synthesis()

            # Clean up Audio Service
            if self.audio_service and self.audio_service.is_recording:
                self.audio_service.stop_recording()

            self.logger.info("CoreBridge cleanup completed")

        except Exception as e:
            self.logger.error(f"Error during CoreBridge cleanup: {e}")