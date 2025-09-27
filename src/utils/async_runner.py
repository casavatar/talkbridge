"""
Non-blocking task execution utilities for TalkBridge.

This module provides ThreadPoolExecutor-based task execution with
safe cross-thread communication patterns for UI applications.
"""

import logging
import threading
import weakref
from concurrent.futures import ThreadPoolExecutor, Future, as_completed
from functools import wraps
from typing import Callable, Any, Optional, Dict, List
from dataclasses import dataclass, field
from datetime import datetime
import tkinter as tk

logger = logging.getLogger(__name__)


@dataclass
class TaskProgress:
    """Progress information for long-running tasks."""
    current: int = 0
    total: int = 100
    message: str = ""
    stage: str = ""
    timestamp: datetime = field(default_factory=datetime.now)
    
    @property
    def percentage(self) -> float:
        """Get progress as percentage."""
        if self.total <= 0:
            return 0.0
        return min(100.0, (self.current / self.total) * 100.0)


class ProgressReporter:
    """Thread-safe progress reporting for background tasks."""
    
    def __init__(self, total: int = 100, message: str = ""):
        self.total = total
        self.current = 0
        self.message = message
        self.stage = ""
        self._callbacks: List[Callable[[TaskProgress], None]] = []
        self._lock = threading.RLock()
    
    def on_progress(self, callback: Callable[[TaskProgress], None]) -> None:
        """Register a progress callback."""
        with self._lock:
            self._callbacks.append(callback)
    
    def update(self, current: Optional[int] = None, message: Optional[str] = None, stage: Optional[str] = None) -> None:
        """Update progress information."""
        with self._lock:
            if current is not None:
                self.current = current
            if message is not None:
                self.message = message
            if stage is not None:
                self.stage = stage
            
            progress = TaskProgress(
                current=self.current,
                total=self.total,
                message=self.message,
                stage=self.stage
            )
            
            # Notify callbacks
            for callback in self._callbacks[:]:  # Copy to avoid modification during iteration
                try:
                    callback(progress)
                except Exception as e:
                    logger.error(f"Error in progress callback: {e}")
    
    def increment(self, amount: int = 1, message: Optional[str] = None, stage: Optional[str] = None) -> None:
        """Increment progress by amount."""
        with self._lock:
            self.update(self.current + amount, message, stage)
    
    def set_total(self, total: int) -> None:
        """Update the total progress amount."""
        with self._lock:
            self.total = total


class TaskResult:
    """Container for task execution results."""
    
    def __init__(self, success: bool, result: Any = None, error: Optional[Exception] = None):
        self.success = success
        self.result = result
        self.error = error
        self.timestamp = datetime.now()


