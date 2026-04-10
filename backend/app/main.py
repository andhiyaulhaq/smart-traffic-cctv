import asyncio
from fastapi import FastAPI
from pydantic import BaseModel
from aiortc import RTCPeerConnection, RTCSessionDescription
from app.services.webrtc import SyntheticVideoTrack, FileVideoStreamTrack

app = FastAPI(title="Smart Traffic CCTV API")

# Schema for WebRTC Offer
class Offer(BaseModel):
    sdp: str
    type: str

# Store peer connections to manage their lifecycle
pcs = set()

@app.post("/offer")
async def offer(offer_data: Offer):
    offer = RTCSessionDescription(sdp=offer_data.sdp, type=offer_data.type)
    pc = RTCPeerConnection()
    pcs.add(pc)

    @pc.on("connectionstatechange")
    async def on_connectionstatechange():
        print(f"Connection state is {pc.connectionState}")
        if pc.connectionState == "failed" or pc.connectionState == "closed":
            pcs.discard(pc)

    # Use the real video track instead of the synthetic one
    pc.addTrack(FileVideoStreamTrack(video_path="data/traffic.mp4"))

    await pc.setRemoteDescription(offer)
    answer = await pc.createAnswer()
    await pc.setLocalDescription(answer)

    return {"sdp": pc.localDescription.sdp, "type": pc.localDescription.type}

@app.on_event("shutdown")
async def on_shutdown():
    coros = [pc.close() for pc in pcs]
    await asyncio.gather(*coros)
    pcs.clear()

@app.get("/health")
async def health_check():
    return {"status": "ok", "message": "Backend is running!"}
