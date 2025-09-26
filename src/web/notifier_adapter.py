"""
Web Notification Adapter for Flask applications.

This module provides a Flask-compatible notification system that
integrates with the framework-agnostic notifier using polling or WebSockets.
"""

import json
import threading
import logging
from collections import deque
from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta

from ..ui.notifier import NotifierPort, Notification, Level

logger = logging.getLogger(__name__)


class WebNotificationBuffer:
    """
    Thread-safe ring buffer for web notifications.
    
    Stores notifications that can be polled by web clients.
    """
    
    def __init__(self, max_size: int = 100):
        """
        Initialize the notification buffer.
        
        Args:
            max_size: Maximum number of notifications to keep
        """
        self.max_size = max_size
        self._buffer = deque(maxlen=max_size)
        self._lock = threading.RLock()
        self._id_counter = 0
    
    def add(self, notification: Notification) -> int:
        """
        Add a notification to the buffer.
        
        Args:
            notification: The notification to add
            
        Returns:
            The notification ID
        """
        with self._lock:
            self._id_counter += 1
            notification_data = {
                'id': self._id_counter,
                'level': notification.level.value,
                'message': notification.message,
                'details': notification.details,
                'context': notification.context,
                'timestamp': notification.timestamp.isoformat() if hasattr(notification, 'timestamp') else datetime.now().isoformat()
            }
            self._buffer.append(notification_data)
            return self._id_counter
    
    def get_since(self, since_id: int = 0) -> List[Dict[str, Any]]:
        """
        Get notifications since a given ID.
        
        Args:
            since_id: Only return notifications with ID > since_id
            
        Returns:
            List of notification dictionaries
        """
        with self._lock:
            return [n for n in self._buffer if n['id'] > since_id]
    
    def get_all(self) -> List[Dict[str, Any]]:
        """Get all notifications in the buffer."""
        with self._lock:
            return list(self._buffer)
    
    def clear(self) -> None:
        """Clear all notifications."""
        with self._lock:
            self._buffer.clear()
    
    def get_latest(self, count: int = 10) -> List[Dict[str, Any]]:
        """
        Get the latest N notifications.
        
        Args:
            count: Number of notifications to return
            
        Returns:
            List of latest notification dictionaries
        """
        with self._lock:
            latest = list(self._buffer)[-count:] if self._buffer else []
            return latest


class WebNotifier(NotifierPort):
    """
    Web notification adapter for Flask applications.
    
    This class implements the NotifierPort protocol and provides
    thread-safe notification handling for web applications.
    """
    
    def __init__(self, buffer_size: int = 100):
        """
        Initialize the web notifier.
        
        Args:
            buffer_size: Maximum number of notifications to buffer
        """
        self.buffer = WebNotificationBuffer(buffer_size)
        self._websocket_clients = set()
        self._websocket_lock = threading.RLock()
    
    def push(self, note: Notification) -> None:
        """
        Handle a notification by adding it to the buffer.
        
        Args:
            note: The notification to handle
        """
        try:
            notification_id = self.buffer.add(note)
            
            # If we have WebSocket clients, send real-time notification
            self._broadcast_to_websockets(note, notification_id)
            
        except Exception as e:
            logger.error(f"Error handling web notification: {e}")
    
    def _broadcast_to_websockets(self, notification: Notification, notification_id: int) -> None:
        """
        Broadcast notification to WebSocket clients.
        
        Args:
            notification: The notification to broadcast
            notification_id: The notification ID
        """
        if not self._websocket_clients:
            return
            
        try:
            message_data = {
                'id': notification_id,
                'level': notification.level.value,
                'message': notification.message,
                'details': notification.details,
                'context': notification.context,
                'timestamp': notification.timestamp.isoformat() if hasattr(notification, 'timestamp') else datetime.now().isoformat()
            }
            
            # Note: Actual WebSocket implementation would depend on the WebSocket library used
            # This is a placeholder for the broadcast logic
            logger.debug(f"Broadcasting notification to {len(self._websocket_clients)} WebSocket clients")
            
        except Exception as e:
            logger.error(f"Error broadcasting to WebSocket clients: {e}")
    
    def register_websocket_client(self, client_id: str) -> None:
        """Register a WebSocket client for real-time notifications."""
        with self._websocket_lock:
            self._websocket_clients.add(client_id)
            logger.debug(f"Registered WebSocket client: {client_id}")
    
    def unregister_websocket_client(self, client_id: str) -> None:
        """Unregister a WebSocket client."""
        with self._websocket_lock:
            self._websocket_clients.discard(client_id)
            logger.debug(f"Unregistered WebSocket client: {client_id}")
    
    def get_notifications_since(self, since_id: int = 0) -> List[Dict[str, Any]]:
        """
        Get notifications since a given ID (for polling).
        
        Args:
            since_id: Only return notifications with ID > since_id
            
        Returns:
            List of notification dictionaries
        """
        return self.buffer.get_since(since_id)
    
    def get_latest_notifications(self, count: int = 10) -> List[Dict[str, Any]]:
        """
        Get the latest notifications.
        
        Args:
            count: Number of notifications to return
            
        Returns:
            List of latest notification dictionaries
        """
        return self.buffer.get_latest(count)
    
    def clear_notifications(self) -> None:
        """Clear all notifications."""
        self.buffer.clear()


