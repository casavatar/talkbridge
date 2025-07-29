#----------------------------------------------------------------------------------------------------------------------------
# description: Loading Animation Module
#----------------------------------------------------------------------------------------------------------------------------
# 
# author: ingekastel
# date: 2025-06-02
# version: 1.0
# 
# requirements:
# - time Python package 
# - threading Python package
# - sys Python package
# - os Python package
# - typing Python package
# - math Python package
#----------------------------------------------------------------------------------------------------------------------------
# functions:    
# - LoadingAnimation: Base class for loading animations
# - SpinnerAnimation: Spinning loading animation
# - ProgressBar: Progress bar animation
# - PulseAnimation: Pulsing loading animation
# - WaveAnimation: Wave-like loading animation
# - LoadingManager: Manager for multiple loading animations
# - LoadingDemo: Demo class to showcase different loading animations        
#----------------------------------------------------------------------------------------------------------------------------

import time
import threading
import sys
import os
from typing import Optional, Callable, List
import math


class LoadingAnimation:
    """
    Base class for loading animations.
    """
    
    def __init__(self, message: str = "Loading...", speed: float = 0.1):
        """
        Initialize loading animation.
        
        Args:
            message: Message to display
            speed: Animation speed in seconds
        """
        self.message = message
        self.speed = speed
        self.is_running = False
        self.thread = None
    
    def start(self):
        """Start the loading animation."""
        self.is_running = True
        self.thread = threading.Thread(target=self._animate)
        self.thread.daemon = True
        self.thread.start()
    
    def stop(self):
        """Stop the loading animation."""
        self.is_running = False
        if self.thread:
            self.thread.join()
        print()  # New line after animation
    
    def _animate(self):
        """Override this method in subclasses."""
        pass


class SpinnerAnimation(LoadingAnimation):
    """Spinning loading animation."""
    
    def __init__(self, message: str = "Loading...", style: str = "dots"):
        super().__init__(message)
        self.style = style
        self.frame = 0
        
        # Different spinner styles
        self.spinners = {
            'dots': ['⠋', '⠙', '⠹', '⠸', '⠼', '⠴', '⠦', '⠧', '⠇', '⠏'],
            'arrows': ['←', '↖', '↑', '↗', '→', '↘', '↓', '↙'],
            'bars': ['▌', '▀', '▐', '▄'],
            'dots2': ['⣾', '⣽', '⣻', '⢿', '⡿', '⣟', '⣯', '⣷'],
            'dots3': ['⠋', '⠙', '⠹', '⠸', '⠼', '⠴', '⠦', '⠧', '⠇', '⠏'],
            'dots4': ['⠋', '⠙', '⠹', '⠸', '⠼', '⠴', '⠦', '⠧', '⠇', '⠏'],
            'dots5': ['⠋', '⠙', '⠹', '⠸', '⠼', '⠴', '⠦', '⠧', '⠇', '⠏'],
            'dots6': ['⠋', '⠙', '⠹', '⠸', '⠼', '⠴', '⠦', '⠧', '⠇', '⠏'],
            'dots7': ['⠋', '⠙', '⠹', '⠸', '⠼', '⠴', '⠦', '⠧', '⠇', '⠏'],
            'dots8': ['⠋', '⠙', '⠹', '⠸', '⠼', '⠴', '⠦', '⠧', '⠇', '⠏'],
            'dots9': ['⠋', '⠙', '⠹', '⠸', '⠼', '⠴', '⠦', '⠧', '⠇', '⠏'],
            'dots10': ['⠋', '⠙', '⠹', '⠸', '⠼', '⠴', '⠦', '⠧', '⠇', '⠏'],
            'dots11': ['⠋', '⠙', '⠹', '⠸', '⠼', '⠴', '⠦', '⠧', '⠇', '⠏'],
            'dots12': ['⠋', '⠙', '⠹', '⠸', '⠼', '⠴', '⠦', '⠧', '⠇', '⠏'],
        }
    
    def _animate(self):
        """Animate the spinner."""
        spinner = self.spinners.get(self.style, self.spinners['dots'])
        
        while self.is_running:
            spinner_char = spinner[self.frame % len(spinner)]
            print(f"\r{spinner_char} {self.message}", end='', flush=True)
            time.sleep(self.speed)
            self.frame += 1


