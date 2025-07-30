# TalkBridge Modules Overview

Comprehensive overview of all modules in the TalkBridge system, their purposes, dependencies, and interactions.

## Table of Contents

1. [Core Modules](#core-modules)
2. [Audio Processing Modules](#audio-processing-modules)
3. [AI/ML Modules](#aiml-modules)
4. [Web Interface Modules](#web-interface-modules)
5. [Utility Modules](#utility-modules)
6. [Demo Modules](#demo-modules)
7. [Module Dependencies](#module-dependencies)
8. [Module Interactions](#module-interactions)

## Core Modules

### Audio Module (`src/audio/`)

**Purpose**: Handles all audio-related functionality including capture, playback, processing, and synthesis.

**Components**:
- `capture.py`: Real-time audio capture from microphone using PyAudio
- `player.py`: Audio playback functionality with volume control
- `effects.py`: Audio processing effects (noise reduction, echo cancellation)
- `generator.py`: Audio generation utilities for testing and demos
- `synthesizer.py`: Audio synthesis helpers for TTS integration

**Dependencies**:
- `pyaudio`: Audio capture and playback
- `numpy`: Audio data processing
- `scipy`: Audio signal processing
- `librosa`: Audio analysis and features
- `soundfile`: Audio file I/O

**Interactions**:
- Receives audio input from microphone
- Provides audio data to STT module
- Receives synthesized audio from TTS module
- Outputs audio to speakers/headphones
- Integrates with animation module for lip sync

**Key Functions**:
```python
# Audio capture
capture_audio(duration=5.0) -> bytes

# Audio playback
play_audio(audio_data: bytes) -> bool

# Audio processing
process_audio(audio_data: bytes) -> bytes
```

### Speech-to-Text Module (`src/stt/`)

**Purpose**: Converts speech audio to text using offline Whisper models.

**Components**:
- `whisper_client.py`: Whisper model integration and inference
- `transcriber.py`: Main transcription interface and API
- `audio_processor.py`: Audio preprocessing for optimal STT performance

**Dependencies**:
- `whisper`: OpenAI Whisper for speech recognition
- `torch`: PyTorch for model inference
- `numpy`: Audio data processing
- `librosa`: Audio feature extraction

**Interactions**:
- Receives audio data from audio module
- Sends transcribed text to translation module
- Provides transcription status to UI
- Logs transcription results

**Key Functions**:
```python
# Transcribe audio
transcribe_audio(audio_data: bytes) -> str

# Get transcription info
get_transcription_info() -> dict

# Process audio chunk
process_chunk(audio_chunk: bytes) -> str
```

### Language Model Module (`src/ollama/`)

**Purpose**: Generates AI responses using local Ollama models.

**Components**:
- `ollama_client.py`: Ollama API client for model communication
- `conversation_manager.py`: Manages conversation state and history
- `model_manager.py`: Handles model loading, switching, and management
- `prompt_engineer.py`: Constructs and optimizes prompts for better responses
- `streaming_client.py`: Handles streaming responses for real-time interaction

**Dependencies**:
- `requests`: HTTP client for Ollama API
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

**Purpose**: Translates text between languages (primarily English to Spanish).

**Components**:
- `translator.py`: Main translation interface and API
- `offline_translator.py`: Offline translation engine using local models
- `language_detector.py`: Detects input language automatically

**Dependencies**:
- `transformers`: Hugging Face transformers for translation models
- `torch`: PyTorch for model inference
- `sentencepiece`: Tokenization for translation models
- `sacremoses`: Moses tokenization

**Interactions**:
- Receives transcribed text from STT module
- Translates text to target language
- Sends translated text to LLM module
- Provides translation status to UI
- Logs translation results

**Key Functions**:
```python
# Translate text
translate_text(text: str, source_lang: str = "en", target_lang: str = "es") -> str

# Get supported languages
get_supported_languages() -> List[str]

# Detect language
detect_language(text: str) -> str
```

### Text-to-Speech Module (`src/tts/`)

**Purpose**: Converts text to speech using voice cloning and synthesis.

**Components**:
- `voice_cloner.py`: Voice cloning functionality using Coqui TTS
- `synthesizer.py`: Main TTS interface and API
- `config.py`: TTS configuration and settings

**Dependencies**:
- `TTS`: Coqui TTS for speech synthesis
- `torch`: PyTorch for model inference
- `numpy`: Audio data processing
- `librosa`: Audio analysis
- `soundfile`: Audio file I/O

**Interactions**:
- Receives AI responses from LLM module
- Synthesizes speech from text
- Sends audio data to animation module
- Provides audio to audio playback module
- Logs synthesis results

**Key Functions**:
```python
# Synthesize voice
synthesize_voice(text: str, output_path: str = None) -> bytes

# Clone voice
clone_voice_from_samples(audio_samples: List[str]) -> str

# Get synthesis info
get_synthesis_info() -> dict
```

### Animation Module (`src/animation/`)

**Purpose**: Handles avatar animation and facial synchronization with speech.

**Components**:
- `face_sync.py`: Facial animation and lip synchronization using MediaPipe
- `audio_visualizer.py`: Audio visualization for real-time feedback
- `interactive_animations.py`: Interactive animation controls
- `loading_animation.py`: Loading and transition animations

**Dependencies**:
- `mediapipe`: Google MediaPipe for facial landmark detection
- `opencv-python`: Computer vision for video processing
- `pygame`: Audio playback and timing
- `numpy`: Numerical computations
- `librosa`: Audio analysis for lip sync

**Interactions**:
- Receives audio data from TTS module
- Synchronizes facial movements with speech
- Provides animation frames to UI
- Integrates with webcam for real-time avatar
- Logs animation performance

**Key Functions**:
```python
# Run face sync
run_face_sync(audio_path: str) -> dict

# Detect landmarks
detect_facial_landmarks(frame) -> List[tuple]

# Update animation
update_animation_state(audio_features: dict) -> dict
```

## Web Interface Modules

### UI Module (`src/ui/`)

**Purpose**: Provides the web-based user interface using Streamlit.

**Components**:
- `web_interface.py`: Main Streamlit application entry point
- `auth/`: Authentication system and user management
- `components/`: Reusable UI components
- `api/`: API wrappers for backend modules
- `assets/`: Static files (CSS, images, etc.)

**Dependencies**:
- `streamlit`: Web application framework
- `pandas`: Data handling for UI
- `plotly`: Interactive charts and visualizations
- `pillow`: Image processing for UI

**Interactions**:
- Provides user interface for all system functions
- Manages user authentication and sessions
- Coordinates between all backend modules
- Displays real-time status and results
- Handles user input and configuration

**Key Functions**:
```python
# Main application
main() -> None

# Render dashboard
render_dashboard() -> None

# Handle authentication
authenticate_user(username: str, password: str) -> bool
```

### Authentication Module (`src/ui/auth/`)

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