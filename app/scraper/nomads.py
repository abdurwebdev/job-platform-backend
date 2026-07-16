from typing import Any, Optional

from app.scraper.base_api import BaseApiScraper
from app.scraper.job_factory import build_job
from app.scraper.schemas import StandardJob


class WorkingNomadsScraper(BaseApiScraper):
    data_key = None  # response is a raw JSON array, not wrapped in a key

    def __init__(self):
        super().__init__(
            url="https://www.workingnomads.com/api/exposed_jobs/",
            source_name="WorkingNomads",
        )

    def map_item(self, item: Any) -> Optional[StandardJob]:
        description = self.clean_html(item.get("description", ""))
        tags = item.get("tags", "")
        tags_list = [t.strip() for t in tags.split(",")] if tags else []

        return build_job(
            title=item.get("title"),
            url=item.get("url"),
            company_name=item.get("company_name"),
            company_logo=None,
            category=item.get("category_name") or "General",
            tags=tags_list,
            job_type="Full-time",
            publication_date=item.get("pub_date"),
            salary="Undisclosed",
            candidate_required_location=item.get("location") or "Global",
            description=description,
            source=self.source_name,
            remote=True,
            location=item.get("location"),
            external_id=item.get("url"),
        )