from typing import List, Optional

from sqlalchemy.orm import Session

from app.models.job_model import Job


class JobRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_all_jobs(self) -> List[Job]:
        return self.db.query(Job).all()

    def get_job_by_id(self, job_id: int) -> Optional[Job]:
        return (
            self.db.query(Job)
            .filter(Job.id == job_id)
            .first()
        )

    def get_existing_urls(self) -> set[str]:
        return {
            url
            for (url,) in self.db.query(Job.url).all()
        }

    def add_job(self, job: Job) -> None:
        self.db.add(job)

    def flush(self) -> None:
        self.db.flush()

    def commit(self) -> None:
        self.db.commit()

    def rollback(self) -> None:
        self.db.rollback()

    def begin_nested(self):
        return self.db.begin_nested()
    
    def get_paginated_jobs(self, skip: int, limit: int, search: Optional[str] = None):
        
        
        query = self.db.query(Job)
        if search:
            
            query = query.filter(Job.title.ilike(f"%{search}%"))
        return query.offset(skip).limit(limit).all()

    def count_jobs(self, search: Optional[str] = None) -> int:
        
        
        
        query = self.db.query(Job)
        if search:
            
            
            query = query.filter(Job.title.ilike(f"%{search}%"))
        return query.count()