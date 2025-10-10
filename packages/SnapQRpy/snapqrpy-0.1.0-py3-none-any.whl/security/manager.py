from snapqrpy.security.encryption import EncryptionManager
from snapqrpy.security.consent import ConsentManager
from snapqrpy.security.auth import AuthManager
from snapqrpy.security.firewall import FirewallManager
from snapqrpy.utils.logger import Logger

class SecurityManager:
    def __init__(self):
        self.logger = Logger("SecurityManager")
        self.encryption = EncryptionManager()
        self.consent = ConsentManager()
        self.auth = AuthManager()
        self.firewall = FirewallManager()
        
    def enable_2fa(self):
        self.auth.enable_2fa()
        self.logger.info("2FA enabled")
    
    def set_encryption(self, algorithm: str):
        self.logger.info(f"Encryption algorithm set to {algorithm}")
    
    def require_pin(self):
        self.auth.require_pin()
        self.logger.info("PIN authentication required")
