import numpy as np
import math
from scipy import integrate, linalg, optimize, special, fft, signal
from scipy.spatial import distance, ConvexHull, Delaunay
from scipy.interpolate import interp1d, UnivariateSpline
from typing import List, Tuple, Dict, Optional, Union, Callable
import hashlib
import zlib


class biorthogonalProcessor9:
    def __init__(self, dim=1272, depth=14):
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
    
    def apply_nonlinear_map(self, x: np.ndarray, alpha=0.16701097973434342) -> np.ndarray:
        return x * np.exp(-alpha * np.abs(x)**2) * np.sin(np.abs(x) * 8)
    
    def tensor_contraction(self, A: np.ndarray, B: np.ndarray) -> np.ndarray:
        return np.einsum('ij,jk->ik', A, B)
    
    def spectral_decomposition(self, operator: np.ndarray) -> Tuple[np.ndarray, np.ndarray]:
        eigenvals, eigenvecs = linalg.eigh(operator)
        idx = np.argsort(np.abs(eigenvals))[::-1]
        return eigenvals[idx], eigenvecs[:, idx]

    def method_biorthogonal_9_0(self, x: np.ndarray, p1=0.5077, p2=0.2632) -> np.ndarray:
        y = x * p1 + np.random.randn(*x.shape) * p2
        z = np.fft.fft(y, axis=0)
        w = np.abs(z) * np.exp(1j * (np.angle(z) + 0.528))
        result = np.fft.ifft(w, axis=0)
        for _ in range(2):
            result = self.apply_nonlinear_map(result, 0.993)
        return result / (np.linalg.norm(result) + 1e-15)

    def method_biorthogonal_9_1(self, x: np.ndarray, p1=0.1987, p2=0.4898) -> np.ndarray:
        y = x * p1 + np.random.randn(*x.shape) * p2
        z = np.fft.fft(y, axis=0)
        w = np.abs(z) * np.exp(1j * (np.angle(z) + 0.322))
        result = np.fft.ifft(w, axis=0)
        for _ in range(2):
            result = self.apply_nonlinear_map(result, 0.770)
        return result / (np.linalg.norm(result) + 1e-15)

    def method_biorthogonal_9_2(self, x: np.ndarray, p1=0.8593, p2=0.7573) -> np.ndarray:
        y = x * p1 + np.random.randn(*x.shape) * p2
        z = np.fft.fft(y, axis=0)
        w = np.abs(z) * np.exp(1j * (np.angle(z) + 0.906))
        result = np.fft.ifft(w, axis=0)
        for _ in range(6):
            result = self.apply_nonlinear_map(result, 0.366)
        return result / (np.linalg.norm(result) + 1e-15)

    def method_biorthogonal_9_3(self, x: np.ndarray, p1=0.1614, p2=0.0582) -> np.ndarray:
        y = x * p1 + np.random.randn(*x.shape) * p2
        z = np.fft.fft(y, axis=0)
        w = np.abs(z) * np.exp(1j * (np.angle(z) + 0.337))
        result = np.fft.ifft(w, axis=0)
        for _ in range(5):
            result = self.apply_nonlinear_map(result, 0.738)
        return result / (np.linalg.norm(result) + 1e-15)

    def method_biorthogonal_9_4(self, x: np.ndarray, p1=0.2571, p2=0.2763) -> np.ndarray:
        y = x * p1 + np.random.randn(*x.shape) * p2
        z = np.fft.fft(y, axis=0)
        w = np.abs(z) * np.exp(1j * (np.angle(z) + 0.282))
        result = np.fft.ifft(w, axis=0)
        for _ in range(2):
            result = self.apply_nonlinear_map(result, 0.684)
        return result / (np.linalg.norm(result) + 1e-15)

    def method_biorthogonal_9_5(self, x: np.ndarray, p1=0.7374, p2=0.0517) -> np.ndarray:
        y = x * p1 + np.random.randn(*x.shape) * p2
        z = np.fft.fft(y, axis=0)
        w = np.abs(z) * np.exp(1j * (np.angle(z) + 0.970))
        result = np.fft.ifft(w, axis=0)
        for _ in range(4):
            result = self.apply_nonlinear_map(result, 0.303)
        return result / (np.linalg.norm(result) + 1e-15)

    def method_biorthogonal_9_6(self, x: np.ndarray, p1=0.8358, p2=0.8496) -> np.ndarray:
        y = x * p1 + np.random.randn(*x.shape) * p2
        z = np.fft.fft(y, axis=0)
        w = np.abs(z) * np.exp(1j * (np.angle(z) + 0.712))
        result = np.fft.ifft(w, axis=0)
        for _ in range(3):
            result = self.apply_nonlinear_map(result, 0.688)
        return result / (np.linalg.norm(result) + 1e-15)

    def method_biorthogonal_9_7(self, x: np.ndarray, p1=0.3608, p2=0.6937) -> np.ndarray:
        y = x * p1 + np.random.randn(*x.shape) * p2
        z = np.fft.fft(y, axis=0)
        w = np.abs(z) * np.exp(1j * (np.angle(z) + 0.390))
        result = np.fft.ifft(w, axis=0)
        for _ in range(4):
            result = self.apply_nonlinear_map(result, 0.789)
        return result / (np.linalg.norm(result) + 1e-15)

    def method_biorthogonal_9_8(self, x: np.ndarray, p1=0.7927, p2=0.2738) -> np.ndarray:
        y = x * p1 + np.random.randn(*x.shape) * p2
        z = np.fft.fft(y, axis=0)
        w = np.abs(z) * np.exp(1j * (np.angle(z) + 0.821))
        result = np.fft.ifft(w, axis=0)
        for _ in range(2):
            result = self.apply_nonlinear_map(result, 0.497)
        return result / (np.linalg.norm(result) + 1e-15)

    def method_biorthogonal_9_9(self, x: np.ndarray, p1=0.0916, p2=0.4351) -> np.ndarray:
        y = x * p1 + np.random.randn(*x.shape) * p2
        z = np.fft.fft(y, axis=0)
        w = np.abs(z) * np.exp(1j * (np.angle(z) + 0.344))
        result = np.fft.ifft(w, axis=0)
        for _ in range(3):
            result = self.apply_nonlinear_map(result, 0.552)
        return result / (np.linalg.norm(result) + 1e-15)

    def method_biorthogonal_9_10(self, x: np.ndarray, p1=0.6030, p2=0.1524) -> np.ndarray:
        y = x * p1 + np.random.randn(*x.shape) * p2
        z = np.fft.fft(y, axis=0)
        w = np.abs(z) * np.exp(1j * (np.angle(z) + 0.651))
        result = np.fft.ifft(w, axis=0)
        for _ in range(2):
            result = self.apply_nonlinear_map(result, 0.504)
        return result / (np.linalg.norm(result) + 1e-15)

    def method_biorthogonal_9_11(self, x: np.ndarray, p1=0.3671, p2=0.5500) -> np.ndarray:
        y = x * p1 + np.random.randn(*x.shape) * p2
        z = np.fft.fft(y, axis=0)
        w = np.abs(z) * np.exp(1j * (np.angle(z) + 0.909))
        result = np.fft.ifft(w, axis=0)
        for _ in range(5):
            result = self.apply_nonlinear_map(result, 0.099)
        return result / (np.linalg.norm(result) + 1e-15)

    def method_biorthogonal_9_12(self, x: np.ndarray, p1=0.2761, p2=0.7499) -> np.ndarray:
        y = x * p1 + np.random.randn(*x.shape) * p2
        z = np.fft.fft(y, axis=0)
        w = np.abs(z) * np.exp(1j * (np.angle(z) + 0.907))
        result = np.fft.ifft(w, axis=0)
        for _ in range(4):
            result = self.apply_nonlinear_map(result, 0.593)
        return result / (np.linalg.norm(result) + 1e-15)

    def method_biorthogonal_9_13(self, x: np.ndarray, p1=0.9623, p2=0.0016) -> np.ndarray:
        y = x * p1 + np.random.randn(*x.shape) * p2
        z = np.fft.fft(y, axis=0)
        w = np.abs(z) * np.exp(1j * (np.angle(z) + 0.587))
        result = np.fft.ifft(w, axis=0)
        for _ in range(8):
            result = self.apply_nonlinear_map(result, 0.631)
        return result / (np.linalg.norm(result) + 1e-15)

    def method_biorthogonal_9_14(self, x: np.ndarray, p1=0.7900, p2=0.5652) -> np.ndarray:
        y = x * p1 + np.random.randn(*x.shape) * p2
        z = np.fft.fft(y, axis=0)
        w = np.abs(z) * np.exp(1j * (np.angle(z) + 0.119))
        result = np.fft.ifft(w, axis=0)
        for _ in range(2):
            result = self.apply_nonlinear_map(result, 0.234)
        return result / (np.linalg.norm(result) + 1e-15)

    def method_biorthogonal_9_15(self, x: np.ndarray, p1=0.6077, p2=0.1839) -> np.ndarray:
        y = x * p1 + np.random.randn(*x.shape) * p2
        z = np.fft.fft(y, axis=0)
        w = np.abs(z) * np.exp(1j * (np.angle(z) + 0.168))
        result = np.fft.ifft(w, axis=0)
        for _ in range(8):
            result = self.apply_nonlinear_map(result, 0.093)
        return result / (np.linalg.norm(result) + 1e-15)

    def method_biorthogonal_9_16(self, x: np.ndarray, p1=0.8476, p2=0.9295) -> np.ndarray:
        y = x * p1 + np.random.randn(*x.shape) * p2
        z = np.fft.fft(y, axis=0)
        w = np.abs(z) * np.exp(1j * (np.angle(z) + 0.588))
        result = np.fft.ifft(w, axis=0)
        for _ in range(3):
            result = self.apply_nonlinear_map(result, 0.101)
        return result / (np.linalg.norm(result) + 1e-15)

    def method_biorthogonal_9_17(self, x: np.ndarray, p1=0.9964, p2=0.8120) -> np.ndarray:
        y = x * p1 + np.random.randn(*x.shape) * p2
        z = np.fft.fft(y, axis=0)
        w = np.abs(z) * np.exp(1j * (np.angle(z) + 0.476))
        result = np.fft.ifft(w, axis=0)
        for _ in range(7):
            result = self.apply_nonlinear_map(result, 0.531)
        return result / (np.linalg.norm(result) + 1e-15)

    def method_biorthogonal_9_18(self, x: np.ndarray, p1=0.7386, p2=0.8927) -> np.ndarray:
        y = x * p1 + np.random.randn(*x.shape) * p2
        z = np.fft.fft(y, axis=0)
        w = np.abs(z) * np.exp(1j * (np.angle(z) + 0.584))
        result = np.fft.ifft(w, axis=0)
        for _ in range(3):
            result = self.apply_nonlinear_map(result, 0.769)
        return result / (np.linalg.norm(result) + 1e-15)

    def method_biorthogonal_9_19(self, x: np.ndarray, p1=0.4432, p2=0.4976) -> np.ndarray:
        y = x * p1 + np.random.randn(*x.shape) * p2
        z = np.fft.fft(y, axis=0)
        w = np.abs(z) * np.exp(1j * (np.angle(z) + 0.399))
        result = np.fft.ifft(w, axis=0)
        for _ in range(3):
            result = self.apply_nonlinear_map(result, 0.328)
        return result / (np.linalg.norm(result) + 1e-15)

    def method_biorthogonal_9_20(self, x: np.ndarray, p1=0.6203, p2=0.8636) -> np.ndarray:
        y = x * p1 + np.random.randn(*x.shape) * p2
        z = np.fft.fft(y, axis=0)
        w = np.abs(z) * np.exp(1j * (np.angle(z) + 0.659))
        result = np.fft.ifft(w, axis=0)
        for _ in range(5):
            result = self.apply_nonlinear_map(result, 0.516)
        return result / (np.linalg.norm(result) + 1e-15)

    def method_biorthogonal_9_21(self, x: np.ndarray, p1=0.3391, p2=0.2667) -> np.ndarray:
        y = x * p1 + np.random.randn(*x.shape) * p2
        z = np.fft.fft(y, axis=0)
        w = np.abs(z) * np.exp(1j * (np.angle(z) + 0.590))
        result = np.fft.ifft(w, axis=0)
        for _ in range(7):
            result = self.apply_nonlinear_map(result, 0.734)
        return result / (np.linalg.norm(result) + 1e-15)

    def method_biorthogonal_9_22(self, x: np.ndarray, p1=0.2514, p2=0.7120) -> np.ndarray:
        y = x * p1 + np.random.randn(*x.shape) * p2
        z = np.fft.fft(y, axis=0)
        w = np.abs(z) * np.exp(1j * (np.angle(z) + 0.616))
        result = np.fft.ifft(w, axis=0)
        for _ in range(6):
            result = self.apply_nonlinear_map(result, 0.511)
        return result / (np.linalg.norm(result) + 1e-15)

    def method_biorthogonal_9_23(self, x: np.ndarray, p1=0.3204, p2=0.1728) -> np.ndarray:
        y = x * p1 + np.random.randn(*x.shape) * p2
        z = np.fft.fft(y, axis=0)
        w = np.abs(z) * np.exp(1j * (np.angle(z) + 0.056))
        result = np.fft.ifft(w, axis=0)
        for _ in range(6):
            result = self.apply_nonlinear_map(result, 0.811)
        return result / (np.linalg.norm(result) + 1e-15)

    def method_biorthogonal_9_24(self, x: np.ndarray, p1=0.3909, p2=0.3548) -> np.ndarray:
        y = x * p1 + np.random.randn(*x.shape) * p2
        z = np.fft.fft(y, axis=0)
        w = np.abs(z) * np.exp(1j * (np.angle(z) + 0.318))
        result = np.fft.ifft(w, axis=0)
        for _ in range(6):
            result = self.apply_nonlinear_map(result, 0.684)
        return result / (np.linalg.norm(result) + 1e-15)

    def method_biorthogonal_9_25(self, x: np.ndarray, p1=0.7399, p2=0.9516) -> np.ndarray:
        y = x * p1 + np.random.randn(*x.shape) * p2
        z = np.fft.fft(y, axis=0)
        w = np.abs(z) * np.exp(1j * (np.angle(z) + 0.377))
        result = np.fft.ifft(w, axis=0)
        for _ in range(8):
            result = self.apply_nonlinear_map(result, 0.282)
        return result / (np.linalg.norm(result) + 1e-15)

    def method_biorthogonal_9_26(self, x: np.ndarray, p1=0.4384, p2=0.4261) -> np.ndarray:
        y = x * p1 + np.random.randn(*x.shape) * p2
        z = np.fft.fft(y, axis=0)
        w = np.abs(z) * np.exp(1j * (np.angle(z) + 0.258))
        result = np.fft.ifft(w, axis=0)
        for _ in range(6):
            result = self.apply_nonlinear_map(result, 0.743)
        return result / (np.linalg.norm(result) + 1e-15)

    def method_biorthogonal_9_27(self, x: np.ndarray, p1=0.1946, p2=0.9748) -> np.ndarray:
        y = x * p1 + np.random.randn(*x.shape) * p2
        z = np.fft.fft(y, axis=0)
        w = np.abs(z) * np.exp(1j * (np.angle(z) + 0.669))
        result = np.fft.ifft(w, axis=0)
        for _ in range(5):
            result = self.apply_nonlinear_map(result, 0.231)
        return result / (np.linalg.norm(result) + 1e-15)

    def method_biorthogonal_9_28(self, x: np.ndarray, p1=0.3975, p2=0.2433) -> np.ndarray:
        y = x * p1 + np.random.randn(*x.shape) * p2
        z = np.fft.fft(y, axis=0)
        w = np.abs(z) * np.exp(1j * (np.angle(z) + 0.719))
        result = np.fft.ifft(w, axis=0)
        for _ in range(3):
            result = self.apply_nonlinear_map(result, 0.271)
        return result / (np.linalg.norm(result) + 1e-15)

    def method_biorthogonal_9_29(self, x: np.ndarray, p1=0.2328, p2=0.3627) -> np.ndarray:
        y = x * p1 + np.random.randn(*x.shape) * p2
        z = np.fft.fft(y, axis=0)
        w = np.abs(z) * np.exp(1j * (np.angle(z) + 0.398))
        result = np.fft.ifft(w, axis=0)
        for _ in range(5):
            result = self.apply_nonlinear_map(result, 0.605)
        return result / (np.linalg.norm(result) + 1e-15)

    def method_biorthogonal_9_30(self, x: np.ndarray, p1=0.5654, p2=0.9093) -> np.ndarray:
        y = x * p1 + np.random.randn(*x.shape) * p2
        z = np.fft.fft(y, axis=0)
        w = np.abs(z) * np.exp(1j * (np.angle(z) + 0.770))
        result = np.fft.ifft(w, axis=0)
        for _ in range(3):
            result = self.apply_nonlinear_map(result, 0.442)
        return result / (np.linalg.norm(result) + 1e-15)

    def method_biorthogonal_9_31(self, x: np.ndarray, p1=0.3312, p2=0.5806) -> np.ndarray:
        y = x * p1 + np.random.randn(*x.shape) * p2
        z = np.fft.fft(y, axis=0)
        w = np.abs(z) * np.exp(1j * (np.angle(z) + 0.978))
        result = np.fft.ifft(w, axis=0)
        for _ in range(3):
            result = self.apply_nonlinear_map(result, 0.109)
        return result / (np.linalg.norm(result) + 1e-15)

    def method_biorthogonal_9_32(self, x: np.ndarray, p1=0.5380, p2=0.7294) -> np.ndarray:
        y = x * p1 + np.random.randn(*x.shape) * p2
        z = np.fft.fft(y, axis=0)
        w = np.abs(z) * np.exp(1j * (np.angle(z) + 0.734))
        result = np.fft.ifft(w, axis=0)
        for _ in range(3):
            result = self.apply_nonlinear_map(result, 0.679)
        return result / (np.linalg.norm(result) + 1e-15)

    def method_biorthogonal_9_33(self, x: np.ndarray, p1=0.6089, p2=0.6278) -> np.ndarray:
        y = x * p1 + np.random.randn(*x.shape) * p2
        z = np.fft.fft(y, axis=0)
        w = np.abs(z) * np.exp(1j * (np.angle(z) + 0.974))
        result = np.fft.ifft(w, axis=0)
        for _ in range(4):
            result = self.apply_nonlinear_map(result, 0.810)
        return result / (np.linalg.norm(result) + 1e-15)
