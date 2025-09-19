#!/usr/bin/env python3
"""
TalkBridge Audio - Synthesizer
==============================

Synthesizer module for TalkBridge

Author: TalkBridge Team
Date: 2025-08-19
Version: 1.0

Requirements:
- sounddevice
- numpy
======================================================================
Functions:
- __init__: Initialize ADSR envelope.
- generate: Generate ADSR envelope.
- __init__: Initialize filter.
- process: Process audio through filter. Override in subclasses.
- process: Apply low-pass filter to audio.
- process: Apply high-pass filter to audio.
- __init__: Initialize LFO.
- generate: Generate LFO signal.
- __init__: Initialize audio synthesizer.
- create_voice: Create a new synthesizer voice.
======================================================================
"""

import numpy as np
import sounddevice as sd
import threading
import time
from typing import Optional, Callable, List, Tuple, Dict
import math

class ADSREnvelope:
    """ADSR (Attack, Decay, Sustain, Release) envelope generator."""
    
    def __init__(self, attack: float = 0.1, decay: float = 0.1, 
                 sustain: float = 0.7, release: float = 0.3):
        """
        Initialize ADSR envelope.
        
        Args:
            attack: Attack time in seconds
            decay: Decay time in seconds
            sustain: Sustain level (0.0 to 1.0)
            release: Release time in seconds
        """
        self.attack = attack
        self.decay = decay
        self.sustain = sustain
        self.release = release
    
    def generate(self, duration: float, sample_rate: int = 44100) -> np.ndarray:
        """
        Generate ADSR envelope.
        
        Args:
            duration: Total duration in seconds
            sample_rate: Sample rate in Hz
            
        Returns:
            Envelope as numpy array
        """
        samples = int(sample_rate * duration)
        envelope = np.zeros(samples)
        
        attack_samples = int(self.attack * sample_rate)
        decay_samples = int(self.decay * sample_rate)
        release_samples = int(self.release * sample_rate)
        
        # Attack phase
        if attack_samples > 0:
            envelope[:attack_samples] = np.linspace(0, 1, attack_samples)
        
        # Decay phase
        if decay_samples > 0:
            decay_start = attack_samples
            decay_end = min(decay_start + decay_samples, samples)
            envelope[decay_start:decay_end] = np.linspace(1, self.sustain, decay_end - decay_start)
        
        # Sustain phase
        sustain_start = min(attack_samples + decay_samples, samples)
        release_start = max(samples - release_samples, sustain_start)
        envelope[sustain_start:release_start] = self.sustain
        
        # Release phase
        if release_samples > 0:
            release_end = min(release_start + release_samples, samples)
            envelope[release_start:release_end] = np.linspace(self.sustain, 0, release_end - release_start)
        
        return envelope

class Filter:
    """Audio filter base class."""
    
    def __init__(self, cutoff_freq: float, sample_rate: int = 44100):
        """
        Initialize filter.
        
        Args:
            cutoff_freq: Cutoff frequency in Hz
            sample_rate: Sample rate in Hz
        """
        self.cutoff_freq = cutoff_freq
        self.sample_rate = sample_rate
        self.x_history = np.zeros(2)
        self.y_history = np.zeros(2)
    
    def process(self, audio: np.ndarray) -> np.ndarray:
        """Process audio through filter. Override in subclasses."""
        return audio

class LowPassFilter(Filter):
    """Low-pass filter implementation."""
    
    def process(self, audio: np.ndarray) -> np.ndarray:
        """Apply low-pass filter to audio."""
        # Simple first-order IIR low-pass filter
        alpha = 1.0 / (1.0 + 2 * np.pi * self.cutoff_freq / self.sample_rate)
        
        filtered = np.zeros_like(audio)
        for i in range(len(audio)):
            filtered[i] = alpha * audio[i] + (1 - alpha) * self.y_history[0]
            self.y_history[0] = filtered[i]
        
        return filtered

