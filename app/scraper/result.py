from pydantic import BaseModel
from typing import List, Optional
from app.scraper.schemas import StandardJob

class ScrapeResult(BaseModel):
    source: str
    jobs: List[StandardJob]
    count: int
    success: bool
    error: Optional[str] = None
    duration_ms: int