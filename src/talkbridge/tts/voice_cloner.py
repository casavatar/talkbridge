#! /usr/bin/env python3
"""
TalkBridge TTS - Voice Cloner
=============================

Voice cloner module for TalkBridge

Author: TalkBridge Team
Date: 2025-08-19
Version: 1.0

Requirements:
- TTS
======================================================================
Functions:
- __init__: Initialize the voice cloner with a pre-trained model.
- _load_model: Load the TTS model and move it to the appropriate device.
- clone_voice_from_samples: Clone a voice from reference audio samples.
- synthesize_with_cloned_voice: Synthesize speech using the cloned voice.
- get_available_models: Get list of available TTS models.
- get_model_info: Get information about the loaded model.
======================================================================
"""

import os
import logging
import tempfile
import numpy as np
import soundfile as sf
from pathlib import Path
from typing import List, Optional, Union, Tuple
import torch
from talkbridge.logging_config import get_logger
from talkbridge.utils.error_handler import retry_with_backoff, RetryableError, handle_error

try:
    from TTS.api import TTS
    from TTS.tts.configs.xtts_config import XttsConfig
    from TTS.tts.models.xtts import Xtts
    TTS_AVAILABLE = True
except ImportError:
    # Make TTS optional
    TTS = None
    XttsConfig = None
    Xtts = None
    TTS_AVAILABLE = False
    logger = get_logger(__name__) if 'get_logger' in globals() else None
    if logger:
        logger.warning("TTS library not available. Voice cloning features will be disabled.")

from .config import get_config, get_model_config

# Configure logging
# Logging configuration is handled by src/desktop/logging_config.py
# logging.basicConfig(level=logging.INFO)
logger = get_logger(__name__)

