# Animation Module

A comprehensive animation module for TalkBridge that provides real-time facial animation, lip sync, audio visualization, and interactive animations.

## Features

- **Real-time Facial Animation**: Live facial landmark detection and animation
- **Lip Sync**: Synchronized lip movements with audio playback
- **Eye Blinking**: Natural eye blinking animations
- **Webcam Support**: Real-time webcam input processing
- **Avatar Support**: Static avatar image animation
- **Audio Visualization**: Real-time audio waveform visualization
- **Interactive Animations**: Dynamic visual effects and transitions
- **Cross-platform**: Works on Windows and macOS

## Installation

### Prerequisites

- Python 3.8 or higher
- Webcam (for real-time face sync)
- Audio output device

### Dependencies

Install the required dependencies:

```bash
pip install -r requirements.txt
```

The animation module requires these additional packages:
- `mediapipe>=0.10.0` - Facial landmark detection
- `opencv-python>=4.8.0` - Computer vision and video processing
- `pygame>=2.5.0` - Audio playback and timing

## Quick Start

### Basic Face Sync

```python
from src.animation import FaceSync

# Create face sync with webcam
face_sync = FaceSync(use_webcam=True)

# Run face sync with audio
face_sync.run_face_sync("audio_file.wav")
```

### Avatar Face Sync

```python
from src.animation import FaceSync

# Create face sync with static avatar
face_sync = FaceSync(use_webcam=False, avatar_path="avatar.jpg")

# Run face sync with audio
face_sync.run_face_sync("audio_file.wav")
```

### Facial Landmark Detection

```python
from src.animation import FaceSync

# Create face sync for landmark detection
face_sync = FaceSync(use_webcam=True)

# Get current frame
frame = face_sync.get_frame()

# Detect landmarks
landmarks_data = face_sync.detect_facial_landmarks(frame)

if landmarks_data:
    print(f"Mouth opening: {landmarks_data['mouth_open']}")
    print(f"Eye blink: {landmarks_data['eye_blink']}")
```

## API Reference

### FaceSync Class

The main class for real-time facial animation and lip sync.

#### `__init__(use_webcam=True, avatar_path=None)`

Initialize the face sync system.

**Parameters:**
- `use_webcam` (bool): Whether to use webcam input (True) or static avatar (False)
- `avatar_path` (str, optional): Path to static avatar image (used when use_webcam=False)

#### `run_face_sync(audio_path)`

Main function to run face sync with audio.

**Parameters:**
- `audio_path` (str): Path to audio file for lip sync

**Returns:**
- `bool`: True if face sync completed successfully

#### `detect_facial_landmarks(frame)`

Detect facial landmarks using MediaPipe.

**Parameters:**
- `frame` (np.ndarray): Input image frame

**Returns:**
- `Dict[str, Any]` or `None`: Facial landmark data or None if no face detected

#### `load_audio(audio_path)`

Load audio file for lip sync.

**Parameters:**
- `audio_path` (str): Path to audio file

**Returns:**
- `bool`: True if audio loaded successfully

#### `get_frame()`

Get current frame from webcam or avatar.

**Returns:**
- `np.ndarray` or `None`: Current frame as numpy array

#### `process_frame(frame, animation_state)`

Process frame with facial animation overlays.

**Parameters:**
- `frame` (np.ndarray): Input frame
- `animation_state` (Dict[str, Any]): Current animation state

**Returns:**
- `np.ndarray`: Processed frame with animations

#### `stop()`

Stop the face sync process and cleanup resources.

## Facial Landmark Detection

The module uses MediaPipe for real-time facial landmark detection:

### Landmark Indices

- **Lip Landmarks**: 61, 84, 17, 314, 405, 320, 307, 375, 321, 308, 324, 318
- **Left Eye**: 362, 382, 381, 380, 374, 373, 390, 249, 263, 466, 388, 387
- **Right Eye**: 33, 7, 163, 144, 145, 153, 154, 155, 133, 173, 157, 158

### Features Extracted

- **Mouth Opening**: Calculated from vertical distance between upper and lower lip
- **Eye Blink**: Calculated using Eye Aspect Ratio (EAR)
- **Facial Expressions**: Basic expression classification based on audio features

## Audio Analysis

The module analyzes audio for lip sync:

### Audio Features

- **Energy**: RMS energy for mouth opening intensity
- **Frame Rate**: 30 FPS for smooth animation
- **Synchronization**: Audio playback synchronized with visual animation

### Animation State

```python
animation_state = {
    'mouth_open': 0.0,      # 0.0 to 1.0
    'eye_blink': 0.0,       # 0.0 to 1.0
    'expression': 'neutral'  # 'neutral', 'speaking', 'quiet'
}
```

## Integration with TTS

The face sync module integrates seamlessly with the TTS module:

```python
from src.tts import synthesize_voice
from src.animation import FaceSync

# Generate audio with TTS
audio_bytes = synthesize_voice("Hello, this is a test message.")

# Save audio to file
with open("tts_output.wav", "wb") as f:
    f.write(audio_bytes)

# Use with face sync
face_sync = FaceSync(use_webcam=True)
face_sync.run_face_sync("tts_output.wav")
```

## Performance Optimization

### For Real-time Use

1. **GPU Acceleration**: MediaPipe automatically uses GPU if available
2. **Frame Rate**: 30 FPS for smooth animation
3. **Landmark Caching**: Reuses landmark detection for efficiency
4. **Audio Preprocessing**: Audio features extracted once for entire duration

### Memory Management

- Automatic cleanup of video capture and audio resources
- Efficient landmark detection with MediaPipe
- Minimal memory footprint for real-time processing

## Error Handling

The module includes comprehensive error handling:

```python
try:
    face_sync = FaceSync(use_webcam=True)
    success = face_sync.run_face_sync("audio.wav")
except RuntimeError as e:
    print(f"Face sync failed: {e}")
except FileNotFoundError as e:
    print(f"Audio file not found: {e}")
```

## Troubleshooting

### Common Issues

1. **Webcam Not Found**
   - Ensure webcam is connected and not in use by other applications
   - Check webcam permissions on macOS

2. **Audio Playback Issues**
   - Verify audio file format (WAV, MP3 supported)
   - Check audio device settings

3. **Performance Issues**
   - Reduce frame rate if needed
   - Close other applications to free resources
   - Use GPU acceleration if available

4. **Landmark Detection Issues**
   - Ensure good lighting conditions
   - Position face clearly in camera view
   - Check MediaPipe installation

### System Requirements

- **Minimum**: 4GB RAM, 2GB free disk space
- **Recommended**: 8GB RAM, GPU with 2GB VRAM
- **OS**: Windows 10+ or macOS 10.14+

## Demo

Run the demo script to see the module in action:

```bash
cd src/animation
python face_sync_demo.py
```

This will:
- Test facial landmark detection
- Demonstrate webcam face sync
- Show avatar face sync (if avatar image provided)
- Create test audio files

## Examples

See `src/animation_example.py` for comprehensive usage examples:

```bash
cd src
python animation_example.py
```

## License

This module is part of the TalkBridge project and follows the same license terms.

## Contributing

When contributing to the animation module:

1. Follow the existing code style
2. Add comprehensive error handling
3. Include docstrings for new functions
4. Test on both Windows and macOS
5. Update this README for new features 