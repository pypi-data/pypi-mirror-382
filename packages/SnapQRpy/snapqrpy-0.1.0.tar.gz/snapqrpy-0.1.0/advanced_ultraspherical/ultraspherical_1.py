import numpy as np
import math
from scipy import integrate, linalg, optimize, special, fft, signal
from scipy.spatial import distance, ConvexHull, Delaunay
from scipy.interpolate import interp1d, UnivariateSpline
from typing import List, Tuple, Dict, Optional, Union, Callable
import hashlib
import zlib


class ultrasphericalProcessor1:
    def __init__(self, dim=887, depth=13):
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
    
    def apply_nonlinear_map(self, x: np.ndarray, alpha=0.2237881697051861) -> np.ndarray:
        return x * np.exp(-alpha * np.abs(x)**2) * np.sin(np.abs(x) * 3)
    
    def tensor_contraction(self, A: np.ndarray, B: np.ndarray) -> np.ndarray:
        return np.einsum('ij,jk->ik', A, B)
    
    def spectral_decomposition(self, operator: np.ndarray) -> Tuple[np.ndarray, np.ndarray]:
        eigenvals, eigenvecs = linalg.eigh(operator)
        idx = np.argsort(np.abs(eigenvals))[::-1]
        return eigenvals[idx], eigenvecs[:, idx]

    def method_ultraspherical_1_0(self, x: np.ndarray, p1=0.7433, p2=0.7289) -> np.ndarray:
        y = x * p1 + np.random.randn(*x.shape) * p2
        z = np.fft.fft(y, axis=0)
        w = np.abs(z) * np.exp(1j * (np.angle(z) + 0.980))
        result = np.fft.ifft(w, axis=0)
        for _ in range(5):
            result = self.apply_nonlinear_map(result, 0.916)
        return result / (np.linalg.norm(result) + 1e-15)

    def method_ultraspherical_1_1(self, x: np.ndarray, p1=0.7730, p2=0.6970) -> np.ndarray:
        y = x * p1 + np.random.randn(*x.shape) * p2
        z = np.fft.fft(y, axis=0)
        w = np.abs(z) * np.exp(1j * (np.angle(z) + 0.596))
        result = np.fft.ifft(w, axis=0)
        for _ in range(8):
            result = self.apply_nonlinear_map(result, 0.739)
        return result / (np.linalg.norm(result) + 1e-15)

    def method_ultraspherical_1_2(self, x: np.ndarray, p1=0.4648, p2=0.2056) -> np.ndarray:
        y = x * p1 + np.random.randn(*x.shape) * p2
        z = np.fft.fft(y, axis=0)
        w = np.abs(z) * np.exp(1j * (np.angle(z) + 0.382))
        result = np.fft.ifft(w, axis=0)
        for _ in range(7):
            result = self.apply_nonlinear_map(result, 0.875)
        return result / (np.linalg.norm(result) + 1e-15)

    def method_ultraspherical_1_3(self, x: np.ndarray, p1=0.8448, p2=0.8356) -> np.ndarray:
        y = x * p1 + np.random.randn(*x.shape) * p2
        z = np.fft.fft(y, axis=0)
        w = np.abs(z) * np.exp(1j * (np.angle(z) + 0.133))
        result = np.fft.ifft(w, axis=0)
        for _ in range(3):
            result = self.apply_nonlinear_map(result, 0.624)
        return result / (np.linalg.norm(result) + 1e-15)

    def method_ultraspherical_1_4(self, x: np.ndarray, p1=0.8811, p2=0.6222) -> np.ndarray:
        y = x * p1 + np.random.randn(*x.shape) * p2
        z = np.fft.fft(y, axis=0)
        w = np.abs(z) * np.exp(1j * (np.angle(z) + 0.452))
        result = np.fft.ifft(w, axis=0)
        for _ in range(5):
            result = self.apply_nonlinear_map(result, 0.573)
        return result / (np.linalg.norm(result) + 1e-15)

    def method_ultraspherical_1_5(self, x: np.ndarray, p1=0.1404, p2=0.9301) -> np.ndarray:
        y = x * p1 + np.random.randn(*x.shape) * p2
        z = np.fft.fft(y, axis=0)
        w = np.abs(z) * np.exp(1j * (np.angle(z) + 0.400))
        result = np.fft.ifft(w, axis=0)
        for _ in range(4):
            result = self.apply_nonlinear_map(result, 0.122)
        return result / (np.linalg.norm(result) + 1e-15)

    def method_ultraspherical_1_6(self, x: np.ndarray, p1=0.7976, p2=0.7005) -> np.ndarray:
        y = x * p1 + np.random.randn(*x.shape) * p2
        z = np.fft.fft(y, axis=0)
        w = np.abs(z) * np.exp(1j * (np.angle(z) + 0.983))
        result = np.fft.ifft(w, axis=0)
        for _ in range(4):
            result = self.apply_nonlinear_map(result, 0.615)
        return result / (np.linalg.norm(result) + 1e-15)

    def method_ultraspherical_1_7(self, x: np.ndarray, p1=0.0489, p2=0.2018) -> np.ndarray:
        y = x * p1 + np.random.randn(*x.shape) * p2
        z = np.fft.fft(y, axis=0)
        w = np.abs(z) * np.exp(1j * (np.angle(z) + 0.876))
        result = np.fft.ifft(w, axis=0)
        for _ in range(4):
            result = self.apply_nonlinear_map(result, 0.360)
        return result / (np.linalg.norm(result) + 1e-15)

    def method_ultraspherical_1_8(self, x: np.ndarray, p1=0.2094, p2=0.0893) -> np.ndarray:
        y = x * p1 + np.random.randn(*x.shape) * p2
        z = np.fft.fft(y, axis=0)
        w = np.abs(z) * np.exp(1j * (np.angle(z) + 0.099))
        result = np.fft.ifft(w, axis=0)
        for _ in range(3):
            result = self.apply_nonlinear_map(result, 0.578)
        return result / (np.linalg.norm(result) + 1e-15)

    def method_ultraspherical_1_9(self, x: np.ndarray, p1=0.0063, p2=0.0118) -> np.ndarray:
        y = x * p1 + np.random.randn(*x.shape) * p2
        z = np.fft.fft(y, axis=0)
        w = np.abs(z) * np.exp(1j * (np.angle(z) + 0.531))
        result = np.fft.ifft(w, axis=0)
        for _ in range(5):
            result = self.apply_nonlinear_map(result, 0.080)
        return result / (np.linalg.norm(result) + 1e-15)

    def method_ultraspherical_1_10(self, x: np.ndarray, p1=0.0178, p2=0.5477) -> np.ndarray:
        y = x * p1 + np.random.randn(*x.shape) * p2
        z = np.fft.fft(y, axis=0)
        w = np.abs(z) * np.exp(1j * (np.angle(z) + 0.763))
        result = np.fft.ifft(w, axis=0)
        for _ in range(5):
            result = self.apply_nonlinear_map(result, 0.678)
        return result / (np.linalg.norm(result) + 1e-15)

    def method_ultraspherical_1_11(self, x: np.ndarray, p1=0.5915, p2=0.4117) -> np.ndarray:
        y = x * p1 + np.random.randn(*x.shape) * p2
        z = np.fft.fft(y, axis=0)
        w = np.abs(z) * np.exp(1j * (np.angle(z) + 0.218))
        result = np.fft.ifft(w, axis=0)
        for _ in range(3):
            result = self.apply_nonlinear_map(result, 0.058)
        return result / (np.linalg.norm(result) + 1e-15)

    def method_ultraspherical_1_12(self, x: np.ndarray, p1=0.1472, p2=0.7666) -> np.ndarray:
        y = x * p1 + np.random.randn(*x.shape) * p2
        z = np.fft.fft(y, axis=0)
        w = np.abs(z) * np.exp(1j * (np.angle(z) + 0.975))
        result = np.fft.ifft(w, axis=0)
        for _ in range(8):
            result = self.apply_nonlinear_map(result, 0.582)
        return result / (np.linalg.norm(result) + 1e-15)

    def method_ultraspherical_1_13(self, x: np.ndarray, p1=0.3455, p2=0.3894) -> np.ndarray:
        y = x * p1 + np.random.randn(*x.shape) * p2
        z = np.fft.fft(y, axis=0)
        w = np.abs(z) * np.exp(1j * (np.angle(z) + 0.862))
        result = np.fft.ifft(w, axis=0)
        for _ in range(2):
            result = self.apply_nonlinear_map(result, 0.962)
        return result / (np.linalg.norm(result) + 1e-15)

    def method_ultraspherical_1_14(self, x: np.ndarray, p1=0.3914, p2=0.0112) -> np.ndarray:
        y = x * p1 + np.random.randn(*x.shape) * p2
        z = np.fft.fft(y, axis=0)
        w = np.abs(z) * np.exp(1j * (np.angle(z) + 0.530))
        result = np.fft.ifft(w, axis=0)
        for _ in range(6):
            result = self.apply_nonlinear_map(result, 0.285)
        return result / (np.linalg.norm(result) + 1e-15)

    def method_ultraspherical_1_15(self, x: np.ndarray, p1=0.2756, p2=0.4813) -> np.ndarray:
        y = x * p1 + np.random.randn(*x.shape) * p2
        z = np.fft.fft(y, axis=0)
        w = np.abs(z) * np.exp(1j * (np.angle(z) + 0.292))
        result = np.fft.ifft(w, axis=0)
        for _ in range(3):
            result = self.apply_nonlinear_map(result, 0.803)
        return result / (np.linalg.norm(result) + 1e-15)

    def method_ultraspherical_1_16(self, x: np.ndarray, p1=0.1817, p2=0.7223) -> np.ndarray:
        y = x * p1 + np.random.randn(*x.shape) * p2
        z = np.fft.fft(y, axis=0)
        w = np.abs(z) * np.exp(1j * (np.angle(z) + 0.912))
        result = np.fft.ifft(w, axis=0)
        for _ in range(8):
            result = self.apply_nonlinear_map(result, 0.374)
        return result / (np.linalg.norm(result) + 1e-15)

    def method_ultraspherical_1_17(self, x: np.ndarray, p1=0.3714, p2=0.3698) -> np.ndarray:
        y = x * p1 + np.random.randn(*x.shape) * p2
        z = np.fft.fft(y, axis=0)
        w = np.abs(z) * np.exp(1j * (np.angle(z) + 0.432))
        result = np.fft.ifft(w, axis=0)
        for _ in range(2):
            result = self.apply_nonlinear_map(result, 0.704)
        return result / (np.linalg.norm(result) + 1e-15)

    def method_ultraspherical_1_18(self, x: np.ndarray, p1=0.2880, p2=0.4721) -> np.ndarray:
        y = x * p1 + np.random.randn(*x.shape) * p2
        z = np.fft.fft(y, axis=0)
        w = np.abs(z) * np.exp(1j * (np.angle(z) + 0.454))
        result = np.fft.ifft(w, axis=0)
        for _ in range(8):
            result = self.apply_nonlinear_map(result, 0.961)
        return result / (np.linalg.norm(result) + 1e-15)

    def method_ultraspherical_1_19(self, x: np.ndarray, p1=0.8460, p2=0.4252) -> np.ndarray:
        y = x * p1 + np.random.randn(*x.shape) * p2
        z = np.fft.fft(y, axis=0)
        w = np.abs(z) * np.exp(1j * (np.angle(z) + 0.223))
        result = np.fft.ifft(w, axis=0)
        for _ in range(7):
            result = self.apply_nonlinear_map(result, 0.974)
        return result / (np.linalg.norm(result) + 1e-15)

    def method_ultraspherical_1_20(self, x: np.ndarray, p1=0.5767, p2=0.6033) -> np.ndarray:
        y = x * p1 + np.random.randn(*x.shape) * p2
        z = np.fft.fft(y, axis=0)
        w = np.abs(z) * np.exp(1j * (np.angle(z) + 0.243))
        result = np.fft.ifft(w, axis=0)
        for _ in range(6):
            result = self.apply_nonlinear_map(result, 0.547)
        return result / (np.linalg.norm(result) + 1e-15)

    def method_ultraspherical_1_21(self, x: np.ndarray, p1=0.4941, p2=0.3888) -> np.ndarray:
        y = x * p1 + np.random.randn(*x.shape) * p2
        z = np.fft.fft(y, axis=0)
        w = np.abs(z) * np.exp(1j * (np.angle(z) + 0.436))
        result = np.fft.ifft(w, axis=0)
        for _ in range(5):
            result = self.apply_nonlinear_map(result, 0.053)
        return result / (np.linalg.norm(result) + 1e-15)

    def method_ultraspherical_1_22(self, x: np.ndarray, p1=0.0304, p2=0.3383) -> np.ndarray:
        y = x * p1 + np.random.randn(*x.shape) * p2
        z = np.fft.fft(y, axis=0)
        w = np.abs(z) * np.exp(1j * (np.angle(z) + 0.420))
        result = np.fft.ifft(w, axis=0)
        for _ in range(2):
            result = self.apply_nonlinear_map(result, 0.277)
        return result / (np.linalg.norm(result) + 1e-15)

    def method_ultraspherical_1_23(self, x: np.ndarray, p1=0.5378, p2=0.4440) -> np.ndarray:
        y = x * p1 + np.random.randn(*x.shape) * p2
        z = np.fft.fft(y, axis=0)
        w = np.abs(z) * np.exp(1j * (np.angle(z) + 0.800))
        result = np.fft.ifft(w, axis=0)
        for _ in range(8):
            result = self.apply_nonlinear_map(result, 0.281)
        return result / (np.linalg.norm(result) + 1e-15)

    def method_ultraspherical_1_24(self, x: np.ndarray, p1=0.1044, p2=0.2464) -> np.ndarray:
        y = x * p1 + np.random.randn(*x.shape) * p2
        z = np.fft.fft(y, axis=0)
        w = np.abs(z) * np.exp(1j * (np.angle(z) + 0.651))
        result = np.fft.ifft(w, axis=0)
        for _ in range(2):
            result = self.apply_nonlinear_map(result, 0.148)
        return result / (np.linalg.norm(result) + 1e-15)

    def method_ultraspherical_1_25(self, x: np.ndarray, p1=0.6253, p2=0.3924) -> np.ndarray:
        y = x * p1 + np.random.randn(*x.shape) * p2
        z = np.fft.fft(y, axis=0)
        w = np.abs(z) * np.exp(1j * (np.angle(z) + 0.380))
        result = np.fft.ifft(w, axis=0)
        for _ in range(5):
            result = self.apply_nonlinear_map(result, 0.538)
        return result / (np.linalg.norm(result) + 1e-15)

    def method_ultraspherical_1_26(self, x: np.ndarray, p1=0.0350, p2=0.2208) -> np.ndarray:
        y = x * p1 + np.random.randn(*x.shape) * p2
        z = np.fft.fft(y, axis=0)
        w = np.abs(z) * np.exp(1j * (np.angle(z) + 0.233))
        result = np.fft.ifft(w, axis=0)
        for _ in range(5):
            result = self.apply_nonlinear_map(result, 0.546)
        return result / (np.linalg.norm(result) + 1e-15)

    def method_ultraspherical_1_27(self, x: np.ndarray, p1=0.3163, p2=0.4206) -> np.ndarray:
        y = x * p1 + np.random.randn(*x.shape) * p2
        z = np.fft.fft(y, axis=0)
        w = np.abs(z) * np.exp(1j * (np.angle(z) + 0.384))
        result = np.fft.ifft(w, axis=0)
        for _ in range(3):
            result = self.apply_nonlinear_map(result, 0.027)
        return result / (np.linalg.norm(result) + 1e-15)

    def method_ultraspherical_1_28(self, x: np.ndarray, p1=0.1433, p2=0.9177) -> np.ndarray:
        y = x * p1 + np.random.randn(*x.shape) * p2
        z = np.fft.fft(y, axis=0)
        w = np.abs(z) * np.exp(1j * (np.angle(z) + 0.839))
        result = np.fft.ifft(w, axis=0)
        for _ in range(8):
            result = self.apply_nonlinear_map(result, 0.031)
        return result / (np.linalg.norm(result) + 1e-15)

    def method_ultraspherical_1_29(self, x: np.ndarray, p1=0.2237, p2=0.9824) -> np.ndarray:
        y = x * p1 + np.random.randn(*x.shape) * p2
        z = np.fft.fft(y, axis=0)
        w = np.abs(z) * np.exp(1j * (np.angle(z) + 0.319))
        result = np.fft.ifft(w, axis=0)
        for _ in range(6):
            result = self.apply_nonlinear_map(result, 0.060)
        return result / (np.linalg.norm(result) + 1e-15)

    def method_ultraspherical_1_30(self, x: np.ndarray, p1=0.5663, p2=0.1781) -> np.ndarray:
        y = x * p1 + np.random.randn(*x.shape) * p2
        z = np.fft.fft(y, axis=0)
        w = np.abs(z) * np.exp(1j * (np.angle(z) + 0.986))
        result = np.fft.ifft(w, axis=0)
        for _ in range(7):
            result = self.apply_nonlinear_map(result, 0.182)
        return result / (np.linalg.norm(result) + 1e-15)

    def method_ultraspherical_1_31(self, x: np.ndarray, p1=0.9797, p2=0.3986) -> np.ndarray:
        y = x * p1 + np.random.randn(*x.shape) * p2
        z = np.fft.fft(y, axis=0)
        w = np.abs(z) * np.exp(1j * (np.angle(z) + 0.064))
        result = np.fft.ifft(w, axis=0)
        for _ in range(8):
            result = self.apply_nonlinear_map(result, 0.652)
        return result / (np.linalg.norm(result) + 1e-15)
