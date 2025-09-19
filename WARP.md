# WARP.md

This file provides guidance to WARP (warp.dev) when working with code in this repository.

## Project Overview

TalkBridge is an offline AI voice assistant system that processes audio input, converts it to text, translates between languages, generates AI responses, synthesizes speech, and animates an avatar. The system operates completely locally without requiring internet connectivity.

**Core Features:**
- Real-time voice translation and communication
- AI-powered speech synthesis with voice cloning
- Facial animation and lip synchronization
- Secure web interface with role-based authentication
- Complete offline operation (no external APIs)
- Desktop GUI application and web interface

## Development Commands

### Environment Setup

**Conda Installation (Recommended):**
```bash
# Quick setup
python config/setup_conda_desktop.py

# Manual setup
conda env create -f config/environment-desktop.yaml
conda activate talkbridge-desktop

# Desktop application
python src/desktop/main.py
```

**Traditional pip Installation:**
```bash
pip install -r requirements.txt

# Web interface
cd src/ui
python run_web_interface.py
# Access at http://localhost:8501
```

### Build and Run Commands

```bash
# Development mode (web interface)
make run-dev

# Production mode (local)
make run-prod

# Desktop application
conda activate talkbridge-desktop
python src/desktop/main.py

# Main console application with animations
python src/app.py

# Demo mode
python src/demo/run_demo.py
```

### Testing Commands

```bash
# Run all tests
python -m pytest test/

# Run desktop tests
pytest src/desktop/

# Test specific modules
pytest src/audio/tests/
pytest src/animation/tests/

# Demo conversation test
python src/demo/demo_runner.py
```

### Code Quality

```bash
# Format code
black src/
isort src/

# Lint code
flake8 src/
mypy src/

# Cleanup
make clean
```

### Deployment

```bash
# Install systemd service
make install-systemd

# Install nginx configuration
make install-nginx DOMAIN=your-domain.com

# Setup HTTPS
make tls DOMAIN=your-domain.com

# Check service status
make status
make logs
make health-check
```

## Architecture Overview

TalkBridge uses a modular architecture with clear separation of concerns:

### Core Processing Pipeline
```
Audio Input → STT (Whisper) → Translation → LLM (Ollama) → TTS → Avatar Animation → Audio Output
```

### Module Organization

**Audio Processing (`src/audio/`):**
- `capture.py`: Real-time audio capture from microphone
- `player.py`: Audio playback with volume control
- `effects.py`: Audio processing (noise reduction, echo cancellation)
- `synthesizer.py`: Audio synthesis helpers for TTS integration

**Speech Recognition (`src/stt/`):**
- Uses OpenAI Whisper for offline speech-to-text
- Supports multiple languages with auto-detection
- Real-time audio chunk processing

**Language Model (`src/ollama/`):**
- `ollama_client.py`: Ollama API client for local LLM communication
- `conversation_manager.py`: Manages conversation state and history
- `model_manager.py`: Handles model loading and switching
- `streaming_client.py`: Real-time streaming responses

**Translation (`src/translation/`):**
- `translator.py`: Main translation interface
- `offline_translator.py`: Offline translation using local models
- Supports English ↔ Spanish primarily, extensible to other languages

**Text-to-Speech (`src/tts/`):**
- `voice_cloner.py`: Voice cloning using Coqui TTS
- `synthesizer.py`: Main TTS interface with real-time synthesis
- Supports voice cloning from audio samples

**Animation (`src/animation/`):**
- `face_sync.py`: Facial animation and lip synchronization using MediaPipe
- `audio_visualizer.py`: Real-time audio visualization
- `interactive_animations.py`: Interactive animation controls
- Webcam integration for live avatar animation

**Web Interface (`src/ui/`):**
- `web_interface.py`: Main Streamlit application
- `auth/`: Secure authentication with role-based access (10 user roles)
- `components/`: Reusable UI components (login, dashboard, chat, audio recorder)
- `api/`: API wrappers for all backend modules

**Demo System (`src/demo/`):**
- `demo_runner.py`: Complete system simulation for testing
- `demo_api.py`: Mock implementations of all modules
- Pre-recorded samples for consistent demo experience

### Data Flow Architecture

