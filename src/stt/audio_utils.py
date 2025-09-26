#!/usr/bin/env python3
"""
TalkBridge STT - Audio Utils
============================

Audio utils module for TalkBridge

Author: TalkBridge Team
Date: 2025-08-19
Version: 1.0

Requirements:
- openai-whisper
======================================================================
Functions:
- validate_audio_bytes: Validate audio bytes for transcription.
- save_audio_bytes_to_temp: Save audio bytes to a temporary WAV file.
- validate_audio_file: Validate audio file for transcription.
- get_audio_duration: Get audio duration in seconds.
- check_audio_duration: Check if audio duration is within acceptable limits.
- convert_audio_format: Convert audio file to target format using ffmpeg.
- preprocess_audio: Preprocess audio file for optimal transcription.
- cleanup_temp_file: Clean up temporary audio file.
- create_test_audio: Create test audio data for testing purposes.
- get_audio_info: Get detailed information about audio file.
======================================================================
"""

import os
import tempfile
import wave
import numpy as np
from pathlib import Path
from typing import Optional, Tuple, Union
import logging

try:
    from .config import (
        SAMPLE_RATE, CHANNELS, SUPPORTED_FORMATS, 
        MAX_AUDIO_DURATION, TEMP_AUDIO_PATH
    )
except ImportError:
    # Default values if config is not available
    SAMPLE_RATE = 16000
    CHANNELS = 1
    SUPPORTED_FORMATS = ['.wav', '.mp3', '.m4a', '.flac', '.ogg']
    MAX_AUDIO_DURATION = 600  # 10 minutes
    TEMP_AUDIO_PATH = '/tmp'

# Set up logging
logger = logging.getLogger(__name__)

def validate_audio_bytes(audio_bytes: bytes) -> bool:
    """
    Validate audio bytes for transcription.
    
    Args:
        audio_bytes: Raw audio data as bytes
        
    Returns:
        True if audio is valid, False otherwise
    """
    if not audio_bytes:
        logger.warning("Empty audio data provided")
        return False
    
    # More lenient minimum size check for short audio clips
    if len(audio_bytes) < 512:  # Reduced from 1024 to accommodate shorter clips
        logger.warning(f"Audio data small ({len(audio_bytes)} bytes) - may have transcription issues")
        # Return True but log warning instead of failing
        return True
    
    return True

def save_audio_bytes_to_temp(audio_bytes: bytes, 
                            file_path: Optional[str] = None) -> str:
    """
    Save audio bytes to a temporary WAV file.
    
    Args:
        audio_bytes: Raw audio data as bytes
        file_path: Optional specific file path, otherwise uses temp file
        
    Returns:
        Path to the saved audio file
    """
    if file_path is None:
        # Create temporary file with .wav extension
        temp_fd, temp_path = tempfile.mkstemp(suffix='.wav')
        os.close(temp_fd)
    else:
        temp_path = file_path
    
    try:
        with open(temp_path, 'wb') as f:
            f.write(audio_bytes)
        
        logger.debug(f"Saved audio bytes to temporary file: {temp_path}")
        return temp_path
        
    except Exception as e:
        logger.error(f"Failed to save audio bytes to file: {e}")
        raise

def validate_audio_file(file_path: str) -> bool:
    """
    Validate audio file for transcription.
    
    Args:
        file_path: Path to audio file
        
    Returns:
        True if file is valid, False otherwise
    """
    if not os.path.exists(file_path):
        logger.error(f"Audio file not found: {file_path}")
        return False
    
    # Check file size
    file_size = os.path.getsize(file_path)
    if file_size == 0:
        logger.error(f"Audio file is empty: {file_path}")
        return False
    
    # Check file extension
    file_ext = Path(file_path).suffix.lower()
    if file_ext not in SUPPORTED_FORMATS:
        logger.warning(f"Unsupported audio format: {file_ext}")
        return False
    
    return True

def get_audio_duration(file_path: str) -> float:
    """
    Get audio duration in seconds.
    
    Args:
        file_path: Path to audio file
        
    Returns:
        Duration in seconds
    """
    try:
        with wave.open(file_path, 'rb') as wav_file:
            frames = wav_file.getnframes()
            sample_rate = wav_file.getframerate()
            duration = frames / sample_rate
            return duration
    except Exception as e:
        logger.warning(f"Could not determine audio duration: {e}")
        # Estimate duration based on file size (rough approximation)
        file_size = os.path.getsize(file_path)
        # Assume 16-bit mono at 16kHz
        estimated_duration = file_size / (16000 * 2)
        return estimated_duration

def check_audio_duration(file_path: str) -> bool:
    """
    Check if audio duration is within acceptable limits.
    
    Args:
        file_path: Path to audio file
        
    Returns:
        True if duration is acceptable, False otherwise
    """
    duration = get_audio_duration(file_path)
    
    if duration > MAX_AUDIO_DURATION:
        logger.warning(f"Audio duration ({duration:.2f}s) exceeds maximum ({MAX_AUDIO_DURATION}s)")
        return False
    
    # More lenient minimum duration check - allow shorter audio clips
    if duration < 0.05:  # Less than 50ms - definitely too short
        logger.warning(f"Audio duration too short: {duration:.2f}s")
        return False
    
    # Log but allow short audio (some valid audio can be very brief)
    if duration < 0.5:  # Less than 500ms
        logger.info(f"Short audio duration detected: {duration:.2f}s - proceeding with transcription")
    
    return True

