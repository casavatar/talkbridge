# STT (Speech-to-Text) Module

Offline speech-to-text functionality using OpenAI's Whisper model for the TalkBridge project.

## Features

- **Offline Operation**: No internet connection required after model download
- **Multi-language Support**: Supports 20+ languages including Spanish, English, French, German, etc.
- **Cross-platform**: Works on Windows, macOS, and Linux
- **Device Optimization**: Automatic detection of CPU/GPU/MPS for optimal performance
- **Modular Design**: Easy to extend with other STT engines (Vosk, Faster-Whisper, etc.)
- **Clean API**: Simple interface for transcription tasks

## Installation

### Prerequisites

1. **Python 3.8+**
2. **FFmpeg** (for audio format conversion)
   ```bash
   # Ubuntu/Debian
   sudo apt install ffmpeg
   
   # macOS
   brew install ffmpeg
   
   # Windows
   # Download from https://ffmpeg.org/download.html
   ```

### Dependencies

Install required Python packages:

```bash
pip install openai-whisper torch numpy
```

## Quick Start

### Basic Usage

```python
from src.stt import transcribe_audio, transcribe_file

# Transcribe audio bytes
audio_bytes = b'...'  # Your audio data
text = transcribe_audio(audio_bytes)
print(f"Transcribed text: {text}")

# Transcribe audio file
text = transcribe_file("path/to/audio.wav")
print(f"Transcribed text: {text}")
```

### Advanced Usage

```python
from src.stt import (
    transcribe_audio, 
    load_model, 
    get_model_info,
    get_supported_languages
)

# Load model explicitly
load_model("base")  # Options: tiny, base, small, medium, large

# Check model status
info = get_model_info()
print(f"Model: {info['model_name']}, Device: {info['device']}")

# Get supported languages
languages = get_supported_languages()
print(f"Supported languages: {languages}")

# Transcribe with specific language
text = transcribe_audio(audio_bytes, language="es")
```

## API Reference

### Main Functions

#### `transcribe_audio(audio_bytes: bytes, language: str = "es") -> str`

Transcribe audio bytes to text.

**Parameters:**
- `audio_bytes`: Raw audio data as bytes
- `language`: Language code (default: "es")

**Returns:**
- Transcribed text as string

**Example:**
```python
audio_data = b'...'  # Your audio bytes
text = transcribe_audio(audio_data, language="en")
```

#### `transcribe_file(file_path: str, language: str = "es") -> str`

Transcribe audio file to text.

**Parameters:**
- `file_path`: Path to audio file
- `language`: Language code (default: "es")

**Returns:**
- Transcribed text as string

**Example:**
```python
text = transcribe_file("recording.wav", language="es")
```

#### `transcribe_with_metadata(file_path: str, language: str = "es") -> dict`

Transcribe audio file with detailed metadata.

**Returns:**
- Dictionary with transcription result and metadata including:
  - `text`: Transcribed text
  - `language`: Detected language
  - `segments`: Timestamped segments
  - `model_name`: Model used
  - `device`: Device used

### Model Management

#### `load_model(model_name: str = None) -> bool`

Load Whisper model explicitly.

**Parameters:**
- `model_name`: Model name (tiny, base, small, medium, large)

**Returns:**
- True if successful, False otherwise

#### `unload_model() -> None`

Unload model to free memory.

#### `get_model_info() -> dict`

Get information about current model.

#### `is_model_ready() -> bool`

Check if model is loaded and ready.

### Language Support

#### `get_supported_languages() -> list`

Get list of supported language codes.

#### `is_language_supported(language: str) -> bool`

Check if language is supported.

### Status and Information

#### `get_engine_status() -> dict`

Get comprehensive engine status.

## Configuration

### Model Settings

```python
from src.stt.config import MODEL_NAME, DEFAULT_LANGUAGE, DEVICE

# Available models: tiny, base, small, medium, large
MODEL_NAME = "base"  # Default model

# Default language
DEFAULT_LANGUAGE = "es"  # Spanish

# Device settings
DEVICE = "cpu"  # Options: cpu, cuda, mps
```

