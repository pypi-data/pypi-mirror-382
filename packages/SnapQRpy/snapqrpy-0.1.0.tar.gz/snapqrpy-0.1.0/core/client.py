import asyncio
from typing import Optional, Dict, Any, Callable
from snapqrpy.qr.scanner import QRScanner
from snapqrpy.network.websocket_client import WebSocketClient
from snapqrpy.security.encryption import EncryptionManager
from snapqrpy.stream.display import StreamDisplay
from snapqrpy.utils.logger import Logger
from snapqrpy.device.controller import DeviceController

class SnapQRClient:
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        self.config = config or {}
        self.logger = Logger("SnapQRClient")
        self.qr_scanner = QRScanner()
        self.encryption = EncryptionManager()
        self.display = StreamDisplay()
        self.controller = DeviceController()
        self.ws_client = None
        self.connection_url = None
        self.session_id = None
        self.connected = False
        
    def scan_qr(self, camera_index: int = 0) -> str:
        self.logger.info("Scanning QR code...")
        url = self.qr_scanner.scan(camera_index)
        self.connection_url = url
        return url
    
    def parse_qr_url(self, url: str) -> Dict[str, str]:
        parts = url.replace("snapqr://", "").split("?")
        host_port = parts[0].split(":")
        params = dict(p.split("=") for p in parts[1].split("&")) if len(parts) > 1 else {}
        return {
            "host": host_port[0],
            "port": int(host_port[1]) if len(host_port) > 1 else 8000,
            "token": params.get("token", "")
        }
    
    async def connect_async(self, url: Optional[str] = None):
        if url:
            self.connection_url = url
        
        if not self.connection_url:
            raise ValueError("No connection URL available")
        
        conn_info = self.parse_qr_url(self.connection_url)
        self.ws_client = WebSocketClient(conn_info["host"], conn_info["port"])
        await self.ws_client.connect(conn_info["token"])
        self.connected = True
        self.logger.info(f"Connected to {conn_info['host']}:{conn_info['port']}")
    
    def connect(self, url: Optional[str] = None):
        asyncio.run(self.connect_async(url))
    
    def request_permission(self) -> bool:
        if not self.connected:
            raise RuntimeError("Not connected to server")
        return self.ws_client.request_screen_share()
    
    async def start_screen_share(self):
        if not self.connected:
            raise RuntimeError("Not connected to server")
        await self.display.start()
    
    async def disconnect(self):
        self.connected = False
        if self.ws_client:
            await self.ws_client.disconnect()
        self.logger.info("Disconnected from server")
