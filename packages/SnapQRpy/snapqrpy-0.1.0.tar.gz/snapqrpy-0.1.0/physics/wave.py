import numpy as np
import math
from scipy import signal
from typing import Tuple, List

class WavePhysicsEngine:
    def __init__(self, grid_size: int = 512):
        self.grid_size = grid_size
        self.grid = np.zeros((grid_size, grid_size))
        self.velocity = np.zeros((grid_size, grid_size))
        self.damping = 0.99
        self.wave_speed = 0.5
        
    def propagate_wave(self, dt: float = 0.01):
        laplacian = self._compute_laplacian(self.grid)
        self.velocity += laplacian * self.wave_speed * dt
        self.velocity *= self.damping
        self.grid += self.velocity * dt
        
    def _compute_laplacian(self, field: np.ndarray) -> np.ndarray:
        kernel = np.array([[0, 1, 0], [1, -4, 1], [0, 1, 0]])
        return signal.convolve2d(field, kernel, mode='same', boundary='wrap')
    
    def add_wave_source(self, x: int, y: int, amplitude: float, frequency: float, time: float):
        self.grid[y, x] += amplitude * math.sin(2 * math.pi * frequency * time)
    
    def interference_pattern(self, source1: Tuple[int, int], source2: Tuple[int, int], wavelength: float) -> np.ndarray:
        pattern = np.zeros((self.grid_size, self.grid_size))
        
        for y in range(self.grid_size):
            for x in range(self.grid_size):
                d1 = math.sqrt((x - source1[0])**2 + (y - source1[1])**2)
                d2 = math.sqrt((x - source2[0])**2 + (y - source2[1])**2)
                
                phase_diff = 2 * math.pi * (d2 - d1) / wavelength
                pattern[y, x] = 2 * math.cos(phase_diff / 2)
        
        return pattern
    
    def diffraction_pattern(self, slit_width: float, distance: float, wavelength: float) -> np.ndarray:
        pattern = np.zeros(self.grid_size)
        
        for i in range(self.grid_size):
            theta = (i - self.grid_size / 2) / distance
            beta = math.pi * slit_width * math.sin(theta) / wavelength
            
            if beta != 0:
                pattern[i] = (math.sin(beta) / beta) ** 2
            else:
                pattern[i] = 1.0
        
        return pattern
    
    def doppler_shift(self, source_velocity: float, observer_velocity: float, frequency: float, sound_speed: float = 343.0) -> float:
        return frequency * (sound_speed + observer_velocity) / (sound_speed - source_velocity)
    
    def standing_wave(self, length: float, mode: int, time: float) -> np.ndarray:
        x = np.linspace(0, length, self.grid_size)
        k = mode * math.pi / length
        omega = k * self.wave_speed
        
        return np.sin(k * x) * np.cos(omega * time)
    
    def fourier_decomposition(self, signal_data: np.ndarray) -> Tuple[np.ndarray, np.ndarray]:
        fft = np.fft.fft(signal_data)
        frequencies = np.fft.fftfreq(len(signal_data))
        amplitudes = np.abs(fft)
        
        return frequencies, amplitudes
    
    def dispersion_relation(self, k: float, medium_type: str = 'deep_water') -> float:
        g = 9.81
        
        if medium_type == 'deep_water':
            return math.sqrt(g * k)
        elif medium_type == 'shallow_water':
            h = 1.0
            return k * math.sqrt(g * h)
        else:
            return k * self.wave_speed
    
    def group_velocity(self, k: float) -> float:
        dk = 0.001
        omega1 = self.dispersion_relation(k - dk)
        omega2 = self.dispersion_relation(k + dk)
        
        return (omega2 - omega1) / (2 * dk)
    
    def calculate_energy_flux(self, amplitude: float, frequency: float, density: float = 1.0) -> float:
        omega = 2 * math.pi * frequency
        return 0.5 * density * self.wave_speed * omega**2 * amplitude**2
    
    def refraction_angle(self, incident_angle: float, v1: float, v2: float) -> float:
        return math.asin((v2 / v1) * math.sin(incident_angle))
    
    def critical_angle(self, v1: float, v2: float) -> float:
        if v1 <= v2:
            return math.pi / 2
        return math.asin(v2 / v1)
    
    def waveguide_modes(self, width: float, wavelength: float, mode_number: int) -> float:
        return math.sqrt((2 * math.pi / wavelength)**2 - (mode_number * math.pi / width)**2)
    
    def acoustic_impedance(self, density: float, sound_speed: float) -> float:
        return density * sound_speed
    
    def reflection_coefficient(self, Z1: float, Z2: float) -> float:
        return (Z2 - Z1) / (Z2 + Z1)
    
    def transmission_coefficient(self, Z1: float, Z2: float) -> float:
        return 2 * Z2 / (Z2 + Z1)
