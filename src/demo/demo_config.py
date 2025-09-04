#!/usr/bin/env python3
"""
TalkBridge Demo - Demo Config
=============================

Module configuration

Author: TalkBridge Team
Date: 2025-08-19
Version: 1.0

Requirements:
- PyQt6
======================================================================
Functions:
- is_demo_mode: Check if demo mode is enabled.
- get_demo_setting: Get a demo setting value.
- get_demo_file_path: Get the full path to a demo file.
- ensure_demo_files_exist: Ensure all demo files exist, create placeholder files if missing.
======================================================================
"""

import os
from pathlib import Path

# Demo mode flag - set to True to enable demo mode
DEMO_MODE = True

# Demo mode settings
DEMO_SETTINGS = {
    "enabled": DEMO_MODE,
    "simulate_delays": True,
    "delay_audio_processing": 1.5,  # seconds
    "delay_transcription": 2.0,     # seconds
    "delay_translation": 1.0,       # seconds
    "delay_llm_response": 3.0,      # seconds
    "delay_voice_synthesis": 2.5,   # seconds
    "delay_avatar_animation": 0.5,  # seconds
}

# Demo file paths
DEMO_DIR = Path(__file__).parent / "samples"
DEMO_FILES = {
    "input_audio": DEMO_DIR / "input_audio.wav",
    "transcribed_text": DEMO_DIR / "transcribed.txt",
    "translation": DEMO_DIR / "translation.txt",
    "llm_response": DEMO_DIR / "response.txt",
    "voice_output": DEMO_DIR / "voice_output.wav",
    "avatar_image": DEMO_DIR / "mock_avatar.jpg",
    "conversation_log": DEMO_DIR / "conversation_log.jsonl"
}

# Demo conversation flow
DEMO_CONVERSATION_FLOW = [
    {
        "step": "user_input",
        "description": "User speaks into microphone",
        "file": "input_audio.wav",
        "delay": 0.0
    },
    {
        "step": "transcription",
        "description": "Speech-to-text processing",
        "file": "transcribed.txt",
        "delay": 2.0
    },
    {
        "step": "translation",
        "description": "English to Spanish translation",
        "file": "translation.txt",
        "delay": 1.0
    },
    {
        "step": "llm_response",
        "description": "AI generates response",
        "file": "response.txt",
        "delay": 3.0
    },
    {
        "step": "voice_synthesis",
        "description": "Text-to-speech synthesis",
        "file": "voice_output.wav",
        "delay": 2.5
    },
    {
        "step": "avatar_animation",
        "description": "Avatar lip sync and animation",
        "file": "mock_avatar.jpg",
        "delay": 0.5
    }
]

def is_demo_mode() -> bool:
    """Check if demo mode is enabled."""
    return DEMO_MODE

def get_demo_setting(key: str, default=None):
    """Get a demo setting value."""
    return DEMO_SETTINGS.get(key, default)

def get_demo_file_path(file_key: str) -> str:
    """Get the full path to a demo file."""
    return str(DEMO_FILES.get(file_key, ""))

def ensure_demo_files_exist():
    """Ensure all demo files exist, create placeholder files if missing."""
    for key, file_path in DEMO_FILES.items():
        if not file_path.exists():
            file_path.parent.mkdir(parents=True, exist_ok=True)
            if file_path.suffix == '.txt':
                # Create placeholder text files
                placeholder_content = f"Demo {key.replace('_', ' ').title()}"
                file_path.write_text(placeholder_content)
            elif file_path.suffix == '.wav':
                # Create placeholder audio file (1 second of silence)
                import wave
                import struct
                with wave.open(str(file_path), 'w') as wav_file:
                    wav_file.setnchannels(1)
                    wav_file.setsampwidth(2)
                    wav_file.setframerate(44100)
                    # 1 second of silence
                    silence = struct.pack('<h', 0) * 44100
                    wav_file.writeframes(silence)
            elif file_path.suffix == '.jpg':
                # Create placeholder image
                from PIL import Image
                img = Image.new('RGB', (200, 200), color='gray')
                img.save(file_path)
            elif file_path.suffix == '.jsonl':
                # Create placeholder conversation log
                import json
                placeholder_log = [
                    {"timestamp": "2024-01-01 12:00:00", "user": "demo", "message": "Hello", "translation": "Hola", "response": "Hi there!", "audio_file": "demo_audio.wav"}
                ]
                with open(file_path, 'w') as f:
                    for entry in placeholder_log:
                        f.write(json.dumps(entry) + '\n')

if __name__ == "__main__":
    # Create demo files if they don't exist
    ensure_demo_files_exist()
    print("Demo configuration loaded successfully!")
    print(f"Demo mode: {'ENABLED' if DEMO_MODE else 'DISABLED'}") 