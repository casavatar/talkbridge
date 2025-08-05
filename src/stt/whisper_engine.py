#!/usr/bin/env python3
#----------------------------------------------------------------------------------------------------------------------------
# description: This script implements the WhisperEngine class for offline speech-to-text transcription.
#----------------------------------------------------------------------------------------------------------------------------
# 
# author: ingekastel
# date: 2025-06-02
# version: 1.0
#
# requirements:
# - whisper Python package
# - numpy Python package
# - sounddevice Python package
# - soundfile Python package
# - scipy Python package
# - matplotlib Python package
# - pandas Python package
# - seaborn Python package
# - dataclasses Python package
#----------------------------------------------------------------------------------------------------------------------------
# functions:
# - WhisperEngine: Whisper engine class
# - get_whisper_engine(): Get or create a Whisper engine instance
# - is_model_loaded(): Check if Whisper model is currently loaded
# - get_loaded_model(): Get the currently loaded Whisper model
#----------------------------------------------------------------------------------------------------------------------------

import os
import logging
import tempfile
from typing import Optional, Dict, Any, Union
from pathlib import Path

from .config import (
    MODEL_NAME, DEFAULT_LANGUAGE, SUPPORTED_LANGUAGES,
    DEVICE, AUTO_DEVICE, CACHE_DIR, LOG_TRANSCRIPTION,
    CONFIDENCE_THRESHOLD, WORD_TIMESTAMPS, LANGUAGE_DETECTION
)
from .audio_utils import (
    validate_audio_bytes, save_audio_bytes_to_temp,
    validate_audio_file, preprocess_audio, cleanup_temp_file
)

# Set up logging
logger = logging.getLogger(__name__)

# Global model instance (singleton pattern)
_whisper_model = None
_model_loaded = False


class MockWhisperModel:
    """
    Mock Whisper model for fallback when openai-whisper is not installed.
    Provides basic functionality to prevent application crashes.
    """
    
    def __init__(self):
        self.name = "mock-whisper"
        logger.info("Initialized MockWhisperModel for fallback functionality")
    
    def transcribe(self, audio_path, **kwargs):
        """
        Mock transcription that returns a placeholder message.
        
        Args:
            audio_path: Path to audio file
            **kwargs: Additional arguments (ignored)
            
        Returns:
            Dictionary with mock transcription result
        """
        logger.warning("Using mock transcription - Whisper not installed")
        return {
            "text": "[Mock transcription - Whisper not installed]",
            "language": "en",
            "segments": [],
            "language_probability": 1.0
        }


