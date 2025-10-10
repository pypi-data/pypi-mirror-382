"""
SnapQRpy - Engineering QR Code Generator (هندسة قوية ومتقدمة)
Developer: MERO (@QP4RM)
Telegram: https://t.me/QP4RM

مولد QR code بتقنيات هندسية متقدمة:
- تحسين البيانات والضغط
- إضافة معلومات تصحيح الأخطاء
- تحليل وقياس جودة QR
- تحسين للقراءة في ظروف صعبة
"""

import qrcode
from qrcode.image.svg import SvgPathImage, SvgFillImage
import hashlib
import json
from typing import Dict, List, Optional, Tuple
import math


class EngineeringQRGenerator:
    """
    مولد QR code هندسي متقدم
    
    المميزات الهندسية:
    - تحليل البيانات وتحديد الحجم الأمثل
    - حساب معدل تصحيح الأخطاء المطلوب
    - إضافة checksum للتحقق من صحة البيانات
    - تحسين الكفاءة والموثوقية
    - قياس جودة QR code
    """
    
    def __init__(self):
        self.metadata = {}
        self.quality_metrics = {}
    
    def analyze_data(self, data: str) -> Dict:
        """
        تحليل هندسي للبيانات قبل إنشاء QR
        """
        analysis = {
            'data_length': len(data),
            'data_type': self._detect_data_type(data),
            'compression_ratio': self._calculate_compression_ratio(data),
            'recommended_version': self._calculate_optimal_version(data),
            'recommended_error_correction': self._recommend_error_level(data),
            'estimated_modules': self._estimate_module_count(data),
            'data_hash': hashlib.sha256(data.encode()).hexdigest()[:16]
        }
        return analysis
    
    def _detect_data_type(self, data: str) -> str:
        """كشف نوع البيانات (رابط، نص، رقم، إلخ)"""
        if data.startswith(('http://', 'https://', 'ftp://')):
            return 'URL'
        elif data.startswith(('tel:', 'mailto:')):
            return 'Contact'
        elif data.startswith('BEGIN:VCARD'):
            return 'VCard'
        elif data.isdigit():
            return 'Numeric'
        elif data.isalnum():
            return 'Alphanumeric'
        else:
            return 'Binary'
    
    def _calculate_compression_ratio(self, data: str) -> float:
        """حساب نسبة الضغط الممكنة"""
        import zlib
        compressed = zlib.compress(data.encode())
        ratio = len(compressed) / len(data)
        return round(ratio, 3)
    
    def _calculate_optimal_version(self, data: str) -> int:
        """حساب نسخة QR المثلى حسب حجم البيانات"""
        data_length = len(data)
        
        capacity_table = {
            1: 25, 2: 47, 3: 77, 4: 114, 5: 154,
            6: 195, 7: 224, 8: 279, 9: 335, 10: 395
        }
        
        for version, capacity in capacity_table.items():
            if data_length <= capacity:
                return version
        
        return 10  # أعلى نسخة
    
    def _recommend_error_level(self, data: str) -> str:
        """اقتراح مستوى تصحيح الأخطاء المناسب"""
        data_length = len(data)
        
        if data_length < 50:
            return 'H'  # 30% - بيانات قصيرة تحتاج حماية قصوى
        elif data_length < 150:
            return 'Q'  # 25% - متوازن
        elif data_length < 300:
            return 'M'  # 15% - بيانات متوسطة
        else:
            return 'L'  # 7% - بيانات طويلة تحتاج مساحة
    
    def _estimate_module_count(self, data: str) -> int:
        """تقدير عدد المربعات (modules) في QR"""
        version = self._calculate_optimal_version(data)
        size = 21 + (version - 1) * 4
        return size * size
    
    def generate_engineered_qr(
        self,
        data: str,
        filename: str = 'engineered_qr.svg',
        auto_optimize: bool = True
    ) -> Tuple[str, Dict]:
        """
        إنشاء QR code بتحسينات هندسية
        
        Args:
            data: البيانات المراد تشفيرها
            filename: اسم الملف
            auto_optimize: تحسين تلقائي للإعدادات
        
        Returns:
            tuple: (اسم الملف، معلومات التحليل)
        """
        analysis = self.analyze_data(data)
        
        if auto_optimize:
            error_levels = {
                'L': qrcode.constants.ERROR_CORRECT_L,
                'M': qrcode.constants.ERROR_CORRECT_M,
                'Q': qrcode.constants.ERROR_CORRECT_Q,
                'H': qrcode.constants.ERROR_CORRECT_H,
            }
            error_correction = error_levels[analysis['recommended_error_correction']]
        else:
            error_correction = qrcode.constants.ERROR_CORRECT_H
        
        qr = qrcode.QRCode(
            version=analysis['recommended_version'],
            error_correction=error_correction,
            box_size=15,
            border=4,
        )
        
        enhanced_data = self._add_checksum(data)
        qr.add_data(enhanced_data)
        qr.make(fit=True)
        
        img = qr.make_image(
            image_factory=SvgFillImage,
            fill_color='#000000',
            back_color='#FFFFFF'
        )
        
        img.save(filename)
        
        self.quality_metrics = self._calculate_quality_metrics(qr, analysis)
        
        return filename, {
            'analysis': analysis,
            'quality': self.quality_metrics,
            'file': filename
        }
    
    def _add_checksum(self, data: str) -> str:
        """إضافة checksum للتحقق من سلامة البيانات"""
        checksum = hashlib.md5(data.encode()).hexdigest()[:8]
        return f"{data}|CRC:{checksum}"
    
    def _calculate_quality_metrics(self, qr, analysis: Dict) -> Dict:
        """حساب مقاييس جودة QR code"""
        metrics = {
            'data_density': round(analysis['data_length'] / analysis['estimated_modules'], 4),
            'error_correction_level': analysis['recommended_error_correction'],
            'version': analysis['recommended_version'],
            'total_modules': analysis['estimated_modules'],
            'reliability_score': self._calculate_reliability_score(analysis),
            'scan_difficulty': self._estimate_scan_difficulty(analysis)
        }
        return metrics
    
    def _calculate_reliability_score(self, analysis: Dict) -> float:
        """حساب معدل الموثوقية (0-100)"""
        error_level_scores = {'L': 60, 'M': 75, 'Q': 85, 'H': 95}
        error_score = error_level_scores[analysis['recommended_error_correction']]
        
        density_score = 100 - (analysis['data_length'] / 10)
        density_score = max(50, min(100, density_score))
        
        reliability = (error_score * 0.6 + density_score * 0.4)
        return round(reliability, 2)
    
    def _estimate_scan_difficulty(self, analysis: Dict) -> str:
        """تقدير صعوبة المسح"""
        if analysis['estimated_modules'] < 500:
            return 'سهل جداً'
        elif analysis['estimated_modules'] < 1500:
            return 'سهل'
        elif analysis['estimated_modules'] < 3000:
            return 'متوسط'
        else:
            return 'صعب'
    
    def generate_multi_level_qr(self, data: str) -> Dict[str, str]:
        """
        إنشاء QR codes بمستويات تصحيح مختلفة للمقارنة
        """
        results = {}
        
        for level, name in [('L', 'low'), ('M', 'medium'), ('Q', 'quartile'), ('H', 'high')]:
            qr = qrcode.QRCode(
                version=1,
                error_correction=getattr(qrcode.constants, f'ERROR_CORRECT_{level}'),
                box_size=15,
                border=4,
            )
            qr.add_data(data)
            qr.make(fit=True)
            
            filename = f'qr_{name}_correction.svg'
            img = qr.make_image(
                image_factory=SvgFillImage,
                fill_color='#000000',
                back_color='#FFFFFF'
            )
            img.save(filename)
            results[name] = filename
        
        return results


if __name__ == '__main__':
    generator = EngineeringQRGenerator()
    
    data = "https://t.me/QP4RM - MERO Developer"
    filename, info = generator.generate_engineered_qr(data, 'mero_engineered_qr.svg')
    
    print(f"✅ تم إنشاء QR هندسي: {filename}")
    print(f"📊 التحليل: {json.dumps(info['analysis'], indent=2, ensure_ascii=False)}")
    print(f"📈 الجودة: {json.dumps(info['quality'], indent=2, ensure_ascii=False)}")