def create_flask_routes(app, web_notifier: WebNotifier):
    """
    Create Flask routes for notification polling.
    
    Args:
        app: Flask application instance
        web_notifier: WebNotifier instance
    """
    from flask import request
    
    @app.route('/api/notifications', methods=['GET'])
    def get_notifications():
        """Get latest notifications."""
        try:
            since_id = int(request.args.get('since', 0))
            notifications = web_notifier.get_notifications_since(since_id)
            
            return {
                'success': True,
                'notifications': notifications,
                'count': len(notifications)
            }
        except Exception as e:
            logger.error(f"Error getting notifications: {e}")
            return {
                'success': False,
                'error': str(e),
                'notifications': []
            }, 500
    
    @app.route('/api/notifications/latest', methods=['GET'])
    def get_latest_notifications():
        """Get latest N notifications."""
        try:
            count = int(request.args.get('count', 10))
            notifications = web_notifier.get_latest_notifications(count)
            
            return {
                'success': True,
                'notifications': notifications,
                'count': len(notifications)
            }
        except Exception as e:
            logger.error(f"Error getting latest notifications: {e}")
            return {
                'success': False,
                'error': str(e),
                'notifications': []
            }, 500
    
    @app.route('/api/notifications/clear', methods=['POST'])
    def clear_notifications():
        """Clear all notifications."""
        try:
            web_notifier.clear_notifications()
            return {
                'success': True,
                'message': 'Notifications cleared'
            }
        except Exception as e:
            logger.error(f"Error clearing notifications: {e}")
            return {
                'success': False,
                'error': str(e)
            }, 500


def create_socketio_handlers(socketio, web_notifier: WebNotifier):
    """
    Create Socket.IO handlers for real-time notifications.
    
    Args:
        socketio: Flask-SocketIO instance
        web_notifier: WebNotifier instance
    """
    from flask import request
    
    @socketio.on('connect')
    def handle_connect():
        """Handle client connection."""
        client_id = request.sid
        web_notifier.register_websocket_client(client_id)
        logger.info(f"Client connected: {client_id}")
    
    @socketio.on('disconnect')
    def handle_disconnect():
        """Handle client disconnection."""
        client_id = request.sid
        web_notifier.unregister_websocket_client(client_id)
        logger.info(f"Client disconnected: {client_id}")
    
    @socketio.on('subscribe_notifications')
    def handle_subscribe():
        """Handle notification subscription."""
        client_id = request.sid
        # Send recent notifications to newly subscribed client
        recent = web_notifier.get_latest_notifications(5)
        for notification in recent:
            socketio.emit('notification', notification, room=client_id)


# Global web notifier instance (singleton pattern)
_global_web_notifier: Optional[WebNotifier] = None


def get_web_notifier() -> WebNotifier:
    """Get the global web notifier instance."""
    global _global_web_notifier
    if _global_web_notifier is None:
        _global_web_notifier = WebNotifier()
    return _global_web_notifier


# JavaScript client code template for polling
JS_POLLING_CLIENT = """
class NotificationPoller {
    constructor(baseUrl = '', pollInterval = 2000) {
        this.baseUrl = baseUrl;
        this.pollInterval = pollInterval;
        this.lastNotificationId = 0;
        this.isPolling = false;
        this.callbacks = {
            info: [],
            warning: [],
            error: [],
            success: [],
            debug: []
        };
    }
    
    start() {
        if (this.isPolling) return;
        this.isPolling = true;
        this.poll();
    }
    
    stop() {
        this.isPolling = false;
    }
    
    onNotification(level, callback) {
        if (this.callbacks[level]) {
            this.callbacks[level].push(callback);
        }
    }
    
    async poll() {
        if (!this.isPolling) return;
        
        try {
            const response = await fetch(
                `${this.baseUrl}/api/notifications?since=${this.lastNotificationId}`
            );
            const data = await response.json();
            
            if (data.success && data.notifications.length > 0) {
                for (const notification of data.notifications) {
                    this.handleNotification(notification);
                    this.lastNotificationId = Math.max(this.lastNotificationId, notification.id);
                }
            }
        } catch (error) {
            console.error('Error polling notifications:', error);
        }
        
        if (this.isPolling) {
            setTimeout(() => this.poll(), this.pollInterval);
        }
    }
    
    handleNotification(notification) {
        const callbacks = this.callbacks[notification.level] || [];
        for (const callback of callbacks) {
            try {
                callback(notification);
            } catch (error) {
                console.error('Error in notification callback:', error);
            }
        }
    }
}

// Usage example:
// const poller = new NotificationPoller();
// poller.onNotification('error', (notification) => {
//     showToast(notification.message, 'error');
// });
// poller.start();
"""