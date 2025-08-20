#!/usr/bin/env python3
"""
TalkBridge Utils - Logger
=========================

Módulo logger para TalkBridge

Author: TalkBridge Team
Date: 2025-08-19
Version: 1.0

Requirements:
- None
======================================================================
Functions:
- create_logger: Create a new conversation logger instance.
- log_conversation_entry: Convenience function to log a conversation entry.
- to_dict: Convert entry to dictionary format.
- from_dict: Create entry from dictionary format.
- __init__: Initialize the conversation logger.
- _start_auto_save_thread: Start the auto-save thread.
- log_message: Log a conversation message with all relevant information.
- get_conversation_log: Retrieve conversation log entries with optional filtering.
- save_log_to_file: Save conversation log to file.
- load_log_from_file: Load conversation log from file.
======================================================================
"""

import json
import csv
import threading
import time
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Union, Any
from dataclasses import dataclass, asdict
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@dataclass
class ConversationEntry:
    """Structured conversation entry with all required fields."""
    timestamp: str
    original_text: str
    translated_text: str
    model_response: str
    audio_file_path: Optional[str] = None
    speaker_id: Optional[str] = None
    session_id: Optional[str] = None
    language_from: str = "en"
    language_to: str = "es"
    confidence_score: Optional[float] = None
    processing_time_ms: Optional[float] = None
    entry_type: str = "user_input"
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert entry to dictionary format."""
        return asdict(self)
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'ConversationEntry':
        """Create entry from dictionary format."""
        return cls(**data)


class ConversationLogger:
    """Thread-safe conversation logger for real-time conversation tracking."""
    
    def __init__(self, 
                 buffer_size: int = 100,
                 auto_save_interval: int = 60,
                 default_file_path: Optional[str] = None):
        """Initialize the conversation logger."""
        self._entries: List[ConversationEntry] = []
        self._lock = threading.Lock()
        self._buffer_size = buffer_size
        self._auto_save_interval = auto_save_interval
        self._default_file_path = default_file_path
        self._last_save_time = time.time()
        
        # Start auto-save thread if interval is set
        self._auto_save_thread = None
        if auto_save_interval > 0:
            self._start_auto_save_thread()
    
    def _start_auto_save_thread(self):
        """Start the auto-save thread."""
        def auto_save_worker():
            while True:
                time.sleep(self._auto_save_interval)
                if self._default_file_path:
                    self.save_log_to_file(self._default_file_path)
        
        self._auto_save_thread = threading.Thread(
            target=auto_save_worker, 
            daemon=True
        )
        self._auto_save_thread.start()
    
    def log_message(self, 
                   original_text: str,
                   translated_text: str,
                   model_response: str,
                   audio_file_path: Optional[str] = None,
                   speaker_id: Optional[str] = None,
                   session_id: Optional[str] = None,
                   language_from: str = "en",
                   language_to: str = "es",
                   confidence_score: Optional[float] = None,
                   entry_type: str = "user_input") -> ConversationEntry:
        """Log a conversation message with all relevant information."""
        # Validate required fields
        if not original_text.strip():
            raise ValueError("original_text cannot be empty")
        if not translated_text.strip():
            raise ValueError("translated_text cannot be empty")
        if not model_response.strip():
            raise ValueError("model_response cannot be empty")
        
        # Record start time for processing time calculation
        start_time = time.time()
        
        # Create timestamp
        timestamp = datetime.now().isoformat()
        
        # Create conversation entry
        entry = ConversationEntry(
            timestamp=timestamp,
            original_text=original_text.strip(),
            translated_text=translated_text.strip(),
            model_response=model_response.strip(),
            audio_file_path=audio_file_path,
            speaker_id=speaker_id,
            session_id=session_id,
            language_from=language_from,
            language_to=language_to,
            confidence_score=confidence_score,
            entry_type=entry_type
        )
        
        # Thread-safe addition to entries list
        with self._lock:
            self._entries.append(entry)
            
            # Calculate processing time
            processing_time = (time.time() - start_time) * 1000
            entry.processing_time_ms = processing_time
            
            # Check if buffer is full and auto-save if needed
            if len(self._entries) >= self._buffer_size:
                if self._default_file_path:
                    self._save_entries_to_file(self._default_file_path)
        
        logger.info(f"Logged conversation entry: {entry_type} from {speaker_id or 'unknown'}")
        return entry
    
    def get_conversation_log(self, 
                           limit: Optional[int] = None,
                           session_id: Optional[str] = None,
                           speaker_id: Optional[str] = None,
                           entry_type: Optional[str] = None) -> List[Dict[str, Any]]:
        """Retrieve conversation log entries with optional filtering."""
        with self._lock:
            entries = self._entries.copy()
        
        # Apply filters
        filtered_entries = []
        for entry in entries:
            if session_id and entry.session_id != session_id:
                continue
            if speaker_id and entry.speaker_id != speaker_id:
                continue
            if entry_type and entry.entry_type != entry_type:
                continue
            filtered_entries.append(entry.to_dict())
        
        # Apply limit
        if limit:
            filtered_entries = filtered_entries[-limit:]
        
        return filtered_entries
    
    def save_log_to_file(self, file_path: str, format: str = "auto") -> bool:
        """Save conversation log to file."""
        try:
            # Determine format from file extension if auto
            if format == "auto":
                file_ext = Path(file_path).suffix.lower()
                if file_ext == ".csv":
                    format = "csv"
                elif file_ext in [".jsonl", ".json"]:
                    format = "jsonl"
                else:
                    format = "jsonl"
            
            if format == "jsonl":
                return self._save_as_jsonl(file_path)
            elif format == "csv":
                return self._save_as_csv(file_path)
            else:
                raise ValueError(f"Unsupported format: {format}")
                
        except Exception as e:
            logger.error(f"Failed to save log to {file_path}: {e}")
            return False
    
    def load_log_from_file(self, file_path: str, format: str = "auto") -> bool:
        """Load conversation log from file."""
        try:
            # Determine format from file extension if auto
            if format == "auto":
                file_ext = Path(file_path).suffix.lower()
                if file_ext == ".csv":
                    format = "csv"
                elif file_ext in [".jsonl", ".json"]:
                    format = "jsonl"
                else:
                    format = "jsonl"
            
            if format == "jsonl":
                return self._load_from_jsonl(file_path)
            elif format == "csv":
                return self._load_from_csv(file_path)
            else:
                raise ValueError(f"Unsupported format: {format}")
                
        except Exception as e:
            logger.error(f"Failed to load log from {file_path}: {e}")
            return False
    
    def _save_as_jsonl(self, file_path: str) -> bool:
        """Save entries as JSONL format (one JSON object per line)."""
        try:
            with self._lock:
                entries = self._entries.copy()
            
            with open(file_path, 'w', encoding='utf-8') as f:
                for entry in entries:
                    json.dump(entry.to_dict(), f, ensure_ascii=False)
                    f.write('\n')
            
            logger.info(f"Saved {len(entries)} entries to JSONL file: {file_path}")
            return True
            
        except Exception as e:
            logger.error(f"Error saving JSONL file: {e}")
            return False
    
    def _save_as_csv(self, file_path: str) -> bool:
        """Save entries as CSV format."""
        try:
            with self._lock:
                entries = self._entries.copy()
            
            if not entries:
                logger.warning("No entries to save")
                return True
            
            # Get fieldnames from the first entry
            fieldnames = list(entries[0].to_dict().keys())
            
            with open(file_path, 'w', newline='', encoding='utf-8') as f:
                writer = csv.DictWriter(f, fieldnames=fieldnames)
                writer.writeheader()
                for entry in entries:
                    writer.writerow(entry.to_dict())
            
            logger.info(f"Saved {len(entries)} entries to CSV file: {file_path}")
            return True
            
        except Exception as e:
            logger.error(f"Error saving CSV file: {e}")
            return False
    
    def _load_from_jsonl(self, file_path: str) -> bool:
        """Load entries from JSONL format."""
        try:
            new_entries = []
            with open(file_path, 'r', encoding='utf-8') as f:
                for line_num, line in enumerate(f, 1):
                    line = line.strip()
                    if not line:
                        continue
                    
                    try:
                        data = json.loads(line)
                        entry = ConversationEntry.from_dict(data)
                        new_entries.append(entry)
                    except (json.JSONDecodeError, KeyError) as e:
                        logger.warning(f"Invalid JSON on line {line_num}: {e}")
                        continue
            
            with self._lock:
                self._entries.extend(new_entries)
            
            logger.info(f"Loaded {len(new_entries)} entries from JSONL file: {file_path}")
            return True
            
        except Exception as e:
            logger.error(f"Error loading JSONL file: {e}")
            return False
    
    def _load_from_csv(self, file_path: str) -> bool:
        """Load entries from CSV format."""
        try:
            new_entries = []
            with open(file_path, 'r', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                for row_num, row in enumerate(reader, 2):
                    try:
                        # Convert empty strings to None for optional fields
                        for key, value in row.items():
                            if value == "":
                                row[key] = None
                            elif key in ['confidence_score', 'processing_time_ms']:
                                try:
                                    row[key] = float(value) if value else None
                                except ValueError:
                                    row[key] = None
                        
                        entry = ConversationEntry.from_dict(row)
                        new_entries.append(entry)
                    except Exception as e:
                        logger.warning(f"Invalid CSV data on line {row_num}: {e}")
                        continue
            
            with self._lock:
                self._entries.extend(new_entries)
            
            logger.info(f"Loaded {len(new_entries)} entries from CSV file: {file_path}")
            return True
            
        except Exception as e:
            logger.error(f"Error loading CSV file: {e}")
            return False
    
    def _save_entries_to_file(self, file_path: str) -> bool:
        """Internal method to save current entries to file."""
        try:
            with self._lock:
                entries_to_save = self._entries.copy()
                self._entries.clear()
            
            # Append to existing file
            with open(file_path, 'a', encoding='utf-8') as f:
                for entry in entries_to_save:
                    json.dump(entry.to_dict(), f, ensure_ascii=False)
                    f.write('\n')
            
            logger.info(f"Auto-saved {len(entries_to_save)} entries to {file_path}")
            return True
            
        except Exception as e:
            logger.error(f"Error in auto-save: {e}")
            return False
    
    def clear_log(self) -> None:
        """Clear all logged entries."""
        with self._lock:
            self._entries.clear()
        logger.info("Conversation log cleared")
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get statistics about the conversation log."""
        with self._lock:
            entries = self._entries.copy()
        
        if not entries:
            return {
                "total_entries": 0,
                "sessions": set(),
                "speakers": set(),
                "entry_types": {},
                "languages": {},
                "avg_processing_time_ms": 0.0
            }
        
        # Calculate statistics
        sessions = set(entry.session_id for entry in entries if entry.session_id)
        speakers = set(entry.speaker_id for entry in entries if entry.speaker_id)
        
        entry_types = {}
        for entry in entries:
            entry_types[entry.entry_type] = entry_types.get(entry.entry_type, 0) + 1
        
        languages = {}
        for entry in entries:
            lang_pair = f"{entry.language_from}->{entry.language_to}"
            languages[lang_pair] = languages.get(lang_pair, 0) + 1
        
        processing_times = [entry.processing_time_ms for entry in entries if entry.processing_time_ms]
        avg_processing_time = sum(processing_times) / len(processing_times) if processing_times else 0.0
        
        return {
            "total_entries": len(entries),
            "sessions": list(sessions),
            "speakers": list(speakers),
            "entry_types": entry_types,
            "languages": languages,
            "avg_processing_time_ms": avg_processing_time,
            "date_range": {
                "first_entry": entries[0].timestamp if entries else None,
                "last_entry": entries[-1].timestamp if entries else None
            }
        }
    
    def __len__(self) -> int:
        """Return the number of logged entries."""
        with self._lock:
            return len(self._entries)
    
    def __str__(self) -> str:
        """String representation of the logger."""
        stats = self.get_statistics()
        return f"ConversationLogger(entries={stats['total_entries']}, sessions={len(stats['sessions'])}, speakers={len(stats['speakers'])})"


