"""
Desktop Notification Adapter for CustomTkinter.

This module provides a CustomTkinter-compatible notification system that
integrates with the framework-agnostic notifier.
"""

import queue
import threading
import logging
import tkinter as tk
import customtkinter as ctk
from typing import Optional, Dict, Any
from datetime import datetime, timedelta

from talkbridge.ui.notifier import NotifierPort, Notification, Level

logger = logging.getLogger(__name__)


class ToastManager:
    """
    Manages toast notifications for CustomTkinter applications.
    
    Toasts are non-blocking, auto-dismissing notifications that appear
    at the top-right of the screen.
    """
    
    def __init__(self):
        self._active_toasts: Dict[str, 'Toast'] = {}
        self._toast_counter = 0
        
    def show(self, notification: Notification) -> None:
        """
        Show a toast notification.
        
        Args:
            notification: The notification to display
        """
        try:
            toast_id = f"toast_{self._toast_counter}"
            self._toast_counter += 1
            
            # Create and show toast
            toast = Toast(notification, toast_id, self._on_toast_closed)
            self._active_toasts[toast_id] = toast
            toast.show()
            
        except Exception as e:
            logger.error(f"Failed to show toast notification: {e}")
    
    def _on_toast_closed(self, toast_id: str) -> None:
        """Handle toast being closed."""
        if toast_id in self._active_toasts:
            del self._active_toasts[toast_id]
    
    def close_all(self) -> None:
        """Close all active toasts."""
        for toast in list(self._active_toasts.values()):
            toast.close()
        self._active_toasts.clear()


class Toast:
    """
    Individual toast notification window.
    """
    
    # Color mapping for notification levels
    LEVEL_COLORS = {
        Level.INFO: ("#3b82f6", "#ffffff"),      # Blue background, white text
        Level.SUCCESS: ("#10b981", "#ffffff"),   # Green background, white text
        Level.WARNING: ("#f59e0b", "#000000"),   # Orange background, black text
        Level.ERROR: ("#ef4444", "#ffffff"),     # Red background, white text
        Level.DEBUG: ("#6b7280", "#ffffff"),     # Gray background, white text
    }
    
    def __init__(self, notification: Notification, toast_id: str, on_close_callback):
        self.notification = notification
        self.toast_id = toast_id
        self.on_close_callback = on_close_callback
        self.window: Optional[ctk.CTkToplevel] = None
        self._close_timer: Optional[str] = None
        
    def show(self) -> None:
        """Display the toast notification."""
        try:
            # Create toplevel window
            self.window = ctk.CTkToplevel()
            self.window.title("")
            self.window.resizable(False, False)
            self.window.attributes("-topmost", True)
            
            # Remove window decorations
            self.window.overrideredirect(True)
            
            # Get colors for this notification level
            bg_color, text_color = self.LEVEL_COLORS.get(
                self.notification.level, 
                self.LEVEL_COLORS[Level.INFO]
            )
            
            # Configure window
            self.window.configure(fg_color=bg_color)
            
            # Create main frame
            main_frame = ctk.CTkFrame(
                self.window,
                fg_color=bg_color,
                corner_radius=8
            )
            main_frame.pack(fill="both", expand=True, padx=2, pady=2)
            
            # Create content frame
            content_frame = ctk.CTkFrame(
                main_frame,
                fg_color="transparent"
            )
            content_frame.pack(fill="both", expand=True, padx=12, pady=8)
            
            # Header with level and close button
            header_frame = ctk.CTkFrame(
                content_frame,
                fg_color="transparent"
            )
            header_frame.pack(fill="x", pady=(0, 4))
            
            # Level indicator
            level_text = self.notification.level.value.upper()
            if self.notification.context:
                level_text = f"{self.notification.context} - {level_text}"
                
            level_label = ctk.CTkLabel(
                header_frame,
                text=level_text,
                font=ctk.CTkFont(size=12, weight="bold"),
                text_color=text_color
            )
            level_label.pack(side="left")
            
            # Close button
            close_btn = ctk.CTkButton(
                header_frame,
                text="×",
                width=20,
                height=20,
                font=ctk.CTkFont(size=16, weight="bold"),
                fg_color="transparent",
                text_color=text_color,
                hover_color=("gray70", "gray30"),
                command=self.close
            )
            close_btn.pack(side="right")
            
            # Message
            message_label = ctk.CTkLabel(
                content_frame,
                text=self.notification.message,
                font=ctk.CTkFont(size=13),
                text_color=text_color,
                wraplength=300,
                justify="left"
            )
            message_label.pack(fill="x", pady=(0, 4))
            
            # Details (if provided)
            if self.notification.details:
                details_label = ctk.CTkLabel(
                    content_frame,
                    text=self.notification.details,
                    font=ctk.CTkFont(size=11),
                    text_color=text_color,
                    wraplength=300,
                    justify="left"
                )
                details_label.pack(fill="x")
            
            # Position the toast
            self._position_toast()
            
            # Auto-dismiss after delay
            dismiss_delay = self._get_dismiss_delay()
            self._close_timer = self.window.after(dismiss_delay, self.close)
            
            # Bind click to close
            self._bind_click_to_close(main_frame)
            
        except Exception as e:
            logger.error(f"Failed to create toast window: {e}")
            self.close()
    
    def _position_toast(self) -> None:
        """Position toast at top-right of screen."""
        if not self.window:
            return
            
        try:
            # Update window to get proper size
            self.window.update_idletasks()
            
            # Get screen dimensions
            screen_width = self.window.winfo_screenwidth()
            screen_height = self.window.winfo_screenheight()
            
            # Get window dimensions
            window_width = self.window.winfo_reqwidth()
            window_height = self.window.winfo_reqheight()
            
            # Position at top-right with margin
            margin = 20
            x = screen_width - window_width - margin
            y = margin
            
            # Adjust for multiple toasts (simple stacking)
            toast_offset = len([t for t in ToastManager()._active_toasts.values() 
                              if t.window and t.window.winfo_exists()]) * (window_height + 10)
            y += toast_offset
            
            self.window.geometry(f"{window_width}x{window_height}+{x}+{y}")
            
        except Exception as e:
            logger.error(f"Failed to position toast: {e}")
    
    def _get_dismiss_delay(self) -> int:
        """Get auto-dismiss delay based on notification level."""
        delays = {
            Level.DEBUG: 2000,    # 2 seconds
            Level.INFO: 3000,     # 3 seconds
            Level.SUCCESS: 3000,  # 3 seconds
            Level.WARNING: 5000,  # 5 seconds
            Level.ERROR: 7000,    # 7 seconds
        }
        return delays.get(self.notification.level, 3000)
    
    def _bind_click_to_close(self, widget) -> None:
        """Bind click events to close the toast."""
        try:
            widget.bind("<Button-1>", lambda e: self.close())
            # Recursively bind to all children
            for child in widget.winfo_children():
                if hasattr(child, 'bind'):
                    self._bind_click_to_close(child)
        except Exception:
            pass  # Ignore binding errors
    
    def close(self) -> None:
        """Close the toast notification."""
        try:
            if self._close_timer:
                if self.window and self.window.winfo_exists():
                    self.window.after_cancel(self._close_timer)
                self._close_timer = None
            
            if self.window and self.window.winfo_exists():
                self.window.destroy()
                self.window = None
            
            # Notify manager
            if self.on_close_callback:
                self.on_close_callback(self.toast_id)
                
        except Exception as e:
            logger.error(f"Error closing toast: {e}")