1. **Input Processing:** User speech → Audio capture → STT processing
2. **Language Processing:** Transcription → Translation → LLM response generation
3. **Output Generation:** Response text → TTS synthesis → Avatar animation → Audio playback
4. **State Management:** All interactions logged → Conversation history → User session management

### Configuration Management

**Main Configuration (`config/config.yaml`):**
- Ollama settings (model, timeout, retries)
- Whisper STT configuration (model size, language, device)
- Audio settings (sample rate, channels, chunk size)
- UI preferences (theme, window size, language)

**Python Configuration (`src/config.py`):**
- Environment-specific settings (development/production/testing)
- Path management for all modules
- Feature toggles (demo mode, debug mode, GPU usage)
- Security configuration (session timeouts, password policies)

## Key Dependencies

### Core Runtime Dependencies
- **Python 3.8+** (3.11 recommended for full feature support)
- **PyTorch**: Deep learning framework for all AI models
- **Streamlit**: Web interface framework
- **PySide6/PyQt6**: Desktop GUI framework

### AI/ML Dependencies
- **Whisper**: Speech recognition (offline)
- **TTS (Coqui)**: Speech synthesis and voice cloning
- **Transformers**: Translation models
- **MediaPipe**: Facial landmark detection
- **Ollama**: Local LLM integration

### Audio Dependencies
- **librosa**: Audio analysis and feature extraction
- **sounddevice**: Audio capture and playback
- **pygame**: Audio timing and playback
- **scipy**: Signal processing

### Installation Constraints
- **MediaPipe, TTS, argos-translate**: Require Python ≤3.11
- **Use conda environment for best compatibility**
- **GPU acceleration available for CUDA-capable devices**

## Development Patterns

### Module Communication
- **Direct imports** for core functionality
- **API wrappers** (`src/ui/api/`) for UI integration
- **Event-driven** error handling and logging
- **Configuration-driven** feature toggles

### Error Handling
```python
# All modules use centralized error handling
from utils.error_handler import ErrorHandler

try:
    result = some_operation()
    log_message({"event": "operation_success", "result": result})
except Exception as e:
    ErrorHandler.log_error(e, "operation_context")
    return fallback_response()
```

### Testing Strategy
- **Demo mode** for integration testing without hardware
- **Mock implementations** for all external dependencies
- **Pytest** for unit testing
- **Real-time testing** with actual audio devices

### Authentication System
- **10 user roles** with different permission levels and session timeouts
- **Enhanced security**: SHA-256 salted password hashing
- **Account protection**: Brute force protection and lockouts
- **Session management**: Role-based timeout configuration

## Environment Differences

### Web vs Desktop Applications
- **Web Interface**: Streamlit-based, browser access, multi-user support
- **Desktop Application**: PyQt6-based, single-user, native OS integration
- **Both support**: Full TalkBridge functionality, authentication, real-time processing

### Demo vs Production Modes
- **Demo Mode**: Pre-recorded samples, simulated delays, no hardware requirements
- **Production Mode**: Real-time audio, live AI processing, full hardware integration

### Development vs Production
- **Development**: Debug logging, auto-reload, verbose output, test mode
- **Production**: Warning-level logging, performance optimization, security hardening

## Troubleshooting Common Issues

### Dependency Issues
```bash
# Check dependencies
python src/desktop/main.py  # Shows missing dependency warnings

# Python version compatibility
python --version  # Should be 3.8-3.11 for full features

# Conda environment recommended
conda activate talkbridge-desktop
```

### Audio Issues
```bash
# Check audio devices
python -c "import sounddevice; print(sounddevice.query_devices())"

# Test audio capture
python src/audio/tests/test_capture.py
```

### Model Issues
```bash
# Verify Ollama connection
curl http://localhost:11434/api/tags

# Test Whisper models
python -c "import whisper; print(whisper.available_models())"
```

### Authentication Issues
```bash
# Regenerate user database
python src/json/generate_secure_users.py

# Reset demo state
python -c "from src.demo.demo_runner import get_demo_runner; get_demo_runner().reset_demo()"
```

This comprehensive architecture enables TalkBridge to provide a complete offline AI voice assistant experience while maintaining modularity for easy development and testing.