class HighPassFilter(Filter):
    """High-pass filter implementation."""
    
    def process(self, audio: np.ndarray) -> np.ndarray:
        """Apply high-pass filter to audio."""
        # Simple first-order IIR high-pass filter
        alpha = 1.0 / (1.0 + 2 * np.pi * self.cutoff_freq / self.sample_rate)
        
        filtered = np.zeros_like(audio)
        for i in range(len(audio)):
            filtered[i] = alpha * (self.y_history[0] + audio[i] - self.x_history[0])
            self.x_history[0] = audio[i]
            self.y_history[0] = filtered[i]
        
        return filtered

class LFO:
    """Low Frequency Oscillator for modulation."""
    
    def __init__(self, frequency: float, waveform: str = 'sine'):
        """
        Initialize LFO.
        
        Args:
            frequency: LFO frequency in Hz
            waveform: Waveform type ('sine', 'square', 'triangle', 'sawtooth')
        """
        self.frequency = frequency
        self.waveform = waveform
        self.phase = 0.0
    
    def generate(self, duration: float, sample_rate: int = 44100) -> np.ndarray:
        """
        Generate LFO signal.
        
        Args:
            duration: Duration in seconds
            sample_rate: Sample rate in Hz
            
        Returns:
            LFO signal as numpy array
        """
        t = np.linspace(0, duration, int(sample_rate * duration), False)
        phase = 2 * np.pi * self.frequency * t + self.phase
        
        if self.waveform == 'sine':
            return np.sin(phase)
        elif self.waveform == 'square':
            return np.sign(np.sin(phase))
        elif self.waveform == 'triangle':
            return 2 * np.abs(phase / np.pi - np.floor(phase / np.pi + 0.5)) - 1
        elif self.waveform == 'sawtooth':
            return 2 * (phase / (2 * np.pi) - np.floor(phase / (2 * np.pi) + 0.5))
        else:
            return np.sin(phase)

