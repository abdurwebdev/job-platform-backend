from typing import Dict, List

from pydantic import BaseModel


class SaveSummarySchema(BaseModel):
    scraped: int
    inserted: int
    duplicates: int
    failed: int
    new_jobs: int


class SourceReportSchema(BaseModel):
    """
    Lightweight per-source summary — counts and status only, not the
    actual scraped jobs. The full job list already lives in the DB
    after save_jobs_to_db runs; echoing it back here made the /scrape
    response enormous (thousands of nested job objects) and crashed
    Swagger's docs renderer with a stack overflow trying to display it.
    """

    source: str
    success: bool
    count: int
    duration_ms: int
    error: str | None = None


class JobScrapeResponse(BaseModel):
    sources_run: int
    sources_succeeded: int
    sources_failed: int
    scraped_total: int
    after_dedup: int
    save_summary: SaveSummarySchema
    reports: List[SourceReportSchema]