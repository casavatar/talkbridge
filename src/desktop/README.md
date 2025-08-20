# TalkBridge Desktop Application

> 🚀 **Modern desktop interface for TalkBridge** - Real-time voice translation platform powered by artificial intelligence.

![TalkBridge Desktop](https://img.shields.io/badge/PyQt6-Desktop%20App-blue?style=flat-square) ![Python](https://img.shields.io/badge/Python-3.8%2B-green?style=flat-square) ![Status](https://img.shields.io/badge/Status-In%20Development-orange?style=flat-square)

## 📋 Table of Contents

- [Main Features](#main-features)
- [Architecture](#architecture)
- [Installation](#installation)
- [Usage](#usage)
- [Development](#development)
- [Configuration](#configuration)
- [File Structure](#file-structure)
- [API and Services](#api-and-services)
- [Contributing](#contributing)

## 🎯 Main Features

### ✨ Modern Interface
- **Dark Theme design** with customizable colors
- **Interactive cards** for service status
- **Centralized dashboard** with real-time information
- **Responsive design** adaptable to different resolutions

### 🔧 Integrated Services
- 🎤 **Text-to-Speech (TTS)** with Coqui TTS
- 🎵 **Real-time Audio Capture**
- 🌐 **Multi-language Translation**
- 📹 **Facial Detection** and synchronized animation
- 🤖 **LLM Processing** with Ollama
- 👤 **Animated Avatar** with MediaPipe

### 🛡️ Advanced Features
- **Secure authentication** with session management
- **Persistent state** with auto-save
- **Asynchronous threading** for heavy operations
- **Robust error handling** with detailed logging
- **Centralized configuration** via YAML

## 🏗️ Architecture

```
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
    └── styles.qss          # 🎨 Qt style sheets
```

### 🧬 Architecture Pattern

**MVVM + Service Layer Pattern**
- **Model**: StateManager + Core modules
- **View**: Dashboard, Windows, Dialogs  
- **ViewModel**: CoreBridge services
- **Service Layer**: TTSService, AudioService, etc.

## 📦 Installation

### 📋 System Requirements

- **Python**: 3.8 or higher
- **Operating System**: Windows 10+, Linux, macOS 10.14+
- **RAM**: Minimum 4GB (Recommended 8GB)
- **Space**: ~500MB for dependencies (pip) / ~1.5GB for dependencies (conda)

### 🚀 Recommended: Conda Installation

**Why Conda?** Better dependency management, optimized PyQt6, pre-compiled packages, and GPU support.

```bash
# Quick start
python config/setup_conda_desktop.py

# Or use convenience scripts
# Windows:
start_desktop.bat

# Linux/macOS:
./start_desktop.sh
```

### 🔧 Alternative: pip Installation

```bash
# 1. Install base dependencies
pip install -r requirements.txt

# 2. Install desktop dependencies
pip install -r requirements-desktop.txt

# 3. Verify PyQt6
python -c "from PyQt6.QtWidgets import QApplication; print('✓ PyQt6 OK')"

# 4. Create necessary directories
mkdir -p data/logs config/desktop src/desktop/resources/{icons,images}
```

### 📊 Installation Comparison

| Feature | pip | Conda | Winner |
|---------|-----|-------|--------|
| **PyQt6 Stability** | ⚠️ May have issues | ✅ Rock solid | Conda |
| **Installation Speed** | 15-30 min | 5-10 min | Conda |
| **GPU Support** | Manual setup | Auto-configured | Conda |
| **Disk Space** | ~500MB | ~1.5GB | pip |
| **Scientific Libraries** | Slower | Pre-compiled | Conda |

### 🐛 Common Troubleshooting

<details>
<summary><b>Error: "PyQt6 could not be resolved"</b></summary>

```bash
# En Windows
pip uninstall PyQt6
pip install PyQt6==6.5.0

# En Linux (Ubuntu/Debian)
sudo apt-get install python3-pyqt6
pip install PyQt6

# En macOS
brew install pyqt@6
pip install PyQt6
```
</details>

<details>
<summary><b>Error: "Module 'src.tts.synthesizer' not found"</b></summary>

This is normal - core modules are optional. The application will run in demo mode.

```bash
# To install full core modules
pip install -r requirements.txt
```
</details>

## 🎮 Usage

### 🚀 Start the Application

```bash
# Option 1: Launch script (Windows)
run_desktop.bat

# Option 2: Launch script (Linux/Mac)  
./run_desktop.sh

# Option 3: Direct execution
python src/desktop/main.py
```

### 🔑 First Setup

1. **Login**: User: `admin`, Password: `admin` (demo mode)
2. **Dashboard**: Check service status
3. **Settings**: Adjust preferences in the Tools menu

### 📈 Main Dashboard

The dashboard shows **6 service cards**:

| Service | Status | Description |
|---------|--------|-------------|
| 🎤 **TTS** | 🟢/🔴/🟡 | AI voice synthesis |
| 🎵 **Audio** | 🟢/🔴/🟡 | Capture and processing |
| 🌐 **Translation** | 🟢/🔴/🟡 | Multi-language engine |
| 📹 **Camera** | 🟢/🔴/🟡 | Video capture |
| 👤 **Avatar** | 🟢/🔴/🟡 | Facial animation |
| 🤖 **Ollama** | 🟢/🔴/🟡 | LLM processing |

**Color Codes:**
- 🟢 **Green**: Connected and working
- 🟡 **Yellow**: Initializing or processing  
- 🔴 **Red**: Error or disconnected

### ⚡ Quick Actions

- **New Chat**: Start conversation (coming soon)
- **Settings**: Adjust system preferences
- **Avatar**: Configure facial animation (coming soon)
- **Statistics**: View usage metrics (coming soon)

## 🛠️ Development

### 🏃‍♂️ Development Mode

```bash
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
```

### 🧪 Testing

```bash
# Unit tests
pytest src/desktop/tests/ -v

# UI tests with pytest-qt
pytest src/desktop/tests/test_ui.py --qt-api=pyqt6

# Coverage
coverage run -m pytest
coverage report --include="src/desktop/*"
```

### 📝 Logging and Debugging

**Log Files:**
- `data/logs/desktop.log` - Main log
- `data/logs/errors.log` - Errors only
- `data/logs/app.log` - General application log

**Log Levels:**
```python
# In config/config.yaml
logging:
  level: DEBUG  # DEBUG, INFO, WARNING, ERROR
  console: true
  file_rotation: daily
```

## ⚙️ Configuration

### 📄 Configuration Files

1. **`config/config.yaml`** - Main configuration
2. **`config/desktop/desktop.yaml`** - Desktop-specific
3. **`data/app_state.json`** - Persistent state
4. **QSettings** - User preferences

### 🎨 Theme Customization

```yaml
# In config/desktop/desktop.yaml
desktop:
  theme:
    name: "dark"  # "dark" or "light"
    accent_color: "#0078d4"  # Default blue
    font_family: "Segoe UI"
    font_size: 10
```

**Custom Colors:**
```css
/* In src/desktop/resources/styles.qss */
:root {
  --primary-bg: #2b2b2b;    /* Main background */
  --accent: #0078d4;        /* Accent color */
  --success: #16c60c;       /* Success green */
  --error: #d13438;         /* Error red */
  --warning: #ff8c00;       /* Warning orange */
}
```

### 🔧 Service Configuration

```yaml
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
```

## 📁 File Structure

### 📂 Main Directories

```
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
```

### 🗂️ Modules by Functionality

| Module | Purpose | Key Files |
|--------|---------|-----------|
| **app/** | Application core | `application.py`, `main_window.py`, `state_manager.py` |
| **services/** | Backend services | `core_bridge.py`, `tts_service.py`, `audio_service.py` |
| **windows/** | Main windows | `dashboard.py`, `chat_window.py`, `settings_window.py` |
| **components/** | Reusable components | `audio_controls.py`, `video_widget.py` |
| **dialogs/** | Modal dialogs | `login_dialog.py`, `error_dialog.py` |
| **resources/** | Static resources | `styles.qss`, `icons/`, `images/` |

## 🔌 API and Services

### 🌉 CoreBridge API

```python
# Use services from UI
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
```

### 📊 StateManager API

```python
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
```

### 🎤 TTSService API

```python
# Asynchronous TTS service
from src.desktop.services.core_bridge import TTSService

tts = TTSService(state_manager)

# Connect signals
tts.synthesis_completed.connect(on_synthesis_done)
tts.synthesis_failed.connect(on_synthesis_error)

# Synthesize
success = tts.synthesize_async(
    "Text to synthesize",
    output_path="output.wav",
    voice_settings={"voice": "en-US", "speed": 1.0}
)
```

## 🤝 Contributing

### 🐛 Report Issues

1. **Check** that the issue does not already exist
2. **Include** system information:
   - OS and version
   - Python and PyQt6 version
   - Relevant logs
3. **Describe** steps to reproduce

### 🔧 Pull Requests

1. **Fork** the repository
2. **Create** a branch for your feature: `git checkout -b feature/new-feature`
3. **Commit** changes: `git commit -m 'Add new feature'`
4. **Push** to your branch: `git push origin feature/new-feature`
5. **Open** a Pull Request

### 📝 Code Conventions

- **PEP 8** for Python style
- **Type hints** in all functions
- **Google-style docstrings**
- **Commits** in English with format: `type: description`

```python
def synthesize_voice(text: str, output_path: Optional[str] = None) -> bytes:
    """
    Synthesizes text to voice using the TTS engine.
    
    Args:
        text: Text to synthesize
        output_path: Optional output path
        
    Returns:
        bytes: Generated audio data
        
    Raises:
        TTSError: If synthesis fails
    """
    pass
```

## 📄 License

This project is under the MIT license. See `LICENSE` for details.

---

## 🆘 Support

- **Documentation**: [docs/](docs/)
- **Issues**: [GitHub Issues](https://github.com/casavatar/talkbridge/issues)
- **Discussions**: [GitHub Discussions](https://github.com/casavatar/talkbridge/discussions)
- **Email**: support@talkbridge.com

---

<div align="center">

**🚀 TalkBridge Desktop - Voice Translation Powered by AI 🤖**

[![GitHub stars](https://img.shields.io/github/stars/casavatar/talkbridge?style=social)](https://github.com/casavatar/talkbridge)
[![Follow](https://img.shields.io/github/followers/casavatar?style=social)](https://github.com/casavatar)

</div>
