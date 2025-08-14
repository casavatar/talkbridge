TalkBridge Desktop Application
🚀 Modern desktop interface for TalkBridge - Real-time voice translation platform powered by artificial intelligence.

📋 Table of Contents
Main Features

Architecture

Installation

Usage

Development

Configuration

File Structure

API and Services

Contributing

🎯 Main Features
✨ Modern Interface
Dark Theme design with customizable colors

Interactive cards for service status

Centralized dashboard with real-time information

Responsive design adaptable to different resolutions

🔧 Integrated Services
🎤 Text-to-Speech (TTS) with Coqui TTS

🎵 Real-time Audio Capture

🌐 Multi-language Translation

📹 Facial Detection and synchronized animation

🤖 LLM Processing with Ollama

👤 Animated Avatar with MediaPipe

🛡️ Advanced Features
Secure authentication with session management

Persistent state with auto-save

Asynchronous threading for heavy operations

Robust error handling with detailed logging

Centralized configuration via YAML
...existing code...

🏗️ Architecture
src/desktop/
├── main.py                 # 🚪 Entry point
├── app/
│   ├── application.py      # 🎮 Main application (QApplication)
│   ├── main_window.py      # 🖼️ Main window with MenuBar
│   └── state_manager.py    # 📊 Global state management singleton
├── services/
│   ├── core_bridge.py      # 🌉 UI-Core bridge with threading
│   ├── audio_service.py    # 🎵 Asynchronous audio service
│   └── tts_service.py      # 🎤 TTS service with workers
├── windows/
│   ├── dashboard.py        # 📈 Main dashboard
│   ├── chat_window.py      # 💬 Chat window (coming soon)
│   └── settings_window.py  # ⚙️ Settings (coming soon)
├── components/
│   ├── audio_controls.py   # 🎛️ Audio controls
│   ├── video_widget.py     # 📺 Video/camera widget
│   └── status_bar.py       # 📊 Status bar
├── dialogs/
│   ├── login_dialog.py     # 🔑 Authentication dialog
│   └── error_dialog.py     # ⚠️ Error handling
└── resources/
    └── styles.qss          # 🎨 Qt stylesheets
🧬 Architectural Pattern
MVVM + Service Layer Pattern

Model: StateManager + Core modules

View: Dashboard, Windows, Dialogs

ViewModel: CoreBridge services

Service Layer: TTSService, AudioService, etc.

📦 Installation
📋 System Requirements
Python: 3.8 or higher

Operating System: Windows 10+, Linux, macOS 10.14+

RAM: Minimum 4GB (8GB Recommended)

Disk Space: ~500MB for dependencies

🚀 Automatic Installation
Bash

# 1. Clone the repository (if you haven't already)
git clone https://github.com/youruser/talkbridge.git
cd talkbridge

# 2. Run automatic setup
python setup_desktop.py --install

# 3. Verify installation
python setup_desktop.py --verify
🔧 Manual Installation
Bash

# 1. Install base dependencies
pip install -r requirements.txt

# 2. Install desktop dependencies
pip install -r requirements-desktop.txt

# 3. Verify PyQt6
python -c "from PyQt6.QtWidgets import QApplication; print('✓ PyQt6 OK')"

# 4. Create necessary directories
mkdir -p data/logs config/desktop src/desktop/resources/{icons,images}
🐛 Common Troubleshooting
<details>
<summary><b>Error: "PyQt6 could not be resolved"</b></summary>

Bash

# On Windows
pip uninstall PyQt6
pip install PyQt6==6.5.0

# On Linux (Ubuntu/Debian)
sudo apt-get install python3-pyqt6
pip install PyQt6

# On macOS
brew install pyqt@6
pip install PyQt6
</details>

<details>
<summary><b>Error: "Module 'src.tts.synthesizer' not found"</b></summary>

This is normal - the core modules are optional. The application will run in demo mode.

Bash

# To install the full core modules
pip install -r requirements.txt
</details>

🎮 Usage
🚀 Launching the Application
Bash

# Option 1: Launch script (Windows)
run_desktop.bat

# Option 2: Launch script (Linux/Mac)  
./run_desktop.sh

# Option 3: Direct execution
python src/desktop/main.py
🔑 First-Time Setup
Login: User: admin, Password: admin (demo mode)

Dashboard: Check the status of the services

Settings: Adjust preferences in the Tools menu

📈 Main Dashboard
The dashboard displays 6 service cards:

Service	Status	Description
🎤 TTS	🟢/🔴/🟡	AI-powered voice synthesis
🎵 Audio	🟢/🔴/🟡	Capture and processing
🌐 Translation	🟢/🔴/🟡	Multi-language engine
📹 Camera	🟢/🔴/🟡	Video capture
👤 Avatar	🟢/🔴/🟡	Facial animation
🤖 Ollama	🟢/🔴/🟡	LLM Processing
Color Codes:

🟢 Green: Connected and working

🟡 Yellow: Initializing or processing

🔴 Red: Error or disconnected

⚡ Quick Actions
New Chat: Start conversation (coming soon)

Settings: Adjust system preferences

Avatar: Configure facial animation (coming soon)

Statistics: View usage metrics (coming soon)

🛠️ Development
🏃‍♂️ Development Mode
Bash

# Install development dependencies
python setup_desktop.py --install --dev

# Run with detailed logging
python src/desktop/main.py --debug

# Run tests
pytest src/desktop/ -v

# Check types
mypy src/desktop/

