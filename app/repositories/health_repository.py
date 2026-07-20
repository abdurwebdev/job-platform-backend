from datetime import datetime, timezone
from typing import List

from sqlalchemy.orm import Session

from app.models.source_health_model import SourceHealth
from app.scraper.result import ScrapeResult


class HealthRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_all(self) -> List[SourceHealth]:
        return self.db.query(SourceHealth).order_by(SourceHealth.source).all()

    def upsert_result(self, result: ScrapeResult) -> None:
        now = datetime.now(timezone.utc)

        row = (
            self.db.query(SourceHealth)
            .filter(SourceHealth.source == result.source)
            .first()
        )

        if row is None:
            row = SourceHealth(source=result.source, consecutive_failures=0)
            self.db.add(row)

        row.last_run_at = now
        row.last_success = result.success
        row.last_job_count = result.count
        row.last_duration_ms = result.duration_ms
        row.last_error = result.error

        if result.success:
            row.last_success_at = now
            row.consecutive_failures = 0
        else:
            row.consecutive_failures = (row.consecutive_failures or 0) + 1

    def commit(self) -> None:
        self.db.commit()

    def rollback(self) -> None:
        self.db.rollback()
