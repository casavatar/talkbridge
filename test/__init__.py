"""
TalkBridge Test Suite

Comprehensive test suite for the TalkBridge AI system.
Tests cover all major components including audio processing, 
transcription, TTS, translation, logging, facial animation, and storage.

Run tests with: python -m unittest discover tests
"""

import sys
import os
from pathlib import Path

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent / "src")) 