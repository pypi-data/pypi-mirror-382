import platform

class MacOSPlatform:
    def __init__(self):
        self.version = platform.mac_ver()[0]
