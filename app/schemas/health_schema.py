from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel


class SourceHealthSchema(BaseModel):
    source: str
    status: str  # "healthy" | "degraded" | "down"
    last_run_at: Optional[datetime] = None
    last_success: bool
    last_success_at: Optional[datetime] = None
    last_job_count: int
    last_duration_ms: int
    consecutive_failures: int
    last_error: Optional[str] = None


class HealthSummarySchema(BaseModel):
    total_sources: int
    healthy: int
    degraded: int
    down: int
    sources: List[SourceHealthSchema]
