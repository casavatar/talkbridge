#----------------------------------------------------------------------------------------------------------------------------
# description: This script connects to the Ollama service and uses the Deepseek Coder model to generate a Python function.
#----------------------------------------------------------------------------------------------------------------------------
# 
# author: ingekastel
# date: 2025-06-02
# version: 1.0
# 
# requirements:
# - Docker with Ollama service running
#----------------------------------------------------------------------------------------------------------------------------   

import numpy as np
import time
from ollama.ollama_client import OllamaClient
from audio_capture.audio_capture import AudioCapture

def audio_callback(indata, frames, time_info, status):
    volume_norm = np.linalg.norm(indata) * 10
    print(f"Volume level: {volume_norm:.2f}")

if __name__ == "__main__":
    client = OllamaClient()

    # Verify connection
    if client.ping():
        print("Connection to Ollama verified.")

        # Initialize audio capture
        audio = AudioCapture()

        try:
            # Listen to microphone (you can switch to start_output_stream)
            audio.start_input_stream(audio_callback)

            # Keep the program alive until interrupted
            while True:
                time.sleep(0.1)
        except KeyboardInterrupt:
            print("\nInterrupted by user.")
        finally:
            audio.stop()
    else:
        print("Failed to connect to Ollama. Aborting process.")