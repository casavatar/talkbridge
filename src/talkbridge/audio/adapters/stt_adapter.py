"""
Speech-to-Text Adapter for TalkBridge

Wraps the existing WhisperEngine class to conform to the STTPort interface.
"""

import logging
import asyncio
import time
from typing import Optional, List, Iterator, Dict, Any
import io
import tempfile
import os

from ..ports import STTPort, AudioData, TranscriptionResult, AudioFormat
from ...utils.language_utils import get_supported_languages

try:
    from ...stt.whisper_engine import WhisperEngine
    WHISPER_AVAILABLE = True
except ImportError:
    WHISPER_AVAILABLE = False

class WhisperSTTAdapter:
    """Adapter that wraps WhisperEngine to implement STTPort."""
    
    def __init__(self, model_size: str = "base", device: str = "auto"):
        """Initialize the Whisper STT adapter.
        
        Args:
            model_size: Whisper model size ("tiny", "base", "small", "medium", "large")
            device: Device to use ("cpu", "cuda", "auto")
        """
        self.logger = logging.getLogger("talkbridge.audio.stt_adapter")
        
        if not WHISPER_AVAILABLE:
            raise ImportError("WhisperEngine module not available")
        
        try:
            self.whisper_engine = WhisperEngine(model_size=model_size, device=device)
            self._current_language = None
            self._supported_languages = get_supported_languages('whisper')
            self.logger.info(f"Initialized Whisper STT adapter with model: {model_size}")
        except Exception as e:
            self.logger.error(f"Failed to initialize WhisperEngine: {e}")
            raise
    
    def transcribe(self, audio_data: AudioData) -> TranscriptionResult:
        """Transcribe audio data to text."""
        start_time = time.time()
        
        try:
            # Convert AudioData to format expected by WhisperEngine
            audio_file_path = self._prepare_audio_file(audio_data)
            
            try:
                # Use WhisperEngine's transcribe method
                result = self.whisper_engine.transcribe(
                    audio_file_path,
                    language=audio_data.language_hint or self._current_language
                )
                
                # Extract text and language from result
                if isinstance(result, dict):
                    text = result.get('text', '').strip()
                    language = result.get('language', audio_data.language_hint or 'en')
                    segments = result.get('segments', [])
                elif isinstance(result, str):
                    text = result.strip()
                    language = audio_data.language_hint or self._current_language or 'en'
                    segments = []
                else:
                    text = str(result).strip()
                    language = audio_data.language_hint or self._current_language or 'en'
                    segments = []
                
                processing_time = time.time() - start_time
                
                return TranscriptionResult(
                    text=text,
                    language=language,
                    confidence=1.0,  # Whisper doesn't provide confidence scores
                    segments=segments,
                    processing_time=processing_time
                )
                
            finally:
                # Clean up temporary file
                if os.path.exists(audio_file_path):
                    os.unlink(audio_file_path)
                    
        except Exception as e:
            self.logger.error(f"Transcription failed: {e}")
            processing_time = time.time() - start_time
            
            return TranscriptionResult(
                text="",
                language=audio_data.language_hint or 'en',
                confidence=0.0,
                processing_time=processing_time
            )
    
    async def transcribe_async(self, audio_data: AudioData) -> TranscriptionResult:
        """Transcribe audio data to text asynchronously."""
        # Run transcription in thread pool to avoid blocking
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(None, self.transcribe, audio_data)
    
    def transcribe_stream(self, audio_stream: Iterator[AudioData]) -> Iterator[TranscriptionResult]:
        """Transcribe streaming audio data."""
        for audio_chunk in audio_stream:
            # For streaming, we could implement buffering or sliding window
            # For now, transcribe each chunk individually
            result = self.transcribe(audio_chunk)
            if result.text.strip():  # Only yield non-empty results
                yield result
    
    def set_language(self, language: str) -> bool:
        """Set the expected language for transcription."""
        if language in self._supported_languages:
            self._current_language = language
            self.logger.info(f"Set transcription language to: {language}")
            return True
        else:
            self.logger.warning(f"Language '{language}' not supported")
            return False
    
    def get_supported_languages(self) -> List[str]:
        """Get list of supported languages."""
        return self._supported_languages.copy()
    
    def is_ready(self) -> bool:
        """Check if the STT engine is ready."""
        return self.whisper_engine is not None
    
    def _prepare_audio_file(self, audio_data: AudioData) -> str:
        """Prepare audio data as a temporary file for WhisperEngine."""
        try:
            # Create temporary file with appropriate extension
            if audio_data.format == AudioFormat.WAV:
                suffix = '.wav'
            elif audio_data.format == AudioFormat.MP3:
                suffix = '.mp3'
            elif audio_data.format == AudioFormat.FLAC:
                suffix = '.flac'
            else:
                suffix = '.wav'  # Default to WAV for PCM data
            
            # Create temporary file
            with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as temp_file:
                if audio_data.format == AudioFormat.PCM:
                    # Convert PCM to WAV format
                    wav_data = self._pcm_to_wav(
                        audio_data.data,
                        audio_data.sample_rate,
                        audio_data.channels
                    )
                    temp_file.write(wav_data)
                else:
                    # Write raw audio data for other formats
                    temp_file.write(audio_data.data)
                
                return temp_file.name
                
        except Exception as e:
            self.logger.error(f"Failed to prepare audio file: {e}")
            raise
    
    def _pcm_to_wav(self, pcm_data: bytes, sample_rate: int, channels: int) -> bytes:
        """Convert PCM data to WAV format."""
        try:
            import wave
            import struct
            
            # Create WAV file in memory
            wav_buffer = io.BytesIO()
            
            with wave.open(wav_buffer, 'wb') as wav_file:
                wav_file.setnchannels(channels)
                wav_file.setsampwidth(2)  # 16-bit samples
                wav_file.setframerate(sample_rate)
                
                # Convert bytes to 16-bit samples if needed
                if len(pcm_data) % 2 != 0:
                    pcm_data = pcm_data[:-1]  # Remove odd byte
                
                wav_file.writeframes(pcm_data)
            
            wav_buffer.seek(0)
            return wav_buffer.read()
            
        except Exception as e:
            self.logger.error(f"PCM to WAV conversion failed: {e}")
            # Return original data as fallback
            return pcm_data