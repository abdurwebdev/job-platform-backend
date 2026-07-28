import time
from app.core.logger import logger
from app.scraper.registry import SCRAPERS
from app.scraper.result import ScrapeResult
from app.scraper.schemas import StandardJob
from app.scraper.deduplicate import deduplicate_jobs
from typing import List, Optional


def run_scrapers(scraper_classes: List) -> List[ScrapeResult]:
    """Run an arbitrary subset of scrapers (a "batch"). This is what makes
    it possible to run 51 sources across several short calls instead of
    one long call that times out on a serverless platform."""
    all_scrape_results: List[ScrapeResult] = []

    for scraper_class in scraper_classes:
        scraper = scraper_class()
        start_time = time.perf_counter()

        try:
            logger.info(f"--- Running {scraper.source_name} ---")
            jobs = scraper.scrape()

            # Calculate duration
            duration = int((time.perf_counter() - start_time) * 1000)

            # Store success result
            all_scrape_results.append(
                ScrapeResult(
                    source=scraper.source_name,
                    jobs=jobs,
                    count=len(jobs),
                    success=True,
                    duration_ms=duration,
                )
            )
            logger.info(f"{scraper.source_name} completed " f"jobs={len(jobs)}")

        except Exception as e:
            duration = int((time.perf_counter() - start_time) * 1000)
            logger.exception(f"{scraper.source_name} failed.")

            # Store failure result
            all_scrape_results.append(
                ScrapeResult(
                    source=scraper.source_name,
                    jobs=[],
                    count=0,
                    success=False,
                    error=str(e),
                    duration_ms=duration,
                )
            )

    # Optional: Log summary of failures
    failed = [r.source for r in all_scrape_results if not r.success]
    if failed:
        logger.warning(f"Failed scrapers: {', '.join(failed)}")

    return all_scrape_results


def run_all_scrapers() -> List[ScrapeResult]:
    """Kept for backwards compatibility / local dev. Runs every source in
    one call — fine locally, but on Vercel this is the call that times out.
    Prefer run_scrapers(batch) via the /api/job/scrape?batch_index=... route."""
    return run_scrapers(SCRAPERS)


def run_and_save_jobs(
    scraper_classes: List,
    service,
    health_service,
) -> dict:
    """The full pipeline: run scrapers -> record source health -> dedupe
    across sources -> save to the DB. Both POST /api/job/scrape and the
    in-container scheduler (app/scraper/scheduler.py) call this, so there's
    exactly one place that defines "what a scrape run does" instead of two
    copies that can drift apart.

    `service` and `health_service` are passed in rather than imported,
    because the HTTP route gets them via FastAPI's Depends() (one DB
    session per request), while the scheduler builds its own short-lived
    session per run — same interface (JobService/HealthService), different
    session lifetime.
    """
    scrape_reports = run_scrapers(scraper_classes)

    try:
        health_service.record_run(scrape_reports)
    except Exception:
        logger.exception("Failed to record source health; continuing with save.")

    all_jobs = []
    for report in scrape_reports:
        all_jobs.extend(report.jobs)

    before = len(all_jobs)
    all_jobs = deduplicate_jobs(all_jobs)
    logger.info(
        f"Cross-source dedup: {before} scraped -> {len(all_jobs)} unique "
        f"({before - len(all_jobs)} duplicates removed)"
    )

    save_summary = service.save_jobs_to_db(all_jobs)

    return {
        "scrape_reports": scrape_reports,
        "total_sources": len(scraper_classes),
        "save_summary": save_summary,
    }