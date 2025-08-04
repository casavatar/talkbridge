#!/usr/bin/env python3
"""
STT (Speech-to-Text) API Module

Provides REST API endpoints for speech-to-text functionality:
- Audio recording and transcription
- File-based transcription
- Language support and configuration
- Real-time transcription capabilities

Author: TalkBridge Development Team
Date: 2024-01-01
"""

import os
import logging
from typing import Optional, Dict, Any
from pathlib import Path

# Add src to path for imports
import sys
sys.path.append(str(Path(__file__).parent.parent.parent))

try:
    from stt import (
        transcribe_audio,
        transcribe_file,
        load_model,
        get_supported_languages,
        is_language_supported,
        get_engine_status
    )
except ImportError:
    logging.warning("STT module not available")

# Set up logging
logger = logging.getLogger(__name__)


class STTAPI:
    """
    Speech-to-Text API class.
    
    Provides methods for audio recording, transcription, and management
    of the STT system using the new Whisper-based module.
    """
    
    def __init__(self):
        """Initialize STT API."""
        self.recording_settings = {
            "sample_rate": 16000,
            "channels": 1,
            "chunk_size": 1024
        }
        self.is_recording = False
        
        # Initialize STT engine
        try:
            # Load model on startup (optional)
            load_model()
            logger.info("STT API initialized successfully")
        except Exception as e:
            logger.warning(f"STT initialization warning: {e}")
    
    def start_recording(self) -> bool:
        """
        Start audio recording.
        
        Returns:
            True if recording started successfully, False otherwise
        """
        try:
            # Placeholder for actual recording implementation
            # In a real implementation, this would start audio capture
            self.is_recording = True
            logger.info("Started audio recording")
            return True
        except Exception as e:
            logger.error(f"Failed to start recording: {e}")
            return False
    
    def stop_recording(self) -> Optional[bytes]:
        """
        Stop audio recording and return captured audio.
        
        Returns:
            Audio data as bytes or None if failed
        """
        try:
            self.is_recording = False
            logger.info("Stopped audio recording")
            # Placeholder for actual audio capture
            return b"audio_data_placeholder"
        except Exception as e:
            logger.error(f"Failed to stop recording: {e}")
            return None
    
    def transcribe_audio(self, audio_data: bytes, language: str = "en") -> Optional[str]:
        """
        Transcribe audio data to text using the new STT module.
        
        Args:
            audio_data: Audio data as bytes
            language: Language code for transcription
            
        Returns:
            Transcribed text or None if failed
        """
        try:
            if not audio_data:
                logger.warning("No audio data provided for transcription")
                return None
            
            # Use the new STT module for transcription
            transcribed_text = transcribe_audio(audio_data, language)
            
            logger.info(f"Transcribed {len(audio_data)} bytes to text: {transcribed_text[:50]}...")
            return transcribed_text
            
        except Exception as e:
            logger.error(f"Transcription failed: {e}")
            return None
    
    def transcribe_file(self, audio_file_path: str, language: str = "en") -> Optional[str]:
        """
        Transcribe audio file to text using the new STT module.
        
        Args:
            audio_file_path: Path to audio file
            language: Language code for transcription
            
        Returns:
            Transcribed text or None if failed
        """
        try:
            if not os.path.exists(audio_file_path):
                logger.error(f"Audio file not found: {audio_file_path}")
                return None
            
            # Use the new STT module for file transcription
            transcribed_text = transcribe_file(audio_file_path, language)
            
            logger.info(f"Transcribed file {audio_file_path} to text: {transcribed_text[:50]}...")
            return transcribed_text
            
        except Exception as e:
            logger.error(f"File transcription failed: {e}")
            return None
    
    def get_supported_languages(self) -> list:
        """
        Get list of supported languages for transcription.
        
        Returns:
            List of supported language codes
        """
        try:
            return get_supported_languages()
        except Exception as e:
            logger.error(f"Failed to get supported languages: {e}")
            return [
                {"code": "en", "name": "English"},
                {"code": "es", "name": "Spanish"},
                {"code": "fr", "name": "French"},
                {"code": "de", "name": "German"}
            ]
    
    def is_language_supported(self, language: str) -> bool:
        """
        Check if a language is supported.
        
        Args:
            language: Language code to check
            
        Returns:
            True if language is supported, False otherwise
        """
        try:
            return is_language_supported(language)
        except Exception as e:
            logger.error(f"Failed to check language support: {e}")
            return False
    
    def get_engine_status(self) -> Dict[str, Any]:
        """
        Get comprehensive status of the STT engine.
        
        Returns:
            Dictionary with engine status information
        """
        try:
            return get_engine_status()
        except Exception as e:
            logger.error(f"Failed to get engine status: {e}")
            return {
                "model_loaded": False,
                "model_name": "unknown",
                "device": "unknown",
                "supported_languages": [],
                "default_language": "en"
            }
    
    def update_recording_settings(self, sample_rate: int = 16000, 
                                channels: int = 1, chunk_size: int = 1024) -> None:
        """
        Update recording settings.
        
        Args:
            sample_rate: Audio sample rate
            channels: Number of audio channels
            chunk_size: Audio chunk size
        """
        self.recording_settings.update({
            "sample_rate": sample_rate,
            "channels": channels,
            "chunk_size": chunk_size
        })
        logger.info(f"Updated recording settings: {self.recording_settings}")
    
    def get_recording_status(self) -> Dict[str, Any]:
        """
        Get current recording status.
        
        Returns:
            Dictionary with recording status
        """
        return {
            "is_recording": self.is_recording,
            "settings": self.recording_settings.copy()
        }
    
    def validate_audio_format(self, audio_data: bytes) -> bool:
        """
        Validate audio format for transcription.
        
        Args:
            audio_data: Audio data as bytes
            
        Returns:
            True if format is valid, False otherwise
        """
        try:
            if not audio_data:
                return False
            
            # Basic validation - check minimum size
            if len(audio_data) < 1024:
                return False
            
            # Additional format validation could be added here
            # For now, accept any non-empty data with minimum size
            
            return True
            
        except Exception as e:
            logger.error(f"Audio format validation failed: {e}")
            return False
    
    def create_audio_file(self, audio_data: bytes, filename: str = None) -> Optional[str]:
        """
        Create audio file from bytes.
        
        Args:
            audio_data: Audio data as bytes
            filename: Optional filename, auto-generated if None
            
        Returns:
            Path to created audio file or None if failed
        """
        try:
            if not audio_data:
                logger.error("No audio data provided")
                return None
            
            # Generate filename if not provided
            if filename is None:
                import tempfile
                import time
                timestamp = int(time.time())
                filename = f"audio_{timestamp}.wav"
            
            # Ensure directory exists
            file_path = Path(filename)
            file_path.parent.mkdir(parents=True, exist_ok=True)
            
            # Write audio data to file
            with open(file_path, 'wb') as f:
                f.write(audio_data)
            
            logger.info(f"Created audio file: {file_path}")
            return str(file_path)
            
        except Exception as e:
            logger.error(f"Failed to create audio file: {e}")
            return None
    
    def get_audio_duration(self, audio_data: bytes) -> float:
        """
        Get audio duration in seconds.
        
        Args:
            audio_data: Audio data as bytes
            
        Returns:
            Duration in seconds
        """
        try:
            if not audio_data:
                return 0.0
            
            # Estimate duration based on data size
            # Assuming 16-bit mono at 16kHz
            bytes_per_second = 16000 * 2  # 16-bit = 2 bytes per sample
            duration = len(audio_data) / bytes_per_second
            
            return duration
            
        except Exception as e:
            logger.error(f"Failed to calculate audio duration: {e}")
            return 0.0 