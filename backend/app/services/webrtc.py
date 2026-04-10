import asyncio
import numpy as np
from av import VideoFrame
from aiortc import VideoStreamTrack
import time

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
