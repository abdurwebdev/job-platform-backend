from app.scraper.schemas import StandardJob


def build_job(
    *,
    title,
    url,
    company_name,
    source,
    company_logo=None,
    category="General",
    tags=None,
    job_type="Full-time",
    publication_date=None,
    salary="Undisclosed",
    candidate_required_location="Remote",
    description="",
    remote=False,
    location=None,
    external_id=None,
):
    return StandardJob(
        title=title,
        url=url,
        company_name=company_name,
        company_logo=company_logo,
        category=category,
        tags=tags or [],
        job_type=job_type,
        publication_date=publication_date,
        salary=salary,
        candidate_required_location=candidate_required_location,
        description=description,
        source=source,
        remote=remote,
        location=location,
        external_id=external_id,
    )