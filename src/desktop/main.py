#!/usr/bin/env python3
"""
TalkBridge Desktop - Main Application Entry Point
=================================================

Punto de entrada principal de la aplicación

Author: TalkBridge Team
Date: 2025-08-19
Version: 1.0

Requirements:
- PyQt6
======================================================================
Functions:
- setup_application_settings: Configure global Qt application settings.
- setup_application_logging: Configures the logging system for the desktop application.
- check_dependencies: Checks that critical dependencies are available.
- show_error_dialog: Shows a critical error dialog.
- main: Main function of the application.
======================================================================
"""

import sys
import os
import logging
from pathlib import Path
from typing import Optional

# Add the project root directory to the path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from PyQt6.QtWidgets import QApplication, QMessageBox
from PyQt6.QtCore import QSettings, Qt
from PyQt6.QtGui import QIcon

from src.desktop.app.application import TalkBridgeApplication


def setup_application_settings() -> QSettings:
    """
    Configure global Qt application settings.
    
    Returns:
        QSettings: Application configuration
    """
    QApplication.setOrganizationName("TalkBridge")
    QApplication.setOrganizationDomain("talkbridge.com")
    QApplication.setApplicationName("TalkBridge Desktop")
    QApplication.setApplicationVersion("1.0.0")
    
    return QSettings()


def setup_application_logging() -> None:
    """Configures the logging system for the desktop application."""
    log_dir = project_root / "data" / "logs"
    log_dir.mkdir(parents=True, exist_ok=True)
    
    # Basic logging configuration
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler(log_dir / "desktop.log"),
            logging.StreamHandler()
        ]
    )


def check_dependencies() -> bool:
    """
    Checks that critical dependencies are available.
    
    Returns:
        bool: True if at least PyQt6 is available (minimal mode)
    """
    try:
        # Check PyQt6 (critical dependency)
        from PyQt6.QtWidgets import QApplication
        logging.info("PyQt6 available")
        
        # Try to check core TalkBridge modules (optional)
        optional_modules = [
            'src.tts.synthesizer',
            'src.audio.capture', 
            'src.ui.auth.auth_manager',
            'src.translation.translator'
        ]
        
        available_count = 0
        for module in optional_modules:
            try:
                __import__(module)
                available_count += 1
                logging.info(f"Module {module} available")
            except ImportError:
                logging.warning(f"Module {module} not available (demo mode)")
        
        logging.info(f"Core modules available: {available_count}/{len(optional_modules)}")
        return True  # Always continue if PyQt6 is available
        
    except ImportError as e:
        logging.error(f"PyQt6 not available: {e}")
        return False


def show_error_dialog(title: str, message: str) -> None:
    """
    Shows a critical error dialog.
    
    Args:
        title: Dialog title
        message: Error message
    """
    app = QApplication.instance()
    if app is None:
        app = QApplication(sys.argv)
    
    msg_box = QMessageBox()
    msg_box.setIcon(QMessageBox.Icon.Critical)
    msg_box.setWindowTitle(title)
    msg_box.setText(message)
    msg_box.setStandardButtons(QMessageBox.StandardButton.Ok)
    msg_box.exec()


def main() -> int:
    """
    Main function of the application.
    
    Returns:
        int: Application exit code
    """
    try:
        # Early logging setup
        setup_application_logging()
        logger = logging.getLogger("talkbridge.desktop")
        logger.info("Starting TalkBridge Desktop Application...")
        
        # Check dependencies
        if not check_dependencies():
            show_error_dialog(
                "Dependency Error",
                "PyQt6 is not available.\n"
                "Please install PyQt6:\n"
                "pip install PyQt6"
            )
            return 1
        
        # Configure application settings
        settings = setup_application_settings()
        
        # Create and run the main application
        app = TalkBridgeApplication(sys.argv)
        
        # Set application icon if it exists
        icon_path = project_root / "src" / "desktop" / "resources" / "icon.ico"
        if icon_path.exists():
            app.setWindowIcon(QIcon(str(icon_path)))
        
        # Set global style if it exists
        styles_path = project_root / "src" / "desktop" / "resources" / "styles_simple.qss"
        if styles_path.exists():
            with open(styles_path, 'r', encoding='utf-8') as f:
                app.setStyleSheet(f.read())
        
        logger.info("Application configured successfully")
        
        # Run the application
        result = app.run()
        
        logger.info(f"Application finished with code: {result}")
        return result
        
    except Exception as e:
        error_msg = f"Critical error initializing the application: {str(e)}"
        logging.error(error_msg, exc_info=True)
        show_error_dialog("Critical Error", error_msg)
        return 1


if __name__ == "__main__":
    # Enable DPI scaling on Windows
    if hasattr(Qt, 'AA_EnableHighDpiScaling'):
        QApplication.setAttribute(Qt.ApplicationAttribute.AA_EnableHighDpiScaling, True)
    if hasattr(Qt, 'AA_UseHighDpiPixmaps'):
        QApplication.setAttribute(Qt.ApplicationAttribute.AA_UseHighDpiPixmaps, True)
    
    sys.exit(main())