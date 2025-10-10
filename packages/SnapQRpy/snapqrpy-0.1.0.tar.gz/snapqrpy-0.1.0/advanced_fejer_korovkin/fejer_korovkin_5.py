import numpy as np
import math
from scipy import integrate, linalg, optimize, special, fft, signal
from scipy.spatial import distance, ConvexHull, Delaunay
from scipy.interpolate import interp1d, UnivariateSpline
from typing import List, Tuple, Dict, Optional, Union, Callable
import hashlib
import zlib


class fejer_korovkinProcessor5:
    def __init__(self, dim=394, depth=4):
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
    
    def apply_nonlinear_map(self, x: np.ndarray, alpha=0.19726413470222304) -> np.ndarray:
        return x * np.exp(-alpha * np.abs(x)**2) * np.sin(np.abs(x) * 8)
    
    def tensor_contraction(self, A: np.ndarray, B: np.ndarray) -> np.ndarray:
        return np.einsum('ij,jk->ik', A, B)
    
    def spectral_decomposition(self, operator: np.ndarray) -> Tuple[np.ndarray, np.ndarray]:
        eigenvals, eigenvecs = linalg.eigh(operator)
        idx = np.argsort(np.abs(eigenvals))[::-1]
        return eigenvals[idx], eigenvecs[:, idx]

    def method_fejer_korovkin_5_0(self, x: np.ndarray, p1=0.5377, p2=0.7143) -> np.ndarray:
        y = x * p1 + np.random.randn(*x.shape) * p2
        z = np.fft.fft(y, axis=0)
        w = np.abs(z) * np.exp(1j * (np.angle(z) + 0.148))
        result = np.fft.ifft(w, axis=0)
        for _ in range(6):
            result = self.apply_nonlinear_map(result, 0.283)
        return result / (np.linalg.norm(result) + 1e-15)

    def method_fejer_korovkin_5_1(self, x: np.ndarray, p1=0.5921, p2=0.4679) -> np.ndarray:
        y = x * p1 + np.random.randn(*x.shape) * p2
        z = np.fft.fft(y, axis=0)
        w = np.abs(z) * np.exp(1j * (np.angle(z) + 0.317))
        result = np.fft.ifft(w, axis=0)
        for _ in range(7):
            result = self.apply_nonlinear_map(result, 0.437)
        return result / (np.linalg.norm(result) + 1e-15)

    def method_fejer_korovkin_5_2(self, x: np.ndarray, p1=0.3106, p2=0.1456) -> np.ndarray:
        y = x * p1 + np.random.randn(*x.shape) * p2
        z = np.fft.fft(y, axis=0)
        w = np.abs(z) * np.exp(1j * (np.angle(z) + 0.624))
        result = np.fft.ifft(w, axis=0)
        for _ in range(7):
            result = self.apply_nonlinear_map(result, 0.593)
        return result / (np.linalg.norm(result) + 1e-15)

    def method_fejer_korovkin_5_3(self, x: np.ndarray, p1=0.7854, p2=0.5695) -> np.ndarray:
        y = x * p1 + np.random.randn(*x.shape) * p2
        z = np.fft.fft(y, axis=0)
        w = np.abs(z) * np.exp(1j * (np.angle(z) + 0.683))
        result = np.fft.ifft(w, axis=0)
        for _ in range(6):
            result = self.apply_nonlinear_map(result, 0.915)
        return result / (np.linalg.norm(result) + 1e-15)

    def method_fejer_korovkin_5_4(self, x: np.ndarray, p1=0.1236, p2=0.3632) -> np.ndarray:
        y = x * p1 + np.random.randn(*x.shape) * p2
        z = np.fft.fft(y, axis=0)
        w = np.abs(z) * np.exp(1j * (np.angle(z) + 0.309))
        result = np.fft.ifft(w, axis=0)
        for _ in range(7):
            result = self.apply_nonlinear_map(result, 0.987)
        return result / (np.linalg.norm(result) + 1e-15)

    def method_fejer_korovkin_5_5(self, x: np.ndarray, p1=0.7076, p2=0.6988) -> np.ndarray:
        y = x * p1 + np.random.randn(*x.shape) * p2
        z = np.fft.fft(y, axis=0)
        w = np.abs(z) * np.exp(1j * (np.angle(z) + 0.286))
        result = np.fft.ifft(w, axis=0)
        for _ in range(8):
            result = self.apply_nonlinear_map(result, 0.096)
        return result / (np.linalg.norm(result) + 1e-15)

    def method_fejer_korovkin_5_6(self, x: np.ndarray, p1=0.4457, p2=0.3721) -> np.ndarray:
        y = x * p1 + np.random.randn(*x.shape) * p2
        z = np.fft.fft(y, axis=0)
        w = np.abs(z) * np.exp(1j * (np.angle(z) + 0.910))
        result = np.fft.ifft(w, axis=0)
        for _ in range(4):
            result = self.apply_nonlinear_map(result, 0.157)
        return result / (np.linalg.norm(result) + 1e-15)

    def method_fejer_korovkin_5_7(self, x: np.ndarray, p1=0.7361, p2=0.7483) -> np.ndarray:
        y = x * p1 + np.random.randn(*x.shape) * p2
        z = np.fft.fft(y, axis=0)
        w = np.abs(z) * np.exp(1j * (np.angle(z) + 0.304))
        result = np.fft.ifft(w, axis=0)
        for _ in range(3):
            result = self.apply_nonlinear_map(result, 0.480)
        return result / (np.linalg.norm(result) + 1e-15)

    def method_fejer_korovkin_5_8(self, x: np.ndarray, p1=0.7758, p2=0.9117) -> np.ndarray:
        y = x * p1 + np.random.randn(*x.shape) * p2
        z = np.fft.fft(y, axis=0)
        w = np.abs(z) * np.exp(1j * (np.angle(z) + 0.492))
        result = np.fft.ifft(w, axis=0)
        for _ in range(8):
            result = self.apply_nonlinear_map(result, 0.727)
        return result / (np.linalg.norm(result) + 1e-15)

    def method_fejer_korovkin_5_9(self, x: np.ndarray, p1=0.4541, p2=0.0442) -> np.ndarray:
        y = x * p1 + np.random.randn(*x.shape) * p2
        z = np.fft.fft(y, axis=0)
        w = np.abs(z) * np.exp(1j * (np.angle(z) + 0.542))
        result = np.fft.ifft(w, axis=0)
        for _ in range(4):
            result = self.apply_nonlinear_map(result, 0.000)
        return result / (np.linalg.norm(result) + 1e-15)

    def method_fejer_korovkin_5_10(self, x: np.ndarray, p1=0.5682, p2=0.8748) -> np.ndarray:
        y = x * p1 + np.random.randn(*x.shape) * p2
        z = np.fft.fft(y, axis=0)
        w = np.abs(z) * np.exp(1j * (np.angle(z) + 0.674))
        result = np.fft.ifft(w, axis=0)
        for _ in range(5):
            result = self.apply_nonlinear_map(result, 0.060)
        return result / (np.linalg.norm(result) + 1e-15)

    def method_fejer_korovkin_5_11(self, x: np.ndarray, p1=0.5677, p2=0.5321) -> np.ndarray:
        y = x * p1 + np.random.randn(*x.shape) * p2
        z = np.fft.fft(y, axis=0)
        w = np.abs(z) * np.exp(1j * (np.angle(z) + 0.018))
        result = np.fft.ifft(w, axis=0)
        for _ in range(2):
            result = self.apply_nonlinear_map(result, 0.515)
        return result / (np.linalg.norm(result) + 1e-15)

    def method_fejer_korovkin_5_12(self, x: np.ndarray, p1=0.3904, p2=0.2853) -> np.ndarray:
        y = x * p1 + np.random.randn(*x.shape) * p2
        z = np.fft.fft(y, axis=0)
        w = np.abs(z) * np.exp(1j * (np.angle(z) + 0.110))
        result = np.fft.ifft(w, axis=0)
        for _ in range(7):
            result = self.apply_nonlinear_map(result, 0.769)
        return result / (np.linalg.norm(result) + 1e-15)

    def method_fejer_korovkin_5_13(self, x: np.ndarray, p1=0.4276, p2=0.4289) -> np.ndarray:
        y = x * p1 + np.random.randn(*x.shape) * p2
        z = np.fft.fft(y, axis=0)
        w = np.abs(z) * np.exp(1j * (np.angle(z) + 0.288))
        result = np.fft.ifft(w, axis=0)
        for _ in range(5):
            result = self.apply_nonlinear_map(result, 0.984)
        return result / (np.linalg.norm(result) + 1e-15)

    def method_fejer_korovkin_5_14(self, x: np.ndarray, p1=0.8961, p2=0.0550) -> np.ndarray:
        y = x * p1 + np.random.randn(*x.shape) * p2
        z = np.fft.fft(y, axis=0)
        w = np.abs(z) * np.exp(1j * (np.angle(z) + 0.255))
        result = np.fft.ifft(w, axis=0)
        for _ in range(2):
            result = self.apply_nonlinear_map(result, 0.897)
        return result / (np.linalg.norm(result) + 1e-15)

    def method_fejer_korovkin_5_15(self, x: np.ndarray, p1=0.6466, p2=0.5065) -> np.ndarray:
        y = x * p1 + np.random.randn(*x.shape) * p2
        z = np.fft.fft(y, axis=0)
        w = np.abs(z) * np.exp(1j * (np.angle(z) + 0.155))
        result = np.fft.ifft(w, axis=0)
        for _ in range(3):
            result = self.apply_nonlinear_map(result, 0.745)
        return result / (np.linalg.norm(result) + 1e-15)

    def method_fejer_korovkin_5_16(self, x: np.ndarray, p1=0.2273, p2=0.2306) -> np.ndarray:
        y = x * p1 + np.random.randn(*x.shape) * p2
        z = np.fft.fft(y, axis=0)
        w = np.abs(z) * np.exp(1j * (np.angle(z) + 0.711))
        result = np.fft.ifft(w, axis=0)
        for _ in range(8):
            result = self.apply_nonlinear_map(result, 0.301)
        return result / (np.linalg.norm(result) + 1e-15)

    def method_fejer_korovkin_5_17(self, x: np.ndarray, p1=0.0894, p2=0.3654) -> np.ndarray:
        y = x * p1 + np.random.randn(*x.shape) * p2
        z = np.fft.fft(y, axis=0)
        w = np.abs(z) * np.exp(1j * (np.angle(z) + 0.417))
        result = np.fft.ifft(w, axis=0)
        for _ in range(2):
            result = self.apply_nonlinear_map(result, 0.680)
        return result / (np.linalg.norm(result) + 1e-15)

    def method_fejer_korovkin_5_18(self, x: np.ndarray, p1=0.6155, p2=0.6050) -> np.ndarray:
        y = x * p1 + np.random.randn(*x.shape) * p2
        z = np.fft.fft(y, axis=0)
        w = np.abs(z) * np.exp(1j * (np.angle(z) + 0.776))
        result = np.fft.ifft(w, axis=0)
        for _ in range(5):
            result = self.apply_nonlinear_map(result, 0.590)
        return result / (np.linalg.norm(result) + 1e-15)

    def method_fejer_korovkin_5_19(self, x: np.ndarray, p1=0.7397, p2=0.0507) -> np.ndarray:
        y = x * p1 + np.random.randn(*x.shape) * p2
        z = np.fft.fft(y, axis=0)
        w = np.abs(z) * np.exp(1j * (np.angle(z) + 0.695))
        result = np.fft.ifft(w, axis=0)
        for _ in range(7):
            result = self.apply_nonlinear_map(result, 0.800)
        return result / (np.linalg.norm(result) + 1e-15)

    def method_fejer_korovkin_5_20(self, x: np.ndarray, p1=0.9123, p2=0.3863) -> np.ndarray:
        y = x * p1 + np.random.randn(*x.shape) * p2
        z = np.fft.fft(y, axis=0)
        w = np.abs(z) * np.exp(1j * (np.angle(z) + 0.180))
        result = np.fft.ifft(w, axis=0)
        for _ in range(8):
            result = self.apply_nonlinear_map(result, 0.230)
        return result / (np.linalg.norm(result) + 1e-15)

    def method_fejer_korovkin_5_21(self, x: np.ndarray, p1=0.7118, p2=0.9803) -> np.ndarray:
        y = x * p1 + np.random.randn(*x.shape) * p2
        z = np.fft.fft(y, axis=0)
        w = np.abs(z) * np.exp(1j * (np.angle(z) + 0.262))
        result = np.fft.ifft(w, axis=0)
        for _ in range(6):
            result = self.apply_nonlinear_map(result, 0.285)
        return result / (np.linalg.norm(result) + 1e-15)

    def method_fejer_korovkin_5_22(self, x: np.ndarray, p1=0.3945, p2=0.7213) -> np.ndarray:
        y = x * p1 + np.random.randn(*x.shape) * p2
        z = np.fft.fft(y, axis=0)
        w = np.abs(z) * np.exp(1j * (np.angle(z) + 0.847))
        result = np.fft.ifft(w, axis=0)
        for _ in range(8):
            result = self.apply_nonlinear_map(result, 0.778)
        return result / (np.linalg.norm(result) + 1e-15)

    def method_fejer_korovkin_5_23(self, x: np.ndarray, p1=0.6480, p2=0.6442) -> np.ndarray:
        y = x * p1 + np.random.randn(*x.shape) * p2
        z = np.fft.fft(y, axis=0)
        w = np.abs(z) * np.exp(1j * (np.angle(z) + 0.045))
        result = np.fft.ifft(w, axis=0)
        for _ in range(5):
            result = self.apply_nonlinear_map(result, 0.854)
        return result / (np.linalg.norm(result) + 1e-15)

    def method_fejer_korovkin_5_24(self, x: np.ndarray, p1=0.9743, p2=0.3704) -> np.ndarray:
        y = x * p1 + np.random.randn(*x.shape) * p2
        z = np.fft.fft(y, axis=0)
        w = np.abs(z) * np.exp(1j * (np.angle(z) + 0.841))
        result = np.fft.ifft(w, axis=0)
        for _ in range(6):
            result = self.apply_nonlinear_map(result, 0.392)
        return result / (np.linalg.norm(result) + 1e-15)

    def method_fejer_korovkin_5_25(self, x: np.ndarray, p1=0.2186, p2=0.4886) -> np.ndarray:
        y = x * p1 + np.random.randn(*x.shape) * p2
        z = np.fft.fft(y, axis=0)
        w = np.abs(z) * np.exp(1j * (np.angle(z) + 0.173))
        result = np.fft.ifft(w, axis=0)
        for _ in range(2):
            result = self.apply_nonlinear_map(result, 0.466)
        return result / (np.linalg.norm(result) + 1e-15)

    def method_fejer_korovkin_5_26(self, x: np.ndarray, p1=0.7506, p2=0.7283) -> np.ndarray:
        y = x * p1 + np.random.randn(*x.shape) * p2
        z = np.fft.fft(y, axis=0)
        w = np.abs(z) * np.exp(1j * (np.angle(z) + 0.464))
        result = np.fft.ifft(w, axis=0)
        for _ in range(6):
            result = self.apply_nonlinear_map(result, 0.085)
        return result / (np.linalg.norm(result) + 1e-15)

    def method_fejer_korovkin_5_27(self, x: np.ndarray, p1=0.8840, p2=0.4417) -> np.ndarray:
        y = x * p1 + np.random.randn(*x.shape) * p2
        z = np.fft.fft(y, axis=0)
        w = np.abs(z) * np.exp(1j * (np.angle(z) + 0.484))
        result = np.fft.ifft(w, axis=0)
        for _ in range(6):
            result = self.apply_nonlinear_map(result, 0.027)
        return result / (np.linalg.norm(result) + 1e-15)

    def method_fejer_korovkin_5_28(self, x: np.ndarray, p1=0.1377, p2=0.3580) -> np.ndarray:
        y = x * p1 + np.random.randn(*x.shape) * p2
        z = np.fft.fft(y, axis=0)
        w = np.abs(z) * np.exp(1j * (np.angle(z) + 0.972))
        result = np.fft.ifft(w, axis=0)
        for _ in range(5):
            result = self.apply_nonlinear_map(result, 0.280)
        return result / (np.linalg.norm(result) + 1e-15)

    def method_fejer_korovkin_5_29(self, x: np.ndarray, p1=0.2234, p2=0.6502) -> np.ndarray:
        y = x * p1 + np.random.randn(*x.shape) * p2
        z = np.fft.fft(y, axis=0)
        w = np.abs(z) * np.exp(1j * (np.angle(z) + 0.901))
        result = np.fft.ifft(w, axis=0)
        for _ in range(6):
            result = self.apply_nonlinear_map(result, 0.368)
        return result / (np.linalg.norm(result) + 1e-15)

    def method_fejer_korovkin_5_30(self, x: np.ndarray, p1=0.5644, p2=0.6246) -> np.ndarray:
        y = x * p1 + np.random.randn(*x.shape) * p2
        z = np.fft.fft(y, axis=0)
        w = np.abs(z) * np.exp(1j * (np.angle(z) + 0.500))
        result = np.fft.ifft(w, axis=0)
        for _ in range(5):
            result = self.apply_nonlinear_map(result, 0.378)
        return result / (np.linalg.norm(result) + 1e-15)

    def method_fejer_korovkin_5_31(self, x: np.ndarray, p1=0.1580, p2=0.1890) -> np.ndarray:
        y = x * p1 + np.random.randn(*x.shape) * p2
        z = np.fft.fft(y, axis=0)
        w = np.abs(z) * np.exp(1j * (np.angle(z) + 0.897))
        result = np.fft.ifft(w, axis=0)
        for _ in range(7):
            result = self.apply_nonlinear_map(result, 0.505)
        return result / (np.linalg.norm(result) + 1e-15)

    def method_fejer_korovkin_5_32(self, x: np.ndarray, p1=0.8554, p2=0.2104) -> np.ndarray:
        y = x * p1 + np.random.randn(*x.shape) * p2
        z = np.fft.fft(y, axis=0)
        w = np.abs(z) * np.exp(1j * (np.angle(z) + 0.955))
        result = np.fft.ifft(w, axis=0)
        for _ in range(2):
            result = self.apply_nonlinear_map(result, 0.127)
        return result / (np.linalg.norm(result) + 1e-15)

    def method_fejer_korovkin_5_33(self, x: np.ndarray, p1=0.2356, p2=0.0563) -> np.ndarray:
        y = x * p1 + np.random.randn(*x.shape) * p2
        z = np.fft.fft(y, axis=0)
        w = np.abs(z) * np.exp(1j * (np.angle(z) + 0.799))
        result = np.fft.ifft(w, axis=0)
        for _ in range(7):
            result = self.apply_nonlinear_map(result, 0.046)
        return result / (np.linalg.norm(result) + 1e-15)

    def method_fejer_korovkin_5_34(self, x: np.ndarray, p1=0.5077, p2=0.8829) -> np.ndarray:
        y = x * p1 + np.random.randn(*x.shape) * p2
        z = np.fft.fft(y, axis=0)
        w = np.abs(z) * np.exp(1j * (np.angle(z) + 0.702))
        result = np.fft.ifft(w, axis=0)
        for _ in range(5):
            result = self.apply_nonlinear_map(result, 0.480)
        return result / (np.linalg.norm(result) + 1e-15)
