from app.scraper.lever import LeverScraper


def test_maps_basic_job():
    scraper = LeverScraper(company_slug="leverdemo", company_name="Lever Demo")

    job = scraper.map_item({
        "id": "abc-123",
        "text": "Senior Backend Engineer",
        "hostedUrl": "https://jobs.lever.co/leverdemo/abc-123",
        "categories": {
            "location": "Remote - US",
            "team": "Engineering",
            "commitment": "Full-time",
        },
        "workplaceType": "remote",
        "createdAt": 1750000000000,
        "description": "<p>Build things at scale</p>",
    })

    assert job.title == "Senior Backend Engineer"
    assert job.company_name == "Lever Demo"
    assert job.source == "Lever:leverdemo"
    assert job.category == "Engineering"
    assert job.candidate_required_location == "Remote - US"
    assert "Build things at scale" in job.description


def test_handles_missing_categories():
    scraper = LeverScraper(company_slug="acme")

    job = scraper.map_item({
        "id": "1",
        "text": "Intern",
        "hostedUrl": "https://jobs.lever.co/acme/1",
        "categories": {},
        "description": "",
    })

    assert job.company_name == "Acme"
    assert job.category == "General"
    assert job.candidate_required_location == "Remote"
