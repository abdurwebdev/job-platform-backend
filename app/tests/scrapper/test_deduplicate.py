from app.scraper.deduplicate import deduplicate_jobs
from app.scraper.schemas import StandardJob


def _job(**overrides):
    defaults = dict(
        title="Backend Engineer",
        url="https://example.com/1",
        company_name="Acme",
        category="Eng",
        job_type="Full-time",
        candidate_required_location="Remote",
        description="desc",
        source="TestSource",
    )
    defaults.update(overrides)
    return StandardJob(**defaults)


def test_removes_exact_url_duplicates():
    jobs = [_job(url="https://a.com/1"), _job(url="https://a.com/1")]
    result = deduplicate_jobs(jobs)
    assert len(result) == 1


def test_removes_cross_source_duplicates_by_title_and_company():
    jobs = [
        _job(url="https://a.com/1", company_name="Acme Inc.", title="Backend Engineer", source="A"),
        _job(url="https://b.com/2", company_name="Acme", title="Backend Engineer (Remote)", source="B"),
    ]
    result = deduplicate_jobs(jobs)
    assert len(result) == 1
    assert result[0].source == "A"  # keeps first occurrence


def test_keeps_genuinely_different_jobs():
    jobs = [
        _job(url="https://a.com/1", title="Backend Engineer", company_name="Acme"),
        _job(url="https://a.com/2", title="Frontend Engineer", company_name="Acme"),
        _job(url="https://b.com/1", title="Backend Engineer", company_name="OtherCo"),
    ]
    result = deduplicate_jobs(jobs)
    assert len(result) == 3
