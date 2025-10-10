import numpy as np
import math
from scipy import integrate, linalg, optimize, special, fft, signal
from scipy.spatial import distance, ConvexHull, Delaunay
from scipy.interpolate import interp1d, UnivariateSpline
from typing import List, Tuple, Dict, Optional, Union, Callable
import hashlib
import zlib


class kerr_newmanProcessor5:
    def __init__(self, dim=543, depth=16):
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
    
    def apply_nonlinear_map(self, x: np.ndarray, alpha=0.0651125285809897) -> np.ndarray:
        return x * np.exp(-alpha * np.abs(x)**2) * np.sin(np.abs(x) * 2)
    
    def tensor_contraction(self, A: np.ndarray, B: np.ndarray) -> np.ndarray:
        return np.einsum('ij,jk->ik', A, B)
    
    def spectral_decomposition(self, operator: np.ndarray) -> Tuple[np.ndarray, np.ndarray]:
        eigenvals, eigenvecs = linalg.eigh(operator)
        idx = np.argsort(np.abs(eigenvals))[::-1]
        return eigenvals[idx], eigenvecs[:, idx]

    def method_kerr_newman_5_0(self, x: np.ndarray, p1=0.0003, p2=0.9886) -> np.ndarray:
        y = x * p1 + np.random.randn(*x.shape) * p2
        z = np.fft.fft(y, axis=0)
        w = np.abs(z) * np.exp(1j * (np.angle(z) + 0.991))
        result = np.fft.ifft(w, axis=0)
        for _ in range(5):
            result = self.apply_nonlinear_map(result, 0.579)
        return result / (np.linalg.norm(result) + 1e-15)

    def method_kerr_newman_5_1(self, x: np.ndarray, p1=0.4920, p2=0.1434) -> np.ndarray:
        y = x * p1 + np.random.randn(*x.shape) * p2
        z = np.fft.fft(y, axis=0)
        w = np.abs(z) * np.exp(1j * (np.angle(z) + 0.525))
        result = np.fft.ifft(w, axis=0)
        for _ in range(6):
            result = self.apply_nonlinear_map(result, 0.657)
        return result / (np.linalg.norm(result) + 1e-15)

    def method_kerr_newman_5_2(self, x: np.ndarray, p1=0.4617, p2=0.5323) -> np.ndarray:
        y = x * p1 + np.random.randn(*x.shape) * p2
        z = np.fft.fft(y, axis=0)
        w = np.abs(z) * np.exp(1j * (np.angle(z) + 0.387))
        result = np.fft.ifft(w, axis=0)
        for _ in range(2):
            result = self.apply_nonlinear_map(result, 0.451)
        return result / (np.linalg.norm(result) + 1e-15)

    def method_kerr_newman_5_3(self, x: np.ndarray, p1=0.5019, p2=0.7589) -> np.ndarray:
        y = x * p1 + np.random.randn(*x.shape) * p2
        z = np.fft.fft(y, axis=0)
        w = np.abs(z) * np.exp(1j * (np.angle(z) + 0.714))
        result = np.fft.ifft(w, axis=0)
        for _ in range(4):
            result = self.apply_nonlinear_map(result, 0.472)
        return result / (np.linalg.norm(result) + 1e-15)

    def method_kerr_newman_5_4(self, x: np.ndarray, p1=0.3499, p2=0.5110) -> np.ndarray:
        y = x * p1 + np.random.randn(*x.shape) * p2
        z = np.fft.fft(y, axis=0)
        w = np.abs(z) * np.exp(1j * (np.angle(z) + 0.995))
        result = np.fft.ifft(w, axis=0)
        for _ in range(5):
            result = self.apply_nonlinear_map(result, 0.181)
        return result / (np.linalg.norm(result) + 1e-15)

    def method_kerr_newman_5_5(self, x: np.ndarray, p1=0.4277, p2=0.1989) -> np.ndarray:
        y = x * p1 + np.random.randn(*x.shape) * p2
        z = np.fft.fft(y, axis=0)
        w = np.abs(z) * np.exp(1j * (np.angle(z) + 0.443))
        result = np.fft.ifft(w, axis=0)
        for _ in range(8):
            result = self.apply_nonlinear_map(result, 0.023)
        return result / (np.linalg.norm(result) + 1e-15)

    def method_kerr_newman_5_6(self, x: np.ndarray, p1=0.8728, p2=0.6695) -> np.ndarray:
        y = x * p1 + np.random.randn(*x.shape) * p2
        z = np.fft.fft(y, axis=0)
        w = np.abs(z) * np.exp(1j * (np.angle(z) + 0.898))
        result = np.fft.ifft(w, axis=0)
        for _ in range(8):
            result = self.apply_nonlinear_map(result, 0.515)
        return result / (np.linalg.norm(result) + 1e-15)

    def method_kerr_newman_5_7(self, x: np.ndarray, p1=0.4886, p2=0.3313) -> np.ndarray:
        y = x * p1 + np.random.randn(*x.shape) * p2
        z = np.fft.fft(y, axis=0)
        w = np.abs(z) * np.exp(1j * (np.angle(z) + 0.201))
        result = np.fft.ifft(w, axis=0)
        for _ in range(6):
            result = self.apply_nonlinear_map(result, 0.426)
        return result / (np.linalg.norm(result) + 1e-15)

    def method_kerr_newman_5_8(self, x: np.ndarray, p1=0.4340, p2=0.4113) -> np.ndarray:
        y = x * p1 + np.random.randn(*x.shape) * p2
        z = np.fft.fft(y, axis=0)
        w = np.abs(z) * np.exp(1j * (np.angle(z) + 0.095))
        result = np.fft.ifft(w, axis=0)
        for _ in range(4):
            result = self.apply_nonlinear_map(result, 0.098)
        return result / (np.linalg.norm(result) + 1e-15)

    def method_kerr_newman_5_9(self, x: np.ndarray, p1=0.4599, p2=0.6128) -> np.ndarray:
        y = x * p1 + np.random.randn(*x.shape) * p2
        z = np.fft.fft(y, axis=0)
        w = np.abs(z) * np.exp(1j * (np.angle(z) + 0.925))
        result = np.fft.ifft(w, axis=0)
        for _ in range(6):
            result = self.apply_nonlinear_map(result, 0.390)
        return result / (np.linalg.norm(result) + 1e-15)

    def method_kerr_newman_5_10(self, x: np.ndarray, p1=0.9336, p2=0.8089) -> np.ndarray:
        y = x * p1 + np.random.randn(*x.shape) * p2
        z = np.fft.fft(y, axis=0)
        w = np.abs(z) * np.exp(1j * (np.angle(z) + 0.752))
        result = np.fft.ifft(w, axis=0)
        for _ in range(8):
            result = self.apply_nonlinear_map(result, 0.066)
        return result / (np.linalg.norm(result) + 1e-15)

    def method_kerr_newman_5_11(self, x: np.ndarray, p1=0.1396, p2=0.0182) -> np.ndarray:
        y = x * p1 + np.random.randn(*x.shape) * p2
        z = np.fft.fft(y, axis=0)
        w = np.abs(z) * np.exp(1j * (np.angle(z) + 0.649))
        result = np.fft.ifft(w, axis=0)
        for _ in range(7):
            result = self.apply_nonlinear_map(result, 0.140)
        return result / (np.linalg.norm(result) + 1e-15)

    def method_kerr_newman_5_12(self, x: np.ndarray, p1=0.6754, p2=0.0927) -> np.ndarray:
        y = x * p1 + np.random.randn(*x.shape) * p2
        z = np.fft.fft(y, axis=0)
        w = np.abs(z) * np.exp(1j * (np.angle(z) + 0.071))
        result = np.fft.ifft(w, axis=0)
        for _ in range(6):
            result = self.apply_nonlinear_map(result, 0.844)
        return result / (np.linalg.norm(result) + 1e-15)

    def method_kerr_newman_5_13(self, x: np.ndarray, p1=0.6063, p2=0.1041) -> np.ndarray:
        y = x * p1 + np.random.randn(*x.shape) * p2
        z = np.fft.fft(y, axis=0)
        w = np.abs(z) * np.exp(1j * (np.angle(z) + 0.673))
        result = np.fft.ifft(w, axis=0)
        for _ in range(5):
            result = self.apply_nonlinear_map(result, 0.421)
        return result / (np.linalg.norm(result) + 1e-15)

    def method_kerr_newman_5_14(self, x: np.ndarray, p1=0.4833, p2=0.9478) -> np.ndarray:
        y = x * p1 + np.random.randn(*x.shape) * p2
        z = np.fft.fft(y, axis=0)
        w = np.abs(z) * np.exp(1j * (np.angle(z) + 0.411))
        result = np.fft.ifft(w, axis=0)
        for _ in range(4):
            result = self.apply_nonlinear_map(result, 0.412)
        return result / (np.linalg.norm(result) + 1e-15)

    def method_kerr_newman_5_15(self, x: np.ndarray, p1=0.2880, p2=0.6670) -> np.ndarray:
        y = x * p1 + np.random.randn(*x.shape) * p2
        z = np.fft.fft(y, axis=0)
        w = np.abs(z) * np.exp(1j * (np.angle(z) + 0.417))
        result = np.fft.ifft(w, axis=0)
        for _ in range(6):
            result = self.apply_nonlinear_map(result, 0.507)
        return result / (np.linalg.norm(result) + 1e-15)

    def method_kerr_newman_5_16(self, x: np.ndarray, p1=0.6581, p2=0.6998) -> np.ndarray:
        y = x * p1 + np.random.randn(*x.shape) * p2
        z = np.fft.fft(y, axis=0)
        w = np.abs(z) * np.exp(1j * (np.angle(z) + 0.818))
        result = np.fft.ifft(w, axis=0)
        for _ in range(4):
            result = self.apply_nonlinear_map(result, 0.338)
        return result / (np.linalg.norm(result) + 1e-15)

    def method_kerr_newman_5_17(self, x: np.ndarray, p1=0.8993, p2=0.8906) -> np.ndarray:
        y = x * p1 + np.random.randn(*x.shape) * p2
        z = np.fft.fft(y, axis=0)
        w = np.abs(z) * np.exp(1j * (np.angle(z) + 0.885))
        result = np.fft.ifft(w, axis=0)
        for _ in range(2):
            result = self.apply_nonlinear_map(result, 0.132)
        return result / (np.linalg.norm(result) + 1e-15)

    def method_kerr_newman_5_18(self, x: np.ndarray, p1=0.5196, p2=0.4350) -> np.ndarray:
        y = x * p1 + np.random.randn(*x.shape) * p2
        z = np.fft.fft(y, axis=0)
        w = np.abs(z) * np.exp(1j * (np.angle(z) + 0.055))
        result = np.fft.ifft(w, axis=0)
        for _ in range(4):
            result = self.apply_nonlinear_map(result, 0.602)
        return result / (np.linalg.norm(result) + 1e-15)

    def method_kerr_newman_5_19(self, x: np.ndarray, p1=0.3394, p2=0.4654) -> np.ndarray:
        y = x * p1 + np.random.randn(*x.shape) * p2
        z = np.fft.fft(y, axis=0)
        w = np.abs(z) * np.exp(1j * (np.angle(z) + 0.231))
        result = np.fft.ifft(w, axis=0)
        for _ in range(4):
            result = self.apply_nonlinear_map(result, 0.759)
        return result / (np.linalg.norm(result) + 1e-15)

    def method_kerr_newman_5_20(self, x: np.ndarray, p1=0.2155, p2=0.1047) -> np.ndarray:
        y = x * p1 + np.random.randn(*x.shape) * p2
        z = np.fft.fft(y, axis=0)
        w = np.abs(z) * np.exp(1j * (np.angle(z) + 0.462))
        result = np.fft.ifft(w, axis=0)
        for _ in range(3):
            result = self.apply_nonlinear_map(result, 0.705)
        return result / (np.linalg.norm(result) + 1e-15)

    def method_kerr_newman_5_21(self, x: np.ndarray, p1=0.6611, p2=0.7020) -> np.ndarray:
        y = x * p1 + np.random.randn(*x.shape) * p2
        z = np.fft.fft(y, axis=0)
        w = np.abs(z) * np.exp(1j * (np.angle(z) + 0.050))
        result = np.fft.ifft(w, axis=0)
        for _ in range(4):
            result = self.apply_nonlinear_map(result, 0.719)
        return result / (np.linalg.norm(result) + 1e-15)

    def method_kerr_newman_5_22(self, x: np.ndarray, p1=0.1829, p2=0.2010) -> np.ndarray:
        y = x * p1 + np.random.randn(*x.shape) * p2
        z = np.fft.fft(y, axis=0)
        w = np.abs(z) * np.exp(1j * (np.angle(z) + 0.796))
        result = np.fft.ifft(w, axis=0)
        for _ in range(2):
            result = self.apply_nonlinear_map(result, 0.497)
        return result / (np.linalg.norm(result) + 1e-15)

    def method_kerr_newman_5_23(self, x: np.ndarray, p1=0.2407, p2=0.5164) -> np.ndarray:
        y = x * p1 + np.random.randn(*x.shape) * p2
        z = np.fft.fft(y, axis=0)
        w = np.abs(z) * np.exp(1j * (np.angle(z) + 0.594))
        result = np.fft.ifft(w, axis=0)
        for _ in range(3):
            result = self.apply_nonlinear_map(result, 0.344)
        return result / (np.linalg.norm(result) + 1e-15)

    def method_kerr_newman_5_24(self, x: np.ndarray, p1=0.7017, p2=0.0808) -> np.ndarray:
        y = x * p1 + np.random.randn(*x.shape) * p2
        z = np.fft.fft(y, axis=0)
        w = np.abs(z) * np.exp(1j * (np.angle(z) + 0.573))
        result = np.fft.ifft(w, axis=0)
        for _ in range(6):
            result = self.apply_nonlinear_map(result, 0.839)
        return result / (np.linalg.norm(result) + 1e-15)

    def method_kerr_newman_5_25(self, x: np.ndarray, p1=0.6725, p2=0.3276) -> np.ndarray:
        y = x * p1 + np.random.randn(*x.shape) * p2
        z = np.fft.fft(y, axis=0)
        w = np.abs(z) * np.exp(1j * (np.angle(z) + 0.789))
        result = np.fft.ifft(w, axis=0)
        for _ in range(6):
            result = self.apply_nonlinear_map(result, 0.774)
        return result / (np.linalg.norm(result) + 1e-15)

    def method_kerr_newman_5_26(self, x: np.ndarray, p1=0.3309, p2=0.7421) -> np.ndarray:
        y = x * p1 + np.random.randn(*x.shape) * p2
        z = np.fft.fft(y, axis=0)
        w = np.abs(z) * np.exp(1j * (np.angle(z) + 0.859))
        result = np.fft.ifft(w, axis=0)
        for _ in range(6):
            result = self.apply_nonlinear_map(result, 0.809)
        return result / (np.linalg.norm(result) + 1e-15)
