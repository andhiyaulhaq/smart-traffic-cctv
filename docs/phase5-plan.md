# Phase 5: Add ByteTrack for Persistent Tracking - Technical Implementation Plan

## Objective
The goal is to transition from frame-by-frame vehicle detection to persistent vehicle tracking. By leveraging the **ByteTrack** algorithm built into the Ultralytics YOLOv8 package, we will assign a unique track ID to each detected vehicle. This prevents double-counting and allows us to track trajectories across consecutive frames, which is essential for the line-crossing logic in Phase 6.

## 1. Backend – Update AI Service (`app/services/ai.py`)

Modify the existing `YOLOInference` service to use `model.track()` instead of standard inference. This instructs the model to retain object history between frames.

1. **Modify `YOLOInference.detect` (or rename to `track_vehicles`):**
   Update the logic to pass `persist=True` and `tracker="bytetrack.yaml"`. Also, extract the tracking ID from the bounding box data.

   ```python
   # backend/app/services/ai.py
   
   import cv2
   from ultralytics import YOLO
   import numpy as np

   class YOLOInference:
       def __init__(self, model_path: str = "yolov8n.pt"):
           self.model = YOLO(model_path)
           self.vehicle_classes = [2, 3, 5, 7] # car, motorcycle, bus, truck

       def detect(self, frame: np.ndarray) -> np.ndarray:
           """
           Runs tracking on a frame and returns an annotated frame with Track IDs.
           """
           # Use model.track instead of model()
           # persist=True ensures it remembers tracks from the previous frames
           # tracker="bytetrack.yaml" uses the ByteTrack algorithm overhead
           results = self.model.track(
               frame, 
               persist=True, 
               tracker="bytetrack.yaml", 
               verbose=False
           )[0]
           
           boxes = results.boxes
           
           if boxes is None or len(boxes) == 0:
               return frame

           for box in boxes:
               # Filter for vehicle classes
               cls = int(box.cls[0])
               if cls not in self.vehicle_classes:
                   continue
               
               # Extract bounding box 
               x1, y1, x2, y2 = map(int, box.xyxy[0])
               conf = float(box.conf[0])
               
               # Extract Track ID (can be None if the tracker hasn't assigned one yet)
               track_id = int(box.id[0]) if box.id is not None else -1
               
               # Prepare annotation label
               class_name = results.names[cls]
               if track_id != -1:
                   label = f"{class_name} ID:{track_id} {conf:.2f}"
               else:
                   label = f"{class_name} {conf:.2f}"
               
               # Draw bounding box and label
               cv2.rectangle(frame, (x1, y1), (x2, y2), (255, 165, 0), 2)  # Orange for tracked
               cv2.putText(frame, label, (x1, y1 - 10), 
                           cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 165, 0), 2)
           
           return frame
   ```

## 2. Tracking and Performance Considerations

In Phase 4, we introduced an optimization to skip frames (`process_every_n`).

- **Tracker Continuity:** ByteTrack thrives on temporal continuity. If too many frames are skipped, vehicles may move too much between processed frames, causing the tracker to lose the object and re-assign a new ID (ID switches).
- **Adjustment:** If ID switches happen frequently, reduce `process_every_n` to `1` (process every frame) or `2` in `HLSVideoStreamTrack`. If this causes lag, the better optimization is to shrink the resolution of the frame passed to the YOLO model (e.g., resize to 640x360 prior to tracking, then map boxes back or just stream the smaller frame).

No changes are strictly required in `HLSVideoStreamTrack` except perhaps tuning `process_every_n`.

## 3. Frontend – Verification

No changes are needed on the frontend in this phase. The UI receives standard WebRTC video frames.

1. **Verify Functionality:**
   - Observe the live stream in the frontend dashboard.
   - Bounding boxes will now include an `ID: X` label (e.g., `car ID:1 0.85`).
   - Check that as a vehicle moves across the screen, its ID number remains constant.
   - If an object gets temporarily occluded (e.g., moving behind a lamppost), check if ByteTrack successfully assigns the same ID when it reappears.

## 4. Execution Steps Checklist

- [ ] Modify `backend/app/services/ai.py` to use `model.track(..., persist=True, tracker="bytetrack.yaml")`.
- [ ] Add logic to safely extract `box.id` (handling cases where it might be `None`).
- [ ] Include the `track_id` in the `cv2.putText` annotation.
- [ ] Run the backend and observe the frontend video stream to verify tracking persistence.
- [ ] (Optional) Tune `process_every_n` in `HLSVideoStreamTrack` if tracker stability is poor.
