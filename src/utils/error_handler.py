#!/usr/bin/env python3
"""
TalkBridge Utils - Error Handler
================================

Módulo error_handler para TalkBridge

Author: TalkBridge Team
Date: 2025-08-19
Version: 1.0

Requirements:
- None
======================================================================
Functions:
- log_error: Log an exception to the error log file with timestamp and context.
- format_error: Format an exception into a user-friendly message.
- get_last_errors: Retrieve the last N error log entries.
- suppress_non_critical: Optionally suppress non-critical errors (extend as needed).
- raise_or_log: Raise critical errors, log and suppress non-critical ones.
- wrap_function: Decorator to auto-log uncaught errors in a function.
- wrapper: Función wrapper
======================================================================
"""

import os
import logging
import traceback
from datetime import datetime
from typing import List, Callable, Any, TypeVar, cast

# Ensure logs directory exists
LOG_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'logs')
os.makedirs(LOG_DIR, exist_ok=True)
ERROR_LOG_FILE = os.path.join(LOG_DIR, 'errors.log')

# Configure logging
logging.basicConfig(
    filename=ERROR_LOG_FILE,
    filemode='a',
    format='%(asctime)s [%(levelname)s] %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S',
    level=logging.ERROR
)
logger = logging.getLogger('TalkBridgeErrorHandler')


class SystemErrorHandled(Exception):
    """
    Custom exception for system-level handled errors.
    Use this to distinguish between critical and non-critical errors.
    """
    pass


class ErrorHandler:
    """
    Centralized error handler for the TalkBridge system.
    Provides static methods for logging, formatting, and error management.
    """

    @staticmethod
    def log_error(error: Exception, context: str = "") -> None:
        """
        Log an exception to the error log file with timestamp and context.
        Args:
            error: The exception instance
            context: Optional context string (e.g., module or function name)
        """
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        error_type = type(error).__name__
        tb_str = ''.join(traceback.format_exception(type(error), error, error.__traceback__))
        log_entry = f"{timestamp} [{error_type}] {context}: {error}\n{tb_str}\n"
        logger.error(log_entry)

    @staticmethod
    def format_error(error: Exception, context: str = "") -> str:
        """
        Format an exception into a user-friendly message.
        Args:
            error: The exception instance
            context: Optional context string
        Returns:
            User-friendly error message string
        """
        error_type = type(error).__name__
        if context:
            return f"An error occurred in {context}: {error_type} - {error}"
        else:
            return f"An error occurred: {error_type} - {error}"

    @staticmethod
    def get_last_errors(limit: int = 10) -> List[str]:
        """
        Retrieve the last N error log entries.
        Args:
            limit: Number of recent errors to retrieve
        Returns:
            List of error log lines (most recent first)
        """
        if not os.path.exists(ERROR_LOG_FILE):
            return []
        with open(ERROR_LOG_FILE, 'r', encoding='utf-8') as f:
            lines = f.readlines()
        # Filter only lines that look like error entries
        error_lines = [line for line in lines if 'ERROR' in line or 'Traceback' in line]
        return error_lines[-limit:][::-1]  # Most recent first

    @staticmethod
    def suppress_non_critical(error: Exception) -> bool:
        """
        Optionally suppress non-critical errors (extend as needed).
        Args:
            error: The exception instance
        Returns:
            True if error is non-critical and can be suppressed
        """
        # Example: suppress FileNotFoundError in some contexts
        return isinstance(error, FileNotFoundError)

    @staticmethod
    def raise_or_log(error: Exception, context: str = "") -> None:
        """
        Raise critical errors, log and suppress non-critical ones.
        Args:
            error: The exception instance
            context: Optional context string
        """
        if ErrorHandler.suppress_non_critical(error):
            ErrorHandler.log_error(error, context)
        else:
            ErrorHandler.log_error(error, context)
            raise SystemErrorHandled(ErrorHandler.format_error(error, context)) from error

    @staticmethod
    def wrap_function(func: Callable) -> Callable:
        """
        Decorator to auto-log uncaught errors in a function.
        Args:
            func: The function to wrap
        Returns:
            Wrapped function
        """
        def wrapper(*args, **kwargs):
            try:
                return func(*args, **kwargs)
            except Exception as e:
                ErrorHandler.log_error(e, context=func.__name__)
                # Optionally re-raise or suppress
                raise
        return wrapper

# Example usage in another module (e.g., tts/synthesizer.py):
#
# from utils.error_handler import ErrorHandler
#
# @ErrorHandler.wrap_function
# def synthesize_voice(text):
#     ...
#     raise RuntimeError("TTS model not loaded")
#
# try:
#     synthesize_voice("Hello")
# except Exception as e:
#     print(ErrorHandler.format_error(e, context="TTS Synthesis"))
#
# # To log an error manually:
# try:
#     ...
# except Exception as e:
#     ErrorHandler.log_error(e, context="face_sync.detect_landmarks") 