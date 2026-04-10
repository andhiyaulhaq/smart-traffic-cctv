# Phase 4: Vehicle Detection (YOLO) without Tracking - Technical Implementation Plan

## Objective
The goal is to integrate real-time object detection into our live stream. We will use the YOLOv8 model to identify vehicles (cars, trucks, buses, motorcycles) and draw bounding boxes around them before the frames are sent via WebRTC. This phase focuses on detection only, without persistent tracking or counting.

## 1. Backend – Install Dependencies

1. **Install Ultralytics:**
   Add the `ultralytics` package which provides the YOLOv8 implementation.
   ```bash
   cd backend
   uv add ultralytics
   ```

## 2. Backend – AI Service (`app/services/ai.py`)

Create a dedicated service to handle model loading and inference. This keeps the AI logic separate from the streaming logic.

1. **Implement `YOLOInference`:**
   Create `backend/app/services/ai.py`.

   ```python
   import cv2
   from ultralytics import YOLO
   import numpy as np

   class YOLOInference:
       def __init__(self, model_path: str = "yolov8n.pt"):
           # Load the model (it will be downloaded automatically on first run)
           self.model = YOLO(model_path)
           # Define vehicle class IDs for COCO dataset
           # 2: car, 3: motorcycle, 5: bus, 7: truck
           self.vehicle_classes = [2, 3, 5, 7]

       def detect(self, frame: np.ndarray) -> np.ndarray:
           """
           Runs detection on a frame and returns an annotated frame.
           """
           # Run inference
           results = self.model(frame, verbose=False)[0]
           
           # Get detections
           boxes = results.boxes
           
           for box in boxes:
               # Filter for vehicles
               cls = int(box.cls[0])
               if cls not in self.vehicle_classes:
                   continue
               
               # Get coordinates
               x1, y1, x2, y2 = map(int, box.xyxy[0])
               conf = float(box.conf[0])
               label = f"{results.names[cls]} {conf:.2f}"
               
               # Draw bounding box
               cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 255, 0), 2)
               
               # Draw label
               cv2.putText(frame, label, (x1, y1 - 10), 
                           cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)
           
           return frame
   ```

## 3. Backend – Update `HLSVideoStreamTrack` (`app/services/webrtc.py`)

Integrate the `YOLOInference` service into the video track.

1. **Modify `HLSVideoStreamTrack`:**
   Update `backend/app/services/webrtc.py` to include detection and simple performance optimization.

   ```python
   from app.services.ai import YOLOInference

   class HLSVideoStreamTrack(VideoStreamTrack):
       def __init__(self, stream_url: str):
           super().__init__()
           self.stream_url = stream_url
           self.cap = None
           self.fps = 30.0
           self.detector = YOLOInference()
           # Performance optimization: process every Nth frame
           self.frame_count = 0
           self.process_every_n = 2  # Skip frames to maintain real-time performance if needed
           self.connect()

       # ... connect() implementation ...

       async def recv(self):
           pts, time_base = await self.next_timestamp()

           ret, frame = False, None
           if self.cap and self.cap.isOpened():
               ret, frame = self.cap.read()

           if not ret:
               # ... reconnection logic ...
               return placeholder_frame

           # Performance optimization: skip inference on some frames
           self.frame_count += 1
           if self.frame_count % self.process_every_n == 0:
               # Run YOLO detection
               frame = self.detector.detect(frame)
           
           # Convert to av.VideoFrame
           video_frame = VideoFrame.from_ndarray(frame, format="bgr24")
           video_frame.pts = pts
           video_frame.time_base = time_base

           await asyncio.sleep(1.0 / self.fps)
           return video_frame
   ```

## 4. Performance Optimizations (Crucial)

Object detection is computationally expensive. To ensure the stream remains "live" and doesn't lag significantly:

- **Model Selection:** We use `yolov8n.pt` (Nano), the fastest and lightest version.
- **Frame Skipping:** The `process_every_n` parameter allows us to run inference on (e.g.) every 2nd or 3rd frame while still displaying the raw stream (or drawing the boxes from the previous detection).
- **Resolution Scaling:** If needed, we can resize the frame to a smaller resolution (e.g., 640x480) before passing it to YOLO.

## 5. Frontend – Verification

No changes are required in the React/Next.js code. The frontend will automatically display the annotated frames with bounding boxes as they are processed by the backend and sent over WebRTC.

1. **Verify Functionality:**
   - Observe the live stream in the browser.
   - Bounding boxes (green) should appear around cars, trucks, buses, and motorcycles.
   - Labels should indicate the class and confidence score.
   - Check the backend console for FPS or any performance warnings.

## 6. Execution Steps Checklist

- [ ] Run `uv add ultralytics` in `backend/`.
- [ ] Create `backend/app/services/ai.py` with `YOLOInference` class.
- [ ] Initialize `YOLOInference` in `HLSVideoStreamTrack.__init__`.
- [ ] Implement detection logic in `HLSVideoStreamTrack.recv()`.
- [ ] Test real-time performance and adjust `process_every_n` if lag occurs.
- [ ] Verify that the frontend correctly displays annotated video frames.
