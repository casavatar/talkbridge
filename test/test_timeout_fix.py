#!/usr/bin/env python3
"""
Test script to verify the authentication timeout fix.
This simulates the timeout scenario to ensure UI recovery works correctly.
"""

import time
import threading
from unittest.mock import MagicMock, patch
import tkinter as tk
import customtkinter as ctk

# Mock the auth manager to simulate slow authentication
class MockAuthManager:
    def __init__(self, delay=35):  # Delay longer than 30s timeout
        self.delay = delay

    def authenticate(self, username, password):
        """Simulate slow authentication that exceeds timeout."""
        print(f"Mock auth: Sleeping for {self.delay} seconds...")
        time.sleep(self.delay)
        print("Mock auth: Completed after delay")
        return True, {"username": username}, "Mock authentication successful"

def test_timeout_scenario():
    """Test the timeout recovery scenario."""
    print("Starting timeout test...")

    # Create test app
    app = ctk.CTk()
    app.withdraw()  # Hide main window

    try:
        # Import and patch the auth manager
        from src.talkbridge.desktop.dialogs.login_dialog import LoginDialog

        # Create dialog with mocked auth manager
        dialog = LoginDialog(app)
        dialog.auth_manager = MockAuthManager(delay=35)  # 35 seconds > 30 second timeout

        # Override timeout for faster testing
        original_setup = dialog._setup_auth_timeout
        def fast_timeout():
            """Set up 3-second timeout for testing."""
            if dialog.timeout_job:
                try:
                    dialog.dialog.after_cancel(dialog.timeout_job)
                except:
                    pass
                dialog.timeout_job = None

            def timeout_handler():
                dialog.timeout_job = None
                if dialog.auth_state.value == "authenticating":
                    print("TEST: Timeout triggered!")
                    from src.talkbridge.desktop.dialogs.login_dialog import AuthenticationState
                    dialog.set_auth_state(AuthenticationState.TIMEOUT)
                    dialog._on_auth_complete(False, "Test timeout message")

            dialog.timeout_job = dialog.dialog.after(3000, timeout_handler)  # 3 second timeout

        dialog._setup_auth_timeout = fast_timeout

        print("Opening login dialog...")
        print("The dialog should:")
        print("1. Show 'Signing in...' state")
        print("2. After 3 seconds, timeout and show error message")
        print("3. UI should be re-enabled for retry")
        print("4. You can close the dialog to complete the test")

        result = dialog.show()
        print(f"Dialog result: {result}")

    except Exception as e:
        print(f"Test error: {e}")
        import traceback
        traceback.print_exc()
    finally:
        app.destroy()

if __name__ == "__main__":
    test_timeout_scenario()