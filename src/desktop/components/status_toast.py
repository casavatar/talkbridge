#!/usr/bin/env python3
"""
TalkBridge Desktop - Status Toast Component
===========================================

Transient notification component for displaying status messages, warnings, and errors.
Features auto-dismiss, different severity levels, and non-intrusive overlay display.

Author: TalkBridge Team
Date: 2025-09-18
Version: 1.0
"""

import logging
import time
from typing import Optional, Dict, List, Callable
from pathlib import Path
import customtkinter as ctk

from src.desktop.ui.events import EventBus, EventHandler, StatusEvent, Level
from src.desktop.ui.theme import (
    ColorPalette, Typography, Spacing, Dimensions
)

class ToastNotification:
    """Individual toast notification widget."""
    
    def __init__(self, parent: ctk.CTkFrame, message: str, level: Level = "info",
                 duration: Optional[float] = None, on_dismiss: Optional[Callable[['ToastNotification'], None]] = None):
        self.parent = parent
        self.message = message
        self.level = level
        self.duration = duration or self._get_default_duration(level)
        self.on_dismiss = on_dismiss
        self.timestamp = time.time()
        
        # Color scheme based on level
        self.colors = self._get_level_colors(level)
        
        # UI components
        self.container = None
        self.dismiss_timer = None
        
        # Create the toast UI
        self.create_toast()
        
        # Schedule auto-dismiss
        if self.duration > 0:
            self.schedule_dismiss()
    
    def _get_default_duration(self, level: Level) -> float:
        """Get default duration based on message level."""
        durations = {
            "info": 3.0,
            "success": 2.0,
            "warning": 5.0,
            "error": 8.0
        }
        return durations.get(level, 3.0)
    
    def _get_level_colors(self, level: Level) -> Dict[str, str]:
        """Get color scheme for the message level."""
        color_schemes = {
            "info": {
                "bg": "#1e3a8a",
                "border": "#3b82f6",
                "text": "#ffffff",
                "icon": "ℹ️"
            },
            "success": {
                "bg": "#166534",
                "border": "#22c55e",
                "text": "#ffffff",
                "icon": "✅"
            },
            "warning": {
                "bg": "#92400e",
                "border": "#f59e0b",
                "text": "#ffffff",
                "icon": "⚠️"
            },
            "error": {
                "bg": "#991b1b",
                "border": "#ef4444",
                "text": "#ffffff",
                "icon": "❌"
            }
        }
        return color_schemes.get(level, color_schemes["info"])
    
    def create_toast(self) -> None:
        """Create the toast notification UI."""
        # Main container with animation
        self.container = ctk.CTkFrame(
            self.parent,
            fg_color=self.colors["bg"],
            border_color=self.colors["border"],
            border_width=2,
            corner_radius=8
        )
        self.container.pack(fill="x", padx=10, pady=2)
        
        # Content frame
        content_frame = ctk.CTkFrame(self.container, fg_color="transparent")
        content_frame.pack(fill="x", padx=10, pady=8)
        
        # Icon
        icon_label = ctk.CTkLabel(
            content_frame,
            text=self.colors["icon"],
            font=ctk.CTkFont(size=16),
            text_color=self.colors["text"],
            width=30
        )
        icon_label.pack(side="left", padx=(0, 8))
        
        # Message text
        message_label = ctk.CTkLabel(
            content_frame,
            text=self.message,
            font=(Typography.FONT_FAMILY_PRIMARY, Typography.FONT_SIZE_CAPTION),
            text_color=self.colors["text"],
            anchor="w"
        )
        message_label.pack(side="left", fill="x", expand=True)
        
        # Dismiss button
        dismiss_button = ctk.CTkButton(
            content_frame,
            text="×",
            width=25,
            height=25,
            font=ctk.CTkFont(size=14, weight="bold"),
            fg_color="transparent",
            text_color=self.colors["text"],
            hover_color=self.colors["border"],
            command=self.dismiss
        )
        dismiss_button.pack(side="right")
        
        # Timestamp (for debugging/development)
        if hasattr(logging, 'DEBUG') and logging.getLogger().level <= logging.DEBUG:
            timestamp_str = time.strftime("%H:%M:%S", time.localtime(self.timestamp))
            timestamp_label = ctk.CTkLabel(
                content_frame,
                text=timestamp_str,
                font=(Typography.FONT_FAMILY_PRIMARY, 10),
                text_color="#888888"
            )
            timestamp_label.pack(side="right", padx=(5, 0))
    
    def schedule_dismiss(self) -> None:
        """Schedule automatic dismissal."""
        if self.container:
            self.dismiss_timer = self.container.after(
                int(self.duration * 1000),
                self.dismiss
            )
    
    def dismiss(self) -> None:
        """Dismiss the toast notification."""
        # Cancel timer if still pending
        if self.dismiss_timer and self.container is not None:
            try:
                self.container.after_cancel(self.dismiss_timer)
            except Exception:
                # Timer may have already fired
                pass
        
        # Destroy UI
        if self.container:
            self.container.destroy()
        
        # Notify parent
        if self.on_dismiss:
            self.on_dismiss(self)

