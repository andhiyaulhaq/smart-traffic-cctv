import cv2
from ultralytics import YOLO
import numpy as np

class YOLOInference:
    """
    Service for running YOLOv8 object detection on video frames.
    """
    def __init__(self, model_path: str = "yolov8n.pt"):
        # Load the model (Nano version for speed)
        # It will be downloaded automatically on the first run
        self.model = YOLO(model_path)
        
        # COCO class IDs for vehicles
        # 2: car, 3: motorcycle, 5: bus, 7: truck
        self.vehicle_classes = [2, 3, 5, 7]

    def detect(self, frame: np.ndarray) -> np.ndarray:
        """
        Detects and tracks vehicles in a frame and returns the annotated frame.
        """
        # Run tracking
        # persist=True retains history between frames
        # tracker="bytetrack.yaml" uses the ByteTrack tracker
        # verbose=False suppresses prediction logs in console
        results = self.model.track(frame, persist=True, tracker="bytetrack.yaml", verbose=False)[0]
        
        # Get detection results
        boxes = results.boxes
        names = results.names
        
        if boxes is None or len(boxes) == 0:
            return frame

        for box in boxes:
            cls_id = int(box.cls[0])
            
            # Filter for vehicle classes only
            if cls_id not in self.vehicle_classes:
                continue
            
            # Extract coordinates and confidence
            x1, y1, x2, y2 = map(int, box.xyxy[0])
            conf = float(box.conf[0])
            class_name = names[cls_id]
            
            # Extract Track ID
            track_id = int(box.id[0]) if box.id is not None else -1
            
            # Prepare label text
            if track_id != -1:
                label = f"{class_name} ID:{track_id} {conf:.2f}"
            else:
                label = f"{class_name} {conf:.2f}"
            
            # Bounding box color (Orange for tracked: BGR)
            color = (0, 165, 255)
            
            # Draw the bounding box
            cv2.rectangle(frame, (x1, y1), (x2, y2), color, 2)
            
            # Draw the label background
            (w, h), _ = cv2.getTextSize(label, cv2.FONT_HERSHEY_SIMPLEX, 0.5, 1)
            cv2.rectangle(frame, (x1, y1 - 20), (x1 + w, y1), color, -1)
            
            # Draw the text label
            cv2.putText(frame, label, (x1, y1 - 5), 
                        cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1)
        
        return frame