class AsyncTaskRunner:
    """
    Thread-safe task runner for UI applications.
    
    Provides non-blocking task execution with progress reporting
    and safe UI thread communication.
    """
    
    def __init__(self, max_workers: int = 4):
        """
        Initialize the task runner.
        
        Args:
            max_workers: Maximum number of concurrent tasks
        """
        self.executor = ThreadPoolExecutor(max_workers=max_workers)
        self._active_tasks: Dict[str, Future] = {}
        self._task_counter = 0
        self._lock = threading.RLock()
        self._ui_roots: List[weakref.ref] = []  # Weak references to UI roots
    
    def register_ui_root(self, root) -> None:
        """
        Register a UI root for thread-safe callbacks.
        
        Args:
            root: UI root (tkinter.Tk or similar) for scheduling callbacks
        """
        # Use weak reference to avoid memory leaks
        self._ui_roots.append(weakref.ref(root))
    
    def _get_active_ui_root(self):
        """Get an active UI root for scheduling callbacks."""
        for root_ref in self._ui_roots[:]:  # Copy to modify during iteration
            root = root_ref()
            if root is None:
                # Clean up dead references
                self._ui_roots.remove(root_ref)
            elif hasattr(root, 'winfo_exists') and root.winfo_exists():
                return root
        return None
    
    def run_task_async(
        self,
        task_func: Callable,
        *args,
        on_success: Optional[Callable[[Any], None]] = None,
        on_error: Optional[Callable[[Exception], None]] = None,
        on_complete: Optional[Callable[[TaskResult], None]] = None,
        on_progress: Optional[Callable[[TaskProgress], None]] = None,
        task_name: Optional[str] = None,
        notify_progress: bool = False,
        **kwargs
    ) -> str:
        """
        Run a task asynchronously with optional callbacks.
        
        Args:
            task_func: Function to execute in background thread
            *args: Arguments for task function
            on_success: Callback for successful completion (UI thread)
            on_error: Callback for errors (UI thread)
            on_complete: Callback for completion regardless of result (UI thread)
            on_progress: Callback for progress updates (UI thread)
            task_name: Optional name for the task
            notify_progress: Whether to send progress notifications
            **kwargs: Keyword arguments for task function
            
        Returns:
            Task ID for tracking
        """
        with self._lock:
            self._task_counter += 1
            task_id = task_name or f"task_{self._task_counter}"
        
        # Create progress reporter if needed
        progress_reporter = None
        if on_progress or notify_progress:
            progress_reporter = ProgressReporter()
            if on_progress:
                progress_reporter.on_progress(
                    lambda p: self._schedule_ui_callback(on_progress, p)
                )
            if notify_progress:
                progress_reporter.on_progress(self._send_progress_notification)
        
        # Wrap task function to handle progress and results
        def wrapped_task():
            try:
                # Pass progress reporter to task if it accepts it
                import inspect
                sig = inspect.signature(task_func)
                if 'progress' in sig.parameters:
                    kwargs['progress'] = progress_reporter
                
                result = task_func(*args, **kwargs)
                return TaskResult(True, result)
            except Exception as e:
                logger.exception(f"Task {task_id} failed: {e}")
                return TaskResult(False, error=e)
        
        # Submit task
        future = self.executor.submit(wrapped_task)
        
        # Store task reference
        with self._lock:
            self._active_tasks[task_id] = future
        
        # Add completion callback
        future.add_done_callback(
            lambda fut: self._handle_task_completion(
                task_id, fut, on_success, on_error, on_complete
            )
        )
        
        logger.debug(f"Started async task: {task_id}")
        return task_id
    
    def _handle_task_completion(
        self,
        task_id: str,
        future: Future,
        on_success: Optional[Callable] = None,
        on_error: Optional[Callable] = None,
        on_complete: Optional[Callable] = None
    ) -> None:
        """Handle task completion and schedule UI callbacks."""
        try:
            task_result = future.result()
            
            # Schedule UI callbacks
            if task_result.success and on_success:
                self._schedule_ui_callback(on_success, task_result.result)
            elif not task_result.success and on_error:
                self._schedule_ui_callback(on_error, task_result.error)
            
            if on_complete:
                self._schedule_ui_callback(on_complete, task_result)
            
        except Exception as e:
            logger.error(f"Error handling task completion for {task_id}: {e}")
            if on_error:
                self._schedule_ui_callback(on_error, e)
        finally:
            # Clean up task reference
            with self._lock:
                self._active_tasks.pop(task_id, None)
    
    def _schedule_ui_callback(self, callback: Callable, *args) -> None:
        """Schedule a callback to run in the UI thread."""
        if not callback:
            return
            
        ui_root = self._get_active_ui_root()
        if ui_root:
            try:
                ui_root.after(0, lambda: callback(*args))
            except Exception as e:
                logger.error(f"Failed to schedule UI callback: {e}")
        else:
            # No UI root available, run callback directly (non-UI context)
            try:
                callback(*args)
            except Exception as e:
                logger.error(f"Error in callback: {e}")
    
    def _send_progress_notification(self, progress: TaskProgress) -> None:
        """Send progress notification via notifier system."""
        try:
            from ..ui.notifier import notify_info
            
            percentage = progress.percentage
            message = f"{progress.message} ({percentage:.0f}%)"
            if progress.stage:
                message = f"{progress.stage}: {message}"
                
            notify_info(
                message,
                context="Task Progress",
                details=f"{progress.current}/{progress.total}"
            )
        except ImportError:
            logger.debug("Notifier not available for progress updates")
        except Exception as e:
            logger.error(f"Error sending progress notification: {e}")
    
    def cancel_task(self, task_id: str) -> bool:
        """
        Cancel a running task.
        
        Args:
            task_id: ID of task to cancel
            
        Returns:
            True if task was cancelled, False otherwise
        """
        with self._lock:
            future = self._active_tasks.get(task_id)
            if future:
                cancelled = future.cancel()
                if cancelled:
                    self._active_tasks.pop(task_id, None)
                    logger.debug(f"Cancelled task: {task_id}")
                return cancelled
        return False
    
    def is_task_running(self, task_id: str) -> bool:
        """Check if a task is currently running."""
        with self._lock:
            future = self._active_tasks.get(task_id)
            return future is not None and not future.done()
    
    def get_active_tasks(self) -> List[str]:
        """Get list of active task IDs."""
        with self._lock:
            return [tid for tid, future in self._active_tasks.items() if not future.done()]
    
    def wait_for_completion(self, timeout: Optional[float] = None) -> None:
        """
        Wait for all active tasks to complete.
        
        Args:
            timeout: Maximum time to wait in seconds
        """
        with self._lock:
            futures = list(self._active_tasks.values())
        
        if futures:
            logger.debug(f"Waiting for {len(futures)} tasks to complete")
            for future in as_completed(futures, timeout=timeout):
                try:
                    future.result()  # This will raise any exceptions
                except Exception as e:
                    logger.error(f"Task failed during shutdown: {e}")
    
    def shutdown(self, wait: bool = True) -> None:
        """
        Shutdown the task runner.
        
        Args:
            wait: Whether to wait for active tasks to complete
        """
        logger.debug("Shutting down async task runner")
        
        if wait:
            try:
                self.wait_for_completion(timeout=30.0)  # 30 second timeout
            except Exception as e:
                logger.warning(f"Timeout waiting for tasks during shutdown: {e}")
        
        self.executor.shutdown(wait=False)
        with self._lock:
            self._active_tasks.clear()


