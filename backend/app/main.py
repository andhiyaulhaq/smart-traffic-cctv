import asyncio
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from pydantic import BaseModel
from aiortc import RTCPeerConnection, RTCSessionDescription
from app.services.webrtc import HLSVideoStreamTrack
from app.config import settings
from app.database.connection import init_db
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

@app.on_event("shutdown")
async def on_shutdown():
    coros = [pc.close() for pc in pcs]
    await asyncio.gather(*coros)
    pcs.clear()

@app.get("/health")
async def health_check():
    return {"status": "ok", "message": "Backend is running!"}
