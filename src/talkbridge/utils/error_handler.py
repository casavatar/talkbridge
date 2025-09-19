#!/usr/bin/env python3
"""
TalkBridge Utils - Enhanced Error Handler
=========================================

Robust error handler with retry logic, backoff, and user notifications

Author: TalkBridge Team
Date: 2025-09-18
Version: 2.0

Requirements:
- None
======================================================================
Functions:
- handle_error: Handle errors with optional user notification and retry logic
- retry_with_backoff: Decorator for automatic retry with exponential backoff
- log_error: Log an exception to the error log file with timestamp and context
- format_error: Format an exception into a user-friendly message
- get_last_errors: Retrieve the last N error log entries
- suppress_non_critical: Determine if errors can be safely suppressed
- raise_or_log: Raise critical errors, log and suppress non-critical ones
- wrap_function: Decorator to auto-log uncaught errors in a function
======================================================================
"""

import os
import logging
import traceback
import time
import random
from datetime import datetime
from typing import List, Callable, Any, TypeVar, Optional, Dict, Type
from functools import wraps
from talkbridge.logging_config import get_logger

logger = get_logger(__name__)

# Type variables for generic typing
F = TypeVar('F', bound=Callable[..., Any])

class RetryableError(Exception):
    """Exception that can be retried with backoff."""
    pass

class CriticalError(Exception):
    """Exception that should not be retried and must be escalated."""
    pass

class UserNotificationError(Exception):
    """Exception that requires user notification."""
    pass

def handle_error(exc: Exception, context: str, user_message: str = "", 
                 logger_instance: Optional[logging.Logger] = None) -> None:
    """
    Handle errors with structured logging and optional user notification.
    
    Args:
        exc: Exception that occurred
        context: Context where error occurred (e.g. "Audio", "Desktop", "TTS")
        user_message: Custom message to show user (if empty, uses default)
        logger_instance: Specific logger to use (defaults to module logger)
    """
    log = logger_instance or logger
    log.error(f"Error in {context}: {exc}", exc_info=True)
    
    # For UserNotificationError or when user_message is provided, notify user
    if isinstance(exc, UserNotificationError) or user_message:
        try:
            message = user_message or str(exc)
            notify_error(f"{context}: {message}")
        except Exception as notify_exc:
            log.warning(f"Failed to show user notification: {notify_exc}")
    
    # Re-raise if it's a critical error
    if isinstance(exc, CriticalError):
        raise exc

def retry_with_backoff(
    max_retries: int = 3,
    initial_delay: float = 1.0,
    max_delay: float = 60.0,
    backoff_factor: float = 2.0,
    jitter: bool = True,
    retryable_exceptions: Optional[List[Type[Exception]]] = None
) -> Callable[[F], F]:
    """
    Decorator for automatic retry with exponential backoff.
    
    Args:
        max_retries: Maximum number of retry attempts
        initial_delay: Initial delay between retries (seconds)
        max_delay: Maximum delay between retries (seconds) 
        backoff_factor: Factor to multiply delay by on each retry
        jitter: Add random jitter to prevent thundering herd
        retryable_exceptions: List of exception types that can be retried
    
    Returns:
        Decorator function
    """
    if retryable_exceptions is None:
        retryable_exceptions = [RetryableError, ConnectionError, TimeoutError]
    
    def decorator(func: F) -> F:
        @wraps(func)
        def wrapper(*args, **kwargs):
            last_exception = None
            delay = initial_delay
            
            for attempt in range(max_retries + 1):
                try:
                    return func(*args, **kwargs)
                except Exception as e:
                    last_exception = e
                    
                    # Check if this exception type is retryable
                    if not any(isinstance(e, exc_type) for exc_type in retryable_exceptions):
                        logger.error(f"Non-retryable error in {func.__name__}: {e}", exc_info=True)
                        raise
                    
                    # If this is the last attempt, don't retry
                    if attempt == max_retries:
                        logger.error(f"Max retries ({max_retries}) exceeded in {func.__name__}: {e}", exc_info=True)
                        raise
                    
                    # Add jitter to delay if enabled
                    actual_delay = delay
                    if jitter:
                        actual_delay *= (0.5 + random.random())
                    
                    logger.warning(f"Retrying {func.__name__} in {actual_delay:.2f}s (attempt {attempt + 1}/{max_retries}): {e}")
                    time.sleep(actual_delay)
                    
                    # Increase delay for next attempt
                    delay = min(delay * backoff_factor, max_delay)
            
            # This should never be reached, but just in case
            raise last_exception
        
        return wrapper
    return decorator

