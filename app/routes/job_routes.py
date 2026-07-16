from fastapi import APIRouter, Depends, Response

from app.dependencies import get_job_service
from app.schemas.job_schema import (
    JobDetailOverview,
    JobUIOverviewSchema,
)
from app.scraper.orchestrator import run_all_scrapers
from app.services.job_service import JobService
from app.core.logger import logger


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


@router.get(
    "/all",
    response_model=list[JobUIOverviewSchema],
)
def get_all_jobs(
    response: Response,
    service: JobService = Depends(get_job_service),
):
    logger.info("Fetching all Jobs")
    response.headers["Cache-Control"] = "no-store, no-cache, must-revalidate, max-age=0"
    response.headers["Pragma"] = "no-cache"

    return service.get_all_jobs()


@router.get(
    "/job-detail/{jobId}",
    response_model=JobDetailOverview,
)
def get_job_details(
    jobId: int,
    service: JobService = Depends(get_job_service),
):
    return service.get_job_details(jobId)
