#!/usr/bin/env python3
"""
Demo Module Tests

Unit tests for the TalkBridge demo module components.
Tests demo configuration, runner, APIs, and UI components.

Author: TalkBridge Team
Date: 2024-01-01
Version: 1.0.0
"""

import unittest
import tempfile
import os
import json
import time
from pathlib import Path
from unittest.mock import patch, MagicMock

# Add src to path for imports
import sys
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from demo.demo_config import (
    is_demo_mode, get_demo_setting, get_demo_file_path,
    DEMO_MODE, DEMO_SETTINGS, DEMO_FILES, ensure_demo_files_exist
)

from demo.demo_runner import (
    DemoRunner, get_demo_runner, run_demo_conversation
)

from demo.demo_api import (
    DemoTTsAPI, DemoSTTAPI, DemoLLMAPI, DemoTranslationAPI,
    DemoAnimationAPI, DemoAudioAPI,
    get_api_instance, get_tts_api, get_stt_api, get_llm_api,
    get_translation_api, get_animation_api, get_audio_api
)


class TestDemoConfig(unittest.TestCase):
    """Test demo configuration functionality."""
    
    def test_is_demo_mode(self):
        """Test demo mode detection."""
        # Should return the value of DEMO_MODE
        result = is_demo_mode()
        self.assertIsInstance(result, bool)
    
    def test_get_demo_setting(self):
        """Test getting demo settings."""
        # Test existing setting
        enabled = get_demo_setting("enabled")
        self.assertIsInstance(enabled, bool)
        
        # Test non-existent setting with default
        default_value = get_demo_setting("non_existent", "default")
        self.assertEqual(default_value, "default")
    
    def test_get_demo_file_path(self):
        """Test getting demo file paths."""
        # Test existing file key
        path = get_demo_file_path("input_audio")
        self.assertIsInstance(path, str)
        self.assertTrue(path.endswith("input_audio.wav"))
        
        # Test non-existent file key
        path = get_demo_file_path("non_existent")
        self.assertEqual(path, "")
    
    def test_ensure_demo_files_exist(self):
        """Test demo file creation."""
        with tempfile.TemporaryDirectory() as temp_dir:
            # Mock the demo directory
            with patch('demo.demo_config.DEMO_DIR', Path(temp_dir)):
                ensure_demo_files_exist()
                
                # Check that files were created
                for key, file_path in DEMO_FILES.items():
                    if hasattr(file_path, 'exists'):
                        # This would be a real path object
                        pass
                    else:
                        # This is a string path
                        path = Path(temp_dir) / f"{key}.txt"
                        if path.suffix == '.txt':
                            self.assertTrue(path.exists())


