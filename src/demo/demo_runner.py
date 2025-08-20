#!/usr/bin/env python3
"""
TalkBridge Demo - Demo Runner
=============================

Módulo demo_runner para TalkBridge

Author: TalkBridge Team
Date: 2025-08-19
Version: 1.0

Requirements:
- PyQt6
======================================================================
Functions:
- get_demo_runner: Get the global demo runner instance.
- run_demo_conversation: Run a demo conversation and return results.
- __init__: Initialize the demo runner.
- _load_conversation_log: Load existing conversation log from demo files.
- register_callback: Register a callback function for a specific step.
- simulate_audio_capture: Simulate audio capture by reading from demo file.
- simulate_transcription: Simulate speech-to-text transcription.
- simulate_translation: Simulate English to Spanish translation.
- simulate_llm_response: Simulate LLM response generation.
- simulate_voice_synthesis: Simulate text-to-speech synthesis.
======================================================================
"""

import time
import json
import wave
import base64
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Tuple
import threading

from .demo_config import (
    is_demo_mode, get_demo_setting, get_demo_file_path,
    DEMO_CONVERSATION_FLOW, ensure_demo_files_exist
)

# Import error handler for logging
try:
    from ..utils.error_handler import ErrorHandler
except ImportError:
    # Fallback if error handler not available
    class ErrorHandler:
        @staticmethod
        def log_error(error, context=""):
            print(f"ERROR [{context}]: {error}")
        @staticmethod
        def format_error(error, context=""):
            return f"Error in {context}: {error}"


