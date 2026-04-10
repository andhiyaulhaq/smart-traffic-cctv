# Smart Traffic CCTV

A real-time vehicle counting system that ingests a live CCTV HLS stream, detects and tracks vehicles, counts crossings over a virtual line, and displays the results in a modern web dashboard. 

## Overview
This project showcases real-time computer vision capabilities integrated with a modern web stack. It uses YOLOv8 and ByteTrack to reliably identify, track, and count vehicles parsing a live feed, and presents it in a real-time dashboard powered by WebRTC.

### Tech Stack
*   **Backend Support**: FastAPI (Python), utilizing `uv` for package management.
*   **Object Detection & Tracking**: YOLOv8 + ByteTrack.
*   **Database**: SQLite.
*   **Real-time Streaming**: WebRTC via `aiortc` (Backend) and `simple-peer` (Frontend). 
*   **Frontend**: Next.js (App Router), styled with Tailwind CSS and `shadcn/ui`, utilizing `pnpm`.

## Project Structure
*   `/backend` - Provides API endpoints (REST & WebSockets) and handles computer vision tasks (processing the live feed via OpenCV).
*   `/frontend` - Contains the Next.js React application driving the dashboard UI.
*   `/docs` - Project documentation, planning, and design.

## How to Run

The system requires running both the backend server and the frontend development server concurrently. 

### Prerequisites
*   Node.js and `pnpm` installed.
*   Python 3.11+ and `uv` installed.

### 1. Start the Backend (FastAPI)

Open a new terminal session and navigate to the `backend` directory:

```bash
cd backend
# Run the FastAPI server via uvicorn wrapper
uv run uvicorn app.main:app --reload --port 8000
```
The backend API will be accessible at `http://localhost:8000`.

### 2. Start the Frontend (Next.js)

Open a second terminal session and navigate to the `frontend` directory:

```bash
cd frontend
# Install dependencies if this is your first time:
# pnpm install
# Start the development server
pnpm dev --port 3000
```
The frontend dashboard will be accessible at `http://localhost:3000`.

*Note: The frontend is configured to proxy API requests prefixed with `/api` directly to the backend running on port 8000.*

---
**Status**: Currently in Phase 0 (Project Scaffolding complete; baseline connection established).
