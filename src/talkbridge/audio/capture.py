"""
TalkBridge Audio - Capture
==========================

Capture module for TalkBridge

Author: TalkBridge Team
Date: 2025-08-19
Version: 1.0

Requirements:
- sounddevice
- numpy
- soundfile
======================================================================
Functions:
- get_default_device_info: Get information about default audio devices.
- test_audio_system: Test the complete audio system.
- __init__: Function __init__
- list_devices: List available audio devices.
- test_microphone_access: Test if microphone access is available.
- start_input_stream: Start capturing microphone audio continuously.
- start_output_stream: Start capturing system output audio (if supported by the system).
- record_fixed_duration: Record audio for a fixed duration.
- record_audio: Record audio for a fixed duration and save to file.
- get_audio_buffer: Get the current audio buffer and clear it.
- stop: Stop audio capture.
======================================================================
"""

import sounddevice as sd
import numpy as np
import logging
import platform
import subprocess
from typing import Optional, Callable, Dict, Any, List, Tuple
from talkbridge.logging_config import get_logger
from talkbridge.utils.error_handler import handle_error, retry_with_backoff, RetryableError, CriticalError

logger = get_logger(__name__)

class AudioCapture:
    def __init__(self, sample_rate=None, channels=1, device=None, loopback_mode=False):
        # Validate and set device
        self.device = device
        self.loopback_mode = loopback_mode  # Flag for system audio capture
        
        # Enhanced device logging
        logger.info(f"Initializing AudioCapture with device={device}, loopback_mode={loopback_mode}")
        
        # Log detailed device information
        try:
            if device is not None:
                device_info = sd.query_devices(device)
                logger.info(f"Selected device {device}: {device_info.get('name', 'Unknown')} "
                          f"(inputs: {device_info.get('max_input_channels', 0)}, "
                          f"outputs: {device_info.get('max_output_channels', 0)}, "
                          f"default_sr: {device_info.get('default_samplerate', 'Unknown')})")
            else:
                default_device = sd.query_devices(kind='input')
                logger.info(f"Using default input device: {default_device.get('name', 'Unknown')} "
                          f"(inputs: {default_device.get('max_input_channels', 0)})")
        except Exception as e:
            logger.warning(f"Could not query device information: {e}")
        
        # Auto-detect optimal sample rate if not provided
        if sample_rate is None:
            sample_rate = self._get_optimal_sample_rate(device)
        elif not isinstance(sample_rate, int) or sample_rate <= 0:
            logger.warning(f"Invalid sample_rate {sample_rate}, auto-detecting optimal rate")
            sample_rate = self._get_optimal_sample_rate(device)
        
        # Validate channels
        if not isinstance(channels, int) or channels <= 0:
            logger.warning(f"Invalid channels {channels}, using default 1")
            channels = 1
            
        self.sample_rate = sample_rate
        self.channels = channels
        self.stream = None
        self.is_recording = False
        self.audio_buffer = []
        
        logger.info(f"AudioCapture initialized successfully - sample_rate={self.sample_rate}, channels={self.channels}, device={self.device}, loopback_mode={self.loopback_mode}")
        
        # Test device accessibility
        try:
            test_frames = int(0.01 * self.sample_rate)  # 10ms test
            test_recording = sd.rec(
                test_frames,
                samplerate=self.sample_rate,
                channels=self.channels,
                dtype=np.float32,
                device=self.device
            )
            sd.wait()
            logger.info(f"Device access test successful - recorded {len(test_recording)} frames")
        except Exception as e:
            logger.error(f"Device access test failed: {e}. Voice input may not work properly.")
            # Log system audio info for debugging
            try:
                logger.debug(f"Available audio devices: {len(sd.query_devices())}")
                logger.debug(f"Default input device: {sd.query_devices(kind='input').get('name', 'Unknown')}")
                logger.debug(f"Default output device: {sd.query_devices(kind='output').get('name', 'Unknown')}")
            except Exception as e:
                logger.debug(f"Could not query audio device information: {e}")

    def initialize_device_by_index(self, device_index: int | str | None = "auto", samplerate: int = 44100, channels: int = 1) -> bool:
        """
        Initialize audio device by index or device hint.
        
        Args:
            device_index: Device index (int), device name (str), None, or "auto" for default
            samplerate: Sample rate for the device
            channels: Number of audio channels
            
        Returns:
            bool: True if initialization successful, False otherwise
        """
        try:
            devices = sd.query_devices()
            
            # Handle different device_index types
            if device_index == "auto" or device_index is None:
                # Use default input device
                default_device = sd.default.device[0] if sd.default.device else None
                selected_index = default_device
                logger.info("Using auto-selected default input device")
            elif isinstance(device_index, int):
                # Direct device index
                if 0 <= device_index < len(devices):
                    selected_index = device_index
                else:
                    logger.error(f"Device index {device_index} out of range (0-{len(devices)-1})")
                    return False
            elif isinstance(device_index, str):
                # Device name lookup
                matches = [i for i, d in enumerate(devices) if device_index.lower() in d["name"].lower()]
                if not matches:
                    logger.error(f"No device found matching: {device_index}")
                    return False
                selected_index = matches[0]
                logger.info(f"Found device match: {devices[selected_index]['name']}")
            else:
                logger.error(f"Invalid device_index type: {type(device_index)}")
                return False
            
            # Validate the selected device has input channels
            device_info = devices[selected_index]
            if device_info.get('max_input_channels', 0) <= 0:
                logger.error(f"Device {selected_index} ({device_info['name']}) has no input channels")
                return False
            
            # Update instance variables
            self.device = selected_index
            self.sample_rate = samplerate
            self.channels = min(channels, device_info.get('max_input_channels', 1))
            
            # Log selected device details
            logger.info(f"Selected audio device {selected_index}: {device_info['name']}")
            logger.info(f"Device details - Input channels: {device_info.get('max_input_channels', 0)}, "
                       f"Output channels: {device_info.get('max_output_channels', 0)}, "
                       f"Default SR: {device_info.get('default_samplerate', 'Unknown')}")
            
            # Set sounddevice defaults
            sd.default.device = selected_index
            sd.default.samplerate = self.sample_rate
            sd.default.channels = self.channels
            
            # Test device accessibility
            try:
                test_frames = int(0.01 * self.sample_rate)  # 10ms test
                test_recording = sd.rec(
                    test_frames,
                    samplerate=self.sample_rate,
                    channels=self.channels,
                    dtype=np.float32,
                    device=selected_index
                )
                sd.wait()
                logger.info(f"Device initialization test successful - recorded {len(test_recording)} frames")
                return True
                
            except Exception as e:
                logger.error(f"Device initialization test failed: {e}")
                return False
                
        except Exception as e:
            logger.error(f"Failed to initialize device: {e}", exc_info=True)
            return False

    def get_loopback_devices(self) -> List[Dict[str, Any]]:
        """
        Get available loopback/output recording devices for all platforms.
        
        Returns:
            List[Dict]: List of loopback devices with platform-specific info
        """
        loopback_devices = []
        system = platform.system().lower()
        
        try:
            devices = sd.query_devices()
            
            if system == "windows":
                # Windows WASAPI loopback devices
                for i, device_info in enumerate(devices):
                    device_name = device_info['name'].lower()
                    
                    # Look for output devices that support loopback
                    if device_info['max_output_channels'] > 0:
                        # Common Windows output device names
                        if any(keyword in device_name for keyword in [
                            'speakers', 'headphones', 'output', 'realtek', 
                            'audio', 'sound', 'stereo mix', 'what u hear'
                        ]):
                            loopback_devices.append({
                                'index': i,
                                'name': device_info['name'],
                                'platform': 'windows',
                                'type': 'wasapi_loopback',
                                'channels': device_info['max_output_channels'],
                                'sample_rate': device_info['default_samplerate'],
                                'hostapi': device_info['hostapi']
                            })
                            
            elif system == "linux":
                # Linux PulseAudio monitor devices
                try:
                    # Query PulseAudio for monitor sources
                    result = subprocess.run(
                        ['pactl', 'list', 'sources', 'short'], 
                        capture_output=True, text=True, timeout=5
                    )
                    if result.returncode == 0:
                        lines = result.stdout.strip().split('\n')
                        for line in lines:
                            if 'monitor' in line.lower():
                                parts = line.split('\t')
                                if len(parts) >= 2:
                                    loopback_devices.append({
                                        'index': parts[1],  # PulseAudio source name
                                        'name': parts[1],
                                        'platform': 'linux',
                                        'type': 'pulseaudio_monitor',
                                        'channels': 2,  # Usually stereo
                                        'sample_rate': 44100,  # Common default
                                        'hostapi': None
                                    })
                except (subprocess.TimeoutExpired, FileNotFoundError, subprocess.SubprocessError) as e:
                    logger.warning(f"Failed to query PulseAudio sources: {e}")
                
                # Also check sounddevice for monitor devices
                for i, device_info in enumerate(devices):
                    device_name = device_info['name'].lower()
                    if 'monitor' in device_name or 'loopback' in device_name:
                        loopback_devices.append({
                            'index': i,
                            'name': device_info['name'],
                            'platform': 'linux',
                            'type': 'alsa_monitor',
                            'channels': device_info['max_input_channels'],
                            'sample_rate': device_info['default_samplerate'],
                            'hostapi': device_info['hostapi']
                        })
                        
            elif system == "darwin":  # macOS
                # macOS virtual audio devices
                for i, device_info in enumerate(devices):
                    device_name = device_info['name'].lower()
                    if any(keyword in device_name for keyword in [
                        'blackhole', 'soundflower', 'loopback', 'virtual'
                    ]):
                        loopback_devices.append({
                            'index': i,
                            'name': device_info['name'],
                            'platform': 'macos',
                            'type': 'virtual_audio',
                            'channels': device_info['max_input_channels'],
                            'sample_rate': device_info['default_samplerate'],
                            'hostapi': device_info['hostapi']
                        })
            
            logger.info(f"Found {len(loopback_devices)} loopback devices on {system}")
            return loopback_devices
            
        except Exception as e:
            logger.error(f"Error detecting loopback devices: {e}")
            return []

    def is_loopback_supported(self) -> Tuple[bool, str]:
        """
        Check if system audio loopback recording is supported on current platform.
        
        Returns:
            Tuple[bool, str]: (is_supported, info_message)
        """
        system = platform.system().lower()
        
        if system == "windows":
            # Check for WASAPI support
            try:
                devices = sd.query_devices()
                wasapi_devices = [d for d in devices if d.get('hostapi') == 2]  # WASAPI
                if wasapi_devices:
                    return True, "WASAPI loopback supported"
                else:
                    return False, "WASAPI not available"
            except Exception as e:
                logger.warning(f"Failed to detect WASAPI support: {e}")
                return False, "Cannot detect WASAPI support"
                
        elif system == "linux":
            # Check for PulseAudio
            try:
                result = subprocess.run(['pactl', '--version'], 
                                      capture_output=True, timeout=2)
                if result.returncode == 0:
                    return True, "PulseAudio monitor sources supported"
                else:
                    return False, "PulseAudio not detected"
            except (subprocess.TimeoutExpired, FileNotFoundError) as e:
                logger.debug(f"PulseAudio not available: {e}")
                return False, "PulseAudio not available"
                
        elif system == "darwin":  # macOS
            # Check for virtual audio devices
            loopback_devices = self.get_loopback_devices()
            if loopback_devices:
                return True, f"Virtual audio devices available: {len(loopback_devices)}"
            else:
                return False, "Requires BlackHole or similar virtual audio driver"
        
        return False, f"Platform {system} not supported"

    def record_system_audio_chunk(self, duration: float = 0.1, device_index: Optional[int] = None) -> Optional[np.ndarray]:
        """
        Record a chunk of system audio output using platform-specific loopback.
        
        Args:
            duration: Duration in seconds to record
            device_index: Specific loopback device to use
            
        Returns:
            Optional[np.ndarray]: Audio data chunk or None if recording fails
        """
        try:
            system = platform.system().lower()
            
            if system == "windows":
                return self._record_windows_loopback(duration, device_index)
            elif system == "linux":
                return self._record_linux_loopback(duration, device_index)
            elif system == "darwin":
                return self._record_macos_loopback(duration, device_index)
            else:
                logger.error(f"System audio recording not supported on {system}")
                return None
                
        except Exception as e:
            logger.error(f"Failed to record system audio chunk: {e}")
            return None

    def _record_windows_loopback(self, duration: float, device_index: Optional[int] = None) -> Optional[np.ndarray]:
        """Record system audio on Windows using WASAPI loopback."""
        try:
            import sounddevice as sd
            
            # Find WASAPI output device for loopback
            if device_index is None:
                devices = sd.query_devices()
                wasapi_devices = [d for i, d in enumerate(devices) if d.get('hostapi') == 2 and d['max_output_channels'] > 0]
                if not wasapi_devices:
                    logger.error("No WASAPI output devices found for loopback")
                    return None
                device_index = next(i for i, d in enumerate(devices) if d == wasapi_devices[0])
            
            # Record with WASAPI loopback (Note: requires special configuration)
            frames = int(duration * self.sample_rate)
            
            # For Windows, we need to use input stream with special loopback flag
            # This is a limitation of sounddevice - true WASAPI loopback needs lower-level access
            logger.warning("Windows WASAPI loopback requires system configuration (Stereo Mix)")
            
            recording = sd.rec(
                frames,
                samplerate=self.sample_rate,
                channels=2,  # Usually stereo for system audio
                dtype=np.float32,
                device=device_index
            )
            sd.wait()
            
            return recording
            
        except Exception as e:
            logger.error(f"Windows loopback recording failed: {e}")
            return None

    def _record_linux_loopback(self, duration: float, device_name: Optional[str] = None) -> Optional[np.ndarray]:
        """Record system audio on Linux using PulseAudio monitor."""
        try:
            # Find PulseAudio monitor source
            if device_name is None:
                try:
                    result = subprocess.run(
                        ['pactl', 'list', 'sources', 'short'],
                        capture_output=True, text=True, timeout=5
                    )
                    if result.returncode == 0:
                        lines = result.stdout.strip().split('\n')
                        for line in lines:
                            if 'monitor' in line.lower():
                                parts = line.split('\t')
                                if len(parts) >= 2:
                                    device_name = parts[1]
                                    break
                except Exception as e:
                    logger.warning(f"Failed to find PulseAudio monitor: {e}")
                    return None
            
            if device_name is None:
                logger.error("No PulseAudio monitor source found")
                return None
            
            # Record from monitor device
            frames = int(duration * self.sample_rate)
            
            recording = sd.rec(
                frames,
                samplerate=self.sample_rate,
                channels=2,  # Usually stereo for system audio
                dtype=np.float32,
                device=device_name  # Use PulseAudio device name
            )
            sd.wait()
            
            return recording
            
        except Exception as e:
            logger.error(f"Linux loopback recording failed: {e}")
            return None

    def _record_macos_loopback(self, duration: float, device_index: Optional[int] = None) -> Optional[np.ndarray]:
        """Record system audio on macOS using virtual audio devices."""
        try:
            # Find virtual audio device (BlackHole, etc.)
            if device_index is None:
                loopback_devices = self.get_loopback_devices()
                if not loopback_devices:
                    logger.error("No virtual audio devices found. Install BlackHole or similar.")
                    return None
                device_index = loopback_devices[0]['index']
            
            frames = int(duration * self.sample_rate)
            
            recording = sd.rec(
                frames,
                samplerate=self.sample_rate,
                channels=2,  # Usually stereo for system audio
                dtype=np.float32,
                device=device_index
            )
            sd.wait()
            
            return recording
            
        except Exception as e:
            logger.error(f"macOS loopback recording failed: {e}")
            return None

    def _get_optimal_sample_rate(self, device=None):
        """Get the optimal sample rate for the specified device."""
        try:
            if device is None:
                device = sd.default.device[0]  # Default input device
            
            device_info = sd.query_devices(device)
            default_rate = int(device_info['default_samplerate'])
            
            # Common sample rates to test in order of preference
            preferred_rates = [44100, 48000, 22050, 16000, 8000]
            
            # If default rate is in our preferred list, use it
            if default_rate in preferred_rates:
                logger.info(f"Using device default sample rate: {default_rate}")
                return default_rate
            
            # Test preferred rates
            for rate in preferred_rates:
                try:
                    sd.check_input_settings(device=device, samplerate=rate)
                    logger.info(f"Selected optimal sample rate: {rate} for device {device}")
                    return rate
                except Exception:
                    # This rate is not supported, try next one
                    continue
            
            # Fallback to device default
            logger.warning(f"Using device default sample rate as fallback: {default_rate}")
            return default_rate
            
        except Exception as e:
            logger.error(f"Error detecting optimal sample rate: {e}, using 44100 as fallback")
            return 44100

    def _validate_and_get_supported_sample_rate(self, requested_rate):
        """
        Validate if the requested sample rate is supported by the device.
        If not, find and return a supported fallback rate.
        
        Args:
            requested_rate: The sample rate to validate
            
        Returns:
            int: A supported sample rate or None if no rate works
        """
        try:
            # Get device info for debugging
            device = self.device if self.device is not None else sd.default.device[0]
            device_info = sd.query_devices(device)
            logger.debug(f"Using device: {device_info['name']}, default rate: {device_info['default_samplerate']}")
            
            # First, try the requested rate
            try:
                sd.check_input_settings(
                    device=device, 
                    samplerate=requested_rate,
                    channels=self.channels,
                    dtype=np.float32
                )
                logger.debug(f"Requested sample rate {requested_rate} is supported")
                return requested_rate
            except Exception as e:
                logger.warning(f"Requested sample rate {requested_rate} not supported: {e}")
            
            # Try common fallback rates in order of preference
            fallback_rates = [44100, 48000, 22050, 16000, 8000, int(device_info['default_samplerate'])]
            
            for rate in fallback_rates:
                if rate == requested_rate:  # Already tested above
                    continue
                try:
                    sd.check_input_settings(
                        device=device,
                        samplerate=rate,
                        channels=self.channels,
                        dtype=np.float32
                    )
                    logger.info(f"Using fallback sample rate: {rate}")
                    return rate
                except Exception:
                    continue
            
            logger.error("No supported sample rate found for the current device")
            return None
            
        except Exception as e:
            logger.error(f"Error validating sample rate: {e}")
            return None

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
            # Validate sample rate before testing
            validated_sample_rate = self._validate_and_get_supported_sample_rate(self.sample_rate)
            if validated_sample_rate is None:
                logger.error("No supported sample rate found for microphone test")
                return False
            
            # Try to create a short test recording
            test_duration = 0.1  # 100ms test
            test_data = sd.rec(
                int(test_duration * validated_sample_rate), 
                samplerate=validated_sample_rate, 
                channels=self.channels,
                device=self.device
            )
            sd.wait()  # Wait for recording to complete
            
            # Check if we got valid data
            if test_data is not None and len(test_data) > 0:
                logger.info("Microphone access test successful")
                return True
            else:
                logger.warning("Microphone test returned empty data")
                return False
                
        except Exception as e:
            logger.error(f"Microphone access test failed: {e}")
            return False
    
    def is_output_capture_available(self) -> bool:
        """Check if system output capture is available."""
        is_supported, _ = self.is_loopback_supported()
        return is_supported

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
            logger.info("Microphone capture initiated. Press Ctrl+C to stop.")
            
        except Exception as e:
            logger.error(f"Failed to start input stream: {e}")
            logger.error(f"Failed to start microphone capture: {e}")
            raise

    def start_output_stream(self, callback: Optional[Callable] = None, device: Optional[int] = None):
        """Start capturing system output audio (if supported by the system)."""
        try:
            # First, try to find a loopback or monitor device
            devices = sd.query_devices()
            loopback_device = None
            
            # Look for different types of loopback/monitor devices across platforms
            for i, device_info in enumerate(devices):
                device_name = device_info['name'].lower()
                # Windows devices
                if ('stereo mix' in device_name or 
                    'what u hear' in device_name or
                    'speakers' in device_name and 'monitor' in device_name):
                    loopback_device = i
                    break
                # Linux PulseAudio devices
                elif ('monitor' in device_name or 
                      'loopback' in device_name or
                      '.monitor' in device_name):
                    loopback_device = i
                    break
                # macOS devices 
                elif ('blackhole' in device_name or
                      'soundflower' in device_name):
                    loopback_device = i
                    break
            
            # On Linux, try to use PulseAudio monitor devices if available
            if loopback_device is None:
                try:
                    import subprocess
                    result = subprocess.run(['pactl', 'list', 'sources', 'short'], 
                                          capture_output=True, text=True, timeout=5)
                    if result.returncode == 0:
                        lines = result.stdout.strip().split('\n')
                        for line in lines:
                            if 'monitor' in line.lower():
                                # Found a monitor source, try to use it
                                parts = line.split('\t')
                                if len(parts) > 1:
                                    monitor_name = parts[1]
                                    logger.info(f"Found PulseAudio monitor: {monitor_name}")
                                    # Use PulseAudio device name directly
                                    loopback_device = monitor_name
                                    break
                except (subprocess.TimeoutExpired, FileNotFoundError, subprocess.SubprocessError):
                    pass
            
            if loopback_device is None:
                # Fallback: try using default input device with warning
                logger.warning("No dedicated loopback device found. Using default input device as fallback.")
                loopback_device = sd.default.device[0]  # Default input device
                if loopback_device is None:
                    raise Exception("No audio input device available for output capture.")

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
            
            if isinstance(loopback_device, str):
                device_name = loopback_device
            else:
                device_name = devices[loopback_device]['name'] if loopback_device < len(devices) else "Default"
            logger.info(f"Output capture started using device: {device_name}")
            
        except Exception as e:
            logger.error(f"Failed to start output capture: {e}")
            # Don't raise the exception, just log it and continue
            logger.info("Output capture unavailable. System audio recording disabled.")
            return False

    def record_fixed_duration(self, duration: float, device: Optional[int] = None) -> np.ndarray:
        """Record audio for a fixed duration."""
        try:
            # Use instance device if no device specified
            if device is None:
                device = self.device
                
            logger.info(f"Recording {duration} seconds of audio...")
            
            # Validate device compatibility first
            if device is not None:
                try:
                    sd.check_input_settings(device=device, samplerate=self.sample_rate, channels=self.channels)
                except Exception as e:
                    logger.warning(f"Device {device} not compatible with current settings: {e}")
                    # Try to get optimal settings for this device
                    optimal_rate = self._get_optimal_sample_rate(device)
                    if optimal_rate != self.sample_rate:
                        logger.info(f"Adjusting sample rate from {self.sample_rate} to {optimal_rate} for device {device}")
                        self.sample_rate = optimal_rate
            
            # Validate and get supported sample rate
            validated_sample_rate = self._validate_and_get_supported_sample_rate(self.sample_rate)
            if validated_sample_rate is None:
                logger.error("No supported sample rate found for recording")
                raise RuntimeError("No supported sample rate available for audio recording")
            
            if validated_sample_rate != self.sample_rate:
                logger.info(f"Using validated sample rate {validated_sample_rate} for recording")
            
            recording = sd.rec(
                int(duration * validated_sample_rate),
                samplerate=validated_sample_rate,
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

    def record_audio(self, duration: float, device: Optional[int] = None, output_path: Optional[str] = None) -> str:
        """
        Record audio for a fixed duration and save to file.
        
        Args:
            duration: Duration in seconds to record
            device: Audio device to use (None for default)
            output_path: Path to save the audio file (None for auto-generated temp file)
            
        Returns:
            str: Path to the saved audio file
        """
        try:
            import tempfile
            import soundfile as sf
            from pathlib import Path
            
            # Record the audio data
            audio_data = self.record_fixed_duration(duration, device)
            
            # Generate output path if not provided
            if output_path is None:
                temp_file = tempfile.NamedTemporaryFile(suffix='.wav', delete=False)
                output_path = temp_file.name
                temp_file.close()
            
            # Ensure the directory exists
            Path(output_path).parent.mkdir(parents=True, exist_ok=True)
            
            # Save audio data to file
            sf.write(output_path, audio_data, self.sample_rate)
            logger.info(f"Audio saved to: {output_path}")
            
            return output_path
            
        except ImportError as e:
            logger.error("soundfile library not available. Install with: pip install soundfile")
            raise ImportError("soundfile library required for saving audio files") from e
        except Exception as e:
            logger.error(f"Failed to record and save audio: {e}")
            raise

    def get_audio_buffer(self) -> np.ndarray:
        """Get the current audio buffer and clear it."""
        if not self.audio_buffer:
            return np.array([])
        
        # Concatenate all audio chunks
        audio_data = np.concatenate(self.audio_buffer, axis=0)
        self.audio_buffer.clear()
        return audio_data

    def capture_chunk(self, duration: float = 0.1) -> Optional[np.ndarray]:
        """
        Capture one audio chunk from the device for real-time processing.
        
        This method is used by the pipeline manager for continuous audio capture
        and processing. It internally uses the record_chunk method.
        
        Args:
            duration: Duration in seconds to capture (default: 0.1s)
            
        Returns:
            Optional[np.ndarray]: Audio data chunk or None if capture fails
        """
        try:
            # Use the existing record_chunk implementation
            audio_data = self.record_chunk(duration=duration, sample_rate=self.sample_rate)
            
            if audio_data is not None:
                logger.debug(f"Captured audio chunk: {audio_data.shape}, "
                           f"max: {np.max(np.abs(audio_data)):.4f}")
                return audio_data
            else:
                logger.warning("No audio data captured in chunk")
                return None
                
        except Exception as e:
            logger.error(f"Failed to capture audio chunk: {e}")
            return None

    def stop(self):
        """Stop audio capture."""
        if self.stream:
            self.stream.stop()
            self.stream.close()
            self.stream = None
            self.is_recording = False
            logger.info("Audio capture stopped")
            logger.info("Capture stopped.")

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.stop()

    def record_chunk(self, duration: float = 0.1, sample_rate: Optional[int] = None) -> Optional[np.ndarray]:
        """
        Record a small chunk of audio for streaming applications.
        
        Args:
            duration: Duration in seconds to record (default: 0.1s)
            sample_rate: Sample rate to use (default: instance sample_rate)
            
        Returns:
            Optional[np.ndarray]: Audio data chunk or None if recording fails
            
        Note:
            This method is designed for real-time streaming where small chunks
            are continuously captured and processed.
        """
        try:
            # Enhanced debug logging
            logger.debug(f"Recording chunk - Duration: {duration}s, Device: {self.device}, Channels: {self.channels}")
            
            # Validate inputs
            if duration <= 0:
                logger.warning(f"Invalid duration {duration}, using default 0.1s")
                duration = 0.1
                
            if sample_rate is None:
                sample_rate = self.sample_rate
            elif not isinstance(sample_rate, int) or sample_rate <= 0:
                logger.warning(f"Invalid sample_rate {sample_rate}, using instance rate {self.sample_rate}")
                sample_rate = self.sample_rate
            
            # Check if audio system is available
            if not hasattr(sd, 'rec') or not callable(sd.rec):
                logger.error("SoundDevice recording not available")
                return None
            
            # Log device information before recording
            try:
                if self.device is not None:
                    device_info = sd.query_devices(self.device)
                    logger.debug(f"Using device {self.device}: {device_info.get('name', 'Unknown')} "
                               f"(inputs: {device_info.get('max_input_channels', 0)}, "
                               f"hostapi: {device_info.get('hostapi', 'Unknown')})")
                else:
                    default_device = sd.query_devices(kind='input')
                    logger.debug(f"Using default input device: {default_device.get('name', 'Unknown')}")
            except Exception as e:
                logger.warning(f"Could not query device info: {e}")
            
            # Validate sample rate with device before recording
            validated_sample_rate = self._validate_and_get_supported_sample_rate(sample_rate)
            if validated_sample_rate is None:
                logger.error("No supported sample rate found for audio recording")
                return None
            
            if validated_sample_rate != sample_rate:
                logger.info(f"Using validated sample rate {validated_sample_rate} instead of requested {sample_rate}")
                sample_rate = validated_sample_rate
            
            # Record the chunk
            frames = int(duration * sample_rate)
            logger.debug(f"Recording {frames} frames at {sample_rate}Hz...")
            
            recording = sd.rec(
                frames,
                samplerate=sample_rate,
                channels=self.channels,
                dtype=np.float32,
                device=self.device
            )
            sd.wait()  # Wait until recording is finished
            
            # Validate recording result
            if recording is None or len(recording) == 0:
                logger.warning("Empty recording chunk received")
                return None
                
            # Flatten if mono channel
            if self.channels == 1 and recording.ndim > 1:
                recording = recording.flatten()
            
            # Log audio signal statistics for debugging
            audio_max = np.max(np.abs(recording))
            audio_rms = np.sqrt(np.mean(recording**2))
            audio_energy = np.sum(recording**2)
            
            logger.debug(f"Audio chunk stats - Max: {audio_max:.4f}, RMS: {audio_rms:.4f}, "
                        f"Energy: {audio_energy:.4f}, Shape: {recording.shape}")
            
            # Alert if signal is very weak (might indicate device issues)
            if audio_max < 0.001:
                logger.warning(f"Very weak audio signal detected (max: {audio_max:.6f}). "
                             f"Check microphone connection and input levels.")
            elif audio_max > 0.1:
                logger.debug(f"Strong audio signal detected (max: {audio_max:.4f})")
                
            return recording
            
        except Exception as e:
            logger.error(f"Failed to record audio chunk: {e}")
            # Log additional debugging info on error
            try:
                logger.debug(f"Error context - Device: {self.device}, Channels: {self.channels}, "
                           f"Sample rate: {getattr(self, 'sample_rate', 'Unknown')}")
                if hasattr(sd, 'query_devices'):
                    devices = sd.query_devices()
                    logger.debug(f"Available devices: {len(devices) if devices is not None else 0}")
            except Exception as e:
                logger.debug(f"Could not gather device debug information: {e}")
            return None

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
    logger.info("Testing Audio System...")
    
    try:
        # Test device listing
        capture = AudioCapture()
        devices_info = capture.list_devices()
        
        logger.info(f"Found {len(devices_info['devices'])} audio devices")
        logger.info(f"Default input device: {devices_info['default_input']}")
        logger.info(f"Default output device: {devices_info['default_output']}")
        
        # Test microphone access
        logger.info("Testing microphone access...")
        if capture.test_microphone_access():
            logger.info("Microphone access successful")
        else:
            logger.error("Microphone access failed")
            return False
        
        # Test short recording
        logger.info("Testing 2-second recording...")
        recording = capture.record_fixed_duration(2.0)
        logger.info(f"Recording completed: {recording.shape} samples")
        
        logger.info("Audio system test completed successfully!")
        return True
        
    except Exception as e:
        logger.error(f"Audio system test failed: {e}")
        return False

if __name__ == "__main__":
    test_audio_system()