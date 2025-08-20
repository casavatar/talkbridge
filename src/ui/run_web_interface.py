#!/usr/bin/env python3
"""
TalkBridge UI - Run Web Interface
=================================

Interfaz del módulo

Author: TalkBridge Team
Date: 2025-08-19
Version: 1.0

Requirements:
- PyQt6
- Flask
======================================================================
Functions:
- main: Main function to run the web interface.
======================================================================
"""

import os
import sys
from pathlib import Path

# Add src to path for imports
sys.path.append(str(Path(__file__).parent.parent))

def main():
    """Main function to run the web interface."""
    try:
        # Check if required directories exist
        assets_dir = Path(__file__).parent / "assets"
        if not assets_dir.exists():
            print("Creating assets directory...")
            assets_dir.mkdir(parents=True, exist_ok=True)
        
        # Check if CSS file exists
        css_file = assets_dir / "style.css"
        if not css_file.exists():
            print("Warning: style.css not found in assets directory")
        
        # Import and run the web interface
        from web_interface import main as run_web_interface
        
        print("🎤 Starting TalkBridge Web Interface...")
        print("📱 Open your browser and go to: http://localhost:8501")
        print("🔐 Default credentials:")
        print("   - Admin: username=admin, password=admin123")
        print("   - User: username=user, password=user123")
        print("")
        print("Press Ctrl+C to stop the server")
        
        # Run the web interface
        run_web_interface()
        
    except KeyboardInterrupt:
        print("\n🛑 Web interface stopped by user")
    except Exception as e:
        print(f"❌ Error running web interface: {e}")
        print("Please check that all dependencies are installed:")
        print("  pip install -r requirements.txt")
        return 1
    
    return 0

if __name__ == "__main__":
    exit(main()) 