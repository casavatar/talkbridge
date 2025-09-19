#!/usr/bin/env python3
"""
TalkBridge Web Server
=====================

Consolidated Flask-based web server for TalkBridge

Author: TalkBridge Team
Date: 2025-09-18
Version: 2.0

Requirements:
- Flask
- Flask-CORS
======================================================================
"""

import os
import sys
import json
import webbrowser
import threading
from pathlib import Path
from typing import Optional

# Import Flask with graceful fallback
try:
    from flask import Flask, render_template, request, jsonify, send_from_directory
    from flask_cors import CORS
    FLASK_AVAILABLE = True
except ImportError:
    FLASK_AVAILABLE = False
    Flask = None
    CORS = None

# Import centralized logging
from talkbridge.logging_config import get_logger

# Import notification system
try:
    from ..ui.notifier import notifier, notify, Level, subscribe
    from .notifier_adapter import WebNotifier, create_flask_routes
    NOTIFICATIONS_AVAILABLE = True
except ImportError:
    NOTIFICATIONS_AVAILABLE = False
    notifier = None

logger = get_logger(__name__)

class TalkBridgeWebServer:
    """Flask-based web server for TalkBridge application."""
    
    def __init__(self, host='localhost', port=8080, debug=False):
        """
        Initialize the web server.
        
        Args:
            host: Server host address
            port: Server port number
            debug: Enable Flask debug mode
        """
        if not FLASK_AVAILABLE:
            raise ImportError("Flask is required to run the web server. Install with: pip install flask flask-cors")
        
        self.host = host
        self.port = port
        self.debug = debug
        self.app = None
        self.server_thread = None
        self.is_running = False
        
        # Initialize web notifier and subscribe to centralized notifier
        self.web_notifier = None
        if NOTIFICATIONS_AVAILABLE:
            try:
                self.web_notifier = WebNotifier()
                subscribe(self.web_notifier)
                logger.info("Web server integrated with centralized notification system")
            except Exception as e:
                logger.warning(f"Failed to initialize web notifier: {e}")
        
        self._setup_flask_app()
    
    def _setup_flask_app(self):
        """Set up the Flask application."""
        # Create Flask app with proper template and static directories
        template_dir = Path(__file__).parent / "templates"
        static_dir = Path(__file__).parent / "static"
        
        self.app = Flask(
            __name__,
            template_folder=str(template_dir),
            static_folder=str(static_dir)
        )
        
        # Enable CORS for cross-origin requests
        CORS(self.app, origins="*")
        
        # Configure app
        self.app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'talkbridge-dev-key')
        
        # Set up routes
        self._setup_routes()
        
        # Set up notification routes if available
        if NOTIFICATIONS_AVAILABLE and self.web_notifier:
            create_flask_routes(self.app, self.web_notifier)
    
    def _setup_routes(self):
        """Set up Flask routes."""
        
        @self.app.route('/')
        def index():
            """Main index page."""
            return render_template('index.html')
        
        @self.app.route('/health')
        def health_check():
            """Health check endpoint."""
            return jsonify({
                'status': 'healthy',
                'service': 'talkbridge-web',
                'notifications_enabled': NOTIFICATIONS_AVAILABLE
            })
        
        @self.app.route('/api/status')
        def api_status():
            """API status endpoint."""
            return jsonify({
                'web_server': 'running',
                'notifications': 'enabled' if NOTIFICATIONS_AVAILABLE else 'disabled',
                'timestamp': __import__('time').time()
            })
        
        @self.app.route('/static/<path:filename>')
        def serve_static(filename):
            """Serve static files."""
            static_dir = Path(__file__).parent / "static"
            return send_from_directory(static_dir, filename)
        
        # Error handlers
        @self.app.errorhandler(404)
        def not_found(error):
            """Handle 404 errors."""
            return render_template('error.html', 
                                 error_code=404, 
                                 error_message="Page not found"), 404
        
        @self.app.errorhandler(500)
        def internal_error(error):
            """Handle 500 errors."""
            logger.error(f"Internal server error: {error}")
            if NOTIFICATIONS_AVAILABLE:
                try:
                    notify("Web server encountered an internal error", Level.ERROR, category="web_server")
                except Exception as e:
                    logger.warning(f"Failed to send error notification: {e}")
            
            return render_template('error.html',
                                 error_code=500,
                                 error_message="Internal server error"), 500
    
    def start(self, open_browser=True):
        """Start the web server."""
        try:
            logger.info(f"Starting TalkBridge web server on http://{self.host}:{self.port}")
            
            # Send startup notification
            if NOTIFICATIONS_AVAILABLE:
                try:
                    notify(f"Web server starting on {self.host}:{self.port}", Level.INFO, category="web_server")
                except Exception as e:
                    logger.warning(f"Failed to send startup notification: {e}")
            
            # Start server in a separate thread if not in debug mode
            if self.debug:
                # In debug mode, run directly (blocking)
                self.app.run(host=self.host, port=self.port, debug=True)
            else:
                # Production mode - run in thread
                self.server_thread = threading.Thread(
                    target=lambda: self.app.run(
                        host=self.host, 
                        port=self.port, 
                        debug=False,
                        use_reloader=False
                    ),
                    daemon=True
                )
                self.server_thread.start()
                self.is_running = True
            
            # Open browser if requested
            if open_browser and not self.debug:
                self._open_browser()
            
            return True
            
        except Exception as e:
            logger.error(f"Failed to start web server: {e}")
            if NOTIFICATIONS_AVAILABLE:
                try:
                    notify(f"Failed to start web server: {e}", Level.ERROR, category="web_server")
                except Exception as ex:
                    logger.warning(f"Failed to send error notification: {ex}")
            return False
    
    def _open_browser(self):
        """Open the default browser to the web interface."""
        try:
            url = f"http://{self.host}:{self.port}"
            webbrowser.open(url)
            logger.info(f"Opened browser to: {url}")
        except Exception as e:
            logger.warning(f"Could not open browser automatically: {e}")
            logger.info(f"Please open your browser and navigate to: http://{self.host}:{self.port}")
            if notifier:
                notifier.notify_info(f"Web server running at http://{self.host}:{self.port}")
    
    def stop(self):
        """Stop the web server."""
        if self.is_running:
            self.is_running = False
            logger.info("Web server stopped")
            
            if NOTIFICATIONS_AVAILABLE:
                try:
                    notify("Web server stopped", Level.INFO, category="web_server")
                except Exception as e:
                    logger.warning(f"Failed to send stop notification: {e}")
    
    def is_server_running(self):
        """Check if the server is running."""
        return self.is_running

