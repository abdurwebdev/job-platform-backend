from typing import Dict, List, Optional
import time

from fastapi import HTTPException

from app.core.logger import logger
from app.models.job_model import Job
from app.repositories.job_repository import JobRepository
from app.scraper.schemas import StandardJob


class JobService:
    def __init__(self, repository: JobRepository):
        self.repository = repository

    def get_all_jobs(self) -> List[Job]:
        return self.repository.get_all_jobs()

    def get_paginated_jobs(
        self,
        page: int,
        limit: int,
        search: Optional[str] = None,
        category: Optional[str] = None,
        job_type: Optional[str] = None,
        location: Optional[str] = None,
        sort: Optional[str] = None,
    ) -> Dict:
        skip = (page - 1) * limit

        jobs = self.repository.get_paginated_jobs(
            skip,
            limit,
            search=search,
            category=category,
            job_type=job_type,
            location=location,
            sort=sort,
        )

        total = self.repository.count_jobs(
            search=search,
            category=category,
            job_type=job_type,
            location=location,
        )

        return {
            "jobs": jobs,
            "total": total,
            "page": page,
            "limit": limit,
        }

    def get_job_details(self, job_id: int) -> Job:
        job = self.repository.get_job_by_id(job_id)

        if job is None:
            raise HTTPException(
                status_code=404,
                detail="Job not found.",
            )

        return job

    def save_jobs_to_db(self, jobs: List[StandardJob]) -> Dict[str, int]:
        start = time.perf_counter()

        if not jobs:
            logger.warning("No jobs received for saving.")
            return {
                "scraped": 0,
                "inserted": 0,
                "duplicates": 0,
                "failed": 0,
                "new_jobs": 0,
            }

        failed = 0
        rows = []

        for job in jobs:
            if not job.url:
                failed += 1
                logger.warning(f"Skipping job without URL: {job.title}")
                continue

            rows.append(
                {
                    "title": job.title,
                    "url": job.url,
                    "company_name": job.company_name,
                    "company_logo": job.company_logo,
                    "category": job.category,
                    "tags": job.tags,
                    "job_type": job.job_type,
                    "publication_date": job.publication_date,
                    "salary": job.salary,
                    "candidate_required_location": job.candidate_required_location,
                    "description": job.description,
                    "source": job.source,
                }
            )

        try:
            inserted = self.repository.bulk_upsert_jobs(rows)
            self.repository.commit()
        except Exception:
            self.repository.rollback()
            logger.exception("Bulk job insert failed.")
            raise

        duplicates = len(rows) - inserted
        elapsed = time.perf_counter() - start

        logger.info(
            f"Job save completed in {elapsed:.2f}s | "
            f"scraped={len(jobs)} inserted={inserted} "
            f"duplicates={duplicates} failed={failed}"
        )

        return {
            "scraped": len(jobs),
            "inserted": inserted,
            "duplicates": duplicates,
            "failed": failed,
            "new_jobs": inserted,
        }