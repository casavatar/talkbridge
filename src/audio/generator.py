#!/usr/bin/env python3
"""
TalkBridge Audio - Generator
============================

Módulo generator para TalkBridge

Author: TalkBridge Team
Date: 2025-08-19
Version: 1.0

Requirements:
- sounddevice
- numpy
======================================================================
Functions:
- __init__: Initialize audio generator.
- generate_sine_wave: Generate a sine wave.
- generate_square_wave: Generate a square wave.
- generate_sawtooth_wave: Generate a sawtooth wave.
- generate_triangle_wave: Generate a triangle wave.
- generate_white_noise: Generate white noise.
- generate_pink_noise: Generate pink noise (1/f noise).
- generate_frequency_sweep: Generate a frequency sweep.
- generate_chord: Generate a chord from multiple frequencies.
- generate_melody: Generate a melody from note names and durations.
======================================================================
"""

import numpy as np
import sounddevice as sd
import threading
import time
from typing import Optional, Callable, List, Tuple
import math


class AudioGenerator:
    """
    Audio generator for creating various types of audio signals.
    """
    
    def __init__(self, sample_rate: int = 44100):
        """
        Initialize audio generator.
        
        Args:
            sample_rate: Sample rate in Hz
        """
        self.sample_rate = sample_rate
        self.is_playing = False
        self.current_audio = None
        self.stream = None
        
    def generate_sine_wave(self, frequency: float, duration: float, amplitude: float = 0.5) -> np.ndarray:
        """
        Generate a sine wave.
        
        Args:
            frequency: Frequency in Hz
            duration: Duration in seconds
            amplitude: Amplitude (0.0 to 1.0)
            
        Returns:
            Audio data as numpy array
        """
        t = np.linspace(0, duration, int(self.sample_rate * duration), False)
        audio = amplitude * np.sin(2 * np.pi * frequency * t)
        return audio
    
    def generate_square_wave(self, frequency: float, duration: float, amplitude: float = 0.5) -> np.ndarray:
        """
        Generate a square wave.
        
        Args:
            frequency: Frequency in Hz
            duration: Duration in seconds
            amplitude: Amplitude (0.0 to 1.0)
            
        Returns:
            Audio data as numpy array
        """
        t = np.linspace(0, duration, int(self.sample_rate * duration), False)
        audio = amplitude * np.sign(np.sin(2 * np.pi * frequency * t))
        return audio
    
    def generate_sawtooth_wave(self, frequency: float, duration: float, amplitude: float = 0.5) -> np.ndarray:
        """
        Generate a sawtooth wave.
        
        Args:
            frequency: Frequency in Hz
            duration: Duration in seconds
            amplitude: Amplitude (0.0 to 1.0)
            
        Returns:
            Audio data as numpy array
        """
        t = np.linspace(0, duration, int(self.sample_rate * duration), False)
        audio = amplitude * (2 * (t * frequency - np.floor(t * frequency + 0.5)))
        return audio
    
    def generate_triangle_wave(self, frequency: float, duration: float, amplitude: float = 0.5) -> np.ndarray:
        """
        Generate a triangle wave.
        
        Args:
            frequency: Frequency in Hz
            duration: Duration in seconds
            amplitude: Amplitude (0.0 to 1.0)
            
        Returns:
            Audio data as numpy array
        """
        t = np.linspace(0, duration, int(self.sample_rate * duration), False)
        sawtooth = 2 * (t * frequency - np.floor(t * frequency + 0.5))
        audio = amplitude * (2 * np.abs(sawtooth) - 1)
        return audio
    
    def generate_white_noise(self, duration: float, amplitude: float = 0.5) -> np.ndarray:
        """
        Generate white noise.
        
        Args:
            duration: Duration in seconds
            amplitude: Amplitude (0.0 to 1.0)
            
        Returns:
            Audio data as numpy array
        """
        samples = int(self.sample_rate * duration)
        audio = amplitude * np.random.uniform(-1, 1, samples)
        return audio
    
    def generate_pink_noise(self, duration: float, amplitude: float = 0.5) -> np.ndarray:
        """
        Generate pink noise (1/f noise).
        
        Args:
            duration: Duration in seconds
            amplitude: Amplitude (0.0 to 1.0)
            
        Returns:
            Audio data as numpy array
        """
        samples = int(self.sample_rate * duration)
        
        # Generate white noise
        white_noise = np.random.uniform(-1, 1, samples)
        
        # Apply pink noise filter
        b = [0.049922035, -0.095993537, 0.050612699, -0.004408786]
        a = [1.0, -2.494956002, 2.017265875, -0.522189400]
        
        audio = amplitude * np.convolve(white_noise, b, mode='same')
        return audio
    
    def generate_frequency_sweep(self, start_freq: float, end_freq: float, duration: float, 
                                amplitude: float = 0.5, sweep_type: str = 'linear') -> np.ndarray:
        """
        Generate a frequency sweep.
        
        Args:
            start_freq: Starting frequency in Hz
            end_freq: Ending frequency in Hz
            duration: Duration in seconds
            amplitude: Amplitude (0.0 to 1.0)
            sweep_type: 'linear' or 'exponential'
            
        Returns:
            Audio data as numpy array
        """
        t = np.linspace(0, duration, int(self.sample_rate * duration), False)
        
        if sweep_type == 'linear':
            frequency = start_freq + (end_freq - start_freq) * t / duration
        elif sweep_type == 'exponential':
            frequency = start_freq * (end_freq / start_freq) ** (t / duration)
        else:
            raise ValueError("sweep_type must be 'linear' or 'exponential'")
        
        # Generate phase
        phase = 2 * np.pi * np.cumsum(frequency) / self.sample_rate
        audio = amplitude * np.sin(phase)
        return audio
    
    def generate_chord(self, frequencies: List[float], duration: float, amplitude: float = 0.5) -> np.ndarray:
        """
        Generate a chord from multiple frequencies.
        
        Args:
            frequencies: List of frequencies in Hz
            duration: Duration in seconds
            amplitude: Amplitude (0.0 to 1.0)
            
        Returns:
            Audio data as numpy array
        """
        t = np.linspace(0, duration, int(self.sample_rate * duration), False)
        audio = np.zeros_like(t)
        
        for freq in frequencies:
            audio += amplitude * np.sin(2 * np.pi * freq * t)
        
        # Normalize to prevent clipping
        audio = audio / len(frequencies)
        return audio
    
    def generate_melody(self, notes: List[Tuple[str, float]], tempo: float = 120.0, 
                       amplitude: float = 0.5) -> np.ndarray:
        """
        Generate a melody from note names and durations.
        
        Args:
            notes: List of (note_name, duration) tuples
            tempo: Tempo in BPM
            amplitude: Amplitude (0.0 to 1.0)
            
        Returns:
            Audio data as numpy array
        """
        # Note frequencies (A4 = 440 Hz)
        note_frequencies = {
            'C': 261.63, 'C#': 277.18, 'D': 293.66, 'D#': 311.13,
            'E': 329.63, 'F': 349.23, 'F#': 369.99, 'G': 392.00,
            'G#': 415.30, 'A': 440.00, 'A#': 466.16, 'B': 493.88
        }
        
        # Convert tempo to seconds per beat
        seconds_per_beat = 60.0 / tempo
        
        audio_segments = []
        
        for note_name, duration_beats in notes:
            if note_name == 'REST':
                # Generate silence
                duration_seconds = duration_beats * seconds_per_beat
                samples = int(self.sample_rate * duration_seconds)
                segment = np.zeros(samples)
            else:
                # Generate note
                frequency = note_frequencies.get(note_name.upper(), 440.0)
                duration_seconds = duration_beats * seconds_per_beat
                segment = self.generate_sine_wave(frequency, duration_seconds, amplitude)
            
            audio_segments.append(segment)
        
        # Concatenate all segments
        audio = np.concatenate(audio_segments)
        return audio
    
    def play_audio(self, audio: np.ndarray, blocking: bool = True):
        """
        Play audio data.
        
        Args:
            audio: Audio data as numpy array
            blocking: Whether to block until playback is complete
        """
        if blocking:
            sd.play(audio, self.sample_rate)
            sd.wait()
        else:
            sd.play(audio, self.sample_rate)
    
    def save_audio(self, audio: np.ndarray, filename: str):
        """
        Save audio data to a file.
        
        Args:
            audio: Audio data as numpy array
            filename: Output filename
        """
        import scipy.io.wavfile as wav
        wav.write(filename, self.sample_rate, audio.astype(np.float32))
    
    def generate_audio_demo(self):
        """Generate a demo of various audio types."""
        print("🎵 Audio Generator Demo")
        print("=" * 30)
        
        # Generate different types of audio
        demos = [
            ("Sine Wave (440 Hz)", self.generate_sine_wave(440, 2.0)),
            ("Square Wave (220 Hz)", self.generate_square_wave(220, 2.0)),
            ("Sawtooth Wave (330 Hz)", self.generate_sawtooth_wave(330, 2.0)),
            ("Triangle Wave (550 Hz)", self.generate_triangle_wave(550, 2.0)),
            ("White Noise", self.generate_white_noise(2.0)),
            ("Pink Noise", self.generate_pink_noise(2.0)),
            ("Frequency Sweep", self.generate_frequency_sweep(200, 2000, 3.0)),
            ("C Major Chord", self.generate_chord([261.63, 329.63, 392.00], 2.0)),
            ("Simple Melody", self.generate_melody([
                ('C', 1.0), ('D', 1.0), ('E', 1.0), ('F', 1.0),
                ('G', 1.0), ('A', 1.0), ('B', 1.0), ('C', 2.0)
            ], tempo=120))
        ]
        
        for name, audio in demos:
            print(f"\nPlaying: {name}")
            self.play_audio(audio, blocking=True)
            time.sleep(0.5)
        
        print("\n✅ Audio generation demo completed!")


if __name__ == "__main__":
    # Run demo
    generator = AudioGenerator()
    generator.generate_audio_demo() 