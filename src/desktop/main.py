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

# Early configuration of error suppression
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

# Basic suppression setup (before heavy imports)
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '2'  # Suppress TF warnings
os.environ['GLOG_minloglevel'] = '2'      # Suppress MediaPipe warnings
os.environ['OPENCV_LOG_LEVEL'] = 'ERROR'  # Suppress OpenCV warnings
os.environ['PYGAME_HIDE_SUPPORT_PROMPT'] = '1'  # Suppress pygame prompt

# Advanced suppression if available
try:
    from src.utils.error_suppression import suppress_ml_warnings, configure_camera_fallback
    suppress_ml_warnings()
    configure_camera_fallback()
except ImportError:
    pass  # Fallback already configured above

# Set CustomTkinter appearance
ctk.set_appearance_mode("dark")  # Modes: "System" (standard), "Dark", "Light"
ctk.set_default_color_theme("blue")  # Themes: "blue" (standard), "green", "dark-blue"


def setup_application_logging(log_level: int = logging.INFO) -> None:
    """
    Configures the logging system for the desktop application.
    
    Args:
        log_level: The logging level to use
    """
    # Set up logging
    log_dir = project_root / "data" / "logs"
    log_dir.mkdir(parents=True, exist_ok=True)
    
    log_file = log_dir / "desktop_ctk.log"
    
    # Configure logging
    logging.basicConfig(
        level=log_level,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler(log_file),
            logging.StreamHandler(sys.stdout)
        ]
    )
    
    # Set specific loggers
    logging.getLogger("talkbridge").setLevel(log_level)
    
    # Suppress noisy loggers
    logging.getLogger("matplotlib").setLevel(logging.WARNING)
    logging.getLogger("PIL").setLevel(logging.WARNING)
    
    logger = logging.getLogger("talkbridge.desktop.main")
    logger.info("Desktop application logging configured")


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
        from src.desktop.app.application import TalkBridgeApplication
        
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
