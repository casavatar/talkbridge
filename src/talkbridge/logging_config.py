#!/usr/bin/env python3
"""
TalkBridge - Centralized Logging Configuration
==============================================

Unified logging system for the entire TalkBridge project.
Provides consistent formatting, rotating file handlers, and proper error handling.

Author: TalkBridge Team
Date: 2025-09-18
Version: 2.0

Features:
- Rotating file handlers to prevent log files from growing too large
- Console output with timestamps and module information
- Structured logging levels: DEBUG, INFO, WARNING, ERROR, CRITICAL
- Context-aware error logging with stack traces
- Thread-safe logging configuration
- Development vs Production logging modes
"""

import logging
import logging.handlers
import sys
import os
from pathlib import Path
from typing import Optional, Dict, Any
import threading
from datetime import datetime

# Thread-safe configuration lock
_config_lock = threading.Lock()
_logging_configured = False

# Centralized log directory - All logs go to data/logs/
PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
LOG_DIR = PROJECT_ROOT / "data" / "logs"
LOG_FILE = LOG_DIR / "talkbridge.log"

# Ensure log directory exists
LOG_DIR.mkdir(parents=True, exist_ok=True)

# Project-wide logger names
LOGGER_NAMES = {
    "main": "talkbridge",
    "audio": "talkbridge.audio",
    "stt": "talkbridge.stt", 
    "tts": "talkbridge.tts",
    "translation": "talkbridge.translation",
    "ui": "talkbridge.ui",
    "desktop": "talkbridge.desktop",
    "pipeline": "talkbridge.pipeline",
    "auth": "talkbridge.auth",
    "utils": "talkbridge.utils",
    "demo": "talkbridge.demo",
    "test": "talkbridge.test"
}

# Log levels configuration
LOG_LEVELS = {
    "DEBUG": logging.DEBUG,
    "INFO": logging.INFO, 
    "WARNING": logging.WARNING,
    "ERROR": logging.ERROR,
    "CRITICAL": logging.CRITICAL
}

# Default configuration
DEFAULT_CONFIG = {
    "console_level": "INFO",
    "file_level": "DEBUG", 
    "log_dir": str(LOG_DIR),  # Use centralized log directory
    "log_file": "talkbridge.log",
    "max_file_size": 10 * 1024 * 1024,  # 10MB
    "backup_count": 5,
    "format_console": "%(asctime)s | %(name)-20s | %(levelname)-8s | %(message)s",
    "format_file": "%(asctime)s | %(name)-30s | %(levelname)-8s | %(filename)s:%(lineno)d | %(funcName)s() | %(message)s",
    "date_format": "%Y-%m-%d %H:%M:%S"
}

