#! /usr/bin/env python3
"""
TalkBridge TTS - Synthesizer
============================

Módulo synthesizer para TalkBridge

Author: TalkBridge Team
Date: 2025-08-19
Version: 1.0

Requirements:
- TTS
======================================================================
Functions:
- _get_voice_cloner: Get or create a global voice cloner instance.
- synthesize_voice: Main function to synthesize speech from text using voice cloning.
- _synthesize_default_voice: Synthesize speech using the default voice (no cloning).
- setup_voice_cloning: Set up voice cloning with reference samples.
- get_synthesis_info: Get information about the current synthesis setup.
- list_available_models: Get list of available TTS models.
======================================================================
"""

import os
import logging
import tempfile
from pathlib import Path
from typing import List, Optional, Union
import soundfile as sf

from .voice_cloner import VoiceCloner
from .config import get_config, AUDIO_CONFIG

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Global voice cloner instance for caching
_voice_cloner = None


def _get_voice_cloner() -> VoiceCloner:
    """
    Get or create a global voice cloner instance.
    
    Returns:
        VoiceCloner: The voice cloner instance
    """
    global _voice_cloner
    if _voice_cloner is None:
        _voice_cloner = VoiceCloner()
    return _voice_cloner


def synthesize_voice(text: str, 
                    output_path: Optional[str] = None,
                    reference_samples: Optional[List[Union[str, Path]]] = None,
                    language: str = "en",
                    clone_voice: bool = True) -> Union[bytes, str]:
    """
    Main function to synthesize speech from text using voice cloning.
    
    This function provides a high-level interface for text-to-speech synthesis
    with optional voice cloning capabilities. It can work with or without
    voice cloning depending on the parameters provided.
    
    Args:
        text: Text to synthesize into speech
        output_path: Optional path to save the audio file. If None, returns audio as bytes
        reference_samples: List of audio file paths for voice cloning. If None, uses default voice
        language: Language code for synthesis (default: "en")
        clone_voice: Whether to use voice cloning (default: True)
        
    Returns:
        Union[bytes, str]: Audio data as bytes or file path if output_path is provided
        
    Raises:
        ValueError: If text is empty or invalid
        RuntimeError: If synthesis fails
        FileNotFoundError: If reference samples are not found
    """
    # Input validation
    if not text or not text.strip():
        raise ValueError("Text cannot be empty")
    
    if len(text.strip()) == 0:
        raise ValueError("Text cannot be empty or whitespace only")
    
    try:
        # Get voice cloner instance
        voice_cloner = _get_voice_cloner()
        
        # Handle voice cloning if requested
        if clone_voice and reference_samples:
            logger.info("Setting up voice cloning with provided samples")
            success = voice_cloner.clone_voice_from_samples(reference_samples)
            if not success:
                logger.warning("Voice cloning failed, falling back to default voice")
                clone_voice = False
        
        # Synthesize speech
        if clone_voice and hasattr(voice_cloner, 'reference_samples'):
            # Use cloned voice
            logger.info("Synthesizing with cloned voice")
            result = voice_cloner.synthesize_with_cloned_voice(
                text=text,
                output_path=output_path,
                language=language
            )
        else:
            # Use default voice (no cloning)
            logger.info("Synthesizing with default voice")
            result = _synthesize_default_voice(
                text=text,
                output_path=output_path,
                language=language,
                voice_cloner=voice_cloner
            )
        
        logger.info(f"Successfully synthesized {len(text)} characters")
        return result
        
    except Exception as e:
        logger.error(f"Speech synthesis failed: {e}")
        raise RuntimeError(f"Speech synthesis failed: {e}")


def _synthesize_default_voice(text: str,
                             output_path: Optional[str] = None,
                             language: str = "en",
                             voice_cloner: VoiceCloner = None) -> Union[bytes, str]:
    """
    Synthesize speech using the default voice (no cloning).
    
    Args:
        text: Text to synthesize
        output_path: Optional path to save the audio file
        language: Language code for synthesis
        voice_cloner: Voice cloner instance
        
    Returns:
        Union[bytes, str]: Audio data as bytes or file path
    """
    if voice_cloner is None:
        voice_cloner = _get_voice_cloner()
    
    try:
        if output_path:
            # Save to file
            voice_cloner.tts.tts_to_file(
                text=text,
                language=language,
                file_path=output_path
            )
            logger.info(f"Audio saved to: {output_path}")
            return output_path
        else:
            # Return audio as bytes
            audio_data = voice_cloner.tts.tts(
                text=text,
                language=language
            )
            
            # Convert to bytes
            with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as temp_file:
                sf.write(temp_file.name, audio_data, AUDIO_CONFIG["sample_rate"])
                with open(temp_file.name, 'rb') as f:
                    audio_bytes = f.read()
                os.unlink(temp_file.name)
            
            logger.info(f"Generated audio: {len(audio_bytes)} bytes")
            return audio_bytes
            
    except Exception as e:
        logger.error(f"Default voice synthesis failed: {e}")
        raise RuntimeError(f"Default voice synthesis failed: {e}")


def setup_voice_cloning(reference_samples: List[Union[str, Path]]) -> bool:
    """
    Set up voice cloning with reference samples.
    
    This function can be called before synthesize_voice to pre-configure
    voice cloning, which can improve performance for multiple synthesis calls.
    
    Args:
        reference_samples: List of audio file paths for voice cloning
        
    Returns:
        bool: True if voice cloning setup was successful
    """
    try:
        voice_cloner = _get_voice_cloner()
        return voice_cloner.clone_voice_from_samples(reference_samples)
    except Exception as e:
        logger.error(f"Voice cloning setup failed: {e}")
        return False


def get_synthesis_info() -> dict:
    """
    Get information about the current synthesis setup.
    
    Returns:
        dict: Information about the voice cloner and synthesis capabilities
    """
    try:
        voice_cloner = _get_voice_cloner()
        return voice_cloner.get_model_info()
    except Exception as e:
        logger.error(f"Failed to get synthesis info: {e}")
        return {"error": str(e)}


def list_available_models() -> List[str]:
    """
    Get list of available TTS models.
    
    Returns:
        List[str]: List of available model names
    """
    try:
        voice_cloner = _get_voice_cloner()
        return voice_cloner.get_available_models()
    except Exception as e:
        logger.error(f"Failed to get available models: {e}")
        return [] 