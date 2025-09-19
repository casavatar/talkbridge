#!/usr/bin/env python3
"""
TalkBridge Utils - Storage Manager
==================================

Module manager/manager

Author: TalkBridge Team
Date: 2025-08-19
Version: 1.0

Requirements:
- None
======================================================================
Functions:
- create_storage_manager: Create a new storage manager instance.
- get_default_storage_manager: Get the default storage manager instance.
- __init__: Initialize the storage manager.
- _create_folders: Create all necessary folders if they don't exist.
- _generate_unique_filename: Generate a unique filename with timestamp and optional user ID.
- _get_file_hash: Generate SHA-256 hash of file content.
- save_audio_sample: Save audio sample with unique filename.
- save_log_file: Save log file with unique filename.
- get_model_path: Get the path for a specific model.
- save_avatar: Save avatar file with unique filename.
======================================================================
"""

import os
import shutil
import uuid
import hashlib
from datetime import datetime, timedelta
from pathlib import Path
from typing import Optional, List, Dict, Any, Union
import logging
import json

# Configure logging
# Logging configuration is handled by src/desktop/logging_config.py
# logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class StorageManager:
    """
    Manages file storage and organization for the TalkBridge AI system.
    
    This class handles the creation and management of data folders,
    file operations with unique naming, and cleanup utilities.
    
    Folder Structure:
    - data/audio_samples/: User voice recordings
    - data/logs/: Conversation logs (JSONL/CSV)
    - data/models/: Local models (Whisper, TTS, translation)
    - data/avatars/: Avatar images or 3D models
    """
    
    def __init__(self, base_path: str = "data"):
        """
        Initialize the storage manager.
        
        Args:
            base_path: Base directory for all data storage
        """
        self.base_path = Path(base_path)
        self.folders = {
            "audio_samples": self.base_path / "audio_samples",
            "logs": self.base_path / "logs",
            "models": self.base_path / "models",
            "avatars": self.base_path / "avatars"
        }
        
        # Create all necessary folders
        self._create_folders()
        
        # Track file operations for cleanup
        self._file_operations = []
    
    def _create_folders(self) -> None:
        """Create all necessary folders if they don't exist."""
        try:
            for folder_name, folder_path in self.folders.items():
                folder_path.mkdir(parents=True, exist_ok=True)
                logger.info(f"Ensured folder exists: {folder_path}")
                
                # Create .gitkeep files to preserve empty folders
                gitkeep_file = folder_path / ".gitkeep"
                if not gitkeep_file.exists():
                    gitkeep_file.touch()
                    
        except PermissionError as e:
            logger.error(f"Permission denied creating folders: {e}")
            raise
        except Exception as e:
            logger.error(f"Error creating folders: {e}")
            raise
    
    def _generate_unique_filename(self, 
                                prefix: str, 
                                extension: str, 
                                user_id: Optional[str] = None) -> str:
        """
        Generate a unique filename with timestamp and optional user ID.
        
        Args:
            prefix: File prefix (e.g., 'audio', 'log', 'avatar')
            extension: File extension (e.g., '.wav', '.jsonl', '.png')
            user_id: Optional user identifier
            
        Returns:
            Unique filename string
        """
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S_%f")[:-3]  # Remove microseconds
        unique_id = str(uuid.uuid4())[:8]
        
        if user_id:
            # Sanitize user_id for filename safety
            safe_user_id = "".join(c for c in user_id if c.isalnum() or c in ('-', '_'))
            filename = f"{prefix}_{safe_user_id}_{timestamp}_{unique_id}{extension}"
        else:
            filename = f"{prefix}_{timestamp}_{unique_id}{extension}"
        
        return filename
    
    def _get_file_hash(self, file_bytes: bytes) -> str:
        """
        Generate SHA-256 hash of file content.
        
        Args:
            file_bytes: File content as bytes
            
        Returns:
            SHA-256 hash string
        """
        return hashlib.sha256(file_bytes).hexdigest()
    
    def save_audio_sample(self, 
                         audio_bytes: bytes, 
                         user_id: str,
                         format: str = "wav") -> str:
        """
        Save audio sample with unique filename.
        
        Args:
            audio_bytes: Audio data as bytes
            user_id: User identifier
            format: Audio format (wav, mp3, etc.)
            
        Returns:
            Path to saved audio file
            
        Raises:
            ValueError: If audio_bytes is empty
            PermissionError: If unable to write to file
        """
        if not audio_bytes:
            raise ValueError("Audio bytes cannot be empty")
        
        try:
            # Generate filename
            extension = f".{format.lower()}"
            filename = self._generate_unique_filename("audio", extension, user_id)
            file_path = self.folders["audio_samples"] / filename
            
            # Save file
            with open(file_path, 'wb') as f:
                f.write(audio_bytes)
            
            # Generate hash for verification
            file_hash = self._get_file_hash(audio_bytes)
            
            # Create metadata file
            metadata = {
                "user_id": user_id,
                "filename": filename,
                "file_hash": file_hash,
                "file_size": len(audio_bytes),
                "format": format,
                "created_at": datetime.now().isoformat(),
                "original_filename": filename
            }
            
            metadata_path = file_path.with_suffix('.json')
            with open(metadata_path, 'w', encoding='utf-8') as f:
                json.dump(metadata, f, indent=2, ensure_ascii=False)
            
            logger.info(f"Saved audio sample: {file_path} ({len(audio_bytes)} bytes)")
            return str(file_path)
            
        except PermissionError as e:
            logger.error(f"Permission denied saving audio sample: {e}")
            raise
        except Exception as e:
            logger.error(f"Error saving audio sample: {e}")
            raise
    
    def save_log_file(self, 
                     log_data: str, 
                     session_id: str,
                     format: str = "jsonl") -> str:
        """
        Save log file with unique filename.
        
        Args:
            log_data: Log data as string
            session_id: Session identifier
            format: Log format (jsonl, csv)
            
        Returns:
            Path to saved log file
            
        Raises:
            ValueError: If log_data is empty
            PermissionError: If unable to write to file
        """
        if not log_data.strip():
            raise ValueError("Log data cannot be empty")
        
        try:
            # Generate filename
            extension = f".{format.lower()}"
            filename = self._generate_unique_filename("log", extension, session_id)
            file_path = self.folders["logs"] / filename
            
            # Save file
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(log_data)
            
            # Create metadata file
            metadata = {
                "session_id": session_id,
                "filename": filename,
                "file_size": len(log_data.encode('utf-8')),
                "format": format,
                "created_at": datetime.now().isoformat(),
                "entry_count": len(log_data.strip().split('\n')) if log_data.strip() else 0
            }
            
            metadata_path = file_path.with_suffix('.json')
            with open(metadata_path, 'w', encoding='utf-8') as f:
                json.dump(metadata, f, indent=2, ensure_ascii=False)
            
            logger.info(f"Saved log file: {file_path} ({len(log_data)} characters)")
            return str(file_path)
            
        except PermissionError as e:
            logger.error(f"Permission denied saving log file: {e}")
            raise
        except Exception as e:
            logger.error(f"Error saving log file: {e}")
            raise
    
    def get_model_path(self, model_name: str) -> str:
        """
        Get the path for a specific model.
        
        Args:
            model_name: Name of the model
            
        Returns:
            Path to model directory
            
        Raises:
            ValueError: If model_name is empty
        """
        if not model_name.strip():
            raise ValueError("Model name cannot be empty")
        
        # Sanitize model name for directory safety
        safe_model_name = "".join(c for c in model_name if c.isalnum() or c in ('-', '_'))
        model_path = self.folders["models"] / safe_model_name
        
        # Create model directory if it doesn't exist
        model_path.mkdir(parents=True, exist_ok=True)
        
        logger.info(f"Model path: {model_path}")
        return str(model_path)
    
    def save_avatar(self, 
                   file_bytes: bytes, 
                   user_id: str,
                   format: str = "png") -> str:
        """
        Save avatar file with unique filename.
        
        Args:
            file_bytes: Avatar file data as bytes
            user_id: User identifier
            format: Image format (png, jpg, etc.)
            
        Returns:
            Path to saved avatar file
            
        Raises:
            ValueError: If file_bytes is empty
            PermissionError: If unable to write to file
        """
        if not file_bytes:
            raise ValueError("Avatar file bytes cannot be empty")
        
        try:
            # Generate filename
            extension = f".{format.lower()}"
            filename = self._generate_unique_filename("avatar", extension, user_id)
            file_path = self.folders["avatars"] / filename
            
            # Save file
            with open(file_path, 'wb') as f:
                f.write(file_bytes)
            
            # Generate hash for verification
            file_hash = self._get_file_hash(file_bytes)
            
            # Create metadata file
            metadata = {
                "user_id": user_id,
                "filename": filename,
                "file_hash": file_hash,
                "file_size": len(file_bytes),
                "format": format,
                "created_at": datetime.now().isoformat(),
                "original_filename": filename
            }
            
            metadata_path = file_path.with_suffix('.json')
            with open(metadata_path, 'w', encoding='utf-8') as f:
                json.dump(metadata, f, indent=2, ensure_ascii=False)
            
            logger.info(f"Saved avatar: {file_path} ({len(file_bytes)} bytes)")
            return str(file_path)
            
        except PermissionError as e:
            logger.error(f"Permission denied saving avatar: {e}")
            raise
        except Exception as e:
            logger.error(f"Error saving avatar: {e}")
            raise
    
    def cleanup_old_files(self, 
                         folder: str, 
                         days_old: int,
                         file_pattern: Optional[str] = None) -> int:
        """
        Clean up old files from specified folder.
        
        Args:
            folder: Folder name ('audio_samples', 'logs', 'avatars')
            days_old: Remove files older than this many days
            file_pattern: Optional file pattern to match (e.g., '*.wav')
            
        Returns:
            Number of files removed
            
        Raises:
            ValueError: If folder is invalid or days_old is negative
        """
        if folder not in self.folders:
            raise ValueError(f"Invalid folder: {folder}")
        
        if days_old < 0:
            raise ValueError("days_old must be non-negative")
        
        try:
            folder_path = self.folders[folder]
            cutoff_date = datetime.now() - timedelta(days=days_old)
            removed_count = 0
            
            # Get all files in folder
            if file_pattern:
                files = list(folder_path.glob(file_pattern))
            else:
                files = [f for f in folder_path.iterdir() if f.is_file()]
            
            for file_path in files:
                # Skip metadata files and .gitkeep
                if file_path.name in ['.gitkeep', '.gitignore'] or file_path.suffix == '.json':
                    continue
                
                # Check file modification time
                try:
                    mtime = datetime.fromtimestamp(file_path.stat().st_mtime)
                    if mtime < cutoff_date:
                        # Remove main file
                        file_path.unlink()
                        removed_count += 1
                        
                        # Remove metadata file if it exists
                        metadata_path = file_path.with_suffix('.json')
                        if metadata_path.exists():
                            metadata_path.unlink()
                        
                        logger.info(f"Removed old file: {file_path}")
                        
                except (OSError, PermissionError) as e:
                    logger.warning(f"Could not remove file {file_path}: {e}")
                    continue
            
            logger.info(f"Cleanup completed: removed {removed_count} files from {folder}")
            return removed_count
            
        except Exception as e:
            logger.error(f"Error during cleanup: {e}")
            raise
    
    def get_folder_info(self, folder: str) -> Dict[str, Any]:
        """
        Get information about a folder.
        
        Args:
            folder: Folder name
            
        Returns:
            Dictionary with folder information
            
        Raises:
            ValueError: If folder is invalid
        """
        if folder not in self.folders:
            raise ValueError(f"Invalid folder: {folder}")
        
        try:
            folder_path = self.folders[folder]
            
            # Get all files
            files = [f for f in folder_path.iterdir() if f.is_file()]
            
            # Calculate total size
            total_size = sum(f.stat().st_size for f in files)
            
            # Count files by type
            file_types = {}
            for file in files:
                ext = file.suffix.lower()
                file_types[ext] = file_types.get(ext, 0) + 1
            
            # Get oldest and newest files
            if files:
                files_with_time = [(f, f.stat().st_mtime) for f in files]
                files_with_time.sort(key=lambda x: x[1])
                oldest_file = files_with_time[0][0].name
                newest_file = files_with_time[-1][0].name
            else:
                oldest_file = None
                newest_file = None
            
            return {
                "folder": folder,
                "path": str(folder_path),
                "exists": folder_path.exists(),
                "total_files": len(files),
                "total_size_bytes": total_size,
                "file_types": file_types,
                "oldest_file": oldest_file,
                "newest_file": newest_file,
                "last_modified": datetime.fromtimestamp(folder_path.stat().st_mtime).isoformat() if folder_path.exists() else None
            }
            
        except Exception as e:
            logger.error(f"Error getting folder info for {folder}: {e}")
            return {
                "folder": folder,
                "error": str(e)
            }
    
    def get_all_folders_info(self) -> Dict[str, Dict[str, Any]]:
        """
        Get information about all folders.
        
        Returns:
            Dictionary with information about all folders
        """
        return {
            folder: self.get_folder_info(folder)
            for folder in self.folders.keys()
        }
    
    def backup_folder(self, 
                     folder: str, 
                     backup_path: str,
                     include_metadata: bool = True) -> str:
        """
        Create a backup of a folder.
        
        Args:
            folder: Folder name to backup
            backup_path: Path for backup
            include_metadata: Whether to include metadata files
            
        Returns:
            Path to backup directory
            
        Raises:
            ValueError: If folder is invalid
        """
        if folder not in self.folders:
            raise ValueError(f"Invalid folder: {folder}")
        
        try:
            source_path = self.folders[folder]
            backup_dir = Path(backup_path) / f"{folder}_backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
            
            # Create backup directory
            backup_dir.mkdir(parents=True, exist_ok=True)
            
            # Copy files
            copied_count = 0
            for file_path in source_path.iterdir():
                if file_path.is_file():
                    # Skip .gitkeep files
                    if file_path.name == '.gitkeep':
                        continue
                    
                    # Skip metadata files if not requested
                    if not include_metadata and file_path.suffix == '.json':
                        continue
                    
                    # Copy file
                    dest_path = backup_dir / file_path.name
                    shutil.copy2(file_path, dest_path)
                    copied_count += 1
            
            logger.info(f"Backup created: {backup_dir} ({copied_count} files)")
            return str(backup_dir)
            
        except Exception as e:
            logger.error(f"Error creating backup: {e}")
            raise
    
    def validate_file_integrity(self, file_path: str) -> Dict[str, Any]:
        """
        Validate file integrity by checking hash.
        
        Args:
            file_path: Path to file to validate
            
        Returns:
            Dictionary with validation results
        """
        try:
            file_path_obj = Path(file_path)
            if not file_path_obj.exists():
                return {
                    "valid": False,
                    "error": "File does not exist"
                }
            
            # Read file content
            with open(file_path_obj, 'rb') as f:
                file_bytes = f.read()
            
            # Calculate current hash
            current_hash = self._get_file_hash(file_bytes)
            
            # Check for metadata file
            metadata_path = file_path_obj.with_suffix('.json')
            stored_hash = None
            
            if metadata_path.exists():
                try:
                    with open(metadata_path, 'r', encoding='utf-8') as f:
                        metadata = json.load(f)
                        stored_hash = metadata.get('file_hash')
                except Exception as e:
                    logger.warning(f"Could not read metadata file: {e}")
            
            # Validate
            is_valid = stored_hash is None or current_hash == stored_hash
            
            return {
                "valid": is_valid,
                "current_hash": current_hash,
                "stored_hash": stored_hash,
                "file_size": len(file_bytes),
                "metadata_exists": metadata_path.exists()
            }
            
        except Exception as e:
            return {
                "valid": False,
                "error": str(e)
            }
    
    def __str__(self) -> str:
        """String representation of the storage manager."""
        folders_info = self.get_all_folders_info()
        total_files = sum(info.get('total_files', 0) for info in folders_info.values())
        total_size = sum(info.get('total_size_bytes', 0) for info in folders_info.values())
        
        return f"StorageManager(base_path={self.base_path}, folders={len(self.folders)}, files={total_files}, size={total_size} bytes)"

