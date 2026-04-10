# Phase 7: User Interface & Configuration - Technical Implementation Plan

## Objective
The goal is to enhance the system with user-facing configuration and data visualization. This includes implementing dynamic virtual line adjustment via the UI, a historical chart to view vehicle trends, and status overlays to improve the dashboard's usability.

## 1. Backend – Models and Schemas
Create Pydantic models to standardize configuration and statistics exchange.

### [NEW] `backend/app/models/schemas.py`
```python
from pydantic import BaseModel, Field
from typing import List, Dict

class LineConfig(BaseModel):
    x1: float = Field(0.0, ge=0.0, le=1.0)
    y1: float = Field(0.5, ge=0.0, le=1.0)
    x2: float = Field(1.0, ge=0.0, le=1.0)
    y2: float = Field(0.5, ge=0.0, le=1.0)

class HourlyCount(BaseModel):
    hour: str
    count: int

class StatsResponse(BaseModel):
    today_total: Dict[str, int]
    hourly_counts: List[HourlyCount]
```

## 2. Backend – Database Expansion
Update the repository to provide historical data.

### `backend/app/database/repository.py`
Add `get_hourly_stats()`:
```python
async def get_hourly_stats():
    async with get_db() as db:
        async with db.execute(
            """
            SELECT strftime('%H:00', timestamp) as hour, COUNT(*) as count 
            FROM counting_events 
            WHERE date(timestamp) = date('now')
            GROUP BY hour
            ORDER BY hour ASC
            """
        ) as cursor:
            rows = await cursor.fetchall()
            return [{"hour": row["hour"], "count": row["count"]} for row in rows]
```

## 3. Backend – Configuration API
Implement endpoints for the frontend to read and write settings.

### `backend/app/main.py`
1. **Global State**: Store `current_line_config` in memory (initialize with defaults).
2. **Endpoints**:
   - `GET /line`: Return current configuration.
   - `POST /line`: Validate with `LineConfig` model and update global state.
   - `GET /stats/hourly`: Aggregate data for the history chart.

## 4. Backend – Dynamic Line Integration
Ensure the video processing pipeline reacts to line changes without restarting the stream.

### `backend/app/services/tracker.py`
Add `update_line(coords: list)` to `LineCounter`.

### `backend/app/services/webrtc.py`
In `HLSVideoStreamTrack.recv()`, periodically check the global state for line updates and call `self._tracker.update_line()`.

## 5. Frontend – Advanced Dashboard Features

### 1. `src/components/LineConfig.tsx`
Create a panel with sliders for adjusting line height ($y1, y2$).
- Use `shadcn/ui` Slider and Label.
- "Save Config" button that calls `POST /api/line`.

### 2. `src/components/HistoryChart.tsx`
Render an area chart showing traffic volume over the day.
- Use `recharts`.
- Fetch data from `/api/stats/hourly`.

### 3. `src/lib/api.ts`
Implement typed fetch functions for the new configuration and stats endpoints.

## 6. Execution Steps Checklist

- [ ] Create `backend/app/models/schemas.py`.
- [ ] Implement `get_hourly_stats` in `repository.py`.
- [ ] Add `/line` and `/stats/hourly` endpoints to `main.py`.
- [ ] Implement dynamic line updates in `LineCounter` and `HLSVideoStreamTrack`.
- [ ] Build the `LineConfig` UI component in Next.js.
- [ ] Build the `HistoryChart` component using Recharts.
- [ ] Integrate components into `src/app/page.tsx`.
- [ ] Add connection status indicators (Status Badge).
- [ ] Verify that moving the line in the UI updates the video stream overlay instantly.