# Convenience functions
def create_logger(buffer_size: int = 100, 
                 auto_save_interval: int = 60,
                 default_file_path: Optional[str] = None) -> ConversationLogger:
    """Create a new conversation logger instance."""
    return ConversationLogger(
        buffer_size=buffer_size,
        auto_save_interval=auto_save_interval,
        default_file_path=default_file_path
    )


def log_conversation_entry(logger_instance: ConversationLogger,
                         original_text: str,
                         translated_text: str,
                         model_response: str,
                         **kwargs) -> ConversationEntry:
    """Convenience function to log a conversation entry."""
    return logger_instance.log_message(
        original_text=original_text,
        translated_text=translated_text,
        model_response=model_response,
        **kwargs
    )


# Example usage
if __name__ == "__main__":
    # Create logger instance
    conv_logger = create_logger(
        buffer_size=10,
        auto_save_interval=30,
        default_file_path="conversation_log.jsonl"
    )
    
    # Example conversation entries
    entries = [
        {
            "original_text": "Hello, how are you?",
            "translated_text": "Hola, ¿cómo estás?",
            "model_response": "I'm doing well, thank you for asking!",
            "speaker_id": "user_001",
            "session_id": "session_001"
        },
        {
            "original_text": "What's the weather like today?",
            "translated_text": "¿Cómo está el clima hoy?",
            "model_response": "I don't have access to real-time weather data, but I can help you find weather information!",
            "speaker_id": "user_001",
            "session_id": "session_001"
        }
    ]
    
    # Log entries
    for entry_data in entries:
        conv_logger.log_message(**entry_data)
    
    # Get conversation log
    log_entries = conv_logger.get_conversation_log()
    print(f"Logged {len(log_entries)} entries")
    
    # Get statistics
    stats = conv_logger.get_statistics()
    print(f"Statistics: {stats}")
    
    # Save to different formats
    conv_logger.save_log_to_file("conversation_log.jsonl", "jsonl")
    conv_logger.save_log_to_file("conversation_log.csv", "csv")
    
    print("Logger test completed successfully!") 