# TalkBridge Modules Overview

Comprehensive overview of all modules in the TalkBridge real-time voice translation and communication platform, their purposes, dependencies, and interactions.

## Table of Contents

1. [Core Modules](#core-modules)
2. [Audio Processing Modules](#audio-processing-modules)
3. [AI/ML Modules](#aiml-modules)
4. [Interface Modules](#interface-modules)
5. [Desktop Application Modules](#desktop-application-modules)
6. [Web Interface Modules](#web-interface-modules)
7. [Utility Modules](#utility-modules)
8. [Demo Modules](#demo-modules)
9. [Module Dependencies](#module-dependencies)
10. [Module Interactions](#module-interactions)

## Core Modules

### Audio Module (`src/audio/`)

**Purpose**: Comprehensive audio processing system handling capture, playback, effectwws, and generation.

**Components**:
- `capture.py`: Real-time audio capture from microphone using PyAudio with configurable parameters
- `player.py`: Advanced audio playback with volume control, effects, and multi-device support
- `effects.py`: Audio processing effects including noise reduction, echo cancellation, and filters
- `generator.py`: Audio generation utilities for notifications, testing, and procedural audio
- `synthesizer.py`: Audio synthesis helpers for TTS integration and audio post-processing

**Dependencies**:
- `pyaudio`: Audio capture and playback interface
- `numpy`: Audio data processing and mathematical operations
- `scipy`: Advanced audio signal processing and filtering
- `librosa`: Audio analysis, feature extraction, and manipulation
- `soundfile`: High-quality audio file I/O operations
- `sounddevice`: Alternative audio interface with advanced features

**Interactions**:
- Receives audio input from microphone hardware
- Provides processed audio data to STT module
- Receives synthesized audio from TTS module with voice cloning
- Outputs audio to speakers/headphones with effects
- Integrates with animation module for real-time lip sync
- Connects to demo system for audio simulation

**Key Functions**:
```python
# Real-time audio capture with effects
capture_audio_stream(duration=5.0, apply_effects=True) -> bytes

# Advanced audio playback with device selection
play_audio_enhanced(audio_data: bytes, device_id: int = None) -> bool

# Audio effects processing pipeline
apply_audio_effects(audio_data: bytes, effects_config: dict) -> bytes

# Audio generation for notifications
generate_notification_sound(frequency: float, duration: float) -> bytes
```

### Speech-to-Text Module (`src/stt/`)

**Purpose**: Advanced speech recognition system converting audio to text using offline Whisper models.

**Components**:
- `whisper_engine.py`: Whisper model integration with GPU acceleration and model management
- `interface.py`: Main transcription API with streaming support and language detection
- `audio_utils.py`: Audio preprocessing, optimization, and format conversion for STT
- `config.py`: STT configuration management, model selection, and performance tuning

**Dependencies**:
- `whisper`: OpenAI Whisper for high-quality speech recognition
- `torch`: PyTorch for model inference and GPU acceleration
- `numpy`: Audio data processing and tensor operations
- `librosa`: Audio feature extraction and preprocessing
- `transformers`: Additional model support and optimization

**Interactions**:
- Receives preprocessed audio data from audio module
- Sends transcribed text to translation module
- Provides real-time transcription status to UI components
- Logs transcription results and performance metrics
- Integrates with demo system for simulated transcription

**Key Functions**:
```python
# Advanced transcription with language detection
transcribe_audio_advanced(audio_data: bytes, detect_language: bool = True) -> dict

# Streaming transcription for real-time use
transcribe_streaming(audio_stream: Iterator[bytes]) -> Iterator[str]

# Batch transcription for multiple files
transcribe_batch(audio_files: List[str]) -> List[dict]

# Get model information and performance stats
get_transcription_info() -> dict
```

### Language Model Module (`src/ollama/`)

**Purpose**: Advanced AI conversation system using local Ollama models with streaming and conversation management.

**Components**:
- `ollama_client.py`: Enhanced Ollama API client with health monitoring and error handling
- `conversation_manager.py`: Advanced conversation state management with persistence and search
- `model_manager.py`: Comprehensive model management including installation and testing
- `prompt_engineer.py`: Intelligent prompt construction, optimization, and template management
- `streaming_client.py`: Real-time streaming responses with callbacks and event handling

**Dependencies**:
- `requests`: HTTP client for Ollama API communication
- `json`: Data serialization for conversation storage
- `threading`: Concurrent processing for streaming responses
- `queue`: Event handling for real-time streaming
- `pathlib`: File system operations for model management

**Interactions**:
- Receives translated text from translation module
- Sends generated responses to TTS module
- Manages conversation state and history
- Provides streaming responses to UI components
- Integrates with demo system for simulated AI responses
- Logs conversation data and model performance

**Key Functions**:
```python
# Enhanced text generation with streaming
generate_response_streaming(prompt: str, model: str) -> Iterator[str]

# Conversation management with context
manage_conversation(conv_id: str, message: str) -> str

# Model health monitoring and testing
test_model_performance(model_name: str) -> dict

# Advanced conversation search and export
search_conversations(query: str) -> List[dict]
```
- `json`: JSON data handling
- `asyncio`: Asynchronous operations
- `threading`: Background processing

**Interactions**:
- Receives translated text from translation module
- Generates AI responses
- Sends responses to TTS module
- Maintains conversation context
- Provides response status to UI

**Key Functions**:
```python
# Generate response
generate_response(user_message: str, context: str = "") -> str

# Chat conversation
chat_conversation(messages: List[dict]) -> str

# Get model info
get_model_info() -> dict
```

### Translation Module (`src/translation/`)

**Purpose**: Multi-language translation system with automatic language detection and optimization.

**Components**:
- `translator.py`: Main translation interface with caching and optimization
- `offline_translator.py`: Offline translation engine using local models
- `language_detector.py`: Automatic language detection and confidence scoring

**Dependencies**:
- `transformers`: Hugging Face transformers for translation models
- `torch`: PyTorch for model inference and optimization
- `langdetect`: Language detection library
- `numpy`: Numerical operations for model processing

**Interactions**:
- Receives transcribed text from STT module
- Sends translated text to LLM module
- Provides translation confidence scores to UI
- Caches frequently used translations
- Integrates with demo system for simulated translations

**Key Functions**:
```python
# Advanced translation with language detection
translate_text_advanced(text: str, target_lang: str = "auto") -> dict

# Batch translation for multiple texts
translate_batch(texts: List[str], target_lang: str) -> List[dict]

# Language detection with confidence
detect_language(text: str) -> dict

# Translation caching and optimization
get_translation_cache_stats() -> dict
```

### Text-to-Speech Module (`src/tts/`)

**Purpose**: Advanced speech synthesis with voice cloning capabilities using Coqui TTS.

**Components**:
- `voice_cloner.py`: Voice cloning functionality using Coqui TTS YourTTS model with GPU optimization
- `synthesizer.py`: Main TTS interface with voice cloning integration and streaming support
- `config.py`: TTS configuration management, model selection, and voice profile management

**Dependencies**:
- `TTS`: Coqui TTS library for advanced voice synthesis and cloning
- `torch`: PyTorch for model inference and GPU acceleration
- `numpy`: Audio data processing and manipulation
- `soundfile`: High-quality audio file operations
- `librosa`: Audio analysis and feature extraction

**Interactions**:
- Receives text responses from LLM module
- Provides synthesized audio to audio module
- Integrates with animation module for lip-sync timing
- Manages voice cloning profiles and samples
- Provides synthesis status to UI components
- Integrates with demo system for voice simulation

**Key Functions**:
```python
# Voice cloning from reference samples
clone_voice_from_samples(samples: List[str]) -> bool

# Advanced text synthesis with cloned voice
synthesize_with_cloned_voice(text: str, voice_profile: str) -> bytes

# Real-time streaming synthesis
synthesize_streaming(text_stream: Iterator[str]) -> Iterator[bytes]

# Voice profile management
manage_voice_profiles() -> dict

# Model information and performance metrics
get_synthesis_info() -> dict
```

### Animation Module (`src/animation/`)

**Purpose**: Advanced avatar animation and facial synchronization with enhanced MediaPipe integration.

**Components**:
- `face_sync.py`: Facial animation and lip synchronization using MediaPipe with emotion detection
- `audio_visualizer.py`: Real-time audio visualization with multiple display modes
- `interactive_animations.py`: Interactive animation controls with particle systems
- `loading_animation.py`: Loading and transition animations with progress tracking
- `camera_manager.py`: Webcam integration and video processing with device management

**Dependencies**:
- `mediapipe`: Google MediaPipe for facial landmark detection and analysis
- `opencv-python`: Computer vision for video processing and camera interface
- `pygame`: Audio playback timing and interactive graphics
- `numpy`: Numerical computations for animation calculations
- `librosa`: Audio analysis for lip sync timing and frequency analysis

**Interactions**:
- Receives audio data from TTS module for lip synchronization
- Synchronizes facial movements with speech timing
- Provides animation frames to UI components
- Integrates with webcam for real-time avatar overlay
- Manages camera devices and video processing
- Logs animation performance and timing metrics

**Key Functions**:
```python
# Advanced face sync with emotion detection
run_face_sync_enhanced(audio_path: str, emotion: str = "neutral") -> dict

# Real-time facial landmark detection
detect_facial_landmarks_realtime(frame, model_complexity: int = 1) -> dict

# Interactive animation management
manage_interactive_animations(animation_type: str, parameters: dict) -> bool

# Camera device management
manage_camera_devices() -> List[dict]
```

## Interface Modules

### Desktop Application Module (`src/desktop/`)

**Purpose**: Comprehensive PySide6-based desktop application with tabbed interface and advanced state management.

**Key Components**:

#### Application Core (`src/desktop/app/`)
- `main.py`: Desktop application entry point with dependency checking
- `application.py`: Main application class (TalkBridgeApplication) with service coordination
- `main_window.py`: Main window with integrated tabs and menu system
- `state_manager.py`: Advanced application state management with persistence

#### UI Components (`src/desktop/components/`)
- `chat_tab.py`: Real-time conversation interface with voice recording
- `avatar_tab.py`: Avatar display and webcam integration with animation controls
- `settings_tab.py`: Comprehensive system configuration interface

#### Dialogs (`src/desktop/dialogs/`)
- `login_dialog.py`: Enhanced authentication dialog with security features

#### Services (`src/desktop/services/`)
- `core_bridge.py`: Service integration bridge coordinating all backend modules

#### UI Utilities (`src/desktop/ui/`)
- `ui_utils.py`: Platform-specific UI utilities and cross-platform fixes
- `theme.py`: Unified design system and theming for CustomTkinter components

#### Windows (`src/desktop/windows/`)
- `dashboard.py`: Service status dashboard with real-time monitoring

**Dependencies**:
- `PySide6`: Modern Qt6 bindings for Python with advanced widgets
- `logging`: Comprehensive logging system
- `json`: Configuration and state serialization
- `pathlib`: Modern file system operations
- `threading`: Background service management

**Key Features**:
- **Tabbed Interface**: Integrated chat, avatar, and settings in single window
- **Real-time Processing**: Live audio processing and avatar animation
- **State Persistence**: Automatic saving and restoration of application state
- **Service Monitoring**: Real-time status of all backend services
- **Authentication**: Secure login with session management
- **Configuration**: Comprehensive settings management
- **Platform Optimization**: Automatic detection and fixes for Wayland and other display servers

**Platform-Specific Features**:
- **Wayland Support**: Automatic detection and optimization for Wayland display server
- **Cross-platform Compatibility**: OS-specific fixes for Linux, Windows, and macOS
- **Display Scaling**: Intelligent scaling adjustments for different display configurations
- **Font Rendering**: Enhanced text clarity on various display systems

### Web Interface Module (`src/ui/`)

**Purpose**: Advanced Streamlit-based web application with device management and real-time communication.

**Key Components**:

#### Core Web Application (`src/ui/`)
- `web_interface.py`: Main Streamlit application with dashboard interface
- `web_server.py`: Enhanced web server with device permissions and security

#### Authentication (`src/ui/auth/`)
- Enhanced authentication system with role-based access control

#### Components (`src/ui/components/`)
- `dashboard.py`: Main dashboard with real-time chat and controls
- `login.py`: Web-based authentication interface
- Reusable UI components for consistent interface

#### API Wrappers (`src/ui/api/`)
- `llm_api.py`: Ollama LLM integration for web interface
- `tts_api.py`: TTS and voice cloning API wrapper
- `stt_api.py`: Speech recognition API integration
- `translation_api.py`: Translation service wrapper
- `animation_api.py`: Avatar animation API interface

**Dependencies**:
- `streamlit`: Modern web application framework
- `asyncio`: Asynchronous web operations
- `websockets`: Real-time communication
- `ssl`: Secure HTTPS/WSS connections
- `threading`: Background processing

**Key Features**:
- **Device Permissions**: Advanced camera/microphone permission management
- **Real-time Communication**: WebSocket-based real-time updates
- **Responsive Design**: Mobile-friendly interface
- **Security**: HTTPS/SSL encryption and secure authentication
- **API Integration**: Seamless integration with all backend services

## Utility Modules

### Enhanced Utilities Module (`src/utils/`)

**Purpose**: Comprehensive utility system providing shared functionality across all modules.

**Components**:
- `logger.py`: Advanced logging system with rotation, filtering, and performance monitoring
- `error_handler.py`: Centralized error handling with user-friendly messages and recovery
- `storage_manager.py`: Advanced file storage and data management with backup/restore
- `config.py`: Global configuration management with validation and hot-reloading
- `error_suppression.py`: System for suppressing ML/AI library warnings and optimization

**Dependencies**:
- `logging`: Python logging with advanced handlers
- `pathlib`: Modern file system operations
- `json`: Configuration serialization
- `yaml`: Configuration file support
- `threading`: Thread-safe operations

**Key Features**:
- **Advanced Logging**: Structured logging with multiple outputs and log rotation
- **Error Recovery**: Intelligent error recovery and fallback mechanisms
- **Configuration Management**: Hot-reloadable configuration with validation
- **Performance Monitoring**: System performance tracking and optimization
- **Data Persistence**: Reliable data storage with backup and recovery

### Desktop UI Utilities Module (`src/desktop/ui/`)

**Purpose**: Platform-specific UI utilities and cross-platform compatibility system for desktop applications.

**Components**:
- `ui_utils.py`: Platform detection, Wayland fixes, and UI configuration utilities
- `theme.py`: Unified design system and theming for CustomTkinter components

**Key Functions** (from `ui_utils.py`):
```python
# Operating system and display server detection
detect_operating_system() -> str
is_wayland_session() -> bool

# Platform-specific fixes and optimizations  
apply_wayland_fixes() -> None
configure_ui() -> None

# Environment and diagnostic information
get_display_info() -> dict
get_ui_environment_info() -> dict

# UI utilities for consistent display
clean_text(text: str) -> str
icon(name: str, size: Tuple[int, int]) -> Optional[ctk.CTkImage]
```

**Dependencies**:
- `customtkinter`: Modern GUI framework
- `platform`: OS detection and system information
- `subprocess`: System command execution for display server detection
- `os`: Environment variable management
- `PIL` (optional): Image processing for icons

**Key Features**:
- **Wayland Detection**: Comprehensive Wayland display server detection using multiple methods
- **Platform-Specific Fixes**: Automatic application of fixes for CustomTkinter on Wayland
- **Environment Variable Management**: Intelligent setting of display server compatibility variables
- **Cross-platform Support**: OS-specific optimizations for Linux, Windows, and macOS
- **Display Scaling**: Automatic scaling adjustments to prevent blurry text and UI elements
- **Font Rendering**: Enhanced text clarity through display server configuration
- **Diagnostic Tools**: Comprehensive environment and fix status reporting

**Wayland-Specific Fixes**:
- Forces X11 backend through XWayland for better CustomTkinter compatibility
- Sets explicit scaling factors to prevent fractional scaling issues
- Configures font rendering improvements for text clarity
- Disables problematic auto-scaling features that cause UI issues
- Applied automatically at startup when Wayland is detected

### Authentication Module (`src/auth/`)

**Purpose**: Enhanced security system with role-based access control.

**Components**:
- `auth_manager.py`: Advanced authentication with brute force protection and audit logging

**Key Features**:
- **Enhanced Security**: SHA-256 salted password hashing
- **Role-based Access**: Multiple user roles with granular permissions
- **Session Management**: Secure session handling with configurable timeouts
- **Audit Trail**: Comprehensive login tracking and security monitoring
- **Brute Force Protection**: Account locking and rate limiting

## Demo Modules

### Comprehensive Demo System (`src/demo/`)

**Purpose**: Advanced demo and testing system with realistic simulations.

**Components**:

#### Core Demo System
- `demo_runner.py`: Advanced demo conversation simulation engine
- `demo_api.py`: Demo API wrappers for all backend modules
- `demo_ui.py`: Demo UI components and simulation controls
- `demo_config.py`: Demo configuration and scenario management

#### Individual Module Demos
- `tts_demo.py`: TTS and voice cloning demonstration
- `ollama_demo.py`: LLM integration and streaming demos
- `animation_demo.py`: Avatar animation and face sync demos
- `audio_demo.py`: Audio processing and effects demonstrations
- `translation_demo.py`: Translation system demonstrations
- `face_sync_demo.py`: Facial animation synchronization demos

**Dependencies**:
- All backend modules (with mocking capabilities)
- `unittest.mock`: Sophisticated mocking system
- `random`: Realistic data generation
- `time`: Timing simulation

**Key Features**:
- **Realistic Simulation**: Authentic behavior simulation without hardware
- **Performance Testing**: Load testing and performance benchmarking
- **Integration Testing**: End-to-end system testing
- **Educational Examples**: Comprehensive examples for each module
- **Development Support**: Tools for development and debugging

**Demo Scenarios**:
- **Voice Cloning Demo**: Complete voice cloning workflow
- **Real-time Conversation**: Simulated real-time chat with all features
- **Animation Showcase**: Avatar animation capabilities demonstration
- **Performance Benchmarks**: System performance and optimization testing
## Module Dependencies

### Application-Level Dependencies

```
TalkBridge System Dependencies:

Desktop Application:
main.py
├── TalkBridgeApplication (PySide6)
├── StateManager (Configuration & Persistence)
├── CoreBridge (Service Coordination)
├── MainWindow (UI Container)
│   ├── ChatTab → stt/, translation/, ollama/, tts/
│   ├── AvatarTab → animation/, audio/, camera/
│   └── SettingsTab → config/, auth/
└── LoginDialog → auth/

Web Application:
web_server.py
├── WebServerManager (Device Management)
├── TalkBridgeWebInterface (Streamlit)
├── Dashboard → API Wrappers → Backend Modules
├── Authentication → auth/
└── Components → Specialized UI Elements

Backend Processing Chain:
audio/capture → stt/whisper_engine → translation/translator
→ ollama/conversation_manager → tts/voice_cloner → animation/face_sync
→ audio/player
```

### Inter-Module Communication Patterns

```
Service Communication Patterns:

1. Desktop Application Communication:
   MainWindow ↔ CoreBridge ↔ Backend Services
   Components → StateManager → Persistence
   Services → Utils/Logger → Logging System

2. Web Application Communication:
   Streamlit UI → API Wrappers → Backend Services
   WebSocket → Real-time Updates → Client Browser
   Session Manager → Authentication → User Management

3. Backend Module Chain:
   Audio Input → STT → Translation → LLM → TTS → Animation → Audio Output
   
4. Demo System Integration:
   Demo APIs → Mocked Backend Services → Simulated Responses
   Performance Testing → Real Backend Services → Benchmarking

5. Configuration Flow:
   YAML Config → utils/config → Module Configuration
   State Manager → Application State → Component State
```

## Module Interactions

### Real-time Processing Flow

```
Desktop Application Real-time Flow:

User Interaction (ChatTab)
    ↓
Audio Capture (audio/capture)
    ↓
Speech Recognition (stt/whisper_engine)
    ↓
Language Translation (translation/translator)
    ↓
AI Response Generation (ollama/streaming_client)
    ↓
Voice Synthesis + Cloning (tts/voice_cloner)
    ↓
Avatar Animation Sync (animation/face_sync)
    ↓
Audio Output (audio/player)
    ↓
State Persistence (StateManager)

Web Application Processing Flow:

Browser Input (Dashboard)
    ↓
API Wrapper (ui/api/*)
    ↓
Backend Service Processing
    ↓
Real-time Response Streaming
    ↓
WebSocket Updates (web_server)
    ↓
Client Display Update
```

### Error Handling and Recovery

```
Error Handling Chain:

Module Error → utils/error_handler → User-friendly Message
    ↓
Logging (utils/logger) → File System (utils/storage_manager)
    ↓
Recovery Mechanism → Fallback Operation
    ↓
State Restoration → Continue Operation

Demo Mode Fallback:

Service Unavailable → Demo Mode Detection → Simulated Response
    ↓
demo/demo_api → Realistic Simulation → User Experience Maintained
```

### Performance Optimization Integration

```
Performance Management:

Memory Management:
- StateManager: Application state caching
- Model Loading: Lazy loading and caching
- Audio Processing: Buffer management
- Animation: Frame rate optimization

Threading Coordination:
- Main UI Thread: User interface responsiveness
- Audio Thread: Real-time audio processing
- Service Threads: Backend processing
- Animation Thread: Smooth avatar rendering

Caching Strategy:
- Configuration: Hot-reloadable settings
- Models: Intelligent model caching
- Voice Profiles: Voice cloning cache
- Conversations: Chat history caching
```

---

**Note**: This modular architecture supports both desktop and web deployment scenarios while maintaining consistent functionality across all interfaces. The comprehensive demo system ensures reliable testing and development workflows, while the enhanced utility modules provide robust error handling and performance optimization.
```

### Authentication Module (`src/auth/`)

**Purpose**: Handles user authentication and session management.

**Components**:
- `auth_manager.py`: Main authentication logic and user management
- `session_handler.py`: Session state management
- `permission_manager.py`: Role-based access control

**Dependencies**:
- `hashlib`: Password hashing
- `secrets`: Cryptographic salt generation
- `json`: User data storage
- `datetime`: Session timing

**Interactions**:
- Validates user credentials
- Manages user sessions
- Controls access to system features
- Logs authentication events

**Key Functions**:
```python
# Authenticate user
authenticate(username: str, password: str) -> bool

# Add user
add_user(username: str, password: str, role: str) -> bool

# Check permissions
has_permission(user: str, permission: str) -> bool
```

### UI Components (`src/ui/components/`)

**Purpose**: Reusable UI components for the web interface.

**Components**:
- `login.py`: Login form component
- `dashboard.py`: Main dashboard layout
- `audio_recorder.py`: Audio recording interface
- `chat_interface.py`: Chat display and input
- `avatar_display.py`: Avatar visualization
- `settings.py`: Configuration interface

**Dependencies**:
- `streamlit`: UI framework
- `streamlit-ace`: Code editor component
- `streamlit-option-menu`: Menu components

**Interactions**:
- Provides UI elements for user interaction
- Handles user input and validation
- Displays system status and results
- Manages component state

**Key Functions**:
```python
# Render login form
render_login_form() -> bool

# Render audio recorder
render_audio_recorder() -> bytes

# Render chat interface
render_chat_interface() -> str
```

### API Wrappers (`src/ui/api/`)

**Purpose**: Provides API interfaces for backend modules.

**Components**:
- `tts_api.py`: TTS module API wrapper
- `stt_api.py`: STT module API wrapper
- `llm_api.py`: LLM module API wrapper
- `translation_api.py`: Translation module API wrapper
- `animation_api.py`: Animation module API wrapper

**Dependencies**:
- Backend module imports
- `typing`: Type hints
- `asyncio`: Asynchronous operations

**Interactions**:
- Provides clean API interfaces for UI
- Handles module communication
- Manages error handling and logging
- Coordinates between UI and backend

**Key Functions**:
```python
# TTS API
synthesize_voice(text: str) -> bytes

# STT API
transcribe_audio(audio_data: bytes) -> str

# LLM API
generate_response(message: str) -> str
```

## Utility Modules

### Utils Module (`src/utils/`)

**Purpose**: Shared utilities and helper functions used across the system.

**Components**:
- `error_handler.py`: Centralized error handling and logging
- `logger.py`: Logging utilities and configuration
- `storage_manager.py`: File storage and management
- `config.py`: Global configuration management

**Dependencies**:
- `logging`: Python logging framework
- `os`: Operating system interface
- `pathlib`: Path manipulation
- `json`: Data serialization
- `datetime`: Time handling

**Interactions**:
- Provides utilities to all modules
- Handles system-wide error management
- Manages file storage and organization
- Provides configuration access

**Key Functions**:
```python
# Error handling
log_error(error: Exception, context: str) -> None

# Logging
log_message(entry: dict) -> None

# Storage
save_audio_sample(audio_bytes: bytes, user_id: str) -> str
```

### Demo Module (`src/demo/`)

**Purpose**: Provides demo mode functionality for testing without hardware.

**Components**:
- `demo_runner.py`: Main demo conversation runner
- `demo_api.py`: Demo API wrappers for all modules
- `demo_ui.py`: Demo-specific UI components
- `demo_config.py`: Demo configuration and settings

**Dependencies**:
- All backend module APIs
- `streamlit`: UI framework
- `time`: Timing simulation
- `json`: Demo data handling

**Interactions**:
- Simulates all system functionality
- Provides consistent demo experience
- Uses predefined sample files
- Integrates with main UI

**Key Functions**:
```python
# Run demo conversation
run_demo_conversation() -> dict

# Simulate audio capture
simulate_audio_capture() -> bytes

# Simulate transcription
simulate_transcription(audio_data: bytes) -> str
```

## Module Dependencies

### Dependency Graph

```
ui/ (Web Interface)
├── auth/ (Authentication)
│   └── utils/ (Utilities)
├── components/ (UI Components)
│   └── api/ (API Wrappers)
└── api/ (API Wrappers)
    ├── tts/ (Text-to-Speech)
    ├── stt/ (Speech-to-Text)
    ├── ollama/ (Language Model)
    ├── translation/ (Translation)
    └── animation/ (Animation)
        └── audio/ (Audio Processing)

audio/ (Audio Processing)
├── stt/ (Speech Recognition)
├── tts/ (Speech Synthesis)
└── animation/ (Avatar Animation)

stt/ (Speech Recognition)
├── translation/ (Translation)
└── utils/ (Utilities)

translation/ (Translation)
├── ollama/ (Language Model)
└── utils/ (Utilities)

ollama/ (Language Model)
├── tts/ (Speech Synthesis)
└── utils/ (Utilities)

tts/ (Speech Synthesis)
├── animation/ (Avatar Animation)
├── audio/ (Audio Processing)
└── utils/ (Utilities)

animation/ (Avatar Animation)
├── audio/ (Audio Processing)
└── utils/ (Utilities)

demo/ (Demo Mode)
├── All modules (via API wrappers)
└── ui/ (Web Interface)

utils/ (Utilities)
└── All modules (shared utilities)
```

### External Dependencies

#### Core Dependencies
- **Python 3.8+**: Runtime environment
- **Streamlit**: Web interface framework
- **PyTorch**: Deep learning framework
- **NumPy**: Numerical computing
- **OpenCV**: Computer vision

#### Audio Dependencies
- **PyAudio**: Audio capture and playback
- **Librosa**: Audio analysis
- **SoundFile**: Audio file I/O
- **SciPy**: Signal processing

#### AI/ML Dependencies
- **Whisper**: Speech recognition
- **TTS**: Speech synthesis
- **Transformers**: Translation models
- **MediaPipe**: Facial landmark detection

#### Web Dependencies
- **Streamlit**: Web framework
- **Pandas**: Data handling
- **Plotly**: Visualizations
- **Pillow**: Image processing

## Module Interactions

### Data Flow Between Modules

```
1. User Input Flow
   ui/web_interface.py
   ↓
   ui/components/audio_recorder.py
   ↓
   audio/capture.py
   ↓
   stt/transcriber.py
   ↓
   translation/translator.py
   ↓
   ollama/conversation_manager.py
   ↓
   tts/synthesizer.py
   ↓
   animation/face_sync.py
   ↓
   audio/player.py
   ↓
   ui/components/avatar_display.py

2. Error Handling Flow
   Any Module
   ↓
   utils/error_handler.py
   ↓
   utils/logger.py
   ↓
   utils/storage_manager.py
   ↓
   Log Files

3. Configuration Flow
   Any Module
   ↓
   utils/config.py
   ↓
   Environment Variables
   ↓
   Configuration Files

4. Demo Mode Flow
   ui/web_interface.py
   ↓
   demo/demo_runner.py
   ↓
   demo/demo_api.py
   ↓
   All Module APIs (simulated)
   ↓
   demo/demo_ui.py
   ↓
   ui/components/ (demo display)
```

### API Integration Patterns

#### Synchronous API Calls
```python
# Direct module calls
from audio.capture import capture_audio
from stt.transcriber import transcribe_audio

audio_data = capture_audio(duration=5.0)
transcription = transcribe_audio(audio_data)
```

#### Asynchronous API Calls
```python
# Async module calls
import asyncio
from ollama.conversation_manager import ConversationManager

async def get_response(message):
    manager = ConversationManager()
    response = await manager.generate_response(message)
    return response
```

#### Event-Driven Integration
```python
# Event-based integration
from utils.logger import log_message
from utils.error_handler import log_error

def process_audio(audio_data):
    try:
        result = transcribe_audio(audio_data)
        log_message({"event": "transcription", "result": result})
        return result
    except Exception as e:
        log_error(e, "audio_processing")
        return None
```

### Module Communication Patterns

#### Direct Import
```python
# Direct module import
from tts.synthesizer import synthesize_voice
from translation.translator import translate_text

# Use directly
audio = synthesize_voice("Hello world")
translation = translate_text("Hello", "en", "es")
```

#### API Wrapper
```python
# Through API wrapper
from ui.api.tts_api import get_tts_api
from ui.api.translation_api import get_translation_api

tts_api = get_tts_api()
translation_api = get_translation_api()

audio = tts_api.synthesize_voice("Hello world")
translation = translation_api.translate_text("Hello", "en", "es")
```

#### Event Bus
```python
# Event-based communication
from utils.event_bus import EventBus

event_bus = EventBus()

# Subscribe to events
@event_bus.subscribe("audio_captured")
def handle_audio_captured(audio_data):
    transcription = transcribe_audio(audio_data)
    event_bus.publish("transcription_complete", transcription)

# Publish events
event_bus.publish("audio_captured", audio_data)
```

## Performance Considerations

### Module Loading
- **Lazy Loading**: Modules loaded only when needed
- **Caching**: Frequently used modules cached in memory
- **Resource Management**: Proper cleanup of module resources

### Memory Management
- **Audio Buffers**: Efficient audio buffer management
- **Model Loading**: Models loaded once and reused
- **Garbage Collection**: Proper cleanup of temporary objects

### CPU Optimization
- **Parallel Processing**: Independent modules run in parallel
- **Async Operations**: Non-blocking operations where possible
- **Background Processing**: Heavy operations run in background

### Latency Optimization
- **Real-time Pipeline**: Optimized for low-latency processing
- **Buffer Management**: Efficient buffer handling for audio
- **Caching**: Response caching for repeated requests

---

**Note**: This modular architecture allows for easy extension, testing, and maintenance. Each module can be developed and tested independently while maintaining clear interfaces for integration. 