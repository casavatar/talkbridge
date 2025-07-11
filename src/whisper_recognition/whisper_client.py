#-----------------------------------------------------------------------
# description: Whisper Client for Audio Transcription
#------------------------------------------------------------------------
#
# author: ingekastel
# date: 2025-06-02
# version: 1.0
#
# requirements:
# - Whisper model (e.g., base, small, medium, large)
# - sounddevice for audio recording
# - numpy for audio data handling       
#-----------------------------------------------------------------------

import whisper
import sounddevice as sd
import numpy as np

class WhisperClient:
    def __init__(self, model_name="base"):
        print("Loading whisper model...")
        self.model = whisper.load_model(model_name)
        print("Whisper model loaded.")

    def record_audio(self, duration=5, sample_rate=16000):
        print(f"Recording {duration} seconds of audio...")
        audio = sd.rec(int(duration * sample_rate), samplerate=sample_rate, channels=1)
        sd.wait()
        audio = np.squeeze(audio)
        return audio

    def transcribe_audio(self, audio, sample_rate=16000):
        print("Transcribing audio...")
        result = self.model.transcribe(audio, language="es", fp16=False)
        text = result["text"]
        print(f"Transcribed text: {text}")
        return text