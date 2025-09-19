#!/usr/bin/env python3
"""
TalkBridge Desktop - UI Events System
===================================

Event contracts and pub-sub system for decoupling UI components from business logic.

Author: TalkBridge Team
Date: 2025-09-18
Version: 1.0
"""

from typing import Callable, Protocol, Literal, List, Dict, Any, Optional
from dataclasses import dataclass
import logging
import time

# Type aliases for better readability
Level = Literal["info", "warning", "error", "success"]
AudioSource = Literal["mic", "system"]
DeviceType = Literal["input", "output", "loopback"]

@dataclass
class TranscriptEvent:
    """Event data for speech transcription."""
    source: AudioSource
    text: str
    language: str
    confidence: Optional[float] = None
    timestamp: Optional[float] = None

@dataclass
class TranslationEvent:
    """Event data for translation."""
    source: AudioSource
    original_text: str
    source_language: str
    target_language: str
    translated_text: str
    timestamp: Optional[float] = None

@dataclass
class StatusEvent:
    """Event data for status notifications."""
    message: str
    level: Level = "info"
    duration: Optional[float] = None  # Auto-dismiss after this many seconds
    timestamp: Optional[float] = None

@dataclass
class DeviceEvent:
    """Event data for device changes."""
    device_type: DeviceType
    device_id: Optional[str] = None
    device_name: Optional[str] = None
    is_available: bool = True
    timestamp: Optional[float] = None

@dataclass
class AudioStateEvent:
    """Event data for audio state changes."""
    source: AudioSource
    is_active: bool
    device_name: Optional[str] = None
    timestamp: Optional[float] = None

class UIEvents(Protocol):
    """Protocol defining UI event contracts."""
    
    def on_transcript(self, event: TranscriptEvent) -> None:
        """Handle speech transcript event."""
        ...
    
    def on_translation(self, event: TranslationEvent) -> None:
        """Handle translation event."""
        ...
    
    def on_status(self, event: StatusEvent) -> None:
        """Handle status notification event."""
        ...
    
    def on_device_change(self, event: DeviceEvent) -> None:
        """Handle device availability change event."""
        ...
    
    def on_audio_state_change(self, event: AudioStateEvent) -> None:
        """Handle audio capture state change event."""
        ...

class EventBus:
    """Simple pub-sub event bus for UI components."""
    
    def __init__(self):
        """Initialize the event bus."""
        self.logger = logging.getLogger("talkbridge.ui.events")
        self._subscribers: Dict[str, List[Callable]] = {
            "transcript": [],
            "translation": [],
            "status": [],
            "device_change": [],
            "audio_state_change": []
        }
        
    def subscribe(self, event_type: str, callback: Callable) -> None:
        """Subscribe a callback to an event type."""
        if event_type not in self._subscribers:
            self.logger.warning(f"Unknown event type: {event_type}")
            return
            
        if callback not in self._subscribers[event_type]:
            self._subscribers[event_type].append(callback)
            self.logger.debug(f"Subscribed callback to {event_type} events")
    
    def unsubscribe(self, event_type: str, callback: Callable) -> None:
        """Unsubscribe a callback from an event type."""
        if event_type in self._subscribers and callback in self._subscribers[event_type]:
            self._subscribers[event_type].remove(callback)
            self.logger.debug(f"Unsubscribed callback from {event_type} events")
    
    def emit_transcript(self, source: AudioSource, text: str, language: str, 
                       confidence: Optional[float] = None) -> None:
        """Emit a transcript event."""
        event = TranscriptEvent(
            source=source,
            text=text,
            language=language,
            confidence=confidence,
            timestamp=time.time()
        )
        self._emit("transcript", event)
    
    def emit_translation(self, source: AudioSource, original_text: str, 
                        source_language: str, target_language: str, 
                        translated_text: str) -> None:
        """Emit a translation event."""
        event = TranslationEvent(
            source=source,
            original_text=original_text,
            source_language=source_language,
            target_language=target_language,
            translated_text=translated_text,
            timestamp=time.time()
        )
        self._emit("translation", event)
    
    def emit_status(self, message: str, level: Level = "info", 
                   duration: Optional[float] = None) -> None:
        """Emit a status notification event."""
        event = StatusEvent(
            message=message,
            level=level,
            duration=duration,
            timestamp=time.time()
        )
        self._emit("status", event)
    
    def emit_device_change(self, device_type: DeviceType, device_id: Optional[str] = None,
                          device_name: Optional[str] = None, is_available: bool = True) -> None:
        """Emit a device change event."""
        event = DeviceEvent(
            device_type=device_type,
            device_id=device_id,
            device_name=device_name,
            is_available=is_available,
            timestamp=time.time()
        )
        self._emit("device_change", event)
    
    def emit_audio_state_change(self, source: AudioSource, is_active: bool,
                               device_name: Optional[str] = None) -> None:
        """Emit an audio state change event."""
        event = AudioStateEvent(
            source=source,
            is_active=is_active,
            device_name=device_name,
            timestamp=time.time()
        )
        self._emit("audio_state_change", event)
    
    def _emit(self, event_type: str, event_data: Any) -> None:
        """Internal method to emit events to all subscribers."""
        try:
            subscribers = self._subscribers.get(event_type, [])
            self.logger.debug(f"Emitting {event_type} event to {len(subscribers)} subscribers")
            
            for callback in subscribers[:]:  # Copy list to avoid modification during iteration
                try:
                    callback(event_data)
                except Exception as e:
                    self.logger.error(f"Error in event callback for {event_type}: {e}")
                    # Continue with other callbacks even if one fails
                    
        except Exception as e:
            self.logger.error(f"Error emitting {event_type} event: {e}")

class EventHandler:
    """Base class for components that handle UI events."""
    
    def __init__(self, event_bus: EventBus):
        """Initialize with event bus reference."""
        self.event_bus = event_bus
        self.logger = logging.getLogger(f"talkbridge.ui.{self.__class__.__name__.lower()}")
        
    def subscribe_to_events(self) -> None:
        """Override to subscribe to relevant events."""
        pass
    
    def unsubscribe_from_events(self) -> None:
        """Override to clean up event subscriptions."""
        pass

# Convenience functions for common event patterns
def create_transcript_event(source: AudioSource, text: str, language: str, 
                           confidence: Optional[float] = None) -> TranscriptEvent:
    """Create a transcript event with current timestamp."""
    return TranscriptEvent(
        source=source,
        text=text,
        language=language,
        confidence=confidence,
        timestamp=time.time()
    )

def create_status_event(message: str, level: Level = "info", 
                       duration: Optional[float] = None) -> StatusEvent:
    """Create a status event with current timestamp."""
    return StatusEvent(
        message=message,
        level=level,
        duration=duration,
        timestamp=time.time()
    )

# Global event bus instance (singleton pattern)
_global_event_bus: Optional[EventBus] = None

def get_global_event_bus() -> EventBus:
    """Get the global event bus instance."""
    global _global_event_bus
    if _global_event_bus is None:
        _global_event_bus = EventBus()
    return _global_event_bus

def reset_global_event_bus() -> None:
    """Reset the global event bus (useful for testing)."""
    global _global_event_bus
    _global_event_bus = None