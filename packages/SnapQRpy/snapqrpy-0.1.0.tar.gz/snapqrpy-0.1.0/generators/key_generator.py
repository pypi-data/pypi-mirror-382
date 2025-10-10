import secrets

class KeyGenerator:
    def generate(self):
        return secrets.token_hex(32)
