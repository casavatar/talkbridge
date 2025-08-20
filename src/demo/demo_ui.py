#!/usr/bin/env python3
"""
TalkBridge Demo - Demo Ui
=========================

Módulo demo_ui para TalkBridge

Author: TalkBridge Team
Date: 2025-08-19
Version: 1.0

Requirements:
- PyQt6
======================================================================
Functions:
- render_demo_header: Render demo mode header with status information.
- render_demo_status: Render demo system status.
- render_demo_audio_recorder: Render demo audio recorder component.
- render_demo_transcription: Render demo transcription display.
- render_demo_translation: Render demo translation display.
- render_demo_llm_response: Render demo LLM response display.
- render_demo_voice_synthesis: Render demo voice synthesis display.
- render_demo_avatar: Render demo avatar display.
- render_demo_conversation_log: Render demo conversation history.
- render_demo_full_conversation: Render full demo conversation flow.
======================================================================
"""

import streamlit as st
import time
import json
from datetime import datetime
from typing import Dict, List, Optional
import base64

from demo.demo_runner import get_demo_runner, run_demo_conversation
from demo.demo_config import is_demo_mode, get_demo_setting, get_demo_file_path
from demo.demo_api import (
    get_tts_api, get_stt_api, get_llm_api, 
    get_translation_api, get_animation_api, get_audio_api
)


def render_demo_header():
    """Render demo mode header with status information."""
    st.markdown("""
    <div style="background-color: #ff6b6b; padding: 10px; border-radius: 5px; margin-bottom: 20px;">
        <h3 style="color: white; margin: 0;">🎭 DEMO MODE ACTIVE</h3>
        <p style="color: white; margin: 5px 0 0 0; font-size: 14px;">
            Running in simulation mode - no real hardware or external services required
        </p>
    </div>
    """, unsafe_allow_html=True)


def render_demo_status():
    """Render demo system status."""
    st.subheader("📊 Demo System Status")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric("Demo Mode", "ACTIVE" if is_demo_mode() else "INACTIVE")
    
    with col2:
        demo_runner = get_demo_runner()
        st.metric("Conversations", len(demo_runner.get_conversation_history()))
    
    with col3:
        st.metric("System Status", "Ready")


def render_demo_audio_recorder():
    """Render demo audio recorder component."""
    st.subheader("🎤 Demo Audio Recording")
    
    # Demo recording controls
    col1, col2, col3 = st.columns([2, 1, 1])
    
    with col1:
        recording_duration = st.slider("Recording Duration (seconds)", 1, 10, 5)
    
    with col2:
        if st.button("🎙️ Start Recording", key="demo_record_start"):
            with st.spinner(f"Recording for {recording_duration} seconds..."):
                # Simulate recording delay
                if get_demo_setting("simulate_delays"):
                    time.sleep(recording_duration)
                
                st.success("✅ Recording completed!")
                st.session_state.demo_audio_captured = True
    
    with col3:
        if st.button("🔄 Reset", key="demo_record_reset"):
            st.session_state.demo_audio_captured = False
            st.session_state.demo_transcription = ""
            st.session_state.demo_translation = ""
            st.session_state.demo_response = ""
            st.rerun()
    
    # Show demo audio file info
    if st.session_state.get("demo_audio_captured", False):
        st.info("📁 Demo audio captured from: `samples/input_audio.wav`")
        
        # Display audio file
        try:
            audio_file = get_demo_file_path("input_audio")
            with open(audio_file, "rb") as f:
                audio_bytes = f.read()
            
            st.audio(audio_bytes, format="audio/wav")
        except Exception as e:
            st.error(f"Could not load demo audio: {e}")


def render_demo_transcription():
    """Render demo transcription display."""
    st.subheader("📝 Demo Transcription")
    
    if st.session_state.get("demo_audio_captured", False):
        with st.spinner("Processing speech..."):
            # Simulate transcription delay
            if get_demo_setting("simulate_delays"):
                time.sleep(get_demo_setting("delay_transcription", 2.0))
            
            # Load demo transcription
            try:
                transcript_file = get_demo_file_path("transcribed_text")
                with open(transcript_file, 'r', encoding='utf-8') as f:
                    transcription = f.read().strip()
                
                st.session_state.demo_transcription = transcription
                st.success("✅ Transcription completed!")
                
            except Exception as e:
                st.error(f"Could not load demo transcription: {e}")
                st.session_state.demo_transcription = "Hello, how are you?"
    
    # Display transcription
    if st.session_state.get("demo_transcription"):
        st.text_area("Transcribed Text:", st.session_state.demo_transcription, height=100, key="transcribed_text_demo")


