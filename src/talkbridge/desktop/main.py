#!/usr/bin/env python3
"""
TalkBridge Desktop - Main Application Entry Point (CustomTkinter)
================================================================

Main entry point for the CustomTkinter application

Author: TalkBridge Team
Date: 2025-09-03
Version: 2.0

Requirements:
- customtkinter
- tkinter
======================================================================
Functions:
- setup_application_logging: Configures the logging system for the desktop application.
- check_dependencies: Checks that critical dependencies are available.
- show_error_dialog: Shows a critical error dialog.
- main: Main function of the application.
======================================================================
"""

import sys
import os
import logging
import tkinter as tk
from pathlib import Path
from typing import Optional, Tuple
import customtkinter as ctk

# Import robust project root resolver early
from talkbridge.utils.project_root import get_project_root, get_logs_dir

# Early configuration of error suppression
project_root = get_project_root()

# Import logging protection early
from talkbridge.logging_config import get_logger, mark_logging_configured, ensure_error_logging

# Import and configure UI constants
from talkbridge.desktop.ui.ui_utils import configure_ui, icon, clean_text, strip_variation_selectors
from talkbridge.desktop.ui.theme import ComponentThemes, Dimensions, Typography, ColorPalette

# Configure UI early
configure_ui()

# Basic suppression setup (before heavy imports)
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '2'  # Suppress TF warnings
os.environ['GLOG_minloglevel'] = '2'      # Suppress MediaPipe warnings
os.environ['OPENCV_LOG_LEVEL'] = 'ERROR'  # Suppress OpenCV warnings
os.environ['PYGAME_HIDE_SUPPORT_PROMPT'] = '1'  # Suppress pygame prompt

# Advanced suppression if available
try:
    from talkbridge.utils.error_suppression import suppress_ml_warnings, configure_camera_fallback
    suppress_ml_warnings()
    configure_camera_fallback()
except ImportError:
    pass  # Fallback already configured above

# Apply unified theme (configuration done by ui_utils)
try:
    from talkbridge.desktop.ui.theme import get_customtkinter_theme
    theme_config = get_customtkinter_theme()
    # Note: CustomTkinter theme configuration is applied at widget level
except ImportError:
    pass  # Fallback to default theme

def setup_application_logging(log_level: int = logging.INFO) -> None:
    """
    Configures the comprehensive logging system for the desktop application.
    
    Features:
    - General application logs to desktop.log
    - Error-level logs to errors.log  
    - Console output for development
    - Proper formatting and error handling
    
    Args:
        log_level: The logging level to use for general logging
    """
    # Set up logging directory using robust resolver
    log_dir = get_logs_dir()
    log_dir.mkdir(parents=True, exist_ok=True)
    
    # Define log files
    desktop_log_file = log_dir / "desktop.log"
    errors_log_file = log_dir / "errors.log"
    
    # Clear any existing logging configuration to avoid conflicts
    for handler in logging.root.handlers[:]:
        logging.root.removeHandler(handler)
    
    # Create formatters
    detailed_formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    error_formatter = logging.Formatter(
        '%(asctime)s [%(levelname)s] %(name)s:%(lineno)d - %(message)s'
    )
    
    # Create handlers
    handlers = []
    
    # 1. Desktop log handler (all logs >= INFO)
    desktop_handler = logging.FileHandler(desktop_log_file, encoding='utf-8')
    desktop_handler.setLevel(log_level)
    desktop_handler.setFormatter(detailed_formatter)
    handlers.append(desktop_handler)
    
    # 2. Error log handler (only ERROR and CRITICAL)
    error_handler = logging.FileHandler(errors_log_file, encoding='utf-8')
    error_handler.setLevel(logging.ERROR)
    error_handler.setFormatter(error_formatter)
    handlers.append(error_handler)
    
    # 3. Console handler for development
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(log_level)
    console_handler.setFormatter(detailed_formatter)
    handlers.append(console_handler)
    
    # Configure root logger
    # logging.basicConfig(
    #     level=logging.INFO,
    #     format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    # )
    
    # Set specific logger levels
    logging.getLogger("talkbridge").setLevel(log_level)
    
    # Suppress noisy third-party loggers
    logging.getLogger("matplotlib").setLevel(logging.WARNING)
    logging.getLogger("PIL").setLevel(logging.WARNING)
    logging.getLogger("urllib3").setLevel(logging.WARNING)
    logging.getLogger("requests").setLevel(logging.WARNING)
    
    # Test logging configuration
    logger = logging.getLogger("talkbridge.desktop.main")
    logger.info("Desktop application logging configured")
    logger.info(f"Log files: desktop={desktop_log_file}, errors={errors_log_file}")
    
    # Test error logging (using debug level to avoid noise in error logs)
    try:
        # This will create a test entry to verify logging is working
        logger.debug("Logging configuration test - DEBUG level logging working")
    except Exception as e:
        logger.warning(f"Warning: Error logging test failed: {e}")
    
    # Mark logging as configured to prevent module overrides
    mark_logging_configured()
    
    # Ensure error logging is working
    ensure_error_logging()

def check_dependencies() -> Tuple[bool, str]:
    """
    Checks that critical dependencies are available.
    
    Returns:
        Tuple of (success, error_message)
    """
    missing_deps = []
    
    try:
        import customtkinter
    except ImportError:
        missing_deps.append("customtkinter")
    
    try:
        import tkinter
    except ImportError:
        missing_deps.append("tkinter")
    
    if missing_deps:
        error_msg = f"Missing required dependencies: {', '.join(missing_deps)}\n\n"
        error_msg += "Please install with:\n"
        if "customtkinter" in missing_deps:
            error_msg += "pip install customtkinter\n"
        return False, error_msg
    
    return True, ""

def show_error_dialog(title: str, message: str) -> None:
    """
    Shows a critical error dialog using tkinter.
    
    Args:
        title: Dialog title
        message: Error message
    """
    import tkinter.messagebox as msgbox
    
    root = tk.Tk()
    root.withdraw()  # Hide the main window
    
    msgbox.showerror(title, message)
    root.destroy()

def main() -> int:
    """
    Main function of the application.
    
    Returns:
        Exit code (0 for success, non-zero for error)
    """
    # Setup logging first
    setup_application_logging()
    logger = logging.getLogger("talkbridge.desktop.main")
    
    logger.info("Starting TalkBridge Desktop (CustomTkinter)")
    
    try:
        # Check dependencies
        success, error_msg = check_dependencies()
        if not success:
            logger.error(f"Dependency check failed: {error_msg}")
            show_error_dialog("Dependency Error", error_msg)
            return 1
        
        # Import application after dependency check
        from talkbridge.desktop.app.application import TalkBridgeApplication
        
        # Create and run application
        app = TalkBridgeApplication()
        exit_code = app.run()
        
        logger.info(f"Application finished with exit code: {exit_code}")
        return exit_code
        
    except Exception as e:
        error_msg = f"Critical error starting application: {str(e)}"
        logger.exception(error_msg)
        show_error_dialog("Critical Error", error_msg)
        return 1

if __name__ == "__main__":
    sys.exit(main())
