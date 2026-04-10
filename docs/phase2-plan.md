# Phase 2: Replace Synthetic Frames with Real Video - Technical Implementation Plan

## Objective
The goal is to replace the dummy, synthetic video stream with an actual local video file (`.mp4`) stream passed via WebRTC. This step introduces OpenCV to our backend for video reading, building the exact `cv2.VideoCapture` pipeline that will be used for live HLS streams in the next phase.

## 1. Backend – Add Dependencies

1. **Install OpenCV:**
   We need OpenCV to read video files (and eventually network streams). We can use the headless version since we do not need GUI features on the backend.
   Navigate to the `backend/` directory and run:
   ```bash
   cd backend
   uv add opencv-python-headless
   ```

2. **Add a Sample Video File:**
   Create a directory for sample data and add a short `.mp4` video.
   ```bash
   mkdir -p backend/data
   ```
   *(Download or copy a sample traffic `.mp4` video and save it as `backend/data/traffic.mp4`)*

## 2. Backend – OpenCV Video Reader Track (`app/services/webrtc.py`)

1. **Implement `FileVideoStreamTrack`:**
   Open `backend/app/services/webrtc.py` and replace or append the new class that reads frames sequentially using `cv2.VideoCapture`. Unlike static images or simple patterns, reading a file needs pacing, so we use `asyncio.sleep` to match the video's original framerate.

   ```python
   import asyncio
   import cv2
   import numpy as np
   import time
   from av import VideoFrame
   from aiortc import VideoStreamTrack

   class FileVideoStreamTrack(VideoStreamTrack):
       """
       Reads frames from a local video file using OpenCV and streams them via WebRTC.
       """
       def __init__(self, video_path: str):
           super().__init__()
           self.video_path = video_path
           self.cap = cv2.VideoCapture(video_path)
           
           if not self.cap.isOpened():
               print(f"Warning: Could not open video file: {video_path}")
           
           # Get video FPS to pace the stream
           self.fps = self.cap.get(cv2.CAP_PROP_FPS)
           if self.fps <= 0 or np.isnan(self.fps):
               self.fps = 30.0

           self._start_time = None

       async def recv(self):
           pts, time_base = await self.next_timestamp()

           # Read the next frame
           ret, frame = self.cap.read()
           
           if not ret:
               # If the video ends, loop it from the beginning
               self.cap.set(cv2.CAP_PROP_POS_FRAMES, 0)
               ret, frame = self.cap.read()
               if not ret:
                   # If it still fails, return a black frame 
                   frame = np.zeros((480, 640, 3), dtype=np.uint8)

           # Convert to av.VideoFrame format
           # OpenCV reads in BGR, which is matched by format="bgr24"
           video_frame = VideoFrame.from_ndarray(frame, format="bgr24")
           video_frame.pts = pts
           video_frame.time_base = time_base

           # Pace the frames to roughly match the desired FPS
           await asyncio.sleep(1.0 / self.fps)

           return video_frame

       def stop(self):
           """Ensure we release the cv2 VideoCapture when the track stops."""
           super().stop()
           if self.cap:
               self.cap.release()
   ```

## 3. Backend – Update WebRTC Endpoint (`app/main.py`)

1. **Modify `/offer` endpoint:**
   Update `backend/app/main.py` to use `FileVideoStreamTrack` instead of `SyntheticVideoTrack`.

   ```python
   # Import the new track
   from app.services.webrtc import FileVideoStreamTrack

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

       # Provide the path to the sample video
       video_path = "data/traffic.mp4"
       pc.addTrack(FileVideoStreamTrack(video_path=video_path))

       await pc.setRemoteDescription(offer)
       answer = await pc.createAnswer()
       await pc.setLocalDescription(answer)

       return {"sdp": pc.localDescription.sdp, "type": pc.localDescription.type}
   ```

## 4. Frontend – Verification

**No major code changes are needed on the frontend for Phase 2.** The frontend's `useWebRTC` hook and `VideoPlayer` component are already capable of rendering whatever video stream the backend sends.

1. **Verify Functionality:**
   - Place a `traffic.mp4` inside the `backend/data/` folder.
   - Restart the FastAPI backend (`uv run uvicorn app.main:app --reload --port 8000`).
   - Run the Next.js frontend (`pnpm dev --port 3000`).
   - Navigate to `http://localhost:3000`. You should now see the `traffic.mp4` playing on a continuous loop inside the player component instead of the shifting color box.

## 5. Execution Steps Checklist
- [ ] Run `uv add opencv-python-headless` in `backend/`.
- [ ] Create `backend/data/` directory and add `traffic.mp4`.
- [ ] Create/Update `FileVideoStreamTrack` in `backend/app/services/webrtc.py`.
- [ ] Update `/offer` endpoint in `backend/app/main.py` to use the new track.
- [ ] Test the full stack locally and confirm the video loops smoothly on the frontend dashboard.
