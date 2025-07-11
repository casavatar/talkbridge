#---------------------------------------------------------------------------------
# description: This module provides functionality to capture audio from the microphone
# and system output using the sounddevice library.
#-----------------------------------------------------------------------------------
#
# author: ingekastel
# date: 2025-06-02
# version: 1.0
#
# requirements:
# - sounddevice library
# - numpy library
#-----------------------------------------------------------------------------------

import sounddevice as sd
import numpy as np

class AudioCapture:
    def __init__(self, sample_rate=44100, channels=1):
        self.sample_rate = sample_rate
        self.channels = channels
        self.stream = None

    def start_input_stream(self, callback):
        """It begins to capture microphone audio continuously."""
        self.stream = sd.InputStream(
            samplerate=self.sample_rate,
            channels=self.channels,
            callback=callback
        )
        self.stream.start()
        print("Microphone capture initiated. Press Ctrl+C to stop.")

    def start_output_stream(self, callback):
        """It begins to capture system output audio (loopback, if available)."""
        try:
            self.stream = sd.InputStream(
                samplerate=self.sample_rate,
                channels=self.channels,
                callback=callback,
                device='loopback'
            )
            self.stream.start()
            print("Output capture initiated. Press Ctrl+C to stop.")
        except Exception as e:
            print(f"Failed to start output capture: {e}")

    def stop(self):
        if self.stream:
            self.stream.stop()
            self.stream.close()
            print("Capture stopped.")
