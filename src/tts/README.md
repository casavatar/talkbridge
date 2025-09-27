# TTS (Text-to-Speech) Module

A comprehensive text-to-speech synthesis module with voice cloning capabilities using Coqui TTS framework. This module provides offline speech synthesis that works on both Windows and macOS.

## Features

- **Offline Speech Synthesis**: Works completely offline without internet connection
- **Voice Cloning**: Clone voices from reference audio samples
- **Multi-language Support**: Supports multiple languages for synthesis
- **Low Latency**: Optimized for real-time use
- **Cross-platform**: Works on Windows and macOS
- **Flexible Output**: Returns audio as bytes or saves to file

## Installation

### Prerequisites

- Python 3.8 or higher
- PyTorch (will be installed automatically with TTS)

### Dependencies

Install the required dependencies:

```bash
pip install -r requirements.txt
```

The TTS module requires these additional packages:

- `TTS>=0.22.0` - Coqui TTS framework
- `librosa>=0.10.0` - Audio processing
- `torchaudio>=0.12.0` - Audio operations
- `soundfile>=0.12.0` - Audio file I/O

## Quick Start

### Basic Usage

```python
from src.tts import synthesize_voice

# Basic text-to-speech synthesis
audio_bytes = synthesize_voice("Hello, world!")
print(f"Generated {len(audio_bytes)} bytes of audio")

# Save to file
synthesize_voice("Hello, world!", output_path="output.wav")
```

### Voice Cloning

```python
from src.tts import synthesize_voice, setup_voice_cloning

# Set up voice cloning with reference samples
reference_samples = ["voice_sample_1.wav", "voice_sample_2.wav"]
setup_voice_cloning(reference_samples)

# Synthesize with cloned voice
audio_bytes = synthesize_voice(
    text="This will sound like the reference voice",
    reference_samples=reference_samples
)
```

### Advanced Usage

```python
from src.tts import synthesize_voice, get_synthesis_info

# Multi-language synthesis
texts = {
    "en": "Hello, this is English",
    "es": "Hola, esto es español",
    "fr": "Bonjour, c'est français"
}

for language, text in texts.items():
    synthesize_voice(
        text=text,
        output_path=f"output_{language}.wav",
        language=language
    )

# Get system information
info = get_synthesis_info()
print(f"Model: {info['model_name']}")
print(f"Device: {info['device']}")
```

## API Reference

### Main Functions

#### `synthesize_voice(text, output_path=None, reference_samples=None, language="en", clone_voice=True)`

Main function for text-to-speech synthesis.

**Parameters:**

- `text` (str): Text to synthesize
- `output_path` (str, optional): Path to save audio file
- `reference_samples` (List[str], optional): Audio files for voice cloning
- `language` (str): Language code (default: "en")
- `clone_voice` (bool): Whether to use voice cloning (default: True)

**Returns:**

- `bytes` or `str`: Audio data as bytes or file path

#### `setup_voice_cloning(reference_samples)`

Pre-configure voice cloning for better performance.

**Parameters:**

- `reference_samples` (List[str]): Audio file paths for voice cloning

**Returns:**

- `bool`: True if setup was successful

#### `get_synthesis_info()`

Get information about the current synthesis setup.

**Returns:**

- `dict`: System information including model name, device, etc.

#### `list_available_models()`

Get list of available TTS models.

**Returns:**

- `List[str]`: Available model names

### VoiceCloner Class

The `VoiceCloner` class provides lower-level access to voice cloning functionality:

```python
from src.tts import VoiceCloner

# Initialize voice cloner
cloner = VoiceCloner()

# Clone voice from samples
success = cloner.clone_voice_from_samples(["sample1.wav", "sample2.wav"])

# Synthesize with cloned voice
audio_bytes = cloner.synthesize_with_cloned_voice("Hello, world!")
```

## Voice Cloning Guide

### Preparing Reference Audio

For best voice cloning results:

1. **Audio Quality**: Use high-quality audio (44.1kHz, 16-bit or higher)
2. **Duration**: Each sample should be 3-10 seconds long
3. **Content**: Use clear speech with minimal background noise
4. **Format**: WAV, MP3, or FLAC files are supported
5. **Quantity**: 1-3 samples usually provide good results

### Example Reference Audio Setup

```python
# Create reference samples
reference_samples = [
    "my_voice_sample_1.wav",  # 5 seconds of clear speech
    "my_voice_sample_2.wav",  # Another 5 seconds, different content
]

# Set up voice cloning
setup_voice_cloning(reference_samples)

# Use for multiple synthesis calls
texts = [
    "Hello, this is my cloned voice.",
    "I can speak in different languages.",
    "The voice cloning works very well."
]

for text in texts:
    audio_bytes = synthesize_voice(text, reference_samples=reference_samples)
```

## Error Handling

The module includes comprehensive error handling:

```python
try:
    audio_bytes = synthesize_voice("Hello, world!")
except ValueError as e:
    print(f"Invalid input: {e}")
except RuntimeError as e:
    print(f"Synthesis failed: {e}")
except FileNotFoundError as e:
    print(f"Reference file not found: {e}")
```

## Performance Optimization

### For Real-time Use

1. **Pre-load the model**: The module automatically caches the TTS model
2. **Reuse voice cloning**: Set up voice cloning once and reuse for multiple calls
3. **Use appropriate text length**: Shorter texts (1-2 sentences) work faster
4. **GPU acceleration**: The module automatically uses CUDA if available

### Memory Management

The module uses lazy loading and caching to minimize memory usage:

```python
# Model is loaded only when first used
from src.tts import synthesize_voice

# First call loads the model
audio1 = synthesize_voice("First call")

# Subsequent calls reuse the loaded model
audio2 = synthesize_voice("Second call")
```

## Troubleshooting

### Common Issues

1. **Model Download Fails**
   - Check internet connection for initial model download
   - Models are cached locally after first download

2. **Voice Cloning Quality**
   - Ensure reference audio is clear and high-quality
   - Try different reference samples
   - Increase sample duration (5-10 seconds)

3. **Memory Issues**
   - Close other applications to free memory
   - Use shorter text inputs
   - Consider using CPU instead of GPU

4. **Audio Quality Issues**
   - Check audio file format and quality
   - Ensure sample rate compatibility
   - Verify output path permissions

### System Requirements

- **Minimum**: 4GB RAM, 2GB free disk space
- **Recommended**: 8GB RAM, 5GB free disk space, GPU with 4GB VRAM
- **OS**: Windows 10+ or macOS 10.14+

## Demo

Run the demo script to see the module in action:

```bash
cd src
python tts_demo.py
```

This will:

- Show system information
- Demonstrate basic synthesis
- Create demo voice samples
- Test voice cloning
- Show multilingual capabilities

## License

This module is part of the TalkBridge project and follows the same license terms.

## Contributing

When contributing to the TTS module:

1. Follow the existing code style
2. Add comprehensive error handling
3. Include docstrings for new functions
4. Test on both Windows and macOS
5. Update this README for new features
