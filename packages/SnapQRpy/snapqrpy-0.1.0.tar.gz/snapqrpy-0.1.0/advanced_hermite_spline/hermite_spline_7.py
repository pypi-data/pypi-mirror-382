import numpy as np
import math
from scipy import integrate, linalg, optimize, special, fft, signal
from scipy.spatial import distance, ConvexHull, Delaunay
from scipy.interpolate import interp1d, UnivariateSpline
from typing import List, Tuple, Dict, Optional, Union, Callable
import hashlib
import zlib


class hermite_splineProcessor7:
    def __init__(self, dim=1363, depth=10):
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
    
    def apply_nonlinear_map(self, x: np.ndarray, alpha=0.5338214018326954) -> np.ndarray:
        return x * np.exp(-alpha * np.abs(x)**2) * np.sin(np.abs(x) * 2)
    
    def tensor_contraction(self, A: np.ndarray, B: np.ndarray) -> np.ndarray:
        return np.einsum('ij,jk->ik', A, B)
    
    def spectral_decomposition(self, operator: np.ndarray) -> Tuple[np.ndarray, np.ndarray]:
        eigenvals, eigenvecs = linalg.eigh(operator)
        idx = np.argsort(np.abs(eigenvals))[::-1]
        return eigenvals[idx], eigenvecs[:, idx]

    def method_hermite_spline_7_0(self, x: np.ndarray, p1=0.5952, p2=0.5964) -> np.ndarray:
        y = x * p1 + np.random.randn(*x.shape) * p2
        z = np.fft.fft(y, axis=0)
        w = np.abs(z) * np.exp(1j * (np.angle(z) + 0.377))
        result = np.fft.ifft(w, axis=0)
        for _ in range(8):
            result = self.apply_nonlinear_map(result, 0.357)
        return result / (np.linalg.norm(result) + 1e-15)

    def method_hermite_spline_7_1(self, x: np.ndarray, p1=0.7198, p2=0.3418) -> np.ndarray:
        y = x * p1 + np.random.randn(*x.shape) * p2
        z = np.fft.fft(y, axis=0)
        w = np.abs(z) * np.exp(1j * (np.angle(z) + 0.252))
        result = np.fft.ifft(w, axis=0)
        for _ in range(6):
            result = self.apply_nonlinear_map(result, 0.474)
        return result / (np.linalg.norm(result) + 1e-15)

    def method_hermite_spline_7_2(self, x: np.ndarray, p1=0.7302, p2=0.1988) -> np.ndarray:
        y = x * p1 + np.random.randn(*x.shape) * p2
        z = np.fft.fft(y, axis=0)
        w = np.abs(z) * np.exp(1j * (np.angle(z) + 0.279))
        result = np.fft.ifft(w, axis=0)
        for _ in range(3):
            result = self.apply_nonlinear_map(result, 0.036)
        return result / (np.linalg.norm(result) + 1e-15)

    def method_hermite_spline_7_3(self, x: np.ndarray, p1=0.5426, p2=0.3066) -> np.ndarray:
        y = x * p1 + np.random.randn(*x.shape) * p2
        z = np.fft.fft(y, axis=0)
        w = np.abs(z) * np.exp(1j * (np.angle(z) + 0.582))
        result = np.fft.ifft(w, axis=0)
        for _ in range(7):
            result = self.apply_nonlinear_map(result, 0.181)
        return result / (np.linalg.norm(result) + 1e-15)

    def method_hermite_spline_7_4(self, x: np.ndarray, p1=0.2297, p2=0.9458) -> np.ndarray:
        y = x * p1 + np.random.randn(*x.shape) * p2
        z = np.fft.fft(y, axis=0)
        w = np.abs(z) * np.exp(1j * (np.angle(z) + 0.709))
        result = np.fft.ifft(w, axis=0)
        for _ in range(5):
            result = self.apply_nonlinear_map(result, 0.891)
        return result / (np.linalg.norm(result) + 1e-15)

    def method_hermite_spline_7_5(self, x: np.ndarray, p1=0.9863, p2=0.5260) -> np.ndarray:
        y = x * p1 + np.random.randn(*x.shape) * p2
        z = np.fft.fft(y, axis=0)
        w = np.abs(z) * np.exp(1j * (np.angle(z) + 0.063))
        result = np.fft.ifft(w, axis=0)
        for _ in range(2):
            result = self.apply_nonlinear_map(result, 0.529)
        return result / (np.linalg.norm(result) + 1e-15)

    def method_hermite_spline_7_6(self, x: np.ndarray, p1=0.0638, p2=0.7393) -> np.ndarray:
        y = x * p1 + np.random.randn(*x.shape) * p2
        z = np.fft.fft(y, axis=0)
        w = np.abs(z) * np.exp(1j * (np.angle(z) + 0.401))
        result = np.fft.ifft(w, axis=0)
        for _ in range(7):
            result = self.apply_nonlinear_map(result, 0.397)
        return result / (np.linalg.norm(result) + 1e-15)

    def method_hermite_spline_7_7(self, x: np.ndarray, p1=0.5912, p2=0.2139) -> np.ndarray:
        y = x * p1 + np.random.randn(*x.shape) * p2
        z = np.fft.fft(y, axis=0)
        w = np.abs(z) * np.exp(1j * (np.angle(z) + 0.680))
        result = np.fft.ifft(w, axis=0)
        for _ in range(6):
            result = self.apply_nonlinear_map(result, 0.739)
        return result / (np.linalg.norm(result) + 1e-15)

    def method_hermite_spline_7_8(self, x: np.ndarray, p1=0.6953, p2=0.0729) -> np.ndarray:
        y = x * p1 + np.random.randn(*x.shape) * p2
        z = np.fft.fft(y, axis=0)
        w = np.abs(z) * np.exp(1j * (np.angle(z) + 0.459))
        result = np.fft.ifft(w, axis=0)
        for _ in range(6):
            result = self.apply_nonlinear_map(result, 0.641)
        return result / (np.linalg.norm(result) + 1e-15)

    def method_hermite_spline_7_9(self, x: np.ndarray, p1=0.0060, p2=0.2065) -> np.ndarray:
        y = x * p1 + np.random.randn(*x.shape) * p2
        z = np.fft.fft(y, axis=0)
        w = np.abs(z) * np.exp(1j * (np.angle(z) + 0.271))
        result = np.fft.ifft(w, axis=0)
        for _ in range(7):
            result = self.apply_nonlinear_map(result, 0.485)
        return result / (np.linalg.norm(result) + 1e-15)

    def method_hermite_spline_7_10(self, x: np.ndarray, p1=0.0017, p2=0.3145) -> np.ndarray:
        y = x * p1 + np.random.randn(*x.shape) * p2
        z = np.fft.fft(y, axis=0)
        w = np.abs(z) * np.exp(1j * (np.angle(z) + 0.593))
        result = np.fft.ifft(w, axis=0)
        for _ in range(6):
            result = self.apply_nonlinear_map(result, 0.700)
        return result / (np.linalg.norm(result) + 1e-15)

    def method_hermite_spline_7_11(self, x: np.ndarray, p1=0.1546, p2=0.4833) -> np.ndarray:
        y = x * p1 + np.random.randn(*x.shape) * p2
        z = np.fft.fft(y, axis=0)
        w = np.abs(z) * np.exp(1j * (np.angle(z) + 0.478))
        result = np.fft.ifft(w, axis=0)
        for _ in range(3):
            result = self.apply_nonlinear_map(result, 0.249)
        return result / (np.linalg.norm(result) + 1e-15)

    def method_hermite_spline_7_12(self, x: np.ndarray, p1=0.3834, p2=0.2922) -> np.ndarray:
        y = x * p1 + np.random.randn(*x.shape) * p2
        z = np.fft.fft(y, axis=0)
        w = np.abs(z) * np.exp(1j * (np.angle(z) + 0.424))
        result = np.fft.ifft(w, axis=0)
        for _ in range(8):
            result = self.apply_nonlinear_map(result, 0.233)
        return result / (np.linalg.norm(result) + 1e-15)

    def method_hermite_spline_7_13(self, x: np.ndarray, p1=0.4057, p2=0.2625) -> np.ndarray:
        y = x * p1 + np.random.randn(*x.shape) * p2
        z = np.fft.fft(y, axis=0)
        w = np.abs(z) * np.exp(1j * (np.angle(z) + 0.950))
        result = np.fft.ifft(w, axis=0)
        for _ in range(3):
            result = self.apply_nonlinear_map(result, 0.700)
        return result / (np.linalg.norm(result) + 1e-15)

    def method_hermite_spline_7_14(self, x: np.ndarray, p1=0.0107, p2=0.5230) -> np.ndarray:
        y = x * p1 + np.random.randn(*x.shape) * p2
        z = np.fft.fft(y, axis=0)
        w = np.abs(z) * np.exp(1j * (np.angle(z) + 0.112))
        result = np.fft.ifft(w, axis=0)
        for _ in range(4):
            result = self.apply_nonlinear_map(result, 0.032)
        return result / (np.linalg.norm(result) + 1e-15)

    def method_hermite_spline_7_15(self, x: np.ndarray, p1=0.8390, p2=0.6652) -> np.ndarray:
        y = x * p1 + np.random.randn(*x.shape) * p2
        z = np.fft.fft(y, axis=0)
        w = np.abs(z) * np.exp(1j * (np.angle(z) + 0.313))
        result = np.fft.ifft(w, axis=0)
        for _ in range(8):
            result = self.apply_nonlinear_map(result, 0.143)
        return result / (np.linalg.norm(result) + 1e-15)

    def method_hermite_spline_7_16(self, x: np.ndarray, p1=0.9016, p2=0.6198) -> np.ndarray:
        y = x * p1 + np.random.randn(*x.shape) * p2
        z = np.fft.fft(y, axis=0)
        w = np.abs(z) * np.exp(1j * (np.angle(z) + 0.307))
        result = np.fft.ifft(w, axis=0)
        for _ in range(6):
            result = self.apply_nonlinear_map(result, 0.681)
        return result / (np.linalg.norm(result) + 1e-15)

    def method_hermite_spline_7_17(self, x: np.ndarray, p1=0.2066, p2=0.9682) -> np.ndarray:
        y = x * p1 + np.random.randn(*x.shape) * p2
        z = np.fft.fft(y, axis=0)
        w = np.abs(z) * np.exp(1j * (np.angle(z) + 0.203))
        result = np.fft.ifft(w, axis=0)
        for _ in range(8):
            result = self.apply_nonlinear_map(result, 0.967)
        return result / (np.linalg.norm(result) + 1e-15)

    def method_hermite_spline_7_18(self, x: np.ndarray, p1=0.7049, p2=0.1445) -> np.ndarray:
        y = x * p1 + np.random.randn(*x.shape) * p2
        z = np.fft.fft(y, axis=0)
        w = np.abs(z) * np.exp(1j * (np.angle(z) + 0.002))
        result = np.fft.ifft(w, axis=0)
        for _ in range(3):
            result = self.apply_nonlinear_map(result, 0.979)
        return result / (np.linalg.norm(result) + 1e-15)

    def method_hermite_spline_7_19(self, x: np.ndarray, p1=0.8971, p2=0.3212) -> np.ndarray:
        y = x * p1 + np.random.randn(*x.shape) * p2
        z = np.fft.fft(y, axis=0)
        w = np.abs(z) * np.exp(1j * (np.angle(z) + 0.569))
        result = np.fft.ifft(w, axis=0)
        for _ in range(6):
            result = self.apply_nonlinear_map(result, 0.277)
        return result / (np.linalg.norm(result) + 1e-15)

    def method_hermite_spline_7_20(self, x: np.ndarray, p1=0.1538, p2=0.9105) -> np.ndarray:
        y = x * p1 + np.random.randn(*x.shape) * p2
        z = np.fft.fft(y, axis=0)
        w = np.abs(z) * np.exp(1j * (np.angle(z) + 0.589))
        result = np.fft.ifft(w, axis=0)
        for _ in range(2):
            result = self.apply_nonlinear_map(result, 0.304)
        return result / (np.linalg.norm(result) + 1e-15)

    def method_hermite_spline_7_21(self, x: np.ndarray, p1=0.8147, p2=0.3252) -> np.ndarray:
        y = x * p1 + np.random.randn(*x.shape) * p2
        z = np.fft.fft(y, axis=0)
        w = np.abs(z) * np.exp(1j * (np.angle(z) + 0.226))
        result = np.fft.ifft(w, axis=0)
        for _ in range(4):
            result = self.apply_nonlinear_map(result, 0.290)
        return result / (np.linalg.norm(result) + 1e-15)

    def method_hermite_spline_7_22(self, x: np.ndarray, p1=0.8399, p2=0.2503) -> np.ndarray:
        y = x * p1 + np.random.randn(*x.shape) * p2
        z = np.fft.fft(y, axis=0)
        w = np.abs(z) * np.exp(1j * (np.angle(z) + 0.901))
        result = np.fft.ifft(w, axis=0)
        for _ in range(6):
            result = self.apply_nonlinear_map(result, 0.674)
        return result / (np.linalg.norm(result) + 1e-15)

    def method_hermite_spline_7_23(self, x: np.ndarray, p1=0.4968, p2=0.2846) -> np.ndarray:
        y = x * p1 + np.random.randn(*x.shape) * p2
        z = np.fft.fft(y, axis=0)
        w = np.abs(z) * np.exp(1j * (np.angle(z) + 0.582))
        result = np.fft.ifft(w, axis=0)
        for _ in range(5):
            result = self.apply_nonlinear_map(result, 0.700)
        return result / (np.linalg.norm(result) + 1e-15)

    def method_hermite_spline_7_24(self, x: np.ndarray, p1=0.5969, p2=0.9957) -> np.ndarray:
        y = x * p1 + np.random.randn(*x.shape) * p2
        z = np.fft.fft(y, axis=0)
        w = np.abs(z) * np.exp(1j * (np.angle(z) + 0.446))
        result = np.fft.ifft(w, axis=0)
        for _ in range(8):
            result = self.apply_nonlinear_map(result, 0.760)
        return result / (np.linalg.norm(result) + 1e-15)

    def method_hermite_spline_7_25(self, x: np.ndarray, p1=0.4525, p2=0.2434) -> np.ndarray:
        y = x * p1 + np.random.randn(*x.shape) * p2
        z = np.fft.fft(y, axis=0)
        w = np.abs(z) * np.exp(1j * (np.angle(z) + 0.422))
        result = np.fft.ifft(w, axis=0)
        for _ in range(5):
            result = self.apply_nonlinear_map(result, 0.166)
        return result / (np.linalg.norm(result) + 1e-15)

    def method_hermite_spline_7_26(self, x: np.ndarray, p1=0.7409, p2=0.3702) -> np.ndarray:
        y = x * p1 + np.random.randn(*x.shape) * p2
        z = np.fft.fft(y, axis=0)
        w = np.abs(z) * np.exp(1j * (np.angle(z) + 0.583))
        result = np.fft.ifft(w, axis=0)
        for _ in range(4):
            result = self.apply_nonlinear_map(result, 0.713)
        return result / (np.linalg.norm(result) + 1e-15)

    def method_hermite_spline_7_27(self, x: np.ndarray, p1=0.9279, p2=0.7282) -> np.ndarray:
        y = x * p1 + np.random.randn(*x.shape) * p2
        z = np.fft.fft(y, axis=0)
        w = np.abs(z) * np.exp(1j * (np.angle(z) + 0.030))
        result = np.fft.ifft(w, axis=0)
        for _ in range(8):
            result = self.apply_nonlinear_map(result, 0.999)
        return result / (np.linalg.norm(result) + 1e-15)

    def method_hermite_spline_7_28(self, x: np.ndarray, p1=0.9867, p2=0.2255) -> np.ndarray:
        y = x * p1 + np.random.randn(*x.shape) * p2
        z = np.fft.fft(y, axis=0)
        w = np.abs(z) * np.exp(1j * (np.angle(z) + 0.086))
        result = np.fft.ifft(w, axis=0)
        for _ in range(4):
            result = self.apply_nonlinear_map(result, 0.973)
        return result / (np.linalg.norm(result) + 1e-15)

    def method_hermite_spline_7_29(self, x: np.ndarray, p1=0.5510, p2=0.6992) -> np.ndarray:
        y = x * p1 + np.random.randn(*x.shape) * p2
        z = np.fft.fft(y, axis=0)
        w = np.abs(z) * np.exp(1j * (np.angle(z) + 0.458))
        result = np.fft.ifft(w, axis=0)
        for _ in range(4):
            result = self.apply_nonlinear_map(result, 0.854)
        return result / (np.linalg.norm(result) + 1e-15)

    def method_hermite_spline_7_30(self, x: np.ndarray, p1=0.2123, p2=0.9597) -> np.ndarray:
        y = x * p1 + np.random.randn(*x.shape) * p2
        z = np.fft.fft(y, axis=0)
        w = np.abs(z) * np.exp(1j * (np.angle(z) + 0.227))
        result = np.fft.ifft(w, axis=0)
        for _ in range(8):
            result = self.apply_nonlinear_map(result, 0.086)
        return result / (np.linalg.norm(result) + 1e-15)

    def method_hermite_spline_7_31(self, x: np.ndarray, p1=0.8815, p2=0.5464) -> np.ndarray:
        y = x * p1 + np.random.randn(*x.shape) * p2
        z = np.fft.fft(y, axis=0)
        w = np.abs(z) * np.exp(1j * (np.angle(z) + 0.433))
        result = np.fft.ifft(w, axis=0)
        for _ in range(8):
            result = self.apply_nonlinear_map(result, 0.276)
        return result / (np.linalg.norm(result) + 1e-15)

    def method_hermite_spline_7_32(self, x: np.ndarray, p1=0.0199, p2=0.1027) -> np.ndarray:
        y = x * p1 + np.random.randn(*x.shape) * p2
        z = np.fft.fft(y, axis=0)
        w = np.abs(z) * np.exp(1j * (np.angle(z) + 0.746))
        result = np.fft.ifft(w, axis=0)
        for _ in range(8):
            result = self.apply_nonlinear_map(result, 0.280)
        return result / (np.linalg.norm(result) + 1e-15)

    def method_hermite_spline_7_33(self, x: np.ndarray, p1=0.0156, p2=0.2164) -> np.ndarray:
        y = x * p1 + np.random.randn(*x.shape) * p2
        z = np.fft.fft(y, axis=0)
        w = np.abs(z) * np.exp(1j * (np.angle(z) + 0.697))
        result = np.fft.ifft(w, axis=0)
        for _ in range(2):
            result = self.apply_nonlinear_map(result, 0.455)
        return result / (np.linalg.norm(result) + 1e-15)

    def method_hermite_spline_7_34(self, x: np.ndarray, p1=0.5695, p2=0.2949) -> np.ndarray:
        y = x * p1 + np.random.randn(*x.shape) * p2
        z = np.fft.fft(y, axis=0)
        w = np.abs(z) * np.exp(1j * (np.angle(z) + 0.218))
        result = np.fft.ifft(w, axis=0)
        for _ in range(5):
            result = self.apply_nonlinear_map(result, 0.114)
        return result / (np.linalg.norm(result) + 1e-15)
