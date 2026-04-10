Here’s the updated project description – now using **Next.js (App Router)** instead of Vite+React, while keeping **real‑time CCTV streaming (HLS)** and **ByteTrack** for robust vehicle tracking. The frontend package manager remains **`pnpm`**, and the backend still uses **`uv`** (Python).

---

## Real-Time Vehicle Counting System with ByteTrack – Detailed Portfolio Project Description

### Overview  
This project is a **real-time vehicle counting system** that ingests a live CCTV HLS stream (e.g., public traffic camera), detects and **tracks** vehicles using YOLOv8 + ByteTrack, counts crossings over a virtual line, and displays the results in a modern web dashboard. The backend is built with **FastAPI** (handling WebRTC signaling, HLS ingestion, and database operations), while the frontend uses **Next.js (App Router)** with **shadcn/ui** components. All data is persisted in **SQLite** using **raw SQL** (no ORM), with **Pydantic** models for validation.  

The system is designed as a **production‑ready portfolio piece** showcasing real‑time computer vision with **object tracking**, live HLS stream processing, WebRTC for low‑latency streaming, async API design, and a modern Next.js frontend. The first demo uses a **public CCTV HLS stream** – no local file or hardware required.

---

### Core Features

| Feature | Description |
|---------|-------------|
| **Live HLS stream input** | Read an `.m3u8` URL (e.g., public CCTV) using OpenCV + FFmpeg, process frames in real time. |
| **YOLOv8 vehicle detection** | Detect `car`, `truck`, `bus`, `motorcycle` (COCO classes) – filter out `person`, `bicycle`, etc. |
| **ByteTrack object tracking** | Assign unique IDs to each detected vehicle across frames, enabling per‑vehicle trajectory analysis. |
| **Virtual line crossing with tracking** | Count a vehicle only **once** when its tracked bounding box center crosses the line. Tracking prevents double‑counting (e.g., when a vehicle pauses on the line or moves back and forth). |
| **WebRTC streaming** | Stream processed video (with bounding boxes, track IDs, and line overlay) to the browser with sub‑second latency. |
| **Real‑time dashboard** | Next.js frontend showing live video, current vehicle counts (today/total), per‑class breakdown, and a historical chart. |
| **Database logging** | SQLite tables for `counting_events` (timestamp, direction, vehicle_class, track_id, confidence) and `sessions`. |
| **REST API + WebSocket** | REST endpoints for configuration and stats; WebSocket for live count updates. |
| **Async processing** | FastAPI’s background tasks to run YOLO + ByteTrack inference without blocking the streaming pipeline. |
| **Stream resilience** | Automatic reconnection if HLS stream drops; buffering management to avoid lag accumulation. |

---

### Tech Stack & Justification

| Layer | Technology | Why |
|-------|------------|-----|
| **Python package manager** | `uv` (astral-sh/uv) | Extremely fast, replaces `pip` / `poetry` / `requirements.txt`. Single tool for deps, virtual envs, and scripting. |
| **Backend** | FastAPI | High performance, async support, automatic OpenAPI docs, easy WebRTC signaling integration. |
| **WebRTC** | `aiortc` (Python) + native browser `RTCPeerConnection` (frontend) | Lightweight, works without third‑party media servers or heavy dependencies. |
| **Object Detection & Tracking** | YOLOv8 + ByteTrack (via `model.track(..., tracker="bytetrack.yaml")`) | State‑of‑the‑art tracking that handles occlusions and ID switches well. Built into Ultralytics. |
| **HLS Ingestion** | OpenCV (`cv2.VideoCapture`) with FFmpeg backend | Can read HLS streams directly; FFmpeg handles re-buffering and reconnection. |
| **Video Processing** | OpenCV + `numpy` | Frame capture, drawing, and transformation. |
| **Database** | SQLite + `aiosqlite` | Zero‑config, ACID compliant, and async driver. Raw SQL gives full control. |
| **Validation** | Pydantic v2 | Data validation, settings management, and serialization (used by FastAPI). |
| **Frontend package manager** | `pnpm` | Disk‑efficient, fast, works seamlessly with Next.js. |
| **Frontend framework** | Next.js 14+ (App Router) | React framework with SSR/SSG capabilities, great developer experience, and easy integration with shadcn/ui. |
| **UI Library** | shadcn/ui + Tailwind CSS | Accessible, customisable components (card, chart, slider, etc.). Works perfectly with Next.js. |
| **State & Streaming** | Zustand + WebSocket | Real‑time count updates and video element management. |
| **Charts** | Recharts | Built on React, works well with shadcn/ui and Next.js. |

---

### Project Structure

#### Backend (using `uv`)

