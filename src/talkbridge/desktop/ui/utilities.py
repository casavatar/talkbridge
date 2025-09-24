"""
UI Threading Utilities for TalkBridge Desktop.

This module provides thread-safe utilities for executing UI operations in CustomTkinter
applications. It ensures that UI updates are always performed on the main thread to
avoid threading issues and crashes.
"""

import logging
import queue
import threading
import weakref
from typing import Any, Callable, Optional, Union

# Try to import customtkinter for UI operations
try:
    import customtkinter as ctk
    import tkinter as tk
    CUSTOMTKINTER_AVAILABLE = True
except ImportError:
    CUSTOMTKINTER_AVAILABLE = False
    ctk = None
    tk = None

logger = logging.getLogger(__name__)

# Global registry for UI roots (weak references to avoid memory leaks)
_ui_roots: list = []

def register_ui_root(root: Union["ctk.CTk", "tk.Tk"]) -> None:
    """
    Register a UI root for thread-safe callbacks.
    
    Args:
        root: UI root (CTk or Tk instance) for scheduling callbacks
    """
    global _ui_roots
    if root and hasattr(root, 'after'):
        # Use weak reference to avoid memory leaks
        _ui_roots.append(weakref.ref(root))
        logger.debug(f"Registered UI root: {type(root).__name__}")

def _get_active_ui_root() -> Optional[Union["ctk.CTk", "tk.Tk"]]:
    """Get an active UI root for scheduling callbacks."""
    global _ui_roots
    
    for root_ref in _ui_roots[:]:  # Copy to modify during iteration
        root = root_ref()
        if root is None:
            # Clean up dead references
            _ui_roots.remove(root_ref)
        elif hasattr(root, 'winfo_exists'):
            try:
                if root.winfo_exists():
                    return root
            except Exception:
                # Root might be destroyed, remove reference
                _ui_roots.remove(root_ref)
        else:
            # If we can't check existence, assume it's valid
            return root
    
    return None

def ui_thread_call(fn: Callable, *args, **kwargs) -> None:
    """
    Schedule a function to run safely in the UI thread.
    
    This function ensures that UI updates are always performed on the main thread,
    preventing threading-related crashes and ensuring proper UI behavior.
    
    Args:
        fn: Function to call in the UI thread
        *args: Positional arguments for the function
        **kwargs: Keyword arguments for the function
    
    Example:
        # Safe UI update from background thread
        def update_label():
            label.configure(text="Updated!")
        
        ui_thread_call(update_label)
        
        # With arguments
        ui_thread_call(label.configure, text="New text")
    """
    if not CUSTOMTKINTER_AVAILABLE:
        logger.warning("CustomTkinter not available, executing function directly")
        try:
            fn(*args, **kwargs)
        except Exception as e:
            logger.error(f"Error executing function directly: {e}")
        return
    
    # Check if we're already on the main thread
    if threading.current_thread() is threading.main_thread():
        try:
            fn(*args, **kwargs)
        except Exception as e:
            logger.error(f"Error executing function on main thread: {e}")
        return
    
    # We're on a background thread, need to schedule on UI thread
    ui_root = _get_active_ui_root()
    if ui_root:
        try:
            ui_root.after(0, lambda: _safe_execute(fn, *args, **kwargs))
            logger.debug(f"Scheduled function {fn.__name__} for UI thread execution")
        except Exception as e:
            logger.error(f"Failed to schedule UI callback: {e}")
    else:
        # No UI root available, try to execute directly as fallback
        logger.warning("No UI root available, executing function directly")
        try:
            fn(*args, **kwargs)
        except Exception as e:
            logger.error(f"Error executing function as fallback: {e}")

def _safe_execute(fn: Callable, *args, **kwargs) -> None:
    """Safely execute a function with error handling."""
    try:
        fn(*args, **kwargs)
    except Exception as e:
        logger.error(f"Error in UI thread callback {fn.__name__}: {e}")