def convert_audio_format(input_path: str, 
                        output_path: str, 
                        target_sample_rate: int = SAMPLE_RATE,
                        target_channels: int = CHANNELS) -> bool:
    """
    Convert audio file to target format using ffmpeg.
    
    Args:
        input_path: Path to input audio file
        output_path: Path to output audio file
        target_sample_rate: Target sample rate
        target_channels: Target number of channels
        
    Returns:
        True if conversion successful, False otherwise
    """
    try:
        import subprocess
        
        # Build ffmpeg command
        cmd = [
            'ffmpeg', '-y',  # Overwrite output file
            '-i', input_path,
            '-ar', str(target_sample_rate),
            '-ac', str(target_channels),
            '-f', 'wav',
            output_path
        ]
        
        # Run conversion
        result = subprocess.run(cmd, capture_output=True, text=True)
        
        if result.returncode == 0:
            logger.debug(f"Successfully converted audio: {input_path} -> {output_path}")
            return True
        else:
            logger.error(f"Audio conversion failed: {result.stderr}")
            return False
            
    except FileNotFoundError:
        logger.error("ffmpeg not found. Please install ffmpeg for audio conversion.")
        return False
    except Exception as e:
        logger.error(f"Audio conversion error: {e}")
        return False

def preprocess_audio(file_path: str) -> str:
    """
    Preprocess audio file for optimal transcription.
    
    Args:
        file_path: Path to audio file
        
    Returns:
        Path to preprocessed audio file
    """
    # Check if preprocessing is needed
    if not validate_audio_file(file_path):
        raise ValueError(f"Invalid audio file: {file_path}")
    
    # Check duration with improved error handling
    try:
        if not check_audio_duration(file_path):
            # Instead of failing, try to process anyway with a warning
            duration = get_audio_duration(file_path)
            logger.warning(f"Audio duration ({duration:.2f}s) may be problematic but attempting transcription")
    except Exception as e:
        logger.warning(f"Could not validate audio duration: {e} - attempting transcription anyway")
    
    # If file is already in correct format, return as is
    file_ext = Path(file_path).suffix.lower()
    if file_ext == '.wav':
        # Check if WAV file has correct parameters
        try:
            with wave.open(file_path, 'rb') as wav_file:
                if (wav_file.getframerate() == SAMPLE_RATE and 
                    wav_file.getnchannels() == CHANNELS):
                    return file_path
        except Exception:
            pass
    
    # Convert to proper format
    temp_output = tempfile.mktemp(suffix='.wav')
    
    if convert_audio_format(file_path, temp_output):
        return temp_output
    else:
        # If conversion fails, return original file
        logger.warning(f"Audio conversion failed, using original file: {file_path}")
        return file_path

def cleanup_temp_file(file_path: str) -> None:
    """
    Clean up temporary audio file.
    
    Args:
        file_path: Path to temporary file to delete
    """
    try:
        if os.path.exists(file_path):
            os.remove(file_path)
            logger.debug(f"Cleaned up temporary file: {file_path}")
    except Exception as e:
        logger.warning(f"Failed to cleanup temporary file {file_path}: {e}")

def create_test_audio(duration: float = 2.0, 
                     sample_rate: int = SAMPLE_RATE,
                     frequency: float = 440.0) -> bytes:
    """
    Create test audio data for testing purposes.
    
    Args:
        duration: Duration in seconds
        sample_rate: Sample rate in Hz
        frequency: Frequency of test tone in Hz
        
    Returns:
        Audio data as bytes
    """
    # Generate sine wave
    t = np.linspace(0, duration, int(sample_rate * duration), False)
    audio_data = np.sin(2 * np.pi * frequency * t)
    
    # Convert to 16-bit PCM (ensure proper typing)
    audio_data = np.multiply(audio_data, np.float64(32767)).astype(np.int16)
    
    # Create WAV file in memory
    import io
    with io.BytesIO() as wav_buffer:
        with wave.open(wav_buffer, 'wb') as wav_file:
            wav_file.setnchannels(CHANNELS)
            wav_file.setsampwidth(2)  # 16-bit
            wav_file.setframerate(sample_rate)
            wav_file.writeframes(audio_data.tobytes())
        
        return wav_buffer.getvalue()

def get_audio_info(file_path: str) -> dict:
    """
    Get detailed information about audio file.
    
    Args:
        file_path: Path to audio file
        
    Returns:
        Dictionary with audio information
    """
    info = {
        'file_path': file_path,
        'file_size': os.path.getsize(file_path),
        'duration': 0.0,
        'sample_rate': 0,
        'channels': 0,
        'format': Path(file_path).suffix.lower()
    }
    
    try:
        with wave.open(file_path, 'rb') as wav_file:
            info['sample_rate'] = wav_file.getframerate()
            info['channels'] = wav_file.getnchannels()
            info['duration'] = wav_file.getnframes() / wav_file.getframerate()
    except Exception as e:
        logger.warning(f"Could not read audio info: {e}")
    
    return info 