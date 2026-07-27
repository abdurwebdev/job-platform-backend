import math
from fastapi import APIRouter, Depends, Response, Query, Header, HTTPException
from typing import Optional

from app.dependencies import get_job_service, get_health_service
from app.schemas.job_schema import JobDetailOverview
from app.scraper.orchestrator import run_scrapers
from app.scraper.registry import SCRAPERS
from app.scraper.deduplicate import deduplicate_jobs
from app.services.job_service import JobService
from app.services.health_service import HealthService
from app.core.logger import logger
from app.schemas.job_schema import PaginatedJobsResponse
from app.config.config import settings

router = APIRouter(
    prefix="/api/job",
    tags=["Jobs"],
)


def _check_scrape_secret(x_scrape_secret: Optional[str]) -> None:
    """If SCRAPE_SECRET is configured, require callers to send it."""
    if settings.scrape_secret and x_scrape_secret != settings.scrape_secret:
        raise HTTPException(
            status_code=401, detail="Missing or invalid X-Scrape-Secret header."
        )


@router.get("/scrape/meta")
def scrape_meta(batch_size: int = Query(6, ge=1)):
    total_sources = len(SCRAPERS)
    return {
        "total_sources": total_sources,
        "batch_size": batch_size,
        "total_batches": math.ceil(total_sources / batch_size),
    }


@router.post("/scrape")
def scrape_jobs(
    batch_index: Optional[int] = Query(
        None,
        ge=0,
        description="0-based batch to run. Omit to run ALL sources in one call.",
    ),
    batch_size: Optional[int] = Query(
        None, ge=1, description="Sources per batch. Required if batch_index is set."
    ),
    x_scrape_secret: Optional[str] = Header(None, alias="X-Scrape-Secret"),
    service: JobService = Depends(get_job_service),
    health_service: HealthService = Depends(get_health_service),
):
    _check_scrape_secret(x_scrape_secret)

    if batch_index is not None:
        if batch_size is None:
            raise HTTPException(
                status_code=400,
                detail="batch_size is required when batch_index is given.",
            )
        start = batch_index * batch_size
        end = start + batch_size
        scrapers_to_run = SCRAPERS[start:end]

        if not scrapers_to_run:
            return {
                "batch_index": batch_index,
                "batch_size": batch_size,
                "total_sources": len(SCRAPERS),
                "total_batches": math.ceil(len(SCRAPERS) / batch_size),
                "sources_run": 0,
                "message": "batch_index out of range — nothing to run.",
            }
    else:
        scrapers_to_run = SCRAPERS

    try:
        scrape_reports = run_scrapers(scrapers_to_run)
    except Exception as e:
        logger.critical(f"Scraper orchestration failed: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Scraping failed: {str(e)}")

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
        "batch_index": batch_index,
        "batch_size": batch_size,
        "total_sources": len(SCRAPERS),
        "sources_run": len(scrape_reports),
        "sources_succeeded": sum(1 for r in scrape_reports if r.success),
        "sources_failed": sum(1 for r in scrape_reports if not r.success),
        "scraped_total": before,
        "after_dedup": len(all_jobs),
        "save_summary": save_summary,
        "reports": scrape_reports,
    }


@router.get("/all", response_model=PaginatedJobsResponse)
def get_all_jobs(
    page: int = 1,
    limit: int = 20,
    search: Optional[str] = None,
    category: Optional[str] = None,
    location: Optional[str] = None,
    sort: Optional[str] = None,
    job_type: Optional[str] = Query(None, alias="type"),
    service: JobService = Depends(get_job_service),
):
    return service.get_paginated_jobs(
        page=page,
        limit=limit,
        search=search,
        category=category,
        job_type=job_type,
        location=location,
        sort=sort,
    )

@router.get(
    "/job-detail/{jobId}",
    response_model=JobDetailOverview,
)
def get_job_details(
    jobId: int,
    service: JobService = Depends(get_job_service),
):
    return service.get_job_details(jobId)
