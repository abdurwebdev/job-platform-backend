from app.scraper.greenhouse import GreenhouseScraper


def test_maps_basic_job():
    scraper = GreenhouseScraper(board_token="anthropic", company_name="Anthropic")

    job = scraper.map_item({
        "id": 123456,
        "title": "Research Engineer",
        "updated_at": "2026-07-15T08:00:00Z",
        "location": {"name": "San Francisco, CA"},
        "absolute_url": "https://boards.greenhouse.io/anthropic/jobs/123456",
        "content": "<p>Work on frontier models</p>",
        "metadata": [
            {"id": 1, "name": "Department", "value": "Research"}
        ],
    })

    assert job.title == "Research Engineer"
    assert job.company_name == "Anthropic"
    assert job.source == "Greenhouse:anthropic"
    assert job.category == "Research"
    assert job.external_id == "123456"
    assert "Work on frontier models" in job.description


def test_handles_missing_location_and_metadata():
    scraper = GreenhouseScraper(board_token="acme")

    job = scraper.map_item({
        "id": 1,
        "title": "Intern",
        "absolute_url": "https://boards.greenhouse.io/acme/jobs/1",
        "content": "",
    })

    assert job.company_name == "Acme"
    assert job.candidate_required_location == "Remote"
    assert job.category == "General"