# Global task runner instance
_global_task_runner: Optional[AsyncTaskRunner] = None


def get_task_runner() -> AsyncTaskRunner:
    """Get the global task runner instance."""
    global _global_task_runner
    if _global_task_runner is None:
        _global_task_runner = AsyncTaskRunner()
    return _global_task_runner


def run_async(
    task_func: Callable,
    *args,
    on_success: Optional[Callable] = None,
    on_error: Optional[Callable] = None,
    on_progress: Optional[Callable] = None,
    task_name: Optional[str] = None,
    **kwargs
) -> str:
    """
    Convenience function to run a task asynchronously.
    
    Args:
        task_func: Function to execute
        *args: Arguments for function
        on_success: Success callback
        on_error: Error callback
        on_progress: Progress callback
        task_name: Optional task name
        **kwargs: Keyword arguments for function
        
    Returns:
        Task ID
    """
    return get_task_runner().run_task_async(
        task_func,
        *args,
        on_success=on_success,
        on_error=on_error,
        on_progress=on_progress,
        task_name=task_name,
        **kwargs
    )


def async_task(
    on_success: Optional[Callable] = None,
    on_error: Optional[Callable] = None,
    on_progress: Optional[Callable] = None,
    task_name: Optional[str] = None,
    notify_progress: bool = False
):
    """
    Decorator to make a function run asynchronously.
    
    Args:
        on_success: Success callback
        on_error: Error callback
        on_progress: Progress callback
        task_name: Task name
        notify_progress: Whether to send progress notifications
        
    Returns:
        Decorated function that returns task ID when called
    """
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            return get_task_runner().run_task_async(
                func,
                *args,
                on_success=on_success,
                on_error=on_error,
                on_progress=on_progress,
                task_name=task_name or func.__name__,
                notify_progress=notify_progress,
                **kwargs
            )
        return wrapper
    return decorator


def ui_thread_call(func: Callable, *args) -> None:
    """
    Schedule a function to run in the UI thread.
    
    Args:
        func: Function to call
        *args: Arguments for function
    """
    get_task_runner()._schedule_ui_callback(func, *args)


# Context manager for progress reporting
class ProgressContext:
    """Context manager for automatic progress reporting."""
    
    def __init__(self, total: int = 100, message: str = "", auto_increment: bool = True):
        self.progress = ProgressReporter(total, message)
        self.auto_increment = auto_increment
        self._steps = 0
    
    def __enter__(self) -> ProgressReporter:
        return self.progress
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        if self.auto_increment and exc_type is None:
            # Auto-complete on success
            self.progress.update(self.progress.total, "Completed")
        elif exc_type is not None:
            # Report error
            self.progress.update(message="Failed", stage="Error")
    
    def step(self, message: Optional[str] = None) -> None:
        """Advance to next step with auto-increment."""
        if self.auto_increment:
            self._steps += 1
            self.progress.update(self._steps, message)