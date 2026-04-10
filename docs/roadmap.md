## Detailed Priority List – Step‑by‑Step Implementation

The goal is to **get a working video stream from the backend to the frontend as early as possible**, then incrementally add detection, tracking, counting, and polish. Each step produces a **working, testable increment**.

---

### Phase 0 – Project Scaffolding (1–2 days)

- Set up project directories (`backend/`, `frontend/`).
- Initialize `uv` in `backend/` with `pyproject.toml` (add FastAPI, uvicorn, python-dotenv, pydantic).
- Initialize `pnpm` in `frontend/` with Next.js + TypeScript + Tailwind CSS.
- Install `shadcn/ui` (follow Next.js setup).
- Create a simple “Hello World” API endpoint in FastAPI and a Next.js page that fetches it to verify communication.

**Deliverable:** Backend runs on `localhost:8000`, frontend on `localhost:3000`, proxy configured (or CORS enabled).

---

### Phase 1 – Basic WebRTC Streaming (Week 1 priority)

**Goal:** Stream *unprocessed* video from a file or test source to the frontend.

1. **Backend – WebRTC track skeleton**  
   - Implement a dummy `VideoStreamTrack` that generates synthetic frames (e.g., coloured rectangles or a test pattern) at 30 fps.  
   - Create a `/offer` endpoint that returns an SDP answer using `aiortc`.  
   - No OpenCV, no YOLO yet.

2. **Frontend – WebRTC signalling**
   - No extra WebRTC libraries required (use native browser `RTCPeerConnection`).
   - Create a `useWebRTC` hook that calls `/offer`, exchanges SDP, and attaches the remote stream to a `<video>` element.  
   - Display the video.

**Deliverable:** Frontend shows a synthetic video stream from the backend. This proves WebRTC works.

---

### Phase 2 – Replace Synthetic Frames with Real Video (Week 2)

**Goal:** Stream an actual video file (local MP4) via WebRTC.

3. **Backend – OpenCV video reader**  
   - Use `cv2.VideoCapture` to open a local video file (hardcoded path for now).  
   - In the `VideoStreamTrack`, read frames sequentially, convert to JPEG (or YUV), and send.  
   - Handle frame rate (e.g., sleep to match original FPS).  
   - No detection yet – just pass the raw frame.

4. **Frontend – Verify**  
   - Confirm that the frontend now plays the video file.

**Deliverable:** Frontend plays any local video file streamed via WebRTC.

---

### Phase 3 – HLS Live Stream Ingestion (Week 3)

**Goal:** Replace local file with a live HLS (`.m3u8`) stream.

5. **Backend – HLS reader**  
   - Use `cv2.VideoCapture` with FFmpeg backend: `cv2.VideoCapture(hls_url, cv2.CAP_FFMPEG)`.  
   - Implement simple retry logic (if stream drops, re‑open).  
   - Feed frames into the same `VideoStreamTrack`.  
   - Add configuration via `.env` for the HLS URL.

6. **Frontend – No changes needed** (stream just works).

**Deliverable:** Frontend displays the live CCTV stream.

---

### Phase 4 – Add Vehicle Detection (YOLO) without Tracking (Week 4)

**Goal:** Draw bounding boxes on detected vehicles (but no counting yet).

7. **Backend – YOLO integration**  
   - Install `ultralytics`.  
   - Load YOLOv8 model (e.g., `yolov8n.pt`).  
   - In the processing loop, run `model(frame)` on each frame.  
   - Filter for vehicle classes (car, truck, bus, motorcycle).  
   - Draw bounding boxes on the frame (using OpenCV).  
   - The `VideoStreamTrack` now sends annotated frames.  
   - Performance: measure FPS; if too slow, skip every other frame or reduce resolution.

8. **Frontend – Verify**  
   - Bounding boxes appear on the live stream.

**Deliverable:** Live stream shows bounding boxes around vehicles.

---

