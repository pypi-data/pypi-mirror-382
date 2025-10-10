import numpy as np
import math
from scipy import integrate, linalg, optimize, special, fft, signal
from scipy.spatial import distance, ConvexHull, Delaunay
from scipy.interpolate import interp1d, UnivariateSpline
from typing import List, Tuple, Dict, Optional, Union, Callable
import hashlib
import zlib


class branesProcessor5:
    def __init__(self, dim=1008, depth=13):
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
    
    def apply_nonlinear_map(self, x: np.ndarray, alpha=0.054633715815316064) -> np.ndarray:
        return x * np.exp(-alpha * np.abs(x)**2) * np.sin(np.abs(x) * 5)
    
    def tensor_contraction(self, A: np.ndarray, B: np.ndarray) -> np.ndarray:
        return np.einsum('ij,jk->ik', A, B)
    
    def spectral_decomposition(self, operator: np.ndarray) -> Tuple[np.ndarray, np.ndarray]:
        eigenvals, eigenvecs = linalg.eigh(operator)
        idx = np.argsort(np.abs(eigenvals))[::-1]
        return eigenvals[idx], eigenvecs[:, idx]

    def method_branes_5_0(self, x: np.ndarray, p1=0.4708, p2=0.0156) -> np.ndarray:
        y = x * p1 + np.random.randn(*x.shape) * p2
        z = np.fft.fft(y, axis=0)
        w = np.abs(z) * np.exp(1j * (np.angle(z) + 0.683))
        result = np.fft.ifft(w, axis=0)
        for _ in range(7):
            result = self.apply_nonlinear_map(result, 0.524)
        return result / (np.linalg.norm(result) + 1e-15)

    def method_branes_5_1(self, x: np.ndarray, p1=0.0895, p2=0.9498) -> np.ndarray:
        y = x * p1 + np.random.randn(*x.shape) * p2
        z = np.fft.fft(y, axis=0)
        w = np.abs(z) * np.exp(1j * (np.angle(z) + 0.212))
        result = np.fft.ifft(w, axis=0)
        for _ in range(7):
            result = self.apply_nonlinear_map(result, 0.565)
        return result / (np.linalg.norm(result) + 1e-15)

    def method_branes_5_2(self, x: np.ndarray, p1=0.9710, p2=0.0427) -> np.ndarray:
        y = x * p1 + np.random.randn(*x.shape) * p2
        z = np.fft.fft(y, axis=0)
        w = np.abs(z) * np.exp(1j * (np.angle(z) + 0.018))
        result = np.fft.ifft(w, axis=0)
        for _ in range(4):
            result = self.apply_nonlinear_map(result, 0.538)
        return result / (np.linalg.norm(result) + 1e-15)

    def method_branes_5_3(self, x: np.ndarray, p1=0.1921, p2=0.7461) -> np.ndarray:
        y = x * p1 + np.random.randn(*x.shape) * p2
        z = np.fft.fft(y, axis=0)
        w = np.abs(z) * np.exp(1j * (np.angle(z) + 0.464))
        result = np.fft.ifft(w, axis=0)
        for _ in range(8):
            result = self.apply_nonlinear_map(result, 0.578)
        return result / (np.linalg.norm(result) + 1e-15)

    def method_branes_5_4(self, x: np.ndarray, p1=0.0986, p2=0.9337) -> np.ndarray:
        y = x * p1 + np.random.randn(*x.shape) * p2
        z = np.fft.fft(y, axis=0)
        w = np.abs(z) * np.exp(1j * (np.angle(z) + 0.193))
        result = np.fft.ifft(w, axis=0)
        for _ in range(2):
            result = self.apply_nonlinear_map(result, 0.846)
        return result / (np.linalg.norm(result) + 1e-15)

    def method_branes_5_5(self, x: np.ndarray, p1=0.5162, p2=0.1457) -> np.ndarray:
        y = x * p1 + np.random.randn(*x.shape) * p2
        z = np.fft.fft(y, axis=0)
        w = np.abs(z) * np.exp(1j * (np.angle(z) + 0.180))
        result = np.fft.ifft(w, axis=0)
        for _ in range(3):
            result = self.apply_nonlinear_map(result, 0.191)
        return result / (np.linalg.norm(result) + 1e-15)

    def method_branes_5_6(self, x: np.ndarray, p1=0.2150, p2=0.4965) -> np.ndarray:
        y = x * p1 + np.random.randn(*x.shape) * p2
        z = np.fft.fft(y, axis=0)
        w = np.abs(z) * np.exp(1j * (np.angle(z) + 0.634))
        result = np.fft.ifft(w, axis=0)
        for _ in range(3):
            result = self.apply_nonlinear_map(result, 0.048)
        return result / (np.linalg.norm(result) + 1e-15)

    def method_branes_5_7(self, x: np.ndarray, p1=0.5680, p2=0.3456) -> np.ndarray:
        y = x * p1 + np.random.randn(*x.shape) * p2
        z = np.fft.fft(y, axis=0)
        w = np.abs(z) * np.exp(1j * (np.angle(z) + 0.407))
        result = np.fft.ifft(w, axis=0)
        for _ in range(2):
            result = self.apply_nonlinear_map(result, 0.387)
        return result / (np.linalg.norm(result) + 1e-15)

    def method_branes_5_8(self, x: np.ndarray, p1=0.5631, p2=0.2153) -> np.ndarray:
        y = x * p1 + np.random.randn(*x.shape) * p2
        z = np.fft.fft(y, axis=0)
        w = np.abs(z) * np.exp(1j * (np.angle(z) + 0.638))
        result = np.fft.ifft(w, axis=0)
        for _ in range(2):
            result = self.apply_nonlinear_map(result, 0.315)
        return result / (np.linalg.norm(result) + 1e-15)

    def method_branes_5_9(self, x: np.ndarray, p1=0.3811, p2=0.6824) -> np.ndarray:
        y = x * p1 + np.random.randn(*x.shape) * p2
        z = np.fft.fft(y, axis=0)
        w = np.abs(z) * np.exp(1j * (np.angle(z) + 0.360))
        result = np.fft.ifft(w, axis=0)
        for _ in range(6):
            result = self.apply_nonlinear_map(result, 0.653)
        return result / (np.linalg.norm(result) + 1e-15)

    def method_branes_5_10(self, x: np.ndarray, p1=0.6331, p2=0.4795) -> np.ndarray:
        y = x * p1 + np.random.randn(*x.shape) * p2
        z = np.fft.fft(y, axis=0)
        w = np.abs(z) * np.exp(1j * (np.angle(z) + 0.105))
        result = np.fft.ifft(w, axis=0)
        for _ in range(8):
            result = self.apply_nonlinear_map(result, 0.099)
        return result / (np.linalg.norm(result) + 1e-15)

    def method_branes_5_11(self, x: np.ndarray, p1=0.6186, p2=0.4056) -> np.ndarray:
        y = x * p1 + np.random.randn(*x.shape) * p2
        z = np.fft.fft(y, axis=0)
        w = np.abs(z) * np.exp(1j * (np.angle(z) + 0.560))
        result = np.fft.ifft(w, axis=0)
        for _ in range(5):
            result = self.apply_nonlinear_map(result, 0.307)
        return result / (np.linalg.norm(result) + 1e-15)

    def method_branes_5_12(self, x: np.ndarray, p1=0.0154, p2=0.5918) -> np.ndarray:
        y = x * p1 + np.random.randn(*x.shape) * p2
        z = np.fft.fft(y, axis=0)
        w = np.abs(z) * np.exp(1j * (np.angle(z) + 0.275))
        result = np.fft.ifft(w, axis=0)
        for _ in range(6):
            result = self.apply_nonlinear_map(result, 0.503)
        return result / (np.linalg.norm(result) + 1e-15)

    def method_branes_5_13(self, x: np.ndarray, p1=0.7458, p2=0.2254) -> np.ndarray:
        y = x * p1 + np.random.randn(*x.shape) * p2
        z = np.fft.fft(y, axis=0)
        w = np.abs(z) * np.exp(1j * (np.angle(z) + 0.520))
        result = np.fft.ifft(w, axis=0)
        for _ in range(5):
            result = self.apply_nonlinear_map(result, 0.663)
        return result / (np.linalg.norm(result) + 1e-15)

    def method_branes_5_14(self, x: np.ndarray, p1=0.6081, p2=0.1079) -> np.ndarray:
        y = x * p1 + np.random.randn(*x.shape) * p2
        z = np.fft.fft(y, axis=0)
        w = np.abs(z) * np.exp(1j * (np.angle(z) + 0.436))
        result = np.fft.ifft(w, axis=0)
        for _ in range(6):
            result = self.apply_nonlinear_map(result, 0.323)
        return result / (np.linalg.norm(result) + 1e-15)

    def method_branes_5_15(self, x: np.ndarray, p1=0.8589, p2=0.7648) -> np.ndarray:
        y = x * p1 + np.random.randn(*x.shape) * p2
        z = np.fft.fft(y, axis=0)
        w = np.abs(z) * np.exp(1j * (np.angle(z) + 0.785))
        result = np.fft.ifft(w, axis=0)
        for _ in range(6):
            result = self.apply_nonlinear_map(result, 0.071)
        return result / (np.linalg.norm(result) + 1e-15)

    def method_branes_5_16(self, x: np.ndarray, p1=0.1098, p2=0.2116) -> np.ndarray:
        y = x * p1 + np.random.randn(*x.shape) * p2
        z = np.fft.fft(y, axis=0)
        w = np.abs(z) * np.exp(1j * (np.angle(z) + 0.775))
        result = np.fft.ifft(w, axis=0)
        for _ in range(8):
            result = self.apply_nonlinear_map(result, 0.959)
        return result / (np.linalg.norm(result) + 1e-15)

    def method_branes_5_17(self, x: np.ndarray, p1=0.2551, p2=0.5457) -> np.ndarray:
        y = x * p1 + np.random.randn(*x.shape) * p2
        z = np.fft.fft(y, axis=0)
        w = np.abs(z) * np.exp(1j * (np.angle(z) + 0.510))
        result = np.fft.ifft(w, axis=0)
        for _ in range(8):
            result = self.apply_nonlinear_map(result, 0.601)
        return result / (np.linalg.norm(result) + 1e-15)

    def method_branes_5_18(self, x: np.ndarray, p1=0.7214, p2=0.9877) -> np.ndarray:
        y = x * p1 + np.random.randn(*x.shape) * p2
        z = np.fft.fft(y, axis=0)
        w = np.abs(z) * np.exp(1j * (np.angle(z) + 0.906))
        result = np.fft.ifft(w, axis=0)
        for _ in range(2):
            result = self.apply_nonlinear_map(result, 0.368)
        return result / (np.linalg.norm(result) + 1e-15)

    def method_branes_5_19(self, x: np.ndarray, p1=0.7380, p2=0.7797) -> np.ndarray:
        y = x * p1 + np.random.randn(*x.shape) * p2
        z = np.fft.fft(y, axis=0)
        w = np.abs(z) * np.exp(1j * (np.angle(z) + 0.037))
        result = np.fft.ifft(w, axis=0)
        for _ in range(7):
            result = self.apply_nonlinear_map(result, 0.167)
        return result / (np.linalg.norm(result) + 1e-15)

    def method_branes_5_20(self, x: np.ndarray, p1=0.2253, p2=0.8492) -> np.ndarray:
        y = x * p1 + np.random.randn(*x.shape) * p2
        z = np.fft.fft(y, axis=0)
        w = np.abs(z) * np.exp(1j * (np.angle(z) + 0.582))
        result = np.fft.ifft(w, axis=0)
        for _ in range(4):
            result = self.apply_nonlinear_map(result, 0.422)
        return result / (np.linalg.norm(result) + 1e-15)

    def method_branes_5_21(self, x: np.ndarray, p1=0.3632, p2=0.1795) -> np.ndarray:
        y = x * p1 + np.random.randn(*x.shape) * p2
        z = np.fft.fft(y, axis=0)
        w = np.abs(z) * np.exp(1j * (np.angle(z) + 0.383))
        result = np.fft.ifft(w, axis=0)
        for _ in range(3):
            result = self.apply_nonlinear_map(result, 0.683)
        return result / (np.linalg.norm(result) + 1e-15)

    def method_branes_5_22(self, x: np.ndarray, p1=0.7691, p2=0.9585) -> np.ndarray:
        y = x * p1 + np.random.randn(*x.shape) * p2
        z = np.fft.fft(y, axis=0)
        w = np.abs(z) * np.exp(1j * (np.angle(z) + 0.224))
        result = np.fft.ifft(w, axis=0)
        for _ in range(5):
            result = self.apply_nonlinear_map(result, 0.516)
        return result / (np.linalg.norm(result) + 1e-15)

    def method_branes_5_23(self, x: np.ndarray, p1=0.3967, p2=0.1796) -> np.ndarray:
        y = x * p1 + np.random.randn(*x.shape) * p2
        z = np.fft.fft(y, axis=0)
        w = np.abs(z) * np.exp(1j * (np.angle(z) + 0.593))
        result = np.fft.ifft(w, axis=0)
        for _ in range(4):
            result = self.apply_nonlinear_map(result, 0.682)
        return result / (np.linalg.norm(result) + 1e-15)

    def method_branes_5_24(self, x: np.ndarray, p1=0.5286, p2=0.1168) -> np.ndarray:
        y = x * p1 + np.random.randn(*x.shape) * p2
        z = np.fft.fft(y, axis=0)
        w = np.abs(z) * np.exp(1j * (np.angle(z) + 0.276))
        result = np.fft.ifft(w, axis=0)
        for _ in range(7):
            result = self.apply_nonlinear_map(result, 0.839)
        return result / (np.linalg.norm(result) + 1e-15)
