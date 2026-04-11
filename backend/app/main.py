import asyncio
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from pydantic import BaseModel
from typing import List
from aiortc import RTCPeerConnection, RTCSessionDescription
from app.services.webrtc import HLSVideoStreamTrack
from app.config import settings
from app.database.connection import init_db
from app.database.repository import get_total_counts, get_hourly_stats, get_recent_events
from app.models.schemas import LineConfig, StatsResponse, CountEvent
import json

app = FastAPI(title="Smart Traffic CCTV API")

# WebSocket Connection Manager
class ConnectionManager:
    def __init__(self):
        self.active_connections: list[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)

    def disconnect(self, websocket: WebSocket):
        if websocket in self.active_connections:
            self.active_connections.remove(websocket)

    async def broadcast(self, message: dict):
        for connection in self.active_connections:
            try:
                await connection.send_text(json.dumps(message))
            except Exception:
                # Connection might be closed
                continue

manager = ConnectionManager()

# Global broadcast function for use in services
async def broadcast_count_update(data: dict):
    await manager.broadcast(data)

# Global Line Configuration (In-memory for simplicity in Phase 7)
# Initialized with default horizontal line in the middle
current_line_config = {
    "x1": 0.0,
    "y1": 0.5,
    "x2": 1.0,
    "y2": 0.5
}

def get_line_config():
    return [
        current_line_config["x1"],
        current_line_config["y1"],
        current_line_config["x2"],
        current_line_config["y2"]
    ]

# Schema for WebRTC Offer
class Offer(BaseModel):
    sdp: str
    type: str

# Store peer connections
pcs = set()

@app.on_event("startup")
async def startup_event():
    await init_db()

@app.post("/offer")
async def offer(offer_data: Offer):
    offer = RTCSessionDescription(sdp=offer_data.sdp, type=offer_data.type)
    pc = RTCPeerConnection()
    pcs.add(pc)

    @pc.on("connectionstatechange")
    async def on_connectionstatechange():
        if pc.connectionState == "failed" or pc.connectionState == "closed":
            pcs.discard(pc)

    # Use the HLS stream track
    pc.addTrack(HLSVideoStreamTrack(stream_url=settings.HLS_STREAM_URL))

    await pc.setRemoteDescription(offer)
    answer = await pc.createAnswer()
    await pc.setLocalDescription(answer)

    return {"sdp": pc.localDescription.sdp, "type": pc.localDescription.type}

@app.websocket("/ws/counts")
async def websocket_endpoint(websocket: WebSocket):
    await manager.connect(websocket)
    try:
        while True:
            # Keep connection alive
            await websocket.receive_text()
    except WebSocketDisconnect:
        manager.disconnect(websocket)

@app.get("/line", response_model=LineConfig)
async def get_line():
    return current_line_config

@app.post("/line")
async def update_line(config: LineConfig):
    global current_line_config
    current_line_config = config.model_dump()
    return {"status": "success", "config": current_line_config}

@app.get("/stats/today", response_model=StatsResponse)
async def get_today_stats():
    counts = await get_total_counts()
    hourly = await get_hourly_stats()
    return {
        "enter": counts["enter"],
        "exit": counts["exit"],
        "hourly_counts": hourly
    }

@app.get("/events", response_model=List[CountEvent])
async def get_events(limit: int = 50):
    return await get_recent_events(limit)

@app.on_event("shutdown")
async def on_shutdown():
    coros = [pc.close() for pc in pcs]
    await asyncio.gather(*coros)
    pcs.clear()

@app.get("/health")
async def health_check():
    return {"status": "ok", "message": "Backend is running!"}