### Phase 5 – Add ByteTrack for Persistent Tracking (Week 5)

**Goal:** Assign unique IDs to vehicles and draw them on the stream.

9. **Backend – ByteTrack via `model.track`**  
   - Change `model(frame)` to `model.track(frame, persist=True, tracker='bytetrack.yaml')`.  
   - Extract track IDs, bounding boxes, classes, confidences.  
   - Draw track ID numbers on each bounding box.

10. **Frontend – No changes** (just displays the enriched stream).

**Deliverable:** Vehicles have persistent IDs that follow them across frames.

---

### Phase 6 – Virtual Line Crossing Counting (Week 5–6)

**Goal:** Count vehicles that cross a predefined line, log to SQLite, and show counts via WebSocket.

11. **Backend – Line crossing logic**  
    - Define a virtual line (two points: `(x1, y1)` and `(x2, y2)`).  
    - For each tracked vehicle, store previous frame’s bounding box centre.  
    - Check if the line segment between previous and current centre crosses the virtual line (line‑segment intersection).  
    - If crossing occurs and this track ID hasn’t been counted for the current direction, increment counter, insert into SQLite, and broadcast via WebSocket.

12. **Backend – SQLite + WebSocket**  
    - Create `counting_events` table (raw SQL).  
    - Implement a WebSocket endpoint (`/ws/counts`) that pushes every count event to all connected clients.

13. **Frontend – Real‑time counter display**  
    - Use `useWebSocket` hook to listen for count updates.  
    - Display “Entered” and “Exited” totals (and per‑class if desired).  
    - Add a simple `CounterCard` component.

**Deliverable:** Every time a vehicle crosses the line, the counter increments on the dashboard.

---

### Phase 7 – User Interface & Configuration (Week 6)

**Goal:** Make the line adjustable and show historical data.

14. **Frontend – Line configuration slider**  
    - Add a slider or draggable handle to change line position.  
    - On change, call `POST /line` with new coordinates (Pydantic validated).  
    - Backend stores current line in memory (and optionally in SQLite config table).

15. **Frontend – Historical chart**  
    - Add a `GET /stats/hourly` endpoint that aggregates counts per hour from SQLite.  
    - Use Recharts to plot a line chart of counts over time.

16. **Frontend – Error & status overlay**  
    - Show stream connection status, dropped frames, reconnection attempts.

**Deliverable:** Fully functional dashboard with adjustable line and historical chart.

---

### Phase 8 – Production Polish (Week 6+)

**Goal:** Dockerise, add tests, optimise performance.

17. **Docker Compose**  
    - Dockerfile for backend (with `uv`), Dockerfile for frontend (Next.js standalone output).  
    - Compose file to run both services.

18. **Testing**  
    - Backend: `pytest` with async tests for counting logic, database.  
    - Frontend: Vitest or Jest for components.

19. **Performance optimisations**  
    - Model quantisation (ONNX, TensorRT).  
    - Frame skipping or resolution reduction if needed.

20. **Documentation**  
    - `README.md` with architecture diagram (Mermaid), setup instructions, demo GIF.

---

## Summary Priority Table (Minimum Viable Product First)

| Priority | Feature | Status |
|----------|---------|--------|
| **P0** | WebRTC streaming (synthetic frames) | Must work |
| **P1** | Stream local video file | Must work |
| **P2** | Stream HLS live URL | Must work |
| **P3** | YOLO detection (bounding boxes) | Must work |
| **P4** | ByteTrack (track IDs) | Must work |
| **P5** | Line crossing + SQLite logging | Must work |
| **P6** | WebSocket + frontend counter | Must work |
| **P7** | Adjustable line UI | Nice to have |
| **P8** | Historical chart | Nice to have |
| **P9** | Docker + tests | Polish |

**Crucially:** Do not add detection, tracking, or counting until Phase 1–3 are fully working. Always keep a working version at the end of each day.