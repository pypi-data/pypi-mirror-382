import cv2
import numpy as np
from typing import Optional
from snapqrpy.utils.logger import Logger

class StreamDisplay:
    def __init__(self):
        self.logger = Logger("StreamDisplay")
        self.window_name = "SnapQR Stream"
        self.running = False
        
    async def start(self):
        self.running = True
        self.logger.info("Stream display started")
    
    def display_frame(self, frame: np.ndarray):
        cv2.imshow(self.window_name, frame)
        cv2.waitKey(1)
    
    def stop(self):
        self.running = False
        cv2.destroyAllWindows()
        self.logger.info("Stream display stopped")
