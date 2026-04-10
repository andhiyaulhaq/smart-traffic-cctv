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

    def update_line(self, line_coords: list):
        """Updates the virtual line coordinates."""
        self.line_coords = line_coords
        # Optionally clear track history if the line moves significantly
        # self.track_history = {} 

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
            
            # Determine direction based on line midpoint
            # If line is more horizontal, use Y-axis
            # If line is more vertical, use X-axis
            dx = abs(p2[0] - p1[0])
            dy = abs(p2[1] - p1[1])
            
            if dy > dx: # More vertical line
                mid_x = (p1[0] + p2[0]) / 2
                if last_center[0] < mid_x and center[0] >= mid_x:
                    self.counts["enter"] += 1
                    return "enter"
                else:
                    self.counts["exit"] += 1
                    return "exit"
            else: # More horizontal line
                mid_y = (p1[1] + p2[1]) / 2
                if last_center[1] < mid_y and center[1] >= mid_y:
                    self.counts["enter"] += 1
                    return "enter"
                else:
                    self.counts["exit"] += 1
                    return "exit"
                
        return None

    def get_counts(self):
        return self.counts

    def get_line_pixels(self, frame_shape: tuple):
        """Returns pixel coordinates of the line."""
        h, w = frame_shape[:2]
        p1 = (int(self.line_coords[0] * w), int(self.line_coords[1] * h))
        p2 = (int(self.line_coords[2] * w), int(self.line_coords[3] * h))
        return p1, p2
