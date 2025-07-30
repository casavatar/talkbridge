#!/usr/bin/env python3
"""
Test module for Conversation Logger

Tests the conversation logging functionality including:
- Log entry creation and validation
- File saving and loading (JSONL/CSV)
- Data consistency and integrity
- Thread safety and error handling
- Statistics and filtering

Author: TalkBridge QA Team
Date: 2024-01-01
"""

import unittest
import tempfile
import os
import json
import csv
from pathlib import Path
from datetime import datetime
import shutil

# Import the logger module
from utils.logger import ConversationLogger, ConversationEntry, create_logger


class TestConversationLogger(unittest.TestCase):
    """Test cases for the ConversationLogger class."""
    
    def setUp(self):
        """Set up test fixtures before each test method."""
        # Create temporary directory for test files
        self.test_dir = tempfile.mkdtemp()
        self.logger = ConversationLogger(
            buffer_size=10,
            auto_save_interval=0,  # Disable auto-save for testing
            default_file_path=None
        )
    
    def tearDown(self):
        """Clean up after each test method."""
        # Remove temporary directory
        shutil.rmtree(self.test_dir, ignore_errors=True)
    
    def test_log_entry_creation(self):
        """Test creating a conversation log entry with all fields."""
        # Create test data
        original_text = "Hello, how are you?"
        translated_text = "Hola, ¿cómo estás?"
        model_response = "I'm doing well, thank you for asking!"
        user_id = "test_user_001"
        session_id = "test_session_001"
        
        # Log the entry
        entry = self.logger.log_message(
            original_text=original_text,
            translated_text=translated_text,
            model_response=model_response,
            speaker_id=user_id,
            session_id=session_id,
            language_from="en",
            language_to="es",
            confidence_score=0.95,
            entry_type="user_input"
        )
        
        # Verify entry was created correctly
        self.assertIsInstance(entry, ConversationEntry)
        self.assertEqual(entry.original_text, original_text)
        self.assertEqual(entry.translated_text, translated_text)
        self.assertEqual(entry.model_response, model_response)
        self.assertEqual(entry.speaker_id, user_id)
        self.assertEqual(entry.session_id, session_id)
        self.assertEqual(entry.language_from, "en")
        self.assertEqual(entry.language_to, "es")
        self.assertEqual(entry.confidence_score, 0.95)
        self.assertEqual(entry.entry_type, "user_input")
        
        # Verify timestamp is recent
        timestamp = datetime.fromisoformat(entry.timestamp)
        time_diff = abs((datetime.now() - timestamp).total_seconds())
        self.assertLess(time_diff, 5)  # Should be within 5 seconds
        
        # Verify processing time was recorded
        self.assertIsNotNone(entry.processing_time_ms)
        self.assertGreater(entry.processing_time_ms, 0)
    
    def test_log_entry_validation(self):
        """Test validation of required fields in log entries."""
        # Test empty original text
        with self.assertRaises(ValueError):
            self.logger.log_message(
                original_text="",
                translated_text="Hola",
                model_response="Response"
            )
        
        # Test empty translated text
        with self.assertRaises(ValueError):
            self.logger.log_message(
                original_text="Hello",
                translated_text="",
                model_response="Response"
            )
        
        # Test empty model response
        with self.assertRaises(ValueError):
            self.logger.log_message(
                original_text="Hello",
                translated_text="Hola",
                model_response=""
            )
        
        # Test whitespace-only text
        with self.assertRaises(ValueError):
            self.logger.log_message(
                original_text="   ",
                translated_text="Hola",
                model_response="Response"
            )
    
    def test_save_and_load_jsonl(self):
        """Test saving and loading log entries in JSONL format."""
        # Create test entries
        entries_data = [
            {
                "original_text": "Hello, how are you?",
                "translated_text": "Hola, ¿cómo estás?",
                "model_response": "I'm doing well!",
                "speaker_id": "user_001",
                "session_id": "session_001"
            },
            {
                "original_text": "What's the weather like?",
                "translated_text": "¿Cómo está el clima?",
                "model_response": "I don't have access to weather data.",
                "speaker_id": "user_001",
                "session_id": "session_001"
            }
        ]
        
        # Log entries
        for entry_data in entries_data:
            self.logger.log_message(**entry_data)
        
        # Save to JSONL file
        jsonl_file = os.path.join(self.test_dir, "test_log.jsonl")
        success = self.logger.save_log_to_file(jsonl_file, "jsonl")
        self.assertTrue(success)
        
        # Verify file was created
        self.assertTrue(os.path.exists(jsonl_file))
        
        # Create new logger and load the file
        new_logger = ConversationLogger()
        success = new_logger.load_log_from_file(jsonl_file, "jsonl")
        self.assertTrue(success)
        
        # Verify entries were loaded correctly
        loaded_entries = new_logger.get_conversation_log()
        self.assertEqual(len(loaded_entries), 2)
        
        # Check first entry
        first_entry = loaded_entries[0]
        self.assertEqual(first_entry["original_text"], "Hello, how are you?")
        self.assertEqual(first_entry["translated_text"], "Hola, ¿cómo estás?")
        self.assertEqual(first_entry["model_response"], "I'm doing well!")
        self.assertEqual(first_entry["speaker_id"], "user_001")
        self.assertEqual(first_entry["session_id"], "session_001")
    
    def test_save_and_load_csv(self):
        """Test saving and loading log entries in CSV format."""
        # Create test entries
        entries_data = [
            {
                "original_text": "Good morning",
                "translated_text": "Buenos días",
                "model_response": "Good morning to you too!",
                "speaker_id": "user_002",
                "session_id": "session_002"
            }
        ]
        
        # Log entries
        for entry_data in entries_data:
            self.logger.log_message(**entry_data)
        
        # Save to CSV file
        csv_file = os.path.join(self.test_dir, "test_log.csv")
        success = self.logger.save_log_to_file(csv_file, "csv")
        self.assertTrue(success)
        
        # Verify file was created
        self.assertTrue(os.path.exists(csv_file))
        
        # Create new logger and load the file
        new_logger = ConversationLogger()
        success = new_logger.load_log_from_file(csv_file, "csv")
        self.assertTrue(success)
        
        # Verify entries were loaded correctly
        loaded_entries = new_logger.get_conversation_log()
        self.assertEqual(len(loaded_entries), 1)
        
        # Check entry
        entry = loaded_entries[0]
        self.assertEqual(entry["original_text"], "Good morning")
        self.assertEqual(entry["translated_text"], "Buenos días")
        self.assertEqual(entry["model_response"], "Good morning to you too!")
        self.assertEqual(entry["speaker_id"], "user_002")
        self.assertEqual(entry["session_id"], "session_002")
    
    def test_log_filtering(self):
        """Test filtering log entries by various criteria."""
        # Create test entries with different speakers and sessions
        test_entries = [
            {
                "original_text": "Hello user 1",
                "translated_text": "Hola usuario 1",
                "model_response": "Hello!",
                "speaker_id": "user_001",
                "session_id": "session_001"
            },
            {
                "original_text": "Hello user 2",
                "translated_text": "Hola usuario 2",
                "model_response": "Hello!",
                "speaker_id": "user_002",
                "session_id": "session_001"
            },
            {
                "original_text": "Hello user 1 again",
                "translated_text": "Hola usuario 1 de nuevo",
                "model_response": "Hello again!",
                "speaker_id": "user_001",
                "session_id": "session_002"
            }
        ]
        
        # Log entries
        for entry_data in test_entries:
            self.logger.log_message(**entry_data)
        
        # Test filtering by speaker
        user_001_entries = self.logger.get_conversation_log(speaker_id="user_001")
        self.assertEqual(len(user_001_entries), 2)
        
        # Test filtering by session
        session_001_entries = self.logger.get_conversation_log(session_id="session_001")
        self.assertEqual(len(session_001_entries), 2)
        
        # Test filtering by entry type
        user_input_entries = self.logger.get_conversation_log(entry_type="user_input")
        self.assertEqual(len(user_input_entries), 3)
        
        # Test filtering by speaker and session
        filtered_entries = self.logger.get_conversation_log(
            speaker_id="user_001",
            session_id="session_001"
        )
        self.assertEqual(len(filtered_entries), 1)
        
        # Test limit
        limited_entries = self.logger.get_conversation_log(limit=2)
        self.assertEqual(len(limited_entries), 2)
    
    def test_statistics(self):
        """Test statistics generation for conversation logs."""
        # Create test entries
        test_entries = [
            {
                "original_text": "Hello",
                "translated_text": "Hola",
                "model_response": "Hi!",
                "speaker_id": "user_001",
                "session_id": "session_001"
            },
            {
                "original_text": "Goodbye",
                "translated_text": "Adiós",
                "model_response": "Bye!",
                "speaker_id": "user_002",
                "session_id": "session_002"
            }
        ]
        
        # Log entries
        for entry_data in test_entries:
            self.logger.log_message(**entry_data)
        
        # Get statistics
        stats = self.logger.get_statistics()
        
        # Verify statistics
        self.assertEqual(stats["total_entries"], 2)
        self.assertEqual(len(stats["sessions"]), 2)
        self.assertEqual(len(stats["speakers"]), 2)
        self.assertEqual(stats["entry_types"]["user_input"], 2)
        self.assertEqual(stats["languages"]["en->es"], 2)
        self.assertGreater(stats["avg_processing_time_ms"], 0)
        
        # Verify date range
        self.assertIsNotNone(stats["date_range"]["first_entry"])
        self.assertIsNotNone(stats["date_range"]["last_entry"])
    
    def test_empty_log_statistics(self):
        """Test statistics for empty log."""
        stats = self.logger.get_statistics()
        
        self.assertEqual(stats["total_entries"], 0)
        self.assertEqual(len(stats["sessions"]), 0)
        self.assertEqual(len(stats["speakers"]), 0)
        self.assertEqual(stats["avg_processing_time_ms"], 0.0)
    
    def test_clear_log(self):
        """Test clearing the conversation log."""
        # Add some entries
        self.logger.log_message(
            original_text="Hello",
            translated_text="Hola",
            model_response="Hi!"
        )
        
        # Verify entry was added
        self.assertEqual(len(self.logger), 1)
        
        # Clear log
        self.logger.clear_log()
        
        # Verify log is empty
        self.assertEqual(len(self.logger), 0)
        self.assertEqual(len(self.logger.get_conversation_log()), 0)
    
    def test_conversation_entry_dataclass(self):
        """Test the ConversationEntry dataclass functionality."""
        # Create entry directly
        entry = ConversationEntry(
            timestamp="2024-01-01T12:00:00",
            original_text="Hello",
            translated_text="Hola",
            model_response="Hi!",
            speaker_id="user_001",
            session_id="session_001"
        )
        
        # Test to_dict method
        entry_dict = entry.to_dict()
        self.assertIsInstance(entry_dict, dict)
        self.assertEqual(entry_dict["original_text"], "Hello")
        self.assertEqual(entry_dict["translated_text"], "Hola")
        self.assertEqual(entry_dict["speaker_id"], "user_001")
        
        # Test from_dict method
        new_entry = ConversationEntry.from_dict(entry_dict)
        self.assertEqual(new_entry.original_text, "Hello")
        self.assertEqual(new_entry.translated_text, "Hola")
        self.assertEqual(new_entry.speaker_id, "user_001")
    
    def test_convenience_functions(self):
        """Test convenience functions for logger creation and usage."""
        # Test create_logger function
        logger = create_logger(buffer_size=5, auto_save_interval=0)
        self.assertIsInstance(logger, ConversationLogger)
        
        # Test log_conversation_entry function
        from utils.logger import log_conversation_entry
        
        entry = log_conversation_entry(
            logger,
            original_text="Test",
            translated_text="Prueba",
            model_response="Test response",
            speaker_id="test_user"
        )
        
        self.assertIsInstance(entry, ConversationEntry)
        self.assertEqual(entry.original_text, "Test")
        self.assertEqual(entry.translated_text, "Prueba")
        self.assertEqual(entry.speaker_id, "test_user")


if __name__ == "__main__":
    unittest.main() 