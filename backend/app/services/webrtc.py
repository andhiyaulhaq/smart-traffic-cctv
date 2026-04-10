import asyncio
import cv2
import numpy as np
import time
from av import VideoFrame
from aiortc import VideoStreamTrack

class SyntheticVideoTrack(VideoStreamTrack):
    """
    A video stream track that generates synthetic frames.
    """
    def __init__(self):
        super().__init__()
        self.counter = 0

    async def recv(self):
        pts, time_base = await self.next_timestamp()
        
        # Generate a synthetic frame: a simple colored square that shifts color
        self.counter += 1
        img = np.zeros((480, 640, 3), dtype=np.uint8)
        
        # Change color based on counter to create a visual effect
        r = int((np.sin(self.counter * 0.1) + 1) * 127)
        g = int((np.cos(self.counter * 0.1) + 1) * 127)
        img[:] = (r, g, 150)  # BGR format
        
        # Convert to av.VideoFrame
        frame = VideoFrame.from_ndarray(img, format="bgr24")
        frame.pts = pts
        frame.time_base = time_base
        
        return frame

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

    async def recv(self):
        # next_timestamp() handles the pacing based on the track's internal clock
        pts, time_base = await self.next_timestamp()

        # Read the next frame in a thread to avoid blocking the event loop
        loop = asyncio.get_event_loop()
        ret, frame = await loop.run_in_executor(None, self.cap.read)
        
        if not ret:
            # If the video ends, loop it from the beginning
            await loop.run_in_executor(None, lambda: self.cap.set(cv2.CAP_PROP_POS_FRAMES, 0))
            ret, frame = await loop.run_in_executor(None, self.cap.read)
            if not ret:
                # If it still fails, return a black frame 
                frame = np.zeros((480, 640, 3), dtype=np.uint8)

        # Convert to av.VideoFrame format
        # OpenCV reads in BGR, which is matched by format="bgr24"
        video_frame = VideoFrame.from_ndarray(frame, format="bgr24")
        video_frame.pts = pts
        video_frame.time_base = time_base

        return video_frame

    def stop(self):
        """Ensure we release the cv2 VideoCapture when the track stops."""
        super().stop()
        if self.cap:
            self.cap.release()
