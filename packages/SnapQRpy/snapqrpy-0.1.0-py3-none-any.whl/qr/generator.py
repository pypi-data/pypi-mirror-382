import qrcode
from typing import Optional, Any
from io import BytesIO
from snapqrpy.utils.logger import Logger

class QRGenerator:
    def __init__(self, version: int = 1, box_size: int = 10, border: int = 4):
        self.version = version
        self.box_size = box_size
        self.border = border
        self.logger = Logger("QRGenerator")
        
    def generate(self, data: str, error_correction: int = qrcode.constants.ERROR_CORRECT_L):
        qr = qrcode.QRCode(
            version=self.version,
            error_correction=error_correction,
            box_size=self.box_size,
            border=self.border,
        )
        qr.add_data(data)
        qr.make(fit=True)
        img = qr.make_image(fill_color="black", back_color="white")
        self.logger.info(f"Generated QR code for data: {data[:50]}...")
        return img
    
    def generate_with_logo(self, data: str, logo_path: str):
        from PIL import Image
        qr_img = self.generate(data)
        logo = Image.open(logo_path)
        qr_width, qr_height = qr_img.size
        logo_size = qr_width // 4
        logo = logo.resize((logo_size, logo_size))
        logo_pos = ((qr_width - logo_size) // 2, (qr_height - logo_size) // 2)
        qr_img.paste(logo, logo_pos)
        return qr_img
    
    def generate_colored(self, data: str, fill_color: str = "black", back_color: str = "white"):
        qr = qrcode.QRCode(
            version=self.version,
            error_correction=qrcode.constants.ERROR_CORRECT_H,
            box_size=self.box_size,
            border=self.border,
        )
        qr.add_data(data)
        qr.make(fit=True)
        return qr.make_image(fill_color=fill_color, back_color=back_color)
    
    def to_bytes(self, qr_image) -> bytes:
        buffer = BytesIO()
        qr_image.save(buffer, format='PNG')
        return buffer.getvalue()
    
    def save(self, qr_image, path: str):
        qr_image.save(path)
        self.logger.info(f"QR code saved to {path}")
