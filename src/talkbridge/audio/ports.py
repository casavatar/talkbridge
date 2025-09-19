"""
Audio Pipeline Ports/Interfaces for TalkBridge

This module defines the port interfaces for the audio pipeline components
using the hexagonal architecture pattern. These protocols ensure clear
separation of concerns and enable testability.
"""

from abc import ABC, abstractmethod
from typing import Protocol, Dict, Any, Optional, List, Iterator, AsyncIterator
from dataclasses import dataclass
from enum import Enum
import asyncio

class AudioFormat(Enum):
    """Supported audio formats."""
    WAV = "wav"
    MP3 = "mp3"
    PCM = "pcm"
    FLAC = "flac"

@dataclass
class AudioData:
    """Container for audio data with metadata."""
    data: bytes
    sample_rate: int
    channels: int
    format: AudioFormat
    source_type: str  # "microphone", "system_audio", "file"
    language_hint: Optional[str] = None
    device_info: Optional[str] = None

@dataclass
class TranscriptionResult:
    """Result from speech-to-text processing."""
    text: str
    language: str
    confidence: float
    segments: Optional[List[Dict[str, Any]]] = None
    processing_time: Optional[float] = None

@dataclass
class TranslationResult:
    """Result from translation processing."""
    original_text: str
    translated_text: str
    source_language: str
    target_language: str
    confidence: float
    processing_time: Optional[float] = None

@dataclass
class SynthesisResult:
    """Result from text-to-speech processing."""
    audio_data: bytes
    sample_rate: int
    format: AudioFormat
    processing_time: Optional[float] = None

@dataclass
class DeviceInfo:
    """Audio device information."""
    index: int
    name: str
    max_input_channels: int
    max_output_channels: int
    default_sample_rate: float
    is_default: bool = False

class AudioCapturePort(Protocol):
    """Port for audio capture functionality."""
    
    @abstractmethod
    def list_devices(self) -> Dict[str, List[DeviceInfo]]:
        """List available audio devices."""
        ...
    
    @abstractmethod
    def start_recording(self, device_index: Optional[int] = None,
                       sample_rate: int = 44100, channels: int = 1) -> bool:
        """Start audio recording from specified device."""
        ...
    
    @abstractmethod
    def stop_recording(self) -> bool:
        """Stop audio recording."""
        ...
    
    @abstractmethod
    def get_audio_chunk(self) -> Optional[AudioData]:
        """Get the next available audio chunk."""
        ...
    
    @abstractmethod
    def is_recording(self) -> bool:
        """Check if currently recording."""
        ...
    
    @abstractmethod
    def test_device_access(self, device_index: Optional[int] = None) -> bool:
        """Test access to audio device."""
        ...

class STTPort(Protocol):
    """Port for Speech-to-Text functionality."""
    
    @abstractmethod
    def transcribe(self, audio_data: AudioData) -> TranscriptionResult:
        """Transcribe audio data to text."""
        ...
    
    @abstractmethod
    async def transcribe_async(self, audio_data: AudioData) -> TranscriptionResult:
        """Transcribe audio data to text asynchronously."""
        ...
    
    @abstractmethod
    def transcribe_stream(self, audio_stream: Iterator[AudioData]) -> Iterator[TranscriptionResult]:
        """Transcribe streaming audio data."""
        ...
    
    @abstractmethod
    def set_language(self, language: str) -> bool:
        """Set the expected language for transcription."""
        ...
    
    @abstractmethod
    def get_supported_languages(self) -> List[str]:
        """Get list of supported languages."""
        ...
    
    @abstractmethod
    def is_ready(self) -> bool:
        """Check if the STT engine is ready."""
        ...

class TranslationPort(Protocol):
    """Port for translation functionality."""
    
    @abstractmethod
    def translate(self, text: str, source_lang: str, target_lang: str) -> TranslationResult:
        """Translate text from source to target language."""
        ...
    
    @abstractmethod
    async def translate_async(self, text: str, source_lang: str, target_lang: str) -> TranslationResult:
        """Translate text asynchronously."""
        ...
    
    @abstractmethod
    def detect_language(self, text: str) -> str:
        """Detect the language of given text."""
        ...
    
    @abstractmethod
    def get_supported_languages(self) -> List[str]:
        """Get list of supported languages."""
        ...
    
    @abstractmethod
    def is_ready(self) -> bool:
        """Check if the translation service is ready."""
        ...

