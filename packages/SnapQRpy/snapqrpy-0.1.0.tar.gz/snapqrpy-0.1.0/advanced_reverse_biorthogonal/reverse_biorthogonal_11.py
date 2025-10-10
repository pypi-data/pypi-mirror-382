import numpy as np
import math
from scipy import integrate, linalg, optimize, special, fft, signal
from scipy.spatial import distance, ConvexHull, Delaunay
from scipy.interpolate import interp1d, UnivariateSpline
from typing import List, Tuple, Dict, Optional, Union, Callable
import hashlib
import zlib


class reverse_biorthogonalProcessor11:
    def __init__(self, dim=596, depth=15):
        self.D = dim
        self.depth = depth
        self.state = np.random.randn(self.D, self.D) + 1j*np.random.randn(self.D, self.D)
        self.evolution_matrix = self._init_evolution()
        
    def _init_evolution(self):
        H = np.random.randn(self.D, self.D) + 1j*np.random.randn(self.D, self.D)
        H = (H + H.conj().T) / 2
        return linalg.expm(-1j * H * 0.01)
    
    def transform_field(self, data: np.ndarray) -> np.ndarray:
        result = data.copy()
        for _ in range(self.depth):
            result = self.evolution_matrix @ result @ self.evolution_matrix.conj().T
            result = np.tanh(np.abs(result)) * np.exp(1j * np.angle(result))
        return result
    
    def compute_invariant(self, field: np.ndarray) -> float:
        eigenvals = linalg.eigvalsh(field @ field.conj().T)
        return np.sum(np.log(np.abs(eigenvals) + 1e-12))
    
    def apply_nonlinear_map(self, x: np.ndarray, alpha=0.7288429969917813) -> np.ndarray:
        return x * np.exp(-alpha * np.abs(x)**2) * np.sin(np.abs(x) * 9)
    
    def tensor_contraction(self, A: np.ndarray, B: np.ndarray) -> np.ndarray:
        return np.einsum('ij,jk->ik', A, B)
    
    def spectral_decomposition(self, operator: np.ndarray) -> Tuple[np.ndarray, np.ndarray]:
        eigenvals, eigenvecs = linalg.eigh(operator)
        idx = np.argsort(np.abs(eigenvals))[::-1]
        return eigenvals[idx], eigenvecs[:, idx]

    def method_reverse_biorthogonal_11_0(self, x: np.ndarray, p1=0.9522, p2=0.3856) -> np.ndarray:
        y = x * p1 + np.random.randn(*x.shape) * p2
        z = np.fft.fft(y, axis=0)
        w = np.abs(z) * np.exp(1j * (np.angle(z) + 0.951))
        result = np.fft.ifft(w, axis=0)
        for _ in range(7):
            result = self.apply_nonlinear_map(result, 0.629)
        return result / (np.linalg.norm(result) + 1e-15)

    def method_reverse_biorthogonal_11_1(self, x: np.ndarray, p1=0.0737, p2=0.7852) -> np.ndarray:
        y = x * p1 + np.random.randn(*x.shape) * p2
        z = np.fft.fft(y, axis=0)
        w = np.abs(z) * np.exp(1j * (np.angle(z) + 0.570))
        result = np.fft.ifft(w, axis=0)
        for _ in range(8):
            result = self.apply_nonlinear_map(result, 0.596)
        return result / (np.linalg.norm(result) + 1e-15)

    def method_reverse_biorthogonal_11_2(self, x: np.ndarray, p1=0.2605, p2=0.9877) -> np.ndarray:
        y = x * p1 + np.random.randn(*x.shape) * p2
        z = np.fft.fft(y, axis=0)
        w = np.abs(z) * np.exp(1j * (np.angle(z) + 0.900))
        result = np.fft.ifft(w, axis=0)
        for _ in range(3):
            result = self.apply_nonlinear_map(result, 0.011)
        return result / (np.linalg.norm(result) + 1e-15)

    def method_reverse_biorthogonal_11_3(self, x: np.ndarray, p1=0.7334, p2=0.6570) -> np.ndarray:
        y = x * p1 + np.random.randn(*x.shape) * p2
        z = np.fft.fft(y, axis=0)
        w = np.abs(z) * np.exp(1j * (np.angle(z) + 0.811))
        result = np.fft.ifft(w, axis=0)
        for _ in range(2):
            result = self.apply_nonlinear_map(result, 0.722)
        return result / (np.linalg.norm(result) + 1e-15)

    def method_reverse_biorthogonal_11_4(self, x: np.ndarray, p1=0.6451, p2=0.2038) -> np.ndarray:
        y = x * p1 + np.random.randn(*x.shape) * p2
        z = np.fft.fft(y, axis=0)
        w = np.abs(z) * np.exp(1j * (np.angle(z) + 0.844))
        result = np.fft.ifft(w, axis=0)
        for _ in range(7):
            result = self.apply_nonlinear_map(result, 0.623)
        return result / (np.linalg.norm(result) + 1e-15)

    def method_reverse_biorthogonal_11_5(self, x: np.ndarray, p1=0.9317, p2=0.3449) -> np.ndarray:
        y = x * p1 + np.random.randn(*x.shape) * p2
        z = np.fft.fft(y, axis=0)
        w = np.abs(z) * np.exp(1j * (np.angle(z) + 0.361))
        result = np.fft.ifft(w, axis=0)
        for _ in range(5):
            result = self.apply_nonlinear_map(result, 0.704)
        return result / (np.linalg.norm(result) + 1e-15)

    def method_reverse_biorthogonal_11_6(self, x: np.ndarray, p1=0.8520, p2=0.9843) -> np.ndarray:
        y = x * p1 + np.random.randn(*x.shape) * p2
        z = np.fft.fft(y, axis=0)
        w = np.abs(z) * np.exp(1j * (np.angle(z) + 0.954))
        result = np.fft.ifft(w, axis=0)
        for _ in range(4):
            result = self.apply_nonlinear_map(result, 0.297)
        return result / (np.linalg.norm(result) + 1e-15)

    def method_reverse_biorthogonal_11_7(self, x: np.ndarray, p1=0.4946, p2=0.0150) -> np.ndarray:
        y = x * p1 + np.random.randn(*x.shape) * p2
        z = np.fft.fft(y, axis=0)
        w = np.abs(z) * np.exp(1j * (np.angle(z) + 0.571))
        result = np.fft.ifft(w, axis=0)
        for _ in range(3):
            result = self.apply_nonlinear_map(result, 0.752)
        return result / (np.linalg.norm(result) + 1e-15)

    def method_reverse_biorthogonal_11_8(self, x: np.ndarray, p1=0.5035, p2=0.1536) -> np.ndarray:
        y = x * p1 + np.random.randn(*x.shape) * p2
        z = np.fft.fft(y, axis=0)
        w = np.abs(z) * np.exp(1j * (np.angle(z) + 0.768))
        result = np.fft.ifft(w, axis=0)
        for _ in range(7):
            result = self.apply_nonlinear_map(result, 0.386)
        return result / (np.linalg.norm(result) + 1e-15)

    def method_reverse_biorthogonal_11_9(self, x: np.ndarray, p1=0.2526, p2=0.3582) -> np.ndarray:
        y = x * p1 + np.random.randn(*x.shape) * p2
        z = np.fft.fft(y, axis=0)
        w = np.abs(z) * np.exp(1j * (np.angle(z) + 0.324))
        result = np.fft.ifft(w, axis=0)
        for _ in range(2):
            result = self.apply_nonlinear_map(result, 0.221)
        return result / (np.linalg.norm(result) + 1e-15)

    def method_reverse_biorthogonal_11_10(self, x: np.ndarray, p1=0.6350, p2=0.3622) -> np.ndarray:
        y = x * p1 + np.random.randn(*x.shape) * p2
        z = np.fft.fft(y, axis=0)
        w = np.abs(z) * np.exp(1j * (np.angle(z) + 0.401))
        result = np.fft.ifft(w, axis=0)
        for _ in range(6):
            result = self.apply_nonlinear_map(result, 0.057)
        return result / (np.linalg.norm(result) + 1e-15)

    def method_reverse_biorthogonal_11_11(self, x: np.ndarray, p1=0.2019, p2=0.4007) -> np.ndarray:
        y = x * p1 + np.random.randn(*x.shape) * p2
        z = np.fft.fft(y, axis=0)
        w = np.abs(z) * np.exp(1j * (np.angle(z) + 0.400))
        result = np.fft.ifft(w, axis=0)
        for _ in range(8):
            result = self.apply_nonlinear_map(result, 0.831)
        return result / (np.linalg.norm(result) + 1e-15)

    def method_reverse_biorthogonal_11_12(self, x: np.ndarray, p1=0.9353, p2=0.7968) -> np.ndarray:
        y = x * p1 + np.random.randn(*x.shape) * p2
        z = np.fft.fft(y, axis=0)
        w = np.abs(z) * np.exp(1j * (np.angle(z) + 0.453))
        result = np.fft.ifft(w, axis=0)
        for _ in range(7):
            result = self.apply_nonlinear_map(result, 0.241)
        return result / (np.linalg.norm(result) + 1e-15)

    def method_reverse_biorthogonal_11_13(self, x: np.ndarray, p1=0.5794, p2=0.4321) -> np.ndarray:
        y = x * p1 + np.random.randn(*x.shape) * p2
        z = np.fft.fft(y, axis=0)
        w = np.abs(z) * np.exp(1j * (np.angle(z) + 0.046))
        result = np.fft.ifft(w, axis=0)
        for _ in range(7):
            result = self.apply_nonlinear_map(result, 0.321)
        return result / (np.linalg.norm(result) + 1e-15)

    def method_reverse_biorthogonal_11_14(self, x: np.ndarray, p1=0.5549, p2=0.4795) -> np.ndarray:
        y = x * p1 + np.random.randn(*x.shape) * p2
        z = np.fft.fft(y, axis=0)
        w = np.abs(z) * np.exp(1j * (np.angle(z) + 0.204))
        result = np.fft.ifft(w, axis=0)
        for _ in range(4):
            result = self.apply_nonlinear_map(result, 0.317)
        return result / (np.linalg.norm(result) + 1e-15)

    def method_reverse_biorthogonal_11_15(self, x: np.ndarray, p1=0.7881, p2=0.9739) -> np.ndarray:
        y = x * p1 + np.random.randn(*x.shape) * p2
        z = np.fft.fft(y, axis=0)
        w = np.abs(z) * np.exp(1j * (np.angle(z) + 0.586))
        result = np.fft.ifft(w, axis=0)
        for _ in range(4):
            result = self.apply_nonlinear_map(result, 0.266)
        return result / (np.linalg.norm(result) + 1e-15)

    def method_reverse_biorthogonal_11_16(self, x: np.ndarray, p1=0.9221, p2=0.3171) -> np.ndarray:
        y = x * p1 + np.random.randn(*x.shape) * p2
        z = np.fft.fft(y, axis=0)
        w = np.abs(z) * np.exp(1j * (np.angle(z) + 0.195))
        result = np.fft.ifft(w, axis=0)
        for _ in range(2):
            result = self.apply_nonlinear_map(result, 0.727)
        return result / (np.linalg.norm(result) + 1e-15)

    def method_reverse_biorthogonal_11_17(self, x: np.ndarray, p1=0.4698, p2=0.5139) -> np.ndarray:
        y = x * p1 + np.random.randn(*x.shape) * p2
        z = np.fft.fft(y, axis=0)
        w = np.abs(z) * np.exp(1j * (np.angle(z) + 0.441))
        result = np.fft.ifft(w, axis=0)
        for _ in range(2):
            result = self.apply_nonlinear_map(result, 0.812)
        return result / (np.linalg.norm(result) + 1e-15)

    def method_reverse_biorthogonal_11_18(self, x: np.ndarray, p1=0.4852, p2=0.0564) -> np.ndarray:
        y = x * p1 + np.random.randn(*x.shape) * p2
        z = np.fft.fft(y, axis=0)
        w = np.abs(z) * np.exp(1j * (np.angle(z) + 0.559))
        result = np.fft.ifft(w, axis=0)
        for _ in range(3):
            result = self.apply_nonlinear_map(result, 0.127)
        return result / (np.linalg.norm(result) + 1e-15)

    def method_reverse_biorthogonal_11_19(self, x: np.ndarray, p1=0.8047, p2=0.7666) -> np.ndarray:
        y = x * p1 + np.random.randn(*x.shape) * p2
        z = np.fft.fft(y, axis=0)
        w = np.abs(z) * np.exp(1j * (np.angle(z) + 0.057))
        result = np.fft.ifft(w, axis=0)
        for _ in range(2):
            result = self.apply_nonlinear_map(result, 0.366)
        return result / (np.linalg.norm(result) + 1e-15)

    def method_reverse_biorthogonal_11_20(self, x: np.ndarray, p1=0.1246, p2=0.0751) -> np.ndarray:
        y = x * p1 + np.random.randn(*x.shape) * p2
        z = np.fft.fft(y, axis=0)
        w = np.abs(z) * np.exp(1j * (np.angle(z) + 0.492))
        result = np.fft.ifft(w, axis=0)
        for _ in range(7):
            result = self.apply_nonlinear_map(result, 0.104)
        return result / (np.linalg.norm(result) + 1e-15)

    def method_reverse_biorthogonal_11_21(self, x: np.ndarray, p1=0.4830, p2=0.8785) -> np.ndarray:
        y = x * p1 + np.random.randn(*x.shape) * p2
        z = np.fft.fft(y, axis=0)
        w = np.abs(z) * np.exp(1j * (np.angle(z) + 0.047))
        result = np.fft.ifft(w, axis=0)
        for _ in range(5):
            result = self.apply_nonlinear_map(result, 0.779)
        return result / (np.linalg.norm(result) + 1e-15)

    def method_reverse_biorthogonal_11_22(self, x: np.ndarray, p1=0.0880, p2=0.7376) -> np.ndarray:
        y = x * p1 + np.random.randn(*x.shape) * p2
        z = np.fft.fft(y, axis=0)
        w = np.abs(z) * np.exp(1j * (np.angle(z) + 0.991))
        result = np.fft.ifft(w, axis=0)
        for _ in range(5):
            result = self.apply_nonlinear_map(result, 0.131)
        return result / (np.linalg.norm(result) + 1e-15)

    def method_reverse_biorthogonal_11_23(self, x: np.ndarray, p1=0.6626, p2=0.9416) -> np.ndarray:
        y = x * p1 + np.random.randn(*x.shape) * p2
        z = np.fft.fft(y, axis=0)
        w = np.abs(z) * np.exp(1j * (np.angle(z) + 0.182))
        result = np.fft.ifft(w, axis=0)
        for _ in range(6):
            result = self.apply_nonlinear_map(result, 0.995)
        return result / (np.linalg.norm(result) + 1e-15)

    def method_reverse_biorthogonal_11_24(self, x: np.ndarray, p1=0.8036, p2=0.7985) -> np.ndarray:
        y = x * p1 + np.random.randn(*x.shape) * p2
        z = np.fft.fft(y, axis=0)
        w = np.abs(z) * np.exp(1j * (np.angle(z) + 0.344))
        result = np.fft.ifft(w, axis=0)
        for _ in range(2):
            result = self.apply_nonlinear_map(result, 0.232)
        return result / (np.linalg.norm(result) + 1e-15)

    def method_reverse_biorthogonal_11_25(self, x: np.ndarray, p1=0.4191, p2=0.8419) -> np.ndarray:
        y = x * p1 + np.random.randn(*x.shape) * p2
        z = np.fft.fft(y, axis=0)
        w = np.abs(z) * np.exp(1j * (np.angle(z) + 0.573))
        result = np.fft.ifft(w, axis=0)
        for _ in range(7):
            result = self.apply_nonlinear_map(result, 0.121)
        return result / (np.linalg.norm(result) + 1e-15)

    def method_reverse_biorthogonal_11_26(self, x: np.ndarray, p1=0.2238, p2=0.8073) -> np.ndarray:
        y = x * p1 + np.random.randn(*x.shape) * p2
        z = np.fft.fft(y, axis=0)
        w = np.abs(z) * np.exp(1j * (np.angle(z) + 0.596))
        result = np.fft.ifft(w, axis=0)
        for _ in range(2):
            result = self.apply_nonlinear_map(result, 0.249)
        return result / (np.linalg.norm(result) + 1e-15)

    def method_reverse_biorthogonal_11_27(self, x: np.ndarray, p1=0.9854, p2=0.2866) -> np.ndarray:
        y = x * p1 + np.random.randn(*x.shape) * p2
        z = np.fft.fft(y, axis=0)
        w = np.abs(z) * np.exp(1j * (np.angle(z) + 0.853))
        result = np.fft.ifft(w, axis=0)
        for _ in range(6):
            result = self.apply_nonlinear_map(result, 0.284)
        return result / (np.linalg.norm(result) + 1e-15)