class TestDemoRunner(unittest.TestCase):
    """Test demo runner functionality."""
    
    def setUp(self):
        """Set up test environment."""
        self.temp_dir = tempfile.mkdtemp()
        self.demo_runner = DemoRunner()
    
    def tearDown(self):
        """Clean up test environment."""
        import shutil
        shutil.rmtree(self.temp_dir, ignore_errors=True)
    
    def test_demo_runner_initialization(self):
        """Test demo runner initialization."""
        self.assertIsInstance(self.demo_runner, DemoRunner)
        self.assertEqual(self.demo_runner.current_step, 0)
        self.assertIsInstance(self.demo_runner.conversation_history, list)
        self.assertFalse(self.demo_runner.is_running)
    
    def test_simulate_audio_capture(self):
        """Test audio capture simulation."""
        with patch('demo.demo_runner.get_demo_file_path') as mock_get_path:
            mock_get_path.return_value = os.path.join(self.temp_dir, "test_audio.wav")
            
            # Create a test audio file
            with open(mock_get_path.return_value, 'wb') as f:
                f.write(b'test_audio_data')
            
            result = self.demo_runner.simulate_audio_capture()
            self.assertIsInstance(result, bytes)
    
    def test_simulate_transcription(self):
        """Test transcription simulation."""
        with patch('demo.demo_runner.get_demo_file_path') as mock_get_path:
            mock_get_path.return_value = os.path.join(self.temp_dir, "test_transcript.txt")
            
            # Create a test transcript file
            with open(mock_get_path.return_value, 'w') as f:
                f.write("Hello, how are you?")
            
            result = self.demo_runner.simulate_transcription(b'audio_data')
            self.assertIsInstance(result, str)
            self.assertEqual(result, "Hello, how are you?")
    
    def test_simulate_translation(self):
        """Test translation simulation."""
        with patch('demo.demo_runner.get_demo_file_path') as mock_get_path:
            mock_get_path.return_value = os.path.join(self.temp_dir, "test_translation.txt")
            
            # Create a test translation file
            with open(mock_get_path.return_value, 'w') as f:
                f.write("Hola, ¿cómo estás?")
            
            result = self.demo_runner.simulate_translation("Hello, how are you?")
            self.assertIsInstance(result, str)
            self.assertEqual(result, "Hola, ¿cómo estás?")
    
    def test_simulate_llm_response(self):
        """Test LLM response simulation."""
        with patch('demo.demo_runner.get_demo_file_path') as mock_get_path:
            mock_get_path.return_value = os.path.join(self.temp_dir, "test_response.txt")
            
            # Create a test response file
            with open(mock_get_path.return_value, 'w') as f:
                f.write("I'm doing well, thank you!")
            
            result = self.demo_runner.simulate_llm_response("Hello", "Hola")
            self.assertIsInstance(result, str)
            self.assertEqual(result, "I'm doing well, thank you!")
    
    def test_simulate_voice_synthesis(self):
        """Test voice synthesis simulation."""
        with patch('demo.demo_runner.get_demo_file_path') as mock_get_path:
            mock_get_path.return_value = os.path.join(self.temp_dir, "test_voice.wav")
            
            # Create a test voice file
            with open(mock_get_path.return_value, 'wb') as f:
                f.write(b'test_voice_data')
            
            result = self.demo_runner.simulate_voice_synthesis("Hello world")
            self.assertIsInstance(result, bytes)
    
    def test_get_avatar_image(self):
        """Test avatar image retrieval."""
        with patch('demo.demo_runner.get_demo_file_path') as mock_get_path:
            mock_get_path.return_value = os.path.join(self.temp_dir, "test_avatar.jpg")
            
            result = self.demo_runner.get_avatar_image()
            self.assertIsInstance(result, str)
            self.assertEqual(result, os.path.join(self.temp_dir, "test_avatar.jpg"))
    
    def test_run_full_conversation(self):
        """Test full conversation simulation."""
        # Mock demo mode to be enabled
        with patch('demo.demo_runner.is_demo_mode', return_value=True):
            # Mock all file operations
            with patch('demo.demo_runner.get_demo_file_path') as mock_get_path:
                mock_get_path.side_effect = lambda key: os.path.join(self.temp_dir, f"test_{key}.txt")
                
                # Create test files
                test_files = {
                    "input_audio": "test_audio.wav",
                    "transcribed_text": "Hello, how are you?",
                    "translation": "Hola, ¿cómo estás?",
                    "llm_response": "I'm doing well, thank you!",
                    "voice_output": "test_voice.wav",
                    "avatar_image": "test_avatar.jpg"
                }
                
                for key, content in test_files.items():
                    file_path = os.path.join(self.temp_dir, f"test_{key}.txt")
                    if key.endswith('.wav'):
                        with open(file_path, 'wb') as f:
                            f.write(b'test_data')
                    else:
                        with open(file_path, 'w') as f:
                            f.write(content)
                
                result = self.demo_runner.run_full_conversation()
                
                self.assertIsInstance(result, dict)
                self.assertIn("transcription", result)
                self.assertIn("translation", result)
                self.assertIn("llm_response", result)
                self.assertIn("voice_audio", result)
                self.assertIn("avatar_image", result)
    
    def test_get_conversation_history(self):
        """Test conversation history retrieval."""
        history = self.demo_runner.get_conversation_history()
        self.assertIsInstance(history, list)
    
    def test_reset_demo(self):
        """Test demo reset functionality."""
        # Set some state
        self.demo_runner.current_step = 5
        self.demo_runner.conversation_history = [{"test": "data"}]
        self.demo_runner.is_running = True
        
        # Reset
        self.demo_runner.reset_demo()
        
        # Check reset
        self.assertEqual(self.demo_runner.current_step, 0)
        self.assertEqual(self.demo_runner.conversation_history, [])
        self.assertFalse(self.demo_runner.is_running)


