#!/usr/bin/env python3
"""
TalkBridge Desktop - Minimal Test
=================================

Basic test of the desktop interface to verify
that PyQt6 and main components work.
"""

import sys
from pathlib import Path

# Add the project root directory to the path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from PyQt6.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QWidget, QPushButton, QLabel
from PyQt6.QtCore import Qt


class TestWindow(QMainWindow):
    """Simple test window."""
    
    def __init__(self):
        super().__init__()
        self.setWindowTitle("TalkBridge Desktop - Test")
        self.setFixedSize(600, 400)
        
        # Central widget
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # Layout
        layout = QVBoxLayout(central_widget)
        layout.setSpacing(20)
        layout.setContentsMargins(40, 40, 40, 40)
        
        # Title
        title = QLabel("🚀 TalkBridge Desktop")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title.setStyleSheet("""
            font-size: 24px;
            font-weight: bold;
            color: #ffffff;
            background-color: transparent;
            padding: 20px;
        """)
        layout.addWidget(title)
        
        # Description
        desc = QLabel("Desktop interface working correctly ✅")
        desc.setAlignment(Qt.AlignmentFlag.AlignCenter)
        desc.setStyleSheet("""
            font-size: 14px;
            color: #cccccc;
            background-color: transparent;
            padding: 10px;
        """)
        layout.addWidget(desc)
        
        # System info
        info = QLabel(f"Python: {sys.version}")
        info.setAlignment(Qt.AlignmentFlag.AlignCenter)
        info.setStyleSheet("""
            font-size: 10px;
            color: #888888;
            background-color: transparent;
            padding: 5px;
        """)
        layout.addWidget(info)
        
        # Close button
        close_btn = QPushButton("Close Application")
        close_btn.clicked.connect(self.close)
        close_btn.setStyleSheet("""
            QPushButton {
                background-color: #0078d4;
                color: #ffffff;
                border: none;
                border-radius: 6px;
                padding: 12px 24px;
                font-weight: bold;
                font-size: 12px;
            }
            QPushButton:hover {
                background-color: #106ebe;
            }
            QPushButton:pressed {
                background-color: #005a9e;
            }
        """)
        layout.addWidget(close_btn)
        
        layout.addStretch()
        
        # Window style
        self.setStyleSheet("""
            QMainWindow {
                background-color: #2b2b2b;
                color: #ffffff;
            }
        """)
        
        # Center window
        self.center()
    
    def center(self):
        """Center the window on the screen."""
        screen = self.screen().availableGeometry()
        window = self.frameGeometry()
        window.moveCenter(screen.center())
        self.move(window.topLeft())


def main():
    """Main test function."""
    print("🚀 Starting TalkBridge Desktop test...")
    
    # Create application
    app = QApplication(sys.argv)
    app.setApplicationName("TalkBridge Desktop Test")
    
    # Create window
    window = TestWindow()
    window.show()
    
    print("✅ Window created and shown")
    print("💡 Close the window to finish the test")
    
    # Run application
    result = app.exec()
    
    print(f"🏁 Application finished (code: {result})")
    return result


if __name__ == "__main__":
    sys.exit(main())