class TalkBridgeLogger:
    """Centralized logger configuration and management."""
    
    def __init__(self):
        self.config = DEFAULT_CONFIG.copy()
        self.loggers: Dict[str, logging.Logger] = {}
        self._handlers_created = False
        
    def configure_logging(
        self,
        console_level: str = "INFO",
        file_level: str = "DEBUG",
        log_dir: Optional[str] = None,
        development_mode: bool = True,
        force_reconfigure: bool = False
    ) -> None:
        """
        Configure the centralized logging system.
        
        Args:
            console_level: Console output level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
            file_level: File output level  
            log_dir: Directory for log files (defaults to 'data/logs')
            development_mode: Enable more verbose logging for development
            force_reconfigure: Force reconfiguration even if already configured
        """
        global _logging_configured
        
        with _config_lock:
            if _logging_configured and not force_reconfigure:
                return
                
            # Update configuration
            self.config.update({
                "console_level": console_level,
                "file_level": file_level,
                "log_dir": log_dir or str(LOG_DIR)  # Always use centralized LOG_DIR if not specified
            })
            
            # Adjust for development mode
            if development_mode:
                self.config["console_level"] = "DEBUG" if console_level == "INFO" else console_level
                self.config["format_console"] = "%(asctime)s | %(name)-15s | %(levelname)-5s | %(filename)s:%(lineno)d | %(message)s"
            
            # Create log directory
            log_path = Path(self.config["log_dir"])
            log_path.mkdir(parents=True, exist_ok=True)
            
            # Clear any existing handlers to prevent duplicates
            root_logger = logging.getLogger()
            for handler in root_logger.handlers[:]:
                root_logger.removeHandler(handler)
            
            # Set root logger level to DEBUG to capture everything
            root_logger.setLevel(logging.DEBUG)
            
            # Create handlers
            self._create_console_handler()
            self._create_file_handler()
            
            # Configure project loggers
            self._configure_project_loggers()
            
            _logging_configured = True
            
            # Log successful configuration
            logger = self.get_logger("talkbridge.logging")
            logger.info(f"Logging system configured - Console: {console_level}, File: {file_level}")
            logger.info(f"Log directory: {log_path.absolute()}")
            
    def _create_console_handler(self) -> None:
        """Create and configure console handler."""
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setLevel(LOG_LEVELS[self.config["console_level"]])
        
        console_formatter = logging.Formatter(
            fmt=self.config["format_console"],
            datefmt=self.config["date_format"]
        )
        console_handler.setFormatter(console_formatter)
        
        # Add to root logger
        logging.getLogger().addHandler(console_handler)
        
    def _create_file_handler(self) -> None:
        """Create and configure rotating file handler."""
        log_file_path = Path(self.config["log_dir"]) / self.config["log_file"]
        
        file_handler = logging.handlers.RotatingFileHandler(
            filename=log_file_path,
            maxBytes=self.config["max_file_size"],
            backupCount=self.config["backup_count"],
            encoding='utf-8'
        )
        file_handler.setLevel(LOG_LEVELS[self.config["file_level"]])
        
        file_formatter = logging.Formatter(
            fmt=self.config["format_file"],
            datefmt=self.config["date_format"]
        )
        file_handler.setFormatter(file_formatter)
        
        # Add to root logger  
        logging.getLogger().addHandler(file_handler)
        
    def _configure_project_loggers(self) -> None:
        """Configure all project-specific loggers."""
        for name, logger_name in LOGGER_NAMES.items():
            logger = logging.getLogger(logger_name)
            logger.setLevel(logging.DEBUG)  # Let handlers control the actual level
            self.loggers[name] = logger
            
    def get_logger(self, name: str) -> logging.Logger:
        """
        Get a logger instance with proper configuration.
        
        Args:
            name: Logger name (preferably __name__ from calling module)
            
        Returns:
            Configured logger instance
        """
        # Ensure logging is configured
        if not _logging_configured:
            self.configure_logging()
            
        return logging.getLogger(name)
    
    def get_module_logger(self, module_type: str) -> logging.Logger:
        """
        Get a logger for a specific module type.
        
        Args:
            module_type: Type of module (audio, stt, tts, etc.)
            
        Returns:
            Configured logger instance
        """
        if module_type in self.loggers:
            return self.loggers[module_type]
        
        # Fallback to creating new logger
        logger_name = f"talkbridge.{module_type}"
        return self.get_logger(logger_name)

# Global logger instance
_logger_instance = TalkBridgeLogger()

def configure_logging(
    console_level: str = "INFO",
    file_level: str = "DEBUG", 
    log_dir: Optional[str] = None,
    development_mode: bool = True,
    force_reconfigure: bool = False
) -> None:
    """
    Configure the global logging system.
    
    Args:
        console_level: Console output level
        file_level: File output level
        log_dir: Directory for log files
        development_mode: Enable development logging features
        force_reconfigure: Force reconfiguration even if already configured
    """
    _logger_instance.configure_logging(
        console_level=console_level,
        file_level=file_level,
        log_dir=log_dir,
        development_mode=development_mode,
        force_reconfigure=force_reconfigure
    )

def get_logger(name: str) -> logging.Logger:
    """
    Get a logger instance with proper configuration.
    
    Args:
        name: Logger name (preferably __name__ from calling module)
        
    Returns:
        Configured logger instance
        
    Example:
        logger = get_logger(__name__)
        logger.info("Module initialized")
    """
    return _logger_instance.get_logger(name)

def get_module_logger(module_type: str) -> logging.Logger:
    """
    Get a logger for a specific module type.
    
    Args:
        module_type: Module type (audio, stt, tts, translation, ui, desktop)
        
    Returns:
        Configured logger instance
        
    Example:
        logger = get_module_logger("audio")
        logger.error("Audio capture failed")
    """
    return _logger_instance.get_module_logger(module_type)

