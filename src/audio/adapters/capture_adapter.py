"""
Audio Capture Adapter for TalkBridge

Wraps the existing AudioCapture class to conform to the AudioCapturePort interface.
"""

import logging
import time
from typing import Optional, Dict, List, Iterator
from queue import Queue, Empty, Full
import threading
import numpy as np

from ..ports import AudioCapturePort, AudioData, AudioFormat, DeviceInfo

try:
    from ..capture import AudioCapture
    AUDIO_CAPTURE_AVAILABLE = True
except ImportError:
    AudioCapture = None
    AUDIO_CAPTURE_AVAILABLE = False

class AudioCaptureAdapter:
    """Adapter that wraps AudioCapture to implement AudioCapturePort."""
    
    def __init__(self, loopback_mode: bool = False, device: Optional[int] = None,
                 sample_rate: Optional[int] = None):
        """Initialize the audio capture adapter.
        
        Args:
            loopback_mode: Whether to capture system audio (loopback)
            device: Device index to use (None for default)
            sample_rate: Sample rate to use (None for auto-detect)
        """
        self.logger = logging.getLogger("talkbridge.audio.capture_adapter")
        
        if not AUDIO_CAPTURE_AVAILABLE or AudioCapture is None:
            raise ImportError("AudioCapture module not available")
        
        self.capture_engine = AudioCapture(
            loopback_mode=loopback_mode,
            device=device,
            sample_rate=sample_rate
        )
        
        self._recording = False
        self._audio_queue = Queue()
        self._recording_thread = None
        self._source_type = "system_audio" if loopback_mode else "microphone"
        self._current_device = device
        
        # Audio format settings
        self._sample_rate = sample_rate or 44100
        self._channels = 1
        self._device_info = None
        
    def list_devices(self) -> Dict[str, List[DeviceInfo]]:
        """List available audio devices."""
        try:
            devices_info = self.capture_engine.list_devices()
            result = {
                'input_devices': [],
                'output_devices': [],
                'default_input': devices_info.get('default_input'),
                'default_output': devices_info.get('default_output')
            }
            
            # Convert to DeviceInfo objects
            for device_data in devices_info.get('devices', []):
                device_info = DeviceInfo(
                    index=device_data.get('index', 0),
                    name=device_data.get('name', 'Unknown'),
                    max_input_channels=device_data.get('max_input_channels', 0),
                    max_output_channels=device_data.get('max_output_channels', 0),
                    default_sample_rate=device_data.get('default_sample_rate', 44100),
                    is_default=(device_data.get('index') == devices_info.get('default_input') or
                               device_data.get('index') == devices_info.get('default_output'))
                )
                
                if device_info.max_input_channels > 0:
                    result['input_devices'].append(device_info)
                if device_info.max_output_channels > 0:
                    result['output_devices'].append(device_info)
            
            return result
            
        except Exception as e:
            self.logger.error(f"Failed to list devices: {e}")
            return {'input_devices': [], 'output_devices': []}
    
    def start_recording(self, device_index: Optional[int] = None,
                       sample_rate: int = 44100, channels: int = 1) -> bool:
        """Start audio recording from specified device."""
        if self._recording:
            self.logger.warning("Already recording")
            return False
        
        try:
            # Update device if specified
            if device_index is not None:
                self._current_device = device_index
                # Reinitialize capture engine with new device
                if AudioCapture is None:
                    raise RuntimeError("AudioCapture module not available")
                loopback_mode = self._source_type == "system_audio"
                self.capture_engine = AudioCapture(
                    loopback_mode=loopback_mode,
                    device=device_index,
                    sample_rate=sample_rate
                )
            
            self._sample_rate = sample_rate
            self._channels = channels
            
            # Start recording in separate thread
            self._recording = True
            self._recording_thread = threading.Thread(target=self._recording_worker, daemon=True)
            self._recording_thread.start()
            
            self.logger.info(f"Started recording from device {self._current_device} "
                           f"at {sample_rate}Hz, {channels} channels")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to start recording: {e}")
            self._recording = False
            return False
    
    def stop_recording(self) -> bool:
        """Stop audio recording."""
        if not self._recording:
            self.logger.warning("Not currently recording")
            return False
        
        try:
            self._recording = False
            
            if self._recording_thread and self._recording_thread.is_alive():
                self._recording_thread.join(timeout=2.0)
            
            # Clear any remaining audio chunks
            while not self._audio_queue.empty():
                try:
                    self._audio_queue.get_nowait()
                except Empty:
                    break
            
            self.logger.info("Stopped recording")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to stop recording: {e}")
            return False
    
    def get_audio_chunk(self) -> Optional[AudioData]:
        """Get the next available audio chunk."""
        try:
            audio_data = self._audio_queue.get_nowait()
            return audio_data
        except Empty:
            return None
        except Exception as e:
            self.logger.error(f"Failed to get audio chunk: {e}")
            return None
    
    def is_recording(self) -> bool:
        """Check if currently recording."""
        return self._recording and (self._recording_thread is not None and 
                                   self._recording_thread.is_alive())
    
    def test_device_access(self, device_index: Optional[int] = None) -> bool:
        """Test access to audio device."""
        try:
            if hasattr(self.capture_engine, 'test_microphone_access'):
                return self.capture_engine.test_microphone_access()
            else:
                # Fallback: try to create a temporary capture session
                if AudioCapture is None:
                    return False  # Cannot test without AudioCapture
                test_device = device_index or self._current_device
                temp_capture = AudioCapture(
                    loopback_mode=self._source_type == "system_audio",
                    device=test_device,
                    sample_rate=self._sample_rate
                )
                return True  # If no exception, assume success
                
        except Exception as e:
            self.logger.error(f"Device access test failed: {e}")
            return False
    
    def _recording_worker(self):
        """Worker thread for continuous audio recording."""
        try:
            chunk_duration = 1.0  # Record 1-second chunks
            
            while self._recording:
                try:
                    # Record audio chunk
                    audio_bytes = self.capture_engine.record_chunk(duration=chunk_duration)
                    
                    if audio_bytes is not None:
                        # Convert numpy array to bytes if necessary
                        if isinstance(audio_bytes, np.ndarray):
                            audio_data_bytes = audio_bytes.tobytes()
                        elif isinstance(audio_bytes, bytes):
                            audio_data_bytes = audio_bytes
                        else:
                            # Try to convert to bytes
                            audio_data_bytes = bytes(audio_bytes)
                        
                        # Create AudioData object
                        audio_data = AudioData(
                            data=audio_data_bytes,
                            sample_rate=self._sample_rate,
                            channels=self._channels,
                            format=AudioFormat.PCM,
                            source_type=self._source_type,
                            device_info=str(self._current_device) if self._current_device else "default"
                        )
                        
                        # Add to queue (non-blocking, drop if queue is full)
                        try:
                            self._audio_queue.put_nowait(audio_data)
                        except Full:
                            # Queue full, drop oldest chunk
                            try:
                                self._audio_queue.get_nowait()
                                self._audio_queue.put_nowait(audio_data)
                            except (Empty, Full):
                                # Still couldn't add, skip this chunk
                                pass
                    
                    time.sleep(0.1)  # Small delay to prevent tight loop
                    
                except Exception as e:
                    self.logger.error(f"Error in recording worker: {e}")
                    if not self._recording:
                        break
                    time.sleep(0.5)  # Wait before retrying
                    
        except Exception as e:
            self.logger.error(f"Recording worker thread failed: {e}")
        finally:
            self.logger.debug("Recording worker thread finished")
    
    def get_audio_stream(self) -> Iterator[AudioData]:
        """Get an iterator of audio data chunks."""
        while self.is_recording():
            chunk = self.get_audio_chunk()
            if chunk:
                yield chunk
            else:
                time.sleep(0.01)  # Small delay if no data available