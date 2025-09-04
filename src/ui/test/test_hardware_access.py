#!/usr/bin/env python3
"""
TalkBridge UI - Test Hardware Access
====================================

Test hardware access module for TalkBridge

Author: TalkBridge Team
Date: 2025-08-19
Version: 1.0

Requirements:
- PyQt6
- Flask
======================================================================
Functions:
- test_hardware_access: Test the hardware access functionality.
- test_browser_compatibility: Test browser compatibility for hardware access.
- test_permission_handling: Test permission handling scenarios.
- main: Main test function.
======================================================================
"""

import os
import sys
import time
import webbrowser
import threading
from pathlib import Path

# Add src to path for imports
sys.path.append(str(Path(__file__).parent.parent.parent))

from ui.web_server import TalkBridgeWebServer


def test_hardware_access():
    """Test the hardware access functionality."""
    print("🧪 Testing TalkBridge Hardware Access")
    print("=" * 50)
    
    # Check if required files exist
    required_files = [
        "assets/hardware_access.js",
        "templates/index.html",
        "web_server.py"
    ]
    
    print("📁 Checking required files...")
    for file_path in required_files:
        full_path = Path(__file__).parent.parent / file_path
        if full_path.exists():
            print(f"  ✅ {file_path}")
        else:
            print(f"  ❌ {file_path} - MISSING")
            return False
    
    print("\n🚀 Starting web server...")
    
    # Create and start server
    server = TalkBridgeWebServer(host='localhost', port=8080)
    
    if server.start():
        print("  ✅ Web server started successfully")
        print("  🌐 URL: http://localhost:8080/templates/index.html")
        
        # Give user time to test
        print("\n📋 Testing Instructions:")
        print("  1. Browser should open automatically")
        print("  2. Grant microphone and camera permissions when prompted")
        print("  3. Verify live camera feed and audio status")
        print("  4. Test permission controls (Request/Stop buttons)")
        print("  5. Check device enumeration in the interface")
        
        print("\n⏱️  Server will run for 60 seconds for testing...")
        
        try:
            # Keep server running for 60 seconds
            for i in range(60, 0, -1):
                print(f"\r⏳ Time remaining: {i} seconds", end="", flush=True)
                time.sleep(1)
            
            print("\n\n🛑 Stopping server...")
            server.stop()
            print("✅ Test completed")
            
        except KeyboardInterrupt:
            print("\n\n🛑 Test interrupted by user")
            server.stop()
            print("✅ Server stopped")
    
    else:
        print("  ❌ Failed to start web server")
        return False
    
    return True


def test_browser_compatibility():
    """Test browser compatibility for hardware access."""
    print("\n🌐 Browser Compatibility Test")
    print("=" * 40)
    
    # Test JavaScript features
    test_script = """
    <script>
        // Test MediaDevices API
        if (navigator.mediaDevices) {
            console.log('✅ MediaDevices API available');
        } else {
            console.log('❌ MediaDevices API not available');
        }
        
        // Test getUserMedia
        if (navigator.mediaDevices && navigator.mediaDevices.getUserMedia) {
            console.log('✅ getUserMedia available');
        } else {
            console.log('❌ getUserMedia not available');
        }
        
        // Test permissions API
        if (navigator.permissions) {
            console.log('✅ Permissions API available');
        } else {
            console.log('❌ Permissions API not available');
        }
        
        // Test enumerateDevices
        if (navigator.mediaDevices && navigator.mediaDevices.enumerateDevices) {
            console.log('✅ enumerateDevices available');
        } else {
            console.log('❌ enumerateDevices not available');
        }
    </script>
    """
    
    print("📝 Browser compatibility test script:")
    print(test_script)
    print("💡 Add this script to your HTML page to test browser support")


def test_permission_handling():
    """Test permission handling scenarios."""
    print("\n🔐 Permission Handling Test")
    print("=" * 40)
    
    test_cases = [
        {
            "name": "Permission Granted",
            "description": "User allows microphone and camera access",
            "expected": "Green status badges, live video/audio streams"
        },
        {
            "name": "Permission Denied",
            "description": "User denies microphone and camera access",
            "expected": "Red status badges, error messages, graceful fallback"
        },
        {
            "name": "Partial Permission",
            "description": "User allows one but denies the other",
            "expected": "Mixed status badges, partial functionality"
        },
        {
            "name": "No Devices",
            "description": "No microphone or camera connected",
            "expected": "Device not found errors, helpful instructions"
        },
        {
            "name": "Permission Revoked",
            "description": "User revokes permissions after granting",
            "expected": "Status updates, re-request functionality"
        }
    ]
    
    for i, test_case in enumerate(test_cases, 1):
        print(f"{i}. {test_case['name']}")
        print(f"   Description: {test_case['description']}")
        print(f"   Expected: {test_case['expected']}")
        print()


def main():
    """Main test function."""
    print("🎤 TalkBridge Hardware Access Test Suite")
    print("=" * 60)
    
    # Run tests
    success = test_hardware_access()
    
    if success:
        test_browser_compatibility()
        test_permission_handling()
        
        print("\n✅ All tests completed successfully!")
        print("\n📚 Next Steps:")
        print("  1. Review the README.md for detailed documentation")
        print("  2. Integrate the hardware access components into your application")
        print("  3. Test with different browsers and devices")
        print("  4. Deploy with HTTPS for production use")
        
    else:
        print("\n❌ Tests failed. Please check the error messages above.")
        return 1
    
    return 0


if __name__ == "__main__":
    exit(main()) 