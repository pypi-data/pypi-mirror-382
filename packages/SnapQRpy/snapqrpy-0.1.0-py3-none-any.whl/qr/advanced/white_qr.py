"""
SnapQRpy - White QR Code Generator (سهل القراءة من الهاتف)
Developer: MERO (@QP4RM)
Telegram: https://t.me/QP4RM

مولد QR code بخلفية بيضاء ومربعات سوداء واضحة
مصمم خصيصاً لسهولة القراءة من الهواتف المحمولة
"""

import qrcode
from qrcode.image.svg import SvgPathImage, SvgFillImage
from typing import Optional, Literal


class WhiteQRGenerator:
    """
    مولد QR code احترافي بخلفية بيضاء نقية
    
    المميزات:
    - خلفية بيضاء نقية 100%
    - مربعات سوداء واضحة عالية التباين
    - تصحيح أخطاء عالي المستوى (Error Correction Level H)
    - حجم قابل للتخصيص
    - جودة عالية للمسح من الموبايل
    """
    
    def __init__(
        self, 
        box_size: int = 20,  # حجم أكبر لوضوح أفضل
        border: int = 4,
        error_correction: str = 'H'  # أعلى مستوى تصحيح أخطاء
    ):
        self.box_size = box_size
        self.border = border
        
        error_levels = {
            'L': qrcode.constants.ERROR_CORRECT_L,  # 7% تصحيح
            'M': qrcode.constants.ERROR_CORRECT_M,  # 15% تصحيح
            'Q': qrcode.constants.ERROR_CORRECT_Q,  # 25% تصحيح
            'H': qrcode.constants.ERROR_CORRECT_H,  # 30% تصحيح (الأفضل)
        }
        self.error_correction = error_levels.get(error_correction, qrcode.constants.ERROR_CORRECT_H)
    
    def generate_white_qr(
        self, 
        data: str,
        format: Literal['svg', 'png'] = 'svg',
        fill_color: str = 'black',
        back_color: str = 'white'
    ):
        """
        إنشاء QR code بخلفية بيضاء نقية
        
        Args:
            data: البيانات المراد تشفيرها
            format: صيغة الملف (svg أو png)
            fill_color: لون المربعات (افتراضي: أسود)
            back_color: لون الخلفية (افتراضي: أبيض)
        
        Returns:
            QR code image object
        """
        qr = qrcode.QRCode(
            version=None,  # سيتم تحديده تلقائياً حسب البيانات
            error_correction=self.error_correction,
            box_size=self.box_size,
            border=self.border,
        )
        
        qr.add_data(data)
        qr.make(fit=True)
        
        if format == 'svg':
            img = qr.make_image(
                image_factory=SvgFillImage,
                fill_color=fill_color,
                back_color=back_color
            )
        else:
            img = qr.make_image(
                fill_color=fill_color,
                back_color=back_color
            )
        
        return img
    
    def generate_high_contrast(self, data: str, filename: str = 'white_qr.svg'):
        """
        إنشاء QR code بأعلى تباين (أسود على أبيض)
        مثالي للقراءة من الهواتف في أي إضاءة
        """
        img = self.generate_white_qr(
            data=data,
            format='svg',
            fill_color='#000000',  # أسود نقي
            back_color='#FFFFFF'   # أبيض نقي
        )
        img.save(filename)
        return filename
    
    def generate_inverted(self, data: str, filename: str = 'inverted_qr.svg'):
        """
        إنشاء QR code معكوس (أبيض على أسود)
        مفيد للخلفيات الداكنة
        """
        img = self.generate_white_qr(
            data=data,
            format='svg',
            fill_color='#FFFFFF',  # أبيض
            back_color='#000000'   # أسود
        )
        img.save(filename)
        return filename
    
    def generate_colored(
        self, 
        data: str, 
        fill_color: str = '#1E40AF',  # أزرق داكن
        back_color: str = '#FFFFFF',  # أبيض
        filename: str = 'colored_qr.svg'
    ):
        """
        إنشاء QR code ملون بخلفية بيضاء
        يمكن اختيار أي لون للمربعات
        """
        img = self.generate_white_qr(
            data=data,
            format='svg',
            fill_color=fill_color,
            back_color=back_color
        )
        img.save(filename)
        return filename
    
    def print_ascii_white(self, data: str):
        """
        طباعة QR code في الطرفية بخلفية بيضاء (معكوس)
        """
        qr = qrcode.QRCode(
            version=1,
            error_correction=self.error_correction,
            box_size=1,
            border=2,
        )
        qr.add_data(data)
        qr.make(fit=True)
        
        qr.print_ascii(invert=True)


if __name__ == '__main__':
    generator = WhiteQRGenerator(box_size=20, error_correction='H')
    
    generator.generate_high_contrast(
        "https://t.me/QP4RM",
        "mero_white_qr.svg"
    )
    print("✅ تم إنشاء QR بخلفية بيضاء: mero_white_qr.svg")
