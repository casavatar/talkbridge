#!/usr/bin/env python3
"""
TalkBridge Demo - Tts Demo
==========================

TTS demo module for TalkBridge

Author: TalkBridge Team
Date: 2025-08-19
Version: 1.0

Requirements:
- PyQt6
======================================================================
Functions:
- demo_basic_synthesis: Demonstrate basic text-to-speech synthesis.
- demo_voice_cloning: Demonstrate voice cloning functionality.
- demo_multilingual: Demonstrate multilingual synthesis.
- demo_system_info: Display system information and available models.
- create_demo_audio_samples: Create demo audio samples for testing voice cloning.
- main: Main demo function.
======================================================================
"""

import os
import sys
import tempfile
from pathlib import Path

# Add src to path for imports
sys.path.append(str(Path(__file__).parent))

from tts import synthesize_voice, setup_voice_cloning, get_synthesis_info, list_available_models


def demo_basic_synthesis():
    """Demonstrate basic text-to-speech synthesis."""
    print("=== Basic TTS Synthesis Demo ===")
    
    text = "Hello! This is a demonstration of text-to-speech synthesis using Coqui TTS."
    
    try:
        # Synthesize without voice cloning
        print(f"Synthesizing: '{text}'")
        audio_bytes = synthesize_voice(
            text=text,
            clone_voice=False
        )
        
        print(f"✅ Successfully generated {len(audio_bytes)} bytes of audio")
        
        # Save to file
        output_path = "demo_output_basic.wav"
        synthesize_voice(
            text=text,
            output_path=output_path,
            clone_voice=False
        )
        print(f"✅ Audio saved to: {output_path}")
        
    except Exception as e:
        print(f"❌ Basic synthesis failed: {e}")


def demo_voice_cloning():
    """Demonstrate voice cloning functionality."""
    print("\n=== Voice Cloning Demo ===")
    
    # Check if reference samples exist
    reference_samples = [
        "reference_voice_1.wav",
        "reference_voice_2.wav"
    ]
    
    # Check which samples exist
    available_samples = [s for s in reference_samples if os.path.exists(s)]
    
    if not available_samples:
        print("⚠️  No reference audio samples found. Creating demo samples...")
        print("   To use voice cloning, place audio files named 'reference_voice_1.wav'")
        print("   and 'reference_voice_2.wav' in the current directory.")
        return
    
    print(f"Found {len(available_samples)} reference samples: {available_samples}")
    
    text = "This is a demonstration of voice cloning. My voice should sound like the reference samples."
    
    try:
        # Set up voice cloning
        print("Setting up voice cloning...")
        success = setup_voice_cloning(available_samples)
        
        if success:
            print("✅ Voice cloning setup successful")
            
            # Synthesize with cloned voice
            print(f"Synthesizing with cloned voice: '{text}'")
            audio_bytes = synthesize_voice(
                text=text,
                reference_samples=available_samples
            )
            
            print(f"✅ Successfully generated {len(audio_bytes)} bytes of cloned audio")
            
            # Save to file
            output_path = "demo_output_cloned.wav"
            synthesize_voice(
                text=text,
                output_path=output_path,
                reference_samples=available_samples
            )
            print(f"✅ Cloned audio saved to: {output_path}")
        else:
            print("❌ Voice cloning setup failed")
            
    except Exception as e:
        print(f"❌ Voice cloning demo failed: {e}")


def demo_multilingual():
    """Demonstrate multilingual synthesis."""
    print("\n=== Multilingual Synthesis Demo ===")
    
    texts = {
        "en": "Hello! This is English text.",
        "es": "¡Hola! Este es texto en español.",
        "fr": "Bonjour! Ceci est du texte en français.",
        "de": "Hallo! Das ist deutscher Text."
    }
    
    for language, text in texts.items():
        try:
            print(f"Synthesizing in {language}: '{text}'")
            output_path = f"demo_output_{language}.wav"
            
            synthesize_voice(
                text=text,
                output_path=output_path,
                language=language,
                clone_voice=False
            )
            
            print(f"✅ {language} audio saved to: {output_path}")
            
        except Exception as e:
            print(f"❌ {language} synthesis failed: {e}")


def demo_system_info():
    """Display system information and available models."""
    print("\n=== System Information ===")
    
    # Get synthesis info
    info = get_synthesis_info()
    print("Synthesis System Info:")
    for key, value in info.items():
        print(f"  {key}: {value}")
    
    # Get available models
    print("\nAvailable TTS Models:")
    models = list_available_models()
    if models:
        for i, model in enumerate(models[:5], 1):  # Show first 5 models
            print(f"  {i}. {model}")
        if len(models) > 5:
            print(f"  ... and {len(models) - 5} more models")
    else:
        print("  No models found")


def create_demo_audio_samples():
    """Create demo audio samples for testing voice cloning."""
    print("\n=== Creating Demo Audio Samples ===")
    
    try:
        # Create a simple demo text
        demo_text = "This is a demo audio sample for voice cloning testing."
        
        # Generate two different samples
        for i in range(1, 3):
            output_path = f"reference_voice_{i}.wav"
            
            # Add some variation to the text
            varied_text = f"Sample {i}: {demo_text}"
            
            synthesize_voice(
                text=varied_text,
                output_path=output_path,
                clone_voice=False
            )
            
            print(f"✅ Created demo sample {i}: {output_path}")
            
    except Exception as e:
        print(f"❌ Failed to create demo samples: {e}")


def main():
    """Main demo function."""
    print("🎤 TTS Voice Cloning Demo")
    print("=" * 50)
    
    # Show system info first
    demo_system_info()
    
    # Basic synthesis demo
    demo_basic_synthesis()
    
    # Create demo samples if none exist
    if not any(os.path.exists(f"reference_voice_{i}.wav") for i in range(1, 3)):
        create_demo_audio_samples()
    
    # Voice cloning demo
    demo_voice_cloning()
    
    # Multilingual demo
    demo_multilingual()
    
    print("\n" + "=" * 50)
    print("🎉 Demo completed!")
    print("\nGenerated files:")
    for file in os.listdir("."):
        if file.startswith("demo_output_") or file.startswith("reference_voice_"):
            print(f"  - {file}")


if __name__ == "__main__":
    main() 