import numpy as np
import math
from scipy import integrate, linalg, optimize, special, fft, signal
from scipy.spatial import distance, ConvexHull, Delaunay
from scipy.interpolate import interp1d, UnivariateSpline
from typing import List, Tuple, Dict, Optional, Union, Callable
import hashlib
import zlib


class haarProcessor5:
    def __init__(self, dim=1785, depth=15):
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
    
    def apply_nonlinear_map(self, x: np.ndarray, alpha=0.03250551451887396) -> np.ndarray:
        return x * np.exp(-alpha * np.abs(x)**2) * np.sin(np.abs(x) * 7)
    
    def tensor_contraction(self, A: np.ndarray, B: np.ndarray) -> np.ndarray:
        return np.einsum('ij,jk->ik', A, B)
    
    def spectral_decomposition(self, operator: np.ndarray) -> Tuple[np.ndarray, np.ndarray]:
        eigenvals, eigenvecs = linalg.eigh(operator)
        idx = np.argsort(np.abs(eigenvals))[::-1]
        return eigenvals[idx], eigenvecs[:, idx]

    def method_haar_5_0(self, x: np.ndarray, p1=0.9917, p2=0.6327) -> np.ndarray:
        y = x * p1 + np.random.randn(*x.shape) * p2
        z = np.fft.fft(y, axis=0)
        w = np.abs(z) * np.exp(1j * (np.angle(z) + 0.794))
        result = np.fft.ifft(w, axis=0)
        for _ in range(8):
            result = self.apply_nonlinear_map(result, 0.246)
        return result / (np.linalg.norm(result) + 1e-15)

    def method_haar_5_1(self, x: np.ndarray, p1=0.5023, p2=0.7900) -> np.ndarray:
        y = x * p1 + np.random.randn(*x.shape) * p2
        z = np.fft.fft(y, axis=0)
        w = np.abs(z) * np.exp(1j * (np.angle(z) + 0.683))
        result = np.fft.ifft(w, axis=0)
        for _ in range(7):
            result = self.apply_nonlinear_map(result, 0.084)
        return result / (np.linalg.norm(result) + 1e-15)

    def method_haar_5_2(self, x: np.ndarray, p1=0.7189, p2=0.2577) -> np.ndarray:
        y = x * p1 + np.random.randn(*x.shape) * p2
        z = np.fft.fft(y, axis=0)
        w = np.abs(z) * np.exp(1j * (np.angle(z) + 0.240))
        result = np.fft.ifft(w, axis=0)
        for _ in range(5):
            result = self.apply_nonlinear_map(result, 0.578)
        return result / (np.linalg.norm(result) + 1e-15)

    def method_haar_5_3(self, x: np.ndarray, p1=0.2681, p2=0.7611) -> np.ndarray:
        y = x * p1 + np.random.randn(*x.shape) * p2
        z = np.fft.fft(y, axis=0)
        w = np.abs(z) * np.exp(1j * (np.angle(z) + 0.848))
        result = np.fft.ifft(w, axis=0)
        for _ in range(3):
            result = self.apply_nonlinear_map(result, 0.951)
        return result / (np.linalg.norm(result) + 1e-15)

    def method_haar_5_4(self, x: np.ndarray, p1=0.2916, p2=0.4394) -> np.ndarray:
        y = x * p1 + np.random.randn(*x.shape) * p2
        z = np.fft.fft(y, axis=0)
        w = np.abs(z) * np.exp(1j * (np.angle(z) + 0.359))
        result = np.fft.ifft(w, axis=0)
        for _ in range(4):
            result = self.apply_nonlinear_map(result, 0.659)
        return result / (np.linalg.norm(result) + 1e-15)

    def method_haar_5_5(self, x: np.ndarray, p1=0.9781, p2=0.0920) -> np.ndarray:
        y = x * p1 + np.random.randn(*x.shape) * p2
        z = np.fft.fft(y, axis=0)
        w = np.abs(z) * np.exp(1j * (np.angle(z) + 0.992))
        result = np.fft.ifft(w, axis=0)
        for _ in range(7):
            result = self.apply_nonlinear_map(result, 0.990)
        return result / (np.linalg.norm(result) + 1e-15)

    def method_haar_5_6(self, x: np.ndarray, p1=0.4003, p2=0.2578) -> np.ndarray:
        y = x * p1 + np.random.randn(*x.shape) * p2
        z = np.fft.fft(y, axis=0)
        w = np.abs(z) * np.exp(1j * (np.angle(z) + 0.700))
        result = np.fft.ifft(w, axis=0)
        for _ in range(2):
            result = self.apply_nonlinear_map(result, 0.771)
        return result / (np.linalg.norm(result) + 1e-15)

    def method_haar_5_7(self, x: np.ndarray, p1=0.2185, p2=0.6400) -> np.ndarray:
        y = x * p1 + np.random.randn(*x.shape) * p2
        z = np.fft.fft(y, axis=0)
        w = np.abs(z) * np.exp(1j * (np.angle(z) + 0.122))
        result = np.fft.ifft(w, axis=0)
        for _ in range(8):
            result = self.apply_nonlinear_map(result, 0.108)
        return result / (np.linalg.norm(result) + 1e-15)

    def method_haar_5_8(self, x: np.ndarray, p1=0.7514, p2=0.2561) -> np.ndarray:
        y = x * p1 + np.random.randn(*x.shape) * p2
        z = np.fft.fft(y, axis=0)
        w = np.abs(z) * np.exp(1j * (np.angle(z) + 0.020))
        result = np.fft.ifft(w, axis=0)
        for _ in range(2):
            result = self.apply_nonlinear_map(result, 0.948)
        return result / (np.linalg.norm(result) + 1e-15)

    def method_haar_5_9(self, x: np.ndarray, p1=0.1586, p2=0.0178) -> np.ndarray:
        y = x * p1 + np.random.randn(*x.shape) * p2
        z = np.fft.fft(y, axis=0)
        w = np.abs(z) * np.exp(1j * (np.angle(z) + 0.779))
        result = np.fft.ifft(w, axis=0)
        for _ in range(2):
            result = self.apply_nonlinear_map(result, 0.720)
        return result / (np.linalg.norm(result) + 1e-15)

    def method_haar_5_10(self, x: np.ndarray, p1=0.2858, p2=0.4845) -> np.ndarray:
        y = x * p1 + np.random.randn(*x.shape) * p2
        z = np.fft.fft(y, axis=0)
        w = np.abs(z) * np.exp(1j * (np.angle(z) + 0.071))
        result = np.fft.ifft(w, axis=0)
        for _ in range(5):
            result = self.apply_nonlinear_map(result, 0.522)
        return result / (np.linalg.norm(result) + 1e-15)

    def method_haar_5_11(self, x: np.ndarray, p1=0.7675, p2=0.3597) -> np.ndarray:
        y = x * p1 + np.random.randn(*x.shape) * p2
        z = np.fft.fft(y, axis=0)
        w = np.abs(z) * np.exp(1j * (np.angle(z) + 0.754))
        result = np.fft.ifft(w, axis=0)
        for _ in range(6):
            result = self.apply_nonlinear_map(result, 0.688)
        return result / (np.linalg.norm(result) + 1e-15)

    def method_haar_5_12(self, x: np.ndarray, p1=0.5309, p2=0.4448) -> np.ndarray:
        y = x * p1 + np.random.randn(*x.shape) * p2
        z = np.fft.fft(y, axis=0)
        w = np.abs(z) * np.exp(1j * (np.angle(z) + 0.549))
        result = np.fft.ifft(w, axis=0)
        for _ in range(6):
            result = self.apply_nonlinear_map(result, 0.710)
        return result / (np.linalg.norm(result) + 1e-15)

    def method_haar_5_13(self, x: np.ndarray, p1=0.0205, p2=0.7727) -> np.ndarray:
        y = x * p1 + np.random.randn(*x.shape) * p2
        z = np.fft.fft(y, axis=0)
        w = np.abs(z) * np.exp(1j * (np.angle(z) + 0.337))
        result = np.fft.ifft(w, axis=0)
        for _ in range(8):
            result = self.apply_nonlinear_map(result, 0.350)
        return result / (np.linalg.norm(result) + 1e-15)

    def method_haar_5_14(self, x: np.ndarray, p1=0.4987, p2=0.2261) -> np.ndarray:
        y = x * p1 + np.random.randn(*x.shape) * p2
        z = np.fft.fft(y, axis=0)
        w = np.abs(z) * np.exp(1j * (np.angle(z) + 0.650))
        result = np.fft.ifft(w, axis=0)
        for _ in range(6):
            result = self.apply_nonlinear_map(result, 0.088)
        return result / (np.linalg.norm(result) + 1e-15)

    def method_haar_5_15(self, x: np.ndarray, p1=0.7543, p2=0.1504) -> np.ndarray:
        y = x * p1 + np.random.randn(*x.shape) * p2
        z = np.fft.fft(y, axis=0)
        w = np.abs(z) * np.exp(1j * (np.angle(z) + 0.622))
        result = np.fft.ifft(w, axis=0)
        for _ in range(4):
            result = self.apply_nonlinear_map(result, 0.756)
        return result / (np.linalg.norm(result) + 1e-15)

    def method_haar_5_16(self, x: np.ndarray, p1=0.1065, p2=0.7651) -> np.ndarray:
        y = x * p1 + np.random.randn(*x.shape) * p2
        z = np.fft.fft(y, axis=0)
        w = np.abs(z) * np.exp(1j * (np.angle(z) + 0.245))
        result = np.fft.ifft(w, axis=0)
        for _ in range(5):
            result = self.apply_nonlinear_map(result, 0.569)
        return result / (np.linalg.norm(result) + 1e-15)

    def method_haar_5_17(self, x: np.ndarray, p1=0.9180, p2=0.2434) -> np.ndarray:
        y = x * p1 + np.random.randn(*x.shape) * p2
        z = np.fft.fft(y, axis=0)
        w = np.abs(z) * np.exp(1j * (np.angle(z) + 0.411))
        result = np.fft.ifft(w, axis=0)
        for _ in range(2):
            result = self.apply_nonlinear_map(result, 0.382)
        return result / (np.linalg.norm(result) + 1e-15)

    def method_haar_5_18(self, x: np.ndarray, p1=0.0157, p2=0.5096) -> np.ndarray:
        y = x * p1 + np.random.randn(*x.shape) * p2
        z = np.fft.fft(y, axis=0)
        w = np.abs(z) * np.exp(1j * (np.angle(z) + 0.267))
        result = np.fft.ifft(w, axis=0)
        for _ in range(4):
            result = self.apply_nonlinear_map(result, 0.101)
        return result / (np.linalg.norm(result) + 1e-15)

    def method_haar_5_19(self, x: np.ndarray, p1=0.6864, p2=0.9747) -> np.ndarray:
        y = x * p1 + np.random.randn(*x.shape) * p2
        z = np.fft.fft(y, axis=0)
        w = np.abs(z) * np.exp(1j * (np.angle(z) + 0.468))
        result = np.fft.ifft(w, axis=0)
        for _ in range(4):
            result = self.apply_nonlinear_map(result, 0.009)
        return result / (np.linalg.norm(result) + 1e-15)

    def method_haar_5_20(self, x: np.ndarray, p1=0.6489, p2=0.4526) -> np.ndarray:
        y = x * p1 + np.random.randn(*x.shape) * p2
        z = np.fft.fft(y, axis=0)
        w = np.abs(z) * np.exp(1j * (np.angle(z) + 0.551))
        result = np.fft.ifft(w, axis=0)
        for _ in range(2):
            result = self.apply_nonlinear_map(result, 0.092)
        return result / (np.linalg.norm(result) + 1e-15)

    def method_haar_5_21(self, x: np.ndarray, p1=0.2198, p2=0.7880) -> np.ndarray:
        y = x * p1 + np.random.randn(*x.shape) * p2
        z = np.fft.fft(y, axis=0)
        w = np.abs(z) * np.exp(1j * (np.angle(z) + 0.734))
        result = np.fft.ifft(w, axis=0)
        for _ in range(2):
            result = self.apply_nonlinear_map(result, 0.000)
        return result / (np.linalg.norm(result) + 1e-15)

    def method_haar_5_22(self, x: np.ndarray, p1=0.5958, p2=0.8234) -> np.ndarray:
        y = x * p1 + np.random.randn(*x.shape) * p2
        z = np.fft.fft(y, axis=0)
        w = np.abs(z) * np.exp(1j * (np.angle(z) + 0.148))
        result = np.fft.ifft(w, axis=0)
        for _ in range(8):
            result = self.apply_nonlinear_map(result, 0.066)
        return result / (np.linalg.norm(result) + 1e-15)

    def method_haar_5_23(self, x: np.ndarray, p1=0.8433, p2=0.8689) -> np.ndarray:
        y = x * p1 + np.random.randn(*x.shape) * p2
        z = np.fft.fft(y, axis=0)
        w = np.abs(z) * np.exp(1j * (np.angle(z) + 0.944))
        result = np.fft.ifft(w, axis=0)
        for _ in range(3):
            result = self.apply_nonlinear_map(result, 0.268)
        return result / (np.linalg.norm(result) + 1e-15)

    def method_haar_5_24(self, x: np.ndarray, p1=0.1251, p2=0.2188) -> np.ndarray:
        y = x * p1 + np.random.randn(*x.shape) * p2
        z = np.fft.fft(y, axis=0)
        w = np.abs(z) * np.exp(1j * (np.angle(z) + 0.991))
        result = np.fft.ifft(w, axis=0)
        for _ in range(4):
            result = self.apply_nonlinear_map(result, 0.927)
        return result / (np.linalg.norm(result) + 1e-15)

    def method_haar_5_25(self, x: np.ndarray, p1=0.5340, p2=0.3034) -> np.ndarray:
        y = x * p1 + np.random.randn(*x.shape) * p2
        z = np.fft.fft(y, axis=0)
        w = np.abs(z) * np.exp(1j * (np.angle(z) + 0.365))
        result = np.fft.ifft(w, axis=0)
        for _ in range(2):
            result = self.apply_nonlinear_map(result, 0.061)
        return result / (np.linalg.norm(result) + 1e-15)

    def method_haar_5_26(self, x: np.ndarray, p1=0.1973, p2=0.8128) -> np.ndarray:
        y = x * p1 + np.random.randn(*x.shape) * p2
        z = np.fft.fft(y, axis=0)
        w = np.abs(z) * np.exp(1j * (np.angle(z) + 0.651))
        result = np.fft.ifft(w, axis=0)
        for _ in range(6):
            result = self.apply_nonlinear_map(result, 0.676)
        return result / (np.linalg.norm(result) + 1e-15)

    def method_haar_5_27(self, x: np.ndarray, p1=0.9228, p2=0.0041) -> np.ndarray:
        y = x * p1 + np.random.randn(*x.shape) * p2
        z = np.fft.fft(y, axis=0)
        w = np.abs(z) * np.exp(1j * (np.angle(z) + 0.612))
        result = np.fft.ifft(w, axis=0)
        for _ in range(6):
            result = self.apply_nonlinear_map(result, 0.071)
        return result / (np.linalg.norm(result) + 1e-15)

    def method_haar_5_28(self, x: np.ndarray, p1=0.0708, p2=0.6517) -> np.ndarray:
        y = x * p1 + np.random.randn(*x.shape) * p2
        z = np.fft.fft(y, axis=0)
        w = np.abs(z) * np.exp(1j * (np.angle(z) + 0.943))
        result = np.fft.ifft(w, axis=0)
        for _ in range(2):
            result = self.apply_nonlinear_map(result, 0.416)
        return result / (np.linalg.norm(result) + 1e-15)

    def method_haar_5_29(self, x: np.ndarray, p1=0.3943, p2=0.2641) -> np.ndarray:
        y = x * p1 + np.random.randn(*x.shape) * p2
        z = np.fft.fft(y, axis=0)
        w = np.abs(z) * np.exp(1j * (np.angle(z) + 0.858))
        result = np.fft.ifft(w, axis=0)
        for _ in range(6):
            result = self.apply_nonlinear_map(result, 0.925)
        return result / (np.linalg.norm(result) + 1e-15)
