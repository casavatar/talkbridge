# 🎤 TalkBridge

**Advanced real-time voice translation and communication platform with AI-powered speech synthesis, facial animation, and multi-interface support.**

[![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)](https://python.org)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)
[![Platform](https://img.shields.io/badge/Platform-Windows%20%7C%20macOS%20%7C%20Linux-lightgrey.svg)](https://github.com/casavatar/talkbridge)
[![GUI](https://img.shields.io/badge/GUI-CustomTkinter-orange.svg)](https://github.com/TomSchimansky/CustomTkinter)

## 🌟 Features

### 🗣️ **Text-to-Speech Module Features**

```bash
# Enable debug logging
export TALKBRIDGE_DEBUG=1
python src/desktop/main.py

# Check logs
tail -f data/logs/app.log
tail -f data/logs/desktop.log
tail -f data/logs/errors.log
```

## 🔍 Troubleshooting

### Common Issues and Solutions

#### 🎤 Audio Issues

**Problem**: No audio input/output detected

```bash
# Check audio devices
python -c "import pyaudio; pa = pyaudio.PyAudio(); [print(f'{i}: {pa.get_device_info_by_index(i)[\"name\"]}') for i in range(pa.get_device_count())]"
```

**Solution**: Update device ID in config.yaml

```yaml
audio:
  input_device: 1  # Replace with correct device ID
  output_device: 2
```

**Problem**: Poor audio quality

```yaml
# Increase audio quality in config.yaml
audio:
  sample_rate: 44100  # Higher sample rate
  chunk_size: 512     # Smaller chunks for lower latency
  channels: 2         # Stereo for better quality
```

#### 🖥️ Desktop Application Issues

**Problem**: PyQt6/PySide6 import errors

```bash
# Reinstall with conda (recommended)
conda install pyside6 pyqt6

# Or with pip
pip install PySide6 PyQt6
```

**Problem**: Application crashes on startup

```bash
# Check for missing dependencies
python config/error_diagnostic.py

# Run post-install fixes
python config/post_install_fix.py
```

**Problem**: Wayland display issues (Linux)

```bash
# Check if running on Wayland
echo $WAYLAND_DISPLAY
echo $XDG_SESSION_TYPE

# TalkBridge automatically detects and fixes Wayland issues, but if problems persist:

# Force X11 mode (temporary)
export GDK_BACKEND=x11
export QT_QPA_PLATFORM=xcb
python src/desktop/main.py

# Check environment info
python -c "
from src.desktop.ui.ui_utils import get_ui_environment_info
import json
print(json.dumps(get_ui_environment_info(), indent=2))
"
```

**Wayland-specific symptoms**:

- Blurry or pixelated text in the desktop application
- UI elements appearing at wrong sizes
- Window positioning problems
- Font rendering issues

**Note**: TalkBridge automatically applies Wayland fixes at startup. No manual configuration required.

#### 🌐 Web Interface Module Module

**Problem**: Streamlit won't start

```bash
# Check port availability
netstat -an | grep 8501

# Use different port
streamlit run src/ui/main_app.py --server.port 8502
```

**Problem**: File upload issues

```yaml
# Increase upload limits in config.yaml
web:
  max_upload_size: 500  # MB
  max_file_size: 100    # MB per file
```

#### 🤖 AI Model Issues

**Problem**: Ollama connection failed

```bash
# Check Ollama status
curl http://localhost:11434/api/tags

# Start Ollama service
ollama serve

# Pull required model
ollama pull llama2
```

**Problem**: Whisper model loading issues

```bash
# Download Whisper models manually
python -c "import whisper; whisper.load_model('base')"

# Use smaller model for testing
python -c "import whisper; whisper.load_model('tiny')"
```

#### 🎭 Animation Issues

**Problem**: Camera not detected

```python
# Test camera access
import cv2
cap = cv2.VideoCapture(0)
print(f"Camera available: {cap.isOpened()}")
cap.release()
```

**Problem**: Poor facial tracking

```yaml
# Adjust tracking settings in config.yaml
animation:
  facial_tracking:
    confidence_threshold: 0.3  # Lower for better detection
    smoothing_factor: 0.8      # Higher for smoother animation
```

### Performance Optimization

#### 🚀 Desktop Performance

```yaml
# Optimize desktop settings
desktop:
  update_interval: 50     # Faster UI updates
  auto_save_interval: 30  # Less frequent saves
  max_history: 100        # Limit conversation history
```

#### 🌐 Web Performance

```yaml
# Optimize web settings
web:
  cache_size: 100         # MB
  session_cleanup: 300    # seconds
  max_concurrent: 10      # users
```

### Log Analysis

**Check specific logs for issues:**

```bash
# Application errors
grep "ERROR" data/logs/app.log

# Desktop-specific issues
grep "CRITICAL" data/logs/desktop.log

# Translation problems
grep "translation" data/logs/errors.log

# Audio processing issues
grep "audio" data/logs/app.log
```

### Getting Help

1. **Check Documentation**: Review `/doc/` folder for detailed guides
2. **Run Diagnostics**: Use `python config/error_diagnostic.py`
3. **Enable Debug Mode**: Set `TALKBRIDGE_DEBUG=1`
4. **Check Dependencies**: Run `pip check` or `conda list`
5. **Update Components**: Ensure all dependencies are current

## � Feature Details

### 🗣️ **Text-to-Speech Features**

- **Voice Cloning**: Clone user's voice from minimal audio samples (3-10 seconds)
- **Multi-speaker Support**: Support for multiple voice profiles and switching
- **Offline Processing**: Complete offline functionality on Windows, macOS, and Linux
- **Coqui TTS Integration**: Uses YourTTS model for high-quality multilingual voice cloning
- **Real-time Synthesis**: Low latency for live communication with streaming support
- **Multiple Languages**: Support for 50+ languages and accents
- **SSML Support**: Advanced speech control with Speech Synthesis Markup Language

### 🎭 **Enhanced Facial Animation**

- **Advanced Lip Sync**: Synchronize mouth movements with speech audio using MediaPipe
- **Real-time Tracking**: Facial landmark detection with emotion recognition
- **Eye Blinking**: Natural eye movement animations with timing control
- **Webcam Integration**: Live webcam feed processing with device management
- **Avatar Support**: Static and animated avatar options with customization
- **Interactive Controls**: Real-time animation parameter adjustment
- **Emotion Detection**: Facial expression analysis and animation

### 🖥️ **Multi-Interface Support**

- **Desktop Application**: Modern PySide6-based GUI with tabbed interface
- **Web Interface**: Responsive Streamlit dashboard with real-time updates
- **CLI Access**: Command-line interface for automation and scripting
- **API Integration**: RESTful API for third-party integration
- **Cross-platform**: Windows, macOS, and Linux support with automatic Wayland optimization

### 🤖 **AI Integration**

- **Local LLM Support**: Ollama integration with streaming responses
- **Conversation Management**: Persistent chat history with search and export
- **Model Management**: Dynamic model loading and performance monitoring
- **Streaming Responses**: Real-time AI response generation
- **Context Awareness**: Intelligent conversation context management

### 🔐 **Enhanced Security & Authentication**

- **Multi-layer Security**: Enhanced SHA-256 salted password hashing
- **Role-based Access**: Multiple user roles (admin, user, guest) with granular permissions
- **Account Protection**: Brute force protection and account locking mechanisms
- **Session Management**: Configurable session timeouts and security monitoring
- **Audit Trail**: Comprehensive login tracking and security logging
- **Privacy-first**: Local processing ensures data privacy

### 🎵 **Advanced Audio Processing**

- **Real-time Processing**: Low-latency audio capture and playback
- **Audio Effects**: Noise reduction, echo cancellation, and enhancement
- **Multi-device Support**: Automatic device detection and selection
- **Format Support**: Multiple audio formats with automatic conversion
- **Streaming Audio**: Real-time audio streaming and processing

### 🛠️ **Platform Optimizations**

- **Wayland Support**: Automatic detection and fixes for Linux Wayland display server
- **Display Scaling**: Intelligent scaling adjustments for high-DPI displays
- **Font Rendering**: Enhanced text clarity across different display systems
- **Cross-Platform UI**: Consistent user experience across Windows, macOS, and Linux
- **Environment Detection**: Comprehensive OS and display server detection with automatic optimization

## 📁 Project Structure

```text
talkbridge/
├── 🔧 config/
│   ├── config.yaml              # Main configuration file
│   ├── environment-*.yaml       # Environment-specific configurations
│   └── setup_conda_*.py         # Conda environment setup scripts
├── 📊 data/
│   ├── app_state.json          # Application state persistence
│   └── logs/                   # Comprehensive logging system
├── 💻 src/                     # Main source code (flattened structure)
│   ├── 🎯 Core Application
│   │   ├── app.py              # Main CLI application entry point
│   │   ├── config.py           # Global configuration management
│   │   ├── errors.py           # Centralized error handling
│   │   └── logging_config.py   # Centralized logging system
│   │
│   ├── 🎵 Audio Processing
│   │   ├── audio/              # Audio capture, playback, and effects
│   │   │   ├── capture.py      # Real-time audio capture
│   │   │   ├── player.py       # Advanced audio playbook
│   │   │   ├── effects.py      # Audio processing effects
│   │   │   ├── generator.py    # Audio generation utilities
│   │   │   └── synthesizer.py  # Audio synthesis helpers
│   │   │
│   │   └── stt/                # Speech-to-text processing
│   │       ├── whisper_engine.py # Whisper model integration
│   │       ├── interface.py    # Main transcription API
│   │       ├── audio_utils.py  # Audio preprocessing
│   │       └── config.py       # STT configuration
│   │
│   ├── 🤖 AI Integration
│   │   ├── ollama/             # LLM integration and conversation
│   │   │   ├── ollama_client.py      # Enhanced Ollama API client
│   │   │   ├── conversation_manager.py # Conversation management
│   │   │   ├── model_manager.py      # Model management system
│   │   │   ├── prompt_engineer.py    # Prompt optimization
│   │   │   └── streaming_client.py   # Real-time streaming
│   │   │
│   │   ├── translation/        # Multi-language translation
│   │   │   ├── translator.py   # Main translation interface
│   │   │   ├── offline_translator.py # Offline translation
│   │   │   └── language_detector.py  # Language detection
│   │   │
│   │   └── tts/                # Text-to-speech and voice cloning
│   │       ├── voice_cloner.py # Advanced voice cloning (Coqui TTS)
│   │       ├── synthesizer.py  # Main TTS interface
│   │       └── config.py       # TTS configuration management
│   │
│   ├── 🎭 Animation & Video
│   │   └── animation/          # Avatar animation and facial sync
│   │       ├── face_sync.py    # Facial animation with MediaPipe
│   │       ├── audio_visualizer.py # Real-time audio visualization
│   │       ├── interactive_animations.py # Interactive controls
│   │       ├── camera_manager.py # Webcam integration
│   │       └── loading_animation.py # UI animations
│   │
│   ├── 🖥️ Desktop Application
│   │   └── desktop/            # CustomTkinter-based desktop GUI
│   │       ├── main.py         # Desktop app entry point
│   │       ├── app/            # Application core
│   │       │   ├── application.py    # Main application class
│   │       │   ├── main_window.py    # Main window with tabs
│   │       │   └── state_manager.py  # Application state
│   │       ├── components/     # UI components
│   │       │   ├── chat_tab.py       # Conversation interface
│   │       │   ├── avatar_tab.py     # Avatar display and controls
│   │       │   └── settings_tab.py   # Configuration interface
│   │       ├── dialogs/        # Modal dialogs
│   │       │   └── login_dialog.py   # Authentication dialog
│   │       ├── services/       # Backend integration
│   │       │   └── core_bridge.py    # Service coordinator
│   │       ├── ui/             # Platform utilities
│   │       │   ├── ui_utils.py       # Wayland fixes and platform utilities
│   │       │   └── theme.py          # Unified design system
│   │       └── windows/        # Additional windows
│   │           └── dashboard.py      # Service status dashboard
│   │
│   ├── 🌐 Web Application
│   │   └── web/                # Flask/Streamlit-based web interface
│   │       ├── interface.py    # Main web application
│   │       ├── server.py       # Enhanced web server
│   │       ├── components/     # Web UI components
│   │       │   ├── dashboard.py      # Main dashboard
│   │       │   └── login.py          # Web authentication
│   │       └── api/            # API wrappers
│   │           ├── llm_api.py        # LLM integration
│   │           ├── tts_api.py        # TTS integration
│   │           ├── stt_api.py        # STT integration
│   │           ├── translation_api.py # Translation integration
│   │           └── animation_api.py  # Animation integration
│   │
│   ├── 🔐 Authentication & Security
│   │   └── auth/               # Authentication system
│   │       ├── auth_manager.py # Enhanced security management
│   │       ├── user_store.py   # User database management
│   │       └── utils/          # Authentication utilities
│   │           ├── password_config.py    # Password configuration
│   │           ├── user_generator.py     # User generation
│   │           └── encryption_verifier.py # Encryption verification
│   │
│   ├── 🛠️ Utilities
│   │   ├── ui/                 # UI utilities and components
│   │   │   └── notifier.py     # Cross-platform notifications
│   │   └── utils/              # Shared utilities and helpers
│   │       ├── error_handler.py      # Centralized error handling
│   │       ├── config_validator.py   # Configuration validation
│   │       ├── project_root.py       # Project path utilities
│   │       └── error_suppression.py  # System optimization
│   │
│   └── 🎪 Demo System
│       └── demo/               # Comprehensive demo and testing
│           ├── demo_runner.py  # Demo simulation engine
│           ├── demo_api.py     # Demo API wrappers
│           ├── demo_config.py  # Demo configuration
│           ├── *_demo.py       # Individual module demos
│           └── run_demo.py     # Demo launcher
│
├── 🧪 test/                    # Comprehensive test suite
│   ├── test_*.py              # Module-specific tests
│   └── integration/           # Integration tests
│
├── 📚 doc/                     # Documentation
│   ├── architecture.md        # System architecture
│   ├── modules_overview.md    # Module documentation
│   └── project_overview.md    # Project overview
│
├── 📋 requirements*.txt        # Dependencies
├── 🚀 launch_desktop.sh       # Desktop app launcher
├── 🐳 Dockerfile             # Container deployment
└── 📄 README.md               # This file
```

│   ├── animation/               # Facial animation module
│   │   ├── face_sync.py         # Real-time facial animation
│   │   ├── audio_visualizer.py  # Audio visualization
│   │   ├── interactive_animations.py
│   │   ├── loading_animation.py
│   │   └── README.md            # Animation documentation
│   ├── ui/                      # Web interface
│   │   ├── web_interface.py     # Main Streamlit app
│   │   ├── run_web_interface.py # App runner
│   │   ├── components/          # UI components
│   │   │   ├── login.py         # Login interface
│   │   │   ├── dashboard.py     # Main dashboard
│   │   │   ├── audio_recorder.py # Audio recording
│   │   │   ├── chat_interface.py # Chat functionality
│   │   │   └── avatar_display.py # Avatar controls
│   │   ├── api/                 # API interfaces
│   │   │   ├── tts_api.py       # TTS API wrapper
│   │   │   ├── stt_api.py       # Speech-to-text API
│   │   │   ├── llm_api.py       # Language model API
│   │   │   ├── translation_api.py # Translation API
│   │   │   └── animation_api.py # Animation API
│   │   └── assets/              # Static assets
│   │       └── style.css        # Custom styling
│   ├── json/                    # User data
│   │   ├── users.json           # User database
│   │   ├── generate_secure_users.py # Password generator
│   │   └── README.md            # User system docs
│   ├── auth/                    # Authentication system
│   │   └── auth_manager.py      # User management
│   ├── audio/                   # Audio processing
│   │   ├── capture.py           # Audio capture
│   │   ├── effects.py           # Audio effects
│   │   ├── generator.py         # Audio generation
│   │   ├── player.py            # Audio playback
│   │   ├── synthesizer.py       # Audio synthesis
│   │   └── README.md            # Audio documentation
│   ├── ollama/                  # LLM integration
│   │   ├── conversation_manager.py # Chat management
│   │   ├── model_manager.py     # Model management
│   │   ├── ollama_client.py     # Ollama client
│   │   ├── prompt_engineer.py   # Prompt engineering
│   │   ├── streaming_client.py  # Streaming support
│   │   └── README.md            # Ollama documentation
│   ├── translation/             # Translation module
│   │   ├── translator.py        # Translation engine
│   │   ├── offline_translator.py # Offline translation
│   │   └── README.md            # Translation docs
│   └── utils/                   # Utility functions
├── test/                        # Test files
├── requirements.txt              # Python dependencies
└── README.md                    # This file

```text

## 🚀 Quick Start

### Prerequisites

- **Python 3.8+**
- **Windows 10+ or macOS 10.14+**
- **Webcam** (for facial animation)
- **Microphone** (for voice input)

### Installation Options

TalkBridge supports two installation methods to best suit your needs:

#### 🐍 **Option 1: Traditional pip Installation (Web Interface)**
Best for web-based usage and development:

1. **Clone the repository**

   ```bash

   git clone https://github.com/casavatar/talkbridge.git
   cd talkbridge

   ```

1. **Install dependencies**

   ```bash

   pip install -r requirements.txt

   ```

1. **Run the web interface**

   ```bash

   cd src/web
   python run_web_interface.py

   ```

1. **Access the application**: `http://localhost:8501`

### 🐳 **Option 2: Conda Installation (Desktop Application) - RECOMMENDED**

Best for desktop GUI application with optimized dependencies:

1. **Clone the repository**

   ```bash

   git clone https://github.com/casavatar/talkbridge.git
   cd talkbridge

   ```

1. **Quick setup with launch scripts**

   ```bash

   # Windows PowerShell

   .\launch_desktop.ps1

   # Linux/macOS Bash

   ./launch_desktop.sh

   ```

1. **Or manual conda setup**

   ```bash

   # Desktop environment (CustomTkinter, PyTorch CPU)

   python config/setup_conda_desktop.py

   # Or web environment (Flask, Streamlit, lightweight)

   python config/setup_conda_web.py

   ```

1. **Run the applications**

   ```bash

   # Desktop application

   conda activate talkbridge-desktop
   export PYTHONPATH=src  # Linux/macOS

   # $env:PYTHONPATH="src"  # Windows PowerShell

   python -m desktop.main

   # Web application

   conda activate talkbridge-web
   export PYTHONPATH=src
   python -m web.interface

   ```

## 📚 Usage Examples

### 🖥️ Desktop Application

The desktop interface provides a complete GUI experience:

```python

# Start the desktop application

python src/desktop/main.py

# Features available in desktop mode:

# - Real-time voice translation

# - Facial animation sync

# - Voice cloning

# - Conversation history

# - Multiple language pairs

# - Advanced audio controls

```

**Key Features:**

- **Live Translation**: Speak in one language, hear it in another
- **Voice Cloning**: Train custom voices for more natural output
- **Facial Animation**: Real-time lip-sync for avatars
- **Chat Integration**: LLM-powered conversations with translation

### 🌐 Web Interface

The Streamlit web interface offers browser-based access:

```python

# Start the web interface

cd src/ui
python run_web_interface.py

# Or using streamlit directly:

streamlit run main_app.py --server.port 8501

```

**Features:**

- **Multi-tab Interface**: Organized workflow
- **Device Management**: Audio device selection
- **Real-time Processing**: Live audio translation
- **Export Options**: Save conversations and audio

### 🎯 API Usage

Integrate TalkBridge components into your applications:

```python

# Set up Python path for imports

import sys
sys.path.insert(0, 'src')

# Translation API

from translation.translator import Translator
translator = Translator()
result = translator.translate("Hello world", "en", "es")

# Text-to-Speech API

from tts.voice_cloner import VoiceCloner
tts = VoiceCloner()
audio = tts.synthesize_voice("Hello world", output_path="output.wav")

# Speech-to-Text API

from stt.whisper_engine import WhisperEngine
stt = WhisperEngine()
text = stt.transcribe("audio_file.wav")

# LLM Integration

from ollama.ollama_client import OllamaClient
llm = OllamaClient()
response = llm.generate("Translate this to Spanish: Hello world")

```

### 🎮 Demo System

Explore features with the built-in demo system:

```bash

# Run interactive demos

python src/demo/run_demo.py

# Specific demo examples:

python src/demo/translation_demo.py    # Translation demo
python src/demo/tts_demo.py           # Text-to-speech demo
python src/demo/face_sync_demo.py     # Facial animation demo
python src/demo/ollama_demo.py        # LLM integration demo

```

#### 🎯 **Which option should you choose?**

| Feature | pip Installation | Conda Installation |
|---------|------------------|-------------------|
| **Web Interface** | ✅ Primary focus | ✅ Compatible |
| **Desktop GUI** | ⚠️ Basic support | ✅ **Optimized** |
| **PyQt6 Stability** | ⚠️ May have issues | ✅ **Rock solid** |
| **GPU Support** | ⚠️ Manual setup | ✅ **Auto-configured** |
| **Scientific Libraries** | ⚠️ Slower install | ✅ **Pre-compiled** |
| **Dependency Conflicts** | ⚠️ Possible | ✅ **Isolated** |
| **Installation Speed** | ⚠️ Can be slow | ✅ **Faster** |

**Recommendation**: Use **conda** for desktop application development and production use.

## ⚙️ Configuration

### 📝 Basic Configuration

TalkBridge uses a YAML configuration file located at `config/config.yaml`:

```yaml

# Audio Settings

audio:
  input_device: "default"
  output_device: "default"
  sample_rate: 16000
  channels: 1
  chunk_size: 1024

# Translation Settings

translation:
  default_source: "auto"
  default_target: "en"
  cache_enabled: true

# TTS Settings

tts:
  default_voice: "speaker_01"
  speed: 1.0
  quality: "high"

# Animation Settings

animation:
  face_detection: true
  smoothing_factor: 0.7
  fps: 30

# LLM Settings

ollama:
  base_url: "http://localhost:11434"
  default_model: "llama2"
  temperature: 0.7

```

### 🔧 Advanced Configuration

**Desktop Application Settings:**

```yaml

desktop:
  theme: "dark"
  window_size: [1200, 800]
  auto_save: true
  update_interval: 100

```

**Web Interface Settings:**

```yaml

web:
  port: 8501
  host: "localhost"
  max_upload_size: 200
  session_timeout: 3600

```

### 🔒 Security Configuration

Configure user authentication and access control:

```python

# Generate secure user credentials

python src/json/generate_secure_users.py

# Configure authentication in config.yaml

auth:
  enabled: true
  password_policy:
    min_length: 8
    require_special: true
  session_duration: 3600

```

## 🛠️ Development Guide

### 📁 Project Structure for Developers

```text

talkbridge/
├── src/
│   ├── desktop/           # PySide6 desktop application
│   │   ├── main.py        # Desktop entry point
│   │   ├── app/           # Core application logic
│   │   ├── components/    # Reusable UI components
│   │   ├── dialogs/       # Dialog windows
│   │   └── windows/       # Main application windows
│   ├── ui/                # Streamlit web interface
│   │   ├── main_app.py    # Web entry point
│   │   ├── pages/         # Multi-page interface
│   │   └── components/    # Streamlit components
│   ├── animation/         # Facial animation system
│   ├── audio/             # Audio processing
│   ├── ollama/            # LLM integration
│   ├── tts/               # Text-to-speech
│   ├── stt/               # Speech-to-text
│   └── translation/       # Translation engine
├── config/                # Configuration files
├── test/                  # Unit tests
└── doc/                   # Documentation

```

### 🧪 Running Tests

```bash

# Run all tests

python -m pytest test/

# Run specific test modules

python -m pytest test/test_tts.py
python -m pytest test/test_stt_module.py
python -m pytest test/test_translate.py

# Run with coverage

python -m pytest --cov=src test/

```

### 🐛 Debugging

Enable debug mode for development:

```bash

# Enable debug logging

export TALKBRIDGE_DEBUG=1
python src/desktop/main.py

# Check logs

tail -f data/logs/app.log
tail -f data/logs/desktop.log
tail -f data/logs/errors.log

```

## 🔧 Configuration

### TTS Configuration

```yaml

# config/config.yaml

tts:
  default_model: "tts_models/multilingual/multi-dataset/your_tts"
  sample_rate: 22050
  voice_cloning:
    min_sample_duration: 3.0
    max_sample_duration: 10.0
  performance:
    use_gpu: true
    batch_size: 4

```

### Animation Configuration

```yaml

animation:
  webcam:
    device_id: 0
    resolution: [640, 480]
    fps: 30
  facial_tracking:
    confidence_threshold: 0.5
    landmark_count: 468
  audio_sync:
    energy_threshold: 0.01
    blink_threshold: 0.2

```

### Security Configuration

```yaml

security:
  max_failed_attempts: 5
  session_timeout: 1800
  password_min_length: 8
  require_password_change: true

```

## 🎯 Core Modules

### 🗣️ TTS Module

**File**: `src/tts/`

**Features**:

- Voice cloning from audio samples
- Real-time speech synthesis
- Multi-language support
- Offline processing
- Low latency optimization

**Usage**:

```python

from tts import synthesize_voice, setup_voice_cloning

# Setup voice cloning

setup_voice_cloning("path/to/voice/samples")

# Synthesize speech

audio_data = synthesize_voice("Hello, world!", output_path="output.wav")

```

### 🎭 Animation Module

**File**: `src/animation/`

**Features**:

- Real-time facial landmark detection
- Lip synchronization with audio
- Eye blinking animations
- Webcam integration
- Avatar support

**Usage**:

```python

from animation import FaceSync

# Initialize face sync

face_sync = FaceSync(use_webcam=True)

# Run facial animation with audio

face_sync.run_face_sync("audio_file.wav")

```

### 🌐 Web Interface Module

**File**: `src/ui/`

**Features**:

- Streamlit-based dashboard
- Secure authentication
- Real-time chat interface
- Audio recording and playback
- Avatar display and controls

**Usage**:

```bash

cd src/ui
python run_web_interface.py

```

## 🔐 Security Features

### User Management

- **10 User Roles**: Admin, User, Moderator, Translator, Developer, Analyst, Support, Guest, Test, Demo
- **Enhanced Security**: Salted password hashing with SHA-256
- **Account Protection**: Brute force protection and account locking
- **Session Management**: Role-based session timeouts
- **Audit Trail**: Comprehensive login tracking

### Authentication Flow

1. **User Login**: Username/password verification
2. **Account Check**: Verify account status and permissions
3. **Session Creation**: Create secure session with timeout
4. **Activity Monitoring**: Track user actions and login history

### Security Levels

- **High**: Admin, Developer (2-hour sessions)
- **Medium**: User, Moderator, Translator, Analyst, Support (30-40 min sessions)
- **Low**: Guest (15-minute sessions)

## 📊 User Roles & Permissions

| Role | Security Level | Session Timeout | Key Permissions |
|------|---------------|-----------------|-----------------|
| **Admin** | High | 1 hour | User management, System settings, View logs |
| **Moderator** | Medium | 40 min | Voice chat, Translation, Moderate chat |
| **User** | Medium | 30 min | Voice chat, Translation, Avatar control |
| **Translator** | Medium | 40 min | Advanced translation, Language management |
| **Developer** | High | 2 hours | System settings, Debug mode, API access |
| **Analyst** | Medium | 1 hour | View analytics, Export data, User activity |
| **Support** | Medium | 40 min | User activity, Unlock accounts, Support tickets |
| **Guest** | Low | 15 min | Voice chat, Translation, Avatar control |

## 🛠️ Development

### Running Tests

```bash

python -m pytest test/

```

### Code Style

```bash

# Format code

black src/
isort src/

# Lint code

flake8 src/
mypy src/

```

### Adding New Features

1. Create feature branch: `git checkout -b feature/new-feature`
2. Implement changes in appropriate module
3. Add tests in `test/` directory
4. Update documentation
5. Submit pull request

## 🔧 API Reference

### TTS API

```python

# Main synthesis function

synthesize_voice(text: str, output_path: str = None) -> bytes

# Voice cloning setup

setup_voice_cloning(voice_samples_path: str) -> bool

# Get synthesis info

get_synthesis_info() -> dict

```

### Animation API

```python

# Face sync class

class FaceSync:
    def __init__(self, use_webcam: bool = True)
    def run_face_sync(self, audio_path: str)
    def detect_facial_landmarks(self, frame)

```

### Web Interface API

```python

# Authentication

class AuthManager:
    def authenticate(self, username: str, password: str) -> bool
    def add_user(self, username: str, password: str, role: str) -> bool

# Dashboard

class Dashboard:
    def render(self)
    def update_chat_history(self, message: str)

```

## 🐛 Troubleshooting

### Common Issues

#### TTS Module Issues

- **Problem**: Model not found
- **Solution**: Download models using `TTS --list_models` and `TTS --download_model`

#### Animation Module Issues

- **Problem**: Webcam not detected
- **Solution**: Check device permissions and try different device IDs

#### Web Interface Issues

- **Problem**: Authentication fails
- **Solution**: Set PYTHONPATH and regenerate users:

  ```bash

  cd src
  python -m utils.generate_secure_users

  ```

#### Performance Issues

- **Problem**: Slow synthesis
- **Solution**: Enable GPU in config and optimize batch size

### Debug Mode

```bash

# Enable debug logging

export TALKBRIDGE_DEBUG=true

# Enable development mode (shows passwords)

export TALKBRIDGE_DEV_MODE=true

```

## 📈 Performance Optimization

### TTS Optimization

- Use GPU acceleration when available
- Optimize batch size for your hardware
- Use appropriate model size for latency vs quality
- Cache frequently used voice models

### Animation Optimization

- Reduce webcam resolution for better performance
- Use lower FPS for less CPU usage
- Optimize facial landmark detection parameters
- Use hardware acceleration for video processing

### Web Interface Optimization

- Enable session caching
- Optimize database queries
- Use CDN for static assets
- Implement proper error handling

## 🤝 Contributing

1. **Fork the repository**
2. **Create feature branch**: `git checkout -b feature/amazing-feature`
3. **Commit changes**: `git commit -m 'Add amazing feature'`
4. **Push to branch**: `git push origin feature/amazing-feature`
5. **Open pull request**

### Development Guidelines

- Follow PEP 8 style guidelines
- Add comprehensive tests for new features
- Update documentation for API changes
- Ensure cross-platform compatibility
- Test security features thoroughly

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- **Coqui TTS** for speech synthesis capabilities
- **MediaPipe** for facial landmark detection
- **Streamlit** for web interface framework
- **OpenCV** for computer vision processing
- **Pygame** for audio playback and timing

## 📞 Support

- **Documentation**: Check module-specific README files
- **Issues**: Report bugs via GitHub Issues
- **Discussions**: Join community discussions
- **Security**: Report security issues privately

---