def render_demo_translation():
    """Render demo translation display."""
    st.subheader("🌐 Demo Translation")
    
    if st.session_state.get("demo_transcription"):
        with st.spinner("Translating to Spanish..."):
            # Simulate translation delay
            if get_demo_setting("simulate_delays"):
                time.sleep(get_demo_setting("delay_translation", 1.0))
            
            # Load demo translation
            try:
                translation_file = get_demo_file_path("translation")
                with open(translation_file, 'r', encoding='utf-8') as f:
                    translation = f.read().strip()
                
                st.session_state.demo_translation = translation
                st.success("✅ Translation completed!")
                
            except Exception as e:
                st.error(f"Could not load demo translation: {e}")
                st.session_state.demo_translation = "Hola, ¿cómo estás?"
    
    # Display translation
    if st.session_state.get("demo_translation"):
        col1, col2 = st.columns(2)
        with col1:
            st.text_area("Original (English):", st.session_state.demo_transcription, height=100)
        with col2:
            st.text_area("Translation (Spanish):", st.session_state.demo_translation, height=100)


def render_demo_llm_response():
    """Render demo LLM response display."""
    st.subheader("🤖 Demo AI Response")
    
    if st.session_state.get("demo_translation"):
        with st.spinner("Generating AI response..."):
            # Simulate LLM delay
            if get_demo_setting("simulate_delays"):
                time.sleep(get_demo_setting("delay_llm_response", 3.0))
            
            # Load demo response
            try:
                response_file = get_demo_file_path("llm_response")
                with open(response_file, 'r', encoding='utf-8') as f:
                    response = f.read().strip()
                
                st.session_state.demo_response = response
                st.success("✅ AI response generated!")
                
            except Exception as e:
                st.error(f"Could not load demo response: {e}")
                st.session_state.demo_response = "I'm doing well, thank you for asking! How can I help you today?"
    
    # Display response
    if st.session_state.get("demo_response"):
        st.text_area("AI Response:", st.session_state.demo_response, height=150, key="ai_response_demo")


def render_demo_voice_synthesis():
    """Render demo voice synthesis display."""
    st.subheader("🔊 Demo Voice Synthesis")
    
    if st.session_state.get("demo_response"):
        with st.spinner("Synthesizing voice..."):
            # Simulate synthesis delay
            if get_demo_setting("simulate_delays"):
                time.sleep(get_demo_setting("delay_voice_synthesis", 2.5))
            
            st.success("✅ Voice synthesis completed!")
            st.session_state.demo_voice_synthesized = True
    
    # Display synthesized audio
    if st.session_state.get("demo_voice_synthesized", False):
        try:
            voice_file = get_demo_file_path("voice_output")
            with open(voice_file, "rb") as f:
                voice_bytes = f.read()
            
            st.audio(voice_bytes, format="audio/wav")
            st.info("📁 Demo voice synthesized from: `samples/voice_output.wav`")
            
        except Exception as e:
            st.error(f"Could not load demo voice: {e}")


def render_demo_avatar():
    """Render demo avatar display."""
    st.subheader("👤 Demo Avatar")
    
    try:
        avatar_file = get_demo_file_path("avatar_image")
        
        # Display avatar image
        st.image(avatar_file, caption="Demo Avatar", use_column_width=True)
        
        # Avatar controls
        col1, col2, col3 = st.columns(3)
        
        with col1:
            if st.button("🎭 Lip Sync", key="demo_lip_sync"):
                with st.spinner("Synchronizing lip movements..."):
                    if get_demo_setting("simulate_delays"):
                        time.sleep(get_demo_setting("delay_avatar_animation", 0.5))
                    st.success("✅ Lip sync completed!")
        
        with col2:
            if st.button("👁️ Eye Blink", key="demo_eye_blink"):
                with st.spinner("Blinking eyes..."):
                    if get_demo_setting("simulate_delays"):
                        time.sleep(0.3)
                    st.success("✅ Eye blink completed!")
        
        with col3:
            if st.button("😊 Expression", key="demo_expression"):
                with st.spinner("Changing expression..."):
                    if get_demo_setting("simulate_delays"):
                        time.sleep(0.5)
                    st.success("✅ Expression changed!")
        
    except Exception as e:
        st.error(f"Could not load demo avatar: {e}")


def render_demo_conversation_log():
    """Render demo conversation history."""
    st.subheader("📚 Demo Conversation History")
    
    demo_runner = get_demo_runner()
    conversation_history = demo_runner.get_conversation_history()
    
    if conversation_history:
        for i, entry in enumerate(reversed(conversation_history)):
            with st.expander(f"Conversation {len(conversation_history) - i} - {entry.get('timestamp', 'Unknown')}"):
                col1, col2 = st.columns(2)
                
                with col1:
                    st.write("**User:**", entry.get('message', ''))
                    st.write("**Translation:**", entry.get('translation', ''))
                
                with col2:
                    st.write("**AI Response:**", entry.get('response', ''))
                    if entry.get('audio_file'):
                        st.write("**Audio:**", entry.get('audio_file', ''))
    else:
        st.info("No conversation history yet. Start a demo conversation to see results.")


