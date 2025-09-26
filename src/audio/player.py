#!/usr/bin/env python3
"""
TalkBridge Audio - Player
=========================

Player module for TalkBridge with enhanced logging and error handling.

Author: TalkBridge Team
Date: 2025-09-18
Version: 2.0 (Enhanced error handling)

Requirements:
- sounddevice
- numpy
======================================================================
Functions:
- __init__: Initialize audio player.
- load_audio_file: Load audio from file.
- _load_wav_file: Load WAV file.
- save_audio_file: Save audio to file.
- play_audio: Play audio data.
- start_streaming: Start streaming audio from callback.
- stop_streaming: Stop audio streaming.
- set_volume: Set playback volume.
- add_to_playlist: Add track to playlist.
- load_playlist: Load playlist from file.
======================================================================
"""

import numpy as np
import sys
from pathlib import Path

from src.logging_config import get_logger, log_exception
from src.utils.exceptions import (
    AudioPlaybackError, create_audio_capture_error,
    TalkBridgeError
)
import sounddevice as sd
import threading
import time
import queue
from typing import Optional, Callable, List, Dict, Any
import os
import wave
import json

class AudioPlayer:
    """Advanced audio player with streaming and playlist capabilities."""
    
    def __init__(self, sample_rate: int = 44100, buffer_size: int = 1024):
        """
        Initialize audio player.
        
        Args:
            sample_rate: Sample rate in Hz
            buffer_size: Audio buffer size in samples
        """
        self.sample_rate = sample_rate
        self.buffer_size = buffer_size
        self.is_playing = False
        self.is_paused = False
        self.volume = 1.0
        self.current_track = None
        self.playlist = []
        self.current_index = 0
        
        # Initialize logging
        self.logger = get_logger(__name__)
        
        # Audio buffers
        self.audio_queue = queue.Queue()
        self.output_stream = None
        
        # Callbacks
        self.on_track_change = None
        self.on_playback_end = None
        self.on_progress = None
        
        # Threading
        self.playback_thread = None
        self.processing_thread = None
    
    def load_audio_file(self, filename: str) -> Optional[np.ndarray]:
        """
        Load audio from file.
        
        Args:
            filename: Audio file path
            
        Returns:
            Audio data as numpy array
            
        Raises:
            AudioPlaybackError: If file format unsupported or loading fails
        """
        try:
            if filename.endswith('.wav'):
                return self._load_wav_file(filename)
            else:
                error_msg = f"Unsupported file format: {filename}"
                self.logger.error(error_msg)
                raise AudioPlaybackError(
                    message=error_msg,
                    user_message=f"File format not supported: {Path(filename).suffix}"
                )
        except AudioPlaybackError:
            # Re-raise our custom errors
            raise
        except Exception as e:
            error_msg = f"Error loading audio file {filename}: {str(e)}"
            log_exception(self.logger, e, f"Failed to load audio file: {filename}")
            raise AudioPlaybackError(
                message=error_msg,
                user_message=f"Failed to load audio file: {Path(filename).name}"
            )
            return None
    
    def _load_wav_file(self, filename: str) -> np.ndarray:
        """Load WAV file."""
        with wave.open(filename, 'rb') as wav_file:
            frames = wav_file.readframes(wav_file.getnframes())
            audio = np.frombuffer(frames, dtype=np.int16)
            
            # Convert to float and normalize
            audio = audio.astype(np.float32) / 32768.0
            
            # Convert to mono if stereo
            if wav_file.getnchannels() == 2:
                audio = audio.reshape(-1, 2).mean(axis=1)
            
            return audio
    
    def save_audio_file(self, audio: np.ndarray, filename: str):
        """
        Save audio to file.
        
        Args:
            audio: Audio data as numpy array
            filename: Output filename
        """
        try:
            # Convert to int16
            audio_int16 = (audio * 32767).astype(np.int16)
            
            with wave.open(filename, 'wb') as wav_file:
                wav_file.setnchannels(1)
                wav_file.setsampwidth(2)
                wav_file.setframerate(self.sample_rate)
                wav_file.writeframes(audio_int16.tobytes())
        except Exception as e:
            print(f"Error saving audio file {filename}: {e}")
    
    def play_audio(self, audio: np.ndarray, blocking: bool = True):
        """
        Play audio data.
        
        Args:
            audio: Audio data as numpy array
            blocking: Whether to block until playback is complete
        """
        if blocking:
            sd.play(audio * self.volume, self.sample_rate)
            sd.wait()
        else:
            sd.play(audio * self.volume, self.sample_rate)
    
    def start_streaming(self, audio_callback: Callable[[], np.ndarray]):
        """
        Start streaming audio from callback.
        
        Args:
            audio_callback: Function that returns audio data
        """
        self.is_playing = True
        
        def stream_callback(outdata, frames, time, status):
            if status:
                print(f"Stream status: {status}")
            
            try:
                audio_data = audio_callback()
                if len(audio_data) >= frames:
                    outdata[:] = audio_data[:frames] * self.volume
                else:
                    outdata[:len(audio_data)] = audio_data * self.volume
                    outdata[len(audio_data):] = 0
            except Exception as e:
                print(f"Stream callback error: {e}")
                outdata[:] = 0
        
        self.output_stream = sd.OutputStream(
            samplerate=self.sample_rate,
            channels=1,
            callback=stream_callback
        )
        self.output_stream.start()
    
    def stop_streaming(self):
        """Stop audio streaming."""
        self.is_playing = False
        if self.output_stream:
            self.output_stream.stop()
            self.output_stream.close()
            self.output_stream = None
    
    def set_volume(self, volume: float):
        """
        Set playback volume.
        
        Args:
            volume: Volume level (0.0 to 1.0)
        """
        self.volume = max(0.0, min(1.0, volume))
    
    def add_to_playlist(self, track_info: Dict[str, Any]):
        """
        Add track to playlist.
        
        Args:
            track_info: Track information dictionary
        """
        self.playlist.append(track_info)
    
    def load_playlist(self, playlist_file: str):
        """
        Load playlist from file.
        
        Args:
            playlist_file: Playlist file path
        """
        try:
            with open(playlist_file, 'r') as f:
                self.playlist = json.load(f)
        except Exception as e:
            print(f"Error loading playlist {playlist_file}: {e}")
    
    def save_playlist(self, playlist_file: str):
        """
        Save playlist to file.
        
        Args:
            playlist_file: Playlist file path
        """
        try:
            with open(playlist_file, 'w') as f:
                json.dump(self.playlist, f, indent=2)
        except Exception as e:
            print(f"Error saving playlist {playlist_file}: {e}")
    
    def play_playlist(self, start_index: int = 0):
        """
        Start playing playlist.
        
        Args:
            start_index: Starting track index
        """
        if not self.playlist:
            print("Playlist is empty")
            return
        
        self.current_index = start_index
        self._play_current_track()
    
    def _play_current_track(self):
        """Play current track in playlist."""
        if self.current_index >= len(self.playlist):
            if self.on_playback_end:
                self.on_playback_end()
            return
        
        track = self.playlist[self.current_index]
        self.current_track = track
        
        if self.on_track_change:
            self.on_track_change(track)
        
        # Load and play audio
        if 'file' in track:
            audio = self.load_audio_file(track['file'])
            if audio is not None:
                self.play_audio(audio, blocking=True)
        
        # Move to next track
        self.current_index += 1
        self._play_current_track()
    
    def next_track(self):
        """Skip to next track."""
        if self.current_index < len(self.playlist) - 1:
            self.current_index += 1
            self._play_current_track()
    
    def previous_track(self):
        """Go to previous track."""
        if self.current_index > 0:
            self.current_index -= 1
            self._play_current_track()
    
    def pause(self):
        """Pause playback."""
        self.is_paused = True
        if self.output_stream:
            self.output_stream.stop()
    
    def resume(self):
        """Resume playback."""
        self.is_paused = False
        if self.output_stream:
            self.output_stream.start()
    
    def stop(self):
        """Stop playback."""
        self.is_playing = False
        self.is_paused = False
        self.stop_streaming()
    
    def get_playlist_info(self) -> Dict[str, Any]:
        """Get playlist information."""
        return {
            'total_tracks': len(self.playlist),
            'current_index': self.current_index,
            'current_track': self.current_track,
            'is_playing': self.is_playing,
            'is_paused': self.is_paused,
            'volume': self.volume
        }
    
    def create_audio_generator(self, frequency: float = 440.0, 
                             duration: float = 1.0) -> Callable[[], np.ndarray]:
        """
        Create an audio generator function.
        
        Args:
            frequency: Frequency in Hz
            duration: Duration in seconds
            
        Returns:
            Audio generator function
        """
        t = np.linspace(0, duration, int(self.sample_rate * duration), False)
        audio = np.sin(2 * np.pi * frequency * t)
        
        def generator():
            return audio
        
        return generator
    
    def create_audio_processor(self, audio: np.ndarray, 
                             processor: Callable[[np.ndarray], np.ndarray]) -> Callable[[], np.ndarray]:
        """
        Create an audio processor function.
        
        Args:
            audio: Input audio
            processor: Audio processing function
            
        Returns:
            Processed audio generator function
        """
        processed_audio = processor(audio)
        
        def generator():
            return processed_audio
        
        return generator
    
    def player_demo(self):
        """Generate a demo of audio player capabilities."""
        self.logger.info("🎵 Starting Audio Player Demo")
        self.logger.info("=" * 30)
        
        # Create test audio
        t = np.linspace(0, 2, int(self.sample_rate * 2), False)
        test_audio = np.sin(2 * np.pi * 440 * t)
        
        # Save test audio
        test_file = "test_audio.wav"
        try:
            self.save_audio_file(test_audio, test_file)
        except AudioPlaybackError as e:
            self.logger.error(f"Failed to save test audio: {e.user_message}")
            return
        
        # Create playlist
        self.playlist = [
            {'name': 'Test Audio', 'file': test_file, 'duration': 2.0},
            {'name': 'Generated Tone', 'file': None, 'duration': 1.0}
        ]
        
        # Set up callbacks
        def on_track_change(track):
            print(f"Now playing: {track['name']}")
        
        def on_playback_end():
            print("Playback ended")
        
        self.on_track_change = on_track_change
        self.on_playback_end = on_playback_end
        
        # Play playlist
        print("Playing playlist...")
        self.play_playlist()
        
        # Clean up
        if os.path.exists(test_file):
            os.remove(test_file)
        
        print("\n✅ Player demo completed!")

