#!/usr/bin/env python3
"""
TalkBridge Desktop - Main Application Entry Point
=================================================

Main entry point for the application

Author: TalkBridge Team
Date: 2025-08-19
Version: 1.0

Requirements:
- PySide6
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
from typing import Optional, Tuple

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

from PySide6.QtWidgets import QApplication, QMessageBox
from PySide6.QtCore import QSettings, Qt
from PySide6.QtGui import QIcon

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
    
    # Clear any existing handlers to avoid conflicts
    root_logger = logging.getLogger()
    for handler in root_logger.handlers[:]:
        root_logger.removeHandler(handler)
    
    # Configure logging with force=True to override previous configurations
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler(log_dir / "desktop.log"),
            logging.FileHandler(log_dir / "app.log"),  # General application log
            logging.StreamHandler()
        ],
        force=True  # Force reconfiguration
    )
    
    # Also configure error logging to write to errors.log
    error_handler = logging.FileHandler(log_dir / "errors.log")
    error_handler.setLevel(logging.ERROR)
    error_handler.setFormatter(logging.Formatter('%(asctime)s [%(levelname)s] %(message)s'))
    logging.getLogger().addHandler(error_handler)


def check_dependencies() -> Tuple[bool, bool]:
    """
    Checks that critical dependencies are available and provides detailed feedback.
    
    Returns:
        Tuple[bool, bool]: (core_deps_available, has_missing_optional)
    """
    try:
        # Check PySide6 (critical dependency)
        from PySide6.QtWidgets import QApplication
        logging.info("✓ PySide6 available")
        
        # Define required dependencies with installation instructions
        dependencies = {
            'src.tts.synthesizer': {
                'name': 'TTS Synthesizer',
                'install': 'pip install TTS>=0.22.0',
                'description': 'Text-to-Speech synthesis capabilities',
                'optional': True
            },
            'src.audio.capture': {
                'name': 'Audio Capture',
                'install': 'included in project',
                'description': 'Audio recording and processing',
                'optional': False
            },
            'src.auth.auth_manager': {
                'name': 'Authentication Manager',
                'install': 'included in project',
                'description': 'User authentication system',
                'optional': False
            },
            'src.translation.translator': {
                'name': 'Translation Engine',
                'install': 'included in project',
                'description': 'Text translation capabilities',
                'optional': False
            }
        }
        
        # Additional optional dependencies
        optional_deps = {
            'argostranslate': {
                'name': 'Argos Translate',
                'install': 'pip install argos-translate>=1.9.0',
                'description': 'Offline translation support'
            },
            'mediapipe': {
                'name': 'MediaPipe',
                'install': 'pip install mediapipe>=0.10.0',
                'description': 'Face animation and detection'
            },
            'TTS': {
                'name': 'Coqui TTS',
                'install': 'pip install TTS>=0.22.0',
                'description': 'Advanced text-to-speech synthesis'
            }
        }
        
        available_count = 0
        missing_core = []
        missing_optional = []
        
        # Check core TalkBridge modules
        for module_name, info in dependencies.items():
            try:
                __import__(module_name)
                available_count += 1
                logging.info(f"✓ {info['name']} available")
            except ImportError:
                if info['optional']:
                    missing_optional.append((module_name, info))
                    logging.warning(f"⚠ {info['name']} not available (optional)")
                else:
                    missing_core.append((module_name, info))
                    logging.warning(f"✗ {info['name']} not available (REQUIRED)")
        
        # Check additional optional dependencies
        for dep_name, info in optional_deps.items():
            try:
                __import__(dep_name)
                logging.info(f"✓ {info['name']} available")
            except ImportError:
                missing_optional.append((dep_name, info))
                logging.warning(f"⚠ {info['name']} not available (optional)")
        
        # Summary
        total_core = len([d for d in dependencies.values() if not d['optional']])
        core_available = len([d for d in dependencies.values() if not d['optional']]) - len(missing_core)
        
        logging.info(f"Dependencies Status: {core_available}/{total_core} core modules, "
                    f"{available_count}/{len(dependencies)} total TalkBridge modules")
        
        # Display missing dependencies information
        if missing_core:
            logging.error("Missing REQUIRED dependencies:")
            for module_name, info in missing_core:
                logging.error(f"  - {info['name']}: {info['description']}")
                logging.error(f"    Install: {info['install']}")
        
        if missing_optional:
            logging.info("Missing OPTIONAL dependencies (reduced functionality):")
            for module_name, info in missing_optional:
                logging.info(f"  - {info['name']}: {info['description']}")
                logging.info(f"    Install: {info['install']}")
        
        # Return status
        core_deps_ok = len(missing_core) == 0
        has_missing_optional = len(missing_optional) > 0
        
        return core_deps_ok, has_missing_optional
        
    except ImportError as e:
        logging.error(f"✗ PySide6 not available: {e}")
        logging.error("Install with: pip install PySide6")
        return False, False


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


def show_dependency_warning() -> None:
    """
    Shows a user-friendly warning about missing optional dependencies.
    """
    try:
        from PySide6.QtWidgets import QMessageBox
        
        app = QApplication.instance()
        if app is None:
            return
        
        message = """
