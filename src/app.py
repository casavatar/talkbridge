#!/usr/bin/env python3
"""
TalkBridge - Main Application
=============================

Talkbridge main application

Author: TalkBridge Team
Date: 2025-08-19
Version: 1.0

Requirements:
- None
======================================================================
Functions:
- audio_callback: Audio_callback function
- create_notification_sound: Create a notification sound using audio generation.
- main: Main application with integrated animations and audio generation.
======================================================================
"""

import numpy as np
import time
from ollama.ollama_client import OllamaClient
from audio.capture import AudioCapture
from audio import AudioGenerator, AudioSynthesizer, AudioEffects, AudioPlayer
from animation import AudioVisualizer, LoadingAnimation
from animation.loading_animation import SpinnerAnimation, ProgressBar
from animation.interactive_animations import InteractiveAnimations

def audio_callback(indata, frames, time_info, status):
    volume_norm = np.linalg.norm(indata) * 10
    print(f"Volume level: {volume_norm:.2f}")
    return indata.flatten()  # Return audio data for visualization

def create_notification_sound():
    """Create a notification sound using audio generation."""
    generator = AudioGenerator()
    effects = AudioEffects()
    
    # Generate notification tone
    tone = generator.generate_sine_wave(800, 0.5)
    
    # Apply effects for better sound
    processed = effects.apply_compressor(tone, threshold=-20, ratio=4)
    processed = effects.apply_limiter(processed, threshold=0.8)
    
    return processed

def main():
    """Main application with integrated animations and audio generation."""
    print("🎬 TalkBridge with Animation & Audio Generation System 🎬")
    print("=" * 60)
    
    # Initialize components
    client = OllamaClient()
    audio = AudioCapture()
    
    # Initialize audio generation components
    audio_generator = AudioGenerator()
    audio_synthesizer = AudioSynthesizer()
    audio_effects = AudioEffects()
    audio_player = AudioPlayer()
    
    # Initialize animation manager
    animation_manager = InteractiveAnimations()
    
    # Verify connection with loading animation
    print("\n🔗 Connecting to Ollama...")
    spinner = SpinnerAnimation("Connecting to Ollama service...", style="dots")
    spinner.start()
    
    try:
        if client.ping():
            spinner.stop()
            print("✅ Connection to Ollama verified.")
            
            # Create audio visualizer
            print("\n🎵 Starting audio visualization...")
            visualizer = AudioVisualizer("bars")
            
            # Create some interactive animations
            animation_manager.create_particle_system("particles", 30)
            animation_manager.create_geometric_animation("processing", "circle")
            
            # Generate a welcome sound
            print("\n🔊 Generating welcome sound...")
            welcome_sound = create_notification_sound()
            audio_generator.play_audio(welcome_sound, blocking=True)
            
            # Start audio capture with visualization
            print("\n🎤 Starting audio capture with visualization...")
            print("Press Ctrl+C to stop")
            
            try:
                # Start audio capture
                audio.start_input_stream(audio_callback)
                
                # Start visualizations
                visualizer.start_visualization(audio_callback)
                
                # Start some interactive animations
                animation_manager.start_animation("particles")
                
                # Keep the program alive
                while True:
                    time.sleep(0.1)
                    
            except KeyboardInterrupt:
                print("\n⏹️  Stopping all animations and audio capture...")
                
                # Stop all animations with progress indication
                progress = ProgressBar(4, 30, "Stopping components")
                progress.start()
                
                # Stop audio
                audio.stop()
                progress.update(1)
                
                # Stop visualizer
                visualizer.stop()
                progress.update(2)
                
                # Stop interactive animations
                animation_manager.stop_all()
                progress.update(3)
                
                # Generate exit sound
                exit_sound = audio_generator.generate_sine_wave(400, 0.3)
                audio_generator.play_audio(exit_sound, blocking=False)
                progress.update(4)
                progress.stop()
                
                print("✅ All components stopped successfully.")
                
        else:
            spinner.stop()
            print("❌ Failed to connect to Ollama. Aborting process.")
            
    except Exception as e:
        spinner.stop()
        print(f"❌ Error: {e}")
        print("Make sure Ollama is running and accessible.")

if __name__ == "__main__":
    main()