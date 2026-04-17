"""
Foundry AI — WebSocket Connection Manager
Manages WebSocket connections per project for real-time updates.
"""

from fastapi import WebSocket
from typing import Dict, List
from datetime import datetime
import json
import structlog

logger = structlog.get_logger()


class ConnectionManager:
    """Manages active WebSocket connections grouped by project_id."""

    def __init__(self):
        self.active_connections: Dict[str, List[WebSocket]] = {}

    async def connect(self, websocket: WebSocket, project_id: str):
        """Accept and register a WebSocket connection."""
        await websocket.accept()
        if project_id not in self.active_connections:
            self.active_connections[project_id] = []
        self.active_connections[project_id].append(websocket)

    def disconnect(self, websocket: WebSocket, project_id: str):
        """Remove a WebSocket connection."""
        if project_id in self.active_connections:
            self.active_connections[project_id].remove(websocket)
            if not self.active_connections[project_id]:
                del self.active_connections[project_id]

    async def send_event(self, project_id: str, event: str, data: dict = None):
        """Broadcast an event to all connections watching a project."""
        if project_id not in self.active_connections:
            return

        message = json.dumps({
            "event": event,
            "project_id": project_id,
            "data": data or {},
            "timestamp": datetime.utcnow().isoformat(),
        })

        disconnected = []
        for connection in self.active_connections[project_id]:
            try:
                await connection.send_text(message)
            except Exception:
                disconnected.append(connection)

        # Clean up disconnected clients
        for conn in disconnected:
            self.disconnect(conn, project_id)

    async def send_log(self, project_id: str, source: str, message: str, level: str = "info"):
        """Send a log entry event."""
        await self.send_event(project_id, "log", {
            "source": source,
            "level": level,
            "message": message,
        })


# Singleton instance
manager = ConnectionManager()