class TestDemoAPI(unittest.TestCase):
    """Test demo API wrappers."""
    
    def setUp(self):
        """Set up test environment."""
        self.temp_dir = tempfile.mkdtemp()
    
    def tearDown(self):
        """Clean up test environment."""
        import shutil
        shutil.rmtree(self.temp_dir, ignore_errors=True)
    
    def test_demo_tts_api(self):
        """Test demo TTS API."""
        api = DemoTTsAPI()
        
        # Test synthesize_voice
        with patch('demo.demo_api.is_demo_mode', return_value=True):
            with patch.object(api.demo_runner, 'simulate_voice_synthesis') as mock_synth:
                mock_synth.return_value = b'test_audio'
                result = api.synthesize_voice("Hello world")
                self.assertEqual(result, b'test_audio')
        
        # Test get_synthesis_info
        info = api.get_synthesis_info()
        self.assertIsInstance(info, dict)
        self.assertIn("model", info)
        self.assertIn("status", info)
        
        # Test list_available_models
        models = api.list_available_models()
        self.assertIsInstance(models, list)
    
    def test_demo_stt_api(self):
        """Test demo STT API."""
        api = DemoSTTAPI()
        
        # Test transcribe_audio
        with patch('demo.demo_api.is_demo_mode', return_value=True):
            with patch.object(api.demo_runner, 'simulate_transcription') as mock_trans:
                mock_trans.return_value = "Hello world"
                result = api.transcribe_audio(b'audio_data')
                self.assertEqual(result, "Hello world")
        
        # Test get_transcription_info
        info = api.get_transcription_info()
        self.assertIsInstance(info, dict)
        self.assertIn("model", info)
        self.assertIn("status", info)
    
    def test_demo_llm_api(self):
        """Test demo LLM API."""
        api = DemoLLMAPI()
        
        # Test generate_response
        with patch('demo.demo_api.is_demo_mode', return_value=True):
            with patch.object(api.demo_runner, 'simulate_llm_response') as mock_llm:
                mock_llm.return_value = "I'm doing well!"
                result = api.generate_response("Hello", "context")
                self.assertEqual(result, "I'm doing well!")
        
        # Test chat_conversation
        messages = [{"role": "user", "content": "Hello"}]
        with patch('demo.demo_api.is_demo_mode', return_value=True):
            with patch.object(api.demo_runner, 'simulate_llm_response') as mock_llm:
                mock_llm.return_value = "Hi there!"
                result = api.chat_conversation(messages)
                self.assertEqual(result, "Hi there!")
        
        # Test get_model_info
        info = api.get_model_info()
        self.assertIsInstance(info, dict)
        self.assertIn("model", info)
        self.assertIn("status", info)
    
    def test_demo_translation_api(self):
        """Test demo translation API."""
        api = DemoTranslationAPI()
        
        # Test translate_text
        with patch('demo.demo_api.is_demo_mode', return_value=True):
            with patch.object(api.demo_runner, 'simulate_translation') as mock_trans:
                mock_trans.return_value = "Hola mundo"
                result = api.translate_text("Hello world")
                self.assertEqual(result, "Hola mundo")
        
        # Test get_supported_languages
        languages = api.get_supported_languages()
        self.assertIsInstance(languages, list)
        self.assertIn("en", languages)
        self.assertIn("es", languages)
        
        # Test get_translation_info
        info = api.get_translation_info()
        self.assertIsInstance(info, dict)
        self.assertIn("model", info)
        self.assertIn("status", info)
    
    def test_demo_animation_api(self):
        """Test demo animation API."""
        api = DemoAnimationAPI()
        
        # Test get_avatar_image
        with patch('demo.demo_api.is_demo_mode', return_value=True):
            with patch.object(api.demo_runner, 'get_avatar_image') as mock_avatar:
                mock_avatar.return_value = "/path/to/avatar.jpg"
                result = api.get_avatar_image()
                self.assertEqual(result, "/path/to/avatar.jpg")
        
        # Test run_face_sync
        with patch('demo.demo_api.is_demo_mode', return_value=True):
            with patch('demo.demo_api.get_demo_setting', return_value=False):
                with patch.object(api.demo_runner, 'get_avatar_image') as mock_avatar:
                    mock_avatar.return_value = "/path/to/avatar.jpg"
                    result = api.run_face_sync("/path/to/audio.wav")
                    self.assertIsInstance(result, dict)
                    self.assertIn("status", result)
                    self.assertIn("avatar_image", result)
        
        # Test get_animation_info
        info = api.get_animation_info()
        self.assertIsInstance(info, dict)
        self.assertIn("model", info)
        self.assertIn("status", info)
    
    def test_demo_audio_api(self):
        """Test demo audio API."""
        api = DemoAudioAPI()
        
        # Test capture_audio
        with patch('demo.demo_api.is_demo_mode', return_value=True):
            with patch.object(api.demo_runner, 'simulate_audio_capture') as mock_capture:
                mock_capture.return_value = b'audio_data'
                result = api.capture_audio(5.0)
                self.assertEqual(result, b'audio_data')
        
        # Test play_audio
        with patch('demo.demo_api.is_demo_mode', return_value=True):
            with patch('demo.demo_api.get_demo_setting', return_value=False):
                result = api.play_audio(b'audio_data')
                self.assertTrue(result)
        
        # Test get_audio_info
        info = api.get_audio_info()
        self.assertIsInstance(info, dict)
        self.assertIn("sample_rate", info)
        self.assertIn("channels", info)
        self.assertIn("format", info)
        self.assertIn("status", info)


