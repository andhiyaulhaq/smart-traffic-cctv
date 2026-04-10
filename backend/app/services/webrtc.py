import asyncio
import cv2
import numpy as np
import time
from av import VideoFrame
from aiortc import VideoStreamTrack
from app.services.ai import YOLOInference
from app.services.tracker import LineCounter
from app.database.repository import save_count_event, get_total_counts

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
        self._detector = YOLOInference()
        self._tracker = LineCounter()
        self._frame_count = 0
        self._process_every_n = 1 # Process every frame for better tracker continuity
        self._connect()
        
        # Initial counts from DB
        self._counts = {"enter": 0, "exit": 0}
        asyncio.create_task(self._sync_counts())

    async def _sync_counts(self):
        """Syncs the in-memory tracker counts with the database."""
        db_counts = await get_total_counts()
        self._tracker.counts = db_counts
        self._counts = db_counts

    def _connect(self):
        if self.cap:
            self.cap.release()
        
        # cv2.CAP_FFMPEG is explicitly passed to ensure proper network/HLS handling
        self.cap = cv2.VideoCapture(self.stream_url, cv2.CAP_FFMPEG)
        
        if not self.cap.isOpened():
            print(f"Warning: Could not open HLS stream: {self.stream_url}")
        else:
            fps = self.cap.get(cv2.CAP_PROP_FPS)
            if fps > 0 and not np.isnan(fps):
                self.fps = fps

    async def recv(self):
        pts, time_base = await self.next_timestamp()

        loop = asyncio.get_event_loop()
        ret, frame = False, None
        
        if self.cap and self.cap.isOpened():
            ret, frame = await loop.run_in_executor(None, self.cap.read)

        if ret:
            self._frame_count += 1
            
            # Update line coordinates from global config
            from app.main import get_line_config
            self._tracker.update_line(get_line_config())

            if self._frame_count % self._process_every_n == 0:
                # Run detection and tracking
                frame, detections = await loop.run_in_executor(None, self._detector.detect, frame)
                
                # Check for line crossings
                for det in detections:
                    direction = self._tracker.check_crossing(det["track_id"], det["center"], frame.shape)
                    if direction:
                        # Crossing detected!
                        self._counts = self._tracker.get_counts()
                        # Save to DB and broadcast (fire and forget tasks)
                        asyncio.create_task(save_count_event(
                            direction=direction,
                            vehicle_class=det["class_name"],
                            track_id=det["track_id"],
                            confidence=det["confidence"]
                        ))
                        
                        # We need the broadcast function from main.py
                        # But wait, to avoid circular imports, we can use a callback or import locally
                        from app.main import broadcast_count_update
                        asyncio.create_task(broadcast_count_update({
                            "type": "count_update",
                            "counts": self._counts,
                            "event": {
                                "direction": direction,
                                "class_name": det["class_name"],
                                "track_id": det["track_id"]
                            }
                        }))

            # Draw the virtual line
            p1, p2 = self._tracker.get_line_pixels(frame.shape)
            cv2.line(frame, p1, p2, (255, 0, 0), 2) # Blue line
            
            # Draw counts on frame
            enter_text = f"Entered: {self._counts['enter']}"
            exit_text = f"Exited: {self._counts['exit']}"
            cv2.putText(frame, enter_text, (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 255, 0), 2)
            cv2.putText(frame, exit_text, (10, 60), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 0, 255), 2)

        if not ret:
            # Connection dropped or stalled
            print("Stream read failed or stream ended. Reconnecting...")
            await loop.run_in_executor(None, self._connect)
            
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

        return video_frame

    def stop(self):
        """Ensure we release the cv2 VideoCapture when the track stops."""
        super().stop()
        if self.cap:
            self.cap.release()
