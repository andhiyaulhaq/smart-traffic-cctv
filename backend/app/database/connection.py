import aiosqlite
import os
from contextlib import asynccontextmanager

DB_PATH = "traffic.db"
SCHEMA_PATH = os.path.join(os.path.dirname(__file__), "queries.sql")

@asynccontextmanager
async def get_db():
    # Connect to the database
    db = await aiosqlite.connect(DB_PATH)
    try:
        # Enable dictionary-like access to rows
        db.row_factory = aiosqlite.Row
        yield db
    finally:
        await db.close()

async def init_db():
    """Initializes the database with the schema if it doesn't exist."""
    async with get_db() as db:
        with open(SCHEMA_PATH, "r") as f:
            schema = f.read()
        await db.executescript(schema)
        await db.commit()
    print(f"Database initialized at {DB_PATH}")
