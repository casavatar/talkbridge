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
    import customtkinter as ctk
    import tkinter as tk
    CUSTOMTKINTER_AVAILABLE = True
except ImportError:
    CUSTOMTKINTER_AVAILABLE = False

try:
    import yaml
    YAML_AVAILABLE = True
except ImportError:
    YAML_AVAILABLE = False

# Dependency status
DEPENDENCIES_OK = CUSTOMTKINTER_AVAILABLE and YAML_AVAILABLE

if not DEPENDENCIES_OK:
    import warnings
    missing = []
    if not CUSTOMTKINTER_AVAILABLE:
        missing.append("customtkinter")
    if not YAML_AVAILABLE:
        missing.append("PyYAML")

    warnings.warn(
        f"Missing dependencies: {', '.join(missing)}. "
        f"Install with: pip install {' '.join(missing)}",
        ImportWarning
    )

# Main module availability check (don't import, just check if it exists)
if DEPENDENCIES_OK:
    try:
        import importlib.util
        main_spec = importlib.util.find_spec("talkbridge.desktop.main")
        MAIN_AVAILABLE = main_spec is not None
    except ImportError:
        MAIN_AVAILABLE = False
else:
    MAIN_AVAILABLE = False

__all__ = [
    "__version__",
    "__author__", 
    "__email__",
    "DEPENDENCIES_OK",
    "CUSTOMTKINTER_AVAILABLE",
    "YAML_AVAILABLE",
    "MAIN_AVAILABLE"
]

# Note: main is not imported automatically to prevent duplicate import issues
# when using python -m talkbridge.desktop.main
