import numpy as np
import math
from typing import Tuple, List, Optional

class RayTracingEngine:
    def __init__(self, screen_width: int = 1920, screen_height: int = 1080):
        self.width = screen_width
        self.height = screen_height
        self.fov = 90
        self.max_depth = 5
        self.rays_cache = {}
        
    def trace_ray(self, origin: np.ndarray, direction: np.ndarray, depth: int = 0) -> np.ndarray:
        if depth > self.max_depth:
            return np.array([0, 0, 0])
        
        direction = direction / np.linalg.norm(direction)
        t_min = float('inf')
        hit_point = None
        hit_normal = None
        
        for i in range(100):
            t = i * 0.1
            point = origin + direction * t
            if self._intersects_sphere(point, np.array([0, 0, 5]), 1.0):
                if t < t_min:
                    t_min = t
                    hit_point = point
                    hit_normal = self._sphere_normal(point, np.array([0, 0, 5]))
        
        if hit_point is not None:
            reflected = self._reflect(direction, hit_normal)
            return self.trace_ray(hit_point + hit_normal * 0.001, reflected, depth + 1) * 0.8
        
        return self._sky_color(direction)
    
    def _intersects_sphere(self, point: np.ndarray, center: np.ndarray, radius: float) -> bool:
        return np.linalg.norm(point - center) < radius
    
    def _sphere_normal(self, point: np.ndarray, center: np.ndarray) -> np.ndarray:
        normal = point - center
        return normal / np.linalg.norm(normal)
    
    def _reflect(self, incident: np.ndarray, normal: np.ndarray) -> np.ndarray:
        return incident - 2 * np.dot(incident, normal) * normal
    
    def _sky_color(self, direction: np.ndarray) -> np.ndarray:
        t = 0.5 * (direction[1] + 1.0)
        return (1.0 - t) * np.array([1, 1, 1]) + t * np.array([0.5, 0.7, 1.0])
    
    def render_pixel(self, x: int, y: int) -> np.ndarray:
        u = (x + 0.5) / self.width
        v = (y + 0.5) / self.height
        
        aspect_ratio = self.width / self.height
        fov_rad = math.radians(self.fov)
        
        px = (2 * u - 1) * aspect_ratio * math.tan(fov_rad / 2)
        py = (1 - 2 * v) * math.tan(fov_rad / 2)
        
        direction = np.array([px, py, -1])
        origin = np.array([0, 0, 0])
        
        return self.trace_ray(origin, direction)
    
    def calculate_refraction(self, incident: np.ndarray, normal: np.ndarray, n1: float, n2: float) -> Optional[np.ndarray]:
        cos_i = -np.dot(normal, incident)
        eta = n1 / n2
        k = 1 - eta * eta * (1 - cos_i * cos_i)
        
        if k < 0:
            return None
        
        return eta * incident + (eta * cos_i - math.sqrt(k)) * normal
    
    def fresnel_reflectance(self, incident: np.ndarray, normal: np.ndarray, n1: float, n2: float) -> float:
        cos_i = -np.dot(normal, incident)
        sin_t = (n1 / n2) * math.sqrt(max(0, 1 - cos_i * cos_i))
        
        if sin_t >= 1:
            return 1.0
        
        cos_t = math.sqrt(max(0, 1 - sin_t * sin_t))
        
        rs = ((n2 * cos_i - n1 * cos_t) / (n2 * cos_i + n1 * cos_t)) ** 2
        rp = ((n1 * cos_i - n2 * cos_t) / (n1 * cos_i + n2 * cos_t)) ** 2
        
        return (rs + rp) / 2
    
    def compute_caustics(self, light_pos: np.ndarray, surfaces: List) -> np.ndarray:
        caustic_map = np.zeros((self.height, self.width, 3))
        
        for surface in surfaces:
            for i in range(1000):
                ray_dir = self._random_direction()
                refracted = self.calculate_refraction(ray_dir, surface.normal, 1.0, surface.ior)
                
                if refracted is not None:
                    hit = self._trace_to_plane(light_pos, refracted, surface.plane)
                    if hit is not None:
                        x, y = self._world_to_screen(hit)
                        if 0 <= x < self.width and 0 <= y < self.height:
                            caustic_map[y, x] += np.array([1, 1, 1])
        
        return caustic_map / np.max(caustic_map)
    
    def _random_direction(self) -> np.ndarray:
        theta = np.random.uniform(0, 2 * np.pi)
        phi = np.random.uniform(0, np.pi)
        
        x = np.sin(phi) * np.cos(theta)
        y = np.sin(phi) * np.sin(theta)
        z = np.cos(phi)
        
        return np.array([x, y, z])
    
    def _trace_to_plane(self, origin: np.ndarray, direction: np.ndarray, plane) -> Optional[np.ndarray]:
        denom = np.dot(plane.normal, direction)
        if abs(denom) > 1e-6:
            t = np.dot(plane.point - origin, plane.normal) / denom
            if t >= 0:
                return origin + direction * t
        return None
    
    def _world_to_screen(self, point: np.ndarray) -> Tuple[int, int]:
        x = int((point[0] + 1) * self.width / 2)
        y = int((1 - point[1]) * self.height / 2)
        return (x, y)
    
    def apply_tone_mapping(self, color: np.ndarray) -> np.ndarray:
        exposure = 1.0
        color = color * exposure
        return color / (color + 1)
    
    def gamma_correction(self, color: np.ndarray, gamma: float = 2.2) -> np.ndarray:
        return np.power(color, 1.0 / gamma)

class PhotonMapper:
    def __init__(self):
        self.photon_map = []
        self.max_photons = 100000
        
    def emit_photons(self, light_sources: List, scene_objects: List):
        for light in light_sources:
            for _ in range(light.intensity):
                photon_dir = self._sample_hemisphere(light.normal)
                self._trace_photon(light.position, photon_dir, light.power, scene_objects, 0)
    
    def _sample_hemisphere(self, normal: np.ndarray) -> np.ndarray:
        theta = np.random.uniform(0, 2 * np.pi)
        phi = np.arccos(np.random.uniform(0, 1))
        
        x = np.sin(phi) * np.cos(theta)
        y = np.sin(phi) * np.sin(theta)
        z = np.cos(phi)
        
        local_dir = np.array([x, y, z])
        return self._align_to_normal(local_dir, normal)
    
    def _align_to_normal(self, vec: np.ndarray, normal: np.ndarray) -> np.ndarray:
        up = np.array([0, 1, 0]) if abs(normal[1]) < 0.9 else np.array([1, 0, 0])
        tangent = np.cross(normal, up)
        tangent = tangent / np.linalg.norm(tangent)
        bitangent = np.cross(normal, tangent)
        
        return vec[0] * tangent + vec[1] * bitangent + vec[2] * normal
    
    def _trace_photon(self, pos: np.ndarray, direction: np.ndarray, power: np.ndarray, objects: List, depth: int):
        if depth > 5 or len(self.photon_map) >= self.max_photons:
            return
        
        hit = self._find_intersection(pos, direction, objects)
        if hit:
            self.photon_map.append({'position': hit.point, 'power': power, 'direction': direction})
            
            if np.random.random() < hit.material.diffuse:
                new_dir = self._sample_hemisphere(hit.normal)
                self._trace_photon(hit.point, new_dir, power * hit.material.albedo, objects, depth + 1)
    
    def _find_intersection(self, origin: np.ndarray, direction: np.ndarray, objects: List):
        return None
