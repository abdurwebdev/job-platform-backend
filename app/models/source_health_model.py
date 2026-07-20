from sqlalchemy import Column, String, Integer, Boolean, DateTime, Text

from app.database.database import Base


class SourceHealth(Base):
    """
    One row per scraper source. Updated every time /api/job/scrape runs.
    This is what turns "we have 50 sources" into "we have 50 sources and
    we know which ones are actually working right now" — the Week 3 ask.
    """

    __tablename__ = "source_health"

    source = Column(String, primary_key=True)

    last_run_at = Column(DateTime(timezone=True), nullable=True)
    last_success = Column(Boolean, default=False)
    last_success_at = Column(DateTime(timezone=True), nullable=True)
    last_job_count = Column(Integer, default=0)
    last_duration_ms = Column(Integer, default=0)
    last_error = Column(Text, nullable=True)
    consecutive_failures = Column(Integer, default=0)