```
backend/
├── pyproject.toml            # uv project definition (dependencies, scripts)
├── uv.lock
├── .env
├── app/
│   ├── main.py               # FastAPI app, WebSocket, WebRTC endpoints
│   ├── config.py             # Pydantic settings (HLS stream URL, line coords, model)
│   ├── database/
│   │   ├── connection.py     # aiosqlite connection manager
│   │   ├── queries.sql       # Raw SQL create/insert/select statements
│   │   └── repository.py     # Functions that execute raw SQL
│   ├── models/
│   │   ├── schemas.py        # Pydantic models (CountEvent, LineConfig, etc.)
│   │   └── detection.py      # YOLO wrapper (load model, track with ByteTrack)
│   ├── services/
│   │   ├── tracker.py        # Line crossing logic using track IDs + per‑vehicle crossing state
│   │   ├── webrtc.py         # aiortc peer connection, video track
│   │   ├── hls_reader.py     # Async HLS stream reader (manages cv2.VideoCapture, reconnects)
│   │   └── pipeline.py       # Async frame producer -> detector + tracker -> broadcaster
│   └── utils/
│       ├── logger.py
│       └── frames_to_webrtc.py  # Convert OpenCV frames to video stream
```

#### Frontend (using `pnpm` + Next.js)

```
frontend/
├── package.json              # managed by pnpm
├── pnpm-lock.yaml
├── next.config.js            # Next.js configuration (CORS, rewrites for API proxy)
├── tailwind.config.js
├── postcss.config.js
├── src/
│   ├── app/
│   │   ├── layout.tsx        # Root layout (includes shadcn/ui provider)
│   │   ├── page.tsx          # Main dashboard page (client component)
│   │   └── globals.css       # Tailwind + shadcn styles
│   ├── components/
│   │   ├── ui/               # shadcn/ui components (button, card, slider, etc.)
│   │   ├── VideoPlayer.tsx   # WebRTC <video> element with auto‑play
│   │   ├── CounterCard.tsx   # Displays current in/out counts per vehicle class
│   │   ├── LineConfig.tsx    # Sliders to adjust virtual line position
│   │   └── HistoryChart.tsx  # Recharts line chart of counts per minute
│   ├── hooks/
│   │   ├── useWebRTC.ts      # native RTCPeerConnection initialisation, signalling
│   │   └── useWebSocket.ts   # listen for real‑time count updates
│   ├── lib/
│   │   ├── api.ts            # typed fetch calls (can use Next.js API routes as proxy)
│   │   └── utils.ts
│   └── types/                # TypeScript types shared with backend (optional)
```

**Note:** Next.js will run separately from FastAPI (e.g., on port 3000). To avoid CORS issues, you can configure `next.config.js` with `rewrites` to proxy API requests to the backend (e.g., `/api/*` → `http://localhost:8000/*`). WebSocket connections go directly to the backend.

---

### How It Works (Data Flow)

1. **Backend startup** – Loads YOLOv8 + ByteTrack, initialises the HLS stream reader (using `cv2.VideoCapture` with FFmpeg), creates SQLite tables, starts an async background task that continuously reads frames from the live stream.
2. **HLS ingestion** – `hls_reader.py` wraps `cv2.VideoCapture` and handles:
   - Opening the `.m3u8` URL with `cv2.CAP_FFMPEG`.
   - If the stream drops, it automatically retries (exponential backoff).
   - Frames are read at real‑time pace (no faster than stream FPS) to avoid massive buffering.
3. **WebRTC signalling** – Frontend calls `/offer` endpoint (proxied via Next.js rewrite or direct to backend), backend creates an `aiortc` `RTCPeerConnection`, adds a `VideoStreamTrack` that yields processed frames, and returns the SDP answer.
4. **Frame processing pipeline**  
   - Read frame from HLS reader → resize → call `model.track(frame, persist=True, tracker='bytetrack.yaml')`.  
   - Filter results to vehicle classes (`car`, `truck`, `bus`, `motorcycle`).  
   - For each tracked vehicle, obtain: bounding box, track ID, class, confidence.  
   - Update `tracker.py`: maintain dictionary of last known positions per track ID, and a set of already‑counted track IDs for the current crossing direction.  
   - Check line crossing: if the vehicle’s bounding box center crosses the virtual line **and** the track ID hasn’t been counted for this crossing → increment counter, log event (with track ID), mark track ID as counted.  
   - Draw bounding boxes, track IDs, line, and current counts on the frame.  
   - Put frame into a thread‑safe queue for the WebRTC track.
5. **WebRTC streaming** – The `VideoStreamTrack` reads from the queue at the stream’s natural frame rate (e.g., 25‑30 fps), converts frame to JPEG or raw YUV, and sends it to the browser.
6. **Frontend display** – `VideoPlayer` renders the stream, `CounterCard` updates via WebSocket, `HistoryChart` queries REST endpoint `/stats/hourly` (via fetch).

