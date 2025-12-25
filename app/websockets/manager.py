from fastapi import WebSocket, WebSocketDisconnect
from typing import Dict, List, Set
import json
import asyncio
from collections import defaultdict
import threading


class ConnectionManager:
    """Manages WebSocket connections for real-time updates."""
    
    def __init__(self):
        # Map user_id -> Set of WebSocket connections
        self.active_connections: Dict[int, Set[WebSocket]] = defaultdict(set)
        # Map WebSocket -> user_id for quick lookup
        self.connection_users: Dict[WebSocket, int] = {}
        # Lock for thread-safe operations (using threading.Lock for cross-thread safety)
        self._lock = threading.Lock()
    
    async def connect(self, websocket: WebSocket, user_id: int):
        """Connect a WebSocket for a user."""
        with self._lock:
            self.active_connections[user_id].add(websocket)
            self.connection_users[websocket] = user_id
    
    async def disconnect(self, websocket: WebSocket):
        """Disconnect a WebSocket."""
        with self._lock:
            user_id = self.connection_users.pop(websocket, None)
            if user_id and websocket in self.active_connections[user_id]:
                self.active_connections[user_id].discard(websocket)
                # Clean up empty sets
                if not self.active_connections[user_id]:
                    del self.active_connections[user_id]
    
    async def send_personal_message(self, message: dict, user_id: int):
        """Send a message to all connections of a specific user."""
        if user_id not in self.active_connections:
            return
        
        # Create a copy of the set to avoid modification during iteration
        connections = list(self.active_connections[user_id])
        
        disconnected = []
        for connection in connections:
            try:
                await connection.send_json(message)
            except Exception as e:
                # Connection is dead, mark for removal
                disconnected.append(connection)
        
        # Remove disconnected connections
        with self._lock:
            for conn in disconnected:
                if conn in self.connection_users:
                    user_id = self.connection_users.pop(conn, None)
                    if user_id and conn in self.active_connections[user_id]:
                        self.active_connections[user_id].discard(conn)
                        if not self.active_connections[user_id]:
                            del self.active_connections[user_id]
    
    async def send_to_multiple_users(self, message: dict, user_ids: List[int]):
        """Send a message to multiple users."""
        for user_id in user_ids:
            await self.send_personal_message(message, user_id)
    
    async def broadcast(self, message: dict):
        """Broadcast a message to all connected users."""
        all_user_ids = list(self.active_connections.keys())
        await self.send_to_multiple_users(message, all_user_ids)
    
    def get_connected_users(self) -> List[int]:
        """Get list of currently connected user IDs."""
        return list(self.active_connections.keys())


# Global connection manager instance
manager = ConnectionManager()

