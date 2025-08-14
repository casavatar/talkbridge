"""
TalkBridge Desktop Application Package
=====================================

Modern desktop interface for TalkBridge using PyQt6.

Author: TalkBridge Team
Version: 1.0.0
Date: 2025

Main components:
- Application: Application lifecycle management
- StateManager: Centralized state management
- CoreBridge: Bridge between UI and core services
- Dashboard: Main view with service status
- LoginDialog: User authentication

Usage:
    from src.desktop.main import main
    main()
"""

__version__ = "1.0.0"
__author__ = "TalkBridge Team"
__email__ = "support@talkbridge.com"

# Verify critical units
try:
    from PyQt6.QtWidgets import QApplication
    PYQT6_AVAILABLE = True
except ImportError:
    PYQT6_AVAILABLE = False

try:
    import yaml
    YAML_AVAILABLE = True
except ImportError:
    YAML_AVAILABLE = False

# Dependency status
DEPENDENCIES_OK = PYQT6_AVAILABLE and YAML_AVAILABLE

if not DEPENDENCIES_OK:
    import warnings
    missing = []
    if not PYQT6_AVAILABLE:
        missing.append("PyQt6")
    if not YAML_AVAILABLE:
        missing.append("PyYAML")

    warnings.warn(
        f"Missing dependencies: {', '.join(missing)}. "
        f"Install with: pip install {' '.join(missing)}",
        ImportWarning
    )

__all__ = [
    "__version__",
    "__author__", 
    "__email__",
    "DEPENDENCIES_OK",
    "PYQT6_AVAILABLE",
    "YAML_AVAILABLE"
]