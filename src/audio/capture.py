"""
TalkBridge Audio - Capture
==========================

Módulo capture para TalkBridge

Author: TalkBridge Team
Date: 2025-08-19
Version: 1.0

Requirements:
- sounddevice
- numpy
======================================================================
Functions:
- get_default_device_info: Get information about default audio devices.
- test_audio_system: Test the complete audio system.
- __init__: Función __init__
- list_devices: List available audio devices.
- test_microphone_access: Test if microphone access is available.
- start_input_stream: Start capturing microphone audio continuously.
- start_output_stream: Start capturing system output audio (if supported by the system).
- record_fixed_duration: Record audio for a fixed duration.
- get_audio_buffer: Get the current audio buffer and clear it.
- stop: Stop audio capture.
======================================================================
"""

import sounddevice as sd
import numpy as np
import logging
from typing import Optional, Callable, Dict, Any

logger = logging.getLogger(__name__)

class AudioCapture:
    def __init__(self, sample_rate=44100, channels=1):
        self.sample_rate = sample_rate
        self.channels = channels
        self.stream = None
        self.is_recording = False
        self.audio_buffer = []

    def list_devices(self) -> Dict[str, Any]:
        """List available audio devices."""
        try:
            devices = sd.query_devices()
            return {
                'devices': devices,
                'default_input': sd.default.device[0],
                'default_output': sd.default.device[1]
            }
        except Exception as e:
            logger.error(f"Error listing audio devices: {e}")
            return {'devices': [], 'default_input': None, 'default_output': None}

    def test_microphone_access(self) -> bool:
        """Test if microphone access is available."""
        try:
            # Try to create a short test recording
            test_duration = 0.1  # 100ms
            recording = sd.rec(
                int(test_duration * self.sample_rate), 
                samplerate=self.sample_rate,
                channels=self.channels,
                dtype=np.float32
            )
            sd.wait()
            logger.info("Microphone access test successful")
            return True
        except Exception as e:
            logger.error(f"Microphone access test failed: {e}")
            return False

    def start_input_stream(self, callback: Optional[Callable] = None, device: Optional[int] = None):
        """Start capturing microphone audio continuously."""
        try:
            if self.stream is not None:
                self.stop()

            def audio_callback(indata, frames, time, status):
                if status:
                    logger.warning(f"Audio callback status: {status}")
                
                # Store audio data
                self.audio_buffer.append(indata.copy())
                
                # Call user callback if provided
                if callback:
                    callback(indata, frames, time, status)

            self.stream = sd.InputStream(
                samplerate=self.sample_rate,
                channels=self.channels,
                callback=audio_callback,
                device=device  # Use specified device or system default
            )
            self.stream.start()
            self.is_recording = True
            logger.info("Microphone capture started successfully")
            print("Microphone capture initiated. Press Ctrl+C to stop.")
            
        except Exception as e:
            logger.error(f"Failed to start input stream: {e}")
            print(f"Failed to start microphone capture: {e}")
            raise

    def start_output_stream(self, callback: Optional[Callable] = None, device: Optional[int] = None):
        """Start capturing system output audio (if supported by the system)."""
        try:
            # First, try to find a loopback or monitor device
            devices = sd.query_devices()
            loopback_device = None
            
            # Look for Windows WASAPI loopback devices
            for i, device_info in enumerate(devices):
                device_name = device_info['name'].lower()
                if ('stereo mix' in device_name or 
                    'what u hear' in device_name or
                    'loopback' in device_name or
                    'monitor' in device_name):
                    loopback_device = i
                    break
            
            if loopback_device is None:
                raise Exception("No loopback/monitor device found. Enable 'Stereo Mix' in Windows sound settings.")

            def audio_callback(indata, frames, time, status):
                if status:
                    logger.warning(f"Output audio callback status: {status}")
                
                # Store audio data
                self.audio_buffer.append(indata.copy())
                
                # Call user callback if provided
                if callback:
                    callback(indata, frames, time, status)

            self.stream = sd.InputStream(
                samplerate=self.sample_rate,
                channels=self.channels,
                callback=audio_callback,
                device=loopback_device
            )
            self.stream.start()
            self.is_recording = True
            logger.info(f"Output capture started using device: {devices[loopback_device]['name']}")
            print("Output capture initiated. Press Ctrl+C to stop.")
            
        except Exception as e:
            logger.error(f"Failed to start output capture: {e}")
            print(f"Failed to start output capture: {e}")
            print("Tip: Enable 'Stereo Mix' or similar loopback device in Windows sound settings")
            raise

    def record_fixed_duration(self, duration: float, device: Optional[int] = None) -> np.ndarray:
        """Record audio for a fixed duration."""
        try:
            logger.info(f"Recording {duration} seconds of audio...")
            recording = sd.rec(
                int(duration * self.sample_rate),
                samplerate=self.sample_rate,
                channels=self.channels,
                dtype=np.float32,
                device=device
            )
            sd.wait()  # Wait until recording is finished
            logger.info("Recording completed")
            return recording
        except Exception as e:
            logger.error(f"Failed to record audio: {e}")
            raise

    def get_audio_buffer(self) -> np.ndarray:
        """Get the current audio buffer and clear it."""
        if not self.audio_buffer:
            return np.array([])
        
        # Concatenate all audio chunks
        audio_data = np.concatenate(self.audio_buffer, axis=0)
        self.audio_buffer.clear()
        return audio_data

    def stop(self):
        """Stop audio capture."""
        if self.stream:
            self.stream.stop()
            self.stream.close()
            self.stream = None
            self.is_recording = False
            logger.info("Audio capture stopped")
            print("Capture stopped.")

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.stop()

# Utility functions
def get_default_device_info():
    """Get information about default audio devices."""
    try:
        device_info = {
            'input': sd.query_devices(sd.default.device[0]),
            'output': sd.query_devices(sd.default.device[1])
        }
        return device_info
    except Exception as e:
        logger.error(f"Error getting device info: {e}")
        return None

def test_audio_system():
    """Test the complete audio system."""
    print("🎵 Testing Audio System...")
    print("="*40)
    
    try:
        # Test device listing
        capture = AudioCapture()
        devices_info = capture.list_devices()
        
        print(f"📱 Found {len(devices_info['devices'])} audio devices")
        print(f"🎤 Default input device: {devices_info['default_input']}")
        print(f"🔊 Default output device: {devices_info['default_output']}")
        
        # Test microphone access
        print("\n🎤 Testing microphone access...")
        if capture.test_microphone_access():
            print("✅ Microphone access successful")
        else:
            print("❌ Microphone access failed")
            return False
        
        # Test short recording
        print("\n📹 Testing 2-second recording...")
        recording = capture.record_fixed_duration(2.0)
        print(f"✅ Recording completed: {recording.shape} samples")
        
        print("\n🎉 Audio system test completed successfully!")
        return True
        
    except Exception as e:
        print(f"❌ Audio system test failed: {e}")
        return False

if __name__ == "__main__":
    test_audio_system()