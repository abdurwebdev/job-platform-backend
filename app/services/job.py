from typing import Any, Dict, List, Sequence
from fastapi import HTTPException
from sqlalchemy.orm import Session

from app.core.logger import logger
from app.models.job import Job


def get_alljobs(db: Session) -> Sequence[Job]:
    """Fetches all jobs from the database."""
    jobs = db.query(Job).all()
    if not jobs:
        return []
    return jobs
    
  
def save_jobs_to_db(jobs: List[Any], db: Session) -> Dict[str, int]:
    """Saves a batch of raw scraped jobs into the database while ignoring duplicates.
    
    Uses savepoints to track failures per-job accurately without rolling back the whole batch.
    """
    inserted = 0
    duplicates = 0
    failed = 0
    
    if not jobs:
        logger.warning("No jobs provided to save_jobs_to_db.")
        return {"scrapped": 0, "inserted": 0, "duplicates": 0, "failed": 0, "new_jobs": 0}
        
    try:
        logger.info(f"Running {jobs[0].source} Scrapper....")
        logger.info(f"Fetched {len(jobs)} Jobs.....")
        
        # Pull down existing URLs to optimize duplicate checking locally
        existing_urls = {
            url for (url,) in db.query(Job.url).all()
        }
    except Exception:
        logger.exception("Fatal error: Failed to fetch existing job URLs from database.")
        raise

    for job in jobs:
        if job.url in existing_urls:
            duplicates += 1
            logger.info(f"Duplicate Job Skipped {job.title}")
            continue
            
        # 1. Establish a savepoint for this individual job
        db.begin_nested() 
        try:
            new_job = Job(
                title=job.title,
                company_name=job.company_name,
                url=job.url,
                category=job.category,
                tags=job.tags,
                job_type=job.job_type,
                publication_date=job.publication_date,
                candidate_required_location=job.candidate_required_location,
                salary=job.salary,
                description=job.description,
                source=job.source
            )
            db.add(new_job)
            db.flush()  # 2. Force SQLAlchemy to check constraints/errors immediately
            inserted += 1
        except Exception:
            db.rollback()  # 3. Roll back ONLY this single bad job
            failed += 1
            logger.exception(f"Failed to insert individual job: {job.title}")

    # 4. Commit all successful insertions safely at the end
    try:
        db.commit()
        logger.info(f"Inserted {inserted} Jobs.....")
        logger.info(f"{jobs[0].source} scrape completed successfully.")
    except Exception:
        db.rollback()
        logger.exception("Fatal error committing the scraping batch transaction.")
        raise
        
    return {
        "scrapped": len(jobs),
        "inserted": inserted,
        "duplicates": duplicates,
        "failed": failed,
        "new_jobs": inserted
    }


def showdetails(job_id: Any, db: Session) -> Job:
    """Retrieves a single job by its ID or raises a 404 error if not found."""
    isexists = db.query(Job).filter(Job.id == job_id).first()
    if not isexists:
        raise HTTPException(
            status_code=404,
            detail="Job not found!"
        )
    return isexists