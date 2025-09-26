"""
User-Facing Error System for TalkBridge.

This module provides structured error handling that separates
technical details from user-facing messages.
"""

import logging
from typing import Optional, Dict, Any
from dataclasses import dataclass

logger = logging.getLogger(__name__)


class UserFacingError(Exception):
    """
    Exception that carries both user-facing and technical information.
    
    This exception is designed to separate what users see from what
    developers need for debugging.
    """
    
    def __init__(
        self, 
        message: str, 
        *, 
        context: str | None = None, 
        details: str | None = None,
        error_code: str | None = None,
        recoverable: bool = True,
        user_action: str | None = None
    ):
        """
        Initialize a user-facing error.
        
        Args:
            message: User-friendly error message (what the user sees)
            context: Context/category where the error occurred (e.g., "Audio Capture")
            details: Technical details for logging/debugging
            error_code: Optional error code for programmatic handling
            recoverable: Whether the user can potentially recover from this error
            user_action: Suggested action for the user to take
        """
        super().__init__(message)
        self.message = message
        self.context = context
        self.details = details
        self.error_code = error_code
        self.recoverable = recoverable
        self.user_action = user_action
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization."""
        return {
            'message': self.message,
            'context': self.context,
            'details': self.details,
            'error_code': self.error_code,
            'recoverable': self.recoverable,
            'user_action': self.user_action
        }
    
    def __str__(self) -> str:
        """String representation for logging."""
        parts = [self.message]
        if self.context:
            parts.append(f"Context: {self.context}")
        if self.details:
            parts.append(f"Details: {self.details}")
        if self.error_code:
            parts.append(f"Code: {self.error_code}")
        return " | ".join(parts)


@dataclass
class ErrorContext:
    """Context information for error handling."""
    operation: str
    component: str
    user_visible: bool = True
    retry_possible: bool = False
    
    
class ErrorCategory:
    """Common error categories with standardized messages."""
    
    # Audio/Microphone errors
    MICROPHONE_NOT_AVAILABLE = "microphone_not_available"
    AUDIO_DEVICE_ERROR = "audio_device_error"
    AUDIO_PERMISSION_DENIED = "audio_permission_denied"
    
    # Network/Connection errors
    NETWORK_CONNECTION_FAILED = "network_connection_failed"
    SERVICE_UNAVAILABLE = "service_unavailable"
    TIMEOUT_ERROR = "timeout_error"
    
    # Authentication errors
    AUTHENTICATION_FAILED = "authentication_failed"
    AUTHORIZATION_DENIED = "authorization_denied"
    SESSION_EXPIRED = "session_expired"
    
    # File/Storage errors
    FILE_NOT_FOUND = "file_not_found"
    PERMISSION_DENIED = "permission_denied"
    DISK_FULL = "disk_full"
    
    # Service errors
    SERVICE_INITIALIZATION_FAILED = "service_initialization_failed"
    MODEL_LOADING_FAILED = "model_loading_failed"
    PROCESSING_ERROR = "processing_error"
    
    # Configuration errors
    INVALID_CONFIGURATION = "invalid_configuration"
    MISSING_DEPENDENCY = "missing_dependency"
    
    # User input errors
    INVALID_INPUT = "invalid_input"
    VALIDATION_FAILED = "validation_failed"


class ErrorHandler:
    """
    Centralized error handling with user notification integration.
    """
    
    def __init__(self):
        self._error_messages = self._init_error_messages()
    
    def _init_error_messages(self) -> Dict[str, Dict[str, str]]:
        """Initialize standard error messages."""
        return {
            ErrorCategory.MICROPHONE_NOT_AVAILABLE: {
                'message': 'Microphone not available',
                'context': 'Audio Capture',
                'user_action': 'Please check your microphone connection and permissions'
            },
            ErrorCategory.AUDIO_DEVICE_ERROR: {
                'message': 'Audio device error',
                'context': 'Audio System',
                'user_action': 'Please check your audio device settings'
            },
            ErrorCategory.AUDIO_PERMISSION_DENIED: {
                'message': 'Microphone permission denied',
                'context': 'Audio Permissions',
                'user_action': 'Please grant microphone access in your system settings'
            },
            ErrorCategory.NETWORK_CONNECTION_FAILED: {
                'message': 'Network connection failed',
                'context': 'Network',
                'user_action': 'Please check your internet connection'
            },
            ErrorCategory.SERVICE_UNAVAILABLE: {
                'message': 'Service temporarily unavailable',
                'context': 'Service Connection',
                'user_action': 'Please try again in a few moments'
            },
            ErrorCategory.TIMEOUT_ERROR: {
                'message': 'Operation timed out',
                'context': 'Network',
                'user_action': 'Please try again or check your connection'
            },
            ErrorCategory.AUTHENTICATION_FAILED: {
                'message': 'Authentication failed',
                'context': 'Authentication',
                'user_action': 'Please check your username and password'
            },
            ErrorCategory.AUTHORIZATION_DENIED: {
                'message': 'Access denied',
                'context': 'Authorization',
                'user_action': 'You do not have permission for this action'
            },
            ErrorCategory.SESSION_EXPIRED: {
                'message': 'Session expired',
                'context': 'Authentication',
                'user_action': 'Please log in again'
            },
            ErrorCategory.FILE_NOT_FOUND: {
                'message': 'File not found',
                'context': 'File System',
                'user_action': 'Please check the file path'
            },
            ErrorCategory.PERMISSION_DENIED: {
                'message': 'Permission denied',
                'context': 'File System',
                'user_action': 'Please check file permissions'
            },
            ErrorCategory.DISK_FULL: {
                'message': 'Insufficient disk space',
                'context': 'Storage',
                'user_action': 'Please free up disk space'
            },
            ErrorCategory.SERVICE_INITIALIZATION_FAILED: {
                'message': 'Service failed to start',
                'context': 'System',
                'user_action': 'Please restart the application'
            },
            ErrorCategory.MODEL_LOADING_FAILED: {
                'message': 'AI model failed to load',
                'context': 'AI Processing',
                'user_action': 'Please check your internet connection or try again'
            },
            ErrorCategory.PROCESSING_ERROR: {
                'message': 'Processing failed',
                'context': 'Processing',
                'user_action': 'Please try again'
            },
            ErrorCategory.INVALID_CONFIGURATION: {
                'message': 'Invalid configuration',
                'context': 'Configuration',
                'user_action': 'Please check your settings'
            },
            ErrorCategory.MISSING_DEPENDENCY: {
                'message': 'Required component not available',
                'context': 'System',
                'user_action': 'Please ensure all dependencies are installed'
            },
            ErrorCategory.INVALID_INPUT: {
                'message': 'Invalid input',
                'context': 'Input Validation',
                'user_action': 'Please check your input and try again'
            },
            ErrorCategory.VALIDATION_FAILED: {
                'message': 'Validation failed',
                'context': 'Input Validation',
                'user_action': 'Please correct the highlighted fields'
            }
        }
    
    def create_user_error(
        self, 
        error_category: str, 
        details: str = None,
        original_exception: Exception = None,
        **kwargs
    ) -> UserFacingError:
        """
        Create a user-facing error from a category.
        
        Args:
            error_category: Error category from ErrorCategory
            details: Technical details for logging
            original_exception: Original exception that caused this error
            **kwargs: Additional parameters to override defaults
            
        Returns:
            UserFacingError instance
        """
        error_info = self._error_messages.get(error_category, {
            'message': 'An unexpected error occurred',
            'context': 'System',
            'user_action': 'Please try again or contact support'
        })
        
        # Merge with provided kwargs
        merged_info = {**error_info, **kwargs}
        
        # Add original exception details if provided
        if original_exception and not details:
            details = str(original_exception)
        
        return UserFacingError(
            message=merged_info['message'],
            context=merged_info.get('context'),
            details=details,
            error_code=error_category,
            user_action=merged_info.get('user_action'),
            recoverable=merged_info.get('recoverable', True)
        )
    
    def handle_exception(
        self, 
        exception: Exception, 
        context: ErrorContext,
        notify_user: bool = True
    ) -> Optional[UserFacingError]:
        """
        Handle an exception with appropriate logging and user notification.
        
        Args:
            exception: The exception to handle
            context: Context information
            notify_user: Whether to send user notification
            
        Returns:
            UserFacingError if created, None otherwise
        """
        # Log technical details
        logger.error(
            f"Error in {context.component}.{context.operation}: {exception}",
            exc_info=True
        )
        
        user_error = None
        
        # If it's already a UserFacingError, use it directly
        if isinstance(exception, UserFacingError):
            user_error = exception
        elif context.user_visible:
            # Try to map common exceptions to user-friendly errors
            user_error = self._map_exception_to_user_error(exception, context)
        
        # Send notification if requested
        if notify_user and user_error:
            self._notify_user_of_error(user_error)
        
        return user_error
    
    def _map_exception_to_user_error(
        self, 
        exception: Exception, 
        context: ErrorContext
    ) -> UserFacingError:
        """
        Map a technical exception to a user-friendly error.
        
        Args:
            exception: The exception to map
            context: Context information
            
        Returns:
            UserFacingError instance
        """
        exception_name = type(exception).__name__
        exception_message = str(exception).lower()
        
        # Audio-related errors
        if 'audio' in context.component.lower() or 'microphone' in exception_message:
            if 'permission' in exception_message or 'access' in exception_message:
                return self.create_user_error(
                    ErrorCategory.AUDIO_PERMISSION_DENIED, 
                    str(exception)
                )
            elif 'device' in exception_message or 'not found' in exception_message:
                return self.create_user_error(
                    ErrorCategory.MICROPHONE_NOT_AVAILABLE,
                    str(exception)
                )
            else:
                return self.create_user_error(
                    ErrorCategory.AUDIO_DEVICE_ERROR,
                    str(exception)
                )
        
        # Network-related errors
        if any(keyword in exception_name.lower() for keyword in ['connection', 'network', 'timeout']):
            if 'timeout' in exception_name.lower():
                return self.create_user_error(
                    ErrorCategory.TIMEOUT_ERROR,
                    str(exception)
                )
            else:
                return self.create_user_error(
                    ErrorCategory.NETWORK_CONNECTION_FAILED,
                    str(exception)
                )
        
        # File system errors
        if exception_name in ['FileNotFoundError', 'IOError']:
            return self.create_user_error(
                ErrorCategory.FILE_NOT_FOUND,
                str(exception)
            )
        elif exception_name == 'PermissionError':
            return self.create_user_error(
                ErrorCategory.PERMISSION_DENIED,
                str(exception)
            )
        
        # Generic error
        return UserFacingError(
            message="An unexpected error occurred",
            context=context.component,
            details=str(exception),
            error_code="generic_error",
            user_action="Please try again or contact support"
        )
    
    def _notify_user_of_error(self, user_error: UserFacingError) -> None:
        """
        Send user notification for an error.
        
        Args:
            user_error: The user-facing error to notify about
        """
        try:
            from .ui.notifier import notify_error
            
            notify_error(
                user_error.message,
                context=user_error.context,
                details=user_error.user_action
            )
        except ImportError:
            # Fallback if notifier is not available
            logger.warning(f"Could not send user notification: {user_error}")


# Global error handler instance
_global_error_handler: Optional[ErrorHandler] = None


def get_error_handler() -> ErrorHandler:
    """Get the global error handler instance."""
    global _global_error_handler
    if _global_error_handler is None:
        _global_error_handler = ErrorHandler()
    return _global_error_handler


def handle_user_facing_error(
    error_category: str,
    details: str = None,
    original_exception: Exception = None,
    context: str = None,
    notify: bool = True
) -> UserFacingError:
    """
    Convenience function to create and handle a user-facing error.
    
    Args:
        error_category: Error category from ErrorCategory
        details: Technical details
        original_exception: Original exception
        context: Error context
        notify: Whether to notify user
        
    Returns:
        UserFacingError instance
    """
    handler = get_error_handler()
    user_error = handler.create_user_error(
        error_category, 
        details, 
        original_exception,
        context=context
    )
    
    if notify:
        handler._notify_user_of_error(user_error)
    
    return user_error


# Context manager for error handling
class ErrorHandlingContext:
    """Context manager for automatic error handling."""
    
    def __init__(
        self, 
        component: str, 
        operation: str, 
        notify_user: bool = True,
        suppress_exceptions: bool = False
    ):
        self.context = ErrorContext(operation, component)
        self.notify_user = notify_user
        self.suppress_exceptions = suppress_exceptions
        self.error_handler = get_error_handler()
    
    def __enter__(self):
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        if exc_type is not None:
            self.error_handler.handle_exception(
                exc_val, 
                self.context, 
                self.notify_user
            )
            return self.suppress_exceptions  # Suppress if requested
        return False