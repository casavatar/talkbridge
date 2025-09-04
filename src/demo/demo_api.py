#!/usr/bin/env python3
"""
TalkBridge Demo - Demo Api
==========================

Módulo demo_api para TalkBridge

Author: TalkBridge Team
Date: 2025-08-19
Version: 1.0

Requirements:
- PyQt6
======================================================================
Functions:
- get_api_instance: Get API instance based on demo mode.
- get_tts_api: Get TTS API instance.
- get_stt_api: Get STT API instance.
- get_llm_api: Get LLM API instance.
- get_translation_api: Get Translation API instance.
- get_animation_api: Get Animation API instance.
- get_audio_api: Get Audio API instance.
- __init__: Function __init__
- synthesize_voice: Simulate voice synthesis.
- get_synthesis_info: Get demo synthesis information.
======================================================================
"""

import time
import json
from typing import Dict, List, Optional, Any
from pathlib import Path

from .demo_runner import get_demo_runner, DemoRunner
from .demo_config import is_demo_mode, get_demo_setting


class DemoTTsAPI:
    """Demo TTS API wrapper."""
    
    def __init__(self):
        self.demo_runner = get_demo_runner()
    
    def synthesize_voice(self, text: str, output_path: str = None) -> bytes:
        """
        Simulate voice synthesis.
        Args:
            text: Text to synthesize
            output_path: Optional output path (not used in demo)
        Returns:
            Audio data as bytes
        """
        if not is_demo_mode():
            raise RuntimeError("Demo mode not enabled")
        
        return self.demo_runner.simulate_voice_synthesis(text)
    
    def get_synthesis_info(self) -> Dict:
        """Get demo synthesis information."""
        return {
            "model": "demo_tts_model",
            "status": "ready",
            "sample_rate": 22050,
            "channels": 1
        }
    
    def list_available_models(self) -> List[str]:
        """List available demo models."""
        return ["demo_voice_model"]


class DemoSTTAPI:
    """Demo Speech-to-Text API wrapper."""
    
    def __init__(self):
        self.demo_runner = get_demo_runner()
    
    def transcribe_audio(self, audio_data: bytes) -> str:
        """
        Simulate audio transcription.
        Args:
            audio_data: Audio data
        Returns:
            Transcribed text
        """
        if not is_demo_mode():
            raise RuntimeError("Demo mode not enabled")
        
        # Use the new STT module for real transcription in demo mode
        try:
            from src.stt import transcribe_audio as stt_transcribe
            return stt_transcribe(audio_data, language="es")
        except Exception as e:
            # Fallback to simulation if STT module fails
            return self.demo_runner.simulate_transcription(audio_data)
    
    def get_transcription_info(self) -> Dict:
        """Get demo transcription information."""
        return {
            "model": "demo_whisper_model",
            "status": "ready",
            "language": "en"
        }


class DemoLLMAPI:
    """Demo LLM API wrapper."""
    
    def __init__(self):
        self.demo_runner = get_demo_runner()
    
    def generate_response(self, user_message: str, context: str = "") -> str:
        """
        Simulate LLM response generation.
        Args:
            user_message: User input message
            context: Optional context
        Returns:
            AI response
        """
        if not is_demo_mode():
            raise RuntimeError("Demo mode not enabled")
        
        return self.demo_runner.simulate_llm_response(user_message, context)
    
    def chat_conversation(self, messages: List[Dict]) -> str:
        """
        Simulate chat conversation.
        Args:
            messages: List of conversation messages
        Returns:
            AI response
        """
        if not is_demo_mode():
            raise RuntimeError("Demo mode not enabled")
        
        # Get the last user message
        user_message = ""
        for msg in reversed(messages):
            if msg.get("role") == "user":
                user_message = msg.get("content", "")
                break
        
        return self.demo_runner.simulate_llm_response(user_message, "")
    
    def get_model_info(self) -> Dict:
        """Get demo model information."""
        return {
            "model": "demo_llama_model",
            "status": "ready",
            "context_length": 4096
        }


class DemoTranslationAPI:
    """Demo Translation API wrapper."""
    
    def __init__(self):
        self.demo_runner = get_demo_runner()
    
    def translate_text(self, text: str, source_lang: str = "en", target_lang: str = "es") -> str:
        """
        Simulate text translation.
        Args:
            text: Text to translate
            source_lang: Source language
            target_lang: Target language
        Returns:
            Translated text
        """
        if not is_demo_mode():
            raise RuntimeError("Demo mode not enabled")
        
        return self.demo_runner.simulate_translation(text)
    
    def get_supported_languages(self) -> List[str]:
        """Get supported languages."""
        return ["en", "es", "fr", "de"]
    
    def get_translation_info(self) -> Dict:
        """Get demo translation information."""
        return {
            "model": "demo_translation_model",
            "status": "ready",
            "supported_languages": ["en", "es", "fr", "de"]
        }


