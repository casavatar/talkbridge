"""
TalkBridge Web Package Entry Point
==================================

Allows running the web server with:
    python -m talkbridge.web

Author: TalkBridge Team
Date: 2025-09-18
Version: 2.0
"""

from .server import run

if __name__ == "__main__":
    run()