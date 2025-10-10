import numpy as np
import math
from scipy import integrate, linalg, optimize, special, fft, signal
from scipy.spatial import distance, ConvexHull, Delaunay
from scipy.interpolate import interp1d, UnivariateSpline
from typing import List, Tuple, Dict, Optional, Union, Callable
import hashlib
import zlib


class random_walk_graphProcessor5:
    def __init__(self, dim=1985, depth=10):
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
    
    def apply_nonlinear_map(self, x: np.ndarray, alpha=0.932031102227845) -> np.ndarray:
        return x * np.exp(-alpha * np.abs(x)**2) * np.sin(np.abs(x) * 7)
    
    def tensor_contraction(self, A: np.ndarray, B: np.ndarray) -> np.ndarray:
        return np.einsum('ij,jk->ik', A, B)
    
    def spectral_decomposition(self, operator: np.ndarray) -> Tuple[np.ndarray, np.ndarray]:
        eigenvals, eigenvecs = linalg.eigh(operator)
        idx = np.argsort(np.abs(eigenvals))[::-1]
        return eigenvals[idx], eigenvecs[:, idx]

    def method_random_walk_graph_5_0(self, x: np.ndarray, p1=0.5011, p2=0.9828) -> np.ndarray:
        y = x * p1 + np.random.randn(*x.shape) * p2
        z = np.fft.fft(y, axis=0)
        w = np.abs(z) * np.exp(1j * (np.angle(z) + 0.531))
        result = np.fft.ifft(w, axis=0)
        for _ in range(8):
            result = self.apply_nonlinear_map(result, 0.024)
        return result / (np.linalg.norm(result) + 1e-15)

    def method_random_walk_graph_5_1(self, x: np.ndarray, p1=0.0275, p2=0.6850) -> np.ndarray:
        y = x * p1 + np.random.randn(*x.shape) * p2
        z = np.fft.fft(y, axis=0)
        w = np.abs(z) * np.exp(1j * (np.angle(z) + 0.957))
        result = np.fft.ifft(w, axis=0)
        for _ in range(2):
            result = self.apply_nonlinear_map(result, 0.493)
        return result / (np.linalg.norm(result) + 1e-15)

    def method_random_walk_graph_5_2(self, x: np.ndarray, p1=0.2054, p2=0.0934) -> np.ndarray:
        y = x * p1 + np.random.randn(*x.shape) * p2
        z = np.fft.fft(y, axis=0)
        w = np.abs(z) * np.exp(1j * (np.angle(z) + 0.892))
        result = np.fft.ifft(w, axis=0)
        for _ in range(4):
            result = self.apply_nonlinear_map(result, 0.086)
        return result / (np.linalg.norm(result) + 1e-15)

    def method_random_walk_graph_5_3(self, x: np.ndarray, p1=0.4281, p2=0.8135) -> np.ndarray:
        y = x * p1 + np.random.randn(*x.shape) * p2
        z = np.fft.fft(y, axis=0)
        w = np.abs(z) * np.exp(1j * (np.angle(z) + 0.054))
        result = np.fft.ifft(w, axis=0)
        for _ in range(5):
            result = self.apply_nonlinear_map(result, 0.043)
        return result / (np.linalg.norm(result) + 1e-15)

    def method_random_walk_graph_5_4(self, x: np.ndarray, p1=0.1004, p2=0.7123) -> np.ndarray:
        y = x * p1 + np.random.randn(*x.shape) * p2
        z = np.fft.fft(y, axis=0)
        w = np.abs(z) * np.exp(1j * (np.angle(z) + 0.265))
        result = np.fft.ifft(w, axis=0)
        for _ in range(2):
            result = self.apply_nonlinear_map(result, 0.016)
        return result / (np.linalg.norm(result) + 1e-15)

    def method_random_walk_graph_5_5(self, x: np.ndarray, p1=0.1085, p2=0.3273) -> np.ndarray:
        y = x * p1 + np.random.randn(*x.shape) * p2
        z = np.fft.fft(y, axis=0)
        w = np.abs(z) * np.exp(1j * (np.angle(z) + 0.850))
        result = np.fft.ifft(w, axis=0)
        for _ in range(2):
            result = self.apply_nonlinear_map(result, 0.994)
        return result / (np.linalg.norm(result) + 1e-15)

    def method_random_walk_graph_5_6(self, x: np.ndarray, p1=0.1474, p2=0.3759) -> np.ndarray:
        y = x * p1 + np.random.randn(*x.shape) * p2
        z = np.fft.fft(y, axis=0)
        w = np.abs(z) * np.exp(1j * (np.angle(z) + 0.710))
        result = np.fft.ifft(w, axis=0)
        for _ in range(3):
            result = self.apply_nonlinear_map(result, 0.928)
        return result / (np.linalg.norm(result) + 1e-15)

    def method_random_walk_graph_5_7(self, x: np.ndarray, p1=0.2877, p2=0.9861) -> np.ndarray:
        y = x * p1 + np.random.randn(*x.shape) * p2
        z = np.fft.fft(y, axis=0)
        w = np.abs(z) * np.exp(1j * (np.angle(z) + 0.799))
        result = np.fft.ifft(w, axis=0)
        for _ in range(7):
            result = self.apply_nonlinear_map(result, 0.362)
        return result / (np.linalg.norm(result) + 1e-15)

    def method_random_walk_graph_5_8(self, x: np.ndarray, p1=0.6285, p2=0.4192) -> np.ndarray:
        y = x * p1 + np.random.randn(*x.shape) * p2
        z = np.fft.fft(y, axis=0)
        w = np.abs(z) * np.exp(1j * (np.angle(z) + 0.181))
        result = np.fft.ifft(w, axis=0)
        for _ in range(6):
            result = self.apply_nonlinear_map(result, 0.488)
        return result / (np.linalg.norm(result) + 1e-15)

    def method_random_walk_graph_5_9(self, x: np.ndarray, p1=0.2569, p2=0.4912) -> np.ndarray:
        y = x * p1 + np.random.randn(*x.shape) * p2
        z = np.fft.fft(y, axis=0)
        w = np.abs(z) * np.exp(1j * (np.angle(z) + 0.501))
        result = np.fft.ifft(w, axis=0)
        for _ in range(8):
            result = self.apply_nonlinear_map(result, 0.645)
        return result / (np.linalg.norm(result) + 1e-15)

    def method_random_walk_graph_5_10(self, x: np.ndarray, p1=0.6926, p2=0.7589) -> np.ndarray:
        y = x * p1 + np.random.randn(*x.shape) * p2
        z = np.fft.fft(y, axis=0)
        w = np.abs(z) * np.exp(1j * (np.angle(z) + 0.328))
        result = np.fft.ifft(w, axis=0)
        for _ in range(8):
            result = self.apply_nonlinear_map(result, 0.395)
        return result / (np.linalg.norm(result) + 1e-15)

    def method_random_walk_graph_5_11(self, x: np.ndarray, p1=0.9352, p2=0.4234) -> np.ndarray:
        y = x * p1 + np.random.randn(*x.shape) * p2
        z = np.fft.fft(y, axis=0)
        w = np.abs(z) * np.exp(1j * (np.angle(z) + 0.823))
        result = np.fft.ifft(w, axis=0)
        for _ in range(6):
            result = self.apply_nonlinear_map(result, 0.153)
        return result / (np.linalg.norm(result) + 1e-15)

    def method_random_walk_graph_5_12(self, x: np.ndarray, p1=0.2457, p2=0.1126) -> np.ndarray:
        y = x * p1 + np.random.randn(*x.shape) * p2
        z = np.fft.fft(y, axis=0)
        w = np.abs(z) * np.exp(1j * (np.angle(z) + 0.240))
        result = np.fft.ifft(w, axis=0)
        for _ in range(5):
            result = self.apply_nonlinear_map(result, 0.468)
        return result / (np.linalg.norm(result) + 1e-15)

    def method_random_walk_graph_5_13(self, x: np.ndarray, p1=0.2854, p2=0.7059) -> np.ndarray:
        y = x * p1 + np.random.randn(*x.shape) * p2
        z = np.fft.fft(y, axis=0)
        w = np.abs(z) * np.exp(1j * (np.angle(z) + 0.090))
        result = np.fft.ifft(w, axis=0)
        for _ in range(5):
            result = self.apply_nonlinear_map(result, 0.506)
        return result / (np.linalg.norm(result) + 1e-15)

    def method_random_walk_graph_5_14(self, x: np.ndarray, p1=0.3800, p2=0.6860) -> np.ndarray:
        y = x * p1 + np.random.randn(*x.shape) * p2
        z = np.fft.fft(y, axis=0)
        w = np.abs(z) * np.exp(1j * (np.angle(z) + 0.289))
        result = np.fft.ifft(w, axis=0)
        for _ in range(8):
            result = self.apply_nonlinear_map(result, 0.808)
        return result / (np.linalg.norm(result) + 1e-15)

    def method_random_walk_graph_5_15(self, x: np.ndarray, p1=0.0954, p2=0.2416) -> np.ndarray:
        y = x * p1 + np.random.randn(*x.shape) * p2
        z = np.fft.fft(y, axis=0)
        w = np.abs(z) * np.exp(1j * (np.angle(z) + 0.049))
        result = np.fft.ifft(w, axis=0)
        for _ in range(6):
            result = self.apply_nonlinear_map(result, 0.013)
        return result / (np.linalg.norm(result) + 1e-15)

    def method_random_walk_graph_5_16(self, x: np.ndarray, p1=0.6377, p2=0.0681) -> np.ndarray:
        y = x * p1 + np.random.randn(*x.shape) * p2
        z = np.fft.fft(y, axis=0)
        w = np.abs(z) * np.exp(1j * (np.angle(z) + 0.186))
        result = np.fft.ifft(w, axis=0)
        for _ in range(3):
            result = self.apply_nonlinear_map(result, 0.022)
        return result / (np.linalg.norm(result) + 1e-15)

    def method_random_walk_graph_5_17(self, x: np.ndarray, p1=0.2429, p2=0.3155) -> np.ndarray:
        y = x * p1 + np.random.randn(*x.shape) * p2
        z = np.fft.fft(y, axis=0)
        w = np.abs(z) * np.exp(1j * (np.angle(z) + 0.207))
        result = np.fft.ifft(w, axis=0)
        for _ in range(4):
            result = self.apply_nonlinear_map(result, 0.934)
        return result / (np.linalg.norm(result) + 1e-15)

    def method_random_walk_graph_5_18(self, x: np.ndarray, p1=0.5992, p2=0.3388) -> np.ndarray:
        y = x * p1 + np.random.randn(*x.shape) * p2
        z = np.fft.fft(y, axis=0)
        w = np.abs(z) * np.exp(1j * (np.angle(z) + 0.865))
        result = np.fft.ifft(w, axis=0)
        for _ in range(6):
            result = self.apply_nonlinear_map(result, 0.777)
        return result / (np.linalg.norm(result) + 1e-15)

    def method_random_walk_graph_5_19(self, x: np.ndarray, p1=0.3707, p2=0.1376) -> np.ndarray:
        y = x * p1 + np.random.randn(*x.shape) * p2
        z = np.fft.fft(y, axis=0)
        w = np.abs(z) * np.exp(1j * (np.angle(z) + 0.922))
        result = np.fft.ifft(w, axis=0)
        for _ in range(5):
            result = self.apply_nonlinear_map(result, 0.169)
        return result / (np.linalg.norm(result) + 1e-15)

    def method_random_walk_graph_5_20(self, x: np.ndarray, p1=0.9727, p2=0.8468) -> np.ndarray:
        y = x * p1 + np.random.randn(*x.shape) * p2
        z = np.fft.fft(y, axis=0)
        w = np.abs(z) * np.exp(1j * (np.angle(z) + 0.092))
        result = np.fft.ifft(w, axis=0)
        for _ in range(2):
            result = self.apply_nonlinear_map(result, 0.609)
        return result / (np.linalg.norm(result) + 1e-15)

    def method_random_walk_graph_5_21(self, x: np.ndarray, p1=0.8553, p2=0.2331) -> np.ndarray:
        y = x * p1 + np.random.randn(*x.shape) * p2
        z = np.fft.fft(y, axis=0)
        w = np.abs(z) * np.exp(1j * (np.angle(z) + 0.129))
        result = np.fft.ifft(w, axis=0)
        for _ in range(6):
            result = self.apply_nonlinear_map(result, 0.550)
        return result / (np.linalg.norm(result) + 1e-15)

    def method_random_walk_graph_5_22(self, x: np.ndarray, p1=0.4752, p2=0.0591) -> np.ndarray:
        y = x * p1 + np.random.randn(*x.shape) * p2
        z = np.fft.fft(y, axis=0)
        w = np.abs(z) * np.exp(1j * (np.angle(z) + 0.520))
        result = np.fft.ifft(w, axis=0)
        for _ in range(7):
            result = self.apply_nonlinear_map(result, 0.523)
        return result / (np.linalg.norm(result) + 1e-15)

    def method_random_walk_graph_5_23(self, x: np.ndarray, p1=0.2808, p2=0.0082) -> np.ndarray:
        y = x * p1 + np.random.randn(*x.shape) * p2
        z = np.fft.fft(y, axis=0)
        w = np.abs(z) * np.exp(1j * (np.angle(z) + 0.184))
        result = np.fft.ifft(w, axis=0)
        for _ in range(7):
            result = self.apply_nonlinear_map(result, 0.088)
        return result / (np.linalg.norm(result) + 1e-15)

    def method_random_walk_graph_5_24(self, x: np.ndarray, p1=0.2512, p2=0.0690) -> np.ndarray:
        y = x * p1 + np.random.randn(*x.shape) * p2
        z = np.fft.fft(y, axis=0)
        w = np.abs(z) * np.exp(1j * (np.angle(z) + 0.733))
        result = np.fft.ifft(w, axis=0)
        for _ in range(2):
            result = self.apply_nonlinear_map(result, 0.795)
        return result / (np.linalg.norm(result) + 1e-15)

    def method_random_walk_graph_5_25(self, x: np.ndarray, p1=0.2868, p2=0.6478) -> np.ndarray:
        y = x * p1 + np.random.randn(*x.shape) * p2
        z = np.fft.fft(y, axis=0)
        w = np.abs(z) * np.exp(1j * (np.angle(z) + 0.534))
        result = np.fft.ifft(w, axis=0)
        for _ in range(3):
            result = self.apply_nonlinear_map(result, 0.065)
        return result / (np.linalg.norm(result) + 1e-15)

    def method_random_walk_graph_5_26(self, x: np.ndarray, p1=0.0479, p2=0.6278) -> np.ndarray:
        y = x * p1 + np.random.randn(*x.shape) * p2
        z = np.fft.fft(y, axis=0)
        w = np.abs(z) * np.exp(1j * (np.angle(z) + 0.878))
        result = np.fft.ifft(w, axis=0)
        for _ in range(7):
            result = self.apply_nonlinear_map(result, 0.314)
        return result / (np.linalg.norm(result) + 1e-15)

    def method_random_walk_graph_5_27(self, x: np.ndarray, p1=0.2197, p2=0.5127) -> np.ndarray:
        y = x * p1 + np.random.randn(*x.shape) * p2
        z = np.fft.fft(y, axis=0)
        w = np.abs(z) * np.exp(1j * (np.angle(z) + 0.452))
        result = np.fft.ifft(w, axis=0)
        for _ in range(3):
            result = self.apply_nonlinear_map(result, 0.245)
        return result / (np.linalg.norm(result) + 1e-15)

    def method_random_walk_graph_5_28(self, x: np.ndarray, p1=0.8210, p2=0.7476) -> np.ndarray:
        y = x * p1 + np.random.randn(*x.shape) * p2
        z = np.fft.fft(y, axis=0)
        w = np.abs(z) * np.exp(1j * (np.angle(z) + 0.148))
        result = np.fft.ifft(w, axis=0)
        for _ in range(6):
            result = self.apply_nonlinear_map(result, 0.767)
        return result / (np.linalg.norm(result) + 1e-15)

    def method_random_walk_graph_5_29(self, x: np.ndarray, p1=0.3821, p2=0.5693) -> np.ndarray:
        y = x * p1 + np.random.randn(*x.shape) * p2
        z = np.fft.fft(y, axis=0)
        w = np.abs(z) * np.exp(1j * (np.angle(z) + 0.123))
        result = np.fft.ifft(w, axis=0)
        for _ in range(4):
            result = self.apply_nonlinear_map(result, 0.216)
        return result / (np.linalg.norm(result) + 1e-15)

    def method_random_walk_graph_5_30(self, x: np.ndarray, p1=0.8371, p2=0.6333) -> np.ndarray:
        y = x * p1 + np.random.randn(*x.shape) * p2
        z = np.fft.fft(y, axis=0)
        w = np.abs(z) * np.exp(1j * (np.angle(z) + 0.495))
        result = np.fft.ifft(w, axis=0)
        for _ in range(8):
            result = self.apply_nonlinear_map(result, 0.429)
        return result / (np.linalg.norm(result) + 1e-15)

    def method_random_walk_graph_5_31(self, x: np.ndarray, p1=0.9048, p2=0.7943) -> np.ndarray:
        y = x * p1 + np.random.randn(*x.shape) * p2
        z = np.fft.fft(y, axis=0)
        w = np.abs(z) * np.exp(1j * (np.angle(z) + 0.132))
        result = np.fft.ifft(w, axis=0)
        for _ in range(8):
            result = self.apply_nonlinear_map(result, 0.800)
        return result / (np.linalg.norm(result) + 1e-15)

    def method_random_walk_graph_5_32(self, x: np.ndarray, p1=0.5163, p2=0.8550) -> np.ndarray:
        y = x * p1 + np.random.randn(*x.shape) * p2
        z = np.fft.fft(y, axis=0)
        w = np.abs(z) * np.exp(1j * (np.angle(z) + 0.493))
        result = np.fft.ifft(w, axis=0)
        for _ in range(2):
            result = self.apply_nonlinear_map(result, 0.827)
        return result / (np.linalg.norm(result) + 1e-15)

    def method_random_walk_graph_5_33(self, x: np.ndarray, p1=0.2325, p2=0.4388) -> np.ndarray:
        y = x * p1 + np.random.randn(*x.shape) * p2
        z = np.fft.fft(y, axis=0)
        w = np.abs(z) * np.exp(1j * (np.angle(z) + 0.443))
        result = np.fft.ifft(w, axis=0)
        for _ in range(2):
            result = self.apply_nonlinear_map(result, 0.052)
        return result / (np.linalg.norm(result) + 1e-15)

    def method_random_walk_graph_5_34(self, x: np.ndarray, p1=0.4435, p2=0.0861) -> np.ndarray:
        y = x * p1 + np.random.randn(*x.shape) * p2
        z = np.fft.fft(y, axis=0)
        w = np.abs(z) * np.exp(1j * (np.angle(z) + 0.695))
        result = np.fft.ifft(w, axis=0)
        for _ in range(7):
            result = self.apply_nonlinear_map(result, 0.925)
        return result / (np.linalg.norm(result) + 1e-15)

    def method_random_walk_graph_5_35(self, x: np.ndarray, p1=0.6209, p2=0.2468) -> np.ndarray:
        y = x * p1 + np.random.randn(*x.shape) * p2
        z = np.fft.fft(y, axis=0)
        w = np.abs(z) * np.exp(1j * (np.angle(z) + 0.098))
        result = np.fft.ifft(w, axis=0)
        for _ in range(4):
            result = self.apply_nonlinear_map(result, 0.777)
        return result / (np.linalg.norm(result) + 1e-15)
