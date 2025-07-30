#!/usr/bin/env python3
"""
Test module for Storage Manager

Tests the storage management functionality including:
- Folder creation and organization
- File saving with unique naming
- File integrity validation
- Cleanup operations
- Cross-platform compatibility

Author: TalkBridge QA Team
Date: 2024-01-01
"""

import unittest
import tempfile
import os
import shutil
import json
from pathlib import Path
from datetime import datetime, timedelta
import time

# Import the storage manager module
from utils.storage_manager import StorageManager, create_storage_manager


class TestStorageManager(unittest.TestCase):
    """Test cases for the StorageManager class."""
    
    def setUp(self):
        """Set up test fixtures before each test method."""
        # Create temporary directory for test files
        self.test_dir = tempfile.mkdtemp()
        self.storage = StorageManager(base_path=self.test_dir)
    
    def tearDown(self):
        """Clean up after each test method."""
        # Remove temporary directory
        shutil.rmtree(self.test_dir, ignore_errors=True)
    
    def test_folder_creation(self):
        """Test that all required folders are created correctly."""
        # Check that all folders exist
        expected_folders = ["audio_samples", "logs", "models", "avatars"]
        
        for folder_name in expected_folders:
            folder_path = self.storage.folders[folder_name]
            self.assertTrue(folder_path.exists())
            self.assertTrue(folder_path.is_dir())
            
            # Check that .gitkeep file was created
            gitkeep_file = folder_path / ".gitkeep"
            self.assertTrue(gitkeep_file.exists())
    
    def test_save_audio_sample(self):
        """Test saving audio samples with proper naming and metadata."""
        # Create test audio data
        test_audio = b"fake audio data for testing"
        user_id = "test_user_001"
        
        # Save audio sample
        file_path = self.storage.save_audio_sample(
            audio_bytes=test_audio,
            user_id=user_id,
            format="wav"
        )
        
        # Verify file was created
        self.assertTrue(os.path.exists(file_path))
        
        # Verify file content
        with open(file_path, 'rb') as f:
            saved_audio = f.read()
        self.assertEqual(saved_audio, test_audio)
        
        # Verify filename format
        filename = os.path.basename(file_path)
        self.assertTrue(filename.startswith("audio_test_user_001_"))
        self.assertTrue(filename.endswith(".wav"))
        
        # Verify metadata file was created
        metadata_path = file_path.replace('.wav', '.json')
        self.assertTrue(os.path.exists(metadata_path))
        
        # Verify metadata content
        with open(metadata_path, 'r', encoding='utf-8') as f:
            metadata = json.load(f)
        
        self.assertEqual(metadata["user_id"], user_id)
        self.assertEqual(metadata["format"], "wav")
        self.assertEqual(metadata["file_size"], len(test_audio))
        self.assertIn("file_hash", metadata)
        self.assertIn("created_at", metadata)
    
    def test_save_log_file(self):
        """Test saving log files with proper naming and metadata."""
        # Create test log data
        test_log = "test log entry\nsecond line\nthird line"
        session_id = "test_session_001"
        
        # Save log file
        file_path = self.storage.save_log_file(
            log_data=test_log,
            session_id=session_id,
            format="jsonl"
        )
        
        # Verify file was created
        self.assertTrue(os.path.exists(file_path))
        
        # Verify file content
        with open(file_path, 'r', encoding='utf-8') as f:
            saved_log = f.read()
        self.assertEqual(saved_log, test_log)
        
        # Verify filename format
        filename = os.path.basename(file_path)
        self.assertTrue(filename.startswith("log_test_session_001_"))
        self.assertTrue(filename.endswith(".jsonl"))
        
        # Verify metadata file was created
        metadata_path = file_path.replace('.jsonl', '.json')
        self.assertTrue(os.path.exists(metadata_path))
        
        # Verify metadata content
        with open(metadata_path, 'r', encoding='utf-8') as f:
            metadata = json.load(f)
        
        self.assertEqual(metadata["session_id"], session_id)
        self.assertEqual(metadata["format"], "jsonl")
        self.assertEqual(metadata["file_size"], len(test_log.encode('utf-8')))
        self.assertEqual(metadata["entry_count"], 3)  # 3 lines
        self.assertIn("created_at", metadata)
    
    def test_save_avatar(self):
        """Test saving avatar files with proper naming and metadata."""
        # Create test avatar data
        test_avatar = b"fake avatar image data"
        user_id = "test_user_001"
        
        # Save avatar
        file_path = self.storage.save_avatar(
            file_bytes=test_avatar,
            user_id=user_id,
            format="png"
        )
        
        # Verify file was created
        self.assertTrue(os.path.exists(file_path))
        
        # Verify file content
        with open(file_path, 'rb') as f:
            saved_avatar = f.read()
        self.assertEqual(saved_avatar, test_avatar)
        
        # Verify filename format
        filename = os.path.basename(file_path)
        self.assertTrue(filename.startswith("avatar_test_user_001_"))
        self.assertTrue(filename.endswith(".png"))
        
        # Verify metadata file was created
        metadata_path = file_path.replace('.png', '.json')
        self.assertTrue(os.path.exists(metadata_path))
        
        # Verify metadata content
        with open(metadata_path, 'r', encoding='utf-8') as f:
            metadata = json.load(f)
        
        self.assertEqual(metadata["user_id"], user_id)
        self.assertEqual(metadata["format"], "png")
        self.assertEqual(metadata["file_size"], len(test_avatar))
        self.assertIn("file_hash", metadata)
        self.assertIn("created_at", metadata)
    
    def test_get_model_path(self):
        """Test getting model paths and directory creation."""
        # Test with simple model name
        model_name = "whisper-large"
        model_path = self.storage.get_model_path(model_name)
        
        # Verify path was created
        self.assertTrue(os.path.exists(model_path))
        self.assertTrue(os.path.isdir(model_path))
        
        # Verify path format
        expected_path = os.path.join(self.test_dir, "models", "whisper-large")
        self.assertEqual(model_path, expected_path)
        
        # Test with complex model name (should be sanitized)
        complex_model_name = "whisper-large-v2.0@user/model"
        complex_model_path = self.storage.get_model_path(complex_model_name)
        
        # Verify sanitized path was created
        self.assertTrue(os.path.exists(complex_model_path))
        expected_sanitized = os.path.join(self.test_dir, "models", "whisper-large-v20usermodel")
        self.assertEqual(complex_model_path, expected_sanitized)
    
    def test_validation_errors(self):
        """Test validation of input parameters."""
        # Test empty audio bytes
        with self.assertRaises(ValueError):
            self.storage.save_audio_sample(b"", "user_001")
        
        # Test empty log data
        with self.assertRaises(ValueError):
            self.storage.save_log_file("", "session_001")
        
        # Test empty avatar bytes
        with self.assertRaises(ValueError):
            self.storage.save_avatar(b"", "user_001")
        
        # Test empty model name
        with self.assertRaises(ValueError):
            self.storage.get_model_path("")
        
        # Test invalid folder for cleanup
        with self.assertRaises(ValueError):
            self.storage.cleanup_old_files("invalid_folder", 7)
        
        # Test negative days for cleanup
        with self.assertRaises(ValueError):
            self.storage.cleanup_old_files("audio_samples", -1)
    
    def test_cleanup_old_files(self):
        """Test cleanup of old files from folders."""
        # Create some test files with different timestamps
        audio_folder = self.storage.folders["audio_samples"]
        
        # Create old file (modify timestamp to be old)
        old_file = audio_folder / "old_audio.wav"
        old_file.write_bytes(b"old audio data")
        
        # Set file modification time to 10 days ago
        old_time = time.time() - (10 * 24 * 3600)
        os.utime(old_file, (old_time, old_time))
        
        # Create recent file
        recent_file = audio_folder / "recent_audio.wav"
        recent_file.write_bytes(b"recent audio data")
        
        # Create metadata files
        old_metadata = old_file.with_suffix('.json')
        old_metadata.write_text('{"test": "metadata"}')
        
        recent_metadata = recent_file.with_suffix('.json')
        recent_metadata.write_text('{"test": "metadata"}')
        
        # Run cleanup for files older than 5 days
        removed_count = self.storage.cleanup_old_files("audio_samples", 5)
        
        # Verify old file was removed
        self.assertFalse(old_file.exists())
        self.assertFalse(old_metadata.exists())
        
        # Verify recent file was kept
        self.assertTrue(recent_file.exists())
        self.assertTrue(recent_metadata.exists())
        
        # Verify correct count
        self.assertEqual(removed_count, 1)
    
    def test_cleanup_with_pattern(self):
        """Test cleanup with file pattern matching."""
        audio_folder = self.storage.folders["audio_samples"]
        
        # Create files with different extensions
        wav_file = audio_folder / "test.wav"
        wav_file.write_bytes(b"wav data")
        
        mp3_file = audio_folder / "test.mp3"
        mp3_file.write_bytes(b"mp3 data")
        
        # Set old timestamps
        old_time = time.time() - (10 * 24 * 3600)
        os.utime(wav_file, (old_time, old_time))
        os.utime(mp3_file, (old_time, old_time))
        
        # Cleanup only WAV files
        removed_count = self.storage.cleanup_old_files("audio_samples", 5, "*.wav")
        
        # Verify only WAV file was removed
        self.assertFalse(wav_file.exists())
        self.assertTrue(mp3_file.exists())
        self.assertEqual(removed_count, 1)
    
    def test_get_folder_info(self):
        """Test getting information about folders."""
        # Add some test files
        audio_folder = self.storage.folders["audio_samples"]
        test_file = audio_folder / "test.wav"
        test_file.write_bytes(b"test data")
        
        # Get folder information
        info = self.storage.get_folder_info("audio_samples")
        
        # Verify information
        self.assertEqual(info["folder"], "audio_samples")
        self.assertEqual(info["total_files"], 2)  # test.wav + .gitkeep
        self.assertGreater(info["total_size_bytes"], 0)
        self.assertIn(".wav", info["file_types"])
        self.assertIn(".gitkeep", info["file_types"])
        self.assertIsNotNone(info["last_modified"])
    
    def test_get_all_folders_info(self):
        """Test getting information about all folders."""
        all_info = self.storage.get_all_folders_info()
        
        # Verify all folders are included
        expected_folders = ["audio_samples", "logs", "models", "avatars"]
        for folder in expected_folders:
            self.assertIn(folder, all_info)
            self.assertEqual(all_info[folder]["folder"], folder)
            self.assertTrue(all_info[folder]["exists"])
    
    def test_backup_folder(self):
        """Test backing up folders."""
        # Add some test files
        logs_folder = self.storage.folders["logs"]
        test_file = logs_folder / "test.jsonl"
        test_file.write_text("test log data")
        
        # Create backup
        backup_path = self.storage.backup_folder(
            folder="logs",
            backup_path=self.test_dir,
            include_metadata=True
        )
        
        # Verify backup was created
        self.assertTrue(os.path.exists(backup_path))
        
        # Verify files were copied
        backup_dir = Path(backup_path)
        self.assertTrue((backup_dir / "test.jsonl").exists())
        
        # Verify backup directory name format
        backup_name = os.path.basename(backup_path)
        self.assertTrue(backup_name.startswith("logs_backup_"))
    
    def test_validate_file_integrity(self):
        """Test file integrity validation."""
        # Create a test file
        audio_folder = self.storage.folders["audio_samples"]
        test_file = audio_folder / "test.wav"
        test_data = b"test audio data"
        test_file.write_bytes(test_data)
        
        # Create metadata file
        metadata_file = test_file.with_suffix('.json')
        metadata = {
            "file_hash": self.storage._get_file_hash(test_data),
            "file_size": len(test_data)
        }
        metadata_file.write_text(json.dumps(metadata))
        
        # Validate file integrity
        validation = self.storage.validate_file_integrity(str(test_file))
        
        # Verify validation results
        self.assertTrue(validation["valid"])
        self.assertEqual(validation["file_size"], len(test_data))
        self.assertTrue(validation["metadata_exists"])
        self.assertIn("current_hash", validation)
        self.assertIn("stored_hash", validation)
    
    def test_validate_file_integrity_corrupted(self):
        """Test file integrity validation with corrupted file."""
        # Create a test file
        audio_folder = self.storage.folders["audio_samples"]
        test_file = audio_folder / "test.wav"
        test_data = b"test audio data"
        test_file.write_bytes(test_data)
        
        # Create metadata file with wrong hash
        metadata_file = test_file.with_suffix('.json')
        metadata = {
            "file_hash": "wrong_hash_here",
            "file_size": len(test_data)
        }
        metadata_file.write_text(json.dumps(metadata))
        
        # Validate file integrity
        validation = self.storage.validate_file_integrity(str(test_file))
        
        # Verify validation detected corruption
        self.assertFalse(validation["valid"])
        self.assertNotEqual(validation["current_hash"], validation["stored_hash"])
    
    def test_validate_file_integrity_missing(self):
        """Test file integrity validation with missing file."""
        validation = self.storage.validate_file_integrity("nonexistent_file.wav")
        
        # Verify validation results
        self.assertFalse(validation["valid"])
        self.assertIn("error", validation)
    
    def test_convenience_functions(self):
        """Test convenience functions for storage manager creation."""
        # Test create_storage_manager function
        storage = create_storage_manager("test_data")
        self.assertIsInstance(storage, StorageManager)
        self.assertEqual(storage.base_path.name, "test_data")
        
        # Test get_default_storage_manager function
        from utils.storage_manager import get_default_storage_manager
        default_storage = get_default_storage_manager()
        self.assertIsInstance(default_storage, StorageManager)
        self.assertEqual(default_storage.base_path.name, "data")
    
    def test_string_representation(self):
        """Test string representation of storage manager."""
        # Add some test files
        audio_folder = self.storage.folders["audio_samples"]
        test_file = audio_folder / "test.wav"
        test_file.write_bytes(b"test data")
        
        # Get string representation
        str_repr = str(self.storage)
        
        # Verify format
        self.assertIn("StorageManager", str_repr)
        self.assertIn("folders=4", str_repr)
        self.assertIn("files=", str_repr)
        self.assertIn("size=", str_repr)
        self.assertIn("bytes", str_repr)


if __name__ == "__main__":
    unittest.main() 