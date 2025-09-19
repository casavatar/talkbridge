# TalkBridge Demo Module

The demo module provides a complete simulation of the TalkBridge AI voice assistant system without requiring real hardware (microphone, camera) or external services (Whisper, Ollama, TTS).

## Features

- **Complete System Simulation**: Simulates all major components (audio capture, transcription, translation, LLM response, voice synthesis, avatar animation)
- **Predefined Static Files**: Uses sample files to demonstrate the full conversation flow
- **Web Interface Integration**: Seamlessly integrates with the Streamlit web interface
- **Configurable Delays**: Simulates realistic processing times for each step
- **Cross-Platform**: Works on Windows and macOS
- **Fully Offline**: No internet connection required

## Quick Start

### 1. Enable Demo Mode

Edit `src/demo/demo_config.py` and set:
```python
DEMO_MODE = True
```

### 2. Run Demo Tests

```bash
# Test the demo system
python src/demo/run_demo.py --test

# Run a demo conversation
python src/demo/run_demo.py --run

# Show configuration
python src/demo/run_demo.py --config
```

### 3. Run Web Demo

```bash
# Run standalone demo interface
streamlit run src/demo/demo_ui.py

# Or integrate with main web interface
streamlit run src/ui/web_interface.py
```

## Demo Files

The demo system uses predefined files in `src/demo/samples/`:

- `input_audio.wav`: Simulated user audio input
- `transcribed.txt`: Transcribed text from audio
- `translation.txt`: Spanish translation of transcribed text
- `response.txt`: AI-generated response
- `voice_output.wav`: Synthesized voice audio
- `mock_avatar.jpg`: Avatar image for display
- `conversation_log.jsonl`: Conversation history

## Configuration

### Demo Settings

Edit `src/demo/demo_config.py` to customize:

```python
DEMO_SETTINGS = {
    "enabled": True,
    "simulate_delays": True,
    "delay_audio_processing": 1.5,
    "delay_transcription": 2.0,
    "delay_translation": 1.0,
    "delay_llm_response": 3.0,
    "delay_voice_synthesis": 2.5,
    "delay_avatar_animation": 0.5,
}
```

### Conversation Flow

The demo follows this conversation flow:

1. **User Input**: Simulate audio capture
2. **Transcription**: Process speech-to-text
3. **Translation**: Translate English to Spanish
4. **LLM Response**: Generate AI response
5. **Voice Synthesis**: Convert text to speech
6. **Avatar Animation**: Synchronize facial movements

## API Integration

The demo provides API wrappers that match the real APIs:

```python
from demo.demo_api import (
    get_tts_api, get_stt_api, get_llm_api,
    get_translation_api, get_animation_api, get_audio_api
)

# Use demo APIs
tts_api = get_tts_api()
audio_data = tts_api.synthesize_voice("Hello world")

stt_api = get_stt_api()
transcription = stt_api.transcribe_audio(audio_data)
```

## Web Interface Components

### Demo Dashboard

The demo dashboard includes:

- **Demo Header**: Shows demo mode status
- **System Status**: Displays metrics and status
- **Audio Recording**: Simulated audio capture
- **Transcription**: Speech-to-text processing
- **Translation**: English to Spanish translation
- **AI Response**: LLM response generation
- **Voice Synthesis**: Text-to-speech conversion
- **Avatar Display**: Static avatar with animations
- **Conversation History**: Log of all conversations
- **Settings Panel**: Demo configuration

### Usage in Web Interface

```python
from demo.demo_ui import render_demo_dashboard

# In your Streamlit app
if is_demo_mode():
    render_demo_dashboard()
else:
    # Render real interface
    render_real_dashboard()
```

## Demo Runner

The `DemoRunner` class provides the core simulation functionality:

```python
from demo.demo_runner import get_demo_runner

demo_runner = get_demo_runner()

# Run full conversation
results = demo_runner.run_full_conversation()

# Get conversation history
history = demo_runner.get_conversation_history()

# Reset demo state
demo_runner.reset_demo()
```

## Error Handling

The demo system includes comprehensive error handling:

- Graceful fallbacks for missing files
- Error logging to `logs/errors.log`
- User-friendly error messages
- Automatic file creation for missing samples

## Customization

### Adding Custom Demo Files

1. Place your files in `src/demo/samples/`
2. Update `DEMO_FILES` in `demo_config.py`
3. Modify the demo runner to use your files

### Custom Conversation Flow

Edit `DEMO_CONVERSATION_FLOW` in `demo_config.py`:

```python
DEMO_CONVERSATION_FLOW = [
    {
        "step": "custom_step",
        "description": "Custom processing step",
        "file": "custom_file.txt",
        "delay": 1.0
    }
]
```

### Custom API Wrappers

Create custom API wrappers by extending the base classes:

```python
class CustomDemoAPI(DemoTTsAPI):
    def synthesize_voice(self, text: str) -> bytes:
        # Custom implementation
        return custom_audio_data
```

## Testing

### Unit Tests

```bash
# Run demo tests
python -m unittest test.test_demo

# Test specific components
python -m unittest test.test_demo.test_demo_runner
python -m unittest test.test_demo.test_demo_api
```

### Integration Tests

```bash
# Test web interface integration
python src/demo/run_demo.py --test

# Test full conversation flow
python src/demo/run_demo.py --run
```

## Troubleshooting

### Common Issues

1. **Demo files not found**: Run `ensure_demo_files_exist()` to create placeholder files
2. **Import errors**: Ensure `src` is in your Python path
3. **Web interface not loading**: Check Streamlit installation and dependencies
4. **Audio not playing**: Verify audio file format and browser compatibility

### Debug Mode

Enable debug logging:

```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

### File Permissions

Ensure the demo has write permissions to:
- `src/demo/samples/`
- `logs/`
- `data/`

## Architecture

```
src/demo/
├── __init__.py              # Module initialization
├── demo_config.py           # Configuration and settings
├── demo_runner.py           # Main demo runner
├── demo_api.py              # API wrappers
├── demo_ui.py               # Streamlit UI components
├── run_demo.py              # Standalone runner script
├── README.md                # This file
└── samples/                 # Demo files
    ├── input_audio.wav
    ├── transcribed.txt
    ├── translation.txt
    ├── response.txt
    ├── voice_output.wav
    ├── mock_avatar.jpg
    └── conversation_log.jsonl
```

## Dependencies

- **Standard Libraries**: `os`, `time`, `json`, `datetime`, `pathlib`
- **Streamlit**: For web interface components
- **PIL**: For image processing (optional)
- **wave**: For audio file handling (optional)

## License

This demo module is part of the TalkBridge project and follows the same license terms.

## Support

For issues and questions:
1. Check the troubleshooting section
2. Review the error logs in `logs/errors.log`
3. Test with `python src/demo/run_demo.py --test`
4. Create an issue in the project repository 