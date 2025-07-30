# 🎤 TalkBridge

**Real-time voice translation and communication platform with AI-powered speech synthesis, facial animation, and secure web interface.**

[![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)](https://python.org)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)
[![Platform](https://img.shields.io/badge/Platform-Windows%20%7C%20macOS-lightgrey.svg)](https://github.com/your-repo/talkbridge)

## 🌟 Features

### 🗣️ **Speech Synthesis (TTS)**
- **Voice Cloning**: Clone user's voice from audio samples
- **Offline Processing**: Complete offline functionality on Windows and macOS
- **Coqui TTS Integration**: Uses YourTTS model for multilingual voice cloning
- **Real-time Synthesis**: Low latency for live communication
- **Multiple Languages**: Support for multiple languages and accents

### 🎭 **Facial Animation**
- **Lip Sync**: Synchronize mouth movements with speech audio
- **Real-time Tracking**: MediaPipe facial landmark detection
- **Eye Blinking**: Natural eye movement animations
- **Webcam Integration**: Live webcam feed processing
- **Avatar Support**: Static and animated avatar options

### 🌐 **Web Interface**
- **Streamlit Dashboard**: Modern, responsive web interface
- **Secure Authentication**: Role-based user management
- **Real-time Chat**: Live chat with translation
- **Audio Recording**: Built-in audio capture and playback
- **Avatar Display**: Animated avatar with facial expressions

### 🔐 **Security & Authentication**
- **Enhanced Security**: Salted password hashing with SHA-256
- **Role-based Access**: Multiple user roles with specific permissions
- **Account Protection**: Brute force protection and account locking
- **Session Management**: Configurable session timeouts
- **Audit Trail**: Comprehensive login tracking and monitoring

## 📁 Project Structure

```
talkbridge/
├── config/
│   └── config.yaml              # Centralized configuration
├── src/
│   ├── tts/                     # Text-to-Speech module
│   │   ├── voice_cloner.py      # Voice cloning functionality
│   │   ├── synthesizer.py       # Speech synthesis API
│   │   ├── config.py            # TTS configuration
│   │   └── README.md            # TTS documentation
│   ├── animation/               # Facial animation module
│   │   ├── face_sync.py         # Real-time facial animation
│   │   ├── audio_visualizer.py  # Audio visualization
│   │   ├── interactive_animations.py
│   │   ├── loading_animation.py
│   │   └── README.md            # Animation documentation
│   ├── ui/                      # Web interface
│   │   ├── web_interface.py     # Main Streamlit app
│   │   ├── run_web_interface.py # App runner
│   │   ├── auth/                # Authentication system
│   │   │   └── auth_manager.py  # User management
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
│   │   ├── json/                # User data
│   │   │   ├── users.json       # User database
│   │   │   ├── generate_secure_users.py # Password generator
│   │   │   └── README.md        # User system docs
│   │   └── assets/              # Static assets
│   │       └── style.css        # Custom styling
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
```

## 🚀 Quick Start

### Prerequisites

- **Python 3.8+**
- **Windows 10+ or macOS 10.14+**
- **Webcam** (for facial animation)
- **Microphone** (for voice input)

### Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/your-repo/talkbridge.git
   cd talkbridge
   ```

2. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Generate secure users** (optional)
   ```bash
   cd src/ui/json
   python generate_secure_users.py
   ```

4. **Run the web interface**
   ```bash
   cd src/ui
   python run_web_interface.py
   ```

5. **Access the application**
   - Open your browser and go to: `http://localhost:8501`
   - Default credentials:
     - **Admin**: `admin` / `[generated password]`
     - **User**: `user` / `[generated password]`

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

### 🌐 Web Interface
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

**TTS Module Issues**
- **Problem**: Model not found
- **Solution**: Download models using `TTS --list_models` and `TTS --download_model`

**Animation Module Issues**
- **Problem**: Webcam not detected
- **Solution**: Check device permissions and try different device IDs

**Web Interface Issues**
- **Problem**: Authentication fails
- **Solution**: Regenerate users with `python generate_secure_users.py`

**Performance Issues**
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

**Made with ❤️ for real-time communication and AI-powered voice synthesis** 