class AudioSynthesizer:
    """Advanced audio synthesizer with modulation and filtering."""
    
    def __init__(self, sample_rate: int = 44100):
        """
        Initialize audio synthesizer.
        
        Args:
            sample_rate: Sample rate in Hz
        """
        self.sample_rate = sample_rate
        self.voices = {}  # Active voices
        self.voice_id = 0
    
    def create_voice(self, frequency: float, duration: float, 
                    envelope: Optional[ADSREnvelope] = None,
                    filters: Optional[List[Filter]] = None,
                    lfo: Optional[LFO] = None) -> int:
        """
        Create a new synthesizer voice.
        
        Args:
            frequency: Base frequency in Hz
            duration: Duration in seconds
            envelope: ADSR envelope
            filters: List of filters to apply
            lfo: LFO for modulation
            
        Returns:
            Voice ID
        """
        voice_id = self.voice_id
        self.voice_id += 1
        
        # Generate base waveform
        t = np.linspace(0, duration, int(self.sample_rate * duration), False)
        audio = np.sin(2 * np.pi * frequency * t)
        
        # Apply envelope
        if envelope:
            env = envelope.generate(duration, self.sample_rate)
            audio *= env
        
        # Apply LFO modulation
        if lfo:
            lfo_signal = lfo.generate(duration, self.sample_rate)
            # Modulate frequency
            modulated_freq = frequency * (1 + 0.1 * lfo_signal)
            audio = np.sin(2 * np.pi * modulated_freq * t)
            if envelope:
                audio *= env
        
        # Apply filters
        if filters:
            for filter_obj in filters:
                audio = filter_obj.process(audio)
        
        self.voices[voice_id] = {
            'audio': audio,
            'start_time': time.time(),
            'duration': duration
        }
        
        return voice_id
    
    def play_voice(self, voice_id: int, blocking: bool = True):
        """
        Play a specific voice.
        
        Args:
            voice_id: Voice ID to play
            blocking: Whether to block until playback is complete
        """
        if voice_id in self.voices:
            voice = self.voices[voice_id]
            sd.play(voice['audio'], self.sample_rate)
            if blocking:
                sd.wait()
    
    def play_all_voices(self, blocking: bool = True):
        """Play all active voices."""
        for voice_id in self.voices:
            self.play_voice(voice_id, blocking=False)
        if blocking:
            sd.wait()
    
    def generate_polyphonic_chord(self, frequencies: List[float], duration: float,
                                 envelope: Optional[ADSREnvelope] = None) -> np.ndarray:
        """
        Generate a polyphonic chord.
        
        Args:
            frequencies: List of frequencies
            duration: Duration in seconds
            envelope: ADSR envelope
            
        Returns:
            Combined audio as numpy array
        """
        combined_audio = np.zeros(int(self.sample_rate * duration))
        
        for freq in frequencies:
            voice_id = self.create_voice(freq, duration, envelope)
            combined_audio += self.voices[voice_id]['audio']
        
        # Normalize to prevent clipping
        combined_audio = combined_audio / len(frequencies)
        return combined_audio
    
    def generate_fm_synthesis(self, carrier_freq: float, modulator_freq: float,
                             modulation_index: float, duration: float,
                             envelope: Optional[ADSREnvelope] = None) -> np.ndarray:
        """
        Generate FM synthesis.
        
        Args:
            carrier_freq: Carrier frequency in Hz
            modulator_freq: Modulator frequency in Hz
            modulation_index: Modulation index
            duration: Duration in seconds
            envelope: ADSR envelope
            
        Returns:
            FM synthesis audio as numpy array
        """
        t = np.linspace(0, duration, int(self.sample_rate * duration), False)
        
        # Generate modulator
        modulator = np.sin(2 * np.pi * modulator_freq * t)
        
        # Generate carrier with frequency modulation
        phase = 2 * np.pi * carrier_freq * t + modulation_index * modulator
        audio = np.sin(phase)
        
        # Apply envelope
        if envelope:
            env = envelope.generate(duration, self.sample_rate)
            audio *= env
        
        return audio
    
    def generate_am_synthesis(self, carrier_freq: float, modulator_freq: float,
                             modulation_depth: float, duration: float,
                             envelope: Optional[ADSREnvelope] = None) -> np.ndarray:
        """
        Generate AM synthesis.
        
        Args:
            carrier_freq: Carrier frequency in Hz
            modulator_freq: Modulator frequency in Hz
            modulation_depth: Modulation depth (0.0 to 1.0)
            duration: Duration in seconds
            envelope: ADSR envelope
            
        Returns:
            AM synthesis audio as numpy array
        """
        t = np.linspace(0, duration, int(self.sample_rate * duration), False)
        
        # Generate carrier and modulator
        carrier = np.sin(2 * np.pi * carrier_freq * t)
        modulator = np.sin(2 * np.pi * modulator_freq * t)
        
        # Apply amplitude modulation
        audio = carrier * (1 + modulation_depth * modulator)
        
        # Apply envelope
        if envelope:
            env = envelope.generate(duration, self.sample_rate)
            audio *= env
        
        return audio
    
    def synthesize_demo(self):
        """Generate a demo of various synthesis techniques."""
        print("🎹 Advanced Audio Synthesizer Demo")
        print("=" * 40)
        
        # Create envelope
        envelope = ADSREnvelope(attack=0.1, decay=0.2, sustain=0.6, release=0.3)
        
        # Create filters
        lowpass = LowPassFilter(1000, self.sample_rate)
        highpass = HighPassFilter(500, self.sample_rate)
        
        # Create LFO
        lfo = LFO(5.0, 'sine')  # 5 Hz sine wave LFO
        
        demos = [
            ("Basic Voice", self.create_voice(440, 2.0, envelope)),
            ("Filtered Voice", self.create_voice(440, 2.0, envelope, [lowpass])),
            ("LFO Modulated Voice", self.create_voice(440, 2.0, envelope, lfo=lfo)),
            ("Polyphonic Chord", self.generate_polyphonic_chord([261.63, 329.63, 392.00], 2.0, envelope)),
            ("FM Synthesis", self.generate_fm_synthesis(440, 220, 5.0, 2.0, envelope)),
            ("AM Synthesis", self.generate_am_synthesis(440, 110, 0.5, 2.0, envelope))
        ]
        
        for name, audio in demos:
            print(f"\nPlaying: {name}")
            if isinstance(audio, int):  # Voice ID
                self.play_voice(audio, blocking=True)
            else:  # Audio array
                sd.play(audio, self.sample_rate)
                sd.wait()
            time.sleep(0.5)
        
        print("\n✅ Synthesis demo completed!")

if __name__ == "__main__":
    # Run demo
    synth = AudioSynthesizer()
    synth.synthesize_demo() 