class DesktopNotifier(NotifierPort):
    """
    Desktop notification adapter for CustomTkinter applications.
    
    This class implements the NotifierPort protocol and provides
    thread-safe notification handling for desktop applications.
    """
    
    def __init__(self, root_window: tk.Tk):
        """
        Initialize the desktop notifier.
        
        Args:
            root_window: The main tkinter window
        """
        self.root = root_window
        self.notification_queue = queue.Queue()
        self.toast_manager = ToastManager()
        self._pump_running = False
        
    def push(self, note: Notification) -> None:
        """
        Handle a notification by queuing it for UI thread processing.
        
        Args:
            note: The notification to handle
        """
        try:
            self.notification_queue.put_nowait(note)
        except queue.Full:
            logger.warning("Notification queue is full, dropping notification")
    
    def start_pump(self) -> None:
        """Start the notification pump in the UI thread."""
        if not self._pump_running:
            self._pump_running = True
            self._pump_notifications()
    
    def stop_pump(self) -> None:
        """Stop the notification pump."""
        self._pump_running = False
        self.toast_manager.close_all()
    
    def _pump_notifications(self) -> None:
        """Process queued notifications in the UI thread."""
        if not self._pump_running:
            return
            
        try:
            # Process all queued notifications
            while True:
                try:
                    note = self.notification_queue.get_nowait()
                    self.toast_manager.show(note)
                except queue.Empty:
                    break
                except Exception as e:
                    logger.error(f"Error processing notification: {e}")
            
            # Schedule next pump
            if self._pump_running and self.root and self.root.winfo_exists():
                self.root.after(100, self._pump_notifications)
                
        except Exception as e:
            logger.error(f"Error in notification pump: {e}")
    
    def show_notification_directly(self, level: Level, message: str, 
                                 details: str = None, context: str = None) -> None:
        """
        Show a notification directly (for testing or immediate display).
        
        Args:
            level: Notification level
            message: Notification message
            details: Optional details
            context: Optional context
        """
        notification = Notification(level, message, details, context)
        self.toast_manager.show(notification)


# Global toast manager instance (singleton pattern)
_global_toast_manager: Optional[ToastManager] = None


def get_toast_manager() -> ToastManager:
    """Get the global toast manager instance."""
    global _global_toast_manager
    if _global_toast_manager is None:
        _global_toast_manager = ToastManager()
    return _global_toast_manager