class ProgressBar(LoadingAnimation):
    """Progress bar animation."""
    
    def __init__(self, total: int = 100, width: int = 50, message: str = "Progress"):
        super().__init__(message)
        self.total = total
        self.width = width
        self.current = 0
        self.start_time = None
    
    def update(self, value: int):
        """Update progress value."""
        self.current = min(value, self.total)
    
    def _animate(self):
        """Animate the progress bar."""
        self.start_time = time.time()
        
        while self.is_running and self.current < self.total:
            percentage = self.current / self.total
            filled_width = int(self.width * percentage)
            bar = '█' * filled_width + '░' * (self.width - filled_width)
            
            elapsed = time.time() - self.start_time
            eta = (elapsed / max(percentage, 0.001)) * (1 - percentage) if percentage > 0 else 0
            
            print(f"\r{self.message}: [{bar}] {percentage:.1%} | ETA: {eta:.1f}s", 
                  end='', flush=True)
            time.sleep(self.speed)
        
        if self.current >= self.total:
            print(f"\r{self.message}: [{'█' * self.width}] 100% | Complete!", flush=True)


class PulseAnimation(LoadingAnimation):
    """Pulsing loading animation."""
    
    def __init__(self, message: str = "Processing...", pulse_chars: str = "●○"):
        super().__init__(message)
        self.pulse_chars = pulse_chars
        self.frame = 0
    
    def _animate(self):
        """Animate the pulse."""
        while self.is_running:
            pulse_char = self.pulse_chars[self.frame % len(self.pulse_chars)]
            print(f"\r{pulse_char} {self.message}", end='', flush=True)
            time.sleep(self.speed)
            self.frame += 1


class WaveAnimation(LoadingAnimation):
    """Wave-like loading animation."""
    
    def __init__(self, message: str = "Loading...", wave_chars: str = "▁▂▃▄▅▆▇█"):
        super().__init__(message)
        self.wave_chars = wave_chars
        self.frame = 0
    
    def _animate(self):
        """Animate the wave."""
        while self.is_running:
            wave = ""
            for i in range(10):
                char_idx = (self.frame + i) % len(self.wave_chars)
                wave += self.wave_chars[char_idx]
            
            print(f"\r{wave} {self.message}", end='', flush=True)
            time.sleep(self.speed)
            self.frame += 1


class LoadingManager:
    """Manager for multiple loading animations."""
    
    def __init__(self):
        self.animations = []
    
    def add_animation(self, animation: LoadingAnimation):
        """Add an animation to the manager."""
        self.animations.append(animation)
    
    def start_all(self):
        """Start all animations."""
        for animation in self.animations:
            animation.start()
    
    def stop_all(self):
        """Stop all animations."""
        for animation in self.animations:
            animation.stop()
    
    def clear(self):
        """Clear all animations."""
        self.stop_all()
        self.animations.clear()


class LoadingDemo:
    """Demo class to showcase different loading animations."""
    
    @staticmethod
    def run_spinner_demo():
        """Demo spinner animations."""
        print("Spinner Animation Demo:")
        print("=" * 30)
        
        styles = ['dots', 'arrows', 'bars', 'dots2']
        
        for style in styles:
            print(f"\n{style.upper()} style:")
            spinner = SpinnerAnimation(f"Loading with {style} style...", style)
            spinner.start()
            time.sleep(2)
            spinner.stop()
    
    @staticmethod
    def run_progress_demo():
        """Demo progress bar."""
        print("\nProgress Bar Demo:")
        print("=" * 30)
        
        progress = ProgressBar(100, 40, "Processing files")
        progress.start()
        
        for i in range(0, 101, 5):
            progress.update(i)
            time.sleep(0.1)
        
        progress.stop()
    
    @staticmethod
    def run_pulse_demo():
        """Demo pulse animation."""
        print("\nPulse Animation Demo:")
        print("=" * 30)
        
        pulse = PulseAnimation("Processing data...")
        pulse.start()
        time.sleep(3)
        pulse.stop()
    
    @staticmethod
    def run_wave_demo():
        """Demo wave animation."""
        print("\nWave Animation Demo:")
        print("=" * 30)
        
        wave = WaveAnimation("Loading modules...")
        wave.start()
        time.sleep(3)
        wave.stop()
    
    @staticmethod
    def run_all_demos():
        """Run all loading animation demos."""
        LoadingDemo.run_spinner_demo()
        LoadingDemo.run_progress_demo()
        LoadingDemo.run_pulse_demo()
        LoadingDemo.run_wave_demo()


if __name__ == "__main__":
    # Run demo
    LoadingDemo.run_all_demos() 