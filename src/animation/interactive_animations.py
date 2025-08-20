#!/usr/bin/env python3
"""
TalkBridge Animation - Interactive Animations
=============================================

Módulo interactive_animations para TalkBridge

Author: TalkBridge Team
Date: 2025-08-19
Version: 1.0

Requirements:
- mediapipe
- opencv-python
======================================================================
Functions:
- __init__: Initialize particle system.
- _initialize_particles: Initialize particle positions and velocities.
- start: Start the particle system animation.
- _setup_animation: Setup matplotlib animation.
- _update_particles: Update particle positions and velocities.
- stop: Stop the particle system.
- __init__: Initialize geometric animation.
- start: Start the geometric animation.
- _setup_animation: Setup matplotlib animation.
- _update_animation: Update the geometric animation.
======================================================================
"""

import numpy as np
import matplotlib.pyplot as plt
import matplotlib.animation as animation
from matplotlib.patches import Circle, Rectangle, Polygon
import threading
import time
from typing import List, Tuple, Optional, Callable
import math
import random


class ParticleSystem:
    """Particle system animation."""
    
    def __init__(self, num_particles: int = 100, bounds: Tuple[float, float, float, float] = (-1, 1, -1, 1)):
        """
        Initialize particle system.
        
        Args:
            num_particles: Number of particles
            bounds: (x_min, x_max, y_min, y_max) bounds for particles
        """
        self.num_particles = num_particles
        self.bounds = bounds
        self.particles = []
        self.fig = None
        self.ax = None
        self.is_running = False
        
        self._initialize_particles()
    
    def _initialize_particles(self):
        """Initialize particle positions and velocities."""
        x_min, x_max, y_min, y_max = self.bounds
        
        for _ in range(self.num_particles):
            particle = {
                'x': random.uniform(x_min, x_max),
                'y': random.uniform(y_min, y_max),
                'vx': random.uniform(-0.1, 0.1),
                'vy': random.uniform(-0.1, 0.1),
                'size': random.uniform(0.01, 0.05),
                'color': random.random()
            }
            self.particles.append(particle)
    
    def start(self):
        """Start the particle system animation."""
        self.is_running = True
        self._setup_animation()
        plt.show()
    
    def _setup_animation(self):
        """Setup matplotlib animation."""
        plt.ion()
        self.fig, self.ax = plt.subplots(figsize=(10, 8))
        self.ax.set_xlim(self.bounds[0], self.bounds[1])
        self.ax.set_ylim(self.bounds[2], self.bounds[3])
        self.ax.set_aspect('equal')
        self.ax.set_facecolor('black')
        self.fig.patch.set_facecolor('black')
        
        # Create particle circles
        self.particle_circles = []
        for particle in self.particles:
            circle = Circle((particle['x'], particle['y']), particle['size'], 
                          facecolor=plt.cm.viridis(particle['color']), alpha=0.7)
            self.ax.add_patch(circle)
            self.particle_circles.append(circle)
    
    def _update_particles(self):
        """Update particle positions and velocities."""
        x_min, x_max, y_min, y_max = self.bounds
        
        for i, particle in enumerate(self.particles):
            # Update position
            particle['x'] += particle['vx']
            particle['y'] += particle['vy']
            
            # Bounce off boundaries
            if particle['x'] <= x_min or particle['x'] >= x_max:
                particle['vx'] *= -1
            if particle['y'] <= y_min or particle['y'] >= y_max:
                particle['vy'] *= -1
            
            # Keep particles in bounds
            particle['x'] = max(x_min, min(x_max, particle['x']))
            particle['y'] = max(y_min, min(y_max, particle['y']))
            
            # Update circle position
            self.particle_circles[i].center = (particle['x'], particle['y'])
    
    def stop(self):
        """Stop the particle system."""
        self.is_running = False
        plt.close('all')


