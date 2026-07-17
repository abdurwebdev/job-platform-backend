from app.scraper.nomads import WorkingNomadsScraper

def test_maps_basic_job():
    scraper = WorkingNomadsScraper()
    job = scraper.map_item({
        "title": "Backend Engineer",
        "url": "https://example.com/job/1",
        "company_name": "Acme",
        "category_name": "Development",
        "tags": "python, fastapi",
        "location": "Remote",
        "description": "<p>Build things</p>",
        "pub_date": "2026-07-01T10:00:00-04:00",
    })
    assert job.title == "Backend Engineer"
    assert job.tags == ["python", "fastapi"]
    assert job.description == "Build things"