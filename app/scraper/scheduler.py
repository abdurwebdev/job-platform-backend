"""
Runs scraping on a schedule from inside the running container, instead of
relying on GitHub Actions to hit POST /api/job/scrape from outside.

Why a plain threading.Thread instead of a library like APScheduler or
Celery: the container is now a single long-running process (not
serverless), the scrape job itself is synchronous code (requests/httpx
calls, not async), and we only need "run this every N hours" — not cron
expressions, retries, or distributed workers. A daemon thread with a sleep
loop is the smallest thing that correctly does that job. If requirements
grow (multiple jobs, distributed workers, missed-run recovery), APScheduler
or a real task queue would be the next step up — this is intentionally not
that, yet.
"""

import threading
import time

from app.config.config import settings
from app.core.logger import logger
from app.database.database import SessionLocal
from app.repositories.job_repository import JobRepository
from app.repositories.health_repository import HealthRepository
from app.services.job_service import JobService
from app.services.health_service import HealthService
from app.scraper.orchestrator import run_and_save_jobs
from app.scraper.registry import SCRAPERS

# How long to wait after container startup before the first scrape, so a
# fresh deploy doesn't immediately hammer every source while the app is
# still finishing its own startup checks.
STARTUP_DELAY_SECONDS = 60


def _run_one_cycle() -> None:
    """One full scrape-and-save run, with its own DB session.

    This builds its own JobService/HealthService rather than reusing
    FastAPI's Depends()-based ones, because those only exist for the
    lifetime of an HTTP request — there's no request here, just a
    background thread, so we open a session, use it, and close it
    ourselves (mirrors what get_db() does per-request).
    """
    db = SessionLocal()
    try:
        service = JobService(JobRepository(db))
        health_service = HealthService(HealthRepository(db))
        result = run_and_save_jobs(SCRAPERS, service, health_service)
        logger.info(
            "Scheduled scrape complete: "
            f"{result['save_summary']}"
        )
    except Exception:
        # Never let one bad run kill the loop — log it and try again
        # next interval.
        logger.exception("Scheduled scrape run failed.")
    finally:
        db.close()


def _scheduler_loop() -> None:
    time.sleep(STARTUP_DELAY_SECONDS)

    interval_seconds = settings.scrape_interval_hours * 3600

    while True:
        logger.info("Scheduler: starting scrape run.")
        _run_one_cycle()
        logger.info(
            f"Scheduler: sleeping {settings.scrape_interval_hours}h until next run."
        )
        time.sleep(interval_seconds)


def start_scheduler() -> None:
    """Call once from the app's startup (lifespan). No-op if disabled."""
    if not settings.scheduler_enabled:
        logger.info("Scheduler disabled (SCHEDULER_ENABLED=false) — skipping.")
        return

    thread = threading.Thread(target=_scheduler_loop, daemon=True)
    thread.start()
    logger.info(
        f"Scheduler started: scraping every {settings.scrape_interval_hours}h, "
        f"first run in {STARTUP_DELAY_SECONDS}s."
    )
