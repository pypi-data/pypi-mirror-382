from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2
from cryptography.hazmat.primitives.asymmetric import rsa, padding
from Crypto.Cipher import AES, ChaCha20_Poly1305
from Crypto.Random import get_random_bytes
import base64
import secrets
from typing import Tuple, Optional
from snapqrpy.utils.logger import Logger

class EncryptionManager:
    def __init__(self):
        self.logger = Logger("EncryptionManager")
        self.fernet_key = Fernet.generate_key()
        self.fernet = Fernet(self.fernet_key)
        self.rsa_private_key = None
        self.rsa_public_key = None
        
    def generate_token(self, length: int = 32) -> str:
        return secrets.token_urlsafe(length)
    
    def generate_rsa_keys(self, key_size: int = 4096) -> Tuple[bytes, bytes]:
        private_key = rsa.generate_private_key(public_exponent=65537, key_size=key_size)
        self.rsa_private_key = private_key
        self.rsa_public_key = private_key.public_key()
        self.logger.info(f"Generated RSA-{key_size} key pair")
        return (private_key, private_key.public_key())
    
    def encrypt_fernet(self, data: bytes) -> bytes:
        return self.fernet.encrypt(data)
    
    def decrypt_fernet(self, encrypted_data: bytes) -> bytes:
        return self.fernet.decrypt(encrypted_data)
    
    def encrypt_aes_gcm(self, data: bytes, key: Optional[bytes] = None) -> Tuple[bytes, bytes, bytes]:
        if not key:
            key = get_random_bytes(32)
        cipher = AES.new(key, AES.MODE_GCM)
        ciphertext, tag = cipher.encrypt_and_digest(data)
        return (ciphertext, cipher.nonce, tag)
    
    def decrypt_aes_gcm(self, ciphertext: bytes, key: bytes, nonce: bytes, tag: bytes) -> bytes:
        cipher = AES.new(key, AES.MODE_GCM, nonce=nonce)
        return cipher.decrypt_and_verify(ciphertext, tag)
    
    def encrypt_chacha20(self, data: bytes) -> Tuple[bytes, bytes, bytes]:
        key = get_random_bytes(32)
        cipher = ChaCha20_Poly1305.new(key=key)
        ciphertext, tag = cipher.encrypt_and_digest(data)
        return (ciphertext, cipher.nonce, tag)
    
    def hash_password(self, password: str, salt: Optional[bytes] = None) -> Tuple[bytes, bytes]:
        if not salt:
            salt = get_random_bytes(32)
        kdf = PBKDF2(
            algorithm=hashes.SHA256(),
            length=32,
            salt=salt,
            iterations=100000,
        )
        key = kdf.derive(password.encode())
        return (key, salt)
    
    def verify_password(self, password: str, key: bytes, salt: bytes) -> bool:
        kdf = PBKDF2(
            algorithm=hashes.SHA256(),
            length=32,
            salt=salt,
            iterations=100000,
        )
        try:
            kdf.verify(password.encode(), key)
            return True
        except:
            return False