TalkBridge is running in limited mode due to missing optional dependencies.

Some features may not be available:
• Advanced text-to-speech (TTS)
• Offline translation (argos-translate)  
• Face animation (MediaPipe)

To enable all features, install missing dependencies:
pip install TTS>=0.22.0 argos-translate>=1.9.0 mediapipe>=0.10.0

Note: Some dependencies require Python ≤3.11. 
Consider using a Python 3.11 environment for full functionality.
        """.strip()
        
        msg_box = QMessageBox()
        msg_box.setIcon(QMessageBox.Icon.Warning)
        msg_box.setWindowTitle("TalkBridge - Limited Mode")
        msg_box.setText(message)
        msg_box.setStandardButtons(QMessageBox.StandardButton.Ok)
        msg_box.exec()
        
    except ImportError:
        # Fallback to console warning if QMessageBox not available
        print("Warning: TalkBridge running in limited mode due to missing dependencies")
        print("Install missing dependencies for full functionality")


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
        core_deps_ok, has_missing_optional = check_dependencies()
        if not core_deps_ok:
            show_error_dialog(
                "Dependency Error",
                "Critical dependencies are missing.\n"
                "Please check the console output for details."
            )
            return 1
        
        logger.info("Dependencies check completed")
        
        # Configure thread cleanup for robust shutdown
        try:
            from src.utils.error_suppression import setup_qt_thread_cleanup
            active_threads = setup_qt_thread_cleanup()
            logger.info("Qt thread cleanup configured")
        except ImportError:
            logger.warning("Thread cleanup utilities not available")
            active_threads = []
        
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
        
        # Show dependency warning to user if needed (only if there are missing optional deps)
        if has_missing_optional:
            show_dependency_warning()
        
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
    # Enable DPI scaling on Windows (modern approach for Qt 6+)
    # Note: AA_EnableHighDpiScaling and AA_UseHighDpiPixmaps are deprecated in Qt 6
    # High DPI scaling is enabled by default in Qt 6, but we can set the policy
    try:
        # For Qt 6.0+, use the new high DPI scaling policy
        if hasattr(QApplication, 'setHighDpiScaleFactorRoundingPolicy'):
            from PySide6.QtCore import Qt
            QApplication.setHighDpiScaleFactorRoundingPolicy(
                Qt.HighDpiScaleFactorRoundingPolicy.PassThrough
            )
    except (ImportError, AttributeError):
        # Fallback for older Qt versions if needed
        if hasattr(Qt, 'AA_EnableHighDpiScaling'):
            QApplication.setAttribute(Qt.ApplicationAttribute.AA_EnableHighDpiScaling, True)
        if hasattr(Qt, 'AA_UseHighDpiPixmaps'):
            QApplication.setAttribute(Qt.ApplicationAttribute.AA_UseHighDpiPixmaps, True)
    
    sys.exit(main())
