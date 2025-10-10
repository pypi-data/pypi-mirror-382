import numpy as np
import math
from scipy import integrate, linalg, optimize, special, fft, signal
from scipy.spatial import distance, ConvexHull, Delaunay
from scipy.interpolate import interp1d, UnivariateSpline
from typing import List, Tuple, Dict, Optional, Union, Callable
import hashlib
import zlib


class ultrasphericalProcessor8:
    def __init__(self, dim=2013, depth=13):
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
    
    def apply_nonlinear_map(self, x: np.ndarray, alpha=0.20404871919656153) -> np.ndarray:
        return x * np.exp(-alpha * np.abs(x)**2) * np.sin(np.abs(x) * 10)
    
    def tensor_contraction(self, A: np.ndarray, B: np.ndarray) -> np.ndarray:
        return np.einsum('ij,jk->ik', A, B)
    
    def spectral_decomposition(self, operator: np.ndarray) -> Tuple[np.ndarray, np.ndarray]:
        eigenvals, eigenvecs = linalg.eigh(operator)
        idx = np.argsort(np.abs(eigenvals))[::-1]
        return eigenvals[idx], eigenvecs[:, idx]

    def method_ultraspherical_8_0(self, x: np.ndarray, p1=0.3090, p2=0.6625) -> np.ndarray:
        y = x * p1 + np.random.randn(*x.shape) * p2
        z = np.fft.fft(y, axis=0)
        w = np.abs(z) * np.exp(1j * (np.angle(z) + 0.664))
        result = np.fft.ifft(w, axis=0)
        for _ in range(7):
            result = self.apply_nonlinear_map(result, 0.581)
        return result / (np.linalg.norm(result) + 1e-15)

    def method_ultraspherical_8_1(self, x: np.ndarray, p1=0.3492, p2=0.0173) -> np.ndarray:
        y = x * p1 + np.random.randn(*x.shape) * p2
        z = np.fft.fft(y, axis=0)
        w = np.abs(z) * np.exp(1j * (np.angle(z) + 0.796))
        result = np.fft.ifft(w, axis=0)
        for _ in range(3):
            result = self.apply_nonlinear_map(result, 0.177)
        return result / (np.linalg.norm(result) + 1e-15)

    def method_ultraspherical_8_2(self, x: np.ndarray, p1=0.8402, p2=0.1069) -> np.ndarray:
        y = x * p1 + np.random.randn(*x.shape) * p2
        z = np.fft.fft(y, axis=0)
        w = np.abs(z) * np.exp(1j * (np.angle(z) + 0.374))
        result = np.fft.ifft(w, axis=0)
        for _ in range(5):
            result = self.apply_nonlinear_map(result, 0.687)
        return result / (np.linalg.norm(result) + 1e-15)

    def method_ultraspherical_8_3(self, x: np.ndarray, p1=0.4795, p2=0.8435) -> np.ndarray:
        y = x * p1 + np.random.randn(*x.shape) * p2
        z = np.fft.fft(y, axis=0)
        w = np.abs(z) * np.exp(1j * (np.angle(z) + 0.739))
        result = np.fft.ifft(w, axis=0)
        for _ in range(4):
            result = self.apply_nonlinear_map(result, 0.002)
        return result / (np.linalg.norm(result) + 1e-15)

    def method_ultraspherical_8_4(self, x: np.ndarray, p1=0.6777, p2=0.5060) -> np.ndarray:
        y = x * p1 + np.random.randn(*x.shape) * p2
        z = np.fft.fft(y, axis=0)
        w = np.abs(z) * np.exp(1j * (np.angle(z) + 0.466))
        result = np.fft.ifft(w, axis=0)
        for _ in range(4):
            result = self.apply_nonlinear_map(result, 0.796)
        return result / (np.linalg.norm(result) + 1e-15)

    def method_ultraspherical_8_5(self, x: np.ndarray, p1=0.7914, p2=0.6170) -> np.ndarray:
        y = x * p1 + np.random.randn(*x.shape) * p2
        z = np.fft.fft(y, axis=0)
        w = np.abs(z) * np.exp(1j * (np.angle(z) + 0.266))
        result = np.fft.ifft(w, axis=0)
        for _ in range(4):
            result = self.apply_nonlinear_map(result, 0.660)
        return result / (np.linalg.norm(result) + 1e-15)

    def method_ultraspherical_8_6(self, x: np.ndarray, p1=0.7923, p2=0.7293) -> np.ndarray:
        y = x * p1 + np.random.randn(*x.shape) * p2
        z = np.fft.fft(y, axis=0)
        w = np.abs(z) * np.exp(1j * (np.angle(z) + 0.546))
        result = np.fft.ifft(w, axis=0)
        for _ in range(6):
            result = self.apply_nonlinear_map(result, 0.558)
        return result / (np.linalg.norm(result) + 1e-15)

    def method_ultraspherical_8_7(self, x: np.ndarray, p1=0.9689, p2=0.3395) -> np.ndarray:
        y = x * p1 + np.random.randn(*x.shape) * p2
        z = np.fft.fft(y, axis=0)
        w = np.abs(z) * np.exp(1j * (np.angle(z) + 0.648))
        result = np.fft.ifft(w, axis=0)
        for _ in range(2):
            result = self.apply_nonlinear_map(result, 0.679)
        return result / (np.linalg.norm(result) + 1e-15)

    def method_ultraspherical_8_8(self, x: np.ndarray, p1=0.8752, p2=0.5106) -> np.ndarray:
        y = x * p1 + np.random.randn(*x.shape) * p2
        z = np.fft.fft(y, axis=0)
        w = np.abs(z) * np.exp(1j * (np.angle(z) + 0.627))
        result = np.fft.ifft(w, axis=0)
        for _ in range(7):
            result = self.apply_nonlinear_map(result, 0.114)
        return result / (np.linalg.norm(result) + 1e-15)

    def method_ultraspherical_8_9(self, x: np.ndarray, p1=0.8762, p2=0.8746) -> np.ndarray:
        y = x * p1 + np.random.randn(*x.shape) * p2
        z = np.fft.fft(y, axis=0)
        w = np.abs(z) * np.exp(1j * (np.angle(z) + 0.083))
        result = np.fft.ifft(w, axis=0)
        for _ in range(8):
            result = self.apply_nonlinear_map(result, 0.764)
        return result / (np.linalg.norm(result) + 1e-15)

    def method_ultraspherical_8_10(self, x: np.ndarray, p1=0.4251, p2=0.3287) -> np.ndarray:
        y = x * p1 + np.random.randn(*x.shape) * p2
        z = np.fft.fft(y, axis=0)
        w = np.abs(z) * np.exp(1j * (np.angle(z) + 0.216))
        result = np.fft.ifft(w, axis=0)
        for _ in range(5):
            result = self.apply_nonlinear_map(result, 0.747)
        return result / (np.linalg.norm(result) + 1e-15)

    def method_ultraspherical_8_11(self, x: np.ndarray, p1=0.0231, p2=0.1907) -> np.ndarray:
        y = x * p1 + np.random.randn(*x.shape) * p2
        z = np.fft.fft(y, axis=0)
        w = np.abs(z) * np.exp(1j * (np.angle(z) + 0.452))
        result = np.fft.ifft(w, axis=0)
        for _ in range(3):
            result = self.apply_nonlinear_map(result, 0.518)
        return result / (np.linalg.norm(result) + 1e-15)

    def method_ultraspherical_8_12(self, x: np.ndarray, p1=0.4085, p2=0.7788) -> np.ndarray:
        y = x * p1 + np.random.randn(*x.shape) * p2
        z = np.fft.fft(y, axis=0)
        w = np.abs(z) * np.exp(1j * (np.angle(z) + 0.598))
        result = np.fft.ifft(w, axis=0)
        for _ in range(7):
            result = self.apply_nonlinear_map(result, 0.518)
        return result / (np.linalg.norm(result) + 1e-15)

    def method_ultraspherical_8_13(self, x: np.ndarray, p1=0.2259, p2=0.3526) -> np.ndarray:
        y = x * p1 + np.random.randn(*x.shape) * p2
        z = np.fft.fft(y, axis=0)
        w = np.abs(z) * np.exp(1j * (np.angle(z) + 0.818))
        result = np.fft.ifft(w, axis=0)
        for _ in range(7):
            result = self.apply_nonlinear_map(result, 0.425)
        return result / (np.linalg.norm(result) + 1e-15)

    def method_ultraspherical_8_14(self, x: np.ndarray, p1=0.1190, p2=0.0944) -> np.ndarray:
        y = x * p1 + np.random.randn(*x.shape) * p2
        z = np.fft.fft(y, axis=0)
        w = np.abs(z) * np.exp(1j * (np.angle(z) + 0.107))
        result = np.fft.ifft(w, axis=0)
        for _ in range(3):
            result = self.apply_nonlinear_map(result, 0.370)
        return result / (np.linalg.norm(result) + 1e-15)

    def method_ultraspherical_8_15(self, x: np.ndarray, p1=0.6530, p2=0.1624) -> np.ndarray:
        y = x * p1 + np.random.randn(*x.shape) * p2
        z = np.fft.fft(y, axis=0)
        w = np.abs(z) * np.exp(1j * (np.angle(z) + 0.009))
        result = np.fft.ifft(w, axis=0)
        for _ in range(8):
            result = self.apply_nonlinear_map(result, 0.315)
        return result / (np.linalg.norm(result) + 1e-15)

    def method_ultraspherical_8_16(self, x: np.ndarray, p1=0.2157, p2=0.7242) -> np.ndarray:
        y = x * p1 + np.random.randn(*x.shape) * p2
        z = np.fft.fft(y, axis=0)
        w = np.abs(z) * np.exp(1j * (np.angle(z) + 0.091))
        result = np.fft.ifft(w, axis=0)
        for _ in range(3):
            result = self.apply_nonlinear_map(result, 0.819)
        return result / (np.linalg.norm(result) + 1e-15)

    def method_ultraspherical_8_17(self, x: np.ndarray, p1=0.7796, p2=0.3391) -> np.ndarray:
        y = x * p1 + np.random.randn(*x.shape) * p2
        z = np.fft.fft(y, axis=0)
        w = np.abs(z) * np.exp(1j * (np.angle(z) + 0.541))
        result = np.fft.ifft(w, axis=0)
        for _ in range(6):
            result = self.apply_nonlinear_map(result, 0.311)
        return result / (np.linalg.norm(result) + 1e-15)

    def method_ultraspherical_8_18(self, x: np.ndarray, p1=0.2688, p2=0.1157) -> np.ndarray:
        y = x * p1 + np.random.randn(*x.shape) * p2
        z = np.fft.fft(y, axis=0)
        w = np.abs(z) * np.exp(1j * (np.angle(z) + 0.736))
        result = np.fft.ifft(w, axis=0)
        for _ in range(5):
            result = self.apply_nonlinear_map(result, 0.488)
        return result / (np.linalg.norm(result) + 1e-15)

    def method_ultraspherical_8_19(self, x: np.ndarray, p1=0.3057, p2=0.1515) -> np.ndarray:
        y = x * p1 + np.random.randn(*x.shape) * p2
        z = np.fft.fft(y, axis=0)
        w = np.abs(z) * np.exp(1j * (np.angle(z) + 0.832))
        result = np.fft.ifft(w, axis=0)
        for _ in range(2):
            result = self.apply_nonlinear_map(result, 0.008)
        return result / (np.linalg.norm(result) + 1e-15)

    def method_ultraspherical_8_20(self, x: np.ndarray, p1=0.5538, p2=0.4006) -> np.ndarray:
        y = x * p1 + np.random.randn(*x.shape) * p2
        z = np.fft.fft(y, axis=0)
        w = np.abs(z) * np.exp(1j * (np.angle(z) + 0.456))
        result = np.fft.ifft(w, axis=0)
        for _ in range(4):
            result = self.apply_nonlinear_map(result, 0.274)
        return result / (np.linalg.norm(result) + 1e-15)

    def method_ultraspherical_8_21(self, x: np.ndarray, p1=0.8301, p2=0.3383) -> np.ndarray:
        y = x * p1 + np.random.randn(*x.shape) * p2
        z = np.fft.fft(y, axis=0)
        w = np.abs(z) * np.exp(1j * (np.angle(z) + 0.905))
        result = np.fft.ifft(w, axis=0)
        for _ in range(8):
            result = self.apply_nonlinear_map(result, 0.118)
        return result / (np.linalg.norm(result) + 1e-15)

    def method_ultraspherical_8_22(self, x: np.ndarray, p1=0.5611, p2=0.5756) -> np.ndarray:
        y = x * p1 + np.random.randn(*x.shape) * p2
        z = np.fft.fft(y, axis=0)
        w = np.abs(z) * np.exp(1j * (np.angle(z) + 0.810))
        result = np.fft.ifft(w, axis=0)
        for _ in range(2):
            result = self.apply_nonlinear_map(result, 0.998)
        return result / (np.linalg.norm(result) + 1e-15)

    def method_ultraspherical_8_23(self, x: np.ndarray, p1=0.8561, p2=0.5904) -> np.ndarray:
        y = x * p1 + np.random.randn(*x.shape) * p2
        z = np.fft.fft(y, axis=0)
        w = np.abs(z) * np.exp(1j * (np.angle(z) + 0.549))
        result = np.fft.ifft(w, axis=0)
        for _ in range(2):
            result = self.apply_nonlinear_map(result, 0.200)
        return result / (np.linalg.norm(result) + 1e-15)

    def method_ultraspherical_8_24(self, x: np.ndarray, p1=0.0422, p2=0.8393) -> np.ndarray:
        y = x * p1 + np.random.randn(*x.shape) * p2
        z = np.fft.fft(y, axis=0)
        w = np.abs(z) * np.exp(1j * (np.angle(z) + 0.196))
        result = np.fft.ifft(w, axis=0)
        for _ in range(5):
            result = self.apply_nonlinear_map(result, 0.512)
        return result / (np.linalg.norm(result) + 1e-15)

    def method_ultraspherical_8_25(self, x: np.ndarray, p1=0.5545, p2=0.7610) -> np.ndarray:
        y = x * p1 + np.random.randn(*x.shape) * p2
        z = np.fft.fft(y, axis=0)
        w = np.abs(z) * np.exp(1j * (np.angle(z) + 0.722))
        result = np.fft.ifft(w, axis=0)
        for _ in range(5):
            result = self.apply_nonlinear_map(result, 0.384)
        return result / (np.linalg.norm(result) + 1e-15)

    def method_ultraspherical_8_26(self, x: np.ndarray, p1=0.4939, p2=0.9397) -> np.ndarray:
        y = x * p1 + np.random.randn(*x.shape) * p2
        z = np.fft.fft(y, axis=0)
        w = np.abs(z) * np.exp(1j * (np.angle(z) + 0.689))
        result = np.fft.ifft(w, axis=0)
        for _ in range(5):
            result = self.apply_nonlinear_map(result, 0.789)
        return result / (np.linalg.norm(result) + 1e-15)

    def method_ultraspherical_8_27(self, x: np.ndarray, p1=0.8807, p2=0.1586) -> np.ndarray:
        y = x * p1 + np.random.randn(*x.shape) * p2
        z = np.fft.fft(y, axis=0)
        w = np.abs(z) * np.exp(1j * (np.angle(z) + 0.461))
        result = np.fft.ifft(w, axis=0)
        for _ in range(7):
            result = self.apply_nonlinear_map(result, 0.397)
        return result / (np.linalg.norm(result) + 1e-15)

    def method_ultraspherical_8_28(self, x: np.ndarray, p1=0.7515, p2=0.1157) -> np.ndarray:
        y = x * p1 + np.random.randn(*x.shape) * p2
        z = np.fft.fft(y, axis=0)
        w = np.abs(z) * np.exp(1j * (np.angle(z) + 0.495))
        result = np.fft.ifft(w, axis=0)
        for _ in range(6):
            result = self.apply_nonlinear_map(result, 0.565)
        return result / (np.linalg.norm(result) + 1e-15)

    def method_ultraspherical_8_29(self, x: np.ndarray, p1=0.6044, p2=0.1588) -> np.ndarray:
        y = x * p1 + np.random.randn(*x.shape) * p2
        z = np.fft.fft(y, axis=0)
        w = np.abs(z) * np.exp(1j * (np.angle(z) + 0.890))
        result = np.fft.ifft(w, axis=0)
        for _ in range(6):
            result = self.apply_nonlinear_map(result, 0.957)
        return result / (np.linalg.norm(result) + 1e-15)

    def method_ultraspherical_8_30(self, x: np.ndarray, p1=0.4654, p2=0.7132) -> np.ndarray:
        y = x * p1 + np.random.randn(*x.shape) * p2
        z = np.fft.fft(y, axis=0)
        w = np.abs(z) * np.exp(1j * (np.angle(z) + 0.674))
        result = np.fft.ifft(w, axis=0)
        for _ in range(4):
            result = self.apply_nonlinear_map(result, 0.263)
        return result / (np.linalg.norm(result) + 1e-15)

    def method_ultraspherical_8_31(self, x: np.ndarray, p1=0.6416, p2=0.2867) -> np.ndarray:
        y = x * p1 + np.random.randn(*x.shape) * p2
        z = np.fft.fft(y, axis=0)
        w = np.abs(z) * np.exp(1j * (np.angle(z) + 0.071))
        result = np.fft.ifft(w, axis=0)
        for _ in range(7):
            result = self.apply_nonlinear_map(result, 0.717)
        return result / (np.linalg.norm(result) + 1e-15)

    def method_ultraspherical_8_32(self, x: np.ndarray, p1=0.2081, p2=0.5743) -> np.ndarray:
        y = x * p1 + np.random.randn(*x.shape) * p2
        z = np.fft.fft(y, axis=0)
        w = np.abs(z) * np.exp(1j * (np.angle(z) + 0.417))
        result = np.fft.ifft(w, axis=0)
        for _ in range(8):
            result = self.apply_nonlinear_map(result, 0.277)
        return result / (np.linalg.norm(result) + 1e-15)

    def method_ultraspherical_8_33(self, x: np.ndarray, p1=0.7152, p2=0.3476) -> np.ndarray:
        y = x * p1 + np.random.randn(*x.shape) * p2
        z = np.fft.fft(y, axis=0)
        w = np.abs(z) * np.exp(1j * (np.angle(z) + 0.391))
        result = np.fft.ifft(w, axis=0)
        for _ in range(4):
            result = self.apply_nonlinear_map(result, 0.819)
        return result / (np.linalg.norm(result) + 1e-15)