---

### API Endpoints (REST + WebSocket)

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/health` | Health check |
| POST | `/offer` | WebRTC SDP offer → returns answer SDP |
| GET | `/stats/today` | Total counts for today (entered/exited per vehicle class) |
| GET | `/stats/hourly` | Aggregated counts per hour (for chart) |
| POST | `/line` | Update virtual line coordinates (Pydantic validated) |
| GET | `/line` | Get current line coordinates |
| WebSocket | `/ws/counts` | Real‑time count updates (JSON: `{direction, class, track_id, total_entered, total_exited}`) |

---

### Database Schema (Raw SQL)

```sql
-- tables.sql
CREATE TABLE IF NOT EXISTS counting_events (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
    direction TEXT NOT NULL CHECK(direction IN ('enter', 'exit')),
    vehicle_class TEXT NOT NULL,   -- 'car', 'truck', 'bus', 'motorcycle'
    track_id INTEGER NOT NULL,     -- ByteTrack ID
    confidence REAL,
    line_id INTEGER DEFAULT 1
);

CREATE TABLE IF NOT EXISTS system_events (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
    event_type TEXT,
    details TEXT
);

CREATE INDEX idx_events_timestamp ON counting_events(timestamp);
CREATE INDEX idx_events_class ON counting_events(vehicle_class);
CREATE INDEX idx_events_track ON counting_events(track_id);
```

Repository function example:

```python
async def insert_count_event(direction: str, vehicle_class: str, track_id: int, confidence: float):
    async with get_db() as db:
        await db.execute(
            "INSERT INTO counting_events (direction, vehicle_class, track_id, confidence) VALUES (?, ?, ?, ?)",
            (direction, vehicle_class, track_id, confidence)
        )
        await db.commit()
```

---

### Additional Tooling & Features (Advice for a Stronger Portfolio)

| Area | Suggestion | Why it helps |
|------|------------|---------------|
| **Deployment** | Docker Compose (backend + frontend) + GitHub Actions CI/CD | Shows DevOps maturity; easy to demo. |
| **Performance** | Use ONNX runtime or TensorRT for YOLO (2-3x faster) | Handles higher resolution / real‑time streams. |
| **Stream resilience** | Use `ffmpeg` with timeouts; fallback to a static image on failure | Demonstrates robustness for production. |
| **Authentication** | JWT-based auth (FastAPI `HTTPBearer`) + protected WebRTC endpoints | Adds security (essential for real products). |
| **Multi‑stream** | Extend schema with `camera_id` and allow switching between multiple HLS URLs via UI | Demonstrates scalability. |
| **Advanced tracking** | Tune ByteTrack parameters (track_thresh, match_thresh) for vehicles | Improves ID stability under occlusion. |
| **Admin panel** | shadcn/ui table to view raw counting events with pagination | Makes debugging transparent. |
| **Prometheus metrics** | Export `vehicles_counted_total` and `inference_latency_seconds` | Shows monitoring awareness. |
| **Testing** | Pytest for backend (async tests with `pytest-asyncio`) + Jest/Vitest for frontend | Proves reliability. |
| **Documentation** | OpenAPI (auto‑generated) + a `README.md` with architecture diagram (Mermaid) | Essential for portfolio explanation. |
| **Stream info overlay** | Show bitrate, dropped frames, reconnect status on frontend | Adds polish and debugging info. |
| **Next.js API routes** | Optional proxy for REST endpoints to avoid CORS | Simplifies frontend configuration. |

---

### Why This Is a Great Portfolio Project

- **Real‑world data** – Processes a live public CCTV stream (no simulated video), showcasing ability to handle real‑time, unreliable sources.  
- **End‑to‑end** – From HLS ingestion to Next.js dashboard, you own the entire pipeline.  
- **Modern stack** – FastAPI, WebRTC, Next.js, shadcn/ui, raw SQL, `uv`, `pnpm` – all industry‑relevant.  
- **Real‑time complexity** – Async coordination between HLS stream reading, ML inference + tracking, database writes, and WebRTC streaming.  
- **Tracking for accuracy** – ByteTrack eliminates double‑counting, demonstrating advanced CV skills.  
- **Measurable outcome** – Vehicle counting is directly applicable to traffic monitoring, toll systems, and smart parking.  
- **Demo‑ready** – Just provide the HLS URL and run; no extra hardware or video files needed.  
- **Next.js advantages** – SSR/SSG capabilities, great developer experience, easy deployment on Vercel (if backend is separately hosted).  

By implementing this project and highlighting the additional tooling (Docker, ONNX, Prometheus, tests), you will demonstrate **full‑stack, real‑time, and DevOps skills** – exactly what companies look for in a senior portfolio.