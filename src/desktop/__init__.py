#! /src/desktop/windows/dashboard.py
#----------------------------------------------------------------------------------------------------------------------------
# description: Dashboard UI for TalkBridge Desktop application
#----------------------------------------------------------------------------------------------------------------------------
# author: ingekastel
# date: 2025-06-02
# version: 1.0
#----------------------------------------------------------------------------------------------------------------------------
# requirements:
# - PyQt6
#----------------------------------------------------------------------------------------------------------------------------
# functions:
# - setup_application_settings: Configure global Qt application settings
# - setup_application_logging: Configure logging for the application
# - check_dependencies: Check for critical dependencies
# - show_error_dialog: Display an error dialog
#----------------------------------------------------------------------------------------------------------------------------

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