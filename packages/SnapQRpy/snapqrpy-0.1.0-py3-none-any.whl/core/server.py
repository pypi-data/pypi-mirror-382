import asyncio
import socket
import json
from typing import Optional, Dict, Any
from snapqrpy.qr.generator import QRGenerator
from snapqrpy.network.websocket_server import WebSocketServer
from snapqrpy.security.encryption import EncryptionManager
from snapqrpy.security.consent import ConsentManager
from snapqrpy.stream.capture import ScreenCapture
from snapqrpy.utils.logger import Logger

class SnapQRServer:
    def __init__(self, port: int = 8000, host: str = "0.0.0.0", config: Optional[Dict[str, Any]] = None):
        self.port = port
        self.host = host
        self.config = config or {}
        self.logger = Logger("SnapQRServer")
        self.qr_generator = QRGenerator()
        self.encryption = EncryptionManager()
        self.consent_manager = ConsentManager()
        self.screen_capture = ScreenCapture()
        self.ws_server = None
        self.sessions = {}
        self.running = False
        
    def generate_qr(self, data: Optional[str] = None) -> Any:
        if not data:
            data = self._generate_connection_url()
        return self.qr_generator.generate(data)
    
    def _generate_connection_url(self) -> str:
        hostname = socket.gethostname()
        ip = socket.gethostbyname(hostname)
        token = self.encryption.generate_token()
        return f"snapqr://{ip}:{self.port}?token={token}"
    
    async def start_async(self):
        self.running = True
        self.ws_server = WebSocketServer(self.host, self.port)
        await self.ws_server.start()
        self.logger.info(f"Server started on {self.host}:{self.port}")
        
    def start(self):
        asyncio.run(self.start_async())
    
    async def stop(self):
        self.running = False
        if self.ws_server:
            await self.ws_server.stop()
        self.logger.info("Server stopped")
    
    def accept_connection(self, session_id: str) -> bool:
        return self.consent_manager.grant_permission(session_id)
    
    def reject_connection(self, session_id: str) -> bool:
        return self.consent_manager.deny_permission(session_id)
