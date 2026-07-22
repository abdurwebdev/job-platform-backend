from typing import List, Optional
from sqlalchemy.dialects.postgresql import insert as pg_insert
from sqlalchemy import func, cast, BigInteger
from sqlalchemy.orm import Session

from app.models.job_model import Job


class JobRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_all_jobs(self) -> List[Job]:
        return self.db.query(Job).all()

    def get_job_by_id(self, job_id: int) -> Optional[Job]:
        return self.db.query(Job).filter(Job.id == job_id).first()

    def get_existing_urls(self) -> set[str]:
        return {url for (url,) in self.db.query(Job.url).all()}

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

    def _filtered_query(
        self,
        search: Optional[str] = None,
        category: Optional[str] = None,
        job_type: Optional[str] = None,
        location: Optional[str] = None,
    ):
        query = self.db.query(Job)

        if search:
            query = query.filter(Job.title.ilike(f"%{search}%"))

        # Case-insensitive exact match: the frontend sends dropdown values,
        # not free text, so ilike-with-wildcards isn't the right tool here.
        if category:
            query = query.filter(func.lower(Job.category) == category.lower())

        if job_type:
            query = query.filter(func.lower(Job.job_type) == job_type.lower())

        # Location stays a "contains" match since values like "Remote" vs
        # "Remote - US" vs "Worldwide" don't line up as clean exact matches.
        if location:
            query = query.filter(Job.candidate_required_location.ilike(f"%{location}%"))

        return query

    def _sorted_query(self, query, sort: Optional[str]):
        if sort == "alphabetical":
            return query.order_by(Job.title.asc())

        if sort == "salary":
            # Salary is free-text ("$90k-$120k", "Not specified", "DOE", ...),
            # not a number, so this is a best-effort sort: strip everything
            # but digits and order by that. A range like "90000-120000"
            # becomes "90000120000" (digits concatenated), so it's not a
            # precise numeric ranking — but it's stable and roughly groups
            # higher numbers together, which is enough for a filter dropdown.
            numeric_salary = func.nullif(
                func.regexp_replace(Job.salary, "[^0-9]", "", "g"), ""
            )
            return query.order_by(cast(numeric_salary, BigInteger).desc().nullslast())

        # default: newest first
        return query.order_by(Job.publication_date.desc().nullslast())

    def get_paginated_jobs(
        self,
        skip: int,
        limit: int,
        search: Optional[str] = None,
        category: Optional[str] = None,
        job_type: Optional[str] = None,
        location: Optional[str] = None,
        sort: Optional[str] = None,
    ):
        query = self._filtered_query(search, category, job_type, location)
        query = self._sorted_query(query, sort)
        return query.offset(skip).limit(limit).all()

    def count_jobs(
        self,
        search: Optional[str] = None,
        category: Optional[str] = None,
        job_type: Optional[str] = None,
        location: Optional[str] = None,
    ) -> int:
        return self._filtered_query(search, category, job_type, location).count()

    def bulk_upsert_jobs(self, job_dicts: List[dict]) -> int:
        """Insert all rows in one statement, skip rows whose url already exists.
        Returns the number of rows actually inserted."""
        if not job_dicts:
            return 0

        stmt = pg_insert(Job).values(job_dicts)
        stmt = stmt.on_conflict_do_nothing(index_elements=["url"])
        result = self.db.execute(stmt)
        return result.rowcount
