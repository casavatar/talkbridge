"""
Audio Player Adapter for TalkBridge

Wraps the existing audio player functionality to conform to the AudioPlayerPort interface.
"""

import logging
import asyncio
import time
import threading
from typing import Optional
import tempfile
import os

from ..ports import AudioPlayerPort, AudioData, AudioFormat

# Import numpy at module level
try:
    import numpy as np
    NUMPY_AVAILABLE = True
except ImportError:
    NUMPY_AVAILABLE = False

try:
    from ...audio.player import AudioPlayer
    AUDIO_PLAYER_AVAILABLE = True
except ImportError:
    try:
        # Fallback to creating basic player functionality
        import sounddevice as sd
        import wave
        import io
        SOUNDDEVICE_AVAILABLE = True
    except ImportError:
        SOUNDDEVICE_AVAILABLE = False
    AUDIO_PLAYER_AVAILABLE = False

class AudioPlayerAdapter:
    """Adapter that wraps audio player functionality to implement AudioPlayerPort."""
    
    def __init__(self, device: Optional[int] = None):
        """Initialize the audio player adapter.
        
        Args:
            device: Output device index to use (None for default)
        """
        self.logger = logging.getLogger("talkbridge.audio.player_adapter")
        
        self._device = device
        self._playing = False
        self._volume = 1.0
        self._current_thread = None
        
        if AUDIO_PLAYER_AVAILABLE:
            try:
                self.audio_player = AudioPlayer(device=device)
                self._use_audio_player = True
                self.logger.info("Initialized audio player adapter with AudioPlayer")
            except Exception as e:
                self.logger.warning(f"Failed to initialize AudioPlayer: {e}")
                self._use_audio_player = False
        else:
            self._use_audio_player = False
        
        if not self._use_audio_player and not SOUNDDEVICE_AVAILABLE:
            raise ImportError("No audio player modules available")
        
        if not self._use_audio_player:
            self.logger.info("Using sounddevice fallback for audio playback")
    
    def play(self, audio_data: AudioData) -> bool:
        """Play audio data."""
        if self._playing:
            self.logger.warning("Already playing audio")
            return False
        
        try:
            self._playing = True
            
            if self._use_audio_player:
                return self._play_with_audio_player(audio_data)
            else:
                return self._play_with_sounddevice(audio_data)
                
        except Exception as e:
            self.logger.error(f"Audio playback failed: {e}")
            self._playing = False
            return False
    
    async def play_async(self, audio_data: AudioData) -> bool:
        """Play audio data asynchronously."""
        # Run playback in thread pool to avoid blocking
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(None, self.play, audio_data)
    
    def stop(self) -> bool:
        """Stop audio playback."""
        try:
            if not self._playing:
                return True
            
            self._playing = False
            
            if self._use_audio_player and hasattr(self.audio_player, 'stop'):
                self.audio_player.stop()
            elif SOUNDDEVICE_AVAILABLE:
                sd.stop()
            
            # Wait for playback thread to finish
            if self._current_thread and self._current_thread.is_alive():
                self._current_thread.join(timeout=1.0)
            
            self.logger.info("Stopped audio playback")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to stop audio playback: {e}")
            return False
    
    def is_playing(self) -> bool:
        """Check if audio is currently playing."""
        return self._playing and (self._current_thread is not None and 
                                 self._current_thread.is_alive())
    
    def set_volume(self, volume: float) -> bool:
        """Set playback volume (0.0 to 1.0)."""
        try:
            self._volume = max(0.0, min(1.0, volume))
            
            if self._use_audio_player and hasattr(self.audio_player, 'set_volume'):
                self.audio_player.set_volume(self._volume)
            
            self.logger.info(f"Set volume to {self._volume}")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to set volume: {e}")
            return False
    
    def _play_with_audio_player(self, audio_data: AudioData) -> bool:
        """Play audio using the AudioPlayer class."""
        try:
            # Prepare audio file for AudioPlayer
            audio_file_path = self._prepare_audio_file(audio_data)
            
            def playback_worker():
                try:
                    self.audio_player.play(audio_file_path)
                    # Wait for playback to complete
                    while self.audio_player.is_playing() and self._playing:
                        time.sleep(0.1)
                finally:
                    self._playing = False
                    if os.path.exists(audio_file_path):
                        os.unlink(audio_file_path)
            
            # Start playback in separate thread
            self._current_thread = threading.Thread(target=playback_worker, daemon=True)
            self._current_thread.start()
            
            return True
            
        except Exception as e:
            self.logger.error(f"AudioPlayer playback failed: {e}")
            self._playing = False
            return False
    
    def _play_with_sounddevice(self, audio_data: AudioData) -> bool:
        """Play audio using sounddevice fallback."""
        if not SOUNDDEVICE_AVAILABLE:
            return False
        
        try:
            # Convert audio data to numpy array
            audio_array = self._audio_data_to_numpy(audio_data)
            
            def playback_worker():
                try:
                    # Apply volume
                    if self._volume != 1.0:
                        audio_array_vol = audio_array * self._volume
                    else:
                        audio_array_vol = audio_array
                    
                    # Play audio
                    sd.play(
                        audio_array_vol,
                        samplerate=audio_data.sample_rate,
                        device=self._device,
                        channels=audio_data.channels
                    )
                    
                    # Wait for playback to complete
                    sd.wait()
                    
                finally:
                    self._playing = False
            
            # Start playback in separate thread
            self._current_thread = threading.Thread(target=playback_worker, daemon=True)
            self._current_thread.start()
            
            return True
            
        except Exception as e:
            self.logger.error(f"Sounddevice playback failed: {e}")
            self._playing = False
            return False
    
    def _prepare_audio_file(self, audio_data: AudioData) -> str:
        """Prepare audio data as a temporary file."""
        try:
            # Create temporary file with appropriate extension
            if audio_data.format == AudioFormat.WAV:
                suffix = '.wav'
            elif audio_data.format == AudioFormat.MP3:
                suffix = '.mp3'
            elif audio_data.format == AudioFormat.FLAC:
                suffix = '.flac'
            else:
                suffix = '.wav'  # Default to WAV
            
            # Create temporary file
            with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as temp_file:
                if audio_data.format == AudioFormat.PCM:
                    # Convert PCM to WAV format
                    wav_data = self._pcm_to_wav(
                        audio_data.data,
                        audio_data.sample_rate,
                        audio_data.channels
                    )
                    temp_file.write(wav_data)
                else:
                    # Write raw audio data for other formats
                    temp_file.write(audio_data.data)
                
                return temp_file.name
                
        except Exception as e:
            self.logger.error(f"Failed to prepare audio file: {e}")
            raise
    
    def _audio_data_to_numpy(self, audio_data: AudioData):
        """Convert AudioData to numpy array for sounddevice."""
        if not NUMPY_AVAILABLE:
            raise RuntimeError("NumPy not available for audio processing")
            
        try:
            if audio_data.format == AudioFormat.PCM:
                # Convert PCM bytes to numpy array
                audio_array = np.frombuffer(audio_data.data, dtype=np.int16)
                # Normalize to [-1, 1] range
                audio_array = audio_array.astype(np.float32) / 32768.0
            else:
                # For other formats, try to convert via WAV
                wav_data = self._pcm_to_wav(
                    audio_data.data,
                    audio_data.sample_rate,
                    audio_data.channels
                )
                
                # Read WAV data
                with io.BytesIO(wav_data) as wav_buffer:
                    with wave.open(wav_buffer, 'rb') as wav_file:
                        frames = wav_file.readframes(wav_file.getnframes())
                        audio_array = np.frombuffer(frames, dtype=np.int16)
                        audio_array = audio_array.astype(np.float32) / 32768.0
            
            # Reshape for multi-channel audio
            if audio_data.channels > 1:
                audio_array = audio_array.reshape(-1, audio_data.channels)
            
            return audio_array
            
        except Exception as e:
            self.logger.error(f"Failed to convert audio data to numpy: {e}")
            raise
    
    def _pcm_to_wav(self, pcm_data: bytes, sample_rate: int, channels: int) -> bytes:
        """Convert PCM data to WAV format."""
        try:
            import wave
            
            # Create WAV file in memory
            wav_buffer = io.BytesIO()
            
            with wave.open(wav_buffer, 'wb') as wav_file:
                wav_file.setnchannels(channels)
                wav_file.setsampwidth(2)  # 16-bit samples
                wav_file.setframerate(sample_rate)
                
                # Convert bytes to 16-bit samples if needed
                if len(pcm_data) % 2 != 0:
                    pcm_data = pcm_data[:-1]  # Remove odd byte
                
                wav_file.writeframes(pcm_data)
            
            wav_buffer.seek(0)
            return wav_buffer.read()
            
        except Exception as e:
            self.logger.error(f"PCM to WAV conversion failed: {e}")
            return pcm_data  # Return original data as fallback