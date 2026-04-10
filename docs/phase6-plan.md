# Phase 6: Virtual Line Crossing Counting - Technical Implementation Plan

## Objective
The goal is to implement the core business logic: counting vehicles that cross a virtual line. This involves detecting the crossing using the persistent Track IDs from Phase 5, logging these events to a SQLite database, and broadcasting the updates to the frontend via WebSockets for a real-time count display.

## 1. Backend – Install Database Dependencies
We will use `aiosqlite` for asynchronous database operations and `websockets` for real-time updates.

```bash
cd backend
uv add aiosqlite
```

## 2. Backend – Database Layer

Create a structured database layer to handle persistence.

### 1. Schema Definition (`backend/app/database/queries.sql`)
```sql
CREATE TABLE IF NOT EXISTS counting_events (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
    direction TEXT NOT NULL CHECK(direction IN ('enter', 'exit')),
    vehicle_class TEXT NOT NULL,
    track_id INTEGER NOT NULL,
    confidence REAL
);

-- Index for faster aggregation
CREATE INDEX IF NOT EXISTS idx_counting_events_timestamp ON counting_events(timestamp);
```

### 2. Connection Manager (`backend/app/database/connection.py`)
Implement an async engine to handle SQLite connections.

### 3. Repository (`backend/app/database/repository.py`)
Implement functions like `insert_count_event` and `get_today_stats`.

## 3. Backend – Line Crossing Logic (`backend/app/services/tracker.py`)

Create a `LineCounter` class to manage the crossing detection.

1. **Detection Algorithm**: 
   - Store the last known center point `(x, y)` for each active `track_id`.
   - When a new frame arrives, check if the segment connecting the *previous center* and *current center* intersects with the *virtual line segment*.
   - Use the **cross product method** to determine if the segments intersect.

2. **Crossing Direction**:
   - Determine whether the movement is "entering" or "exiting" based on the vector direction relative to the line's normal.

3. **Prevention of Double Counting**:
   - Maintain a set of `counted_ids` per session to ensure a vehicle is only counted once.

## 4. Backend – WebSocket Communication (`backend/app/main.py`)

1. **Connection Manager**:
   - Maintain a list of active WebSocket connections.
   - Implement a `broadcast` method to send JSON updates to all connected dashboards.

2. **API Endpoint**:
   - Add `@app.websocket("/ws/counts")` to handle incoming frontend connections.

## 5. Backend – Integration (`backend/app/services/webrtc.py`)

1. **Initialize Tracker**:
   - In `HLSVideoStreamTrack`, initialize the `LineCounter` with predefined line coordinates (e.g., across the middle of the frame).

2. **Process Frames**:
   - In `recv()`, after tracking:
     - Extract centers of tracked boxes.
     - Call `tracker.check_crossing(track_id, center, class_name)`.
     - Draw the virtual line (e.g., blue) on the frame.
     - Draw the running total counts in the corner of the video.

## 6. Frontend – Real-time Dashboard Updates

### 1. WebSocket Hook (`frontend/src/hooks/useWebSocket.ts`)
Create a custom hook to manage the WebSocket lifecycle, automatically reconnecting if the connection drops, and updating a global or local state (via Zustand or `useState`).

### 2. Update Counter Display (`frontend/src/components/CounterCard.tsx`)
Create or update components to show the live counts received via WebSocket.

## 7. Execution Steps Checklist

- [ ] Run `uv add aiosqlite` and initialize the SQLite database.
- [ ] Create `backend/app/database/` with connection, query, and repository logic.
- [ ] Implement `LineCounter` logic in `backend/app/services/tracker.py`.
- [ ] Integrate `LineCounter` and drawing logic into `HLSVideoStreamTrack`.
- [ ] Implement WebSocket signal broadcasting in `main.py`.
- [ ] Create `useWebSocket` hook in the frontend.
- [ ] Update the dashboard UI to display real-time vehicle counts.
- [ ] Verify that crossing the line increments the counter on the dashboard in real-time.
