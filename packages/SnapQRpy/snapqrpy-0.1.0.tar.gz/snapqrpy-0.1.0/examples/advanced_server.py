from snapqrpy import SnapQRServer
from snapqrpy.config import ConfigManager

config = ConfigManager()
server = SnapQRServer(config=config.load_yaml("config.yaml"))
server.start()