### Audio Settings

```python
from src.stt.config import SAMPLE_RATE, CHANNELS, MAX_AUDIO_DURATION

SAMPLE_RATE = 16000  # Hz
CHANNELS = 1  # Mono
MAX_AUDIO_DURATION = 300  # Maximum 5 minutes
```

## Supported Audio Formats

- WAV (recommended)
- MP3
- M4A
- FLAC
- OGG

## Supported Languages

- English (en)
- Spanish (es) - Default
- French (fr)
- German (de)
- Italian (it)
- Portuguese (pt)
- Russian (ru)
- Japanese (ja)
- Korean (ko)
- Chinese (zh)
- Arabic (ar)
- Hindi (hi)
- Dutch (nl)
- Polish (pl)
- Swedish (sv)
- Turkish (tr)
- Vietnamese (vi)
- Thai (th)
- Czech (cs)
- Danish (da)

## Performance Tips

### Model Selection

- **tiny**: Fastest, lowest accuracy (~39MB)
- **base**: Good balance (~74MB)
- **small**: Better accuracy (~244MB)
- **medium**: High accuracy (~769MB)
- **large**: Best accuracy (~1550MB)

### Device Optimization

- **CPU**: Compatible with all systems
- **CUDA**: NVIDIA GPUs (requires PyTorch with CUDA)
- **MPS**: Apple Silicon Macs (requires PyTorch with MPS)

### Memory Management

```python
from src.stt import unload_model

# Unload model when done
unload_model()
```

## Error Handling

```python
from src.stt import transcribe_audio

try:
    text = transcribe_audio(audio_bytes)
except ValueError as e:
    print(f"Invalid audio data: {e}")
except RuntimeError as e:
    print(f"Model loading failed: {e}")
except Exception as e:
    print(f"Transcription failed: {e}")
```

## Integration with TalkBridge

### Update STT API

Replace the placeholder implementation in `src/ui/api/stt_api.py`:

```python
from src.stt import transcribe_audio, transcribe_file

class STTAPI:
    def transcribe_audio(self, audio_data: bytes, language: str = "en") -> Optional[str]:
        try:
            return transcribe_audio(audio_data, language)
        except Exception as e:
            logger.error(f"Transcription failed: {e}")
            return None
    
    def transcribe_file(self, audio_file_path: str, language: str = "en") -> Optional[str]:
        try:
            return transcribe_file(audio_file_path, language)
        except Exception as e:
            logger.error(f"File transcription failed: {e}")
            return None
```

### Update Demo API

Update `src/demo/demo_api.py`:

```python
from src.stt import transcribe_audio

def transcribe_audio(self, audio_data: bytes) -> str:
    return transcribe_audio(audio_data, language="es")
```

## Testing

Run the existing test suite:

```bash
python -m unittest test.test_transcribe
```

## Troubleshooting

### Common Issues

1. **"Whisper not installed"**
   ```bash
   pip install openai-whisper
   ```

2. **"ffmpeg not found"**
   - Install FFmpeg (see Installation section)

3. **"CUDA not available"**
   - Install PyTorch with CUDA support
   - Or use CPU: `DEVICE = "cpu"`

4. **"Model download failed"**
   - Check internet connection for initial download
   - Verify cache directory permissions

### Performance Issues

1. **Slow transcription**
   - Use smaller model (tiny, base)
   - Use GPU if available
   - Reduce audio duration

2. **High memory usage**
   - Unload model when not needed
   - Use smaller model
   - Process shorter audio segments

## Development

### Adding New STT Engines

The modular design allows easy addition of other STT engines:

1. Create new engine class (e.g., `VoskEngine`)
2. Implement required methods
3. Update interface to support engine selection
4. Add configuration options

### Extending Language Support

1. Add language codes to `SUPPORTED_LANGUAGES`
2. Test with sample audio
3. Update documentation

## License

Part of the TalkBridge project. See main project license.

## Contributing

1. Follow existing code style
2. Add tests for new features
3. Update documentation
4. Test on multiple platforms 