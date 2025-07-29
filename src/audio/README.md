# Audio Module for TalkBridge

This module provides comprehensive audio capabilities for the TalkBridge application, including audio generation, synthesis, effects processing, and playback.

## Features

### 🎵 Audio Generation
- **Basic waveforms**: Sine, square, sawtooth, triangle waves
- **Noise generation**: White noise, pink noise
- **Frequency sweeps**: Linear and exponential sweeps
- **Chord generation**: Multi-frequency audio synthesis
- **Melody generation**: Note-based melody creation

### 🎹 Advanced Synthesis
- **ADSR envelopes**: Attack, Decay, Sustain, Release
- **Filters**: Low-pass, high-pass filters
- **LFO modulation**: Low Frequency Oscillator for modulation
- **FM synthesis**: Frequency modulation synthesis
- **AM synthesis**: Amplitude modulation synthesis
- **Polyphonic synthesis**: Multiple voice support

### 🎛️ Audio Effects
- **Reverb and delay**: Room simulation and echo effects
- **Distortion and overdrive**: Harmonic distortion
- **Chorus and flanger**: Modulation effects
- **Compression and limiting**: Dynamic range processing
- **EQ and filtering**: 3-band equalizer
- **Bit crusher**: Digital distortion effects
- **Ring modulator**: Frequency modulation effects

### 🎧 Audio Playback
- **Audio streaming**: Real-time audio streaming
- **Playlist management**: Track organization and playback
- **File I/O**: WAV file support
- **Volume control**: Playback volume adjustment
- **Audio processing chains**: Multiple effects in sequence

## Installation

Make sure you have the required dependencies:

```bash
pip install numpy sounddevice scipy wave
```

## Quick Start

### Basic Audio Generation

```python
from audio import AudioGenerator

# Create audio generator
generator = AudioGenerator()

# Generate a sine wave
sine_wave = generator.generate_sine_wave(frequency=440, duration=2.0)
generator.play_audio(sine_wave)

# Generate a chord
chord = generator.generate_chord([261.63, 329.63, 392.00], duration=2.0)
generator.play_audio(chord)

# Generate a melody
melody = generator.generate_melody([
    ('C', 1.0), ('D', 1.0), ('E', 1.0), ('F', 1.0),
    ('G', 1.0), ('A', 1.0), ('B', 1.0), ('C', 2.0)
], tempo=120)
generator.play_audio(melody)
```

### Advanced Synthesis

```python
from audio import AudioSynthesizer

# Create synthesizer
synth = AudioSynthesizer()

# Create ADSR envelope
envelope = synth.ADSREnvelope(attack=0.1, decay=0.2, sustain=0.6, release=0.3)

# Create filters
lowpass = synth.LowPassFilter(1000, synth.sample_rate)
highpass = synth.HighPassFilter(500, synth.sample_rate)

# Create LFO
lfo = synth.LFO(5.0, 'sine')

# Generate voice with envelope and filters
voice_id = synth.create_voice(440, 2.0, envelope, [lowpass])
synth.play_voice(voice_id)

# Generate FM synthesis
fm_audio = synth.generate_fm_synthesis(440, 220, 5.0, 2.0, envelope)
synth.play_audio(fm_audio)
```

### Audio Effects

```python
from audio import AudioEffects

# Create effects processor
effects = AudioEffects()

# Generate test audio
import numpy as np
t = np.linspace(0, 3, 44100 * 3, False)
test_audio = np.sin(2 * np.pi * 440 * t)

# Apply reverb
reverb_audio = effects.apply_reverb(test_audio, room_size=0.7, wet_level=0.4)
effects.play_audio(reverb_audio)

# Apply effects chain
effects_chain = [
    ('compressor', {'threshold': -20, 'ratio': 2}),
    ('eq', {'low_gain': 1.2, 'mid_gain': 0.9, 'high_gain': 1.1}),
    ('reverb', {'room_size': 0.5, 'wet_level': 0.3}),
    ('limiter', {'threshold': 0.8})
]

processed_audio = effects.apply_effects_chain(test_audio, effects_chain)
effects.play_audio(processed_audio)
```

