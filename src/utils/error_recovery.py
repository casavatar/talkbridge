#!/usr/bin/env python3
"""
TalkBridge Utils - Error Recovery
================================

Centralized error recovery system for UI components and multimedia operations.
This module provides recovery strategies for camera, MediaPipe, UI components,
and other recoverable errors in desktop applications.

Author: TalkBridge Team
Date: 2025-09-26
Version: 1.0

Requirements:
- logging
- typing
- Optional: opencv-python, mediapipe

Responsibilities:
- UI Component Recovery: Handle None UI components and widget failures
- Camera Recovery: Robust camera initialization and fallback strategies
- MediaPipe Recovery: Handle MediaPipe initialization and attribute errors
- Animation Recovery: Manage animation state and UI update failures
- Resource Recovery: Clean up and reinitialize resources safely

Functions:
- recover_ui_component: Safe UI component operations with fallback
- recover_camera_capture: Camera initialization with multiple fallback strategies
- recover_mediapipe_init: MediaPipe initialization with graceful degradation
- recover_animation_state: Animation state recovery and UI synchronization
- recover_canvas_operations: Canvas drawing operations with error handling
- create_recovery_context: Create error recovery context manager
- register_recovery_handler: Register custom recovery handlers
- get_recovery_statistics: Get recovery operation statistics
======================================================================
"""

import logging
import traceback
import time
import os
from typing import Optional, Any, Callable, Dict, List, Tuple, Union, TypeVar, Generic
from functools import wraps
from datetime import datetime
from dataclasses import dataclass, field
from enum import Enum

# Import centralized logging
try:
    from ..logging_config import get_logger
except ImportError:
    # Fallback for standalone usage
    def get_logger(name: str) -> logging.Logger:
        return logging.getLogger(name)

logger = get_logger(__name__)

# Type definitions
T = TypeVar('T')
ComponentType = TypeVar('ComponentType')

class RecoveryLevel(Enum):
    """Recovery operation severity levels"""
    SILENT = "silent"        # No user notification
    INFO = "info"           # Informational recovery
    WARNING = "warning"     # Warning-level recovery
    ERROR = "error"         # Error-level recovery
    CRITICAL = "critical"   # Critical recovery required

class ComponentState(Enum):
    """UI Component states for recovery tracking"""
    UNKNOWN = "unknown"
    AVAILABLE = "available"
    UNAVAILABLE = "unavailable"
    RECOVERING = "recovering"
    FAILED = "failed"

@dataclass
class RecoveryResult:
    """Result of a recovery operation"""
    success: bool
    result: Any = None
    error: Optional[Exception] = None
    recovery_time: float = 0.0
    attempts: int = 0
    fallback_used: bool = False
    message: str = ""

@dataclass 
class RecoveryStats:
    """Statistics for recovery operations"""
    total_recoveries: int = 0
    successful_recoveries: int = 0
    failed_recoveries: int = 0
    average_recovery_time: float = 0.0
    recovery_by_type: Dict[str, int] = field(default_factory=dict)
    last_recovery: Optional[datetime] = None

