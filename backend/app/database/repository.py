from app.database.connection import get_db

async def save_count_event(direction: str, vehicle_class: str, track_id: int, confidence: float):
    """
    Saves a vehicle crossing event to the database.
    """
    async with get_db() as db:
        await db.execute(
            """
            INSERT INTO counting_events (direction, vehicle_class, track_id, confidence)
            VALUES (?, ?, ?, ?)
            """,
            (direction, vehicle_class, track_id, confidence)
        )
        await db.commit()

async def get_total_counts():
    """
    Gets the total counts for each direction.
    """
    async with get_db() as db:
        async with db.execute(
            "SELECT direction, COUNT(*) as count FROM counting_events GROUP BY direction"
        ) as cursor:
            rows = await cursor.fetchall()
            counts = {"enter": 0, "exit": 0}
            for row in rows:
                counts[row["direction"]] = row["count"]
            return counts

async def get_hourly_stats():
    """
    Gets vehicle counts aggregated by hour for the current day.
    """
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

async def get_recent_events(limit: int = 50):
    """
    Gets the most recent vehicle crossing events.
    """
    async with get_db() as db:
        async with db.execute(
            "SELECT * FROM counting_events ORDER BY timestamp DESC LIMIT ?", (limit,)
        ) as cursor:
            rows = await cursor.fetchall()
            return [dict(row) for row in rows]
