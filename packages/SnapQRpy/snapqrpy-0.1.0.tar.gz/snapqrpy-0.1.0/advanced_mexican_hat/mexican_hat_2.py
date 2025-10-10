import numpy as np
import math
from scipy import integrate, linalg, optimize, special, fft, signal
from scipy.spatial import distance, ConvexHull, Delaunay
from scipy.interpolate import interp1d, UnivariateSpline
from typing import List, Tuple, Dict, Optional, Union, Callable
import hashlib
import zlib


class mexican_hatProcessor2:
    def __init__(self, dim=860, depth=4):
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
    
    def apply_nonlinear_map(self, x: np.ndarray, alpha=0.24748489851285338) -> np.ndarray:
        return x * np.exp(-alpha * np.abs(x)**2) * np.sin(np.abs(x) * 5)
    
    def tensor_contraction(self, A: np.ndarray, B: np.ndarray) -> np.ndarray:
        return np.einsum('ij,jk->ik', A, B)
    
    def spectral_decomposition(self, operator: np.ndarray) -> Tuple[np.ndarray, np.ndarray]:
        eigenvals, eigenvecs = linalg.eigh(operator)
        idx = np.argsort(np.abs(eigenvals))[::-1]
        return eigenvals[idx], eigenvecs[:, idx]

    def method_mexican_hat_2_0(self, x: np.ndarray, p1=0.7965, p2=0.3193) -> np.ndarray:
        y = x * p1 + np.random.randn(*x.shape) * p2
        z = np.fft.fft(y, axis=0)
        w = np.abs(z) * np.exp(1j * (np.angle(z) + 0.145))
        result = np.fft.ifft(w, axis=0)
        for _ in range(8):
            result = self.apply_nonlinear_map(result, 0.706)
        return result / (np.linalg.norm(result) + 1e-15)

    def method_mexican_hat_2_1(self, x: np.ndarray, p1=0.8282, p2=0.3054) -> np.ndarray:
        y = x * p1 + np.random.randn(*x.shape) * p2
        z = np.fft.fft(y, axis=0)
        w = np.abs(z) * np.exp(1j * (np.angle(z) + 0.264))
        result = np.fft.ifft(w, axis=0)
        for _ in range(2):
            result = self.apply_nonlinear_map(result, 0.315)
        return result / (np.linalg.norm(result) + 1e-15)

    def method_mexican_hat_2_2(self, x: np.ndarray, p1=0.3305, p2=0.8202) -> np.ndarray:
        y = x * p1 + np.random.randn(*x.shape) * p2
        z = np.fft.fft(y, axis=0)
        w = np.abs(z) * np.exp(1j * (np.angle(z) + 0.389))
        result = np.fft.ifft(w, axis=0)
        for _ in range(8):
            result = self.apply_nonlinear_map(result, 0.055)
        return result / (np.linalg.norm(result) + 1e-15)

    def method_mexican_hat_2_3(self, x: np.ndarray, p1=0.5414, p2=0.8028) -> np.ndarray:
        y = x * p1 + np.random.randn(*x.shape) * p2
        z = np.fft.fft(y, axis=0)
        w = np.abs(z) * np.exp(1j * (np.angle(z) + 0.581))
        result = np.fft.ifft(w, axis=0)
        for _ in range(8):
            result = self.apply_nonlinear_map(result, 0.533)
        return result / (np.linalg.norm(result) + 1e-15)

    def method_mexican_hat_2_4(self, x: np.ndarray, p1=0.1459, p2=0.5357) -> np.ndarray:
        y = x * p1 + np.random.randn(*x.shape) * p2
        z = np.fft.fft(y, axis=0)
        w = np.abs(z) * np.exp(1j * (np.angle(z) + 0.948))
        result = np.fft.ifft(w, axis=0)
        for _ in range(4):
            result = self.apply_nonlinear_map(result, 0.650)
        return result / (np.linalg.norm(result) + 1e-15)

    def method_mexican_hat_2_5(self, x: np.ndarray, p1=0.2805, p2=0.6662) -> np.ndarray:
        y = x * p1 + np.random.randn(*x.shape) * p2
        z = np.fft.fft(y, axis=0)
        w = np.abs(z) * np.exp(1j * (np.angle(z) + 0.728))
        result = np.fft.ifft(w, axis=0)
        for _ in range(4):
            result = self.apply_nonlinear_map(result, 0.772)
        return result / (np.linalg.norm(result) + 1e-15)

    def method_mexican_hat_2_6(self, x: np.ndarray, p1=0.9716, p2=0.4120) -> np.ndarray:
        y = x * p1 + np.random.randn(*x.shape) * p2
        z = np.fft.fft(y, axis=0)
        w = np.abs(z) * np.exp(1j * (np.angle(z) + 0.883))
        result = np.fft.ifft(w, axis=0)
        for _ in range(3):
            result = self.apply_nonlinear_map(result, 0.979)
        return result / (np.linalg.norm(result) + 1e-15)

    def method_mexican_hat_2_7(self, x: np.ndarray, p1=0.8489, p2=0.4295) -> np.ndarray:
        y = x * p1 + np.random.randn(*x.shape) * p2
        z = np.fft.fft(y, axis=0)
        w = np.abs(z) * np.exp(1j * (np.angle(z) + 0.893))
        result = np.fft.ifft(w, axis=0)
        for _ in range(4):
            result = self.apply_nonlinear_map(result, 0.143)
        return result / (np.linalg.norm(result) + 1e-15)

    def method_mexican_hat_2_8(self, x: np.ndarray, p1=0.1158, p2=0.0745) -> np.ndarray:
        y = x * p1 + np.random.randn(*x.shape) * p2
        z = np.fft.fft(y, axis=0)
        w = np.abs(z) * np.exp(1j * (np.angle(z) + 0.219))
        result = np.fft.ifft(w, axis=0)
        for _ in range(4):
            result = self.apply_nonlinear_map(result, 0.463)
        return result / (np.linalg.norm(result) + 1e-15)

    def method_mexican_hat_2_9(self, x: np.ndarray, p1=0.4064, p2=0.2940) -> np.ndarray:
        y = x * p1 + np.random.randn(*x.shape) * p2
        z = np.fft.fft(y, axis=0)
        w = np.abs(z) * np.exp(1j * (np.angle(z) + 0.727))
        result = np.fft.ifft(w, axis=0)
        for _ in range(3):
            result = self.apply_nonlinear_map(result, 0.311)
        return result / (np.linalg.norm(result) + 1e-15)

    def method_mexican_hat_2_10(self, x: np.ndarray, p1=0.4062, p2=0.3835) -> np.ndarray:
        y = x * p1 + np.random.randn(*x.shape) * p2
        z = np.fft.fft(y, axis=0)
        w = np.abs(z) * np.exp(1j * (np.angle(z) + 0.297))
        result = np.fft.ifft(w, axis=0)
        for _ in range(7):
            result = self.apply_nonlinear_map(result, 0.979)
        return result / (np.linalg.norm(result) + 1e-15)

    def method_mexican_hat_2_11(self, x: np.ndarray, p1=0.8171, p2=0.0514) -> np.ndarray:
        y = x * p1 + np.random.randn(*x.shape) * p2
        z = np.fft.fft(y, axis=0)
        w = np.abs(z) * np.exp(1j * (np.angle(z) + 0.154))
        result = np.fft.ifft(w, axis=0)
        for _ in range(6):
            result = self.apply_nonlinear_map(result, 0.530)
        return result / (np.linalg.norm(result) + 1e-15)

    def method_mexican_hat_2_12(self, x: np.ndarray, p1=0.1709, p2=0.9836) -> np.ndarray:
        y = x * p1 + np.random.randn(*x.shape) * p2
        z = np.fft.fft(y, axis=0)
        w = np.abs(z) * np.exp(1j * (np.angle(z) + 0.294))
        result = np.fft.ifft(w, axis=0)
        for _ in range(8):
            result = self.apply_nonlinear_map(result, 0.056)
        return result / (np.linalg.norm(result) + 1e-15)

    def method_mexican_hat_2_13(self, x: np.ndarray, p1=0.2957, p2=0.2345) -> np.ndarray:
        y = x * p1 + np.random.randn(*x.shape) * p2
        z = np.fft.fft(y, axis=0)
        w = np.abs(z) * np.exp(1j * (np.angle(z) + 0.433))
        result = np.fft.ifft(w, axis=0)
        for _ in range(7):
            result = self.apply_nonlinear_map(result, 0.944)
        return result / (np.linalg.norm(result) + 1e-15)

    def method_mexican_hat_2_14(self, x: np.ndarray, p1=0.4521, p2=0.1862) -> np.ndarray:
        y = x * p1 + np.random.randn(*x.shape) * p2
        z = np.fft.fft(y, axis=0)
        w = np.abs(z) * np.exp(1j * (np.angle(z) + 0.857))
        result = np.fft.ifft(w, axis=0)
        for _ in range(2):
            result = self.apply_nonlinear_map(result, 0.959)
        return result / (np.linalg.norm(result) + 1e-15)

    def method_mexican_hat_2_15(self, x: np.ndarray, p1=0.3144, p2=0.7390) -> np.ndarray:
        y = x * p1 + np.random.randn(*x.shape) * p2
        z = np.fft.fft(y, axis=0)
        w = np.abs(z) * np.exp(1j * (np.angle(z) + 0.657))
        result = np.fft.ifft(w, axis=0)
        for _ in range(2):
            result = self.apply_nonlinear_map(result, 0.102)
        return result / (np.linalg.norm(result) + 1e-15)

    def method_mexican_hat_2_16(self, x: np.ndarray, p1=0.4195, p2=0.1300) -> np.ndarray:
        y = x * p1 + np.random.randn(*x.shape) * p2
        z = np.fft.fft(y, axis=0)
        w = np.abs(z) * np.exp(1j * (np.angle(z) + 0.946))
        result = np.fft.ifft(w, axis=0)
        for _ in range(3):
            result = self.apply_nonlinear_map(result, 0.562)
        return result / (np.linalg.norm(result) + 1e-15)

    def method_mexican_hat_2_17(self, x: np.ndarray, p1=0.9476, p2=0.8587) -> np.ndarray:
        y = x * p1 + np.random.randn(*x.shape) * p2
        z = np.fft.fft(y, axis=0)
        w = np.abs(z) * np.exp(1j * (np.angle(z) + 0.748))
        result = np.fft.ifft(w, axis=0)
        for _ in range(4):
            result = self.apply_nonlinear_map(result, 0.504)
        return result / (np.linalg.norm(result) + 1e-15)

    def method_mexican_hat_2_18(self, x: np.ndarray, p1=0.7854, p2=0.0699) -> np.ndarray:
        y = x * p1 + np.random.randn(*x.shape) * p2
        z = np.fft.fft(y, axis=0)
        w = np.abs(z) * np.exp(1j * (np.angle(z) + 0.157))
        result = np.fft.ifft(w, axis=0)
        for _ in range(3):
            result = self.apply_nonlinear_map(result, 0.927)
        return result / (np.linalg.norm(result) + 1e-15)

    def method_mexican_hat_2_19(self, x: np.ndarray, p1=0.6465, p2=0.5240) -> np.ndarray:
        y = x * p1 + np.random.randn(*x.shape) * p2
        z = np.fft.fft(y, axis=0)
        w = np.abs(z) * np.exp(1j * (np.angle(z) + 0.260))
        result = np.fft.ifft(w, axis=0)
        for _ in range(2):
            result = self.apply_nonlinear_map(result, 0.874)
        return result / (np.linalg.norm(result) + 1e-15)

    def method_mexican_hat_2_20(self, x: np.ndarray, p1=0.2550, p2=0.4408) -> np.ndarray:
        y = x * p1 + np.random.randn(*x.shape) * p2
        z = np.fft.fft(y, axis=0)
        w = np.abs(z) * np.exp(1j * (np.angle(z) + 0.751))
        result = np.fft.ifft(w, axis=0)
        for _ in range(6):
            result = self.apply_nonlinear_map(result, 0.907)
        return result / (np.linalg.norm(result) + 1e-15)

    def method_mexican_hat_2_21(self, x: np.ndarray, p1=0.3701, p2=0.8753) -> np.ndarray:
        y = x * p1 + np.random.randn(*x.shape) * p2
        z = np.fft.fft(y, axis=0)
        w = np.abs(z) * np.exp(1j * (np.angle(z) + 0.714))
        result = np.fft.ifft(w, axis=0)
        for _ in range(3):
            result = self.apply_nonlinear_map(result, 0.393)
        return result / (np.linalg.norm(result) + 1e-15)

    def method_mexican_hat_2_22(self, x: np.ndarray, p1=0.2273, p2=0.2715) -> np.ndarray:
        y = x * p1 + np.random.randn(*x.shape) * p2
        z = np.fft.fft(y, axis=0)
        w = np.abs(z) * np.exp(1j * (np.angle(z) + 0.698))
        result = np.fft.ifft(w, axis=0)
        for _ in range(3):
            result = self.apply_nonlinear_map(result, 0.460)
        return result / (np.linalg.norm(result) + 1e-15)

    def method_mexican_hat_2_23(self, x: np.ndarray, p1=0.4150, p2=0.0229) -> np.ndarray:
        y = x * p1 + np.random.randn(*x.shape) * p2
        z = np.fft.fft(y, axis=0)
        w = np.abs(z) * np.exp(1j * (np.angle(z) + 0.364))
        result = np.fft.ifft(w, axis=0)
        for _ in range(7):
            result = self.apply_nonlinear_map(result, 0.051)
        return result / (np.linalg.norm(result) + 1e-15)

    def method_mexican_hat_2_24(self, x: np.ndarray, p1=0.6273, p2=0.4536) -> np.ndarray:
        y = x * p1 + np.random.randn(*x.shape) * p2
        z = np.fft.fft(y, axis=0)
        w = np.abs(z) * np.exp(1j * (np.angle(z) + 0.475))
        result = np.fft.ifft(w, axis=0)
        for _ in range(7):
            result = self.apply_nonlinear_map(result, 0.797)
        return result / (np.linalg.norm(result) + 1e-15)

    def method_mexican_hat_2_25(self, x: np.ndarray, p1=0.0718, p2=0.7024) -> np.ndarray:
        y = x * p1 + np.random.randn(*x.shape) * p2
        z = np.fft.fft(y, axis=0)
        w = np.abs(z) * np.exp(1j * (np.angle(z) + 0.556))
        result = np.fft.ifft(w, axis=0)
        for _ in range(5):
            result = self.apply_nonlinear_map(result, 0.973)
        return result / (np.linalg.norm(result) + 1e-15)

    def method_mexican_hat_2_26(self, x: np.ndarray, p1=0.2915, p2=0.2561) -> np.ndarray:
        y = x * p1 + np.random.randn(*x.shape) * p2
        z = np.fft.fft(y, axis=0)
        w = np.abs(z) * np.exp(1j * (np.angle(z) + 0.432))
        result = np.fft.ifft(w, axis=0)
        for _ in range(5):
            result = self.apply_nonlinear_map(result, 0.785)
        return result / (np.linalg.norm(result) + 1e-15)

    def method_mexican_hat_2_27(self, x: np.ndarray, p1=0.5881, p2=0.0624) -> np.ndarray:
        y = x * p1 + np.random.randn(*x.shape) * p2
        z = np.fft.fft(y, axis=0)
        w = np.abs(z) * np.exp(1j * (np.angle(z) + 0.249))
        result = np.fft.ifft(w, axis=0)
        for _ in range(7):
            result = self.apply_nonlinear_map(result, 0.917)
        return result / (np.linalg.norm(result) + 1e-15)

    def method_mexican_hat_2_28(self, x: np.ndarray, p1=0.0559, p2=0.1270) -> np.ndarray:
        y = x * p1 + np.random.randn(*x.shape) * p2
        z = np.fft.fft(y, axis=0)
        w = np.abs(z) * np.exp(1j * (np.angle(z) + 0.848))
        result = np.fft.ifft(w, axis=0)
        for _ in range(8):
            result = self.apply_nonlinear_map(result, 0.295)
        return result / (np.linalg.norm(result) + 1e-15)

    def method_mexican_hat_2_29(self, x: np.ndarray, p1=0.8236, p2=0.3346) -> np.ndarray:
        y = x * p1 + np.random.randn(*x.shape) * p2
        z = np.fft.fft(y, axis=0)
        w = np.abs(z) * np.exp(1j * (np.angle(z) + 0.024))
        result = np.fft.ifft(w, axis=0)
        for _ in range(6):
            result = self.apply_nonlinear_map(result, 0.473)
        return result / (np.linalg.norm(result) + 1e-15)

    def method_mexican_hat_2_30(self, x: np.ndarray, p1=0.2331, p2=0.8911) -> np.ndarray:
        y = x * p1 + np.random.randn(*x.shape) * p2
        z = np.fft.fft(y, axis=0)
        w = np.abs(z) * np.exp(1j * (np.angle(z) + 0.113))
        result = np.fft.ifft(w, axis=0)
        for _ in range(6):
            result = self.apply_nonlinear_map(result, 0.894)
        return result / (np.linalg.norm(result) + 1e-15)

    def method_mexican_hat_2_31(self, x: np.ndarray, p1=0.4311, p2=0.3112) -> np.ndarray:
        y = x * p1 + np.random.randn(*x.shape) * p2
        z = np.fft.fft(y, axis=0)
        w = np.abs(z) * np.exp(1j * (np.angle(z) + 0.179))
        result = np.fft.ifft(w, axis=0)
        for _ in range(3):
            result = self.apply_nonlinear_map(result, 0.180)
        return result / (np.linalg.norm(result) + 1e-15)

    def method_mexican_hat_2_32(self, x: np.ndarray, p1=0.6461, p2=0.6403) -> np.ndarray:
        y = x * p1 + np.random.randn(*x.shape) * p2
        z = np.fft.fft(y, axis=0)
        w = np.abs(z) * np.exp(1j * (np.angle(z) + 0.447))
        result = np.fft.ifft(w, axis=0)
        for _ in range(3):
            result = self.apply_nonlinear_map(result, 0.641)
        return result / (np.linalg.norm(result) + 1e-15)

    def method_mexican_hat_2_33(self, x: np.ndarray, p1=0.5474, p2=0.3575) -> np.ndarray:
        y = x * p1 + np.random.randn(*x.shape) * p2
        z = np.fft.fft(y, axis=0)
        w = np.abs(z) * np.exp(1j * (np.angle(z) + 0.662))
        result = np.fft.ifft(w, axis=0)
        for _ in range(6):
            result = self.apply_nonlinear_map(result, 0.140)
        return result / (np.linalg.norm(result) + 1e-15)

    def method_mexican_hat_2_34(self, x: np.ndarray, p1=0.8538, p2=0.1332) -> np.ndarray:
        y = x * p1 + np.random.randn(*x.shape) * p2
        z = np.fft.fft(y, axis=0)
        w = np.abs(z) * np.exp(1j * (np.angle(z) + 0.569))
        result = np.fft.ifft(w, axis=0)
        for _ in range(6):
            result = self.apply_nonlinear_map(result, 0.723)
        return result / (np.linalg.norm(result) + 1e-15)

    def method_mexican_hat_2_35(self, x: np.ndarray, p1=0.4560, p2=0.8431) -> np.ndarray:
        y = x * p1 + np.random.randn(*x.shape) * p2
        z = np.fft.fft(y, axis=0)
        w = np.abs(z) * np.exp(1j * (np.angle(z) + 0.147))
        result = np.fft.ifft(w, axis=0)
        for _ in range(4):
            result = self.apply_nonlinear_map(result, 0.477)
        return result / (np.linalg.norm(result) + 1e-15)