class RecoveryManager:
    """Central manager for error recovery operations"""
    
    def __init__(self):
        self.stats = RecoveryStats()
        self.component_states: Dict[str, ComponentState] = {}
        self.recovery_handlers: Dict[str, Callable] = {}
        self.fallback_strategies: Dict[str, List[Callable]] = {}
        
    def register_handler(self, component_type: str, handler: Callable) -> None:
        """Register a recovery handler for a component type"""
        self.recovery_handlers[component_type] = handler
        logger.debug(f"Registered recovery handler for {component_type}")
    
    def add_fallback_strategy(self, component_type: str, strategy: Callable) -> None:
        """Add a fallback strategy for a component type"""
        if component_type not in self.fallback_strategies:
            self.fallback_strategies[component_type] = []
        self.fallback_strategies[component_type].append(strategy)
        logger.debug(f"Added fallback strategy for {component_type}")
    
    def update_component_state(self, component_id: str, state: ComponentState) -> None:
        """Update the state of a tracked component"""
        old_state = self.component_states.get(component_id, ComponentState.UNKNOWN)
        self.component_states[component_id] = state
        if old_state != state:
            logger.debug(f"Component {component_id} state: {old_state.value} -> {state.value}")
    
    def get_recovery_statistics(self) -> RecoveryStats:
        """Get current recovery statistics"""
        return self.stats
    
    def _record_recovery(self, recovery_type: str, success: bool, recovery_time: float) -> None:
        """Record recovery operation statistics"""
        self.stats.total_recoveries += 1
        self.stats.last_recovery = datetime.now()
        
        if success:
            self.stats.successful_recoveries += 1
        else:
            self.stats.failed_recoveries += 1
        
        # Update average recovery time
        total_time = self.stats.average_recovery_time * (self.stats.total_recoveries - 1)
        self.stats.average_recovery_time = (total_time + recovery_time) / self.stats.total_recoveries
        
        # Track by type
        if recovery_type not in self.stats.recovery_by_type:
            self.stats.recovery_by_type[recovery_type] = 0
        self.stats.recovery_by_type[recovery_type] += 1

# Global recovery manager instance
recovery_manager = RecoveryManager()

def recovery_wrapper(
    recovery_type: str,
    level: RecoveryLevel = RecoveryLevel.WARNING,
    max_attempts: int = 3,
    backoff_factor: float = 1.0,
    fallback_result: Any = None
) -> Callable:
    """
    Decorator for automatic error recovery with configurable strategies
    
    Args:
        recovery_type: Type of recovery for statistics tracking
        level: Recovery level for logging and notification
        max_attempts: Maximum recovery attempts
        backoff_factor: Exponential backoff factor between attempts
        fallback_result: Result to return if all recovery attempts fail
    """
    def decorator(func: Callable[..., T]) -> Callable[..., T]:
        @wraps(func)
        def wrapper(*args, **kwargs) -> T:
            start_time = time.time()
            last_exception = None
            
            for attempt in range(max_attempts):
                try:
                    recovery_manager.update_component_state(recovery_type, ComponentState.RECOVERING)
                    result = func(*args, **kwargs)
                    recovery_manager.update_component_state(recovery_type, ComponentState.AVAILABLE)
                    
                    if attempt > 0:  # Recovery was needed
                        recovery_time = time.time() - start_time
                        recovery_manager._record_recovery(recovery_type, True, recovery_time)
                        logger.info(f"Recovery successful for {recovery_type} after {attempt + 1} attempts")
                    
                    return result
                    
                except Exception as e:
                    last_exception = e
                    recovery_manager.update_component_state(recovery_type, ComponentState.FAILED)
                    
                    if attempt < max_attempts - 1:
                        wait_time = backoff_factor * (2 ** attempt)
                        logger.warning(f"Recovery attempt {attempt + 1} failed for {recovery_type}: {e}")
                        logger.debug(f"Retrying in {wait_time:.2f} seconds...")
                        time.sleep(wait_time)
                    else:
                        recovery_time = time.time() - start_time
                        recovery_manager._record_recovery(recovery_type, False, recovery_time)
                        logger.error(f"All recovery attempts failed for {recovery_type}: {e}")
            
            # Try fallback strategies
            if recovery_type in recovery_manager.fallback_strategies:
                for strategy in recovery_manager.fallback_strategies[recovery_type]:
                    try:
                        logger.info(f"Attempting fallback strategy for {recovery_type}")
                        result = strategy(*args, **kwargs)
                        recovery_manager.update_component_state(recovery_type, ComponentState.AVAILABLE)
                        recovery_time = time.time() - start_time
                        recovery_manager._record_recovery(recovery_type, True, recovery_time)
                        return result
                    except Exception as fallback_error:
                        logger.warning(f"Fallback strategy failed for {recovery_type}: {fallback_error}")
            
            # Final fallback
            recovery_manager.update_component_state(recovery_type, ComponentState.UNAVAILABLE)
            if level in [RecoveryLevel.CRITICAL, RecoveryLevel.ERROR] and last_exception:
                raise last_exception
            
            logger.warning(f"Using fallback result for {recovery_type}")
            return fallback_result
            
        return wrapper
    return decorator