class GeometricAnimation:
    """Geometric shape animations."""
    
    def __init__(self, shape: str = "circle"):
        """
        Initialize geometric animation.
        
        Args:
            shape: Shape type ('circle', 'square', 'triangle', 'polygon')
        """
        self.shape = shape
        self.fig = None
        self.ax = None
        self.is_running = False
        self.angle = 0
        self.scale = 1.0
        
    def start(self):
        """Start the geometric animation."""
        self.is_running = True
        self._setup_animation()
        plt.show()
    
    def _setup_animation(self):
        """Setup matplotlib animation."""
        plt.ion()
        self.fig, self.ax = plt.subplots(figsize=(8, 8))
        self.ax.set_xlim(-2, 2)
        self.ax.set_ylim(-2, 2)
        self.ax.set_aspect('equal')
        self.ax.set_facecolor('black')
        self.fig.patch.set_facecolor('black')
        self.ax.axis('off')
        
        if self.shape == "circle":
            self.shape_patch = Circle((0, 0), 0.5, facecolor='cyan', alpha=0.7)
        elif self.shape == "square":
            self.shape_patch = Rectangle((-0.5, -0.5), 1, 1, facecolor='magenta', alpha=0.7)
        elif self.shape == "triangle":
            triangle_points = np.array([[-0.5, -0.3], [0.5, -0.3], [0, 0.5]])
            self.shape_patch = Polygon(triangle_points, facecolor='yellow', alpha=0.7)
        elif self.shape == "polygon":
            # Create a star-like polygon
            angles = np.linspace(0, 2*np.pi, 10, endpoint=False)
            outer_radius = 0.5
            inner_radius = 0.2
            points = []
            for i, angle in enumerate(angles):
                radius = outer_radius if i % 2 == 0 else inner_radius
                x = radius * np.cos(angle)
                y = radius * np.sin(angle)
                points.append([x, y])
            self.shape_patch = Polygon(points, facecolor='green', alpha=0.7)
        
        self.ax.add_patch(self.shape_patch)
    
    def _update_animation(self):
        """Update the geometric animation."""
        if not self.is_running:
            return
        
        # Rotate and scale
        self.angle += 0.05
        self.scale = 0.8 + 0.2 * np.sin(self.angle * 2)
        
        # Apply transformations
        if self.shape == "circle":
            self.shape_patch.center = (0.5 * np.sin(self.angle), 0.3 * np.cos(self.angle))
            self.shape_patch.radius = 0.5 * self.scale
        elif self.shape == "square":
            self.shape_patch.set_xy((-0.5 * self.scale, -0.5 * self.scale))
            self.shape_patch.set_width(self.scale)
            self.shape_patch.set_height(self.scale)
        elif self.shape == "triangle":
            # Rotate triangle points
            center = np.array([0, 0])
            points = np.array([[-0.5, -0.3], [0.5, -0.3], [0, 0.5]])
            rotated_points = []
            for point in points:
                # Rotate around center
                cos_a, sin_a = np.cos(self.angle), np.sin(self.angle)
                x = point[0] * cos_a - point[1] * sin_a
                y = point[0] * sin_a + point[1] * cos_a
                rotated_points.append([x * self.scale, y * self.scale])
            self.shape_patch.set_xy(rotated_points)
        elif self.shape == "polygon":
            # Similar rotation for polygon
            angles = np.linspace(0, 2*np.pi, 10, endpoint=False)
            outer_radius = 0.5 * self.scale
            inner_radius = 0.2 * self.scale
            points = []
            for i, angle in enumerate(angles):
                radius = outer_radius if i % 2 == 0 else inner_radius
                x = radius * np.cos(angle + self.angle)
                y = radius * np.sin(angle + self.angle)
                points.append([x, y])
            self.shape_patch.set_xy(points)
        
        plt.pause(0.01)
    
    def stop(self):
        """Stop the geometric animation."""
        self.is_running = False
        plt.close('all')


class WaveformAnimation:
    """Waveform animation with interactive controls."""
    
    def __init__(self, frequency: float = 1.0, amplitude: float = 1.0):
        """
        Initialize waveform animation.
        
        Args:
            frequency: Wave frequency
            amplitude: Wave amplitude
        """
        self.frequency = frequency
        self.amplitude = amplitude
        self.fig = None
        self.ax = None
        self.is_running = False
        self.time = 0
        
    def start(self):
        """Start the waveform animation."""
        self.is_running = True
        self._setup_animation()
        plt.show()
    
    def _setup_animation(self):
        """Setup matplotlib animation."""
        plt.ion()
        self.fig, self.ax = plt.subplots(figsize=(12, 6))
        self.ax.set_xlim(0, 4*np.pi)
        self.ax.set_ylim(-1.5, 1.5)
        self.ax.set_facecolor('black')
        self.fig.patch.set_facecolor('black')
        self.ax.grid(True, alpha=0.3)
        
        # Create multiple wave lines
        self.wave_lines = []
        colors = ['cyan', 'magenta', 'yellow', 'green']
        
        for i, color in enumerate(colors):
            line, = self.ax.plot([], [], color=color, linewidth=2, alpha=0.7)
            self.wave_lines.append(line)
    
    def _update_animation(self):
        """Update the waveform animation."""
        if not self.is_running:
            return
        
        x = np.linspace(0, 4*np.pi, 200)
        
        # Generate different wave types
        waves = [
            self.amplitude * np.sin(self.frequency * x + self.time),  # Sine
            self.amplitude * np.cos(self.frequency * x + self.time),  # Cosine
            self.amplitude * np.sin(2 * self.frequency * x + self.time),  # Double frequency
            self.amplitude * 0.5 * (np.sin(self.frequency * x + self.time) + 
                                   np.sin(2 * self.frequency * x + self.time))  # Combined
        ]
        
        for i, (line, wave) in enumerate(zip(self.wave_lines, waves)):
            line.set_data(x, wave)
        
        self.time += 0.1
        plt.pause(0.01)
    
    def stop(self):
        """Stop the waveform animation."""
        self.is_running = False
        plt.close('all')


