<![CDATA["""
Thought Collision Engine — WebSocket Events Route
"""
from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from loguru import logger
import json
import asyncio
from core.events import event_bus

router = APIRouter()

class ConnectionManager:
    def __init__(self):
        self.active_connections: list[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)

    def disconnect(self, websocket: WebSocket):
        if websocket in self.active_connections:
            self.active_connections.remove(websocket)

    async def broadcast(self, message: str):
        for connection in self.active_connections:
            try:
                await connection.send_text(message)
            except Exception as e:
                logger.error(f"WebSocket broadcast error: {e}")
                self.disconnect(connection)

manager = ConnectionManager()

# Background task to listen to EventBus and forward to WebSockets
async def event_to_ws_forwarder(topic: str, payload: dict):
    if manager.active_connections:
        message = json.dumps({"topic": topic, "payload": payload})
        await manager.broadcast(message)

# Subscribe to all ingestion events
event_bus.subscribe("ingestion.*", event_to_ws_forwarder)

@router.websocket("/ws/events")
async def websocket_endpoint(websocket: WebSocket):
    await manager.connect(websocket)
    try:
        while True:
            # Keep connection open, client might send heartbeats
            data = await websocket.receive_text()
            if data == "ping":
                await websocket.send_text("pong")
    except WebSocketDisconnect:
        manager.disconnect(websocket)
]]>
