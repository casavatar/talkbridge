#!/usr/bin/env python3
#----------------------------------------------------------------------------------------------------------------------------
# description: Animation Demo Script for TalkBridge
#----------------------------------------------------------------------------------------------------------------------------
# 
# author: ingekastel
# date: 2025-06-02
# version: 1.0
#----------------------------------------------------------------------------------------------------------------------------
# 
# requirements:
# - numpy Python package
# - matplotlib Python package
# - sounddevice Python package
# - soundfile Python package
# - scipy Python package
# - seaborn Python package
#----------------------------------------------------------------------------------------------------------------------------
# functions:
# - demo_audio_visualizer: Demo the audio visualizer animations
# - demo_loading_animations: Demo the loading animations
# - demo_interactive_animations: Demo the interactive animations
# - demo_animation_manager: Demo the animation manager
#----------------------------------------------------------------------------------------------------------------------------

import time
import sys
import os

# Add the src directory to the path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from animation import AudioVisualizer, LoadingAnimation, InteractiveAnimations
from animation.loading_animation import SpinnerAnimation, ProgressBar, PulseAnimation, WaveAnimation
from animation.interactive_animations import ParticleSystem, GeometricAnimation, WaveformAnimation


def demo_audio_visualizer():
    """Demo the audio visualizer animations."""
    print("\n" + "="*50)
    print("AUDIO VISUALIZER DEMO")
    print("="*50)
    
    styles = ['bars', 'wave', 'circular', 'spectrum']
    
    for style in styles:
        print(f"\nRunning {style.upper()} visualization...")
        print("Press Ctrl+C to stop and continue to next style")
        
        visualizer = AudioVisualizer(style)
        
        def demo_audio_callback():
            # Simulate audio data
            import numpy as np
            return np.random.rand(1024) * 0.5
        
        try:
            visualizer.start_visualization(demo_audio_callback)
            time.sleep(5)  # Show each style for 5 seconds
        except KeyboardInterrupt:
            print("\nStopped by user")
        finally:
            visualizer.stop()


def demo_loading_animations():
    """Demo the loading animations."""
    print("\n" + "="*50)
    print("LOADING ANIMATIONS DEMO")
    print("="*50)
    
    # Spinner animations
    print("\n1. Spinner Animations:")
    spinner_styles = ['dots', 'arrows', 'bars', 'dots2']
    
    for style in spinner_styles:
        print(f"\n   {style.upper()} style:")
        spinner = SpinnerAnimation(f"Loading with {style} style...", style)
        spinner.start()
        time.sleep(2)
        spinner.stop()
    
    # Progress bar
    print("\n2. Progress Bar:")
    progress = ProgressBar(100, 40, "Processing files")
    progress.start()
    
    for i in range(0, 101, 5):
        progress.update(i)
        time.sleep(0.1)
    
    progress.stop()
    
    # Pulse animation
    print("\n3. Pulse Animation:")
    pulse = PulseAnimation("Processing data...")
    pulse.start()
    time.sleep(3)
    pulse.stop()
    
    # Wave animation
    print("\n4. Wave Animation:")
    wave = WaveAnimation("Loading modules...")
    wave.start()
    time.sleep(3)
    wave.stop()


def demo_interactive_animations():
    """Demo the interactive animations."""
    print("\n" + "="*50)
    print("INTERACTIVE ANIMATIONS DEMO")
    print("="*50)
    
    # Particle system
    print("\n1. Particle System:")
    print("   Press Ctrl+C to stop")
    particles = ParticleSystem(50)
    try:
        particles.start()
        time.sleep(5)
    except KeyboardInterrupt:
        print("\nStopped by user")
    finally:
        particles.stop()
    
    # Geometric animations
    print("\n2. Geometric Animations:")
    shapes = ['circle', 'square', 'triangle', 'polygon']
    
    for shape in shapes:
        print(f"\n   {shape.upper()} animation:")
        print("   Press Ctrl+C to stop")
        geo_anim = GeometricAnimation(shape)
        try:
            geo_anim.start()
            time.sleep(3)
        except KeyboardInterrupt:
            print("\nStopped by user")
        finally:
            geo_anim.stop()
    
    # Waveform animation
    print("\n3. Waveform Animation:")
    print("   Press Ctrl+C to stop")
    wave_anim = WaveformAnimation(frequency=2.0, amplitude=1.0)
    try:
        wave_anim.start()
        time.sleep(5)
    except KeyboardInterrupt:
        print("\nStopped by user")
    finally:
        wave_anim.stop()


def demo_animation_manager():
    """Demo the animation manager."""
    print("\n" + "="*50)
    print("ANIMATION MANAGER DEMO")
    print("="*50)
    
    manager = InteractiveAnimations()
    
    # Create different animations
    print("\nCreating animations...")
    manager.create_particle_system("particles", 30)
    manager.create_geometric_animation("circle", "circle")
    manager.create_waveform_animation("waves", 1.5, 0.8)
    
    print(f"Available animations: {manager.list_animations()}")
    
    # Start animations one by one
    for name in manager.list_animations():
        print(f"\nStarting {name} animation...")
        print("Press Ctrl+C to stop and continue to next")
        try:
            manager.start_animation(name)
            time.sleep(3)
        except KeyboardInterrupt:
            print("\nStopped by user")
        finally:
            manager.stop_animation(name)
    
    print("\nAll animations completed!")


def main():
    """Main demo function."""
    print("🎬 TALKBRIDGE ANIMATION DEMO 🎬")
    print("This demo showcases all animation capabilities")
    print("Press Ctrl+C at any time to stop animations and continue")
    
    try:
        # Run all demos
        demo_loading_animations()
        demo_interactive_animations()
        demo_animation_manager()
        
        # Audio visualizer demo (requires matplotlib backend)
        print("\n" + "="*50)
        print("AUDIO VISUALIZER DEMO (Optional)")
        print("="*50)
        print("This demo requires a graphical backend.")
        print("If you're running in a headless environment, this may not work.")
        
        response = input("\nDo you want to run the audio visualizer demo? (y/n): ")
        if response.lower() in ['y', 'yes']:
            try:
                demo_audio_visualizer()
            except Exception as e:
                print(f"Audio visualizer demo failed: {e}")
                print("This is normal in headless environments.")
        
        print("\n" + "="*50)
        print("🎉 ALL ANIMATION DEMOS COMPLETED! 🎉")
        print("="*50)
        print("\nAnimation capabilities include:")
        print("✅ Loading animations (spinners, progress bars, pulses, waves)")
        print("✅ Interactive animations (particles, geometric shapes, waveforms)")
        print("✅ Audio visualizations (bars, waves, circular, spectrum)")
        print("✅ Animation management system")
        print("\nYou can now integrate these animations into your TalkBridge application!")
        
    except KeyboardInterrupt:
        print("\n\nDemo interrupted by user. Exiting...")
    except Exception as e:
        print(f"\nDemo error: {e}")
        print("Make sure all dependencies are installed:")
        print("pip install numpy matplotlib sounddevice scipy requests")


if __name__ == "__main__":
    main() 