class InteractiveAnimations:
    """Main class for managing interactive animations."""
    
    def __init__(self):
        self.animations = {}
        self.is_running = False
    
    def create_particle_system(self, name: str, num_particles: int = 100):
        """Create a particle system animation."""
        animation = ParticleSystem(num_particles)
        self.animations[name] = animation
        return animation
    
    def create_geometric_animation(self, name: str, shape: str = "circle"):
        """Create a geometric animation."""
        animation = GeometricAnimation(shape)
        self.animations[name] = animation
        return animation
    
    def create_waveform_animation(self, name: str, frequency: float = 1.0, amplitude: float = 1.0):
        """Create a waveform animation."""
        animation = WaveformAnimation(frequency, amplitude)
        self.animations[name] = animation
        return animation
    
    def start_animation(self, name: str):
        """Start a specific animation."""
        if name in self.animations:
            self.animations[name].start()
    
    def stop_animation(self, name: str):
        """Stop a specific animation."""
        if name in self.animations:
            self.animations[name].stop()
    
    def stop_all(self):
        """Stop all animations."""
        for animation in self.animations.values():
            animation.stop()
        self.animations.clear()
    
    def list_animations(self):
        """List all available animations."""
        return list(self.animations.keys())


class AnimationDemo:
    """Demo class for interactive animations."""
    
    @staticmethod
    def run_particle_demo():
        """Run particle system demo."""
        print("Particle System Demo")
        print("=" * 30)
        
        particles = ParticleSystem(50)
        try:
            particles.start()
            time.sleep(5)
        except KeyboardInterrupt:
            pass
        finally:
            particles.stop()
    
    @staticmethod
    def run_geometric_demo():
        """Run geometric animation demo."""
        print("Geometric Animation Demo")
        print("=" * 30)
        
        shapes = ['circle', 'square', 'triangle', 'polygon']
        
        for shape in shapes:
            print(f"Running {shape} animation...")
            geo_anim = GeometricAnimation(shape)
            try:
                geo_anim.start()
                time.sleep(3)
            except KeyboardInterrupt:
                pass
            finally:
                geo_anim.stop()
    
    @staticmethod
    def run_waveform_demo():
        """Run waveform animation demo."""
        print("Waveform Animation Demo")
        print("=" * 30)
        
        wave_anim = WaveformAnimation(frequency=2.0, amplitude=1.0)
        try:
            wave_anim.start()
            time.sleep(5)
        except KeyboardInterrupt:
            pass
        finally:
            wave_anim.stop()
    
    @staticmethod
    def run_interactive_demo():
        """Run interactive animations demo."""
        print("Interactive Animations Demo")
        print("=" * 30)
        
        manager = InteractiveAnimations()
        
        # Create different animations
        manager.create_particle_system("particles", 30)
        manager.create_geometric_animation("circle", "circle")
        manager.create_waveform_animation("waves", 1.5, 0.8)
        
        print("Available animations:", manager.list_animations())
        
        # Start all animations
        for name in manager.list_animations():
            print(f"Starting {name}...")
            manager.start_animation(name)
            time.sleep(2)
        
        time.sleep(3)
        manager.stop_all()


if __name__ == "__main__":
    # Run demos
    AnimationDemo.run_particle_demo()
    AnimationDemo.run_geometric_demo()
    AnimationDemo.run_waveform_demo()
    AnimationDemo.run_interactive_demo() 