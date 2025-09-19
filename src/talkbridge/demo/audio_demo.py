#!/usr/bin/env python3
"""
TalkBridge Demo - Audio Demo
============================

Módulo audio_demo para TalkBridge

Author: TalkBridge Team
Date: 2025-08-19
Version: 1.0

Requirements:
- PyQt6
======================================================================
Functions:
- demo_audio_generator: Demo the audio generator capabilities.
- demo_audio_synthesizer: Demo the advanced audio synthesizer.
- demo_audio_effects: Demo the audio effects processor.
- demo_audio_player: Demo the audio player capabilities.
- demo_audio_integration: Demo integration with existing audio capture.
- main: Main demo function.
- on_track_change: Function on_track_change
- on_playback_end: Function on_playback_end
======================================================================
"""
from talkbridge.audio import AudioGenerator, AudioSynthesizer, AudioEffects, AudioPlayer
from talkbridge.audio.capture import AudioCapture


import time
import os

# Import TalkBridge audio modules
from talkbridge.audio import AudioGenerator, AudioSynthesizer, AudioEffects, AudioPlayer
from talkbridge.audio.capture import AudioCapture

def demo_audio_generator():
    """Demo the audio generator capabilities."""
    print("\n" + "="*50)
    print("AUDIO GENERATOR DEMO")
    print("="*50)
    
    generator = AudioGenerator()
    
    print("Generating and playing various audio types...")
    print("Press Ctrl+C to stop any demo")
    
    try:
        # Generate different types of audio
        demos = [
            ("Sine Wave (440 Hz)", generator.generate_sine_wave(440, 2.0)),
            ("Square Wave (220 Hz)", generator.generate_square_wave(220, 2.0)),
            ("Sawtooth Wave (330 Hz)", generator.generate_sawtooth_wave(330, 2.0)),
            ("Triangle Wave (550 Hz)", generator.generate_triangle_wave(550, 2.0)),
            ("White Noise", generator.generate_white_noise(2.0)),
            ("Pink Noise", generator.generate_pink_noise(2.0)),
            ("Frequency Sweep (200-2000 Hz)", generator.generate_frequency_sweep(200, 2000, 3.0)),
            ("C Major Chord", generator.generate_chord([261.63, 329.63, 392.00], 2.0)),
            ("Simple Melody", generator.generate_melody([
                ('C', 1.0), ('D', 1.0), ('E', 1.0), ('F', 1.0),
                ('G', 1.0), ('A', 1.0), ('B', 1.0), ('C', 2.0)
            ], tempo=120))
        ]
        
        for name, audio in demos:
            print(f"\nPlaying: {name}")
            generator.play_audio(audio, blocking=True)
            time.sleep(0.5)
        
        print("\n✅ Audio generator demo completed!")
        
    except KeyboardInterrupt:
        print("\nDemo interrupted by user")

def demo_audio_synthesizer():
    """Demo the advanced audio synthesizer."""
    print("\n" + "="*50)
    print("AUDIO SYNTHESIZER DEMO")
    print("="*50)
    
    synth = AudioSynthesizer()
    
    print("Demonstrating advanced synthesis techniques...")
    print("Press Ctrl+C to stop any demo")
    
    try:
        # Create envelope
        envelope = synth.ADSREnvelope(attack=0.1, decay=0.2, sustain=0.6, release=0.3)
        
        # Create filters
        lowpass = synth.LowPassFilter(1000, synth.sample_rate)
        highpass = synth.HighPassFilter(500, synth.sample_rate)
        
        # Create LFO
        lfo = synth.LFO(5.0, 'sine')  # 5 Hz sine wave LFO
        
        demos = [
            ("Basic Voice", synth.create_voice(440, 2.0, envelope)),
            ("Filtered Voice", synth.create_voice(440, 2.0, envelope, [lowpass])),
            ("LFO Modulated Voice", synth.create_voice(440, 2.0, envelope, lfo=lfo)),
            ("Polyphonic Chord", synth.generate_polyphonic_chord([261.63, 329.63, 392.00], 2.0, envelope)),
            ("FM Synthesis", synth.generate_fm_synthesis(440, 220, 5.0, 2.0, envelope)),
            ("AM Synthesis", synth.generate_am_synthesis(440, 110, 0.5, 2.0, envelope))
        ]
        
        for name, audio in demos:
            print(f"\nPlaying: {name}")
            if isinstance(audio, int):  # Voice ID
                synth.play_voice(audio, blocking=True)
            else:  # Audio array
                synth.play_audio(audio, blocking=True)
            time.sleep(0.5)
        
        print("\n✅ Audio synthesizer demo completed!")
        
    except KeyboardInterrupt:
        print("\nDemo interrupted by user")

