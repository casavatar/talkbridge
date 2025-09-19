"""
Framework-agnostic notification system for TalkBridge.

This module provides a central event bus for notifications that can be consumed
by both Desktop (CustomTkinter) and Web (Flask) UIs without tight coupling.
"""

from dataclasses import dataclass
from enum import Enum
from typing import Optional, Callable, Protocol, List
import threading
import logging

logger = logging.getLogger(__name__)


class Level(str, Enum):
    """Notification severity levels."""
    INFO = "info"
    WARNING = "warning"
    ERROR = "error"
    SUCCESS = "success"
    DEBUG = "debug"


@dataclass
class Notification:
    """
    A notification message with context and details.
    
    Attributes:
        level: Severity level of the notification
        message: User-facing message (short, descriptive)
        details: Optional technical details for debugging
        context: Optional context/category (e.g., "Audio Capture", "Authentication")
        timestamp: When the notification was created
    """
    level: Level
    message: str
    details: Optional[str] = None
    context: Optional[str] = None
    
    def __post_init__(self):
        """Set timestamp after initialization."""
        import datetime
        if not hasattr(self, 'timestamp'):
            self.timestamp = datetime.datetime.now()


class NotifierPort(Protocol):
    """
    Protocol for notification handlers.
    
    UI implementations should implement this interface to receive notifications.
    """
    
    def push(self, note: Notification) -> None:
        """
        Handle a notification.
        
        Args:
            note: The notification to handle
        """
        ...


# Global subscriber registry
_subscribers: List[NotifierPort] = []
_subscribers_lock = threading.RLock()


def subscribe(handler: NotifierPort) -> None:
    """
    Subscribe a handler to receive notifications.
    
    Args:
        handler: NotifierPort implementation that will receive notifications
    """
    with _subscribers_lock:
        if handler not in _subscribers:
            _subscribers.append(handler)
            logger.debug(f"Subscribed notification handler: {type(handler).__name__}")


def unsubscribe(handler: NotifierPort) -> None:
    """
    Unsubscribe a handler from receiving notifications.
    
    Args:
        handler: NotifierPort implementation to remove
    """
    with _subscribers_lock:
        if handler in _subscribers:
            _subscribers.remove(handler)
            logger.debug(f"Unsubscribed notification handler: {type(handler).__name__}")


def notify(level: Level, message: str, *, details: str | None = None, context: str | None = None) -> None:
    """
    Send a notification to all subscribed handlers.
    
    Args:
        level: Severity level
        message: User-facing message
        details: Optional technical details
        context: Optional context/category
    """
    note = Notification(level, message, details, context)
    
    # Create a snapshot of subscribers to avoid holding lock during notification
    with _subscribers_lock:
        subscribers_snapshot = list(_subscribers)
    
    # Notify all subscribers
    for subscriber in subscribers_snapshot:
        try:
            subscriber.push(note)
        except Exception as e:
            # Don't let one bad subscriber break others
            logger.error(f"Error in notification handler {type(subscriber).__name__}: {e}")


# Convenience functions for common notification levels
def notify_info(msg: str, **kw) -> None:
    """Send an info notification."""
    notify(Level.INFO, msg, **kw)


def notify_warn(msg: str, **kw) -> None:
    """Send a warning notification."""
    notify(Level.WARNING, msg, **kw)


def notify_error(msg: str, **kw) -> None:
    """Send an error notification."""
    notify(Level.ERROR, msg, **kw)


def notify_success(msg: str, **kw) -> None:
    """Send a success notification."""
    notify(Level.SUCCESS, msg, **kw)


def notify_debug(msg: str, **kw) -> None:
    """Send a debug notification."""
    notify(Level.DEBUG, msg, **kw)


def get_subscriber_count() -> int:
    """Get the number of active subscribers (for testing/debugging)."""
    with _subscribers_lock:
        return len(_subscribers)


def clear_subscribers() -> None:
    """Clear all subscribers (for testing)."""
    with _subscribers_lock:
        _subscribers.clear()
        logger.debug("Cleared all notification subscribers")


# Context manager for temporary subscriptions
class NotificationSubscription:
    """Context manager for temporary notification subscriptions."""
    
    def __init__(self, handler: NotifierPort):
        self.handler = handler
    
    def __enter__(self) -> NotifierPort:
        subscribe(self.handler)
        return self.handler
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        unsubscribe(self.handler)