# Convenience functions
def create_storage_manager(base_path: str = "data") -> StorageManager:
    """
    Create a new storage manager instance.
    
    Args:
        base_path: Base directory for all data storage
        
    Returns:
        StorageManager instance
    """
    return StorageManager(base_path)

def get_default_storage_manager() -> StorageManager:
    """
    Get the default storage manager instance.
    
    Returns:
        StorageManager instance with default settings
    """
    return StorageManager()

# Example usage
if __name__ == "__main__":
    # Create storage manager
    storage = create_storage_manager()
    
    # Test folder creation
    logging.info("Created folders:")
    for folder_name, folder_path in storage.folders.items():
        logging.info(f"  {folder_name}: {folder_path}")
    
    # Test file operations
    test_audio = b"fake audio data"
    test_log = "test log data\nsecond line"
    test_avatar = b"fake avatar data"
    
    try:
        # Save test files
        audio_path = storage.save_audio_sample(test_audio, "test_user")
        log_path = storage.save_log_file(test_log, "test_session")
        avatar_path = storage.save_avatar(test_avatar, "test_user")
        
        logging.info(f"\nSaved files:")
        logging.info(f"  Audio: {audio_path}")
        logging.info(f"  Log: {log_path}")
        logging.info(f"  Avatar: {avatar_path}")
        
        # Get folder information
        logging.info(f"\nFolder information:")
        folders_info = storage.get_all_folders_info()
        for folder, info in folders_info.items():
            logging.info(f"  {folder}: {info['total_files']} files, {info['total_size_bytes']} bytes")
        
        # Test model path
        model_path = storage.get_model_path("whisper-large")
        logging.info(f"\nModel path: {model_path}")
        
        # Test file validation
        validation = storage.validate_file_integrity(audio_path)
        logging.info(f"\nFile validation: {validation}")
        
        logging.info("\nStorage manager test completed successfully!")
        
    except Exception as e:
        logging.error(f"Error during testing: {e}") 