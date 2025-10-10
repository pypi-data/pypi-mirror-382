import platform

class LinuxPlatform:
    def __init__(self):
        self.distro = platform.system()
