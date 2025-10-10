import uuid

class IDGenerator:
    def generate(self):
        return str(uuid.uuid4())