class StatusToast(EventHandler):
    """
    Status toast component for displaying transient notifications.
    
    Features:
    - Multiple severity levels (info, success, warning, error)
    - Auto-dismiss with configurable duration
    - Manual dismiss option
    - Non-intrusive overlay positioning
    - Queue management for multiple notifications
    """
    
    def __init__(self, parent: ctk.CTkFrame, event_bus: EventBus):
        """Initialize status toast component."""
        super().__init__(event_bus)
        self.parent = parent
        
        # Toast management
        self.active_toasts: List[ToastNotification] = []
        self.max_toasts = 5  # Maximum visible toasts
        
        # UI components
        self.toast_container = None
        self.setup_ui()
        
        # Subscribe to events
        self.subscribe_to_events()
    
    def setup_ui(self) -> None:
        """Setup the toast container UI."""
        # Create overlay container for toasts
        self.toast_container = ctk.CTkFrame(
            self.parent,
            fg_color="transparent"
        )
        # Position at top-right (will be packed later when first toast appears)
    
    def subscribe_to_events(self) -> None:
        """Subscribe to relevant events."""
        self.event_bus.subscribe("status", self.show_toast)
    
    def unsubscribe_from_events(self) -> None:
        """Unsubscribe from events."""
        self.event_bus.unsubscribe("status", self.show_toast)
    
    def show_toast(self, event: StatusEvent) -> None:
        """Show a toast notification from an event."""
        self.logger.debug(f"Showing toast: {event.level} - {event.message}")
        self.show(event.message, event.level, event.duration)
    
    def show(self, message: str, level: Level = "info", 
             duration: Optional[float] = None) -> None:
        """Show a toast notification."""
        # Ensure container is visible
        if self.toast_container is not None and not self.toast_container.winfo_viewable():
            self.toast_container.pack(side="top", fill="x", padx=10, pady=5)
        
        # Limit number of active toasts
        while len(self.active_toasts) >= self.max_toasts:
            oldest_toast = self.active_toasts[0]
            oldest_toast.dismiss()
        
        # Create new toast
        if self.toast_container is not None:
            toast = ToastNotification(
                self.toast_container,
                message=message,
                level=level,
                duration=duration,
                on_dismiss=self._on_toast_dismissed
            )
        else:
            self.logger.error("Cannot create toast: toast_container is None")
            return
        
        self.active_toasts.append(toast)
        self.logger.debug(f"Added toast (total: {len(self.active_toasts)})")
    
    def _on_toast_dismissed(self, toast: ToastNotification) -> None:
        """Handle toast dismissal."""
        if toast in self.active_toasts:
            self.active_toasts.remove(toast)
            self.logger.debug(f"Removed toast (remaining: {len(self.active_toasts)})")
        
        # Hide container if no toasts remain
        if not self.active_toasts and self.toast_container is not None:
            self.toast_container.pack_forget()
    
    def show_info(self, message: str, duration: Optional[float] = None) -> None:
        """Show an info toast."""
        self.show(message, "info", duration)
    
    def show_success(self, message: str, duration: Optional[float] = None) -> None:
        """Show a success toast."""
        self.show(message, "success", duration)
    
    def show_warning(self, message: str, duration: Optional[float] = None) -> None:
        """Show a warning toast."""
        self.show(message, "warning", duration)
    
    def show_error(self, message: str, duration: Optional[float] = None) -> None:
        """Show an error toast."""
        self.show(message, "error", duration)
    
    def clear_all(self) -> None:
        """Clear all active toasts."""
        self.logger.info("Clearing all toasts")
        
        # Dismiss all active toasts
        for toast in self.active_toasts[:]:  # Copy list to avoid modification during iteration
            toast.dismiss()
        
        # Clear the list
        self.active_toasts.clear()
        
        # Hide container
        if self.toast_container is not None:
            self.toast_container.pack_forget()
    
    def get_active_count(self) -> int:
        """Get number of active toasts."""
        return len(self.active_toasts)
    
    def has_error_toasts(self) -> bool:
        """Check if there are any active error toasts."""
        return any(toast.level == "error" for toast in self.active_toasts)
    
    def has_warning_toasts(self) -> bool:
        """Check if there are any active warning toasts."""
        return any(toast.level == "warning" for toast in self.active_toasts)
    
    def cleanup(self) -> None:
        """Clean up resources."""
        self.logger.info("Cleaning up status toast")
        self.unsubscribe_from_events()
        self.clear_all()

class ToastManager:
    """
    Singleton toast manager for global toast notifications.
    Provides static methods for easy toast creation throughout the application.
    """
    
    _instance: Optional['ToastManager'] = None
    _toast_component: Optional[StatusToast] = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance
    
    @classmethod
    def initialize(cls, parent: ctk.CTkFrame, event_bus: EventBus) -> None:
        """Initialize the global toast manager."""
        manager = cls()
        manager._toast_component = StatusToast(parent, event_bus)
    
    @classmethod
    def show_info(cls, message: str, duration: Optional[float] = None) -> None:
        """Show a global info toast."""
        if cls._instance and cls._instance._toast_component:
            cls._instance._toast_component.show_info(message, duration)
    
    @classmethod
    def show_success(cls, message: str, duration: Optional[float] = None) -> None:
        """Show a global success toast."""
        if cls._instance and cls._instance._toast_component:
            cls._instance._toast_component.show_success(message, duration)
    
    @classmethod
    def show_warning(cls, message: str, duration: Optional[float] = None) -> None:
        """Show a global warning toast."""
        if cls._instance and cls._instance._toast_component:
            cls._instance._toast_component.show_warning(message, duration)
    
    @classmethod
    def show_error(cls, message: str, duration: Optional[float] = None) -> None:
        """Show a global error toast."""
        if cls._instance and cls._instance._toast_component:
            cls._instance._toast_component.show_error(message, duration)
    
    @classmethod
    def clear_all(cls) -> None:
        """Clear all global toasts."""
        if cls._instance and cls._instance._toast_component:
            cls._instance._toast_component.clear_all()
    
    @classmethod
    def cleanup(cls) -> None:
        """Clean up global toast manager."""
        if cls._instance and cls._instance._toast_component:
            cls._instance._toast_component.cleanup()
        cls._instance = None