def log_exception(
    logger: logging.Logger, 
    exception: Exception, 
    context: str = "",
    notify_ui: bool = False
) -> None:
    """
    Log an exception with full context and stack trace.
    
    Args:
        logger: Logger instance to use
        exception: Exception to log
        context: Additional context information
        notify_ui: Whether to also notify the UI layer
        
    Example:
        try:
            risky_operation()
        except ValueError as e:
            log_exception(logger, e, "Failed to parse user input")
    """
    error_msg = f"{context}: {str(exception)}" if context else str(exception)
    logger.exception(error_msg)
    
    # TODO: Integrate with UI notification system when notify_ui=True
    # This will be implemented in the UI integration task

def add_error_context(logger: logging.Logger, component: str) -> None:
    """
    Add error context to a logger for better traceability.
    
    Args:
        logger: Logger instance
        component: Component name for context
        
    Example:
        logger = get_logger(__name__)
        add_error_context(logger, "AudioCapture")
    """
    # This function can be enhanced to add custom filters or adapters
    # For now, it serves as a placeholder for future enhancements
    pass

def setup_development_logging() -> None:
    """Setup logging optimized for development."""
    configure_logging(
        console_level="DEBUG",
        file_level="DEBUG",
        development_mode=True
    )

def setup_production_logging(log_dir: str = "/var/log/talkbridge") -> None:
    """Setup logging optimized for production."""
    configure_logging(
        console_level="WARNING",
        file_level="INFO",
        log_dir=log_dir,
        development_mode=False
    )

def get_log_statistics() -> Dict[str, Any]:
    """
    Get statistics about the current logging configuration.
    
    Returns:
        Dictionary with logging statistics
    """
    stats = {
        "configured": _logging_configured,
        "log_dir": _logger_instance.config["log_dir"],
        "console_level": _logger_instance.config["console_level"],
        "file_level": _logger_instance.config["file_level"],
        "active_loggers": len(_logger_instance.loggers),
        "timestamp": datetime.now().isoformat()
    }
    
    # Add log file information if available
    log_file_path = Path(_logger_instance.config["log_dir"]) / _logger_instance.config["log_file"]
    if log_file_path.exists():
        stats["log_file_size"] = log_file_path.stat().st_size
        stats["log_file_path"] = str(log_file_path.absolute())
    
    return stats

def reset_logging_for_testing() -> None:
    """
    Reset logging configuration for testing purposes.
    
    Warning: This should only be used in tests!
    """
    global _logging_configured
    
    with _config_lock:
        # Clear all handlers
        root_logger = logging.getLogger()
        for handler in root_logger.handlers[:]:
            handler.close()
            root_logger.removeHandler(handler)
        
        # Reset global state
        _logging_configured = False
        _logger_instance._handlers_created = False
        _logger_instance.loggers.clear()
        
        # Reset config to defaults
        _logger_instance.config = DEFAULT_CONFIG.copy()

def mark_logging_configured() -> None:
    """Mark logging as configured to prevent module overrides."""
    global _logging_configured
    _logging_configured = True

def is_logging_configured() -> bool:
    """Check if logging has been configured."""
    return _logging_configured

def ensure_error_logging() -> bool:
    """
    Ensure that error logging is properly configured.
    Always returns True as error logging is handled by the unified system.
    
    Returns:
        True if error logging is configured
    """
    return _logging_configured

def add_error_context(logger: logging.Logger, context: str = "") -> None:
    """
    Add context information to error logging.
    
    Args:
        logger: Logger instance
        context: Additional context string
    """
    def error_with_context(msg, *args, **kwargs):
        """Enhanced error logging with context."""
        if context:
            enhanced_msg = f"[{context}] {msg}"
        else:
            enhanced_msg = msg
        return logger._original_error(enhanced_msg, *args, **kwargs)
    
    # Store original error method and replace with enhanced version
    if not hasattr(logger, '_original_error'):
        logger._original_error = logger.error
        logger.error = error_with_context

# Initialize logging on import with safe defaults
# This ensures logging works even if configure_logging() is never called explicitly
if not _logging_configured:
    try:
        configure_logging(development_mode=True)
    except Exception:
        # Fallback: ensure minimal logging without using basicConfig
        # Create a simple logger if none exists
        logger = logging.getLogger("talkbridge")
        if not logger.handlers:
            handler = logging.StreamHandler()
            formatter = logging.Formatter(
                "%(asctime)s | %(name)s | %(levelname)s | %(message)s",
                datefmt="%Y-%m-%d %H:%M:%S"
            )
            handler.setFormatter(formatter)
            logger.addHandler(handler)
            logger.setLevel(logging.INFO)