class DemoAnimationAPI:
    """Demo Animation API wrapper."""
    
    def __init__(self):
        self.demo_runner = get_demo_runner()
    
    def get_avatar_image(self) -> str:
        """
        Get demo avatar image path.
        Returns:
            Path to avatar image
        """
        if not is_demo_mode():
            raise RuntimeError("Demo mode not enabled")
        
        return self.demo_runner.get_avatar_image()
    
    def run_face_sync(self, audio_path: str) -> Dict:
        """
        Simulate face synchronization.
        Args:
            audio_path: Path to audio file
        Returns:
            Animation state dictionary
        """
        if not is_demo_mode():
            raise RuntimeError("Demo mode not enabled")
        
        # Simulate processing delay
        if get_demo_setting("simulate_delays"):
            time.sleep(get_demo_setting("delay_avatar_animation", 0.5))
        
        return {
            "status": "playing",
            "avatar_image": self.demo_runner.get_avatar_image(),
            "audio_sync": True,
            "lip_sync": True,
            "eye_blink": True
        }
    
    def get_animation_info(self) -> Dict:
        """Get demo animation information."""
        return {
            "model": "demo_face_sync_model",
            "status": "ready",
            "fps": 30,
            "resolution": "640x480"
        }


class DemoAudioAPI:
    """Demo Audio API wrapper."""
    
    def __init__(self):
        self.demo_runner = get_demo_runner()
    
    def capture_audio(self, duration: float = 5.0) -> bytes:
        """
        Simulate audio capture.
        Args:
            duration: Recording duration in seconds
        Returns:
            Audio data as bytes
        """
        if not is_demo_mode():
            raise RuntimeError("Demo mode not enabled")
        
        # Simulate recording delay
        if get_demo_setting("simulate_delays"):
            time.sleep(duration)
        
        return self.demo_runner.simulate_audio_capture()
    
    def play_audio(self, audio_data: bytes) -> bool:
        """
        Simulate audio playback.
        Args:
            audio_data: Audio data to play
        Returns:
            Success status
        """
        if not is_demo_mode():
            raise RuntimeError("Demo mode not enabled")
        
        # Simulate playback delay
        if get_demo_setting("simulate_delays"):
            time.sleep(1.0)
        
        return True
    
    def get_audio_info(self) -> Dict:
        """Get demo audio information."""
        return {
            "sample_rate": 44100,
            "channels": 1,
            "format": "wav",
            "status": "ready"
        }


# Factory function to get appropriate API based on demo mode
def get_api_instance(api_type: str):
    """
    Get API instance based on demo mode.
    Args:
        api_type: Type of API ('tts', 'stt', 'llm', 'translation', 'animation', 'audio')
    Returns:
        API instance
    """
    if not is_demo_mode():
        # Return real API instances (import here to avoid circular imports)
        try:
            if api_type == "tts":
                from ..tts.synthesizer import synthesize_voice
                return type('RealTTsAPI', (), {
                    'synthesize_voice': synthesize_voice,
                    'get_synthesis_info': lambda: {"status": "real_mode"},
                    'list_available_models': lambda: ["real_model"]
                })()
            # Add other real API imports as needed
        except ImportError:
            pass
    
    # Return demo API instances
    if api_type == "tts":
        return DemoTTsAPI()
    elif api_type == "stt":
        return DemoSTTAPI()
    elif api_type == "llm":
        return DemoLLMAPI()
    elif api_type == "translation":
        return DemoTranslationAPI()
    elif api_type == "animation":
        return DemoAnimationAPI()
    elif api_type == "audio":
        return DemoAudioAPI()
    else:
        raise ValueError(f"Unknown API type: {api_type}")


# Convenience functions for easy access
def get_tts_api():
    """Get TTS API instance."""
    return get_api_instance("tts")


def get_stt_api():
    """Get STT API instance."""
    return get_api_instance("stt")


def get_llm_api():
    """Get LLM API instance."""
    return get_api_instance("llm")


def get_translation_api():
    """Get Translation API instance."""
    return get_api_instance("translation")


def get_animation_api():
    """Get Animation API instance."""
    return get_api_instance("animation")


def get_audio_api():
    """Get Audio API instance."""
    return get_api_instance("audio")


if __name__ == "__main__":
    # Test demo APIs
    print("Testing Demo APIs...")
    print(f"Demo mode enabled: {is_demo_mode()}")
    
    # Test each API
    apis = {
        "tts": get_tts_api(),
        "stt": get_stt_api(),
        "llm": get_llm_api(),
        "translation": get_translation_api(),
        "animation": get_animation_api(),
        "audio": get_audio_api()
    }
    
    for name, api in apis.items():
        print(f"{name.upper()} API: {type(api).__name__}")
    
    print("Demo APIs initialized successfully!") 