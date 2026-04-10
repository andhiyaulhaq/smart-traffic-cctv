from pydantic import BaseModel, Field
from typing import List, Dict, Optional

class LineConfig(BaseModel):
    x1: float = Field(0.0, ge=0.0, le=1.0)
    y1: float = Field(0.5, ge=0.0, le=1.0)
    x2: float = Field(1.0, ge=0.0, le=1.0)
    y2: float = Field(0.5, ge=0.0, le=1.0)

class HourlyCount(BaseModel):
    hour: str
    count: int

class StatsResponse(BaseModel):
    enter: int
    exit: int
    hourly_counts: List[HourlyCount]
