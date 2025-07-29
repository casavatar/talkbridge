# Animation Module for TalkBridge

This module provides comprehensive animation capabilities for the TalkBridge application, including audio visualizations, loading animations, and interactive visualizations.

## Features

### 🎵 Audio Visualizations
- **Real-time audio visualization** with multiple styles
- **Bar charts, waveforms, circular displays, and spectrum analyzers**
- **Customizable color schemes and animation parameters**
- **Thread-safe audio processing**

### ⏳ Loading Animations
- **Spinner animations** with multiple styles (dots, arrows, bars)
- **Progress bars** with ETA calculations
- **Pulse animations** for processing indicators
- **Wave animations** for loading states
- **Animation manager** for coordinating multiple animations

### 🎨 Interactive Animations
- **Particle systems** with physics simulation
- **Geometric animations** (circles, squares, triangles, polygons)
- **Waveform animations** with multiple wave types
- **Interactive controls** and real-time parameter adjustment

## Installation

Make sure you have the required dependencies:

```bash
pip install numpy matplotlib sounddevice scipy requests
```

## Quick Start

### Basic Usage

```python
from animation import AudioVisualizer, LoadingAnimation, InteractiveAnimations

# Create a loading spinner
spinner = LoadingAnimation("Processing...")
spinner.start()
# ... do some work ...
spinner.stop()

# Create an audio visualizer
visualizer = AudioVisualizer("bars")
visualizer.start_visualization(audio_callback)
```

### Loading Animations

```python
from animation.loading_animation import SpinnerAnimation, ProgressBar, PulseAnimation

# Spinner with different styles
spinner = SpinnerAnimation("Loading...", style="dots")
spinner.start()
time.sleep(2)
spinner.stop()

# Progress bar
progress = ProgressBar(100, 50, "Processing files")
progress.start()
for i in range(0, 101, 10):
    progress.update(i)
    time.sleep(0.1)
progress.stop()

# Pulse animation
pulse = PulseAnimation("Processing data...")
pulse.start()
time.sleep(3)
pulse.stop()
```

### Audio Visualizations

```python
from animation.audio_visualizer import AudioVisualizer

# Create visualizer with different styles
styles = ['bars', 'wave', 'circular', 'spectrum']

for style in styles:
    visualizer = AudioVisualizer(style)
    
    def audio_callback():
        # Return your audio data here
        import numpy as np
        return np.random.rand(1024) * 0.5
    
    visualizer.start_visualization(audio_callback)
    time.sleep(5)
    visualizer.stop()
```

### Interactive Animations

```python
from animation.interactive_animations import ParticleSystem, GeometricAnimation, WaveformAnimation

# Particle system
particles = ParticleSystem(100)
particles.start()
time.sleep(5)
particles.stop()

# Geometric animations
shapes = ['circle', 'square', 'triangle', 'polygon']
for shape in shapes:
    geo_anim = GeometricAnimation(shape)
    geo_anim.start()
    time.sleep(3)
    geo_anim.stop()

# Waveform animation
wave_anim = WaveformAnimation(frequency=2.0, amplitude=1.0)
wave_anim.start()
time.sleep(5)
wave_anim.stop()
```

### Animation Manager

```python
from animation.interactive_animations import InteractiveAnimations

# Create animation manager
manager = InteractiveAnimations()

# Create different animations
manager.create_particle_system("particles", 50)
manager.create_geometric_animation("circle", "circle")
manager.create_waveform_animation("waves", 1.5, 0.8)

# Start animations
for name in manager.list_animations():
    manager.start_animation(name)
    time.sleep(2)
    manager.stop_animation(name)
```

## Integration with TalkBridge

### Audio Processing Integration

```python
from animation.audio_visualizer import AudioVisualizer
from audio.capture import AudioCapture

def audio_callback(indata, frames, time_info, status):
    # Process audio data and return for visualization
    return indata.flatten()

# Initialize audio capture and visualizer
audio = AudioCapture()
visualizer = AudioVisualizer("bars")

# Start both audio capture and visualization
audio.start_input_stream(audio_callback)
visualizer.start_visualization(audio_callback)
```

### Loading States for LLM Operations

```python
from animation.loading_animation import SpinnerAnimation
from llm.ollama_client import OllamaClient

def process_with_llm():
    spinner = SpinnerAnimation("Generating response...", style="dots")
    spinner.start()
    
    try:
        client = OllamaClient()
        response = client.generate("Hello, how are you?")
        return response
    finally:
        spinner.stop()
```

## Configuration

### Audio Visualizer Settings

```python
visualizer = AudioVisualizer(
    style="bars",  # 'bars', 'wave', 'circular', 'spectrum'
)

# Customize parameters
visualizer.bar_count = 64
visualizer.max_amplitude = 2.0
visualizer.smoothing_factor = 0.9
```

### Loading Animation Settings

```python
spinner = SpinnerAnimation(
    message="Loading...",
    style="dots",  # 'dots', 'arrows', 'bars', 'dots2'
    speed=0.1
)

progress = ProgressBar(
    total=100,
    width=50,
    message="Progress"
)
```

## Demo

Run the comprehensive demo to see all animations in action:

```bash
cd src
python animation_demo.py
```

This will showcase:
- All loading animation styles
- Interactive particle systems
- Geometric shape animations
- Waveform visualizations
- Audio visualizer styles

## API Reference

### AudioVisualizer

- `__init__(style="bars")` - Initialize with animation style
- `start_visualization(audio_callback)` - Start visualization with audio data callback
- `stop()` - Stop visualization
- `change_style(style)` - Change animation style

### LoadingAnimation (Base Class)

- `__init__(message="Loading...", speed=0.1)` - Initialize with message and speed
- `start()` - Start animation
- `stop()` - Stop animation

### SpinnerAnimation

- `__init__(message="Loading...", style="dots")` - Initialize spinner
- Available styles: 'dots', 'arrows', 'bars', 'dots2'

### ProgressBar

- `__init__(total=100, width=50, message="Progress")` - Initialize progress bar
- `update(value)` - Update progress value

### InteractiveAnimations

- `create_particle_system(name, num_particles)` - Create particle system
- `create_geometric_animation(name, shape)` - Create geometric animation
- `create_waveform_animation(name, frequency, amplitude)` - Create waveform
- `start_animation(name)` - Start specific animation
- `stop_animation(name)` - Stop specific animation
- `list_animations()` - List all animations

## Troubleshooting

### Common Issues

1. **Matplotlib backend errors**: Use `matplotlib.use('TkAgg')` or `matplotlib.use('Agg')` for headless environments
2. **Audio device errors**: Ensure sounddevice is properly installed and audio devices are available
3. **Performance issues**: Reduce animation complexity or increase update intervals

### Dependencies

Make sure all required packages are installed:

```bash
pip install -r requirements.txt
```

## Contributing

To add new animation types:

1. Create a new class inheriting from `LoadingAnimation` or appropriate base class
2. Implement the required methods (`_animate()` for loading animations)
3. Add the new class to the appropriate `__init__.py` file
4. Update this README with usage examples

## License

This animation module is part of the TalkBridge project and follows the same license terms. 