# Format code
black src/desktop/
🧪 Testing
Bash

# Unit tests
pytest src/desktop/tests/ -v

# UI tests with pytest-qt
pytest src/desktop/tests/test_ui.py --qt-api=pyqt6

# Coverage
coverage run -m pytest
coverage report --include="src/desktop/*"
📝 Logging and Debugging
Log Files:

data/logs/desktop.log - Main log

data/logs/errors.log - Errors only

data/logs/app.log - General application log

Log Levels:

Python

# In config/config.yaml
logging:
  level: DEBUG  # DEBUG, INFO, WARNING, ERROR
  console: true
  file_rotation: daily
⚙️ Configuration
📄 Configuration Files
config/config.yaml - Main configuration

config/desktop/desktop.yaml - Desktop-specific

data/app_state.json - Persistent state

QSettings - User preferences

🎨 Theme Customization
YAML

# In config/desktop/desktop.yaml
desktop:
  theme:
    name: "dark"  # "dark" or "light"
    accent_color: "#0078d4"  # Default blue
    font_family: "Segoe UI"
    font_size: 10
Custom Colors:

CSS

/* In src/desktop/resources/styles.qss */
:root {
  --primary-bg: #2b2b2b;    /* Main background */
  --accent: #0078d4;        /* Accent color */
  --success: #16c60c;       /* Success green */
  --error: #d13438;         /* Error red */
  --warning: #ff8c00;       /* Warning orange */
}
🔧 Service Configuration
YAML

# Enable/disable services
services:
  tts: true
  audio: true  
  translation: false  # Disable translation
  ollama: true
  animation: false    # Disable animation
  camera: true

# Specific configuration
tts:
  voice: "default"
  speed: 1.0
  pitch: 1.0
  
audio:
  sample_rate: 44100
  channels: 1
  chunk_size: 1024
📁 File Structure
📂 Main Directories
talkbridge/
├── src/desktop/           # 🖥️ Desktop application
├── data/                  # 💾 Persistent data
│   ├── logs/             # 📋 Log files
│   ├── cache/            # 🗃️ Temporary cache
│   ├── temp/             # 📁 Temporary files
│   └── exports/          # 📤 Exports
├── config/               # ⚙️ Configurations
│   ├── config.yaml       # 📄 Main config
│   └── desktop/          # 🖥️ Desktop config
└── requirements-desktop.txt # 📦 Dependencies
🗂️ Modules by Functionality
Module	Purpose	Key Files
app/	Application Core	application.py, main_window.py, state_manager.py
services/	Backend services	core_bridge.py, tts_service.py, audio_service.py
windows/	Main windows	dashboard.py, chat_window.py, settings_window.py
components/	Reusable components	audio_controls.py, video_widget.py
dialogs/	Modal dialogs	login_dialog.py, error_dialog.py
resources/	Static resources	styles.qss, icons/, images/
🔌 API and Services
🌉 CoreBridge API
Python

# Use services from the UI
from src.desktop.services.core_bridge import CoreBridge

bridge = CoreBridge(state_manager)
bridge.initialize_all_services()

# Text synthesis
bridge.synthesize_text("Hello world", voice="en-US")

# Audio capture  
bridge.start_audio_recording()
audio_data = bridge.stop_audio_recording()

# Check status
status = bridge.get_service_status("tts")  # "connected", "error", etc.
📊 StateManager API
Python

# Configuration management
from src.desktop.app.state_manager import StateManager

state = StateManager()
state.initialize()

# Configuration
voice = state.get_config("tts.voice", "default")
state.set_config("tts.speed", 1.2)

# Service status
state.set_service_status("tts", "connected")
service_status = state.get_service_status("tts")

# User session
state.set_user_session("admin", is_authenticated=True)
session = state.get_user_session()
🎤 TTSService API
Python

# Asynchronous TTS Service
from src.desktop.services.core_bridge import TTSService

tts = TTSService(state_manager)

# Connect signals
tts.synthesis_completed.connect(on_synthesis_done)
tts.synthesis_failed.connect(on_synthesis_error)

# Synthesize
success = tts.synthesize_async(
    "Text to be synthesized",
    output_path="output.wav",
    voice_settings={"voice": "en-US", "speed": 1.0}
)
🤝 Contributing
🐛 Reporting Issues
Check that the issue does not already exist

Include system information:

OS and version

Python and PyQt6 version

Relevant logs

Describe the steps to reproduce

🔧 Pull Requests
Fork the repository

Create a branch for your feature: git checkout -b feature/new-feature

Commit your changes: git commit -m 'Add new feature'

Push to your branch: git push origin feature/new-feature

Open a Pull Request

📝 Code Conventions
PEP 8 for Python style

Type hints in all functions

Google-style docstrings

Commit messages in Spanish with the format: type: description

Python

def synthesize_voice(text: str, output_path: Optional[str] = None) -> bytes:
    '''
    Synthesizes text to speech using the TTS engine.
    
    Args:
        text: Text to be synthesized
        output_path: Optional output path
        
    Returns:
        bytes: Generated audio data
        
    Raises:
        TTSError: If synthesis fails
    '''
    pass
📄 License
This project is licensed under the MIT License. See LICENSE for more details.

🆘 Support
Documentation: docs/

Issues: GitHub Issues

Discussions: GitHub Discussions

Email: support@talkbridge.com

<div align="center">

🚀 TalkBridge Desktop - AI-Powered Voice Translation 🤖

</div>