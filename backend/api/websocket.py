from fastapi import WebSocket
from typing import List
import asyncio


class ConnectionManager:
    def __init__(self):
        self.active_connections: List[WebSocket] = []
        self._lock = asyncio.Lock()

    async def connect(self, websocket: WebSocket):
        """
        Accept and register a WebSocket connection.
        """
        await websocket.accept()

        async with self._lock:
            self.active_connections.append(websocket)

        print(f"[WS] Connected. Total clients: {len(self.active_connections)}")

    async def disconnect(self, websocket: WebSocket):
        """
        Safely remove a WebSocket connection.
        """
        async with self._lock:
            if websocket in self.active_connections:
                self.active_connections.remove(websocket)

        print(f"[WS] Disconnected. Remaining: {len(self.active_connections)}")

    async def send_personal_message(self, websocket: WebSocket, message: dict):
        """
        Send message to a single client.
        """
        try:
            await websocket.send_json(message)
        except Exception:
            await self.disconnect(websocket)

    async def broadcast(self, message: dict):
        """
        Broadcast message to all clients safely.
        Removes dead connections automatically.
        """
        async with self._lock:
            connections = self.active_connections.copy()

        for connection in connections:
            try:
                await connection.send_json(message)
            except Exception:
                await self.disconnect(connection)


# Global manager
manager = ConnectionManager()