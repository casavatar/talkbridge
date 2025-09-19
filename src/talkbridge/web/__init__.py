"""
TalkBridge Web Package
======================

Consolidated web interface and server for TalkBridge

Author: TalkBridge Team
Date: 2025-09-18
Version: 2.0
"""

from .server import TalkBridgeWebServer, run
from .interface import TalkBridgeWebInterface, main as interface_main

try:
    from .notifier_adapter import WebNotificationBuffer
    NOTIFICATIONS_AVAILABLE = True
except ImportError:
    NOTIFICATIONS_AVAILABLE = False

__all__ = [
    'TalkBridgeWebServer',
    'TalkBridgeWebInterface', 
    'run',
    'interface_main',
    'NOTIFICATIONS_AVAILABLE'
]

if NOTIFICATIONS_AVAILABLE:
    __all__.append('WebNotificationBuffer')