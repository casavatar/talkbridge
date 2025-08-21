"""
TalkBridge Desktop - Main Window
================================

Ventana principal con pestañas integradas para chat, avatar y configuración.

Author: TalkBridge Team
Date: 2025-08-19
Version: 1.0

Requirements:
- PyQt6
======================================================================
Functions:
- __init__: Initialize the main window with tabs
- setup_ui: Sets up the main interface with tab widget
- create_menu_bar: Creates the menu bar
- create_status_bar: Creates the status bar
- configure_window: Configures window properties
- center_window: Centers the window on the screen
- connect_signals: Connects component signals
- show_logout_dialog: Shows logout confirmation dialog
- logout: Handles user logout
======================================================================
"""

import logging
from typing import Optional
from pathlib import Path

from PySide6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QMenuBar, QStatusBar, QTabWidget, QToolBar,
    QLabel, QMessageBox, QPushButton, QApplication
)
from PySide6.QtCore import Signal, QTimer, Qt, QSize
from PySide6.QtGui import QAction, QFont, QIcon

# Import the tab components
from src.desktop.components.chat_tab import ChatTab
from src.desktop.components.avatar_tab import AvatarTab  
from src.desktop.components.settings_tab import SettingsTab


class MainWindow(QMainWindow):
    """
    Main window of TalkBridge Desktop with integrated tabs.

    Features:
    - Tab widget with Chat, Avatar, and Settings tabs
    - MenuBar with main options
    - StatusBar with status information
    - Logout functionality
    """

    # Signals
    window_closing = Signal()
    logout_requested = Signal()
    view_changed = Signal(str)  # Emitted when view changes
    
    def __init__(self, state_manager=None, core_bridge=None, parent=None):
        super().__init__(parent)

        self.state_manager = state_manager
        self.core_bridge = core_bridge
        self.logger = logging.getLogger("talkbridge.desktop.mainwindow")

        # Main widgets
        self.central_widget: Optional[QWidget] = None
        self.tab_widget: Optional[QTabWidget] = None
        self.chat_tab: Optional[ChatTab] = None
        self.avatar_tab: Optional[AvatarTab] = None
        self.settings_tab: Optional[SettingsTab] = None
        self.status_label: Optional[QLabel] = None

        try:
            self.setup_ui()
            self.logger.info("UI setup completed")
        except Exception as e:
            self.logger.error(f"Error in setup_ui: {e}")
            raise
            
        try:
            self.create_menu_bar()
            self.logger.info("Menu bar created")
        except Exception as e:
            self.logger.error(f"Error in create_menu_bar: {e}")
            raise
            
        try:
            self.create_status_bar()
            self.logger.info("Status bar created")
        except Exception as e:
            self.logger.error(f"Error in create_status_bar: {e}")
            raise
            
        try:
            self.connect_signals()
            self.logger.info("Signals connected")
        except Exception as e:
            self.logger.error(f"Error in connect_signals: {e}")
            raise

        # Configure window
        self.configure_window()

        self.logger.info("MainWindow initialized with integrated tabs")
    
    def setup_ui(self) -> None:
        """Sets up the main interface with tab widget."""
        # Central widget
        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)

        layout = QVBoxLayout(self.central_widget)
        layout.setContentsMargins(5, 5, 5, 5)
        layout.setSpacing(5)

        # Header with title and logout button
        header_layout = QHBoxLayout()
        
        # Title
        title_label = QLabel("🌉 TalkBridge Desktop")
        title_font = QFont()
        title_font.setPointSize(18)
        title_font.setBold(True)
        title_label.setFont(title_font)
        title_label.setStyleSheet("color: #2196F3; padding: 10px;")
        header_layout.addWidget(title_label)
        
        header_layout.addStretch()
        
        # Logout button
        self.logout_button = QPushButton("🚪 Cerrar Sesión")
        self.logout_button.setStyleSheet("""
            QPushButton {
                background-color: #f44336;
                color: white;
                border: none;
                border-radius: 15px;
                padding: 8px 16px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #d32f2f;
            }
        """)
        self.logout_button.clicked.connect(self.show_logout_dialog)
        header_layout.addWidget(self.logout_button)
        
        layout.addLayout(header_layout)

        # Tab widget for main content
        self.tab_widget = QTabWidget()
        self.tab_widget.setTabPosition(QTabWidget.TabPosition.North)
        self.tab_widget.setMovable(False)
        self.tab_widget.setDocumentMode(True)
        
        # Style the tab widget
        self.tab_widget.setStyleSheet("""
            QTabWidget::pane {
                border: 1px solid #cccccc;
                border-radius: 5px;
                background-color: white;
            }
            QTabBar::tab {
                background-color: #f0f0f0;
                border: 1px solid #cccccc;
                border-bottom: none;
                border-top-left-radius: 5px;
                border-top-right-radius: 5px;
                padding: 8px 16px;
                margin-right: 2px;
                font-weight: bold;
            }
            QTabBar::tab:selected {
                background-color: white;
                color: #2196F3;
            }
            QTabBar::tab:hover {
                background-color: #e3f2fd;
            }
        """)

        # Create and add tabs
        try:
            # Chat Tab
            self.chat_tab = ChatTab()
            self.tab_widget.addTab(self.chat_tab, "💬 Chat Traducido")
            
            # Avatar Tab  
            self.avatar_tab = AvatarTab()
            self.tab_widget.addTab(self.avatar_tab, "👤 Avatar Animado")
            
            # Settings Tab
            self.settings_tab = SettingsTab()
            self.tab_widget.addTab(self.settings_tab, "⚙️ Configuración")
            
            self.logger.info("All tabs created successfully")
            
        except Exception as e:
            self.logger.error(f"Error creating tabs: {e}")
            # Create a fallback simple tab if there are issues
            fallback_widget = QWidget()
            fallback_layout = QVBoxLayout(fallback_widget)
            fallback_label = QLabel("Error al cargar componentes. Ejecutando en modo básico.")
            fallback_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            fallback_layout.addWidget(fallback_label)
            self.tab_widget.addTab(fallback_widget, "⚠️ Modo Básico")

        layout.addWidget(self.tab_widget)

    def create_menu_bar(self) -> None:
        """Creates the menu bar."""
        menubar = self.menuBar()
        
        # File menu
        file_menu = menubar.addMenu("&Archivo")
        
        # Settings action
        settings_action = QAction("⚙️ &Configuración", self)
        settings_action.setShortcut("Ctrl+,")
        settings_action.triggered.connect(lambda: self.tab_widget.setCurrentIndex(2))
        file_menu.addAction(settings_action)
        
        file_menu.addSeparator()
        
        # Logout action
        logout_action = QAction("🚪 &Cerrar Sesión", self)
        logout_action.setShortcut("Ctrl+L")
        logout_action.triggered.connect(self.show_logout_dialog)
        file_menu.addAction(logout_action)
        
        # Exit action
        exit_action = QAction("❌ &Salir", self)
        exit_action.setShortcut("Ctrl+Q")
        exit_action.triggered.connect(self.close)
        file_menu.addAction(exit_action)
        
        # View menu
        view_menu = menubar.addMenu("&Ver")
        
        # Tab actions
        chat_action = QAction("💬 &Chat", self)
        chat_action.setShortcut("Ctrl+1")
        chat_action.triggered.connect(lambda: self.tab_widget.setCurrentIndex(0))
        view_menu.addAction(chat_action)
        
        avatar_action = QAction("👤 &Avatar", self)
        avatar_action.setShortcut("Ctrl+2")
        avatar_action.triggered.connect(lambda: self.tab_widget.setCurrentIndex(1))
        view_menu.addAction(avatar_action)
        
        # Help menu
        help_menu = menubar.addMenu("&Ayuda")
        
        about_action = QAction("ℹ️ &Acerca de", self)
        about_action.triggered.connect(self.show_about_dialog)
        help_menu.addAction(about_action)

    def create_status_bar(self) -> None:
        """Creates the status bar."""
        statusbar = self.statusBar()
        
        # Status label
        self.status_label = QLabel("✅ Listo")
        self.status_label.setStyleSheet("color: #4CAF50; font-weight: bold; padding: 5px;")
        statusbar.addWidget(self.status_label)
        
        # Add permanent widgets
        statusbar.addPermanentWidget(QLabel("TalkBridge v1.0"))

    def configure_window(self) -> None:
        """Configures window properties."""
        # Window properties
        self.setWindowTitle("TalkBridge Desktop - Chat Traducido con IA")
        self.setMinimumSize(1200, 800)
        self.resize(1400, 900)
        
        # Try to set window icon
        try:
            icon_path = "src/desktop/resources/icon.ico"
            if Path(icon_path).exists():
                self.setWindowIcon(QIcon(icon_path))
        except Exception:
            pass  # Icon not found, continue without it
        
        # Center window
        self.center_window()

    def center_window(self) -> None:
        """Centers the window on the screen."""
        try:
            # Get screen geometry
            screen = QApplication.primaryScreen()
            screen_geometry = screen.availableGeometry()
            
            # Calculate center position
            x = (screen_geometry.width() - self.width()) // 2
            y = (screen_geometry.height() - self.height()) // 2
            
            # Move window to center
            self.move(x, y)
            
        except Exception as e:
            self.logger.warning(f"Could not center window: {e}")

    def connect_signals(self) -> None:
        """Connects component signals."""
        try:
            # Connect tab signals to status updates
            if hasattr(self.chat_tab, 'status_changed'):
                self.chat_tab.status_changed.connect(self.update_status)
            if hasattr(self.chat_tab, 'error_occurred'):
                self.chat_tab.error_occurred.connect(self.show_error_message)
                
            if hasattr(self.avatar_tab, 'status_changed'):
                self.avatar_tab.status_changed.connect(self.update_status)
            if hasattr(self.avatar_tab, 'error_occurred'):
                self.avatar_tab.error_occurred.connect(self.show_error_message)
                
            if hasattr(self.settings_tab, 'settings_saved'):
                self.settings_tab.settings_saved.connect(
                    lambda: self.update_status("Configuración guardada exitosamente")
                )
            if hasattr(self.settings_tab, 'error_occurred'):
                self.settings_tab.error_occurred.connect(self.show_error_message)
            
            # Connect tab changes
            self.tab_widget.currentChanged.connect(self.on_tab_changed)
            
        except Exception as e:
            self.logger.error(f"Error connecting signals: {e}")

    def on_tab_changed(self, index: int) -> None:
        """Handles tab changes."""
        tab_names = ["Chat", "Avatar", "Configuración"]
        if 0 <= index < len(tab_names):
            self.update_status(f"Pestaña activa: {tab_names[index]}")

    def update_status(self, message: str) -> None:
        """Updates the status bar message."""
        if self.status_label:
            self.status_label.setText(message)
            self.status_label.setStyleSheet("color: #2196F3; font-weight: bold; padding: 5px;")
            
            # Reset to default after 5 seconds
            QTimer.singleShot(5000, lambda: (
                self.status_label.setText("✅ Listo"),
                self.status_label.setStyleSheet("color: #4CAF50; font-weight: bold; padding: 5px;")
            ))

    def show_error_message(self, message: str) -> None:
        """Shows an error message in status bar and as popup."""
        if self.status_label:
            self.status_label.setText(f"❌ Error: {message}")
            self.status_label.setStyleSheet("color: #f44336; font-weight: bold; padding: 5px;")
        
        # Also show as popup for important errors
        QMessageBox.warning(self, "Error", message)

    def show_logout_dialog(self) -> None:
        """Shows logout confirmation dialog."""
        reply = QMessageBox.question(
            self, "Cerrar Sesión",
            "¿Estás seguro de que quieres cerrar sesión?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No
        )
        
        if reply == QMessageBox.StandardButton.Yes:
            self.logout()

    def logout(self) -> None:
        """Handles user logout."""
        try:
            # Stop any ongoing processes
            if hasattr(self.avatar_tab, 'webcam_active') and self.avatar_tab.webcam_active:
                self.avatar_tab.stop_webcam()
            
            # Emit logout signal
            self.logout_requested.emit()
            
            # Close window
            self.close()
            
        except Exception as e:
            self.logger.error(f"Error during logout: {e}")

    def show_about_dialog(self) -> None:
        """Shows about dialog."""
        about_text = """
        <h2>🌉 TalkBridge Desktop</h2>
        <p><b>Versión:</b> 1.0.0</p>
        <p><b>Descripción:</b> Aplicación de chat traducido con IA y avatar animado</p>
        <br>
        <p><b>Características:</b></p>
        <ul>
        <li>💬 Chat traducido en tiempo real</li>
        <li>🎤 Reconocimiento de voz</li>
        <li>🤖 Respuestas de IA con Ollama</li>
        <li>👤 Avatar animado con sincronización labial</li>
        <li>🔊 Síntesis de voz avanzada</li>
        </ul>
        <br>
        <p><b>Desarrollado por:</b> TalkBridge Team</p>
        <p><b>Fecha:</b> 2025-08-19</p>
        """
        
        QMessageBox.about(self, "Acerca de TalkBridge", about_text)

    def closeEvent(self, event) -> None:
        """Handles window close event."""
        try:
            # Stop any ongoing processes
            if hasattr(self.avatar_tab, 'webcam_active') and self.avatar_tab.webcam_active:
                self.avatar_tab.stop_webcam()
            
            # Emit closing signal
            self.window_closing.emit()
            
            # Accept the close event
            event.accept()
            
        except Exception as e:
            self.logger.error(f"Error during window close: {e}")
            event.accept()  # Still close even if there's an error

        # Show main tab widget by default
        # self.stacked_widget.setCurrentWidget(self.dashboard)
    
    def create_menu_bar(self) -> None:
        """Creates the menu bar."""
        menubar = self.menuBar()

        # File menu
        file_menu = menubar.addMenu("&File")

        # New Chat action
        new_chat_action = QAction("&New Chat", self)
        new_chat_action.setShortcut("Ctrl+N")
        new_chat_action.setStatusTip("Start new conversation")
        new_chat_action.triggered.connect(lambda: self.show_view("chat"))
        file_menu.addAction(new_chat_action)

        file_menu.addSeparator()

        # Exit action
        exit_action = QAction("&Exit", self)
        exit_action.setShortcut("Ctrl+Q")
        exit_action.setStatusTip("Exit the application")
        exit_action.triggered.connect(self.close)
        file_menu.addAction(exit_action)

        # View menu (already handled in create_menu_bar - removed duplicate)
        
        # Additional view actions can be added here if needed

        # Tools menu
        tools_menu = menubar.addMenu("&Tools")

        settings_action = QAction("&Settings", self)
        settings_action.setShortcut("Ctrl+,")
        settings_action.triggered.connect(lambda: self.show_view("settings"))
        tools_menu.addAction(settings_action)

        # Help menu
        help_menu = menubar.addMenu("&Help")

        about_action = QAction("&About", self)
        about_action.triggered.connect(self.show_about)
        help_menu.addAction(about_action)
    
    def create_status_bar(self) -> None:
        """Creates the status bar."""
        self.statusBar().showMessage("TalkBridge Desktop - Ready")

        # Label to show user info
        self.user_status_label = QLabel("User: Loading...")
        self.statusBar().addPermanentWidget(self.user_status_label)

        # Label to show connection status
        self.connection_status_label = QLabel("●")
        self.connection_status_label.setStyleSheet("color: #16c60c; font-size: 16px;")
        self.statusBar().addPermanentWidget(self.connection_status_label)
    
    def configure_window(self) -> None:
        """Configures window properties."""
        self.setWindowTitle("TalkBridge Desktop - Real-Time Voice Translation")

        # Size and position
        if self.state_manager:
            width = self.state_manager.get_config("ui.window_size.width", 1200)
            height = self.state_manager.get_config("ui.window_size.height", 800)
        else:
            width, height = 1200, 800

        self.resize(width, height)

        # Center window
        self.center_window()

        # Minimum size
        self.setMinimumSize(800, 600)
    
    def center_window(self) -> None:
        """Centers the window on the screen."""
        screen = self.screen().availableGeometry()
        window = self.frameGeometry()
        window.moveCenter(screen.center())
        self.move(window.topLeft())
    
    def connect_signals(self) -> None:
        """Connects component signals."""
        # Connect tab signals if needed
        if hasattr(self.chat_tab, 'status_changed'):
            self.chat_tab.status_changed.connect(self.update_status)
            
        if hasattr(self.avatar_tab, 'status_changed'):
            self.avatar_tab.status_changed.connect(self.update_status)
            
        if hasattr(self.settings_tab, 'status_changed'):
            self.settings_tab.status_changed.connect(self.update_status)

        if self.state_manager:
            self.state_manager.user_session_changed.connect(
                self.update_user_status
            )
            self.state_manager.service_status_changed.connect(
                self.update_connection_status
            )
    
    def show_view(self, view_name: str) -> None:
        """
        Shows a specific view by switching to the appropriate tab.

        Args:
            view_name: Name of the view to show ("chat", "avatar", "settings")
        """
        if view_name == "chat":
            self.tab_widget.setCurrentIndex(0)
            self.statusBar().showMessage("Vista: Chat Traducido")
        elif view_name == "avatar":
            self.tab_widget.setCurrentIndex(1)
            self.statusBar().showMessage("Vista: Avatar Animado")
        elif view_name == "settings":
            self.tab_widget.setCurrentIndex(2)
            self.statusBar().showMessage("Vista: Configuración")
        else:
            self.statusBar().showMessage("Vista desconocida")

        self.view_changed.emit(view_name)
    
    def update_user_status(self, user_session) -> None:
        """
        Updates user info in the status bar.

        Args:
            user_session: Current user session
        """
        if user_session and user_session.is_authenticated:
            self.user_status_label.setText(f"User: {user_session.username}")
        else:
            self.user_status_label.setText("User: Not authenticated")
    
    def update_connection_status(self, service_name: str, status: str) -> None:
        """
        Updates the connection status indicator.

        Args:
            service_name: Name of the service
            status: Service status
        """
        # Determine color based on critical service states
        critical_services = ["tts", "audio", "translation"]

        if service_name in critical_services:
            if status == "connected":
                color = "#16c60c"  # Green
            elif status == "error":
                color = "#d13438"  # Red
            else:
                color = "#ff8c00"  # Orange

            self.connection_status_label.setStyleSheet(f"color: {color}; font-size: 16px;")
    
    def show_about(self) -> None:
        """Shows the 'About' dialog."""
        about_text = """
        <h2>TalkBridge Desktop</h2>
        <p><b>Version:</b> 1.0.0</p>
        <p><b>Description:</b> Real-time voice translation platform with AI</p>
        <p><b>Features:</b></p>
        <ul>
            <li>Voice synthesis with Coqui TTS</li>
            <li>Multi-language translation</li>
            <li>Synchronized facial animation</li>
            <li>LLM integration (Ollama)</li>
            <li>Real-time audio processing</li>
        </ul>
        <p><b>Developed by:</b> TalkBridge Team</p>
        """

        QMessageBox.about(self, "About TalkBridge", about_text)
    
    def closeEvent(self, event) -> None:
        """Handles the window close event."""
        self.logger.info("Closing main window...")

        # Save window size
        if self.state_manager:
            self.state_manager.set_config("ui.window_size.width", self.width())
            self.state_manager.set_config("ui.window_size.height", self.height())

        # Emit close signal
        self.window_closing.emit()

        # Accept close event
        event.accept()

        self.logger.info("Main window closed")
