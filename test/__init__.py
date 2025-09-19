"""
TalkBridge Test Suite

Comprehensive test suite for the TalkBridge AI system.
Tests cover all major components including audio processing, 
transcription, TTS, translation, logging, facial animation, and storage.

Run tests with: python -m unittest discover tests
"""
# Test package initialization
import sys
from pathlib import Path

# Add src to path for testing
src_path = Path(__file__).parent.parent / "src"
if str(src_path) not in sys.path:
    sys.path.insert(0, str(src_path))


import os

# Add src to path for imports
