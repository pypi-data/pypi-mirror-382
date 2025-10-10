import pyotp
import hashlib
from typing import Optional, Dict
from snapqrpy.utils.logger import Logger

class AuthManager:
    def __init__(self):
        self.logger = Logger("AuthManager")
        self.totp_secrets: Dict[str, str] = {}
        self.pin_hashes: Dict[str, str] = {}
        self.two_factor_enabled = False
        self.pin_required = False
        
    def enable_2fa(self):
        self.two_factor_enabled = True
        
    def disable_2fa(self):
        self.two_factor_enabled = False
        
    def generate_totp_secret(self, user_id: str) -> str:
        secret = pyotp.random_base32()
        self.totp_secrets[user_id] = secret
        return secret
    
    def verify_totp(self, user_id: str, code: str) -> bool:
        if user_id not in self.totp_secrets:
            return False
        totp = pyotp.TOTP(self.totp_secrets[user_id])
        return totp.verify(code)
    
    def require_pin(self):
        self.pin_required = True
        
    def set_pin(self, user_id: str, pin: str):
        pin_hash = hashlib.sha256(pin.encode()).hexdigest()
        self.pin_hashes[user_id] = pin_hash
        
    def verify_pin(self, user_id: str, pin: str) -> bool:
        if user_id not in self.pin_hashes:
            return False
        pin_hash = hashlib.sha256(pin.encode()).hexdigest()
        return self.pin_hashes[user_id] == pin_hash
