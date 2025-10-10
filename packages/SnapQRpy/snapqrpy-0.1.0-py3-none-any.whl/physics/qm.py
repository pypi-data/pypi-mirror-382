import numpy as np
import math
from scipy.linalg import eigh
from typing import Tuple, List

class QuantumMechanicsEngine:
    def __init__(self):
        self.hbar = 1.054571817e-34
        self.electron_mass = 9.10938356e-31
        self.planck = 6.62607015e-34
        
    def schrodinger_evolve(self, psi: np.ndarray, hamiltonian: np.ndarray, dt: float) -> np.ndarray:
        evolution_operator = np.exp(-1j * hamiltonian * dt / self.hbar)
        return evolution_operator @ psi
    
    def probability_density(self, psi: np.ndarray) -> np.ndarray:
        return np.abs(psi) ** 2
    
    def expectation_value(self, psi: np.ndarray, operator: np.ndarray) -> complex:
        return np.vdot(psi, operator @ psi)
    
    def uncertainty(self, psi: np.ndarray, operator: np.ndarray) -> float:
        avg = self.expectation_value(psi, operator)
        avg_sq = self.expectation_value(psi, operator @ operator)
        return math.sqrt(abs(avg_sq - avg**2))
    
    def heisenberg_uncertainty(self, delta_x: float, delta_p: float) -> bool:
        return delta_x * delta_p >= self.hbar / 2
    
    def particle_in_box(self, n: int, L: float, x: float) -> float:
        return math.sqrt(2/L) * math.sin(n * math.pi * x / L)
    
    def energy_levels_box(self, n: int, L: float, mass: float) -> float:
        return (n**2 * math.pi**2 * self.hbar**2) / (2 * mass * L**2)
    
    def harmonic_oscillator_wavefunction(self, n: int, x: float, omega: float, mass: float) -> float:
        alpha = mass * omega / self.hbar
        hermite = self._hermite_polynomial(n, math.sqrt(alpha) * x)
        normalization = math.sqrt(math.sqrt(alpha / math.pi) / (2**n * math.factorial(n)))
        
        return normalization * hermite * math.exp(-alpha * x**2 / 2)
    
    def _hermite_polynomial(self, n: int, x: float) -> float:
        if n == 0:
            return 1
        elif n == 1:
            return 2 * x
        else:
            return 2 * x * self._hermite_polynomial(n-1, x) - 2 * (n-1) * self._hermite_polynomial(n-2, x)
    
    def hydrogen_wavefunction(self, n: int, l: int, m: int, r: float, theta: float, phi: float) -> complex:
        a0 = 5.29177210903e-11
        rho = 2 * r / (n * a0)
        
        radial = self._laguerre_polynomial(n-l-1, 2*l+1, rho) * math.exp(-rho/2) * rho**l
        angular = self._spherical_harmonic(l, m, theta, phi)
        
        return radial * angular
    
    def _laguerre_polynomial(self, n: int, alpha: int, x: float) -> float:
        if n == 0:
            return 1
        elif n == 1:
            return 1 + alpha - x
        else:
            return ((2*n + alpha - 1 - x) * self._laguerre_polynomial(n-1, alpha, x) - 
                    (n + alpha - 1) * self._laguerre_polynomial(n-2, alpha, x)) / n
    
    def _spherical_harmonic(self, l: int, m: int, theta: float, phi: float) -> complex:
        return 1.0
    
    def tunneling_probability(self, E: float, V0: float, L: float, mass: float) -> float:
        if E >= V0:
            return 1.0
        
        kappa = math.sqrt(2 * mass * (V0 - E)) / self.hbar
        return math.exp(-2 * kappa * L)
    
    def spin_matrices(self) -> Tuple[np.ndarray, np.ndarray, np.ndarray]:
        sigma_x = np.array([[0, 1], [1, 0]]) * self.hbar / 2
        sigma_y = np.array([[0, -1j], [1j, 0]]) * self.hbar / 2
        sigma_z = np.array([[1, 0], [0, -1]]) * self.hbar / 2
        
        return sigma_x, sigma_y, sigma_z
    
    def entanglement_entropy(self, rho: np.ndarray) -> float:
        eigenvalues = np.linalg.eigvalsh(rho)
        eigenvalues = eigenvalues[eigenvalues > 1e-10]
        
        return -np.sum(eigenvalues * np.log2(eigenvalues))
    
    def bell_state(self, state_type: int = 0) -> np.ndarray:
        bell_states = [
            np.array([1, 0, 0, 1]) / math.sqrt(2),
            np.array([1, 0, 0, -1]) / math.sqrt(2),
            np.array([0, 1, 1, 0]) / math.sqrt(2),
            np.array([0, 1, -1, 0]) / math.sqrt(2),
        ]
        return bell_states[state_type]
    
    def quantum_fourier_transform(self, state: np.ndarray) -> np.ndarray:
        n = len(state)
        omega = np.exp(2j * math.pi / n)
        
        qft_matrix = np.array([[omega**(i*j) for j in range(n)] for i in range(n)]) / math.sqrt(n)
        
        return qft_matrix @ state
