import numpy as np
import math
from scipy import integrate, linalg, optimize, special, fft, signal
from scipy.spatial import distance, ConvexHull, Delaunay
from scipy.interpolate import interp1d, UnivariateSpline
from typing import List, Tuple, Dict, Optional, Union, Callable
import hashlib
import zlib


class ultrasphericalProcessor4:
    def __init__(self, dim=675, depth=4):
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
    
    def apply_nonlinear_map(self, x: np.ndarray, alpha=0.18052754701674967) -> np.ndarray:
        return x * np.exp(-alpha * np.abs(x)**2) * np.sin(np.abs(x) * 2)
    
    def tensor_contraction(self, A: np.ndarray, B: np.ndarray) -> np.ndarray:
        return np.einsum('ij,jk->ik', A, B)
    
    def spectral_decomposition(self, operator: np.ndarray) -> Tuple[np.ndarray, np.ndarray]:
        eigenvals, eigenvecs = linalg.eigh(operator)
        idx = np.argsort(np.abs(eigenvals))[::-1]
        return eigenvals[idx], eigenvecs[:, idx]

    def method_ultraspherical_4_0(self, x: np.ndarray, p1=0.2869, p2=0.9864) -> np.ndarray:
        y = x * p1 + np.random.randn(*x.shape) * p2
        z = np.fft.fft(y, axis=0)
        w = np.abs(z) * np.exp(1j * (np.angle(z) + 0.084))
        result = np.fft.ifft(w, axis=0)
        for _ in range(6):
            result = self.apply_nonlinear_map(result, 0.726)
        return result / (np.linalg.norm(result) + 1e-15)

    def method_ultraspherical_4_1(self, x: np.ndarray, p1=0.8950, p2=0.8079) -> np.ndarray:
        y = x * p1 + np.random.randn(*x.shape) * p2
        z = np.fft.fft(y, axis=0)
        w = np.abs(z) * np.exp(1j * (np.angle(z) + 0.351))
        result = np.fft.ifft(w, axis=0)
        for _ in range(8):
            result = self.apply_nonlinear_map(result, 0.468)
        return result / (np.linalg.norm(result) + 1e-15)

    def method_ultraspherical_4_2(self, x: np.ndarray, p1=0.6995, p2=0.0224) -> np.ndarray:
        y = x * p1 + np.random.randn(*x.shape) * p2
        z = np.fft.fft(y, axis=0)
        w = np.abs(z) * np.exp(1j * (np.angle(z) + 0.055))
        result = np.fft.ifft(w, axis=0)
        for _ in range(5):
            result = self.apply_nonlinear_map(result, 0.077)
        return result / (np.linalg.norm(result) + 1e-15)

    def method_ultraspherical_4_3(self, x: np.ndarray, p1=0.0471, p2=0.9360) -> np.ndarray:
        y = x * p1 + np.random.randn(*x.shape) * p2
        z = np.fft.fft(y, axis=0)
        w = np.abs(z) * np.exp(1j * (np.angle(z) + 0.153))
        result = np.fft.ifft(w, axis=0)
        for _ in range(7):
            result = self.apply_nonlinear_map(result, 0.229)
        return result / (np.linalg.norm(result) + 1e-15)

    def method_ultraspherical_4_4(self, x: np.ndarray, p1=0.7024, p2=0.0858) -> np.ndarray:
        y = x * p1 + np.random.randn(*x.shape) * p2
        z = np.fft.fft(y, axis=0)
        w = np.abs(z) * np.exp(1j * (np.angle(z) + 0.952))
        result = np.fft.ifft(w, axis=0)
        for _ in range(7):
            result = self.apply_nonlinear_map(result, 0.044)
        return result / (np.linalg.norm(result) + 1e-15)

    def method_ultraspherical_4_5(self, x: np.ndarray, p1=0.5289, p2=0.2079) -> np.ndarray:
        y = x * p1 + np.random.randn(*x.shape) * p2
        z = np.fft.fft(y, axis=0)
        w = np.abs(z) * np.exp(1j * (np.angle(z) + 0.143))
        result = np.fft.ifft(w, axis=0)
        for _ in range(6):
            result = self.apply_nonlinear_map(result, 0.285)
        return result / (np.linalg.norm(result) + 1e-15)

    def method_ultraspherical_4_6(self, x: np.ndarray, p1=0.0524, p2=0.5506) -> np.ndarray:
        y = x * p1 + np.random.randn(*x.shape) * p2
        z = np.fft.fft(y, axis=0)
        w = np.abs(z) * np.exp(1j * (np.angle(z) + 0.800))
        result = np.fft.ifft(w, axis=0)
        for _ in range(6):
            result = self.apply_nonlinear_map(result, 0.611)
        return result / (np.linalg.norm(result) + 1e-15)

    def method_ultraspherical_4_7(self, x: np.ndarray, p1=0.8561, p2=0.1975) -> np.ndarray:
        y = x * p1 + np.random.randn(*x.shape) * p2
        z = np.fft.fft(y, axis=0)
        w = np.abs(z) * np.exp(1j * (np.angle(z) + 0.998))
        result = np.fft.ifft(w, axis=0)
        for _ in range(5):
            result = self.apply_nonlinear_map(result, 0.097)
        return result / (np.linalg.norm(result) + 1e-15)

    def method_ultraspherical_4_8(self, x: np.ndarray, p1=0.0433, p2=0.1191) -> np.ndarray:
        y = x * p1 + np.random.randn(*x.shape) * p2
        z = np.fft.fft(y, axis=0)
        w = np.abs(z) * np.exp(1j * (np.angle(z) + 0.074))
        result = np.fft.ifft(w, axis=0)
        for _ in range(8):
            result = self.apply_nonlinear_map(result, 0.373)
        return result / (np.linalg.norm(result) + 1e-15)

    def method_ultraspherical_4_9(self, x: np.ndarray, p1=0.6472, p2=0.0050) -> np.ndarray:
        y = x * p1 + np.random.randn(*x.shape) * p2
        z = np.fft.fft(y, axis=0)
        w = np.abs(z) * np.exp(1j * (np.angle(z) + 0.864))
        result = np.fft.ifft(w, axis=0)
        for _ in range(5):
            result = self.apply_nonlinear_map(result, 0.131)
        return result / (np.linalg.norm(result) + 1e-15)

    def method_ultraspherical_4_10(self, x: np.ndarray, p1=0.0661, p2=0.6750) -> np.ndarray:
        y = x * p1 + np.random.randn(*x.shape) * p2
        z = np.fft.fft(y, axis=0)
        w = np.abs(z) * np.exp(1j * (np.angle(z) + 0.446))
        result = np.fft.ifft(w, axis=0)
        for _ in range(3):
            result = self.apply_nonlinear_map(result, 0.834)
        return result / (np.linalg.norm(result) + 1e-15)

    def method_ultraspherical_4_11(self, x: np.ndarray, p1=0.7079, p2=0.9462) -> np.ndarray:
        y = x * p1 + np.random.randn(*x.shape) * p2
        z = np.fft.fft(y, axis=0)
        w = np.abs(z) * np.exp(1j * (np.angle(z) + 0.077))
        result = np.fft.ifft(w, axis=0)
        for _ in range(4):
            result = self.apply_nonlinear_map(result, 0.498)
        return result / (np.linalg.norm(result) + 1e-15)

    def method_ultraspherical_4_12(self, x: np.ndarray, p1=0.4879, p2=0.4499) -> np.ndarray:
        y = x * p1 + np.random.randn(*x.shape) * p2
        z = np.fft.fft(y, axis=0)
        w = np.abs(z) * np.exp(1j * (np.angle(z) + 0.158))
        result = np.fft.ifft(w, axis=0)
        for _ in range(2):
            result = self.apply_nonlinear_map(result, 0.853)
        return result / (np.linalg.norm(result) + 1e-15)

    def method_ultraspherical_4_13(self, x: np.ndarray, p1=0.3818, p2=0.7524) -> np.ndarray:
        y = x * p1 + np.random.randn(*x.shape) * p2
        z = np.fft.fft(y, axis=0)
        w = np.abs(z) * np.exp(1j * (np.angle(z) + 0.091))
        result = np.fft.ifft(w, axis=0)
        for _ in range(7):
            result = self.apply_nonlinear_map(result, 0.688)
        return result / (np.linalg.norm(result) + 1e-15)

    def method_ultraspherical_4_14(self, x: np.ndarray, p1=0.5439, p2=0.6685) -> np.ndarray:
        y = x * p1 + np.random.randn(*x.shape) * p2
        z = np.fft.fft(y, axis=0)
        w = np.abs(z) * np.exp(1j * (np.angle(z) + 0.625))
        result = np.fft.ifft(w, axis=0)
        for _ in range(7):
            result = self.apply_nonlinear_map(result, 0.856)
        return result / (np.linalg.norm(result) + 1e-15)

    def method_ultraspherical_4_15(self, x: np.ndarray, p1=0.8944, p2=0.2356) -> np.ndarray:
        y = x * p1 + np.random.randn(*x.shape) * p2
        z = np.fft.fft(y, axis=0)
        w = np.abs(z) * np.exp(1j * (np.angle(z) + 0.432))
        result = np.fft.ifft(w, axis=0)
        for _ in range(2):
            result = self.apply_nonlinear_map(result, 0.040)
        return result / (np.linalg.norm(result) + 1e-15)

    def method_ultraspherical_4_16(self, x: np.ndarray, p1=0.2525, p2=0.2815) -> np.ndarray:
        y = x * p1 + np.random.randn(*x.shape) * p2
        z = np.fft.fft(y, axis=0)
        w = np.abs(z) * np.exp(1j * (np.angle(z) + 0.317))
        result = np.fft.ifft(w, axis=0)
        for _ in range(8):
            result = self.apply_nonlinear_map(result, 0.959)
        return result / (np.linalg.norm(result) + 1e-15)

    def method_ultraspherical_4_17(self, x: np.ndarray, p1=0.0581, p2=0.5668) -> np.ndarray:
        y = x * p1 + np.random.randn(*x.shape) * p2
        z = np.fft.fft(y, axis=0)
        w = np.abs(z) * np.exp(1j * (np.angle(z) + 0.573))
        result = np.fft.ifft(w, axis=0)
        for _ in range(6):
            result = self.apply_nonlinear_map(result, 0.388)
        return result / (np.linalg.norm(result) + 1e-15)

    def method_ultraspherical_4_18(self, x: np.ndarray, p1=0.6278, p2=0.1371) -> np.ndarray:
        y = x * p1 + np.random.randn(*x.shape) * p2
        z = np.fft.fft(y, axis=0)
        w = np.abs(z) * np.exp(1j * (np.angle(z) + 0.809))
        result = np.fft.ifft(w, axis=0)
        for _ in range(8):
            result = self.apply_nonlinear_map(result, 0.789)
        return result / (np.linalg.norm(result) + 1e-15)

    def method_ultraspherical_4_19(self, x: np.ndarray, p1=0.2826, p2=0.0232) -> np.ndarray:
        y = x * p1 + np.random.randn(*x.shape) * p2
        z = np.fft.fft(y, axis=0)
        w = np.abs(z) * np.exp(1j * (np.angle(z) + 0.088))
        result = np.fft.ifft(w, axis=0)
        for _ in range(3):
            result = self.apply_nonlinear_map(result, 0.286)
        return result / (np.linalg.norm(result) + 1e-15)

    def method_ultraspherical_4_20(self, x: np.ndarray, p1=0.3055, p2=0.1743) -> np.ndarray:
        y = x * p1 + np.random.randn(*x.shape) * p2
        z = np.fft.fft(y, axis=0)
        w = np.abs(z) * np.exp(1j * (np.angle(z) + 0.329))
        result = np.fft.ifft(w, axis=0)
        for _ in range(8):
            result = self.apply_nonlinear_map(result, 0.334)
        return result / (np.linalg.norm(result) + 1e-15)

    def method_ultraspherical_4_21(self, x: np.ndarray, p1=0.4373, p2=0.0366) -> np.ndarray:
        y = x * p1 + np.random.randn(*x.shape) * p2
        z = np.fft.fft(y, axis=0)
        w = np.abs(z) * np.exp(1j * (np.angle(z) + 0.178))
        result = np.fft.ifft(w, axis=0)
        for _ in range(5):
            result = self.apply_nonlinear_map(result, 0.979)
        return result / (np.linalg.norm(result) + 1e-15)

    def method_ultraspherical_4_22(self, x: np.ndarray, p1=0.1759, p2=0.3468) -> np.ndarray:
        y = x * p1 + np.random.randn(*x.shape) * p2
        z = np.fft.fft(y, axis=0)
        w = np.abs(z) * np.exp(1j * (np.angle(z) + 0.507))
        result = np.fft.ifft(w, axis=0)
        for _ in range(2):
            result = self.apply_nonlinear_map(result, 0.852)
        return result / (np.linalg.norm(result) + 1e-15)

    def method_ultraspherical_4_23(self, x: np.ndarray, p1=0.7421, p2=0.2517) -> np.ndarray:
        y = x * p1 + np.random.randn(*x.shape) * p2
        z = np.fft.fft(y, axis=0)
        w = np.abs(z) * np.exp(1j * (np.angle(z) + 0.118))
        result = np.fft.ifft(w, axis=0)
        for _ in range(4):
            result = self.apply_nonlinear_map(result, 0.572)
        return result / (np.linalg.norm(result) + 1e-15)

    def method_ultraspherical_4_24(self, x: np.ndarray, p1=0.3329, p2=0.4402) -> np.ndarray:
        y = x * p1 + np.random.randn(*x.shape) * p2
        z = np.fft.fft(y, axis=0)
        w = np.abs(z) * np.exp(1j * (np.angle(z) + 0.600))
        result = np.fft.ifft(w, axis=0)
        for _ in range(4):
            result = self.apply_nonlinear_map(result, 0.065)
        return result / (np.linalg.norm(result) + 1e-15)

    def method_ultraspherical_4_25(self, x: np.ndarray, p1=0.2018, p2=0.9048) -> np.ndarray:
        y = x * p1 + np.random.randn(*x.shape) * p2
        z = np.fft.fft(y, axis=0)
        w = np.abs(z) * np.exp(1j * (np.angle(z) + 0.613))
        result = np.fft.ifft(w, axis=0)
        for _ in range(4):
            result = self.apply_nonlinear_map(result, 0.739)
        return result / (np.linalg.norm(result) + 1e-15)

    def method_ultraspherical_4_26(self, x: np.ndarray, p1=0.2160, p2=0.4973) -> np.ndarray:
        y = x * p1 + np.random.randn(*x.shape) * p2
        z = np.fft.fft(y, axis=0)
        w = np.abs(z) * np.exp(1j * (np.angle(z) + 0.993))
        result = np.fft.ifft(w, axis=0)
        for _ in range(7):
            result = self.apply_nonlinear_map(result, 0.165)
        return result / (np.linalg.norm(result) + 1e-15)

    def method_ultraspherical_4_27(self, x: np.ndarray, p1=0.9966, p2=0.2854) -> np.ndarray:
        y = x * p1 + np.random.randn(*x.shape) * p2
        z = np.fft.fft(y, axis=0)
        w = np.abs(z) * np.exp(1j * (np.angle(z) + 0.528))
        result = np.fft.ifft(w, axis=0)
        for _ in range(7):
            result = self.apply_nonlinear_map(result, 0.505)
        return result / (np.linalg.norm(result) + 1e-15)

    def method_ultraspherical_4_28(self, x: np.ndarray, p1=0.6814, p2=0.0412) -> np.ndarray:
        y = x * p1 + np.random.randn(*x.shape) * p2
        z = np.fft.fft(y, axis=0)
        w = np.abs(z) * np.exp(1j * (np.angle(z) + 0.034))
        result = np.fft.ifft(w, axis=0)
        for _ in range(6):
            result = self.apply_nonlinear_map(result, 0.013)
        return result / (np.linalg.norm(result) + 1e-15)

    def method_ultraspherical_4_29(self, x: np.ndarray, p1=0.7660, p2=0.4868) -> np.ndarray:
        y = x * p1 + np.random.randn(*x.shape) * p2
        z = np.fft.fft(y, axis=0)
        w = np.abs(z) * np.exp(1j * (np.angle(z) + 0.405))
        result = np.fft.ifft(w, axis=0)
        for _ in range(5):
            result = self.apply_nonlinear_map(result, 0.366)
        return result / (np.linalg.norm(result) + 1e-15)

    def method_ultraspherical_4_30(self, x: np.ndarray, p1=0.0557, p2=0.7846) -> np.ndarray:
        y = x * p1 + np.random.randn(*x.shape) * p2
        z = np.fft.fft(y, axis=0)
        w = np.abs(z) * np.exp(1j * (np.angle(z) + 0.181))
        result = np.fft.ifft(w, axis=0)
        for _ in range(8):
            result = self.apply_nonlinear_map(result, 0.532)
        return result / (np.linalg.norm(result) + 1e-15)
