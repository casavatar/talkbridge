#!/usr/bin/env python3
"""
TalkBridge Demo - Animation Example
===================================

Módulo animation_example para TalkBridge

Author: TalkBridge Team
Date: 2025-08-19
Version: 1.0

Requirements:
- PyQt6
======================================================================
Functions:
- example_webcam_face_sync: Example of webcam-based face sync.
- example_avatar_face_sync: Example of avatar-based face sync.
- example_facial_landmark_detection: Example of facial landmark detection.
- example_integration_with_tts: Example of integrating face sync with TTS output.
- main: Run all animation examples.
======================================================================
"""
from talkbridge.animation import FaceSync


import os

# Import TalkBridge animation modules
from talkbridge.animation import FaceSync

def example_webcam_face_sync():
    """Example of webcam-based face sync."""
    print("=== Webcam Face Sync Example ===")
    
    try:
        # Create face sync with webcam
        face_sync = FaceSync(use_webcam=True)
        
        # Example audio file (you would use your TTS output)
        audio_file = "example_audio.wav"
        
        if not os.path.exists(audio_file):
            print(f"⚠️  Audio file not found: {audio_file}")
            print("   Please create an audio file or use TTS output")
            return False
        
        print(f"Starting webcam face sync with: {audio_file}")
        print("Press 'q' to quit during playback")
        
        # Run face sync
        success = face_sync.run_face_sync(audio_file)
        
        if success:
            print("✅ Webcam face sync completed")
            return True
        else:
            print("❌ Webcam face sync failed")
            return False
            
    except Exception as e:
        print(f"❌ Webcam example failed: {e}")
        return False

def example_avatar_face_sync():
    """Example of avatar-based face sync."""
    print("\n=== Avatar Face Sync Example ===")
    
    try:
        # Check for avatar image
        avatar_path = "avatar.jpg"
        if not os.path.exists(avatar_path):
            print(f"⚠️  Avatar image not found: {avatar_path}")
            print("   Please place an avatar image in the current directory")
            return False
        
        # Create face sync with avatar
        face_sync = FaceSync(use_webcam=False, avatar_path=avatar_path)
        
        # Example audio file
        audio_file = "example_audio.wav"
        if not os.path.exists(audio_file):
            print(f"⚠️  Audio file not found: {audio_file}")
            print("   Please create an audio file or use TTS output")
            return False
        
        print(f"Starting avatar face sync with: {audio_file}")
        print("Press 'q' to quit during playback")
        
        # Run face sync
        success = face_sync.run_face_sync(audio_file)
        
        if success:
            print("✅ Avatar face sync completed")
            return True
        else:
            print("❌ Avatar face sync failed")
            return False
            
    except Exception as e:
        print(f"❌ Avatar example failed: {e}")
        return False

def example_facial_landmark_detection():
    """Example of facial landmark detection."""
    print("\n=== Facial Landmark Detection Example ===")
    
    try:
        # Create face sync for landmark detection
        face_sync = FaceSync(use_webcam=True)
        
        print("Starting facial landmark detection...")
        print("Press 'q' to quit")
        
        # Simple detection loop
        cap = face_sync.cap
        
        while True:
            ret, frame = cap.read()
            if not ret:
                break
            
            # Detect landmarks
            landmarks_data = face_sync.detect_facial_landmarks(frame)
            
            if landmarks_data:
                # Draw landmarks
                frame = face_sync._draw_landmarks(frame, landmarks_data)
                
                # Add information overlay
                cv2.putText(frame, "Facial Landmarks Detected", (10, 30), 
                          cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
                cv2.putText(frame, f"Mouth Opening: {landmarks_data['mouth_open']:.2f}", (10, 60), 
                          cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 255), 1)
                cv2.putText(frame, f"Eye Blink: {landmarks_data['eye_blink']:.2f}", (10, 80), 
                          cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 0, 255), 1)
                cv2.putText(frame, "Press 'q' to quit", (10, frame.shape[0] - 20), 
                          cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1)
            
            cv2.imshow('Facial Landmark Detection', frame)
            
            key = cv2.waitKey(1) & 0xFF
            if key == ord('q'):
                break
        
        cv2.destroyAllWindows()
        print("✅ Facial landmark detection completed")
        return True
        
    except Exception as e:
        print(f"❌ Landmark detection example failed: {e}")
        return False

def example_integration_with_tts():
    """Example of integrating face sync with TTS output."""
    print("\n=== TTS Integration Example ===")
    
    try:
        # This would integrate with your TTS module
        # from ..tts import synthesize_voice
        
        print("This example shows how to integrate face sync with TTS:")
        print("1. Generate audio using TTS module")
        print("2. Use the audio file with face sync")
        print("3. Real-time lip sync with generated speech")
        
        # Example workflow:
        # 1. Generate audio with TTS
        # audio_bytes = synthesize_voice("Hello, this is a test message.")
        # 
        # 2. Save audio to file
        # with open("tts_output.wav", "wb") as f:
        #     f.write(audio_bytes)
        # 
        # 3. Use with face sync
        # face_sync = FaceSync(use_webcam=True)
        # face_sync.run_face_sync("tts_output.wav")
        
        print("✅ TTS integration example completed")
        return True
        
    except Exception as e:
        print(f"❌ TTS integration example failed: {e}")
        return False

def main():
    """Run all animation examples."""
    print("🎭 Animation Module Examples")
    print("=" * 50)
    
    # Run examples
    examples = [
        ("Facial Landmark Detection", example_facial_landmark_detection),
        ("Webcam Face Sync", example_webcam_face_sync),
        ("Avatar Face Sync", example_avatar_face_sync),
        ("TTS Integration", example_integration_with_tts),
    ]
    
    passed = 0
    total = len(examples)
    
    for example_name, example_func in examples:
        print(f"\n--- {example_name} ---")
        if example_func():
            passed += 1
        else:
            print(f"❌ {example_name} failed")
    
    print("\n" + "=" * 50)
    print(f"📊 Example Results: {passed}/{total} examples passed")
    
    if passed == total:
        print("🎉 All examples completed successfully!")
    else:
        print("⚠️  Some examples failed. Check the errors above.")
    
    print("\nUsage Instructions:")
    print("1. Ensure you have a webcam connected")
    print("2. Install required dependencies: pip install -r requirements.txt")
    print("3. Create audio files for testing")
    print("4. Optionally place avatar images for avatar examples")
    print("5. Run the face sync demo: python src/animation/face_sync_demo.py")

if __name__ == "__main__":
    main() 