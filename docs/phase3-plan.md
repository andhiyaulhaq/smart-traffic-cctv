# Phase 3: HLS Live Stream Ingestion - Technical Implementation Plan

## Objective
The goal is to replace the local static video file with a live network HLS (`.m3u8`) stream. This involves updating our OpenCV implementation to connect to a remote stream, adding robustness like automatic reconnection if the stream drops, and introducing configuration for the stream URL.

## 1. Backend – Configuration Setup (`app/config.py`)

1. **Install Pydantic Settings:**
   Add `pydantic-settings` to manage environment variables efficiently.
   ```bash
   cd backend
   uv add pydantic-settings
   ```

2. **Add Settings Management:**
   Create `backend/app/config.py` to handle the HLS stream URL configuration.
   ```python
   from pydantic_settings import BaseSettings

   class Settings(BaseSettings):
       # Fallback public stream if not provided
       hls_stream_url: str = "http://devimages.apple.com.edgekey.net/streaming/examples/bipbop_4x3/bipbop_4x3_variant.m3u8"

       class Config:
           env_file = ".env"

   settings = Settings()
   ```

3. **Update `.env` file:**
   Create or update `backend/.env` to include your target HLS stream URL.
   ```env
   HLS_STREAM_URL=http://devimages.apple.com.edgekey.net/streaming/examples/bipbop_4x3/bipbop_4x3_variant.m3u8
   ```

## 2. Backend – HLS Video Track Service (`app/services/webrtc.py`)

To handle the network stream, we will create a dedicated `HLSVideoStreamTrack`. This track needs to correctly handle network fluctuations and connection drops, which are very common when streaming over HLS via OpenCV.

1. **Implement `HLSVideoStreamTrack`:**
   Add this class in `backend/app/services/webrtc.py`. It includes retry logic to continuously attempt reconnection if reading the stream fails.

   ```python
   import asyncio
   import cv2
   import numpy as np
   from av import VideoFrame
   from aiortc import VideoStreamTrack

   class HLSVideoStreamTrack(VideoStreamTrack):
       """
       Reads frames from an HLS stream using OpenCV and streams them via WebRTC.
       Includes basic retry logic if the stream drops.
       """
       def __init__(self, stream_url: str):
           super().__init__()
           self.stream_url = stream_url
           self.cap = None
           self.fps = 30.0  # Default fallback FPS
           self.connect()

       def connect(self):
           print(f"Connecting to HLS stream: {self.stream_url}")
           if self.cap:
               self.cap.release()
           
           # cv2.CAP_FFMPEG is explicitly passed to ensure proper network/HLS handling
           self.cap = cv2.VideoCapture(self.stream_url, cv2.CAP_FFMPEG)
           
           if not self.cap.isOpened():
               print("Warning: Could not open HLS stream")
           else:
               fps = self.cap.get(cv2.CAP_PROP_FPS)
               if fps > 0 and not np.isnan(fps):
                   self.fps = fps
               print(f"Stream connected successfully. Framerate: {self.fps} FPS")

       async def recv(self):
           pts, time_base = await self.next_timestamp()

           ret, frame = False, None
           if self.cap and self.cap.isOpened():
               ret, frame = self.cap.read()

           if not ret:
               # Connection dropped or stalled
               print("Stream read failed or stream ended. Reconnecting...")
               self.connect()
               
               # Return a placeholder frame with a "RECONNECTING..." message
               frame = np.zeros((480, 640, 3), dtype=np.uint8)
               cv2.putText(frame, "RECONNECTING...", (50, 240), 
                           cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)
               
               # Small delay to prevent spamming reconnection attempts instantly
               await asyncio.sleep(1.0)
           
           # Convert the numpy array frame to an av.VideoFrame
           video_frame = VideoFrame.from_ndarray(frame, format="bgr24")
           video_frame.pts = pts
           video_frame.time_base = time_base

           # Control the stream pace
           await asyncio.sleep(1.0 / self.fps)

           return video_frame

       def stop(self):
           """Ensure we release the cv2 VideoCapture when the track stops."""
           super().stop()
           if self.cap:
               self.cap.release()
   ```

## 3. Backend – Update WebRTC Endpoint (`app/main.py`)

Update the WebRTC `/offer` endpoint to use the new `HLSVideoStreamTrack`, driven by our Pydantic settings.

1. **Modify `/offer` endpoint (`app/main.py`):**
   ```python
   # Import the new track and config settings
   from app.services.webrtc import HLSVideoStreamTrack
   from app.config import settings

   # ... existing code ...

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

       # Instantiate the track using the URL from configuration
       pc.addTrack(HLSVideoStreamTrack(stream_url=settings.hls_stream_url))

       await pc.setRemoteDescription(offer)
       answer = await pc.createAnswer()
       await pc.setLocalDescription(answer)

       return {"sdp": pc.localDescription.sdp, "type": pc.localDescription.type}
   ```

## 4. Frontend – Verification

No backend-specific logic or UI changes are needed on the frontend in Phase 3. `VideoPlayer` dynamically plays whatever video stream the backend's `RTCPeerConnection` sends over.

1. **Verify Functionality:**
   - Start the backend: `uv run uvicorn app.main:app --reload --port 8000`.
   - Start the frontend: `pnpm dev --port 3000`.
   - Open your browser to `http://localhost:3000`.
   - The WebRTC player should display the live public HLS video stream rather than the static video file.
   - If the stream drops or network disconnects temporarily on the backend, the player should show the "RECONNECTING..." frame and then resume correctly once it restores.

## 5. Execution Steps Checklist

- [ ] Run `uv add pydantic-settings` inside `backend/`.
- [ ] Create `backend/app/config.py` to instantiate `Settings` model.
- [ ] Add the `HLS_STREAM_URL` environment variable to `backend/.env`.
- [ ] Create the `HLSVideoStreamTrack` class with OpenCV stream handling and reconnection logic in `backend/app/services/webrtc.py`.
- [ ] Update `/offer` in `backend/app/main.py` to add `HLSVideoStreamTrack` using the `settings.hls_stream_url`.
- [ ] Open the Next.js app on `localhost:3000` to verify a live network stream is loading and streaming seamlessly via WebRTC.
