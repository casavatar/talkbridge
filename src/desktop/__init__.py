#! /src/desktop/windows/dashboard.py
"""
TalkBridge Desktop -   Init   - Package Initialization
======================================================

Inicialización del paquete

Author: TalkBridge Team
Date: 2025-08-19
Version: 1.0

Requirements:
- PyQt6
"""

__version__ = "1.0.0"
__author__ = "TalkBridge Team"
__email__ = "support@talkbridge.com"

# Verify critical units
try:
    from PySide6.QtWidgets import QApplication
    PYSIDE6_AVAILABLE = True
except ImportError:
    PYSIDE6_AVAILABLE = False

try:
    import yaml
    YAML_AVAILABLE = True
except ImportError:
    YAML_AVAILABLE = False

# Dependency status
DEPENDENCIES_OK = PYSIDE6_AVAILABLE and YAML_AVAILABLE

if not DEPENDENCIES_OK:
    import warnings
    missing = []
    if not PYSIDE6_AVAILABLE:
        missing.append("PySide6")
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
    "PYSIDE6_AVAILABLE",
    "YAML_AVAILABLE"
]
