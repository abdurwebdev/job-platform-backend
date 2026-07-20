from typing import List

from app.core.logger import logger
from app.repositories.health_repository import HealthRepository
from app.scraper.result import ScrapeResult


# A source that has failed 3 runs in a row is flagged "down" even if
# today's individual run technically completed — a single bad run can
# be a blip, three in a row usually means the site changed or is
# actively blocking us.
FAILURE_THRESHOLD = 3


class HealthService:
    def __init__(self, repository: HealthRepository):
        self.repository = repository

    def record_run(self, results: List[ScrapeResult]) -> None:
        try:
            for result in results:
                self.repository.upsert_result(result)
            self.repository.commit()
        except Exception:
            self.repository.rollback()
            logger.exception("Failed to persist source health.")
            raise

    def get_health_summary(self) -> List[dict]:
        rows = self.repository.get_all()

        summary = []
        for row in rows:
            if row.consecutive_failures >= FAILURE_THRESHOLD:
                status = "down"
            elif not row.last_success:
                status = "degraded"
            else:
                status = "healthy"

            summary.append(
                {
                    "source": row.source,
                    "status": status,
                    "last_run_at": row.last_run_at,
                    "last_success": row.last_success,
                    "last_success_at": row.last_success_at,
                    "last_job_count": row.last_job_count,
                    "last_duration_ms": row.last_duration_ms,
                    "consecutive_failures": row.consecutive_failures,
                    "last_error": row.last_error,
                }
            )

        return summary
