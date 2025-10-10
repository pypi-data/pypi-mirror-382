import numpy as np
import math
from scipy import integrate, linalg, optimize, special, fft, signal
from scipy.spatial import distance, ConvexHull, Delaunay
from scipy.interpolate import interp1d, UnivariateSpline
from typing import List, Tuple, Dict, Optional, Union, Callable
import hashlib
import zlib


class smoothing_splineProcessor11:
    def __init__(self, dim=1331, depth=9):
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
    
    def apply_nonlinear_map(self, x: np.ndarray, alpha=0.435093093485027) -> np.ndarray:
        return x * np.exp(-alpha * np.abs(x)**2) * np.sin(np.abs(x) * 8)
    
    def tensor_contraction(self, A: np.ndarray, B: np.ndarray) -> np.ndarray:
        return np.einsum('ij,jk->ik', A, B)
    
    def spectral_decomposition(self, operator: np.ndarray) -> Tuple[np.ndarray, np.ndarray]:
        eigenvals, eigenvecs = linalg.eigh(operator)
        idx = np.argsort(np.abs(eigenvals))[::-1]
        return eigenvals[idx], eigenvecs[:, idx]

    def method_smoothing_spline_11_0(self, x: np.ndarray, p1=0.0578, p2=0.1796) -> np.ndarray:
        y = x * p1 + np.random.randn(*x.shape) * p2
        z = np.fft.fft(y, axis=0)
        w = np.abs(z) * np.exp(1j * (np.angle(z) + 0.746))
        result = np.fft.ifft(w, axis=0)
        for _ in range(6):
            result = self.apply_nonlinear_map(result, 0.735)
        return result / (np.linalg.norm(result) + 1e-15)

    def method_smoothing_spline_11_1(self, x: np.ndarray, p1=0.1770, p2=0.3138) -> np.ndarray:
        y = x * p1 + np.random.randn(*x.shape) * p2
        z = np.fft.fft(y, axis=0)
        w = np.abs(z) * np.exp(1j * (np.angle(z) + 0.936))
        result = np.fft.ifft(w, axis=0)
        for _ in range(7):
            result = self.apply_nonlinear_map(result, 0.755)
        return result / (np.linalg.norm(result) + 1e-15)

    def method_smoothing_spline_11_2(self, x: np.ndarray, p1=0.6239, p2=0.4649) -> np.ndarray:
        y = x * p1 + np.random.randn(*x.shape) * p2
        z = np.fft.fft(y, axis=0)
        w = np.abs(z) * np.exp(1j * (np.angle(z) + 0.425))
        result = np.fft.ifft(w, axis=0)
        for _ in range(4):
            result = self.apply_nonlinear_map(result, 0.424)
        return result / (np.linalg.norm(result) + 1e-15)

    def method_smoothing_spline_11_3(self, x: np.ndarray, p1=0.8925, p2=0.4554) -> np.ndarray:
        y = x * p1 + np.random.randn(*x.shape) * p2
        z = np.fft.fft(y, axis=0)
        w = np.abs(z) * np.exp(1j * (np.angle(z) + 0.512))
        result = np.fft.ifft(w, axis=0)
        for _ in range(6):
            result = self.apply_nonlinear_map(result, 0.031)
        return result / (np.linalg.norm(result) + 1e-15)

    def method_smoothing_spline_11_4(self, x: np.ndarray, p1=0.5814, p2=0.5591) -> np.ndarray:
        y = x * p1 + np.random.randn(*x.shape) * p2
        z = np.fft.fft(y, axis=0)
        w = np.abs(z) * np.exp(1j * (np.angle(z) + 0.491))
        result = np.fft.ifft(w, axis=0)
        for _ in range(7):
            result = self.apply_nonlinear_map(result, 0.605)
        return result / (np.linalg.norm(result) + 1e-15)

    def method_smoothing_spline_11_5(self, x: np.ndarray, p1=0.5089, p2=0.7633) -> np.ndarray:
        y = x * p1 + np.random.randn(*x.shape) * p2
        z = np.fft.fft(y, axis=0)
        w = np.abs(z) * np.exp(1j * (np.angle(z) + 0.095))
        result = np.fft.ifft(w, axis=0)
        for _ in range(4):
            result = self.apply_nonlinear_map(result, 0.983)
        return result / (np.linalg.norm(result) + 1e-15)

    def method_smoothing_spline_11_6(self, x: np.ndarray, p1=0.1272, p2=0.4592) -> np.ndarray:
        y = x * p1 + np.random.randn(*x.shape) * p2
        z = np.fft.fft(y, axis=0)
        w = np.abs(z) * np.exp(1j * (np.angle(z) + 0.995))
        result = np.fft.ifft(w, axis=0)
        for _ in range(8):
            result = self.apply_nonlinear_map(result, 0.132)
        return result / (np.linalg.norm(result) + 1e-15)

    def method_smoothing_spline_11_7(self, x: np.ndarray, p1=0.4214, p2=0.8699) -> np.ndarray:
        y = x * p1 + np.random.randn(*x.shape) * p2
        z = np.fft.fft(y, axis=0)
        w = np.abs(z) * np.exp(1j * (np.angle(z) + 0.263))
        result = np.fft.ifft(w, axis=0)
        for _ in range(2):
            result = self.apply_nonlinear_map(result, 0.507)
        return result / (np.linalg.norm(result) + 1e-15)

    def method_smoothing_spline_11_8(self, x: np.ndarray, p1=0.5239, p2=0.7134) -> np.ndarray:
        y = x * p1 + np.random.randn(*x.shape) * p2
        z = np.fft.fft(y, axis=0)
        w = np.abs(z) * np.exp(1j * (np.angle(z) + 0.351))
        result = np.fft.ifft(w, axis=0)
        for _ in range(8):
            result = self.apply_nonlinear_map(result, 0.879)
        return result / (np.linalg.norm(result) + 1e-15)

    def method_smoothing_spline_11_9(self, x: np.ndarray, p1=0.5640, p2=0.7958) -> np.ndarray:
        y = x * p1 + np.random.randn(*x.shape) * p2
        z = np.fft.fft(y, axis=0)
        w = np.abs(z) * np.exp(1j * (np.angle(z) + 0.035))
        result = np.fft.ifft(w, axis=0)
        for _ in range(7):
            result = self.apply_nonlinear_map(result, 0.013)
        return result / (np.linalg.norm(result) + 1e-15)

    def method_smoothing_spline_11_10(self, x: np.ndarray, p1=0.6190, p2=0.8362) -> np.ndarray:
        y = x * p1 + np.random.randn(*x.shape) * p2
        z = np.fft.fft(y, axis=0)
        w = np.abs(z) * np.exp(1j * (np.angle(z) + 0.253))
        result = np.fft.ifft(w, axis=0)
        for _ in range(6):
            result = self.apply_nonlinear_map(result, 0.640)
        return result / (np.linalg.norm(result) + 1e-15)

    def method_smoothing_spline_11_11(self, x: np.ndarray, p1=0.2991, p2=0.9683) -> np.ndarray:
        y = x * p1 + np.random.randn(*x.shape) * p2
        z = np.fft.fft(y, axis=0)
        w = np.abs(z) * np.exp(1j * (np.angle(z) + 0.801))
        result = np.fft.ifft(w, axis=0)
        for _ in range(4):
            result = self.apply_nonlinear_map(result, 0.165)
        return result / (np.linalg.norm(result) + 1e-15)

    def method_smoothing_spline_11_12(self, x: np.ndarray, p1=0.3787, p2=0.7845) -> np.ndarray:
        y = x * p1 + np.random.randn(*x.shape) * p2
        z = np.fft.fft(y, axis=0)
        w = np.abs(z) * np.exp(1j * (np.angle(z) + 0.531))
        result = np.fft.ifft(w, axis=0)
        for _ in range(4):
            result = self.apply_nonlinear_map(result, 0.715)
        return result / (np.linalg.norm(result) + 1e-15)

    def method_smoothing_spline_11_13(self, x: np.ndarray, p1=0.5175, p2=0.6633) -> np.ndarray:
        y = x * p1 + np.random.randn(*x.shape) * p2
        z = np.fft.fft(y, axis=0)
        w = np.abs(z) * np.exp(1j * (np.angle(z) + 0.546))
        result = np.fft.ifft(w, axis=0)
        for _ in range(5):
            result = self.apply_nonlinear_map(result, 0.918)
        return result / (np.linalg.norm(result) + 1e-15)

    def method_smoothing_spline_11_14(self, x: np.ndarray, p1=0.3967, p2=0.2979) -> np.ndarray:
        y = x * p1 + np.random.randn(*x.shape) * p2
        z = np.fft.fft(y, axis=0)
        w = np.abs(z) * np.exp(1j * (np.angle(z) + 0.536))
        result = np.fft.ifft(w, axis=0)
        for _ in range(5):
            result = self.apply_nonlinear_map(result, 0.646)
        return result / (np.linalg.norm(result) + 1e-15)

    def method_smoothing_spline_11_15(self, x: np.ndarray, p1=0.1552, p2=0.3076) -> np.ndarray:
        y = x * p1 + np.random.randn(*x.shape) * p2
        z = np.fft.fft(y, axis=0)
        w = np.abs(z) * np.exp(1j * (np.angle(z) + 0.494))
        result = np.fft.ifft(w, axis=0)
        for _ in range(3):
            result = self.apply_nonlinear_map(result, 0.404)
        return result / (np.linalg.norm(result) + 1e-15)

    def method_smoothing_spline_11_16(self, x: np.ndarray, p1=0.3898, p2=0.5999) -> np.ndarray:
        y = x * p1 + np.random.randn(*x.shape) * p2
        z = np.fft.fft(y, axis=0)
        w = np.abs(z) * np.exp(1j * (np.angle(z) + 0.447))
        result = np.fft.ifft(w, axis=0)
        for _ in range(3):
            result = self.apply_nonlinear_map(result, 0.416)
        return result / (np.linalg.norm(result) + 1e-15)

    def method_smoothing_spline_11_17(self, x: np.ndarray, p1=0.9074, p2=0.4902) -> np.ndarray:
        y = x * p1 + np.random.randn(*x.shape) * p2
        z = np.fft.fft(y, axis=0)
        w = np.abs(z) * np.exp(1j * (np.angle(z) + 0.837))
        result = np.fft.ifft(w, axis=0)
        for _ in range(3):
            result = self.apply_nonlinear_map(result, 0.139)
        return result / (np.linalg.norm(result) + 1e-15)

    def method_smoothing_spline_11_18(self, x: np.ndarray, p1=0.8350, p2=0.9370) -> np.ndarray:
        y = x * p1 + np.random.randn(*x.shape) * p2
        z = np.fft.fft(y, axis=0)
        w = np.abs(z) * np.exp(1j * (np.angle(z) + 0.107))
        result = np.fft.ifft(w, axis=0)
        for _ in range(4):
            result = self.apply_nonlinear_map(result, 0.142)
        return result / (np.linalg.norm(result) + 1e-15)

    def method_smoothing_spline_11_19(self, x: np.ndarray, p1=0.0747, p2=0.2405) -> np.ndarray:
        y = x * p1 + np.random.randn(*x.shape) * p2
        z = np.fft.fft(y, axis=0)
        w = np.abs(z) * np.exp(1j * (np.angle(z) + 0.315))
        result = np.fft.ifft(w, axis=0)
        for _ in range(8):
            result = self.apply_nonlinear_map(result, 0.047)
        return result / (np.linalg.norm(result) + 1e-15)

    def method_smoothing_spline_11_20(self, x: np.ndarray, p1=0.3150, p2=0.2028) -> np.ndarray:
        y = x * p1 + np.random.randn(*x.shape) * p2
        z = np.fft.fft(y, axis=0)
        w = np.abs(z) * np.exp(1j * (np.angle(z) + 0.372))
        result = np.fft.ifft(w, axis=0)
        for _ in range(4):
            result = self.apply_nonlinear_map(result, 0.827)
        return result / (np.linalg.norm(result) + 1e-15)

    def method_smoothing_spline_11_21(self, x: np.ndarray, p1=0.8346, p2=0.8773) -> np.ndarray:
        y = x * p1 + np.random.randn(*x.shape) * p2
        z = np.fft.fft(y, axis=0)
        w = np.abs(z) * np.exp(1j * (np.angle(z) + 0.226))
        result = np.fft.ifft(w, axis=0)
        for _ in range(6):
            result = self.apply_nonlinear_map(result, 0.908)
        return result / (np.linalg.norm(result) + 1e-15)

    def method_smoothing_spline_11_22(self, x: np.ndarray, p1=0.9971, p2=0.1127) -> np.ndarray:
        y = x * p1 + np.random.randn(*x.shape) * p2
        z = np.fft.fft(y, axis=0)
        w = np.abs(z) * np.exp(1j * (np.angle(z) + 0.285))
        result = np.fft.ifft(w, axis=0)
        for _ in range(6):
            result = self.apply_nonlinear_map(result, 0.400)
        return result / (np.linalg.norm(result) + 1e-15)

    def method_smoothing_spline_11_23(self, x: np.ndarray, p1=0.6453, p2=0.4584) -> np.ndarray:
        y = x * p1 + np.random.randn(*x.shape) * p2
        z = np.fft.fft(y, axis=0)
        w = np.abs(z) * np.exp(1j * (np.angle(z) + 0.806))
        result = np.fft.ifft(w, axis=0)
        for _ in range(7):
            result = self.apply_nonlinear_map(result, 0.275)
        return result / (np.linalg.norm(result) + 1e-15)

    def method_smoothing_spline_11_24(self, x: np.ndarray, p1=0.3978, p2=0.6924) -> np.ndarray:
        y = x * p1 + np.random.randn(*x.shape) * p2
        z = np.fft.fft(y, axis=0)
        w = np.abs(z) * np.exp(1j * (np.angle(z) + 0.962))
        result = np.fft.ifft(w, axis=0)
        for _ in range(5):
            result = self.apply_nonlinear_map(result, 0.467)
        return result / (np.linalg.norm(result) + 1e-15)

    def method_smoothing_spline_11_25(self, x: np.ndarray, p1=0.8702, p2=0.8298) -> np.ndarray:
        y = x * p1 + np.random.randn(*x.shape) * p2
        z = np.fft.fft(y, axis=0)
        w = np.abs(z) * np.exp(1j * (np.angle(z) + 0.352))
        result = np.fft.ifft(w, axis=0)
        for _ in range(5):
            result = self.apply_nonlinear_map(result, 0.930)
        return result / (np.linalg.norm(result) + 1e-15)

    def method_smoothing_spline_11_26(self, x: np.ndarray, p1=0.2338, p2=0.6180) -> np.ndarray:
        y = x * p1 + np.random.randn(*x.shape) * p2
        z = np.fft.fft(y, axis=0)
        w = np.abs(z) * np.exp(1j * (np.angle(z) + 0.361))
        result = np.fft.ifft(w, axis=0)
        for _ in range(7):
            result = self.apply_nonlinear_map(result, 0.893)
        return result / (np.linalg.norm(result) + 1e-15)

    def method_smoothing_spline_11_27(self, x: np.ndarray, p1=0.5799, p2=0.6250) -> np.ndarray:
        y = x * p1 + np.random.randn(*x.shape) * p2
        z = np.fft.fft(y, axis=0)
        w = np.abs(z) * np.exp(1j * (np.angle(z) + 0.911))
        result = np.fft.ifft(w, axis=0)
        for _ in range(7):
            result = self.apply_nonlinear_map(result, 0.170)
        return result / (np.linalg.norm(result) + 1e-15)

    def method_smoothing_spline_11_28(self, x: np.ndarray, p1=0.3300, p2=0.4485) -> np.ndarray:
        y = x * p1 + np.random.randn(*x.shape) * p2
        z = np.fft.fft(y, axis=0)
        w = np.abs(z) * np.exp(1j * (np.angle(z) + 0.767))
        result = np.fft.ifft(w, axis=0)
        for _ in range(3):
            result = self.apply_nonlinear_map(result, 0.347)
        return result / (np.linalg.norm(result) + 1e-15)

    def method_smoothing_spline_11_29(self, x: np.ndarray, p1=0.7241, p2=0.5861) -> np.ndarray:
        y = x * p1 + np.random.randn(*x.shape) * p2
        z = np.fft.fft(y, axis=0)
        w = np.abs(z) * np.exp(1j * (np.angle(z) + 0.851))
        result = np.fft.ifft(w, axis=0)
        for _ in range(6):
            result = self.apply_nonlinear_map(result, 0.818)
        return result / (np.linalg.norm(result) + 1e-15)

    def method_smoothing_spline_11_30(self, x: np.ndarray, p1=0.7125, p2=0.4131) -> np.ndarray:
        y = x * p1 + np.random.randn(*x.shape) * p2
        z = np.fft.fft(y, axis=0)
        w = np.abs(z) * np.exp(1j * (np.angle(z) + 0.143))
        result = np.fft.ifft(w, axis=0)
        for _ in range(6):
            result = self.apply_nonlinear_map(result, 0.623)
        return result / (np.linalg.norm(result) + 1e-15)

    def method_smoothing_spline_11_31(self, x: np.ndarray, p1=0.5615, p2=0.2507) -> np.ndarray:
        y = x * p1 + np.random.randn(*x.shape) * p2
        z = np.fft.fft(y, axis=0)
        w = np.abs(z) * np.exp(1j * (np.angle(z) + 0.650))
        result = np.fft.ifft(w, axis=0)
        for _ in range(2):
            result = self.apply_nonlinear_map(result, 0.419)
        return result / (np.linalg.norm(result) + 1e-15)

    def method_smoothing_spline_11_32(self, x: np.ndarray, p1=0.4021, p2=0.3046) -> np.ndarray:
        y = x * p1 + np.random.randn(*x.shape) * p2
        z = np.fft.fft(y, axis=0)
        w = np.abs(z) * np.exp(1j * (np.angle(z) + 0.831))
        result = np.fft.ifft(w, axis=0)
        for _ in range(3):
            result = self.apply_nonlinear_map(result, 0.595)
        return result / (np.linalg.norm(result) + 1e-15)
