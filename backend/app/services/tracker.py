import numpy as np

class LineCounter:
    """
    Handles vehicle counting by detecting line crossings.
    """
    def __init__(self, line_coords: list = None):
        # Default: horizontal line across the middle (normalized)
        if line_coords is None:
            self.line_coords = [0.0, 0.5, 1.0, 0.5]
        else:
            self.line_coords = line_coords
            
        self.track_history = {}  # {track_id: last_center}
        self.counted_ids = set()
        self.counts = {"enter": 0, "exit": 0}

    def _ccw(self, A, B, C):
        """Tests if the points A, B, C are in counter-clockwise order."""
        return (C[1] - A[1]) * (B[0] - A[0]) > (B[1] - A[1]) * (C[0] - A[0])

    def _intersect(self, A, B, C, D):
        """Returns True if segment AB intersects segment CD."""
        return self._ccw(A, C, D) != self._ccw(B, C, D) and \
               self._ccw(A, B, C) != self._ccw(A, B, D)

    def check_crossing(self, track_id: int, center: tuple, frame_shape: tuple):
        """
        Checks if a vehicle has crossed the virtual line.
        Returns the direction ('enter' or 'exit') if crossed, else None.
        """
        h, w = frame_shape[:2]
        # Convert normalized line to pixel coordinates
        p1 = (int(self.line_coords[0] * w), int(self.line_coords[1] * h))
        p2 = (int(self.line_coords[2] * w), int(self.line_coords[3] * h))
        
        last_center = self.track_history.get(track_id)
        self.track_history[track_id] = center
        
        if last_center is None:
            return None
            
        # Check if crossed the line
        if self._intersect(last_center, center, p1, p2):
            # To avoid double counting the same ID
            if track_id in self.counted_ids:
                return None
                
            self.counted_ids.add(track_id)
            
            # Simple direction logic: 
            # If moving from top (y < line_y) to bottom (y > line_y) -> 'enter'
            # If moving from bottom to top -> 'exit'
            # (Assuming horizontal line at middle)
            line_y = p1[1]
            if last_center[1] < line_y and center[1] >= line_y:
                self.counts["enter"] += 1
                return "enter"
            elif last_center[1] > line_y and center[1] <= line_y:
                self.counts["exit"] += 1
                return "exit"
            else:
                # If the line is vertical or vehicle movement is horizontal,
                # this simple logic might need refinement.
                # For now, we assume standard traffic flow (vertical movement).
                self.counts["enter"] += 1
                return "enter"
                
        return None

    def get_counts(self):
        return self.counts

    def get_line_pixels(self, frame_shape: tuple):
        """Returns pixel coordinates of the line."""
        h, w = frame_shape[:2]
        p1 = (int(self.line_coords[0] * w), int(self.line_coords[1] * h))
        p2 = (int(self.line_coords[2] * w), int(self.line_coords[3] * h))
        return p1, p2