# UI Component Recovery Functions

def safe_ui_operation(
    component: Any,
    operation: str,
    *args,
    component_name: str = "UI Component",
    **kwargs
) -> RecoveryResult:
    """
    Safely perform UI operations with None checks and error recovery
    
    Args:
        component: UI component to operate on
        operation: Method name to call on the component
        *args: Arguments for the operation
        component_name: Human-readable component name for logging
        **kwargs: Keyword arguments for the operation
    
    Returns:
        RecoveryResult with operation outcome
    """
    start_time = time.time()
    
    try:
        # Check if component exists
        if component is None:
            return RecoveryResult(
                success=False,
                error=ValueError(f"{component_name} is None"),
                recovery_time=time.time() - start_time,
                message=f"{component_name} not available"
            )
        
        # Check if component has the requested operation
        if not hasattr(component, operation):
            return RecoveryResult(
                success=False,
                error=AttributeError(f"{component_name} has no attribute '{operation}'"),
                recovery_time=time.time() - start_time,
                message=f"Operation '{operation}' not available on {component_name}"
            )
        
        # Perform the operation
        method = getattr(component, operation)
        result = method(*args, **kwargs)
        
        return RecoveryResult(
            success=True,
            result=result,
            recovery_time=time.time() - start_time,
            message=f"Operation '{operation}' successful on {component_name}"
        )
        
    except Exception as e:
        logger.warning(f"UI operation failed: {component_name}.{operation}({args}, {kwargs}): {e}")
        return RecoveryResult(
            success=False,
            error=e,
            recovery_time=time.time() - start_time,
            message=f"Operation '{operation}' failed on {component_name}: {str(e)}"
        )

def recover_canvas_operations(canvas: Any, operations: List[Tuple[str, tuple, dict]]) -> List[RecoveryResult]:
    """
    Perform multiple canvas operations with recovery for each
    
    Args:
        canvas: Canvas widget
        operations: List of (method_name, args, kwargs) tuples
    
    Returns:
        List of RecoveryResult for each operation
    """
    if canvas is None:
        logger.warning("Canvas is None, skipping all operations")
        return [RecoveryResult(success=False, error=ValueError("Canvas is None"), message="Canvas not available")]
    
    results = []
    for method_name, args, kwargs in operations:
        result = safe_ui_operation(canvas, method_name, *args, component_name="Canvas", **kwargs)
        results.append(result)
        
        # If a critical operation fails, stop the sequence
        if not result.success and method_name in ['create_image', 'create_text']:
            logger.warning(f"Critical canvas operation '{method_name}' failed, stopping sequence")
            break
    
    return results

# Camera Recovery Functions

@recovery_wrapper("camera_capture", RecoveryLevel.ERROR, max_attempts=3)
def recover_camera_capture(camera_index: int = 0, **camera_props) -> Optional[Any]:
    """
    Initialize camera capture with recovery and fallback strategies
    
    Args:
        camera_index: Camera index to try
        **camera_props: Additional camera properties to set
    
    Returns:
        VideoCapture object or None if recovery failed
    """
    try:
        import cv2
    except ImportError:
        logger.error("OpenCV not available for camera recovery")
        raise ImportError("OpenCV required for camera operations")
    
    # Try to create VideoCapture
    cap = cv2.VideoCapture(camera_index)
    
    if not cap.isOpened():
        raise RuntimeError(f"Failed to open camera at index {camera_index}")
    
    # Test camera by reading a frame
    ret, frame = cap.read()
    if not ret or frame is None:
        cap.release()
        raise RuntimeError(f"Camera at index {camera_index} cannot capture frames")
    
    # Apply camera properties
    for prop, value in camera_props.items():
        if hasattr(cv2, prop):
            cap.set(getattr(cv2, prop), value)
    
    logger.info(f"Camera recovery successful for index {camera_index}")
    return cap

