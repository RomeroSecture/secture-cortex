"""Meeting WebSocket connection manager — handles rooms, broadcasting, and role filtering."""

import uuid
from dataclasses import dataclass, field
from datetime import UTC, datetime

import structlog
from fastapi import WebSocket

from app.config import settings

logger = structlog.get_logger()

# Role → settings attribute name for confidence threshold
_ROLE_THRESHOLD_ATTRS: dict[str, str] = {
    "tech_lead": "confidence_tech_lead",
    "developer": "confidence_developer",
    "pm": "confidence_pm",
    "commercial": "confidence_commercial",
    "admin": "confidence_admin",
}


@dataclass
class RoleConnection:
    """A WebSocket connection with user role and confidence threshold."""

    ws: WebSocket
    user_role: str = "developer"
    confidence_threshold: float = field(default=0.5)

    @classmethod
    def create(cls, ws: WebSocket, role: str = "developer") -> "RoleConnection":
        """Create a connection with the threshold for the given role."""
        attr = _ROLE_THRESHOLD_ATTRS.get(role, "confidence_admin")
        threshold = getattr(settings, attr, 0.5)
        return cls(ws=ws, user_role=role, confidence_threshold=threshold)


class MeetingManager:
    """Manages WebSocket connections grouped by meeting ID (rooms)."""

    def __init__(self) -> None:
        self.active_connections: dict[uuid.UUID, list[RoleConnection]] = {}

    async def connect(
        self,
        meeting_id: uuid.UUID,
        websocket: WebSocket,
        role: str = "developer",
    ) -> None:
        """Accept and register a WebSocket connection to a meeting room."""
        await websocket.accept()
        conn = RoleConnection.create(websocket, role)
        if meeting_id not in self.active_connections:
            self.active_connections[meeting_id] = []
        self.active_connections[meeting_id].append(conn)
        logger.info(
            "ws_connected",
            meeting_id=str(meeting_id),
            role=role,
        )

    def disconnect(
        self,
        meeting_id: uuid.UUID,
        websocket: WebSocket,
    ) -> None:
        """Remove a WebSocket from a meeting room."""
        if meeting_id in self.active_connections:
            self.active_connections[meeting_id] = [
                c for c in self.active_connections[meeting_id]
                if c.ws != websocket
            ]
            if not self.active_connections[meeting_id]:
                del self.active_connections[meeting_id]
        logger.info("ws_disconnected", meeting_id=str(meeting_id))

    async def broadcast(
        self,
        meeting_id: uuid.UUID,
        message: dict,
    ) -> None:
        """Send a JSON message to all connections in a meeting room."""
        message["timestamp"] = datetime.now(UTC).isoformat()
        connections = self.active_connections.get(meeting_id, [])
        for conn in connections:
            try:
                await conn.ws.send_json(message)
            except Exception:
                logger.warning(
                    "ws_send_failed",
                    meeting_id=str(meeting_id),
                )

    async def broadcast_role_filtered(
        self,
        meeting_id: uuid.UUID,
        insight_msg: dict,
        target_roles: list[str],
        confidence: float,
    ) -> None:
        """Send insight only to users whose role matches target_roles
        and whose confidence threshold is met."""
        insight_msg["timestamp"] = datetime.now(UTC).isoformat()
        connections = self.active_connections.get(meeting_id, [])
        sent_count = 0
        for conn in connections:
            if conn.user_role not in target_roles:
                continue
            if confidence < conn.confidence_threshold:
                continue
            try:
                await conn.ws.send_json(insight_msg)
                sent_count += 1
            except Exception:
                logger.warning(
                    "ws_role_send_failed",
                    meeting_id=str(meeting_id),
                    role=conn.user_role,
                )
        if sent_count > 0:
            logger.debug(
                "role_filtered_broadcast",
                meeting_id=str(meeting_id),
                targets=target_roles,
                sent=sent_count,
            )

    def get_connection_count(self, meeting_id: uuid.UUID) -> int:
        """Get number of active connections for a meeting."""
        return len(self.active_connections.get(meeting_id, []))

    def get_connected_roles(self, meeting_id: uuid.UUID) -> list[str]:
        """Get unique roles of connected users for a meeting."""
        connections = self.active_connections.get(meeting_id, [])
        return list({c.user_role for c in connections})


# Singleton instance
meeting_manager = MeetingManager()
