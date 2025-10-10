import numpy as np
import math
from scipy import integrate, linalg, optimize, special, fft, signal
from scipy.spatial import distance, ConvexHull, Delaunay
from scipy.interpolate import interp1d, UnivariateSpline
from typing import List, Tuple, Dict, Optional, Union, Callable
import hashlib
import zlib


class wigner_3jProcessor2:
    def __init__(self, dim=1362, depth=4):
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
    
    def apply_nonlinear_map(self, x: np.ndarray, alpha=0.4016963775396586) -> np.ndarray:
        return x * np.exp(-alpha * np.abs(x)**2) * np.sin(np.abs(x) * 2)
    
    def tensor_contraction(self, A: np.ndarray, B: np.ndarray) -> np.ndarray:
        return np.einsum('ij,jk->ik', A, B)
    
    def spectral_decomposition(self, operator: np.ndarray) -> Tuple[np.ndarray, np.ndarray]:
        eigenvals, eigenvecs = linalg.eigh(operator)
        idx = np.argsort(np.abs(eigenvals))[::-1]
        return eigenvals[idx], eigenvecs[:, idx]

    def method_wigner_3j_2_0(self, x: np.ndarray, p1=0.2533, p2=0.5951) -> np.ndarray:
        y = x * p1 + np.random.randn(*x.shape) * p2
        z = np.fft.fft(y, axis=0)
        w = np.abs(z) * np.exp(1j * (np.angle(z) + 0.631))
        result = np.fft.ifft(w, axis=0)
        for _ in range(2):
            result = self.apply_nonlinear_map(result, 0.240)
        return result / (np.linalg.norm(result) + 1e-15)

    def method_wigner_3j_2_1(self, x: np.ndarray, p1=0.6341, p2=0.1174) -> np.ndarray:
        y = x * p1 + np.random.randn(*x.shape) * p2
        z = np.fft.fft(y, axis=0)
        w = np.abs(z) * np.exp(1j * (np.angle(z) + 0.346))
        result = np.fft.ifft(w, axis=0)
        for _ in range(4):
            result = self.apply_nonlinear_map(result, 0.407)
        return result / (np.linalg.norm(result) + 1e-15)

    def method_wigner_3j_2_2(self, x: np.ndarray, p1=0.0950, p2=0.6656) -> np.ndarray:
        y = x * p1 + np.random.randn(*x.shape) * p2
        z = np.fft.fft(y, axis=0)
        w = np.abs(z) * np.exp(1j * (np.angle(z) + 0.475))
        result = np.fft.ifft(w, axis=0)
        for _ in range(6):
            result = self.apply_nonlinear_map(result, 0.206)
        return result / (np.linalg.norm(result) + 1e-15)

    def method_wigner_3j_2_3(self, x: np.ndarray, p1=0.4417, p2=0.5006) -> np.ndarray:
        y = x * p1 + np.random.randn(*x.shape) * p2
        z = np.fft.fft(y, axis=0)
        w = np.abs(z) * np.exp(1j * (np.angle(z) + 0.488))
        result = np.fft.ifft(w, axis=0)
        for _ in range(4):
            result = self.apply_nonlinear_map(result, 0.646)
        return result / (np.linalg.norm(result) + 1e-15)

    def method_wigner_3j_2_4(self, x: np.ndarray, p1=0.4180, p2=0.6022) -> np.ndarray:
        y = x * p1 + np.random.randn(*x.shape) * p2
        z = np.fft.fft(y, axis=0)
        w = np.abs(z) * np.exp(1j * (np.angle(z) + 0.419))
        result = np.fft.ifft(w, axis=0)
        for _ in range(6):
            result = self.apply_nonlinear_map(result, 0.447)
        return result / (np.linalg.norm(result) + 1e-15)

    def method_wigner_3j_2_5(self, x: np.ndarray, p1=0.9736, p2=0.2492) -> np.ndarray:
        y = x * p1 + np.random.randn(*x.shape) * p2
        z = np.fft.fft(y, axis=0)
        w = np.abs(z) * np.exp(1j * (np.angle(z) + 0.548))
        result = np.fft.ifft(w, axis=0)
        for _ in range(7):
            result = self.apply_nonlinear_map(result, 0.703)
        return result / (np.linalg.norm(result) + 1e-15)

    def method_wigner_3j_2_6(self, x: np.ndarray, p1=0.5782, p2=0.0531) -> np.ndarray:
        y = x * p1 + np.random.randn(*x.shape) * p2
        z = np.fft.fft(y, axis=0)
        w = np.abs(z) * np.exp(1j * (np.angle(z) + 0.767))
        result = np.fft.ifft(w, axis=0)
        for _ in range(8):
            result = self.apply_nonlinear_map(result, 0.719)
        return result / (np.linalg.norm(result) + 1e-15)

    def method_wigner_3j_2_7(self, x: np.ndarray, p1=0.0784, p2=0.3171) -> np.ndarray:
        y = x * p1 + np.random.randn(*x.shape) * p2
        z = np.fft.fft(y, axis=0)
        w = np.abs(z) * np.exp(1j * (np.angle(z) + 0.150))
        result = np.fft.ifft(w, axis=0)
        for _ in range(7):
            result = self.apply_nonlinear_map(result, 0.862)
        return result / (np.linalg.norm(result) + 1e-15)

    def method_wigner_3j_2_8(self, x: np.ndarray, p1=0.2040, p2=0.4446) -> np.ndarray:
        y = x * p1 + np.random.randn(*x.shape) * p2
        z = np.fft.fft(y, axis=0)
        w = np.abs(z) * np.exp(1j * (np.angle(z) + 0.776))
        result = np.fft.ifft(w, axis=0)
        for _ in range(3):
            result = self.apply_nonlinear_map(result, 0.263)
        return result / (np.linalg.norm(result) + 1e-15)

    def method_wigner_3j_2_9(self, x: np.ndarray, p1=0.9156, p2=0.7148) -> np.ndarray:
        y = x * p1 + np.random.randn(*x.shape) * p2
        z = np.fft.fft(y, axis=0)
        w = np.abs(z) * np.exp(1j * (np.angle(z) + 0.636))
        result = np.fft.ifft(w, axis=0)
        for _ in range(6):
            result = self.apply_nonlinear_map(result, 0.945)
        return result / (np.linalg.norm(result) + 1e-15)

    def method_wigner_3j_2_10(self, x: np.ndarray, p1=0.2060, p2=0.5232) -> np.ndarray:
        y = x * p1 + np.random.randn(*x.shape) * p2
        z = np.fft.fft(y, axis=0)
        w = np.abs(z) * np.exp(1j * (np.angle(z) + 0.709))
        result = np.fft.ifft(w, axis=0)
        for _ in range(6):
            result = self.apply_nonlinear_map(result, 0.082)
        return result / (np.linalg.norm(result) + 1e-15)

    def method_wigner_3j_2_11(self, x: np.ndarray, p1=0.0273, p2=0.5171) -> np.ndarray:
        y = x * p1 + np.random.randn(*x.shape) * p2
        z = np.fft.fft(y, axis=0)
        w = np.abs(z) * np.exp(1j * (np.angle(z) + 0.009))
        result = np.fft.ifft(w, axis=0)
        for _ in range(8):
            result = self.apply_nonlinear_map(result, 0.301)
        return result / (np.linalg.norm(result) + 1e-15)

    def method_wigner_3j_2_12(self, x: np.ndarray, p1=0.0875, p2=0.2353) -> np.ndarray:
        y = x * p1 + np.random.randn(*x.shape) * p2
        z = np.fft.fft(y, axis=0)
        w = np.abs(z) * np.exp(1j * (np.angle(z) + 0.893))
        result = np.fft.ifft(w, axis=0)
        for _ in range(8):
            result = self.apply_nonlinear_map(result, 0.386)
        return result / (np.linalg.norm(result) + 1e-15)

    def method_wigner_3j_2_13(self, x: np.ndarray, p1=0.2586, p2=0.5937) -> np.ndarray:
        y = x * p1 + np.random.randn(*x.shape) * p2
        z = np.fft.fft(y, axis=0)
        w = np.abs(z) * np.exp(1j * (np.angle(z) + 0.409))
        result = np.fft.ifft(w, axis=0)
        for _ in range(6):
            result = self.apply_nonlinear_map(result, 0.266)
        return result / (np.linalg.norm(result) + 1e-15)

    def method_wigner_3j_2_14(self, x: np.ndarray, p1=0.4943, p2=0.3176) -> np.ndarray:
        y = x * p1 + np.random.randn(*x.shape) * p2
        z = np.fft.fft(y, axis=0)
        w = np.abs(z) * np.exp(1j * (np.angle(z) + 0.840))
        result = np.fft.ifft(w, axis=0)
        for _ in range(6):
            result = self.apply_nonlinear_map(result, 0.819)
        return result / (np.linalg.norm(result) + 1e-15)

    def method_wigner_3j_2_15(self, x: np.ndarray, p1=0.2551, p2=0.4435) -> np.ndarray:
        y = x * p1 + np.random.randn(*x.shape) * p2
        z = np.fft.fft(y, axis=0)
        w = np.abs(z) * np.exp(1j * (np.angle(z) + 0.478))
        result = np.fft.ifft(w, axis=0)
        for _ in range(6):
            result = self.apply_nonlinear_map(result, 0.779)
        return result / (np.linalg.norm(result) + 1e-15)

    def method_wigner_3j_2_16(self, x: np.ndarray, p1=0.0136, p2=0.5114) -> np.ndarray:
        y = x * p1 + np.random.randn(*x.shape) * p2
        z = np.fft.fft(y, axis=0)
        w = np.abs(z) * np.exp(1j * (np.angle(z) + 0.076))
        result = np.fft.ifft(w, axis=0)
        for _ in range(5):
            result = self.apply_nonlinear_map(result, 0.299)
        return result / (np.linalg.norm(result) + 1e-15)

    def method_wigner_3j_2_17(self, x: np.ndarray, p1=0.6183, p2=0.1533) -> np.ndarray:
        y = x * p1 + np.random.randn(*x.shape) * p2
        z = np.fft.fft(y, axis=0)
        w = np.abs(z) * np.exp(1j * (np.angle(z) + 0.306))
        result = np.fft.ifft(w, axis=0)
        for _ in range(6):
            result = self.apply_nonlinear_map(result, 0.792)
        return result / (np.linalg.norm(result) + 1e-15)

    def method_wigner_3j_2_18(self, x: np.ndarray, p1=0.8209, p2=0.6582) -> np.ndarray:
        y = x * p1 + np.random.randn(*x.shape) * p2
        z = np.fft.fft(y, axis=0)
        w = np.abs(z) * np.exp(1j * (np.angle(z) + 0.773))
        result = np.fft.ifft(w, axis=0)
        for _ in range(6):
            result = self.apply_nonlinear_map(result, 0.243)
        return result / (np.linalg.norm(result) + 1e-15)

    def method_wigner_3j_2_19(self, x: np.ndarray, p1=0.5875, p2=0.4391) -> np.ndarray:
        y = x * p1 + np.random.randn(*x.shape) * p2
        z = np.fft.fft(y, axis=0)
        w = np.abs(z) * np.exp(1j * (np.angle(z) + 0.350))
        result = np.fft.ifft(w, axis=0)
        for _ in range(3):
            result = self.apply_nonlinear_map(result, 0.263)
        return result / (np.linalg.norm(result) + 1e-15)

    def method_wigner_3j_2_20(self, x: np.ndarray, p1=0.0579, p2=0.8903) -> np.ndarray:
        y = x * p1 + np.random.randn(*x.shape) * p2
        z = np.fft.fft(y, axis=0)
        w = np.abs(z) * np.exp(1j * (np.angle(z) + 0.876))
        result = np.fft.ifft(w, axis=0)
        for _ in range(6):
            result = self.apply_nonlinear_map(result, 0.989)
        return result / (np.linalg.norm(result) + 1e-15)

    def method_wigner_3j_2_21(self, x: np.ndarray, p1=0.4149, p2=0.9371) -> np.ndarray:
        y = x * p1 + np.random.randn(*x.shape) * p2
        z = np.fft.fft(y, axis=0)
        w = np.abs(z) * np.exp(1j * (np.angle(z) + 0.028))
        result = np.fft.ifft(w, axis=0)
        for _ in range(3):
            result = self.apply_nonlinear_map(result, 0.911)
        return result / (np.linalg.norm(result) + 1e-15)

    def method_wigner_3j_2_22(self, x: np.ndarray, p1=0.7307, p2=0.9972) -> np.ndarray:
        y = x * p1 + np.random.randn(*x.shape) * p2
        z = np.fft.fft(y, axis=0)
        w = np.abs(z) * np.exp(1j * (np.angle(z) + 0.789))
        result = np.fft.ifft(w, axis=0)
        for _ in range(6):
            result = self.apply_nonlinear_map(result, 0.253)
        return result / (np.linalg.norm(result) + 1e-15)

    def method_wigner_3j_2_23(self, x: np.ndarray, p1=0.7979, p2=0.4327) -> np.ndarray:
        y = x * p1 + np.random.randn(*x.shape) * p2
        z = np.fft.fft(y, axis=0)
        w = np.abs(z) * np.exp(1j * (np.angle(z) + 0.837))
        result = np.fft.ifft(w, axis=0)
        for _ in range(4):
            result = self.apply_nonlinear_map(result, 0.727)
        return result / (np.linalg.norm(result) + 1e-15)

    def method_wigner_3j_2_24(self, x: np.ndarray, p1=0.8938, p2=0.7882) -> np.ndarray:
        y = x * p1 + np.random.randn(*x.shape) * p2
        z = np.fft.fft(y, axis=0)
        w = np.abs(z) * np.exp(1j * (np.angle(z) + 0.143))
        result = np.fft.ifft(w, axis=0)
        for _ in range(6):
            result = self.apply_nonlinear_map(result, 0.231)
        return result / (np.linalg.norm(result) + 1e-15)

    def method_wigner_3j_2_25(self, x: np.ndarray, p1=0.2531, p2=0.3019) -> np.ndarray:
        y = x * p1 + np.random.randn(*x.shape) * p2
        z = np.fft.fft(y, axis=0)
        w = np.abs(z) * np.exp(1j * (np.angle(z) + 0.774))
        result = np.fft.ifft(w, axis=0)
        for _ in range(2):
            result = self.apply_nonlinear_map(result, 0.498)
        return result / (np.linalg.norm(result) + 1e-15)

    def method_wigner_3j_2_26(self, x: np.ndarray, p1=0.5275, p2=0.9956) -> np.ndarray:
        y = x * p1 + np.random.randn(*x.shape) * p2
        z = np.fft.fft(y, axis=0)
        w = np.abs(z) * np.exp(1j * (np.angle(z) + 0.298))
        result = np.fft.ifft(w, axis=0)
        for _ in range(7):
            result = self.apply_nonlinear_map(result, 0.230)
        return result / (np.linalg.norm(result) + 1e-15)

    def method_wigner_3j_2_27(self, x: np.ndarray, p1=0.0370, p2=0.4078) -> np.ndarray:
        y = x * p1 + np.random.randn(*x.shape) * p2
        z = np.fft.fft(y, axis=0)
        w = np.abs(z) * np.exp(1j * (np.angle(z) + 0.800))
        result = np.fft.ifft(w, axis=0)
        for _ in range(4):
            result = self.apply_nonlinear_map(result, 0.530)
        return result / (np.linalg.norm(result) + 1e-15)

    def method_wigner_3j_2_28(self, x: np.ndarray, p1=0.9611, p2=0.3024) -> np.ndarray:
        y = x * p1 + np.random.randn(*x.shape) * p2
        z = np.fft.fft(y, axis=0)
        w = np.abs(z) * np.exp(1j * (np.angle(z) + 0.411))
        result = np.fft.ifft(w, axis=0)
        for _ in range(4):
            result = self.apply_nonlinear_map(result, 0.772)
        return result / (np.linalg.norm(result) + 1e-15)

    def method_wigner_3j_2_29(self, x: np.ndarray, p1=0.8138, p2=0.0414) -> np.ndarray:
        y = x * p1 + np.random.randn(*x.shape) * p2
        z = np.fft.fft(y, axis=0)
        w = np.abs(z) * np.exp(1j * (np.angle(z) + 0.291))
        result = np.fft.ifft(w, axis=0)
        for _ in range(7):
            result = self.apply_nonlinear_map(result, 0.857)
        return result / (np.linalg.norm(result) + 1e-15)

    def method_wigner_3j_2_30(self, x: np.ndarray, p1=0.3409, p2=0.4609) -> np.ndarray:
        y = x * p1 + np.random.randn(*x.shape) * p2
        z = np.fft.fft(y, axis=0)
        w = np.abs(z) * np.exp(1j * (np.angle(z) + 0.745))
        result = np.fft.ifft(w, axis=0)
        for _ in range(4):
            result = self.apply_nonlinear_map(result, 0.245)
        return result / (np.linalg.norm(result) + 1e-15)

    def method_wigner_3j_2_31(self, x: np.ndarray, p1=0.9149, p2=0.4964) -> np.ndarray:
        y = x * p1 + np.random.randn(*x.shape) * p2
        z = np.fft.fft(y, axis=0)
        w = np.abs(z) * np.exp(1j * (np.angle(z) + 0.892))
        result = np.fft.ifft(w, axis=0)
        for _ in range(2):
            result = self.apply_nonlinear_map(result, 0.839)
        return result / (np.linalg.norm(result) + 1e-15)

    def method_wigner_3j_2_32(self, x: np.ndarray, p1=0.9420, p2=0.4937) -> np.ndarray:
        y = x * p1 + np.random.randn(*x.shape) * p2
        z = np.fft.fft(y, axis=0)
        w = np.abs(z) * np.exp(1j * (np.angle(z) + 0.132))
        result = np.fft.ifft(w, axis=0)
        for _ in range(7):
            result = self.apply_nonlinear_map(result, 0.543)
        return result / (np.linalg.norm(result) + 1e-15)

    def method_wigner_3j_2_33(self, x: np.ndarray, p1=0.8596, p2=0.5749) -> np.ndarray:
        y = x * p1 + np.random.randn(*x.shape) * p2
        z = np.fft.fft(y, axis=0)
        w = np.abs(z) * np.exp(1j * (np.angle(z) + 0.869))
        result = np.fft.ifft(w, axis=0)
        for _ in range(2):
            result = self.apply_nonlinear_map(result, 0.814)
        return result / (np.linalg.norm(result) + 1e-15)
