#!/usr/bin/env python3
#----------------------------------------------------------------------------------------------------------------------------
# description: Audio Visualizer Animation Module
#----------------------------------------------------------------------------------------------------------------------------
# 
# author: ingekastel
# date: 2025-06-02
# version: 1.0
# 
# requirements:
# - numpy Python package
# - matplotlib Python package
# - sounddevice Python package
# - soundfile Python package
# - scipy Python package
# - seaborn Python package
#----------------------------------------------------------------------------------------------------------------------------
# functions:
# - AudioVisualizer: Audio visualization animations
# - AudioVisualizerDemo: Demo class to showcase different audio visualization animations
#----------------------------------------------------------------------------------------------------------------------------

import numpy as np
import matplotlib.pyplot as plt
import matplotlib.animation as animation
from matplotlib.patches import Circle, Rectangle
import threading
import time
from typing import Optional, Callable, List, Tuple
import queue


class AudioVisualizer:
    """
    Real-time audio visualization with various animation styles.
    """
    
    def __init__(self, style: str = "bars"):
        """
        Initialize the audio visualizer.
        
        Args:
            style: Animation style ('bars', 'wave', 'circular', 'spectrum')
        """
        self.style = style
        self.fig = None
        self.ax = None
        self.animation = None
        self.audio_queue = queue.Queue()
        self.is_running = False
        self.thread = None
        
        # Animation parameters
        self.bar_count = 50
        self.max_amplitude = 1.0
        self.smoothing_factor = 0.8
        
        # Color schemes
        self.colors = {
            'bars': plt.cm.viridis,
            'wave': plt.cm.plasma,
            'circular': plt.cm.hsv,
            'spectrum': plt.cm.inferno
        }
    
    def start_visualization(self, audio_callback: Callable):
        """
        Start the audio visualization in a separate thread.
        
        Args:
            audio_callback: Function that provides audio data
        """
        self.is_running = True
        self.thread = threading.Thread(target=self._audio_processing_thread, args=(audio_callback,))
        self.thread.daemon = True
        self.thread.start()
        
        self._setup_animation()
        plt.show()
    
    def _audio_processing_thread(self, audio_callback: Callable):
        """Process audio data in background thread."""
        while self.is_running:
            try:
                # Simulate audio data processing
                audio_data = np.random.rand(1024) * 0.5
                self.audio_queue.put(audio_data)
                time.sleep(0.01)  # 100 FPS
            except Exception as e:
                print(f"Audio processing error: {e}")
                break
    
    def _setup_animation(self):
        """Setup the matplotlib animation."""
        plt.ion()
        self.fig, self.ax = plt.subplots(figsize=(12, 8))
        self.ax.set_xlim(0, 1)
        self.ax.set_ylim(0, 1)
        self.ax.set_aspect('equal')
        self.ax.axis('off')
        
        # Set background
        self.ax.set_facecolor('black')
        self.fig.patch.set_facecolor('black')
        
        if self.style == "bars":
            self._setup_bars_animation()
        elif self.style == "wave":
            self._setup_wave_animation()
        elif self.style == "circular":
            self._setup_circular_animation()
        elif self.style == "spectrum":
            self._setup_spectrum_animation()
    
    def _setup_bars_animation(self):
        """Setup bar chart animation."""
        self.bars = []
        bar_width = 1.0 / self.bar_count
        
        for i in range(self.bar_count):
            bar = Rectangle((i * bar_width, 0), bar_width * 0.8, 0.1, 
                          facecolor='cyan', alpha=0.7)
            self.ax.add_patch(bar)
            self.bars.append(bar)
    
    def _setup_wave_animation(self):
        """Setup wave animation."""
        self.line, = self.ax.plot([], [], 'cyan', linewidth=2)
        self.ax.set_xlim(0, 1)
        self.ax.set_ylim(-0.5, 0.5)
    
    def _setup_circular_animation(self):
        """Setup circular animation."""
        self.circles = []
        center_x, center_y = 0.5, 0.5
        
        for i in range(8):
            angle = i * 2 * np.pi / 8
            radius = 0.3
            x = center_x + radius * np.cos(angle)
            y = center_y + radius * np.sin(angle)
            
            circle = Circle((x, y), 0.05, facecolor='cyan', alpha=0.7)
            self.ax.add_patch(circle)
            self.circles.append(circle)
    
    def _setup_spectrum_animation(self):
        """Setup spectrum analyzer animation."""
        self.spectrum_bars = []
        bar_width = 1.0 / 64
        
        for i in range(64):
            bar = Rectangle((i * bar_width, 0), bar_width * 0.9, 0.1, 
                          facecolor='magenta', alpha=0.7)
            self.ax.add_patch(bar)
            self.spectrum_bars.append(bar)
    
    def _update_animation(self, frame):
        """Update animation frame."""
        try:
            if not self.audio_queue.empty():
                audio_data = self.audio_queue.get_nowait()
                amplitude = np.mean(np.abs(audio_data))
                
                if self.style == "bars":
                    self._update_bars(amplitude)
                elif self.style == "wave":
                    self._update_wave(audio_data)
                elif self.style == "circular":
                    self._update_circular(amplitude)
                elif self.style == "spectrum":
                    self._update_spectrum(audio_data)
                    
        except queue.Empty:
            pass
        
        return []
    
    def _update_bars(self, amplitude):
        """Update bar chart animation."""
        for i, bar in enumerate(self.bars):
            height = amplitude * np.sin(i * 0.2 + time.time()) * 0.5 + 0.1
            bar.set_height(max(0.01, height))
            bar.set_facecolor(self.colors['bars'](i / len(self.bars)))
    
    def _update_wave(self, audio_data):
        """Update wave animation."""
        x = np.linspace(0, 1, len(audio_data))
        y = audio_data * 0.3
        self.line.set_data(x, y)
    
    def _update_circular(self, amplitude):
        """Update circular animation."""
        for i, circle in enumerate(self.circles):
            scale = amplitude * np.sin(i * 0.5 + time.time()) + 0.5
            circle.set_radius(0.02 + scale * 0.08)
            circle.set_facecolor(self.colors['circular'](i / len(self.circles)))
    
    def _update_spectrum(self, audio_data):
        """Update spectrum analyzer animation."""
        # Simulate FFT-like data
        spectrum = np.abs(np.fft.fft(audio_data))[:64]
        spectrum = spectrum / np.max(spectrum) if np.max(spectrum) > 0 else spectrum
        
        for i, bar in enumerate(self.spectrum_bars):
            height = spectrum[i] * 0.8 + 0.1
            bar.set_height(height)
            bar.set_facecolor(self.colors['spectrum'](i / len(self.spectrum_bars)))
    
    def stop(self):
        """Stop the visualization."""
        self.is_running = False
        if self.thread:
            self.thread.join()
        plt.close('all')
    
    def change_style(self, style: str):
        """Change animation style."""
        self.style = style
        if self.fig:
            plt.close(self.fig)
        self._setup_animation()


class AudioVisualizerDemo:
    """Demo class to showcase different animation styles."""
    
    @staticmethod
    def run_demo():
        """Run a demo of all animation styles."""
        styles = ['bars', 'wave', 'circular', 'spectrum']
        
        for style in styles:
            print(f"Running {style} animation...")
            visualizer = AudioVisualizer(style)
            
            def demo_callback():
                return np.random.rand(1024) * 0.5
            
            try:
                visualizer.start_visualization(demo_callback)
                time.sleep(5)  # Show each style for 5 seconds
            except KeyboardInterrupt:
                pass
            finally:
                visualizer.stop()


if __name__ == "__main__":
    # Run demo
    AudioVisualizerDemo.run_demo() 