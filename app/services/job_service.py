from typing import Dict, List

from fastapi import HTTPException
from sqlalchemy.orm import Session

from app.core.logger import logger
from app.models.job_model import Job
from app.repositories.job_repository import JobRepository
from app.scraper.schemas import StandardJob


def get_all_jobs(db: Session) -> List[Job]:
    repository = JobRepository(db)
    return repository.get_all_jobs()


def get_job_details(job_id: int, db: Session) -> Job:
    repository = JobRepository(db)

    job = repository.get_job_by_id(job_id)

    if job is None:
        raise HTTPException(
            status_code=404,
            detail="Job not found.",
        )

    return job


def save_jobs_to_db(
    jobs: List[StandardJob],
    db: Session,
) -> Dict[str, int]:

    repository = JobRepository(db)

    if not jobs:
        logger.warning("No jobs received for saving.")

        return {
            "scraped": 0,
            "inserted": 0,
            "duplicates": 0,
            "failed": 0,
            "new_jobs": 0,
        }

    inserted = 0
    duplicates = 0
    failed = 0

    try:
        existing_urls = repository.get_existing_urls()

        logger.info(
            f"Fetched {len(existing_urls)} existing job URLs."
        )

    except Exception:
        logger.exception(
            "Failed fetching existing URLs."
        )
        raise

    for job in jobs:

        if not job.url:
            failed += 1

            logger.warning(
                f"Skipping job without URL: {job.title}"
            )

            continue

        if job.url in existing_urls:
            duplicates += 1

            logger.info(
                f"Duplicate skipped: {job.title}"
            )

            continue

        try:

            with repository.begin_nested():

                new_job = Job(
                    title=job.title,
                    url=job.url,
                    company_name=job.company_name,
                    company_logo=job.company_logo,
                    category=job.category,
                    tags=job.tags,
                    job_type=job.job_type,
                    publication_date=job.publication_date,
                    salary=job.salary,
                    candidate_required_location=job.candidate_required_location,
                    description=job.description,
                    source=job.source,
                )

                repository.add_job(new_job)

                repository.flush()

            existing_urls.add(job.url)

            inserted += 1

        except Exception:

            failed += 1

            logger.exception(
                f"Failed inserting job: {job.title}"
            )

    try:

        repository.commit()

        logger.info(
            f"Successfully inserted {inserted} jobs."
        )

    except Exception:

        repository.rollback()

        logger.exception(
            "Database commit failed."
        )

        raise

    return {
        "scraped": len(jobs),
        "inserted": inserted,
        "duplicates": duplicates,
        "failed": failed,
        "new_jobs": inserted,
    }