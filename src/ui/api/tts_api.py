#! /usr/bin/env python3
"""
TalkBridge UI - Tts Api
=======================

Módulo tts_api para TalkBridge

Author: TalkBridge Team
Date: 2025-08-19
Version: 1.0

Requirements:
- PyQt6
- Flask
======================================================================
Functions:
- __init__: Initialize the TTS API.
- synthesize_text: Synthesize text to speech.
- setup_voice_cloning: Set up voice cloning with reference samples.
- get_synthesis_info: Get information about the TTS system.
- list_available_models: Get list of available TTS models.
- update_voice_settings: Update voice synthesis settings.
- create_audio_file: Create an audio file from text.
- get_audio_bytes: Get audio data as bytes.
- validate_text: Validate text for synthesis.
- get_supported_languages: Get list of supported languages.
======================================================================
"""

import streamlit as st
import tempfile
import os
from pathlib import Path
from typing import Optional, Dict, Any
import logging

# Add src to path for imports
import sys
sys.path.append(str(Path(__file__).parent.parent.parent))

try:
    from tts import synthesize_voice, setup_voice_cloning, get_synthesis_info
    TTS_AVAILABLE = True
except ImportError:
    logging.warning("TTS module not available")
    TTS_AVAILABLE = False

logger = logging.getLogger(__name__)


class TTSAPI:
    """API interface for TTS functionality."""
    
    def __init__(self):
        """Initialize the TTS API."""
        self.voice_cloning_setup = False
        self.current_voice_model = "default"
        self.voice_settings = {
            "speed": 1.0,
            "pitch": 0,
            "language": "en"
        }
    
    def synthesize_text(self, text: str, output_path: Optional[str] = None, 
                       language: str = "en", voice_cloning: bool = False,
                       reference_samples: Optional[list] = None) -> Optional[bytes]:
        """
        Synthesize text to speech.
        
        Args:
            text: Text to synthesize
            output_path: Optional path to save audio file
            language: Language code for synthesis
            voice_cloning: Whether to use voice cloning
            reference_samples: Audio files for voice cloning
            
        Returns:
            Audio data as bytes or None if failed
        """
        try:
            if not TTS_AVAILABLE:
                logger.error("TTS module not available")
                return None
                
            if not text.strip():
                logger.warning("Empty text provided for synthesis")
                return None
            
            # Update voice settings
            self.voice_settings["language"] = language
            
            # Synthesize voice
            result = synthesize_voice(
                text=text,
                output_path=output_path,
                reference_samples=reference_samples,
                language=language,
                clone_voice=voice_cloning
            )
            
            if isinstance(result, bytes):
                logger.info(f"Successfully synthesized {len(text)} characters to {len(result)} bytes")
                return result
            elif isinstance(result, str):
                logger.info(f"Successfully synthesized to file: {result}")
                return None  # File was saved, no bytes returned
            else:
                logger.error("Unexpected result type from synthesize_voice")
                return None
                
        except Exception as e:
            logger.error(f"TTS synthesis failed: {e}")
            st.error(f"Text-to-speech synthesis failed: {e}")
            return None
    
    def setup_voice_cloning(self, reference_samples: list) -> bool:
        """
        Set up voice cloning with reference samples.
        
        Args:
            reference_samples: List of audio file paths for voice cloning
            
        Returns:
            True if setup successful
        """
        try:
            success = setup_voice_cloning(reference_samples)
            if success:
                self.voice_cloning_setup = True
                logger.info("Voice cloning setup successful")
            return success
        except Exception as e:
            logger.error(f"Voice cloning setup failed: {e}")
            return False
    
    def get_synthesis_info(self) -> Dict[str, Any]:
        """
        Get information about the TTS system.
        
        Returns:
            Dictionary containing TTS system information
        """
        try:
            info = get_synthesis_info()
            return info
        except Exception as e:
            logger.error(f"Failed to get synthesis info: {e}")
            return {"error": str(e)}
    
    def list_available_models(self) -> list:
        """
        Get list of available TTS models.
        
        Returns:
            List of available model names
        """
        try:
            from tts import list_available_models
            models = list_available_models()
            return models
        except Exception as e:
            logger.error(f"Failed to get available models: {e}")
            return []
    
    def update_voice_settings(self, speed: float = 1.0, pitch: int = 0, 
                            language: str = "en") -> None:
        """
        Update voice synthesis settings.
        
        Args:
            speed: Voice speed (0.5 to 2.0)
            pitch: Voice pitch (-12 to 12)
            language: Language code
        """
        self.voice_settings.update({
            "speed": max(0.5, min(2.0, speed)),
            "pitch": max(-12, min(12, pitch)),
            "language": language
        })
        logger.info(f"Updated voice settings: {self.voice_settings}")
    
    def create_audio_file(self, text: str, filename: str = None) -> Optional[str]:
        """
        Create an audio file from text.
        
        Args:
            text: Text to synthesize
            filename: Optional filename for the audio file
            
        Returns:
            Path to created audio file or None if failed
        """
        try:
            if not filename:
                filename = f"tts_output_{hash(text) % 10000}.wav"
            
            # Create temp directory if needed
            temp_dir = Path("temp")
            temp_dir.mkdir(exist_ok=True)
            
            output_path = temp_dir / filename
            
            # Synthesize to file
            result = self.synthesize_text(
                text=text,
                output_path=str(output_path),
                language=self.voice_settings["language"]
            )
            
            if output_path.exists():
                logger.info(f"Created audio file: {output_path}")
                return str(output_path)
            else:
                logger.error("Audio file was not created")
                return None
                
        except Exception as e:
            logger.error(f"Failed to create audio file: {e}")
            return None
    
    def get_audio_bytes(self, text: str) -> Optional[bytes]:
        """
        Get audio data as bytes.
        
        Args:
            text: Text to synthesize
            
        Returns:
            Audio data as bytes or None if failed
        """
        return self.synthesize_text(text=text)
    
    def validate_text(self, text: str) -> bool:
        """
        Validate text for synthesis.
        
        Args:
            text: Text to validate
            
        Returns:
            True if text is valid for synthesis
        """
        if not text or not text.strip():
            return False
        
        # Check text length (reasonable limit)
        if len(text) > 1000:
            return False
        
        # Check for valid characters
        valid_chars = set("abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789 .,!?;:'\"()-")
        text_chars = set(text)
        
        if not text_chars.issubset(valid_chars):
            # Allow some special characters
            special_chars = set("áéíóúñüçàèìòùâêîôûäëïöüß")
            text_chars = text_chars - special_chars
            if not text_chars.issubset(valid_chars):
                return False
        
        return True
    
    def get_supported_languages(self) -> list:
        """
        Get list of supported languages.
        
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
    
    def get_current_settings(self) -> Dict[str, Any]:
        """
        Get current TTS settings.
        
        Returns:
            Dictionary containing current settings
        """
        return {
            "voice_settings": self.voice_settings,
            "voice_cloning_setup": self.voice_cloning_setup,
            "current_voice_model": self.current_voice_model,
            "synthesis_info": self.get_synthesis_info()
        } 