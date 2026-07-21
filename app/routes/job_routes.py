from fastapi import APIRouter, Depends, Query
from typing import Optional

from app.dependencies import get_job_service, get_health_service
from app.schemas.job_schema import (
    JobDetailOverview,
    PaginatedJobsResponse,
)
from app.schemas.scrape_schema import JobScrapeResponse
from app.scraper.orchestrator import run_all_scrapers
from app.scraper.deduplicate import deduplicate_jobs
from app.services.job_service import JobService
from app.services.health_service import HealthService
from app.core.logger import logger

router = APIRouter(
    prefix="/api/job",
    tags=["Jobs"],
)


@router.post("/scrape", response_model=JobScrapeResponse)
def scrape_jobs(
    service: JobService = Depends(get_job_service),
    health_service: HealthService = Depends(get_health_service),
):
    scrape_reports = run_all_scrapers()

    # Persist per-source health (success/failure, count, duration) so
    # GET /api/health/scrapers reflects this run, not stale data.
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
        "sources_run": len(scrape_reports),
        "sources_succeeded": sum(1 for r in scrape_reports if r.success),
        "sources_failed": sum(1 for r in scrape_reports if not r.success),
        "scraped_total": before,
        "after_dedup": len(all_jobs),
        "save_summary": save_summary,
        "reports": [
            {
                "source": r.source,
                "success": r.success,
                "count": r.count,
                "duration_ms": r.duration_ms,
                "error": r.error,
            }
            for r in scrape_reports
        ],
    }


@router.get("/all", response_model=PaginatedJobsResponse)
def get_all_jobs(
    page: int = Query(1, ge=1, description="1-indexed page number"),
    limit: int = Query(20, ge=1, le=100, description="Results per page, max 100"),
    search: Optional[str] = None,
    service: JobService = Depends(get_job_service),
):
    return service.get_paginated_jobs(page, limit, search)


@router.get(
    "/job-detail/{job_id}",
    response_model=JobDetailOverview,
    responses={404: {"description": "Job not found"}},
)
def get_job_details(
    job_id: int,
    service: JobService = Depends(get_job_service),
):
    return service.get_job_details(job_id)
