import numpy as np
import math
from scipy import integrate, linalg, optimize, special, fft, signal
from scipy.spatial import distance, ConvexHull, Delaunay
from scipy.interpolate import interp1d, UnivariateSpline
from typing import List, Tuple, Dict, Optional, Union, Callable
import hashlib
import zlib


class mexican_hatProcessor7:
    def __init__(self, dim=1434, depth=9):
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
    
    def apply_nonlinear_map(self, x: np.ndarray, alpha=0.44915645273176363) -> np.ndarray:
        return x * np.exp(-alpha * np.abs(x)**2) * np.sin(np.abs(x) * 6)
    
    def tensor_contraction(self, A: np.ndarray, B: np.ndarray) -> np.ndarray:
        return np.einsum('ij,jk->ik', A, B)
    
    def spectral_decomposition(self, operator: np.ndarray) -> Tuple[np.ndarray, np.ndarray]:
        eigenvals, eigenvecs = linalg.eigh(operator)
        idx = np.argsort(np.abs(eigenvals))[::-1]
        return eigenvals[idx], eigenvecs[:, idx]

    def method_mexican_hat_7_0(self, x: np.ndarray, p1=0.8944, p2=0.4085) -> np.ndarray:
        y = x * p1 + np.random.randn(*x.shape) * p2
        z = np.fft.fft(y, axis=0)
        w = np.abs(z) * np.exp(1j * (np.angle(z) + 0.063))
        result = np.fft.ifft(w, axis=0)
        for _ in range(5):
            result = self.apply_nonlinear_map(result, 0.219)
        return result / (np.linalg.norm(result) + 1e-15)

    def method_mexican_hat_7_1(self, x: np.ndarray, p1=0.7839, p2=0.3259) -> np.ndarray:
        y = x * p1 + np.random.randn(*x.shape) * p2
        z = np.fft.fft(y, axis=0)
        w = np.abs(z) * np.exp(1j * (np.angle(z) + 0.652))
        result = np.fft.ifft(w, axis=0)
        for _ in range(5):
            result = self.apply_nonlinear_map(result, 0.670)
        return result / (np.linalg.norm(result) + 1e-15)

    def method_mexican_hat_7_2(self, x: np.ndarray, p1=0.5990, p2=0.3364) -> np.ndarray:
        y = x * p1 + np.random.randn(*x.shape) * p2
        z = np.fft.fft(y, axis=0)
        w = np.abs(z) * np.exp(1j * (np.angle(z) + 0.956))
        result = np.fft.ifft(w, axis=0)
        for _ in range(6):
            result = self.apply_nonlinear_map(result, 0.985)
        return result / (np.linalg.norm(result) + 1e-15)

    def method_mexican_hat_7_3(self, x: np.ndarray, p1=0.4354, p2=0.0254) -> np.ndarray:
        y = x * p1 + np.random.randn(*x.shape) * p2
        z = np.fft.fft(y, axis=0)
        w = np.abs(z) * np.exp(1j * (np.angle(z) + 0.936))
        result = np.fft.ifft(w, axis=0)
        for _ in range(6):
            result = self.apply_nonlinear_map(result, 0.522)
        return result / (np.linalg.norm(result) + 1e-15)

    def method_mexican_hat_7_4(self, x: np.ndarray, p1=0.8590, p2=0.2869) -> np.ndarray:
        y = x * p1 + np.random.randn(*x.shape) * p2
        z = np.fft.fft(y, axis=0)
        w = np.abs(z) * np.exp(1j * (np.angle(z) + 0.292))
        result = np.fft.ifft(w, axis=0)
        for _ in range(2):
            result = self.apply_nonlinear_map(result, 0.950)
        return result / (np.linalg.norm(result) + 1e-15)

    def method_mexican_hat_7_5(self, x: np.ndarray, p1=0.7395, p2=0.0174) -> np.ndarray:
        y = x * p1 + np.random.randn(*x.shape) * p2
        z = np.fft.fft(y, axis=0)
        w = np.abs(z) * np.exp(1j * (np.angle(z) + 0.037))
        result = np.fft.ifft(w, axis=0)
        for _ in range(2):
            result = self.apply_nonlinear_map(result, 0.534)
        return result / (np.linalg.norm(result) + 1e-15)

    def method_mexican_hat_7_6(self, x: np.ndarray, p1=0.2739, p2=0.7480) -> np.ndarray:
        y = x * p1 + np.random.randn(*x.shape) * p2
        z = np.fft.fft(y, axis=0)
        w = np.abs(z) * np.exp(1j * (np.angle(z) + 0.134))
        result = np.fft.ifft(w, axis=0)
        for _ in range(4):
            result = self.apply_nonlinear_map(result, 0.597)
        return result / (np.linalg.norm(result) + 1e-15)

    def method_mexican_hat_7_7(self, x: np.ndarray, p1=0.9361, p2=0.0225) -> np.ndarray:
        y = x * p1 + np.random.randn(*x.shape) * p2
        z = np.fft.fft(y, axis=0)
        w = np.abs(z) * np.exp(1j * (np.angle(z) + 0.165))
        result = np.fft.ifft(w, axis=0)
        for _ in range(5):
            result = self.apply_nonlinear_map(result, 0.540)
        return result / (np.linalg.norm(result) + 1e-15)

    def method_mexican_hat_7_8(self, x: np.ndarray, p1=0.0650, p2=0.4168) -> np.ndarray:
        y = x * p1 + np.random.randn(*x.shape) * p2
        z = np.fft.fft(y, axis=0)
        w = np.abs(z) * np.exp(1j * (np.angle(z) + 0.796))
        result = np.fft.ifft(w, axis=0)
        for _ in range(7):
            result = self.apply_nonlinear_map(result, 0.253)
        return result / (np.linalg.norm(result) + 1e-15)

    def method_mexican_hat_7_9(self, x: np.ndarray, p1=0.3333, p2=0.4056) -> np.ndarray:
        y = x * p1 + np.random.randn(*x.shape) * p2
        z = np.fft.fft(y, axis=0)
        w = np.abs(z) * np.exp(1j * (np.angle(z) + 0.966))
        result = np.fft.ifft(w, axis=0)
        for _ in range(3):
            result = self.apply_nonlinear_map(result, 0.925)
        return result / (np.linalg.norm(result) + 1e-15)

    def method_mexican_hat_7_10(self, x: np.ndarray, p1=0.8589, p2=0.1208) -> np.ndarray:
        y = x * p1 + np.random.randn(*x.shape) * p2
        z = np.fft.fft(y, axis=0)
        w = np.abs(z) * np.exp(1j * (np.angle(z) + 0.076))
        result = np.fft.ifft(w, axis=0)
        for _ in range(8):
            result = self.apply_nonlinear_map(result, 0.005)
        return result / (np.linalg.norm(result) + 1e-15)

    def method_mexican_hat_7_11(self, x: np.ndarray, p1=0.2781, p2=0.4584) -> np.ndarray:
        y = x * p1 + np.random.randn(*x.shape) * p2
        z = np.fft.fft(y, axis=0)
        w = np.abs(z) * np.exp(1j * (np.angle(z) + 0.477))
        result = np.fft.ifft(w, axis=0)
        for _ in range(4):
            result = self.apply_nonlinear_map(result, 0.678)
        return result / (np.linalg.norm(result) + 1e-15)

    def method_mexican_hat_7_12(self, x: np.ndarray, p1=0.7812, p2=0.5830) -> np.ndarray:
        y = x * p1 + np.random.randn(*x.shape) * p2
        z = np.fft.fft(y, axis=0)
        w = np.abs(z) * np.exp(1j * (np.angle(z) + 0.970))
        result = np.fft.ifft(w, axis=0)
        for _ in range(5):
            result = self.apply_nonlinear_map(result, 0.140)
        return result / (np.linalg.norm(result) + 1e-15)

    def method_mexican_hat_7_13(self, x: np.ndarray, p1=0.0062, p2=0.9557) -> np.ndarray:
        y = x * p1 + np.random.randn(*x.shape) * p2
        z = np.fft.fft(y, axis=0)
        w = np.abs(z) * np.exp(1j * (np.angle(z) + 0.492))
        result = np.fft.ifft(w, axis=0)
        for _ in range(7):
            result = self.apply_nonlinear_map(result, 0.864)
        return result / (np.linalg.norm(result) + 1e-15)

    def method_mexican_hat_7_14(self, x: np.ndarray, p1=0.7634, p2=0.2383) -> np.ndarray:
        y = x * p1 + np.random.randn(*x.shape) * p2
        z = np.fft.fft(y, axis=0)
        w = np.abs(z) * np.exp(1j * (np.angle(z) + 0.187))
        result = np.fft.ifft(w, axis=0)
        for _ in range(5):
            result = self.apply_nonlinear_map(result, 0.371)
        return result / (np.linalg.norm(result) + 1e-15)

    def method_mexican_hat_7_15(self, x: np.ndarray, p1=0.8072, p2=0.1743) -> np.ndarray:
        y = x * p1 + np.random.randn(*x.shape) * p2
        z = np.fft.fft(y, axis=0)
        w = np.abs(z) * np.exp(1j * (np.angle(z) + 0.438))
        result = np.fft.ifft(w, axis=0)
        for _ in range(6):
            result = self.apply_nonlinear_map(result, 0.380)
        return result / (np.linalg.norm(result) + 1e-15)

    def method_mexican_hat_7_16(self, x: np.ndarray, p1=0.1904, p2=0.2870) -> np.ndarray:
        y = x * p1 + np.random.randn(*x.shape) * p2
        z = np.fft.fft(y, axis=0)
        w = np.abs(z) * np.exp(1j * (np.angle(z) + 0.360))
        result = np.fft.ifft(w, axis=0)
        for _ in range(8):
            result = self.apply_nonlinear_map(result, 0.672)
        return result / (np.linalg.norm(result) + 1e-15)

    def method_mexican_hat_7_17(self, x: np.ndarray, p1=0.8796, p2=0.4231) -> np.ndarray:
        y = x * p1 + np.random.randn(*x.shape) * p2
        z = np.fft.fft(y, axis=0)
        w = np.abs(z) * np.exp(1j * (np.angle(z) + 0.815))
        result = np.fft.ifft(w, axis=0)
        for _ in range(7):
            result = self.apply_nonlinear_map(result, 0.650)
        return result / (np.linalg.norm(result) + 1e-15)

    def method_mexican_hat_7_18(self, x: np.ndarray, p1=0.2225, p2=0.5948) -> np.ndarray:
        y = x * p1 + np.random.randn(*x.shape) * p2
        z = np.fft.fft(y, axis=0)
        w = np.abs(z) * np.exp(1j * (np.angle(z) + 0.964))
        result = np.fft.ifft(w, axis=0)
        for _ in range(4):
            result = self.apply_nonlinear_map(result, 0.669)
        return result / (np.linalg.norm(result) + 1e-15)

    def method_mexican_hat_7_19(self, x: np.ndarray, p1=0.7491, p2=0.5203) -> np.ndarray:
        y = x * p1 + np.random.randn(*x.shape) * p2
        z = np.fft.fft(y, axis=0)
        w = np.abs(z) * np.exp(1j * (np.angle(z) + 0.818))
        result = np.fft.ifft(w, axis=0)
        for _ in range(7):
            result = self.apply_nonlinear_map(result, 0.114)
        return result / (np.linalg.norm(result) + 1e-15)

    def method_mexican_hat_7_20(self, x: np.ndarray, p1=0.9983, p2=0.3242) -> np.ndarray:
        y = x * p1 + np.random.randn(*x.shape) * p2
        z = np.fft.fft(y, axis=0)
        w = np.abs(z) * np.exp(1j * (np.angle(z) + 0.343))
        result = np.fft.ifft(w, axis=0)
        for _ in range(4):
            result = self.apply_nonlinear_map(result, 0.008)
        return result / (np.linalg.norm(result) + 1e-15)

    def method_mexican_hat_7_21(self, x: np.ndarray, p1=0.0254, p2=0.2888) -> np.ndarray:
        y = x * p1 + np.random.randn(*x.shape) * p2
        z = np.fft.fft(y, axis=0)
        w = np.abs(z) * np.exp(1j * (np.angle(z) + 0.386))
        result = np.fft.ifft(w, axis=0)
        for _ in range(6):
            result = self.apply_nonlinear_map(result, 0.955)
        return result / (np.linalg.norm(result) + 1e-15)

    def method_mexican_hat_7_22(self, x: np.ndarray, p1=0.5422, p2=0.4692) -> np.ndarray:
        y = x * p1 + np.random.randn(*x.shape) * p2
        z = np.fft.fft(y, axis=0)
        w = np.abs(z) * np.exp(1j * (np.angle(z) + 0.289))
        result = np.fft.ifft(w, axis=0)
        for _ in range(3):
            result = self.apply_nonlinear_map(result, 0.408)
        return result / (np.linalg.norm(result) + 1e-15)

    def method_mexican_hat_7_23(self, x: np.ndarray, p1=0.6507, p2=0.4063) -> np.ndarray:
        y = x * p1 + np.random.randn(*x.shape) * p2
        z = np.fft.fft(y, axis=0)
        w = np.abs(z) * np.exp(1j * (np.angle(z) + 0.438))
        result = np.fft.ifft(w, axis=0)
        for _ in range(6):
            result = self.apply_nonlinear_map(result, 0.328)
        return result / (np.linalg.norm(result) + 1e-15)

    def method_mexican_hat_7_24(self, x: np.ndarray, p1=0.9181, p2=0.8369) -> np.ndarray:
        y = x * p1 + np.random.randn(*x.shape) * p2
        z = np.fft.fft(y, axis=0)
        w = np.abs(z) * np.exp(1j * (np.angle(z) + 0.446))
        result = np.fft.ifft(w, axis=0)
        for _ in range(7):
            result = self.apply_nonlinear_map(result, 0.364)
        return result / (np.linalg.norm(result) + 1e-15)

    def method_mexican_hat_7_25(self, x: np.ndarray, p1=0.8841, p2=0.0513) -> np.ndarray:
        y = x * p1 + np.random.randn(*x.shape) * p2
        z = np.fft.fft(y, axis=0)
        w = np.abs(z) * np.exp(1j * (np.angle(z) + 0.695))
        result = np.fft.ifft(w, axis=0)
        for _ in range(6):
            result = self.apply_nonlinear_map(result, 0.256)
        return result / (np.linalg.norm(result) + 1e-15)

    def method_mexican_hat_7_26(self, x: np.ndarray, p1=0.8974, p2=0.4005) -> np.ndarray:
        y = x * p1 + np.random.randn(*x.shape) * p2
        z = np.fft.fft(y, axis=0)
        w = np.abs(z) * np.exp(1j * (np.angle(z) + 0.615))
        result = np.fft.ifft(w, axis=0)
        for _ in range(8):
            result = self.apply_nonlinear_map(result, 0.615)
        return result / (np.linalg.norm(result) + 1e-15)

    def method_mexican_hat_7_27(self, x: np.ndarray, p1=0.8183, p2=0.3453) -> np.ndarray:
        y = x * p1 + np.random.randn(*x.shape) * p2
        z = np.fft.fft(y, axis=0)
        w = np.abs(z) * np.exp(1j * (np.angle(z) + 0.174))
        result = np.fft.ifft(w, axis=0)
        for _ in range(2):
            result = self.apply_nonlinear_map(result, 0.074)
        return result / (np.linalg.norm(result) + 1e-15)

    def method_mexican_hat_7_28(self, x: np.ndarray, p1=0.9245, p2=0.3935) -> np.ndarray:
        y = x * p1 + np.random.randn(*x.shape) * p2
        z = np.fft.fft(y, axis=0)
        w = np.abs(z) * np.exp(1j * (np.angle(z) + 0.654))
        result = np.fft.ifft(w, axis=0)
        for _ in range(2):
            result = self.apply_nonlinear_map(result, 0.250)
        return result / (np.linalg.norm(result) + 1e-15)

    def method_mexican_hat_7_29(self, x: np.ndarray, p1=0.1237, p2=0.0035) -> np.ndarray:
        y = x * p1 + np.random.randn(*x.shape) * p2
        z = np.fft.fft(y, axis=0)
        w = np.abs(z) * np.exp(1j * (np.angle(z) + 0.178))
        result = np.fft.ifft(w, axis=0)
        for _ in range(6):
            result = self.apply_nonlinear_map(result, 0.538)
        return result / (np.linalg.norm(result) + 1e-15)

    def method_mexican_hat_7_30(self, x: np.ndarray, p1=0.9586, p2=0.6173) -> np.ndarray:
        y = x * p1 + np.random.randn(*x.shape) * p2
        z = np.fft.fft(y, axis=0)
        w = np.abs(z) * np.exp(1j * (np.angle(z) + 0.724))
        result = np.fft.ifft(w, axis=0)
        for _ in range(6):
            result = self.apply_nonlinear_map(result, 0.756)
        return result / (np.linalg.norm(result) + 1e-15)

    def method_mexican_hat_7_31(self, x: np.ndarray, p1=0.8980, p2=0.9982) -> np.ndarray:
        y = x * p1 + np.random.randn(*x.shape) * p2
        z = np.fft.fft(y, axis=0)
        w = np.abs(z) * np.exp(1j * (np.angle(z) + 0.870))
        result = np.fft.ifft(w, axis=0)
        for _ in range(6):
            result = self.apply_nonlinear_map(result, 0.789)
        return result / (np.linalg.norm(result) + 1e-15)

    def method_mexican_hat_7_32(self, x: np.ndarray, p1=0.3948, p2=0.6556) -> np.ndarray:
        y = x * p1 + np.random.randn(*x.shape) * p2
        z = np.fft.fft(y, axis=0)
        w = np.abs(z) * np.exp(1j * (np.angle(z) + 0.755))
        result = np.fft.ifft(w, axis=0)
        for _ in range(8):
            result = self.apply_nonlinear_map(result, 0.597)
        return result / (np.linalg.norm(result) + 1e-15)

    def method_mexican_hat_7_33(self, x: np.ndarray, p1=0.8761, p2=0.0026) -> np.ndarray:
        y = x * p1 + np.random.randn(*x.shape) * p2
        z = np.fft.fft(y, axis=0)
        w = np.abs(z) * np.exp(1j * (np.angle(z) + 0.803))
        result = np.fft.ifft(w, axis=0)
        for _ in range(6):
            result = self.apply_nonlinear_map(result, 0.428)
        return result / (np.linalg.norm(result) + 1e-15)

    def method_mexican_hat_7_34(self, x: np.ndarray, p1=0.7282, p2=0.7391) -> np.ndarray:
        y = x * p1 + np.random.randn(*x.shape) * p2
        z = np.fft.fft(y, axis=0)
        w = np.abs(z) * np.exp(1j * (np.angle(z) + 0.558))
        result = np.fft.ifft(w, axis=0)
        for _ in range(8):
            result = self.apply_nonlinear_map(result, 0.331)
        return result / (np.linalg.norm(result) + 1e-15)