def register_camera_fallbacks():
    """Register fallback strategies for camera recovery"""
    
    def try_different_backends(camera_index: int = 0, **camera_props):
        """Try different camera backends"""
        import cv2
        backends = [cv2.CAP_DSHOW, cv2.CAP_V4L2, cv2.CAP_GSTREAMER]
        
        for backend in backends:
            try:
                cap = cv2.VideoCapture(camera_index, backend)
                if cap.isOpened():
                    ret, _ = cap.read()
                    if ret:
                        logger.info(f"Camera fallback successful with backend {backend}")
                        return cap
                cap.release()
            except Exception as e:
                logger.debug(f"Backend {backend} failed: {e}")
        
        raise RuntimeError("All camera backends failed")
    
    def try_different_indices(camera_index: int = 0, **camera_props):
        """Try different camera indices"""
        import cv2
        for idx in range(5):  # Try indices 0-4
            try:
                cap = cv2.VideoCapture(idx)
                if cap.isOpened():
                    ret, _ = cap.read()
                    if ret:
                        logger.info(f"Camera fallback successful with index {idx}")
                        return cap
                cap.release()
            except Exception as e:
                logger.debug(f"Camera index {idx} failed: {e}")
        
        raise RuntimeError("No working camera indices found")
    
    recovery_manager.add_fallback_strategy("camera_capture", try_different_backends)
    recovery_manager.add_fallback_strategy("camera_capture", try_different_indices)

# MediaPipe Recovery Functions

@recovery_wrapper("mediapipe_init", RecoveryLevel.WARNING, max_attempts=2)
def recover_mediapipe_component(component_path: str) -> Optional[Any]:
    """
    Initialize MediaPipe components with safe attribute access
    
    Args:
        component_path: Dot-separated path to MediaPipe component (e.g., 'solutions.face_mesh')
    
    Returns:
        MediaPipe component or None if recovery failed
    """
    try:
        import mediapipe as mp
    except ImportError:
        logger.warning("MediaPipe not available")
        return None
    
    # Navigate the component path safely
    current = mp
    path_parts = component_path.split('.')
    
    for part in path_parts:
        if not hasattr(current, part):
            logger.warning(f"MediaPipe component path '{component_path}' not found at '{part}'")
            return None
        current = getattr(current, part)
    
    logger.debug(f"MediaPipe component '{component_path}' recovered successfully")
    return current

def safe_mediapipe_operation(mp_instance: Any, operation_path: str, *args, **kwargs) -> RecoveryResult:
    """
    Safely perform MediaPipe operations with attribute checking
    
    Args:
        mp_instance: MediaPipe instance
        operation_path: Dot-separated path to operation
        *args, **kwargs: Operation arguments
    
    Returns:
        RecoveryResult with operation outcome
    """
    if mp_instance is None:
        return RecoveryResult(
            success=False,
            error=ValueError("MediaPipe instance is None"),
            message="MediaPipe not available"
        )
    
    try:
        # Navigate to the operation
        current = mp_instance
        path_parts = operation_path.split('.')
        
        for part in path_parts[:-1]:
            if not hasattr(current, part):
                return RecoveryResult(
                    success=False,
                    error=AttributeError(f"MediaPipe path '{operation_path}' not found at '{part}'"),
                    message=f"MediaPipe operation path incomplete"
                )
            current = getattr(current, part)
        
        # Get the final operation
        operation_name = path_parts[-1]
        if not hasattr(current, operation_name):
            return RecoveryResult(
                success=False,
                error=AttributeError(f"MediaPipe operation '{operation_name}' not found"),
                message=f"MediaPipe operation not available"
            )
        
        operation = getattr(current, operation_name)
        
        # Execute the operation
        if callable(operation):
            result = operation(*args, **kwargs)
        else:
            result = operation
        
        return RecoveryResult(
            success=True,
            result=result,
            message=f"MediaPipe operation '{operation_path}' successful"
        )
        
    except Exception as e:
        return RecoveryResult(
            success=False,
            error=e,
            message=f"MediaPipe operation '{operation_path}' failed: {str(e)}"
        )

