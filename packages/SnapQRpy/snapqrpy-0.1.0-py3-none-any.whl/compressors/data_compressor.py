import zlib

class DataCompressor:
    def compress(self, data):
        return zlib.compress(data)