def ui_safe_call(widget: Union["ctk.CTk", "tk.Tk", "ctk.CTkBaseClass", "tk.Widget"], func: Callable, *args, **kwargs) -> None:
    """
    Safely schedule a Tkinter call if the main loop is alive.
    
    This function ensures UI operations are always performed on the main thread
    by using the widget's .after() method to schedule the call, with robust
    error handling for destroyed widgets and inactive main loops.
    
    Args:
        widget: The Tkinter/CustomTkinter widget to use for scheduling
        func: Function to call safely on the main thread  
        *args: Positional arguments for the function
        **kwargs: Keyword arguments for the function
        
    Example:
        # Safe UI update from background thread
        ui_safe_call(dialog, dialog.destroy)
        ui_safe_call(label, label.configure, text="New text")
    """
    if not widget:
        logger.warning("ui_safe_call skipped: widget is None")
        return
        
    try:
        # Check if widget and root are valid before scheduling
        if hasattr(widget, 'winfo_exists'):
            try:
                if not widget.winfo_exists():
                    logger.warning("ui_safe_call skipped: widget no longer exists.")
                    return
            except RuntimeError:
                logger.warning("ui_safe_call skipped: widget already destroyed.")
                return
        
        # Get the root window to check main loop status
        try:
            if hasattr(widget, 'winfo_toplevel'):
                root = widget.winfo_toplevel()
                if not root or not root.winfo_exists():
                    logger.warning("ui_safe_call skipped: main loop not running.")
                    return
        except (RuntimeError, AttributeError):
            logger.warning("ui_safe_call skipped: cannot access main loop.")
            return
        
        # Check if we're already on the main thread
        if threading.current_thread() is threading.main_thread():
            # On main thread, execute directly after widget validation
            func(*args, **kwargs)
        else:
            # On background thread, schedule for main thread execution
            if hasattr(widget, 'after'):
                try:
                    widget.after(0, lambda: _safe_execute_on_widget(widget, func, *args, **kwargs))
                    logger.debug(f"Scheduled UI safe call for {func.__name__} on widget {type(widget).__name__}")
                except RuntimeError as e:
                    # Catch "main thread is not in main loop"
                    logger.error("ui_safe_call failed: %s", e)
                    # Emergency fallback: log instead of crashing
                    try:
                        func(*args, **kwargs)
                        logger.warning(f"Emergency fallback execution succeeded for {func.__name__}")
                    except Exception as inner:
                        logger.error("Fallback execution failed: %s", inner)
            else:
                logger.warning(f"Widget {type(widget).__name__} doesn't have .after() method")
    except Exception as e:
        logger.error(f"UI safe call failed for {func.__name__}: {e}", exc_info=True)

def _safe_execute_on_widget(widget: Union["ctk.CTk", "tk.Tk", "ctk.CTkBaseClass", "tk.Widget"], func: Callable, *args, **kwargs) -> None:
    """Safely execute a function on a widget with existence check."""
    try:
        # Ensure widget validity before executing
        if not widget:
            logger.warning("Cannot execute on None widget")
            return
            
        if hasattr(widget, 'winfo_exists'):
            try:
                if widget.winfo_exists():
                    func(*args, **kwargs)
                else:
                    logger.debug(f"Widget destroyed before execution of {func.__name__}")
            except RuntimeError as e:
                logger.warning(f"Widget destroyed during {func.__name__} check: {e}")
        else:
            # Widget doesn't have winfo_exists (might be CTk root), try directly
            func(*args, **kwargs)
    except Exception as e:
        logger.error(f"UI execution failed: {e}", exc_info=True)