def demo_audio_effects():
    """Demo the audio effects processor."""
    print("\n" + "="*50)
    print("AUDIO EFFECTS DEMO")
    print("="*50)
    
    effects = AudioEffects()
    
    print("Demonstrating various audio effects...")
    print("Press Ctrl+C to stop any demo")
    
    try:
        # Generate test audio
        t = effects.sample_rate * 3  # 3 seconds
        t = np.linspace(0, 3, int(t), False)
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
        
        for name, effects_list in effects_chains:
            print(f"\nPlaying: {name}")
            processed = effects.apply_effects_chain(test_audio, effects_list)
            effects.play_audio(processed, blocking=True)
            time.sleep(0.5)
        
        print("\n✅ Audio effects demo completed!")
        
    except KeyboardInterrupt:
        print("\nDemo interrupted by user")

def demo_audio_player():
    """Demo the audio player capabilities."""
    print("\n" + "="*50)
    print("AUDIO PLAYER DEMO")
    print("="*50)
    
    player = AudioPlayer()
    
    print("Demonstrating audio player capabilities...")
    
    try:
        # Create test audio
        t = np.linspace(0, 2, int(player.sample_rate * 2), False)
        test_audio = np.sin(2 * np.pi * 440 * t)
        
        # Save test audio
        test_file = "test_audio.wav"
        player.save_audio_file(test_audio, test_file)
        
        # Create playlist
        player.playlist = [
            {'name': 'Test Audio', 'file': test_file, 'duration': 2.0},
            {'name': 'Generated Tone', 'file': None, 'duration': 1.0}
        ]
        
        # Set up callbacks
        def on_track_change(track):
            print(f"Now playing: {track['name']}")
        
        def on_playback_end():
            print("Playback ended")
        
        player.on_track_change = on_track_change
        player.on_playback_end = on_playback_end
        
        # Play playlist
        print("Playing playlist...")
        player.play_playlist()
        
        # Clean up
        if os.path.exists(test_file):
            os.remove(test_file)
        
        print("\n✅ Audio player demo completed!")
        
    except Exception as e:
        print(f"Player demo error: {e}")

def demo_audio_integration():
    """Demo integration with existing audio capture."""
    print("\n" + "="*50)
    print("AUDIO INTEGRATION DEMO")
    print("="*50)
    
    try:
        from audio.capture import AudioCapture
        from audio.generator import AudioGenerator
        from audio.effects import AudioEffects
        
        # Initialize components
        capture = AudioCapture()
        generator = AudioGenerator()
        effects = AudioEffects()
        
        print("Testing audio integration...")
        print("This demo will generate audio and apply effects")
        
        # Generate audio
        audio = generator.generate_sine_wave(440, 2.0)
        
        # Apply effects
        processed = effects.apply_reverb(audio, room_size=0.5, wet_level=0.3)
        
        # Play processed audio
        print("Playing processed audio...")
        generator.play_audio(processed, blocking=True)
        
        print("\n✅ Audio integration demo completed!")
        
    except Exception as e:
        print(f"Integration demo error: {e}")

def main():
    """Main demo function."""
    print("🎵 TALKBRIDGE AUDIO GENERATION DEMO 🎵")
    print("This demo showcases all audio generation capabilities")
    print("Press Ctrl+C at any time to stop demos and continue")
    
    try:
        # Run all demos
        demo_audio_generator()
        demo_audio_synthesizer()
        demo_audio_effects()
        demo_audio_player()
        demo_audio_integration()
        
        print("\n" + "="*50)
        print("🎉 ALL AUDIO DEMOS COMPLETED! 🎉")
        print("="*50)
        print("\nAudio generation capabilities include:")
        print("✅ Basic audio generation (sine, square, sawtooth, triangle waves)")
        print("✅ Noise generation (white, pink)")
        print("✅ Frequency sweeps and chords")
        print("✅ Melody generation with note names")
        print("✅ Advanced synthesis (ADSR, filters, LFO, FM/AM)")
        print("✅ Audio effects (reverb, delay, distortion, chorus, flanger)")
        print("✅ Audio playback and streaming")
        print("✅ Audio file I/O and playlist management")
        print("\nYou can now integrate these audio capabilities into your TalkBridge application!")
        
    except KeyboardInterrupt:
        print("\n\nDemo interrupted by user. Exiting...")
    except Exception as e:
        print(f"\nDemo error: {e}")
        print("Make sure all dependencies are installed:")
        print("pip install numpy sounddevice scipy")

if __name__ == "__main__":
    main() 