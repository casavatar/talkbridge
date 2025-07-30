#!/usr/bin/env python3
#----------------------------------------------------------------------------------------------------------------------------
# description: Face Sync Demo Script
#----------------------------------------------------------------------------------------------------------------------------
# 
# author: ingekastel
# date: 2025-06-02
# version: 1.0
#----------------------------------------------------------------------------------------------------------------------------
# 
# requirements:
# - numpy Python package
# - mediapipe Python package
# - pygame Python package
# - librosa Python package
# - opencv-python Python package
# - soundfile Python package
# - time Python package
# - threading Python package
# - typing Python package
# - dataclasses Python package  
#----------------------------------------------------------------------------------------------------------------------------       
# functions:
# - demo_webcam_face_sync: Demo the webcam face sync capabilities
# - demo_avatar_face_sync: Demo the avatar face sync capabilities
# - demo_facial_landmarks: Demo the facial landmark detection capabilities
# - create_test_audio: Create a test audio file for demo
# - main: Main function to run all demos
#----------------------------------------------------------------------------------------------------------------------------   

import os
import sys
import tempfile
from pathlib import Path

# Add src to path for imports
sys.path.append(str(Path(__file__).parent))

from face_sync import FaceSync


def demo_webcam_face_sync():
    """Demonstrate face sync with webcam input."""
    print("=== Webcam Face Sync Demo ===")
    
    try:
        # Create face sync with webcam
        face_sync = FaceSync(use_webcam=True)
        
        # Check if we have a test audio file
        test_audio = "test_audio.wav"
        if not os.path.exists(test_audio):
            print(f"⚠️  Test audio file not found: {test_audio}")
            print("   Please create a test_audio.wav file or use an existing audio file.")
            return False
        
        print(f"Using test audio: {test_audio}")
        print("Starting webcam face sync...")
        print("Press 'q' to quit during playback")
        
        # Run face sync
        success = face_sync.run_face_sync(test_audio)
        
        if success:
            print("✅ Webcam face sync completed successfully")
            return True
        else:
            print("❌ Webcam face sync failed")
            return False
            
    except Exception as e:
        print(f"❌ Webcam demo failed: {e}")
        return False


def demo_avatar_face_sync():
    """Demonstrate face sync with static avatar."""
    print("\n=== Avatar Face Sync Demo ===")
    
    try:
        # Check for avatar image
        avatar_path = "avatar.jpg"
        if not os.path.exists(avatar_path):
            print(f"⚠️  Avatar image not found: {avatar_path}")
            print("   Please place an avatar image named 'avatar.jpg' in the current directory.")
            return False
        
        # Create face sync with avatar
        face_sync = FaceSync(use_webcam=False, avatar_path=avatar_path)
        
        # Check for test audio
        test_audio = "test_audio.wav"
        if not os.path.exists(test_audio):
            print(f"⚠️  Test audio file not found: {test_audio}")
            print("   Please create a test_audio.wav file or use an existing audio file.")
            return False
        
        print(f"Using avatar: {avatar_path}")
        print(f"Using test audio: {test_audio}")
        print("Starting avatar face sync...")
        print("Press 'q' to quit during playback")
        
        # Run face sync
        success = face_sync.run_face_sync(test_audio)
        
        if success:
            print("✅ Avatar face sync completed successfully")
            return True
        else:
            print("❌ Avatar face sync failed")
            return False
            
    except Exception as e:
        print(f"❌ Avatar demo failed: {e}")
        return False


def demo_facial_landmarks():
    """Demonstrate facial landmark detection without audio."""
    print("\n=== Facial Landmark Detection Demo ===")
    
    try:
        # Create face sync with webcam
        face_sync = FaceSync(use_webcam=True)
        
        print("Starting facial landmark detection...")
        print("Press 'q' to quit")
        
        # Simple landmark detection loop
        cap = face_sync.cap
        face_mesh = face_sync.face_mesh
        
        while True:
            ret, frame = cap.read()
            if not ret:
                break
            
            # Detect landmarks
            landmarks_data = face_sync.detect_facial_landmarks(frame)
            
            if landmarks_data:
                # Draw landmarks
                frame = face_sync._draw_landmarks(frame, landmarks_data)
                
                # Add info text
                cv2.putText(frame, "Facial Landmarks Detected", (10, 30), 
                          cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
                cv2.putText(frame, f"Mouth Open: {landmarks_data['mouth_open']:.2f}", (10, 60), 
                          cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 255), 1)
                cv2.putText(frame, f"Eye Blink: {landmarks_data['eye_blink']:.2f}", (10, 80), 
                          cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 0, 255), 1)
            
            cv2.imshow('Facial Landmarks', frame)
            
            key = cv2.waitKey(1) & 0xFF
            if key == ord('q'):
                break
        
        cv2.destroyAllWindows()
        print("✅ Facial landmark detection demo completed")
        return True
        
    except Exception as e:
        print(f"❌ Facial landmark demo failed: {e}")
        return False


def create_test_audio():
    """Create a simple test audio file for demo."""
    print("\n=== Creating Test Audio ===")
    
    try:
        import numpy as np
        import soundfile as sf
        
        # Create a simple test audio
        sample_rate = 22050
        duration = 3.0  # 3 seconds
        t = np.linspace(0, duration, int(sample_rate * duration))
        
        # Create a simple tone with some variation
        frequency = 440  # A4 note
        audio = np.sin(2 * np.pi * frequency * t) * 0.3
        
        # Add some amplitude variation to simulate speech
        envelope = np.sin(2 * np.pi * 2 * t) * 0.5 + 0.5  # 2 Hz envelope
        audio = audio * envelope
        
        # Save test audio
        test_audio_path = "test_audio.wav"
        sf.write(test_audio_path, audio, sample_rate)
        
        print(f"✅ Created test audio: {test_audio_path}")
        return True
        
    except Exception as e:
        print(f"❌ Failed to create test audio: {e}")
        return False


def main():
    """Run all face sync demos."""
    print("🎭 Face Sync Demo")
    print("=" * 50)
    
    # Create test audio if needed
    if not os.path.exists("test_audio.wav"):
        create_test_audio()
    
    # Run demos
    demos = [
        ("Facial Landmark Detection", demo_facial_landmarks),
        ("Webcam Face Sync", demo_webcam_face_sync),
        ("Avatar Face Sync", demo_avatar_face_sync),
    ]
    
    passed = 0
    total = len(demos)
    
    for demo_name, demo_func in demos:
        print(f"\n--- {demo_name} ---")
        if demo_func():
            passed += 1
        else:
            print(f"❌ {demo_name} failed")
    
    print("\n" + "=" * 50)
    print(f"📊 Demo Results: {passed}/{total} demos passed")
    
    if passed == total:
        print("🎉 All demos completed successfully!")
    else:
        print("⚠️  Some demos failed. Check the errors above.")
    
    print("\nSetup Instructions:")
    print("1. Ensure you have a webcam connected")
    print("2. Place 'test_audio.wav' in the current directory")
    print("3. Optionally place 'avatar.jpg' for avatar demo")
    print("4. Install required dependencies: pip install -r requirements.txt")


if __name__ == "__main__":
    main() 