class DemoRunner:
    """
    Demo runner that simulates the full TalkBridge system.
    Provides mock implementations for all major components.
    """

    def __init__(self):
        """Initialize the demo runner."""
        self.current_step = 0
        self.conversation_history = []
        self.is_running = False
        self.callback_functions = {}
        
        # Ensure demo files exist
        ensure_demo_files_exist()
        
        # Load demo conversation log
        self._load_conversation_log()

    def _load_conversation_log(self):
        """Load existing conversation log from demo files."""
        log_file = get_demo_file_path("conversation_log")
        try:
            with open(log_file, 'r', encoding='utf-8') as f:
                for line in f:
                    if line.strip():
                        self.conversation_history.append(json.loads(line))
        except FileNotFoundError:
            # Create default conversation entry
            self.conversation_history = [{
                "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "user": "demo_user",
                "message": "Hello, how are you?",
                "translation": "Hola, ¿cómo estás?",
                "response": "I'm doing well, thank you for asking! How can I help you today?",
                "audio_file": "demo_voice_output.wav"
            }]

    def register_callback(self, step: str, callback_func):
        """Register a callback function for a specific step."""
        self.callback_functions[step] = callback_func

    def simulate_audio_capture(self) -> bytes:
        """
        Simulate audio capture by reading from demo file.
        Returns:
            Audio data as bytes
        """
        try:
            audio_file = get_demo_file_path("input_audio")
            with open(audio_file, 'rb') as f:
                return f.read()
        except Exception as e:
            ErrorHandler.log_error(e, "demo_audio_capture")
            # Return empty audio data
            return b''

    def simulate_transcription(self, audio_data: bytes) -> str:
        """
        Simulate speech-to-text transcription.
        Args:
            audio_data: Audio data (not used in demo)
        Returns:
            Transcribed text
        """
        try:
            # Simulate processing delay
            if get_demo_setting("simulate_delays"):
                time.sleep(get_demo_setting("delay_transcription", 2.0))
            
            # Read from demo file
            transcript_file = get_demo_file_path("transcribed_text")
            with open(transcript_file, 'r', encoding='utf-8') as f:
                return f.read().strip()
        except Exception as e:
            ErrorHandler.log_error(e, "demo_transcription")
            return "Hello, how are you?"

    def simulate_translation(self, text: str) -> str:
        """
        Simulate English to Spanish translation.
        Args:
            text: English text to translate
        Returns:
            Spanish translation
        """
        try:
            # Simulate processing delay
            if get_demo_setting("simulate_delays"):
                time.sleep(get_demo_setting("delay_translation", 1.0))
            
            # Read from demo file
            translation_file = get_demo_file_path("translation")
            with open(translation_file, 'r', encoding='utf-8') as f:
                return f.read().strip()
        except Exception as e:
            ErrorHandler.log_error(e, "demo_translation")
            return "Hola, ¿cómo estás?"

    def simulate_llm_response(self, user_message: str, translation: str) -> str:
        """
        Simulate LLM response generation.
        Args:
            user_message: Original user message
            translation: Spanish translation
        Returns:
            AI response
        """
        try:
            # Simulate processing delay
            if get_demo_setting("simulate_delays"):
                time.sleep(get_demo_setting("delay_llm_response", 3.0))
            
            # Read from demo file
            response_file = get_demo_file_path("llm_response")
            with open(response_file, 'r', encoding='utf-8') as f:
                return f.read().strip()
        except Exception as e:
            ErrorHandler.log_error(e, "demo_llm_response")
            return "I'm doing well, thank you for asking! How can I help you today?"

    def simulate_voice_synthesis(self, text: str) -> bytes:
        """
        Simulate text-to-speech synthesis.
        Args:
            text: Text to synthesize
        Returns:
            Audio data as bytes
        """
        try:
            # Simulate processing delay
            if get_demo_setting("simulate_delays"):
                time.sleep(get_demo_setting("delay_voice_synthesis", 2.5))
            
            # Read from demo file
            voice_file = get_demo_file_path("voice_output")
            with open(voice_file, 'rb') as f:
                return f.read()
        except Exception as e:
            ErrorHandler.log_error(e, "demo_voice_synthesis")
            # Return empty audio data
            return b''

    def get_avatar_image(self) -> str:
        """
        Get the demo avatar image path.
        Returns:
            Path to avatar image
        """
        try:
            avatar_file = get_demo_file_path("avatar_image")
            return avatar_file
        except Exception as e:
            ErrorHandler.log_error(e, "demo_avatar_image")
            return ""

    def run_full_conversation(self) -> Dict:
        """
        Run a complete simulated conversation.
        Returns:
            Dictionary with conversation results
        """
        if not is_demo_mode():
            raise RuntimeError("Demo mode is not enabled")

        self.is_running = True
        results = {
            "user_input": "",
            "transcription": "",
            "translation": "",
            "llm_response": "",
            "voice_audio": b"",
            "avatar_image": "",
            "conversation_log": []
        }

        try:
            # Step 1: Simulate audio capture
            if "user_input" in self.callback_functions:
                self.callback_functions["user_input"]("Simulating audio capture...")
            
            audio_data = self.simulate_audio_capture()
            results["user_input"] = "Demo audio input"

            # Step 2: Simulate transcription
            if "transcription" in self.callback_functions:
                self.callback_functions["transcription"]("Processing speech...")
            
            transcription = self.simulate_transcription(audio_data)
            results["transcription"] = transcription

            # Step 3: Simulate translation
            if "translation" in self.callback_functions:
                self.callback_functions["translation"]("Translating to Spanish...")
            
            translation = self.simulate_translation(transcription)
            results["translation"] = translation

            # Step 4: Simulate LLM response
            if "llm_response" in self.callback_functions:
                self.callback_functions["llm_response"]("Generating AI response...")
            
            llm_response = self.simulate_llm_response(transcription, translation)
            results["llm_response"] = llm_response

            # Step 5: Simulate voice synthesis
            if "voice_synthesis" in self.callback_functions:
                self.callback_functions["voice_synthesis"]("Synthesizing voice...")
            
            voice_audio = self.simulate_voice_synthesis(llm_response)
            results["voice_audio"] = voice_audio

            # Step 6: Get avatar image
            avatar_image = self.get_avatar_image()
            results["avatar_image"] = avatar_image

            # Update conversation history
            conversation_entry = {
                "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "user": "demo_user",
                "message": transcription,
                "translation": translation,
                "response": llm_response,
                "audio_file": "demo_voice_output.wav"
            }
            self.conversation_history.append(conversation_entry)
            results["conversation_log"] = self.conversation_history

            # Save updated conversation log
            self._save_conversation_log()

        except Exception as e:
            ErrorHandler.log_error(e, "demo_full_conversation")
            results["error"] = ErrorHandler.format_error(e, "Demo Runner")

        finally:
            self.is_running = False

        return results

    def _save_conversation_log(self):
        """Save conversation history to demo log file."""
        try:
            log_file = get_demo_file_path("conversation_log")
            with open(log_file, 'w', encoding='utf-8') as f:
                for entry in self.conversation_history:
                    f.write(json.dumps(entry) + '\n')
        except Exception as e:
            ErrorHandler.log_error(e, "demo_save_conversation_log")

    def get_conversation_history(self) -> List[Dict]:
        """Get the conversation history."""
        return self.conversation_history

    def reset_demo(self):
        """Reset the demo state."""
        self.current_step = 0
        self.conversation_history = []
        self.is_running = False

    def is_demo_mode_enabled(self) -> bool:
        """Check if demo mode is enabled."""
        return is_demo_mode()


# Global demo runner instance
demo_runner = DemoRunner()


def get_demo_runner() -> DemoRunner:
    """Get the global demo runner instance."""
    return demo_runner


def run_demo_conversation() -> Dict:
    """
    Run a demo conversation and return results.
    Returns:
        Dictionary with conversation results
    """
    return demo_runner.run_full_conversation()


if __name__ == "__main__":
    # Test the demo runner
    print("Testing Demo Runner...")
    print(f"Demo mode enabled: {is_demo_mode()}")
    
    # Run a test conversation
    results = run_demo_conversation()
    print("Demo conversation completed!")
    print(f"Results: {list(results.keys())}") 