from fastapi import APIRouter, Depends, Response
from typing import Optional

from app.dependencies import get_job_service
from app.schemas.job_schema import (
    JobDetailOverview,
    JobUIOverviewSchema,
)
from app.scraper.orchestrator import run_all_scrapers
from app.services.job_service import JobService
from app.core.logger import logger
from app.schemas.job_schema import PaginatedJobsResponse

router = APIRouter(
    prefix="/api/job",
    tags=["Jobs"],
)


@router.post("/scrape")
def scrape_jobs(
    service: JobService = Depends(get_job_service),
):
    scrape_reports = run_all_scrapers()

    all_jobs = []

    for report in scrape_reports:
        all_jobs.extend(report.jobs)

    service.save_jobs_to_db(all_jobs)

    return scrape_reports


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
