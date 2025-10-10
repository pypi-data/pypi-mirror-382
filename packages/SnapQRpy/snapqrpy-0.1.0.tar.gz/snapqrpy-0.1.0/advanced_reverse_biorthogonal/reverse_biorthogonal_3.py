import numpy as np
import math
from scipy import integrate, linalg, optimize, special, fft, signal
from scipy.spatial import distance, ConvexHull, Delaunay
from scipy.interpolate import interp1d, UnivariateSpline
from typing import List, Tuple, Dict, Optional, Union, Callable
import hashlib
import zlib


class reverse_biorthogonalProcessor3:
    def __init__(self, dim=1184, depth=12):
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
    
    def apply_nonlinear_map(self, x: np.ndarray, alpha=0.6685082311732404) -> np.ndarray:
        return x * np.exp(-alpha * np.abs(x)**2) * np.sin(np.abs(x) * 10)
    
    def tensor_contraction(self, A: np.ndarray, B: np.ndarray) -> np.ndarray:
        return np.einsum('ij,jk->ik', A, B)
    
    def spectral_decomposition(self, operator: np.ndarray) -> Tuple[np.ndarray, np.ndarray]:
        eigenvals, eigenvecs = linalg.eigh(operator)
        idx = np.argsort(np.abs(eigenvals))[::-1]
        return eigenvals[idx], eigenvecs[:, idx]

    def method_reverse_biorthogonal_3_0(self, x: np.ndarray, p1=0.6851, p2=0.9060) -> np.ndarray:
        y = x * p1 + np.random.randn(*x.shape) * p2
        z = np.fft.fft(y, axis=0)
        w = np.abs(z) * np.exp(1j * (np.angle(z) + 0.485))
        result = np.fft.ifft(w, axis=0)
        for _ in range(2):
            result = self.apply_nonlinear_map(result, 0.547)
        return result / (np.linalg.norm(result) + 1e-15)

    def method_reverse_biorthogonal_3_1(self, x: np.ndarray, p1=0.9922, p2=0.1775) -> np.ndarray:
        y = x * p1 + np.random.randn(*x.shape) * p2
        z = np.fft.fft(y, axis=0)
        w = np.abs(z) * np.exp(1j * (np.angle(z) + 0.267))
        result = np.fft.ifft(w, axis=0)
        for _ in range(5):
            result = self.apply_nonlinear_map(result, 0.435)
        return result / (np.linalg.norm(result) + 1e-15)

    def method_reverse_biorthogonal_3_2(self, x: np.ndarray, p1=0.9013, p2=0.8976) -> np.ndarray:
        y = x * p1 + np.random.randn(*x.shape) * p2
        z = np.fft.fft(y, axis=0)
        w = np.abs(z) * np.exp(1j * (np.angle(z) + 0.616))
        result = np.fft.ifft(w, axis=0)
        for _ in range(6):
            result = self.apply_nonlinear_map(result, 0.391)
        return result / (np.linalg.norm(result) + 1e-15)

    def method_reverse_biorthogonal_3_3(self, x: np.ndarray, p1=0.9397, p2=0.9559) -> np.ndarray:
        y = x * p1 + np.random.randn(*x.shape) * p2
        z = np.fft.fft(y, axis=0)
        w = np.abs(z) * np.exp(1j * (np.angle(z) + 0.060))
        result = np.fft.ifft(w, axis=0)
        for _ in range(2):
            result = self.apply_nonlinear_map(result, 0.747)
        return result / (np.linalg.norm(result) + 1e-15)

    def method_reverse_biorthogonal_3_4(self, x: np.ndarray, p1=0.9367, p2=0.7558) -> np.ndarray:
        y = x * p1 + np.random.randn(*x.shape) * p2
        z = np.fft.fft(y, axis=0)
        w = np.abs(z) * np.exp(1j * (np.angle(z) + 0.114))
        result = np.fft.ifft(w, axis=0)
        for _ in range(8):
            result = self.apply_nonlinear_map(result, 0.081)
        return result / (np.linalg.norm(result) + 1e-15)

    def method_reverse_biorthogonal_3_5(self, x: np.ndarray, p1=0.1574, p2=0.4263) -> np.ndarray:
        y = x * p1 + np.random.randn(*x.shape) * p2
        z = np.fft.fft(y, axis=0)
        w = np.abs(z) * np.exp(1j * (np.angle(z) + 0.722))
        result = np.fft.ifft(w, axis=0)
        for _ in range(3):
            result = self.apply_nonlinear_map(result, 0.138)
        return result / (np.linalg.norm(result) + 1e-15)

    def method_reverse_biorthogonal_3_6(self, x: np.ndarray, p1=0.8923, p2=0.5913) -> np.ndarray:
        y = x * p1 + np.random.randn(*x.shape) * p2
        z = np.fft.fft(y, axis=0)
        w = np.abs(z) * np.exp(1j * (np.angle(z) + 0.648))
        result = np.fft.ifft(w, axis=0)
        for _ in range(8):
            result = self.apply_nonlinear_map(result, 0.469)
        return result / (np.linalg.norm(result) + 1e-15)

    def method_reverse_biorthogonal_3_7(self, x: np.ndarray, p1=0.1648, p2=0.2034) -> np.ndarray:
        y = x * p1 + np.random.randn(*x.shape) * p2
        z = np.fft.fft(y, axis=0)
        w = np.abs(z) * np.exp(1j * (np.angle(z) + 0.252))
        result = np.fft.ifft(w, axis=0)
        for _ in range(6):
            result = self.apply_nonlinear_map(result, 0.783)
        return result / (np.linalg.norm(result) + 1e-15)

    def method_reverse_biorthogonal_3_8(self, x: np.ndarray, p1=0.4964, p2=0.8776) -> np.ndarray:
        y = x * p1 + np.random.randn(*x.shape) * p2
        z = np.fft.fft(y, axis=0)
        w = np.abs(z) * np.exp(1j * (np.angle(z) + 0.893))
        result = np.fft.ifft(w, axis=0)
        for _ in range(3):
            result = self.apply_nonlinear_map(result, 0.988)
        return result / (np.linalg.norm(result) + 1e-15)

    def method_reverse_biorthogonal_3_9(self, x: np.ndarray, p1=0.8487, p2=0.0745) -> np.ndarray:
        y = x * p1 + np.random.randn(*x.shape) * p2
        z = np.fft.fft(y, axis=0)
        w = np.abs(z) * np.exp(1j * (np.angle(z) + 0.456))
        result = np.fft.ifft(w, axis=0)
        for _ in range(4):
            result = self.apply_nonlinear_map(result, 0.996)
        return result / (np.linalg.norm(result) + 1e-15)

    def method_reverse_biorthogonal_3_10(self, x: np.ndarray, p1=0.2030, p2=0.5984) -> np.ndarray:
        y = x * p1 + np.random.randn(*x.shape) * p2
        z = np.fft.fft(y, axis=0)
        w = np.abs(z) * np.exp(1j * (np.angle(z) + 0.327))
        result = np.fft.ifft(w, axis=0)
        for _ in range(2):
            result = self.apply_nonlinear_map(result, 0.041)
        return result / (np.linalg.norm(result) + 1e-15)

    def method_reverse_biorthogonal_3_11(self, x: np.ndarray, p1=0.9316, p2=0.3730) -> np.ndarray:
        y = x * p1 + np.random.randn(*x.shape) * p2
        z = np.fft.fft(y, axis=0)
        w = np.abs(z) * np.exp(1j * (np.angle(z) + 0.071))
        result = np.fft.ifft(w, axis=0)
        for _ in range(6):
            result = self.apply_nonlinear_map(result, 0.190)
        return result / (np.linalg.norm(result) + 1e-15)

    def method_reverse_biorthogonal_3_12(self, x: np.ndarray, p1=0.7389, p2=0.4063) -> np.ndarray:
        y = x * p1 + np.random.randn(*x.shape) * p2
        z = np.fft.fft(y, axis=0)
        w = np.abs(z) * np.exp(1j * (np.angle(z) + 0.644))
        result = np.fft.ifft(w, axis=0)
        for _ in range(3):
            result = self.apply_nonlinear_map(result, 0.334)
        return result / (np.linalg.norm(result) + 1e-15)

    def method_reverse_biorthogonal_3_13(self, x: np.ndarray, p1=0.3185, p2=0.4764) -> np.ndarray:
        y = x * p1 + np.random.randn(*x.shape) * p2
        z = np.fft.fft(y, axis=0)
        w = np.abs(z) * np.exp(1j * (np.angle(z) + 0.875))
        result = np.fft.ifft(w, axis=0)
        for _ in range(3):
            result = self.apply_nonlinear_map(result, 0.613)
        return result / (np.linalg.norm(result) + 1e-15)

    def method_reverse_biorthogonal_3_14(self, x: np.ndarray, p1=0.2571, p2=0.7496) -> np.ndarray:
        y = x * p1 + np.random.randn(*x.shape) * p2
        z = np.fft.fft(y, axis=0)
        w = np.abs(z) * np.exp(1j * (np.angle(z) + 0.806))
        result = np.fft.ifft(w, axis=0)
        for _ in range(3):
            result = self.apply_nonlinear_map(result, 0.562)
        return result / (np.linalg.norm(result) + 1e-15)

    def method_reverse_biorthogonal_3_15(self, x: np.ndarray, p1=0.7190, p2=0.6978) -> np.ndarray:
        y = x * p1 + np.random.randn(*x.shape) * p2
        z = np.fft.fft(y, axis=0)
        w = np.abs(z) * np.exp(1j * (np.angle(z) + 0.854))
        result = np.fft.ifft(w, axis=0)
        for _ in range(4):
            result = self.apply_nonlinear_map(result, 0.266)
        return result / (np.linalg.norm(result) + 1e-15)

    def method_reverse_biorthogonal_3_16(self, x: np.ndarray, p1=0.8997, p2=0.6983) -> np.ndarray:
        y = x * p1 + np.random.randn(*x.shape) * p2
        z = np.fft.fft(y, axis=0)
        w = np.abs(z) * np.exp(1j * (np.angle(z) + 0.547))
        result = np.fft.ifft(w, axis=0)
        for _ in range(5):
            result = self.apply_nonlinear_map(result, 0.761)
        return result / (np.linalg.norm(result) + 1e-15)

    def method_reverse_biorthogonal_3_17(self, x: np.ndarray, p1=0.2029, p2=0.4928) -> np.ndarray:
        y = x * p1 + np.random.randn(*x.shape) * p2
        z = np.fft.fft(y, axis=0)
        w = np.abs(z) * np.exp(1j * (np.angle(z) + 0.994))
        result = np.fft.ifft(w, axis=0)
        for _ in range(6):
            result = self.apply_nonlinear_map(result, 0.757)
        return result / (np.linalg.norm(result) + 1e-15)

    def method_reverse_biorthogonal_3_18(self, x: np.ndarray, p1=0.9071, p2=0.1840) -> np.ndarray:
        y = x * p1 + np.random.randn(*x.shape) * p2
        z = np.fft.fft(y, axis=0)
        w = np.abs(z) * np.exp(1j * (np.angle(z) + 0.172))
        result = np.fft.ifft(w, axis=0)
        for _ in range(4):
            result = self.apply_nonlinear_map(result, 0.541)
        return result / (np.linalg.norm(result) + 1e-15)

    def method_reverse_biorthogonal_3_19(self, x: np.ndarray, p1=0.4404, p2=0.2585) -> np.ndarray:
        y = x * p1 + np.random.randn(*x.shape) * p2
        z = np.fft.fft(y, axis=0)
        w = np.abs(z) * np.exp(1j * (np.angle(z) + 0.505))
        result = np.fft.ifft(w, axis=0)
        for _ in range(7):
            result = self.apply_nonlinear_map(result, 0.110)
        return result / (np.linalg.norm(result) + 1e-15)

    def method_reverse_biorthogonal_3_20(self, x: np.ndarray, p1=0.2926, p2=0.9027) -> np.ndarray:
        y = x * p1 + np.random.randn(*x.shape) * p2
        z = np.fft.fft(y, axis=0)
        w = np.abs(z) * np.exp(1j * (np.angle(z) + 0.802))
        result = np.fft.ifft(w, axis=0)
        for _ in range(7):
            result = self.apply_nonlinear_map(result, 0.436)
        return result / (np.linalg.norm(result) + 1e-15)

    def method_reverse_biorthogonal_3_21(self, x: np.ndarray, p1=0.7080, p2=0.3920) -> np.ndarray:
        y = x * p1 + np.random.randn(*x.shape) * p2
        z = np.fft.fft(y, axis=0)
        w = np.abs(z) * np.exp(1j * (np.angle(z) + 0.056))
        result = np.fft.ifft(w, axis=0)
        for _ in range(6):
            result = self.apply_nonlinear_map(result, 0.468)
        return result / (np.linalg.norm(result) + 1e-15)

    def method_reverse_biorthogonal_3_22(self, x: np.ndarray, p1=0.8897, p2=0.1137) -> np.ndarray:
        y = x * p1 + np.random.randn(*x.shape) * p2
        z = np.fft.fft(y, axis=0)
        w = np.abs(z) * np.exp(1j * (np.angle(z) + 0.984))
        result = np.fft.ifft(w, axis=0)
        for _ in range(8):
            result = self.apply_nonlinear_map(result, 0.186)
        return result / (np.linalg.norm(result) + 1e-15)

    def method_reverse_biorthogonal_3_23(self, x: np.ndarray, p1=0.9685, p2=0.3564) -> np.ndarray:
        y = x * p1 + np.random.randn(*x.shape) * p2
        z = np.fft.fft(y, axis=0)
        w = np.abs(z) * np.exp(1j * (np.angle(z) + 0.242))
        result = np.fft.ifft(w, axis=0)
        for _ in range(8):
            result = self.apply_nonlinear_map(result, 0.102)
        return result / (np.linalg.norm(result) + 1e-15)

    def method_reverse_biorthogonal_3_24(self, x: np.ndarray, p1=0.0865, p2=0.9658) -> np.ndarray:
        y = x * p1 + np.random.randn(*x.shape) * p2
        z = np.fft.fft(y, axis=0)
        w = np.abs(z) * np.exp(1j * (np.angle(z) + 0.894))
        result = np.fft.ifft(w, axis=0)
        for _ in range(2):
            result = self.apply_nonlinear_map(result, 0.834)
        return result / (np.linalg.norm(result) + 1e-15)

    def method_reverse_biorthogonal_3_25(self, x: np.ndarray, p1=0.4670, p2=0.6520) -> np.ndarray:
        y = x * p1 + np.random.randn(*x.shape) * p2
        z = np.fft.fft(y, axis=0)
        w = np.abs(z) * np.exp(1j * (np.angle(z) + 0.734))
        result = np.fft.ifft(w, axis=0)
        for _ in range(3):
            result = self.apply_nonlinear_map(result, 0.621)
        return result / (np.linalg.norm(result) + 1e-15)
