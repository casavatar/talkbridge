#! /usr/bin/env python3
#-------------------------------------------------------------------------------------------------
# description: STT API Module
#-------------------------------------------------------------------------------------------------
#
# author: ingekastel
# date: 2025-06-02
# version: 1.0
#-------------------------------------------------------------------------------------------------

# requirements:
# - streamlit Python package
# - tempfile Python package
# - os Python package
# - pathlib Python package
# - typing Python package
# - logging Python package
#-------------------------------------------------------------------------------------------------
# functions:
# - STTAPI: STT API class
# - start_recording: Start audio recording
# - stop_recording: Stop audio recording
# - transcribe_audio: Transcribe audio data to text
# - transcribe_file: Transcribe audio file to text
# - get_supported_languages: Get list of supported languages
# - update_recording_settings: Update recording settings
# - get_recording_status: Get current recording status
# - validate_audio_format: Validate audio data format
# - create_audio_file: Create an audio file from audio data
# - get_audio_duration: Get audio duration in seconds
#-------------------------------------------------------------------------------------------------

import streamlit as st
import tempfile
import os
from pathlib import Path
from typing import Optional, Dict, Any
import logging

logger = logging.getLogger(__name__)


class STTAPI:
    """API interface for STT functionality."""
    
    def __init__(self):
        """Initialize the STT API."""
        self.current_language = "en"
        self.recording_settings = {
            "sample_rate": 16000,
            "channels": 1,
            "chunk_size": 1024
        }
        self.is_recording = False
    
    def start_recording(self) -> bool:
        """
        Start audio recording.
        
        Returns:
            True if recording started successfully
        """
        try:
            self.is_recording = True
            logger.info("Started audio recording")
            return True
        except Exception as e:
            logger.error(f"Failed to start recording: {e}")
            return False
    
    def stop_recording(self) -> Optional[bytes]:
        """
        Stop audio recording and return audio data.
        
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
        Transcribe audio data to text.
        
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
            
            # Placeholder for actual transcription
            # In a real implementation, this would use a speech recognition library
            transcribed_text = "This is a placeholder transcription. In a real implementation, this would contain the actual transcribed text from the audio data."
            
            logger.info(f"Transcribed {len(audio_data)} bytes to text: {transcribed_text[:50]}...")
            return transcribed_text
            
        except Exception as e:
            logger.error(f"Transcription failed: {e}")
            return None
    
    def transcribe_file(self, audio_file_path: str, language: str = "en") -> Optional[str]:
        """
        Transcribe audio file to text.
        
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
            
            # Read audio file
            with open(audio_file_path, 'rb') as f:
                audio_data = f.read()
            
            return self.transcribe_audio(audio_data, language)
            
        except Exception as e:
            logger.error(f"File transcription failed: {e}")
            return None
    
    def get_supported_languages(self) -> list:
        """
        Get list of supported languages for transcription.
        
        Returns:
            List of supported language codes
        """
        return [
            {"code": "en", "name": "English"},
            {"code": "es", "name": "Spanish"},
            {"code": "fr", "name": "French"},
            {"code": "de", "name": "German"},
            {"code": "it", "name": "Italian"},
            {"code": "pt", "name": "Portuguese"},
            {"code": "ru", "name": "Russian"},
            {"code": "ja", "name": "Japanese"},
            {"code": "ko", "name": "Korean"},
            {"code": "zh", "name": "Chinese"}
        ]
    
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
            Dictionary containing recording status
        """
        return {
            "is_recording": self.is_recording,
            "current_language": self.current_language,
            "recording_settings": self.recording_settings
        }
    
    def validate_audio_format(self, audio_data: bytes) -> bool:
        """
        Validate audio data format.
        
        Args:
            audio_data: Audio data to validate
            
        Returns:
            True if audio format is valid
        """
        if not audio_data:
            return False
        
        # Basic validation - check if data looks like audio
        if len(audio_data) < 100:  # Too small for meaningful audio
            return False
        
        # Check for common audio file headers
        audio_headers = [b'RIFF', b'ID3', b'\xff\xfb', b'\xff\xf3']  # WAV, MP3 headers
        for header in audio_headers:
            if audio_data.startswith(header):
                return True
        
        # If no recognized header, assume it's raw audio data
        return True
    
    def create_audio_file(self, audio_data: bytes, filename: str = None) -> Optional[str]:
        """
        Create an audio file from audio data.
        
        Args:
            audio_data: Audio data as bytes
            filename: Optional filename for the audio file
            
        Returns:
            Path to created audio file or None if failed
        """
        try:
            if not filename:
                filename = f"stt_recording_{hash(audio_data) % 10000}.wav"
            
            # Create temp directory if needed
            temp_dir = Path("temp")
            temp_dir.mkdir(exist_ok=True)
            
            output_path = temp_dir / filename
            
            # Write audio data to file
            with open(output_path, 'wb') as f:
                f.write(audio_data)
            
            logger.info(f"Created audio file: {output_path}")
            return str(output_path)
            
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
            # Rough estimation based on data size and sample rate
            sample_rate = self.recording_settings["sample_rate"]
            channels = self.recording_settings["channels"]
            bytes_per_sample = 2  # Assuming 16-bit audio
            
            total_samples = len(audio_data) / bytes_per_sample
            duration = total_samples / (sample_rate * channels)
            
            return max(0.0, duration)
            
        except Exception as e:
            logger.error(f"Failed to calculate audio duration: {e}")
            return 0.0 