#! /usr/bin/env python3
#-------------------------------------------------------------------------------------------------
# description: Audio Recorder Component
#-------------------------------------------------------------------------------------------------
#
# author: ingekastel
# date: 2025-06-02
# version: 1.0
#
# requirements:
# - streamlit Python package
# - tempfile Python package
# - os Python package
# - pathlib Python package
# - typing Python package
# - logging Python package
#-------------------------------------------------------------------------------------------------  
# functions:
# - AudioRecorder: Audio recorder component class
# - render_recording_interface: Render the audio recording interface
# - _start_recording: Start audio recording
# - _stop_recording: Stop audio recording
# - _render_recording_settings: Render recording settings
# - create_audio_file: Create an audio file from audio data
# - get_recording_status: Get current recording status
# - clear_audio: Clear the current audio data
# - get_audio_duration: Get audio duration in seconds
#-------------------------------------------------------------------------------------------------

import streamlit as st
import tempfile
import os
from pathlib import Path
from typing import Optional, Dict, Any
import logging

logger = logging.getLogger(__name__)


class AudioRecorder:
    """Audio recorder component for web interface."""
    
    def __init__(self):
        """Initialize the audio recorder."""
        self.recording_settings = {
            "sample_rate": 16000,
            "channels": 1,
            "duration": 10,  # seconds
            "format": "wav"
        }
        self.is_recording = False
        self.current_audio = None
    
    def render_recording_interface(self) -> Optional[bytes]:
        """
        Render the audio recording interface.
        
        Returns:
            Audio data as bytes if recording completed, None otherwise
        """
        st.markdown("#### 🎙️ Audio Recording")
        
        # Recording controls
        col1, col2, col3 = st.columns(3)
        
        with col1:
            if st.button("🔴 Start Recording", use_container_width=True, type="primary"):
                self._start_recording()
        
        with col2:
            if st.button("⏹️ Stop Recording", use_container_width=True):
                audio_data = self._stop_recording()
                if audio_data:
                    st.success("Recording completed!")
                    return audio_data
                else:
                    st.warning("No recording in progress.")
        
        with col3:
            if st.button("🎵 Play Last Recording", use_container_width=True):
                if self.current_audio:
                    st.audio(self.current_audio, format='audio/wav')
                else:
                    st.warning("No audio recorded yet.")
        
        # Recording status
        if self.is_recording:
            st.markdown("**Recording in progress...** 🎙️")
            st.progress(0.5)  # Placeholder progress
        
        # Recording settings
        with st.expander("⚙️ Recording Settings"):
            self._render_recording_settings()
        
        return None
    
    def _start_recording(self) -> None:
        """Start audio recording."""
        try:
            self.is_recording = True
            st.session_state.recording = True
            logger.info("Started audio recording")
        except Exception as e:
            logger.error(f"Failed to start recording: {e}")
            st.error("Failed to start recording")
    
    def _stop_recording(self) -> Optional[bytes]:
        """Stop audio recording and return audio data."""
        try:
            self.is_recording = False
            st.session_state.recording = False
            logger.info("Stopped audio recording")
            
            # Placeholder for actual audio capture
            # In a real implementation, this would capture actual audio
            audio_data = b"audio_data_placeholder"
            self.current_audio = audio_data
            
            return audio_data
            
        except Exception as e:
            logger.error(f"Failed to stop recording: {e}")
            st.error("Failed to stop recording")
            return None
    
    def _render_recording_settings(self) -> None:
        """Render recording settings controls."""
        col1, col2 = st.columns(2)
        
        with col1:
            self.recording_settings["sample_rate"] = st.selectbox(
                "Sample Rate",
                [8000, 16000, 22050, 44100],
                index=1
            )
            
            self.recording_settings["channels"] = st.selectbox(
                "Channels",
                [1, 2],
                index=0
            )
        
        with col2:
            self.recording_settings["duration"] = st.slider(
                "Max Duration (seconds)",
                1, 60, 10
            )
            
            self.recording_settings["format"] = st.selectbox(
                "Format",
                ["wav", "mp3", "flac"],
                index=0
            )
        
        if st.button("💾 Save Settings", use_container_width=True):
            st.success("Recording settings saved!")
    
    def create_audio_file(self, audio_data: bytes, filename: str = None) -> Optional[str]:
        """
        Create an audio file from audio data.
        
        Args:
            audio_data: Audio data as bytes
            filename: Optional filename
            
        Returns:
            Path to created audio file or None if failed
        """
        try:
            if not filename:
                filename = f"recording_{hash(audio_data) % 10000}.{self.recording_settings['format']}"
            
            # Create temp directory if needed
            temp_dir = Path("temp")
            temp_dir.mkdir(exist_ok=True)
            
            output_path = temp_dir / filename
            
            # Write audio data to file
            with open(output_path, 'wb') as f:
                f.write(audio_data)
            
            logger.info(f"Created audio file: {output_path}")
            return str(output_path)
            
        except Exception as e:
            logger.error(f"Failed to create audio file: {e}")
            return None
    
    def get_recording_status(self) -> Dict[str, Any]:
        """
        Get current recording status.
        
        Returns:
            Dictionary containing recording status
        """
        return {
            "is_recording": self.is_recording,
            "recording_settings": self.recording_settings,
            "has_audio": self.current_audio is not None
        }
    
    def clear_audio(self) -> None:
        """Clear the current audio data."""
        self.current_audio = None
        logger.info("Cleared audio data")
    
    def get_audio_duration(self, audio_data: bytes) -> float:
        """
        Get audio duration in seconds.
        
        Args:
            audio_data: Audio data as bytes
            
        Returns:
            Duration in seconds
        """
        try:
            # Rough estimation based on data size and sample rate
            sample_rate = self.recording_settings["sample_rate"]
            channels = self.recording_settings["channels"]
            bytes_per_sample = 2  # Assuming 16-bit audio
            
            total_samples = len(audio_data) / bytes_per_sample
            duration = total_samples / (sample_rate * channels)
            
            return max(0.0, duration)
            
        except Exception as e:
            logger.error(f"Failed to calculate audio duration: {e}")
            return 0.0 