def render_demo_full_conversation():
    """Render full demo conversation flow."""
    st.subheader("🔄 Full Demo Conversation")
    
    if st.button("🚀 Run Full Demo Conversation", key="demo_full_conversation"):
        with st.spinner("Running complete demo conversation..."):
            try:
                results = run_demo_conversation()
                
                if "error" not in results:
                    st.success("✅ Demo conversation completed successfully!")
                    
                    # Display results in tabs
                    tab1, tab2, tab3, tab4 = st.tabs(["📝 Text", "🔊 Audio", "👤 Avatar", "📊 Log"])
                    
                    with tab1:
                        col1, col2 = st.columns(2)
                        with col1:
                            st.write("**Original:**", results.get("transcription", ""))
                            st.write("**Translation:**", results.get("translation", ""))
                        with col2:
                            st.write("**AI Response:**", results.get("llm_response", ""))
                    
                    with tab2:
                        if results.get("voice_audio"):
                            st.audio(results["voice_audio"], format="audio/wav")
                        else:
                            st.info("No audio available in demo")
                    
                    with tab3:
                        avatar_path = results.get("avatar_image", "")
                        if avatar_path:
                            st.image(avatar_path, caption="Demo Avatar", use_column_width=True)
                        else:
                            st.info("No avatar available in demo")
                    
                    with tab4:
                        log_entries = results.get("conversation_log", [])
                        for entry in log_entries:
                            st.json(entry)
                else:
                    st.error(f"Demo conversation failed: {results['error']}")
                    
            except Exception as e:
                st.error(f"Demo conversation error: {e}")


def render_demo_settings():
    """Render demo settings panel."""
    st.subheader("⚙️ Demo Settings")
    
    # Demo mode toggle
    demo_enabled = st.checkbox("Enable Demo Mode", value=is_demo_mode(), key="demo_mode_toggle")
    
    if demo_enabled != is_demo_mode():
        st.warning("Demo mode setting change requires restart to take effect.")
    
    # Delay settings
    st.write("**Simulation Delays:**")
    col1, col2 = st.columns(2)
    
    with col1:
        transcription_delay = st.slider("Transcription Delay (s)", 0.0, 5.0, get_demo_setting("delay_transcription", 2.0))
        translation_delay = st.slider("Translation Delay (s)", 0.0, 3.0, get_demo_setting("delay_translation", 1.0))
        llm_delay = st.slider("LLM Response Delay (s)", 0.0, 5.0, get_demo_setting("delay_llm_response", 3.0))
    
    with col2:
        synthesis_delay = st.slider("Voice Synthesis Delay (s)", 0.0, 5.0, get_demo_setting("delay_voice_synthesis", 2.5))
        avatar_delay = st.slider("Avatar Animation Delay (s)", 0.0, 2.0, get_demo_setting("delay_avatar_animation", 0.5))
        simulate_delays = st.checkbox("Simulate Delays", value=get_demo_setting("simulate_delays", True), key="simulate_delays_demo")
    
    # Demo file info
    st.write("**Demo Files:**")
    demo_files = {
        "Input Audio": get_demo_file_path("input_audio"),
        "Transcription": get_demo_file_path("transcribed_text"),
        "Translation": get_demo_file_path("translation"),
        "LLM Response": get_demo_file_path("llm_response"),
        "Voice Output": get_demo_file_path("voice_output"),
        "Avatar Image": get_demo_file_path("avatar_image")
    }
    
    for name, path in demo_files.items():
        st.text(f"{name}: {path}")


def render_demo_dashboard():
    """Render the complete demo dashboard."""
    render_demo_header()
    
    # Demo status
    render_demo_status()
    
    # Demo tabs
    tab1, tab2, tab3, tab4, tab5 = st.tabs([
        "🎤 Audio Recording", 
        "📝 Transcription", 
        "🌐 Translation", 
        "🤖 AI Response", 
        "🔊 Voice Synthesis"
    ])
    
    with tab1:
        render_demo_audio_recorder()
    
    with tab2:
        render_demo_transcription()
    
    with tab3:
        render_demo_translation()
    
    with tab4:
        render_demo_llm_response()
    
    with tab5:
        render_demo_voice_synthesis()
    
    # Avatar and conversation
    st.markdown("---")
    col1, col2 = st.columns(2)
    
    with col1:
        render_demo_avatar()
    
    with col2:
        render_demo_full_conversation()
    
    # Conversation history and settings
    st.markdown("---")
    col1, col2 = st.columns([2, 1])
    
    with col1:
        render_demo_conversation_log()
    
    with col2:
        render_demo_settings()


if __name__ == "__main__":
    st.set_page_config(page_title="TalkBridge Demo", layout="wide")
    st.title("TalkBridge Demo Mode")
    render_demo_dashboard() 