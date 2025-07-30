#!/usr/bin/env python3
"""
Simple test script for the animation system.
"""

import time
import sys
import os

# Add the src directory to the path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def test_loading_animations():
    """Test loading animations."""
    print("Testing loading animations...")
    
    try:
        from animation.loading_animation import SpinnerAnimation, ProgressBar, PulseAnimation
        
        # Test spinner
        print("  - Testing spinner animation...")
        spinner = SpinnerAnimation("Testing spinner...", style="dots")
        spinner.start()
        time.sleep(2)
        spinner.stop()
        
        # Test progress bar
        print("  - Testing progress bar...")
        progress = ProgressBar(100, 30, "Testing progress")
        progress.start()
        for i in range(0, 101, 10):
            progress.update(i)
            time.sleep(0.1)
        progress.stop()
        
        # Test pulse
        print("  - Testing pulse animation...")
        pulse = PulseAnimation("Testing pulse...")
        pulse.start()
        time.sleep(2)
        pulse.stop()
        
        print("✅ Loading animations test passed!")
        return True
        
    except Exception as e:
        print(f"❌ Loading animations test failed: {e}")
        return False

def test_interactive_animations():
    """Test interactive animations."""
    print("Testing interactive animations...")
    
    try:
        from animation.interactive_animations import InteractiveAnimations
        
        # Test animation manager
        manager = InteractiveAnimations()
        manager.create_particle_system("test_particles", 10)
        manager.create_geometric_animation("test_circle", "circle")
        
        print(f"  - Created animations: {manager.list_animations()}")
        
        # Test starting and stopping
        for name in manager.list_animations():
            print(f"  - Testing {name}...")
            manager.start_animation(name)
            time.sleep(1)
            manager.stop_animation(name)
        
        manager.stop_all()
        print("✅ Interactive animations test passed!")
        return True
        
    except Exception as e:
        print(f"❌ Interactive animations test failed: {e}")
        return False

def test_audio_visualizer():
    """Test audio visualizer (basic test without GUI)."""
    print("Testing audio visualizer...")
    
    try:
        from animation.audio_visualizer import AudioVisualizer
        import numpy as np
        
        # Test creation
        visualizer = AudioVisualizer("bars")
        print("  - Audio visualizer created successfully")
        
        # Test style change
        visualizer.change_style("wave")
        print("  - Style change successful")
        
        print("✅ Audio visualizer test passed!")
        return True
        
    except Exception as e:
        print(f"❌ Audio visualizer test failed: {e}")
        return False

def test_imports():
    """Test that all modules can be imported."""
    print("Testing imports...")
    
    try:
        from animation import AudioVisualizer, LoadingAnimation, InteractiveAnimations
        from animation.loading_animation import SpinnerAnimation, ProgressBar, PulseAnimation, WaveAnimation
        from animation.interactive_animations import ParticleSystem, GeometricAnimation, WaveformAnimation
        
        print("✅ All imports successful!")
        return True
        
    except Exception as e:
        print(f"❌ Import test failed: {e}")
        return False

def main():
    """Run all tests."""
    print("🧪 Animation System Test Suite")
    print("=" * 40)
    
    tests = [
        ("Import Test", test_imports),
        ("Loading Animations", test_loading_animations),
        ("Interactive Animations", test_interactive_animations),
        ("Audio Visualizer", test_audio_visualizer),
    ]
    
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        print(f"\n📋 Running {test_name}...")
        if test_func():
            passed += 1
        print()
    
    print("=" * 40)
    print(f"📊 Test Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed! Animation system is working correctly.")
        return 0
    else:
        print("⚠️  Some tests failed. Check the output above for details.")
        return 1

if __name__ == "__main__":
    exit(main()) 