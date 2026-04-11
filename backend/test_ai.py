from app.services.ai import YOLOInference
import cv2
import numpy as np

def test_inference():
    print("Initializing YOLOInference...")
    detector = YOLOInference()
    print("Initializer done.")
    
    # Create a dummy frame (black)
    frame = np.zeros((480, 640, 3), dtype=np.uint8)
    
    print("Testing detection on dummy frame...")
    annotated_frame, detections = detector.detect(frame)
    print("Detection done.")
    print("Result frame shape:", annotated_frame.shape)
    print("Number of detections:", len(detections))

if __name__ == "__main__":
    test_inference()
