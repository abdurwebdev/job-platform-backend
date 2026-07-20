from fastapi import APIRouter, Depends, Response
from typing import Optional

from app.dependencies import get_job_service, get_health_service
from app.schemas.job_schema import (
    JobDetailOverview,
    JobUIOverviewSchema,
)
from app.scraper.orchestrator import run_all_scrapers
from app.scraper.deduplicate import deduplicate_jobs
from app.services.job_service import JobService
from app.services.health_service import HealthService
from app.core.logger import logger
from app.schemas.job_schema import PaginatedJobsResponse

router = APIRouter(
    prefix="/api/job",
    tags=["Jobs"],
)


@router.post("/scrape")
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
        "reports": scrape_reports,
    }


# routes/job_routes.py
@router.get("/all", response_model=PaginatedJobsResponse)
def get_all_jobs(
    page: int = 1,
    limit: int = 20,
    search: Optional[str] = None,  # also: use Optional[str], not bare str
    service: JobService = Depends(get_job_service),
):
    skip = (page - 1) * limit
    jobs = service.repository.get_paginated_jobs(skip, limit, search)
    total = service.repository.count_jobs(search)
    return {"jobs": jobs, "total": total, "page": page, "limit": limit}


@router.get(
    "/job-detail/{jobId}",
    response_model=JobDetailOverview,
)
def get_job_details(
    jobId: int,
    service: JobService = Depends(get_job_service),
):
    return service.get_job_details(jobId)