def schedule_ui_update(
    interval_ms: int, 
    fn: Callable, 
    *args, 
    repeat: bool = True,
    root: Optional[Union["ctk.CTk", "tk.Tk"]] = None,
    **kwargs
) -> Optional[str]:
    """
    Schedule a periodic UI update.
    
    Args:
        interval_ms: Interval in milliseconds between updates
        fn: Function to call periodically
        *args: Positional arguments for the function
        repeat: If True, schedule recurring updates. If False, run only once.
        root: Specific UI root to use. If None, uses the first available root.
        **kwargs: Keyword arguments for the function
    
    Returns:
        Timer ID that can be used to cancel the update, or None if scheduling failed
    
    Example:
        # Update status every 2 seconds
        timer_id = schedule_ui_update(2000, update_status_label)
        
        # One-time delayed update
        schedule_ui_update(1000, show_message, "Hello!", repeat=False)
        
        # Cancel scheduled update (if you have the timer_id)
        # root.after_cancel(timer_id)
    """
    if not CUSTOMTKINTER_AVAILABLE:
        logger.warning("CustomTkinter not available, cannot schedule UI update")
        return None
    
    # Use provided root or get an active one
    ui_root = root or _get_active_ui_root()
    if not ui_root:
        logger.warning("No UI root available, cannot schedule UI update")
        return None
    
    def _wrapped():
        try:
            fn(*args, **kwargs)
            if repeat:
                # Schedule the next execution
                ui_root.after(interval_ms, _wrapped)
        except Exception as e:
            logger.error(f"Error in scheduled UI update {fn.__name__}: {e}")
    
    try:
        # Schedule the first execution
        timer_id = ui_root.after(interval_ms, _wrapped)
        logger.debug(f"Scheduled periodic UI update for {fn.__name__} every {interval_ms}ms")
        return timer_id
    except Exception as e:
        logger.error(f"Failed to schedule UI update: {e}")
        return None

def cancel_ui_update(timer_id: str, root: Optional[Union["ctk.CTk", "tk.Tk"]] = None) -> bool:
    """
    Cancel a scheduled UI update.
    
    Args:
        timer_id: Timer ID returned by schedule_ui_update
        root: UI root that scheduled the update. If None, tries all available roots.
    
    Returns:
        True if successfully cancelled, False otherwise
    """
    if not CUSTOMTKINTER_AVAILABLE or not timer_id:
        return False
    
    # Use provided root or get an active one
    ui_root = root or _get_active_ui_root()
    if not ui_root:
        logger.warning("No UI root available, cannot cancel UI update")
        return False
    
    try:
        ui_root.after_cancel(timer_id)
        logger.debug(f"Cancelled UI update timer {timer_id}")
        return True
    except Exception as e:
        logger.error(f"Failed to cancel UI update timer {timer_id}: {e}")
        return False

def is_ui_thread() -> bool:
    """
    Check if the current thread is the main UI thread.
    
    Returns:
        True if running on the main thread, False otherwise
    """
    return threading.current_thread() is threading.main_thread()

def get_ui_root_info() -> dict:
    """
    Get information about registered UI roots for debugging.
    
    Returns:
        Dictionary with UI root information
    """
    global _ui_roots
    active_roots = []
    dead_refs = 0
    
    for root_ref in _ui_roots[:]:
        root = root_ref()
        if root is None:
            dead_refs += 1
        else:
            try:
                exists = hasattr(root, 'winfo_exists') and root.winfo_exists()
                active_roots.append({
                    'type': type(root).__name__,
                    'exists': exists,
                    'id': id(root)
                })
            except Exception:
                dead_refs += 1
    
    return {
        'total_registered': len(_ui_roots),
        'active_roots': active_roots,
        'dead_references': dead_refs,
        'customtkinter_available': CUSTOMTKINTER_AVAILABLE,
        'current_thread_is_main': is_ui_thread()
    }

# Export the main utility functions
__all__ = [
    "ui_thread_call",
    "schedule_ui_update",
    "cancel_ui_update",
    "register_ui_root",
    "is_ui_thread",
    "get_ui_root_info",
    "CUSTOMTKINTER_AVAILABLE"
]