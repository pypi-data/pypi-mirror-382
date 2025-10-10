import numpy as np
import math
from scipy import integrate, linalg, optimize, special, fft, signal
from scipy.spatial import distance, ConvexHull, Delaunay
from scipy.interpolate import interp1d, UnivariateSpline
from typing import List, Tuple, Dict, Optional, Union, Callable
import hashlib
import zlib


class subtree_kernelProcessor1:
    def __init__(self, dim=638, depth=16):
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
    
    def apply_nonlinear_map(self, x: np.ndarray, alpha=0.2143230294046501) -> np.ndarray:
        return x * np.exp(-alpha * np.abs(x)**2) * np.sin(np.abs(x) * 2)
    
    def tensor_contraction(self, A: np.ndarray, B: np.ndarray) -> np.ndarray:
        return np.einsum('ij,jk->ik', A, B)
    
    def spectral_decomposition(self, operator: np.ndarray) -> Tuple[np.ndarray, np.ndarray]:
        eigenvals, eigenvecs = linalg.eigh(operator)
        idx = np.argsort(np.abs(eigenvals))[::-1]
        return eigenvals[idx], eigenvecs[:, idx]

    def method_subtree_kernel_1_0(self, x: np.ndarray, p1=0.4255, p2=0.3921) -> np.ndarray:
        y = x * p1 + np.random.randn(*x.shape) * p2
        z = np.fft.fft(y, axis=0)
        w = np.abs(z) * np.exp(1j * (np.angle(z) + 0.078))
        result = np.fft.ifft(w, axis=0)
        for _ in range(5):
            result = self.apply_nonlinear_map(result, 0.376)
        return result / (np.linalg.norm(result) + 1e-15)

    def method_subtree_kernel_1_1(self, x: np.ndarray, p1=0.6021, p2=0.2160) -> np.ndarray:
        y = x * p1 + np.random.randn(*x.shape) * p2
        z = np.fft.fft(y, axis=0)
        w = np.abs(z) * np.exp(1j * (np.angle(z) + 0.435))
        result = np.fft.ifft(w, axis=0)
        for _ in range(7):
            result = self.apply_nonlinear_map(result, 0.703)
        return result / (np.linalg.norm(result) + 1e-15)

    def method_subtree_kernel_1_2(self, x: np.ndarray, p1=0.2272, p2=0.7516) -> np.ndarray:
        y = x * p1 + np.random.randn(*x.shape) * p2
        z = np.fft.fft(y, axis=0)
        w = np.abs(z) * np.exp(1j * (np.angle(z) + 0.216))
        result = np.fft.ifft(w, axis=0)
        for _ in range(2):
            result = self.apply_nonlinear_map(result, 0.498)
        return result / (np.linalg.norm(result) + 1e-15)

    def method_subtree_kernel_1_3(self, x: np.ndarray, p1=0.7378, p2=0.7621) -> np.ndarray:
        y = x * p1 + np.random.randn(*x.shape) * p2
        z = np.fft.fft(y, axis=0)
        w = np.abs(z) * np.exp(1j * (np.angle(z) + 0.303))
        result = np.fft.ifft(w, axis=0)
        for _ in range(2):
            result = self.apply_nonlinear_map(result, 0.407)
        return result / (np.linalg.norm(result) + 1e-15)

    def method_subtree_kernel_1_4(self, x: np.ndarray, p1=0.9716, p2=0.3040) -> np.ndarray:
        y = x * p1 + np.random.randn(*x.shape) * p2
        z = np.fft.fft(y, axis=0)
        w = np.abs(z) * np.exp(1j * (np.angle(z) + 0.255))
        result = np.fft.ifft(w, axis=0)
        for _ in range(5):
            result = self.apply_nonlinear_map(result, 0.527)
        return result / (np.linalg.norm(result) + 1e-15)

    def method_subtree_kernel_1_5(self, x: np.ndarray, p1=0.4811, p2=0.6803) -> np.ndarray:
        y = x * p1 + np.random.randn(*x.shape) * p2
        z = np.fft.fft(y, axis=0)
        w = np.abs(z) * np.exp(1j * (np.angle(z) + 0.037))
        result = np.fft.ifft(w, axis=0)
        for _ in range(2):
            result = self.apply_nonlinear_map(result, 0.943)
        return result / (np.linalg.norm(result) + 1e-15)

    def method_subtree_kernel_1_6(self, x: np.ndarray, p1=0.7618, p2=0.1392) -> np.ndarray:
        y = x * p1 + np.random.randn(*x.shape) * p2
        z = np.fft.fft(y, axis=0)
        w = np.abs(z) * np.exp(1j * (np.angle(z) + 0.547))
        result = np.fft.ifft(w, axis=0)
        for _ in range(8):
            result = self.apply_nonlinear_map(result, 0.891)
        return result / (np.linalg.norm(result) + 1e-15)

    def method_subtree_kernel_1_7(self, x: np.ndarray, p1=0.6300, p2=0.6572) -> np.ndarray:
        y = x * p1 + np.random.randn(*x.shape) * p2
        z = np.fft.fft(y, axis=0)
        w = np.abs(z) * np.exp(1j * (np.angle(z) + 0.610))
        result = np.fft.ifft(w, axis=0)
        for _ in range(4):
            result = self.apply_nonlinear_map(result, 0.900)
        return result / (np.linalg.norm(result) + 1e-15)

    def method_subtree_kernel_1_8(self, x: np.ndarray, p1=0.5817, p2=0.6788) -> np.ndarray:
        y = x * p1 + np.random.randn(*x.shape) * p2
        z = np.fft.fft(y, axis=0)
        w = np.abs(z) * np.exp(1j * (np.angle(z) + 0.402))
        result = np.fft.ifft(w, axis=0)
        for _ in range(2):
            result = self.apply_nonlinear_map(result, 0.793)
        return result / (np.linalg.norm(result) + 1e-15)

    def method_subtree_kernel_1_9(self, x: np.ndarray, p1=0.8633, p2=0.8062) -> np.ndarray:
        y = x * p1 + np.random.randn(*x.shape) * p2
        z = np.fft.fft(y, axis=0)
        w = np.abs(z) * np.exp(1j * (np.angle(z) + 0.068))
        result = np.fft.ifft(w, axis=0)
        for _ in range(6):
            result = self.apply_nonlinear_map(result, 0.807)
        return result / (np.linalg.norm(result) + 1e-15)

    def method_subtree_kernel_1_10(self, x: np.ndarray, p1=0.8505, p2=0.1881) -> np.ndarray:
        y = x * p1 + np.random.randn(*x.shape) * p2
        z = np.fft.fft(y, axis=0)
        w = np.abs(z) * np.exp(1j * (np.angle(z) + 0.551))
        result = np.fft.ifft(w, axis=0)
        for _ in range(8):
            result = self.apply_nonlinear_map(result, 0.700)
        return result / (np.linalg.norm(result) + 1e-15)

    def method_subtree_kernel_1_11(self, x: np.ndarray, p1=0.8109, p2=0.7317) -> np.ndarray:
        y = x * p1 + np.random.randn(*x.shape) * p2
        z = np.fft.fft(y, axis=0)
        w = np.abs(z) * np.exp(1j * (np.angle(z) + 0.974))
        result = np.fft.ifft(w, axis=0)
        for _ in range(8):
            result = self.apply_nonlinear_map(result, 0.434)
        return result / (np.linalg.norm(result) + 1e-15)

    def method_subtree_kernel_1_12(self, x: np.ndarray, p1=0.1730, p2=0.9521) -> np.ndarray:
        y = x * p1 + np.random.randn(*x.shape) * p2
        z = np.fft.fft(y, axis=0)
        w = np.abs(z) * np.exp(1j * (np.angle(z) + 0.163))
        result = np.fft.ifft(w, axis=0)
        for _ in range(5):
            result = self.apply_nonlinear_map(result, 0.187)
        return result / (np.linalg.norm(result) + 1e-15)

    def method_subtree_kernel_1_13(self, x: np.ndarray, p1=0.2444, p2=0.2994) -> np.ndarray:
        y = x * p1 + np.random.randn(*x.shape) * p2
        z = np.fft.fft(y, axis=0)
        w = np.abs(z) * np.exp(1j * (np.angle(z) + 0.101))
        result = np.fft.ifft(w, axis=0)
        for _ in range(8):
            result = self.apply_nonlinear_map(result, 0.326)
        return result / (np.linalg.norm(result) + 1e-15)

    def method_subtree_kernel_1_14(self, x: np.ndarray, p1=0.5240, p2=0.3278) -> np.ndarray:
        y = x * p1 + np.random.randn(*x.shape) * p2
        z = np.fft.fft(y, axis=0)
        w = np.abs(z) * np.exp(1j * (np.angle(z) + 0.683))
        result = np.fft.ifft(w, axis=0)
        for _ in range(6):
            result = self.apply_nonlinear_map(result, 0.166)
        return result / (np.linalg.norm(result) + 1e-15)

    def method_subtree_kernel_1_15(self, x: np.ndarray, p1=0.2836, p2=0.5637) -> np.ndarray:
        y = x * p1 + np.random.randn(*x.shape) * p2
        z = np.fft.fft(y, axis=0)
        w = np.abs(z) * np.exp(1j * (np.angle(z) + 0.962))
        result = np.fft.ifft(w, axis=0)
        for _ in range(5):
            result = self.apply_nonlinear_map(result, 0.227)
        return result / (np.linalg.norm(result) + 1e-15)

    def method_subtree_kernel_1_16(self, x: np.ndarray, p1=0.5536, p2=0.9919) -> np.ndarray:
        y = x * p1 + np.random.randn(*x.shape) * p2
        z = np.fft.fft(y, axis=0)
        w = np.abs(z) * np.exp(1j * (np.angle(z) + 0.940))
        result = np.fft.ifft(w, axis=0)
        for _ in range(7):
            result = self.apply_nonlinear_map(result, 0.987)
        return result / (np.linalg.norm(result) + 1e-15)

    def method_subtree_kernel_1_17(self, x: np.ndarray, p1=0.5335, p2=0.7277) -> np.ndarray:
        y = x * p1 + np.random.randn(*x.shape) * p2
        z = np.fft.fft(y, axis=0)
        w = np.abs(z) * np.exp(1j * (np.angle(z) + 0.826))
        result = np.fft.ifft(w, axis=0)
        for _ in range(2):
            result = self.apply_nonlinear_map(result, 0.884)
        return result / (np.linalg.norm(result) + 1e-15)

    def method_subtree_kernel_1_18(self, x: np.ndarray, p1=0.1327, p2=0.5183) -> np.ndarray:
        y = x * p1 + np.random.randn(*x.shape) * p2
        z = np.fft.fft(y, axis=0)
        w = np.abs(z) * np.exp(1j * (np.angle(z) + 0.483))
        result = np.fft.ifft(w, axis=0)
        for _ in range(3):
            result = self.apply_nonlinear_map(result, 0.437)
        return result / (np.linalg.norm(result) + 1e-15)

    def method_subtree_kernel_1_19(self, x: np.ndarray, p1=0.2180, p2=0.2866) -> np.ndarray:
        y = x * p1 + np.random.randn(*x.shape) * p2
        z = np.fft.fft(y, axis=0)
        w = np.abs(z) * np.exp(1j * (np.angle(z) + 0.932))
        result = np.fft.ifft(w, axis=0)
        for _ in range(3):
            result = self.apply_nonlinear_map(result, 0.835)
        return result / (np.linalg.norm(result) + 1e-15)

    def method_subtree_kernel_1_20(self, x: np.ndarray, p1=0.7882, p2=0.7174) -> np.ndarray:
        y = x * p1 + np.random.randn(*x.shape) * p2
        z = np.fft.fft(y, axis=0)
        w = np.abs(z) * np.exp(1j * (np.angle(z) + 0.471))
        result = np.fft.ifft(w, axis=0)
        for _ in range(5):
            result = self.apply_nonlinear_map(result, 0.367)
        return result / (np.linalg.norm(result) + 1e-15)

    def method_subtree_kernel_1_21(self, x: np.ndarray, p1=0.5161, p2=0.5849) -> np.ndarray:
        y = x * p1 + np.random.randn(*x.shape) * p2
        z = np.fft.fft(y, axis=0)
        w = np.abs(z) * np.exp(1j * (np.angle(z) + 0.245))
        result = np.fft.ifft(w, axis=0)
        for _ in range(6):
            result = self.apply_nonlinear_map(result, 0.685)
        return result / (np.linalg.norm(result) + 1e-15)

    def method_subtree_kernel_1_22(self, x: np.ndarray, p1=0.9547, p2=0.2609) -> np.ndarray:
        y = x * p1 + np.random.randn(*x.shape) * p2
        z = np.fft.fft(y, axis=0)
        w = np.abs(z) * np.exp(1j * (np.angle(z) + 0.476))
        result = np.fft.ifft(w, axis=0)
        for _ in range(8):
            result = self.apply_nonlinear_map(result, 0.137)
        return result / (np.linalg.norm(result) + 1e-15)

    def method_subtree_kernel_1_23(self, x: np.ndarray, p1=0.0288, p2=0.9063) -> np.ndarray:
        y = x * p1 + np.random.randn(*x.shape) * p2
        z = np.fft.fft(y, axis=0)
        w = np.abs(z) * np.exp(1j * (np.angle(z) + 0.763))
        result = np.fft.ifft(w, axis=0)
        for _ in range(7):
            result = self.apply_nonlinear_map(result, 0.940)
        return result / (np.linalg.norm(result) + 1e-15)

    def method_subtree_kernel_1_24(self, x: np.ndarray, p1=0.6715, p2=0.7959) -> np.ndarray:
        y = x * p1 + np.random.randn(*x.shape) * p2
        z = np.fft.fft(y, axis=0)
        w = np.abs(z) * np.exp(1j * (np.angle(z) + 0.233))
        result = np.fft.ifft(w, axis=0)
        for _ in range(6):
            result = self.apply_nonlinear_map(result, 0.292)
        return result / (np.linalg.norm(result) + 1e-15)

    def method_subtree_kernel_1_25(self, x: np.ndarray, p1=0.4248, p2=0.3679) -> np.ndarray:
        y = x * p1 + np.random.randn(*x.shape) * p2
        z = np.fft.fft(y, axis=0)
        w = np.abs(z) * np.exp(1j * (np.angle(z) + 0.545))
        result = np.fft.ifft(w, axis=0)
        for _ in range(2):
            result = self.apply_nonlinear_map(result, 0.185)
        return result / (np.linalg.norm(result) + 1e-15)

    def method_subtree_kernel_1_26(self, x: np.ndarray, p1=0.1086, p2=0.3732) -> np.ndarray:
        y = x * p1 + np.random.randn(*x.shape) * p2
        z = np.fft.fft(y, axis=0)
        w = np.abs(z) * np.exp(1j * (np.angle(z) + 0.931))
        result = np.fft.ifft(w, axis=0)
        for _ in range(4):
            result = self.apply_nonlinear_map(result, 0.523)
        return result / (np.linalg.norm(result) + 1e-15)

    def method_subtree_kernel_1_27(self, x: np.ndarray, p1=0.0980, p2=0.1383) -> np.ndarray:
        y = x * p1 + np.random.randn(*x.shape) * p2
        z = np.fft.fft(y, axis=0)
        w = np.abs(z) * np.exp(1j * (np.angle(z) + 0.698))
        result = np.fft.ifft(w, axis=0)
        for _ in range(7):
            result = self.apply_nonlinear_map(result, 0.513)
        return result / (np.linalg.norm(result) + 1e-15)

    def method_subtree_kernel_1_28(self, x: np.ndarray, p1=0.5801, p2=0.7840) -> np.ndarray:
        y = x * p1 + np.random.randn(*x.shape) * p2
        z = np.fft.fft(y, axis=0)
        w = np.abs(z) * np.exp(1j * (np.angle(z) + 0.557))
        result = np.fft.ifft(w, axis=0)
        for _ in range(4):
            result = self.apply_nonlinear_map(result, 0.261)
        return result / (np.linalg.norm(result) + 1e-15)

    def method_subtree_kernel_1_29(self, x: np.ndarray, p1=0.7790, p2=0.3358) -> np.ndarray:
        y = x * p1 + np.random.randn(*x.shape) * p2
        z = np.fft.fft(y, axis=0)
        w = np.abs(z) * np.exp(1j * (np.angle(z) + 0.630))
        result = np.fft.ifft(w, axis=0)
        for _ in range(7):
            result = self.apply_nonlinear_map(result, 0.695)
        return result / (np.linalg.norm(result) + 1e-15)

    def method_subtree_kernel_1_30(self, x: np.ndarray, p1=0.6383, p2=0.0839) -> np.ndarray:
        y = x * p1 + np.random.randn(*x.shape) * p2
        z = np.fft.fft(y, axis=0)
        w = np.abs(z) * np.exp(1j * (np.angle(z) + 0.902))
        result = np.fft.ifft(w, axis=0)
        for _ in range(7):
            result = self.apply_nonlinear_map(result, 0.263)
        return result / (np.linalg.norm(result) + 1e-15)

    def method_subtree_kernel_1_31(self, x: np.ndarray, p1=0.2469, p2=0.8056) -> np.ndarray:
        y = x * p1 + np.random.randn(*x.shape) * p2
        z = np.fft.fft(y, axis=0)
        w = np.abs(z) * np.exp(1j * (np.angle(z) + 0.777))
        result = np.fft.ifft(w, axis=0)
        for _ in range(7):
            result = self.apply_nonlinear_map(result, 0.103)
        return result / (np.linalg.norm(result) + 1e-15)

    def method_subtree_kernel_1_32(self, x: np.ndarray, p1=0.1945, p2=0.1384) -> np.ndarray:
        y = x * p1 + np.random.randn(*x.shape) * p2
        z = np.fft.fft(y, axis=0)
        w = np.abs(z) * np.exp(1j * (np.angle(z) + 0.539))
        result = np.fft.ifft(w, axis=0)
        for _ in range(6):
            result = self.apply_nonlinear_map(result, 0.477)
        return result / (np.linalg.norm(result) + 1e-15)

    def method_subtree_kernel_1_33(self, x: np.ndarray, p1=0.9362, p2=0.2422) -> np.ndarray:
        y = x * p1 + np.random.randn(*x.shape) * p2
        z = np.fft.fft(y, axis=0)
        w = np.abs(z) * np.exp(1j * (np.angle(z) + 0.814))
        result = np.fft.ifft(w, axis=0)
        for _ in range(6):
            result = self.apply_nonlinear_map(result, 0.933)
        return result / (np.linalg.norm(result) + 1e-15)

    def method_subtree_kernel_1_34(self, x: np.ndarray, p1=0.5559, p2=0.5023) -> np.ndarray:
        y = x * p1 + np.random.randn(*x.shape) * p2
        z = np.fft.fft(y, axis=0)
        w = np.abs(z) * np.exp(1j * (np.angle(z) + 0.414))
        result = np.fft.ifft(w, axis=0)
        for _ in range(7):
            result = self.apply_nonlinear_map(result, 0.972)
        return result / (np.linalg.norm(result) + 1e-15)

    def method_subtree_kernel_1_35(self, x: np.ndarray, p1=0.5980, p2=0.0792) -> np.ndarray:
        y = x * p1 + np.random.randn(*x.shape) * p2
        z = np.fft.fft(y, axis=0)
        w = np.abs(z) * np.exp(1j * (np.angle(z) + 0.763))
        result = np.fft.ifft(w, axis=0)
        for _ in range(3):
            result = self.apply_nonlinear_map(result, 0.964)
        return result / (np.linalg.norm(result) + 1e-15)
