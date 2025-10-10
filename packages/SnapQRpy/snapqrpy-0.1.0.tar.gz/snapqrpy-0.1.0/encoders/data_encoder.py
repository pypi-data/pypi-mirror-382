import base64

class DataEncoder:
    def encode(self, data):
        return base64.b64encode(data)
