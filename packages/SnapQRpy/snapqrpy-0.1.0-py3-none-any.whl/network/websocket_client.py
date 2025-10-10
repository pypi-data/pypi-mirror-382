import asyncio
import websockets
from typing import Optional, Callable
from snapqrpy.utils.logger import Logger

class WebSocketClient:
    def __init__(self, host: str, port: int):
        self.host = host
        self.port = port
        self.logger = Logger("WebSocketClient")
        self.websocket = None
        self.connected = False
        
    async def connect(self, token: str):
        uri = f"ws://{self.host}:{self.port}?token={token}"
        self.websocket = await websockets.connect(uri)
        self.connected = True
        self.logger.info(f"Connected to {uri}")
    
    async def send(self, message: str):
        if self.websocket and self.connected:
            await self.websocket.send(message)
    
    async def receive(self) -> str:
        if self.websocket and self.connected:
            return await self.websocket.recv()
        return ""
    
    def request_screen_share(self) -> bool:
        self.logger.info("Requesting screen share permission")
        return True
    
    async def disconnect(self):
        if self.websocket:
            await self.websocket.close()
            self.connected = False
            self.logger.info("Disconnected from server")
