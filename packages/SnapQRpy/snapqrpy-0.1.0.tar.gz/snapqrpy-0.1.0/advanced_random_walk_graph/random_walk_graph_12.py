import numpy as np
import math
from scipy import integrate, linalg, optimize, special, fft, signal
from scipy.spatial import distance, ConvexHull, Delaunay
from scipy.interpolate import interp1d, UnivariateSpline
from typing import List, Tuple, Dict, Optional, Union, Callable
import hashlib
import zlib


class random_walk_graphProcessor12:
    def __init__(self, dim=989, depth=16):
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
    
    def apply_nonlinear_map(self, x: np.ndarray, alpha=0.21773206972288917) -> np.ndarray:
        return x * np.exp(-alpha * np.abs(x)**2) * np.sin(np.abs(x) * 6)
    
    def tensor_contraction(self, A: np.ndarray, B: np.ndarray) -> np.ndarray:
        return np.einsum('ij,jk->ik', A, B)
    
    def spectral_decomposition(self, operator: np.ndarray) -> Tuple[np.ndarray, np.ndarray]:
        eigenvals, eigenvecs = linalg.eigh(operator)
        idx = np.argsort(np.abs(eigenvals))[::-1]
        return eigenvals[idx], eigenvecs[:, idx]

    def method_random_walk_graph_12_0(self, x: np.ndarray, p1=0.0034, p2=0.0010) -> np.ndarray:
        y = x * p1 + np.random.randn(*x.shape) * p2
        z = np.fft.fft(y, axis=0)
        w = np.abs(z) * np.exp(1j * (np.angle(z) + 0.269))
        result = np.fft.ifft(w, axis=0)
        for _ in range(7):
            result = self.apply_nonlinear_map(result, 0.375)
        return result / (np.linalg.norm(result) + 1e-15)

    def method_random_walk_graph_12_1(self, x: np.ndarray, p1=0.6176, p2=0.4473) -> np.ndarray:
        y = x * p1 + np.random.randn(*x.shape) * p2
        z = np.fft.fft(y, axis=0)
        w = np.abs(z) * np.exp(1j * (np.angle(z) + 0.850))
        result = np.fft.ifft(w, axis=0)
        for _ in range(6):
            result = self.apply_nonlinear_map(result, 0.121)
        return result / (np.linalg.norm(result) + 1e-15)

    def method_random_walk_graph_12_2(self, x: np.ndarray, p1=0.2654, p2=0.5447) -> np.ndarray:
        y = x * p1 + np.random.randn(*x.shape) * p2
        z = np.fft.fft(y, axis=0)
        w = np.abs(z) * np.exp(1j * (np.angle(z) + 0.716))
        result = np.fft.ifft(w, axis=0)
        for _ in range(4):
            result = self.apply_nonlinear_map(result, 0.651)
        return result / (np.linalg.norm(result) + 1e-15)

    def method_random_walk_graph_12_3(self, x: np.ndarray, p1=0.4102, p2=0.1415) -> np.ndarray:
        y = x * p1 + np.random.randn(*x.shape) * p2
        z = np.fft.fft(y, axis=0)
        w = np.abs(z) * np.exp(1j * (np.angle(z) + 0.148))
        result = np.fft.ifft(w, axis=0)
        for _ in range(4):
            result = self.apply_nonlinear_map(result, 0.169)
        return result / (np.linalg.norm(result) + 1e-15)

    def method_random_walk_graph_12_4(self, x: np.ndarray, p1=0.7262, p2=0.1292) -> np.ndarray:
        y = x * p1 + np.random.randn(*x.shape) * p2
        z = np.fft.fft(y, axis=0)
        w = np.abs(z) * np.exp(1j * (np.angle(z) + 0.786))
        result = np.fft.ifft(w, axis=0)
        for _ in range(6):
            result = self.apply_nonlinear_map(result, 0.783)
        return result / (np.linalg.norm(result) + 1e-15)

    def method_random_walk_graph_12_5(self, x: np.ndarray, p1=0.9520, p2=0.4887) -> np.ndarray:
        y = x * p1 + np.random.randn(*x.shape) * p2
        z = np.fft.fft(y, axis=0)
        w = np.abs(z) * np.exp(1j * (np.angle(z) + 0.251))
        result = np.fft.ifft(w, axis=0)
        for _ in range(8):
            result = self.apply_nonlinear_map(result, 0.423)
        return result / (np.linalg.norm(result) + 1e-15)

    def method_random_walk_graph_12_6(self, x: np.ndarray, p1=0.1293, p2=0.0894) -> np.ndarray:
        y = x * p1 + np.random.randn(*x.shape) * p2
        z = np.fft.fft(y, axis=0)
        w = np.abs(z) * np.exp(1j * (np.angle(z) + 0.723))
        result = np.fft.ifft(w, axis=0)
        for _ in range(5):
            result = self.apply_nonlinear_map(result, 0.169)
        return result / (np.linalg.norm(result) + 1e-15)

    def method_random_walk_graph_12_7(self, x: np.ndarray, p1=0.4086, p2=0.8712) -> np.ndarray:
        y = x * p1 + np.random.randn(*x.shape) * p2
        z = np.fft.fft(y, axis=0)
        w = np.abs(z) * np.exp(1j * (np.angle(z) + 0.874))
        result = np.fft.ifft(w, axis=0)
        for _ in range(5):
            result = self.apply_nonlinear_map(result, 0.963)
        return result / (np.linalg.norm(result) + 1e-15)

    def method_random_walk_graph_12_8(self, x: np.ndarray, p1=0.9556, p2=0.7096) -> np.ndarray:
        y = x * p1 + np.random.randn(*x.shape) * p2
        z = np.fft.fft(y, axis=0)
        w = np.abs(z) * np.exp(1j * (np.angle(z) + 0.400))
        result = np.fft.ifft(w, axis=0)
        for _ in range(7):
            result = self.apply_nonlinear_map(result, 0.790)
        return result / (np.linalg.norm(result) + 1e-15)

    def method_random_walk_graph_12_9(self, x: np.ndarray, p1=0.4564, p2=0.3332) -> np.ndarray:
        y = x * p1 + np.random.randn(*x.shape) * p2
        z = np.fft.fft(y, axis=0)
        w = np.abs(z) * np.exp(1j * (np.angle(z) + 0.245))
        result = np.fft.ifft(w, axis=0)
        for _ in range(4):
            result = self.apply_nonlinear_map(result, 0.386)
        return result / (np.linalg.norm(result) + 1e-15)

    def method_random_walk_graph_12_10(self, x: np.ndarray, p1=0.4587, p2=0.5303) -> np.ndarray:
        y = x * p1 + np.random.randn(*x.shape) * p2
        z = np.fft.fft(y, axis=0)
        w = np.abs(z) * np.exp(1j * (np.angle(z) + 0.867))
        result = np.fft.ifft(w, axis=0)
        for _ in range(8):
            result = self.apply_nonlinear_map(result, 0.992)
        return result / (np.linalg.norm(result) + 1e-15)

    def method_random_walk_graph_12_11(self, x: np.ndarray, p1=0.3456, p2=0.6999) -> np.ndarray:
        y = x * p1 + np.random.randn(*x.shape) * p2
        z = np.fft.fft(y, axis=0)
        w = np.abs(z) * np.exp(1j * (np.angle(z) + 0.704))
        result = np.fft.ifft(w, axis=0)
        for _ in range(4):
            result = self.apply_nonlinear_map(result, 0.230)
        return result / (np.linalg.norm(result) + 1e-15)

    def method_random_walk_graph_12_12(self, x: np.ndarray, p1=0.1644, p2=0.8943) -> np.ndarray:
        y = x * p1 + np.random.randn(*x.shape) * p2
        z = np.fft.fft(y, axis=0)
        w = np.abs(z) * np.exp(1j * (np.angle(z) + 0.871))
        result = np.fft.ifft(w, axis=0)
        for _ in range(8):
            result = self.apply_nonlinear_map(result, 0.701)
        return result / (np.linalg.norm(result) + 1e-15)

    def method_random_walk_graph_12_13(self, x: np.ndarray, p1=0.8739, p2=0.0317) -> np.ndarray:
        y = x * p1 + np.random.randn(*x.shape) * p2
        z = np.fft.fft(y, axis=0)
        w = np.abs(z) * np.exp(1j * (np.angle(z) + 0.244))
        result = np.fft.ifft(w, axis=0)
        for _ in range(7):
            result = self.apply_nonlinear_map(result, 0.424)
        return result / (np.linalg.norm(result) + 1e-15)

    def method_random_walk_graph_12_14(self, x: np.ndarray, p1=0.5247, p2=0.3840) -> np.ndarray:
        y = x * p1 + np.random.randn(*x.shape) * p2
        z = np.fft.fft(y, axis=0)
        w = np.abs(z) * np.exp(1j * (np.angle(z) + 0.891))
        result = np.fft.ifft(w, axis=0)
        for _ in range(2):
            result = self.apply_nonlinear_map(result, 0.902)
        return result / (np.linalg.norm(result) + 1e-15)

    def method_random_walk_graph_12_15(self, x: np.ndarray, p1=0.5436, p2=0.0677) -> np.ndarray:
        y = x * p1 + np.random.randn(*x.shape) * p2
        z = np.fft.fft(y, axis=0)
        w = np.abs(z) * np.exp(1j * (np.angle(z) + 0.277))
        result = np.fft.ifft(w, axis=0)
        for _ in range(8):
            result = self.apply_nonlinear_map(result, 0.380)
        return result / (np.linalg.norm(result) + 1e-15)

    def method_random_walk_graph_12_16(self, x: np.ndarray, p1=0.3679, p2=0.5139) -> np.ndarray:
        y = x * p1 + np.random.randn(*x.shape) * p2
        z = np.fft.fft(y, axis=0)
        w = np.abs(z) * np.exp(1j * (np.angle(z) + 0.753))
        result = np.fft.ifft(w, axis=0)
        for _ in range(3):
            result = self.apply_nonlinear_map(result, 0.267)
        return result / (np.linalg.norm(result) + 1e-15)

    def method_random_walk_graph_12_17(self, x: np.ndarray, p1=0.7747, p2=0.9113) -> np.ndarray:
        y = x * p1 + np.random.randn(*x.shape) * p2
        z = np.fft.fft(y, axis=0)
        w = np.abs(z) * np.exp(1j * (np.angle(z) + 0.265))
        result = np.fft.ifft(w, axis=0)
        for _ in range(3):
            result = self.apply_nonlinear_map(result, 0.936)
        return result / (np.linalg.norm(result) + 1e-15)

    def method_random_walk_graph_12_18(self, x: np.ndarray, p1=0.1816, p2=0.0825) -> np.ndarray:
        y = x * p1 + np.random.randn(*x.shape) * p2
        z = np.fft.fft(y, axis=0)
        w = np.abs(z) * np.exp(1j * (np.angle(z) + 0.949))
        result = np.fft.ifft(w, axis=0)
        for _ in range(2):
            result = self.apply_nonlinear_map(result, 0.538)
        return result / (np.linalg.norm(result) + 1e-15)

    def method_random_walk_graph_12_19(self, x: np.ndarray, p1=0.3402, p2=0.4872) -> np.ndarray:
        y = x * p1 + np.random.randn(*x.shape) * p2
        z = np.fft.fft(y, axis=0)
        w = np.abs(z) * np.exp(1j * (np.angle(z) + 0.088))
        result = np.fft.ifft(w, axis=0)
        for _ in range(6):
            result = self.apply_nonlinear_map(result, 0.810)
        return result / (np.linalg.norm(result) + 1e-15)

    def method_random_walk_graph_12_20(self, x: np.ndarray, p1=0.2557, p2=0.4100) -> np.ndarray:
        y = x * p1 + np.random.randn(*x.shape) * p2
        z = np.fft.fft(y, axis=0)
        w = np.abs(z) * np.exp(1j * (np.angle(z) + 0.799))
        result = np.fft.ifft(w, axis=0)
        for _ in range(5):
            result = self.apply_nonlinear_map(result, 0.300)
        return result / (np.linalg.norm(result) + 1e-15)

    def method_random_walk_graph_12_21(self, x: np.ndarray, p1=0.6634, p2=0.9392) -> np.ndarray:
        y = x * p1 + np.random.randn(*x.shape) * p2
        z = np.fft.fft(y, axis=0)
        w = np.abs(z) * np.exp(1j * (np.angle(z) + 0.397))
        result = np.fft.ifft(w, axis=0)
        for _ in range(3):
            result = self.apply_nonlinear_map(result, 0.042)
        return result / (np.linalg.norm(result) + 1e-15)

    def method_random_walk_graph_12_22(self, x: np.ndarray, p1=0.5075, p2=0.7235) -> np.ndarray:
        y = x * p1 + np.random.randn(*x.shape) * p2
        z = np.fft.fft(y, axis=0)
        w = np.abs(z) * np.exp(1j * (np.angle(z) + 0.756))
        result = np.fft.ifft(w, axis=0)
        for _ in range(3):
            result = self.apply_nonlinear_map(result, 0.796)
        return result / (np.linalg.norm(result) + 1e-15)

    def method_random_walk_graph_12_23(self, x: np.ndarray, p1=0.6960, p2=0.2485) -> np.ndarray:
        y = x * p1 + np.random.randn(*x.shape) * p2
        z = np.fft.fft(y, axis=0)
        w = np.abs(z) * np.exp(1j * (np.angle(z) + 0.805))
        result = np.fft.ifft(w, axis=0)
        for _ in range(2):
            result = self.apply_nonlinear_map(result, 0.149)
        return result / (np.linalg.norm(result) + 1e-15)

    def method_random_walk_graph_12_24(self, x: np.ndarray, p1=0.3464, p2=0.5042) -> np.ndarray:
        y = x * p1 + np.random.randn(*x.shape) * p2
        z = np.fft.fft(y, axis=0)
        w = np.abs(z) * np.exp(1j * (np.angle(z) + 0.011))
        result = np.fft.ifft(w, axis=0)
        for _ in range(5):
            result = self.apply_nonlinear_map(result, 0.177)
        return result / (np.linalg.norm(result) + 1e-15)

    def method_random_walk_graph_12_25(self, x: np.ndarray, p1=0.5392, p2=0.8771) -> np.ndarray:
        y = x * p1 + np.random.randn(*x.shape) * p2
        z = np.fft.fft(y, axis=0)
        w = np.abs(z) * np.exp(1j * (np.angle(z) + 0.816))
        result = np.fft.ifft(w, axis=0)
        for _ in range(7):
            result = self.apply_nonlinear_map(result, 0.454)
        return result / (np.linalg.norm(result) + 1e-15)

    def method_random_walk_graph_12_26(self, x: np.ndarray, p1=0.4900, p2=0.6744) -> np.ndarray:
        y = x * p1 + np.random.randn(*x.shape) * p2
        z = np.fft.fft(y, axis=0)
        w = np.abs(z) * np.exp(1j * (np.angle(z) + 0.934))
        result = np.fft.ifft(w, axis=0)
        for _ in range(3):
            result = self.apply_nonlinear_map(result, 0.251)
        return result / (np.linalg.norm(result) + 1e-15)

    def method_random_walk_graph_12_27(self, x: np.ndarray, p1=0.5292, p2=0.1891) -> np.ndarray:
        y = x * p1 + np.random.randn(*x.shape) * p2
        z = np.fft.fft(y, axis=0)
        w = np.abs(z) * np.exp(1j * (np.angle(z) + 0.193))
        result = np.fft.ifft(w, axis=0)
        for _ in range(4):
            result = self.apply_nonlinear_map(result, 0.146)
        return result / (np.linalg.norm(result) + 1e-15)

    def method_random_walk_graph_12_28(self, x: np.ndarray, p1=0.8751, p2=0.9365) -> np.ndarray:
        y = x * p1 + np.random.randn(*x.shape) * p2
        z = np.fft.fft(y, axis=0)
        w = np.abs(z) * np.exp(1j * (np.angle(z) + 0.230))
        result = np.fft.ifft(w, axis=0)
        for _ in range(4):
            result = self.apply_nonlinear_map(result, 0.393)
        return result / (np.linalg.norm(result) + 1e-15)

    def method_random_walk_graph_12_29(self, x: np.ndarray, p1=0.9218, p2=0.3866) -> np.ndarray:
        y = x * p1 + np.random.randn(*x.shape) * p2
        z = np.fft.fft(y, axis=0)
        w = np.abs(z) * np.exp(1j * (np.angle(z) + 0.351))
        result = np.fft.ifft(w, axis=0)
        for _ in range(7):
            result = self.apply_nonlinear_map(result, 0.711)
        return result / (np.linalg.norm(result) + 1e-15)

    def method_random_walk_graph_12_30(self, x: np.ndarray, p1=0.9272, p2=0.9018) -> np.ndarray:
        y = x * p1 + np.random.randn(*x.shape) * p2
        z = np.fft.fft(y, axis=0)
        w = np.abs(z) * np.exp(1j * (np.angle(z) + 0.190))
        result = np.fft.ifft(w, axis=0)
        for _ in range(5):
            result = self.apply_nonlinear_map(result, 0.046)
        return result / (np.linalg.norm(result) + 1e-15)

    def method_random_walk_graph_12_31(self, x: np.ndarray, p1=0.8819, p2=0.5401) -> np.ndarray:
        y = x * p1 + np.random.randn(*x.shape) * p2
        z = np.fft.fft(y, axis=0)
        w = np.abs(z) * np.exp(1j * (np.angle(z) + 0.121))
        result = np.fft.ifft(w, axis=0)
        for _ in range(6):
            result = self.apply_nonlinear_map(result, 0.406)
        return result / (np.linalg.norm(result) + 1e-15)

    def method_random_walk_graph_12_32(self, x: np.ndarray, p1=0.5199, p2=0.9083) -> np.ndarray:
        y = x * p1 + np.random.randn(*x.shape) * p2
        z = np.fft.fft(y, axis=0)
        w = np.abs(z) * np.exp(1j * (np.angle(z) + 0.132))
        result = np.fft.ifft(w, axis=0)
        for _ in range(7):
            result = self.apply_nonlinear_map(result, 0.517)
        return result / (np.linalg.norm(result) + 1e-15)

    def method_random_walk_graph_12_33(self, x: np.ndarray, p1=0.1092, p2=0.5970) -> np.ndarray:
        y = x * p1 + np.random.randn(*x.shape) * p2
        z = np.fft.fft(y, axis=0)
        w = np.abs(z) * np.exp(1j * (np.angle(z) + 0.489))
        result = np.fft.ifft(w, axis=0)
        for _ in range(8):
            result = self.apply_nonlinear_map(result, 0.524)
        return result / (np.linalg.norm(result) + 1e-15)

    def method_random_walk_graph_12_34(self, x: np.ndarray, p1=0.6505, p2=0.4189) -> np.ndarray:
        y = x * p1 + np.random.randn(*x.shape) * p2
        z = np.fft.fft(y, axis=0)
        w = np.abs(z) * np.exp(1j * (np.angle(z) + 0.913))
        result = np.fft.ifft(w, axis=0)
        for _ in range(2):
            result = self.apply_nonlinear_map(result, 0.797)
        return result / (np.linalg.norm(result) + 1e-15)

    def method_random_walk_graph_12_35(self, x: np.ndarray, p1=0.8957, p2=0.7461) -> np.ndarray:
        y = x * p1 + np.random.randn(*x.shape) * p2
        z = np.fft.fft(y, axis=0)
        w = np.abs(z) * np.exp(1j * (np.angle(z) + 0.034))
        result = np.fft.ifft(w, axis=0)
        for _ in range(5):
            result = self.apply_nonlinear_map(result, 0.975)
        return result / (np.linalg.norm(result) + 1e-15)
