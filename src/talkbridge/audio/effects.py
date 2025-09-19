#!/usr/bin/env python3
"""
TalkBridge Audio - Effects
==========================

Effects module for TalkBridge

Author: TalkBridge Team
Date: 2025-08-19
Version: 1.0

Requirements:
- sounddevice
- numpy
======================================================================
Functions:
- __init__: Initialize audio effects processor.
- apply_reverb: Apply reverb effect.
- apply_delay: Apply delay effect.
- apply_distortion: Apply distortion effect.
- apply_chorus: Apply chorus effect.
- apply_flanger: Apply flanger effect.
- apply_compressor: Apply compression effect.
- apply_limiter: Apply limiting effect.
- apply_eq: Apply 3-band EQ.
- apply_bit_crusher: Apply bit crusher effect.
======================================================================
"""

import numpy as np
import sounddevice as sd
import time
from typing import Optional, List, Tuple
import math

class AudioEffects:
    """Audio effects processor."""
    
    def __init__(self, sample_rate: int = 44100):
        """
        Initialize audio effects processor.
        
        Args:
            sample_rate: Sample rate in Hz
        """
        self.sample_rate = sample_rate
        self.delay_buffer = np.zeros(sample_rate * 2)  # 2 second delay buffer
        self.delay_index = 0
    
    def apply_reverb(self, audio: np.ndarray, room_size: float = 0.5, 
                    damping: float = 0.5, wet_level: float = 0.3) -> np.ndarray:
        """
        Apply reverb effect.
        
        Args:
            audio: Input audio
            room_size: Room size (0.0 to 1.0)
            damping: Damping factor (0.0 to 1.0)
            wet_level: Wet signal level (0.0 to 1.0)
            
        Returns:
            Audio with reverb applied
        """
        # Simple reverb implementation using multiple delays
        dry = audio.copy()
        wet = np.zeros_like(audio)
        
        # Create multiple delay taps
        delays = [int(self.sample_rate * 0.03 * room_size),  # 30ms
                 int(self.sample_rate * 0.05 * room_size),  # 50ms
                 int(self.sample_rate * 0.07 * room_size)]  # 70ms
        
        for delay_samples in delays:
            if delay_samples > 0:
                delayed = np.zeros_like(audio)
                delayed[delay_samples:] = audio[:-delay_samples] * damping
                wet += delayed
        
        # Mix dry and wet signals
        result = (1 - wet_level) * dry + wet_level * wet
        return result
    
    def apply_delay(self, audio: np.ndarray, delay_time: float = 0.5, 
                   feedback: float = 0.3, wet_level: float = 0.5) -> np.ndarray:
        """
        Apply delay effect.
        
        Args:
            audio: Input audio
            delay_time: Delay time in seconds
            feedback: Feedback amount (0.0 to 1.0)
            wet_level: Wet signal level (0.0 to 1.0)
            
        Returns:
            Audio with delay applied
        """
        delay_samples = int(delay_time * self.sample_rate)
        result = np.zeros_like(audio)
        
        for i in range(len(audio)):
            # Add delayed signal
            if i >= delay_samples:
                result[i] = audio[i] + feedback * result[i - delay_samples]
            else:
                result[i] = audio[i]
        
        # Mix with original
        result = (1 - wet_level) * audio + wet_level * result
        return result
    
    def apply_distortion(self, audio: np.ndarray, drive: float = 0.5, 
                        mix: float = 0.5) -> np.ndarray:
        """
        Apply distortion effect.
        
        Args:
            audio: Input audio
            drive: Distortion drive (0.0 to 1.0)
            mix: Mix level (0.0 to 1.0)
            
        Returns:
            Audio with distortion applied
        """
        # Apply drive
        driven = audio * (1 + drive * 10)
        
        # Apply soft clipping
        distorted = np.tanh(driven)
        
        # Mix with original
        result = (1 - mix) * audio + mix * distorted
        return result
    
    def apply_chorus(self, audio: np.ndarray, rate: float = 1.5, 
                    depth: float = 0.002, mix: float = 0.5) -> np.ndarray:
        """
        Apply chorus effect.
        
        Args:
            audio: Input audio
            rate: LFO rate in Hz
            depth: Modulation depth in seconds
            mix: Mix level (0.0 to 1.0)
            
        Returns:
            Audio with chorus applied
        """
        t = np.linspace(0, len(audio) / self.sample_rate, len(audio), False)
        
        # Generate LFO for modulation
        lfo = np.sin(2 * np.pi * rate * t)
        
        # Create modulated delay
        modulated_delay = depth * self.sample_rate * (1 + lfo)
        
        # Apply modulated delay
        chorus = np.zeros_like(audio)
        for i in range(len(audio)):
            delay_samples = int(modulated_delay[i])
            if i >= delay_samples:
                chorus[i] = audio[i - delay_samples]
            else:
                chorus[i] = audio[i]
        
        # Mix with original
        result = (1 - mix) * audio + mix * chorus
        return result
    
    def apply_flanger(self, audio: np.ndarray, rate: float = 0.5, 
                     depth: float = 0.005, feedback: float = 0.3, 
                     mix: float = 0.5) -> np.ndarray:
        """
        Apply flanger effect.
        
        Args:
            audio: Input audio
            rate: LFO rate in Hz
            depth: Modulation depth in seconds
            feedback: Feedback amount (0.0 to 1.0)
            mix: Mix level (0.0 to 1.0)
            
        Returns:
            Audio with flanger applied
        """
        t = np.linspace(0, len(audio) / self.sample_rate, len(audio), False)
        
        # Generate LFO for modulation
        lfo = np.sin(2 * np.pi * rate * t)
        
        # Create modulated delay
        modulated_delay = depth * self.sample_rate * (1 + lfo)
        
        # Apply modulated delay with feedback
        flanger = np.zeros_like(audio)
        for i in range(len(audio)):
            delay_samples = int(modulated_delay[i])
            if i >= delay_samples:
                flanger[i] = audio[i] + feedback * flanger[i - delay_samples]
            else:
                flanger[i] = audio[i]
        
        # Mix with original
        result = (1 - mix) * audio + mix * flanger
        return result
    
    def apply_compressor(self, audio: np.ndarray, threshold: float = -20.0, 
                        ratio: float = 4.0, attack: float = 0.005, 
                        release: float = 0.1) -> np.ndarray:
        """
        Apply compression effect.
        
        Args:
            audio: Input audio
            threshold: Compression threshold in dB
            ratio: Compression ratio
            attack: Attack time in seconds
            release: Release time in seconds
            
        Returns:
            Audio with compression applied
        """
        # Convert to dB
        threshold_linear = 10 ** (threshold / 20)
        
        # Calculate RMS
        rms = np.sqrt(np.mean(audio ** 2))
        
        # Calculate gain reduction
        if rms > threshold_linear:
            gain_reduction = (rms / threshold_linear) ** (1 / ratio - 1)
        else:
            gain_reduction = 1.0
        
        # Apply attack and release
        attack_samples = int(attack * self.sample_rate)
        release_samples = int(release * self.sample_rate)
        
        # Simple envelope follower
        envelope = np.zeros_like(audio)
        for i in range(len(audio)):
            if i == 0:
                envelope[i] = gain_reduction
            else:
                if gain_reduction < envelope[i-1]:
                    # Attack phase
                    envelope[i] = envelope[i-1] + (gain_reduction - envelope[i-1]) / attack_samples
                else:
                    # Release phase
                    envelope[i] = envelope[i-1] + (gain_reduction - envelope[i-1]) / release_samples
        
        return audio * envelope
    
    def apply_limiter(self, audio: np.ndarray, threshold: float = 0.8) -> np.ndarray:
        """
        Apply limiting effect.
        
        Args:
            audio: Input audio
            threshold: Limiting threshold (0.0 to 1.0)
            
        Returns:
            Audio with limiting applied
        """
        # Simple hard limiter
        limited = np.clip(audio, -threshold, threshold)
        return limited
    
    def apply_eq(self, audio: np.ndarray, low_gain: float = 1.0, 
                mid_gain: float = 1.0, high_gain: float = 1.0) -> np.ndarray:
        """
        Apply 3-band EQ.
        
        Args:
            audio: Input audio
            low_gain: Low frequency gain
            mid_gain: Mid frequency gain
            high_gain: High frequency gain
            
        Returns:
            Audio with EQ applied
        """
        # Simple 3-band EQ using filters
        # Low-pass filter for lows
        low_cutoff = 250  # Hz
        low_alpha = 1.0 / (1.0 + 2 * np.pi * low_cutoff / self.sample_rate)
        low_filtered = np.zeros_like(audio)
        for i in range(len(audio)):
            if i == 0:
                low_filtered[i] = low_alpha * audio[i]
            else:
                low_filtered[i] = low_alpha * audio[i] + (1 - low_alpha) * low_filtered[i-1]
        
        # High-pass filter for highs
        high_cutoff = 4000  # Hz
        high_alpha = 1.0 / (1.0 + 2 * np.pi * high_cutoff / self.sample_rate)
        high_filtered = np.zeros_like(audio)
        for i in range(len(audio)):
            if i == 0:
                high_filtered[i] = high_alpha * audio[i]
            else:
                high_filtered[i] = high_alpha * (high_filtered[i-1] + audio[i] - audio[i-1])
        
        # Mid frequencies
        mid_filtered = audio - low_filtered - high_filtered
        
        # Apply gains and combine
        result = low_gain * low_filtered + mid_gain * mid_filtered + high_gain * high_filtered
        return result
    
    def apply_bit_crusher(self, audio: np.ndarray, bit_depth: int = 8, 
                         sample_rate_reduction: float = 0.5) -> np.ndarray:
        """
        Apply bit crusher effect.
        
        Args:
            audio: Input audio
            bit_depth: Bit depth for quantization
            sample_rate_reduction: Sample rate reduction factor
            
        Returns:
            Audio with bit crusher applied
        """
        # Quantize to specified bit depth
        max_value = 2 ** (bit_depth - 1) - 1
        quantized = np.round(audio * max_value) / max_value
        
        # Sample rate reduction
        if sample_rate_reduction < 1.0:
            step = int(1 / sample_rate_reduction)
            reduced = np.zeros_like(quantized)
            for i in range(0, len(quantized), step):
                reduced[i:i+step] = quantized[i]
            return reduced
        
        return quantized
    
    def apply_ring_modulator(self, audio: np.ndarray, frequency: float = 100.0, 
                           mix: float = 0.5) -> np.ndarray:
        """
        Apply ring modulator effect.
        
        Args:
            audio: Input audio
            frequency: Modulator frequency in Hz
            mix: Mix level (0.0 to 1.0)
            
        Returns:
            Audio with ring modulation applied
        """
        t = np.linspace(0, len(audio) / self.sample_rate, len(audio), False)
        modulator = np.sin(2 * np.pi * frequency * t)
        
        # Ring modulation
        modulated = audio * modulator
        
        # Mix with original
        result = (1 - mix) * audio + mix * modulated
        return result
    
    def apply_effects_chain(self, audio: np.ndarray, effects: List[Tuple[str, dict]]) -> np.ndarray:
        """
        Apply a chain of effects.
        
        Args:
            audio: Input audio
            effects: List of (effect_name, parameters) tuples
            
        Returns:
            Audio with effects chain applied
        """
        result = audio.copy()
        
        effect_methods = {
            'reverb': self.apply_reverb,
            'delay': self.apply_delay,
            'distortion': self.apply_distortion,
            'chorus': self.apply_chorus,
            'flanger': self.apply_flanger,
            'compressor': self.apply_compressor,
            'limiter': self.apply_limiter,
            'eq': self.apply_eq,
            'bit_crusher': self.apply_bit_crusher,
            'ring_modulator': self.apply_ring_modulator
        }
        
        for effect_name, params in effects:
            if effect_name in effect_methods:
                result = effect_methods[effect_name](result, **params)
        
        return result
    
    def effects_demo(self):
        """Generate a demo of various audio effects."""
        print("🎛️  Audio Effects Demo")
        print("=" * 30)
        
        # Generate test audio
        t = np.linspace(0, 3, int(self.sample_rate * 3), False)
        test_audio = np.sin(2 * np.pi * 440 * t) + 0.3 * np.sin(2 * np.pi * 880 * t)
        
        # Define effects chains
        effects_chains = [
            ("Reverb", [('reverb', {'room_size': 0.7, 'damping': 0.3, 'wet_level': 0.4})]),
            ("Delay", [('delay', {'delay_time': 0.5, 'feedback': 0.3, 'wet_level': 0.6})]),
            ("Distortion", [('distortion', {'drive': 0.8, 'mix': 0.7})]),
            ("Chorus", [('chorus', {'rate': 1.5, 'depth': 0.002, 'mix': 0.5})]),
            ("Flanger", [('flanger', {'rate': 0.5, 'depth': 0.005, 'feedback': 0.3, 'mix': 0.5})]),
            ("Compressor", [('compressor', {'threshold': -20, 'ratio': 4, 'attack': 0.005, 'release': 0.1})]),
            ("EQ", [('eq', {'low_gain': 1.5, 'mid_gain': 0.8, 'high_gain': 1.2})]),
            ("Bit Crusher", [('bit_crusher', {'bit_depth': 4, 'sample_rate_reduction': 0.3})]),
            ("Ring Modulator", [('ring_modulator', {'frequency': 100, 'mix': 0.3})]),
            ("Effects Chain", [
                ('compressor', {'threshold': -20, 'ratio': 2, 'attack': 0.01, 'release': 0.1}),
                ('eq', {'low_gain': 1.2, 'mid_gain': 0.9, 'high_gain': 1.1}),
                ('reverb', {'room_size': 0.5, 'damping': 0.5, 'wet_level': 0.3}),
                ('limiter', {'threshold': 0.8})
            ])
        ]
        
        for name, effects in effects_chains:
            print(f"\nPlaying: {name}")
            processed = self.apply_effects_chain(test_audio, effects)
            sd.play(processed, self.sample_rate)
            sd.wait()
            time.sleep(0.5)
        
        print("\n✅ Effects demo completed!")

if __name__ == "__main__":
    # Run demo
    effects = AudioEffects()
    effects.effects_demo() 