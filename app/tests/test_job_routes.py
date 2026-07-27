"""
Tests for GET /api/job/all — search, filters, sort, pagination.

These test the route in isolation: we mount just job_router on a bare
FastAPI() app and override get_job_service with a fake that records the
kwargs it was called with. No real database required.

Assumed contract (matches JobService.get_paginated_jobs's existing
signature):
    route reads query params page, limit, search, category, location,
    sort, and the query key `type` (that's what JobsGridClient sends),
    then calls:
        service.get_paginated_jobs(
            page=..., limit=..., search=..., category=...,
            job_type=..., location=..., sort=...,
        )

If your route wires things up differently, the failing test names below
tell you exactly which piece of the contract is off.
"""

from datetime import datetime, timezone
from typing import Optional

from fastapi import FastAPI
from fastapi.testclient import TestClient

from app.dependencies import get_job_service
from app.routes.job_routes import router as job_router


def _job_dict(**overrides):
    defaults = dict(
        id=1,
        title="Backend Engineer",
        url="https://example.com/jobs/1",
        company_name="Acme",
        company_logo=None,
        category="Engineering",
        tags=["python", "fastapi"],
        job_type="Full-time",
        publication_date=datetime.now(timezone.utc).isoformat(),
        salary="$100k",
        candidate_required_location="Remote",
        source="RemoteOK",
    )
    defaults.update(overrides)
    return defaults


class FakeJobService:
    """Stands in for JobService. Records every call, returns canned data."""

    def __init__(self, jobs=None, total=None):
        self.jobs = jobs if jobs is not None else [_job_dict()]
        self.total = total if total is not None else len(self.jobs)
        self.calls = []

    def get_paginated_jobs(
        self,
        page: int,
        limit: int,
        search: Optional[str] = None,
        category: Optional[str] = None,
        job_type: Optional[str] = None,
        location: Optional[str] = None,
        sort: Optional[str] = None,
    ):
        self.calls.append(
            dict(
                page=page,
                limit=limit,
                search=search,
                category=category,
                job_type=job_type,
                location=location,
                sort=sort,
            )
        )
        return {
            "jobs": self.jobs,
            "total": self.total,
            "page": page,
            "limit": limit,
        }


def _client(fake_service):
    app = FastAPI()
    app.include_router(job_router)
    app.dependency_overrides[get_job_service] = lambda: fake_service
    return TestClient(app)


def test_defaults_to_page_1_limit_20():
    fake = FakeJobService()
    client = _client(fake)

    res = client.get("/api/job/all")

    assert res.status_code == 200
    assert fake.calls[0]["page"] == 1
    assert fake.calls[0]["limit"] == 20


def test_passes_search_through():
    fake = FakeJobService()
    client = _client(fake)

    client.get("/api/job/all", params={"search": "backend"})

    assert fake.calls[0]["search"] == "backend"


def test_maps_query_key_type_to_job_type():
    """The frontend (JobsGridClient) sends `type`, not `job_type`, in the
    query string. If this fails, filtering by job type is silently broken
    for every user even though the service layer supports it."""
    fake = FakeJobService()
    client = _client(fake)

    client.get("/api/job/all", params={"type": "Full-time"})

    assert fake.calls[0]["job_type"] == "Full-time"


def test_passes_category_location_sort_through():
    fake = FakeJobService()
    client = _client(fake)

    client.get(
        "/api/job/all",
        params={"category": "Engineering", "location": "Remote", "sort": "salary"},
    )

    call = fake.calls[0]
    assert call["category"] == "Engineering"
    assert call["location"] == "Remote"
    assert call["sort"] == "salary"


def test_combines_all_filters_in_one_request():
    fake = FakeJobService()
    client = _client(fake)

    client.get(
        "/api/job/all",
        params={
            "search": "engineer",
            "category": "Engineering",
            "type": "Full-time",
            "location": "Remote",
            "sort": "alphabetical",
            "page": 2,
            "limit": 10,
        },
    )

    call = fake.calls[0]
    assert call == {
        "page": 2,
        "limit": 10,
        "search": "engineer",
        "category": "Engineering",
        "job_type": "Full-time",
        "location": "Remote",
        "sort": "alphabetical",
    }


def test_blank_filter_values_dont_error():
    """GridFilters sends '' when a dropdown is set to 'all' (see
    selectedCategory !== 'all' ? selectedCategory : ''). This must not
    500, and must not be treated as a literal search for the empty string."""
    fake = FakeJobService()
    client = _client(fake)

    res = client.get(
        "/api/job/all",
        params={"category": "", "type": "", "location": "", "search": ""},
    )

    assert res.status_code == 200
    call = fake.calls[0]
    assert not call["category"]
    assert not call["job_type"]
    assert not call["location"]
    assert not call["search"]


def test_custom_page_and_limit():
    fake = FakeJobService()
    client = _client(fake)

    client.get("/api/job/all", params={"page": 3, "limit": 5})

    assert fake.calls[0]["page"] == 3
    assert fake.calls[0]["limit"] == 5


def test_response_shape_matches_schema():
    fake = FakeJobService(jobs=[_job_dict(id=7, title="Data Engineer")], total=1)
    client = _client(fake)

    res = client.get("/api/job/all")
    body = res.json()

    assert body["total"] == 1
    assert body["page"] == 1
    assert body["limit"] == 20
    assert body["jobs"][0]["id"] == 7
    assert body["jobs"][0]["title"] == "Data Engineer"
    assert body["jobs"][0]["tags"] == ["python", "fastapi"]


def test_empty_results_return_empty_list_not_error():
    fake = FakeJobService(jobs=[], total=0)
    client = _client(fake)

    res = client.get("/api/job/all")

    assert res.status_code == 200
    body = res.json()
    assert body["jobs"] == []
    assert body["total"] == 0