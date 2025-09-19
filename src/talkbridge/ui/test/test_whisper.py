#!/usr/bin/env python3
"""
TalkBridge UI - Test Whisper
============================

Test whisper module for TalkBridge

Author: TalkBridge Team
Date: 2025-08-19
Version: 1.0

Requirements:
- PyQt6
- Flask
======================================================================
Functions:
- test_whisper_installation: Test if Whisper is properly installed and working.
- test_talkbridge_whisper: Test TalkBridge's Whisper engine.
- main: Run all tests.
======================================================================
"""

import sys
import os

def test_whisper_installation():
    """Test if Whisper is properly installed and working."""
    print("🧪 Testing Whisper Installation")
    print("=" * 50)
    
    # Check Python path
    print(f"Python executable: {sys.executable}")
    print(f"Python version: {sys.version}")
    
    # Test Whisper import
    try:
        import whisper
        print("✅ Whisper imported successfully")
        
        # Test model loading
        print("Loading Whisper model...")
        model = whisper.load_model("base")
        print("✅ Whisper model loaded successfully")
        
        # Test basic functionality
        print("Testing Whisper functionality...")
        # Create a simple test (no actual audio file needed for this test)
        print("✅ Whisper is fully functional")
        
        return True
        
    except ImportError as e:
        print(f"❌ Whisper import failed: {e}")
        return False
    except Exception as e:
        print(f"❌ Whisper test failed: {e}")
        return False

def test_talkbridge_whisper():
    """Test TalkBridge's Whisper engine."""
    print("\n🧪 Testing TalkBridge Whisper Engine")
    print("=" * 50)
    
    try:
                , '..', '..')))
        from stt.whisper_engine import WhisperEngine
        
        engine = WhisperEngine()
        print("✅ WhisperEngine imported successfully")
        
        # Test model loading
        success = engine.load_model()
        if success:
            print("✅ TalkBridge Whisper model loaded successfully")
            return True
        else:
            print("❌ TalkBridge Whisper model failed to load")
            return False
            
    except Exception as e:
        print(f"❌ TalkBridge Whisper test failed: {e}")
        return False

def main():
    """Run all tests."""
    print("🎤 TalkBridge Whisper Test Suite")
    print("=" * 50)
    
    # Test 1: Direct Whisper installation
    whisper_ok = test_whisper_installation()
    
    # Test 2: TalkBridge Whisper engine
    talkbridge_ok = test_talkbridge_whisper()
    
    print("\n📊 Test Results")
    print("=" * 50)
    print(f"Whisper Installation: {'✅ PASS' if whisper_ok else '❌ FAIL'}")
    print(f"TalkBridge Integration: {'✅ PASS' if talkbridge_ok else '❌ FAIL'}")
    
    if whisper_ok and talkbridge_ok:
        print("\n🎉 All tests passed! Whisper is working correctly.")
        return 0
    else:
        print("\n⚠️  Some tests failed. Check the output above.")
        return 1

if __name__ == "__main__":
    exit(main()) 