class TestDemoIntegration(unittest.TestCase):
    """Test demo module integration."""
    
    def test_get_api_instance(self):
        """Test API instance factory."""
        # Test demo mode
        with patch('demo.demo_api.is_demo_mode', return_value=True):
            tts_api = get_api_instance("tts")
            self.assertIsInstance(tts_api, DemoTTsAPI)
            
            stt_api = get_api_instance("stt")
            self.assertIsInstance(stt_api, DemoSTTAPI)
            
            llm_api = get_api_instance("llm")
            self.assertIsInstance(llm_api, DemoLLMAPI)
        
        # Test invalid API type
        with self.assertRaises(ValueError):
            get_api_instance("invalid")
    
    def test_convenience_functions(self):
        """Test convenience API functions."""
        with patch('demo.demo_api.is_demo_mode', return_value=True):
            tts_api = get_tts_api()
            self.assertIsInstance(tts_api, DemoTTsAPI)
            
            stt_api = get_stt_api()
            self.assertIsInstance(stt_api, DemoSTTAPI)
            
            llm_api = get_llm_api()
            self.assertIsInstance(llm_api, DemoLLMAPI)
            
            translation_api = get_translation_api()
            self.assertIsInstance(translation_api, DemoTranslationAPI)
            
            animation_api = get_animation_api()
            self.assertIsInstance(animation_api, DemoAnimationAPI)
            
            audio_api = get_audio_api()
            self.assertIsInstance(audio_api, DemoAudioAPI)


if __name__ == "__main__":
    unittest.main() 