class AudioStreamer:
    """Real-time audio streaming with processing."""
    
    def __init__(self, sample_rate: int = 44100, buffer_size: int = 1024):
        """
        Initialize audio streamer.
        
        Args:
            sample_rate: Sample rate in Hz
            buffer_size: Buffer size in samples
        """
        self.sample_rate = sample_rate
        self.buffer_size = buffer_size
        self.is_streaming = False
        self.audio_queue = queue.Queue()
        self.processor = None
        
    def start_streaming(self, audio_source: Callable[[], np.ndarray], 
                       processor: Optional[Callable[[np.ndarray], np.ndarray]] = None):
        """
        Start audio streaming.
        
        Args:
            audio_source: Function that generates audio data
            processor: Optional audio processing function
        """
        self.is_streaming = True
        self.processor = processor
        
        def stream_callback(outdata, frames, time, status):
            if status:
                print(f"Stream status: {status}")
            
            try:
                # Get audio from source
                audio_data = audio_source()
                
                # Apply processor if available
                if self.processor:
                    audio_data = self.processor(audio_data)
                
                # Ensure correct size
                if len(audio_data) >= frames:
                    outdata[:] = audio_data[:frames]
                else:
                    outdata[:len(audio_data)] = audio_data
                    outdata[len(audio_data):] = 0
                    
            except Exception as e:
                print(f"Stream callback error: {e}")
                outdata[:] = 0
        
        self.output_stream = sd.OutputStream(
            samplerate=self.sample_rate,
            channels=1,
            callback=stream_callback
        )
        self.output_stream.start()
    
    def stop_streaming(self):
        """Stop audio streaming."""
        self.is_streaming = False
        if self.output_stream:
            self.output_stream.stop()
            self.output_stream.close()
            self.output_stream = None

if __name__ == "__main__":
    # Run demo
    player = AudioPlayer()
    player.player_demo() 