# Animation Recovery Functions

class AnimationStateManager:
    """Manages animation state with recovery capabilities"""
    
    def __init__(self):
        self.states: Dict[str, Dict[str, Any]] = {}
        self.callbacks: Dict[str, List[Callable]] = {}
    
    def save_state(self, animation_id: str, state: Dict[str, Any]) -> None:
        """Save animation state for recovery"""
        self.states[animation_id] = state.copy()
        logger.debug(f"Animation state saved for '{animation_id}'")
    
    def restore_state(self, animation_id: str) -> Optional[Dict[str, Any]]:
        """Restore animation state"""
        if animation_id in self.states:
            logger.debug(f"Animation state restored for '{animation_id}'")
            return self.states[animation_id].copy()
        return None
    
    def register_state_callback(self, animation_id: str, callback: Callable) -> None:
        """Register callback for state changes"""
        if animation_id not in self.callbacks:
            self.callbacks[animation_id] = []
        self.callbacks[animation_id].append(callback)
    
    def notify_state_change(self, animation_id: str, new_state: Dict[str, Any]) -> None:
        """Notify callbacks of state changes"""
        if animation_id in self.callbacks:
            for callback in self.callbacks[animation_id]:
                try:
                    callback(animation_id, new_state)
                except Exception as e:
                    logger.warning(f"Animation state callback failed: {e}")

animation_state_manager = AnimationStateManager()

@recovery_wrapper("animation_state", RecoveryLevel.INFO, max_attempts=2)
def recover_animation_state(animation_id: str, ui_components: Dict[str, Any]) -> RecoveryResult:
    """
    Recover animation state and synchronize UI components
    
    Args:
        animation_id: Unique animation identifier
        ui_components: Dictionary of UI components to update
    
    Returns:
        RecoveryResult with recovery outcome
    """
    start_time = time.time()
    
    try:
        # Restore saved state
        saved_state = animation_state_manager.restore_state(animation_id)
        if not saved_state:
            logger.info(f"No saved state found for animation '{animation_id}'")
            return RecoveryResult(
                success=True,
                message="No saved state to recover"
            )
        
        # Update UI components with saved state
        updated_components = []
        for component_name, component in ui_components.items():
            if component is None:
                continue
                
            # Update component based on saved state
            if component_name in saved_state:
                component_state = saved_state[component_name]
                for prop, value in component_state.items():
                    result = safe_ui_operation(component, prop, value, component_name=component_name)
                    if result.success:
                        updated_components.append(f"{component_name}.{prop}")
        
        return RecoveryResult(
            success=True,
            result=updated_components,
            recovery_time=time.time() - start_time,
            message=f"Animation state recovered for '{animation_id}': {len(updated_components)} components updated"
        )
        
    except Exception as e:
        return RecoveryResult(
            success=False,
            error=e,
            recovery_time=time.time() - start_time,
            message=f"Animation state recovery failed for '{animation_id}': {str(e)}"
        )

# Context Manager for Recovery Operations