### Audio Playback

```python
from audio import AudioPlayer

# Create audio player
player = AudioPlayer()

# Generate and save audio
generator = AudioGenerator()
audio = generator.generate_sine_wave(440, 2.0)
player.save_audio_file(audio, "test_audio.wav")

# Create playlist
player.playlist = [
    {'name': 'Test Audio', 'file': 'test_audio.wav', 'duration': 2.0},
    {'name': 'Generated Tone', 'file': None, 'duration': 1.0}
]

# Set up callbacks
def on_track_change(track):
    print(f"Now playing: {track['name']}")

player.on_track_change = on_track_change

# Play playlist
player.play_playlist()
```

## Integration with TalkBridge

### Audio Generation for Notifications

```python
from audio import AudioGenerator
from audio.effects import AudioEffects

def create_notification_sound():
    generator = AudioGenerator()
    effects = AudioEffects()
    
    # Generate notification tone
    tone = generator.generate_sine_wave(800, 0.5)
    
    # Apply effects
    processed = effects.apply_compressor(tone, threshold=-20, ratio=4)
    processed = effects.apply_limiter(processed, threshold=0.8)
    
    return processed

# Use in your application
notification = create_notification_sound()
generator.play_audio(notification)
```

### Audio Processing Pipeline

```python
from audio import AudioCapture, AudioGenerator, AudioEffects

def audio_processing_pipeline():
    capture = AudioCapture()
    generator = AudioGenerator()
    effects = AudioEffects()
    
    def process_audio_callback(indata, frames, time_info, status):
        # Process captured audio
        audio_data = indata.flatten()
        
        # Apply effects
        processed = effects.apply_eq(audio_data, low_gain=1.2, high_gain=1.1)
        
        # Generate response audio
        response = generator.generate_sine_wave(440, 0.1)
        
        return processed, response
    
    return process_audio_callback
```

## Configuration

### Audio Generator Settings

```python
generator = AudioGenerator(sample_rate=44100)

# Customize parameters
generator.sample_rate = 48000  # Higher sample rate
```

### Effects Settings

```python
effects = AudioEffects(sample_rate=44100)

# Reverb settings
reverb_params = {
    'room_size': 0.7,    # Room size (0.0 to 1.0)
    'damping': 0.3,      # Damping factor (0.0 to 1.0)
    'wet_level': 0.4     # Wet signal level (0.0 to 1.0)
}

# Delay settings
delay_params = {
    'delay_time': 0.5,   # Delay time in seconds
    'feedback': 0.3,     # Feedback amount (0.0 to 1.0)
    'wet_level': 0.6     # Wet signal level (0.0 to 1.0)
}
```

### Synthesizer Settings

```python
synth = AudioSynthesizer(sample_rate=44100)

# ADSR envelope settings
envelope = synth.ADSREnvelope(
    attack=0.1,    # Attack time in seconds
    decay=0.2,     # Decay time in seconds
    sustain=0.6,   # Sustain level (0.0 to 1.0)
    release=0.3    # Release time in seconds
)

# Filter settings
lowpass = synth.LowPassFilter(cutoff_freq=1000, sample_rate=44100)
highpass = synth.HighPassFilter(cutoff_freq=500, sample_rate=44100)
```

## Demo

Run the comprehensive demo to see all audio capabilities in action:

```bash
cd src
python audio_demo.py
```

This will showcase:
- Basic audio generation (sine, square, sawtooth, triangle waves)
- Noise generation (white, pink)
- Frequency sweeps and chords
- Melody generation
- Advanced synthesis (ADSR, filters, LFO, FM/AM)
- Audio effects (reverb, delay, distortion, chorus, flanger)
- Audio playback and streaming
- Audio file I/O and playlist management

## API Reference

### AudioGenerator

