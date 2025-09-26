"""
Text-to-Speech Adapter for TalkBridge

Wraps the existing TTSSynthesizer class to conform to the TTSPort interface.
"""

import logging
import asyncio
import time
from typing import Optional, List
import io

from ..ports import TTSPort, SynthesisResult, AudioFormat
from ...utils.language_utils import get_supported_languages

try:
    from ...tts.synthesizer import synthesize_voice
    TTS_AVAILABLE = True
except Exception:
    # Handle case where module or function doesn't exist
    synthesize_voice = None
    TTS_AVAILABLE = False

class TTSAdapter:
    """Adapter that wraps TTSSynthesizer to implement TTSPort."""
    
    def __init__(self, engine: str = "system", voice: Optional[str] = None):
        """Initialize the TTS adapter.
        
        Args:
            engine: TTS engine to use ("system", "azure", "elevenlabs", etc.)
            voice: Default voice to use
        """
        self.logger = logging.getLogger("talkbridge.audio.tts_adapter")
        
        if not TTS_AVAILABLE or synthesize_voice is None:
            raise ImportError("TTS synthesizer module not available")
        
        # Store configuration since we're using functions instead of a class
        self._engine = engine
        self._default_voice = voice
        self._supported_languages = get_supported_languages('tts')
        self.logger.info(f"Initialized TTS adapter with engine: {engine}")
    
    def synthesize(self, text: str, language: str = "en", voice: Optional[str] = None) -> SynthesisResult:
        """Synthesize speech from text."""
        start_time = time.time()
        
        try:
            # Use the specified voice or fall back to default
            selected_voice = voice or self._default_voice
            
            # Use the synthesize_voice function
            if synthesize_voice is None:
                raise RuntimeError("TTS synthesize function not available")
                
            result = synthesize_voice(
                text=text,
                language=language,
                clone_voice=False  # Use default voice for now
            )
            
            processing_time = time.time() - start_time
            
            # Handle different result formats
            if isinstance(result, dict):
                audio_data = result.get('audio_data', result.get('audio', b''))
                sample_rate = result.get('sample_rate', 22050)
                audio_format = AudioFormat.WAV  # Most TTS engines return WAV
            elif isinstance(result, bytes):
                audio_data = result
                sample_rate = 22050  # Default sample rate
                audio_format = AudioFormat.WAV
            else:
                # Handle file path or other formats
                if isinstance(result, str) and result.endswith('.wav'):
                    # Read audio file
                    with open(result, 'rb') as f:
                        audio_data = f.read()
                    sample_rate = 22050
                    audio_format = AudioFormat.WAV
                else:
                    raise ValueError(f"Unsupported TTS result format: {type(result)}")
            
            return SynthesisResult(
                audio_data=audio_data,
                sample_rate=sample_rate,
                format=audio_format,
                processing_time=processing_time
            )
            
        except Exception as e:
            self.logger.error(f"TTS synthesis failed: {e}")
            processing_time = time.time() - start_time
            
            return SynthesisResult(
                audio_data=b'',
                sample_rate=22050,
                format=AudioFormat.WAV,
                processing_time=processing_time
            )
    
    async def synthesize_async(self, text: str, language: str = "en", voice: Optional[str] = None) -> SynthesisResult:
        """Synthesize speech from text asynchronously."""
        # Run synthesis in thread pool to avoid blocking
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(None, self.synthesize, text, language, voice)
    
    def get_voices(self, language: Optional[str] = None) -> List[str]:
        """Get available voices for a language."""
        try:
            # Since we're using function-based TTS, return default voices
            return self._get_default_voices(language)
                
        except Exception as e:
            self.logger.error(f"Failed to get voices: {e}")
            return self._get_default_voices(language)
    
    def get_supported_languages(self) -> List[str]:
        """Get list of supported languages."""
        return self._supported_languages.copy()
    
    def is_ready(self) -> bool:
        """Check if the TTS engine is ready."""
        try:
            # Test with a simple synthesis
            test_result = self.synthesize("test", "en")
            return len(test_result.audio_data) > 0
        except Exception:
            return False
    
    def _get_default_voices(self, language: Optional[str] = None) -> List[str]:
        """Get default voice names for common languages."""
        default_voices = {
            'en': ['Microsoft David', 'Microsoft Zira', 'Microsoft Mark'],
            'es': ['Microsoft Helena', 'Microsoft Laura', 'Microsoft Pablo'],
            'fr': ['Microsoft Hortense', 'Microsoft Julie', 'Microsoft Paul'],
            'de': ['Microsoft Katja', 'Microsoft Hedda', 'Microsoft Stefan'],
            'it': ['Microsoft Elsa', 'Microsoft Cosimo'],
            'pt': ['Microsoft Helia', 'Microsoft Daniel'],
            'ru': ['Microsoft Irina', 'Microsoft Pavel'],
            'ja': ['Microsoft Haruka', 'Microsoft Ichiro'],
            'ko': ['Microsoft Heami'],
            'zh': ['Microsoft Huihui', 'Microsoft Kangkang']
        }
        
        if language and language in default_voices:
            return default_voices[language]
        elif language:
            return [f"Default {language.upper()} Voice"]
        else:
            # Return all available voices
            all_voices = []
            for voices in default_voices.values():
                all_voices.extend(voices)
            return all_voices