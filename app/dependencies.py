from fastapi import Depends
from sqlalchemy.orm import Session

from app.database.database import get_db
from app.repositories.job_repository import JobRepository
from app.services.job_service import JobService


def get_job_repository(
    db: Session = Depends(get_db),
) -> JobRepository:
    return JobRepository(db)


def get_job_service(
    repository: JobRepository = Depends(get_job_repository),
) -> JobService:
    return JobService(repository)