- `generate_sine_wave(frequency, duration, amplitude)` - Generate sine wave
- `generate_square_wave(frequency, duration, amplitude)` - Generate square wave
- `generate_sawtooth_wave(frequency, duration, amplitude)` - Generate sawtooth wave
- `generate_triangle_wave(frequency, duration, amplitude)` - Generate triangle wave
- `generate_white_noise(duration, amplitude)` - Generate white noise
- `generate_pink_noise(duration, amplitude)` - Generate pink noise
- `generate_frequency_sweep(start_freq, end_freq, duration, amplitude, sweep_type)` - Generate frequency sweep
- `generate_chord(frequencies, duration, amplitude)` - Generate chord
- `generate_melody(notes, tempo, amplitude)` - Generate melody
- `play_audio(audio, blocking)` - Play audio data
- `save_audio(audio, filename)` - Save audio to file

### AudioSynthesizer

- `ADSREnvelope(attack, decay, sustain, release)` - Create ADSR envelope
- `LowPassFilter(cutoff_freq, sample_rate)` - Create low-pass filter
- `HighPassFilter(cutoff_freq, sample_rate)` - Create high-pass filter
- `LFO(frequency, waveform)` - Create LFO
- `create_voice(frequency, duration, envelope, filters, lfo)` - Create synthesizer voice
- `generate_polyphonic_chord(frequencies, duration, envelope)` - Generate polyphonic chord
- `generate_fm_synthesis(carrier_freq, modulator_freq, modulation_index, duration, envelope)` - Generate FM synthesis
- `generate_am_synthesis(carrier_freq, modulator_freq, modulation_depth, duration, envelope)` - Generate AM synthesis

### AudioEffects

- `apply_reverb(audio, room_size, damping, wet_level)` - Apply reverb
- `apply_delay(audio, delay_time, feedback, wet_level)` - Apply delay
- `apply_distortion(audio, drive, mix)` - Apply distortion
- `apply_chorus(audio, rate, depth, mix)` - Apply chorus
- `apply_flanger(audio, rate, depth, feedback, mix)` - Apply flanger
- `apply_compressor(audio, threshold, ratio, attack, release)` - Apply compression
- `apply_limiter(audio, threshold)` - Apply limiting
- `apply_eq(audio, low_gain, mid_gain, high_gain)` - Apply 3-band EQ
- `apply_bit_crusher(audio, bit_depth, sample_rate_reduction)` - Apply bit crusher
- `apply_ring_modulator(audio, frequency, mix)` - Apply ring modulation
- `apply_effects_chain(audio, effects)` - Apply effects chain

### AudioPlayer

- `load_audio_file(filename)` - Load audio from file
- `save_audio_file(audio, filename)` - Save audio to file
- `play_audio(audio, blocking)` - Play audio data
- `start_streaming(audio_callback)` - Start audio streaming
- `stop_streaming()` - Stop audio streaming
- `set_volume(volume)` - Set playback volume
- `add_to_playlist(track_info)` - Add track to playlist
- `load_playlist(playlist_file)` - Load playlist from file
- `save_playlist(playlist_file)` - Save playlist to file
- `play_playlist(start_index)` - Start playing playlist
- `next_track()` - Skip to next track
- `previous_track()` - Go to previous track
- `pause()` - Pause playback
- `resume()` - Resume playback
- `stop()` - Stop playback

## Troubleshooting

### Common Issues

1. **Audio device errors**: Ensure sounddevice is properly installed and audio devices are available
2. **Performance issues**: Reduce audio complexity or increase buffer sizes
3. **File format errors**: Ensure audio files are in supported formats (WAV)
4. **Memory issues**: Process audio in smaller chunks for large files

### Dependencies

Make sure all required packages are installed:

```bash
pip install -r requirements.txt
```

## Contributing

To add new audio capabilities:

1. Create a new class inheriting from appropriate base classes
2. Implement the required methods
3. Add the new class to the appropriate `__init__.py` file
4. Update this README with usage examples

## License

This audio module is part of the TalkBridge project and follows the same license terms. 