import base64

class DataDecoder:
    def decode(self, data):
        return base64.b64decode(data)
