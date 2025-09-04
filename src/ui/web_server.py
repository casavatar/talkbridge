#!/usr/bin/env python3
"""
TalkBridge UI - Web Server
==========================

Web server module for TalkBridge

Author: TalkBridge Team
Date: 2025-08-19
Version: 1.0

Requirements:
- PyQt6
- Flask
======================================================================
Functions:
- main: Main function to run the web server.
- __init__: Function __init__
- end_headers: Add CORS headers for cross-origin requests.
- do_OPTIONS: Handle preflight requests for CORS.
- log_message: Custom logging for request handling.
- __init__: Initialize the web server.
- start: Start the web server.
- _run_server: Run the HTTP server.
- _open_browser: Open the default browser to the web interface.
- stop: Stop the web server.
======================================================================
"""

import os
import sys
from pathlib import Path
from http.server import HTTPServer, SimpleHTTPRequestHandler
import threading
import webbrowser
import logging

# Add src to path for imports
sys.path.append(str(Path(__file__).parent.parent))

logger = logging.getLogger(__name__)


class TalkBridgeHTTPRequestHandler(SimpleHTTPRequestHandler):
    """Custom HTTP request handler for TalkBridge web interface."""
    
    def __init__(self, *args, **kwargs):
        # Set the directory to serve from
        self.directory = Path(__file__).parent
        super().__init__(*args, **kwargs)
    
    def end_headers(self):
        """Add CORS headers for cross-origin requests."""
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        super().end_headers()
    
    def do_OPTIONS(self):
        """Handle preflight requests for CORS."""
        self.send_response(200)
        self.end_headers()
    
    def log_message(self, format, *args):
        """Custom logging for request handling."""
        logger.info(f"Web request: {format % args}")


class TalkBridgeWebServer:
    """Web server for TalkBridge application."""
    
    def __init__(self, host='localhost', port=8080):
        """
        Initialize the web server.
        
        Args:
            host: Server host address
            port: Server port number
        """
        self.host = host
        self.port = port
        self.server = None
        self.server_thread = None
        self.is_running = False
    
    def start(self):
        """Start the web server."""
        try:
            # Create server
            self.server = HTTPServer((self.host, self.port), TalkBridgeHTTPRequestHandler)
            self.is_running = True
            
            logger.info(f"Starting TalkBridge web server on http://{self.host}:{self.port}")
            
            # Start server in a separate thread
            self.server_thread = threading.Thread(target=self._run_server, daemon=True)
            self.server_thread.start()
            
            # Open browser
            self._open_browser()
            
            return True
            
        except Exception as e:
            logger.error(f"Failed to start web server: {e}")
            return False
    
    def _run_server(self):
        """Run the HTTP server."""
        try:
            self.server.serve_forever()
        except KeyboardInterrupt:
            logger.info("Web server stopped by user")
        except Exception as e:
            logger.error(f"Web server error: {e}")
        finally:
            self.is_running = False
    
    def _open_browser(self):
        """Open the default browser to the web interface."""
        try:
            url = f"http://{self.host}:{self.port}/templates/index.html"
            webbrowser.open(url)
            logger.info(f"Opened browser to: {url}")
        except Exception as e:
            logger.warning(f"Could not open browser automatically: {e}")
            print(f"\nPlease open your browser and navigate to: http://{self.host}:{self.port}/templates/index.html")
    
    def stop(self):
        """Stop the web server."""
        if self.server:
            self.server.shutdown()
            self.is_running = False
            logger.info("Web server stopped")
    
    def is_server_running(self):
        """Check if the server is running."""
        return self.is_running


def main():
    """Main function to run the web server."""
    import argparse
    
    parser = argparse.ArgumentParser(description='TalkBridge Web Server')
    parser.add_argument('--host', default='localhost', help='Server host (default: localhost)')
    parser.add_argument('--port', type=int, default=8080, help='Server port (default: 8080)')
    parser.add_argument('--no-browser', action='store_true', help='Do not open browser automatically')
    
    args = parser.parse_args()
    
    # Configure logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    # Create and start server
    server = TalkBridgeWebServer(host=args.host, port=args.port)
    
    if server.start():
        print(f"\n🎤 TalkBridge Web Server")
        print(f"📍 Server running at: http://{args.host}:{args.port}")
        print(f"🌐 Web interface: http://{args.host}:{args.port}/templates/index.html")
        print(f"\n📋 Features:")
        print(f"   • Microphone access with echo cancellation")
        print(f"   • Webcam access with HD video support")
        print(f"   • Real-time permission status monitoring")
        print(f"   • Device enumeration and selection")
        print(f"   • Error handling and user feedback")
        print(f"\n🛑 Press Ctrl+C to stop the server")
        
        try:
            # Keep the main thread alive
            while server.is_server_running():
                import time
                time.sleep(1)
        except KeyboardInterrupt:
            print("\n🛑 Stopping server...")
            server.stop()
            print("✅ Server stopped")
    else:
        print("❌ Failed to start web server")
        sys.exit(1)


if __name__ == "__main__":
    main() 