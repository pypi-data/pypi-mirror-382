import cv2
from pyzbar import pyzbar
from typing import Optional
from snapqrpy.utils.logger import Logger

class QRScanner:
    def __init__(self):
        self.logger = Logger("QRScanner")
        
    def scan(self, camera_index: int = 0, timeout: int = 30) -> str:
        cap = cv2.VideoCapture(camera_index)
        self.logger.info(f"Starting QR scan from camera {camera_index}...")
        
        try:
            frame_count = 0
            max_frames = timeout * 30
            
            while frame_count < max_frames:
                ret, frame = cap.read()
                if not ret:
                    continue
                
                decoded_objects = pyzbar.decode(frame)
                for obj in decoded_objects:
                    data = obj.data.decode('utf-8')
                    if data.startswith('snapqr://'):
                        self.logger.info(f"QR code detected: {data}")
                        cap.release()
                        cv2.destroyAllWindows()
                        return data
                
                cv2.imshow('QR Scanner - Press Q to quit', frame)
                if cv2.waitKey(1) & 0xFF == ord('q'):
                    break
                
                frame_count += 1
                
        finally:
            cap.release()
            cv2.destroyAllWindows()
        
        raise TimeoutError("QR code scan timeout")
    
    def scan_from_image(self, image_path: str) -> Optional[str]:
        image = cv2.imread(image_path)
        decoded_objects = pyzbar.decode(image)
        
        for obj in decoded_objects:
            data = obj.data.decode('utf-8')
            if data.startswith('snapqr://'):
                self.logger.info(f"QR code detected in image: {data}")
                return data
        
        return None
    
    def scan_from_screen(self) -> Optional[str]:
        import mss
        with mss.mss() as sct:
            monitor = sct.monitors[1]
            screenshot = sct.grab(monitor)
            img = cv2.cvtColor(cv2.UMat(screenshot), cv2.COLOR_BGRA2BGR)
            decoded_objects = pyzbar.decode(img)
            
            for obj in decoded_objects:
                data = obj.data.decode('utf-8')
                if data.startswith('snapqr://'):
                    return data
        
        return None
