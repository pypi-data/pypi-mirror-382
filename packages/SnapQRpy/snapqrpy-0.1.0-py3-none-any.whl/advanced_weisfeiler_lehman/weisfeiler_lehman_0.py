import numpy as np
import math
from scipy import integrate, linalg, optimize, special, fft, signal
from scipy.spatial import distance, ConvexHull, Delaunay
from scipy.interpolate import interp1d, UnivariateSpline
from typing import List, Tuple, Dict, Optional, Union, Callable
import hashlib
import zlib


class weisfeiler_lehmanProcessor0:
    def __init__(self, dim=1472, depth=10):
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
    
    def apply_nonlinear_map(self, x: np.ndarray, alpha=0.48995360932982357) -> np.ndarray:
        return x * np.exp(-alpha * np.abs(x)**2) * np.sin(np.abs(x) * 8)
    
    def tensor_contraction(self, A: np.ndarray, B: np.ndarray) -> np.ndarray:
        return np.einsum('ij,jk->ik', A, B)
    
    def spectral_decomposition(self, operator: np.ndarray) -> Tuple[np.ndarray, np.ndarray]:
        eigenvals, eigenvecs = linalg.eigh(operator)
        idx = np.argsort(np.abs(eigenvals))[::-1]
        return eigenvals[idx], eigenvecs[:, idx]

    def method_weisfeiler_lehman_0_0(self, x: np.ndarray, p1=0.6089, p2=0.3141) -> np.ndarray:
        y = x * p1 + np.random.randn(*x.shape) * p2
        z = np.fft.fft(y, axis=0)
        w = np.abs(z) * np.exp(1j * (np.angle(z) + 0.313))
        result = np.fft.ifft(w, axis=0)
        for _ in range(2):
            result = self.apply_nonlinear_map(result, 0.093)
        return result / (np.linalg.norm(result) + 1e-15)

    def method_weisfeiler_lehman_0_1(self, x: np.ndarray, p1=0.8208, p2=0.3942) -> np.ndarray:
        y = x * p1 + np.random.randn(*x.shape) * p2
        z = np.fft.fft(y, axis=0)
        w = np.abs(z) * np.exp(1j * (np.angle(z) + 0.114))
        result = np.fft.ifft(w, axis=0)
        for _ in range(2):
            result = self.apply_nonlinear_map(result, 0.456)
        return result / (np.linalg.norm(result) + 1e-15)

    def method_weisfeiler_lehman_0_2(self, x: np.ndarray, p1=0.3813, p2=0.0047) -> np.ndarray:
        y = x * p1 + np.random.randn(*x.shape) * p2
        z = np.fft.fft(y, axis=0)
        w = np.abs(z) * np.exp(1j * (np.angle(z) + 0.192))
        result = np.fft.ifft(w, axis=0)
        for _ in range(6):
            result = self.apply_nonlinear_map(result, 0.820)
        return result / (np.linalg.norm(result) + 1e-15)

    def method_weisfeiler_lehman_0_3(self, x: np.ndarray, p1=0.7497, p2=0.0904) -> np.ndarray:
        y = x * p1 + np.random.randn(*x.shape) * p2
        z = np.fft.fft(y, axis=0)
        w = np.abs(z) * np.exp(1j * (np.angle(z) + 0.827))
        result = np.fft.ifft(w, axis=0)
        for _ in range(3):
            result = self.apply_nonlinear_map(result, 0.828)
        return result / (np.linalg.norm(result) + 1e-15)

    def method_weisfeiler_lehman_0_4(self, x: np.ndarray, p1=0.5227, p2=0.3195) -> np.ndarray:
        y = x * p1 + np.random.randn(*x.shape) * p2
        z = np.fft.fft(y, axis=0)
        w = np.abs(z) * np.exp(1j * (np.angle(z) + 0.722))
        result = np.fft.ifft(w, axis=0)
        for _ in range(3):
            result = self.apply_nonlinear_map(result, 0.941)
        return result / (np.linalg.norm(result) + 1e-15)

    def method_weisfeiler_lehman_0_5(self, x: np.ndarray, p1=0.5702, p2=0.9434) -> np.ndarray:
        y = x * p1 + np.random.randn(*x.shape) * p2
        z = np.fft.fft(y, axis=0)
        w = np.abs(z) * np.exp(1j * (np.angle(z) + 0.959))
        result = np.fft.ifft(w, axis=0)
        for _ in range(8):
            result = self.apply_nonlinear_map(result, 0.550)
        return result / (np.linalg.norm(result) + 1e-15)

    def method_weisfeiler_lehman_0_6(self, x: np.ndarray, p1=0.9488, p2=0.7807) -> np.ndarray:
        y = x * p1 + np.random.randn(*x.shape) * p2
        z = np.fft.fft(y, axis=0)
        w = np.abs(z) * np.exp(1j * (np.angle(z) + 0.076))
        result = np.fft.ifft(w, axis=0)
        for _ in range(3):
            result = self.apply_nonlinear_map(result, 0.692)
        return result / (np.linalg.norm(result) + 1e-15)

    def method_weisfeiler_lehman_0_7(self, x: np.ndarray, p1=0.5847, p2=0.8283) -> np.ndarray:
        y = x * p1 + np.random.randn(*x.shape) * p2
        z = np.fft.fft(y, axis=0)
        w = np.abs(z) * np.exp(1j * (np.angle(z) + 0.885))
        result = np.fft.ifft(w, axis=0)
        for _ in range(8):
            result = self.apply_nonlinear_map(result, 0.352)
        return result / (np.linalg.norm(result) + 1e-15)

    def method_weisfeiler_lehman_0_8(self, x: np.ndarray, p1=0.0064, p2=0.7331) -> np.ndarray:
        y = x * p1 + np.random.randn(*x.shape) * p2
        z = np.fft.fft(y, axis=0)
        w = np.abs(z) * np.exp(1j * (np.angle(z) + 0.285))
        result = np.fft.ifft(w, axis=0)
        for _ in range(3):
            result = self.apply_nonlinear_map(result, 0.981)
        return result / (np.linalg.norm(result) + 1e-15)

    def method_weisfeiler_lehman_0_9(self, x: np.ndarray, p1=0.5612, p2=0.9741) -> np.ndarray:
        y = x * p1 + np.random.randn(*x.shape) * p2
        z = np.fft.fft(y, axis=0)
        w = np.abs(z) * np.exp(1j * (np.angle(z) + 0.112))
        result = np.fft.ifft(w, axis=0)
        for _ in range(4):
            result = self.apply_nonlinear_map(result, 0.431)
        return result / (np.linalg.norm(result) + 1e-15)

    def method_weisfeiler_lehman_0_10(self, x: np.ndarray, p1=0.0997, p2=0.5480) -> np.ndarray:
        y = x * p1 + np.random.randn(*x.shape) * p2
        z = np.fft.fft(y, axis=0)
        w = np.abs(z) * np.exp(1j * (np.angle(z) + 0.566))
        result = np.fft.ifft(w, axis=0)
        for _ in range(5):
            result = self.apply_nonlinear_map(result, 0.128)
        return result / (np.linalg.norm(result) + 1e-15)

    def method_weisfeiler_lehman_0_11(self, x: np.ndarray, p1=0.9442, p2=0.7304) -> np.ndarray:
        y = x * p1 + np.random.randn(*x.shape) * p2
        z = np.fft.fft(y, axis=0)
        w = np.abs(z) * np.exp(1j * (np.angle(z) + 0.724))
        result = np.fft.ifft(w, axis=0)
        for _ in range(4):
            result = self.apply_nonlinear_map(result, 0.352)
        return result / (np.linalg.norm(result) + 1e-15)

    def method_weisfeiler_lehman_0_12(self, x: np.ndarray, p1=0.4099, p2=0.0796) -> np.ndarray:
        y = x * p1 + np.random.randn(*x.shape) * p2
        z = np.fft.fft(y, axis=0)
        w = np.abs(z) * np.exp(1j * (np.angle(z) + 0.586))
        result = np.fft.ifft(w, axis=0)
        for _ in range(2):
            result = self.apply_nonlinear_map(result, 0.851)
        return result / (np.linalg.norm(result) + 1e-15)

    def method_weisfeiler_lehman_0_13(self, x: np.ndarray, p1=0.8377, p2=0.1582) -> np.ndarray:
        y = x * p1 + np.random.randn(*x.shape) * p2
        z = np.fft.fft(y, axis=0)
        w = np.abs(z) * np.exp(1j * (np.angle(z) + 0.583))
        result = np.fft.ifft(w, axis=0)
        for _ in range(7):
            result = self.apply_nonlinear_map(result, 0.514)
        return result / (np.linalg.norm(result) + 1e-15)

    def method_weisfeiler_lehman_0_14(self, x: np.ndarray, p1=0.1347, p2=0.1715) -> np.ndarray:
        y = x * p1 + np.random.randn(*x.shape) * p2
        z = np.fft.fft(y, axis=0)
        w = np.abs(z) * np.exp(1j * (np.angle(z) + 0.735))
        result = np.fft.ifft(w, axis=0)
        for _ in range(8):
            result = self.apply_nonlinear_map(result, 0.697)
        return result / (np.linalg.norm(result) + 1e-15)

    def method_weisfeiler_lehman_0_15(self, x: np.ndarray, p1=0.5880, p2=0.7302) -> np.ndarray:
        y = x * p1 + np.random.randn(*x.shape) * p2
        z = np.fft.fft(y, axis=0)
        w = np.abs(z) * np.exp(1j * (np.angle(z) + 0.963))
        result = np.fft.ifft(w, axis=0)
        for _ in range(8):
            result = self.apply_nonlinear_map(result, 0.833)
        return result / (np.linalg.norm(result) + 1e-15)

    def method_weisfeiler_lehman_0_16(self, x: np.ndarray, p1=0.4655, p2=0.9791) -> np.ndarray:
        y = x * p1 + np.random.randn(*x.shape) * p2
        z = np.fft.fft(y, axis=0)
        w = np.abs(z) * np.exp(1j * (np.angle(z) + 0.679))
        result = np.fft.ifft(w, axis=0)
        for _ in range(6):
            result = self.apply_nonlinear_map(result, 0.623)
        return result / (np.linalg.norm(result) + 1e-15)

    def method_weisfeiler_lehman_0_17(self, x: np.ndarray, p1=0.1098, p2=0.9403) -> np.ndarray:
        y = x * p1 + np.random.randn(*x.shape) * p2
        z = np.fft.fft(y, axis=0)
        w = np.abs(z) * np.exp(1j * (np.angle(z) + 0.762))
        result = np.fft.ifft(w, axis=0)
        for _ in range(3):
            result = self.apply_nonlinear_map(result, 0.633)
        return result / (np.linalg.norm(result) + 1e-15)

    def method_weisfeiler_lehman_0_18(self, x: np.ndarray, p1=0.2560, p2=0.8787) -> np.ndarray:
        y = x * p1 + np.random.randn(*x.shape) * p2
        z = np.fft.fft(y, axis=0)
        w = np.abs(z) * np.exp(1j * (np.angle(z) + 0.211))
        result = np.fft.ifft(w, axis=0)
        for _ in range(5):
            result = self.apply_nonlinear_map(result, 0.869)
        return result / (np.linalg.norm(result) + 1e-15)

    def method_weisfeiler_lehman_0_19(self, x: np.ndarray, p1=0.9439, p2=0.7151) -> np.ndarray:
        y = x * p1 + np.random.randn(*x.shape) * p2
        z = np.fft.fft(y, axis=0)
        w = np.abs(z) * np.exp(1j * (np.angle(z) + 0.440))
        result = np.fft.ifft(w, axis=0)
        for _ in range(6):
            result = self.apply_nonlinear_map(result, 0.320)
        return result / (np.linalg.norm(result) + 1e-15)

    def method_weisfeiler_lehman_0_20(self, x: np.ndarray, p1=0.3761, p2=0.1001) -> np.ndarray:
        y = x * p1 + np.random.randn(*x.shape) * p2
        z = np.fft.fft(y, axis=0)
        w = np.abs(z) * np.exp(1j * (np.angle(z) + 0.950))
        result = np.fft.ifft(w, axis=0)
        for _ in range(6):
            result = self.apply_nonlinear_map(result, 0.552)
        return result / (np.linalg.norm(result) + 1e-15)

    def method_weisfeiler_lehman_0_21(self, x: np.ndarray, p1=0.6659, p2=0.1722) -> np.ndarray:
        y = x * p1 + np.random.randn(*x.shape) * p2
        z = np.fft.fft(y, axis=0)
        w = np.abs(z) * np.exp(1j * (np.angle(z) + 0.016))
        result = np.fft.ifft(w, axis=0)
        for _ in range(4):
            result = self.apply_nonlinear_map(result, 0.642)
        return result / (np.linalg.norm(result) + 1e-15)

    def method_weisfeiler_lehman_0_22(self, x: np.ndarray, p1=0.4183, p2=0.4831) -> np.ndarray:
        y = x * p1 + np.random.randn(*x.shape) * p2
        z = np.fft.fft(y, axis=0)
        w = np.abs(z) * np.exp(1j * (np.angle(z) + 0.548))
        result = np.fft.ifft(w, axis=0)
        for _ in range(6):
            result = self.apply_nonlinear_map(result, 0.275)
        return result / (np.linalg.norm(result) + 1e-15)

    def method_weisfeiler_lehman_0_23(self, x: np.ndarray, p1=0.3359, p2=0.3099) -> np.ndarray:
        y = x * p1 + np.random.randn(*x.shape) * p2
        z = np.fft.fft(y, axis=0)
        w = np.abs(z) * np.exp(1j * (np.angle(z) + 0.020))
        result = np.fft.ifft(w, axis=0)
        for _ in range(7):
            result = self.apply_nonlinear_map(result, 0.759)
        return result / (np.linalg.norm(result) + 1e-15)

    def method_weisfeiler_lehman_0_24(self, x: np.ndarray, p1=0.4258, p2=0.8116) -> np.ndarray:
        y = x * p1 + np.random.randn(*x.shape) * p2
        z = np.fft.fft(y, axis=0)
        w = np.abs(z) * np.exp(1j * (np.angle(z) + 0.121))
        result = np.fft.ifft(w, axis=0)
        for _ in range(4):
            result = self.apply_nonlinear_map(result, 0.715)
        return result / (np.linalg.norm(result) + 1e-15)

    def method_weisfeiler_lehman_0_25(self, x: np.ndarray, p1=0.7069, p2=0.5990) -> np.ndarray:
        y = x * p1 + np.random.randn(*x.shape) * p2
        z = np.fft.fft(y, axis=0)
        w = np.abs(z) * np.exp(1j * (np.angle(z) + 0.495))
        result = np.fft.ifft(w, axis=0)
        for _ in range(2):
            result = self.apply_nonlinear_map(result, 0.888)
        return result / (np.linalg.norm(result) + 1e-15)

    def method_weisfeiler_lehman_0_26(self, x: np.ndarray, p1=0.8959, p2=0.1335) -> np.ndarray:
        y = x * p1 + np.random.randn(*x.shape) * p2
        z = np.fft.fft(y, axis=0)
        w = np.abs(z) * np.exp(1j * (np.angle(z) + 0.139))
        result = np.fft.ifft(w, axis=0)
        for _ in range(4):
            result = self.apply_nonlinear_map(result, 0.567)
        return result / (np.linalg.norm(result) + 1e-15)

    def method_weisfeiler_lehman_0_27(self, x: np.ndarray, p1=0.4263, p2=0.2436) -> np.ndarray:
        y = x * p1 + np.random.randn(*x.shape) * p2
        z = np.fft.fft(y, axis=0)
        w = np.abs(z) * np.exp(1j * (np.angle(z) + 0.717))
        result = np.fft.ifft(w, axis=0)
        for _ in range(4):
            result = self.apply_nonlinear_map(result, 0.404)
        return result / (np.linalg.norm(result) + 1e-15)

    def method_weisfeiler_lehman_0_28(self, x: np.ndarray, p1=0.1686, p2=0.9675) -> np.ndarray:
        y = x * p1 + np.random.randn(*x.shape) * p2
        z = np.fft.fft(y, axis=0)
        w = np.abs(z) * np.exp(1j * (np.angle(z) + 0.744))
        result = np.fft.ifft(w, axis=0)
        for _ in range(7):
            result = self.apply_nonlinear_map(result, 0.402)
        return result / (np.linalg.norm(result) + 1e-15)
