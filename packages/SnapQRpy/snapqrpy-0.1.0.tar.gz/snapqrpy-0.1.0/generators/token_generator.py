import secrets

class TokenGenerator:
    def generate(self, length=32):
        return secrets.token_urlsafe(length)
