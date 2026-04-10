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