def run():
    """Main function to run the web server."""
    if not FLASK_AVAILABLE:
        logger.error("Flask is not available. Install with: pip install flask flask-cors")
        logger.error("   Or install the full requirements: pip install -r requirements.txt")
        if notifier:
            notifier.notify_error("Flask not available. Please install dependencies.")
        return
    
    import argparse
    
    parser = argparse.ArgumentParser(description='TalkBridge Web Server')
    parser.add_argument('--host', default='localhost', help='Server host (default: localhost)')
    parser.add_argument('--port', type=int, default=8080, help='Server port (default: 8080)')
    parser.add_argument('--no-browser', action='store_true', help='Do not open browser automatically')
    parser.add_argument('--debug', action='store_true', help='Enable debug mode')
    
    args = parser.parse_args()
    
    # Create and start server
    server = TalkBridgeWebServer(host=args.host, port=args.port, debug=args.debug)
    
    if server.start(open_browser=not args.no_browser):
        logger.info("TalkBridge Web Server")
        logger.info(f"Server running at: http://{args.host}:{args.port}")
        logger.info(f"Notifications: {'Enabled' if NOTIFICATIONS_AVAILABLE else 'Disabled'}")
        logger.info("Features:")
        logger.info("   • RESTful API for TalkBridge services")
        logger.info("   • Real-time notifications via REST/WebSocket")
        logger.info("   • Static file serving and templating")
        logger.info("   • CORS support for cross-origin requests")
        logger.info("   • Health monitoring and error handling")
        logger.info("Press Ctrl+C to stop the server")
        
        if notifier:
            notifier.notify_info(f"Web server started at http://{args.host}:{args.port}")
        
        try:
            # Keep the main thread alive (unless in debug mode)
            if not args.debug:
                while server.is_server_running():
                    import time
                    time.sleep(1)
        except KeyboardInterrupt:
            logger.info("Stopping server...")
            server.stop()
            logger.info("Server stopped")
            if notifier:
                notifier.notify_info("Web server stopped")
    else:
        logger.error("Failed to start web server")
        if notifier:
            notifier.notify_error("Failed to start web server")
        sys.exit(1)

if __name__ == "__main__":
    run()