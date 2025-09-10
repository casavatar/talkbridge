#!/usr/bin/env python3
"""
TalkBridge Desktop - Logging Configuration
==========================================

Centralized logging configuration for the desktop application.
Prevents conflicts from multiple logging.basicConfig calls.

Author: TalkBridge Team
Date: 2025-09-09
Version: 1.0
"""

import logging
import sys
from pathlib import Path
from typing import Optional

# Flag to track if logging has been configured
_LOGGING_CONFIGURED = False
_ERROR_HANDLER_CONFIGURED = False


def get_logger(name: str) -> logging.Logger:
    """
    Get a logger instance with proper configuration.
    
    Args:
        name: Logger name (usually __name__)
        
    Returns:
        Configured logger instance
    """
    return logging.getLogger(name)


def configure_module_logging(module_name: str, level: int = logging.INFO) -> logging.Logger:
    """
    Configure logging for a specific module without overriding global config.
    
    Args:
        module_name: Name of the module
        level: Logging level for this module
        
    Returns:
        Configured logger for the module
    """
    logger = logging.getLogger(module_name)
    logger.setLevel(level)
    
    # Don't call basicConfig if already configured
    if not _LOGGING_CONFIGURED:
        logger.warning(f"Global logging not yet configured for module: {module_name}")
    
    return logger


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


def log_exception(logger: logging.Logger, error: Exception, context: str = "") -> None:
    """
    Log an exception with full traceback and context.
    
    Args:
        logger: Logger instance
        error: Exception to log
        context: Additional context information
    """
    error_msg = f"{context}: {type(error).__name__}: {str(error)}" if context else f"{type(error).__name__}: {str(error)}"
    logger.error(error_msg, exc_info=True)


def ensure_error_logging() -> bool:
    """
    Ensure that error logging to errors.log is properly configured.
    
    Returns:
        True if error logging is configured, False otherwise
    """
    global _ERROR_HANDLER_CONFIGURED
    
    if _ERROR_HANDLER_CONFIGURED:
        return True
    
    try:
        # Check if we have an error handler configured
        root_logger = logging.getLogger()
        has_error_handler = False
        
        for handler in root_logger.handlers:
            if isinstance(handler, logging.FileHandler):
                if 'errors.log' in str(handler.baseFilename):
                    if handler.level <= logging.ERROR:
                        has_error_handler = True
                        break
        
        if has_error_handler:
            _ERROR_HANDLER_CONFIGURED = True
            return True
        else:
            # Create emergency error handler if missing
            from pathlib import Path
            project_root = Path(__file__).parent.parent.parent
            log_dir = project_root / "data" / "logs"
            log_dir.mkdir(parents=True, exist_ok=True)
            
            error_file = log_dir / "errors.log"
            error_handler = logging.FileHandler(error_file, encoding='utf-8')
            error_handler.setLevel(logging.ERROR)
            error_handler.setFormatter(
                logging.Formatter('%(asctime)s [%(levelname)s] %(name)s:%(lineno)d - %(message)s')
            )
            
            root_logger.addHandler(error_handler)
            _ERROR_HANDLER_CONFIGURED = True
            
            # Test the handler
            test_logger = logging.getLogger("talkbridge.logging.emergency")
            test_logger.error("Emergency error handler configured - errors.log should be working now")
            
            return True
            
    except Exception as e:
        print(f"Failed to ensure error logging: {e}")
        return False


def mark_logging_configured() -> None:
    """Mark logging as configured to prevent module overrides."""
    global _LOGGING_CONFIGURED
    _LOGGING_CONFIGURED = True


def is_logging_configured() -> bool:
    """Check if logging has been configured."""
    return _LOGGING_CONFIGURED


# Monkey patch to prevent other modules from calling basicConfig
_original_basicConfig = logging.basicConfig

def protected_basicConfig(*args, **kwargs):
    """
    Protected version of basicConfig that warns if called after initial setup.
    """
    if _LOGGING_CONFIGURED and not kwargs.get('force', False):
        caller_frame = sys._getframe(1)
        caller_file = caller_frame.f_code.co_filename
        caller_line = caller_frame.f_lineno
        
        logger = logging.getLogger("talkbridge.logging.protection")
        logger.warning(f"Attempted logging.basicConfig override from {caller_file}:{caller_line} - ignored")
        return
    
    return _original_basicConfig(*args, **kwargs)

# Apply protection
logging.basicConfig = protected_basicConfig