def notify_error(message: str) -> None:
    """
    Attempt to notify user of error through available UI channels.
    
    Args:
        message: Error message to display to user
    """
    # Try desktop notification first - look for active toast manager
    try:
        # Check if we're in desktop mode and can access the event bus
        from talkbridge.desktop.ui.events import EventBus, StatusEvent
        event_bus = EventBus.get_instance()
        event = StatusEvent(
            message=message,
            level="error",
            duration=8.0  # Longer duration for errors
        )
        event_bus.emit("status", event)
        logger.debug(f"Sent error notification to desktop UI: {message}")
        return
    except (ImportError, AttributeError, Exception) as e:
        logger.debug(f"Desktop notification not available: {e}")
    
    # Try web UI notification
    try:
        from talkbridge.ui.notifier import notify_error as web_notify_error
        web_notify_error(message)
        logger.debug(f"Sent error notification to web UI: {message}")
        return
    except ImportError:
        logger.debug("Web UI notification not available")
    
    # Fallback to logging
    logger.error(f"User notification (no UI available): {message}")

class ErrorHandler:
    """
    Centralized error handler for the TalkBridge system.
    Provides static methods for logging, formatting, and error management.
    """

    @staticmethod
    def log_error(error: Exception, context: str = "") -> None:
        """
        Log an exception with context.
        Args:
            error: The exception instance
            context: Optional context string (e.g., module or function name)
        """
        logger.error(f"Error in {context}: {error}", exc_info=True)

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
        Retrieve the last N error log entries from the unified log.
        Args:
            limit: Number of recent errors to retrieve
        Returns:
            List of error log lines (most recent first)
        """
        log_file = os.path.join(os.path.dirname(__file__), '..', '..', '..', 'data', 'logs', 'talkbridge.log')
        if not os.path.exists(log_file):
            return []
        
        try:
            with open(log_file, 'r', encoding='utf-8') as f:
                lines = f.readlines()
            # Filter only lines that contain ERROR level
            error_lines = [line for line in lines if '| ERROR |' in line]
            return error_lines[-limit:][::-1]  # Most recent first
        except Exception as e:
            logger.warning(f"Failed to read log file: {e}")
            return []

    @staticmethod
    def suppress_non_critical(error: Exception) -> bool:
        """
        Determine if errors can be safely suppressed.
        Args:
            error: The exception instance
        Returns:
            True if error is non-critical and can be suppressed
        """
        # Define non-critical error types
        non_critical_types = (
            FileNotFoundError,  # Missing optional files
            ImportError,        # Optional dependencies
            PermissionError,    # When we have fallbacks
        )
        return isinstance(error, non_critical_types)

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
            raise CriticalError(ErrorHandler.format_error(error, context)) from error

    @staticmethod
    def wrap_function(func: Callable) -> Callable:
        """
        Decorator to auto-log uncaught errors in a function.
        Args:
            func: The function to wrap
        Returns:
            Wrapped function
        """
        @wraps(func)
        def wrapper(*args, **kwargs):
            try:
                return func(*args, **kwargs)
            except Exception as e:
                ErrorHandler.log_error(e, context=func.__name__)
                # Re-raise to maintain error propagation
                raise
        return wrapper

# Backward compatibility aliases
SystemErrorHandled = CriticalError

# Example usage and helper functions
def safe_execute(func: Callable, *args, context: str = "", user_notify: bool = False, **kwargs) -> Any:
    """
    Safely execute a function with proper error handling.
    
    Args:
        func: Function to execute
        *args: Positional arguments for function
        context: Context description for error logging
        user_notify: Whether to notify user of errors
        **kwargs: Keyword arguments for function
    
    Returns:
        Function result or None if error occurred
    """
    try:
        return func(*args, **kwargs)
    except Exception as e:
        user_message = f"Operation failed: {str(e)}" if user_notify else ""
        handle_error(e, context or func.__name__, user_message)
        return None

# Example usage:
# 
# # Basic error handling with user notification
# try:
#     risky_operation()
# except Exception as e:
#     handle_error(e, "TTS Synthesis", user_notify=True)
#
# # Retry with exponential backoff
# @retry_with_backoff(max_retries=3, initial_delay=1.0)
# def unstable_network_call():
#     # This will retry up to 3 times with exponential backoff
#     response = requests.get("https://api.example.com/data")
#     if response.status_code == 500:
#         raise RetryableError("Server error, can retry")
#     return response.json()
#
# # Safe execution with error handling
# result = safe_execute(
#     risky_function, 
#     arg1, arg2, 
#     context="Audio Processing", 
#     user_notify=True
# )
#
# # Function wrapper for automatic error logging
# @ErrorHandler.wrap_function
# def synthesize_voice(text):
#     # Implementation here
#     if not text:
#         raise ValueError("Text cannot be empty")
#     return synthesized_audio 