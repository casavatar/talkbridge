#!/usr/bin/env python3
"""
TalkBridge Demo - Tts Example
=============================

TTS example module for TalkBridge

Author: TalkBridge Team
Date: 2025-08-19
Version: 1.0

Requirements:
- PyQt6
======================================================================
Functions:
- example_basic_usage: Example of basic TTS usage without voice cloning.
- example_voice_cloning: Example of voice cloning with reference samples.
- example_multilingual: Example of multilingual synthesis.
- example_system_info: Example of getting system information.
- example_error_handling: Example of error handling.
- main: Run all examples.
======================================================================
"""
from ..tts import VoiceCloner, TTSEngine


import os
from pathlib import Path


from ..tts import synthesize_voice, setup_voice_cloning, get_synthesis_info

def example_basic_usage():
    """Example of basic TTS usage without voice cloning."""
    print("=== Basic TTS Example ===")
    
    # Simple text-to-speech synthesis
    text = "Hello! This is a basic example of text-to-speech synthesis."
    
    try:
        # Generate audio as bytes
        audio_bytes = synthesize_voice(text, clone_voice=False)
        print(f"✅ Generated {len(audio_bytes)} bytes of audio")
        
        # Save to file
        synthesize_voice(text, output_path="basic_example.wav", clone_voice=False)
        print("✅ Saved audio to 'basic_example.wav'")
        
    except Exception as e:
        print(f"❌ Basic example failed: {e}")

def example_voice_cloning():
    """Example of voice cloning with reference samples."""
    print("\n=== Voice Cloning Example ===")
    
    # Check for reference samples
    reference_samples = ["my_voice_1.wav", "my_voice_2.wav"]
    available_samples = [s for s in reference_samples if os.path.exists(s)]
    
    if not available_samples:
        print("⚠️  No reference samples found. Creating demo samples...")
        
        # Create demo samples
        demo_texts = [
            "This is my first voice sample for cloning.",
            "This is my second voice sample for cloning."
        ]
        
        for i, text in enumerate(demo_texts, 1):
            sample_path = f"my_voice_{i}.wav"
            synthesize_voice(text, output_path=sample_path, clone_voice=False)
            print(f"✅ Created demo sample {i}: {sample_path}")
        
        available_samples = [f"my_voice_{i}.wav" for i in range(1, 3)]
    
    # Set up voice cloning
    print(f"Setting up voice cloning with {len(available_samples)} samples...")
    success = setup_voice_cloning(available_samples)
    
    if success:
        # Synthesize with cloned voice
        text = "This text should sound like my voice thanks to voice cloning!"
        
        try:
            audio_bytes = synthesize_voice(
                text=text,
                reference_samples=available_samples
            )
            print(f"✅ Generated cloned voice audio: {len(audio_bytes)} bytes")
            
            # Save cloned voice audio
            synthesize_voice(
                text=text,
                output_path="cloned_voice_example.wav",
                reference_samples=available_samples
            )
            print("✅ Saved cloned voice audio to 'cloned_voice_example.wav'")
            
        except Exception as e:
            print(f"❌ Voice cloning synthesis failed: {e}")
    else:
        print("❌ Voice cloning setup failed")

def example_multilingual():
    """Example of multilingual synthesis."""
    print("\n=== Multilingual Example ===")
    
    texts = {
        "en": "Hello! This is English text.",
        "es": "¡Hola! Este es texto en español.",
        "fr": "Bonjour! Ceci est du texte en français.",
        "de": "Hallo! Das ist deutscher Text."
    }
    
    for language, text in texts.items():
        try:
            output_path = f"multilingual_{language}.wav"
            synthesize_voice(
                text=text,
                output_path=output_path,
                language=language,
                clone_voice=False
            )
            print(f"✅ {language} audio saved to '{output_path}'")
            
        except Exception as e:
            print(f"❌ {language} synthesis failed: {e}")

def example_system_info():
    """Example of getting system information."""
    print("\n=== System Information ===")
    
    try:
        info = get_synthesis_info()
        print("System Information:")
        for key, value in info.items():
            print(f"  {key}: {value}")
            
    except Exception as e:
        print(f"❌ Failed to get system info: {e}")

def example_error_handling():
    """Example of error handling."""
    print("\n=== Error Handling Example ===")
    
    # Test various error conditions
    test_cases = [
        ("", "Empty text"),
        ("   ", "Whitespace-only text"),
        ("A" * 1000, "Very long text"),  # This might exceed limits
    ]
    
    for text, description in test_cases:
        try:
            synthesize_voice(text, clone_voice=False)
            print(f"✅ {description}: Unexpected success")
        except ValueError as e:
            print(f"✅ {description}: Correctly caught ValueError - {e}")
        except RuntimeError as e:
            print(f"✅ {description}: Correctly caught RuntimeError - {e}")
        except Exception as e:
            print(f"⚠️  {description}: Unexpected exception - {e}")

def main():
    """Run all examples."""
    print("🎤 TTS Module Examples")
    print("=" * 50)
    
    # Run examples
    example_basic_usage()
    example_voice_cloning()
    example_multilingual()
    example_system_info()
    example_error_handling()
    
    print("\n" + "=" * 50)
    print("🎉 Examples completed!")
    print("\nGenerated files:")
    for file in os.listdir("."):
        if file.endswith(".wav") and file.startswith(("basic_", "cloned_", "multilingual_", "my_voice_")):
            print(f"  - {file}")

if __name__ == "__main__":
    main() 