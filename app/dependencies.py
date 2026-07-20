from fastapi import Depends
from sqlalchemy.orm import Session

from app.database.database import get_db
from app.repositories.job_repository import JobRepository
from app.repositories.health_repository import HealthRepository
from app.services.job_service import JobService
from app.services.health_service import HealthService


def get_job_repository(
    db: Session = Depends(get_db),
) -> JobRepository:
    return JobRepository(db)


def get_job_service(
    repository: JobRepository = Depends(get_job_repository),
) -> JobService:
    return JobService(repository)


def get_health_repository(
    db: Session = Depends(get_db),
) -> HealthRepository:
    return HealthRepository(db)


def get_health_service(
    repository: HealthRepository = Depends(get_health_repository),
) -> HealthService:
    return HealthService(repository)