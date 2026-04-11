# Phase 8: Production Readiness & Optimization - Technical Implementation Plan

## Objective
The goal of Phase 8 is to transition the project from a development prototype to a production-ready system. This involves containerization, performance tuning, automated testing, and adding an administrative interface to audit the raw counting data.

## 1. Dockerization
Create a standardized environment for deployment using Docker.

### [NEW] `backend/Dockerfile`
- Base image: `python:3.11-slim`
- Install system dependencies for OpenCV and FFmpeg.
- Install `uv`.
- Copy code, install dependencies using `uv sync`.
- Entrypoint: `uv run uvicorn app.main:app --host 0.0.0.0`.

### [NEW] `frontend/Dockerfile`
- Base image: `node:20-alpine` (multi-stage build).
- Stage 1: Build the Next.js app using `pnpm`.
- Stage 2: Serve using the built-in Next.js standalone output for minimal image size.

### [NEW] `docker-compose.yml`
- Orchestrate `backend` and `frontend`.
- Map ports (8000 for backend, 3000 for frontend).
- Set environment variables (HLS URL, Database path).

## 2. Admin Interface: Raw Events Table
Implement a "Logs" section in the dashboard to view the raw `counting_events` from SQLite.

### Backend – `repository.py`
Add `get_recent_events(limit: int = 50)`:
```python
async def get_recent_events(limit: int = 50):
    async with get_db() as db:
        async with db.execute(
            "SELECT * FROM counting_events ORDER BY timestamp DESC LIMIT ?", (limit,)
        ) as cursor:
            return [dict(row) for row in await cursor.fetchall()]
```

### Backend – `main.py`
Add `GET /events` endpoint to return the list of recent crossings.

### Frontend – `src/components/EventsTable.tsx`
- Create a data table using `shadcn/ui` Table components.
- Columns: ID, Timestamp, Direction, Vehicle Class, Track ID, Confidence.
- Integrate into a new "Admin" or "Logs" tab on the main page.

## 3. Performance Optimization
Improve system stability and inference efficiency.

### Backend – `app/config.py`
- Add `FRAME_SKIP` (number of frames to skip between YOLO inferences).
- Add `MODEL_WARMUP` (boolean to run a dummy inference on startup).

### Backend – `services/webrtc.py`
Update `HLSVideoStreamTrack` to respect the `FRAME_SKIP` setting, reducing CPU/GPU load while maintaining the WebRTC stream's visual fluidity.

## 4. Testing Infrastructure
Setup automated tests to ensure logic remains correct during future changes.

### Backend – `backend/tests/`
- Install `pytest`, `pytest-asyncio`, and `httpx`.
- Create `test_counting.py`: Mock frames and verify `LineCounter` correctly increments state.
- Create `test_api.py`: Verify endpoints return correct status codes.

### Frontend – `frontend/src/tests/`
- Install `vitest`.
- Add unit tests for `CounterCard` and `LineConfig` logic.

## 5. Documentation Refresh
Finalize the project's external documentation.

### `README.md`
- Add a Technical Architecture section with a **Mermaid.js diagram**.
- Add detailed "Running with Docker" instructions.
- Add "API Reference" table.

## 6. Execution Steps Checklist

- [ ] Create `backend/Dockerfile`.
- [ ] Create `frontend/Dockerfile` (multi-stage).
- [ ] Create `docker-compose.yml` for local orchestration.
- [ ] Implement `get_recent_events` in `repository.py` and `/events` endpoint in `main.py`.
- [ ] Build `EventsTable.tsx` and add it to the Dashboard UI.
- [ ] Add `FRAME_SKIP` logic to `HLSVideoStreamTrack`.
- [ ] Initialize `pytest` and `vitest` infrastructure.
- [ ] Write at least 2 core unit tests for counting logic.
- [ ] Update `README.md` with the Mermaid architecture diagram and Docker guide.
- [ ] Verify the entire system runs via `docker-compose up`.
