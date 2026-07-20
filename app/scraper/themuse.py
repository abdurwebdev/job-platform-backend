import os
from typing import Any, List, Optional

from app.scraper.base_api import BaseApiScraper
from app.scraper.job_factory import build_job
from app.scraper.schemas import StandardJob
from app.scraper.client import get_json


class TheMuseScraper(BaseApiScraper):
    data_key = "results"
    MAX_PAGES = 3  # be a good citizen of the free tier (500 req/hr unauthenticated)

    def __init__(self):
        api_key = os.environ.get("THEMUSE_API_KEY")
        self.api_key = api_key
        super().__init__(
            url=self._build_url(1),
            source_name="TheMuse",
        )

    def _build_url(self, page: int) -> str:
        url = f"https://www.themuse.com/api/public/jobs?page={page}"
        if self.api_key:
            url += f"&api_key={self.api_key}"
        return url

    def scrape(self) -> List[StandardJob]:
        jobs: List[StandardJob] = []

        for page in range(1, self.MAX_PAGES + 1):
            
            response = get_json(
    self._build_url(page),
    scraper_name=self.source_name,
)
            if not response:
                break

            data = response.get(self.data_key, [])
            if not data:
                break

            jobs.extend(self.parse(data))

        return jobs

    def map_item(self, item: Any) -> Optional[StandardJob]:
        description = self.clean_html(item.get("contents", ""))
        locations = item.get("locations", []) or []
        location_str = ", ".join(l.get("name", "") for l in locations) or "Global"
        categories = item.get("categories", []) or []
        category = categories[0].get("name") if categories else "General"
        company = item.get("company", {}) or {}
        refs = item.get("refs", {}) or {}

        return build_job(
            title=item.get("name"),
            url=refs.get("landing_page"),
            company_name=company.get("name"),
            company_logo=None,
            category=category or "General",
            tags=[],
            job_type=item.get("type") or "Full-time",
            publication_date=item.get("publication_date"),
            salary="Undisclosed",
            candidate_required_location=location_str,
            description=description,
            source=self.source_name,
            remote="flexible" in location_str.lower() or "remote" in location_str.lower(),
            location=location_str,
            external_id=str(item.get("id") or item.get("short_name")),
        )