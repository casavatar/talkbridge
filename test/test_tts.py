#!/usr/bin/env python3
"""
TTS Module Test Script

This script tests the TTS module functionality to ensure it works correctly.
"""
import pytest
from talkbridge.tts import TTSEngine


import os
import tempfile

# Add src to path for imports

def test_imports():
    """Test that all modules can be imported correctly."""
    print("Testing imports...")
    
    try:
        from tts import synthesize_voice, VoiceCloner
        print("✅ TTS module imports successfully")
        return True
    except ImportError as e:
        print(f"❌ Import failed: {e}")
        return False

def test_basic_synthesis():
    """Test basic text-to-speech synthesis."""
    print("\nTesting basic synthesis...")
    
    try:
        from tts import synthesize_voice
        
        # Test with simple text
        text = "Hello, this is a test."
        audio_bytes = synthesize_voice(text, clone_voice=False)
        
        if audio_bytes and len(audio_bytes) > 0:
            print(f"✅ Basic synthesis successful: {len(audio_bytes)} bytes")
            return True
        else:
            print("❌ Basic synthesis failed: No audio generated")
            return False
            
    except Exception as e:
        print(f"❌ Basic synthesis failed: {e}")
        return False

def test_file_output():
    """Test saving audio to file."""
    print("\nTesting file output...")
    
    try:
        from tts import synthesize_voice
        
        # Create temporary file
        with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as temp_file:
            output_path = temp_file.name
        
        # Synthesize to file
        text = "Testing file output."
        result = synthesize_voice(text, output_path=output_path, clone_voice=False)
        
        # Check if file was created and has content
        if os.path.exists(output_path) and os.path.getsize(output_path) > 0:
            print(f"✅ File output successful: {output_path}")
            os.unlink(output_path)  # Clean up
            return True
        else:
            print("❌ File output failed: File not created or empty")
            return False
            
    except Exception as e:
        print(f"❌ File output failed: {e}")
        return False

def test_voice_cloning_setup():
    """Test voice cloning setup (without actual samples)."""
    print("\nTesting voice cloning setup...")
    
    try:
        from tts import setup_voice_cloning
        
        # Test with non-existent files (should handle gracefully)
        fake_samples = ["fake_sample_1.wav", "fake_sample_2.wav"]
        result = setup_voice_cloning(fake_samples)
        
        # Should return False for invalid samples
        if result is False:
            print("✅ Voice cloning setup handled invalid samples correctly")
            return True
        else:
            print("❌ Voice cloning setup should have failed with invalid samples")
            return False
            
    except Exception as e:
        print(f"❌ Voice cloning setup test failed: {e}")
        return False

def test_system_info():
    """Test system information retrieval."""
    print("\nTesting system info...")
    
    try:
        from tts import get_synthesis_info, list_available_models
        
        # Get synthesis info
        info = get_synthesis_info()
        if isinstance(info, dict) and len(info) > 0:
            print("✅ System info retrieved successfully")
            print(f"   Model: {info.get('model_name', 'Unknown')}")
            print(f"   Device: {info.get('device', 'Unknown')}")
        else:
            print("❌ System info retrieval failed")
            return False
        
        # Get available models
        models = list_available_models()
        if isinstance(models, list):
            print(f"✅ Available models retrieved: {len(models)} models")
        else:
            print("❌ Available models retrieval failed")
            return False
            
        return True
        
    except Exception as e:
        print(f"❌ System info test failed: {e}")
        return False

def test_error_handling():
    """Test error handling for invalid inputs."""
    print("\nTesting error handling...")
    
    try:
        from tts import synthesize_voice
        
        # Test empty text
        try:
            synthesize_voice("")
            print("❌ Should have raised ValueError for empty text")
            return False
        except ValueError:
            print("✅ Correctly handled empty text")
        
        # Test whitespace-only text
        try:
            synthesize_voice("   ")
            print("❌ Should have raised ValueError for whitespace-only text")
            return False
        except ValueError:
            print("✅ Correctly handled whitespace-only text")
        
        # Test None text
        try:
            synthesize_voice(None)
            print("❌ Should have raised ValueError for None text")
            return False
        except (ValueError, TypeError):
            print("✅ Correctly handled None text")
        
        return True
        
    except Exception as e:
        print(f"❌ Error handling test failed: {e}")
        return False

def main():
    """Run all tests."""
    print("🧪 TTS Module Test Suite")
    print("=" * 40)
    
    tests = [
        ("Import Test", test_imports),
        ("Basic Synthesis", test_basic_synthesis),
        ("File Output", test_file_output),
        ("Voice Cloning Setup", test_voice_cloning_setup),
        ("System Info", test_system_info),
        ("Error Handling", test_error_handling),
    ]
    
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        print(f"\n--- {test_name} ---")
        if test_func():
            passed += 1
        else:
            print(f"❌ {test_name} failed")
    
    print("\n" + "=" * 40)
    print(f"📊 Test Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed! TTS module is working correctly.")
        return 0
    else:
        print("⚠️  Some tests failed. Please check the errors above.")
        return 1

if __name__ == "__main__":
    exit(main()) 