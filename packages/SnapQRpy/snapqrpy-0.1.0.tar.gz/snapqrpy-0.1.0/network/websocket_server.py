import asyncio
import websockets
from typing import Set, Dict
from snapqrpy.utils.logger import Logger

class WebSocketServer:
    def __init__(self, host: str = "0.0.0.0", port: int = 8000):
        self.host = host
        self.port = port
        self.logger = Logger("WebSocketServer")
        self.clients: Set = set()
        self.server = None
        
    async def handle_client(self, websocket, path):
        self.clients.add(websocket)
        self.logger.info(f"Client connected: {websocket.remote_address}")
        
        try:
            async for message in websocket:
                await self.broadcast(message, exclude=websocket)
        finally:
            self.clients.remove(websocket)
            self.logger.info(f"Client disconnected: {websocket.remote_address}")
    
    async def broadcast(self, message: str, exclude=None):
        for client in self.clients:
            if client != exclude:
                await client.send(message)
    
    async def start(self):
        self.server = await websockets.serve(self.handle_client, self.host, self.port)
        self.logger.info(f"WebSocket server started on {self.host}:{self.port}")
    
    async def stop(self):
        if self.server:
            self.server.close()
            await self.server.wait_closed()
            self.logger.info("WebSocket server stopped")