class TTSPort(Protocol):
    """Port for Text-to-Speech functionality."""
    
    @abstractmethod
    def synthesize(self, text: str, language: str = "en", voice: Optional[str] = None) -> SynthesisResult:
        """Synthesize speech from text."""
        ...
    
    @abstractmethod
    async def synthesize_async(self, text: str, language: str = "en", voice: Optional[str] = None) -> SynthesisResult:
        """Synthesize speech from text asynchronously."""
        ...
    
    @abstractmethod
    def get_voices(self, language: Optional[str] = None) -> List[str]:
        """Get available voices for a language."""
        ...
    
    @abstractmethod
    def get_supported_languages(self) -> List[str]:
        """Get list of supported languages."""
        ...
    
    @abstractmethod
    def is_ready(self) -> bool:
        """Check if the TTS engine is ready."""
        ...

class AudioPlayerPort(Protocol):
    """Port for audio playback functionality."""
    
    @abstractmethod
    def play(self, audio_data: AudioData) -> bool:
        """Play audio data."""
        ...
    
    @abstractmethod
    async def play_async(self, audio_data: AudioData) -> bool:
        """Play audio data asynchronously."""
        ...
    
    @abstractmethod
    def stop(self) -> bool:
        """Stop audio playback."""
        ...
    
    @abstractmethod
    def is_playing(self) -> bool:
        """Check if audio is currently playing."""
        ...
    
    @abstractmethod
    def set_volume(self, volume: float) -> bool:
        """Set playback volume (0.0 to 1.0)."""
        ...

class PipelineStatusCallback(Protocol):
    """Callback interface for pipeline status updates."""
    
    def on_status_change(self, component: str, status: str, details: Dict[str, Any]) -> None:
        """Called when pipeline component status changes."""
        ...
    
    def on_error(self, component: str, error: str, details: Dict[str, Any]) -> None:
        """Called when pipeline component encounters an error."""
        ...

class TranscriptCallback(Protocol):
    """Callback interface for transcript events."""
    
    def on_transcript(self, source: str, text: str, language: str, confidence: float = 1.0) -> None:
        """Called when text transcription is complete.
        
        Args:
            source: Audio source identifier ("microphone", "system_audio", etc.)
            text: Transcribed text content
            language: Detected/specified language code
            confidence: Confidence score (0.0 to 1.0)
        """
        ...

class TranslationCallback(Protocol):
    """Callback interface for translation events."""
    
    def on_translation(self, source: str, original_text: str, translated_text: str, 
                      source_lang: str, target_lang: str) -> None:
        """Called when translation is complete.
        
        Args:
            source: Audio source identifier
            original_text: Original transcribed text
            translated_text: Translated text
            source_lang: Source language code
            target_lang: Target language code
        """
        ...

class AudioPipelinePort(Protocol):
    """Port for the main audio pipeline coordination."""
    
    @abstractmethod
    def start_processing(self) -> bool:
        """Start the audio processing pipeline."""
        ...
    
    @abstractmethod
    def stop_processing(self) -> bool:
        """Stop the audio processing pipeline."""
        ...
    
    @abstractmethod
    def start_source(self, source_type: str, device_index: Optional[int] = None,
                    language_hint: Optional[str] = None) -> bool:
        """Start audio capture from a specific source."""
        ...
    
    @abstractmethod
    def stop_source(self, source_type: str) -> bool:
        """Stop audio capture from a specific source."""
        ...
    
    @abstractmethod
    def set_transcript_callback(self, callback: TranscriptCallback) -> None:
        """Set callback for transcript events."""
        ...
    
    @abstractmethod
    def set_translation_callback(self, callback: TranslationCallback) -> None:
        """Set callback for translation events."""
        ...
    
    @abstractmethod
    def set_status_callback(self, callback: PipelineStatusCallback) -> None:
        """Set callback for status updates."""
        ...
    
    @abstractmethod
    def get_status(self) -> Dict[str, Any]:
        """Get current pipeline status."""
        ...
    
    @abstractmethod
    def configure(self, config: Dict[str, Any]) -> bool:
        """Configure pipeline settings."""
        ...