class VoiceCloner:
    """
    Voice cloning class using Coqui TTS YourTTS model.
    
    This class provides functionality to:
    - Load a pre-trained voice cloning model
    - Clone voices from reference audio samples
    - Synthesize speech with cloned voices
    """
    
    def __init__(self, model_name: str = None):
        """
        Initialize the voice cloner with a pre-trained model.
        
        Args:
            model_name: Name of the TTS model to use. If None, uses default from config.
        """
        if not TTS_AVAILABLE:
            raise ImportError(
                "TTS library not available. Please install it with: pip install TTS>=0.22.0"
            )
            
        config = get_config()
        self.model_name = model_name or config["default_model"]
        self.config = get_model_config(self.model_name)
        self.tts = None
        
        # Set device based on configuration
        performance_config = config["performance"]
        if performance_config["use_gpu"] and torch.cuda.is_available():
            self.device = "cuda"
        else:
            self.device = "cpu"
            
        self._load_model()
        
    @retry_with_backoff(
        max_retries=3, 
        initial_delay=2.0, 
        max_delay=30.0,
        retryable_exceptions=[RetryableError, RuntimeError, OSError]
    )
    def _load_model(self):
        """Load the TTS model and move it to the appropriate device with retry logic."""
        try:
            logger.info(f"Loading TTS model: {self.model_name}")
            self.tts = TTS(model_name=self.model_name)
            
            # Move model to device
            if hasattr(self.tts, 'synthesizer') and hasattr(self.tts.synthesizer, 'to'):
                self.tts.synthesizer.to(self.device)
            
            logger.info(f"Model loaded successfully on {self.device}")
            
        except (RuntimeError, OSError) as e:
            # These might be retryable (memory issues, temporary file problems)
            error_msg = f"Retryable error loading TTS model: {e}"
            logger.warning(error_msg)
            raise RetryableError(error_msg) from e
        except Exception as e:
            # Non-retryable errors (missing dependencies, etc.)
            error_msg = f"Failed to load TTS model: {e}"
            logger.error(error_msg, exc_info=True)
            raise RuntimeError(f"Could not load TTS model: {e}") from e
    
    def clone_voice_from_samples(self, audio_samples: List[Union[str, Path]], 
                                sample_rate: int = None) -> bool:
        """
        Clone a voice from reference audio samples.
        
        Args:
            audio_samples: List of paths to reference audio files
            sample_rate: Target sample rate for audio processing
            
        Returns:
            bool: True if voice cloning was successful
        """
        if not audio_samples:
            raise ValueError("At least one audio sample is required for voice cloning")
        
        # Get sample rate from config if not provided
        if sample_rate is None:
            config = get_config()
            sample_rate = config["audio"]["sample_rate"]
        
        try:
            # Validate audio files
            valid_samples = []
            voice_cloning_config = get_config()["voice_cloning"]
            
            for sample_path in audio_samples:
                if not os.path.exists(sample_path):
                    logger.warning(f"Audio file not found: {sample_path}")
                    continue
                    
                # Check if file is readable
                try:
                    audio, sr = sf.read(sample_path)
                    min_duration = voice_cloning_config["min_sample_duration"]
                    if len(audio) < sr * min_duration:  # Check minimum duration
                        logger.warning(f"Audio file too short: {sample_path}")
                        continue
                    valid_samples.append(str(sample_path))
                except Exception as e:
                    logger.warning(f"Could not read audio file {sample_path}: {e}")
                    continue
            
            if not valid_samples:
                raise ValueError("No valid audio samples found for voice cloning")
            
            logger.info(f"Using {len(valid_samples)} audio samples for voice cloning")
            
            # Store reference samples for later use
            self.reference_samples = valid_samples
            return True
            
        except Exception as e:
            logger.error(f"Voice cloning failed: {e}")
            return False
    
    def synthesize_with_cloned_voice(self, text: str, 
                                   output_path: Optional[str] = None,
                                   language: str = "en") -> Union[bytes, str]:
        """
        Synthesize speech using the cloned voice.
        
        Args:
            text: Text to synthesize
            output_path: Optional path to save the audio file
            language: Language code for synthesis
            
        Returns:
            bytes or str: Audio data as bytes or file path if output_path is provided
        """
        if not hasattr(self, 'reference_samples') or not self.reference_samples:
            raise RuntimeError("No voice cloned. Call clone_voice_from_samples() first")
        
        try:
            # Use the first reference sample for voice cloning
            reference_sample = self.reference_samples[0]
            
            logger.info(f"Synthesizing text: '{text[:50]}...' with cloned voice")
            
            # Synthesize with cloned voice
            if output_path:
                # Save to file
                self.tts.tts_to_file(
                    text=text,
                    speaker_wav=reference_sample,
                    language=language,
                    file_path=output_path
                )
                logger.info(f"Audio saved to: {output_path}")
                return output_path
            else:
                # Return audio as bytes
                audio_data = self.tts.tts(
                    text=text,
                    speaker_wav=reference_sample,
                    language=language
                )
                
                # Convert to bytes
                with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as temp_file:
                    sf.write(temp_file.name, audio_data, 22050)
                    with open(temp_file.name, 'rb') as f:
                        audio_bytes = f.read()
                    os.unlink(temp_file.name)
                
                logger.info(f"Generated audio: {len(audio_bytes)} bytes")
                return audio_bytes
                
        except Exception as e:
            logger.error(f"Speech synthesis failed: {e}")
            raise RuntimeError(f"Speech synthesis failed: {e}")
    
    def get_available_models(self) -> List[str]:
        """Get list of available TTS models."""
        try:
            return TTS().list_models()
        except Exception as e:
            logger.error(f"Failed to get available models: {e}")
            return []
    
    def get_model_info(self) -> dict:
        """Get information about the loaded model."""
        if not self.tts:
            return {"error": "No model loaded"}
        
        return {
            "model_name": self.model_name,
            "device": self.device,
            "has_cloned_voice": hasattr(self, 'reference_samples'),
            "reference_samples_count": len(self.reference_samples) if hasattr(self, 'reference_samples') else 0
        } 