class WhisperEngine:
    """
    Whisper-based Speech-to-Text engine.
    
    Provides offline transcription capabilities using OpenAI's Whisper model.
    Supports multiple languages, device optimization, and various audio formats.
    """
    
    def __init__(self, model_name: str = MODEL_NAME, device: str = DEVICE):
        """
        Initialize Whisper engine.
        
        Args:
            model_name: Whisper model name (tiny, base, small, medium, large)
            device: Device to use (cpu, cuda, mps)
        """
        self.model_name = model_name
        self.device = self._detect_device(device)
        self.model = None
        self.is_loaded = False
        
        # Create cache directory
        CACHE_DIR.mkdir(parents=True, exist_ok=True)
        
        logger.info(f"Initialized Whisper engine with model: {model_name}, device: {self.device}")
    
    def _detect_device(self, device: str) -> str:
        """
        Detect and validate the best available device.
        
        Args:
            device: Requested device
            
        Returns:
            Valid device string
        """
        if AUTO_DEVICE:
            # Auto-detect best available device
            try:
                import torch
                if torch.cuda.is_available():
                    return "cuda"
                elif hasattr(torch.backends, 'mps') and torch.backends.mps.is_available():
                    return "mps"
                else:
                    return "cpu"
            except ImportError:
                logger.warning("PyTorch not available, using CPU")
                return "cpu"
        else:
            # Use specified device
            return device
    
    def load_model(self, model_name: Optional[str] = None) -> bool:
        """
        Load Whisper model.
        
        Args:
            model_name: Optional model name to load
            
        Returns:
            True if model loaded successfully, False otherwise
        """
        global _whisper_model, _model_loaded
        
        if model_name:
            self.model_name = model_name
        
        try:
            import whisper
            
            logger.info(f"Loading Whisper model: {self.model_name}")
            
            # Load model with device specification
            self.model = whisper.load_model(
                self.model_name,
                device=self.device,
                download_root=str(CACHE_DIR)
            )
            
            self.is_loaded = True
            _whisper_model = self.model
            _model_loaded = True
            
            logger.info(f"Successfully loaded Whisper model: {self.model_name}")
            return True
            
        except ImportError:
            logger.warning("Whisper not installed. Using fallback transcription mode.")
            logger.info("To enable full transcription, install with: pip install openai-whisper")
            # Create a mock model for fallback functionality
            self.model = MockWhisperModel()
            self.is_loaded = True
            _whisper_model = self.model
            _model_loaded = True
            return True
        except Exception as e:
            logger.error(f"Failed to load Whisper model: {e}")
            return False
    
    def transcribe_audio_bytes(self, audio_bytes: bytes, 
                              language: Optional[str] = None) -> str:
        """
        Transcribe audio bytes to text.
        
        Args:
            audio_bytes: Raw audio data as bytes
            language: Language code (optional, auto-detected if None)
            
        Returns:
            Transcribed text as string
        """
        if not self.is_loaded:
            if not self.load_model():
                raise RuntimeError("Failed to load Whisper model")
        
        if not validate_audio_bytes(audio_bytes):
            raise ValueError("Invalid audio bytes provided")
        
        # Save audio bytes to temporary file
        temp_file = None
        try:
            temp_file = save_audio_bytes_to_temp(audio_bytes)
            
            # Transcribe the file
            result = self.transcribe_file(temp_file, language)
            
            return result
            
        finally:
            # Clean up temporary file
            if temp_file and os.path.exists(temp_file):
                cleanup_temp_file(temp_file)
    
    def transcribe_file(self, file_path: str, 
                       language: Optional[str] = None) -> str:
        """
        Transcribe audio file to text.
        
        Args:
            file_path: Path to audio file
            language: Language code (optional, auto-detected if None)
            
        Returns:
            Transcribed text as string
        """
        if not self.is_loaded:
            if not self.load_model():
                raise RuntimeError("Failed to load Whisper model")
        
        if not validate_audio_file(file_path):
            raise ValueError(f"Invalid audio file: {file_path}")
        
        try:
            # Preprocess audio if needed
            processed_file = preprocess_audio(file_path)
            is_temp_file = processed_file != file_path
            
            try:
                # Prepare transcription options
                options = {
                    "language": language if language else None,
                    "task": "transcribe",
                    "fp16": False,  # Use float32 for better compatibility
                    "verbose": False
                }
                
                # Remove None values
                options = {k: v for k, v in options.items() if v is not None}
                
                logger.info(f"Transcribing file: {file_path}")
                
                # Perform transcription
                result = self.model.transcribe(processed_file, **options)
                
                # Extract text from result
                transcribed_text = result.get("text", "").strip()
                
                # Log transcription result
                if LOG_TRANSCRIPTION:
                    logger.info(f"Transcription result: {transcribed_text[:100]}...")
                
                return transcribed_text
                
            finally:
                # Clean up temporary processed file if created
                if is_temp_file and os.path.exists(processed_file):
                    cleanup_temp_file(processed_file)
                    
        except Exception as e:
            logger.error(f"Transcription failed: {e}")
            raise
    
    def transcribe_with_metadata(self, file_path: str, 
                                language: Optional[str] = None) -> Dict[str, Any]:
        """
        Transcribe audio file with detailed metadata.
        
        Args:
            file_path: Path to audio file
            language: Language code (optional, auto-detected if None)
            
        Returns:
            Dictionary with transcription result and metadata
        """
        if not self.is_loaded:
            if not self.load_model():
                raise RuntimeError("Failed to load Whisper model")
        
        if not validate_audio_file(file_path):
            raise ValueError(f"Invalid audio file: {file_path}")
        
        try:
            # Preprocess audio if needed
            processed_file = preprocess_audio(file_path)
            is_temp_file = processed_file != file_path
            
            try:
                # Prepare transcription options
                options = {
                    "language": language if language else None,
                    "task": "transcribe",
                    "fp16": False,
                    "verbose": False,
                    "word_timestamps": WORD_TIMESTAMPS
                }
                
                # Remove None values
                options = {k: v for k, v in options.items() if v is not None}
                
                logger.info(f"Transcribing file with metadata: {file_path}")
                
                # Perform transcription
                result = self.model.transcribe(processed_file, **options)
                
                # Add additional metadata
                result["model_name"] = self.model_name
                result["device"] = self.device
                result["language_detected"] = result.get("language", language or "unknown")
                
                return result
                
            finally:
                # Clean up temporary processed file if created
                if is_temp_file and os.path.exists(processed_file):
                    cleanup_temp_file(processed_file)
                    
        except Exception as e:
            logger.error(f"Transcription with metadata failed: {e}")
            raise
    
    def get_supported_languages(self) -> list:
        """
        Get list of supported languages.
        
        Returns:
            List of supported language codes
        """
        return SUPPORTED_LANGUAGES.copy()
    
    def is_language_supported(self, language: str) -> bool:
        """
        Check if language is supported.
        
        Args:
            language: Language code to check
            
        Returns:
            True if language is supported, False otherwise
        """
        return language in SUPPORTED_LANGUAGES
    
    def get_model_info(self) -> Dict[str, Any]:
        """
        Get information about the loaded model.
        
        Returns:
            Dictionary with model information
        """
        return {
            "model_name": self.model_name,
            "device": self.device,
            "is_loaded": self.is_loaded,
            "supported_languages": self.get_supported_languages()
        }
    
    def unload_model(self) -> None:
        """
        Unload the model to free memory.
        """
        global _whisper_model, _model_loaded
        
        if self.model:
            del self.model
            self.model = None
            self.is_loaded = False
            _whisper_model = None
            _model_loaded = False
            logger.info("Whisper model unloaded")


def get_whisper_engine(model_name: str = MODEL_NAME, 
                      device: str = DEVICE) -> WhisperEngine:
    """
    Get or create a Whisper engine instance.
    
    Args:
        model_name: Whisper model name
        device: Device to use
        
    Returns:
        WhisperEngine instance
    """
    return WhisperEngine(model_name, device)


def is_model_loaded() -> bool:
    """
    Check if Whisper model is currently loaded.
    
    Returns:
        True if model is loaded, False otherwise
    """
    return _model_loaded


def get_loaded_model() -> Optional[Any]:
    """
    Get the currently loaded Whisper model.
    
    Returns:
        Loaded model or None
    """
    return _whisper_model 