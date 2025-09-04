#!/usr/bin/env python3
"""
TalkBridge Demo - Run Demo
==========================

Run demo module for TalkBridge

Author: TalkBridge Team
Date: 2025-08-19
Version: 1.0

Requirements:
- PyQt6
======================================================================
Functions:
- test_demo_system: Test the demo system functionality.
- run_web_demo: Run the web-based demo interface.
- show_config: Show demo configuration.
- main: Main demo runner function.
======================================================================
"""

import sys
import argparse
import time
from pathlib import Path

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from demo import (
    is_demo_mode, get_demo_runner, run_demo_conversation,
    render_demo_dashboard, ensure_demo_files_exist
)


def test_demo_system():
    """Test the demo system functionality."""
    print("🧪 Testing Demo System...")
    print(f"Demo mode enabled: {is_demo_mode()}")
    
    # Ensure demo files exist
    print("📁 Ensuring demo files exist...")
    ensure_demo_files_exist()
    print("✅ Demo files ready")
    
    # Test demo runner
    print("🔄 Testing demo runner...")
    demo_runner = get_demo_runner()
    print(f"✅ Demo runner initialized: {type(demo_runner).__name__}")
    
    # Test conversation
    print("💬 Running test conversation...")
    try:
        results = run_demo_conversation()
        print("✅ Test conversation completed!")
        print(f"Results: {list(results.keys())}")
        
        if "error" not in results:
            print("📝 Transcription:", results.get("transcription", "N/A"))
            print("🌐 Translation:", results.get("translation", "N/A"))
            print("🤖 Response:", results.get("llm_response", "N/A"))
            print("🔊 Audio length:", len(results.get("voice_audio", b"")))
            print("👤 Avatar:", results.get("avatar_image", "N/A"))
        else:
            print(f"❌ Error: {results['error']}")
            
    except Exception as e:
        print(f"❌ Test conversation failed: {e}")
    
    # Test conversation history
    print("📚 Testing conversation history...")
    history = demo_runner.get_conversation_history()
    print(f"✅ Found {len(history)} conversation entries")
    
    print("\n🎉 Demo system test completed!")


def run_web_demo():
    """Run the web-based demo interface."""
    print("🌐 Starting web demo interface...")
    print("📝 To run the web demo, use:")
    print("   streamlit run src/demo/demo_ui.py")
    print("\nOr integrate with the main web interface:")
    print("   streamlit run src/ui/web_interface.py")


def show_config():
    """Show demo configuration."""
    print("⚙️ Demo Configuration:")
    print(f"Demo mode: {'ENABLED' if is_demo_mode() else 'DISABLED'}")
    
    from demo.demo_config import DEMO_SETTINGS, DEMO_FILES
    
    print("\n📊 Settings:")
    for key, value in DEMO_SETTINGS.items():
        print(f"  {key}: {value}")
    
    print("\n📁 Files:")
    for key, path in DEMO_FILES.items():
        print(f"  {key}: {path}")
    
    print("\n🎭 Conversation Flow:")
    from demo.demo_config import DEMO_CONVERSATION_FLOW
    for i, step in enumerate(DEMO_CONVERSATION_FLOW, 1):
        print(f"  {i}. {step['step']}: {step['description']} ({step['delay']}s)")


def main():
    """Main demo runner function."""
    parser = argparse.ArgumentParser(description="TalkBridge Demo Runner")
    parser.add_argument("--test", action="store_true", help="Run demo system tests")
    parser.add_argument("--web", action="store_true", help="Show web demo instructions")
    parser.add_argument("--config", action="store_true", help="Show demo configuration")
    parser.add_argument("--run", action="store_true", help="Run a demo conversation")
    
    args = parser.parse_args()
    
    print("🎭 TalkBridge Demo Runner")
    print("=" * 40)
    
    if args.test:
        test_demo_system()
    elif args.web:
        run_web_demo()
    elif args.config:
        show_config()
    elif args.run:
        print("💬 Running demo conversation...")
        results = run_demo_conversation()
        if "error" not in results:
            print("✅ Demo conversation completed successfully!")
            print(f"Transcription: {results.get('transcription', 'N/A')}")
            print(f"Translation: {results.get('translation', 'N/A')}")
            print(f"Response: {results.get('llm_response', 'N/A')}")
        else:
            print(f"❌ Demo conversation failed: {results['error']}")
    else:
        # Default: show help and run tests
        print("No specific action specified. Running tests...")
        print()
        test_demo_system()
        print()
        show_config()
        print()
        print("For more options, use --help")


if __name__ == "__main__":
    main() 