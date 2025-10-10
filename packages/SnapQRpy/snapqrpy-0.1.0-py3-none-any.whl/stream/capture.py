import mss
import numpy as np
from PIL import Image
from typing import Optional, Tuple
from snapqrpy.utils.logger import Logger

class ScreenCapture:
    def __init__(self):
        self.logger = Logger("ScreenCapture")
        self.sct = mss.mss()
        self.monitor = 1
        
    def capture_screen(self) -> np.ndarray:
        monitor = self.sct.monitors[self.monitor]
        screenshot = self.sct.grab(monitor)
        img = Image.frombytes("RGB", screenshot.size, screenshot.rgb)
        return np.array(img)
    
    def capture_region(self, x: int, y: int, width: int, height: int) -> np.ndarray:
        monitor = {"top": y, "left": x, "width": width, "height": height}
        screenshot = self.sct.grab(monitor)
        img = Image.frombytes("RGB", screenshot.size, screenshot.rgb)
        return np.array(img)
    
    def get_screen_size(self) -> Tuple[int, int]:
        monitor = self.sct.monitors[self.monitor]
        return (monitor["width"], monitor["height"])
    
    def set_monitor(self, monitor_index: int):
        if 0 < monitor_index < len(self.sct.monitors):
            self.monitor = monitor_index
            self.logger.info(f"Monitor set to {monitor_index}")