class RecoveryContext:
    """Context manager for error recovery operations"""
    
    def __init__(
        self,
        operation_name: str,
        component_id: Optional[str] = None,
        level: RecoveryLevel = RecoveryLevel.WARNING,
        auto_recover: bool = True
    ):
        self.operation_name = operation_name
        self.component_id = component_id or operation_name
        self.level = level
        self.auto_recover = auto_recover
        self.start_time = None
        self.errors: List[Exception] = []
    
    def __enter__(self):
        self.start_time = time.time()
        recovery_manager.update_component_state(self.component_id, ComponentState.RECOVERING)
        logger.debug(f"Starting recovery context: {self.operation_name}")
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        recovery_time = time.time() - (self.start_time or time.time())
        
        if exc_type is None:
            # Success
            recovery_manager.update_component_state(self.component_id, ComponentState.AVAILABLE)
            if self.errors:  # Had errors but recovered
                recovery_manager._record_recovery(self.operation_name, True, recovery_time)
                logger.info(f"Recovery context completed successfully: {self.operation_name}")
        else:
            # Exception occurred
            recovery_manager.update_component_state(self.component_id, ComponentState.FAILED)
            recovery_manager._record_recovery(self.operation_name, False, recovery_time)
            
            if self.auto_recover and self.level not in [RecoveryLevel.CRITICAL]:
                logger.warning(f"Recovery context failed: {self.operation_name}: {exc_val}")
                return True  # Suppress exception
            else:
                logger.error(f"Critical failure in recovery context: {self.operation_name}: {exc_val}")
        
        return False
    
    def add_error(self, error: Exception) -> None:
        """Add a non-critical error to the context"""
        self.errors.append(error)
        logger.debug(f"Non-critical error added to recovery context: {error}")

# Utility Functions

def handle_user_facing_error(
    error: Exception,
    category: str = "general",
    context: Optional[str] = None,
    recovery_action: Optional[str] = None
) -> None:
    """
    Handle user-facing errors with recovery suggestions
    
    Args:
        error: Exception that occurred
        category: Error category for classification
        context: Additional context information
        recovery_action: Suggested recovery action for user
    """
    error_msg = f"Error in {category}: {str(error)}"
    if context:
        error_msg += f" (Context: {context})"
    
    logger.error(error_msg)
    
    # Update recovery statistics
    recovery_manager._record_recovery(f"user_facing_{category}", False, 0.0)
    
    # Log recovery suggestion
    if recovery_action:
        logger.info(f"Suggested recovery action: {recovery_action}")

def create_safe_fallback(fallback_value: Any = None, log_message: str = "Using fallback value"):
    """
    Create a safe fallback function that returns a default value
    
    Args:
        fallback_value: Value to return as fallback
        log_message: Message to log when fallback is used
    
    Returns:
        Function that returns the fallback value
    """
    def fallback_func(*args, **kwargs):
        logger.info(log_message)
        return fallback_value
    
    return fallback_func

def initialize_recovery_system():
    """Initialize the error recovery system with default configurations"""
    logger.info("Initializing error recovery system...")
    
    # Register default camera fallbacks
    register_camera_fallbacks()
    
    # Set up default component states
    default_components = [
        "camera_capture", "mediapipe_init", "animation_state", 
        "ui_components", "canvas_operations"
    ]
    
    for component in default_components:
        recovery_manager.update_component_state(component, ComponentState.UNKNOWN)
    
    logger.info("Error recovery system initialized successfully")

# Initialize on import
initialize_recovery_system()

# Export public API
__all__ = [
    # Core classes
    'RecoveryManager', 'RecoveryResult', 'RecoveryStats', 'RecoveryLevel', 'ComponentState',
    'RecoveryContext', 'AnimationStateManager',
    
    # Decorators
    'recovery_wrapper',
    
    # UI Recovery
    'safe_ui_operation', 'recover_canvas_operations',
    
    # Camera Recovery  
    'recover_camera_capture', 'register_camera_fallbacks',
    
    # MediaPipe Recovery
    'recover_mediapipe_component', 'safe_mediapipe_operation',
    
    # Animation Recovery
    'recover_animation_state', 'animation_state_manager',
    
    # Utilities
    'handle_user_facing_error', 'create_safe_fallback',
    
    # Global instances
    'recovery_manager'
]